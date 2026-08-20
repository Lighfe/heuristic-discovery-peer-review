# Objective — what "better" means

*Live document. Length budget: ~220 lines while G4's form is open; the M2
sealing decisions should shrink it back toward ~150.*

> **STATUS: APPROVED by the owner 2026-08-10**, replacing the 2026-08-09
> approval withdrawn by `tasks/reviews/review-01.md`. That review rebuilt
> G2 as a certification rate floor, split G3 into a gate plus ranking term
> R3, changed G6 from zero-spend to a cost ceiling, bounded the stopping
> criterion, and reopened G4. Approval unblocks M1 only.
>
> **M2 sealing decisions, closed 2026-08-20** (`tasks/03-milestone-2.md`
> step 10; full working record in
> `runs/2026-08-20-m2-step10-sealing/checklist.md`): G3's cost table and
> per-criterion cap, G4's temperature and form, R1's primary statistic,
> the M3 round cap, and a new G2 addendum (certification-loss citation
> requirement) are all frozen — values stated inline at each gate/term
> below. **Two items remain genuinely open, not resolved by sealing**:
> R1's noise band and tie rule (need a bootstrap run against the newly
> chosen statistic, not yet done) and the G4/R2 noise-band form
> (deferred to M3 — it depends on real red-team re-run data that
> doesn't exist yet, and was never a pure M2 item).

A candidate is compared to another candidate — or to the current criteria —
**lexicographically**: first the gates, all of which must pass; then the
ranking terms, in order. A gate can never be traded against a ranking gain.

**v0 and the gates.** Candidate v0 (the current criteria transcribed
faithfully into the executable layer, built in M1) is the baseline, not a
candidate: it cannot be discarded, but it *is* run through every gate
measurement and the results recorded as baseline findings — under the
pre-review G6 wording v0 itself would have failed, a fact about the gate
caught by exactly this check. The asymmetry is deliberate, and stated once.

## Gates (all must pass; any failure discards the candidate)

- **G1 — twin ordering.** Every sealed twin pair is ordered correctly by the
  executable layer: the degraded twin scores strictly below its original on
  the total, and **ties count as failures**. No-change twins must score
  exactly equal — any movement is a failure. Documented-mitigation twins
  (harmful-component-kept's removal variant, circular-eval's spot-checked
  variant — `plan.md`'s catalogue) require a third relation, **`not_below`**:
  the mitigated twin scores no less than the case it mitigates (≥, not
  necessarily >, since documenting a sound decision need not outscore a
  record that already made the same call). Added 2026-08-13, formalising
  what the catalogue already required in prose; `p01-t02` used this relation
  in the M1 scorer manifest before it was defined here (review-m1.md A6).
  Only these three relations — `strictly_below`, `exactly_equal`,
  `not_below` — are defined; a scorer manifest recording any other relation
  name is a bug, not a result. This gate alone eliminates the
  degenerate optimum. *Satisfiability is engineered, not hoped for*: the two
  halves bind on **disjoint field sets** — degraded mutations flip a
  categorical fact any reasonable criterion tiers on; no-change mutations
  touch only fields outside the plausible read-set of any criterion. M1
  tests this construction on the current instrument; if G1 proves
  unsatisfiable, that is an epistemics amendment for the owner. The sealed
  set **grows over rounds** as owner-approved red-team types enter; G1
  always applies to the full current sealed set, never a one-time snapshot.
  *Scope of a G1 pass*: it demonstrates discrimination of the catalogued
  failure modes — the named types plus approved additions — not general
  discrimination. A candidate written to mirror the catalogue's taxonomy
  would pass G1 while proving nothing beyond it; generality is claimed only
  from red-team rounds (R2), and the writeup must scope G1 claims to
  catalogue coverage (decision `g1-claims-catalogue-coverage`).
- **G2 — certification rate floor.** **At least 75% of `role: corpus` repos
  must certify under the candidate.** *Certifying* means whatever the
  candidate's own text says earns the certificate: for a **threshold-based**
  candidate — v0 included, whose threshold is the course's **11 points**
  (provenance in `courses/llm-zoomcamp-2026/sources.md`) — total score ≥
  that threshold; for a candidate defining explicit certification gates,
  clearing those gates. The floor itself is absolute, never anchored on v0.
  Churn is allowed — a repo that passes today may fail under a candidate,
  provided the rate holds. 75% is a **minimum acceptable, not a target**:
  do not optimise toward it. It is a **rate, not a count** (decision
  `g2-rate-not-count`): ≥9 of 12 today. `plan.md` M2(e) grows the corpus by
  ten real, scored repos to 22 total — the floor recomputes against
  whatever the corpus is at M2 sealing, never carried forward as ≥9 of 12.
  `role: self` and synthetic records are excluded throughout. *Non-vacuity guard*: constructed below-floor records (empty
  repo; no knowledge base or LLM in the flow) must **fail** certification —
  a candidate that certifies everything fails here, not in the rankings.
  *Baseline obligation (M2)*: measure v0's own certification rate r₀ over
  the corpus and record it. The erosion this gate permits is exactly
  r₀ − 75%, so it is **widest when v0 certifies everything** — the expected
  case — and the floor becomes *stricter than today* if r₀ falls below 75%.
  The working hypothesis (0 of 12 fail) is checked, never carried forward.
  **G2 addendum, frozen at M2 sealing, 2026-08-20** (decision
  `g2-certify-loss-citation`): any `role: corpus` record that certifies
  under v0 but does not certify under a candidate must cite, in the
  candidate's writeup, a twin-catalogue entry or red-team finding ID —
  pre-existing or newly catalogued as part of the same candidate's own
  submission — whose **base record ID equals the record losing
  certification**, and which resolves to a real, logged entry in the
  case set or findings log. The check is mechanical: citation exists,
  base record matches, resolves to a real entry — never whether the
  cited defect is "good enough." **Record-specific only**; a general
  finding naming a class of affected records does not satisfy this
  without a citation built on the record in question. Records *gaining*
  certification are not covered — that risk (a record scoring
  artificially high despite real structural badness) is R2's territory.
  Reason: G2's erosion budget (r₀ − 75%) is legally available for any
  reason today, including spending it on discrimination rather than a
  genuine finding; this closes that gap without introducing a judgment
  call into a gate.
- **G3 — review-time ceiling. Frozen at M2 sealing, 2026-08-20**
  (decision `g3-cost-table-frozen`). Reviewer minutes come from a fixed
  cost table keyed by **criterion**, owner-set, read-only to every
  agent — never from the candidate's own claims:

  | criterion | minutes |
  |---|---|
  | problem_description | 2 |
  | retrieval_flow | 10 |
  | retrieval_evaluation | 15 |
  | llm_evaluation | 15 |
  | interface | 5 |
  | ingestion_pipeline | 5 |
  | monitoring | 7 |
  | containerization | 2 |
  | reproducibility | 45 |
  | best_practice_hybrid_search | 6 |
  | best_practice_reranking | 6 |
  | best_practice_query_rewriting | 6 |
  | bonus_cloud_deployment | 5 |

  `bonus_discretionary` carries no minute cost and is excluded from this
  table (decision `g3-g4-r1-exclude-bonus-discretionary`) — it is still
  scored by every criterion mapping exactly as the guidance states; the
  exclusion is measurement-scope only. **v0's total cost: 129 minutes.
  150% ceiling: 193.5 minutes.** A candidate's cost is the sum of table
  entries over the criteria its mapping reads (bonus_discretionary
  excluded the same way). **Per-criterion cap: 60 minutes**, anchored to
  `reproducibility`'s own real cost (45 min) plus its measured 60.0%
  self-consistency — the least reliably judged criterion by a wide
  margin (decision `g3-per-criterion-cap`): a cap set below
  reproducibility's real cost would force reviewers to shortcut exactly
  the criterion most prone to being gotten wrong under time pressure.
  The preference for staying *near* current cost lives in R3, not here.
- **G4 — agreement floor. Form frozen at M2 sealing, 2026-08-20**
  (decision `g4-form-frozen`): **option (4), demoted to a reported
  metric — never a blocking gate.** What G4 measures is **same-model
  self-consistency** of the candidate's prose layer — three stateless
  samples per case from one Gemini model at **temperature 0.7 (frozen)**,
  evidence fields shuffled in an order seeded by (case-id, sample-index,
  protocol-version), protocol-version in the cache key — compared
  against the current rubric's own figure, measured once on the same
  case subset with the same protocol. It is not human reviewer agreement
  and not cross-family agreement (a single M4 measurement on a subset);
  the writeup may not use the bare word "agreement" without this
  qualification.

  **Measured M2 baseline** (`runs/20260819T135911Z-agreement/`,
  `bonus_discretionary` excluded per scope): case-level weighted
  agreement **0.7726**. Per-criterion weighted, all 13 remaining
  criteria: `reproducibility` 0.8668 (the one exception); every other
  criterion clears **0.92** weighted, up to 1.0000 for
  `bonus_cloud_deployment`/`interface`/`retrieval_flow`. Reasoning for
  (4), confirmed against this number rather than assumed: the real
  process already absorbs reviewer variance by design — the course
  assigns three independent human reviewers and takes the **median** of
  their grades (`sources.md`), so one reviewer's inconsistency cannot
  move the outcome, and a per-reviewer consistency floor over-constrains
  the candidate. Residual, recorded not resolved: a median of three
  absorbs *dispersed* disagreement, not *systematic* ambiguity — a
  criterion vague in a way that moves all three reviewers together is
  not defended against by a median, and under (4) nothing else in this
  objective floors prose clarity; `reproducibility` is the one criterion
  showing this pattern today. *Ceiling check*: at 0.7726, same-model
  self-consistency is real, measurable variance, not a ceiling artifact
  — G4 reports something genuine, not a number that flatters every
  candidate.
- **G5 — curriculum bound.** No criterion requires anything the course does
  not teach and the guidance does not tell authors to produce. Checked
  against the module list in the course repo; tools remain unrestricted, as
  the current guidance already promises.
- **G6 — reviewer cost ceiling.** Reviewers do run project code with their
  own credentials: the course already asks students to hold an
  `OPENAI_API_KEY`, and executing is often the fastest reproducibility
  check, so a zero-spend rule fails the current practice it claims to
  protect. The gate is a ceiling: a candidate must not require a reviewer
  to spend more than **≈ €0.10** expected token costs out of pocket to verify 
  one project (reference: re-running the owner's own project cost €0.004), 
  and must not require paid subscriptions or credentials beyond what the course 
  already asks students to hold.

## Ranking terms (order matters; applied only among gate-passing candidates)

Comparisons are made within **noise bands frozen at M2 sealing** — never
declared constants except where review-01 set one (R3), each derived from
the right unit of variation. R1's scorer is deterministic — re-run variance
is exactly zero — so its band comes from **bootstrapping over the corpus
records**; sampled measurements (G4, R2) band on measured re-run variation.
Within a band the term is a tie and the next term is consulted. Expected
consequence, accepted at twelve records and re-checked once `plan.md`
M2(e)'s ten additional repos are sealed: the R1 band is wide on a corpus
this size, R1 ties will be common, and R2 carries more of the ranking work
than its position suggests. The bootstrap is recomputed against whichever
corpus exists at M2 sealing, never carried forward from twelve.

- **R1 — discrimination. Statistic frozen at M2 sealing, 2026-08-20**
  (decision `r1-statistic-frozen`): **record-count-normalized Shannon
  entropy** (H / log2(n), n = corpus record count) as the primary
  statistic, **IQR** (not standard deviation) as the tiebreak, computed
  over candidate scores on the `role: corpus` records versus v0's on the
  same records. Chosen over the original distinct-totals-count statistic
  because entropy retains frequency information distinct-count discards,
  and normalizing by record count (not by the candidate's own point
  range) was confirmed scale-invariant under a direct test — stretching
  the same 22 records' relative positions onto a wider point scale left
  this statistic exactly unchanged, while a range-width-normalized
  variant dropped purely from the wider scale with zero real change in
  discrimination. IQR chosen over std dev for robustness to the
  small-n outlier sensitivity this corpus shows. Synthetic records are
  excluded. R1 precedes R2 by owner confirmation (2026-08-09).
  `bonus_discretionary` is excluded from every R1 total (measurement
  scope only, decision `g3-g4-r1-exclude-bonus-discretionary`).
  A 10,000-resample bootstrap (seed 42) over the 22-record corpus was
  run against the *original* distinct-totals/std-dev statistic during
  the comparison that motivated this switch (distinct-totals point
  estimate 13, 5th-95th percentile band 8–12; std dev point estimate
  3.59, band 2.75–4.19) — informative for the choice above, but **not a
  noise band for the frozen entropy/IQR statistic**, which has not yet
  been bootstrapped itself. **Neither R1's noise band nor the tie rule
  for comparing two candidates' statistics is frozen yet** — both need
  the entropy/IQR statistic's own bootstrap run before R1 is usable for
  a real comparison.
- **R2 — red-team resistance.** Fewer successful attacks per budgeted
  round. An attack is a schema-valid record scoring in the top half of the
  corpus range whose structural badness is stated as a **checkable
  structural fact** — an existing catalogue definition or a new definition
  meeting the twin taste guard, written into the attack report. Novel
  definitions count immediately; owner approval gates only case-set entry.
  Every attempt, including failures, is logged in `runs/`.
- **R3 — reviewer cost, banded.** Differences of **less than 25% of v0's
  cost** under the G3 table are ties and pass to the next term. Above +25%
  (and below G3's 150% ceiling): ranked worse. Below −25%: **not
  rewarded** — treated as a tie and referred to the **adoption critic at
  the round boundary**, which must record either the explanation or the
  fact that none was found. Review time is not a problem this project set
  out to fix ("never change a running system"); a large unexplained drop
  more likely means a criterion got shallower than that review got more
  efficient.

## What each number is computed from

Every measurement names its artifact: twin results, spread, and
certification rates from scorer runs in `runs/` (recomputed, never carried
forward); agreement from cached reviewer transcripts; time costs from the
owner-set table applied to the candidate's declared field mapping. Prose
summaries are not evidence.

## Stated non-coverage and assumptions

- **Every threshold in this document is an owner-set judgment value, not a
  derived quantity**: the 75% floor (G2), the 150% ceiling and
  per-criterion cap (G3), the 25% band (R3), the ≈€0.10 ceiling (G6), the
  G3 cost-table values, the G4 temperature and tolerance, and the M3 round
  cap. Every gate resting on one inherits that conditionality, and the
  writeup says so. Excluded: the R-term noise bands, derived by frozen
  procedures (bootstrap over records; measured re-run variance) — there the
  judgment is the choice of procedure, not the number.
- **No held-out case set exists.** All repos are read during development.
  The end-of-project consistency check is a sanity check and is reported as
  such, never as evidence.
- **The 11-point threshold is owner-confirmed but not independently
  checkable** — it appears only behind the cohort login. It sets v0's
  certification line and therefore r₀; a stale figure would move the
  baseline, not the 75% floor.
- **No real near-threshold project is in the corpus yet.** Synthetic thin
  records probe the certification boundary partially; one of the ten repos
  in `plan.md` M2(e) scores exactly 11, the pass threshold, and the gap
  closes once it is extracted and sealed — until then every G2 claim
  carries this caveat.
- **Twin tests validate the scoring layer only** (evidence→score). The
  repo→evidence step is covered separately by extraction validation and the
  prose↔executable fidelity measurement, and the final writeup may not
  merge these into one claim.
- **Gate bindingness is reported per gate.** If G2 proves near-vacuous, G4
  ceilings out, and G5/G6 are compliance checks, "passed all gates" is two
  compliance checks, one gate that may not bind, one that may not
  discriminate, and one real test — and the writeup must present it that
  way, never as six independent pieces of evidence.

## Stopping criterion (for M3 discovery rounds)

Stop when simultaneously: (a) the current candidate passes all gates;
(b) two consecutive budgeted red-team rounds (fixed attempt count, every
catalogue category plus free-form) produce no new successful attack;
(c) the adoption critic raises no unresolved objection. The claim "nothing
new was found" is backed by the logged attempts, including the failures.
Diminishing returns is recorded in `findings.md` as a result.

**Round cap. Confirmed at M2 sealing, 2026-08-20** (decision
`m3-round-cap-kept-at-8`): **8 budgeted discovery rounds**, unchanged.
Rounds are owner-paced by design, so the cap is sized by owner
availability, not quota. Still uncalibrated — no round has run since the
original 2026-08-10 note, so there was nothing new to calibrate against
at sealing time either; kept as a stop-and-look point, to be revisited
once the first rounds show whether 8 is commonly maxed out, not resized
now on guesswork. If the cap is reached without
(a)–(c): the best candidate that passes all gates ships, labelled
**non-converged**, with its final red-team round's full attack log
attached; if no candidate passes all gates, nothing ships and the writeup
reports that as the project's result. "Ran out of rounds" is a recorded
outcome, never a silent stop.

**Provider failure, distinct from quota pause.** Daily quota exhaustion
pauses at the checkpoint and resumes tomorrow. A provider is declared
**failed** when a needed call has been attempted and errored (non-quota)
on **three distinct dates**, despite backoff and the configured fallback
list. The clock runs on **attempts, not the calendar**: this loop is
owner-paced, so weeks may pass with no attempt made, and no attempt is no
progress toward the condition. Then the loop stops cleanly, logs it in
`runs/`, and the owner chooses between re-configuring (new model version,
new cache namespace — results never mix across models) and waiting. The
same rule governs the M4 cross-family measurement; if the owner declines
to wait, M4 ships without it and the writeup states "cross-family
agreement: not measured — provider unavailable" as a named evidence gap,
not a footnote. (HF credits reset monthly, so *credit* exhaustion is a
quota pause, never a provider failure.)
