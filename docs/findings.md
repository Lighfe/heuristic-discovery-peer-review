# Findings

*Log — append-only, nobody reads it linearly. What the loop learned about
the **evaluation criteria under study**, never about how this lab is built
(that is `decisions.md`). Every entry names the artifact behind it.*

---

## F1 — Three diagnosed failure modes are present in a real submission before any twin is built

**Date:** 2026-08-10
**Artifacts:** `cases/records/p01.yaml`, `cases/records/p02.yaml`,
`tools/generate_twins.py` (rejection analysis during M1 twin construction)
**Status:** observed from extraction. **No scoring run has happened yet**, so
this says nothing about what the current criteria award — only about what is
there to be awarded on.

`project-evaluation-issues.md` is explicit that its examples are
hypothetical: *"The scenarios used to illustrate each problem are
hypothetical; they are chosen to make a failure mode visible, not to describe
any particular submission."* That caveat can now be narrowed for three of
them.

While building M1's twins, three catalogue types were rejected as
unbuildable on p01 — and each for the same reason: **the base record is
already at the defective value, so there is no headroom to degrade it.**

| catalogue type | field | p01 | p02 |
|---|---|---|---|
| `config-drift` | `retrieval_eval_config_matches_shipped` | `differs` | `differs` |
| `config-drift` | `llm_eval_config_matches_shipped` | `differs` | `differs` |
| `unfailable-eval` | `llm_eval_metric_at_ceiling` | `true` | `false` |
| `unfailable-eval` | `retrieval_eval_relevance_rule` | `source_level` (coarsest in the enum) | `document_level` |
| `circular-eval` | `llm_eval_judge_spotchecked` | `false` | `false` |
| `circular-eval` | `llm_eval_question_generator` | `none_committed` | `generator_ties_question_to_passage` |

**What this supports.** `config-drift` and the absence of judge
spot-checking are present in **both** repositories: in each, the
configuration measured is not the configuration shipped, and in each a model
judge's verdicts are never sampled against a human reading. Two of two is a
small number, but these are not scenarios anyone invented — they are the
values two real submissions actually hold.

`unfailable-eval` is p01 only: p02's metrics sit below ceiling (0.805,
0.969) and its relevance rule is one step finer.

**What this does not support.** Nothing here says the current criteria fail
to penalise these. That is exactly what M1's scoring pass measures and it
has not run. It is also two repositories out of twelve, chosen because they
are the two the owner peer-reviewed — so they are not a random sample of the
corpus, and the M2 extraction is the first honest base rate.

**Why it matters anyway.** `circular-eval` was rejected as a twin for a
second reason worth recording separately: the only remaining move on p01 was
`llm_eval_role_overlap: same_family → same_model`, and the schema
deliberately declines to assert a direction for that (owner ruling at the M1
gate — each call runs in a fresh context, so the residual concern is shared
inductive bias, a tendency rather than a defect). So `circular-eval` is
currently **unfalsifiable as a twin type on any record already lacking a
judge spot-check** — a gap in the case set, not a property of the repos.

**Consequence for the case set.** A catalogue type that cannot be
instantiated because every available base already exhibits it is untested,
not passed. If the same holds across the M2 corpus, `config-drift` and
`circular-eval` need base records constructed *without* the defect so the
degradation has somewhere to travel from — the inverse of the usual twin
direction, and worth deciding at M2 sealing.

---

## F2 — Both extracted projects evaluate a configuration that is not the one they ship

**Date:** 2026-08-12
**Artifacts:** `cases/records/p01.yaml`, `cases/records/p02.yaml`
(`retrieval_eval_config_matches_shipped`, `llm_eval_config_matches_shipped`),
`candidates/v0/criteria.yaml`, `docs/superseded.md`
**Status:** measured on two records under candidate v0. **This is candidate
material** — the proposer reads `findings.md` (`plan.md`, roles table), and
this entry exists so the idea below is picked up rather than lost.

### The defect

Both records hold `differs` on **both** configuration fields. The evaluation
each project reports was not run against the system it ships:

- **p01** evaluates four retrieval approaches at `k=20`, reranking to
  `top_k=10`, with no query rewriting — and ships `k=50`, `top_k=5`, with
  rewriting on.
- **p02** measured every reported number against an index built from one
  source, while both committed ingestion scripts build the same-named
  collection from a different source with incompatible id types, so the
  evaluation cannot be re-run against the shipped index at all.

### What the current criteria do about it

**Nothing.** v0 awards p01 the full two points for retrieval evaluation, but
not because the best-performing approach is shipped: the record holds
`retrieval_best_approach_shipped: mixed_result`, meaning the project's own
metrics disagree about which approach wins, and the two points come from
v0's 2-point tier accepting `mixed_result` alongside `yes` —
`criteria.yaml`'s own flagged interpretation (`retrieval_evaluation.interpretation`),
not from an actual best-approach match. That the comparison was run at
different parameters is invisible to it either way, because the criterion
never asks.

The consequence is the §3 pattern from `project-evaluation-issues.md` made
concrete: *the measured system is not the shipped system*, present in both
projects examined, scored by nothing.

### The candidate idea, and why it is not in v0

Requiring `config_matches_shipped: matches` for the two-point tier was
tried in v0 on 2026-08-12 and reverted the same day. It belongs in a
**candidate**: as a change it can be measured against the baseline by R1,
whereas in v0 it silently pre-improves the reference every candidate is
compared to. It also, as built, cost G1 its signal on the
harmful-component twin — both p01 and its degraded twin landed in the same
one-point tier and the twin's distinction vanished. Full reasoning and the
numbers: `docs/superseded.md`, `v0-requires-config-match`.

A candidate adopting it must therefore handle two things that version did
not: keep the harmful-component distinction scoreable alongside the
config-drift denial, and stay inside a point scale where both denials
currently collapse to the same tier.

### Limits

Two repositories, both `owner_reviewed`, so not a random sample of the
corpus — M2's extraction is the first honest base rate. The p01 field value
was confirmed by the owner's field-level validation (2026-08-12); p02's was
too, and its extraction note records that a literal reading of the field's
own definition would have returned `matches`, since every parameter the
definition names does match and the divergence is the corpus itself.

---

## F3 — The twin baseline: which known defects the current criteria cannot see

**Date:** 2026-08-12
**Run:** `runs/2026-08-12-m1-scorer-v0/manifest.json` (candidate v0, 0 requests)
**Artifacts:** `cases/records/p01.yaml`, `cases/twins/*.yaml`,
`candidates/v0/criteria.yaml`

**This is M1's deliverable.** Six twins of p01, each differing from it in one
constructed way whose direction is known because it was built that way.
Recomputed from the run manifest, not carried from prose.

| twin | defect constructed | required | v0 | verdict |
|---|---|---|---|---|
| `p01-t01` | re-ranker whose own numbers condemn it, shipped anyway | below p01 | 21 → 20 | **pass** |
| `p01-t02` | same re-ranker, measured and removed with reasons committed | ≥ t01 | 20 → 21 | **pass** |
| `p01-t03` | three headline figures with no artifact behind them | below p01 | 21 → 21 | **FAIL** |
| `p01-t04` | eight dashboard panels querying tables the app never creates | below p01 | 21 → 21 | **FAIL** |
| `p01-t05` | Flask→FastAPI, Qdrant→Elasticsearch | exactly equal | 21 = 21 | pass |
| `p01-t06` | 53 files → 41 | exactly equal | 21 = 21 | pass |

**G1 fails on this case set: 4 of 6 pass, 2 fail.**

### Why the two failures are findings and not scoring bugs

Both failing twins mutate a field **no criterion reads at all**. The
harness separates this from a twin that moves a read field without crossing
a tier, because a totals table renders the two identically:

- `p01-t03` moves `untraceable_number_count` 18 → 21. **No criterion in the
  current guidance reads any documentation-accuracy field.** Nothing scores
  whether a reported number has anything behind it — the §4 diagnosis,
  confirmed by measurement.
- `p01-t04` moves `monitoring_charts_bound_to_data` `all` → `none`. The
  monitoring criterion reads the panel *count* and never asks whether a
  panel is bound to data. Counting panels is what it does, which is the §2
  diagnosis, confirmed.

The criteria cannot score what they never look at, and both defects are
checkable facts about two committed files. This is one mechanism, not two:
both mutated fields sit outside every criterion's read-set, the same
mechanism behind four of F4's five successful attacks.

### What passes, and the one thing that genuinely works — and the reading it rides on

`p01-t01`'s ordering holds under v0's 2-point retrieval tier accepting
`retrieval_best_approach_shipped: mixed_result` alongside `yes` —
`criteria.yaml`'s own flagged interpretation, named there as "the most
consequential interpretation in v0, and the first row a reviewer of this
transcription should attack." Under the stricter `yes`-only reading, p01
falls from 21 to 20 (its own value is `mixed_result`, not `yes`) while
`p01-t01` stays at 20 (its own value is `no`, which already took the
1-point tier under either reading): the pair ties and G1 fails on it. `p02`
holds `mixed_result` too, so the same reading choice moves its score.

`plan.md` schedules an independent v0 fidelity diff at M2 — a fresh
session, no access to the transcription rationale, checking guidance
against mapping line by line. That diff is not a neutral check on this
finding: if it settles on the strict reading, the one clean pass among the
degraded twins goes with it.

`p01-t01`/`p01-t02` is the pair the incentive argument turns on, and **v0
handles it**: shipping a component its own numbers condemn scores 20, while
measuring it and removing it with reasons committed scores 21. The current
criteria do *not* punish a documented removal, contrary to what the
incentive-gradient argument in §2 might suggest. What they fail to do is
notice the component was harmful in the first place — `reranking.measured_effect`
is read by no criterion; t01 moves only because the derived field
`retrieval_best_approach_shipped` moves with it.

Both no-change twins score exactly equal, so v0 is not noise-sensitive on
technology choice or repository size.

### Scope, stated because G1 invites overreading

A G1 result is discrimination of the **catalogued** failure modes only, never
general discrimination (decision `g1-claims-catalogue-coverage`). One base
record, six twins, three catalogue types plus two no-change kinds. Three
further catalogue types could not be built on p01 at all because p01 already
holds the defective value (F1).

---

## F4 — Five of five attacks on the current criteria succeeded

**Date:** 2026-08-12
**Run:** `runs/2026-08-12-m1-redteam/report.json` (0 requests, deterministic)
**Artifacts:** `runs/2026-08-12-m1-redteam/attack-a*.yaml`,
`tools/redteam_m1.py`

Five budgeted attempts to build a schema-valid record that is structurally
bad and still scores at least p01's 21. **All five succeeded**, and every
one certifies. Each badness is stated as a checkable structural fact, not a
judgment; the constructed records are committed so the claim is auditable.

| # | attack | score | vs p01 |
|---|---|---|---|
| a1 | three techniques implemented, none shipped, none evaluated | 21 | +0 |
| a2 | every reported figure untraceable (`none_traceable`, 40 figures) | 21 | +0 |
| a3 | feedback plus eight panels, every panel bound to nothing | 21 | +0 |
| a4 | one model writes, answers and judges; metric at ceiling | **22** | **+1** |
| a5 | 9 unfollowable steps, 12 dead paths, 6 claims the code contradicts | 21 | +0 |

**Five attacks, one mechanism, plus one that is different.** a1, a2, a3 and
a5 all mutate fields no criterion reads — the same mechanism behind both G1
failures in F3. a4 is the exception: it moves a field `llm_evaluation` does
read (`llm_eval_approaches_compared`), which is why it is the only attack
that gains a point rather than merely holding score.

| # | field(s) mutated | read by any criterion? |
|---|---|---|
| a1 | 9 technique fields (`present`/`shipped_enabled`/`evaluated`/`measured_effect`) | no |
| a2 | `headline_numbers_traceable`, `untraceable_number_count` | no |
| a3 | `monitoring_charts_bound_to_data` | no |
| a5 | `run_instructions_gap_count`, `broken_reference_count`, `document_code_conflicts` | no |
| a4 | `llm_eval_approaches_compared` (plus three circularity fields none of them read) | yes, one |

Reported for R2's ranking, this is **5 successful attacks, 1 distinct
mechanism**: a candidate that reads any documentation-accuracy or
dashboard-binding field defeats a1, a2, a3 and a5 at once, and needs a
separate fix for a4.

### The circularity is already rewarded on real, shipped projects — no attack needed

a4 corroborates this; it is not the load-bearing case. p01 and p02, both
real extracted repositories, already show the criteria paying for circular
evaluation with no constructed record involved:

- **p01** holds `llm_eval_role_overlap: same_family` (the answer generator
  and the judge are different sizes of one model line) and scores 1 of 2 for
  `llm_evaluation` — capped by `llm_eval_approaches_compared: 1`, not by any
  check on role overlap. No criterion reads `llm_eval_role_overlap`, so the
  cap comes entirely from having one approach; role overlap costs it
  nothing further.
- **p02** holds `llm_eval_role_overlap: same_model`,
  `llm_eval_question_generator: generator_ties_question_to_passage` and
  `llm_eval_judge_spotchecked: false` — one model writes the question set,
  generates one of the two compared answers, and judges both, including the
  rival it loses to — and scores the **full 2 of 2** for `llm_evaluation`
  (`runs/2026-08-12-m1-scorer-v0/manifest.json`, `per_criterion.llm_evaluation`
  for p02). The triple role overlap costs it nothing; the criterion counts
  approaches compared and stops there.

p02 needs no approach-count caveat: it clears the two-point tier outright,
on a real, already-shipped submission, holding every circularity field a4
later assembles synthetically.

**a4 is the sharpest constructed result in M1.** A fully circular evaluation — one model
generating the questions from the passages, producing the answers, judging
its own output, no spot-check, reported metric pinned at its maximum —
scores **one point higher than the real project it was built from**, because
the criterion counts approaches compared and a circular setup compares two.
The current criteria reward the circularity.

**No attack was needed against the technique points, the monitoring count or
the reproducibility criterion beyond stating the fact**: each attack is a
single edit to fields the criteria read, or to fields they ignore, and none
required cleverness. That is the finding — the attack surface is not subtle.

### a4 is not an invented monster — it is two real projects recombined

The obvious objection to a synthetic attack is that no repository would ever
hold that record. Checked, and it does not survive: **five of a4's six
answer-evaluation field values are exactly p02's**, a real extracted project.

| field | a4 | p02 (real) | same? |
|---|---|---|---|
| `llm_eval_approaches_compared` | 2 | 2 | yes |
| `llm_eval_role_overlap` | `same_model` | `same_model` | yes |
| `llm_eval_question_generator` | `generator_ties_question_to_passage` | same | yes |
| `llm_eval_judge_spotchecked` | `false` | `false` | yes |
| `llm_eval_present` | `true` | `true` | yes |
| `llm_eval_metric_at_ceiling` | `true` | `false` | **p01 holds `true`** |

The single differing value is held by the *other* real record. So a4 is p02's
answer-evaluation profile with p01's ceiling value — every individual value
observed in a real submission, in a combination nothing prevents. All five
attack records were type-checked against the schema (340 leaf values, all
legal).

### The 22nd point comes from one field, and it is the counting clause

`llm_eval_approaches_compared: 1 → 2` moves `llm_evaluation` from 1 to 2 and
nothing else changes. The tier awarded is *"Multiple approaches are
evaluated, and the best one is used"*.

So the criterion pays a point for **comparing two things**, and the two
things being compared are one model's output judged by that same model
against questions it wrote from the passages. The circularity is not
overlooked by the criterion — it is the mechanism by which the point is
earned.

**Limits.** The bar is p01's 21, because the corpus range over two records
is [17, 21] and too thin to be a range. Zero attacks failed, so this round
says nothing about where v0's resistance begins — a round where everything
succeeds has not found the boundary. M3's rounds run against candidates
built to resist, where failed attacks become informative.

---

## F5 — Same-model self-consistency, smoke test only

**Date:** 2026-08-12, corrected 2026-08-13
**Runs:** `runs/2026-08-12-m1-agreement-smoke/` (24 requests,
`gemini-3.5-flash-lite`, temperature 0.7, protocol 1) — original;
`runs/2026-08-13-m1-agreement-smoke-recomputed/` (0 requests, 24 cache hits)
— same responses, totals recomputed after the bug below was fixed.
**Artifacts:** `agents/reviewer/v1/prompt.md`, `.../agreement.json`,
`loop/agreement.py`, `.cache/`

**NOT A BASELINE.** The task labels this a pipeline smoke test; the baseline
is measured at M2 over the full corpus. It is *same-model self-consistency*
— three stateless samples from one model, fields shuffled in a seeded order
— and is neither human reviewer agreement nor cross-family agreement
(decision `g4-is-self-consistency`). The real process medians three humans,
which this does not stand in for.

### The harness trusted the model's arithmetic, and the model's arithmetic was often wrong

Found at the M1 owner review while checking a discrepancy in this entry.
`loop/agreement.py` read a sample's total straight from the `total` field
the model was asked to report, rather than summing the `points` the same
response listed per criterion. Checked directly against the cached response
text: **16 of the 24 M1 smoke samples (67%) have a self-reported `total`
that does not equal the sum of that response's own per-criterion points**,
off by 1 to 3 points, in both directions. This has nothing to do with
criterion-level judgment — it is the model failing to add thirteen small
integers correctly — and it was inflating every spread and median number
this entry originally reported.

**Fixed**: `loop/agreement.py` now recomputes each sample's total from its
`criteria[].points`, mechanically, and ignores the model's own sum. Rerun on
the existing cache at zero further requests
(`runs/2026-08-13-m1-agreement-smoke-recomputed/agreement.json`). Every
number below is the corrected one.

### Corrected results

| case | totals | spread | median | v0 | diff |
|---|---|---|---|---|---|
| p01 | 21, 21, 21 | 0 | 21 | 21 | 0 |
| p02 | 17, 17, 17 | 0 | 17 | 17 | 0 |
| p01-t01 | 21, 20, 24 | 4 | 21 | 20 | +1 |
| p01-t02 | 24, 21, 20 | 4 | 21 | 21 | 0 |
| p01-t03 | 21, 19, 24 | 5 | 21 | 21 | 0 |
| p01-t04 | 20, 19, 19 | 1 | 19 | 21 | −2 |
| p01-t05 | 20, 21, 19 | 2 | 20 | 21 | −1 |
| p01-t06 | 23, 20, 21 | 3 | 21 | 21 | 0 |

The two real records are now **exactly self-consistent**: all three samples
of p01 and all three of p02 land on the same total once the model's own
addition error is removed. The spread the original entry reported for these
two cases (1–3 points on every case) was entirely an artifact of the bug.
The constructed twins still show real spread, 1 to 5 points — this is not a
measurement problem, it is same-model self-consistency doing what it says.

`agreement-protocol-ceiling` declares G4 decorative if the baseline comes
back ≥ 0.95. Exact-match self-consistency is 2 of 8 corrected, not 0 of 8 —
still well short of a ceiling, so real variance remains for G4 to measure
and its *form* (the M2 decision) still matters.

### The reviewer model applies the retrieval-evaluation criterion as a pure count, ignoring its second clause

`retrieval_evaluation` is the only criterion v0 moves on between p01 (2) and
its degraded twin `p01-t01` (1). The reviewer model scored it **2 in all six
samples**, both cases. But only three of those six samples test anything:
p01 holds `retrieval_best_approach_shipped: mixed_result` — the project's
own metrics disagree about which approach wins, so there is no single "best"
to check against, and scoring 2 there is correct, not a missed check. Only
`p01-t01` holds `retrieval_best_approach_shipped: no`, the value where the
clause has something to bite on: a single best approach is clearly named by
the record, and it is not the one shipped. Its three stated reasons:

> "Four different retrieval approaches are evaluated and reported in the
> retrieval evaluation."
> "Four retrieval approaches are evaluated and reported in a metrics table."
> "Four retrieval approaches are evaluated and compared in the retrieval
> evaluation."

None of the three mentions which approach shipped, in a record that states
in as many words that the shipped approach is not the best-measured one.
**On n=3, the reviewer model applied the counting clause and skipped the
shipping clause.** Three consequences:

1. v0's executable layer is **stricter than this reviewer model applies the
   same text** on this one case — v0 catches the harmful-component twin,
   the model does not. A faithful transcription can be more demanding than
   the practice it transcribes, and the writeup must not present v0 as what
   a reviewer generally does.
2. It strengthens F2. If the shipping clause is already skipped in practice,
   making the shipped configuration an explicit, checkable condition is not
   adding burden — it is asking for a check the text already implies and
   this sample never performs.
3. It is a **prose defect no executable layer can fix**, since the clause is
   unambiguous and simply not applied here. A candidate must make the check
   mechanical or drop the clause; leaving it as prose reproduces this.

At three informative samples this is an observation to confirm at M2 over
the full corpus, not a settled result, but it is specific and falsifiable.

A second, open explanation this does not rule out: `criteria.yaml` notes
the guidance has no written tier for "multiple approaches compared, the best
one not shipped," and the reviewer prompt instructs the model not to refuse
to score. A model facing an untiered case may award the nearest tier rather
than skipping the clause — a rational response to a gap in the guidance,
not necessarily evidence the clause is ignored when a tier exists for it.
The two explanations point to different fixes (make the clause mechanical,
versus write the missing tier) and this sample cannot separate them.

**Confound on record:** reviewer prompts render `basis` sentences that cite
repository paths inline, so citation density varies between fields and may
move a score for reasons unrelated to content (`deferred-to-m2.md` 3j).
