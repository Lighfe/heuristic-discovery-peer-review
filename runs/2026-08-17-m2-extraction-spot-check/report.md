# M2 step 6 — extraction spot-check

Per decision `spot-check-medium`: 8 fields × 20 non-owner-reviewed records
(p03–p12, p14–p23) = 160 checks, plus a note-level assessment on every
record, not only a value-level one (`extraction-agreement-needs-notes`).

## Method and who checked

Each of the 20 records was checked by its own fresh, isolated subagent —
not by the session that has been reading extraction reports and decisions
throughout M2, since that session has priors a genuine independent check
should not have. Each subagent read exactly three things: `cases/schema.md`,
the one record it was checking, and that record's pinned repository clone —
nothing else in this project. This matches the isolation standard used for
extraction itself (`extraction-in-clean-context`), applied here to
verification instead of authorship.

The 8 fields checked on every record: `retrieval_eval_config_matches_shipped`,
`llm_eval_config_matches_shipped`, `llm_eval_metric_at_ceiling`,
`untraceable_number_count`, `retrieval_eval_relevance_rule`,
`llm_eval_judge_spotchecked`, `llm_eval_question_generator`,
`document_code_conflicts`.

## Result: 159/160 field checks agree outright, 1 is a judgment call

Zero flat disagreements. **One caveat, stated here rather than left for a
reader to find three sections down**: p08's `document_code_conflicts` came
back "2 vs. a defensible 3" — the checker found the same underlying facts
but would group them into one more item than the record does (see the
`document_code_conflicts` finding below for the exact locations). The
"160/160" figure is correct only after accepting the record's grouping
choice as within the field's normal judgment latitude, which is a real
but different claim from "every check matched exactly."

Every checked value's `evidence` locators were independently re-derived,
not merely trusted — several checkers recomputed a reported figure
directly from a CSV/JSON/notebook-output rather than reading the record's
`basis` prose and accepting it (e.g. p04's document-conflict count, p18's
ceiling percentages, p21's byte-for-byte notebook output match).

## Note-level findings (not field errors — this is the point of checking notes, not only values)

- **p05, p09, p14**: extraction_notes understated or missed the extent of
  a leaked local path/username inside the source repository (p05: flagged
  1 occurrence, 4 actually exist; p09's leak — a real repo name and
  username in a notebook cell output — wasn't flagged at all; p14 has a
  real first name appearing ~162 times across committed docs/scripts plus
  a leaked Windows path, entirely unflagged). **None of this reached the
  committed record** — see the anonymity check below, run explicitly on
  every record, not assumed.
- **p08**: `document_code_conflicts` may be undercounted by one (2 vs. a
  defensible 3, a granularity judgment call, not a wrong fact) — plus a
  real note-level miss: a tautological "best_k" retrieval metric that a
  README claim rests on without saying so.
- **p16**: one additional hybrid-search figure exists that doesn't quite
  reconcile with either reported number — a minor instance of the same
  "committed numbers don't reconcile" pattern the record's own notes
  already flag once, not flagged a second time.
- **p18**: a headline results table is HTML-commented-out in the
  documentation (invisible on GitHub's render, screenshot only) — not
  flagged, though it doesn't change any field's value under the schema.
- **p21**: the record's dataset is in English but the shipped UI's chat
  strings are in Arabic — not flagged; doesn't affect `corpus_language`
  under the schema (language is read off the dataset, not UI chrome) but
  is the kind of fact other records' notes do call out.
- Every other record's notes were independently read and found complete —
  no additional gap found by the checking subagent.

## Anonymity check — run on every record, not assumed

Every subagent was asked to check whether the source repository leaks a
real name, username, or local path, and — critically — to explicitly grep
that record's own `cases/records/*.yaml` for whatever it found, not just
report on the clone. Results:

- **10 of 20 source repos leak a real identity somewhere** — git commit
  metadata (author name/email, never read by the extractor, per
  `evidence-not-scored`), a `git clone` URL in a README, an explicit
  "Author" section with GitHub/LinkedIn handles (p21), or — the two
  more serious cases — content inside tracked, committed files
  themselves (p09's notebook cell output naming the real repo and a
  username; p14's committed docs naming a first name ~162 times plus a
  leaked Windows path).
- **0 of 20 records leaked any of it.** Every single grep against the
  committed `cases/records/*.yaml` file came back empty. This holds even
  for p09 and p14, where the leak sits inside tracked files the extractor
  read from.
- This is expected, not a violation, under the anonymity model the owner
  stated explicitly at M2 step 5: clones are gitignored and never
  published: an insider recognizing a project from `corpus_domain` is
  accepted; an outsider tracing a record back to a real repo is what the
  model actually protects against, and that held on every record checked.

## A process note on this step itself, not on the records

While briefing the p21 spot-check subagent, the session running this step
included the sentence "this repo scores exactly at the pass threshold in
an external staging dataset" — real-score-adjacent information with no
reason to be in that prompt, since the spot-check task never needed it.
The subagent could not resolve this to an actual number (it never read
`pass-threshold-11`'s value, and was not given the schema/decisions
context that states it), and nothing from it entered any committed file or
this report — but it was an unforced disclosure outside the designated
gitignored staging file, caught and named rather than left unremarked.

## Note-level agreement statement (per `extraction-agreement-needs-notes`)

Value-level agreement: 159/160 outright, 160/160 counting the p08
judgment call as acceptable (stated above, not restated here).

Note-level agreement, corrected — the first version of this report
undercounted this. Two tiers, not one, and the arithmetic now matches the
findings section above exactly:

- **13 of 20 records: nothing found.** p03, p04, p06, p07, p10, p11, p12,
  p13(not applicable — see "what was not checked"), p15, p17, p19, p20,
  p22, p23. (13 records: p03, p04, p06, p07, p10, p11, p12, p15, p17, p19,
  p20, p22, p23.)
- **4 of 20 records: a finding that matters** — p05 (understated leak
  extent), p08 (undercount + missed tautological-metric note), p09
  (unflagged leak inside a tracked file), p14 (unflagged leak inside
  tracked files, the most extensive found). These are the ones that would
  change what a future reader trusts about the record or the source
  repo's hygiene.
- **3 of 20 records: a minor observation, explicitly confirmed not to
  change any field's value** — p16 (an unreconciled third figure), p18
  (a commented-out table), p21 (dataset language vs. UI language). Listed
  separately because each is a real thing an independent reader noticed
  that the original notes didn't, but none of the three checkers who
  found them said it should have moved a score.

13 + 4 + 3 = 20. Do not carry forward "17 of 20 clean" — that number was
wrong and has been replaced here, not just corrected in prose elsewhere.

## What was checked and what was not

Checked: all 20 non-owner-reviewed corpus records (p03–p12, p14–p23), 8
fields each, plus full-text extraction_notes review, plus an anonymity
check, by 20 independent subagents. Not checked: the other ~45 fields per
record (160 checks is the sized sample per `spot-check-medium`, not an
exhaustive re-extraction); p01/p02 (`owner_reviewed`, validated separately
at M1); p13 (`role: self`, feasibility only).
