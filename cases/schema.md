# Evidence record schema — v0

*Live document. Derived from what p01 actually contains (`tasks/02-milestone-1.md`
step 2), then revised in place at the 2026-08-10 owner gate (C1-C8) before any
case was built on it. Nothing course-specific belongs
here: this schema must survive pointing the project at a second zoomcamp.*

**Status: DRAFT — awaiting owner approval at the step-3 gate. No case may be
built on it until then.**

## What a record is

One YAML file per repository, `cases/records/<case_id>.yaml`, stating for
each field below what is true of that repository and where it can be
checked. A record holds **facts and their locations**, never scores and
never judgments. The extractor that produces it is `agents/extractor/v1`.

Twins (`cases/twins/`) are mutations of these records, so the field set is
also the vocabulary available to state a structural defect. A failure mode
that cannot be expressed as a diff over these fields cannot enter the case
set at all — which makes this schema, not the twin generator, the real
limit on what the project can measure.

## The two rules every field obeys

**1. Procedural, not semantic.** A field must be answerable by a reviewer
who does not read the corpus language and does not know the subject. This is
not a simplification, it is the hard constraint from
`project-evaluation-issues.md`: judging whether an evaluation question set is
*good* requires domain knowledge reviewers frequently lack. What survives is
whether evidence *exists*, is *inspectable*, and is *internally consistent*.

So: `retrieval_eval_set_size: 27` (countable) and
`retrieval_eval_relevance_rule: source_level` (readable off the scoring
function), never `retrieval_eval_questions_are_realistic`.

**2. Categorical or countable.** Values are drawn from a stated enum, or are
integers, or are booleans. Free text appears only in `basis` and
`extraction_notes`, which nothing scores. A twin must be able to flip a
field to a different legal value and have the direction of that change be
obvious by construction.

## Read-set marking — why every field carries one

Each field is marked **`scoreable`** or **`descriptive`**.

- **`scoreable`** — a criterion may plausibly read it. Degraded twins mutate
  these.
- **`descriptive`** — records what the project *is*, and no defensible
  criterion should read it. No-change twins mutate **only** these.

This marking is what makes gate G1 satisfiable by construction rather than
by hope (`objective.md` G1, decision `twin-fields-disjoint`). G1 demands
strict ordering on every degraded twin *and* exact equality on every
no-change twin; if both halves pulled on the same fields, no coarse tier
scale could satisfy both. Keeping the sets disjoint is the mechanism.

A candidate whose mapping reads a `descriptive` field fails G1's no-change
half automatically. That is the intended consequence: a criterion that moves
when Flask becomes FastAPI, or when the corpus changes subject, is
noise-sensitive, and the objective is built to catch that.

## Record structure

```yaml
schema_version: 0
case_id: p01
commit: "<40-hex>"
extracted_by: agents/extractor/v1
extracted_on: "YYYY-MM-DD"

fields:
  <field_name>:
    value: <enum member | int | bool | null>
    evidence: ["path:lines", ...]   # [] only when value is `undeterminable`
    basis: "<one line>"             # required for comparisons and counts

extraction_notes:
  - "<what the schema could not express about this repository>"
```

### `undeterminable` and `other` are different answers

Both are legal on every enum field, and conflating them loses the only
signal this schema has about its own inadequacy.

- **`undeterminable`** — *the repository does not settle the question.* The
  evidence is absent, contradictory, or the extractor could not find it.
- **`other`** — *the repository settles it clearly, and the answer is none
  of the listed values.* The actual thing is named in `basis`.

Neither is a failure. `other` is the more important of the two: a field
accumulating `other` values across the corpus is telling you its enum was
drawn from too few projects, which is the standing risk in **Schema
evolution** below.

### Evidence, `basis`, and what reads them downstream

Stated because the three consumers see different things, and a field
designed for the wrong one is wasted:

| consumer | sees | does not see |
|---|---|---|
| executable scorer (plain Python) | `value` only | `evidence`, `basis` |
| reviewer agents (Gemini, prose criteria) | `value` + `basis` | `evidence` locators, repository contents |
| humans — the owner at the M1 validation gate, the M2 spot-check, anyone auditing a finding | everything, plus the pinned clone | — |

So: **`evidence` is for human re-verification, never for scoring.** No
agent can open the files it points at — reviewer agents receive a rendered
record, not a repository, and no repository content is sent to a free-tier
provider beyond what a record contains. `basis` is the one field written to
be read by both a person and a model, which is why it must stand alone as a
sentence rather than gesture at a file.

Re-verification stays possible indefinitely: `repos.yaml` pins every commit,
so a clone is reproducible exactly, and clones persist locally under
`clones/` (gitignored — someone else's code is not ours to redistribute).

### Evidence for computed fields

A few fields are counts over the repository rather than claims located in
it. They use `evidence: ["<repo>"]` and state the exact command in `basis`.
An empty `evidence: []` means **only** `undeterminable` and never "the value
is exact but has no line number".

---

## A. System shape — `scoreable`

| field | type | values |
|---|---|---|
| `knowledge_base_present` | enum | `absent` · `present` |
| `llm_in_flow` | enum | `absent` · `present` |
| `retrieval_flow` | enum | `no_kb_no_llm` · `llm_only` · `kb_and_llm` |
| `problem_statement` | enum | `absent` · `brief` · `specific` |

`retrieval_flow` is `kb_and_llm` when the request path both queries a
knowledge base and calls an LLM. Check the request handler, not the README.

`problem_statement` is `specific` when a named section states **what
question the system answers** and **for whom**; `brief` when the topic is
named but one or both are missing; `absent` when neither. This is the one
field in the schema whose check is a judgment call, and it is confined to
the presence of two stated things rather than their quality.

## B. Interface — `scoreable`

| field | type | values |
|---|---|---|
| `interface_kind` | enum | `none` · `script_or_notebook` · `cli` · `api` · `web_ui` · `other` |
| `interface_evidence_kind` | enum | `none` · `code_only` · `code_and_screenshot` · `code_and_recording` |

`interface_evidence_kind` exists because a reviewer who cannot run a project
silently reviews its documentation instead (`project-evaluation-issues.md`,
constraints). It records whether the documentation compensates. Nothing in
the *current* criteria reads it; it is here so a candidate can.

## C. Ingestion — `scoreable`

| field | type | values |
|---|---|---|
| `ingestion_kind` | enum | `none` · `manual` · `script_or_notebook` · `orchestrated_tool` · `other` |
| `ingestion_single_command` | bool | one documented command runs it end to end |
| `ingestion_output_stated` | bool | document/chunk/vector counts are stated |

## D. Retrieval evaluation — `scoreable`

| field | type | values |
|---|---|---|
| `retrieval_eval_present` | bool | |
| `retrieval_eval_approaches_compared` | int | distinct strategies with reported numbers |
| `retrieval_eval_set_committed` | enum | `absent` · `referenced_not_committed` · `committed` |
| `retrieval_eval_set_size` | int \| null | stated or countable size |
| `retrieval_eval_relevance_rule` | enum | `none` · `source_level` · `document_level` · `passage_level` · `human_labelled` · `other` · `undeterminable` |
| `retrieval_eval_config_matches_shipped` | enum | `matches` · `differs` · `undeterminable` |
| `retrieval_eval_uncertainty_stated` | bool | any interval, variance or uncertainty statement |
| `retrieval_best_approach_shipped` | enum | `yes` · `no` · `mixed_result` · `undeterminable` |

`retrieval_eval_relevance_rule` is read off the scoring function, not the
prose: what does the code count as a hit? Coarser rules make more
retrievals count, which is the "test almost nothing can fail" failure mode
(`project-evaluation-issues.md` §3) reduced to something checkable.

`retrieval_eval_config_matches_shipped` is `differs` when any retrieval
parameter in the evaluation script differs from the request path — depth,
cut-off, model version, or a pipeline stage present in one and not the
other. Name both sides in `basis`. This is §3's "the measured system is not
the shipped system" made countable.

`retrieval_best_approach_shipped` is `mixed_result` when the reported
numbers disagree across metrics about which approach wins. That is a
distinct fact from "the best was not shipped", and collapsing the two would
lose the distinction a candidate most needs.

## E. Answer evaluation — `scoreable`

| field | type | values |
|---|---|---|
| `llm_eval_present` | bool | |
| `llm_eval_approaches_compared` | int | distinct prompts/models with reported numbers |
| `llm_eval_judge_kind` | enum | `none` · `model_judge` · `human` · `offline_metric` · `other` |
| `llm_eval_judge_spotchecked` | bool | a sample of judge verdicts checked by hand, with the result reported |
| `llm_eval_question_generator` | enum | `none_committed` · `generator_committed` · `generator_ties_question_to_passage` · `other` · `undeterminable` |
| `llm_eval_metric_at_ceiling` | bool | a reported metric sits at its maximum for effectively every item |
| `llm_eval_config_matches_shipped` | enum | `matches` · `differs` · `undeterminable` |

`llm_eval_judge_spotchecked` and `llm_eval_question_generator` together
express the circularity failure mode. Neither technique is a defect alone —
a question generated from a known passage has a known answer, and a model
judge is usable once its error rate is known. The defect is doing neither,
and it takes two fields to say that without importing taste.

`llm_eval_question_generator` asks **what is committed**, not what the
author says. An earlier draft had a `hand_written` value, decided by the
README calling the set "curated" — which is an author's claim about a
process that left no trace, and unfalsifiable either way: a generated set
and a typed set are indistinguishable once written down. Committed
generation code, by contrast, is a fact about the repository. So
`none_committed` means exactly "no generator is present, and provenance
rests on assertion" — which is the honest reading and *not* a synonym for
hand-written.

`llm_eval_metric_at_ceiling` is the unfailable-test lever: a metric every
item scores full marks on cannot discriminate, whatever it is named.

## F. Monitoring — `scoreable`

| field | type | values |
|---|---|---|
| `monitoring_kind` | enum | `none` · `feedback_only` · `dashboard_only` · `feedback_and_dashboard` · `other` |
| `monitoring_chart_count` | int | |
| `monitoring_charts_bound_to_data` | enum | `none` · `some` · `all` · `not_applicable` |

`monitoring_charts_bound_to_data` checks each panel's query against the
schema the application actually writes: does every referenced table and
column exist? This is the checkbox-padding lever, and it is structural — a
chart bound to nothing is a fact about two files, not an opinion about
dashboards.

## G. Containerization and reproducibility — `scoreable`

| field | type | values |
|---|---|---|
| `containerization_kind` | enum | `none` · `dockerfile_only` · `compose_dependencies_only` · `compose_full` · `other` |
| `run_instructions` | enum | `none` · `partial` · `complete` |
| `run_instructions_gap_count` | int | steps that cannot be carried out as written |
| `dependency_versions_pinned` | enum | `none` · `lower_bounds_only` · `lockfile_committed` · `exact_pins` · `other` |
| `data_accessible` | enum | `missing` · `manual_steps` · `automated_or_committed` · `other` |

`run_instructions` is `complete` when setup, dependencies, configuration,
required environment variables and the run command are all stated.
`dependency_versions_pinned` distinguishes a lockfile from prose pinning
because the current criteria say "versions for all dependencies are
specified" without saying where — a gap worth measuring rather than
resolving here.

`run_instructions_gap_count` comes from a **desk walk-through**: read the
documented steps in order and count those that cannot be carried out as
written, or that do not achieve what they claim — a step needing an input
the instructions never tell you to obtain, a command referring to a file or
service that no earlier step creates, an ordering that puts a dependency
after its dependent, a step whose effect a later step silently undoes. Name
each gap in `basis`.

**Trace each step into the code it invokes.** Checking only that a step's
inputs exist is not enough and produces a confident zero: p01's documented
order starts the API before ingestion, and the API builds its keyword index
once at startup, so following the instructions exactly yields a system whose
hybrid search is silently dense-only. Nothing about that is visible from the
README alone. The gap was found by the owner running the project, not by the
first walk-through — which is itself the evidence for how deep the tracing
has to go.

Nothing is executed, and the field deliberately does **not** ask whether the
project works. That is unanswerable without running it, and running other
people's capstone code is exactly what the reviewer-time and reviewer-cost
gates exist to bound. What is checkable is whether the written procedure is
self-contained — which is also the honest thing to ask of a reviewer who
cannot run the project either, and who today silently reviews the
documentation instead (`project-evaluation-issues.md`, constraints).

A count rather than an enum: `complete`/`partial` cannot distinguish one
missing `export` from a procedure that never populates its index, and a
count lets a twin move the field by exactly one gap.

## H. Techniques — `scoreable`

One block per technique, keys `hybrid_search`, `reranking`,
`query_rewriting`:

| sub-field | type | values |
|---|---|---|
| `present` | bool | implemented in the repository |
| `shipped_enabled` | bool | active on the request path, not merely present |
| `evaluated` | bool | its effect is measured and the numbers reported |
| `measured_effect` | enum | `improves` · `mixed` · `hurts` · `not_measured` |

This is the harmful-component-kept lever, and the reason it needs four
sub-fields rather than one. The current criteria award a point for
presence, so `present: true` alone earns it — which is exactly the incentive
gradient diagnosed in `project-evaluation-issues.md` §2: shipping a
component whose own numbers show it hurts is the safer bet, because credit
requires nobody to read anything.

`measured_effect` is read off the project's **own reported numbers**, never
from a view about whether the component ought to help. `mixed` when the
reported metrics disagree with each other.

## I. Deployment and bonus — `scoreable`

| field | type | values |
|---|---|---|
| `cloud_deployment` | enum | `none` · `documented_only` · `deployment_code_committed` · `other` |

## J. Documentation accuracy — `scoreable`

Nothing in the current criteria reads this group. It exists because
`project-evaluation-issues.md` §4 says nothing scores whether the
documentation is true, and a candidate cannot repair that without fields to
read.

| field | type | values |
|---|---|---|
| `headline_numbers_traceable` | enum | `no_numbers` · `none_traceable` · `some_traceable` · `all_traceable` |
| `untraceable_number_count` | int | headline figures with no committed artifact behind them |
| `document_number_conflicts` | int | figures that disagree between two committed documents |
| `limitations_section` | enum | `absent` · `cosmetic_only` · `includes_structural` |
| `artifact_reference_strength` | enum | `all_linked` · `all_referenced` · `partially_referenced` · `none` |
| `artifacts_unreferenced_count` | int | expected artifacts named nowhere in the documentation |

A headline number is *traceable* when a committed artifact is **able to
produce it** — a script, a notebook, a stored results file. Checking
traceability still means reading, never running: agreeing with the number is
not required and neither is reproducing it.

But "an artifact exists with a plausible name" is not the test, and an
earlier draft of this paragraph said it was. A notebook that references
names it never imports cannot produce anything, and notebook formats that
store no outputs (marimo `.py`, or `.ipynb` committed with outputs
stripped) carry no numbers of their own. Both were found in p01, where they
turned an `all_traceable` reading into 18 figures with nothing behind them.
So the check is: **would this artifact, read as committed, yield the
reported figure?** Undefined names, absent inputs and stripped outputs all
answer no.

`limitations_section` is `includes_structural` when at least one named
limitation concerns the system's own method or measurement, rather than only
its hardware, scope or budget. The check is which of the two a stated
limitation is about — not whether the list is complete, which nobody can
verify.

`document_number_conflicts` is a **count**, not a verdict. An earlier draft
had a `consistent`/`inconsistent` enum, which spanned everything from a
rounding difference to a repository whose every figure disagrees with every
other — one bucket for two unrelated situations, and a twin could only move
it by flipping the whole thing. Each conflict is named in `basis` with both
sides cited, so the number is auditable rather than asserted.

### Reachability — the unlocatable-project lever

Two fields, because an earlier single enum conflated *how strongly*
artifacts are referenced with *how many* are not referenced at all.

`artifact_reference_strength` grades the weakest reference among the
artifacts present:

- `all_linked` — every expected artifact is reached by a markdown link.
- `all_referenced` — every expected artifact is at least *named* by path
  somewhere in the documentation: a link, a code span, or a plain-text
  project tree. A reviewer can find it.
- `partially_referenced` — at least one expected artifact is named nowhere.
- `none` — no expected artifact is referenced at all.

A plain-text path counts, because a reviewer follows one without difficulty
and the failure mode being captured is *"the artifact exists and nothing
points at it"*, not *"the pointer was not a hyperlink"*. Requiring links
would have scored nearly every repository the same way, and a field constant
across the corpus discriminates nothing.

`artifacts_unreferenced_count` carries the magnitude, over a **fixed
checklist** so the denominator is not the extractor's opinion: evaluation
script or notebook · evaluation question set · monitoring dashboard
definition · ingestion entry point · deployment configuration. Artifacts the
project does not have are excluded from the count, never counted as
unreferenced — this field measures findability, and `containerization_kind`
and friends already measure existence.

Both are facts about the repository's reference graph. "Badly written" is
not, and only the former is admissible (decision
`unlocatable-twin-is-structural`).

## K. Descriptive — `descriptive`, never read by any criterion

| field | type | values |
|---|---|---|
| `corpus_language` | string | primary language of the indexed corpus |
| `corpus_domain` | string | free-text subject label |
| `interface_framework` | string | e.g. `flask`, `streamlit`, `fastapi` |
| `vector_store` | string | e.g. `qdrant`, `elasticsearch`, `in_memory` |
| `llm_provider` | string | e.g. `openai`, `ollama` |
| `repo_file_count` | int | tracked files at the pinned commit |

These exist **so that no-change twins have somewhere to mutate**. A
criterion reading any of them would score a project for choosing Flask over
Streamlit, or for being about wine rather than manufacturing — which is
noise, and G1's no-change half exists to catch precisely that.

Note the asymmetry, deliberate and stated: `interface_framework` is
descriptive while `interface_kind` is scoreable. *Whether* a project has a
web interface is creditable; *which framework* built it is not.

---

## Schema evolution — the ceiling this schema puts on the project

**The standing risk, stated plainly: a schema drawn from the current
criteria can only discover criteria expressible in the current criteria's
vocabulary.** Several fields here are inherited wholesale from the
instrument under study — `ingestion_kind`'s values are the current rubric's
own tiers, and `interface_kind`'s nearly are. Others were drawn from one
person's reading of a handful of projects. Both are how a measuring
instrument quietly reproduces what it was built to question, and no amount
of care inside a fixed field list escapes it.

Two things are done about it, and the second matters more:

**Fields the current criteria cannot read already exist.** Groups D, E, H
and J were built from the *diagnosis*, not the rubric — judge spot-checking,
measured-versus-shipped configuration, per-technique measured effect,
traceability of headline numbers. A candidate can score things v0 structurally
cannot. This widens the vocabulary; it does not make it complete.

**The schema takes proposals, and never from itself.** Any agent in the loop
may propose (a) a new value for an existing enum or (b) a new field — but
proposes only. Entry requires owner approval, on the same footing as
red-team case-set additions (`redteam-cases-via-owner`) and for the same
reason: an agent that can extend what measures it will. Proposals are not
free-form opinion; each must cite the structured evidence that already
accumulates for exactly this purpose:

- **`other` values.** A field returning `other` across several repositories
  is direct evidence its enum was drawn from too few projects, and `basis`
  already names what the real value was.
- **`extraction_notes`.** Every record ends with what the schema could not
  express about that repository. That list is the proposal queue.
- **`undeterminable` clusters.** A field the corpus routinely cannot settle
  is badly posed, not merely unlucky.

**Timing is a cost, not a detail.** A schema change invalidates every record
written under the old one, so proposals land *before* the M2 case-set
sealing, where re-extraction is cheap because it is happening anyway. After
sealing, a schema change costs a full re-extraction of the corpus and a
re-run of every measurement — payable, but never accidental. The version
in `schema_version` is what makes a stale record detectable rather than
silently mixed in.

## Known limits of this schema

- **Built from one repository.** It fits p01 by construction. What it fails
  to express about p02 is a finding, not a defect to patch away quietly —
  and p02 is noted domain-opaque, so it also tests rule 1 above.
- **Tautology risk, inherited.** Twins written against the same schema the
  scorer reads risk proving only that a candidate detects the categories
  someone already named (`plan.md`; decision `g1-claims-catalogue-coverage`).
  A G1 pass is claimed as catalogue coverage only.
- **`problem_statement` is the weakest field**, being the only one whose
  check is a judgment. It is kept because the current criteria score it and
  v0 must be transcribed faithfully. If extraction of p02 disagrees with the
  owner's reading here, that is the field to cut first.

  It has a sharper defect than judgment, found at the M1 gate: the field
  records that an audience and a question are **stated**, never that they
  **cohere**. p01 states its audience as tourists and answers exclusively in
  Portuguese — a combination that scores `specific` while describing a
  system its stated users largely cannot read. Coherence of that kind is not
  procedurally checkable (deciding tourists do not read Portuguese is world
  knowledge, not a fact in the repository), so the schema does not attempt
  it. What the field measures is therefore narrower than its name suggests,
  and any criterion reading it inherits that. Recorded rather than repaired.
- **Extraction is one pass by one model.** The record→score step is what
  twins validate; the repo→record step is covered only by the two
  `owner_reviewed` repos and a later spot-check (`plan.md`).
