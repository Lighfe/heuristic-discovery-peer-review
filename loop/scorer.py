"""The scorer harness: run a candidate over every case and check gate G1.

Free and deterministic — no model calls — which is what makes this runnable
as often as anyone likes. Every number M1 reports about the twins comes from
here, recomputed from the artifacts on each run rather than carried forward
in prose.

What it does:

  * scores every record and every twin under a candidate's executable layer;
  * evaluates each twin's **direction claim** — the twin states, at build
    time, whether it must score strictly below, exactly equal to, or not
    below its comparison case, and this checks that claim rather than
    re-deriving it;
  * separates a twin that failed because a criterion *moved the wrong way*
    from one that failed because **no criterion reads the mutated field at
    all**, which are different findings and read identically in a totals
    table;
  * writes `runs/<run-id>/` with the per-case scores, the G1 verdict, and a
    manifest naming the candidate, the cases and the code that produced it.

    uv run python -m loop.scorer
    uv run python -m loop.scorer --candidate candidates/v0/criteria.yaml
"""

from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import UTC, datetime

import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
RECORDS = REPO / "cases" / "records"
TWINS = REPO / "cases" / "twins"
RUNS = REPO / "runs"

sys.path.insert(0, str(REPO / "candidates" / "v0"))
from score import ScoreResult, load_candidate, score  # noqa: E402

RELATIONS = {
    "strictly_below": lambda d: d < 0,
    "exactly_equal": lambda d: d == 0,
    "not_below": lambda d: d >= 0,
}


@dataclass
class TwinVerdict:
    twin_id: str
    twin_type: str
    against: str
    relation: str
    base_total: int
    twin_total: int
    delta: int
    passed: bool
    mutated_fields: list[str]
    fields_no_criterion_reads: list[str]
    criteria_that_moved: list[str]
    diagnosis: str


def diagnose(passed: bool, unread: list[str], mutated: list[str], moved: list[str]) -> str:
    """Why this twin got the result it did — the part a totals table hides."""
    if passed:
        if not moved and unread == mutated:
            return ("passes because nothing moved and nothing was supposed to: "
                    "no criterion reads any mutated field, which is what a "
                    "no-change twin requires")
        return "passes: the candidate ordered this pair as the construction requires"
    if unread == mutated:
        return ("FAILS because no criterion reads any mutated field. The "
                "candidate is structurally blind to this defect - it cannot "
                "score what it never looks at. This is a finding about the "
                "criteria, not a scoring bug")
    if not moved:
        return ("FAILS although a criterion does read a mutated field: the "
                "field is read but the change did not cross a tier boundary. "
                "Coarse tiering, not blindness")
    return ("FAILS: criteria moved, but not far enough or not in the "
            "direction the construction requires")


def run(candidate_path: pathlib.Path, run_id: str | None = None) -> dict:
    candidate = load_candidate(candidate_path)
    reads = {s["id"]: set(s.get("reads", [])) for s in candidate["criteria"]}
    all_read = {f for fields in reads.values() for f in fields}

    cases: dict[str, dict] = {}
    for path in sorted(RECORDS.glob("*.yaml")) + sorted(TWINS.glob("*.yaml")):
        cases[path.stem] = yaml.safe_load(path.read_text(encoding="utf-8"))

    scores: dict[str, ScoreResult] = {k: score(v, candidate) for k, v in cases.items()}
    points = {k: {c.criterion_id: c.points for c in r.criteria} for k, r in scores.items()}

    verdicts: list[TwinVerdict] = []
    for name, doc in cases.items():
        meta = doc.get("twin")
        if not meta:
            continue
        against = meta["comparison"]["against"]
        relation = meta["comparison"]["relation"]
        mutated = [e["field"].removeprefix("fields.").removesuffix(".value") for e in meta["diff"]]
        unread = [f for f in mutated if f not in all_read]
        moved = [c for c in points[name] if points[name][c] != points[against][c]]
        delta = scores[name].total - scores[against].total
        passed = RELATIONS[relation](delta)
        verdicts.append(TwinVerdict(
            twin_id=name, twin_type=meta["type"], against=against, relation=relation,
            base_total=scores[against].total, twin_total=scores[name].total, delta=delta,
            passed=passed, mutated_fields=mutated, fields_no_criterion_reads=unread,
            criteria_that_moved=moved,
            diagnosis=diagnose(passed, unread, mutated, moved),
        ))

    records_only = [k for k in cases if "twin" not in cases[k]]
    certifying = [k for k in records_only if scores[k].certifies]

    run_id = run_id or datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ") + "-scorer"
    result = {
        "run_id": run_id,
        "kind": "scorer",
        "written_at": datetime.now(UTC).isoformat(),
        "candidate": {
            "name": candidate["candidate"],
            "path": str(candidate_path.relative_to(REPO)),
            "source": candidate["source"],
            "source_lines": candidate["source_lines"],
            "pass_threshold": candidate["pass_threshold"],
        },
        "code_revision": subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=REPO, capture_output=True, text=True
        ).stdout.strip() or None,
        "requests_spent": 0,  # the executable layer never calls a model
        "counts": {
            "records": len(records_only),
            "twins": len(verdicts),
            "records_certifying": len(certifying),
            "twins_passing": sum(1 for v in verdicts if v.passed),
            "twins_failing": sum(1 for v in verdicts if not v.passed),
        },
        "g1": {
            "passed": all(v.passed for v in verdicts),
            "failing_twins": [v.twin_id for v in verdicts if not v.passed],
            "scope": ("G1 is claimed as discrimination of the CATALOGUED failure "
                      "modes only, never as general discrimination (decision "
                      "`g1-claims-catalogue-coverage`)"),
        },
        "scores": {
            k: {
                "total": r.total, "max_total": r.max_total, "certifies": r.certifies,
                "unscoreable_headroom": r.unscoreable_headroom,
                "unmatched_criteria": r.unmatched,
                "per_criterion": points[k],
            } for k, r in scores.items()
        },
        "twin_verdicts": [asdict(v) for v in verdicts],
    }

    out = RUNS / run_id
    out.mkdir(parents=True, exist_ok=True)
    (out / "manifest.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    return result


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--candidate", default="candidates/v0/criteria.yaml")
    ap.add_argument("--run-id", default=None)
    args = ap.parse_args(argv)

    result = run(REPO / args.candidate, args.run_id)
    c = result["counts"]
    print(f"run {result['run_id']}  candidate {result['candidate']['name']}  "
          f"threshold {result['candidate']['pass_threshold']}  requests 0")
    print(f"  {c['records']} records, {c['records_certifying']} certifying")
    print(f"  {c['twins']} twins: {c['twins_passing']} pass, {c['twins_failing']} fail\n")
    for v in result["twin_verdicts"]:
        mark = "PASS" if v["passed"] else "FAIL"
        print(f"  {mark}  {v['twin_id']}  {v['twin_type'][:38]:<38} "
              f"{v['base_total']}->{v['twin_total']} ({v['delta']:+d}) need {v['relation']}")
        print(f"        {v['diagnosis']}")
    print(f"\nG1 over this case set: {'PASS' if result['g1']['passed'] else 'FAIL'}"
          f"  failing: {', '.join(result['g1']['failing_twins']) or 'none'}")
    print(f"manifest: runs/{result['run_id']}/manifest.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
