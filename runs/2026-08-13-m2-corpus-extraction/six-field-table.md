# M2 step 1 — six-field table, 13 records (p01–p13)

Produced by `tasks/03-milestone-2.md` step 1. p03–p12 and p13 extracted
2026-08-13, each by its own clean subagent holding only
`agents/extractor/v1/prompt.md`, `cases/schema.md`, and that record's pinned
clone (`extraction-in-clean-context`). p01/p02 values are read from their
existing M1 records, not re-extracted.

This is the evidence table `docs/deferred-to-m2.md` item 3k asks step 1 to
produce; step 2 works from it to close item 3k (and to inform items 3d, 4, 5,
6, 7). It does not itself decide buildability — that is a step-2 call.

| case_id | retrieval_eval_config_matches_shipped | llm_eval_config_matches_shipped | llm_eval_metric_at_ceiling | retrieval_eval_relevance_rule | llm_eval_judge_spotchecked | llm_eval_question_generator |
|---|---|---|---|---|---|---|
| p01 | differs | differs | true | source_level | false | none_committed |
| p02 | differs | differs | false | document_level | false | generator_ties_question_to_passage |
| p03 | differs | differs | true | passage_level | false | none_committed |
| p04 | differs | matches | true | document_level | false | none_committed |
| p05 | undeterminable | undeterminable | false | none | false | none_committed |
| p06 | differs | matches | null (undeterminable*) | document_level | false | none_committed |
| p07 | matches | matches | true | document_level | false | generator_ties_question_to_passage |
| p08 | differs | matches | true | document_level | false | generator_ties_question_to_passage |
| p09 | matches | matches | true | passage_level | false | none_committed |
| p10 | matches | differs | false | document_level | false | generator_ties_question_to_passage |
| p11 | differs | differs | true | passage_level | false | generator_ties_question_to_passage |
| p12 | differs | differs | false | passage_level | false | none_committed |
| p13 | matches | matches | true | passage_level | true | generator_ties_question_to_passage |

\* p06's judge emits a categorical label (RELEVANT / PARTLY_RELEVANT /
NOT_RELEVANT), not a numeric score, and no committed static aggregate exists
— the dashboard computes distribution live from the DB. The field's bool
type has no clean answer here; recorded `undeterminable` (rendered `null`
above) with the reason in `cases/records/p06.yaml` extraction_notes. This is
itself relevant to item 1 (no threshold for `llm_eval_metric_at_ceiling`).

## Raw values by catalogue-type relevance (for step 2 item 3k, not a decision)

- `retrieval_eval_config_matches_shipped = matches`: p07, p09, p10, p13
- `llm_eval_config_matches_shipped = matches`: p04, p06, p07, p08, p09, p13
- both `matches` on one record (single base for both config-drift sub-cases): p07, p09, p13
- `llm_eval_metric_at_ceiling = false`: p02, p05, p06 (undeterminable, not false), p10, p12
- `retrieval_eval_relevance_rule` finer than `source_level` (document_level/passage_level/human_labelled): all of p02–p04, p06–p13 except p05 (`none`)
- `llm_eval_judge_spotchecked = true`: p13 only
- `llm_eval_question_generator` a committed generator (`generator_ties_question_to_passage`): p02, p07, p08, p10, p11, p13

## Notable cross-record findings surfaced during extraction (not scored, not yet in findings.md)

Each is sourced in its own record's `extraction_notes` / `basis` fields —
listed here only as a pointer for step 2, not as a claim in itself.

- p04: two document-vs-document numeric conflicts and one doc-vs-code
  conflict (`document_number_conflicts: 3`, `document_code_conflicts: 1`).
- p05: notebook outputs contain a plaintext DB connection string and an
  apparent contributor name; not reproduced here, flagged for the owner.
- p07: headline numbers exist only inside screenshot PNGs, never as text.
- p08: Windows username string embedded in a notebook cell output; not
  reproduced.
- p09: retrieval-eval question generator ties questions to passages but the
  schema (group D) has no field to record that, unlike group E.
- p10: LLM-eval notebook is broken as committed (`KeyError` on first item,
  never completes) — no clean schema value for "attempted but incomplete."
- p11: two interfaces present (Streamlit + Flask); `interface_kind` forces
  one value (item 7, already known from p02).
- p12: README's retrieval-evaluation table disagrees with the committed
  `retrieval_report.json` on every figure and on the stated winner
  (`document_code_conflicts: 13`).
- p13: `llm_eval_metric_at_ceiling`'s wording ("sits at its maximum") is
  ambiguous for an inverted-direction rate metric that sits at its floor
  (over-refusal rate = 0.0) — relevant to item 1.

## Schema-fit problems repeated across ≥3 records (candidate signal for step 2)

- `llm_eval_question_generator` cannot express "ties pre-existing Q/A to a
  passage" vs. "generates the Q/A itself" (p03), or mixed provenance across
  two generators in one project (p13) — relevant to item 1's neighbours and
  to the group-E field definitions generally.
- `monitoring_instrumentation`'s `logged` vs. `traced_on_request_path` split
  does not cleanly fit synchronous per-request DB logging wired to a live
  dashboard — recurs in p05, p06, p09, p10, p12. Not one of the 21
  deferred items as written; flagged for the owner to decide whether it
  needs one.
- `problem_statement`'s judgment call recurs as noted risk in p03, p04, p09
  (all resolved without dispute, consistent with the field's known
  weakness, item unchanged).

## Isolation check (`extraction-in-clean-context`)

Verified directly against all 11 subagent transcripts, not assumed. Each
transcript's tool-use log was greped for every `file_path` read: across all
11, the only project files opened besides each repo's own clone were
exactly `agents/extractor/v1/prompt.md` and `cases/schema.md` — no
transcript shows a read of `plan.md`, `decisions.md`, `deferred-to-m2.md`,
or `CLAUDE.md`, and none shows the CLAUDE.md system-prompt-injection marker
(`"Codebase and user instructions are shown below"`) that this session's
own transcript carries. A false-positive hit for "harmful-component-kept"
in one transcript traced to `cases/schema.md`'s own explanatory prose
(group H, which names that term and cites `project-evaluation-issues.md`
by name as part of its permitted text), not to a forbidden file. This is
the same failure mode that corrupted p01's first extraction
(`runs/2026-08-10-extraction-priming/p01.primed.yaml`); here it did not
recur.

## Artifacts

- `cases/records/p03.yaml` … `p12.yaml`, `p13.yaml` — 11 new records,
  `schema_version: 0`, each YAML-validated.
- This file.
