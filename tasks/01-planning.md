# First prompt — Fable 5, planning mode

Save as `tasks/01-planning.md` and paste as the opening message of a
planning-mode session, with `CLAUDE.md`,
`courses/llm-zoomcamp-2026/project-evaluation-guidance.md`,
`courses/llm-zoomcamp-2026/project-evaluation-issues.md` and
`courses/llm-zoomcamp-2026/repos.yaml` already present.

Once run, this file is not edited — amendments append as dated sections.

---

You are planning a project from scratch. Read `CLAUDE.md` first — its
"epistemics" section constrains every design choice below and is not open for
relaxation.

## Goal

Design a loop of agents that discovers better evaluation criteria for
DataTalksClub zoomcamp capstone projects.

The deliverable is a single document: a complete revised
`project-evaluation-guidance.md` — the scoring criteria and the reviewer
guidance around them together, in a form that could replace the course's
current one. Some defects in the current criteria are best repaired by
changing what reviewers are told to do rather than the point scale, which is
why the two ship as one document. Everything else the loop produces is
working evidence in `docs/findings.md` and `runs/`, cited by the deliverable
where it justifies a change.

## Read before designing

- `courses/llm-zoomcamp-2026/project-evaluation-guidance.md` — the course's
  whole project brief, not only the scoring criteria. The surrounding prose
  changes what a reviewer may fairly expect and what an author is told to
  produce, so read it as part of the instrument
- `courses/llm-zoomcamp-2026/project-evaluation-issues.md` — the diagnosis this project
  starts from, four structural problems plus the constraints any revision has
  to respect
- `courses/llm-zoomcamp-2026/repos.yaml` — real past capstone repos
- Fetch `https://github.com/nima-siboni/llm-heuristic-scientists-workshop` —
  a loose structural reference only. Its loop works because it has a cheap
  deterministic non-LLM objective, a fixed executable candidate signature,
  free evaluation, and a held-out scenario. Identify which of those four this
  project can have and which it cannot, and say so explicitly. Do not import
  its optimisation framing by default; a judge-and-critique loop may fit
  better. Justify whichever you pick.
- Fetch `https://github.com/DataTalksClub/llm-zoomcamp` — the curriculum
  bounds what the criteria may fairly ask for. A criterion the course never
  taught is not scoreable. Note that the guidance explicitly permits tools
  beyond the curriculum, so the bound is on criteria, not on technology.

## Hard constraints

- No Anthropic API key. Claude runs only inside Claude Code sessions.
  Programmatic inference comes from two free tiers: Gemini (`GEMINI_API_KEY`)
  as the volume workhorse and Hugging Face (`HF_TOKEN`) as a second model
  family used sparingly for the agreement measurement. Design the role split
  around this; see the cost model in `CLAUDE.md`.
- **The scarce resource is requests per day, not dollars.** Verify the
  current free-tier limits for both providers rather than trusting any
  figure written down here, then size the loop against them: state how many
  requests one pass costs, and what happens when a pass exceeds the day's
  budget.
- No labelled corpus of graded projects, now or later.
- Eleven real repos are pinned by commit in `repos.yaml`: ten peer capstones
  (`role: corpus`) and the owner's own (`role: self`, excluded from anything
  measuring score distribution). They are read, never executed. Extraction is
  one-off and cached.
- **The corpus contains no thin or near-threshold project.** The adoption
  check therefore cannot yet be tested where it matters most — around the
  pass line. Either propose how to close that gap, or state plainly what the
  check does not cover until it is closed.
- Reviewer effort is the binding constraint on anything this produces:
  roughly two to three hours per review, unpaid, sometimes on a project in a
  language or field the reviewer does not know.
- **The result has to be adoptable by the people who own the course.** Read
  the "Whose interests this has to serve" section of `CLAUDE.md` and treat it
  as binding. The goal is not harder criteria — it is criteria whose scores
  discriminate. Certification must stay as achievable as it is today, review
  time must not rise, and the change must be incremental enough to adopt
  between cohorts.

## What the plan must decide, with reasoning

1. **What a candidate is.** An executable scoring function over structured
   evidence, prose criteria an agent applies, or two layers with a mapping
   between them. Decide. The question turns on whether extraction from a repo
   can be cleanly separated from scoring it — separating them makes
   evaluation free and deterministic, at the cost of testing the criteria
   against an abstraction of a project rather than a project. Name what that
   abstraction would hide.
2. **The evidence schema, v0.** Derived from the real repos, not invented.
   Every field must be answerable by a reviewer who does not know the domain.
3. **The twin catalogue.** What structural mutations exist, what direction
   each implies, and how to keep them from encoding one person's taste. Cover
   at least: a component whose own numbers show it hurts, a claim with no
   artifact, measured config differing from shipped config, an evaluation
   whose correctness criterion almost nothing can fail, a project that is
   hard to locate inside its own repository, and a mutation whose
   correct direction is *no change* — criteria that move on noise are as
   broken as criteria that ignore signal.
4. **The loop protocol.** Which agents, what each sees, what it may write,
   and how reviewer agents are kept genuinely independent.
5. **How the degenerate optimum is detected.** Criteria that score every
   project identically satisfy agreement perfectly. State the measurement that
   catches this and where it sits in the objective.
6. **The stopping criterion**, and what evidence backs the claim that the
   red-teamer found nothing new.
7. **How passability is preserved while discrimination increases.** These are
   separate axes and the plan must treat them separately. Define the
   adoption check — scoring the `role: corpus` repos under the current and
   candidate criteria, recalibrating the threshold if the scale changes, and
   requiring
   that the set of projects clearing certification does not shrink — and say
   where in the loop it runs. A candidate that gains discrimination by
   failing more people has not solved the problem.
8. **Milestone 1**: the smallest slice that runs end to end — one real repo
   extracted, a handful of twins, one candidate, one loop pass — and what it
   would prove.

## Stop and ask me about these, and only these

- the objective: what "better" means and how the terms are weighted
- the evidence schema, before cases are built on it
- sealing any case set as held-out, before it is sealed
- any proposal to relax a rule in the `CLAUDE.md` epistemics section
- any design that would need my three past peer reviews as loop input

Everything else, decide yourself and record it as a decision entry.

## Challenge the framing

If the diagnosis in `project-evaluation-issues.md` is wrong somewhere, or
the twin-based approach cannot carry the weight I am putting on it, say so
now rather than building around it. Tell me you are pushing back and why. A plan that quietly
routes around a flaw it noticed is worse than one that stops.

## Deliverables for this session

- `docs/plan.md`
- `docs/objective.md`, draft, marked as needing my approval
- an outline of `docs/proposed-guidance.md` — section headings and what each
  will contain — so the shape of the deliverable is agreed before any of it
  is written. Not the document itself; this session produces no criteria.
- `docs/decisions.md`, covering every decision above and every option you
  rejected with the reason. Follow the live/log rules in `CLAUDE.md`: slugs
  rather than numbers, five lines per entry, grouped by topic. Observations
  about out-of-scope parts of the guidance document go here too, as
  observations.
- `tasks/02-<slug>.md` — the prompt that starts implementation, written for
  an agent that has not seen this session. It should be readable standing
  alone: what to build, in what order, where it must stop and ask, and what
  "done" means for milestone 1. Follow the conventions in `CLAUDE.md` for
  what belongs in `tasks/` versus `agents/`.
- a list of everything you need from me before implementation starts

Write no implementation code in this session.