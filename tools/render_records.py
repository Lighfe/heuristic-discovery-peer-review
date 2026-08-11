"""Render evidence records as readable Markdown.

The YAML records are the artifact — machine-read by the scorer, diffable,
and the thing every claim cites. They are also close to unreadable for a
person, and `extraction_notes` in particular are long prose wrapped in YAML
quoting, which is where the schema's real limits get reported.

So each record gets a generated `.md` companion. Generated, never authored:
regenerating is the only way to change it, so the two cannot drift.

    uv run python tools/render_records.py

Writes `cases/records/<case>.md` for every `cases/records/<case>.yaml`.
"""

from __future__ import annotations

import pathlib
import sys

import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
RECORDS = REPO / "cases" / "records"

# Field groups, in schema order. Anything not listed lands in "Ungrouped",
# which is itself a signal that this file has fallen behind the schema.
GROUPS = [
    ("A. System shape", ["knowledge_base_present", "llm_in_flow", "retrieval_flow", "problem_statement"]),
    ("B. Interface", ["interface_kind", "interface_evidence_kind"]),
    ("C. Ingestion", ["ingestion_kind", "ingestion_single_command", "ingestion_output_stated"]),
    ("D. Retrieval evaluation", [
        "retrieval_eval_present", "retrieval_eval_approaches_compared",
        "retrieval_eval_set_committed", "retrieval_eval_set_size",
        "retrieval_eval_relevance_rule", "retrieval_eval_config_matches_shipped",
        "retrieval_eval_uncertainty_stated", "retrieval_best_approach_shipped"]),
    ("E. Answer evaluation", [
        "llm_eval_present", "llm_eval_approaches_compared", "llm_eval_judge_kind",
        "llm_eval_judge_spotchecked", "llm_eval_question_generator",
        "llm_eval_metric_at_ceiling", "llm_eval_role_overlap",
        "llm_eval_config_matches_shipped"]),
    ("F. Monitoring", [
        "monitoring_kind", "monitoring_dashboard_provenance",
        "monitoring_instrumentation", "monitoring_chart_count",
        "monitoring_charts_bound_to_data"]),
    ("G. Containerization and reproducibility", [
        "containerization_kind", "run_instructions", "run_instructions_gap_count",
        "dependency_versions_pinned", "data_accessible"]),
    ("H. Techniques", ["hybrid_search", "reranking", "query_rewriting"]),
    ("I. Deployment", ["cloud_deployment"]),
    ("J. Documentation accuracy", [
        "headline_numbers_traceable", "untraceable_number_count",
        "document_number_conflicts", "document_code_conflicts",
        "broken_reference_count", "limitations_section",
        "artifact_reference_strength", "artifacts_unreferenced_count"]),
    ("K. Descriptive (no criterion reads these)", [
        "corpus_language", "corpus_domain", "interface_framework",
        "vector_store", "llm_provider", "repo_file_count"]),
]


def fmt(value) -> str:
    if value is None:
        return "`null`"
    if isinstance(value, bool):
        return f"`{str(value).lower()}`"
    if isinstance(value, list):
        return ", ".join(f"`{v}`" for v in value) if value else "*(empty)*"
    return f"`{value}`"


def render_leaf(name: str, node: dict, out: list[str], indent: str = "") -> None:
    out.append(f"{indent}**`{name}`** = {fmt(node.get('value'))}")
    if node.get("basis"):
        out.append(f"{indent}: {node['basis']}")
    ev = node.get("evidence") or []
    if ev:
        out.append(f"{indent}: *evidence:* " + " · ".join(f"`{e}`" for e in ev))
    out.append("")


def render(path: pathlib.Path) -> pathlib.Path:
    doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    fields = doc["fields"]
    case = doc["case_id"]

    out = [
        f"# Evidence record — {case}",
        "",
        "*Generated from the YAML record by `tools/render_records.py`. Do not edit:",
        f"regenerate instead. Source of truth is `cases/records/{case}.yaml`.*",
        "",
        f"- **case:** `{case}`",
        f"- **commit:** `{doc['commit']}`",
        f"- **schema version:** `{doc['schema_version']}`",
        f"- **extracted by:** `{doc['extracted_by']}` on {doc['extracted_on']}",
        "",
    ]

    seen: set[str] = set()
    for title, names in GROUPS:
        present = [n for n in names if n in fields]
        if not present:
            continue
        out += [f"## {title}", ""]
        for name in present:
            seen.add(name)
            node = fields[name]
            if "value" in node:
                render_leaf(name, node, out)
            else:  # technique block
                out += [f"### `{name}`", ""]
                for sub, subnode in node.items():
                    render_leaf(sub, subnode, out, indent="")
    leftover = [n for n in fields if n not in seen]
    if leftover:
        out += ["## Ungrouped — this renderer is behind the schema", ""]
        for name in leftover:
            node = fields[name]
            if "value" in node:
                render_leaf(name, node, out)

    notes = doc.get("extraction_notes") or []
    out += [
        "---",
        "",
        "## Extraction notes",
        "",
        "*What the schema could not express about this repository. This is the",
        "part of a record worth reading: field values say what fits, these say",
        "what does not — and they are the input to any schema proposal.*",
        "",
        f"**{len(notes)} notes.**",
        "",
    ]
    for i, note in enumerate(notes, 1):
        out += [f"### {i}.", "", note.strip(), ""]

    dest = path.with_suffix(".md")
    dest.write_text("\n".join(out), encoding="utf-8")
    return dest


def main() -> int:
    records = sorted(RECORDS.glob("*.yaml"))
    if not records:
        print(f"no records under {RECORDS}", file=sys.stderr)
        return 1
    for path in records:
        dest = render(path)
        print(f"{path.name} -> {dest.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
