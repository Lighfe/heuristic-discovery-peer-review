"""The per-day request ledger.

The binding constraint is requests per day, so the runner has to know how
many it has already spent *today* before it starts a pass — including
requests spent by earlier passes, in earlier sessions, possibly days ago.
That state cannot live in memory.

One append-only JSONL file per UTC date under `runs/ledger/`. Committed:
the ledger is what makes "this pass cost N requests" a checkable claim
rather than a prose summary, and it names no person — only project ids.

Cache hits are deliberately NOT recorded. The ledger answers one question,
"how much quota is gone", and a hit spends none.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path


@dataclass(frozen=True)
class LedgerEntry:
    """One provider attempt.

    Deliberately per *attempt*, not per logical call. A 429-retried call
    spends quota once per attempt, so an aggregate row would already have to
    carry a count — and worse, a retry sequence straddling UTC midnight
    would land its whole count in one day's file when the attempts really
    hit the provider on two. At full-corpus scale that drift is what makes
    the ledger disagree with Google's own dashboard. One row per attempt,
    stamped when the attempt was made, is exact by construction.
    """

    at: str  # ISO-8601 UTC, stamped at the attempt
    run_id: str
    model: str
    case_id: str
    protocol_version: int
    attempt: int  # 1-based ordinal within this logical call
    input_tokens: int
    output_tokens: int
    outcome: str  # "ok" | "error:<kind>"


def utc_now() -> datetime:
    return datetime.now(UTC)


class RequestLedger:
    """Append-only accounting of requests that actually reached the provider."""

    def __init__(self, root: Path, *, clock=utc_now) -> None:
        self.root = root
        self._clock = clock

    def _path_for(self, day: str) -> Path:
        return self.root / f"{day}.jsonl"

    def today(self) -> str:
        return self._clock().date().isoformat()

    def record_attempt(
        self,
        *,
        run_id: str,
        model: str,
        case_id: str,
        protocol_version: int,
        attempt: int,
        input_tokens: int,
        output_tokens: int,
        outcome: str,
    ) -> LedgerEntry:
        """Append one attempt, stamped now. Call this as the attempt returns."""
        now = self._clock()
        entry = LedgerEntry(
            at=now.isoformat(),
            run_id=run_id,
            model=model,
            case_id=case_id,
            protocol_version=protocol_version,
            attempt=attempt,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            outcome=outcome,
        )
        path = self._path_for(now.date().isoformat())
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(asdict(entry), sort_keys=True) + "\n")
        return entry

    def entries_on(self, day: str) -> list[LedgerEntry]:
        path = self._path_for(day)
        if not path.exists():
            return []
        entries = []
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                entries.append(LedgerEntry(**json.loads(line)))
        return entries

    def requests_spent_on(self, day: str, *, model: str | None = None) -> int:
        """Provider requests spent on `day`.

        One row is one attempt, so this is a row count. A call retried three
        times through a 429 backoff consumed three requests of quota, not
        one, and each is dated where it actually happened.
        """
        return sum(
            1
            for entry in self.entries_on(day)
            if model is None or entry.model == model
        )

    def requests_spent_today(self, *, model: str | None = None) -> int:
        return self.requests_spent_on(self.today(), model=model)
