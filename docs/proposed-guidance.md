# Proposed project-evaluation-guidance (OUTLINE ONLY)

*Live document — this is THE DELIVERABLE. As of 2026-08-09 it is an agreed
outline only: section headings and what each will contain. No criteria text
exists yet; none is written until the loop produces evidence for it. The
final document replaces the course's `project-evaluation-guidance.md`
wholesale, so it must contain everything the current one does.*

## Planned structure

1. **Objective, problem statement, datasets, technologies, project ideas** —
   carried from the current guidance verbatim or near-verbatim; out of scope
   for revision, kept so the document is a complete drop-in replacement.
2. **Documentation guidance for authors** — revised: keeps the current
   advice, adds an author checklist that maps each claim a README makes to
   the artifact that backs it. The intent is to make the accuracy criterion
   below cheap for reviewers, but that is an assumption to be priced under
   the G3 cost table, not asserted — if following the ledger costs real
   minutes, the criterion must earn them within the gate.
3. **Certification gates** — new section: the admission-style checks
   (working end-to-end system: knowledge base + LLM in the flow, some
   interface, some ingestion, a problem statement) restated as explicit
   binary gates that certify, generous and unambiguous, replacing the dead
   0/1/2 ladders diagnosed in `project-evaluation-issues.md` §1.
4. **Graded criteria** — the discriminating portion, scored above the gates:
   evaluation validity (procedural checks only — committed and inspectable
   question set, judge spot-checked, decision rule fixed before measurement,
   measured config = shipped config), documentation accuracy (additive:
   points for claims that hold up, per the claims ledger), monitoring,
   containerization, reproducibility, interface quality. Exact criteria and
   tiers come from the loop; total stays in the ~20-point neighbourhood for
   cohort comparability.
5. **Technique points** — conditioned on measured effect rather than
   presence, so a documented removal is worth no less than a kept component
   (repairs the incentive gradient of issues §2).
6. **Reviewer procedure** — revised review tips: time budget per section,
   what evidence to record for any score below full marks, the
   cannot-run-it protocol (declare that the review is documentation-based
   rather than silently switching instruments), and what reviewers are NOT
   asked to judge (semantic quality, domain correctness — per the
   constraints section of the issues doc).
7. **Peer review mechanics, plagiarism policy** — carried verbatim; out of
   scope (see `decisions.md` observations).
8. **Change map** — appendix: current criterion → replacement, with the
   point-mapping that keeps scores roughly comparable across cohorts and
   the recalibrated pass threshold, each change citing its finding.
