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

**Isolation is partial and the writeup must say so.** A Claude Code
subagent in this repository still receives `CLAUDE.md`, which states the
project's purpose. It did not receive the diagnosis, the catalogue, the
plan, or this conversation. "Clean" here means *unprimed by the failure-mode
list*, not *blind*.

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

### Two consequences

**1. Priming made the reader worse, not better.** The expected failure was
that a primed reader would over-report — seeing catalogue failure modes
everywhere. What happened was the opposite: the primed session pattern-matched
the repository against a known list and stopped there, while the unprimed one
followed the schema field by field and checked what the code actually
computes. Checking against a list of known answers is what prevented the
finding. Recorded in `decisions.md` as `extraction-in-clean-context`.

**2. Value-level agreement is the wrong instrument for extraction
validation, and `plan.md` currently relies on it.** A double-extraction
agreement check over field values would have reported 94.7% here and
concluded extraction is reliable — while one run had found a fatal defect
and the other had not. The difference lived entirely in `extraction_notes`,
which no agreement statistic reads. Any extraction-validation claim scoped
to field values must say what it excludes; before M2 sealing, the sampled
spot-check needs a component that compares notes, not only values.

## Schema defect found by this comparison

`corpus_language` and the other group-K `string` fields have no controlled
vocabulary, so two correct extractions can disagree textually. Harmless for
scoring — group K is `descriptive` and no criterion reads it — but it makes
double-extraction agreement understate itself, and no-change twins mutate
exactly these fields. Fix before M2 sealing: constrain to ISO 639-1, or
state that group-K string equality is not part of any agreement measurement.
