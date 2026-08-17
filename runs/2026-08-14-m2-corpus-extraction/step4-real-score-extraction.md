# M2 step 4 — real-score corpus extraction (p14–p23)

Extracted the 10 repos in `courses/llm-zoomcamp-2026/real-score-candidates.yaml`
under the sealed-for-extraction schema (`schema_version: 1`,
`agents/extractor/v2`), joining `role: corpus` and growing the base from 12
to 22 (`repos.yaml` updated; real scores stay in the gitignored staging
file only, never joined into any committed file).

## A real isolation violation, caught and fixed

The first p18 extraction self-reported reading `cases/records/p01.yaml`
and `cases/records/p02.yaml` to check a citation-formatting convention
before writing its own record. This is a categorical violation of
`extraction-in-clean-context`, regardless of whether it changed any fact
in the output. p18 was re-extracted in a fresh subagent with an explicit
instruction not to consult other records for formatting questions and to
note genuine ambiguity in `extraction_notes` instead. The re-extraction is
confirmed clean.

## Isolation check — method, result, and a gap that was closed

Same method as steps 1 and 3: grep every available subagent transcript for
the CLAUDE.md system-injection marker and for reads of `docs/plan.md`,
`docs/decisions.md`, `docs/deferred-to-m2.md`, `CLAUDE.md`,
`repos.yaml`, and `real-score-candidates.yaml`; separately list every
`cases/records/*.yaml` read to catch cross-record contamination.

**Original gap (owner review caught this before it was accepted as a
limitation):** transcripts for p14–p17's original extraction had aged out
of the harness's temp directory and could not be independently
re-verified — only the original prompt constraint and each agent's
self-report existed as evidence. The project's own logic (re-extraction is
free before sealing, costly after) applied directly: p14–p17 were
re-extracted a second time, sequentially, specifically to produce
transcripts that could be checked. All 5 resulting transcripts
(p14, two attempts at p15, p16, p17) were grepped by the same method as
every other record in this step.

**Result — clean, with one real violation caught and fixed:**

- p14, p16, p17: zero forbidden-file reads, zero injection markers.
- **p15's first re-attempt genuinely violated "never execute the
  repository"**: it ran `uv run python3 -c ...` to count CSV rows, which
  silently triggers `uv sync` and installs the target repo's dependencies
  as a side effect. Confirmed directly in the transcript (the exact `uv
  run` command is visible in the tool-call log), not just from the
  agent's own disclosure. `clones/p15`'s `git status` was checked
  afterward and is clean (no stray `.venv` or modified files), but the
  categorical rule was still broken, so this attempt's record was
  discarded.
- p15 was extracted a third time with an explicit ban on invoking the
  target repository's interpreter or package manager (stdlib-only /
  shell-only inspection). This attempt's transcript is clean by both
  checks. `cases/records/p15.yaml` reflects this third attempt.

**All 7 transcripts from the original p18–p23 batch (including the p18
re-extraction) remain clean, as previously reported.** Every
`cases/records/*.yaml` read across all transcripts in this step traces to
an agent reading its own target file's existing header (required by the
Write tool before an overwrite), never a different record.

**What is still not independently verifiable:** the three failed first
attempts at p18–p20 (session-limit interrupts) — but these wrote no
records, so nothing from them entered the sealed set regardless.

## Validation

- All 22 records (`p01`–`p23`) parse as valid YAML, `schema_version: 1`,
  `extracted_by: agents/extractor/v2`.
- Group-H nesting: clean across all 22 (checked programmatically).
- `candidates/v0/score.py` runs cleanly over all 22 plus the 6 M1 twins, no
  crashes. Full test suite: 50/50 passing.

## Six-field table, extended to 22

| case_id | retrieval_eval_config_matches_shipped | llm_eval_config_matches_shipped | llm_eval_metric_at_ceiling | retrieval_eval_relevance_rule | llm_eval_judge_spotchecked | llm_eval_question_generator |
|---|---|---|---|---|---|---|
| p01 | differs | differs | true | source_level | false | none_committed |
| p02 | differs | differs | true | document_level | false | generator_ties_question_to_passage |
| p03 | differs | differs | true | human_labelled | false | none_committed |
| p04 | differs | matches | true | document_level | false | none_committed |
| p05 | undeterminable | undeterminable | null | none | false | none_committed |
| p06 | differs | matches | null | document_level | false | none_committed |
| p07 | matches | matches | true | document_level | false | generator_ties_question_to_passage |
| p08 | differs | matches | true | document_level | false | generator_ties_question_to_passage |
| p09 | matches | matches | true | passage_level | false | none_committed |
| p10 | matches | differs | null | document_level | false | generator_ties_question_to_passage |
| p11 | differs | differs | true | passage_level | false | generator_ties_question_to_passage |
| p12 | matches | differs | false | passage_level | false | none_committed |
| p13 | matches | matches | true | passage_level | true | generator_ties_question_to_passage |
| p14 | differs | matches | false | passage_level | false | other |
| p15 | matches | differs | true | document_level | false | generator_ties_question_to_passage |
| p16 | differs | differs | false | document_level | false | generator_ties_question_to_passage |
| p17 | differs | differs | null | passage_level | false | generator_ties_question_to_passage |

(Table above reflects the verified re-extraction of p14–p17, not the
original unverified pass — see "Isolation check" above. p14's
`llm_eval_question_generator` moved to `other`: its LLM-eval set mixes a
committed passage-tied generator with a hand-typed supplement that has no
generator at all, which no single enum value captures cleanly — flagged
in the record's own `extraction_notes`, not a value the schema currently
resolves. p15's `retrieval_eval_relevance_rule` moved `source_level` →
`document_level` between its own two attempts — ordinary inter-extraction
judgment variance on the same repository, same category of disagreement
as p03's, not caused by the execution violation.)
| p18 | matches | matches | true | document_level | false | generator_ties_question_to_passage |
| p19 | matches | matches | null | document_level | false | none_committed |
| p20 | matches | matches | null | passage_level | false | generator_ties_question_to_passage |
| p21 | matches | matches | null | document_level | false | generator_ties_question_to_passage |
| p22 | differs | undeterminable | null | document_level | false | none_committed |
| p23 | undeterminable | undeterminable | null | none | false | none_committed |

**Correction (this note originally misattributed which records changed and
why — checked properly against the actual step-1 table and each record's
own `extraction_notes`, not asserted):**

- **p02**: `llm_eval_metric_at_ceiling` `false → true`. Genuinely explained
  by item 1's 95%-of-items rule — p02's own `extraction_notes` says so
  directly: faithfulness at 96.9%/98.0% now clears the newly-defined
  threshold, where the old undefined rule read the same numbers as
  "below ceiling" prose.
- **p05**: `llm_eval_metric_at_ceiling` `false → null`. Also genuinely
  item 1: no aggregate metric exists at all for p05, and the new rule
  explicitly says that case is `null`, not a forced `false`.
- **p03**: `retrieval_eval_relevance_rule` `passage_level → human_labelled`.
  **Not explained by item 1** — item 1 only touches
  `llm_eval_metric_at_ceiling`, nothing else. This is genuine disagreement
  between two independent extraction passes over an ambiguous schema
  boundary: p03's ground-truth questions were hand-paired to a target
  `chunk_id`, and the scoring function then exact-matches on that id. The
  step-1 extractor read the *matching mechanism* (exact chunk id) as
  `passage_level`; the step-3 extractor read the *provenance of the label*
  (a human assigned it) as `human_labelled`. `cases/schema.md` does not
  currently say whether these two readings are mutually exclusive or how
  to break the tie. **This is exactly the kind of disagreement
  `extraction-agreement-needs-notes` and step 6's spot-check exist to
  catch** — flagging it here as a live finding, not resolving it
  unilaterally. Whether this needs a clarifying schema rule is an open
  question for the owner, not something decided in this file.
- **p01, p06**: checked directly — **no change** on either field between
  the step-1 and step-4 tables. The original note wrongly listed both.

## 3k signal, for step 5 (not a decision — policy already adopted)

- **`config-drift`**: now has *many* real bases holding `matches` on both
  config fields at once — p07, p09, p13, p18, p19, p20, p21.
- **`unfailable-eval`**: clean `false` (not null) on p12, p14, p16.
- **`circular-eval`**'s `llm_eval_judge_spotchecked: true` sub-case: still
  only p13 across all 22. The committed-generator sub-case is now common
  (11 of 22 records).

## Artifacts

- `cases/records/p14.yaml` … `p23.yaml`.
- `courses/llm-zoomcamp-2026/repos.yaml` — 22 `role: corpus` entries plus
  p13 (`role: self`).
- This file.
