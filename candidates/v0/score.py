"""The executable layer: score an evidence record under a candidate.

Deterministic plain Python over extracted records. No model calls, so twin
tests and the adoption check cost zero requests and can be re-run freely —
which is what makes iteration possible at 500 requests a day.

The scorer is deliberately dumb. All the judgment lives in the candidate's
`criteria.yaml`, where it can be diffed against the guidance text by someone
who has never read this file; anything clever here would be a rule that a
reviewer of the transcription could not see. So this module only:

  * walks each criterion's tiers top-down and takes the first match,
  * reports `unmatched` when no tier fires, rather than defaulting silently,
  * sums, and compares against the candidate's stated pass threshold.

    uv run python candidates/v0/score.py                  # all records + twins
    uv run python candidates/v0/score.py p01 p01-t01      # named cases
"""

from __future__ import annotations

import pathlib
import sys
from dataclasses import dataclass, field
from typing import Any

import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent.parent
CRITERIA = pathlib.Path(__file__).resolve().parent / "criteria.yaml"
RECORDS = REPO / "cases" / "records"
TWINS = REPO / "cases" / "twins"


class MappingError(RuntimeError):
    """The candidate's mapping is malformed. Never defaulted around."""


# --------------------------------------------------------------------------
# Condition evaluation
# --------------------------------------------------------------------------


def read_field(fields: dict, path: str) -> Any:
    """`monitoring_kind` or `reranking.present` -> that field's `value`."""
    node: Any = fields
    for part in path.split("."):
        if not isinstance(node, dict) or part not in node:
            raise MappingError(f"criteria.yaml reads {path!r}, absent from the record")
        node = node[part]
    if not isinstance(node, dict) or "value" not in node:
        raise MappingError(f"criteria.yaml reads {path!r}, which is not a leaf field")
    return node["value"]


def satisfies(actual: Any, expected: Any) -> bool:
    """One condition. Every key in a `when` block must satisfy (AND)."""
    if isinstance(expected, dict):
        if "in" in expected:
            # A list-valued field (e.g. `interface_kind` since M2, schema
            # item 7) matches "in" if ANY element is a member — a project
            # with two interfaces should satisfy a criterion either one
            # alone would satisfy. A scalar field keeps exact membership.
            if isinstance(actual, list):
                return any(a in expected["in"] for a in actual)
            return actual in expected["in"]
        for op in (">=", ">", "<=", "<"):
            if op in expected:
                # null never satisfies a numeric comparison: "at least 5
                # charts" is false when no chart can be counted, and treating
                # null as 0 would conflate "none committed" with "not
                # applicable" (see criteria.yaml, monitoring).
                if not isinstance(actual, int) or isinstance(actual, bool):
                    return False
                bound = expected[op]
                return {
                    ">=": actual >= bound, ">": actual > bound,
                    "<=": actual <= bound, "<": actual < bound,
                }[op]
        raise MappingError(f"unknown condition {expected!r}")
    # Same list-aware rule as "in" above, for bare equality against a
    # list-valued field (e.g. `{interface_kind: none}` against `["none"]`).
    if isinstance(actual, list):
        return expected in actual
    return actual == expected


# --------------------------------------------------------------------------
# Scoring
# --------------------------------------------------------------------------


@dataclass
class CriterionResult:
    criterion_id: str
    points: int
    max_points: int
    matched_tier: str | None      # the tier's `text`, or None
    unmatched: bool               # no tier fired; `fallback` was used
    unscoreable: bool             # the criterion cannot be executed at all


@dataclass
class ScoreResult:
    case_id: str
    total: int
    max_total: int
    certifies: bool
    pass_threshold: int
    criteria: list[CriterionResult] = field(default_factory=list)

    @property
    def unmatched(self) -> list[str]:
        return [c.criterion_id for c in self.criteria if c.unmatched]

    @property
    def unscoreable_headroom(self) -> int:
        """Points no executable layer can award. v0's total is a lower bound."""
        return sum(c.max_points for c in self.criteria if c.unscoreable)


def load_candidate(path: pathlib.Path = CRITERIA) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def score(record: dict, candidate: dict) -> ScoreResult:
    fields = record["fields"]
    threshold = int(candidate["pass_threshold"])
    result = ScoreResult(
        case_id=record["case_id"], total=0, max_total=0,
        certifies=False, pass_threshold=threshold,
    )

    for spec in candidate["criteria"]:
        max_points = int(spec["max_points"])
        result.max_total += max_points

        if spec.get("unscoreable"):
            result.criteria.append(CriterionResult(
                spec["id"], int(spec.get("fallback", 0)), max_points,
                matched_tier=None, unmatched=False, unscoreable=True,
            ))
            result.total += int(spec.get("fallback", 0))
            continue

        points, matched = None, None
        for tier in spec.get("tiers", []):
            if all(satisfies(read_field(fields, f), v) for f, v in tier["when"].items()):
                points, matched = int(tier["points"]), tier["text"]
                break

        unmatched = points is None
        if unmatched:
            if "fallback" not in spec:
                raise MappingError(f"{spec['id']}: no tier matched and no fallback declared")
            points = int(spec["fallback"])

        result.total += points
        result.criteria.append(CriterionResult(
            spec["id"], points, max_points, matched, unmatched, unscoreable=False,
        ))

    result.certifies = result.total >= threshold
    return result


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------


def load_cases(names: list[str]) -> dict[str, dict]:
    paths = sorted(RECORDS.glob("*.yaml")) + sorted(TWINS.glob("*.yaml"))
    cases = {p.stem: yaml.safe_load(p.read_text(encoding="utf-8")) for p in paths}
    if not names:
        return cases
    missing = [n for n in names if n not in cases]
    if missing:
        raise SystemExit(f"unknown case(s): {', '.join(missing)}")
    return {n: cases[n] for n in names}


def main(argv: list[str]) -> int:
    candidate = load_candidate()
    cases = load_cases(argv)

    print(f"candidate {candidate['candidate']} — {candidate['source']} lines {candidate['source_lines']}")
    print(f"pass threshold {candidate['pass_threshold']}\n")
    print(f"{'case':<10} {'total':>6} {'/max':>5} {'certifies':>10}   unmatched criteria")
    for name, record in cases.items():
        r = score(record, candidate)
        flag = "yes" if r.certifies else "NO"
        print(f"{name:<10} {r.total:>6} {r.max_total:>5} {flag:>10}   {', '.join(r.unmatched) or '-'}")

    first = score(next(iter(cases.values())), candidate)
    print(f"\nmaximum executable score {first.max_total - first.unscoreable_headroom}"
          f" of {first.max_total}; {first.unscoreable_headroom} points are"
          f" unscoreable by any executable layer, so every total here is a LOWER"
          f" BOUND on what a human reviewer could award.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
