# Review — decisions.md / findings.md staleness audit — results

**Addendum, 2026-08-21: owner sign-off received on A1, A2, A3, A5, and the
new A6 tally; A4's questions answered with verified numbers. All approved
fixes below have been APPLIED to `docs/decisions.md`, `docs/findings.md`,
and `docs/superseded.md` — this file is kept as the original review
record and is not rewritten to hide what changed. See the end of this
document for the full log of what was actually edited, one extra finding
the A6 tally surfaced (`constructed-base-policy` undercounted its own
record list), and the answers to A4's two open questions.**

Produced from an independent, fresh-session review of `docs/decisions.md`
(900 lines) and `docs/findings.md` (548 lines) against `CLAUDE.md`'s stated
contracts for those two files, run after step 10's `decisions.md` entries
were written. Six independent checks (task items A1–A3, B1–B4) were run in
parallel, each re-deriving its verdicts directly from the cited artifacts
(`cases/records/*.yaml`, `cases/schema.md`, `candidates/v0/criteria.yaml`,
`runs/2026-08-18-m2-sealing-checklist/checklist.md`,
`runs/2026-08-19-m2-step9-measurements/report.md`,
`runs/2026-08-20-m2-step10-sealing/checklist.md`, `loop/agreement.py`,
`docs/superseded.md`), not from memory of the M2 work.

This is not a review of whether the decisions were right — only of whether
the two documents still say what is true now, per each file's own stated
contract.

---

## Part A — items that need an owner decision

### A1. `decisions.md`'s M2-schema-closure entry still says "Not yet sealed"

The unnamed entry under `## Schema` beginning "**M2 schema closure
(2026-08-13).**" (around line 678) ends: *"Twenty of twenty-one resolved
below; item 3e stays open, entry below states why. **Not yet sealed**
(`tasks/03-milestone-2.md` step 8 is a separate, later gate)."*

Both the step-8 sealing-readiness checklist (2026-08-18) and the step-10
formal sealing STOP (2026-08-20, "CLOSED 2026-08-20... all six rows below
are resolved") have since completed. M2 is sealed. The "Not yet sealed"
parenthetical is now factually false — it predates two later gates that
have both closed.

Item 3e correctly staying open is a separate, still-accurate fact,
already carried by `retrieval-best-approach-not-normalised-open` — this is
not being reopened. Only the "Not yet sealed" clause needs updating.

**Proposed fix:** strike or reword the parenthetical, e.g. "Sealed at step
10 (`runs/2026-08-20-m2-step10-sealing/checklist.md`); item 3e's open
status is unaffected and tracked separately below." Awaiting sign-off
before editing.

### A2. Two citation errors found by direct verification against records/artifacts

**`sealing-review-fixes`** (line ~123) states: *"21 of 23 records land
`undeterminable` for label origin."* Direct count over
`cases/records/*.yaml`'s `retrieval_eval_label_origin` field: **20**
`undeterminable`, 2 `none` (p05, p23), 1 `human_labelled` (p03) — 23 total.
The entry overstates the `undeterminable` count by one.

**`monitoring-instrumentation-boundary-fixed`** (line ~283) states:
*"Checked 9: p05, p07, p09, p14, p17 misclassified... p04, p06, p08, p10,
p12 confirmed already correct."* That is 10 named records, not 9 — the
entry's own list contradicts its own count. Worse, it omits **p11**
entirely. The cited source, `runs/2026-08-18-m2-sealing-checklist/checklist.md`
B1, states 11 records were checked (adding p11), with p11 among the six
"confirmed already correct" — `cases/records/p11.yaml` independently holds
`monitoring_instrumentation: logged`, consistent with that. The
decisions.md entry's record count and record list both diverge from its
own cited source.

**Proposed fix:** correct "21 of 23" → "20 of 23" in `sealing-review-fixes`;
correct "Checked 9" → "Checked 11" and add p11 to the confirmed-correct
list in `monitoring-instrumentation-boundary-fixed`. Neither changes any
scoring outcome or conclusion — both are transcription slips in the
decision text, not in the underlying work. Awaiting sign-off before
editing.

### A3. `findings.md` F6 describes a criteria-exclusion scope that step 10 later corrected — a log entry now silently contradicted

F6 (2026-08-19) states bonus exclusion as: *"`bonus_cloud_deployment` and
`bonus_discretionary` are excluded from `max_total` and every total
here"* and *"per-criterion agreement clears 95% on 11 of 12 remaining
criteria."* This was accurate against its own source artifact
(`runs/2026-08-19-m2-step9-measurements/report.md`) at the time.

Step 10 (2026-08-20) narrowed the exclusion: `g3-g4-r1-exclude-bonus-discretionary`
excludes **only** `bonus_discretionary` from G3/G4/R1 — `bonus_cloud_deployment`
was never meant to be excluded, and `g4-form-frozen` correspondingly
reports **"12 of 13 criteria clearing 0.92 weighted"** (13 total criteria,
not F6's 12). `bonus_cloud_deployment` scored a clean 1.0000 either way, so
F6's headline numbers (0.7726 case-level, 0.8668 reproducibility, 36.6%
exact-match) are unaffected — but F6's own prose about *what was excluded*
and *how many criteria remain* no longer matches the corrected, sealed
scope, and nothing in F6 or a later findings.md entry cross-references the
correction. This is exactly the failure mode CLAUDE.md's log convention
warns about: findings.md doesn't self-update, but a later entry silently
contradicting an earlier one without cross-referencing is still a defect.

**Proposed fix:** since findings.md is append-only, this should not be
rewritten in place — add a short dated correction note either appended to
F6 or as part of F6's own text via a bracketed addendum (following the
pattern F6 itself already uses for its "Round 1... superseded above"
aside), stating that step 10 narrowed the bonus exclusion to
`bonus_discretionary` only and that the criteria count is 13, not 12.
Awaiting owner decision on exact placement/wording, consistent with the
"append, don't rewrite" convention for this file.

### A4. Two findings.md wording issues surfaced by a full linear read, flagged for owner judgment

**F6's "did not shrink" claim is not supported by its own numbers.** F6
states: *"the defect `agreement-total-recomputed` found at 67%-of-24 in the
M1 smoke test did not shrink with 5x the case count"* — but F6's own
adjacent number is 69/123 = 56%, an 11-point drop from 67%. The defect
clearly remains large (56% is still bad), but "did not shrink" is not what
the arithmetic shows. This reads as an unflagged overstatement, not an
intentional correction. Needs either a wording fix ("remained large" rather
than "did not shrink") or an explicit justification for why 56% counts as
statistically indistinguishable from 67% — that judgment call belongs to
the owner, not to this audit.

**F5's "thirteen small integers" doesn't match any criteria count on
record.** F5 says the model was *"failing to add thirteen small
integers correctly"* (i.e., criteria count). `candidates/v0/criteria.yaml`
defines 14 scoring criteria total (12 non-bonus + 2 bonus); F6 separately
confirms a 12-criteria non-bonus count. "Thirteen" matches neither 14 nor
12, and nothing in findings.md explains what it does count. Resolving this
needs inspecting the actual M1-era cached reviewer response format, which
is outside `decisions.md`/`findings.md` — handing to the owner rather than
chasing it further per this task's scope.

### A5. Two `decisions.md` topic clusters restate the same numeric finding independently, and one leaves a scope question unanswered

**`retrieval-best-approach-not-normalised-open`** (line ~781) restates,
without citing it, numbers `sealing-review-fixes` (line ~148) already
computed — "8 of 9 mixed_result records hold `decision_basis: measured`,
only p01 doesn't" and "6 of 9 also hold `retrieval_eval_config_matches_shipped:
differs`" appear near-verbatim in both entries. Both cite the same
underlying artifact (the sealing checklist), so a reader can reconcile
them, but neither entry cites the other by slug — a future reader scanning
decisions.md alone can't tell these are the same finding restated with
added detail rather than two independent confirmations.

**The G3/G4/R1 bonus-exclusion cluster has the same problem, plus a real
open question.** `agreement-excludes-bonus-points` (2026-08-19) and
`g3-g4-r1-exclude-bonus-discretionary` (2026-08-20) both independently
state the "7 of 41 cases" `bonus_discretionary` full-range-swing fact,
without cross-referencing each other. More substantively: the earlier
entry excludes **two** fields (`bonus_cloud_deployment` and
`bonus_discretionary`) from G4; the later entry only names
`bonus_discretionary` for G3/G4/R1 and never states `bonus_cloud_deployment`'s
status in G3 or R1 specifically. Given A3 above (F6's exclusion scope was
narrowed at step 10), this is not just a cross-reference nit — it's an
open question about what the sealed scope actually is for G3/R1, and needs
an owner ruling, not just a citation fix.

**Proposed fix (owner decision needed on the second item; the first is a
cheap add):** add a slug cross-reference in
`retrieval-best-approach-not-normalised-open` pointing to
`sealing-review-fixes`. For the second cluster, state explicitly whether
`bonus_cloud_deployment` is excluded from G3's cost table and R1's
statistic (as F6/`g4-form-frozen`'s corrected 13-criteria count implies it
is *not* excluded from anything but G4... or clarify if it should be).

### A6. F1/F2's promised "first honest base rate" from M2 never explicitly lands in findings.md

F1 and F2 (both 2-record, M1-era findings) each state, nearly verbatim,
that the M2 extraction "is the first honest base rate" for `config-drift`
and absent judge spot-checking across the full corpus. F6, the M2 entry
built on the full 22-repo corpus, reports certification rate, real-score
fidelity, and self-consistency — but never reports a corpus-wide base rate
for `retrieval_eval_config_matches_shipped`/`llm_eval_config_matches_shipped`
or `llm_eval_judge_spotchecked`, the specific numbers F1/F2 promised M2
would deliver. Not a contradiction — nothing in F6 says the opposite — but
a promise made twice and apparently left unfulfilled within this file. If
the base rate was computed elsewhere (e.g. in a `runs/` report not
reflected in findings.md), that's a missing forward-pointer, not a missing
computation; if it wasn't computed at all, that's a genuine gap worth
naming. Owner call on which it is and whether a findings.md entry is
warranted.

---

## Part B — mechanical checks settled directly, no owner decision needed

### B1. Dead-citation sweep — clean

Every backtick-quoted file path (27 distinct), schema/criteria field name
(~33 distinct), and tool/function reference in `decisions.md` was checked
against the current repo state. All resolve. Renamed fields
(`retrieval_eval_relevance_rule` → `retrieval_eval_match_strictness` +
`retrieval_eval_label_origin`; `decision_documented: bool` →
`decision_basis`) are correctly documented as historical in
`cases/schema.md` and match what the citing entries claim.
`v0-requires-config-match` correctly resolves to an entry in
`docs/superseded.md`. No broken citations found.

### B2. `A1` open/deferred language sweep — all genuinely open except the item moved to A1 above

Every "stays open" / "deferred" / "pending" hit in `decisions.md` was
checked against later entries and the two most recent sealing artifacts.
Confirmed still accurately open: `retrieval-best-approach-not-normalised-open`
(item 3e), `g4-r2-noise-band-deferred`, `r1-statistic-frozen`'s noise-band
clause, `group-j-restructure-deferred`, `m3-round-cap-kept-at-8`, and the
conditional clause in `claim-without-artifact-p04-entailment` (no third
field has triggered it — verified `APPROVED_ENTAILMENTS` in
`tools/generate_twins.py` still holds only the two originally-scoped
entries). The R1/G2 guardrail design question exists now
(`g2-certify-loss-citation`, `r1-g2-tension-sensecheck`), was resolved at
step 10, and is correctly written as closed rather than left dangling as
open — no staleness there. The one stale item found (the "Not yet sealed"
parenthetical) is reported under A1, since fixing a live document needs
sign-off.

### B3. `Binds:` line inventory and accuracy — list corrected, all three accurate

The task's suggested five-slug list does not match the file as it
currently stands. A fresh grep found only **three** slugs carrying an
actual `Binds:` line: `agreement-stores-per-criterion`,
`group-j-restructure-deferred`, `group-h-worked-example-post-hoc`.
`binds-line-going-forward`, `monitoring-instrumentation-boundary-fixed`,
`p21-gap-count-reconfirmed-not-corrected`, and `agreement-excludes-bonus-points`
contain no literal `Binds:` line (the first only discusses the mechanism,
never states its own binding). All three that do exist were verified
accurate against current state:

- `agreement-stores-per-criterion`: claims the next `agreement.json` will
  carry `per_criterion` per case. Confirmed live in `loop/agreement.py`'s
  `summarise()`; the one run since (`runs/20260819T135911Z-agreement/`)
  predates the change and correctly lacks the field, consistent with the
  entry's "not retroactive" claim.
- `group-j-restructure-deferred`: "Binds: none new" — a negative claim,
  accurate on its face.
- `group-h-worked-example-post-hoc`: "schema read-only after sign-off rule
  stands unchanged" — confirmed: subsequent schema edits were all
  owner-approved sealing-checklist actions, not unilateral agent edits.

**This list itself should replace the task's assumed five-slug list if
this check is ever repeated** — the file has moved on since that list was
written.

### B4. `monitoring_instrumentation` duplicate-cluster check — clean

`monitoring-instrumentation-boundary-fixed` (classification-rule fix) and
`single-repo-fields-kept` (field-retention decision, citing cross-repo
variation) only share the field name in passing and make no overlapping
claim. No duplication found here — contrast with the two clusters flagged
under A5.

### B5. Citation-accuracy spot-checks that matched cleanly

Beyond the two mismatches reported in A2, every other spot-checked claim
matched its cited artifact exactly: `p21-gap-count-reconfirmed-not-corrected`
(gap count 2, both gaps' basis text); `agreement-excludes-bonus-points`
(max_total 26→21, "7 of 41"); and every entry citing
`runs/2026-08-20-m2-step10-sealing/checklist.md` — `g3-per-criterion-cap`
(60 min), `g3-cost-table-frozen` (129 min / 193.5 min ceiling, 13-row
table), `g3-g4-r1-exclude-bonus-discretionary` ("7 of 41" / "9 of 41"),
`g4-form-frozen` (0.7726, 0.8668, 12/13 ≥0.92), `g2-certify-loss-citation`
(mechanism description), `r1-g2-tension-sensecheck` (15.9-point erosion
budget). No further action needed on any of these.

### B6. F6's other headline numbers — clean, cross-checked against `decisions.md`'s citations of the same source

r₀ = 20/22 = 90.9%, 15.9pp erosion budget, real-score check (10/10
certification-decision, 1/10 exact-total, 8-below/1-above-at-p21), 36.6%
exact-match / 0.7726 weighted, reproducibility 0.8668, 69/123 (56%)
arithmetic-defect rate, and the Round-1 superseded figures (29.3% / 0.7157)
all match their source reports exactly and match every place `decisions.md`
cites the same numbers. No drift found beyond the scope issue in A3.

---

## What could sink this, distinct from what is merely unfinished

This audit trusted its own sub-checks' greps and record reads as ground
truth without a second independent re-verification pass — the same
methodological risk `CLAUDE.md`'s "claims are traceable" rule exists to
guard against, applied here to the audit itself rather than to the
project's substantive findings. If any sub-check's grep missed a hit
(e.g., an "open" phrasing worded differently than the patterns searched,
or a citation format the B1 sweep's path/field heuristics didn't catch),
this results doc would under-report staleness rather than over-report it —
the failure mode is silent, not loud. The one item most likely to hide a
miss this way is B1 (dead citations): it enumerates "distinct" tokens by
the auditing agent's own judgment of what counts as a citation, and a
citation in an unusual format (e.g. embedded in a sentence without
backticks) would not have been checked at all.

Separately: A3's and A4's findings.md issues are reported as needing owner
sign-off on *how* to annotate a log file that is not supposed to be
rewritten in place — but no such annotation convention currently exists in
`findings.md` beyond the informal aside pattern F6 itself uses for its
Round-1 figures. If the owner wants a stricter convention (a dedicated
"corrections" section, dated addenda inline, or a separate log), that's a
new process decision this audit surfaces but does not resolve.

---

## Resolution log (2026-08-21)

Owner reviewed Part A and gave sign-off on A1, A2, A3 (with the
correction that `bonus_cloud_deployment` is **not** excluded — only
`bonus_discretionary` is, per the sealed step-10 scope), and A5 (explicit
preference for one unified entry over cross-referenced duplicates, to
keep `decisions.md` from growing). A4 raised two direct questions,
answered below with verification, not assertion. A separate LLM-reviewer
pass flagged the G3/G4/R1 bonus cluster as a bigger issue than a
duplicate — checked, and it was right that it needed Part A treatment,
though the specific fear (a stale 0.7726 number) did not materialize.

### A1 — applied

The M2-schema-closure entry's "Not yet sealed" parenthetical was rewritten
to state M2 sealed at step 10, with item 3e's open status carried forward
unchanged, cross-referenced to `retrieval-best-approach-not-normalised-open`.

### A2 — applied

`sealing-review-fixes`: "21 of 23" → "20 of 23" (with the other two
values named: 2 `none`, 1 `human_labelled`). `monitoring-instrumentation-boundary-fixed`:
"Checked 9" → "Checked 11", p11 added to the confirmed-already-correct
list, matching `runs/2026-08-18-m2-sealing-checklist/checklist.md` B1
exactly.

### A3/A5 — applied, as a full consolidation rather than a cross-reference

Checked the LLM reviewer's specific worry directly before touching
anything: **is the 0.7726 case-level weighted-agreement number actually
stale under the corrected 13-criterion scope, or does it just look that
way?** `runs/2026-08-20-m2-step10-sealing/checklist.md`'s own
per-criterion table lists `bonus_cloud_deployment` at exactly **1.0000**
weighted — zero disagreement across all 41 cases. A criterion with zero
disagreement adds an identical increment to all three samples of every
case, which cannot change which cases' totals agree or disagree — so
0.7726 is genuinely unchanged between "12 criteria, both bonuses excluded"
and "13 criteria, only `bonus_discretionary` excluded." **The number was
never wrong; only the scope description around it was.**

Given that, and per the owner's explicit preference for one unified
entry over duplicated-and-cross-referenced ones: `agreement-excludes-bonus-points`
(2026-08-19, the superseded scope) was moved to `docs/superseded.md` in
full, following the same reversal pattern already used there for
`v0-requires-config-match`. `g3-g4-r1-exclude-bonus-discretionary`
(2026-08-20, the correct scope) now carries a `Supersedes:` line, the
corrected max_total (26 → 23, not 21), and an explicit statement that
`bonus_cloud_deployment` stays in scope for G3/G4/R1. `findings.md` F6 was
rewritten in place (owner explicitly said correctness matters more than
strict append-only for this) to state the 13-criterion scope, with a
dated `[Corrected 2026-08-20]` marker showing what F6 originally said and
why the correction doesn't move any measured number.

The separate `sealing-review-fixes` / `retrieval-best-approach-not-normalised-open`
duplicate (items (4)/(5) restating the same mixed_result/config-drift
numbers) was resolved the same way: `sealing-review-fixes` now points to
the canonical entry instead of restating its numbers, since the canonical
entry already carries strictly more detail (the p02 nuance).

### A4 — answered, no file changes required beyond the formula wording

**"Shouldn't the erosion budget be `r₀ × 75%`, not `r₀ − 75%`?"** No —
`r₀` and `75%` are both already rates (fractions of the corpus), so
subtracting them gives a meaningful quantity in percentage points: how
far the certification rate can fall before breaching the floor.
Multiplying two rates together would produce a rate², which isn't a
meaningful quantity here. **However, a real precision issue exists that
your question surfaced**: with 22 discrete corpus records, no whole count
lands exactly on 75% (16/22 = 72.7%, 17/22 = 77.3%). The true minimum
passing count is 17, so the actual usable safety margin is **3 records**
(20 currently certify, 17 is the floor), which is 13.6 percentage points —
not 15.9. The stated 15.9pp is a continuous idealization that overstates
the real cushion by about 2.3 points (roughly half a record). This affects
no conclusion currently drawn from the number (both readings say "a real,
non-trivial cushion exists"), but it's worth a one-line clarifying note in
`objective.md` and `r1-g2-tension-sensecheck` if you want the precise
discrete figure on record — not applied here since it wasn't part of your
explicit approval list; flagging for a follow-up decision.

**The weighted-agreement formula's phrasing.** Your reading was exactly
right: "3/3"/"2/3"/"0/3" denote case *counts* in each agreement category
(15, 25, and 1 of 41 cases respectively), not literal fractions being
multiplied. Verified arithmetically: (15×1.0 + 25×0.667 + 1×0.0)/41 =
0.7726, exact match. `findings.md` F6 has been reworded to state this in
plain language instead of the compressed pseudo-algebra.

**F5's "thirteen small integers."** Checked against an actual cached M1
response (`.cache/6e/6eafabea...json`, case p01, protocol_version 1): the
model's response lists **14** criteria entries (12 scored + both
`bonus_cloud_deployment` and `bonus_discretionary`), matching v0's
`criteria.yaml` as it existed at the M1 commit (`9e9e625`) — 14 criteria
existed from the start, and the bonus-exclusion decision postdates F5 by
over a week, so "13" was never correct at any point, for either reason.
Fixed to "fourteen" in `findings.md`, with a note explaining why the later
exclusion doesn't retroactively justify "thirteen."

### A6 — resolved with an actual tally, not a cross-reference (per the LLM reviewer's recommendation)

Tallied `retrieval_eval_config_matches_shipped`, `llm_eval_config_matches_shipped`,
and `llm_eval_judge_spotchecked` directly across all 23 committed records,
split by `role`. Results, added to `findings.md` as a dated addendum to
F6:

- **Judge spot-checking**: the reviewer's hypothesis holds exactly. Only
  p13 (`role: self`) holds `llm_eval_judge_spotchecked: true`; among the
  22 `role: corpus` records the rate is **0/22**. This sharpens F1's
  original 2-of-2 finding into a full-corpus result: no real corpus
  submission's judge is ever spot-checked, and the one apparent exception
  doesn't count toward the population.
- **Config-drift did not sharpen the same way, and this tally caught a
  real error while computing it.** `constructed-base-policy`'s own claim
  — "p07, p09, p13 hold `matches` on both config fields" — undercounts:
  checked directly against the exact commit that decision was written
  against, p18, p19, p20, and p21 already held `matches`/`matches` at
  that time too. Corrected count: **6 of 22** corpus records match on both
  fields (not the claimed 3), 6 of 22 differ on both (the strong F1/F2
  form), and 10 are mixed. Fixed in `decisions.md`. Unlike judge
  spot-checking, config-drift does not generalize to "essentially every
  project" at corpus scale — F1/F2's "both projects" framing was accurate
  for n=2 but does not extend to "the whole corpus," only to a majority
  (16 of 22 differ on at least one field).

### What this changes about "what could sink this"

None of the applied fixes touch a measured statistic that any gate,
finding, or ranking decision currently depends on for its conclusion — the
0.7726/0.8668/36.6%/r₀ numbers are all unchanged. The fixes are entirely
in *scope descriptions*, *record counts*, and *citation accuracy* around
those numbers. The one exception worth naming plainly: `constructed-base-policy`'s
corrected record list (7 real bases instead of 3 for config-drift) was
never acted on to build additional twins beyond the ones already in the
catalogue — whether the twin catalogue should now be revisited given more
real bases exist than previously believed is a design question this audit
surfaces but does not answer.
