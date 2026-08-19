"""One-off structural fix: `decision_axes` written as a bare list instead of
a nested `{value, evidence, basis}` leaf, across group H technique blocks.

Found during M2 step 5 (2026-08-17): 13 of 23 records had this on at least
one technique. Independent subagents kept treating `decision_axes`
differently from every other technique sub-field, even after the schema
gained a full worked example (M2 step 3's fix for the same defect on
`present`/`shipped_enabled`/`evaluated`/`measured_effect`/`decision_basis` —
that fix's own example apparently was not salient enough for this one
sub-field). Not re-running extraction: the fix is purely structural, no new
fact is being read from any repository, so a script correctly reconstructs
the nesting.

Evidence and basis are borrowed from the sibling `decision_basis` field on
the same technique block: `decision_axes` is defined as "which measured
quantities the stated justification rests on", i.e. it is naming a facet
of the same justification `decision_basis` already cites evidence for.
Where `decision_basis` is not itself a dict (extremely rare, checked: does
not occur in the affected records), the fallback is empty evidence with a
basis stating why.

    uv run python tools/fix_decision_axes_nesting.py
"""

from __future__ import annotations

import pathlib

import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
RECORDS = REPO / "cases" / "records"
TECHNIQUES = ["hybrid_search", "reranking", "query_rewriting"]


def main() -> int:
    changed = 0
    for path in sorted(RECORDS.glob("p*.yaml")):
        case_id = path.stem
        text = path.read_text(encoding="utf-8")
        doc = yaml.safe_load(text)
        touched = False
        for tech in TECHNIQUES:
            block = doc["fields"].get(tech)
            if not isinstance(block, dict):
                continue
            axes = block.get("decision_axes")
            if isinstance(axes, dict):
                continue  # already correctly nested
            db = block.get("decision_basis")
            db_evidence = db.get("evidence", []) if isinstance(db, dict) else []
            if axes:
                basis = (
                    f"Quantities named in this technique's decision_basis justification: "
                    f"{', '.join(axes)}."
                )
            else:
                basis = "No measured quantities named alongside this technique's decision_basis."
            block["decision_axes"] = {
                "value": axes if isinstance(axes, list) else [],
                "evidence": list(db_evidence),
                "basis": basis,
            }
            touched = True
            print(f"{case_id} {tech}: nested decision_axes={axes!r}")
        if touched:
            new_text = yaml.safe_dump(
                doc, sort_keys=False, allow_unicode=True, default_flow_style=False, width=4096
            )
            path.write_text(new_text, encoding="utf-8")
            changed += 1

    print(f"done: {changed} record(s) fixed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
