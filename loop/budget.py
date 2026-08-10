"""Pre-pass budgeting.

A pass that dies two-thirds through on a rate-limit error has spent the
day's quota for nothing (CLAUDE.md, cost model). So the cost is computed
*before* the pass starts, against the day's remaining quota and against the
budget the pass itself declared, and a pass that does not fit refuses to
start rather than starting hopefully.

The estimate is exact for the part that matters: every planned call is
checked against the cache, and cache hits cost zero. What it cannot know in
advance is retries — a 429-retried call spends quota per attempt. The
remaining-quota check therefore reserves headroom, and the client enforces a
hard stop when the reservation is exhausted mid-pass.
"""

from __future__ import annotations

from dataclasses import dataclass

from loop.cache import ResponseCache
from loop.config import Config
from loop.ledger import RequestLedger


class BudgetExceeded(RuntimeError):
    """The pass does not fit. Always fatal, always before any request."""


@dataclass(frozen=True)
class PlannedCall:
    case_id: str
    prompt: str
    cache_key: str


@dataclass(frozen=True)
class BudgetPlan:
    declared_budget: int
    planned_calls: int
    cache_hits: int
    requests_needed: int
    spent_today: int
    day_quota: int
    remaining_today: int
    headroom_reserved: int

    def as_manifest_fields(self) -> dict[str, int]:
        return {
            "declared_budget": self.declared_budget,
            "planned_calls": self.planned_calls,
            "cache_hits": self.cache_hits,
            "requests_needed": self.requests_needed,
            "spent_today_before_pass": self.spent_today,
            "day_quota": self.day_quota,
            "remaining_today_before_pass": self.remaining_today,
            "retry_headroom_reserved": self.headroom_reserved,
        }


def plan_budget(
    calls: list[PlannedCall],
    *,
    config: Config,
    cache: ResponseCache,
    ledger: RequestLedger,
    declared_budget: int,
    retry_headroom: float = 0.25,
) -> BudgetPlan:
    """Cost the pass and refuse it if it does not fit.

    `declared_budget` is the ceiling the pass states for itself — for M1,
    the task's 60-request limit. It is checked separately from the day's
    remaining quota so that a pass cannot quietly grow just because the
    account happens to have room.
    """
    config.require_spendable()

    cache_hits = sum(1 for call in calls if cache.has(call.cache_key))
    requests_needed = len(calls) - cache_hits

    spent_today = ledger.requests_spent_today(model=config.model)
    day_quota = config.quota.requests_per_day
    remaining_today = max(0, day_quota - spent_today)

    # Headroom exists so retries do not overrun the reservation. A flat
    # percentage is wrong for small passes: at 25%, a two-call pass reserves
    # one spare attempt, so a provider that is genuinely down trips the
    # budget stop before the retry policy has run — and the run reports
    # "out of budget" when the truth is "the provider is failing". Those
    # need to stay distinguishable, so the floor is one full retry sequence.
    headroom = 0
    if requests_needed:
        proportional = int(requests_needed * retry_headroom + 0.999)
        headroom = max(proportional, config.throttle.max_retries - 1)

    if requests_needed > declared_budget:
        raise BudgetExceeded(
            f"pass needs {requests_needed} requests but declared a budget of "
            f"{declared_budget}. Shrink the pass or raise the declared budget "
            "deliberately — do not let it drift."
        )

    if requests_needed + headroom > remaining_today:
        raise BudgetExceeded(
            f"pass needs {requests_needed} requests (+{headroom} reserved for "
            f"retries) but only {remaining_today} of today's {day_quota} remain "
            f"for {config.model}. Resume tomorrow: cached work is not re-spent."
        )

    return BudgetPlan(
        declared_budget=declared_budget,
        planned_calls=len(calls),
        cache_hits=cache_hits,
        requests_needed=requests_needed,
        spent_today=spent_today,
        day_quota=day_quota,
        remaining_today=remaining_today,
        headroom_reserved=headroom,
    )
