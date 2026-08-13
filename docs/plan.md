# Plan

*Live document — rewritten in place, describes only the current plan. Length
budget: ~250 lines (raised 2026-08-10 to absorb review-01; do not drift
further).*

Produced by `tasks/01-planning.md` (2026-08-09), revised by
`tasks/reviews/review-01.md` (2026-08-10). Decisions behind every choice
here live in `decisions.md`; what "better" means lives in `objective.md`
(approved 2026-08-10, which unblocks M1).

## Shape of the loop

This is a **judge-and-critique loop with an executable inner check**, not a
pure optimisation loop. The workshop reference
(`llm-heuristic-scientists-workshop`) works because it has four properties:

1. a cheap deterministic non-LLM objective (a simulator computes lateness),
2. a fixed executable candidate signature (`priority(step, state)`),
3. free evaluation,
4. a held-out scenario.

This project recovers **1–3 only by construction**: the candidate carries an
executable scoring layer over extracted evidence records, so twin tests and
the adoption check run in plain Python at zero request cost. Property **4 is
not available and will not be faked**: every repo is read during development,
`repos.yaml` records that no sealed holdout exists, and the end-of-project
consistency check is reported as a sanity check, never as evidence. Because
the objective cannot be a clean number on unseen data, optimisation pressure
alone is unsafe; the loop therefore alternates *propose → measure → red-team
→ critique*, and the stopping claim rests on logged failed attacks rather
than a converged score.

## What a candidate is

Two layers with an explicit mapping:

- **Prose layer** — a complete replacement `project-evaluation-guidance.md`:
  criteria plus the reviewer guidance around them. This is what ships.
  Content requirement (owner, review-01 B14, for the proposer — not a
  gate): a project should be reviewable **both** by reading the code and
  documentation **and** by executing it; where execution is not realistic
  for a reviewer, the documentation must compensate — screenshots, recorded
  outputs, worked examples.
- **Executable layer** — a deterministic scoring function over evidence
  records. The mapping declares, per prose criterion, which record fields it
  reads and the tier function that turns them into points.

The executable layer is an abstraction and hides real things: the reading
experience of a repo, the cost of *finding* evidence, semantic quality, and
every ambiguity the extractor resolved that a live reviewer would face. Twin
tests validate evidence→score, never repo→evidence. Three measurements keep
the abstraction honest:

- **Extraction validation** — records for the two `owner_reviewed` repos are
  compared against what a careful human reader found (extraction only; the
  owner's verdicts never enter the loop), plus double-extraction agreement
  on a sample.
- **Prose↔executable fidelity** — Gemini reviewer agents apply the *prose*
  criteria to records; systematic disagreement with the executable layer is
  a defect in the candidate (ambiguous prose), not in the reviewers.
- **Reviewer-time estimate** — each criterion carries an estimated minutes
  cost for a human to check it; the total is a gate (see `objective.md`).

## Roles

| agent | runs on | reads | writes |
|---|---|---|---|
| extractor | Claude Code, one-off per repo, cached | pinned repo clone, `cases/schema.md` | `cases/records/` |
| twin generator | plain Python | `cases/records/`, twin catalogue | `cases/twins/` (sealed after review) |
| candidate proposer/reviser | Claude Code | current candidate, findings, attack reports | candidate versions only |
| scorer harness | plain Python, free | candidate executable layer, all cases | run results in `runs/` |
| reviewer agents | Gemini Flash-class | prose criteria + one record each | scores, via the runner |
| second-family reviewer | HF Inference Providers | same as reviewer agents | scores, via the runner |
| red-teamer | Claude Code | candidate (both layers), schema, catalogue *types* | attack reports in `runs/` |
| adoption critic | Claude Code | candidate, adoption-check results, R3 cost flags | critique notes in `runs/` |

Hard rules (from CLAUDE.md epistemics, restated as mechanism):

- `cases/`, `objective.md`, and the constraint list are **read-only to every
  loop agent**. New twin types proposed by the red-teamer enter the case set
  only after owner approval.
- Reviewer independence: each reviewer call is stateless, sees one case, no
  other reviewer's output, evidence fields in an order shuffled
  **deterministically**, seeded by (case-id, sample-index, protocol-version)
  — an unseeded shuffle would change every prompt hash and silently defeat
  the cache. Cache key is (model, prompt-hash, case-id, protocol-version) so
  a re-run costs zero requests and a protocol change can never silently
  reuse results measured under the old protocol.
- The owner's past review verdicts never enter any prompt or comparison.
- The primary reviewer stays Gemini, not headless Claude Code (decision
  `primary-reviewer-not-claude-code`): the G4 protocol needs a fixed
  temperature, which the Claude Code CLI/SDK does not expose; subscription
  quota is opaque, session-windowed, and shared with the high-judgment
  interactive work; and Claude reviewing Claude-proposed candidates would
  put proposer and reviewer in one model family — the exact correlation
  the cross-family measurement exists to break.

## The case set

Records are extracted once per repo. Twins are **record-level mutations
generated by plain Python**: each twin states its structural difference as a
diff over record fields and its known direction, known because it was
constructed. The taste guard is mechanical: a proposed twin that cannot be
expressed as a record-field diff is rejected.

Catalogue (initial; each entry gets both a degraded and, where meaningful, a
documented-mitigation variant):

- harmful-component-kept — component whose own committed numbers show it
  hurts, shipped enabled (direction: down; the documented-removal variant
  must score ≥ it)
- claim-without-artifact — headline number with no committed artifact (down)
- config-drift — measured config differs from shipped config (down)
- unfailable-eval — correctness criterion almost nothing can fail (down)
- circular-eval — generated questions judged by the same machinery, no
  spot-check (down; with a documented judge spot-check: not down)
- sample-too-small — many config decisions settled on a tiny set with no
  uncertainty statement (down)
- unlocatable-project — same content, artifacts unreachable from the README
  (down)
- checkbox-padding — e.g. charts bound to no data source (down)
- **no-change twins** — cosmetic renames, tech swaps (Streamlit↔Flask),
  dataset-domain swaps (direction: **zero**; criteria that move on these are
  noise-sensitive and fail)

Gate G1 demands sensitivity to every degraded twin and total stability on
every no-change twin, which on a coarse tier scale could be unsatisfiable if
both pulled on the same dial. The catalogue therefore enforces **disjoint
field sets**: every degraded mutation must be categorical — it flips a fact
any reasonable criterion tiers on — and every no-change mutation touches
only fields outside the plausible read-set of any criterion. M1 tests this
construction; if G1 proves unsatisfiable anyway, that escalates to the owner
as an epistemics amendment (see `objective.md`).

Known limit, recorded rather than hidden: twins written against the same
schema the scorer reads risk tautology. The sharp version (review-01 B4):
the catalogue types are named categories, so a candidate written to detect
exactly those categories passes G1 completely while demonstrating nothing
general. Cross-criterion conditional twins and the unrestricted red-team
round mitigate but do not close this; the closure is honest labelling — a
G1 pass is claimed as catalogue coverage only (see `objective.md` G1), and
generality claims rest on R2.

## Cost model and budget

The scarce resource is requests per day. Google publishes no free-tier
RPM/TPM/RPD table; limits are per-account and visible only in the
login-gated AI Studio dashboard. **Read there by the owner 2026-08-10** and
stored in `loop/config.toml` with that date:

- `gemini-3.5-flash-lite` — **500 RPD**, ~15 RPM. The primary reviewer.
- `gemini-3.1-flash-lite` — the declared fallback, operator-selected for a
  *new* run only; a run never switches models mid-pass.
- `gemini-2.5-flash` and `gemini-3.5-flash` — **20 RPD**, unusable at any
  volume. The full Flash models are out; the sizing below is Flash-Lite's.
- **Input TPM is ~250k across all of them**, so tokens, not requests, are
  the plausible binding constraint once records are full-size. The client
  meters a rolling 60-second input-token window alongside the request rate.
- HF free tier is **$0.10/month** in credits (the docs mark it subject to
  change) — roughly 50–150 small-model calls a month. Cross-family agreement is therefore measured **once, on the
  final candidate, on a case subset**, and nowhere else.
- Every model call is cached by input hash; re-runs cost zero requests.
- The runner computes a pass's request cost *before* starting, refuses to
  start a pass that exceeds the remaining day budget, checkpoints after
  every call, and resumes. Exponential backoff with jitter on 429. A model
  fallback list exists but a run **fails loudly** rather than switching
  models mid-run.

Sizing of the recurring measurements (at 500 RPD): baseline agreement pass =
12 corpus records × 3 reviewers = 36 requests, once, cached. Candidate
fidelity probe = case subset (~20) × 3 reviewers = 60 requests per candidate
that reaches it. Twin tests and adoption checks are free (executable layer).
A day that exceeds budget ends cleanly at the checkpoint and resumes
tomorrow; nothing is re-spent.

## Milestones

- **M1 — smallest end-to-end slice.** Extract p01 (owner_reviewed, so
  extraction is validatable) → derive schema v0 → **stop: owner approves
  schema** → extract p02 (the second owner_reviewed repo) and validate both
  extractions against the owner's field-level reading — one repo is too
  thin a basis for M1's stated goal of catching catastrophic failure
  cheaply (review-01 B5) → 5–6 twins of p01 (3 catalogue types + 1
  no-change) → candidate v0 = current rubric transcribed to executable form
  + mapping → one pass: scorer on cases, Gemini agreement probe (≤60
  requests), one mini red-team round. Proves the schema is extractable
  (p02 is noted domain-opaque, so it also stresses the procedural-fields
  claim), the pipeline/cache/budget accounting works, and yields the
  baseline finding: which known twins the *current* criteria fail. Spec:
  `tasks/02-milestone-1.md`.
- **M2 — full corpus and case set.** All 12 corpus records + p13
  (**feasibility only** — `role: self`, the owner's own capstone; it
  checks that extraction/schema/scoring run end-to-end on a repo the owner
  can fully verify, and enters no distribution statistic and no G2 rate),
  full twin catalogue, a light extraction spot-check (a few fields per
  record verified as facts in the repo) across the non-owner-reviewed
  corpus before sealing, baseline agreement measured (including the G4
  ceiling check), **v0's real pass rate at the 11-point threshold measured
  over the corpus** (free, scorer harness — replaces the 0-of-12-fail
  hypothesis with a number), case set reviewed and sealed (owner gate). M2
  sealing also freezes, with the owner: the G3 cost table and per-criterion
  cap, the G4 temperature, **G4's form — chosen only once the baseline
  number is in hand**, owner tendency being demotion to a reported metric
  (`objective.md` G4), the R-term noise bands
  (R1's bootstrapped over records — the scorer is deterministic, so re-run
  variance is zero), and the M3 round cap — every measurement parameter is
  fixed before any candidate is compared. Five M2 obligations follow from
  review: (a) an **independent v0 fidelity diff** — a fresh session, with
  no access to the transcription rationale, diffs guidance criterion →
  mapping → field list line by line, because v0 anchors G3/R3 and the
  baseline findings, and a transcription error would bias them
  undetectably; (b) the extraction spot-check **compares extraction notes,
  not only field values** — two records can agree on every field and
  disagree about whether a repository has a fatal defect, because the notes
  carry what the fields cannot express (decision
  `extraction-agreement-needs-notes`; measured at M1, see
  `runs/2026-08-10-extraction-priming/`); (c) the schema items left open at
  the M1 gate are closed *before* sealing, since a later change costs a full
  re-extraction: a controlled vocabulary for group-K string fields, a
  notebook cell-locator convention, and the counting rule for
  `untraceable_number_count`; the full queue is `docs/deferred-to-m2.md`,
  which the sealing checklist works through item by item — the schema is
  **frozen for M1** and every open question was written there rather than
  resolved, because a schema change is free before sealing and costs a full
  corpus re-extraction after it; (d) effort is weighted toward the **twin catalogue**, where
  the objective's real discriminating power concentrates — G2 may prove
  near-vacuous, G4 may ceiling out, and G5/G6 are compliance checks,
  leaving G1 plus the catalogue as the project's validity; (e) **ten real,
  scored repos** (`courses/llm-zoomcamp-2026/real-score-candidates.yaml`,
  sourced by the owner, commits pinned, checked against `repos.yaml` for
  overlap — decision `real-score-dataset-scoped`) are extracted and join
  `role: corpus`, growing the base to 22. Their scores are used for **check
  1 only** — feeding (a)'s independent fidelity diff with real reviewer
  behaviour instead of code-reading alone, and settling the `mixed_result`
  reading dispute that F3's one clean G1 pass rides on (decision
  `retrieval-best-approach-reading-flagged`) — never for grading the
  checklist itself, which the same review rejected as circular (**check
  2**, not run, not at M2 and not against any M3 candidate). One of the ten
  scores exactly 11, the pass threshold, partially closing the "no real
  near-threshold project" gap.
- **M3 — discovery rounds.** Propose → score → red-team → critique, until
  the stopping criterion in `objective.md` is met **or its round cap (8,
  resizable at M2) is reached** — the cap's outcome is defined in
  `objective.md`, never improvised. Findings land in `findings.md`, each
  naming its run. Rounds are **owner-paced by design**:
  red-team case-set additions and any epistemics question batch at round
  boundaries, so the loop deliberately stalls on the owner there — this is
  the "agents may not edit what judges them" rule made operational, and the
  cost in autonomy is accepted, not accidental.
- **M4 — adoption check and writeup.** Final candidate through the full
  gates incl. HF cross-family measurement (provider-failure fallback per
  `objective.md`); an **independent red-team audit** — a fresh session with
  no access to the proposer's rationale runs one full budgeted attack round
  against the final candidate (decision `redteam-fresh-session-audit`;
  same model family, so it breaks session correlation, not family
  correlation, and the writeup says so). **If the audit lands successful
  attacks**, M3 reopens for one more round if the round cap permits;
  if the cap is spent, the candidate still ships and each surviving attack
  is named in the writeup as a **known unpatched attack against the
  shipped criteria**, with its structural fact stated — never demoted to an
  appendix. Then `proposed-guidance.md` is written;
  the writeup reports **per-gate bindingness** — which gates bound, which
  were decorative or compliance checks — never a bare "passed all gates";
  weak consistency check run and labelled as such.

## Challenge-the-framing (recorded, per the task)

- The diagnosis in `project-evaluation-issues.md` holds up against the
  guidance text and the curriculum. One soft spot: "the zero tiers are
  unreachable" is asserted from a corpus containing no thin submission — the
  same coverage gap the adoption check has. It is plausible (a thin project
  plausibly never reaches peer review), but it is currently unmeasured.
- The twin method validates the **scoring layer**, not the whole instrument.
  Extraction reliability and prose↔executable fidelity are measured
  separately (above); the final writeup must claim no more than this chain
  supports, or the project fails its own evidentiary standard.
- The adoption check cannot yet be tested where it matters most — near the
  pass line. Partial mitigation: synthetic thin records constructed at the
  certification boundary. Full mitigation requires a real thin repo (asked
  of the owner); until then the writeup states the gap plainly.
