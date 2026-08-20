# M2 step 9 — measurements on the sealed case set

`tasks/03-milestone-2.md` step 9. Ordering per
`step9-runs-after-checklist-not-after-formal-seal` (`docs/decisions.md`):
runs after the sealing-readiness checklist is fully resolved
(`runs/2026-08-18-m2-sealing-checklist/checklist.md`), not after step 10's
separate formal sealing STOP, which still runs afterward unchanged.

Case set at measurement time: 22 `role: corpus` records (p13 excluded,
`role: self`) + 18 twins = 40 scored cases for 9(b)/9(c); the agreement
pass in 9(a) additionally includes p13 (41 cases total, since
self-consistency is a property of the executable layer + prompt, not
gated on corpus membership) — see `docs/decisions.md`
`corpus-twelve`/`g2-rate-not-count` for why p13 stays out of every rate
and distribution statistic specifically.

## 9(b) — v0's real certification rate r₀

Free, deterministic, `candidates/v0/score.py`, pass threshold 11
(`pass-threshold-11`).

**r₀ = 20 / 22 = 90.9%**

Non-certifying corpus cases: p05, p10. Every other corpus case certifies.

This replaces the "0 of 12 fail" working hypothesis named in the task file
with a measured number over the grown 22-repo corpus. It feeds G2's
erosion budget: the gate permits a candidate's certification rate to fall
no lower than 75%, i.e. an erosion budget of r₀ − 75% = **15.9 percentage
points**, not an arbitrary one (`g2-rate-floor`, `g2-rate-not-count`).

## 9(c) — real-score check 1

Free, deterministic. Does v0's computed total match what real reviewers
did, applying the same written criteria, on the ten real-score repos?
Method: `courses/llm-zoomcamp-2026/real-score-candidates.yaml` (gitignored)
matched to corpus case ids by commit hash against
`courses/llm-zoomcamp-2026/repos.yaml`; v0's `score()` run per matched
case; compared to the real score. **Per
`real-score-dataset-scoped`, the real score value is never printed beside
a repo id and no full per-repo score table appears anywhere below or in
any artifact this check produced — only match/mismatch verdicts and,
where mismatched, direction (never magnitude).**

10 of 10 candidates matched to a corpus case id (p14, p15, p16, p17, p18,
p19, p20, p21, p22, p23) — no unmatched candidates, consistent with
`corpus-twelve`'s "checked for overlap, none excluded."

**Certification-decision agreement: 10 / 10.** v0 and the real reviewer
never disagree on pass/fail for any of the ten.

**Exact-total agreement: 1 / 10** (p20). The other 9 mismatch. This is
not on its own a fidelity failure: `candidates/v0/criteria.yaml` states
plainly that 3 of 26 points are structurally unscoreable by any executable
layer, so every v0 total is a stated lower bound, not a claim of exact
reproduction (`cases/schema.md`'s scorer-output footer says the same).

Direction of the 9 mismatches: **8 below** (v0 < real — the expected
direction, consistent with the 3-point blind spot), **1 above** (v0 >
real — **p21**, the direction this check exists to catch, since v0 should
never score higher than a real reviewer applying the same written
criteria unless the transcription is over-generous somewhere).

**p21, investigated (no real score value used or needed for this):**
v0's per-criterion breakdown for p21 has one `unmatched` criterion
(`llm_evaluation` — no tier in `criteria.yaml`'s mapping fires for this
record's field combination, so it silently falls back rather than
awarding the intended tier) and one `unscoreable` criterion
(`bonus_discretionary`, 3 points, entirely judgment-based, no executable
layer can ever award it). Despite both of these working *against* v0's
total, v0 still comes out above the real reviewer once totalled. Two
readings, neither confirmed here: (a) the real reviewer under-scored this
specific project relative to the written criteria (human variance, not a
v0 defect — the real course medians three reviewers, this is one), or (b)
v0's mapping over-credits p21 on one of the 11 criteria it did score,
independent of the known `llm_evaluation` mapping gap. Not resolved by
this check alone — flagging as a named, real anomaly for the writeup
rather than either explaining it away or treating the 8-below pattern as
if it covered all 9.

**`mixed_result` reading question
(`retrieval-best-approach-reading-flagged`):** of the ten real-score
repos, exactly one (p14) holds `retrieval_best_approach_shipped:
mixed_result`. Its total does not match exactly (as expected — no case in
this batch besides p20 does), so this single data point cannot settle
whether `mixed_result` should count toward `retrieval_evaluation`'s
2-point tier the way `criteria.yaml`'s current mapping treats it — one
repo is not enough evidence either way, consistent with
`retrieval-best-approach-not-normalised-open` staying open and sealed as
a named risk rather than resolved (`docs/decisions.md`, checklist A3).

## 9(a) — baseline agreement

Real Gemini spend (`loop/agreement.py`, gate confirmed by owner
2026-08-19: `step9-runs-after-checklist-not-after-formal-seal`).
`DECLARED_BUDGET` bumped 60 → 155 for M2 scope (23 records + 18 twins × 3
samples = 123 calls + retry headroom); manifest notes updated from "M1
pipeline smoke test, baseline: false" to the real M2 baseline.

Dry-run cost, reported before spending per the task's budget hard limit:
123 requests needed (0 cache hits), well inside the 500 RPD daily quota
and the 155-request declared budget; token throughput stays under the
250K input-TPM cap at the configured throttle.

**Run complete: `runs/20260819T135911Z-agreement/`.** 123/123 requests
made (0 cache hits, as expected for a first M2-scope pass), 0 unparseable
responses, `outcome: complete`, `stopped_early: null`, `cases_not_reached:
[]`. Spend: 123 of the 500-request daily quota, well inside both the day
quota and the 155-request declared budget (31 retry-headroom requests
unused).

**This is the real M2 baseline** (`baseline: true` in both the manifest
and `agreement.json`), superseding the M1 pipeline smoke test
(`findings.md` F5). Same caveat as F5 applies unchanged: this measures
*same-model self-consistency* (three stateless samples, one Gemini model,
temperature 0.7, protocol version 2), not human reviewer agreement and
not cross-family agreement (`g4-is-self-consistency`) — the writeup may
not use the bare word "agreement" for it.

**The model's own arithmetic is still unreliable, at M2 scale.** 69 of
123 samples (56%) have a self-reported `total` that disagrees with the
sum of that same response's own listed per-criterion points — worse than
M1's 67%-of-24 finding only in that it confirms the defect did not shrink
with the larger case set. `loop/agreement.py`'s fix
(`agreement-total-recomputed`) — recompute mechanically from
`criteria[].points`, never trust the reported total — remains load-bearing
and every number below uses the recomputed total exclusively.

**Baseline agreement (exact-match self-consistency, the G4 ceiling-check
metric per `findings.md` F5's convention), bonus points excluded (owner
instruction, 2026-08-19 — see "Baseline agreement, in more detail"
below for the full reasoning): 15 / 41 = 36.6%.** Far below the 0.95
ceiling in `agreement-protocol-ceiling` — same-model self-consistency is
real, measurable variance here, not a ceiling artifact, so **G4 is not
decorative** and its *form* (one of the four options in `objective.md`,
owner's stated tendency toward (4) demotion to a reported metric) is a
live decision at step 10, informed by this actual number rather than an
assumption.

Twin-only vs. record-only spread is worth naming for step 10's
discussion, not analysed further here: constructed twins (`p01-t0N`,
`p12-t0N`, etc.) show the same order of spread as real records — self-
consistency is not obviously worse on synthetic cases, which was a live
concern going into this measurement (`a4-not-prose-fidelity-material`
raised a version of it for red-team cases specifically).

Full per-case totals, spreads, medians, and v0-diffs: `agreement.json` in
the run directory (linked above) — reproduced in the terminal output at
measurement time, not duplicated here to avoid a second, driftable copy.

## Why r₀'s two non-certifying cases fail

p05 and p10 both score exactly 10/26, one point under the 11-point
threshold — the only two non-certifying cases in the 22-repo corpus.
Investigated with the same rigor as the p21 anomaly (independent
per-criterion re-derivation from each record's actual fields, not trust
in the mapping). Both fail for ordinary, defensible reasons; no new
mapping gap, stale field, or misread turned up in either.

**p05** loses points across real, structural absences: no retrieval
evaluation (`retrieval_eval_present: false` — the one retrieval-testing
notebook prints raw results with no ground truth and no computed score),
no LLM evaluation (no prompt/model comparison anywhere, only an
unaggregated binary reaction), no containerization, and none of the three
best-practice techniques or cloud deployment — 0/2, 0/2, 0/2, 0/1 x3, 0/2
respectively, all confirmed against the record's own evidence. Its
`reproducibility: 1/2` is worth naming precisely: `data_accessible:
other` (confirmed directly — an external, key-gated source with no
access instructions given) would read 0 under a literal guidance reading,
but `run_instructions: partial` fires the unconditional 1-point tier
first, top-down. This is the exact, already-disclosed structural fact in
`criteria.yaml`'s own `reproducibility` `interpretation` block
(`data_accessible: other`'s 0-point tier is stated to be permanently
unreachable whenever `run_instructions` is `partial`/`complete`) — not a
new finding, and if anything means v0 is generous to p05 here, not
unfair. `run_instructions_gap_count: 6` independently corroborates that
this project's run process is genuinely broken (no schema-creation step,
no data-population step, a per-question call that crashes on every use).
p05's 10 is a real 10, arguably a slightly flattering one.

**p10** is a different shape: real evaluation work exists
(`retrieval_evaluation: 2/2`, text search demonstrably shipped and
verified to score higher on both reported metrics) but three other
criteria land low or unmatched. `reproducibility: 0/2` is solid and
severe — `run_instructions: none`, confirmed: "README states no setup,
dependency-install, environment-variable, or run command anywhere."
`llm_evaluation: 1/2` (fallback, unmatched) is the same disclosed gap
already named in the p21 investigation and in `criteria.yaml`'s own
`unmappable` block — an evaluation loop exists and is attempted
(`llm_eval_present: true`) but crashes before reporting any comparison
figures (`llm_eval_approaches_compared: 0`), a case the guidance's three
written tiers don't cover. `containerization: 0/2` (fallback, unmatched)
is the one genuinely first-occurrence case in this check: p10 is the
**only record in the 23-case corpus holding `containerization_kind:
other`** — Postgres and Grafana are containerized via raw `docker run`
commands wrapped in Makefile targets, real containerization work, but
neither a Dockerfile nor docker-compose, which are the only two
mechanisms the guidance names. Read literally, `other` matches no written
tier and falls to `fallback: 0` — a faithful transcription of a
guidance that is narrow about mechanism, not a v0 defect, but worth
naming since it is new: no other corpus record has exercised this
fallback path before. `problem_description: 1/2` (`problem_statement:
brief` — the topic is named, no audience is stated) rounds out the total.

Neither case's total traces to a mapping bug, a stale field, or a misread
requiring a decision before step 10. `containerization_kind: other`'s
fallback behavior is worth keeping in mind if a future candidate
broadens the containerization criterion's mechanism vocabulary, but it
does not block sealing or step 10 as v0 currently stands.

## Baseline agreement, in more detail (follow-up, no new spend)

The exact-match figure asks whether all three samples landed on the
*identical* total, a stricter bar than the real course itself uses
(three human reviewers, median taken, unanimity never required). Two
rounds of follow-up analysis, both computed from data already on disk —
zero new Gemini requests for either.

**Round 1** (superseded by round 2 below, kept here for the record, not
as the reported number): a 3-way exact-match breakdown (3/3 / 2/3 / 0/3),
per-criterion storage added to `loop/agreement.py`, a percentage-of-max
scoping exercise, and the raw p01/p12 samples — all computed with bonus
points still included. That pass found the two highest-total-spread
cases (p01, p12) disagreed almost entirely on `bonus_discretionary`, the
one criterion with no written tier.

**Round 2 — bonus points excluded from every total (owner instruction,
2026-08-19).** `bonus_cloud_deployment` (max 2) and `bonus_discretionary`
(max 3) are still scored by Gemini in every sample — nothing about what
the model judges changed — but are excluded from `max_total` (26 → 21),
every case total, and the per-criterion averaging table below. Reason:
round 1 found `bonus_discretionary` swings its full 0-to-3 range in 7 of
41 cases, an unusually volatile untiered field that was distorting the
case-level total-spread signal disproportionately to its actual
frequency of disagreement (`findings.md` F6 has the full round-1 finding
and the selection-bias correction). Recomputed via the same cache-replay
method as round 1 (0 new requests, 123/123 samples recovered, 0
unparseable — identical to every prior pass over this cache). Full
artifact: `runs/20260819T135911Z-agreement/agreement_detailed.json`.

**Case-level (bonus excluded):**

| bucket | count | % |
|---|---|---|
| 3/3 (all three identical) | 15 | 36.6% |
| 2/3 (exactly two agree) | 25 | 61.0% |
| 0/3 (all three differ) | 1 | 2.4% |

Weighted score (owner's formula: 1.0 × 3/3 + 0.667 × 2/3 + 0.0 × 0/3,
averaged): **0.7726**. Both numbers move up from the bonus-included
round (29.3% → 36.6% exact-match; 0.7157 → 0.7726 weighted) but not by
much — bonus points were a real contributor to case-level disagreement,
not the dominant one.

**Per-criterion (bonus excluded), same weighted formula, worst first:**

| criterion | n | 3/3 | 2/3 | 0/3 | weighted |
|---|---|---|---|---|---|
| **reproducibility** | 40* | 24 | 16 | 0 | **0.8668** |
| llm_evaluation | 41 | 38 | 3 | 0 | 0.9756 |
| best_practice_query_rewriting | 41 | 39 | 2 | 0 | 0.9838 |
| containerization | 41 | 39 | 2 | 0 | 0.9838 |
| ingestion_pipeline | 41 | 39 | 2 | 0 | 0.9838 |
| retrieval_evaluation | 41 | 39 | 2 | 0 | 0.9838 |
| best_practice_hybrid_search | 41 | 40 | 1 | 0 | 0.9919 |
| best_practice_reranking | 41 | 40 | 1 | 0 | 0.9919 |
| monitoring | 41 | 40 | 1 | 0 | 0.9919 |
| problem_description | 41 | 40 | 1 | 0 | 0.9919 |
| interface | 41 | 41 | 0 | 0 | 1.0000 |
| retrieval_flow | 41 | 41 | 0 | 0 | 1.0000 |

*`reproducibility` n=40: one sample (p09-t01, sample index 2) omitted the
criterion entirely from its returned list rather than misjudging it —
excluded, not padded, per `per_criterion_points()`'s no-guessing rule.

**With bonus excluded, every criterion but `reproducibility` clears 95%
weighted agreement** — 11 of 12 sit at 0.9756 or above, `interface` and
`retrieval_flow` at a clean 1.0. `reproducibility` alone drags the
distribution down, disagreeing (always by a narrow 1-point margin, never
full-range — confirmed in round 1's per-criterion severity check) on 16
of 41 cases, 39% of the corpus. This is the field with real written
tiers, not an open-ended judgment call — a criterion reviewers should in
principle converge on, and consistently don't.

**One honest divergence worth stating plainly, not smoothing over: the
case-level weighted number (0.7726) is well below the ≥95% most
individual criteria clear, not "somewhere similar" to it.** A case's
total requires all 12 remaining criteria to land on the same value
simultaneously for a 3/3 match; even with 11 of 12 criteria individually
agreeing ≥97.5% of the time, the *joint* probability of all 12 agreeing
at once compounds down fast. A back-of-envelope check confirms this
isn't a computation error: multiplying each criterion's own 3/3-rate
together (treating them as independent, which they are not exactly, but
close) gives ≈41% — the same order of magnitude as the observed 36.6%
exact-match rate. **Per-criterion agreement being high is compatible
with per-case agreement being much lower; they are not the same
question**, and this run shows both numbers rather than only the
flattering one.
