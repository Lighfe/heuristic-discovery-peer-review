# Superseded decisions

*Log — append-only. Each entry is a decision moved here from `decisions.md`
with its full original reasoning, when it was reversed, and by what.*

## `v0-requires-config-match`

**Held 2026-08-12, reversed 2026-08-12** (same day, before any measurement
was published from it). Replaced by `v0-literal-no-inferences`.

### The entry as it stood

> **v0-requires-config-match** — v0's two-point evaluation tiers additionally
> require `*_config_matches_shipped: matches`. Owner, M1 phase 6, and **not a
> transcription** — the guidance says no such thing: "the best one is used"
> cannot be credited from an evaluation of a configuration that is not the one
> shipped. Marked `inference:` in `criteria.yaml` (search that key to
> enumerate every departure). Cost: v0 is stricter than the written criteria,
> both records move, and every comparison against v0 inherits it.

### The original reasoning, in full

An evaluation run against a configuration that is not the one shipped is not
measuring the running system, so the comparison the two-point tier exists to
reward has nothing to attach to. p01 evaluates four retrieval approaches at
`k=20`, reranking to `top_k=10`, with no query rewriting — and ships `k=50`,
`top_k=5`, with rewriting on. Whichever approach led at the evaluated
parameters need not lead at the shipped ones, so "the best one is used" is
unestablished.

That argument was accepted as sound criterion design and is not withdrawn.

### Why it was reversed

Two reasons, the second decisive and measured rather than argued.

**1. A baseline must not be pre-improved.** v0 exists to be the reference
every candidate is compared against — `objective.md` uses it for G3's cost
ceiling, R1's spread comparison and G2's r₀. A v0 stricter than the
instrument it baselines makes every later candidate look *less* like an
improvement, because part of the improvement is already sitting in the
reference.

**2. It blinded v0 to the twin M1 exists to test.** Traced from the fact
that all six twins tied. Under the condition, p01 and `p01-t01` both landed
in the same 1-point tier — p01 for config drift, t01 for shipping a
component its own numbers condemn — and the distinction the twin was built
to expose vanished:

| | p01 | p01-t01 | verdict |
|---|---|---|---|
| literal criteria | 21 | 20 | **−1, G1 passes** |
| with the condition | 20 | 20 | **tie, G1 fails** |

Adding `retrieval_best_approach_shipped` to the condition's tier was tried
and does not fix it: t01 then falls to `fallback: 1`, which is the same
point. Both denials are 1-point outcomes and the course's 0/1/2 ladder has
no room to stack them.

So the condition cost a working G1 signal on the harmful-component twin, in
exchange for making the baseline non-representative. The idea keeps its
merit; it belongs in a candidate, where R1 can measure what it buys.

### Where the idea went instead

`docs/findings.md` F2 — which the candidate proposer reads (`plan.md`,
roles table), so it seeds proposals rather than sitting inert here.
