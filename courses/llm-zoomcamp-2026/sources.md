# Sources — LLM Zoomcamp 2026

Where every input in this directory came from, and what each one is for.
Per-course by design: pointing this project at a different zoomcamp means
rewriting this file and the three beside it, and nothing else.

Captured 2026-08-09 against `DataTalksClub/llm-zoomcamp` at commit
`bc7b6aad6b92a5611d3d37bf7521a363f3b9d398`. Re-pin with:

```sh
git ls-remote https://github.com/DataTalksClub/llm-zoomcamp.git refs/heads/main
```

---

## The instrument under study

**`project-evaluation-guidance.md`** — a verbatim copy of
<https://github.com/DataTalksClub/llm-zoomcamp/blob/main/project.md>.

The whole file, not only the scoring criteria. Its surrounding prose changes
what a reviewer may fairly expect and what an author is told to produce: the
documentation recommendations, the review tips that tell reviewers to clone
at a commit hash, the datasets ruled out, the plagiarism policy. Read as part
of the instrument.

`project-evaluation-issues.md` is the diagnosis of this document and is
pinned to the version above. If the course edits `project.md`, re-capture
both and note what moved.

## The curriculum

**<https://github.com/DataTalksClub/llm-zoomcamp>** — ten weeks covering
retrieval-augmented generation, vector and hybrid search, embeddings, agents
and function calling, evaluation, monitoring, and reranking.

This bounds what the criteria may fairly ask for: a criterion the course
never taught is not scoreable. Note the bound is on *criteria*, not on
technology — the guidance explicitly permits tools outside the curriculum
provided the author explains them.

## The course's own model project

**<https://github.com/DataTalksClub/llm-zoomcamp/tree/main/07-project-example>**

The worked example the course itself holds up as what a good submission looks
like. This is the closest thing available to an authored statement of what
the criteria are *meant* to reward, and it is usable as a sanity check:
**candidate criteria that score the course's own exemplar poorly are
suspect**, and if a candidate does score it poorly, that is a finding to
examine rather than an error to correct away.

## Earlier cohorts

Previous versions live under `cohorts/<year>/project.md` in the same
repository. Useful for one thing only: seeing how the criteria have drifted
between cohorts, which indicates how much change the organisers actually
absorb in practice — and therefore how large a revision is realistic to
propose.

## Structural reference, not a template

**<https://github.com/nima-siboni/llm-heuristic-scientists-workshop>** — a
looping-agent scaffold for heuristic discovery.

Borrowed for shape, not method. Its loop works because it has a cheap
deterministic non-LLM objective, a fixed executable candidate signature, free
evaluation, and a held-out scenario. This project does not have all four, and
`docs/plan.md` is required to state which ones it has and which it does not.
Do not import its optimisation framing by assumption.

## Cohort surface

**<https://courses.datatalks.club/llm-zoomcamp-2026/>** — deadlines,
leaderboard, dashboard, and the submission and review forms.

Certification requires a submitted project plus three completed peer reviews;
certificates are issued once all reviews are in. Self-paced learners are not
eligible for certification.

## How a grade is formed — three reviewers, median

**<https://datatalks.club/faq/llm-zoomcamp.html>**, question "How is my
capstone project going to be evaluated?" (source: `DataTalksClub/faq`,
`_questions/llm-zoomcamp/project/004_9a2e2d2008_*.md`, read 2026-08-10 at
commit `59364d77277ef74e8ad33f354da4416efa57f6a3`):

> Each submitted project will be evaluated by three randomly assigned
> students who have also submitted the project. […] The final grade you
> receive will be the median score of the grades from the peer reviewers.

Load-bearing for gate G4 in `docs/objective.md`: the instrument already
aggregates three independent human reviewers by **median**, not mean, so a
single reviewer's inconsistency cannot move a grade at all. This is the
owner's stated reason for leaning toward demoting G4 to a reported metric.
Its limit is equally structural — a median defends against dispersed
disagreement, not against a criterion that is ambiguous in the same
direction for all three readers.

## The pass threshold — 11 points

**Located 2026-08-10.** The pass threshold for this cohort is **11 points**,
confirmed by the owner from the enrolled cohort dashboard
(<https://courses.datatalks.club/llm-zoomcamp-2026/dashboard>, under
"Project outcomes → score to pass"). The page is login-gated: agents cannot
re-verify it, and re-confirmation for a new cohort is an owner task.

The mechanism is public even though the number is not: the course platform
(<https://github.com/DataTalksClub/course-management-platform>) enforces a
per-course `project_passing_score` (`courses/models/course.py`), refuses to
score a project while it is 0, and computes each submission's `passed` flag
against it. Searched and *not* stating the number, for the record:
`project.md` (current and earlier cohorts), the DataTalksClub FAQ repo, the
docs site (`datatalks.club/docs`), and the public cohort pages. The
threshold anchors baseline findings only; gate G2 in `docs/objective.md` is
an absolute rate floor and does not depend on it (decision
`pass-threshold-11`).

## Not sources

- **The owner's three past peer reviews.** Held out. They never enter the
  loop; see the epistemics section of `CLAUDE.md`.
- **`repos.yaml`.** Gitignored, and the only file mapping a project id to a
  named person.