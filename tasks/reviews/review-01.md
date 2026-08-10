# Review 01 — owner review of `objective.md`, `plan.md`, `02-milestone-1.md`

Save as `tasks/reviews/review-01.md`. Produced from an owner walkthrough of the
three documents with an independent reviewer, 2026-08-10.

This file has two parts. **Part A** is owner decisions — action these. **Part B**
is reviewer observations raised during the walkthrough that the owner has *not*
decided on — check them, argue back where the reviewer is wrong, and record the
outcome in `docs/decisions.md`.

---

## 0. Status change — approval withdrawn

`docs/objective.md` currently carries **"STATUS: APPROVED by the owner
2026-08-09"**. That approval is **withdrawn**.

The changes in Part A are structural, not amendments: G2's anchoring
construction is replaced outright, G3 is split across a gate and a ranking term,
G6's threshold changes from zero to a ceiling, and one of the document's stated
premises turns out to be false (see A1). Re-issue the document as a draft, apply
Part A, and bring it back for approval.

Nothing here unblocks or re-blocks M1 by itself — but note that M1 step 5 builds
candidate v0, and A1 may change what v0 is anchored against.

---

## Part A — owner change requests

### A1. A real pass threshold exists. A stated premise is false.

`objective.md` G2 asserts, as the justification for its whole construction:

> "No institutional pass data exists — the 2026 cohort is under review now, and
> no published threshold or pass set is available to this project"

This is wrong. **The course states a pass threshold of 11 points.** It is not in
the GitHub guidance document; it is in other course documentation, which is why
it was missed.

Consequences:

- The premise must be corrected wherever it appears, not just in G2.
- The "plausible band of thresholds", the monotonicity argument, and "the band
  is an assumption, frozen at M2" all exist *because* no threshold was thought
  to exist. Much of that machinery is now unnecessary.
- **Before relying on it:** confirm 11 points is current for this cohort and not
  a figure carried over from an earlier iteration. Record where it was found.

Note that A2 replaces G2's construction anyway — but the corrected premise
matters independently, because a false premise in an owner-approved document is
a process failure worth understanding, not just a line to edit.

### A2. G2 — replace the superset guarantee with a certification rate floor

**Current:** for every threshold in a band, the set of repos the candidate
certifies must *contain* every repo v0 certifies. A relative, per-repo guarantee.

**Replace with:** an absolute floor on the certification rate.

- **≥ 75% of `role: corpus` repos must certify** under the candidate.
  `role: self` stays excluded.
- **Churn is allowed.** It is acceptable for a specific project that would pass
  under the current criteria to fail under a new candidate, provided the rate
  floor holds. The candidate does not have to certify the *same* set as v0 —
  only *at least as large a fraction*.
- **75% is a minimum acceptable, not a target.** Do not optimise toward it and
  do not treat 75% as a good/bad outcome. The final criteria will be reviewed by
  DataTalksClub, who can adjust anything they find too harsh or too lenient.
- Keep the **non-vacuity guard** unchanged — constructed below-floor records
  (empty repo; no knowledge base or LLM) must still fail certification.

Reasoning to record: the owner's position is that the *current* criteria certify
essentially any submitted RAG system, and that this is a defect the new criteria
must not reproduce. A gate that forbids any individual regression makes that
defect permanent by construction.

This reverses the CLAUDE.md framing **"the same people certified"** and the
"Certification stays achievable" bullet insofar as it was read as *per-person*.
The intent it was protecting — most people still pass, the course stays
finishable — is preserved by the rate floor. Update CLAUDE.md's wording to match,
or explain why it should stand.

Open sub-questions for the building agent:

- **Rate or count?** 75% of 12 is 9. The corpus grows to 13 at M2. Decide
  whether the floor is a fixed rate or a fixed count before M2 sealing.
- **Measure, don't assume.** The owner's working hypothesis is that **0 of 12**
  corpus repos currently fail at the 11-point threshold. This is free to check
  once v0 exists (scorer harness, no requests). Do it, and record the real
  number rather than carrying the hypothesis forward.

### A3. G3 — split into a loosened gate and a graded ranking term

**Current:** candidate reviewer-minutes "must not exceed v0's cost". A hard
ceiling at 0% increase, which fails a candidate that adds two minutes to a
one-hour review.

**Replace with:**

- **G3 (gate):** candidate cost must not exceed **150% of v0's cost**. Hard fail
  above that.
- **R3 (ranking term):** carries the preference for staying close to current
  review time. Target is **under +25%**. Small variance must not be penalised —
  see A4 for the tie band.

The cost table itself stays as designed: owner-set at M2, read-only to every
agent, never taken from a candidate's own claims.

### A4. R3 — tie band, and stop rewarding large decreases

- **Tie band:** differences of **less than 25%** in total reviewer minutes count
  as a tie; the comparison passes to the next term.
- **Large decreases are not automatically good.** R3 currently rewards lower
  minutes unconditionally. It should not reward a large drop that comes with no
  explanation.

Reasoning to record: *"never change a running system."* There are no complaints
that peer review currently takes too long, so review speed was never a problem
this project set out to fix. A large unexplained drop in review time is more
likely to mean a criterion got shallower than that it got more efficient.

### A5. G6 — a cost ceiling, not zero

**Current:** "Nothing in the candidate requires a reviewer to spend money or
hold credentials."

This does not survive contact with how reviews actually happen. **Reviewers do
run the code with their own credentials** — executing the project is usually the
fastest way to check reproducibility, and the course itself asks students to
hold an `OPENAI_API_KEY`.

**Replace with a ceiling:** a candidate must not require a reviewer to spend
more than approximately **$0.10** to verify one project. For reference, the
owner's own project cost **$0.004** to re-run.

See B2 — this change also raises a question about whether v0 clears G6 as
currently worded.

### A6. Stopping criterion — add an upper bound and a provider-failure stop

`objective.md`'s stopping criterion is (a) **and** (b) **and** (c),
simultaneously. There is no bound on how long that can take.

Add two separate things:

- **A maximum round count.** State the outcome if it is reached without (a)/(b)/(c)
  being met — does the best candidate so far ship, labelled non-converged, or
  does nothing ship? This must be explicit; "we ran out of rounds" is not a
  result unless the document says what it produces.
- **A provider-failure stop, distinct from a quota pause.** The plan already
  handles transient failures well (checkpoint, clean resume, backoff with
  jitter, fail loudly rather than switch models mid-run) and already treats
  daily quota exhaustion as a pause that resumes tomorrow. What is *not*
  covered is a provider being unusable for long enough that waiting is not
  viable — particularly HF at M4, where the cross-family agreement measurement
  has no substitute. Define a retry policy and a give-up condition, and state
  what M4 reports if the cross-family measurement cannot be taken.

Note for sizing the round cap: plan.md already makes M3 rounds **owner-paced by
design** (red-team case-set additions and epistemics questions batch at round
boundaries). The practical limit on round count is likely owner availability,
not request quota. Size it accordingly.

### A7. G4 — tolerance is unresolved, bring a proposal

**Not a decision — an open item to work through with the owner.**

G4 currently requires candidate agreement **≥** the current rubric's agreement,
with no tolerance. This is the same cliff-edge defect as the old G3: a
statistically meaningless dip (0.80 → 0.79) fails the candidate outright.

The owner's position, which the proposal has to accommodate:

- The current criteria's **simplicity is a genuine strength** — they are close
  to checkboxes, with little room for interpretation, and that is *why*
  agreement is high today.
- The owner does **not** expect any rewritten prose layer to fully reproduce
  that, and does not consider some agreement drop automatically disqualifying.
- No tolerance number is proposed. Do not invent one and treat it as settled;
  bring options with their consequences.

Keep the ceiling check as designed — if the baseline comes back ≥ 0.95, G4 is
reported as decorative, never as a passed gate.

---

## Part B — reviewer observations, not owner decisions

These came out of the walkthrough. The owner has not ruled on them. Check each,
push back where the reviewer has it wrong, and record the outcome.

### B1. Every threshold in this document is an owner intuition, not a measurement

The 75% floor (A2), 150% ceiling and 25% target (A3), 25% tie band (A4), $0.10
(A5) — plus the pre-existing G3 cost table, G4 temperature, and R-term noise
bands — are all numbers set by judgement with no supporting data.

That is unavoidable and not a criticism. But `objective.md` currently labels only
G2's band as an assumption. The pattern should be named **once, explicitly**, in
"Stated non-coverage and assumptions": these are owner-set parameters, not
derived quantities, and every gate resting on one inherits that conditionality.

### B2. Does v0 clear G6 as currently worded?

If reviewers already run OpenAI-calling code to check reproducibility under the
*current* criteria, and G6 as written forbids any reviewer spend, then **v0 — a
faithful transcription of the current rubric — may fail G6.**

The text is ambiguous about whether v0 is subject to the gates at all or is
treated as an exempt baseline. Both readings are findings:

- If v0 is exempt, the baseline is permitted something candidates are not, and
  that asymmetry should be stated.
- If v0 is not exempt, a gate has been silently failing its own reference point.

A5 likely resolves this in practice. State which reading is correct regardless.

### B3. R2 carries the real ranking work, and nothing checks red-team quality

The documents' own admissions, assembled:

- `objective.md`: with twelve records the R1 band is wide, **"R1 ties will be
  common, and R2 carries more of the ranking work than its position suggests."**
- `plan.md` M2: **"G2 may prove near-vacuous, G4 may ceiling out, and G5/G6 are
  compliance checks, leaving G1 plus the catalogue as the project's validity."**

So the project's discriminating power concentrates in **G1 + the twin catalogue
+ R2**. R2 and the stopping criterion both depend entirely on the red-team agent
being genuinely adversarial, round after round.

Reviewer agreement gets a cross-family check (G4/HF) precisely because same-model
agreement is weak evidence. **Red-team quality gets no equivalent check.** The
red-teamer, proposer, and adoption critic all run as Claude Code.

Question to answer: what stops the red-team round from being weak, repetitive, or
subtly aligned with the proposer's blind spots? "Every attempt is logged" shows
*what* was tried, not that trying harder would have found nothing.

### B4. Catalogue circularity — sharper than the version already recorded

`plan.md` records the general risk ("twins written against the same schema the
scorer reads risk tautology"). The specific version is stronger:

The eight catalogue types are **named categories**. A candidate could be written
to detect exactly those eight named failure modes, pass G1 completely, and
demonstrate nothing about general discrimination. The stated mitigations —
cross-criterion conditional twins, an unrestricted red-team — do not directly
address a candidate that mirrors the catalogue's own taxonomy.

Worth an explicit position in `decisions.md`, and worth constraining what the
final writeup may claim from a G1 pass.

### B5. Extraction validation covers 2 repos out of 12–13

Both are `owner_reviewed` — i.e. the two the owner already knows well, and
therefore the two where an extraction error is most likely to be caught anyway.
Nothing directly validates extraction on the other ten or eleven.

This is not flagged as a limitation the way the no-holdout gap is. Two
suggestions:

- Pull the **second** `owner_reviewed` repo's extraction check into **M1**
  rather than M2, if `repos.yaml` makes that feasible. The owner's stated goal
  for M1 is catching catastrophic failure cheaply; one repo is a thin basis.
- Consider a lighter spot-check across a broader sample before M2 seals.

### B6. No defined mechanism for a v0 error found *after* M2 sealing

M2 already carries the independent v0 fidelity diff (`v0-independent-diff`), and
the reasoning for it is sound — v0 anchors two gates, so one transcription error
biases both undetectably.

But nothing states what happens if an error surfaces **after** sealing, once
comparisons have already run against it. Does v0 get corrected and every prior
comparison invalidated? Is there a re-baseline procedure? Currently undefined.

### B7. `p13 (feasibility only)` is never defined

It appears in `plan.md` M2 and in `02-milestone-1.md` (pinned commit blocks M2).
It is not one of the two roles CLAUDE.md documents for `repos.yaml`
(`corpus`, `self`). What is it, what is it used for, and does it count toward the
A2 rate floor? If it does not, say so in `objective.md`.

### B8. G3 bounds the total, not any single criterion

A candidate that makes nine criteria trivially cheap and one criterion far more
expensive can pass G3 on the total. CLAUDE.md's concern — *"criteria that cost
more time per project will be applied carelessly"* — arguably applies per
criterion, not only in aggregate. Consider a per-criterion cap; if that is
already covered elsewhere, say where.

### B9. `unlocatable-project` sits close to the excluded taste example

Seven of the eight degraded catalogue types describe something structurally
wrong with the *system*. `unlocatable-project` — same content, artifacts
unreachable from the README — describes something wrong with the *navigation*.

CLAUDE.md's own example of what is **not** admissible is *"this README is badly
written."* Reachability is plausibly checkable in a way that "badly written" is
not, so this may be entirely justified — but the twin type sits close enough to
the excluded example that it should be justified explicitly rather than assumed.

### B10. G4 measures same-model self-agreement — do not let the term widen

G4 is three samples from **one** Gemini model at nonzero temperature. That is
not human-to-human reviewer agreement, and it is not cross-family agreement
(which is one measurement, once, at M4, on a subset).

Nothing currently overclaims this. Flagged because the word "agreement" invites
the stronger reading, and the final writeup is the place it would quietly widen.

### B11. "Passes all six gates" overstates the evidence

Following B3: if G2 is near-vacuous, G4 ceilings out, and G5/G6 are compliance
checks, then "the final candidate passed all six gates" is a much weaker claim
than it sounds. The honest version is closer to *two compliance checks, one gate
that may not bind, one that may not discriminate, and one real test.*

`plan.md` already says this internally. It needs to appear in
**`docs/proposed-guidance.md`** and the writeup, not only in the internal plan —
otherwise the deliverable presents evidence it does not have.

### B12. Was headless Claude Code considered for the primary reviewer role?

The plan never rules it in or out. It would **not** substitute for the
second-family role — cross-family agreement structurally requires a different
model family, which is the whole point of the HF spend. But for the *primary*
Gemini reviewer role it might, which would remove the HF fragility question from
everything except the single M4 measurement.

The reviewer does not know whether headless Claude Code supports the required
pattern (cached, budgeted, checkpointed, deterministic batch calls) and is not
guessing. Answer it explicitly, either way.

### B13. Quota figures are still placeholders

`plan.md` assumes **≤250 requests/day** Flash-class as an explicit placeholder,
with real limits to be read from AI Studio on day one of implementation
(`02-milestone-1.md` preconditions). Every sizing figure in the cost section
inherits that. Confirm the real numbers before any sizing is treated as settled.

### B14. Read-vs-execute reviewability — a candidate content note, not a gate change

Raised by the owner during the walkthrough. **This does not belong in
`objective.md`** — it is not about how candidates are judged, it is about what a
good candidate should contain:

> A project should ideally be reviewable **both** by reading the code and
> documentation **and** by executing it. Where execution is not realistically
> possible for a reviewer, the documentation must compensate — screenshots,
> recorded outputs, worked examples.

Record it where candidate content guidance lives, so it reaches the proposer
without contaminating the objective.

### B15. Minor — G1's scope grows over the project

G1 applies to "every sealed twin pair". The case set grows when the red-teamer
finds new types and the owner approves them. This is intended, and consistent
with the design; noted only so nobody reads G1 as a fixed one-time check.

---

## What could sink this, distinct from what is merely wrong

- **A1 is a process failure, not just an error.** A document reached owner
  approval asserting that no pass threshold exists, when one does and the owner
  had access to it. The concern is not the missing number — it is that the
  approval process did not surface it. Worth understanding before the next
  approval gate, since M2 sealing freezes considerably more.
- **B3 is the structural risk.** If G2 proves near-vacuous, G4 ceilings out, and
  R1 mostly ties, then the project's entire validity claim rests on G1, the twin
  catalogue, and R2 — and R2's strength is a function of how hard one agent
  tried to attack its own side's work, with no external check. If that is where
  the project lands, the writeup must say so plainly.
- **B4 sits underneath B3.** If a candidate can pass G1 by mirroring the
  catalogue's taxonomy, then G1 measures catalogue coverage rather than
  discrimination — and the two remaining pillars reduce to one.