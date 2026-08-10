from __future__ import annotations

from datetime import UTC, datetime, timedelta

from loop.cache import CachedResponse, ResponseCache
from loop.ledger import RequestLedger


def _response(key: str = "abc123", **overrides) -> CachedResponse:
    base = dict(
        key=key,
        model="gemini-3.5-flash-lite",
        case_id="p01",
        protocol_version=1,
        prompt_sha256="deadbeef",
        text="2 points",
        input_tokens=1200,
        output_tokens=40,
        requested_at="2026-08-10T12:00:00+00:00",
        run_id="run-1",
        prompt="score this",
        sampling={"temperature": 0.7, "max_output_tokens": 2048},
    )
    base.update(overrides)
    return CachedResponse(**base)


def test_cache_roundtrip(tmp_path):
    cache = ResponseCache(tmp_path / ".cache")
    assert cache.get("abc123") is None
    assert not cache.has("abc123")
    cache.put(_response())
    assert cache.has("abc123")
    assert cache.get("abc123") == _response()


def test_cache_survives_a_new_instance(tmp_path):
    """Cache is on disk, so a later session's re-run is free."""
    ResponseCache(tmp_path / ".cache").put(_response())
    assert ResponseCache(tmp_path / ".cache").get("abc123").text == "2 points"


def test_cache_leaves_no_temp_files_behind(tmp_path):
    cache = ResponseCache(tmp_path / ".cache")
    cache.put(_response())
    assert [p.name for p in (tmp_path / ".cache" / "ab").iterdir()] == ["abc123.json"]


def test_each_attempt_is_one_row(tmp_path):
    """A 429-retried call spends quota per attempt.

    Counting logical calls would understate the day's spend and let a pass
    start that cannot finish.
    """
    now = datetime(2026, 8, 10, 12, 0, tzinfo=UTC)
    ledger = RequestLedger(tmp_path / "ledger", clock=lambda: now)
    for attempt in (1, 2, 3):  # one call, two 429s, then success
        ledger.record_attempt(
            run_id="r", model="m", case_id="p01", protocol_version=1,
            attempt=attempt, input_tokens=10, output_tokens=2,
            outcome="ok" if attempt == 3 else "error:ratelimited",
        )
    assert ledger.requests_spent_today(model="m") == 3


def test_retries_across_utc_midnight_land_on_the_right_days(tmp_path):
    """The reason rows are per-attempt rather than per-call.

    A backoff sequence can straddle midnight. Attributing the whole call to
    the day it finished would silently overstate one day's spend and
    understate the other's, and the ledger would stop agreeing with the
    provider's own dashboard — which is the only thing it is for.
    """
    clock = {"now": datetime(2026, 8, 10, 23, 59, 30, tzinfo=UTC)}
    ledger = RequestLedger(tmp_path / "ledger", clock=lambda: clock["now"])

    ledger.record_attempt(
        run_id="r", model="m", case_id="p01", protocol_version=1, attempt=1,
        input_tokens=1, output_tokens=0, outcome="error:ratelimited",
    )
    clock["now"] += timedelta(seconds=45)  # backoff crosses into the 11th
    ledger.record_attempt(
        run_id="r", model="m", case_id="p01", protocol_version=1, attempt=2,
        input_tokens=1, output_tokens=1, outcome="ok",
    )

    assert ledger.requests_spent_on("2026-08-10", model="m") == 1
    assert ledger.requests_spent_on("2026-08-11", model="m") == 1


def test_ledger_is_per_day_and_per_model(tmp_path):
    day_one = datetime(2026, 8, 10, 23, 0, tzinfo=UTC)
    clock = {"now": day_one}
    ledger = RequestLedger(tmp_path / "ledger", clock=lambda: clock["now"])
    for _ in range(2):
        ledger.record_attempt(
            run_id="r", model="lite", case_id="p01", protocol_version=1,
            attempt=1, input_tokens=1, output_tokens=1, outcome="ok",
        )
    for _ in range(5):
        ledger.record_attempt(
            run_id="r", model="other", case_id="p01", protocol_version=1,
            attempt=1, input_tokens=1, output_tokens=1, outcome="ok",
        )
    assert ledger.requests_spent_today(model="lite") == 2
    assert ledger.requests_spent_today() == 7

    clock["now"] = day_one + timedelta(hours=2)  # next UTC day
    assert ledger.requests_spent_today(model="lite") == 0
    assert ledger.requests_spent_on("2026-08-10", model="lite") == 2


def test_ledger_appends_rather_than_overwrites(tmp_path):
    now = datetime(2026, 8, 10, 12, 0, tzinfo=UTC)
    for _ in range(3):
        RequestLedger(tmp_path / "ledger", clock=lambda: now).record_attempt(
            run_id="r", model="m", case_id="p01", protocol_version=1,
            attempt=1, input_tokens=1, output_tokens=1, outcome="ok",
        )
    entries = RequestLedger(tmp_path / "ledger", clock=lambda: now).entries_on("2026-08-10")
    assert len(entries) == 3
