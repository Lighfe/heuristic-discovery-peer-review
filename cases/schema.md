# Evidence record schema — v0

*Live document. Derived from what p01 actually contains (`tasks/02-milestone-1.md`
step 2), then revised in place at the 2026-08-10 owner gate (C1-C8) before any
case was built on it. Nothing course-specific belongs
here: this schema must survive pointing the project at a second zoomcamp.*

**Status: M2 SCHEMA CLOSURE COMPLETE, STEP 8 SEALING CHECKLIST RESOLVED
(updated 2026-08-19).** `schema_version` bumped 0 → 1 at step 2's
sign-off (2026-08-13); the 22-repo corpus was re-extracted under it at
step 3, the twin catalogue built at step 5, and step 7's independent
fidelity diff found and fixed two `candidates/v0/criteria.yaml`
transcription defects (`runs/2026-08-18-m2-v0-fidelity-diff/`). The step
8 sealing-readiness checklist (`runs/2026-08-18-m2-sealing-checklist/checklist.md`)
is fully worked through and closed — every item resolved, one (3e,
`retrieval_best_approach_shipped`) closed as a named, accepted open risk
rather than fixed; see that field's entry below and `docs/decisions.md`
`retrieval-best-approach-not-normalised-open`. Sealing itself (the
`tasks/03-milestone-2.md` step 8 owner gate proper) is a separate act from
this checklist and happens next, in `docs/decisions.md`.

**Post-sign-off edit, ratified (2026-08-14, confirmed at the M2 sealing
review 2026-08-18):** group H below gained a worked YAML example during
step 3 (re-extraction), after this schema was supposed to have stopped
moving per step 2's sign-off. Made without asking first — a process
violation of the same kind item 3e's handling was written to avoid,
caught by owner review after the fact, not before. Recorded honestly
rather than folded in silently: see `docs/decisions.md`
`group-h-worked-example-post-hoc`. **This edit is documentation-only and
does not change `schema_version`**: it adds no field, no value, no rule
not already implied by "Record structure" above (every leaf is `{value,
evidence, basis}`) — it makes an existing rule concrete after three
independent extractors misread it, rather than stating a new one. No
record needs re-checking against it for that reason alone.

The freeze is deliberate and its reason is arithmetic: a schema change
before M2 sealing is free, because the corpus is being extracted then
anyway; after sealing it costs a full re-extraction plus a re-run of every
measurement. M1's deliverable is the twin baseline, and no further schema
round-trip buys anything toward it.

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

## Domain vs. general knowledge

Rule 1 bars *subject-matter* knowledge — a reviewer answering a field must
not need to understand the corpus domain or read its language. It does
**not** bar general programming or library knowledge: knowing that
`pandas.read_json(dtype={'id', str})` passes a set rather than a mapping
and fails, or that bash `echo` needs `-e` to interpret `\n`, or that a named
image ships a UI, is ordinary software knowledge, not domain expertise, and
is admissible.

**When such knowledge is load-bearing for a value, the record states so in
`extraction_notes`.** This is not a simplification of rule 1 — it is
the rule the owner already applied at the M1 gate (p02's
`run_instructions_gap_count` and monitoring fields), made explicit so two
extractors agree on what they are allowed to know. Without the rule
written down, that agreement is accidental.

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

**The disjointness holds for `value`, not automatically for `basis` (M2).**
A *scoreable* field's `basis` sentence can still embed a *descriptive* fact
in prose (naming the audience, the corpus domain, a vendor) even though its
`value` never does — which silently reintroduces the leak the marking
exists to prevent, for two of the three no-change twin kinds
(`deferred-to-m2.md` §3c). `agents/extractor/v2` states the rule that
closes this going forward: a scoreable field's `basis` states only the
fact being scored, never incidental descriptive context.

## Record structure

```yaml
schema_version: 1
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

### Locators inside notebooks

`.ipynb` files are JSON, so a line number points at an escaped string rather
than at code a reader can find. Notebook evidence therefore uses
**`path:cellN`**, with N the zero-based index into the `cells` array:
`notebooks/rag.ipynb:cell17`. Several cells are cited as
`path:cellN,cellM`.

Stated here because the p02 extraction hit this and invented the convention
mid-run. The convention it chose was the right one, but a locator format
decided per-run is not comparable between records, and an extractor
inventing schema is exactly what `schema-proposals-via-owner` exists to
prevent. Formats belong in the schema, not in an agent's judgment.

Plain `.py` notebooks (marimo, jupytext) are ordinary source files and use
`path:lines`.

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
| `interface_kind` | list[enum] | one or more of `none` · `script_or_notebook` · `cli` · `api` · `web_ui` · `other` (M2; was a single enum) |
| `interface_evidence_kind` | enum | `none` · `code_only` · `code_and_screenshot` · `code_and_recording` |

`interface_evidence_kind` exists because a reviewer who cannot run a project
silently reviews its documentation instead (`project-evaluation-issues.md`,
constraints). It records whether the documentation compensates. Nothing in
the *current* criteria reads it; it is here so a candidate can.

**`interface_kind` is a list (M2).** A single enum forces a project
offering both a web UI and an API — or, as found repeatedly across the
corpus (p01, p02, p08, p11), two separate interfaces — into one value,
silently dropping the other. `none` appears only as the sole element of an
empty-interface record. A criterion reading a single interface still works
unchanged (`{interface_kind: {in: [web_ui, api]}}` now matches if *any*
element of the list is in the set — see `candidates/v0/score.py`'s
membership-test update, `sampling-in-cache-key`-adjacent but a scorer
change, not a protocol one).

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
| `retrieval_eval_match_strictness` | enum | `none` · `source_level` · `document_level` · `passage_level` · `other` · `undeterminable` |
| `retrieval_eval_label_origin` | enum | `none` · `human_labelled` · `generated` · `mixed` · `other` · `undeterminable` |
| `retrieval_eval_config_matches_shipped` | enum | `matches` · `differs` · `undeterminable` |
| `retrieval_eval_uncertainty_stated` | bool | any interval, variance or uncertainty statement |
| `retrieval_best_approach_shipped` | enum | `yes` · `no` · `mixed_result` · `undeterminable` |
| `retrieval_eval_reproducible` | enum | `reproducible_as_committed` · `traceable_not_reproducible` · `neither` |

**Split into two fields (M2, step 8 sealing review) — was one field,
`retrieval_eval_relevance_rule`.** The original field conflated two
separate facts: *how strict the match is* (does a hit require the same
document, the same passage, the same source only) and *who produced the
ground-truth label being matched against* (a human hand-assigned it, a
generator produced it, neither is known). Two independent extractions of
the same repository (p03) read the same fact — a human hand-paired each
question to a target chunk_id, then the scoring function exact-matched on
that id — and landed on different values, one describing the mechanism
(`passage_level`), one describing the provenance (`human_labelled`),
because the field could only hold one answer for two different questions.

`retrieval_eval_match_strictness` is read off the scoring function, not
the prose: what does the code count as a hit? Coarser rules make more
retrievals count, which is the "test almost nothing can fail" failure mode
(`project-evaluation-issues.md` §3) reduced to something checkable. This
is what the old field measured in every record except p03's genuine
ambiguity.

`retrieval_eval_label_origin` records whether the ground-truth label a
retrieval is checked against was assigned by a person, produced by a
committed generator, or can't be determined from what's stated. Filled at
the M2 sealing review from each record's *already-recorded* basis text for
the old field, not a fresh repository read: `human_labelled` where that
text explicitly says a person assigned the label (p03 only, currently);
`none` where no retrieval evaluation exists to have a label at all;
`undeterminable` everywhere else, because the old field's basis text was
written to answer the strictness question, not the provenance one, and
usually says nothing about who produced the label. **This is expected,
not a defect**: it reflects that group D never tracked question-set
provenance the way group E's `llm_eval_question_generator` does, not that
the fact is unknowable — a future extraction could resolve most of these
`undeterminable`s by reading the repository specifically for this
question, which the M2 sealing-review backfill deliberately did not do.

`retrieval_eval_config_matches_shipped` is `differs` when any retrieval
parameter in the evaluation script differs from the request path — depth,
cut-off, model version, or a pipeline stage present in one and not the
other. Name both sides in `basis`. This is §3's "the measured system is not
the shipped system" made countable.

`retrieval_best_approach_shipped` is `mixed_result` when the reported
numbers disagree across metrics about which approach wins. That is a
distinct fact from "the best was not shipped", and collapsing the two would
lose the distinction a candidate most needs.

`retrieval_eval_reproducible` (M2) states whether the retrieval-evaluation
*pipeline itself* can be trusted, independent of what it reports:

- `reproducible_as_committed` — a committed script or notebook, run as
  committed, would regenerate the reported figures from committed inputs:
  no missing imports, no unexecuted cells, no undefined names, no
  silently-dropped denominator.
- `traceable_not_reproducible` — the number cannot be regenerated by
  running committed code, but every step from evaluation set to reported
  figure is still inspectable by reading committed artifacts.
- `neither` — neither holds.

This replaces a four-sub-field sketch the owner rejected as overfit to two
specific repositories. It does not subsume `document_code_conflicts`
(group J — a reported figure the code cannot reach) or
`headline_numbers_traceable` (also group J — whether an artifact exists
that could produce a number at all); it is specifically about whether the
*evaluation pipeline*, if run, would work.

**`retrieval_best_approach_shipped` is not normalised, and this revision
does not fix it (M2, `deferred-to-m2.md` §3e, open).** The field is a
hand-maintained summary of the per-technique `measured_effect` values in
group H; a twin changing one technique's measured effect can make this
field stale without a corresponding edit, which is why
`twin-entailed-change-scoped` had to be invented at all. The permanent fix
— deriving this value from the H blocks at scoring time instead of storing
it — is deferred pending a precise, owner-reviewed derivation rule: this
field anchors the single most contested interpretation in v0
(`retrieval-best-approach-reading-flagged`, findings F2/F3), and a
derivation formula written without that review would just relocate the
judgment call, not remove it. The field stays as written, hand-maintained,
until that rule exists.

## E. Answer evaluation — `scoreable`

| field | type | values |
|---|---|---|
| `llm_eval_present` | bool | |
| `llm_eval_approaches_compared` | int | distinct prompts/models with reported numbers |
| `llm_eval_judge_kind` | enum | `none` · `model_judge` · `human` · `offline_metric` · `other` |
| `llm_eval_judge_spotchecked` | bool | a sample of judge verdicts checked by hand, with the result reported |
| `llm_eval_question_generator` | enum | `none_committed` · `generator_committed` · `generator_ties_question_to_passage` · `other` · `undeterminable` |
| `llm_eval_metric_at_ceiling` | bool \| null | a reported metric is at ceiling per the defined rule below; `null` when no aggregate metric exists to check |
| `llm_eval_role_overlap` | enum | `distinct` · `same_family` · `same_model` · `undeterminable` |
| `llm_eval_config_matches_shipped` | enum | `matches` · `differs` · `undeterminable` |
| `llm_eval_reproducible` | enum | `reproducible_as_committed` · `traceable_not_reproducible` · `neither` |

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

`llm_eval_metric_at_ceiling` is the unfailable-test lever. It is `true` when
a reported metric sits at its maximum for effectively every item — p01
reports faithfulness of **5.00 out of 5**, meaning all 27 items scored full
marks. A measurement nothing fails ranks nothing: it cannot separate a good
system from a bad one, so it carries no information about the system even
though it looks like a result. The field does not say the system is bad or
good; it says the *measurement* has no discriminating power, which is a fact
about the reported numbers and needs no view about the subject matter.
Contrast p02, whose judge scores are 0.805 and 0.969 — below ceiling, so the
metric could in principle have come out worse.

**Ceiling threshold, defined (M2):** a reported metric is *at ceiling* when
at least 95% of scored items achieve that metric's best possible value,
where "best" is the metric's own stated direction — maximum for a
quality/relevance score, **minimum for an error, refusal, or failure
rate**. 95% matches the G4 ceiling-check threshold already frozen in
`objective.md` (`agreement-protocol-ceiling`) rather than inventing a
second number. `value` is `true` iff at least one reported metric qualifies
— evaluated per metric, **never averaged across metrics**: a mean would
hide exactly the one-maxed-metric-among-several case this field exists to
catch. `basis` states each reported metric's direction and per-metric
ceiling status. Where no aggregate metric exists at all (an evaluation
attempted but never completed, or no static aggregate committed), the
value is `null`, not `false` — there is nothing to check for ceiling
behavior, which is a different fact from "checked, and not at ceiling."
(p06's judge emits a categorical label with no committed numeric
aggregate; its `null` value predates this rule and is consistent with it.)

`llm_eval_role_overlap` records how many roles one model occupies:
generating the question set, being a system under comparison, and judging.
p02 has one model in all three, including judging a comparison it loses.
The field states the fact and leaves the consequence to a criterion,
deliberately: each call runs in a fresh context, so this is not information
leaking between roles, and the owner's position (M1 gate) is that shared
identity is weaker evidence of circularity than it first appears. What
remains is shared inductive bias — a judge that makes the same mistakes as
the generator scores them as correct — which is real but is a tendency, not
a defect the schema should assert. `same_family` covers different sizes of
one model line.

`llm_eval_reproducible` (M2) is the answer-evaluation counterpart to
`retrieval_eval_reproducible` (group D) — same three values, same
definitions, applied to the answer-evaluation pipeline: judge run,
question set, generation calls. It states whether the pipeline itself
would work if run, not whether its reported numbers are good.

**When `llm_eval_question_generator` is `none_committed` (M2):** the
generator role has no model in it — there is nothing to overlap with. This
field then compares only the answer-generator and judge roles, and
`basis` must say so explicitly. p01 is exactly this case: its recorded
`same_family` reflects the answer-generator/judge pair only, not a
three-way comparison.

## F. Monitoring — `scoreable`

| field | type | values |
|---|---|---|
| `monitoring_kind` | enum | `none` · `feedback_only` · `dashboard_only` · `feedback_and_dashboard` · `other` |
| `monitoring_dashboard_provenance` | enum | `none` · `committed_definitions` · `stock_tool_ui` · `other` |
| `monitoring_instrumentation` | enum | `none` · `logged` · `traced_on_request_path` |
| `monitoring_chart_count` | int \| null | committed panel definitions; `null` when not applicable |
| `monitoring_charts_bound_to_data` | enum | `none` · `some` · `all` · `not_applicable` |

`monitoring_dashboard_provenance` exists because counting committed panels
silently misreads a whole class of project. p02 deploys a stock
observability image whose UI shows request traces and latency out of the
box; nothing is committed, so a panel count returns **0** — the same value a
project with no monitoring at all gets, while the reviewer is looking at a
working dashboard. The two are opposite situations and the count cannot tell
them apart.

So `monitoring_chart_count` counts **committed panel definitions only**, and
is `null` — not `0` — whenever `monitoring_dashboard_provenance` is
`stock_tool_ui`. `0` then means what it should: a dashboard was defined and
has no panels.

`monitoring_instrumentation` carries the half a panel count cannot see: what
the application itself does. p02 emits OpenTelemetry spans from its retrieval
and serving paths, so the traces a reviewer sees are produced by the
project's own code even though no dashboard is committed. Counting panels
scored that as *nothing*, for a project that had done strictly more work
than one committing a three-panel Grafana JSON. `traced_on_request_path`
means instrumentation runs where requests are served; `logged` means
records are written but nothing is wired to a viewer.

Neither field decides whether a stock tool *should* score as well as a built
dashboard. Together they make the distinction visible so a criterion can
decide, which is the schema's job and not the schema's call.

**The `logged`/`traced_on_request_path` boundary, made literal (M2, step 8
sealing review).** This recurred as a flagged ambiguity on several
records — extractors kept reading it as "is this OpenTelemetry-style
tracing specifically," which the field was never meant to require. Read
the definitions literally instead, as a two-part test: (1) does something
run **during** request handling (not only on an explicit user action like
a feedback click), and (2) is what it writes **consumed by a viewer**
(a dashboard, not just a file nothing reads)? Both true →
`traced_on_request_path`, regardless of whether a tracing/span library is
involved — a synchronous DB write inside the request handler that feeds a
committed dashboard qualifies just as much as OpenTelemetry spans do.
Either false → `logged` (something is written, but not both conditions
hold). Applying this test directly to two records that were flagged as
ambiguous corrected real misclassifications: p05 and p09 were both
`logged` despite a per-request write feeding a real, committed dashboard —
both now `traced_on_request_path`. A third record initially suspected of
the same problem, p12, is genuinely different under the same test: its
write only happens when a user clicks a feedback button (not on every
request) and lands in a CSV with no confirmed viewer — `logged` is correct
there. One record resolving under this test does not confirm every other
flagged record reads the same way; each was checked individually, not
assumed from the pattern.

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

**`run_instructions` and `run_instructions_gap_count` measure different
things and are not redundant (M2).** The enum measures *coverage* — does
the written procedure name every required step category. The count
measures *correctness* — does each named step actually work. A record can
correctly hold `run_instructions: complete` alongside a nonzero gap count:
p01's procedure names every category and is still unrunnable in three
places. **A criterion checking whether the instructions actually work
should read the count, never the enum alone** — reading only the enum
answers a different question than it looks like it answers. v0 currently
reads only the enum, faithfully transcribing the current guidance's own
conflation of the two; this is unchanged (`v0-literal-no-inferences`).

**`data_accessible` is defined (M2, step 8 sealing review).** Previously a
bare enum with no prose — every sibling field in this section has one,
this one didn't. Owner ruling:

- **`manual_steps`** — the data source is named **and** access
  instructions are given: a download link plus destination, or a named
  API/key that is free to obtain (not the project's own LLM API key,
  which is a separate reproducibility concern the schema tracks
  elsewhere). A reader could follow the documented steps and get the data.
- **`other`** — the data source is named but **no** access instructions
  are given (e.g. "the corpus is proprietary hospital records" with
  nothing else stated: what it is, but not how to get it). This is the
  value that answers the guidance's "unclear how to access it" disjunct
  (see `reproducibility`, group above M2's tier-order fix).
- The distinction is whether instructions exist, not whether the source
  is easy to reach: a key-gated source with a stated request process is
  `manual_steps`; the same source with no stated process is `other`.

Checked directly against the corpus at the time this was written: `other`
had never been used for this field (`missing`: 1, `manual_steps`: 1,
`automated_or_committed`: 21) — no empirical precedent existed to conflict
with this ruling. The one `manual_steps` record (p05: "the rest require
fetching from an external, key-gated source with no key or cached copy in
the repository, and **no single documented command performs that
fetch**") reads, under this definition, as `other` — source named, no
access instructions given — and was corrected.

## H. Techniques — `scoreable`

One block per technique, keys `hybrid_search`, `reranking`,
`query_rewriting`. **Each sub-field below is its own leaf — a
`{value, evidence, basis}` mapping, exactly like every other field in this
schema — nested one level deeper under the technique name, never a bare
value.** This has been the single most common structural mistake extractors
make (found and fixed in three separate M2 extractions): writing
`hybrid_search: {present: true, ...}` with bare values instead of
`hybrid_search: {present: {value: true, evidence: [...], basis: "..."}, ...}`.
Worked example, one technique, fully nested:

```yaml
fields:
  hybrid_search:
    present:
      value: true
      evidence: ["src/rag.py:40-58"]
      basis: "combines BM25 and vector search results before reranking"
    shipped_enabled:
      value: true
      evidence: ["src/rag.py:12"]
      basis: "HYBRID_SEARCH=true is the shipped default"
    evaluated:
      value: true
      evidence: ["notebooks/eval.ipynb:cell9"]
      basis: "hit rate/MRR computed for hybrid vs. vector-only"
    measured_effect:
      value: improves
      evidence: ["notebooks/eval.ipynb:cell9"]
      basis: "hybrid MRR 0.81 vs. vector-only MRR 0.74"
    decision_basis:
      value: measured
      evidence: ["README.md:120-124"]
      basis: "shipped because it wins on the project's own MRR comparison"
    decision_axes:
      value: ["mrr", "hit_rate"]
      evidence: ["README.md:120-124"]
      basis: "quantities named in the decision_basis justification above"
```

| sub-field | type | values |
|---|---|---|
| `present` | bool | implemented in the repository |
| `shipped_enabled` | bool | active on the request path, not merely present |
| `evaluated` | bool | its effect is measured and the numbers reported |
| `measured_effect` | enum | `improves` · `mixed` · `hurts` · `not_measured` |
| `decision_basis` | enum | `none` · `argued` · `measured` — see below (M2; was `decision_documented: bool`) |
| `decision_axes` | list[str] | which measured quantities the stated justification rests on |

This is the harmful-component-kept lever, and the reason it needs four
sub-fields rather than one. The current criteria award a point for
presence, so `present: true` alone earns it — which is exactly the incentive
gradient diagnosed in `project-evaluation-issues.md` §2: shipping a
component whose own numbers show it hurts is the safer bet, because credit
requires nobody to read anything.

`measured_effect` is read off the project's **own reported numbers**, never
from a view about whether the component ought to help. `mixed` when the
reported metrics disagree with each other.

`decision_basis` is the field that makes a **documented removal**
visible, and without it the schema could only ever record the negative half
of one. p02 implements a reranker, measures it, and rejects it: MRR improves
but latency rises more than tenfold, and the README says so and says why.
Under the earlier field set that repository was indistinguishable from one
that built a reranker and silently dropped it — `shipped_enabled: false`,
`measured_effect: mixed`, nothing else. The author had in fact done the
exact thing a course on evaluation is trying to teach.

This is the incentive gradient of `project-evaluation-issues.md` §2 reduced
to a checkable fact. Shipping a component is visible in the file tree;
measuring one and removing it is visible only if someone reads the write-up.
A criterion cannot reward the second path unless a field carries it.

**Three-way, not boolean (M2, was `decision_documented: bool`).** A bool
named "documented" reads as "a reason was stated," but the field actually
required more: a choice stated **and** justified by the project's own
measurements. p02's original hybrid-search argument (dense embeddings suit
the domain, on a-priori grounds, no measurement cited) is a real,
documented reason that nonetheless answered `false` under the old
definition — correct under the schema as written, but surprising to
anyone checking the field by its name alone. `decision_basis` states which
case holds:

- `none` — no ship/do-not-ship reasoning is stated at all.
- `argued` — a reason is stated, but rests on a-priori reasoning rather
  than the project's own measurements (p02's original hybrid-search case).
- `measured` — the choice is tied to the project's own reported numbers
  (p02's reranker rejection; the old `true`).

A criterion may still collapse `argued` and `measured` together if it
wants the old boolean behavior; the field now lets one that cares about
the distinction read it.

`decision_axes` names the quantities the justification rests on — e.g.
`["mrr", "hit_rate", "latency", "token costs"]` — because a project may decide on an axis
the retrieval metrics do not cover. p02 decided on latency, which
`measured_effect` cannot see at all: read on retrieval quality alone the
rejection looks unmotivated, and the schema would misreport a reasoned
decision as an arbitrary one. Record the axes the project actually argued
from, not the ones a criterion happens to score.

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
| `untraceable_number_count` | int | **individual reported figures** with no committed artifact able to produce them |
| `document_number_conflicts` | int | figures that disagree between two committed **documents** |
| `document_code_conflicts` | int | claims the committed **code** contradicts |
| `broken_reference_count` | int | documented paths or artifacts that do not exist |
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

`untraceable_number_count` counts **individual figures**, not results
tables or claims: a four-row table of four metrics is sixteen figures. The
rule is stated because it was not, and two extractions free to choose
between "figures", "rows" and "claims" produce numbers that cannot be
compared across repositories even when both are careful.

`document_code_conflicts` is the field two repositories independently
needed and neither had. A claim can disagree with another document — that is
`document_number_conflicts` — or it can disagree with the code, which is a
different and usually worse fact. p01 reports a retrieval hit rate of 52%
while its own scoring function and ingestion labels make 48.1% the ceiling:
not untraceable, not a document conflict, simply unreachable. p02 reports
faithfulness of 0.969 where the judge returns null on parse failures and the
reported rate silently drops them, so the figure is a rate over 962 items
and the document states no denominator. Both are checkable by reading two
committed files against each other, and both were invisible to the schema.

`broken_reference_count` is `artifacts_unreferenced_count` from the other
end: that field counts artifacts nothing points at, this one counts pointers
that reach nothing. p02's README project tree lists two files that are not
tracked and gives three result files under names that do not match the
committed ones. Same findability failure, opposite direction, and a reviewer
following the documentation hits this one first.

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
| `corpus_language` | string | lowercase [ISO 639-1](https://en.wikipedia.org/wiki/List_of_ISO_639_language_codes) code, e.g. `en`, `pt`, `ru`, `de` (M2; was unconstrained free text) |
| `corpus_domain` | string | free-text subject label |
| `interface_framework` | string | e.g. `flask`, `streamlit`, `fastapi` |
| `vector_store` | string | e.g. `qdrant`, `elasticsearch`, `in_memory` |
| `llm_provider` | string | e.g. `openai`, `ollama` |
| `repo_file_count` | int | tracked files at the pinned commit |
| `project_name` | string | synthetic label, e.g. `Project Alpha` — see below (M2) |

**`corpus_language` is constrained (M2).** M1 returned `pt` from one
extraction and `portuguese` from another for the same fact — both correct,
not comparable. The extended M2 corpus repeated the problem across
capitalization and code-vs-name choice (`english`, `English`, `Russian`,
`de` all appeared before this constraint). ISO 639-1 removes the ambiguity;
every value observed so far maps cleanly to one code.

**Group-K string equality is excluded from any extraction-agreement or
spot-check statistic (M2).** These fields are `descriptive` and no
criterion may read them; a double-extraction agreement measurement that
penalizes `pt` vs. `portuguese` disagreement would be measuring wording,
not extraction validity. `corpus_language`'s new constraint reduces the
practical risk but the exclusion applies to all of group K, including the
still-free-text `corpus_domain`.

These exist **so that no-change twins have somewhere to mutate**. A
criterion reading any of them would score a project for choosing Flask over
Streamlit, or for being about wine rather than manufacturing — which is
noise, and G1's no-change half exists to catch precisely that.

Note the asymmetry, deliberate and stated: `interface_framework` is
descriptive while `interface_kind` is scoreable. *Whether* a project has a
web interface is creditable; *which framework* built it is not.

**`project_name` is synthetic and is never extracted (M2).** Every other
field in this schema is a fact read off the repository. This one is not:
it exists only so the cosmetic-rename no-change kind has a field to
mutate — the catalogue names cosmetic renames as a required no-change
type, and until this field existed no field held anything like a project
or brand name at all. **The extractor never touches this field and must
not invent one per repository.** A value assigned per-repo by a model
risks leaking a real project or repo name into the record, which
`agents/extractor`'s anonymity rule exists to prevent. Instead,
`project_name` is assigned by a fixed, deterministic mapping from
`case_id` (`tools/assign_project_names.py`): p01 → `Project Alpha`, p02 →
`Project Beta`, and so on through the Greek alphabet. `evidence: []` and
`basis` states plainly that the value is synthetic, not derived from the
repository — this is not the `undeterminable`/`other` distinction, which
is about facts the schema failed to settle; here there is no fact to
settle at all.

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
