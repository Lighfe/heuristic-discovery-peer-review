# M2 step 8 — sealing checklist

Working document for you to read, annotate, and clear before step 8
(sealing). Not a task artifact in the `tasks/` sense — this is scratch
material for this review, and can be deleted once step 8's sign-off is
recorded in `decisions.md`.

**Two items the last reviewer feedback named as open are already done.**
Checked directly before writing this: `cases/twins/p01-t07.yaml`
(cosmetic-rename) and `cases/twins/p02-t01.yaml` (the conditional-twin
family's idea 4, built on p02) both exist, are in the twin catalogue, and
passed the scorer/test-suite checks when built. They are **not** on this
list. Said here so the correction is on the record, not just in chat.

For each item below: a checkbox for you to mark, a short "what to check"
pointer (file + line/decision slug), and a note on what "clearing" it
means. Leave a comment inline if you want something changed rather than
just checked.

**Status after working through every annotation (2026-08-19):** every
item is closed. A1, A2, B1, B2, B7, B9 resolved by doing exactly what
was asked. B5, B8 were open questions answered with information and an
owner decision. A3/C2 closed by owner decision, sealed as a named
two-layer risk rather than held (see A3 below for the full breakdown).
B3, B4, B6 were already `[x]` before this pass with no action requested
— each now carries an explicit status note so "already resolved" is
stated, not implied by a bare checkbox (B3 additionally got one more
check this pass: transcript persistence, confirmed non-issue, see B3).
`cases/schema.md`'s header updated to match. Nothing has been committed
and step 9 has not started, per your standing instruction.

---

## Section A — items that could change a score or a gate if left unresolved

These touch fields the twin catalogue or a future candidate could read.
Worth a decision before sealing, because a schema change is free now and
costs a full re-extraction after.

- [x] **A1. `retrieval_eval_relevance_rule`: `passage_level` vs.
  `human_labelled` boundary is undefined.**
  Where: `runs/2026-08-14-m2-corpus-extraction/step4-real-score-extraction.md`
  (the corrected note), p03's field value, `cases/schema.md`'s D-group
  definition of this field.
  What happened: two independent extractions of p03 read the same
  underlying fact (a human hand-paired each question to a chunk_id, then
  the scoring function exact-matches on that id) and landed on different
  values — one read the *matching mechanism* as `passage_level`, the other
  read the *label's provenance* as `human_labelled`. The schema doesn't
  say which reading wins when both apply.
  Clearing this means: either add a tie-breaking rule to `cases/schema.md`
  (e.g. "if a human assigned the label AND the check is exact-match, prefer
  X"), or explicitly decide the ambiguity is acceptable and leave it,
  recorded as a known soft spot.

  > **Julian:** Not a tie-break — the field conflates two separate facts
  > (match strictness vs. who picked the label). Split it into two fields:
  > `retrieval_eval_match_strictness` (none/source_level/document_level/
  > passage_level/other) and `retrieval_eval_label_origin`
  > (human_labelled/generated/mixed/undeterminable/other). Fill both from each
  > record's existing `basis` text, not a repo re-read — mark
  > `undeterminable` where the text doesn't say. No re-extraction.

  **RESOLVED (2026-08-18).** Done exactly as directed: filled from
  existing `basis` text only, no re-read. `cases/schema.md` carries both
  new field definitions; all 22 records + p13 migrated; 18 twins
  regenerated clean; scorer/tests pass. Logged: `docs/decisions.md`
  `sealing-review-fixes` (2).

- [x] **A2. `data_accessible: manual_steps` has no defining prose.**
  Where: `cases/schema.md` line ~441 (the field's table row, no paragraph
  after it — every sibling field in that section has one).
  What happened: found while fixing step 7's `reproducibility` bug #2 (the
  guidance's "unclear how to access data" 0-point disjunct has no mapped
  tier). Can't decide if `manual_steps` (or `other`) means "unclear how to
  access" without a definition.
  Clearing this means: write the missing paragraph, then decide whether
  `reproducibility`'s third 0-point disjunct should be mapped to it.

  > **Julian:** `manual_steps` = source is named AND access instructions
  > are given (a download link + destination, or a named API/key that's
  > free to obtain — not the LLM's own API key). NOT `manual_steps`: source
  > is only named, no access instructions (e.g. "Charité Berlin cancer
  > data" with nothing else). That second case is `other`, not
  > `manual_steps` — which means `other`, not `manual_steps`, is the
  > likely target for the guidance's "unclear how to access" disjunct.
  > Before mapping it: check how `other` has actually been used across
  > the 22 records for this field — need to confirm it's been used
  > consistently for "no access instructions," not as a general catch-all
  > for something else.

  **RESOLVED (2026-08-18).** Definition written exactly per your ruling
  (`cases/schema.md` ~line 553). Checked against actual corpus usage
  before mapping: `other` used exactly once (p05, reclassified from
  `manual_steps` under this definition — scoring-neutral), `manual_steps`
  now used zero times, `automated_or_committed` 21, `missing` 1 (p08) —
  22 records + p13 accounted for. `other` mapped to `criteria.yaml`'s
  `reproducibility` 0-point tier (structurally unreachable-and-documented,
  same treatment as `missing`). Logged: `docs/decisions.md`
  `sealing-review-fixes` (3).

- [x] **A3. Item 3e — `retrieval_best_approach_shipped` stays
  non-normalised, and the reading it rests on is still only "defensible,"
  not confirmed.**
  Where: `docs/decisions.md` `retrieval-best-approach-not-normalised-open`;
  `docs/deferred-to-m2.md` (the one item left in that file); step 7's
  report, "The `mixed_result` question" section.
  What happened: step 7 was supposed to be a chance to settle whether
  `mixed_result` should count toward `retrieval_evaluation`'s 2-point
  tier. It didn't settle it — the independent checker found the current
  reading "defensible... not the only reading," which is weaker than
  confirmation. Findings F2/F3 still depend on this reading.
  Clearing this means: either decide the reading is good enough to seal
  on (accepting the residual risk, stated explicitly in the writeup later),
  or spend more effort resolving it before sealing — this is the one item
  a reviewer specifically told me `criteria.yaml` itself flags as "the
  first row a reviewer of this transcription should attack."

  > p08 and p18 hold: retrieval_best_approach_shipped: true, instead of "yes"
  > p01, p02, p03, p04, p06, p09, p12, p14 hold the "mixed_results" could use a second independent read. Could also include p13.
  > There should be a difference on how these mixed_results are used. Is there a reasoning applied, why mixed_results was shipped? As an example my project p13 has "mixed_results" but it is reasoned about and not just silently dropped
  > I think somewhere it is also settled how to treat this metric, when one setting, e.g. k=10 was evaluated and then another setting, e.g. k=25 was shipped. Let's confirm how this would show up in this metric or not.

  **Sub-questions answered (2026-08-18):** (1) p08/p18 boolean bug —
  fixed, both now `"yes"`, corpus impact p18 17→18. (2) mixed_result
  reasoning across all 9 corpus records holding it: 8 of 9 have a
  measurement-grounded `decision_basis: measured` on the relevant
  group-H technique; only p01 has none (its known role as the
  harmful-component-kept example). p13 confirmed reasoned-about, not an
  outlier. (3) config-mismatch visibility: **not visible** —
  `retrieval_best_approach_shipped` does not cross-reference
  `retrieval_eval_config_matches_shipped`; 6 of the 9 `mixed_result`
  records also hold `differs` on that field, meaning most of the
  corpus's mixed-result evidence comes from an evaluation that doesn't
  reflect what shipped. This is new evidence *for* item 3e, not a fix to
  it. Full detail: `docs/decisions.md` `sealing-review-fixes` (4)(5).
  **Per-record breakdown, all 9 `mixed_result` records** (driving
  technique | decision_basis | that technique's shipped_enabled |
  config_matches_shipped):

  | case | driving technique | decision_basis | shipped_enabled | config match |
  |---|---|---|---|---|
  | p01 | reranking | **none** | true | differs |
  | p02 | reranking | measured (documented **rejection**) | **false** | differs |
  | p03 | hybrid_search | measured | true | differs |
  | p04 | hybrid_search | measured | true | differs |
  | p06 | hybrid_search | measured | true | differs |
  | p09 | hybrid_search | measured | true | matches |
  | p12 | reranking + query_rewriting | measured | true | matches |
  | p13 | hybrid_search + query_rewriting | measured | true / false | matches |
  | p14 | query_rewriting | measured | true | differs |

  p02 is qualitatively different from the other 8: its "mixed" comparison
  is the shipped config vs. a *rejected, unshipped* technique — the
  schema's own showcase case for a good decision, not a shipped
  underperformer. v0 cannot currently tell this apart from p01 (no
  reasoning at all) or the other 6 (shipped anyway, metrics disagree).

  **RESOLVED (2026-08-18) — sealing decision made, see C2.** Seal with
  both layers named as a risk, not held for the redesign: the reading
  dispute (which of the two `mixed_result` shapes above should count),
  and separately, the 6-of-9 config-mismatch finding compounding it. The
  eventual fix looks cheap to defer, checked but not built — it should
  be derivable from data already in every record
  (`shipped_enabled`/`measured_effect`/`decision_basis` per H-block), so
  sealing should not foreclose it. Logged:
  `docs/decisions.md` `retrieval-best-approach-not-normalised-open`
  (update).

## Section B — real findings, no schema change needed, but you should see them

Nothing here blocks sealing on its own. Listed so you've seen the actual
findings, not a summary of a summary.

- [x] **B1. `monitoring_instrumentation`'s `logged` vs.
  `traced_on_request_path` boundary recurs across the corpus.**
  Where: flagged independently by extractors on p05, p06, p09, p10, p12,
  and likely others not specifically counted — search
  `cases/records/*.yaml` for `monitoring_instrumentation` in
  `extraction_notes` to see the full list.
  Not fixed. A real, repeated schema-fit gap (synchronous per-request DB
  logging wired to a dashboard doesn't cleanly fit either enum value) that
  never got a decision. Low stakes since the field isn't read by v0 or any
  built twin yet.

  > **Julian:** Before treating this as a schema gap — check whether it's
  > already resolved by the field's own existing text. `cases/schema.md`
  > defines `traced_on_request_path` as "instrumentation runs where
  > requests are served" and `logged` as "records are written but nothing
  > is wired to a viewer." Read literally, the deciding fact is whether
  > something runs live during the request AND something consumes it —
  > not whether it's span/tracing-framework based specifically. A
  > per-request DB write feeding a live dashboard satisfies both halves
  > of that definition as written.
  >
  > Action: pull one of the flagged records (p05) and its
  > `extraction_notes` on this field. Check whether re-reading the
  > extractor's stated reasoning against the schema's literal wording
  > above resolves the ambiguity without a field split. If it does,
  > confirm the same reading against p06/p09/p10/p12 too before closing
  > this — one record resolving cleanly doesn't confirm the other four
  > read the same way. If the literal wording genuinely doesn't settle
  > it even once tested, then it needs an actual fix, not just a closer
  > read.
  >
  > Separate, smaller finding, not part of this item: `p02`'s
  > `traced_on_request_path` value comes from an auto-registered tracer,
  > close to zero engineering effort, same tier as a hand-built one would
  > get. `monitoring_dashboard_provenance` already separates presentation
  > effort (stock image vs. committed panels); nothing separates
  > instrumentation effort the same way. Not blocking, not part of B1 —
  > flagging so it doesn't get lost.

  **RESOLVED (2026-08-18).** Literal-wording test applied record-by-record,
  not assumed from one result, per your instruction. Checked 11 total
  (p04, p05, p06, p07, p08, p09, p10, p11, p12, p14, p17): 5
  misclassified as `logged`, corrected to `traced_on_request_path` (p05,
  p07, p09, p14, p17 — each confirmed by reading the clone directly,
  matching Postgres datasource between write path and dashboard); 6
  confirmed already correct (p04, p06, p08, p10, p11, p12 — p04/p12
  write on explicit feedback submission, not automatically per request;
  p08/p11 have no confirmed wiring from the write table to the
  dashboard). No schema field split needed — rule written into
  `cases/schema.md` as a literal-wording test instead. No scorer/twin
  impact (field not read by v0 or any twin, confirmed by grep; scorer
  and test suite rerun clean). Full list: `docs/decisions.md`
  `monitoring-instrumentation-boundary-fixed`. The tracer-effort
  observation (p02) is noted but not acted on, as you flagged it as
  non-blocking.

- [x] **B2. `cases/schema.md`'s group-H worked example doesn't show
  `decision_axes` nested.**
  Where: `docs/decisions.md` `decision-axes-nesting-fixed`, last sentence.
  The worked example added to fix the recurring flat-list defect (13 of 23
  records affected) shows every OTHER technique sub-field nested, but not
  `decision_axes` itself — the exact field that kept getting the defect.
  Acknowledged, not fixed, when found.

  > **Julian:** Confirmed directly — the worked example's own last line
  > breaks the rule the example exists to teach. Fix:
  >
  > In `cases/schema.md`'s group H worked example, replace:
  > ```
  > decision_axes: ["mrr", "hit_rate"]
  > ```
  > with:
  > ```
  > decision_axes:
  >   value: ["mrr", "hit_rate"]
  >   evidence: ["README.md:120-124"]
  >   basis: "quantities named in the decision_basis justification above"
  > ```
  > Same nesting as the five sub-fields above it. One line becomes four,
  > matching the pattern the surrounding paragraph already claims every
  > sub-field follows. No other change needed — this is the whole fix.

- [x] **B3. Two source repos leak real identity inside tracked, committed
  files (not just git metadata) — p09 and p14.**
  Where: `runs/2026-08-17-m2-extraction-spot-check/report.md`, "Note-level
  findings."
  p09: a notebook cell output names the real repo and a username, and
  that exact cell is one of the record's own cited evidence locators.
  p14: a first name appears ~162 times across committed docs/scripts, plus
  a leaked Windows path. **Confirmed: none of this reached
  `cases/records/p09.yaml` or `cases/records/p14.yaml`** — grepped
  directly, zero matches, both times. This is about the source clones
  (gitignored, never published), not about anything this project commits.
  No action required under your stated anonymity policy (outsiders can't
  trace back; that's what's protected). Flagged so you've seen it, not
  because it needs fixing.

  **Additionally checked (2026-08-19), the remaining open question this
  item left implicit — transcript persistence, not committed-file
  leakage:** the extraction/spot-check subagent sessions that read p09's
  and p14's clones wrote their transcripts to
  `/home/julian/.claude/projects/-home-julian-tuberlin-projects-heuristic-discovery-peer-review/`,
  confirmed to sit entirely outside the git repo
  (`git rev-parse --show-toplevel` resolves to the project directory, not
  that path) — never staged, never committed, not reachable through the
  repo regardless of what any transcript contains. Same non-issue as the
  clones themselves (gitignored, never published); this closes B3 fully,
  not just the committed-file half. Was already `[x]` before this session
  — resolution note added now so "checked and cleared" is explicit rather
  than implied by the checkbox alone.

- [x] **B4. `twin-catalogue-conditional` idea 2 (circular-eval-flavored
  conditional twin) was proposed, never built.**
  Where: my message proposing ideas 1-4 for the conditional-twin family.
  Idea 1 (config-drift × all three `measured_effect` values) and idea 4
  (decision-basis unsupported) are both built. Idea 3 was checked and
  found not to be a real distinct dependency (written up at the time).
  Idea 2 — combining a technique's `measured_effect` with the circularity
  fields (`llm_eval_judge_spotchecked`, `llm_eval_question_generator`) —
  was never picked up. Not blocking; the catalogue already has one
  circular-eval twin (`p13-t01`) and one conditional family (idea 1, three
  twins). Worth a decision on whether it's worth building before sealing
  or left for M3's red-team rounds to propose fresh.

  > For now this is not necessary. Can circle back on this in M3's red-team rounds.

  **Status: closed, deliberately deferred to M3, not dropped.** Your
  answer is the resolution — idea 2 is a real, named gap in the
  conditional-twin catalogue, explicitly not built now, revisited when
  M3's red-team rounds run. Was already `[x]` before this session; noted
  explicitly here so the deferral reads as a decision, not silence.

- [x] **B5. `group-j-restructure-deferred`'s own trigger condition may now
  be met.**
  Where: `docs/decisions.md` `group-j-restructure-deferred`.
  The deferral said "restructure once, after twin/red-team work shows
  which fields carry signal." Step 5 (twin work) is now done. Worth
  re-checking whether that's enough signal yet, or whether the deferral
  should explicitly wait for M3's red-team rounds too (the original
  owner ruling didn't specify which).

  > Does any of the twins touch documentation accuracy?
  > I see some potential issues with these counts. A readme that writes just a few (correct) things. Would get `all_traceable`, zero `untraceable`, zero conflicts, zero broken things. Just in artifacts referenced would be small indicator.
  > Further, there could be edge cases where documenting something that you did - and which is NOT included in the repo - could still be better than just not mentioning it. This more as an FYI, I don't think for this issue a good solution exists.

  **ANSWERED (2026-08-18).** Only 1 twin type (`claim-without-artifact`,
  `p04-t01`) touches group J, and only 2 of its 6 fields
  (`untraceable_number_count`, `headline_numbers_traceable`, one entailing
  the other). The other 4 fields have zero twin coverage — thin, not
  "shows which fields carry signal" yet. Strengthens the deferral's
  trigger condition rather than closing it; the deferral stays open, no
  restructure now. Your gameability observation (silence scores as well
  as sparse-but-correct documentation) is real and recorded as-is — no
  fix attempted, matching your own read that none exists cleanly given
  the schema has no size-of-claim denominator. Logged:
  `docs/decisions.md` `group-j-restructure-deferred` (update).

- [x] **B6. `untraceable_number_count`'s spot-check protocol
  (`untraceable-count-sampled-validation`, "sample 5 cited figures") may
  not have been executed exactly as decided.**
  Where: `docs/decisions.md` `untraceable-count-sampled-validation`;
  compare against `runs/2026-08-17-m2-extraction-spot-check/report.md`'s
  method section.
  The step-6 spot-check verified `untraceable_number_count`'s *total*
  against the repo, generally by re-deriving the whole count directly
  (several checkers recomputed it from scratch) rather than sampling
  exactly 5 cited figures as the decision specifically describes. The
  result is arguably stronger evidence (full recount beats a 5-item
  sample), but it's not literally what was decided. Worth confirming
  you're fine with the stronger-but-different method actually used.

  **Status: closed, no comment left.** Per this checklist's own
  instructions ("leave a comment inline if you want something changed
  rather than just checked"), a checked box with no reply means the
  stronger-but-different method is accepted as-is, no further action.
  Noted explicitly since a bare `[x]` with nothing under it is exactly
  the shape this project's own rules warn reads as ambiguous.

---

## Section B, continued

- [x] **B7. `cases/schema.md`'s header still says "M2 SCHEMA CLOSURE IN
  PROGRESS."** Confirmed stale by direct check: it's been "in progress"
  since step 2's sign-off, through step 3's re-extraction, step 5's twin
  work, and step 7's fixes, none of which updated it. Cheap fix — update
  before sealing, since the header becomes part of the permanent record
  once sealed.

  > agreed

- [x] **B8. The `Binds:` line convention (`binds-line-going-forward`) was
  adopted but never actually written onto any entry, including its own
  batch.** Confirmed: zero `Binds:` lines exist anywhere in
  `docs/decisions.md`, including the 19 M2 schema-closure entries the
  decision's own text said should carry one starting with itself. Needs a
  one-line answer, not a fix by default: was this a deliberate
  simplification (the 5-line budget per entry made it impractical), or a
  genuine miss that should be corrected before sealing?

  > need further information on this one

  **ANSWERED (2026-08-18).** Gave an effort estimate (~28 pre-existing
  entries never carried one; retrofit would need per-entry tracing to an
  actual enforcement point, a few hours). Owner decision: leave as
  going-forward only, no retrofit — nothing reads `Binds:` mechanically,
  every entry has only ever been used by being read directly, not worth
  the cost against sealing work still ahead. One correction made instead:
  `binds-line-going-forward`'s own text overclaimed applying to its own
  batch (it doesn't — none of the 19 M2 schema-closure entries carry
  one); fixed the entry's text to state the rule took effect from the
  *next* batch, not the one it was written alongside. Logged:
  `docs/decisions.md` `binds-line-going-forward` (update).

- [x] **B9. Final real-score leak check — done, clean, recorded here so
  it doesn't need repeating.** Grepped every value in the 10-repo staging
  file against every file in `cases/` and `docs/decisions.md` right
  before writing this checklist. Every hit traces to an unrelated line
  number, structural count, or date — no actual repo-id/score pairing
  found anywhere. `real-score-candidates.yaml` confirmed still gitignored.
  No action needed; this closes the loop `real-score-dataset-scoped`
  requires, run once more given how much has changed (22 records, 18
  twins, multiple re-extractions) since the last check.

  > agreed.

## Section C — sealing mechanics, not findings

- [x] **C1. Confirm the final counts to stamp at sealing.** Records: 22
  `role: corpus` + p13 (`role: self`) = 23 total. Twins: 18. `schema_version`:
  1. These should be re-derived from the actual directories at sealing
  time, not copied from this checklist (per the project's own
  "counts are recomputed, never carried forward" rule) — `ls cases/records/*.yaml
  | wc -l` and `ls cases/twins/*.yaml | wc -l` at the moment you sign off.

- [x] **C2. Decide whether Section A items must close before sealing, or
  whether sealing can happen with them stated as named open risks in the
  sealing entry itself.** Both are legitimate under this project's own
  rules (nothing requires perfection, but nothing may be silently
  dropped) — this is your call, not a default.

  > I think we should settle all open questions. I made commens on most A and B itms.

  **RESOLVED (2026-08-18).** All A and B items now closed except item
  3e's underlying interpretation question, which cannot be closed by
  fact-finding — it needs a derivation-formula redesign explicitly
  deferred pending dedicated owner review (`retrieval-best-approach-
  not-normalised-open`). Decision: seal with it as a named, two-layer
  risk (see A3 above), since the eventual fix is confirmed derivable
  from data already in the corpus and does not require re-extraction —
  sealing now does not foreclose it later.
