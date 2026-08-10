"""The Gemini client: one request at a time, cached, metered, loud on failure.

Four rules from the cost model in CLAUDE.md are implemented here:

1. **Cache first.** A key already in the cache costs nothing and never
   touches the provider.
2. **Throttle deliberately, no parallelism.** Requests are serial with a
   minimum interval, plus a rolling input-token window — with Flash-Lite at
   15 RPM but ~250k input TPM shared across models, either can bind.
3. **Backoff with jitter on 429**, never immediate retry, and every attempt
   is charged to the ledger because every attempt spends quota.
4. **Never switch models mid-run.** A run where half the reviews came from a
   different model is not a measurement. The configured fallback list is
   reported in the error so an operator can choose it for a *new* run; the
   client will not choose it for them.
"""

from __future__ import annotations

import random
import time
from dataclasses import dataclass
from typing import Protocol

from loop.cache import CachedResponse, ResponseCache
from loop.config import Config
from loop.ledger import RequestLedger, utc_now
from loop.protocol import cache_key, prompt_hash


class RateLimited(Exception):
    """Provider said 429. Retryable, with backoff."""


class ModelUnavailable(Exception):
    """The configured model does not exist or is not served. Never retried."""


class TransportError(Exception):
    """Any other provider-side failure. Retryable, with backoff."""


class BudgetHardStop(RuntimeError):
    """The pass consumed its reservation mid-flight and stopped cleanly.

    Not an error in the pass's logic: everything already paid for is in the
    cache, so resuming re-reads it for free.
    """


@dataclass(frozen=True)
class TransportResponse:
    text: str
    input_tokens: int
    output_tokens: int


class Transport(Protocol):
    """The provider seam. Tests substitute a fake; nothing else varies."""

    def generate(
        self,
        *,
        model: str,
        prompt: str,
        temperature: float,
        max_output_tokens: int,
    ) -> TransportResponse: ...


class GeminiTransport:
    """Real transport over `google-genai`."""

    def __init__(self, api_key: str) -> None:
        from google import genai  # imported lazily: tests need no SDK

        self._genai = genai
        self._client = genai.Client(api_key=api_key)

    def generate(
        self,
        *,
        model: str,
        prompt: str,
        temperature: float,
        max_output_tokens: int,
    ) -> TransportResponse:
        from google.genai import errors as genai_errors
        from google.genai import types

        try:
            response = self._client.models.generate_content(
                model=model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=temperature,
                    max_output_tokens=max_output_tokens,
                ),
            )
        except genai_errors.ClientError as exc:
            status = getattr(exc, "code", None)
            if status == 429:
                raise RateLimited(str(exc)) from exc
            if status == 404:
                raise ModelUnavailable(
                    f"model {model!r} is not available: {exc}"
                ) from exc
            raise TransportError(str(exc)) from exc
        except genai_errors.ServerError as exc:
            raise TransportError(str(exc)) from exc

        usage = response.usage_metadata
        text = response.text
        if text is None:
            # A blocked or empty completion is not a score. Fail loudly:
            # silently treating it as an abstention would put a hole in a
            # measurement without anything recording that it happened.
            raise TransportError(
                f"model {model!r} returned no text (finish reason: "
                f"{getattr(response.candidates[0], 'finish_reason', None) if response.candidates else 'no candidates'})"
            )
        return TransportResponse(
            text=text,
            input_tokens=int(getattr(usage, "prompt_token_count", 0) or 0),
            output_tokens=int(getattr(usage, "candidates_token_count", 0) or 0),
        )


class GeminiClient:
    def __init__(
        self,
        *,
        config: Config,
        cache: ResponseCache,
        ledger: RequestLedger,
        transport: Transport,
        run_id: str,
        request_reservation: int,
        sleep=time.sleep,
        monotonic=time.monotonic,
        clock=utc_now,
        rng: random.Random | None = None,
    ) -> None:
        self.config = config
        self.cache = cache
        self.ledger = ledger
        self.transport = transport
        self.run_id = run_id
        self._sleep = sleep
        self._monotonic = monotonic
        self._clock = clock
        self._rng = rng or random.Random()

        self._reservation = request_reservation
        self._attempts_spent = 0
        self._last_request_at: float | None = None
        self._token_window: list[tuple[float, int]] = []

        self.cache_hits = 0
        self.requests_made = 0

    # -- metering -----------------------------------------------------

    def _await_slot(self, estimated_input_tokens: int) -> None:
        """Block until both the RPM and the input-TPM windows allow a call."""
        now = self._monotonic()
        gap = self.config.throttle.min_seconds_between_requests
        if self._last_request_at is not None:
            wait = (self._last_request_at + gap) - now
            if wait > 0:
                self._sleep(wait)
                now = self._monotonic()

        limit = self.config.quota.input_tokens_per_minute
        while True:
            self._token_window = [
                (at, count) for at, count in self._token_window if now - at < 60.0
            ]
            in_window = sum(count for _, count in self._token_window)
            if in_window + estimated_input_tokens <= limit or not self._token_window:
                return
            oldest_at = min(at for at, _ in self._token_window)
            self._sleep(max(0.0, 60.0 - (now - oldest_at)) + 0.1)
            now = self._monotonic()

    def _record_attempt(
        self,
        case_id: str,
        attempt: int,
        input_tokens: int,
        output_tokens: int,
        outcome: str,
    ) -> None:
        """Charge one provider attempt to the ledger, stamped now.

        Called as each attempt returns, not once per logical call: that is
        what keeps a retry sequence straddling UTC midnight attributed to
        the days it actually spent quota on.
        """
        self.ledger.record_attempt(
            run_id=self.run_id,
            model=self.config.model,
            case_id=case_id,
            protocol_version=self.config.protocol_version,
            attempt=attempt,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            outcome=outcome,
        )

    def _charge(self, attempts: int) -> None:
        self._attempts_spent += attempts
        if self._attempts_spent > self._reservation:
            raise BudgetHardStop(
                f"run {self.run_id} consumed its reservation of "
                f"{self._reservation} requests (retries included). Everything "
                "paid for is cached; re-run to resume at zero cost for it."
            )

    # -- the one public call ------------------------------------------

    def complete(self, *, prompt: str, case_id: str) -> tuple[CachedResponse, bool]:
        """Return (response, from_cache).

        The cache write is the checkpoint: once this returns, the response
        survives the process dying.
        """
        key = cache_key(
            model=self.config.model,
            prompt=prompt,
            case_id=case_id,
            protocol_version=self.config.protocol_version,
            sampling=self.config.sampling.as_dict(),
        )
        cached = self.cache.get(key)
        if cached is not None:
            self.cache_hits += 1
            return cached, True

        estimated_input_tokens = max(1, len(prompt) // 3)
        attempts = 0
        delay = self.config.throttle.backoff_initial_seconds
        last_error: Exception | None = None

        while attempts < self.config.throttle.max_retries:
            self._await_slot(estimated_input_tokens)
            attempts += 1
            self._last_request_at = self._monotonic()
            try:
                result = self.transport.generate(
                    model=self.config.model,
                    prompt=prompt,
                    temperature=self.config.sampling.temperature,
                    max_output_tokens=self.config.sampling.max_output_tokens,
                )
            except ModelUnavailable as exc:
                # Never retried and never worked around. Switching to the
                # fallback here would mix models inside one measurement.
                self._token_window.append((self._monotonic(), estimated_input_tokens))
                self._record_attempt(case_id, attempts, 0, 0, "error:model_unavailable")
                self._charge(1)
                raise ModelUnavailable(
                    f"{exc}\nConfigured fallbacks: "
                    f"{list(self.config.fallback_models)}. This run will NOT "
                    "switch models: re-run deliberately with the fallback as "
                    "the primary, under a fresh cache namespace."
                ) from exc
            except (RateLimited, TransportError) as exc:
                last_error = exc
                self._token_window.append((self._monotonic(), estimated_input_tokens))
                self._record_attempt(
                    case_id, attempts, 0, 0, f"error:{type(exc).__name__.lower()}"
                )
                self._charge(1)
                if attempts >= self.config.throttle.max_retries:
                    break
                jitter = self._rng.uniform(0.0, self.config.throttle.backoff_jitter_seconds)
                self._sleep(min(delay, self.config.throttle.backoff_max_seconds) + jitter)
                delay = min(
                    delay * self.config.throttle.backoff_multiplier,
                    self.config.throttle.backoff_max_seconds,
                )
                continue

            self._token_window.append((self._monotonic(), result.input_tokens or estimated_input_tokens))
            response = CachedResponse(
                key=key,
                model=self.config.model,
                case_id=case_id,
                protocol_version=self.config.protocol_version,
                prompt_sha256=prompt_hash(prompt),
                text=result.text,
                input_tokens=result.input_tokens,
                output_tokens=result.output_tokens,
                requested_at=self._clock().isoformat(),
                run_id=self.run_id,
                prompt=prompt,
                sampling=self.config.sampling.as_dict(),
            )
            self.cache.put(response)  # checkpoint
            self._record_attempt(
                case_id, attempts, result.input_tokens, result.output_tokens, "ok"
            )
            self.requests_made += 1
            self._charge(1)
            return response, False

        raise TransportError(
            f"case {case_id}: {attempts} attempts against {self.config.model} all "
            f"failed; last error: {last_error}"
        )
