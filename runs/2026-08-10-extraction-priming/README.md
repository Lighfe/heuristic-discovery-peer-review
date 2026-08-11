# Extraction priming check — 2026-08-10

*Log entry. Append-only; nobody reads `runs/` linearly.*

## What this measured

p01's evidence record was first written by a Claude Code session that had
already read `project-evaluation-issues.md`, the twin catalogue in
`plan.md`, and the owner's live comments — i.e. a session that knew which
failure modes the project was hunting before it opened the repository. The
owner identified that as contaminated evidence at the M1 schema gate.

p01 was therefore re-extracted by a subagent holding **only**
`agents/extractor/v1/prompt.md`, `cases/schema.md` and the pinned clone,
explicitly barred from `docs/`, `tasks/`, `courses/` and any existing
record. p02 was extracted the same way and has no primed counterpart.

Artifacts: `p01.primed.yaml` (superseded, kept only as the comparison
baseline). The clean records are the canonical ones in `cases/records/`.

**Isolation is partial and the writeup must say so.** See *What this does
and does not license* below for what was and was not achieved, and how
compliance was audited.

## Result — field values

57 leaf values compared. **54 agree, 3 differ — 94.7% agreement.**

| field | primed | clean | what it is |
|---|---|---|---|
| `corpus_language` | `pt` | `portuguese` | not a disagreement — the schema types this `string` with no controlled vocabulary, so two correct extractions are not comparable |
| `document_number_conflicts` | 1 | 2 | clean found one more, flagged scope-dependent |
| `run_instructions_gap_count` | 2 | 3 | clean found a third gap: the cloud deploy procedure has no ingestion step at all |

## The result that matters, and it is not the 94.7%

**The clean extraction found a defect the primed one missed entirely, and it
did not show up as a differing field value.**

Ingestion writes `"source": "wikipedia"` (`src/ingestion/wikipedia.py:67`).
Twelve of the 27 test-set items expect `"wikipedia_pt"`. The scoring
function tests exact string equality (`notebooks/01_retrieval_evaluation.py:41-49`),
so those twelve can never register a hit, and two further items are
hard-coded to zero. The maximum achievable hit rate is therefore
**13/27 = 48.1%** — and `docs/evaluation.md:9` reports Hybrid Hit Rate@5 of
**52%**, with two other strategies at exactly 48%.

A reported figure exceeds the ceiling the committed code allows. This is the
strongest form of the claim-without-artifact pattern available: not merely a
number without a traceable artifact, but a number provably inconsistent with
the artifact it names. Both records already agreed the notebooks cannot
execute; only the clean one worked out what the code would produce if they
could.

### What this does and does not license

**It does not show that priming causes anything.** One repository, one pair
of runs, one difference found. Any causal reading is unsupported, and an
earlier version of this file asserted one — that priming makes a reader stop
early. Withdrawn. The rule in `decisions.md` is categorical (a corrupted
context is corrupted) and needs no claim about which reader performs better.

**The two runs differ in four ways at once**, so even the direction of the
difference is not attributable:

| | primed | clean |
|---|---|---|
| agent | the interactive session | a general-purpose subagent |
| system prompt | full, including `CLAUDE.md` | subagent scaffolding, no `CLAUDE.md` |
| conversation history | the entire session | none |
| knowledge of the diagnosis | yes | no |

"The primed reader missed it" and "the two runs were not the same
instrument" are both consistent with the evidence, and this comparison
cannot separate them.

**Isolation was instruction-based, not enforced.** The subagents held full
filesystem tool access and were told which paths not to read. Compliance was
audited afterwards from the transcripts: zero reads of repo-root `docs/`,
`tasks/`, `courses/` or `cases/`; the only matches were the clones' own
documentation, plus `tasks/02-milestone-1.md` occurring as a string inside
`schema.md`'s own header, and `p01.primed.yaml` occurring inside the
prohibition text itself. No `CLAUDE.md` content appears in either transcript.
Compliance held; it was not prevented. A future run wanting a stronger claim
needs filesystem-level isolation — a working tree containing only the prompt,
the schema and the clone.

Residual priming, for completeness: `schema.md` itself mentions twins and
red-teaming, so the clean runs knew the schema serves a testing purpose.
They did not have the failure-mode catalogue.

### The one consequence that does hold

**A value-level agreement statistic may not be reported as extraction
validity, and the reason is structural rather than statistical.**
`extraction_notes` exist precisely to carry what the fields cannot express,
and no value-level comparison reads them — so two records can agree on every
field while disagreeing about whether the repository has a fatal defect.
That follows from what the instrument measures, not from this sample of one.
`plan.md`'s sampled double-extraction spot-check needs a note-comparison
component before M2 sealing, or its claim must state what it excludes.

## Schema defect found by this comparison

`corpus_language` and the other group-K `string` fields have no controlled
vocabulary, so two correct extractions can disagree textually. Harmless for
scoring — group K is `descriptive` and no criterion reads it — but it makes
double-extraction agreement understate itself, and no-change twins mutate
exactly these fields. Fix before M2 sealing: constrain to ISO 639-1, or
state that group-K string equality is not part of any agreement measurement.
