# heuristic-discovery-peer-review

> **Work in progress.** This repository is a design, not a result. No code
> has been written, no project has been analysed, no measurement has been
> taken, and the deliverable is still an empty file. Everything below
> describes what is *intended*.

A loop of agents that searches for better evaluation criteria for
DataTalksClub zoomcamp capstone projects, and produces the evidence needed
to argue for them.

The output is meant to be a single document — `docs/proposed-guidance.md`,
a complete replacement for the course's project brief, carrying revised
scoring criteria together with the reviewer guidance around them.
Everything else the loop produces is working evidence that the document
cites.

The goal is **not stricter criteria**. Today's criteria certify nearly
every submission and cluster scores near the top, so a score carries little
information. The aim is criteria that keep certification just as
achievable while making the scores above the pass line mean something.

## Where things stand — 2026-08-10

Planning and design only. Milestone 1 has not started.

| file | what it is |
|---|---|
| `CLAUDE.md` | the project's constraints — **start here** |
| `docs/objective.md` | what "better" means: six gates, three ranking terms (approved 2026-08-10) |
| `docs/plan.md` | the loop's shape, agent roles, cost model, milestones M1–M4 |
| `docs/decisions.md` | every current design decision, one short block each |
| `docs/proposed-guidance.md` | the deliverable — **empty placeholder** |
| `tasks/` | the prompts steering the work, in order |
| `courses/<slug>/` | the course inputs under study |

Next up is `tasks/02-milestone-1.md`: extract two real capstone repos into
evidence records, build a handful of test cases, transcribe the *current*
criteria into an executable baseline, and run one pass end to end.

## Two things worth knowing before reading further

**There is no labelled corpus of graded projects, and there will not be
one.** Validity comes instead from pairs of records that differ in exactly
one way whose direction is known *because the pair was constructed that
way* — nobody grades anything. The epistemics section of `CLAUDE.md`
explains why, and most other design choices follow from it.

**Every threshold in the design is a judgment value, not a measurement.**
The numbers were set by the project owner with no data behind them, and
`docs/objective.md` names them all in one place so no gate can quietly
present itself as more grounded than it is.

## Anonymity

Capstone projects are referred to only as `p01`, `p02`, … The file mapping
those ids to real repositories and people is gitignored and never
committed, so the published artifacts are anonymous by construction rather
than by discipline.
