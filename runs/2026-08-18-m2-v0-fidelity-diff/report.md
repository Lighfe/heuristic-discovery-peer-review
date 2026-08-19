# M2 step 7 — independent v0 fidelity diff

Per `v0-independent-diff`: a fresh session, isolated from this project's
decision history, diffs `candidates/v0/criteria.yaml` against
`courses/llm-zoomcamp-2026/project-evaluation-guidance.md` line by line,
checking whether the executable transcription is faithful to the source.

## Isolation, technically enforced, verified afterward

Per owner decision (2026-08-18): a local scratch directory was built
containing byte-for-byte copies of exactly the three files step 7's own
text names as the reading list — `project-evaluation-guidance.md`,
`criteria.yaml`, `schema.md` — and nothing else. No `decisions.md`, no
`plan.md`, no `CLAUDE.md`, no `review-m1.md`, no other project file was
present anywhere in that directory tree. This does not amount to an
absolute technical wall (the checking agent runs on the same machine and
filesystem as everything else, so a determined agent could still navigate
elsewhere), but it removes the accidental-discovery risk entirely, and it
is the strongest isolation practical without new sandboxing
infrastructure — decided explicitly, not defaulted.

**Verified after the run, not assumed:** the full transcript was audited.
Zero file reads occurred outside the three permitted files. Zero commands
left the isolated directory (every `cd` stayed inside it). Zero CLAUDE.md
system-injection marker. The transcript does contain the strings
"decisions.md", "plan.md" a few times — traced to their source: they are
citations quoted *inside* `schema.md`'s own text (e.g. "the corresponding
`decisions.md` entries name each change"), which the agent read legally as
part of the one schema file it was given, not files it opened itself.

## Findings, ranked by severity

### 1. `reproducibility` — a tier-ordering bug, not a disclosed interpretation

The guidance's 1-point tier explicitly names a case: "instructions are
clear and complete, the code works, **but the data is missing**" → 1
point. `criteria.yaml`'s tiers are evaluated top-down, first match wins.
The 0-point `data_accessible: missing` tier has no `run_instructions`
condition and is checked before the 1-point tier — so **any record with
`data_accessible: missing` scores 0, unconditionally, including the exact
case the guidance names as worth 1 point.** This silently overrides an
explicit guidance carve-out. No `unmappable`/`interpretation` key on this
criterion covers this case; the criterion's one `unmappable` note is about
a different clause entirely ("it's easy to run the code, and it works").

### 2. `reproducibility` — a second, undisclosed gap in the same criterion

The guidance's 0-point tier has three disjuncts: no instructions, data
missing, **or** "it's unclear how to access it." Only the first two are
mapped to tiers. A record where data exists but access is unclear (a
plausible read of `data_accessible: manual_steps` or `other`) has no
matching tier and falls to `fallback: 1` — scored as if the guidance's
third disjunct doesn't exist, with no disclosure.

### 3. `best_practice_hybrid_search` — reads the wrong field, contradicted by the file's own reasoning elsewhere

`when: {hybrid_search.present: true}`. The guidance text is "Hybrid
search: combining both text and vector search **(at least evaluating
it)**" — the parenthetical makes evaluation the qualifying action, not
mere implementation. `cases/schema.md` group H has a field for exactly
this distinction: `evaluated` (effect measured and reported), separate
from `present` (implemented). The criterion reads `present`, not
`evaluated`. This would be a plausible reading on its own — except the verbatim
next criterion, `best_practice_reranking`, carries an `interpretation` note
stating the transcriber's own reasoning: reranking's guidance clause is "a
bare checkbox... unlike hybrid search, which **at least says 'at least
evaluating it'**." The file's own text shows the distinction was
recognized and correctly applied to reranking (`present`, matching its
unqualified guidance) but not to hybrid search, which should have read
`evaluated` by the same logic and instead also reads `present`. This
reads as a transcription slip, not an argued judgment call — no
`interpretation`/`unmappable` key discloses it.

### 4. `ingestion_pipeline` — cosmetic, but the file claims exactness it doesn't have

Guidance line 130 ends with a trailing space (confirmed via `cat -A`);
the transcribed `guidance_verbatim` drops it. The file's own stated
purpose for this field is character-for-character fidelity. Content is
unaffected; the claim of exactness is technically false in one place.

### 5. `interface` — a documentation gap, not confirmed as a bug

`{interface_kind: {in: [web_ui, api]}}` only means "any element of a
list matches" because of logic added to `score.py` (schema item 7,
M2) — a file outside the three the checker was given, so it could not
verify this behaves as intended. `criteria.yaml`'s own "CONDITION SYNTAX"
header documents `{in: [...]}` only as scalar membership; it does not
state that list-valued fields are handled differently. **Flagged as
unverifiable from the given files, not asserted as a defect** — the
session running this report has separately confirmed `score.py`'s
list-handling is correct (verified when `interface_kind` was widened to a
list at schema closure), so this is a documentation gap in
`criteria.yaml`'s syntax legend, not a live scoring bug. Worth a one-line
fix to the legend regardless.

## What held up clean

`problem_description`, `retrieval_flow`, `containerization`, `monitoring`,
`best_practice_query_rewriting`, `bonus_cloud_deployment`,
`bonus_discretionary` — no issues. The disclosed judgment calls in
`retrieval_evaluation` (the `mixed_result` reading — see below),
`ingestion_pipeline`'s `manual → fallback:1`, and `llm_evaluation`'s
`unmappable` claim were independently re-derived and confirmed as genuine,
argued ambiguities, not errors hiding behind a disclosure. All 14
`guidance_verbatim` blocks matched their cited lines exactly except the
one trailing-space case above, including faithfully reproducing the
source's own inconsistent indentation rather than silently normalizing it.

## The `mixed_result` question — not settled by this diff, and the report says so explicitly

`retrieval-best-approach-reading-flagged` asked whether this diff would
settle the contested reading (does `mixed_result` count toward
`retrieval_evaluation`'s 2-point tier). **It does not settle it.** The
checking agent found the `mixed_result`/`undeterminable` grouping
"defensible but not the only reading — the guidance is silent on both
cases" and "a genuine, disclosed judgment call rather than a hidden
mistake." That is a statement that the current reading is *defensible*,
not a statement that it is *correct* or *the only correct reading* — an
independent reader confirming a call is reasonable is not the same as the
dispute being resolved. Findings F2/F3's dependency on this reading stands
exactly as before this diff ran.

## Disposition — fixed, verified, corpus impact confirmed

Per `v0-independent-diff` / `v0-post-seal-correction`: found before
sealing (step 8 has not run), so fixed directly rather than deferred, with
owner sign-off obtained per-fix given #1 and #3 change real scores.

- **#1 and #2 (reproducibility tier order)**: fixed together, since the
  same reorder resolves both. Owner-approved. Rewritten as a disclosed
  `interpretation` (the guidance genuinely contradicts itself — an
  unqualified 0-point "data missing" clause vs. a named 1-point exception
  for the identical fact — resolved in favour of the specific carve-out,
  same precedence this file already gives `retrieval_evaluation`'s
  `mixed_result` reading). The now-structurally-unreachable
  `data_accessible: missing` tier is documented, not deleted, matching
  this file's existing precedent for `retrieval_evaluation`'s fallback.
- **#3 (hybrid_search present→evaluated)**: fixed. Owner-approved as a
  clean correction, no disclosed judgment call needed — the file's own
  `interpretation` on the sibling `best_practice_reranking` criterion
  already proves the distinction was understood and just not applied here.
- **#4 (trailing-space cosmetic mismatch)**: fixed directly, no scoring
  effect, no sign-off needed.
- **#5 (list-membership syntax undocumented)**: fixed directly — one line
  added to `criteria.yaml`'s own syntax legend. No scoring effect (the
  underlying `score.py` behavior was already correct, confirmed at schema
  closure); this only fixed the file's self-documentation.
- **Bug #2's third disjunct** ("unclear how to access data") stays
  **open, not fixed**: `data_accessible: manual_steps` is listed in
  `cases/schema.md` with no defining prose (checked directly — every
  other field in that section gets a paragraph explaining its values;
  this one doesn't), so there's no basis yet for deciding whether
  `manual_steps` (or `other`) means "unclear how to access." This needs a
  schema definition before it can be mapped, not a `criteria.yaml` change.
  Recorded as an open item, not silently dropped.

**Corpus impact, re-measured after all fixes, all 22 records + all 18
twins, scorer + full test suite clean:**

| record | before | after | change |
|---|---|---|---|
| p05 | 11 (certifies) | **10 (does NOT certify)** | −1, crosses the pass threshold |
| p07 | 16 | 15 | −1 |
| p08 | 14 | 15 | +1 |
| p17 | 19 | 18 | −1 |

**p05 crossing the certification threshold is the material finding here.**
This happened *before* step 9 measures v0's real certification rate r₀ —
which is the correct order per the task's own sequencing (fixes land
before sealing; r₀ is measured after sealing, on the corrected instrument,
not before). Had this fix landed after r₀ was measured, r₀ itself would
have needed recomputing.
