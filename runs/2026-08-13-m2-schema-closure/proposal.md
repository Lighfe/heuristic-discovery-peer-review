# M2 step 2 — schema closure proposal

Working document, not a decision record. Drafted for owner review per
`tasks/03-milestone-2.md` step 2, which requires an explicit decision on
each of 21 items from `docs/deferred-to-m2.md` before the schema seals.
Nothing here is adopted until the owner accepts it — accepted items get
written into `docs/decisions.md` as new entries; rejected or modified items
get redrafted and the reasoning kept.

Each item states: the problem (from `deferred-to-m2.md`), new evidence
from the extended corpus where relevant (`runs/2026-08-13-m2-corpus-extraction/six-field-table.md`
and direct record queries run today), a recommendation, and — where the
call is genuinely contested rather than mechanical — the alternative not
taken and why.

Items are labelled exactly as in `deferred-to-m2.md`.

**Isolation check on the underlying evidence.** Items 1, 3d, 5, 6 and 7
below lean on "new evidence" from the 11 records extracted in step 1. That
evidence is only as good as the extraction isolation
(`extraction-in-clean-context`) — the same rule whose failure required
redoing p01's first extraction. This was checked directly, not assumed:
see "Isolation check" in `runs/2026-08-13-m2-corpus-extraction/six-field-table.md`.
All 11 subagent transcripts show reads of exactly `agents/extractor/v1/prompt.md`
and `cases/schema.md` (plus each repo's own clone) and nothing else —
no `plan.md`, `decisions.md`, `deferred-to-m2.md`, or `CLAUDE.md` in any
transcript, no CLAUDE.md system-injection marker in any transcript.

---

## Preface: the cell-locator convention (raised in the task, not one of the 21)

`tasks/03-milestone-2.md` flags that the cell-locator convention
(`path:cellN`) was already settled when p02 hit it and never entered the
deferred queue — it just needs a formal `decisions.md` entry rather than
re-litigation. **Recommendation: adopt as a one-line confirmation.** No
open question.

---

## 1. `llm_eval_metric_at_ceiling` has no threshold

**Problem.** Bool field, no defined threshold for "effectively every
item," and averaging across metrics would hide the one-maxed-metric case
this field exists to catch.

**New evidence.** p13 sharpens the problem beyond what M1 saw: its
`over_refusal_rate` is 0.0 across all three prompt variants — the
unfailable-test pattern is present, but 0.0 is the metric's *floor*, not
its *maximum* (lower is better for this metric). The field's current
wording ("sits at its maximum") has no correct answer for an
inverted-direction metric.

**Recommendation.** Keep the field boolean (true if *any* reported metric
hits ceiling — do not average, per the risk the deferred item already
names). Add one defined rule to `cases/schema.md`:

> A metric is *at ceiling* when at least 95% of scored items achieve that
> metric's best possible value, where "best" is the metric's own stated
> direction (maximum for quality/relevance scores, minimum for
> error/refusal/failure rates). The extractor states each reported
> metric's direction and per-metric ceiling status in `basis`; the field's
> `value` is true iff at least one qualifies.

95% is chosen to match the G4 ceiling-check threshold already frozen in
`objective.md` (`agreement-protocol-ceiling`), rather than inventing a
second unrelated number.

**Alternative not taken.** A per-metric structure (list of ceiling
metrics) would preserve more information but changes the field's type
from bool to a structured value — a larger schema change for a case
(multiple ceiling metrics on one record) that has not yet occurred in any
of the 13 records. Revisit if it does.

---

## 2. Knowledge provenance — make it an explicit rule

**Problem.** Owner already ruled (2026-08-10): general programming/library
knowledge is admissible when load-bearing, and must be flagged in
`extraction_notes`. This is currently a habit, not a written rule.

**Recommendation.** Formalize the existing ruling verbatim: add a short
section to `cases/schema.md` ("Domain vs. general knowledge") and one
sentence to `agents/extractor/v1/prompt.md`'s "Domain knowledge is not
available to you" section, carving out general programming/library
knowledge as usable-but-flagged. No new field, no re-extraction — this
formalizes a rule already in effect and already followed in all 13
records.

---

## 3. Reproducibility as a per-evaluation property

**Problem.** Owner likes the direction, rejected the first four-sub-field
sketch as overfit to p01/p02's specific wording. Wants: *the results can
be reproduced, or are exactly traceable through the documentation*,
applied per evaluation (retrieval, answer), fewer fields.

**Recommendation.** Two new fields, one per evaluation group, same
3-value enum:

```
retrieval_eval_reproducible: reproducible_as_committed | traceable_not_reproducible | neither
llm_eval_reproducible:       reproducible_as_committed | traceable_not_reproducible | neither
```

- `reproducible_as_committed` — a committed script/notebook, run as
  committed, would regenerate the reported figure(s) from committed
  inputs (no missing imports, no unexecuted cells, no undefined names, no
  silently-dropped denominator).
- `traceable_not_reproducible` — the number cannot be regenerated by
  running committed code, but every step from evaluation set to reported
  figure is still inspectable by reading committed artifacts.
- `neither` — neither holds. This is where p01's non-executing marimo
  notebooks and p02's index-built-from-an-uncommitted-source both land.

This subsumes p01's "notebooks can't execute" and p02's "index built from
a source no committed script uses." It does **not** subsume "reported
figure exceeds what the code can produce" (already `document_code_conflicts`,
group J) or "denominator silently drops failed items" (a `neither`-forcing
fact under the definition above, not a separate field). Two fields, not
four; wording is general rather than keyed to either record.

**Alternative not taken.** Folding reproducibility into the existing
`document_code_conflicts`/`headline_numbers_traceable` fields instead of
adding new ones — rejected because those are group-J (documentation
accuracy) properties about claims, while this is a group-D/E property
about whether an *evaluation pipeline* itself can be rerun, a distinct
fact even where they correlate.

---

## 3a. p02's monitoring prose↔executable divergence

**Problem.** `monitoring_chart_count: null` for p02 (stock dashboard, no
committed panels) means the executable layer can't satisfy "at least N
charts," while a human sees a working dashboard. `deferred-to-m2.md`
already states the fix: a `null` chart count cannot satisfy an "at least
N charts" test, because no committed chart can be counted.

**Recommendation.** No schema change. Confirm the v0 mapping rule already
stated in `deferred-to-m2.md` §3a is the final answer — it does not
change p02's score (verified there: `monitoring_kind: dashboard_only`
caps the criterion at 1 point regardless). Record as "no change, rule
already fixed and documented," closing the item formally.

---

## 3b. `run_instructions` vs `run_instructions_gap_count` contradiction

**Problem.** The enum measures coverage (does the procedure *name* every
step category); the count measures correctness (does each step actually
work). A reader seeing only the enum reaches the opposite conclusion from
the count.

**Recommendation.** No new field. Add one clarifying paragraph to
`cases/schema.md`'s group G section, stating explicitly that the two
fields measure different things and are not redundant, and that **a
criterion checking "does it work" should read the count, never the enum
alone** — matching the schema's existing preference for countable facts
over coarse enums. Prose-only fix; does not touch v0 (which already reads
only the enum, faithfully transcribing the current guidance's
conflation — unchanged per `v0-literal-no-inferences`).

---

## 3c. Scoreable/descriptive split is leaky at `basis`

**Problem.** `basis` text on *scoreable* fields routinely embeds
*descriptive* facts (audience, corpus domain, vendor names), which means a
dataset-domain-swap or cosmetic-rename no-change twin can't be built
without either contaminating a scoreable field's prose or writing a
self-contradictory record. Only the technology-swap no-change kind is
currently buildable clean.

**This is a genuine tradeoff, not a mechanical fix — flagging for your
call rather than picking one.**

- **Option A (recommended): tighten the extractor-prompt rule going
  forward, accept the current gap as a documented limitation.** Add a
  rule: `basis` on a *scoreable* field states only the fact being scored,
  never incidental descriptive context (audience, domain, vendor). This
  costs nothing (prompt-only change), applies automatically to every
  future extraction, but does not retroactively fix p01/p02's or the new
  11 records' already-written `basis` text unless they're re-extracted.
  G1's no-change half is already satisfiable with the one clean kind
  (technology-swap); dataset-domain-swap and cosmetic-rename stay flagged
  as *not currently buildable*, same treatment as any other untested
  catalogue type.
- **Option B: retrofit now.** Rewrite every scoreable field's `basis`
  text across all 13 records under the new rule, before sealing (free
  now, costly after). Buys immediate buildability of two more no-change
  kinds at the cost of a full pass over every record.

**Recommendation: Option A.** The marginal evidentiary value of two more
no-change kinds is smaller than the cost of a full retrofit pass, and
nothing forecloses adding them later once the tightened rule has produced
enough clean records naturally (step 5's real-base search may turn some
up already, since the extended corpus is bigger).

---

## 3d. `claim-without-artifact` has almost no headroom on p01

**Problem.** p01's only clean move is `untraceable_number_count: 18 → 21`
— a small, low-headroom mutation. `deferred-to-m2.md` recommends building
this catalogue type against a different base record with more headroom.

**New evidence, queried directly against all 13 records:**

| case | `headline_numbers_traceable` | `untraceable_number_count` |
|---|---|---|
| p01 | some_traceable | 18 |
| p02 | some_traceable | 2 |
| p03 | some_traceable | 2 |
| p04 | **all_traceable** | **0** |
| p05 | no_numbers | 0 |
| p06 | **all_traceable** | **0** |
| p07 | **all_traceable** | **0** |
| p08 | **all_traceable** | **0** |
| p09 | **all_traceable** | **0** |
| p10 | no_numbers | 0 |
| p11 | **all_traceable** | **0** |
| p12 | **all_traceable** | **0** |
| p13 | **all_traceable** | **0** |

Eight of the eleven new records are `all_traceable` with zero untraceable
numbers currently — a *much* larger single-fact move is available: degrade
several headline numbers from traceable to untraceable in one step,
instead of nudging p01's already-degraded 18 by 3.

**Recommendation.** Adopt the fix in principle now: build
`claim-without-artifact` against one of {p04, p06, p07, p08, p09, p11,
p12, p13} instead of p01. Defer the specific choice to step 5 (twin
construction), where the actual headline-number content of each candidate
determines which gives the cleanest single-fact degradation. This closes
the item's stated concern; no schema change needed, only a change of
which base record the twin generator targets.

---

## 3e. Schema not normalised — `retrieval_best_approach_shipped`

**Problem.** This field is a derived summary of per-technique
`measured_effect` values, so any change to a technique's measured effect
makes it factually stale — every `harmful-component-kept` twin on p01
necessarily moves two fields, not one. Owner scoped the one-time allowance
(`twin-entailed-change-scoped`) to `p01-t01`/`p01-t02` only, refusing it as
a standing rule. `deferred-to-m2.md` names the permanent fix — derive the
field at scoring time instead of storing it — but does not mandate it.

**Recommendation.** Adopt the permanent fix now, while it is free: **drop
`retrieval_best_approach_shipped` as a stored record field.** The scorer
computes it at score time from the per-technique `measured_effect` blocks
already in the record (a small, deterministic function, not a schema
change to the technique blocks themselves). This removes the entailment
problem structurally — a twin that changes one technique's
`measured_effect` no longer forces a second field edit, because there is
no second field. It also removes the standing risk the deferred item
names: "the alternative is an allowlist that grows one owner decision at
a time."

**Cost.** `v0`'s `criteria.yaml` mapping currently reads this field
directly and needs updating to a computed lookup instead — a scorer-harness
change, not a change to what v0 scores or how it reads the guidance text,
so it does not touch `v0-literal-no-inferences` or require re-verifying
v0's fidelity to the guidance.

**Alternative not taken.** Keep the field, keep relying on
`APPROVED_ENTAILMENTS` case by case. Rejected per the deferred item's own
reasoning: it is an allowlist that grows one owner decision at a time,
and the normalising fix is free right now specifically because sealing has
not happened yet.

---

## 3f. `llm_eval_role_overlap` undefined when no generator exists

**Problem.** The field conflates a three-way overlap (generator, answer
model, judge) with a two-way one (answer model, judge) and doesn't say
which it measured when the generator role is unoccupied. Owner answered
"can't tell" for p01 on exactly this gap.

**Recommendation.** No structural change. Add one clarifying sentence to
`cases/schema.md`'s group E section: *when
`llm_eval_question_generator` is `none_committed`, this field compares
only the answer-generator and judge roles; `basis` must say so
explicitly.* Cheap, and matches how the field is already being answered in
practice (p01's `same_family` already reflects a two-way comparison; the
new records show no case where fewer than two roles are occupied, so no
further value is needed).

---

## 3g. `decision_documented`'s name hides the measurement requirement

**Problem.** Bool field named `decision_documented`, but it actually
requires justification *from the project's own measurements* — an
a-priori argued reason (like p02's reranker README argument on domain
grounds) reads as `false` under the schema's own definition, which a
reader checking only the name would not expect.

**New evidence.** The extended corpus shows this is a live distinction,
not a p02 one-off — multiple records have `documented: true` on
measurement grounds (p02 reranking, p03 hybrid_search, p04 hybrid_search,
p06 hybrid_search, p09 hybrid_search, p11 hybrid_search + query_rewriting,
p13 all three techniques) alongside records with argued-but-not-measured
or undocumented cases. A three-way split would be well populated, not
speculative.

**Recommendation.** Adopt the three-way value the deferred item already
proposes, and rename the field so its name states what it checks:

```
decision_basis: none | argued | measured
```

(`decision_documented: bool` retired in favour of `decision_basis`.)
`none` = no stated ship/no-ship reasoning at all; `argued` = a reason is
stated but not tied to the project's own measurements (p02's original
domain argument for hybrid, before the reranker case); `measured` = tied
to the project's own reported numbers (current `true` cases).

**Cost.** Every technique block on every record needs re-answering this
one sub-field under the new three-way rule — cheap (a single pass per
record, not a full re-extraction) but must happen before sealing (step 3).

---

## 3h. A second `document_code_conflicts` candidate on p02, not counted

**Problem.** p02's README claims answers are grounded in
"peer-reviewed or pre-print literature"; ingestion actually indexes only
paper *abstracts*. Deliberately not counted because the counting rule for
this field was itself unfixed.

**Recommendation.** Fold into item 3i (below) rather than treat as a
separate decision — 3i's counting-rule sign-off determines whether a
depth-of-source overstatement like this counts. Once that rule is
written, recount p02 (and check the extended corpus for the same
pattern — worth a quick pass, since "claims broader scope than what's
actually indexed" is a plausible recurring failure mode, not p02-specific)
at step 3's free re-extraction.

---

## 3i. Counts-vs-enums tension and step 6's spot-check sizing

**The most consequential item**, per the deferred queue itself. Two
decisions:

### (a) Which fields stay counts vs. become something else

Owner's own framing, already the right shape: keep counts where a twin
needs headroom and the count is small/bounded; reconsider where large and
open-ended.

**Recommendation.**

- **Keep as exact counts, no change:** `document_number_conflicts`,
  `broken_reference_count`, `run_instructions_gap_count`,
  `document_code_conflicts` (observed range across all 13 records: 0–13 —
  p12's 13 is the outlier but still a small, nameable list per `basis`,
  not an open-ended recount problem).
- **`untraceable_number_count`: keep as an exact count (twins need the
  headroom — see 3d above), but change what validation demands of it.**
  Exhaustive recounting (18 figures across two documents, per the owner's
  own experience) does not scale and was never proposed to repeat.
  Instead: any future validation of this field (step 6's spot-check, or
  later) samples a **fixed number of the cited figures** (recommend 5 per
  record, or all of them if the record cites fewer than 5) rather than
  recounting every one. The field stays a precise count for twin
  construction; the *validation confidence* on it is explicitly sampled,
  not exhaustive, and every report says so.

### (b) Does 3i's sign-off also cover the counting rule for
`untraceable_number_count`?

**Already resolved — no separate item needed.** `cases/schema.md`'s
current text already states the counting rule precisely: *"counts
**individual figures**, not results tables or claims: a four-row table of
four metrics is sixteen figures."* This rule was written into the schema
before this task began (it predates M2). Recommend confirming this in
`decisions.md` as already closed, rather than treating it as open.

### (c) Step 6's spot-check sample size

This is explicitly an owner call (`tasks/03-milestone-2.md`'s hard-limits
section lists it by name) — I am not picking a number, only sizing
options using the leverage rule the task specifies (fields a twin
mutates, fields a candidate reads):

| option | fields checked per record | records | total field-checks |
|---|---|---|---|
| light | 4 (the highest-leverage: the six-field table's `_config_matches_shipped` pair, `llm_eval_metric_at_ceiling`, `untraceable_number_count`) | 20 (all non-owner-reviewed) | 80 |
| medium | 8 (light + `retrieval_eval_relevance_rule`, `llm_eval_judge_spotchecked`, `llm_eval_question_generator`, `document_code_conflicts`) | 20 | 160 |
| heavy | all scoreable fields a sealed twin type currently mutates | 20 | ~300–400 |

Each option also needs the notes-comparison requirement from item 8
folded in (comparing whether the record's `extraction_notes` capture what
a spot-checker independently notices, not only field values).

**I recommend medium** as the default if you don't have a strong
preference: it covers every field this milestone's twin catalogue plans
to mutate, at a cost the owner has already shown willingness to spend
once (the M1 checklist covered 136 fields across 2 records by hand).

---

## 3j. `basis` leaks repo paths into reviewer prompts

**Problem.** `basis` sentences cite file paths inline
(`docs/evaluation.md:19`), so path locators reach the reviewer prompt
through the one field designed to be read by a model, even though
`evidence` locators are never rendered. Risk: citation density could move
a score for reasons unrelated to content.

**Recommendation.** Rendering-layer fix, no schema change, no
re-extraction. `loop/render.py` strips path-shaped citations
(`` `path/to/file.ext:N` `` and `` `path/to/file.ext:N-M` `` patterns,
including `:cellN` for notebooks) from `basis` text specifically in the
copy sent to reviewer prompts, while the unmodified `basis` (with
citations) stays in the committed record for human re-verification. This
is the "stripped variant for prompts, cited variant for humans" option
`deferred-to-m2.md` names, chosen over rewriting `basis` everywhere
because it costs nothing and doesn't touch already-written record text.

**Residual risk to state in the writeup regardless:** a regex-based strip
can miss an unusual citation style; recommend a one-time spot-check of a
sample of rendered, stripped `basis` text against the original before this
becomes load-bearing for the M2 agreement pass (step 9a).

---

## 3k. Which catalogue types need a constructed base

**Problem.** `config-drift` and `circular-eval` held the defect on *both*
records at M1 (p01, p02) — no clean base to degrade from, in either
record.

**New evidence** (full detail in
`runs/2026-08-13-m2-corpus-extraction/six-field-table.md`):

- **`config-drift` is now unblocked.** p07, p09, and p13 hold `matches`
  on *both* `retrieval_eval_config_matches_shipped` and
  `llm_eval_config_matches_shipped` simultaneously — a single clean base
  serves both sub-mutations. No constructed base needed.
- **`unfailable-eval`** was already unblocked at M1 (p02); now has many
  more candidate bases (p02, p05, p06\*, p10, p12 on the ceiling field;
  most of the corpus on the relevance-rule field). \*p06 is
  `undeterminable`, not clean `false` — not usable as a base for this
  field without further definition (see item 1).
- **`circular-eval` stays mostly unblocked, one sub-case still thin.**
  `llm_eval_question_generator` holding a committed generator is common
  now (p02, p07, p08, p10, p11, p13) — that sub-mutation has a real base.
  `llm_eval_judge_spotchecked: true` is held by exactly **one** record
  (p13) across all 13 — that sub-mutation still has only a single real
  base, better than M1's zero, but thin. Whether one real base is enough,
  or whether a constructed base is still warranted for redundancy, is
  worth a step-10 or step-5 judgment call rather than deciding now.

**Recommendation.** Adopt the policy, not a final list: use a real base
wherever the table shows one (now true for `config-drift` and
`unfailable-eval`); construct a synthetic base only for a sub-mutation
that still shows zero real bases after step 4 extends the table to 22
records. Confirm this policy now; the final buildable/not-buildable
list is produced at step 5 as the task specifies.

---

## 4. Group J has accreted — restructure, do not extend

**Problem.** Eight fields, each added to close a single-repository gap.
Owner ruling: restructure once, after the twin work has shown which
fields carry signal — not before.

**Recommendation.** The owner's own rule places this decision *after*
step 5 (twin work), which runs after this schema-closure stop. **Defer
explicitly, with a stated revisit point**, rather than deciding now:
record in `decisions.md` that Group J restructuring is deliberately
deferred until twin/red-team evidence exists (end of M2 or M3 planning),
not silently dropped. No schema change at this stop.

---

## 5. Fields motivated by exactly one repository

**Problem.** `decision_documented`/`decision_axes`, `llm_eval_role_overlap`,
`monitoring_instrumentation`, `monitoring_dashboard_provenance` — each
closed a gap found in p02 alone, untested against a third repository
until now.

**New evidence, queried directly against all 13 records:**

- `llm_eval_role_overlap`: varies genuinely — `same_family` (p01),
  `same_model` (nine of the eleven new records), `other` (p04),
  `undeterminable` (p05). Real discrimination, not constant.
- `monitoring_instrumentation`: varies — `traced_on_request_path`,
  `logged`, and `none` all occur across the new records.
- `monitoring_dashboard_provenance`: varies —
  `committed_definitions` is common, `stock_tool_ui` recurs (p02, p08,
  p10).
- `decision_documented` (pre-3g): varies within *and* across records —
  seven of the eleven new records have at least one technique block with
  `documented: true`, several also have `false` blocks in the same
  record. Strong signal, not a constant.

**Recommendation.** Keep all four fields — none is constant across the
extended corpus, so none fails the discrimination test the item sets.
Close the item as resolved by the M2 extraction itself.

**Observation, not a decision:** `monitoring_instrumentation`'s
`logged`/`traced_on_request_path` boundary was independently flagged as
ambiguous by the extractor in five of the eleven new records
(p05, p06, p09, p10, p12) — a real recurring definitional soft spot, but
not one of the 21 items. Flagging for awareness; recommend leaving it
alone for M2 and revisiting only if it starts affecting a twin or a
candidate's mapping.

---

## 6. Group-K string fields have no controlled vocabulary

**Problem.** `corpus_language` came back inconsistent between two M1
extractions (`pt` vs `portuguese`).

**New evidence.** Across all 13 records, `corpus_language` values are:
`portuguese`, `english` (×8), `Russian`, `de`, `English` — mixing full
language names with an ISO code, and inconsistent capitalization even
within the full-name style. Confirms the problem is real and current, not
hypothetical.

**Recommendation.**

- Constrain `corpus_language` to lowercase ISO 639-1 codes (`en`, `pt`,
  `ru`, `de`, ...). Mechanical, no ambiguity, and every value observed so
  far maps cleanly to one.
- Leave `corpus_domain` as free text (no practical fixed enum for subject
  labels), but add one explicit sentence to `cases/schema.md`: *string
  equality on any Group-K field is excluded from any extraction-agreement
  or spot-check statistic* — already implied by "descriptive, never read
  by any criterion," made explicit so nobody double-extracts these fields
  expecting them to match.
- The 13 already-written records need `corpus_language` re-answered under
  the ISO constraint — cheap, folds into step 3's free re-extraction pass
  if any schema change happens anyway; otherwise a one-field touch-up.

---

## 7. `interface_kind` cannot express more than one interface

**Problem.** p02 ships FastAPI + Streamlit; the field forces one value.
Owner called this minor at M1, deferred rather than fixed.

**New evidence.** The extended corpus shows this recurring, not confined
to p02: p01, p02, p08, and p11 (per the extracting subagents' own reports)
all have more than one interface, and every one is currently forced into
a single `web_ui` (or similar) value that silently drops the second.

**Recommendation.** Given the recurrence, fix now rather than defer
again — the fix is cheap (widen the type) and the cost of deferring keeps
compounding as the corpus grows:

```
interface_kind: list[enum]   # was: enum
```

Same allowed values as today, now a list; single-interface records get a
one-element list, no behavior change for them. `criteria.yaml`'s mapping
(currently reading a scalar) needs a small update to read "does the list
contain X" instead of "does the value equal X" — a scorer-harness change,
not a re-interpretation of the guidance text.

---

## 8. Extraction-agreement must compare notes, not only values

**Problem.** Already decided (`extraction-agreement-needs-notes`). This
item just confirms step 6 implements it.

**Recommendation.** Confirmed, folded into item 3i's spot-check design
above: the spot-check protocol requires a spot-checker to read and
confirm or dispute `extraction_notes`, not only compare field values. No
new decision; record as "already decided, implementation confirmed in
3i's spot-check design."

---

## 9. Proposed post-M1 decisions-review mechanism (`Binds:` line)

**Problem.** Suggested mechanism: every `decisions.md` entry gains a
`Binds:` line naming where it takes effect. Known hole: an entry can
label itself `inert` and escape the review with no site to verify against
— unless `inert` requires its own one-line justification.

**Recommendation.** Adopt the mechanism **as already amended** in the
deferred item (inert requires justification, not just the label). Apply
it going forward to every new `decisions.md` entry from this schema-closure
pass onward — including every entry this document itself will produce, if
accepted. Do **not** mandate retrofitting the ~50 existing entries as part
of M2; that's a bulk pass that can happen later without blocking sealing.
Flag as an optional follow-up task, not a step-2 blocker.

---

## 10. Anchor evaluation expectations to the course's own materials

**Problem.** Owner's proposal: a capstone cannot be required to exceed
what `06-best-practices` and `07-project-example` demonstrate. Both
sources already verified in `deferred-to-m2.md`; the argument and its
limits (bounds what's *demanded*, never licenses ignoring what a project
claims and contradicts; not everything the course does is written down)
are already fully worked out there.

**Recommendation.** Adopt as written — the reasoning is already complete
and carefully bounded in `deferred-to-m2.md` item 10. This closes the item
by ratifying existing text into `decisions.md` rather than redrafting it.
No new analysis needed; just formal sign-off.

---

## Summary for owner review

| # | item | recommendation | owner call needed |
|---|---|---|---|
| — | cell-locator convention | confirm already-settled | rubber-stamp |
| 1 | ceiling threshold | 95% rule, matches G4's number | accept/reject |
| 2 | knowledge provenance | formalize existing ruling | rubber-stamp |
| 3 | reproducibility | 2 new fields (per-evaluation) | accept/reject/modify |
| 3a | p02 monitoring divergence | no change, already fixed | rubber-stamp |
| 3b | run_instructions contradiction | clarifying prose only | rubber-stamp |
| 3c | basis leaks descriptive facts | Option A (tighten prompt, accept gap) vs Option B (retrofit) | **genuine choice** |
| 3d | claim-without-artifact headroom | switch base away from p01 | accept/reject |
| 3e | schema not normalised | drop derived field, compute at score time | accept/reject |
| 3f | role_overlap undefined | clarifying prose only | rubber-stamp |
| 3g | decision_documented name | 3-way `decision_basis` enum | accept/reject/modify |
| 3h | 2nd document_code_conflicts | folds into 3i | rubber-stamp |
| 3i | counts-vs-enums + spot-check size | keep counts, sample untraceable_number_count; **pick light/medium/heavy** | **genuine choice (size)** |
| 3j | basis leaks paths | strip at render time only | accept/reject |
| 3k | constructed-base types | adopt policy, defer final list to step 5 | rubber-stamp |
| 4 | Group J restructure | defer, with stated revisit point | rubber-stamp |
| 5 | single-repo-motivated fields | keep all four, closed by evidence | rubber-stamp |
| 6 | Group-K vocabulary | ISO 639-1 for language, exclude from agreement | accept/reject |
| 7 | interface_kind single-value | widen to list now (recurs 4×) | accept/reject |
| 8 | notes-based agreement | confirmed via 3i | rubber-stamp |
| 9 | `Binds:` line mechanism | adopt going forward, no retrofit | accept/reject |
| 10 | course-materials anchor | ratify as written | rubber-stamp |

Twelve items are effectively mechanical once you've read the reasoning
(rubber-stamp). Three are genuine design choices where I've picked a
recommendation but the alternative is real: **3c** (leaky basis — tighten
vs. retrofit), **3i's sample size** (light/medium/heavy), and to a lesser
extent **3g**'s rename. Everything else changes schema.md, the extractor
prompt, or the scorer harness in a way I can implement immediately once
you sign off.
