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

## Open item — the pass threshold

**Not yet located.** The guidance document states that a project is required
for certification and that three peer reviews must be completed, but names no
minimum score.

Since 2026-08-09 the adoption check no longer blocks on this: gate G2 in
`docs/objective.md` runs over a stated plausible threshold band anchored on
candidate v0's own verdicts, and collapses to a point if the real number is
obtained (decision `g2-anchored-on-construction`). Still worth locating —
places to look: the cohort dashboard above, the course leaderboard, the
certificate guide in the repository README, or the course Slack. If no
numeric threshold exists at all, record that: it is a finding worth having.

## Not sources

- **The owner's three past peer reviews.** Held out. They never enter the
  loop; see the epistemics section of `CLAUDE.md`.
- **`repos.yaml`.** Gitignored, and the only file mapping a project id to a
  named person.