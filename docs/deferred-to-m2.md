# Deferred to M2 — open schema and method questions

*Live document. Items are removed when resolved, not struck through. Each
carries the date it was raised and where the evidence for it sits.*

**Why this file exists.** M1's deliverable is the twin baseline — which
twins the *current* criteria fail — and nothing has been scored yet. Every
schema round-trip pushes that further out, so as of 2026-08-10 the schema is
**frozen for M1** and everything below waits for M2 sealing, where
re-extraction is happening anyway and a change costs nothing extra.

A schema change after M2 sealing costs a full re-extraction of the corpus
plus a re-run of every measurement. Before sealing it is free. That asymmetry
is the whole reason for the freeze, and the whole reason nothing here may be
quietly dropped.

---

## Raised 2026-08-10 (M1 schema gate, owner review of p01/p02 records)

### 1. `llm_eval_metric_at_ceiling` has no threshold

Currently a bool: is a reported metric at its maximum for effectively every
item? p01 reports faithfulness 5.00/5, so `true`. But **4.9/5 is not
defined**, and "effectively every item" is doing unexamined work.

Owner's options, neither settled:

- `all` / `some` / `none` — still needs a threshold to decide membership.
- `metric_ceiling_fraction: float` — but a **mean across metrics hides the
  case this field exists to catch**: one maxed-out metric among several
  normal ones averages away, and that single metric is the unfailable test.

Any fix has to preserve per-metric visibility. A per-metric structure
(fraction at ceiling for each reported metric, or the maximum over metrics)
is the likely shape. Evidence: `cases/records/p01.yaml`
(`llm_eval_metric_at_ceiling: true`, faithfulness 5.00/5) versus
`cases/records/p02.yaml` (0.805 and 0.969, below ceiling).

### 2. Knowledge provenance on a field value — make it an explicit mechanism

Some field values rest on knowledge that is neither "a fact in the
repository" nor domain knowledge, but **general programming or library
knowledge**. Owner's ruling (2026-08-10): such knowledge **is admissible and
should be applied** — and when it is load-bearing, the record **must** carry
an extraction note saying so.

Examples already in the records:

- p02, `run_instructions_gap_count`: `dtype={'id', str}` passed to
  `pandas.read_json` is a *set*, not a mapping, so the call fails. Knowing
  that is Python knowledge.
- p02, same field: bash `echo` does not interpret `\n` without `-e`.
- p02, monitoring: recognising that `arizephoenix/phoenix:latest` ships a
  tracing UI, so a reviewer sees panels the repository never defines.

Right now the p02 extraction flagged these by good judgment. It has to become
a **rule in the schema and in the extractor prompt**, not a habit: state that
library and language knowledge may be used, and that any value depending on
it names that dependency in `extraction_notes`. Without the rule, two
extractors differ on what they are allowed to know, and the records stop
being comparable.

### 3. Reproducibility as a per-evaluation property

Owner likes the direction, rejects the first sketch: four new sub-fields per
evaluation is overkill, and the proposed wordings were "very very specific"
— tuned to the two repositories that motivated them, which is the schema
overfitting risk in miniature.

The idea worth keeping, in the owner's looser framing: *the results can be
reproduced, or are exactly traceable through the documentation.* Applied per
evaluation (retrieval, answer) rather than as one repository-wide verdict.

What it would subsume, currently scattered:

- p01: the committed notebooks cannot execute, so no figure is reproducible.
- p01: the reported figure exceeds what the code can produce
  (`document_code_conflicts`).
- p02: the measured index is built from a source no committed script uses,
  so re-running after the README returns hit rate 0.
- p02: the reported rate silently drops the items where judging failed, and
  no denominator is stated.

Design constraint for M2: **fewer fields than the four sketched**, and
wordings that are not read off these two repositories.

### 3a. Known prose↔executable divergence: p02's monitoring

Found while checking whether the M1 freeze changes anything (2026-08-10).
`monitoring_chart_count` is `null` for p02 because its dashboard is a stock
Phoenix UI with no committed panel definitions. The v0 executable layer
therefore cannot satisfy the current criterion's "*a dashboard with at least
5 charts*" — while a human reviewer who runs the project **sees** panels and
counts them. The owner did exactly that.

This does **not** change p02's v0 score: `monitoring_kind` is
`dashboard_only`, and the current 2-point tier needs feedback collection as
well, which p02 has none of, so it caps at 1 point either way. Verified, not
assumed.

But it is a genuine case where the executable layer and a human applying the
prose reach different readings of the same criterion, and that is precisely
what M2's prose↔executable fidelity probe exists to measure. Recorded now so
the probe has a known instance to check itself against rather than only
discovering divergences it cannot verify.

**v0 mapping rule, fixed now so the transcription is unambiguous:** a `null`
chart count cannot satisfy a "*at least N charts*" test, because no
committed chart can be counted. Faithful to the criterion as written.

### 3b. `run_instructions` and `run_instructions_gap_count` contradict each other

**Findable here because phase 5 builds twins directly off p01's record and
this is the field pair most likely to mislead whoever reads it.** It is a
schema question, not a single-record one, so it belongs in this queue rather
than only in p01's extraction notes — where it currently also sits.

p01 records `run_instructions: complete` beside `run_instructions_gap_count: 3`.
Both are correct under their own definitions: the written procedure names
every required category of step (setup, dependencies, configuration,
environment variables, run command), and is still unrunnable in three
places. **The enum measures coverage; the count measures correctness.** A
reader seeing only the enum concludes the opposite of what the count says,
and a criterion mapping only the enum scores a project full marks for
instructions that do not work.

No change for M1: v0 reads the enum only, which is faithful to the current
criterion's text ("*instructions are clear … it's easy to run the code, and
it works*" — the current wording conflates the same two things, so the
transcription inherits the conflation honestly). At M2 the pair needs
resolving together, probably alongside item 3.

### 3c. The scoreable/descriptive split is clean at `value` and leaky at `basis`

Found by the M1 twin generation (2026-08-10), and it bears on whether gate
G1 is satisfiable rather than on convenience.

The split exists so degraded twins and no-change twins bind on disjoint
fields. It holds perfectly for `value`. It does **not** hold for `basis` —
and `basis` is read by the prose reviewer agents, so a change there is a
change to what a reviewer sees.

Concretely, in p01 the `basis` strings of *scoreable* fields embed
*descriptive* facts: `problem_statement.basis` names the audience and the
subject; `retrieval_eval_relevance_rule.basis` turns on the `wikipedia_pt`
label; `limitations_section.basis` rests on the corpus being non-English;
`llm_eval_judge_kind.basis` and `llm_eval_role_overlap.basis` name the model
vendor. So a **dataset-domain-swap no-change twin cannot be built**: swapping
`corpus_domain` or `corpus_language` forces either a rewrite of prose on
scoreable fields — breaking the no-change half — or a self-contradictory
record. `llm_provider` is unswappable for the same reason.

Only 3 of the 6 descriptive fields (`interface_framework`, `vector_store`,
`repo_file_count`) are swappable without contamination. The catalogue names
three no-change kinds — cosmetic rename, technology swap, dataset-domain
swap — and **only the technology swap is currently expressible.** There is
also no project-name, module-name or path field, so the cosmetic-rename kind
has no field to touch at all; M1's second no-change twin substitutes a
file-count change, which is a liberty and is labelled as one.

The generator enforces disjointness over prose as well as values for the
twins it built. Nothing outside it does, so a future twin restating a
scoreable `basis` while claiming zero movement would break the no-change
gate silently.

### 3d. `claim-without-artifact` has almost no headroom on p01

`headline_numbers_traceable` already sits at `some_traceable`, and
`none_traceable` is unreachable as a single fact: the panel count is
traceable *because* the dashboard JSON is committed, so uncommitting it
drags `monitoring_chart_count`, `monitoring_charts_bound_to_data` and
`monitoring_dashboard_provenance` with it — a different project, not a twin.
The only clean move is `untraceable_number_count: 18 → 21` (removing the
ingestion screenshot's three figures).

**If a candidate tiers that field coarsely, the twin ties and fails G1's
strict-ordering half** — and per the above there is no larger single-fact
move available on this record. Fixing it needs a *different base record*,
not a different twin, which is an argument for building this catalogue type
against a repository with more headroom at M2.

Related trap, recorded so nobody re-treads it:
`retrieval_eval_set_committed: committed → referenced_not_committed` looks
like a clean flip but erases the evidence for `document_code_conflicts: 1`
(the 52%-versus-48.1% finding derives from the committed test-set labels),
so one field degrades while another improves and no direction claim
survives.

### 3e. The schema is not normalised, which is why entailed twin changes exist

`retrieval_best_approach_shipped` is a derived summary of the per-technique
`measured_effect` values: `mixed_result` *means* "the reported metrics
disagree about which approach wins". So changing a technique's measured
effect makes the summary field factually false, and **every**
`harmful-component-kept` twin on p01 necessarily moves two fields. Checked
across all three techniques; there is no single-field version.

The owner ruled at the M1 twin gate that "differs in exactly one way" means
one *fact*, and **scoped that ruling to `p01-t01`/`p01-t02` alone**,
explicitly refusing it as a standing rule (decision
`twin-entailed-change-scoped`, enforced by `APPROVED_ENTAILMENTS`). The
scoping is right, and it means the next base record hitting the same
structure comes back to the owner rather than proceeding.

The permanent fix is normalisation: either derive
`retrieval_best_approach_shipped` from the technique blocks at scoring time
rather than storing it, or drop it and let a criterion compute what it
needs. Then a twin genuinely can differ in one field and the allowance is
not needed at all. Not mandated by the ruling — recorded because the
alternative is an allowlist that grows one owner decision at a time.

Documentation accuracy is now eight fields, each added to close a gap a
single repository exposed: `headline_numbers_traceable`,
`untraceable_number_count`, `document_number_conflicts`,
`document_code_conflicts`, `broken_reference_count`, `limitations_section`,
`artifact_reference_strength`, `artifacts_unreferenced_count`. Item 3 above
overlaps it. Restructure once, at M2, after the twin work has shown which of
these carry signal — not before.

### 5. Fields motivated by exactly one repository

`decision_documented` and `decision_axes` (p02's documented reranker
rejection), `llm_eval_role_overlap` (p02's one model in three roles),
`monitoring_instrumentation` (p02's OpenTelemetry spans),
`monitoring_dashboard_provenance` (p02's stock Phoenix UI). Each closed a
real gap. None has been tested against a third repository. M2's first
corpus extractions are the test; a field that stays constant across twelve
repositories discriminates nothing and should be cut.

### 6. Group-K string fields have no controlled vocabulary

`corpus_language` came back as `pt` from one extraction and `portuguese`
from another — both correct, not comparable. Harmless for scoring (group K
is `descriptive`), but it makes double-extraction agreement understate
itself, and no-change twins mutate exactly these fields. Fix: constrain to
ISO 639-1, or state that group-K string equality is excluded from any
agreement measurement. Evidence:
`runs/2026-08-10-extraction-priming/README.md`.

### 7. `interface_kind` cannot express more than one interface

p02 ships a FastAPI service *and* a Streamlit UI; the field forces one
value, recorded as `web_ui`, and loses the API. Owner: minor, do not
prioritise. A list, or a second field, at M2.

### 8. Extraction-agreement must compare notes, not only values

Already in `decisions.md` as `extraction-agreement-needs-notes` and in
`plan.md` M2(b). Repeated here so the M2 sealing checklist is in one place.

### 9. Proposed mechanism for the post-M1 decisions review

Owner will run a review task after M1 checking that decisions and plan items
correspond. Suggested mechanism, not yet accepted: each `decisions.md` entry
gains a **`Binds:`** line naming where it takes effect — a `plan.md` item, an
enforcement point (a gate, a test, a prompt), or `inert` (rationale for
something already done). The review then checks that every entry names a
site and every named site exists. A plain 1:1 decision→plan-item mapping
would fail on standing rules that legitimately schedule no work, and the
noise would hide the real misses.

**Known hole in the mechanism, and it is the one that matters.** The check
verifies that a *declared* site exists — so it catches an entry pointing at
a plan item that was never written, but it cannot catch an entry that
declares `inert`. Inert entries have nothing to verify against, which makes
`inert` the label under which a decision implying real future work escapes
the entire review. That is exactly the failure the review exists to prevent,
reachable by mislabelling one word. Cheap fix, to adopt with the mechanism:
**`inert` must carry a one-line justification**, not just the label — a
sentence saying what was already done and why nothing remains. A wrong
justification is still possible, but it has to be written down, and a
reviewer reading twenty of them will see the hollow ones.

### 10. Anchor evaluation expectations to the course's own materials

Owner's idea, 2026-08-10. Two sources exist and were verified:

- `06-best-practices` — hybrid search, RRF reranking, LangChain retrievers.
  The current rubric's three technique points map onto it almost exactly, so
  it is already the source, and it anchors gate G5 concretely.
- `07-project-example` — a full RAG project with ground-truth generation,
  Hit Rate / MRR, LLM-as-judge and model comparison.

The argument: **a capstone cannot be required to exceed the course's own
exemplar.** If the example project does not hold out a test set, no
criterion may demand one. This makes operational what `sources.md` already
half-states.

**What the anchor bounds, and what it must not.** It bounds *inventing
requirements the course never demonstrated* — holdouts, sample sizes,
significance testing, anything a learner could not have known to do. It does
**not** bound *noticing that a project's own claimed rigour fails against
its own artifacts*. Every finding this session survives regardless of what
the exemplar does: p01 reports a hit rate its own scoring code cannot reach,
and p02 reports rates whose denominators silently exclude the items where
measurement failed. Neither claim needs a view about how rigorous a capstone
ought to be — both are internal contradictions, and internal consistency is
the one thing `project-evaluation-issues.md` says a reviewer *can* check
without domain knowledge. A future reader must not take this anchor as
"go easy on rigour generally"; it is a ceiling on what may be *demanded*,
never a licence to ignore what a project claims and then contradicts.

Its limit, owner-stated and load-bearing: **not all of it is written down.**
The lecture hand-tuned the synthetic QA pairs; the markdown does not say so.
An agent reading only the repository derives a *weaker* bar than the course
actually demonstrates, so any checklist built this way has a floor set by
what happens to be documented — and the writeup must say that.

This is the input to any "how statistically solid must an evaluation be"
field. Owner's own attempt at stating that bar (2026-08-10) contained no
criterion — n=997 too high, questions synthetic and unnatural, why 997
unexplained, shared retrieval/answer items acceptable, a holdout desirable —
every clause defensible, none checkable. That is the evidence it needs an
external anchor rather than a judgment call. Its own task, after M1.
