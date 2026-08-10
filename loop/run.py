"""Pass driver and run manifest.

A *pass* is a declared list of model calls, budgeted before it starts,
executed serially, and written up in a manifest under `runs/<run-id>/`.

The manifest is the artifact every claim about a run has to point at
(CLAUDE.md: claims are traceable). It names the model, the protocol version,
the prompt hash of every call, requests spent against budget, cache hits,
and the files the pass produced. Prose summaries elsewhere are not evidence;
this is.
"""

from __future__ import annotations

import json
import os
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

from loop.budget import BudgetPlan, PlannedCall, plan_budget
from loop.cache import ResponseCache
from loop.config import REPO_ROOT, Config, ConfigError, load_config
from loop.gemini import (
    BudgetHardStop,
    GeminiClient,
    GeminiTransport,
    Transport,
)
from loop.ledger import RequestLedger
from loop.protocol import cache_key, prompt_hash


def new_run_id(kind: str, *, now: datetime | None = None) -> str:
    stamp = (now or datetime.now(UTC)).strftime("%Y%m%dT%H%M%SZ")
    return f"{stamp}-{kind}"


def load_api_key(env_var: str = "GEMINI_API_KEY", *, repo_root: Path | None = None) -> str:
    """Read the key from the environment, falling back to `.env`.

    `.env` is gitignored. The key never enters a prompt, a manifest or a
    cache entry.
    """
    key = os.environ.get(env_var)
    if not key:
        from dotenv import dotenv_values

        key = dotenv_values((repo_root or REPO_ROOT) / ".env").get(env_var)
    if not key:
        raise ConfigError(
            f"{env_var} is not set in the environment or in .env. "
            "Copy .env.example to .env and fill it in."
        )
    return key


@dataclass
class PassResult:
    run_id: str
    kind: str
    budget: BudgetPlan
    responses: dict[str, str] = field(default_factory=dict)  # cache_key -> text
    calls: list[dict] = field(default_factory=list)
    stopped_early: str | None = None
    # "complete" | "stopped:budget" | "failed:<ExceptionType>". Starts as
    # "incomplete" so a manifest written from a crash that escaped even the
    # handler below is never mistaken for a finished pass.
    outcome: str = "incomplete"
    error: str | None = None
    planned_case_ids: list[str] = field(default_factory=list)

    def cases_not_reached(self) -> list[str]:
        done = {call["case_id"] for call in self.calls}
        return [case_id for case_id in self.planned_case_ids if case_id not in done]


def build_calls(
    specs: list[tuple[str, str]],
    *,
    config: Config,
) -> list[PlannedCall]:
    """`specs` is [(case_id, prompt)] -> planned calls with their cache keys."""
    return [
        PlannedCall(
            case_id=case_id,
            prompt=prompt,
            cache_key=cache_key(
                model=config.model,
                prompt=prompt,
                case_id=case_id,
                protocol_version=config.protocol_version,
                sampling=config.sampling.as_dict(),
            ),
        )
        for case_id, prompt in specs
    ]


def run_pass(
    *,
    kind: str,
    specs: list[tuple[str, str]],
    declared_budget: int,
    config: Config | None = None,
    transport: Transport | None = None,
    repo_root: Path | None = None,
    notes: dict | None = None,
    run_id: str | None = None,
    client_factory: Callable[..., GeminiClient] | None = None,
) -> PassResult:
    """Budget, execute and write up one pass. Refuses to start if it does not fit."""
    config = config or load_config(repo_root=repo_root)
    root = repo_root or REPO_ROOT
    cache = ResponseCache(config.cache_dir)
    ledger = RequestLedger(config.runs_dir / "ledger")
    run_id = run_id or new_run_id(kind)

    calls = build_calls(specs, config=config)
    budget = plan_budget(
        calls,
        config=config,
        cache=cache,
        ledger=ledger,
        declared_budget=declared_budget,
    )

    if transport is None:
        transport = GeminiTransport(load_api_key(repo_root=root))

    factory = client_factory or GeminiClient
    client = factory(
        config=config,
        cache=cache,
        ledger=ledger,
        transport=transport,
        run_id=run_id,
        request_reservation=budget.requests_needed + budget.headroom_reserved,
    )

    result = PassResult(
        run_id=run_id,
        kind=kind,
        budget=budget,
        planned_case_ids=[call.case_id for call in calls],
    )
    try:
        for call in calls:
            try:
                response, from_cache = client.complete(
                    prompt=call.prompt, case_id=call.case_id
                )
            except BudgetHardStop as exc:
                # An orderly stop, not a failure: the reservation ran out and
                # everything paid for is cached.
                result.stopped_early = str(exc)
                result.outcome = "stopped:budget"
                break
            result.responses[call.cache_key] = response.text
            result.calls.append(
                {
                    "case_id": call.case_id,
                    "cache_key": call.cache_key,
                    "prompt_sha256": prompt_hash(call.prompt),
                    "from_cache": from_cache,
                    "input_tokens": response.input_tokens,
                    "output_tokens": response.output_tokens,
                }
            )
        else:
            result.outcome = "complete"
    except BaseException as exc:
        # Exhausted retries, an unavailable model, a KeyboardInterrupt: the
        # run still has to be describable. A failed pass is the one whose
        # manifest matters most — it is what says how much quota went where
        # and which cases never got scored. Losing it is how a partial pass
        # becomes indistinguishable from a clean one.
        result.outcome = f"failed:{type(exc).__name__}"
        result.error = f"{type(exc).__name__}: {exc}"
        raise
    finally:
        write_manifest(
            result,
            config=config,
            client=client,
            repo_root=root,
            notes=notes or {},
        )
    return result


def write_manifest(
    result: PassResult,
    *,
    config: Config,
    client: GeminiClient,
    repo_root: Path,
    notes: dict,
) -> Path:
    run_dir = config.runs_dir / result.run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "run_id": result.run_id,
        "kind": result.kind,
        "written_at": datetime.now(UTC).isoformat(),
        "model": config.model,
        "fallback_models_declared": list(config.fallback_models),
        "protocol_version": config.protocol_version,
        "sampling": config.sampling.as_dict(),
        "quota": {
            "verified_on": config.quota.verified_on,
            "source": config.quota.source,
            "applies_to": config.quota.applies_to,
            "requests_per_day": config.quota.requests_per_day,
            "requests_per_minute": config.quota.requests_per_minute,
            "input_tokens_per_minute": config.quota.input_tokens_per_minute,
        },
        "budget": result.budget.as_manifest_fields(),
        "spent": {
            "requests_made": client.requests_made,
            "cache_hits": client.cache_hits,
        },
        "outcome": result.outcome,
        "error": result.error,
        "stopped_early": result.stopped_early,
        # Named explicitly rather than left as the difference between two
        # lists: on a failed pass, which cases never got scored is the first
        # thing anyone needs, and a measurement missing cases is not the
        # same measurement.
        "cases_not_reached": result.cases_not_reached(),
        "calls": result.calls,
        "notes": notes,
    }
    path = run_dir / "manifest.json"
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    return path
