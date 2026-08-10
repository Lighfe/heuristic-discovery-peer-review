"""Loading and validating `loop/config.toml`.

The quota figures are runtime-discovered config, not constants: see the
header of config.toml. This module's one opinion is that an unverified
quota block may not spend a request.
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent / "config.toml"


class ConfigError(RuntimeError):
    """The configuration is unusable. Always fatal; never defaulted around."""


@dataclass(frozen=True)
class Quota:
    verified: bool
    verified_on: str
    source: str
    applies_to: tuple[str, ...]  # exact model ids these figures were read for
    requests_per_day: int
    requests_per_minute: int
    input_tokens_per_minute: int


@dataclass(frozen=True)
class Throttle:
    min_seconds_between_requests: float
    max_retries: int
    backoff_initial_seconds: float
    backoff_multiplier: float
    backoff_max_seconds: float
    backoff_jitter_seconds: float


@dataclass(frozen=True)
class Sampling:
    temperature: float
    max_output_tokens: int

    def as_dict(self) -> dict[str, object]:
        """The fingerprint that goes into every cache key.

        Kept in step with `protocol.SAMPLING_KEYS`, which a test enforces:
        a sampling knob missing from the key is a silent-staleness bug.
        """
        return {
            "temperature": self.temperature,
            "max_output_tokens": self.max_output_tokens,
        }


@dataclass(frozen=True)
class Config:
    protocol_version: int
    model: str
    fallback_models: tuple[str, ...]
    quota: Quota
    throttle: Throttle
    sampling: Sampling
    cache_dir: Path
    runs_dir: Path

    def require_spendable(self) -> None:
        """Raise unless this config is allowed to spend real requests.

        Called before any pass that would hit the provider. An unverified
        quota block means nobody has read the account's real limits, and
        the runner would be budgeting against a guess.
        """
        if not self.quota.verified:
            raise ConfigError(
                "gemini.quota.verified is false: the account's real rate "
                "limits have not been read from AI Studio. Refusing to "
                "spend requests against a guessed budget."
            )
        if self.sampling.temperature <= 0:
            raise ConfigError(
                "gemini.sampling.temperature must be above zero, or the "
                "self-consistency measurement is vacuously perfect "
                "(decision `agreement-protocol-ceiling`)."
            )


def load_config(path: Path | None = None, repo_root: Path | None = None) -> Config:
    path = path or DEFAULT_CONFIG_PATH
    root = repo_root or REPO_ROOT
    try:
        raw = tomllib.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:  # pragma: no cover - operator error
        raise ConfigError(f"no runner config at {path}") from exc

    # Every key access below goes through this, so a missing *nested* key
    # gets the same named, actionable error as a missing top-level one.
    def need(table: dict, key: str, where: str):
        try:
            return table[key]
        except KeyError:
            raise ConfigError(f"config {path} is missing [{where}] key {key!r}") from None

    gemini = need(raw, "gemini", "top level")
    quota_raw = need(gemini, "quota", "gemini")
    throttle_raw = need(gemini, "throttle", "gemini")
    sampling_raw = need(gemini, "sampling", "gemini")
    paths_raw = need(raw, "paths", "top level")
    protocol_version = int(need(raw, "protocol_version", "top level"))
    model = str(need(gemini, "primary", "gemini"))

    applies_to = need(quota_raw, "applies_to", "gemini.quota")
    if isinstance(applies_to, str):
        raise ConfigError(
            "gemini.quota.applies_to must be a list of exact model ids, not "
            "free text: the model/quota pairing is checked by equality, and "
            "substring matching against prose silently accepts the wrong model."
        )

    quota = Quota(
        verified=bool(need(quota_raw, "verified", "gemini.quota")),
        verified_on=str(need(quota_raw, "verified_on", "gemini.quota")),
        source=str(need(quota_raw, "source", "gemini.quota")),
        applies_to=tuple(str(m) for m in applies_to),
        requests_per_day=int(need(quota_raw, "requests_per_day", "gemini.quota")),
        requests_per_minute=int(need(quota_raw, "requests_per_minute", "gemini.quota")),
        input_tokens_per_minute=int(
            need(quota_raw, "input_tokens_per_minute", "gemini.quota")
        ),
    )

    if quota.verified and model not in quota.applies_to:
        raise ConfigError(
            f"quota figures were read for {list(quota.applies_to)} but the "
            f"primary model is {model!r}. Quota is per-model on the free tier "
            "(2.5-flash is 20 RPD, 3.5-flash-lite is 500), so budgeting one "
            "model against another's limits is not a small error. Re-read the "
            "AI Studio dashboard for the model actually in use."
        )

    return Config(
        protocol_version=protocol_version,
        model=model,
        fallback_models=tuple(str(m) for m in gemini.get("fallback", ())),
        quota=quota,
        throttle=Throttle(
            min_seconds_between_requests=float(
                need(throttle_raw, "min_seconds_between_requests", "gemini.throttle")
            ),
            max_retries=int(need(throttle_raw, "max_retries", "gemini.throttle")),
            backoff_initial_seconds=float(
                need(throttle_raw, "backoff_initial_seconds", "gemini.throttle")
            ),
            backoff_multiplier=float(
                need(throttle_raw, "backoff_multiplier", "gemini.throttle")
            ),
            backoff_max_seconds=float(
                need(throttle_raw, "backoff_max_seconds", "gemini.throttle")
            ),
            backoff_jitter_seconds=float(
                need(throttle_raw, "backoff_jitter_seconds", "gemini.throttle")
            ),
        ),
        sampling=Sampling(
            temperature=float(need(sampling_raw, "temperature", "gemini.sampling")),
            max_output_tokens=int(
                need(sampling_raw, "max_output_tokens", "gemini.sampling")
            ),
        ),
        cache_dir=root / str(need(paths_raw, "cache_dir", "paths")),
        runs_dir=root / str(need(paths_raw, "runs_dir", "paths")),
    )
