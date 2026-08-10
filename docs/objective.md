# Objective — what "better" means

*Live document. Length budget: ~220 lines while G4's form is open; the M2
sealing decisions should shrink it back toward ~150.*

> **STATUS: APPROVED by the owner 2026-08-10**, replacing the 2026-08-09
> approval withdrawn by `tasks/reviews/review-01.md`. That review rebuilt
> G2 as a certification rate floor, split G3 into a gate plus ranking term
> R3, changed G6 from zero-spend to a cost ceiling, bounded the stopping
> criterion, and reopened G4. Approval unblocks M1 only. Two things are
> deliberately unresolved and are decided at M2, not before: **G4's form**
> (measured first, then chosen) and the **M3 round cap** (8, uncalibrated).
> Every other measurement parameter — G3 table and per-criterion cap, G4
> temperature, noise bands — freezes at M2 sealing, where the owner looks
> again.

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
  exactly equal — any movement is a failure. This gate alone eliminates the
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
  `g2-rate-not-count`): ≥9 of 12 today; a thirteenth *corpus* repo — the
  hoped-for real thin repo, since p13 is `role: self` and never counts —
  would make it ≥10. `role: self` and synthetic records are excluded
  throughout. *Non-vacuity guard*: constructed below-floor records (empty
  repo; no knowledge base or LLM in the flow) must **fail** certification —
  a candidate that certifies everything fails here, not in the rankings.
  *Baseline obligation (M2)*: measure v0's own certification rate r₀ over
  the corpus and record it. The erosion this gate permits is exactly
  r₀ − 75%, so it is **widest when v0 certifies everything** — the expected
  case — and the floor becomes *stricter than today* if r₀ falls below 75%.
  The working hypothesis (0 of 12 fail) is checked, never carried forward.
- **G3 — review-time ceiling.** Reviewer minutes come from a fixed cost
  table keyed by evidence-field type, set with the owner at M2 and
  read-only to every agent — never from the candidate's own claims. A
  candidate's cost is the sum of table entries over the fields its mapping
  reads; it must not exceed **150% of v0's cost** computed from the same
  table. Additionally, **no single criterion may exceed a per-criterion
  minute cap**, owner-set at M2 alongside the table: reviewers skip
  individually expensive criteria, so the careless-application risk is
  per-criterion, not only aggregate (decision `g3-per-criterion-cap`). The
  preference for staying *near* current cost lives in R3, not here.
- **G4 — agreement floor (form resolved at M2, *after* the baseline is
  measured).** What G4 measures is **same-model self-consistency** of the
  candidate's prose layer — three stateless samples per case from one
  Gemini model at a fixed temperature above zero (frozen at M2), evidence
  fields shuffled in an order seeded by (case-id, sample-index,
  protocol-version), protocol-version in the cache key — compared against
  the current rubric's own figure, measured once on the same case subset
  with the same protocol. It is not human reviewer agreement and not
  cross-family agreement (a single M4 measurement on a subset); the writeup
  may not use the bare word "agreement" without this qualification.
  **Owner decision 2026-08-10: measure the baseline first, then choose the
  form** — a tolerance fixed before the number is known would be invented
  rather than reasoned. Options carried to M2: (1) *strict ≥ baseline*,
  which keeps the cliff and demands prose as unambiguous as checkboxes;
  (2) *noise-band tie*, tolerating noise but no real drop; (3) *noise band
  plus owner-set δ*, at the cost of one more owner-set number; (4) *demote
  G4 to a reported metric*, no cliff and no floor. **The owner's stated
  tendency is (4)**, because the real process already absorbs reviewer
  variance by design: the course assigns three independent human reviewers
  and takes the **median** of their grades (`sources.md`), so one
  reviewer's inconsistency cannot move the outcome, and a per-reviewer
  consistency floor over-constrains the candidate. Residual to weigh at M2,
  recorded now: a median of three absorbs *dispersed* disagreement, not
  *systematic* ambiguity — a criterion vague in a way that moves all three
  reviewers together, or splits them bimodally, is not defended against by
  a median, and under (4) nothing else in this objective floors prose
  clarity. *Ceiling check* applies whatever the form: if the baseline comes
  back ≥ 0.95, same-model self-consistency cannot separate candidates and
  G4 is reported as decorative — never as a passed gate.
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
consequence, accepted: with twelve records the R1 band is wide, R1 ties
will be common, and R2 carries more of the ranking work than its position
suggests.

- **R1 — discrimination.** Spread of candidate scores over the `role:
  corpus` records versus v0's spread on the same records: count of distinct
  totals first, standard deviation within its band as tiebreak. Synthetic
  records are excluded. R1 precedes R2 by owner confirmation (2026-08-09).
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
- **No real near-threshold project is in the corpus.** Synthetic thin
  records probe the certification boundary partially; the gap closes only
  when a real thin repo is added, and until then every G2 claim carries
  this caveat.
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

**Round cap.** M3 runs at most **8 budgeted discovery rounds**. Rounds are
owner-paced by design, so the cap is sized by owner availability, not
quota. Owner note 2026-08-10: **8 is uncalibrated and nobody can calibrate
it yet** — no round has run, so its real cost in owner time is unknown. It
is therefore a stop-and-look point rather than a limit believed correct:
resizable at M2 sealing, and resizable again once the first two rounds
have shown their actual pace, with the resize and its reason logged in
`runs/`. If the cap is reached without
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
