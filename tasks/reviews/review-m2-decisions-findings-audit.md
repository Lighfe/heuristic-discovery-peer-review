# Review — decisions.md / findings.md staleness audit

Save any output as `tasks/reviews/review-m2-decisions-findings-audit-results.md`,
following the two-part shape of `tasks/reviews/review-m1.md`: Part A is
what needs an owner decision, Part B is what you checked and can settle
yourself, argued back where you think the premise below is wrong.

Run in a **fresh session** — no memory of the M2 step-8/step-9/step-10
work needed, and none should be assumed. Everything you need to check a
claim is either in the two files under review or in the artifact each
entry cites. `docs/decisions.md` is currently 900 lines, `docs/findings.md`
548 — both long enough that staleness accumulates unnoticed, which is
exactly what this task checks for.

**Precondition: run this after step 10's `decisions.md` entries are
written, not before.** This audit checks whether what's written still
says what's true — mid-flight, while step 10 is still being decided,
there's nothing stable yet to audit for that row, and treating an
in-progress discussion as a stale-or-not entry would be checking the
wrong thing.

---

## 0. What this review does not do

This is not a review of whether the *decisions* were right. It is a
review of whether the two documents still *say what is true now*.
`CLAUDE.md` states both documents' contracts explicitly:

- `decisions.md` is **live**: "one short block per current decision...
  Reversing a decision means rewriting the entry in place... The old
  entry with its full original reasoning moves to `docs/superseded.md`.
  Nothing is lost and the live file does not grow from reversals."
- `findings.md` is a **log**: append-only, nobody reads it linearly,
  each entry names the run that produced it.

A live document that still describes something as "open" after it was
closed, or states a number that a later run superseded without a
formal reversal, is broken by its own contract — not wrong when
written, wrong *now*. That is the failure mode this task exists to
find. A log entry is not expected to update itself, but it can still be
factually wrong if it was wrong when written, or if a later entry
silently contradicts it without cross-referencing.

---

## Part A — checks that need an owner decision if they turn something up

### A1. Decisions whose "open"/"deferred" status may have since closed.

Grep `docs/decisions.md` for language like "stays open," "not yet
resolved," "deferred," "pending," "open question," "flagged... not
fixed." For each hit: check whether a *later* entry, a run under
`runs/`, or the current state of `criteria.yaml`/`schema.md`/`objective.md`
actually resolved it — without a formal reversal recording that. Recent
candidates worth checking directly, not assumed still open: item 3e
(`retrieval-best-approach-not-normalised-open`), the G4/R2 noise-band
row, anything under "Schema" that predates the M2 sealing checklist —
**and, if this task runs before step 10's decisions.md rows are
written, the R1/G2 guardrail design question does not exist as an entry
yet and should not be checked for staleness; if it runs after, check
it like any other row.** Run this task after step 10's `decisions.md`
entries land, not mid-flight — the audit is meant to check what's
written, and step 10 isn't finished writing yet.

**Fix, if found**: rewrite the entry in place per the reversal
convention (old reasoning moves to `superseded.md`), don't just flag it
in the results doc.

### A2. Decisions whose cited artifact no longer exists or no longer says what's cited.

Every decision names a file, a run, or a field. Spot-check a sample
(at minimum: every entry added or touched during the M2 sealing
checklist and step 9/10 work — `sealing-review-fixes`,
`monitoring-instrumentation-boundary-fixed`,
`p21-gap-count-reconfirmed-not-corrected`,
`agreement-excludes-bonus-points`, and the step-10 rows once they land)
against the actual current file/field. A citation that pointed to a
correct value in August may point to a value a later fix changed.

### A3. Findings.md entries whose "current" framing predates a later correction.

`findings.md` doesn't rewrite itself by contract, but check for entries
that read as live/current when a *later* finding or decision superseded
their number without saying so. F5 and F6 are the two most likely to
have this problem given how many follow-up rounds each went through
after being first written — check whether every number currently in F6
matches the *last* correction made to it, not an intermediate one.

---

## Part B — mechanical checks you can settle yourself

### B1. Every `decisions.md` entry that names a specific file, field, function, or line number: does it still exist?

Grep every backtick-quoted path/field/function name across the file,
check each resolves. A renamed field or moved file leaves a decision
citing something that no longer exists — the decision may still be
right, but the citation is now false, and per this project's own rule
("a memory that names a specific function, file, or flag is a claim
that it existed *when written*"), that's worth fixing even when the
underlying decision stands.

### B2. Duplicate or near-duplicate decisions on the same topic.

Some topics got revisited across multiple sessions (e.g. the
`monitoring_instrumentation` boundary, `retrieval_best_approach_shipped`,
the G3/G4/R1 step-10 work). Check whether any two entries say
materially the same thing without one citing the other, which would
mean a future reader has to reconcile them by hand instead of reading
one.

### B3. `findings.md` entries whose evidence contradicts a claim made in a *later* section of the same document.

Read linearly once, front to back — the document's own convention says
nobody normally does this, which is exactly why an internal
contradiction could survive undetected. Flag any pair, don't resolve
them yourself if resolving requires new investigation — that becomes
Part A material.

### B4. `Binds:` lines — are the ~5 entries that now carry one (added since `binds-line-going-forward`) still accurate about what they bind to?

Small, bounded check: `binds-line-going-forward`, `group-j-restructure-deferred`,
`monitoring-instrumentation-boundary-fixed`, `p21-gap-count-reconfirmed-not-corrected`,
`agreement-excludes-bonus-points` (confirm this list is current, don't
assume it — search fresh). Confirm each `Binds:` claim still describes
the actual state of the file/rule it names.

---

## Constraints

- **Do not edit `objective.md` or `criteria.yaml`** — this is a
  documentation-accuracy pass on two specific files, not a scope change
  to the project's measurement or scoring layer.
- **Do not silently rewrite `decisions.md` entries in this session.**
  Where Part A finds something, propose the fix in the results doc for
  owner sign-off, following the "report before write" convention — the
  live-document reversal mechanism is cheap to apply once approved, but
  applying it without sign-off on a document this central is exactly
  the kind of action `CLAUDE.md` asks to be transparent and reversible
  about.
- **Nothing here blocks step 10 or M2 sealing.** This is a
  housekeeping pass on two documents, not a gate.
