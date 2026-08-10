from __future__ import annotations

import json
import random
from dataclasses import replace
from datetime import UTC, datetime, timedelta

import pytest

from loop.cache import ResponseCache
from loop.gemini import (
    BudgetHardStop,
    GeminiClient,
    ModelUnavailable,
    RateLimited,
    TransportError,
)
from loop.ledger import RequestLedger
from loop.protocol import cache_key
from loop.run import run_pass
from tests.conftest import FakeTransport

NOW = datetime(2026, 8, 10, 12, 0, tzinfo=UTC)


def fast_client_factory(**kwargs):
    """A GeminiClient whose throttle and backoff waits are virtual.

    `run_pass` builds its own client, so tests exercising the failure paths
    would otherwise sit through real exponential backoff — minutes of
    genuine sleeping to assert on a manifest. The clock is advanced rather
    than skipped, so the throttle logic under test is still the real one.
    """
    ticks = {"t": 0.0}

    def sleep(seconds):
        ticks["t"] += seconds

    return GeminiClient(
        **kwargs,
        sleep=sleep,
        monotonic=lambda: ticks["t"],
        clock=lambda: NOW,
        rng=random.Random(0),
    )


def _client(repo_root, config, transport, *, reservation=100, slept=None):
    ticks = {"t": 0.0}

    def monotonic():
        return ticks["t"]

    def sleep(seconds):
        if slept is not None:
            slept.append(seconds)
        ticks["t"] += seconds

    return GeminiClient(
        config=config,
        cache=ResponseCache(repo_root / ".cache"),
        ledger=RequestLedger(repo_root / "runs" / "ledger", clock=lambda: NOW),
        transport=transport,
        run_id="test-run",
        request_reservation=reservation,
        sleep=sleep,
        monotonic=monotonic,
        clock=lambda: NOW,
        rng=random.Random(0),
    )


def test_second_identical_call_costs_no_request(repo_root, config):
    transport = FakeTransport()
    first = _client(repo_root, config, transport)
    first.complete(prompt="score p01", case_id="p01")

    # Fresh client, fresh in-memory state, same on-disk cache.
    second = _client(repo_root, config, transport)
    response, from_cache = second.complete(prompt="score p01", case_id="p01")

    assert from_cache is True
    assert len(transport.calls) == 1
    assert second.requests_made == 0
    assert response.text == "response-1"


def test_protocol_bump_invalidates_the_cache(repo_root, config):
    """A protocol change may never silently reuse old measurements."""
    transport = FakeTransport()
    _client(repo_root, config, transport).complete(prompt="score p01", case_id="p01")
    bumped = replace(config, protocol_version=config.protocol_version + 1)
    _, from_cache = _client(repo_root, bumped, transport).complete(
        prompt="score p01", case_id="p01"
    )
    assert from_cache is False
    assert len(transport.calls) == 2


def test_rate_limit_backs_off_with_jitter_then_succeeds(repo_root, config):
    slept: list[float] = []
    transport = FakeTransport(failures=[RateLimited("429"), RateLimited("429")])
    client = _client(repo_root, config, transport, slept=slept)
    response, from_cache = client.complete(prompt="score p01", case_id="p01")

    assert (from_cache, len(transport.calls)) == (False, 3)
    backoffs = [s for s in slept if s >= config.throttle.backoff_initial_seconds]
    assert len(backoffs) == 2
    assert backoffs[1] > backoffs[0]  # exponential
    # Jitter: never the bare multiple.
    assert backoffs[0] != config.throttle.backoff_initial_seconds
    assert response.text == "response-3"


def test_every_attempt_is_charged_to_the_ledger(repo_root, config):
    transport = FakeTransport(failures=[RateLimited("429")])
    client = _client(repo_root, config, transport)
    client.complete(prompt="score p01", case_id="p01")
    ledger = RequestLedger(repo_root / "runs" / "ledger", clock=lambda: NOW)
    assert ledger.requests_spent_today(model=config.model) == 2


def test_exhausted_retries_fail_loudly_and_cache_nothing(repo_root, config):
    """A failed call must not leave a cache entry.

    A cached failure would be served forever as a real measurement.
    """
    transport = FakeTransport(
        failures=[TransportError("boom")] * config.throttle.max_retries
    )
    client = _client(repo_root, config, transport)
    with pytest.raises(TransportError, match=r"attempts against .* all"):
        client.complete(prompt="score p01", case_id="p01")

    assert len(transport.calls) == config.throttle.max_retries
    cache = ResponseCache(repo_root / ".cache")
    key = cache_key(
        model=config.model, prompt="score p01", case_id="p01",
        protocol_version=config.protocol_version,
        sampling=config.sampling.as_dict(),
    )
    assert not cache.has(key)
    # Still charged: the provider was hit five times.
    ledger = RequestLedger(repo_root / "runs" / "ledger", clock=lambda: NOW)
    assert ledger.requests_spent_today(model=config.model) == config.throttle.max_retries


def test_model_unavailable_never_switches_to_the_fallback(repo_root, config):
    """A run with two models in it is not a measurement."""
    transport = FakeTransport(failures=[ModelUnavailable("404 no such model")])
    client = _client(repo_root, config, transport)
    with pytest.raises(ModelUnavailable) as exc:
        client.complete(prompt="score p01", case_id="p01")
    assert "will NOT" in str(exc.value)
    assert list(config.fallback_models)[0] in str(exc.value)
    assert len(transport.calls) == 1  # not retried either
    assert all(call["model"] == config.model for call in transport.calls)


def test_requests_are_serial_and_throttled(repo_root, config):
    slept: list[float] = []
    transport = FakeTransport()
    client = _client(repo_root, config, transport, slept=slept)
    for i in range(3):
        client.complete(prompt=f"prompt {i}", case_id=f"p{i:02d}")
    gaps = [s for s in slept if s == pytest.approx(config.throttle.min_seconds_between_requests)]
    assert len(gaps) == 2  # first call needs no wait


def test_reservation_exhaustion_stops_cleanly_with_work_cached(repo_root, config):
    transport = FakeTransport()
    client = _client(repo_root, config, transport, reservation=2)
    client.complete(prompt="a", case_id="p01")
    client.complete(prompt="b", case_id="p02")
    with pytest.raises(BudgetHardStop):
        client.complete(prompt="c", case_id="p03")

    # The third call's response WAS paid for, so it must be cached: resuming
    # tomorrow re-reads it for free rather than paying again.
    resumed = _client(repo_root, config, transport, reservation=10)
    _, from_cache = resumed.complete(prompt="c", case_id="p03")
    assert from_cache is True
    assert len(transport.calls) == 3


def test_run_pass_writes_a_traceable_manifest(repo_root, config):
    transport = FakeTransport()
    result = run_pass(
        client_factory=fast_client_factory,
        kind="smoke",
        specs=[("p01", "prompt one"), ("p02", "prompt two")],
        declared_budget=60,
        config=config,
        transport=transport,
        repo_root=repo_root,
        notes={"label": "non-baseline"},
        run_id="20260810T120000Z-smoke",
    )
    manifest = json.loads(
        (config.runs_dir / result.run_id / "manifest.json").read_text()
    )
    assert manifest["model"] == config.model
    assert manifest["protocol_version"] == config.protocol_version
    assert manifest["spent"] == {"requests_made": 2, "cache_hits": 0}
    assert manifest["budget"]["declared_budget"] == 60
    assert manifest["budget"]["requests_needed"] == 2
    assert manifest["quota"]["verified_on"] == config.quota.verified_on
    assert manifest["notes"] == {"label": "non-baseline"}
    assert [c["case_id"] for c in manifest["calls"]] == ["p01", "p02"]
    assert all(len(c["prompt_sha256"]) == 64 for c in manifest["calls"])


def test_rerunning_a_pass_costs_zero_requests(repo_root, config):
    transport = FakeTransport()
    specs = [("p01", "prompt one"), ("p02", "prompt two")]
    kwargs = dict(
        kind="smoke", specs=specs, declared_budget=60, config=config,
        transport=transport, repo_root=repo_root,
        client_factory=fast_client_factory,
    )
    run_pass(run_id="run-a", **kwargs)
    run_pass(run_id="run-b", **kwargs)
    assert len(transport.calls) == 2
    manifest = json.loads((config.runs_dir / "run-b" / "manifest.json").read_text())
    assert manifest["spent"] == {"requests_made": 0, "cache_hits": 2}


def test_cached_response_records_what_it_was_generated_under(repo_root, config):
    """A cached response must be auditable without re-deriving the config."""
    transport = FakeTransport()
    client = _client(repo_root, config, transport)
    response, _ = client.complete(prompt="score p01", case_id="p01")
    assert response.sampling == config.sampling.as_dict()
    assert response.model == config.model
    assert response.protocol_version == config.protocol_version


def test_a_temperature_edit_does_not_reuse_the_old_response(repo_root, config):
    """The silent-contamination bug, at client level.

    Without sampling in the cache key, this second call would be served
    from cache and a pass contaminated by a mid-work temperature edit would
    look identical to a clean one in every artifact.
    """
    transport = FakeTransport()
    _client(repo_root, config, transport).complete(prompt="score p01", case_id="p01")
    hotter = replace(config, sampling=replace(config.sampling, temperature=0.9))
    _, from_cache = _client(repo_root, hotter, transport).complete(
        prompt="score p01", case_id="p01"
    )
    assert from_cache is False
    assert len(transport.calls) == 2
    assert [c["temperature"] for c in transport.calls] == [0.7, 0.9]


def test_a_failed_pass_still_writes_its_manifest(repo_root, config):
    """The manifest matters most for the run that did not finish.

    Without it, a pass that died two-thirds through is indistinguishable
    from one that never started — and the quota it spent is unaccounted.
    """
    transport = FakeTransport(
        failures=[TransportError("boom")] * config.throttle.max_retries
    )
    with pytest.raises(TransportError):
        run_pass(
            client_factory=fast_client_factory,
            kind="smoke",
            specs=[("p01", "one"), ("p02", "two"), ("p03", "three")],
            declared_budget=60,
            config=config,
            transport=transport,
            repo_root=repo_root,
            run_id="failed-run",
        )

    manifest = json.loads((config.runs_dir / "failed-run" / "manifest.json").read_text())
    assert manifest["outcome"] == "failed:TransportError"
    assert "boom" in manifest["error"]
    assert manifest["cases_not_reached"] == ["p01", "p02", "p03"]
    assert manifest["calls"] == []
    # The quota it burned is still accounted for.
    ledger = RequestLedger(repo_root / "runs" / "ledger")
    assert ledger.requests_spent_today(model=config.model) == config.throttle.max_retries


def test_an_unavailable_model_still_writes_its_manifest(repo_root, config):
    transport = FakeTransport(failures=[ModelUnavailable("404")])
    with pytest.raises(ModelUnavailable):
        run_pass(
            client_factory=fast_client_factory,
            kind="smoke", specs=[("p01", "one")], declared_budget=60,
            config=config, transport=transport, repo_root=repo_root,
            run_id="unavailable-run",
        )
    manifest = json.loads(
        (config.runs_dir / "unavailable-run" / "manifest.json").read_text()
    )
    assert manifest["outcome"] == "failed:ModelUnavailable"
    assert manifest["cases_not_reached"] == ["p01"]


def test_a_partial_pass_names_the_cases_it_never_reached(repo_root, config):
    """A measurement missing cases is not the same measurement."""
    calls_before_failure = {"n": 0}

    class FailAfterTwo(FakeTransport):
        def generate(self, **kwargs):
            calls_before_failure["n"] += 1
            if calls_before_failure["n"] > 2:
                raise ModelUnavailable("model retired mid-pass")
            return super().generate(**kwargs)

    with pytest.raises(ModelUnavailable):
        run_pass(
            client_factory=fast_client_factory,
            kind="smoke",
            specs=[("p01", "1"), ("p02", "2"), ("p03", "3"), ("p04", "4")],
            declared_budget=60, config=config, transport=FailAfterTwo(),
            repo_root=repo_root, run_id="partial-run",
        )

    manifest = json.loads((config.runs_dir / "partial-run" / "manifest.json").read_text())
    assert [c["case_id"] for c in manifest["calls"]] == ["p01", "p02"]
    assert manifest["cases_not_reached"] == ["p03", "p04"]
    assert manifest["spent"]["requests_made"] == 2


def test_manifest_records_a_clean_pass_as_complete(repo_root, config):
    result = run_pass(
        client_factory=fast_client_factory,
        kind="smoke", specs=[("p01", "one")], declared_budget=60,
        config=config, transport=FakeTransport(), repo_root=repo_root,
        run_id="clean-run",
    )
    manifest = json.loads((config.runs_dir / "clean-run" / "manifest.json").read_text())
    assert manifest["outcome"] == "complete"
    assert manifest["error"] is None
    assert manifest["cases_not_reached"] == []
    assert result.outcome == "complete"


def test_a_budget_stop_is_an_orderly_ending_not_a_failure(repo_root, config):
    """The most likely way a real pass ends, and the only one that returns.

    Hitting the reservation is designed behaviour: everything paid for is
    cached, so re-running resumes at zero cost for it. `run_pass` therefore
    returns its partial result rather than raising, unlike the two states
    that mean something went wrong.
    """
    class RateLimitedOnce(FakeTransport):
        """Every case 429s once, then succeeds — a busy provider, not a broken one."""

        def __init__(self):
            super().__init__()
            self._seen: set[str] = set()

        def generate(self, **kwargs):
            prompt = kwargs["prompt"]
            if prompt not in self._seen:
                self._seen.add(prompt)
                self.calls.append(kwargs)
                raise RateLimited("429")
            return super().generate(**kwargs)

    specs = [(f"p{i:02d}", f"prompt {i}") for i in range(1, 11)]
    result = run_pass(  # returns; does not raise
        client_factory=fast_client_factory,
        kind="smoke",
        specs=specs,
        declared_budget=60,
        config=config,
        transport=RateLimitedOnce(),
        repo_root=repo_root,
        run_id="budget-stop-run",
    )

    # 10 calls needing 2 attempts each = 20 attempts against a reservation of
    # 10 + max(ceil(2.5), 4) = 14, so the pass stops part-way.
    assert result.budget.requests_needed == 10
    assert result.budget.headroom_reserved == 4
    assert result.outcome == "stopped:budget"
    assert result.error is None

    manifest = json.loads(
        (config.runs_dir / "budget-stop-run" / "manifest.json").read_text()
    )
    assert manifest["outcome"] == "stopped:budget"
    assert manifest["stopped_early"] is not None
    scored = [c["case_id"] for c in manifest["calls"]]
    assert scored == ["p01", "p02", "p03", "p04", "p05", "p06", "p07"]
    assert manifest["cases_not_reached"] == ["p08", "p09", "p10"]

    # The point of an orderly stop: resuming pays only for what is left.
    resumed = run_pass(
        client_factory=fast_client_factory,
        kind="smoke", specs=specs, declared_budget=60, config=config,
        transport=RateLimitedOnce(), repo_root=repo_root, run_id="resumed-run",
    )
    assert resumed.budget.cache_hits == 7
    assert resumed.budget.requests_needed == 3


def test_retry_loop_stamps_each_attempt_at_its_own_time(repo_root, config):
    """The midnight fix, proven through the real retry loop.

    `test_retries_across_utc_midnight_land_on_the_right_days` drives the
    ledger directly, so it would still pass if the client read the clock
    once and stamped every attempt in a batch afterwards — silently
    restoring the bug behind an API that looks attempt-safe. Here the
    ledger's clock advances with the client's own backoff sleeps.
    """
    virtual = {"t": 0.0}
    start = datetime(2026, 8, 10, 23, 59, 55, tzinfo=UTC)

    def sleep(seconds):
        virtual["t"] += seconds

    client = GeminiClient(
        config=config,
        cache=ResponseCache(repo_root / ".cache"),
        ledger=RequestLedger(
            repo_root / "runs" / "ledger",
            clock=lambda: start + timedelta(seconds=virtual["t"]),
        ),
        transport=FakeTransport(failures=[RateLimited("429")]),
        run_id="midnight-run",
        request_reservation=10,
        sleep=sleep,
        monotonic=lambda: virtual["t"],
        clock=lambda: start + timedelta(seconds=virtual["t"]),
        rng=random.Random(0),
    )
    client.complete(prompt="score p01", case_id="p01")

    # Backoff is >= 8s from 23:59:55, so attempt two lands on the 11th.
    ledger = RequestLedger(repo_root / "runs" / "ledger")
    assert ledger.requests_spent_on("2026-08-10", model=config.model) == 1
    assert ledger.requests_spent_on("2026-08-11", model=config.model) == 1
