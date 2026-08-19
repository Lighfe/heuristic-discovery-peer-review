"""Generate known-direction twins of the evidence records.

This project has no labelled corpus and will never get one, so validity has to
come from pairs whose direction is known *by construction*: a record, and a
mutation of it that any defensible criterion must score strictly lower (or
exactly the same). Nobody grades anything; the sign of the difference is a
property of how the twin was built.

That only holds if the twins are built mechanically. A twin written by hand is
a twin whose author can quietly encode taste, and a twin regenerated with a
different value next week is not a measurement. So: plain Python, no model
calls, no randomness, byte-identical output on every run.

Two rules the generator enforces rather than trusts, because breaking either
one makes the whole gate meaningless:

  * degraded twins mutate `scoreable` fields only;
  * no-change twins mutate `descriptive` fields only.

`cases/schema.md` marks every field with one or the other; FIELD_SPEC below is
that marking transcribed, and it is also the legality check on every mutated
value.

    uv run python tools/generate_twins.py

Writes `cases/twins/<twin_id>.yaml`, one complete record per twin (base fields
with the mutation applied) plus a `twin` metadata block carrying the diff. A
scorer therefore loads a twin exactly as it loads a record, and the diff stays
auditable without re-deriving it.
"""

from __future__ import annotations

import copy
import dataclasses
import pathlib
import sys
from typing import Any

import yaml

# Every legality and entailment check in this file is a plain `assert`.
# Running under `python -O` / `PYTHONOPTIMIZE` strips all of them silently,
# and `main()`'s "all assertions passed" print is not gated on anything, so
# a stripped run would print success while checking nothing. Checked
# 2026-08-17: no `-O` flag or `PYTHONOPTIMIZE` appears anywhere in this
# repo's pyproject.toml, uv.lock, or any Makefile/CI config, and `uv run`
# does not set it by default. Fail loudly rather than silently if that
# ever changes.
if sys.flags.optimize:
    raise SystemExit(
        "generate_twins.py: refusing to run under python -O / PYTHONOPTIMIZE — "
        "every legality and entailment check in this file is a bare assert, "
        "and optimized mode strips them all silently."
    )

REPO = pathlib.Path(__file__).resolve().parent.parent
RECORDS = REPO / "cases" / "records"
TWINS = REPO / "cases" / "twins"

# Evidence locator written onto any field whose value this generator changed.
# The value is constructed, so pointing a human re-verifier at the base
# record's real locators would send them to files that say the opposite.
SYNTHETIC = "<synthetic>"


# --------------------------------------------------------------------------
# The schema, transcribed. `cases/schema.md` is the source of truth; this is
# the machine-checkable shadow of it, and it exists so that "every mutated
# value is legal" and "no twin crossed the read-set line" are assertions
# rather than intentions.
# --------------------------------------------------------------------------

SCOREABLE = "scoreable"
DESCRIPTIVE = "descriptive"

# field name -> (read_set, kind, allowed)
#   kind "enum": allowed is the member list
#   kind "list_enum": allowed is the member list, value is a list of members
#   kind "int" / "int_or_null" / "bool" / "bool_or_null" / "str" / "list_str": allowed is None
FIELD_SPEC: dict[str, tuple[str, str, list[str] | None]] = {
    # A. System shape
    "knowledge_base_present": (SCOREABLE, "enum", ["absent", "present"]),
    "llm_in_flow": (SCOREABLE, "enum", ["absent", "present"]),
    "retrieval_flow": (SCOREABLE, "enum", ["no_kb_no_llm", "llm_only", "kb_and_llm"]),
    "problem_statement": (SCOREABLE, "enum", ["absent", "brief", "specific"]),
    # B. Interface
    "interface_kind": (SCOREABLE, "list_enum", ["none", "script_or_notebook", "cli", "api", "web_ui", "other"]),
    "interface_evidence_kind": (SCOREABLE, "enum", ["none", "code_only", "code_and_screenshot", "code_and_recording"]),
    # C. Ingestion
    "ingestion_kind": (SCOREABLE, "enum", ["none", "manual", "script_or_notebook", "orchestrated_tool", "other"]),
    "ingestion_single_command": (SCOREABLE, "bool", None),
    "ingestion_output_stated": (SCOREABLE, "bool", None),
    # D. Retrieval evaluation
    "retrieval_eval_present": (SCOREABLE, "bool", None),
    "retrieval_eval_approaches_compared": (SCOREABLE, "int", None),
    "retrieval_eval_set_committed": (SCOREABLE, "enum", ["absent", "referenced_not_committed", "committed"]),
    "retrieval_eval_set_size": (SCOREABLE, "int_or_null", None),
    "retrieval_eval_match_strictness": (SCOREABLE, "enum", [
        "none", "source_level", "document_level", "passage_level", "other", "undeterminable"]),
    "retrieval_eval_label_origin": (SCOREABLE, "enum", [
        "none", "human_labelled", "generated", "mixed", "other", "undeterminable"]),
    "retrieval_eval_config_matches_shipped": (SCOREABLE, "enum", ["matches", "differs", "undeterminable"]),
    "retrieval_eval_uncertainty_stated": (SCOREABLE, "bool", None),
    "retrieval_best_approach_shipped": (SCOREABLE, "enum", ["yes", "no", "mixed_result", "undeterminable"]),
    "retrieval_eval_reproducible": (SCOREABLE, "enum", [
        "reproducible_as_committed", "traceable_not_reproducible", "neither"]),
    # E. Answer evaluation
    "llm_eval_present": (SCOREABLE, "bool", None),
    "llm_eval_approaches_compared": (SCOREABLE, "int", None),
    "llm_eval_judge_kind": (SCOREABLE, "enum", ["none", "model_judge", "human", "offline_metric", "other"]),
    "llm_eval_judge_spotchecked": (SCOREABLE, "bool", None),
    "llm_eval_question_generator": (SCOREABLE, "enum", [
        "none_committed", "generator_committed", "generator_ties_question_to_passage", "other", "undeterminable"]),
    "llm_eval_metric_at_ceiling": (SCOREABLE, "bool_or_null", None),
    "llm_eval_role_overlap": (SCOREABLE, "enum", ["distinct", "same_family", "same_model", "undeterminable"]),
    "llm_eval_config_matches_shipped": (SCOREABLE, "enum", ["matches", "differs", "undeterminable"]),
    "llm_eval_reproducible": (SCOREABLE, "enum", [
        "reproducible_as_committed", "traceable_not_reproducible", "neither"]),
    # F. Monitoring
    "monitoring_kind": (SCOREABLE, "enum", [
        "none", "feedback_only", "dashboard_only", "feedback_and_dashboard", "other"]),
    "monitoring_dashboard_provenance": (SCOREABLE, "enum", ["none", "committed_definitions", "stock_tool_ui", "other"]),
    "monitoring_instrumentation": (SCOREABLE, "enum", ["none", "logged", "traced_on_request_path"]),
    "monitoring_chart_count": (SCOREABLE, "int_or_null", None),
    "monitoring_charts_bound_to_data": (SCOREABLE, "enum", ["none", "some", "all", "not_applicable"]),
    # G. Containerization and reproducibility
    "containerization_kind": (SCOREABLE, "enum", [
        "none", "dockerfile_only", "compose_dependencies_only", "compose_full", "other"]),
    "run_instructions": (SCOREABLE, "enum", ["none", "partial", "complete"]),
    "run_instructions_gap_count": (SCOREABLE, "int", None),
    "dependency_versions_pinned": (SCOREABLE, "enum", [
        "none", "lower_bounds_only", "lockfile_committed", "exact_pins", "other"]),
    "data_accessible": (SCOREABLE, "enum", ["missing", "manual_steps", "automated_or_committed", "other"]),
    # I. Deployment and bonus
    "cloud_deployment": (SCOREABLE, "enum", ["none", "documented_only", "deployment_code_committed", "other"]),
    # J. Documentation accuracy
    "headline_numbers_traceable": (SCOREABLE, "enum", [
        "no_numbers", "none_traceable", "some_traceable", "all_traceable"]),
    "untraceable_number_count": (SCOREABLE, "int", None),
    "document_number_conflicts": (SCOREABLE, "int", None),
    "document_code_conflicts": (SCOREABLE, "int", None),
    "broken_reference_count": (SCOREABLE, "int", None),
    "limitations_section": (SCOREABLE, "enum", ["absent", "cosmetic_only", "includes_structural"]),
    "artifact_reference_strength": (SCOREABLE, "enum", [
        "all_linked", "all_referenced", "partially_referenced", "none"]),
    "artifacts_unreferenced_count": (SCOREABLE, "int", None),
    # K. Descriptive
    "corpus_language": (DESCRIPTIVE, "str", None),
    "corpus_domain": (DESCRIPTIVE, "str", None),
    "interface_framework": (DESCRIPTIVE, "str", None),
    "vector_store": (DESCRIPTIVE, "str", None),
    "llm_provider": (DESCRIPTIVE, "str", None),
    "repo_file_count": (DESCRIPTIVE, "int", None),
    "project_name": (DESCRIPTIVE, "str", None),
}

# H. Techniques — one block per technique, same sub-fields, all scoreable.
TECHNIQUES = ["hybrid_search", "reranking", "query_rewriting"]
TECHNIQUE_SPEC: dict[str, tuple[str, str, list[str] | None]] = {
    "present": (SCOREABLE, "bool", None),
    "shipped_enabled": (SCOREABLE, "bool", None),
    "evaluated": (SCOREABLE, "bool", None),
    "measured_effect": (SCOREABLE, "enum", ["improves", "mixed", "hurts", "not_measured"]),
    "decision_basis": (SCOREABLE, "enum", ["none", "argued", "measured"]),
    "decision_axes": (SCOREABLE, "list_str", None),
}

# Legal on every enum field, per the schema's "`undeterminable` and `other`
# are different answers" section.
ENUM_UNIVERSAL = ["undeterminable", "other"]


# --------------------------------------------------------------------------
# Twin specifications
# --------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class Change:
    """One mutated `value`, with the reason its direction is forced.

    `entailed_by` names another changed path when this change is not an
    independent second defect but a value the first one makes arithmetically
    false. See `APPROVED_ENTAILMENTS` for why that needs naming rather than
    explaining in prose.
    """

    path: str
    after: Any
    justification: str
    entailed_by: str | None = None


# Entailed second changes the owner has approved, keyed by twin, each mapping
# the entailed field to the change that forces it.
#
# The epistemics rule is that a twin "differs in exactly one way whose
# direction is known because it was constructed that way". Owner ruling at
# the M1 twin gate: "one way" means one *fact*, so a field the first change
# makes factually false is the same fact recorded twice rather than a second
# defect — **but the allowance is scoped to this specific pair and is not a
# standing rule any future twin-builder may self-invoke by analogy.**
#
# This table is that scoping made mechanical. Without it "entailed" becomes
# the label under which genuinely multi-defect twins pass review, and a twin
# carrying two independent changes cannot support a direction claim about
# either. An entailment not listed here fails the build.
#
# Adding an entry is an owner decision, not a maintenance task.
APPROVED_ENTAILMENTS: dict[str, dict[str, str]] = {
    "p01-t01": {
        "fields.retrieval_best_approach_shipped.value": "fields.reranking.measured_effect.value",
    },
    "p01-t02": {
        "fields.retrieval_best_approach_shipped.value": "fields.reranking.measured_effect.value",
    },
    "p04-t01": {
        "fields.headline_numbers_traceable.value": "fields.untraceable_number_count.value",
    },
}


@dataclasses.dataclass(frozen=True)
class Restate:
    """Prose or locators rewritten so the twin does not contradict itself.

    `basis` is read by prose reviewers and `evidence` by human auditors, so a
    mutated value whose basis still describes the base record is an incoherent
    twin. These carry no direction claim of their own; they are bookkeeping,
    kept separate from `Change` so the load-bearing diff stays legible.
    """

    path: str
    after: Any


@dataclasses.dataclass(frozen=True)
class TwinSpec:
    twin_id: str
    base_case_id: str
    twin_type: str
    direction: str  # down | zero | not_below_base
    against: str  # twin_id or case_id this twin's direction is claimed against
    relation: str  # strictly_below | exactly_equal | not_below
    summary: str
    changes: tuple[Change, ...]
    restates: tuple[Restate, ...] = ()
    note: str | None = None


# Reported retrieval numbers used by the harmful-component twins. The base
# record states hybrid alone as 15/37/52/0.39 and hybrid+re-ranker as
# 19/44/48/0.36 (metrics disagree, hence `mixed`). The twins replace the
# second row with one that trails on every column, which is what turns the
# same shipping decision into a measured-to-hurt one.
RERANK_HURTS_BASIS = (
    "Read off the project's own reported numbers: adding the re-ranker lowers every reported column - "
    "Hit Rate@1 (15% to 11%), @3 (37% to 30%), @5 (52% to 44%) and MRR@10 (0.39 to 0.31)."
)

SPECS: tuple[TwinSpec, ...] = (
    TwinSpec(
        twin_id="p01-t01",
        base_case_id="p01",
        twin_type="harmful-component-kept",
        direction="down",
        against="p01",
        relation="strictly_below",
        summary=(
            "The re-ranker's own reported numbers trail hybrid alone on every metric, and it ships enabled "
            "anyway."
        ),
        changes=(
            Change(
                path="fields.reranking.measured_effect.value",
                after="hurts",
                justification=(
                    "In the base the component's own metrics disagree about it (`mixed`); here they agree it "
                    "degrades retrieval, while `shipped_enabled` stays true. Same shipping decision, strictly "
                    "more of the project's own evidence against it, so the direction is down by construction "
                    "and needs no view on whether re-rankers are a good idea."
                ),
            ),
            Change(
                path="fields.retrieval_best_approach_shipped.value",
                after="no",
                justification=(
                    "Entailed by the mutation above, not an independent defect: `mixed_result` means the "
                    "reported metrics disagree about which approach wins. Once the re-ranked row trails on "
                    "all four columns they no longer disagree, and the shipped path is the losing one. "
                    "Leaving this at `mixed_result` would make the twin arithmetically self-contradictory."
                ),
                entailed_by="fields.reranking.measured_effect.value",
            ),
        ),
        restates=(
            Restate(path="fields.reranking.measured_effect.basis", after=RERANK_HURTS_BASIS),
            Restate(
                path="fields.retrieval_best_approach_shipped.basis",
                after=(
                    "The shipped path is hybrid then re-ranker; hybrid alone leads on all four reported "
                    "metrics (15/37/52/0.39 vs 11/30/44/0.31), so the best-measured approach is not the one "
                    "shipped."
                ),
            ),
            Restate(
                path="fields.reranking.decision_basis.basis",
                after=(
                    "the component ships enabled although its own reported numbers trail hybrid alone on "
                    "every metric; no committed text states why it was kept. limitations.md:10 notes the "
                    "cross-encoder is English-trained but draws no ship/do-not-ship conclusion from the "
                    "measurements"
                ),
            ),
        ),
    ),
    TwinSpec(
        twin_id="p01-t02",
        base_case_id="p01",
        twin_type="harmful-component-kept/documented-removal",
        direction="not_below_base",
        against="p01-t01",
        relation="not_below",
        summary=(
            "Same measured-to-hurt re-ranker as p01-t01, but implemented, measured, removed from the request "
            "path, and the reasoning committed."
        ),
        note=(
            "The mitigation pair is p01-t01 vs p01-t02 and the only claim made is that this twin scores at "
            "least as high as p01-t01. The two differ in exactly four values: shipped_enabled, "
            "decision_basis, decision_axes and retrieval_best_approach_shipped. No relation to p01 "
            "itself is claimed - the base ships a component whose metrics merely disagree, which is a "
            "different situation from either half of this pair."
        ),
        changes=(
            Change(
                path="fields.reranking.measured_effect.value",
                after="hurts",
                justification=(
                    "Held identical to p01-t01 so that the pair differs only in what was done about the "
                    "measurement. Without this the pair would also differ in what the numbers say, and no "
                    "claim about the incentive could be read off the comparison."
                ),
            ),
            Change(
                path="fields.reranking.shipped_enabled.value",
                after=False,
                justification=(
                    "The component measured to hurt is not on the request path. Together with `present: true` "
                    "and `evaluated: true` this is the documented-removal shape: built, measured, dropped."
                ),
            ),
            Change(
                path="fields.reranking.decision_basis.value",
                after="measured",
                justification=(
                    "The removal is stated and justified by the project's own measurements. This is the field "
                    "that distinguishes a reasoned removal from a silent one - without it the twin is "
                    "indistinguishable from a project that built a re-ranker and quietly abandoned it."
                ),
            ),
            Change(
                path="fields.reranking.decision_axes.value",
                after=["hit_rate", "mrr"],
                justification=(
                    "Names the measured quantities the stated justification rests on. Required for coherence "
                    "with `decision_basis: measured`, whose schema definition ties the value to a choice "
                    "'justified by the project's own measurements'; an empty axis list would assert the "
                    "justification rests on nothing measured."
                ),
            ),
            Change(
                path="fields.retrieval_best_approach_shipped.value",
                after="yes",
                justification=(
                    "Entailed: with the re-ranker off the request path, the shipped configuration is hybrid "
                    "alone, which leads all four reported columns. Same entailment as p01-t01's move to `no`, "
                    "resolved the other way by the removal."
                ),
                entailed_by="fields.reranking.measured_effect.value",
            ),
        ),
        restates=(
            Restate(path="fields.reranking.measured_effect.basis", after=RERANK_HURTS_BASIS),
            Restate(
                path="fields.reranking.shipped_enabled.basis",
                after=(
                    "The request handler fuses the dense and sparse result lists and generates from them; no "
                    "re-ranking stage is constructed or called on the request path."
                ),
            ),
            Restate(
                path="fields.reranking.decision_basis.basis",
                after=(
                    "a committed section states the re-ranker was implemented, measured and not shipped, and "
                    "justifies that with the project's own numbers: Hit Rate@1, @3, @5 and MRR@10 all fall "
                    "when it is added"
                ),
            ),
            Restate(
                path="fields.reranking.decision_axes.basis",
                after="the stated justification rests on the reported hit-rate and MRR columns",
            ),
            Restate(
                path="fields.retrieval_best_approach_shipped.basis",
                after=(
                    "The shipped path is hybrid alone, which leads all four reported metrics "
                    "(15/37/52/0.39 vs the re-ranked 11/30/44/0.31), so the best-measured approach is the one "
                    "shipped."
                ),
            ),
            Restate(
                path="fields.retrieval_eval_config_matches_shipped.basis",
                after=(
                    "Compared three parameters: retrieval depth k=20 in the notebook vs k=50 shipped; the "
                    "notebook embeds the raw question with a 'query: ' prefix and no normalisation while the "
                    "request path embeds with no prefix and normalize_embeddings=True; and the notebook "
                    "applies no query rewriting while the request path rewrites first."
                ),
            ),
        ),
    ),
    TwinSpec(
        twin_id="p01-t03",
        base_case_id="p01",
        twin_type="claim-without-artifact",
        direction="down",
        against="p01",
        relation="strictly_below",
        summary=(
            "The ingestion counts are still reported in prose, but the committed screenshot of the pipeline's "
            "own summary log that backed them is not in the repository."
        ),
        note=(
            "Expressed as a count move rather than an enum flip, because p01 admits no enum flip here: "
            "`headline_numbers_traceable` sits at `some_traceable` and `none_traceable` is unreachable "
            "without also uncommitting the dashboard JSON and the question set, which would drag monitoring "
            "and document_code_conflicts with it. Only three figures of headroom exist on this type."
        ),
        changes=(
            Change(
                path="fields.untraceable_number_count.value",
                after=21,
                justification=(
                    "Three reported figures - 1432 documents, 1514 chunks, 1514 vectors - are backed in the "
                    "base by a committed screenshot of the pipeline's summary line, and by nothing else. "
                    "Remove that one artifact and those three figures have no committed artifact able to "
                    "produce them, so the count rises by exactly three. Strictly more reported numbers rest "
                    "on assertion and no other fact about the repository changes, so the direction is down "
                    "by construction."
                ),
            ),
        ),
        restates=(
            Restate(
                path="fields.untraceable_number_count.basis",
                after=(
                    "Counted reported measurement results with no committed artifact able to produce them: 4 "
                    "strategies by 4 metrics in the retrieval table (16), the two answer-quality scores (2), "
                    "and the three ingestion counts (3), whose only stated source is a screenshot that is not "
                    "committed. One of the 16 is additionally unreachable arithmetically - see "
                    "extraction_notes."
                ),
            ),
            Restate(
                path="fields.headline_numbers_traceable.basis",
                after=(
                    "Traceable: the stated test-set size is countable in the committed list, and the panel "
                    "count is countable in the committed dashboard JSON. Not traceable: the ingestion counts, "
                    "which are stated in the architecture doc with no committed artifact producing them; and "
                    "every figure in the evaluation tables, because the only artifacts named for them are two "
                    "marimo .py notebooks that store no cell outputs and, as committed, import none of the "
                    "names they use (mo, TEST_SET, DenseRetriever, BM25Retriever, Reranker, hybrid_fusion, "
                    "embed_query, np, pd, plt) while every cell returns nothing, so no value passes between "
                    "cells."
                ),
            ),
            Restate(
                path="fields.headline_numbers_traceable.evidence",
                after=[
                    "docs/architecture.md:108",
                    "src/evaluation/test_set.py:1-137",
                    "dashboards/food-wine-dashboard.json",
                    "docs/evaluation.md:5-17",
                    "notebooks/01_retrieval_evaluation.py:1-9",
                    "notebooks/02_llm_evaluation.py:1-12",
                ],
            ),
        ),
    ),
    TwinSpec(
        twin_id="p01-t04",
        base_case_id="p01",
        twin_type="checkbox-padding",
        direction="down",
        against="p01",
        relation="strictly_below",
        summary="The same eight committed dashboard panels, none of which queries anything the application writes.",
        changes=(
            Change(
                path="fields.monitoring_charts_bound_to_data.value",
                after="none",
                justification=(
                    "The panel count, the dashboard's existence and the request-path instrumentation are all "
                    "unchanged; what changes is whether the panels reference a table the committed DDL "
                    "creates. Eight panels bound to no data source is strictly less monitoring than eight "
                    "bound to it, and it is a fact about two committed files rather than an opinion about "
                    "dashboards, so the direction is down by construction."
                ),
            ),
        ),
        restates=(
            Restate(
                path="fields.monitoring_charts_bound_to_data.basis",
                after=(
                    "Checked each of the 8 panel rawSql queries against the committed DDL and the logging "
                    "code: every panel selects from a table that no committed DDL creates and that no "
                    "function in the application writes, so no panel can render data."
                ),
            ),
        ),
    ),
    TwinSpec(
        twin_id="p01-t05",
        base_case_id="p01",
        twin_type="no-change",
        direction="zero",
        against="p01",
        relation="exactly_equal",
        summary="The same system on a different stack: a different web framework and a different vector store.",
        note=(
            "Both mutated fields are `descriptive`. Neither product name appears in the basis of any "
            "`scoreable` field in the base record, so no scoreable prose needed restating - which is what "
            "makes this swap expressible at all. See the report for the swaps that are not."
        ),
        changes=(
            Change(
                path="fields.interface_framework.value",
                after="fastapi",
                justification=(
                    "`interface_framework` is descriptive by schema section K while `interface_kind` is "
                    "scoreable: whether a project has a web interface is creditable, which library built it "
                    "is not. Every scoreable fact - a page served at /, posting to a JSON endpoint, with "
                    "screenshots committed - is unchanged, so any movement is a criterion reading a field no "
                    "defensible criterion should read."
                ),
            ),
            Change(
                path="fields.vector_store.value",
                after="elasticsearch",
                justification=(
                    "Descriptive by schema section K. `knowledge_base_present`, `retrieval_flow` and every "
                    "retrieval-evaluation field describe what the request path does, not which product "
                    "stores the vectors, and none of their basis text names the store."
                ),
            ),
        ),
        restates=(
            Restate(
                path="fields.interface_framework.basis",
                after="The application object is a FastAPI app, served by uvicorn.",
            ),
        ),
    ),
    TwinSpec(
        twin_id="p01-t06",
        base_case_id="p01",
        twin_type="no-change",
        direction="zero",
        against="p01",
        relation="exactly_equal",
        summary="The same system with the same artifacts, consolidated into fewer tracked files.",
        note=(
            "A size swap rather than one of the catalogue's three named no-change kinds. It is here because "
            "it is the only other no-change mutation p01 admits without touching prose on a scoreable field, "
            "and because repository size is exactly the kind of thing a criterion must not reward."
        ),
        changes=(
            Change(
                path="fields.repo_file_count.value",
                after=41,
                justification=(
                    "Descriptive by schema section K, and cited by no other field's basis or evidence. Every "
                    "artifact on the reachability checklist is still present and still referenced, every "
                    "technique is still implemented, and the run procedure is unchanged; only how the same "
                    "content is distributed across files differs. A criterion moving on this is scoring "
                    "repository size."
                ),
            ),
        ),
        # No restatement: `repo_file_count`'s own basis is the command that
        # produced it, and no other field's basis or evidence cites the count.
    ),
    # ------------------------------------------------------------------
    # M2 step 5 additions — real bases identified via the 22-repo six-field
    # table (runs/2026-08-14-m2-corpus-extraction/step4-real-score-extraction.md).
    # Each mutates exactly one independent scoreable field: no entailment,
    # so none needs an APPROVED_ENTAILMENTS entry.
    # ------------------------------------------------------------------
    TwinSpec(
        twin_id="p07-t01",
        base_case_id="p07",
        twin_type="config-drift",
        direction="down",
        against="p07",
        relation="strictly_below",
        summary="The committed retrieval evaluation runs at a different depth than the shipped default.",
        changes=(
            Change(
                path="fields.retrieval_eval_config_matches_shipped.value",
                after="differs",
                justification=(
                    "In the base, the committed run's k=4 matches Index.py's DEFAULT_LIMIT=4, which the "
                    "shipped chat and CLI both use unless overridden. Here the committed run is recorded at "
                    "k=10 instead, while the shipped default stays at 4; retriever (postgres_hybrid) and "
                    "embedding model are unchanged. A single retrieval-depth parameter now differs between "
                    "what was measured and what ships, which is exactly the 'measured system is not the "
                    "shipped system' fact this field exists to catch - down by construction, independent of "
                    "whether either depth is a better choice."
                ),
            ),
        ),
        restates=(
            Restate(
                path="fields.retrieval_eval_config_matches_shipped.basis",
                after=(
                    "The committed retrieval run recorded retriever=postgres_hybrid, k=10, "
                    "embedding_model=Xenova/bge-small-en-v1.5. k=10 differs from config.yml.dist's "
                    "index_engine defaults and Index.py's DEFAULT_LIMIT=4, which the shipped chat and CLI "
                    "both use unless overridden; retriever and embedding model still match."
                ),
            ),
        ),
    ),
    TwinSpec(
        twin_id="p12-t01",
        base_case_id="p12",
        twin_type="unfailable-eval",
        direction="down",
        against="p12",
        relation="strictly_below",
        summary="One of three reported judge metrics now sits at ceiling; the other two are unchanged.",
        note=(
            "Only one of the three group-H judge metrics needs to hit ceiling for the field to flip - "
            "`llm_eval_metric_at_ceiling` is true iff at least one qualifying metric exists (schema group E, "
            "M2 ceiling rule), evaluated per metric and never averaged. avg_faithfulness and avg_completeness "
            "are left exactly as measured in the base so the twin makes the smallest change that forces the "
            "field, rather than rewriting the whole evaluation."
        ),
        changes=(
            Change(
                path="fields.llm_eval_metric_at_ceiling.value",
                after=True,
                justification=(
                    "In the base, all three reported metrics (avg_relevance 4.159, avg_faithfulness 3.568, "
                    "avg_completeness 3.795, out of 5) sit well under the 95%-of-items ceiling threshold, and "
                    "individual items score as low as 1/5 on each. Here avg_relevance alone rises to 4.95/5 "
                    "with at least 95% of items scoring the metric's maximum, while faithfulness and "
                    "completeness are unchanged. A measurement where the reported metric can no longer "
                    "separate a good answer from a bad one is the unfailable-test lever this field exists to "
                    "catch, and it takes only one qualifying metric to trigger - down by construction, no "
                    "view needed on whether the judged answers are actually good."
                ),
            ),
        ),
        restates=(
            Restate(
                path="fields.llm_eval_metric_at_ceiling.basis",
                after=(
                    "avg_relevance rises to 4.95 (maximise direction, at least 95% of items scoring the "
                    "metric's maximum 5/5) while avg_faithfulness (3.568) and avg_completeness (3.795) are "
                    "unchanged from the base - one qualifying metric makes the field true, evaluated per "
                    "metric and never averaged."
                ),
            ),
        ),
    ),
    TwinSpec(
        twin_id="p04-t01",
        base_case_id="p04",
        twin_type="claim-without-artifact",
        direction="down",
        against="p04",
        relation="strictly_below",
        summary=(
            "The itinerary evaluation script is no longer committed, so the one headline figure it alone "
            "produces has nothing behind it."
        ),
        note=(
            "Uses the owner-approved entailment `p04-t01` (`APPROVED_ENTAILMENTS`): "
            "`headline_numbers_traceable` is a coarse summary of `untraceable_number_count`, not an "
            "independently-measured fact, so moving the count from 0 forces the summary to move too - one "
            "fact, two representations, same shape as `retrieval_best_approach_shipped` (item 3e). "
            "`claim-without-artifact` moved off p01 for this base per `claim-without-artifact-base-switch`: "
            "p04 is `all_traceable` with zero untraceable figures currently, giving real headroom instead of "
            "p01's marginal 18-to-21 move."
        ),
        changes=(
            Change(
                path="fields.untraceable_number_count.value",
                after=1,
                justification=(
                    "In the base, every headline figure across retrieval, itinerary and LLM-contract "
                    "evaluation traces to a committed, importable script (retrieval.py, itinerary.py, "
                    "llm.py). Here evaluation/itinerary.py is no longer committed, so the itinerary "
                    "mean-fairness figure it alone produces has no committed artifact able to produce it; "
                    "the retrieval and LLM-contract scripts, and every figure they produce, are unchanged. "
                    "One artifact removed, one figure newly untraceable - down by construction, independent "
                    "of whether the fairness figure itself is accurate."
                ),
            ),
            Change(
                path="fields.headline_numbers_traceable.value",
                after="some_traceable",
                justification=(
                    "Entailed by the mutation above, not an independent defect: with one of several headline "
                    "figures no longer traceable to any committed artifact while the rest remain traceable "
                    "via retrieval.py and llm.py, the record can no longer honestly read `all_traceable`. "
                    "The schema's own summary distinguishes this from `none_traceable`, which would require "
                    "every figure to lose its artifact, not just one - a base was deliberately chosen with "
                    "enough real headline figures (retrieval MRR/recall, itinerary fairness, LLM-contract "
                    "scores) that removing one script's worth leaves others intact."
                ),
                entailed_by="fields.untraceable_number_count.value",
            ),
        ),
        restates=(
            Restate(
                path="fields.headline_numbers_traceable.basis",
                after=(
                    "Retrieval and LLM-contract headline figures still trace to committed "
                    "evaluation/retrieval.py and evaluation/llm.py; the itinerary mean-fairness figure has "
                    "no committed artifact able to produce it, since evaluation/itinerary.py is not "
                    "committed."
                ),
            ),
        ),
    ),
    TwinSpec(
        twin_id="p11-t01",
        base_case_id="p11",
        twin_type="sample-too-small",
        direction="down",
        against="p11",
        relation="strictly_below",
        summary="The same retrieval evaluation, on a ground-truth set shrunk from 200 questions to 5.",
        note=(
            "`retrieval_eval_uncertainty_stated` is already `false` in the base (point values only, no "
            "interval or variance) and stays `false` here - only the set size moves. The compound failure "
            "signature the catalogue names ('many config decisions settled on a tiny set with no uncertainty "
            "statement') needs both halves true; the second half was already true and unchanged, so a "
            "single-field move produces the full pattern."
        ),
        changes=(
            Change(
                path="fields.retrieval_eval_set_size.value",
                after=5,
                justification=(
                    "In the base, 200 question rows back the reported hit-rate/MRR figures. Here only 5 do, "
                    "with no interval or variance stated either in the base or here. Every retrieval-config "
                    "decision the project reports numbers for now rests on a sample too small to distinguish "
                    "signal from noise, and nothing in the record says so - down by construction, independent "
                    "of what the actual hit-rate/MRR values are."
                ),
            ),
        ),
        restates=(
            Restate(
                path="fields.retrieval_eval_set_size.basis",
                after="6 lines including header = 5 question rows.",
            ),
        ),
    ),
    TwinSpec(
        twin_id="p10-t01",
        base_case_id="p10",
        twin_type="unlocatable-project",
        direction="down",
        against="p10",
        relation="strictly_below",
        summary=(
            "The same three artifacts exist; a third one - the evaluation question set - now joins the two "
            "already unreferenced."
        ),
        note=(
            "`artifact_reference_strength` stays `partially_referenced`: that value means 'at least one "
            "expected artifact is named nowhere', already true in the base at count 2 and still true at "
            "count 3. No entailment needed - unlike the p04-t01 pair, the enum does not have to move for the "
            "count to move, because the base was chosen already past the enum's threshold."
        ),
        changes=(
            Change(
                path="fields.artifacts_unreferenced_count.value",
                after=3,
                justification=(
                    "In the base, the evaluation notebook and the ingestion module exist but are named "
                    "nowhere in the README, while the evaluation question set is named - two of the fixed "
                    "checklist's five items are unreferenced (monitoring dashboard and deployment "
                    "configuration are absent from the project and excluded from the count per the field's "
                    "own rule). Here the evaluation question set is also named nowhere, joining the other "
                    "two; the artifacts referenced by every other field are unchanged. One more artifact "
                    "unreferenced, same fixed checklist - down by construction."
                ),
            ),
        ),
        restates=(
            Restate(
                path="fields.artifacts_unreferenced_count.basis",
                after=(
                    "of the fixed checklist, three present artifacts are named nowhere in the documentation: "
                    "the evaluation script/notebook, the ingestion entry point, and the evaluation question "
                    "set; a monitoring dashboard definition and a deployment configuration are absent from "
                    "the repository and excluded from the count."
                ),
            ),
        ),
    ),
    TwinSpec(
        twin_id="p01-t07",
        base_case_id="p01",
        twin_type="no-change/cosmetic-rename",
        direction="zero",
        against="p01",
        relation="exactly_equal",
        summary="The same system, same everything, under a different synthetic project name.",
        note=(
            "The third no-change kind, unbuildable until `project_name` existed (schema M2 addition, group "
            "K) - no field held anything like a project or brand name before this. `project_name` is itself "
            "synthetic on every record (`tools/assign_project_names.py`, never extracted), so this twin "
            "swaps one synthetic label for another; the real-world equivalent (renaming an actual repository) "
            "is exactly what this mutation stands in for without touching real names."
        ),
        changes=(
            Change(
                path="fields.project_name.value",
                after="Project Omega",
                justification=(
                    "`project_name` is descriptive and synthetic by construction - it is never read off the "
                    "repository and no other field's `basis` or `evidence` cites it (checked: it is assigned "
                    "after extraction, by a separate deterministic tool, specifically so nothing else in the "
                    "record can depend on it). Changing it is the purest possible no-change mutation: nothing "
                    "about the system, its evidence, or any other field's text moves. A criterion reading "
                    "this field would be scoring a label that carries no information at all."
                ),
            ),
        ),
        # No restatement: `project_name.basis` already reads generically ("assigned by
        # tools/assign_project_names.py from case_id"), true of any value it could hold.
    ),
    # ------------------------------------------------------------------
    # M2 step 5, cross-criterion conditional family (`twin-catalogue-conditional`,
    # idea 1): the same config-drift mutation (retrieval_eval_config_matches_shipped
    # matches -> differs), held against hybrid_search's three possible
    # measured_effect readings, on three different real bases. Tests whether a
    # future candidate applies the config-drift penalty uniformly rather than
    # only in the `improves` case, which is the one most obviously exploitable
    # and the one a partial implementation would be tempted to special-case.
    # ------------------------------------------------------------------
    TwinSpec(
        twin_id="p12-t02",
        base_case_id="p12",
        twin_type="config-drift/conditional",
        direction="down",
        against="p12",
        relation="strictly_below",
        summary="hybrid_search measures to improve retrieval, but now under a drifted evaluation config.",
        note=(
            "Conditional family, `improves` branch. hybrid_search.decision_basis stays `measured` and "
            "unchanged: the project still *believes* its ship decision is grounded in measurement. What "
            "changes is whether that measurement can be trusted - a candidate that credits `improves` "
            "without checking `retrieval_eval_config_matches_shipped` cannot tell this twin from the base."
        ),
        changes=(
            Change(
                path="fields.retrieval_eval_config_matches_shipped.value",
                after="differs",
                justification=(
                    "In the base, strategy hybrid_k20_rerank_rewrite's parameters (top_k=5, retrieve_k=20, "
                    "rewrite and rerank enabled) match rag_pipeline's own shipped defaults exactly. Here the "
                    "evaluated strategy runs at retrieve_k=50 instead of 20, everything else unchanged. The "
                    "hybrid_search.measured_effect: improves claim behind the ship decision now rests on a "
                    "measurement of a system that is not the one shipped - down by construction, independent "
                    "of whether hybrid search actually helps."
                ),
            ),
        ),
        restates=(
            Restate(
                path="fields.retrieval_eval_config_matches_shipped.basis",
                after=(
                    "Strategy hybrid_k20_rerank_rewrite uses top_k=5/retrieve_k=50 with rewrite and rerank "
                    "enabled; rag_pipeline's own shipped defaults are top_k=5/retrieve_k=20. Retrieval depth "
                    "differs; rewrite and rerank flags still match."
                ),
            ),
        ),
    ),
    TwinSpec(
        twin_id="p09-t01",
        base_case_id="p09",
        twin_type="config-drift/conditional",
        direction="down",
        against="p09",
        relation="strictly_below",
        summary="hybrid_search's mixed retrieval result now comes from a drifted evaluation config.",
        note="Conditional family, `mixed` branch - same mutation as p12-t02, different measured_effect value.",
        changes=(
            Change(
                path="fields.retrieval_eval_config_matches_shipped.value",
                after="differs",
                justification=(
                    "In the base, the evaluation notebook imports the retriever module directly and runs at "
                    "k=5, the app's own default. Here the notebook is recorded as running at k=10 instead, "
                    "everything else in the retriever call unchanged. The mixed hit-rate/MRR disagreement "
                    "hybrid_search.decision_basis rests on - hybrid wins on hit-rate, loses on MRR - was "
                    "measured at a depth the shipped path never uses, so neither reported number can be "
                    "trusted to describe the shipped system - down by construction, independent of which "
                    "metric the project chose to decide on."
                ),
            ),
        ),
        restates=(
            Restate(
                path="fields.retrieval_eval_config_matches_shipped.basis",
                after=(
                    "the notebook imports RETRIEVERS/connection directly from retrieval/retrieve.py but "
                    "evaluates at k=10; the app's own default, used on the request path, is k=5."
                ),
            ),
        ),
    ),
    TwinSpec(
        twin_id="p18-t01",
        base_case_id="p18",
        twin_type="config-drift/conditional",
        direction="down",
        against="p18",
        relation="strictly_below",
        summary="hybrid_search's measured-to-hurt result, and the decision built on it, now rest on a drifted config.",
        note=(
            "Conditional family, `hurts` branch - the case most likely to be treated as already 'safe' by an "
            "unconditional candidate, since a technique measured to hurt and correctly kept off the request "
            "path looks like a good outcome regardless of eval trust. It is not: if the eval that produced "
            "'hurts' does not reflect the shipped system, the decision it justified is unverified either way "
            "- the project could equally be wrongly rejecting a technique that would have helped."
        ),
        changes=(
            Change(
                path="fields.retrieval_eval_config_matches_shipped.value",
                after="differs",
                justification=(
                    "In the base, the eval's keyword-only arm and the shipped default (HybridSearcher, "
                    "kw_weight=1.0, vec_weight=0.0) both retrieve at limit=5, so the shipped path returns "
                    "exactly what the keyword-only eval arm measured. Here the eval's keyword-only arm is "
                    "recorded as running at limit=10 instead, while the shipped default stays at limit=5. "
                    "The keyword-only-wins result hybrid_search.decision_basis cites was measured on a "
                    "retrieval depth the shipped path never uses - the 'hurts' verdict, and the ship decision "
                    "resting on it, are both unverified against what actually ships - down by construction, "
                    "independent of whether keyword-only genuinely is the better choice."
                ),
            ),
        ),
        restates=(
            Restate(
                path="fields.retrieval_eval_config_matches_shipped.basis",
                after=(
                    "eval's keyword-only arm retrieves at limit=10; the shipped default (HybridSearcher, "
                    "kw_weight=1.0, vec_weight=0.0) retrieves at limit=5. Retrieval depth differs between "
                    "what was measured and what ships."
                ),
            ),
        ),
    ),
    TwinSpec(
        twin_id="p02-t01",
        base_case_id="p02",
        twin_type="decision-basis-unsupported/conditional",
        direction="down",
        against="p02",
        relation="strictly_below",
        summary="The same removal, the same claim of measurement grounding, with no axes left to name it.",
        note=(
            "Conditional family (`twin-catalogue-conditional`, idea 4): tests whether a candidate requires "
            "`decision_axes` to be non-empty and explanatory when `decision_basis` claims `measured`, or "
            "credits `measured` at face value regardless. No real base in the 22-repo corpus holds "
            "`measured_effect: improves` alongside a measured removal (searched directly, none found); p02's "
            "reranking case (`mixed`, one axis winning, one losing) is the closest real analogue and is used "
            "as-is - the tension idea 4 names does not need `improves` specifically, only a plausible-looking "
            "`measured` claim with the actual axes stripped out."
        ),
        changes=(
            Change(
                path="fields.reranking.decision_axes.value",
                after=[],
                justification=(
                    "In the base, the stated rejection names both traded-off quantities (MRR gain, latency "
                    "cost) that `measured_effect: mixed` itself reports. Here `decision_basis` still reads "
                    "`measured` - the record still claims the choice rests on the project's own numbers - but "
                    "no axis is named at all. A candidate that credits `measured` without checking "
                    "`decision_axes` cannot tell this twin from the base; a candidate that correctly demands "
                    "the axes actually resolve the tension should score this strictly lower, independent of "
                    "whether the underlying removal itself was reasonable."
                ),
            ),
        ),
        restates=(
            Restate(
                path="fields.reranking.decision_axes.basis",
                after="No measured quantities named alongside this technique's decision_basis.",
            ),
        ),
    ),
    TwinSpec(
        twin_id="p17-t01",
        base_case_id="p17",
        twin_type="no-change/dataset-domain-swap",
        direction="zero",
        against="p17",
        relation="exactly_equal",
        summary="The same system over a completely different subject: XAI research literature swapped for beekeeping.",
        note=(
            "Checked field by field, not by keyword search: a keyword grep on domain terms gives false "
            "clears (it read p11 as clean when `problem_statement` there names 'patients seeking medical "
            "advice' without using any word a domain grep would catch). All ~53 scoreable fields on p17 read "
            "as structural or mechanistic, none naming the XAI subject or an audience for it. p17 is not the "
            "only clean base: p01's current record (schema_version 1, re-extracted at step 3 under the "
            "tightened basis rule) also passes the same field-by-field check - the leaky p01 named in early "
            "M1/M2 documents was the v1 extraction, since overwritten. This twin is built on p17 rather than "
            "p01 because p17 was checked first and one clean base is what the catalogue needs; a second "
            "domain-swap twin on p01 is possible but not built here."
        ),
        changes=(
            Change(
                path="fields.corpus_domain.value",
                after="urban beekeeping and pollinator conservation",
                justification=(
                    "Descriptive by schema section K. Every scoreable field on this record was read in full "
                    "and none names the corpus subject, the intended audience, or anything that would read "
                    "differently under a different domain - including `problem_statement`, whose basis "
                    "states only that the Problem section names no audience, not what the problem is. A "
                    "criterion moving on this field is scoring the corpus's subject matter, not the system."
                ),
            ),
        ),
        # No restatement: corpus_domain's own basis ("stated subject of the ingested corpus") is generic and
        # does not name the subject itself, so it needs no rewrite when the subject changes.
    ),
    TwinSpec(
        twin_id="p13-t01",
        base_case_id="p13",
        twin_type="circular-eval",
        direction="down",
        against="p13",
        relation="strictly_below",
        summary="The same LLM-eval question generator, but the judge's verdicts are no longer spot-checked.",
        changes=(
            Change(
                path="fields.llm_eval_judge_spotchecked.value",
                after=False,
                justification=(
                    "In the base, all 30 trap answers from the shipping prompt variant were read by hand and "
                    "compared to the judge's own verdicts (18/30 agreement, reported). Here that check does "
                    "not exist. The question generator is unchanged "
                    "(`generator_ties_question_to_passage` - questions still trace to a specific chunk or a "
                    "fetched external passage), so the only fact that changes is whether the judge's own "
                    "error rate was ever measured against a human reading. Removing the one spot-check this "
                    "project actually ran restores the circularity failure mode the schema names: generated "
                    "questions judged by machinery whose own error rate is never checked - down by "
                    "construction, independent of any view on the corpus or the judge model."
                ),
            ),
        ),
        restates=(
            Restate(
                path="fields.llm_eval_judge_spotchecked.basis",
                after="No committed artifact reports a human check of judge verdicts against a reading of the answers.",
            ),
        ),
    ),
)


# --------------------------------------------------------------------------
# Path handling
# --------------------------------------------------------------------------


def split_path(path: str) -> list[str]:
    return path.split(".")


def get_at(doc: dict, path: str) -> Any:
    node: Any = doc
    for key in split_path(path):
        node = node[key]
    return node


def set_at(doc: dict, path: str, value: Any) -> None:
    keys = split_path(path)
    node: Any = doc
    for key in keys[:-1]:
        node = node[key]
    if keys[-1] not in node:
        raise KeyError(f"{path} does not exist in the base record")
    node[keys[-1]] = value


def field_spec(path: str) -> tuple[str, tuple[str, str, list[str] | None]]:
    """Resolve a dotted path to (field label, spec). Raises on unknown fields."""
    keys = split_path(path)
    if keys[0] != "fields":
        raise KeyError(f"{path} does not address a record field")
    name = keys[1]
    if name in TECHNIQUES:
        sub = keys[2]
        if sub not in TECHNIQUE_SPEC:
            raise KeyError(f"{path}: {sub} is not a technique sub-field")
        return f"{name}.{sub}", TECHNIQUE_SPEC[sub]
    if name not in FIELD_SPEC:
        raise KeyError(f"{path}: {name} is not a field in the schema")
    return name, FIELD_SPEC[name]


def read_set_of(path: str) -> str:
    return field_spec(path)[1][0]


def check_legal(path: str, value: Any) -> None:
    """Assert a mutated value is legal under the schema for its field."""
    label, (_read_set, kind, allowed) = field_spec(path)
    if kind == "enum":
        assert isinstance(value, str), f"{label}: enum value must be a string, got {value!r}"
        assert value in (allowed or []) + ENUM_UNIVERSAL, f"{label}: {value!r} is not a legal member"
    elif kind == "list_enum":
        assert isinstance(value, list) and value, f"{label}: expected a non-empty list, got {value!r}"
        for v in value:
            assert v in (allowed or []) + ENUM_UNIVERSAL, f"{label}: {v!r} is not a legal member"
    elif kind == "bool":
        assert isinstance(value, bool), f"{label}: expected bool, got {value!r}"
    elif kind == "bool_or_null":
        assert value is None or isinstance(value, bool), f"{label}: expected bool or null, got {value!r}"
    elif kind == "int":
        assert isinstance(value, int) and not isinstance(value, bool), f"{label}: expected int, got {value!r}"
    elif kind == "int_or_null":
        assert value is None or (isinstance(value, int) and not isinstance(value, bool)), (
            f"{label}: expected int or null, got {value!r}"
        )
    elif kind == "str":
        assert isinstance(value, str) and value, f"{label}: expected non-empty string, got {value!r}"
    elif kind == "list_str":
        assert isinstance(value, list) and all(isinstance(v, str) for v in value), (
            f"{label}: expected a list of strings, got {value!r}"
        )
    else:  # pragma: no cover - FIELD_SPEC is a closed table
        raise AssertionError(f"{label}: unknown kind {kind}")


# --------------------------------------------------------------------------
# Building
# --------------------------------------------------------------------------


def build(base: dict, spec: TwinSpec) -> dict:
    """Apply one spec to the base record, returning a complete twin record."""
    twin = copy.deepcopy(base)

    diff: list[dict[str, Any]] = []
    for change in spec.changes:
        before = get_at(twin, change.path)
        check_legal(change.path, change.after)
        assert before != change.after, f"{spec.twin_id}: {change.path} is already {change.after!r}"
        # deepcopy so a mutable value is not the same object in both the
        # record and the metadata, which PyYAML would emit as an anchor/alias.
        set_at(twin, change.path, copy.deepcopy(change.after))
        # A constructed value must not keep the base record's locators.
        evidence_path = change.path.removesuffix(".value") + ".evidence"
        set_at(twin, evidence_path, [SYNTHETIC])
        entry: dict[str, Any] = {
            "field": change.path,
            "read_set": read_set_of(change.path),
            "before": copy.deepcopy(before),
            "after": copy.deepcopy(change.after),
            "justification": change.justification,
        }
        if change.entailed_by is not None:
            approved = APPROVED_ENTAILMENTS.get(spec.twin_id, {})
            assert approved.get(change.path) == change.entailed_by, (
                f"{spec.twin_id}: {change.path} is declared entailed by "
                f"{change.entailed_by}, which the owner has not approved. "
                "Entailed second changes are allowed only where APPROVED_ENTAILMENTS "
                "says so — the M1 ruling scoped the allowance to one pair and "
                "explicitly refused it as a standing rule. Take this to the owner."
            )
            entry["entailed_by"] = change.entailed_by
            entry["independent_defect"] = False
        else:
            entry["independent_defect"] = True
        diff.append(entry)

    restated: list[dict[str, Any]] = []
    for restate in spec.restates:
        before = get_at(twin, restate.path)
        assert before != restate.after, f"{spec.twin_id}: {restate.path} is already the restated text"
        set_at(twin, restate.path, copy.deepcopy(restate.after))
        restated.append({
            "field": restate.path,
            "read_set": read_set_of(restate.path),
            "before": copy.deepcopy(before),
            "after": copy.deepcopy(restate.after),
        })

    twin["case_id"] = spec.twin_id
    meta: dict[str, Any] = {
        "twin_id": spec.twin_id,
        "base_case_id": base["case_id"],
        "base_commit": base["commit"],
        "type": spec.twin_type,
        "direction": spec.direction,
        "comparison": {"against": spec.against, "relation": spec.relation},
        "summary": spec.summary,
    }
    if spec.note:
        meta["note"] = spec.note
    meta["diff"] = diff
    meta["restated"] = restated
    meta["generated_by"] = "tools/generate_twins.py"

    # `twin` first so a reader opening the file sees what it is before the
    # 60-odd inherited fields.
    return {"twin": meta, **twin}


HEADER = (
    "# Generated by tools/generate_twins.py. Do not edit: regenerate instead.\n"
    "# A complete evidence record - the base with one mutation applied - plus a\n"
    "# `twin` block stating the diff and the direction that diff forces.\n"
)


def dump(doc: dict) -> str:
    return HEADER + yaml.safe_dump(
        doc, sort_keys=False, allow_unicode=True, default_flow_style=False, width=4096
    )


# --------------------------------------------------------------------------
# Verification — run against what was written, not against what was intended
# --------------------------------------------------------------------------


def flatten(node: Any, prefix: str = "") -> dict[str, Any]:
    """Every leaf of a record as dotted path -> value."""
    out: dict[str, Any] = {}
    if isinstance(node, dict):
        for key, value in node.items():
            out.update(flatten(value, f"{prefix}.{key}" if prefix else key))
    else:
        out[prefix] = node
    return out


def verify(bases: dict[str, dict], written: dict[str, dict], specs: tuple[TwinSpec, ...]) -> list[str]:
    """Re-derive every claim from the files on disk. Returns the checks run."""
    checks: list[str] = []

    for spec in specs:
        base = bases[spec.base_case_id]
        base_flat = flatten({k: v for k, v in base.items() if k != "case_id"})
        doc = written[spec.twin_id]
        meta = doc["twin"]
        record = {k: v for k, v in doc.items() if k not in ("twin", "case_id")}
        twin_flat = flatten(record)

        assert doc["case_id"] == spec.twin_id
        assert meta["base_case_id"] == base["case_id"]
        assert meta["base_commit"] == base["commit"]
        assert set(twin_flat) == set(base_flat), f"{spec.twin_id}: field set differs from the base record"

        # 1. The structural diff is exactly what the metadata claims.
        actual = {p for p in base_flat if base_flat[p] != twin_flat[p]}
        claimed_values = {e["field"] for e in meta["diff"]}
        claimed_prose = {e["field"] for e in meta["restated"]}
        claimed_evidence = {e["field"].removesuffix(".value") + ".evidence" for e in meta["diff"]}
        assert actual == claimed_values | claimed_prose | claimed_evidence, (
            f"{spec.twin_id}: undeclared changes {sorted(actual - (claimed_values | claimed_prose | claimed_evidence))}"
            f" / declared-but-absent {sorted((claimed_values | claimed_prose | claimed_evidence) - actual)}"
        )
        for entry in meta["diff"] + meta["restated"]:
            assert base_flat[entry["field"]] == entry["before"], f"{spec.twin_id}: stale before on {entry['field']}"
            assert twin_flat[entry["field"]] == entry["after"], f"{spec.twin_id}: stale after on {entry['field']}"

        # 2. Every mutated value is legal under the schema.
        for entry in meta["diff"]:
            check_legal(entry["field"], entry["after"])

        # 3. The disjoint-field-sets rule, on values and on prose alike: a
        #    prose reviewer sees `basis`, so restating a scoreable basis in a
        #    no-change twin would break the gate just as a value change would.
        touched = {read_set_of(p) for p in actual}
        if spec.direction == "zero":
            assert touched == {DESCRIPTIVE}, f"{spec.twin_id}: no-change twin touched {sorted(touched)} fields"
        else:
            assert touched == {SCOREABLE}, f"{spec.twin_id}: degraded twin touched {sorted(touched)} fields"

        # 4. Every changed value carries a per-field justification.
        for entry in meta["diff"]:
            assert entry["justification"].strip(), f"{spec.twin_id}: {entry['field']} has no justification"

        checks.append(
            f"  {spec.twin_id:8s} {spec.direction:15s} {len(meta['diff'])} value change(s), "
            f"{len(meta['restated'])} restated, all {sorted(touched)[0]}"
        )

    # 5. The mitigation pair differs only in the removal-and-documentation
    #    fields: the two must share the measurement they are arguing about.
    kept = flatten({k: v for k, v in written["p01-t01"].items() if k not in ("twin", "case_id")})
    removed = flatten({k: v for k, v in written["p01-t02"].items() if k not in ("twin", "case_id")})
    pair_diff = {p.removesuffix(".value") for p in kept if kept[p] != removed[p] and p.endswith(".value")}
    expected = {
        "fields.reranking.shipped_enabled",
        "fields.reranking.decision_basis",
        "fields.reranking.decision_axes",
        "fields.retrieval_best_approach_shipped",
    }
    assert pair_diff == expected, f"mitigation pair differs in {sorted(pair_diff)}, expected {sorted(expected)}"
    assert kept["fields.reranking.measured_effect.value"] == removed["fields.reranking.measured_effect.value"]
    checks.append("  p01-t01/p01-t02 mitigation pair differs in exactly the 4 removal fields, same measured_effect")

    # 6. Determinism: dumping a re-loaded document reproduces the file.
    for spec in specs:
        path = TWINS / f"{spec.twin_id}.yaml"
        assert dump(written[spec.twin_id]) == path.read_text(encoding="utf-8"), f"{spec.twin_id}: not round-trip stable"
    checks.append("  all twins round-trip: reload -> re-dump is byte-identical to the file on disk")

    return checks


def main() -> int:
    base_ids = sorted({spec.base_case_id for spec in SPECS})
    bases: dict[str, dict] = {}
    for base_id in base_ids:
        base_path = RECORDS / f"{base_id}.yaml"
        base = yaml.safe_load(base_path.read_text(encoding="utf-8"))

        unknown = [n for n in base["fields"] if n not in FIELD_SPEC and n not in TECHNIQUES]
        if unknown:
            print(f"{base_id}: base record has fields absent from FIELD_SPEC: {unknown}", file=sys.stderr)
            return 1
        missing = [n for n in FIELD_SPEC if n not in base["fields"]]
        if missing:
            print(f"note: schema fields absent from {base_id}: {missing}")
        bases[base_id] = base

    TWINS.mkdir(parents=True, exist_ok=True)
    written: dict[str, dict] = {}
    for spec in SPECS:
        doc = build(bases[spec.base_case_id], spec)
        (TWINS / f"{spec.twin_id}.yaml").write_text(dump(doc), encoding="utf-8")
        written[spec.twin_id] = doc

    reloaded = {
        spec.twin_id: yaml.safe_load((TWINS / f"{spec.twin_id}.yaml").read_text(encoding="utf-8"))
        for spec in SPECS
    }
    checks = verify(bases, reloaded, SPECS)

    by_base: dict[str, int] = {}
    for spec in SPECS:
        by_base[spec.base_case_id] = by_base.get(spec.base_case_id, 0) + 1
    summary = ", ".join(f"{n} of {b}" for b, n in sorted(by_base.items()))
    print(f"wrote {len(SPECS)} twins ({summary}) to {TWINS.relative_to(REPO)}/")
    for line in checks:
        print(line)
    print("all assertions passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
