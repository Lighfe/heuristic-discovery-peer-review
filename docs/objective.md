# Objective — what "better" means

*Live document. Length budget: ~110 lines.*

> **STATUS: APPROVED by the owner 2026-08-09**, after two external review
> rounds (G1 satisfiability by construction, G2 anchored on candidate v0
> over a threshold band, G3 costs from an owner-set table, G4 protocol and
> ceiling check, R2 admitting novel attacks, noise-banded ranking with R1's
> band bootstrapped over records). Approval unblocks M1 only: every
> measurement parameter — G2 band, G3 table, G4 temperature, noise bands —
> freezes at M2 sealing, where the owner looks again.

A candidate is compared to another candidate — or to the current criteria —
**lexicographically**: first the gates, all of which must pass; then the
ranking terms, in order. A gate can never be traded against a ranking gain.

## Gates (all must pass; any failure discards the candidate)

- **G1 — twin ordering.** Every sealed twin pair is ordered correctly by the
  executable layer: the degraded twin scores strictly below its original on
  the total, and **ties count as failures**. No-change twins must score
  exactly equal — any movement is a failure. This gate alone eliminates the
  degenerate optimum. *Satisfiability is engineered, not hoped for*: the two
  halves bind on **disjoint field sets**. Degraded mutations must be
  categorical — each flips a fact any reasonable criterion tiers on
  (artifact exists or does not, configs match or do not) — while no-change
  mutations touch only fields outside the plausible read-set of any
  criterion. M1 tests this construction on the current instrument. If G1
  still proves unsatisfiable, that is an epistemics amendment and goes to
  the owner; a fraction-of-pairs floor is the candidate relaxation, and it
  is not available by default.
- **G2 — certification not withdrawn.** No institutional pass data exists —
  the 2026 cohort is under review now, and no published threshold or pass
  set is available to this project — so the gate anchors on construction.
  Candidate v0 (the current criteria transcribed faithfully into the
  executable layer, built in M1) supplies the current instrument's verdict
  on every `role: corpus` record. For **every threshold t in a stated
  plausible band**, the set of corpus repos clearing the candidate's
  certification gates must contain every repo scoring ≥ t under v0. The
  requirement is monotone in t, so it binds at the band's lower end. The
  band is an assumption, frozen at M2 sealing with the owner; if the course
  ever states the real threshold, the band collapses to that point and the
  gate is re-run. *Non-vacuity guard*: constructed below-floor records
  (empty repo; no knowledge base or LLM in the flow) must **fail** the
  candidate's certification gates — a candidate that certifies everything
  fails here, not in the rankings. `role: self` is excluded throughout.
- **G3 — review time not increased.** Reviewer minutes come from a fixed
  cost table keyed by evidence-field type, set with the owner at M2 and
  read-only to every agent — never from the candidate's own claims. A
  candidate's cost is the sum of table entries over the fields its mapping
  reads; it must not exceed v0's cost computed from the same table.
- **G4 — agreement floor.** Inter-reviewer agreement of the candidate's
  prose layer must be ≥ the current rubric's agreement, measured once on
  the same case subset with the same protocol (cached baseline). Protocol:
  three stateless samples per case from the Gemini reviewer at a fixed
  temperature above zero (value frozen at M2), evidence fields shuffled in
  an order seeded deterministically by (case-id, sample-index,
  protocol-version), protocol-version included in the cache key. *Ceiling
  check*: if the baseline comes back ≥ 0.95, same-model agreement cannot
  separate candidates; G4 is then declared non-binding and reported as
  decorative — never as a passed gate.
- **G5 — curriculum bound.** No criterion requires anything the course does
  not teach and the guidance does not tell authors to produce. Checked
  against the module list in the course repo; tools remain unrestricted, as
  the current guidance already promises.
- **G6 — no paid access.** Nothing in the candidate requires a reviewer to
  spend money or hold credentials.

## Ranking terms (order matters; applied only among gate-passing candidates)

Comparisons on all three terms are made within **noise bands frozen at M2
sealing** — never declared constants, and each derived from the right unit
of variation. R1's scorer is deterministic: its re-run variance is exactly
zero, and a band built from it would silently restore the strict ordering
banding exists to prevent. R1's band therefore comes from **bootstrapping
over the corpus records** — the uncertainty is which twelve repos happen to
exist, not run-to-run noise. Sampled measurements (G4, R2) take their bands
from measured re-run variation. Within a band the term is a tie and the
next term is consulted. Expected consequence, accepted: with twelve records
the R1 band is wide, R1 ties will be common, and R2 carries more of the
ranking work than its position suggests.

- **R1 — discrimination.** Spread of candidate scores over the `role:
  corpus` records versus v0's spread on the same records: count of distinct
  totals first, standard deviation within its band as tiebreak. Synthetic
  records are excluded from spread statistics. R1 precedes R2 by owner
  confirmation (2026-08-09): red-team resistance already has teeth in the
  stopping criterion, while discrimination is the project's stated goal.
- **R2 — red-team resistance.** Fewer successful attacks per budgeted
  round. An attack is a schema-valid record scoring in the top half of the
  corpus range whose structural badness is stated as a **checkable
  structural fact** — an existing catalogue definition or a new definition
  meeting the twin taste guard, written into the attack report. Novel
  definitions count immediately; owner approval gates only their entry into
  the case set. Every attempt, including failures, is logged in `runs/`.
- **R3 — reviewer cost.** Lower total minutes under the G3 cost table wins.

## What each number is computed from

Every measurement names its artifact: twin results, spread, and G2 band
results from scorer runs in `runs/` (recomputed, never carried forward);
agreement from cached reviewer transcripts; time costs from the owner-set
table applied to the candidate's declared field mapping. Prose summaries are
not evidence.

## Stated non-coverage and assumptions

- **No held-out case set exists.** All repos are read during development.
  The end-of-project consistency check is a sanity check and is reported as
  such, never as evidence.
- **G2's threshold band is an assumption**, stated, not knowledge. No pass
  set exists anywhere yet — reviewing is happening now, in the cohort the
  owner is part of — so G2 protects everyone who would pass under any
  threshold in the band, which is more conservative than knowing the true
  number, but is still conditional on the band containing it.
- **No real near-threshold project is in the corpus.** Synthetic thin
  records probe the certification boundary partially; the gap closes only
  when a real thin repo is added, and until then every G2 claim carries
  this caveat.
- **Twin tests validate the scoring layer only** (evidence→score). The
  repo→evidence step is covered separately by extraction validation and the
  prose↔executable fidelity measurement, and the final writeup may not
  merge these into one claim.

## Stopping criterion (for M3 discovery rounds)

Stop when simultaneously: (a) the current candidate passes all gates;
(b) two consecutive budgeted red-team rounds (fixed attempt count, every
catalogue category plus free-form) produce no new successful attack;
(c) the adoption critic raises no unresolved objection. The claim "nothing
new was found" is backed by the logged attempts, including the failures.
Diminishing returns is recorded in `findings.md` as a result.
