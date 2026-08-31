# heuristic-discovery-peer-review

An agentic loop that discovers better evaluation criteria for
DataTalksClub zoomcamp capstone projects — and produces the evidence
needed to argue for them, without any labelled/graded corpus to train or
check against.

The deliverable is a single revised guidance document: scoring criteria
plus the reviewer guidance around them, structured so it could replace the
course's current brief outright.

## Approach

**No graded projects exist, so validity has to come from construction, not
comparison.** Each real capstone repo is extracted once into a structured
evidence record. From every record, a "twin" is derived by mutating exactly
one structural fact in a known direction — e.g. taking a component whose
own reported numbers show it hurts, and shipping it enabled. Nobody grades
anything; the twin's correct ranking relative to its original is known
because it was built that way.

A candidate scoring function is judged against that twin set, not against
a rubric:

1. **Propose** — an agent drafts a deterministic scoring function over the
   extracted evidence fields.
2. **Gate** — it must rank every twin pair correctly, hold a certification
   rate no worse than the current criteria, and stay under a reviewer-time
   budget. Any gate failure discards the candidate outright, no matter how
   well it ranks.
3. **Rank** — gate-passing candidates are compared on how much they
   discriminate between real projects and how well they resist attack.
4. **Red-team** — a separate agent tries to construct new records that
   score well while being structurally bad, to break the current best
   candidate.

Discovery stops once a candidate clears every gate and survives repeated
red-teaming with no new successful attack.

Two other pieces worth knowing:

- **LLM-as-judge is used for validation, not scoring.** The score itself
  comes from a deterministic function over structured fields. Separate
  reviewer agents — drawn from more than one model family, to avoid a
  single family's blind spots — are used only to check that the
  deterministic score agrees with what an LLM applying the *prose*
  criteria would conclude.
- **Every call is cached by input hash.** The loop runs against
  quota-constrained free-tier APIs, so a re-run must cost zero new
  requests for anything already seen.

## Layout

```
courses/<slug>/     course-specific inputs (the current guidance, source repos)
cases/              evidence records extracted from real repos, and their twins
agents/             versioned prompts for each agent role
loop/               the runner, cache, and model clients
runs/               logged output of every run
docs/               objective, plan, and the deliverable itself
```

`docs/objective.md` defines the gates and ranking terms in full;
`docs/plan.md` lays out the loop's shape and agent roles; `CLAUDE.md`
states the project's hard constraints.

## Stack

Python 3.12, `uv`. Gemini and Hugging Face Inference Providers as the two
model families (no Anthropic API key — Claude runs only as the coding
agent building this).

## Credits

The propose → measure → red-team → critique loop shape and the
executable-candidate pattern are adapted from
[nima-siboni/llm-heuristic-scientists-workshop](https://github.com/nima-siboni/llm-heuristic-scientists-workshop).

The criteria under study belong to
[DataTalksClub/llm-zoomcamp](https://github.com/DataTalksClub/llm-zoomcamp).
