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

**Nothing.** v0 awards p01 the full two points for retrieval evaluation:
four approaches were compared and the best-performing one is shipped, which
is what the criterion asks. That the comparison was run at different
parameters is invisible to it, because the criterion never asks.

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
checkable facts about two committed files.

### What passes, and the one thing that genuinely works

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

**a4 is the sharpest result in M1.** A fully circular evaluation — one model
generating the questions from the passages, producing the answers, judging
its own output, no spot-check, reported metric pinned at its maximum —
scores **one point higher than the real project it was built from**, because
the criterion counts approaches compared and a circular setup compares two.
The current criteria reward the circularity.

**No attack was needed against the technique points, the monitoring count or
the reproducibility criterion beyond stating the fact**: each attack is a
single edit to fields the criteria read, or to fields they ignore, and none
required cleverness. That is the finding — the attack surface is not subtle.

**Limits.** The bar is p01's 21, because the corpus range over two records
is [17, 21] and too thin to be a range. Zero attacks failed, so this round
says nothing about where v0's resistance begins — a round where everything
succeeds has not found the boundary. M3's rounds run against candidates
built to resist, where failed attacks become informative.

---

## F5 — Same-model self-consistency, smoke test only

**Date:** 2026-08-12
**Run:** `runs/2026-08-12-m1-agreement-smoke/` (24 requests,
`gemini-3.5-flash-lite`, temperature 0.7, protocol 1)
**Artifacts:** `agents/reviewer/v1/prompt.md`, `.../agreement.json`

**NOT A BASELINE.** The task labels this a pipeline smoke test; the baseline
is measured at M2 over the full corpus. It is *same-model self-consistency*
— three stateless samples from one model, fields shuffled in a seeded order
— and is neither human reviewer agreement nor cross-family agreement
(decision `g4-is-self-consistency`). The real process medians three humans,
which this does not stand in for.

24 requests, 24 parsed, **zero unparseable**. Result: **no case produced
three identical totals.** Spread was 1–3 points on every one of the eight
cases.

Two observations, both provisional at n=3:

- **The G4 ceiling check would not trigger.** `agreement-protocol-ceiling`
  declares G4 decorative if the baseline comes back ≥ 0.95. Exact-match
  self-consistency here is 0 of 8, so there is real variance for G4 to
  measure — which makes G4's *form* (the M2 decision) matter rather than
  being moot.
- **The prose layer may not reproduce the executable layer's twin
  ordering.** Reviewer medians put `p01-t01` at 23 against p01's 22 — the
  degraded twin scoring *above* its base, the opposite of the executable
  result in F3. If that survives M2's larger sample it is a
  prose↔executable fidelity defect in the current criteria's own wording,
  not in the transcription. At three samples with a two-point spread it is
  an observation to test, not a finding.

**Confound on record:** reviewer prompts render `basis` sentences that cite
repository paths inline, so citation density varies between fields and may
move a score for reasons unrelated to content (`deferred-to-m2.md` 3j).
