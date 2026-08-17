# Deferred to M2 — open schema and method questions

*Live document. Items are removed when resolved, not struck through. Each
carries the date it was raised and where the evidence for it sits.*

**Status (2026-08-13): M2 schema closure resolved 20 of the 21 items this
file held.** Each resolution is recorded in `docs/decisions.md`; the full
reasoning per item is in `runs/2026-08-13-m2-schema-closure/proposal.md`.
One item remains open, below. The schema itself is not yet sealed —
sealing is a separate, later owner gate (`tasks/03-milestone-2.md` step 8).

---

## Open

### 3e. The schema is not normalised — `retrieval_best_approach_shipped`

`retrieval_best_approach_shipped` is a derived summary of the per-technique
`measured_effect` values (group H): `mixed_result` *means* "the reported
metrics disagree about which approach wins". Changing a technique's
measured effect makes the summary field factually stale, which is why
`APPROVED_ENTAILMENTS` and `twin-entailed-change-scoped` exist at all —
scoped to `p01-t01`/`p01-t02` only, refused as a standing rule.

**Not resolved at M2 schema closure, deliberately.** The proposed fix —
derive the field from the H blocks at scoring time instead of storing it —
would remove the entailment problem structurally, but this field anchors
the single most contested interpretation in v0
(`retrieval-best-approach-reading-flagged`, `findings.md` F2/F3): whether
`mixed_result` counts toward the two-point retrieval-evaluation tier is
the first row `criteria.yaml` itself flags as the thing to attack, and the
step-7 independent v0 fidelity diff may still overturn the reading it
currently rests on. Writing a derivation formula now, bundled into a
21-item schema-closure sign-off, would relocate that judgment call rather
than remove it — and the sign-off session runs no cross-check comparable to
the fidelity diff that this specific field needs.

**What resolving it needs:** a derivation rule for
`retrieval_best_approach_shipped` from `hybrid_search.measured_effect`,
`reranking.measured_effect`, `query_rewriting.measured_effect` (and
whichever other technique fields bear on "which approach was best" once
step 7's diff either confirms or overturns the `mixed_result` reading),
reviewed by the owner on its own, not folded into a batch. Candidate
timing: after step 7 (fidelity diff) settles the reading question it
depends on, and before step 8 (sealing) — a normalisation that outlives an
unsettled interpretation question would just need doing twice.

Decision recorded: `retrieval-best-approach-not-normalised-open` in
`docs/decisions.md`.
