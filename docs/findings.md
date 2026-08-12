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
