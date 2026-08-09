# CLAUDE.md — heuristic-discovery-peer-review

## What this project is

A loop of agents that discovers better evaluation criteria for DataTalksClub
zoomcamp capstone projects, and produces the evidence needed to argue for
them.

**The deliverable is one document**: a complete revised
`project-evaluation-guidance.md`, holding the scoring criteria and the
reviewer guidance around them together, in a form that could replace the
course's current one. They ship as a single document because a fix can
otherwise land in the gap between them — several defects in the current
criteria are best repaired by changing what reviewers are told to do rather
than by changing the point scale.

Everything else the loop produces — attacks found against a candidate,
candidate scores, run logs — is working evidence. It lives in
`docs/findings.md` and `runs/`, and the deliverable cites it where it
justifies a change. It is not shipped alongside.

The starting diagnosis is `courses/<slug>/project-evaluation-issues.md`. It is an input,
not a conclusion: if the loop finds the diagnosis wrong, that is a result and
gets recorded, not suppressed.

## The epistemics — these are not negotiable

This project has **no labelled corpus of graded projects and will not get
one.** Everything below follows from that.

- **Validity comes from known-direction pairs, not from human grades.** A
  test case is a project record and a twin of it that differs in exactly one
  way whose direction is known *because it was constructed that way*. A
  candidate that scores the degraded twin equal or higher has failed.
  Nobody grades anything; the sign of the difference is known by
  construction.
- **Reviewer agreement is a floor, never a target.** Criteria awarding every
  project the same score have perfect agreement. Any objective that maximises
  agreement will rediscover checkbox counting. Agreement is a constraint to
  clear alongside a term that punishes a flat scale.
- **The owner's own past reviews never enter the loop.** They are one
  person's taste, three data points. Do not train, tune, or prompt against
  them. Two of the reviewed repos sit in the corpus flagged
  `owner_reviewed`, and their only use is validating that the *extraction
  step* recovers what a careful human reader found — never for judging a
  candidate. The verdicts themselves stay out.
- **The end-of-project consistency check is weak, deliberately.** It runs
  over repos that were read throughout development, so it cannot be a clean
  held-out test. Treat it as a sanity check on the final candidate and say so
  in the writeup; do not report it as evidence.
- **Agents may not edit what judges them.** Test cases, the constraint list
  and the stopping criterion are read-only to every agent in the loop, as is
  any case set sealed as held-out. A loop that can edit its own scorer will.
- **Twins must encode structural facts, not taste.** "A component was added
  whose own reported numbers show it hurts" is structural. "This README is
  badly written" is taste. If a proposed twin cannot be stated as a checkable
  structural difference, it does not go in the case set.

## Out of scope

The guidance document contains more than the scoring criteria, and not all of
it is this project's business. Do not propose changes to:

- **the peer-review reward structure** — how many points a reviewer earns for
  reviewing, and how that is awarded. It is noticeably weak, it is not ours,
  and a proposal that reaches into it will not be adopted.
- the plagiarism policy, the two-attempt structure, or certificate mechanics
- the course curriculum itself

In scope: the scoring criteria, and the guidance that shapes how a review is
conducted and how a project is documented for review.

If an agent finds a defect in an out-of-scope area, it records it as an
observation in `docs/decisions.md` and moves on. It does not design against
it.

## Whose interests this has to serve

The criteria are not only a measuring instrument. They belong to a free
community course whose organisers need people to finish it, and any proposal that
ignores that is rejected on contact whatever its technical merit.

What DataTalksClub and the course tutor need:

- **Certification stays achievable.** A revision that fails people who pass
  under the current criteria is dead. Learners are unpaid volunteers doing this
  around jobs; a course that becomes discouraging loses them.
- **Reviewer workload does not rise.** Reviews are unpaid. Criteria that
  cost more time per project will be applied carelessly, which makes them
  worse than the ones they replaced.
- **Few disputes.** Every criterion requiring judgment generates appeals, and
  appeals land on the organisers.
- **Incremental adoption.** A wholesale replacement mid-cohort is not
  adoptable. Scores should stay roughly comparable with previous cohorts.
- **Nothing requiring paid access** from reviewers.

**Difficulty and discrimination are different axes, and only the second one
is the goal here.** The aim is not stricter criteria; it is criteria whose
scores carry information — the same people certified, but their scores
meaning something above the pass line, where today they cluster.

This converges with the dead-floor problem rather than fighting it. Turning
admission-style criteria into explicit certification gates is exactly what a
course wants: a clear, generous, unambiguous floor that says *you built a
working end-to-end system*. The graded portion above it is then free to carry
real information without threatening anyone's certificate.

**Measured, not asserted.** Score every `role: corpus` repo in
`courses/<slug>/repos.yaml` under the current criteria and under each
candidate. `role: self` is excluded from anything measuring how scores
distribute. The invariant is the *set of projects that clear certification*,
not the raw number of points — if the scale changes, the threshold is
recalibrated with it, and the set must not shrink. Estimated review time per
project must not rise either. A candidate failing these is discarded however
well it scores on everything else.

## Cost model — read before designing anything

There is **no Anthropic API key.** Claude runs only inside Claude Code
sessions on a subscription. Programmatic inference comes from two free tiers:
Google's Gemini API (`GEMINI_API_KEY`) and Hugging Face Inference Providers
(`HF_TOKEN`).

| role | volume | runs on |
|---|---|---|
| planning, architecture, criticism | low, high judgment | Claude Code |
| proposing and revising criteria | low | Claude Code |
| evidence extraction from real repos | one-off per repo | Claude Code |
| reviewer agents scoring cases | high | Gemini free tier (Flash class) |
| second-family reviewer, for agreement | low, deliberate | HF Inference Providers |
| twin generation and mutation | high | plain Python where possible |

**Heterogeneous reviewer models are the point, not a compromise.** Agreement
across model families is far stronger evidence of objectivity than agreement
across temperatures of one model. But the second family is expensive relative
to its quota, so spend it only where cross-family agreement is the actual
measurement.

**The binding constraint is requests per day, not money.** Gemini's free tier
runs to roughly a thousand-odd requests a day at something like 10–15 per
minute for the Flash-class models, and those figures move — check Google's
rate-limit page rather than trusting this paragraph. HF's free tier is
credit-denominated and very small (well under a dollar a month), which is why
it is not the workhorse here.

What follows from that:

- **The cache is structural, not an optimisation.** Every model call is
  cached, keyed by a hash of its inputs. A re-run must cost zero requests for
  anything already seen, or iteration stops being possible.
- **The runner accounts for requests and stops cleanly.** A pass that dies
  two-thirds through on a rate-limit error has spent the day's quota for
  nothing. Budget before starting, and checkpoint so a partial pass resumes.
- **Throttle deliberately; no unbounded parallelism.** At ~15 requests a
  minute, firing a case set concurrently fails immediately. Exponential
  backoff with jitter on 429, never immediate retry.
- **More API keys do not buy more quota** — limits are per project, not per
  key. Do not design around key rotation.
- **Model availability changes on both providers.** The client needs a
  fallback list and must fail loudly rather than silently switching models
  mid-run: a run where half the reviews came from a different model is not a
  measurement.
- **Free-tier prompts may be used to improve the providers' models.** The
  content here derives from public repositories and the id-to-person mapping
  never enters a prompt, so exposure is low — but this is a decision on the
  record, not an oversight.

## Layout

```
courses/<slug>/          per-course inputs — this is the generalisation seam
  project-evaluation-guidance.md   the course's full project brief, verbatim:
                                   objective, documentation guidance, review
                                   tips, scoring criteria, plagiarism rules
  project-evaluation-issues.md     the diagnosis
  sources.md             curriculum repo, reference links
  repos.yaml             real capstone repos, pinned by commit, with roles
                         (`corpus`, `self`) and the `owner_reviewed` flag.
                         **Gitignored** — the only place a project id maps to
                         a person. `repos.example.yaml` documents the shape.
cases/
  schema.md              the evidence-record schema
  records/               one record per real repo, extracted once
  twins/                 mutations, each with its known direction stated
agents/                  component prompts the loop runs, versioned, one
                         directory per role — these are code, not instructions
                         to me
tasks/                   the prompts I write to steer agents, numbered
                         (01-planning.md, 02-…), immutable once run
loop/                    the runner, the cache, the HF client
runs/                    append-only run logs and manifests
docs/
  proposed-guidance.md   THE DELIVERABLE — a complete replacement for the
                         course's project-evaluation-guidance.md: revised
                         scoring criteria plus the reviewer guidance around
                         them
  plan.md                the current plan
  objective.md           what "better" means, and how it is measured
  decisions.md           live — current decisions about this lab, by slug
  superseded.md          log — decisions that were reversed, with their
                         original reasoning
  findings.md            log — what the loop discovered about the criteria
                         under study, each entry naming the run behind it
```

Keep `agents/` and `tasks/` strictly apart. An agent prompt is an
experimental variable whose exact text has to be recoverable for any result
to mean anything; a task prompt is a one-shot instruction and part of the
project's history. Merging them loses both.

Nothing course-specific lives outside `courses/<slug>/`. Adding a second
zoomcamp must require no change to `loop/`, `agents/`, or `cases/schema.md`.

## Working conventions

- **Report before write.** For anything beyond a single-file edit, state what
  will change and wait. Phased work stops at each phase boundary.
- **Verify, don't guess.** Fetch the workshop repo and the course repo rather
  than recalling them. Model names, HF endpoints, and the course's own
  guidance text all change.
- **Every document is either live or a log, and says which.**
  *Live* documents are rewritten in place, describe only what is true now,
  and have a length budget: `proposed-guidance.md`, `plan.md`,
  `objective.md`, `decisions.md`. *Logs* are append-only and nobody reads them
  linearly: `superseded.md`, `findings.md`, `runs/`, `tasks/`. A document
  doing both jobs at once becomes unreadable, which is the failure this rule
  exists to prevent.
- **Decisions are live, not append-only.** `docs/decisions.md` holds one
  short block per *current* decision — what was decided, why, what was
  rejected — identified by slug, grouped by topic, no numbering. Reversing a
  decision means **rewriting the entry in place** to state the new position
  and adding one line: `Supersedes: <slug>, see superseded.md`. The old entry
  with its full original reasoning moves to `docs/superseded.md`. Nothing is
  lost and the live file does not grow from reversals.
- **Length budget: five lines per decision entry.** Anything needing more
  than that is a document, and the entry links to it. Caps are what keep a
  file readable; conventions without caps drift.
- **Decisions and findings are separate.** `decisions.md` is about how this
  lab is built. `findings.md` is what the lab learned about the evaluation
  criteria under study — the actual product — and every entry names the run
  that produced it.
- **Task prompts are immutable once run.** Amend by appending a dated
  section, never by editing what was already executed. This rule applies to
  `tasks/` only, where files are short and run once. It is deliberately *not*
  applied to the live documents above.
- **Counts are recomputed, never carried forward.** Case counts, attack
  counts, and pass rates are re-derived from artifacts after every run.
- **Nothing that names a person is committed.** `repos.yaml` and every cloned
  repository are gitignored. Records, findings, run logs and the deliverable
  refer to projects only as `p01`, `p02`… Anonymity here is structural, not a
  habit to remember: without the mapping there is nothing to leak. Never
  `git add -A` without checking what that would sweep in.
- **Claims are traceable.** Any number in `docs/` names the artifact it came
  from. Prose summaries are not evidence — the project is an argument about
  evidentiary standards and cannot fail its own test.
- Python 3.12, `uv`, pinned versions. Local Ubuntu.

## Definition of done for a discovery run

A run is complete when the red-team agent, given the current candidate,
cannot find a new way to score well while being structurally bad — and that
claim is backed by the attacks it *did* try, logged, including the failures.
Diminishing returns is a result to record, not a reason to stop quietly.