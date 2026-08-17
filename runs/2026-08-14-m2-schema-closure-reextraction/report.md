# M2 step 3 — re-extraction under schema v1 / extractor v2

All 13 records (p01–p13) re-extracted fresh from their pinned clones under
the schema-closure changes recorded in `docs/decisions.md`
(`runs/2026-08-13-m2-schema-closure/proposal.md`). Each ran in its own
clean subagent holding only `agents/extractor/v2/prompt.md`,
`cases/schema.md`, and that record's pinned clone.

## A recurring structural defect, found and fixed

Three of the thirteen re-extractions (p08, p10, p12) — by three independent
subagents, across two different extractor versions (v1 and v2) — wrote
group H's technique blocks (`hybrid_search`, `reranking`,
`query_rewriting`) as flat bare values instead of each sub-field being its
own nested `{value, evidence, basis}` mapping. This crashes the scorer
(`MappingError: ... not a leaf field`) on every affected record.

This is not one mistake; it is the same mistake made independently three
times, which means the schema's own documentation of the shape was not
clear enough — the generic top-of-file example shows only one level of
nesting, and group H needs two. Fixed by adding a fully worked YAML example
directly to `cases/schema.md`'s group H section (see that file). p08, p10,
and p12 were each re-extracted a second time with an explicit warning
pointing at this exact mistake, and all three are now confirmed correctly
nested (checked programmatically, not just by inspection).

## Verification performed

- **YAML validity**: all 13 records parse.
- **Structural check**: every group-H sub-field on every record is a
  `{value, evidence, basis}` mapping — checked programmatically across all
  13, not just the three that were fixed.
- **Scorer regression**: `candidates/v0/score.py` runs cleanly over all 13
  records plus the 6 existing M1 twins, no crashes.
- **Test suite**: 50/50 passing.
- **Isolation** (`extraction-in-clean-context`), method and result stated
  in full, not just a count:
  1. Every `.output` transcript file for this step (33 total — 13 initial
     launches, partial resumes after two session-limit interruptions, and
     2 targeted re-fixes for the group-H defect below) was grepped for the
     CLAUDE.md system-prompt-injection marker
     (`"Codebase and user instructions are shown below"`) and for every
     `"file_path":"..."` tool-use entry matching `docs/plan.md`,
     `docs/decisions.md`, `docs/deferred-to-m2.md`, or `CLAUDE.md` at the
     lab project's root.
  2. A first, looser pass (matching any path *ending* in `decisions.md`,
     not anchored to the lab project's root) flagged two transcripts —
     the two attempts at re-extracting p13 (one that hit the session
     limit, one that completed) — against `clones/p13/docs/decisions.md`.
     Checked directly: this is a file *inside the p13 repository clone
     itself* (p13's own internal decision log, ~3,600 lines, mentioned in
     its own extraction report), legitimate reading material for
     extracting p13, not the lab project's `docs/decisions.md`. The loose
     pattern matched on the filename alone; a false positive, not a
     violation.
  3. The corrected pass, anchored to the lab project's absolute root path,
     found **zero** matches across all 33 transcripts for any of the four
     forbidden files, and zero matches for the injection marker.
  4. A separate check listed every unique `file_path` read across all 33
     transcripts, outside `clones/` and outside the `cases/records/*`
     outputs being written. Result: exactly two files —
     `agents/extractor/v2/prompt.md` and `cases/schema.md` — nothing else.

## What changed in the records themselves

Every value was re-derived from scratch, not diffed against the prior
extraction — per the extractor's normal procedure. Notable by-products,
sourced in each record's own `extraction_notes`:

- p12: `reranking.measured_effect` hit a genuine schema gap — two
  strategies report byte-identical metrics (an exact tie), and the
  `improves/mixed/hurts/not_measured` enum has no clean value for that.
  Recorded as `mixed`, flagged for a future schema round.
- p04, p08, p09, p11, p12: new `document_code_conflicts` /
  `document_number_conflicts` / `run_instructions_gap_count` findings
  surfaced independently of anything M2 was checking for — raw evidence,
  not yet in `findings.md`.
- p10: confirmed fixed and now certifies under v0's scorer as `NO`
  (10/26) on real grounds (`llm_evaluation`, `containerization` unmatched)
  — not a crash.

## Artifacts

- `cases/records/p01.yaml` … `p13.yaml`, all `schema_version: 1`,
  `extracted_by: agents/extractor/v2`.
- `cases/schema.md` — group H gains a worked nesting example (see above).
- This file.
