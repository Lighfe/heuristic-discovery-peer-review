# Where the capstone peer-review rubric breaks

The LLM Zoomcamp capstone is graded by fellow students against a twenty-point
checklist: ten criteria scored 0–2, three technique points, and up to five
bonus points. Reviewers are unpaid volunteers working to a time limit, sometimes
on projects written in a language they do not read or about a subject they do
not know.

This document sets out four structural problems with that checklist. It is a
diagnosis and proposes no replacement. The scenarios used to illustrate each
problem are hypothetical; they are chosen to make a failure mode visible, not
to describe any particular submission.

The rubric also does several things well, and the constraints it satisfies
are real. Those are set out at the end, because any revision that ignores
them will not survive contact with an actual review cycle.

---

## 1. The bottom of the scale is unreachable

Several criteria define a zero tier that no submitted project can occupy.

| criterion | zero tier | who can score it |
|---|---|---|
| Retrieval flow | no knowledge base or LLM is used | nobody who submitted a RAG project |
| Interface | no way to interact with the application at all | nobody who submitted anything runnable |
| Ingestion pipeline | no ingestion | nobody with a populated index |
| Problem description | the problem is not described | nobody who wrote a README |

Retrieval flow is the sharpest case, because its one-point tier — a knowledge
base absent and the LLM queried directly — is equally unreachable. A project
that is a RAG project at all takes both points, and the criterion has no
capacity to say whether the retrieval is any good. Two of twenty points are
settled by the submission being on-topic.

The underlying error is applying one ladder to two different questions. Some
criteria ask *does this qualify as a RAG project* — an admission check, and
genuinely binary. Others ask *how well was this done* — genuinely graded.
Giving both the same 0/1/2 shape spends scale on the first kind that the
second kind needs, and compresses the range in which careful work can
distinguish itself from adequate work.

These four criteria are worth eight points in total, two each. A project that
is merely on topic — with no evaluation of any kind, no monitoring, no
containers and no usable instructions — already collects five of them:

| criterion | maximum | automatic |
|---|---|---|
| Retrieval flow | 2 | 2 |
| Problem description | 2 | 1 |
| Interface | 2 | 1 |
| Ingestion pipeline | 2 | 1 |
| **total** | **8** | **5** |

The scale therefore starts at 5 out of 20 rather than at 0, and only three of
these eight points can be earned by doing the work well.

---

## 2. Components are scored for being present, not for what they did

The three technique points read as a feature list:

> Hybrid search: combining both text and vector search (at least evaluating
> it) (1 point) · Document re-ranking (1 point) · User query rewriting (1 point)

Only hybrid search mentions evaluation. Reranking and query rewriting are
stated as things done.

Consider a system over a board-game rules corpus that adds an LLM query
rewriter. On the project's own numbers the rewriter lowers retrieval quality —
it expands abbreviations into wordings the rules text never uses — and it
adds an API call to every query. It ships enabled, is described in the README
as an improvement, and earns the point. The rubric cannot separate that from
a rewriter that helps, because it never asks what the component did to the
system.

Removing a component after measuring it is permitted, and a reviewer who
reads carefully will credit a documented removal. The problem is that the two
paths carry very different risk for the author:

- **Implement and keep it.** The point is visible in the file tree. Credit is
  near-certain and requires no one to read anything.
- **Implement, measure, remove it.** Credit depends on the reviewer finding
  the evaluation, understanding it, and deciding it counts. Nothing in the
  rubric tells them to.

Shipping a component that hurts the system is therefore the safer bet, even
though the rubric permits the alternative. Authors respond to that gradient,
and it runs directly against what a course on evaluation is trying to teach.

Monitoring has a milder version of the same shape. The two-point tier asks
for feedback collection and at least five charts. Five charts nobody would
consult score identically to five that would surface a real regression, and
collected feedback scores whether it is ever looked at or not. Counting
panels is checkable, which is why it is written that way, but what it
measures is that a dashboard exists.

The second-order effect of all this is that the rubric quietly teaches that a
RAG system is a list of components. The skill actually worth certifying is
closer to the opposite: knowing which components a given corpus needs, and
being able to show it. The weighting reinforces the lesson — the three
technique points are obtainable in an afternoon, and together they are worth
more than either evaluation criterion.

---

## 3. "Evaluation" has no validity floor

Both evaluation criteria count approaches rather than asking whether any
approach measured the right quantity:

> 1 point: only one retrieval approach is evaluated
> 2 points: multiple retrieval approaches are evaluated, and the best one is used

Nothing constrains what the evaluation is worth. Full marks are available for
a measurement that cannot support a conclusion. Four ways that happens:

- **Circularity.** An LLM writes the questions, and an LLM decides whether
  the passage that came back is a good answer. Nothing outside the system
  ever states what the right answer was. Both techniques are fine in
  themselves: generating a question from one specific passage means the
  correct answer is known in advance, and a model judge is usable once a
  sample of its verdicts has been checked by hand and its error rate is
  known. What breaks the evaluation is doing neither. The system is then
  marked by the same machinery that built it, and it cannot score badly.
- **A sample too small for the decisions taken on it.** Half a dozen
  configuration choices are settled from one small question set with no
  statement of uncertainty. Several of those choices are noise, and nothing
  in the write-up distinguishes which.
- **The measured system is not the shipped system.** Retrieval depth,
  reranking cut-off or model version differ between the evaluation script and
  the application, so the reported numbers describe a configuration nobody
  can run.
- **A test almost nothing can fail.** Correctness is defined loosely enough
  that nearly every retrieval counts as a hit — scoring a result correct when
  it merely comes from the right document, say, in a corpus where a handful
  of long documents supply most of the passages. Every configuration scores
  highly, so comparing configurations reveals nothing.

In each case multiple approaches were compared and the better one shipped, so
each scores two points.

The important consequence is that a broken evaluation is not merely a weaker
evaluation. It is worse than none, because its output is a number, and a
number in a README does work: it justifies keeping a component that degrades
the system, it settles configuration choices, and it tells the next reader
that the question has been answered. An unevaluated project leaves its
choices visibly unjustified. A badly evaluated one launders them.

These two criteria are also the most informative in the document — how
someone evaluates their own system says more about their competence than any
other line — and they are capped at two points each, the same as the
retrieval-flow criterion every submission takes automatically.

---

## 4. Nothing scores whether the documentation is true

Reproducibility is the closest criterion, at two points, and it asks a
narrower question than it first appears: are the instructions clear, is the
data accessible, does the code run, are versions pinned. A project can pass
all four while describing a system meaningfully different from the one in the
repository.

Claims that map onto a checkable artifact do get caught in practice. If a
README announces a cloud deployment, a reviewer looks for the deployment
code. If it announces an evaluation and there is no evaluation script, the
criterion scores zero whatever the prose says. That part works.

The gap is the band of claims that are plausible, partially supported, and
expensive to falsify:

- a described behaviour the implementation approximates but does not
  actually have, such as a fallback that silently changes retrieval mode
- headline numbers stated in prose with no committed artifact behind them
- figures that disagree between the README, the notebooks and the report
- a limitations section that lists cosmetic issues and omits the known
  structural ones

None of these is scoreable anywhere. And documentation is now the cheapest
artifact in a project to produce at length, which makes an unscored dimension
an increasingly load-bearing one — particularly for a capstone that doubles
as a portfolio piece, where the accuracy of the write-up is a large part of
what a reader is actually evaluating.

---

## Constraints any revision has to respect

These are the reasons the rubric looks the way it does. Several of the
problems above are the price of requirements that are not negotiable.

**Objectivity.** Volunteer reviewers must reach a defensible score without
arguing taste. Low variance between reviewers matters more here than
precision, and every criterion that requires judgment widens the spread of
scores a given project might receive.

**Curriculum alignment.** Points map onto course modules. Scoring something
the course never taught is unfair.

**Time and money.** Reviews are unpaid and time-boxed. Some projects need a
paid API key the reviewer supplies themselves. Any criterion that demands
extended hands-on testing will not be applied consistently.

**Whether the system can be run at all.** Some projects stand up in ten
minutes; others need a large model download, unavailable hardware, or
credentials the reviewer does not have. When a project cannot be run, the
review silently becomes a review of its documentation — a different
instrument, undeclared, and two projects scoring the same may have been
examined in entirely different ways.

**Domain opacity, which is a hard limit rather than a gap to be closed.**
Judging whether an evaluation question set is *good* — questions a real user
would plausibly ask, answerable from the corpus, not a restatement of the
passage they were generated from — requires knowing the subject matter.
Reviewers frequently do not, and authors routinely cannot assess their own
generated questions without going back to the source material.

What remains checkable without domain knowledge is procedural rather than
semantic: whether the evaluation set is committed and inspectable at a stated
size, whether the decision rule was fixed before the measurement or chosen
after seeing it, whether the configuration measured matches the one that
ships, whether each headline number is traceable to a committed artifact, and
whether any statement of uncertainty accompanies a claimed improvement.

The consequence for design is unavoidable: a reviewer cannot be asked to
certify that the evidence is sound, only that evidence exists, is
inspectable, and is internally consistent. Anything depending on semantic
quality has to be shifted onto the author to make visible, with the reviewer
scoring whether that account was given and whether it contradicts the
artifacts — not whether it is correct. That is weaker than judging quality
directly, and it is the strongest thing available under these constraints.

---

## What a revision has to work out

These are the parts that cannot be settled by argument and have to be worked
through against real submissions.

1. **How to recover the dead range.** Restating admission-style criteria as
   binary prerequisites is one route, and it has a trap: dropping the
   interface criterion out of the score would also drop the real distinction
   between a command-line script and a working UI, which is worth crediting.
   Re-cutting the tiers so that all three are reachable is a second route,
   and there are likely others. Both directions need trying before either is
   preferred.
2. **What the total should be.** It does not have to stay at twenty, but it
   should stay in that neighbourhood — a hundred-point scale implies a
   precision no volunteer review can deliver, and invites arguments over
   single points. The question is what total lets the working range use most
   of the nominal one without inflating apparent precision.
3. **How to score the accuracy of documentation additively.** The mechanism
   has to award points for claims that hold up, not remove them for claims
   that do not, and it has to stay inside what a reviewer can check without
   domain knowledge.
4. **Where each fix belongs.** Some of this needs a change to the rubric.
   Some of it is guidance a reviewer could adopt tomorrow without anyone's
   approval, which makes it testable far sooner. Sorting the list by which
   is which comes before designing either.
5. **What evidence a reviewer records.** Any criterion scored below full
   marks needs a trace of why, both so the author can act on it and so the
   places where the rubric is being stretched become visible rather than
   staying private to each reviewer. What that costs in time is the
   constraint to measure.