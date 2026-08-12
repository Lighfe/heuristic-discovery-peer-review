"""M1's mini red-team round against candidate v0.

Five budgeted attempts to build a **schema-valid** record that is
**structurally bad** and still **scores well** under v0. Every attempt is
logged, including the ones that fail — the stopping claim in
`objective.md` rests on the attacks that were tried, not only on the ones
that worked, and an unlogged failure is indistinguishable from an untried
one.

**What counts as a successful attack** (`objective.md` R2): a schema-valid
record scoring in the top half of the corpus range, whose badness is stated
as a **checkable structural fact** — an existing catalogue definition, or a
new one meeting the twin taste guard. Not "this looks bad to me".

The bar used here is `>= 21`, p01's score: the attack must match the best
real project examined. With only two real records the "corpus range" is
[17, 21] and far too thin to be a range, so the stricter reading is taken
and the thinness is reported rather than hidden.

Attack records are synthetic. They live in `runs/`, never in `cases/` —
the case set is sealed evidence and inventing entries for it would be the
loop editing what judges it.

    uv run python tools/redteam_m1.py
"""

from __future__ import annotations

import copy
import json
import pathlib
import sys
from dataclasses import dataclass, field

import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "candidates" / "v0"))
from score import load_candidate, score  # noqa: E402

OUT = REPO / "runs" / "2026-08-12-m1-redteam"
BAR = 21  # p01's total; see the module docstring


@dataclass
class Attack:
    id: str
    name: str
    structural_fact: str
    catalogue_type: str
    changes: dict[str, object] = field(default_factory=dict)


ATTACKS = [
    Attack(
        id="a1",
        name="Presence-only technique maximiser",
        catalogue_type="harmful-component-kept (generalised)",
        structural_fact=(
            "All three technique components are implemented and none is on the "
            "request path; none has been evaluated; none has a measured effect. "
            "Checkable: `present: true` with `shipped_enabled: false` and "
            "`evaluated: false` for hybrid_search, reranking and query_rewriting."
        ),
        changes={
            "hybrid_search.shipped_enabled": False, "hybrid_search.evaluated": False,
            "hybrid_search.measured_effect": "not_measured",
            "reranking.shipped_enabled": False, "reranking.evaluated": False,
            "reranking.measured_effect": "not_measured",
            "query_rewriting.shipped_enabled": False, "query_rewriting.evaluated": False,
            "query_rewriting.measured_effect": "not_measured",
        },
    ),
    Attack(
        id="a2",
        name="Evaluation whose numbers have no artifact",
        catalogue_type="claim-without-artifact",
        structural_fact=(
            "Every reported figure is untraceable: no committed artifact can "
            "produce any of them. Checkable: `headline_numbers_traceable: "
            "none_traceable` with `untraceable_number_count: 40`."
        ),
        changes={
            "headline_numbers_traceable": "none_traceable",
            "untraceable_number_count": 40,
        },
    ),
    Attack(
        id="a3",
        name="Dashboard bound to nothing",
        catalogue_type="checkbox-padding",
        structural_fact=(
            "Feedback is collected and a dashboard with eight panels is "
            "committed, and every panel queries a table the application never "
            "creates, so all eight render empty forever. Checkable: "
            "`monitoring_charts_bound_to_data: none` with "
            "`monitoring_chart_count: 8`."
        ),
        changes={"monitoring_charts_bound_to_data": "none"},
    ),
    Attack(
        id="a4",
        name="Fully circular answer evaluation",
        catalogue_type="circular-eval",
        structural_fact=(
            "One model writes the questions from the passages, generates the "
            "answers, and judges them, with no sample of its verdicts checked "
            "by hand, and the reported metric sits at its maximum. Checkable: "
            "`llm_eval_role_overlap: same_model`, "
            "`llm_eval_question_generator: generator_ties_question_to_passage`, "
            "`llm_eval_judge_spotchecked: false`, "
            "`llm_eval_metric_at_ceiling: true`."
        ),
        changes={
            "llm_eval_approaches_compared": 2,
            "llm_eval_role_overlap": "same_model",
            "llm_eval_question_generator": "generator_ties_question_to_passage",
            "llm_eval_judge_spotchecked": False,
            "llm_eval_metric_at_ceiling": True,
        },
    ),
    Attack(
        id="a5",
        name="Documentation that contradicts the repository",
        catalogue_type="claim-contradicted-by-artifact (proposed type)",
        structural_fact=(
            "The written procedure names every required step and cannot be "
            "followed: nine steps fail as written, twelve documented paths do "
            "not exist, and six claims are contradicted by the committed code. "
            "Checkable: `run_instructions: complete` with "
            "`run_instructions_gap_count: 9`, `broken_reference_count: 12`, "
            "`document_code_conflicts: 6`."
        ),
        changes={
            "run_instructions_gap_count": 9,
            "broken_reference_count": 12,
            "document_code_conflicts": 6,
        },
    ),
]


def set_at(fields: dict, path: str, value) -> None:
    node = fields
    parts = path.split(".")
    for part in parts[:-1]:
        node = node[part]
    node[parts[-1]]["value"] = value
    node[parts[-1]]["evidence"] = ["<synthetic-attack>"]
    node[parts[-1]]["basis"] = "constructed for the M1 red-team round"


def main() -> int:
    base = yaml.safe_load((REPO / "cases" / "records" / "p01.yaml").read_text(encoding="utf-8"))
    candidate = load_candidate()
    baseline = score(base, candidate)
    OUT.mkdir(parents=True, exist_ok=True)

    results = []
    for attack in ATTACKS:
        record = copy.deepcopy(base)
        record["case_id"] = f"attack-{attack.id}"
        record.pop("extraction_notes", None)
        for path, value in attack.changes.items():
            set_at(record["fields"], path, value)
        result = score(record, candidate)
        succeeded = result.total >= BAR
        results.append({
            "id": attack.id, "name": attack.name,
            "catalogue_type": attack.catalogue_type,
            "structural_fact": attack.structural_fact,
            "fields_changed": list(attack.changes),
            "total": result.total, "bar": BAR, "succeeded": succeeded,
            "certifies": result.certifies,
            "delta_vs_p01": result.total - baseline.total,
        })
        (OUT / f"attack-{attack.id}.yaml").write_text(
            yaml.safe_dump(record, sort_keys=False, allow_unicode=True), encoding="utf-8")

    report = {
        "run_id": "2026-08-12-m1-redteam",
        "candidate": candidate["candidate"],
        "attempts": len(ATTACKS),
        "bar": BAR,
        "bar_rationale": ("p01's total. The corpus range is [17, 21] over two "
                          "records, too thin to be a range, so the stricter "
                          "reading is used and the thinness is reported."),
        "baseline_p01": baseline.total,
        "successful": sum(1 for r in results if r["succeeded"]),
        "failed": sum(1 for r in results if not r["succeeded"]),
        "requests_spent": 0,
        "attacks": results,
    }
    (OUT / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    print(f"candidate {candidate['candidate']}   p01 baseline {baseline.total}   bar >= {BAR}\n")
    for r in results:
        mark = "SUCCESS" if r["succeeded"] else "failed "
        print(f"  {mark}  {r['id']}  {r['name'][:44]:<44} scored {r['total']:>3} "
              f"({r['delta_vs_p01']:+d} vs p01)  certifies={r['certifies']}")
    print(f"\n{report['successful']} of {report['attempts']} attacks succeeded. "
          f"runs/{report['run_id']}/report.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
