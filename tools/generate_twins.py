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

REPO = pathlib.Path(__file__).resolve().parent.parent
RECORDS = REPO / "cases" / "records"
TWINS = REPO / "cases" / "twins"

BASE_CASE = "p01"

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
#   kind "int" / "int_or_null" / "bool" / "str" / "list_str": allowed is None
FIELD_SPEC: dict[str, tuple[str, str, list[str] | None]] = {
    # A. System shape
    "knowledge_base_present": (SCOREABLE, "enum", ["absent", "present"]),
    "llm_in_flow": (SCOREABLE, "enum", ["absent", "present"]),
    "retrieval_flow": (SCOREABLE, "enum", ["no_kb_no_llm", "llm_only", "kb_and_llm"]),
    "problem_statement": (SCOREABLE, "enum", ["absent", "brief", "specific"]),
    # B. Interface
    "interface_kind": (SCOREABLE, "enum", ["none", "script_or_notebook", "cli", "api", "web_ui", "other"]),
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
    "retrieval_eval_relevance_rule": (SCOREABLE, "enum", [
        "none", "source_level", "document_level", "passage_level", "human_labelled", "other", "undeterminable"]),
    "retrieval_eval_config_matches_shipped": (SCOREABLE, "enum", ["matches", "differs", "undeterminable"]),
    "retrieval_eval_uncertainty_stated": (SCOREABLE, "bool", None),
    "retrieval_best_approach_shipped": (SCOREABLE, "enum", ["yes", "no", "mixed_result", "undeterminable"]),
    # E. Answer evaluation
    "llm_eval_present": (SCOREABLE, "bool", None),
    "llm_eval_approaches_compared": (SCOREABLE, "int", None),
    "llm_eval_judge_kind": (SCOREABLE, "enum", ["none", "model_judge", "human", "offline_metric", "other"]),
    "llm_eval_judge_spotchecked": (SCOREABLE, "bool", None),
    "llm_eval_question_generator": (SCOREABLE, "enum", [
        "none_committed", "generator_committed", "generator_ties_question_to_passage", "other", "undeterminable"]),
    "llm_eval_metric_at_ceiling": (SCOREABLE, "bool", None),
    "llm_eval_role_overlap": (SCOREABLE, "enum", ["distinct", "same_family", "same_model", "undeterminable"]),
    "llm_eval_config_matches_shipped": (SCOREABLE, "enum", ["matches", "differs", "undeterminable"]),
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
}

# H. Techniques — one block per technique, same sub-fields, all scoreable.
TECHNIQUES = ["hybrid_search", "reranking", "query_rewriting"]
TECHNIQUE_SPEC: dict[str, tuple[str, str, list[str] | None]] = {
    "present": (SCOREABLE, "bool", None),
    "shipped_enabled": (SCOREABLE, "bool", None),
    "evaluated": (SCOREABLE, "bool", None),
    "measured_effect": (SCOREABLE, "enum", ["improves", "mixed", "hurts", "not_measured"]),
    "decision_documented": (SCOREABLE, "bool", None),
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
                path="fields.reranking.decision_documented.basis",
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
            "decision_documented, decision_axes and retrieval_best_approach_shipped. No relation to p01 "
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
                path="fields.reranking.decision_documented.value",
                after=True,
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
                    "with `decision_documented: true`, whose schema definition is 'stated AND justified by "
                    "the project's own measurements'; an empty axis list would assert the justification rests "
                    "on nothing measured."
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
                path="fields.reranking.decision_documented.basis",
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
    elif kind == "bool":
        assert isinstance(value, bool), f"{label}: expected bool, got {value!r}"
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


def verify(base: dict, written: dict[str, dict], specs: tuple[TwinSpec, ...]) -> list[str]:
    """Re-derive every claim from the files on disk. Returns the checks run."""
    checks: list[str] = []
    base_flat = flatten({k: v for k, v in base.items() if k != "case_id"})

    for spec in specs:
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
        "fields.reranking.decision_documented",
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
    base_path = RECORDS / f"{BASE_CASE}.yaml"
    base = yaml.safe_load(base_path.read_text(encoding="utf-8"))

    unknown = [n for n in base["fields"] if n not in FIELD_SPEC and n not in TECHNIQUES]
    if unknown:
        print(f"base record has fields absent from FIELD_SPEC: {unknown}", file=sys.stderr)
        return 1
    missing = [n for n in FIELD_SPEC if n not in base["fields"]]
    if missing:
        print(f"note: schema fields absent from {BASE_CASE}: {missing}")

    TWINS.mkdir(parents=True, exist_ok=True)
    written: dict[str, dict] = {}
    for spec in SPECS:
        doc = build(base, spec)
        (TWINS / f"{spec.twin_id}.yaml").write_text(dump(doc), encoding="utf-8")
        written[spec.twin_id] = doc

    reloaded = {
        spec.twin_id: yaml.safe_load((TWINS / f"{spec.twin_id}.yaml").read_text(encoding="utf-8"))
        for spec in SPECS
    }
    checks = verify(base, reloaded, SPECS)

    print(f"wrote {len(SPECS)} twins of {BASE_CASE} to {TWINS.relative_to(REPO)}/")
    for line in checks:
        print(line)
    print("all assertions passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
