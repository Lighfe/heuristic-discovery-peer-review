# Second prompt — milestone 1, smallest end-to-end slice

Save as `tasks/02-milestone-1.md`. Run in a fresh session with the repo
checked out. Once run, this file is not edited — amendments append as dated
sections. (Revised in place 2026-08-10 under `tasks/reviews/review-01.md`,
*before* any run — the immutability rule was not in force yet.)

---

You are implementing milestone 1 of this project. You have not seen the
planning session. Read, in this order: `CLAUDE.md` (the epistemics section
binds every choice), `docs/plan.md`, `docs/objective.md`,
`docs/decisions.md`. Do not proceed if `docs/objective.md` still carries its
NEEDS OWNER APPROVAL marker — ask the owner to resolve it first.

## Goal

Prove the pipeline end to end at minimum size: both `owner_reviewed` repos
extracted, a handful of twins, one candidate, one loop pass — and produce
the baseline finding: which known defect twins the *current* course
criteria fail.

## Preconditions (ask the owner for any that are missing)

- `GEMINI_API_KEY` and `HF_TOKEN` in the environment (HF is NOT used in this
  milestone; verify presence only)
- p13's commit pinned in `courses/llm-zoomcamp-2026/repos.yaml` (not used in
  this milestone; it blocks M2, flag it now)
- the actual Gemini free-tier limits for this account, read from AI Studio —
  record them in the runner config with the date
- the owner's field-level reading of p01 **and p02** (decision
  `extraction-validation-scope`: one repo is too thin a basis for a
  milestone meant to catch catastrophic failure cheaply). The protocol is
  strict: the owner re-checks record fields as *facts in the repo* (this
  artifact exists at this path, these numbers appear in this file), never
  as review verdicts. The owner's original peer-review text stays out of
  the session entirely — this is the epistemics line between validating
  extraction and importing taste.

## Build order — stop at each phase boundary and report before continuing

1. **`loop/` runner skeleton.** Python 3.12, `uv`, pinned versions. A Gemini
   client with: input-hash cache keyed by (model, prompt-hash, case-id,
   **protocol-version**) — a re-run of anything already seen costs zero
   requests, and a protocol change can never silently reuse old results.
   Any prompt-affecting randomisation (the evidence-field shuffle) must be
   seeded deterministically by (case-id, sample-index, protocol-version),
   or every re-run generates fresh prompt hashes and the cache guarantee
   silently fails. Request budget declared per pass and checked *before*
   the pass starts, checkpoint after every call with clean resume, exponential
   backoff with jitter on 429, fixed model with a fallback list that **fails
   loudly** rather than switching mid-run, and a per-day request ledger in
   `runs/`. No unbounded parallelism anywhere.
2. **Extractor agent prompt** in `agents/extractor/` (versioned — it is an
   experimental variable, not a task). It reads a pinned repo clone and
   emits an evidence record. Clone p01 at its pinned commit (gitignored,
   never executed), run extraction in this Claude Code session, and draft
   `cases/schema.md` v0 from what p01 actually contains — fields must be
   procedural, answerable by a reviewer without domain knowledge (the
   constraints section of `project-evaluation-issues.md` defines this).
3. **STOP — schema gate.** Present schema v0 to the owner. No case is built
   before approval. (This is one of the five ask-gates; the others are in
   `tasks/01-planning.md`.)
4. **Extract p02** at its pinned commit with the same extractor prompt, and
   validate both records against the owner's field-level readings
   (precondition above). p02 is noted domain-opaque to a general reviewer,
   so it also stresses the schema's claim that fields are procedural —
   answerable without domain knowledge. Schema changes forced by p02 go
   back through the step-3 gate.
5. **Twins.** Plain-Python twin generator producing 5–6 twins of p01's
   record: three catalogue types from `docs/plan.md` (include
   harmful-component-kept and claim-without-artifact) plus one no-change
   twin. Each twin file states its field diff and its direction, known by
   construction. Enforce the disjoint-field-sets rule from `docs/plan.md`:
   degraded mutations flip a categorical fact a criterion can tier on;
   the no-change twin touches only fields outside any plausible criterion
   read-set — this is what makes gate G1 satisfiable, and M1 is its first
   test. Store in `cases/twins/`. From here on, `cases/` is read-only to
   every loop agent.
6. **Candidate v0.** Transcribe the *current* course criteria
   (`courses/llm-zoomcamp-2026/project-evaluation-guidance.md`) into the
   executable layer plus field mapping, changing nothing. Fidelity to the
   current rubric is the point — v0 is the baseline instrument, not a
   proposal. Keep the mapping mechanical and traceable criterion by
   criterion: at M2 a *fresh session* diffs it against the guidance text
   with no access to your rationale (decision `v0-independent-diff`), so
   do not rely on prose explanations to carry the mapping.
7. **One loop pass.** (a) Scorer harness runs candidate v0 over both
   records and all twins — free, deterministic; (b) Gemini agreement probe: ≤60
   requests, 3 independent samples per case (stateless, one case each,
   seeded shuffle, temperature above zero, per `decisions.md`
   agreement-protocol-ceiling). This probe is a **pipeline smoke test, not
   the baseline** — the baseline agreement is measured at M2 over the full
   corpus, and M1's number is labelled non-baseline in the run manifest;
   (c) one mini red-team round in this session: 5 budgeted attempts to make
   a schema-valid, structurally-bad record score well under v0, every
   attempt logged including failures.

## Done means

- `runs/` holds a manifest naming: model, prompt hashes, request count vs
  budget, cache hits, and every artifact the pass produced
- extraction validation: p01's and p02's records compared against careful
  human readings (both are `owner_reviewed` — validation is of the
  extraction step only; no review verdict enters anything)
- `docs/findings.md` opens with baseline entries naming the run: which
  twins candidate v0 (the current criteria) failed and which it passed —
  this twin baseline is evidence the project argues from. The agreement
  number is recorded as a smoke-test result only, explicitly non-baseline
- counts recomputed from artifacts, not carried from prose
- nothing committed that names a person; check `git status` against the
  gitignore before any commit, and never `git add -A`

## Hard limits

- Read-only for agents: `cases/` (after step 5), `docs/objective.md`, the
  constraint list in `CLAUDE.md`
- Budget: this milestone spends at most 60 Gemini requests and 0 HF credits
- Stop and ask the owner about: the schema (step 3), anything that would
  relax a CLAUDE.md epistemics rule, anything that would need the owner's
  past review verdicts. Everything else: decide, and record it in
  `docs/decisions.md` within its five-line budget.
