# Third prompt — milestone 2, full corpus and case set

Save as `tasks/03-milestone-2.md`. Run in a fresh session with the repo
checked out. Once run, this file is not edited — amendments append as dated
sections.

Step 7 (the independent v0 fidelity diff) must run in a **separate** fresh
session holding only the reading list stated in step 7 itself — **not** the
top reading list below. That list includes `docs/decisions.md`, which
contains `v0-literal-no-inferences` — the exact v0 build rationale step 7
exists to check independently of. A step-7 session that first reads the top
list has already seen what it is meant to catch blind.

Step 1's eleven extractions (p03–p12, p13) each run in their own clean
subagent holding only the extractor prompt (`agents/extractor`),
`cases/schema.md`, and the pinned repo clone — never a session that has read
`plan.md`, which states the full twin catalogue (`extraction-in-clean-context`).
This is not a hypothetical risk: it is exactly how p01's first extraction was
contaminated and had to be redone — see the provenance warning in
`runs/2026-08-10-extraction-priming/p01.primed.yaml`.

Steps 2–6 and 8–10 may run in one continuous session, or several, following
the reading list below. Step 1's per-record subagents and step 7's session
may not be part of that session and do not read that list.

---

You are implementing milestone 2 of this project. This reading list is for
the session(s) running steps 2–6 and 8–10 — **not** for step 1's extraction
subagents or step 7's session, which have their own, narrower reading lists
stated in those steps and must not read this one. Read, in this order:
`CLAUDE.md` (the epistemics section binds every choice), `docs/plan.md`
(the M2 milestone entry), `docs/objective.md`, `docs/decisions.md`,
`docs/deferred-to-m2.md`, `cases/schema.md`, `tasks/reviews/review-m1.md`
and `tasks/reviews/review-M1-results.md` (context for why several items
below exist), `courses/llm-zoomcamp-2026/real-score-candidates.yaml`. Do
not proceed if any precondition below is unmet.

## Goal

Grow the case set to its sealed, full-corpus form; close every schema
question M1 deferred; and freeze every measurement parameter M3 needs
before any candidate is compared. **M2 produces no candidate and no
finding about the criteria** — it produces the instrument the M3 loop runs
on. If step 7 or step 9(c) surfaces something about the criteria
themselves rather than about v0's transcription, that is a `findings.md`
entry and should say so explicitly; the boundary is transcription-fidelity
versus criteria-defect, not a hard wall.

## Preconditions (ask the owner for any that are missing)

- p13's commit pinned in `courses/llm-zoomcamp-2026/repos.yaml` (currently
  `"TODO"` — this blocks the milestone; decision `corpus-twelve` flagged it
  would)
- `GEMINI_API_KEY` present (`HF_TOKEN` is not a precondition here — HF is
  **not** used this milestone, decision `hf-final-only` — do not stall M2 on
  it)
- `courses/llm-zoomcamp-2026/real-score-candidates.yaml` complete: 10 rows,
  `commit` and `already_in_corpus` filled for each — verify at run time, not
  from this file's 2026-08-13 date
- the Gemini free-tier limits re-verified from AI Studio if more than a few
  days have passed since the M1 reading (`loop/config.toml` carries the date
  they were last read; refuse to spend a request if stale per
  `quota-runtime-discovered`)

## Build order — stop at each phase boundary and report before continuing

1. **Extract p03–p12 and p13**, under the schema as frozen at M1, **one
   clean subagent per record** (see the isolation note at the top of this
   file) — holding only `agents/extractor`, `cases/schema.md`, and that
   record's pinned clone, nothing else. p13 is
   `role: self`, feasibility only — no distribution statistic, no G2 rate
   (decision `corpus-twelve`). Produce, per corpus record, the six field
   values `deferred-to-m2.md` 3k names
   (`retrieval_eval_config_matches_shipped`,
   `llm_eval_config_matches_shipped`, `llm_eval_metric_at_ceiling`,
   `retrieval_eval_relevance_rule`, `llm_eval_judge_spotchecked`,
   `llm_eval_question_generator`), one table. This table, plus every record
   produced, is the evidence step 2 works from — do not decide the schema
   questions below from p01/p02 alone a second time.

   **Artifact:** `cases/records/p03.yaml` … `p12.yaml`, `p13.yaml`; the
   six-field table.

2. **STOP — schema closure.** Every item below gets an explicit owner
   decision — a schema change, or an explicit "no change" — recorded in
   `decisions.md`. None may be defaulted or silently dropped. 21 items,
   labelled exactly as in `docs/deferred-to-m2.md` so cross-referencing is
   direct.

   `plan.md`'s M2(c) names three examples of what this closes: a controlled
   vocabulary for group-K fields (**item 6**, below), a notebook
   cell-locator convention, and a counting rule for
   `untraceable_number_count`. Checked against `deferred-to-m2.md` while
   drafting this task: the cell-locator convention is **not** one of the 21
   — it was already settled when p02 hit it (`cases/schema.md`'s "Locators
   inside notebooks" section, `path:cellN`) and never entered the deferred
   list, so item 2 here is to confirm that with an explicit `decisions.md`
   entry, not to re-litigate it. The counting rule for
   `untraceable_number_count` is not its own item either — it currently
   rides inside **item 3i** (counts-vs-enums), which decides *whether* to
   keep it a count, not what counts as one instance. Confirm with the owner
   whether 3i's sign-off is meant to cover the counting rule too, or whether
   it needs its own line.

   - **1.** `llm_eval_metric_at_ceiling` has no threshold
   - **2.** Knowledge-provenance mechanism — needs to become a schema and
     extractor-prompt rule, not a habit
   - **3.** Reproducibility as a per-evaluation property (fewer fields than
     the four first sketched)
     - **3a.** p02's monitoring prose↔executable divergence — resolve
       together with 3, or confirm the recorded v0 mapping rule already
       covers it
     - **3b.** `run_instructions` vs `run_instructions_gap_count` contradict
       each other — resolve together with 3
   - **3c.** The scoreable/descriptive split is leaky at `basis`
   - **3d.** `claim-without-artifact` has almost no headroom on p01 — needs
     a different base record
   - **3e.** The schema is not normalised (`retrieval_best_approach_shipped`
     is a derived field stored as data)
   - **3f.** `llm_eval_role_overlap` is undefined when no generator exists
   - **3g.** `decision_documented`'s name does not say it requires
     justification from measurements
   - **3h.** A second `document_code_conflicts` candidate on p02, not
     counted
   - **3i.** Counts-vs-enums tension, and the sizing of step 6's spot-check
     (decide both here)
   - **3j.** `basis` leaks repo paths into reviewer prompts
   - **3k.** Which catalogue types need a constructed base — decide using
     step 1's table, extended by this step's own new records
   - **4.** Group J (documentation accuracy, 8 fields) — restructure now or
     not
   - **5.** Fields motivated by exactly one repository — cut or keep, now
     testable against the newly-extracted records
   - **6.** Group-K string fields have no controlled vocabulary
   - **7.** `interface_kind` cannot express more than one interface — owner
     called this minor at M1; re-confirm or fix now
   - **8.** Extraction-agreement must compare notes, not only values —
     already decided (`extraction-agreement-needs-notes`); confirm the
     spot-check in step 6 implements it, not a fresh decision
   - **9.** Proposed post-M1 decisions-review mechanism (the `Binds:` line)
     — adopt or not
   - **10.** Course-materials anchor (`06-best-practices`,
     `07-project-example`) — decide whether this needs its own
     `decisions.md` entry now or waits for M3 candidate work

   **Artifact:** one `decisions.md` entry (or an explicit "no change, and
   why") per item above — 21 entries.

3. **Re-extraction, only if step 2 changed the schema.** Whatever changed,
   re-extract every affected record — free before sealing, which is the
   entire reason for the freeze. Bump `schema_version`.

   **Artifact:** records updated at the new `schema_version`, or nothing if
   step 2 changed nothing.

4. **STOP — schema sealed.** Only now: extract the ten real-score repos
   from `real-score-candidates.yaml`, under the now-sealed schema. Join
   `role: corpus` (12 → 22). **No separate sign-off** — this step is a
   sequencing checkpoint gated entirely by step 2's sign-off, not a fresh
   approval; the inclusion decision was already made when
   `real-score-dataset-scoped` entered `plan.md` M2(e). Do not start before
   step 2 is signed off; do not wait for step 3's re-extraction of the
   original 12 to literally finish first — only the schema needs to have
   stopped moving.

   Also extend step 1's six-field table with these ten records' values for
   the same six fields — no fresh extraction, just reading them off the
   records step 4 just produced — so step 5 has a full 22-repo table to work
   from instead of step 1's 11-repo one.

   **Artifact:** 10 new `cases/records/*.yaml`; `repos.yaml` updated to 22
   `role: corpus` entries plus p13; the six-field table extended to all 22.

5. **Full twin catalogue.** Every type in `plan.md`'s catalogue, not just
   M1's three plus one no-change: `harmful-component-kept`,
   `claim-without-artifact`, `config-drift`, `unfailable-eval`,
   `circular-eval`, `sample-too-small`, `unlocatable-project`,
   `checkbox-padding`, all three no-change kinds (cosmetic rename, tech
   swap, dataset-domain swap), and the cross-criterion conditional twins
   decision `twin-catalogue-conditional` requires. Use the six-field table
   as extended at step 4 over the full 22-repo corpus to assign each type a
   real base or flag it as needing a constructed one (`deferred-to-m2.md`
   3k). A constructed base is synthetic — excluded from R1 spread and the G2 rate,
   same treatment as `synthetic-thin-records` — and needs owner approval
   before it enters `cases/twins/`, the same gate as any new case-set entry
   (`redteam-cases-via-owner`).

   **Artifact:** `cases/twins/` populated for every catalogue type
   buildable on a real base; a named list of types needing a constructed
   base, with owner approval recorded for each one actually added.

6. **Extraction spot-check** across the non-owner-reviewed corpus — now 20
   records (p03–p12 plus the ten real-score repos). Compares extraction
   **notes**, not only field values (`extraction-agreement-needs-notes`):
   two records can agree on every field and disagree about whether the repo
   has a fatal defect. Sample size is decided in step 2 (item 3i) — sized
   to what the owner can afford, using the derived leverage rule (fields a
   twin mutates, fields a candidate reads), never exhaustive.

   **Artifact:** a spot-check report naming which fields and which records
   were checked, by whom, and which were not; a note-level agreement
   statement, not only a value-level one.

7. **Independent v0 fidelity diff.** Fresh session (see the top of this
   file) reading **only**: `courses/llm-zoomcamp-2026/project-evaluation-guidance.md`,
   `candidates/v0/criteria.yaml`, and `cases/schema.md`'s field list — no
   `decisions.md`, no `CLAUDE.md` decision history, no `plan.md`, no
   `tasks/reviews/review-m1.md`. `candidates/v0/criteria.yaml` was built for
   exactly this check: every criterion carries `guidance_verbatim` to diff
   against the guidance text at its cited lines, and each tier's `when` to
   diff against its `text`; `unmappable` and `interpretation` keys are where
   a transcription error would hide. Diffing guidance criterion → mapping →
   field list line by line (`v0-independent-diff`). v0 anchors G3/R3 and
   every baseline finding, so a transcription error would bias them
   undetectably, and the author confirming its own reading is self-grading.
   Current isolation (`extraction-in-clean-context`) is
   **instruction-based only** — auditable from the transcript, not
   enforced — and this diff is more load-bearing than M1's extraction was.
   Whether that needs strengthening to something enforced (a separate
   checkout, a restricted environment) rather than merely audited is an
   **open question for the owner**, not a default either way.

   **Artifact:** a line-by-line diff report. Any transcription error found
   is fixed directly if found before sealing (step 8), or per
   `v0-post-seal-correction` if found after.

8. **STOP — case set review and sealing (owner gate).** "Sealed" means:
   `cases/records/` and `cases/twins/` are frozen and read-only to every
   agent from this point on; `schema_version` and the case set are stamped
   together; the only way anything is added afterward is a new
   owner-approved red-team type entering per `redteam-cases-via-owner`,
   which grows the sealed set without reopening it.

   **Artifact:** an owner sign-off recorded in `decisions.md` naming the
   case set (record count, twin count, `schema_version`) as sealed.

9. **Measurements on the sealed case set** (not before — see the ordering
   note below):

   a. **Baseline agreement**, including the G4 ceiling check, over the full
      sealed set — using the corrected `loop/agreement.py` (recomputes
      totals from per-criterion points; see `agreement-total-recomputed`).
      This is the real baseline; the M1 number was an explicitly-labelled
      smoke test only.
   b. **v0's real certification rate r₀** over the 22-repo corpus at the
      11-point threshold (`pass-threshold-11`) — free, scorer harness,
      deterministic. Replaces the "0 of 12 fail" working hypothesis with a
      measured number and feeds G2's erosion budget (`g2-rate-floor`: the
      gate permits erosion of exactly r₀ − 75%).
   c. **Real-score check 1 only:** does v0's computed total match what real
      reviewers did, applying the same written criteria, on the ten
      real-score repos — feeding step 7's fidelity diff with real
      behaviour, not only code-reading. Also settle the
      `mixed_result`-vs-`yes`-only reading dispute
      (`retrieval-best-approach-reading-flagged`) using whichever of the
      ten hold `retrieval_best_approach_shipped: mixed_result`. **Check
      2 — whether the current checklist measures quality well — is out of
      scope for this milestone and for any M3 candidate**
      (`real-score-dataset-scoped`); do not reintroduce it because a
      per-criterion breakdown happens to be available for these ten.

   Ordering note: these three run *after* step 8, not before. A number
   computed against an unsealed case set is not a baseline — it can be
   invalidated by whatever the sealing review changes, and step 10 below
   needs 9(a)'s result to be final.

   **Artifact:** `agreement.json` and a manifest over the full corpus; a
   recorded r₀; a real-score check-1 report naming which of the ten repos
   bore on the `mixed_result` reading question, and whether v0's computed
   total matched the real one for that repo — a match/mismatch verdict per
   repo ID, **never the real score value itself printed beside a repo ID**,
   and never a full per-repo score table (`real-score-dataset-scoped`).

10. **STOP — M2 sealing decisions.** Named checklist, every row owner
    sign-off, none assumed:

    - G3 cost table and per-criterion cap
    - G4 temperature
    - **G4's form** — one of the four options in `objective.md`; the
      owner's stated tendency is (4), demotion to a reported metric, but
      this is **confirmed against step 9(a)'s measured baseline, not
      assumed**
    - R-term noise bands (R1's bootstrapped over whichever corpus step 4
      produced — 22 records, never carried forward from twelve; G4/R2 band
      on measured re-run variation)
    - M3 round cap (currently 8, uncalibrated — resizable here with a
      stated reason)

    **Artifact:** one `decisions.md` entry per row, each naming the frozen
    value and the reasoning; `objective.md`'s "freezes at M2 sealing"
    language updated to state the frozen values themselves.

## Done means

- every artifact named above exists and is what it claims to be, none
  carried from prose
- `decisions.md` holds one entry per schema-closure item (step 2), the
  case-set-sealed entry (step 8), and per sealing decision (step 10)
- `findings.md` gains no new entries about the criteria this milestone
  unless step 7 or step 9(c) surfaces one, in which case it is recorded
  and named as such — M2 seals the instrument, M3 uses it
- counts recomputed from artifacts, not carried forward (12 becomes 22
  once step 4 runs; the R1 band is bootstrapped fresh at step 10, not
  reused from M1's twelve-record figure)
- nothing committed that names a person; check `git status` against the
  gitignore before any commit, and never `git add -A`
- `courses/llm-zoomcamp-2026/real-score-candidates.yaml` stays gitignored;
  nothing derived from it that would re-identify a repo/score pair leaks
  into a committed file beyond what `real-score-dataset-scoped` already
  permits (aggregate check-1 findings, never a per-repo score table)

## Hard limits

- Read-only to every agent throughout: `cases/` (once step 8 seals it),
  `docs/objective.md`, the constraint list in `CLAUDE.md` — and, from step
  2's sign-off onward, the schema itself
- Budget: size step 9(a)'s agreement pass before starting it and report the
  cost against `loop/config.toml`'s daily quota before spending; HF stays
  at 0 credits this milestone
- Stop and ask the owner about: every item in step 2's checklist, step 5's
  constructed-base twins, step 6's sample size, step 7's isolation
  mechanism, step 8's sealing, step 9's reordering of baseline
  agreement/pass-rate measurement to run after sealing rather than before
  (plan.md's M2 listing puts them earlier; step 9's ordering note states the
  reason but the reorder itself is unconfirmed), every row of step 10.
  Nothing on this list is decided by the agent running this task.
