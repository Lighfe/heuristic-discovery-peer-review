# Review M1 — results

What `tasks/reviews/review-m1.md` asked for, and what was done. Each item
below states the action taken and the file it landed in, so a reader can
check the claim without re-deriving it. Produced 2026-08-13.

---

## Part A — owner change requests, actioned

**A1 (F5 arithmetic).** Went further than the requested fix. Rather than
just downgrading F5, pulled the six cached per-sample responses for p01 and
`p01-t01` and found the root cause: `loop/agreement.py` was reading each
sample's total from the field the model self-reported, never checking it
against the sum of that same response's own listed per-criterion points.
16 of the 24 M1 smoke samples (67%) had a self-reported total that
disagreed with its own per-criterion sum, by 1–3 points. Fixed
`loop/agreement.py` to recompute the total mechanically, and reran the
smoke test against the existing cache (0 new requests) —
`runs/2026-08-13-m1-agreement-smoke-recomputed/agreement.json`. `findings.md`
F5 is rewritten with the corrected numbers: p01 and p02 turn out to be
exactly self-consistent (spread 0) once the arithmetic bug is removed; the
constructed twins retain real spread. The retrieval-evaluation-clause
finding is kept, but rescoped to n=3 (only `p01-t01`'s samples test
anything; p01's three samples correctly don't name a shipped approach,
since its own value is `mixed_result`), quoted from the three real
`p01-t01` reasons, and the untested missing-tier alternative is named. The
words "reviewers" and "as humans apply them" are replaced with language
scoped to what was actually measured, per `g4-is-self-consistency`.
Decision: `agreement-total-recomputed`.

**A2 / A3 (F3's dependency, F2's wrong reason).** `findings.md` F2 no
longer says the best-performing approach is shipped — it names the actual
value (`mixed_result`) and the interpretive reading that earns the two
points. F3 gets a new subsection stating that `p01-t01`'s pass depends on
that same reading, with the strict-reading recomputation (p01 21→20,
`p01-t01` stays 20, tie, G1 fails; `p02`'s score moves too) and a note that
the M2 independent v0 fidelity diff is not neutral with respect to this
finding. Decision: `retrieval-best-approach-reading-flagged`.

**A4 (attack/mechanism count).** `findings.md` F3 and F4 both note that
the two G1 twin failures and four of the five successful attacks (a1, a2,
a3, a5) share one mechanism — mutating a field no criterion reads — with a
table listing every mutated field's read-by-any-criterion status,
independently re-derived from `criteria.yaml`'s `reads:` lists (all rows
confirmed). F4 states the ranking-write-up rule: "5 successful attacks, 1
distinct mechanism." Decision: `attack-mechanism-count-distinct`.

**A5 (F4 lead evidence).** Verified both halves before writing anything.
p01's `llm_evaluation` score is 1 of 2, not "full marks" as the review
itself claimed — capped by `llm_eval_approaches_compared: 1`, unrelated to
`llm_eval_role_overlap: same_family`. p02's score **is** the full 2 of 2,
confirmed against `runs/2026-08-12-m1-scorer-v0/manifest.json`, despite
`same_model` + `generator_ties_question_to_passage` +
`judge_spotchecked: false` together. `findings.md` F4 now leads with p02's
real-record evidence (no approach-count caveat needed there), corrects the
p01 claim, and keeps a4 as corroboration.

**A6 (undefined `not_below` relation).** `objective.md` G1 now defines
`not_below` (≥) for documented-mitigation twins, matching what `plan.md`'s
catalogue already required in prose for the harmful-component-kept removal
variant and the circular-eval spot-checked variant. States explicitly that
only three relations are defined and a manifest recording any other name is
a bug. Decision: `g1-not-below-defined`.

**A7 (real-score dataset scoping).** Not added to `plan.md` — the review's
own sourcing questions (commit hashes? score provenance? overlap with the
owner's past reviews?) are unanswered and only the owner can answer them.
Recorded the scoping recommendation itself as a decision:
`real-score-dataset-scoped` — check 1 (does v0's code match real reviewer
practice) is in scope and feeds the M2 fidelity diff; check 2 (does the
current checklist measure quality) is excluded, matching the reasoning
`decisions.md` already applies to keep the owner's own reviews out of the
loop.

## Part B — reviewer observations, checked and recorded

**B1 (a4 not prose-fidelity material).** Confirmed directly against
`runs/2026-08-12-m1-redteam/attack-a4.yaml`: every mutated field carries
`basis: constructed for the M1 red-team round` and
`evidence: [<synthetic-attack>]`. Recorded as `a4-not-prose-fidelity-material`
— a4 stays valid for R2, excluded from the agreement probe and any future
fidelity measurement.

**B2 (identical input token counts).** Resolved, not left open. Checked
`loop/render.py` directly: `basis` is rendered for every field (source,
not inference). Rendered p01, `p01-t05` and `p01-t06` offline and extracted
the actual mutated line from each, rather than trusting an aggregate
character count (an aggregate match cannot by itself distinguish "the field
isn't rendered" from "the field is rendered and happens to be the same
length"): `p01-t06`'s rendered line reads `- repo_file_count: 41` against
p01's `- repo_file_count: 53` — genuinely different content, same rendered
*length* because both are two-digit numbers, which is why the two full
prompts tokenize to the same count. `p01-t05`'s rendered record is 10
characters longer than p01's ("Flask app, served by gunicorn" → "FastAPI
app, served by uvicorn"). Neither twin is vacuous at the render layer; the
identical `input_tokens` is a tokenizer coincidence on near-identical text.
Recorded as `render-includes-basis-confirmed`.

**B3 (checklist mislabeling).** Traced to the actual bug:
`twin_mutated_fields()` in `tools/make_validation_checklist.py` indexed
mutations by field name only, with no `base_case_id` scoping, so every
record holding a field of that name inherited the annotation regardless of
which twin actually mutated it. Fixed the generator (now keys by
`base_case_id`, confirmed by rerunning it — it correctly refuses to
overwrite the already-answered `checklist.md`, so the owner's 136 answers
are untouched; only future checklists benefit). Recorded as
`checklist-generator-scoped-by-base-case`.

## Files changed

- `docs/findings.md` — F2, F3, F4, F5 all revised as above.
- `docs/objective.md` — G1 gains the `not_below` relation definition.
- `docs/decisions.md` — 8 new entries across the Cases-and-twins,
  Objective-and-measurement, Schema and Corpus-and-inputs sections.
- `loop/agreement.py` — recomputes totals instead of trusting the model's
  self-reported sum.
- `tools/make_validation_checklist.py` — scopes "mutated by" annotations to
  the twin's actual base case.
- `runs/2026-08-13-m1-agreement-smoke-recomputed/` — new run, 0 requests,
  corrected agreement numbers.

## What could sink this, distinct from what is merely wrong

The agreement-arithmetic bug (A1) was not something `review-m1.md` asked
to be found — it surfaced while trying to satisfy A1's request for the
missing per-sample evidence. It changes F5's numbers substantially (spread
0 instead of 1–3 on the two real records) but not its qualitative
conclusion: the reviewer model still applies the retrieval-evaluation
criterion as a pure count on the one sample that tests it. If a future
session re-runs the M2 baseline agreement pass without checking whether
`gemini-3.5-flash-lite` still mis-sums its own points at a similar rate,
and the recomputation habit in `loop/agreement.py` is ever bypassed (a
different script computing agreement independently, say), this exact bug
can reappear silently — the fix lives in one function, not in a schema or
gate that would catch a second occurrence elsewhere.

The rest of M1's standing risk is unchanged from what `review-m1.md`
already stated: G1's positive evidence is one twin pair, and it now carries
an explicit, cited dependency on a reading `criteria.yaml` names as the
first thing to attack. Nothing in this session's work makes that dependency
go away — it makes it visible and traceable to the M2 fidelity diff that
will settle it.
