# M2 step 10 — sealing decisions checklist (consolidated)

`tasks/03-milestone-2.md` step 10: STOP, named checklist, every row owner
sign-off, none assumed. Supersedes the first draft of this file — this
version folds in three rounds of correction and follow-up analysis.
Nothing below is marked decided unless you explicitly confirmed it in
conversation; several rows are genuinely still open.

**CLOSED 2026-08-20.** Full owner clearance given. All six rows below
are resolved (confirmed, deferred, or explicitly left open, per row) and
written into `docs/objective.md` and `docs/decisions.md`
(`g3-cost-table-frozen`, `g3-per-criterion-cap` update,
`g3-g4-r1-exclude-bonus-discretionary`, `g4-form-frozen`,
`g2-certify-loss-citation`, `r1-statistic-frozen`,
`r1-g2-tension-sensecheck`, `m3-round-cap-kept-at-8`,
`g4-r2-noise-band-deferred`). Two items remain genuinely open past this
closure, stated as such in both files: R1's noise band/tie rule (needs a
bootstrap run against the newly frozen entropy/IQR statistic, not yet
done) and G4/R2's noise-band form (deferred to M3). This file stays as
the working record; it is not rewritten to hide the back-and-forth that
produced the final numbers.

**Scope note, confirmed 2026-08-20**: `bonus_discretionary` is excluded
from G3/G4/R1 measurement and reporting going forward. This is a
measurement/reporting decision only — `candidates/v0/criteria.yaml` and
`candidates/v0/score.py` are untouched, and v0 still scores every project
including `bonus_discretionary` exactly as the guidance states. Nothing
in this checklist proposes editing v0 itself.

---

## 1. G3 cost table and per-criterion cap

**Final 13-row table (your numbers, `bonus_discretionary` dropped):**

| criterion | minutes |
|---|---|
| problem_description | 2 |
| retrieval_flow | 10 |
| retrieval_evaluation | 15 |
| llm_evaluation | 15 |
| interface | 5 |
| ingestion_pipeline | 5 |
| monitoring | 7 |
| containerization | 2 |
| reproducibility | 45 |
| best_practice_hybrid_search | 6 |
| best_practice_reranking | 6 |
| best_practice_query_rewriting | 6 |
| bonus_cloud_deployment | 5 |

**Total: 129 minutes. 150% ceiling: 193.5 minutes.**

**Per-criterion cap: proposed 60 minutes, anchored to reproducibility's
own cost (45 min) plus its measured 60.0% self-consistency — the worst
of any criterion, by a wide margin.** Reasoning: a cap set below
reproducibility's real cost would either force reviewers to shortcut the
one criterion most prone to being gotten wrong under time pressure, or
make it infeasible for any future candidate to keep. This is a proposal,
not confirmed by you as final.

- [x] Confirm the 13-row table as final, or correct further rows.
- [x] Confirm the 60-minute per-criterion cap, or set a different number.

---

## 2. G4 temperature

**Confirmed by you: 0.7, as already frozen in `loop/config.toml` and
already used for the real M2 baseline pass.** No further action.

- [x] Confirmed 0.7.

---

## 3. G4's form

**DECIDED: option (4), reported metric only, never a blocking gate.**
Reporting convention, per your correction — weighted scores only, no
exact-match percentages, no comfort-floor or noise-band discussion in
the record (informative-only metric, kept lean):

**Case-level (13 criteria, `bonus_discretionary` excluded): weighted
score 0.7726.**

**Per-criterion, all 13, weighted:**

| criterion | weighted |
|---|---|
| reproducibility | 0.8668 |
| llm_evaluation | 0.9756 |
| best_practice_query_rewriting | 0.9838 |
| containerization | 0.9838 |
| ingestion_pipeline | 0.9838 |
| retrieval_evaluation | 0.9838 |
| best_practice_hybrid_search | 0.9919 |
| best_practice_reranking | 0.9919 |
| monitoring | 0.9919 |
| problem_description | 0.9919 |
| bonus_cloud_deployment | 1.0000 |
| interface | 1.0000 |
| retrieval_flow | 1.0000 |

**12 of 13 criteria clear 0.92 weighted; `reproducibility` is the one
exception, at 0.8668.**

- [x] Confirmed option (4), reported-metric-only, with this reporting
      convention.

---

## 4. G4/R2 noise band — still unresolved, flagged, not decided

**No recommendation made yet; this is the one row still fully open.**
`objective.md` says the G4/R2 band comes from "measured re-run
variation," and the M2 agreement pass is that measurement, but the exact
shape of the band was never settled:

- Single-value band (e.g. "±1 case-level spread unit") vs. a
  difference-of-two-candidates approach (bootstrap the *difference*
  between two candidates' statistics directly, same as one of the R1 tie
  rule options)?
- Per-case band vs. aggregate band — does every case get its own noise
  tolerance, or is there one number applied to the whole comparison?

No R2 data exists yet (M3 hasn't run), so whatever is decided here has
to work from the G4 agreement data alone until M3 produces its own
re-run variation to check it against.

- [x] **DECIDED: deferred to M3.** Not a pure M2 item to begin with —
      it was always going to depend on real red-team re-run data that
      doesn't exist until M3 runs. First entry on the M3-deferred list
      below.

---

## 5. R1 — primary statistic and tiebreak

**Proposed, not yet confirmed as final: (a) record-count-normalized
Shannon entropy (H / log2(n)) as the primary statistic, IQR as the
tiebreak instead of standard deviation.**

Reasoning, from the actual computed comparison: distinct-totals-count
(the original statistic) throws away frequency information; Shannon
entropy normalized by record count (a) was the only variant that stayed
invariant under a scale-widening simulation (stretching the same 22
records' relative positions onto a 0–30 scale left it exactly unchanged,
while entropy normalized by point-range width dropped from 0.9655 to
0.7211 with zero real change in discrimination — a demonstrated, not
theoretical, vulnerability). IQR (4.50) is more robust than std dev
(3.59) to the small-n outlier sensitivity this exact corpus shows.

**Scope limitation on the scale-widening test, stated plainly**: it only
checks whether the normalization formula manufactures credit from a
wider scale with no real change in discrimination. It does not test
whether a genuinely wider scale would let real records spread out more
in practice (e.g. a judge finally having room to separate two projects
that tie today). That's a different, unmeasured question.

**Sense-check on R1 vs. G2 (certification floor), conclusion stated
plainly**: not a real conflict in the common case — 20 of 22 corpus
records currently pass, with only 12 distinct totals among them, so most
available discrimination gain sits entirely above the certify line and
doesn't require moving anyone across it. But there is a real, bounded
gap: G2's erosion budget (15.9 percentage points) is legally available
for *any* reason, including entropy-chasing rather than genuine
quality-finding, and nothing currently distinguishes the two. The
lexicographic gate ordering blocks the catastrophic version (failing G2
outright disqualifies a candidate before R1 ever matters) but not this
narrower one.

- [x] Confirmed (a) record-count-normalized Shannon entropy + IQR as
      R1's primary statistic and tiebreak.
- [x] **DECIDED (direction): crossing the certify line (v0 → candidate)
      should require citing a specific structural defect, not a score
      delta alone.** See open question below before this becomes an
      `objective.md` rule.

> should definitely cite the defect

**Mechanism resolved.** R2's exact text checked directly
(`objective.md` lines 150-156): R2 is scoped to purpose-built
adversarial records, one attack at a time, red-team constructed — a
different shape from this guardrail, which is a whole-corpus, post-hoc
comparison between v0 and a candidate over the *real* corpus. Folding
into R2 would be the wrong fit. Scoped instead as a narrow addition to
**G2** — the gate whose erosion budget this exists to protect — not a
new top-level gate.

Two design questions resolved as recommendations, not silent defaults:
citations may reference a defect catalogued as part of the *same
candidate's own submission*, not only pre-existing ones (a
pre-existing-only rule would fail a candidate for legitimately
discovering and correctly docking a new real defect — exactly what M3
discovery is supposed to produce); and the requirement applies only to
records **losing** certification, not gains (that's the actual
identified risk — G2's erosion budget spent without cause — gains don't
touch G2's floor and are already R2's territory if the concern is
score inflation).

**Gap found and fixed before this went further**: the first draft only
checked "does a real citation exist," never "does it relate to this
record" — a candidate could cite any unrelated logged finding anywhere
in the case set to justify any record's loss, and the guardrail would
pass without ever meaningfully constraining anything. Fixed, still
mechanical (no judgment call introduced): the cited finding or twin's
base record ID must equal the record actually losing certification.

**Corrected draft, still a proposal, not written to `objective.md` or
`decisions.md`:**

> **G2 addendum (proposed, unconfirmed):** any `role: corpus` record
> that certifies under v0 but does not certify under a candidate must
> cite, in the candidate's writeup, a twin-catalogue entry or red-team
> finding ID — either pre-existing or newly catalogued as part of the
> same candidate's own submission — whose **base record ID equals the
> record losing certification**, and which resolves to a real, logged
> entry in the case set or findings log. The check is mechanical: does
> the citation exist, does its base record match, does it resolve to a
> real entry — never whether the cited defect is "good enough." Records
> gaining certification are not covered.

**DECIDED: record-specific only.** The cited twin or finding's base
record ID must equal the record losing certification — no class-level
citation accepted, even for a general fix that names several affected
records. Trade-off accepted knowingly: a legitimate general fix needs a
citation built on each affected record individually, not just proof the
pattern applies to a class. Chosen for the airtight property over the
convenience.

- [x] R1/G2 guardrail fully specified: G2 addendum, losses only,
      same-candidate or pre-existing citations both allowed,
      record-specific base-ID match required. Ready to write into
      `objective.md`/`decisions.md` at the artifact step.

---

## 6. M3 round cap

**Not yet discussed this round** — held per your instruction to address
G4/R2 and the round cap after the above. Still 8, still explicitly
uncalibrated (no M3 round has run since `objective.md`'s original note
was written).

- [x] **DECIDED: keep at 8.** Revisit once M3 rounds actually run, if
      they commonly max it out.

---

## M3-deferred items (not M2 decisions, tracked so they aren't lost)

- **G4/R2 noise band form** (row 4 above) — needs real red-team re-run
  data to design against; was never a pure M2 item.
- **M3 round cap re-sizing** (row 6 above) — revisit if the first
  rounds commonly hit 8.

---

## Open questions before the artifact step

- **R1/G2 guardrail mechanism** (row 5) — direction confirmed, shape
  not yet specified. See the clarification request inline above.

---

## Artifact once every row above closes

Per the task file: one `docs/decisions.md` entry per confirmed row,
naming the frozen value and the reasoning; `docs/objective.md`'s
"freezes at M2 sealing" language updated to state the frozen values
directly. **Rows 1, 2, 3, 4, 6 are confirmed and ready to write up now**;
row 5's guardrail mechanism needs the clarification above first.

> we should also have a thorough look at decisions.md and findings.md which of thos are outdated and should be removed or overwritten/updated.

**Noted as a separate follow-up, not folded into this pass**: a
decisions.md/findings.md staleness audit is a real, standalone task —
happy to run it once the step-10 artifacts below are written, or now if
you'd rather sequence it first. Your call.
