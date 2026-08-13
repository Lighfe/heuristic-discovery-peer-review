# Review M1 — results

Save as `tasks/reviews/review-M1-results.md`. Produced from an independent
review of `findings.md`, `deferred-to-m2.md`, `decisions.md`, `schema.md`,
`criteria.yaml`, and the M1 run artifacts (records, twins, red-team log,
scorer manifest, agreement probes), 2026-08-13.

This file has two parts, the same as review-01. **Part A** is owner
decisions — action these. **Part B** is reviewer observations the owner has
not decided on — check them, argue back where the reviewer is wrong, and
record the outcome in `decisions.md`.

Each item states the evidence standard applied: which artifact grounds the
claim, and what would change the finding if it turned out false.

---

## 0. What this review does not do

Review-01 checked a plan before work began. A plan can be wrong only by
missing something. This review checks results after work is done. A result
can be wrong by accepting a finding that does not hold, even when every
number in it is correct.

Every field value cited in `findings.md` was checked against the record
files. All values are correct. The problems below are about what the
values are said to show, not about the values themselves.

`findings.md` is not withdrawn. Two of its findings (F2, F5) need
correction before M2 relies on them. One (F3) needs a stated dependency it
does not currently carry. None of this changes M1's status as complete.

---

## Part A — owner change requests

### A1. F5 cannot be checked. The evidence it needs was not in this review's package.

**What is missing.** `agreement.json` gives totals only: three numbers per
case. F5 claims something about the *content* of six model responses — that
all six cite one clause, and none names the shipped approach. That claim
needs the per-sample JSON output the reviewer model produced. It was not
supplied.

**Even with that evidence, F5's n is 3, not 6.** p01 holds
`retrieval_best_approach_shipped: mixed_result`. Under that value there is
no single best approach. A response that does not name one is correct, not
a failure to apply the clause. Only `p01-t01` holds `no`, the value where
the clause has something to bite on. Three of the six samples carry no
information about F5's claim. Pooling them doubles the apparent evidence.

**A second explanation is open, and F5 does not test it.** `criteria.yaml`
states the guidance gives no tier for "multiple approaches compared, best
one not shipped." The reviewer prompt then instructs the model: "Do not
refuse to score." A model facing an untiered case, told not to refuse, may
award the nearest tier. That is a rational response to a gap in the
guidance. It is not evidence that the clause is ignored. F5's fix and this
explanation's fix are different: F5 wants the clause made mechanical; the
gap explanation wants the missing tier written.

**The arithmetic in `findings.md` does not close.** v0 gives p01 21 points
and `p01-t01` 20. The three p01 samples run 22, 21, 22 — an offset of +1,
0, +1 against v0. The three `p01-t01` samples run 23, 21, 23. If retrieval
scores the same 2 points on both cases, the expected `p01-t01` samples are
22, 21, 22, matching p01's offset. The observed samples are one point
higher on two of three. F5 attributes the gap to one 3-point discretionary
award and one reproducibility drop. Those two effects do not produce "+1
twice." Something else moved, and F5 does not say what.

**Wording.** F5 says "reviewers" and "as humans apply them." No human
scored anything in this run. The model was `gemini-3.5-flash-lite`.
Decision `g4-is-self-consistency` already bars the bare word "agreement"
for this measurement. The same bar should cover "reviewers" and "humans."

**Evidence standard.** Field values: checked against `records_p01.yaml`
and `twins_p01-t01.yaml`. Per-sample content: not supplied, marked
unverified. Arithmetic: computed directly from `agreement.json`.

**Fix.** Supply the per-sample JSON, or downgrade F5 to a flagged
observation with n=3 stated and the missing-tier explanation named as
untested. Fix the wording either way.

### A2. F3's one working result depends on a reading `criteria.yaml` itself flags as the first thing to attack.

`findings.md` F3 calls the `p01`/`p01-t01` pair "the one thing that
genuinely works." It does work, under one condition: v0's two-point
retrieval tier accepts both `yes` and `mixed_result`. `criteria.yaml` names
this "the most consequential interpretation in v0, and the first row a
reviewer of this transcription should attack."

Apply the stricter reading, `yes` only:

| case | value | tier under strict reading | total |
|---|---|---|---|
| p01 | `mixed_result` | fallback, 1 point | 20 |
| p01-t01 | `no` | 1 point | 20 |

The pair ties. G1 fails on it. p02 also holds `mixed_result`, so the same
reading choice sets p02's retrieval score too.

**Why this matters now, not later.** `plan.md` schedules an independent v0
fidelity diff at M2 — a fresh session, no access to the transcription
rationale, checking guidance against mapping line by line. If that diff
picks the strict reading, M1's one working twin result disappears on the
spot.

**Evidence standard.** `criteria.yaml`'s own inline flag on the field, plus
direct recomputation of the tier table from `records_p01.yaml` and
`twins_p01-t01.yaml`.

**Fix.** State the dependency in F3 as written now, not after the M2 diff
runs. Do not let the M2 diff treat this as a neutral fidelity check — flag
that a specific finding rides on the outcome.

### A3. F2 gives the wrong reason for p01's two points.

F2 states v0 awards two points because "the best-performing approach is
shipped." The record says `mixed_result`, not `yes`. The two points come
from the same interpretive choice named in A2, not from the shipped
approach being the best-measured one. The rest of F2 is correct: the
`superseded.md` table (21/20 without the config-match condition, 20/20
with it) matches the manifest exactly.

**Evidence standard.** `records_p01.yaml` field value, `criteria.yaml` tier
text, `superseded.md` table, `2026-08-12-m1-scorer-v0_manifest.json`
totals. All checked directly.

**Fix.** Restate F2's reason. Point to A2's dependency instead of a
best-approach claim the record does not support.

### A4. Five successful attacks are one mechanism, reported as five.

Every G1 failure and every successful attack shares one property: the
mutated field is one no criterion reads.

| case | field changed | read by any criterion? |
|---|---|---|
| p01-t03 | `untraceable_number_count` | no |
| p01-t04 | `monitoring_charts_bound_to_data` | no |
| a1 | 9 technique fields | no |
| a2 | `headline_numbers_traceable`, `untraceable_number_count` | no |
| a3 | `monitoring_charts_bound_to_data` | no |
| a5 | `run_instructions_gap_count`, `broken_reference_count`, `document_code_conflicts` | no |
| a4 | the a5 fields, plus one read field | yes, one |

An attack on an unread field cannot lose points. It always succeeds. Five
successes from one mechanism is not five findings. It is one finding,
observed five times.

This matters directly for R2. `objective.md` defines R2 as fewer
successful attacks per round. A future report that says "5 attacks landed"
without this grouping will read as five distinct weaknesses to a reader who
has not traced the fields, when a single fix — a candidate that reads any
documentation-accuracy field — defeats all five at once.

**Evidence standard.** Read-set list taken directly from `criteria.yaml`.
Mutated-field list taken from each twin and attack YAML. Direct
cross-check, no inference.

**Fix.** Report attack count and mechanism count separately in F3/F4:
"5 successful attacks, 1 distinct mechanism." Add a rule to how R2 results
get written up: attacks sharing a mechanism count once for the ranking
narrative, in full in the run log.

### A5. F4's own p01 evidence for `llm_evaluation` circularity is stronger than the a4 attack, and does not depend on p02.

F4's realizability argument leans on a4, which needs p02's record to be
accurate. p02 has one validator: the owner. A cheaper, stronger version of
the same finding does not need an attack at all: p01 itself holds
`llm_eval_role_overlap: same_family`, and the scorer already pays it full
marks for `llm_evaluation`. p02 additionally holds `same_model`,
`generator_ties_question_to_passage`, and `judge_spotchecked: false`, and
the scorer pays it the full 2 points too. The criteria reward a circular
evaluation on real, already-shipped submissions. No constructed record is
needed to show it.

**Evidence standard.** `records_p01.yaml`, `records_p02.yaml`, and
`2026-08-12-m1-scorer-v0_manifest.json` per-criterion scores, checked
directly.

**Fix.** Lead F4 with the p01/p02 real-record evidence. Keep a4 as a
corroborating construction, not the load-bearing case.

### A6. G1's harness recorded a relation `objective.md` does not define.

`objective.md` names two relations for G1: `strictly_below` for degraded
twins, `exactly_equal` for no-change twins. The `p01-t02` twin verdict in
`2026-08-12-m1-scorer-v0_manifest.json` is recorded as `not_below` against
`p01-t01`. That relation exists in no gate document.

Under the project's own rule — agents may not edit what judges them — a
new gate relation is not a free implementation detail. It needs the same
owner sign-off any other gate change gets.

**Evidence standard.** `objective.md` G1 text, cross-checked against the
`relation` field in the scorer manifest's `twin_verdicts` block.

**Fix.** Either add `not_below` to G1's definition with a stated meaning,
or restate `p01-t02` as a second `strictly_below` pair measured against a
different base, so the harness uses only defined relations.

### A7. A new real-score dataset. Scope it before it enters `plan.md`.

You propose extracting ten real capstone repositories, each carrying a real
peer-review score, and running a check at the end of M2 for whether the
current criteria score accurately.

Two different checks are folded into that one sentence. They need
different treatment.

**Check 1 — does v0 match what real reviewers did with the same written
criteria?** This is safe. It does not touch the rule against using human
grades for validity. That rule bars human grades as evidence that the
*criteria* are good. This check does not measure that. It measures whether
v0's *code* matches the *criteria's text*, as real people read that text.
`objective.md` already names this as a separate, uncovered gap: "The
repo→evidence step is covered separately by extraction validation and the
prose↔executable fidelity measurement, and the final writeup may not merge
these into one claim." `plan.md` already plans an independent v0 fidelity
diff at M2, by code review alone. Real scores make that check run against
real behaviour, not only against text. **Recommended: add this, scoped to
v0 only.**

**Check 2 — does the current checklist measure quality well?** This is a
different question, and real scores cannot answer it. A human score under
the current checklist is ground truth for what the checklist outputs, not
for whether the project underneath is good. `reviewer-project-background.md`
states the whole project exists because the checklist has exactly this
flaw — it pays for a component's presence, not its effect. Using real
scores to check "is the scoring accurate" answers a question about the
checklist using the checklist's own output, which proves nothing about the
checklist. This is the same reasoning `decisions.md` already applies to
keep your own three reviews out of the loop, extended to other people's
reviews. **Recommended: do not run this check. Do not run any version of
it against an M3 candidate — a good candidate is meant to score some
projects differently than the current checklist does, so a close match to
human scores there is a bad sign, not a good one.**

**A use your framing does not mention: settling a live dispute inside v0.**
A2 above shows the `mixed_result` reading of `retrieval_best_approach_shipped`
decides the score of both extracted records and the one working twin pair.
If real reviewers, facing a project with metrics that disagree, mostly gave
the two-point tier, that is direct evidence for the reading v0 already
uses. If they mostly gave one point, that is evidence against it. This is
a strong, low-cost use of the same ten records, once check 1 runs.

**A second use: corpus growth.** If the ten repositories carry real commit
hashes, they can join `role: corpus` and grow the extraction base from 12
to 22. Item 3k and item 3d from the deferred-items triage both need a
clean base for `config-drift`, `circular-eval`, and `claim-without-artifact`,
and neither exists in the two extracted records so far. Ten more real
repositories raise the odds one exists. If the ten are chosen to include a
project near the 11-point line, they also close the gap `objective.md`
names directly under "No real near-threshold project is in the corpus."

**Open before this goes into `plan.md`:**

- Do the ten come with commit hashes and public repository links, or
  scores only? Without a repository, no evidence record can be extracted,
  and only a bare total is available for check 1, not a field-level trace.
- Where did the scores come from? `reviewer-project-background.md` states
  peer review scores are not published. Name the source, so the writeup
  can state how much weight the number carries.
- Is a per-criterion breakdown available, or only a total? A total can
  hide two errors that cancel out. A per-criterion breakdown is much
  stronger evidence for check 1.
- Do any of the ten overlap the twelve already planned for M2, or your own
  three past reviews? Overlap with your own reviews needs the same
  exclusion the project already applies elsewhere.
- Timing: running this once the schema is sealed, rather than only "at the
  end of M2," avoids a second extraction pass on these ten records if the
  schema changes after they are first extracted. It does not need to wait
  for the rest of the corpus to finish.

---

## Part B — reviewer observations, not owner decisions

### B1. a4's mutated fields cannot enter any prose-layer measurement.

Every field a4 changes carries `basis: constructed for the M1 red-team
round` and `evidence: <synthetic-attack>`. A reviewer model reading this
record is reading placeholder text, not a repository fact. F4's "type-
checked, 340 leaf values, all legal" claim confirms the record is
well-formed. It does not confirm the record is usable for any measurement
that reads `basis` as prose, including the agreement probe or a future
fidelity check.

**Evidence standard.** Direct read of `2026-08-12-m1-redteam_attack-a4.yaml`.

### B2. p01, p01-t05, and p01-t06 report the same input token count, and one of them should not.

All three report 4532 input tokens. `p01-t05` restates
`interface_framework.basis` from "Flask app, served by gunicorn" to
"FastAPI app, served by uvicorn." That is a real text change and should
move the rendered prompt's token count. Either the count is a coincidence,
or the prompt renderer is not including this field's `basis` text at all —
in which case both no-change twins are vacuous at the layer the agreement
probe measures.

**Evidence standard.** Manifest `input_tokens` fields, cross-checked
against the `basis` diff in `twins_p01-t05.yaml`. Cannot resolve further
without the renderer output; suggest diffing the two rendered prompts
directly.

### B3. The validation checklist mislabels which twin mutated a p02 field.

`2026-08-10-extraction-validation_checklist.md` flags p02's
`untraceable_number_count` as "mutated by p01-t03." `p01-t03` mutates
`p01`, not `p02`. The flag generator appears to key on field name only, not
on which base record the twin actually mutates.

**Evidence standard.** Direct read of the checklist line, cross-checked
against `twins_p01-t03.yaml`'s `twin.base_case_id`.

---

## What could sink this, distinct from what is merely wrong

M1's positive evidence for G1 reduces to one twin pair, and that pair
binds only under one interpretive reading `criteria.yaml` names as the
first thing to attack (A2). M1's negative evidence — two G1 failures, five
attacks — reduces to one mechanism (A4).

Set this beside item 3k from the deferred-items triage. If `config-drift`
and `circular-eval` hold across every corpus record, two catalogue types
have no real base to degrade from, and no corpus size fixes that. `plan.md`
already states the fallback position directly: G2 may prove near-vacuous,
G4 may ceiling out, G5 and G6 are compliance checks, so G1 plus the
catalogue carries the project's validity. M1's result is that G1
currently demonstrates one ordering, and that ordering is one clause
reading away from a tie.

This is survivable, and none of it is new information about whether the
project's approach is sound — it is information about how thin the current
evidence for that approach is. It stops being survivable only if the
writeup carries "two G1 failures and five successful attacks" as seven
independent pieces of evidence rather than one.
