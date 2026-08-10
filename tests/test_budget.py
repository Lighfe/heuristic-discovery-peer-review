from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime

import pytest

from loop.budget import BudgetExceeded, plan_budget
from loop.cache import CachedResponse, ResponseCache
from loop.config import ConfigError
from loop.ledger import RequestLedger
from loop.run import build_calls

NOW = datetime(2026, 8, 10, 12, 0, tzinfo=UTC)


def _fixtures(repo_root, config):
    return (
        ResponseCache(repo_root / ".cache"),
        RequestLedger(repo_root / "runs" / "ledger", clock=lambda: NOW),
    )


def test_a_fitting_pass_plans_cleanly(repo_root, config):
    cache, ledger = _fixtures(repo_root, config)
    calls = build_calls([(f"p{i:02d}", f"prompt {i}") for i in range(10)], config=config)
    plan = plan_budget(
        calls, config=config, cache=cache, ledger=ledger, declared_budget=60
    )
    assert plan.requests_needed == 10
    assert plan.cache_hits == 0
    assert plan.remaining_today == config.quota.requests_per_day


def test_cached_calls_cost_nothing(repo_root, config):
    """The guarantee the whole cost model rests on."""
    cache, ledger = _fixtures(repo_root, config)
    calls = build_calls([("p01", "prompt"), ("p02", "prompt")], config=config)
    cache.put(
        CachedResponse(
            key=calls[0].cache_key, model=config.model, case_id="p01",
            protocol_version=config.protocol_version, prompt_sha256="x",
            text="cached", input_tokens=1, output_tokens=1,
            requested_at=NOW.isoformat(), run_id="earlier", prompt="prompt",
            sampling=config.sampling.as_dict(),
        )
    )
    plan = plan_budget(
        calls, config=config, cache=cache, ledger=ledger, declared_budget=60
    )
    assert (plan.cache_hits, plan.requests_needed) == (1, 1)


def test_pass_over_its_declared_budget_refuses_to_start(repo_root, config):
    cache, ledger = _fixtures(repo_root, config)
    calls = build_calls([(f"p{i:02d}", f"prompt {i}") for i in range(61)], config=config)
    with pytest.raises(BudgetExceeded, match="declared a budget"):
        plan_budget(calls, config=config, cache=cache, ledger=ledger, declared_budget=60)


def test_pass_over_the_day_quota_refuses_to_start(repo_root, config):
    """No request is spent before the refusal — that is the point."""
    cache, ledger = _fixtures(repo_root, config)
    for _ in range(config.quota.requests_per_day - 5):
        ledger.record_attempt(
            run_id="earlier", model=config.model, case_id="p01",
            protocol_version=config.protocol_version, attempt=1,
            input_tokens=1, output_tokens=1, outcome="ok",
        )
    calls = build_calls([(f"p{i:02d}", f"prompt {i}") for i in range(10)], config=config)
    with pytest.raises(BudgetExceeded, match="remain"):
        plan_budget(calls, config=config, cache=cache, ledger=ledger, declared_budget=60)


def test_earlier_spend_on_another_model_does_not_block_this_one(repo_root, config):
    cache, ledger = _fixtures(repo_root, config)
    for _ in range(config.quota.requests_per_day):
        ledger.record_attempt(
            run_id="earlier", model="some-other-model", case_id="p01",
            protocol_version=1, attempt=1, input_tokens=1, output_tokens=1,
            outcome="ok",
        )
    calls = build_calls([("p01", "prompt")], config=config)
    assert plan_budget(
        calls, config=config, cache=cache, ledger=ledger, declared_budget=60
    ).requests_needed == 1


def test_unverified_quota_refuses_to_spend(repo_root, config):
    """Nobody has read the real limits, so any budget is a guess."""
    cache, ledger = _fixtures(repo_root, config)
    unverified = replace(config, quota=replace(config.quota, verified=False))
    with pytest.raises(ConfigError, match="not been read"):
        plan_budget(
            build_calls([("p01", "x")], config=config),
            config=unverified, cache=cache, ledger=ledger, declared_budget=60,
        )


def test_temperature_zero_refuses_to_spend(repo_root, config):
    cache, ledger = _fixtures(repo_root, config)
    zero_temp = replace(config, sampling=replace(config.sampling, temperature=0.0))
    with pytest.raises(ConfigError, match="above zero"):
        plan_budget(
            build_calls([("p01", "x")], config=config),
            config=zero_temp, cache=cache, ledger=ledger, declared_budget=60,
        )


def test_a_temperature_edit_invalidates_the_cached_pass(repo_root, config):
    """The silent-contamination guard, at pass level.

    A pass re-planned under a different temperature must cost requests
    again rather than replaying responses generated at the old one.
    """
    cache, ledger = _fixtures(repo_root, config)
    specs = [("p01", "prompt one"), ("p02", "prompt two")]
    for call in build_calls(specs, config=config):
        cache.put(
            CachedResponse(
                key=call.cache_key, model=config.model, case_id=call.case_id,
                protocol_version=config.protocol_version, prompt_sha256="x",
                text="cached", input_tokens=1, output_tokens=1,
                requested_at=NOW.isoformat(), run_id="earlier",
                prompt=call.prompt, sampling=config.sampling.as_dict(),
            )
        )
    assert plan_budget(
        build_calls(specs, config=config), config=config, cache=cache,
        ledger=ledger, declared_budget=60,
    ).requests_needed == 0

    hotter = replace(config, sampling=replace(config.sampling, temperature=0.9))
    assert plan_budget(
        build_calls(specs, config=hotter), config=hotter, cache=cache,
        ledger=ledger, declared_budget=60,
    ).requests_needed == 2


def test_quota_read_for_another_model_refuses_to_load(repo_root):
    """20 RPD vs 500 RPD: budgeting one model on another's figures is fatal."""
    from loop.config import load_config

    path = repo_root / "loop" / "config.toml"
    path.write_text(
        path.read_text().replace(
            'applies_to = ["gemini-3.5-flash-lite"]', 'applies_to = ["gemini-2.5-flash"]'
        )
    )
    with pytest.raises(ConfigError, match="quota figures were read for"):
        load_config(path=path, repo_root=repo_root)


def test_missing_nested_key_names_itself(repo_root):
    from loop.config import load_config

    path = repo_root / "loop" / "config.toml"
    path.write_text(path.read_text().replace("requests_per_day = 500", ""))
    with pytest.raises(ConfigError, match=r"\[gemini.quota\] key 'requests_per_day'"):
        load_config(path=path, repo_root=repo_root)


def test_headroom_always_covers_one_full_retry_sequence(repo_root, config):
    """Stated explicitly rather than left implicit in a failure-path test.

    Without this floor a small pass trips the budget stop before its retry
    policy has run, so "out of budget" and "the provider is failing" become
    indistinguishable — a distinction `objective.md`'s stopping criterion
    depends on.
    """
    cache, ledger = _fixtures(repo_root, config)
    for size in (1, 2, 5, 60):
        plan = plan_budget(
            build_calls([(f"p{i:02d}", f"prompt {i}") for i in range(size)], config=config),
            config=config, cache=cache, ledger=ledger, declared_budget=60,
        )
        assert plan.headroom_reserved >= config.throttle.max_retries - 1

    # A pass with nothing to do reserves nothing.
    assert plan_budget(
        [], config=config, cache=cache, ledger=ledger, declared_budget=60
    ).headroom_reserved == 0
