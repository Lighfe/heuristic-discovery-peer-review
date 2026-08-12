"""Same-model self-consistency probe.

Three stateless samples per case from one Gemini model at a fixed
temperature above zero, evidence fields shuffled in a seeded order, each
call seeing one case and no other reviewer's output.

**What this measures, stated because the bare word is forbidden.** It is
*same-model self-consistency*, not human reviewer agreement and not
cross-family agreement (decision `g4-is-self-consistency`). The real course
assigns three independent humans and takes the median, so one reviewer's
inconsistency cannot move a grade at all; this number does not stand in for
that and the writeup may not imply it does.

**M1's number is not a baseline.** The task labels this a pipeline smoke
test: the baseline is measured at M2 over the full corpus, and the manifest
here says `baseline: false` so a later reader cannot mistake one for the
other.

    uv run python -m loop.agreement --dry-run     # cost it, spend nothing
    uv run python -m loop.agreement
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import statistics
import sys
from datetime import UTC, datetime

import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "candidates" / "v0"))

from loop.config import load_config  # noqa: E402
from loop.render import render_prompt  # noqa: E402
from loop.run import build_calls, run_pass  # noqa: E402
from score import load_candidate, score  # noqa: E402

SAMPLES = 3
DECLARED_BUDGET = 60  # tasks/02-milestone-1.md hard limit for this milestone


def load_cases() -> dict[str, dict]:
    paths = sorted((REPO / "cases" / "records").glob("*.yaml")) + \
            sorted((REPO / "cases" / "twins").glob("*.yaml"))
    return {p.stem: yaml.safe_load(p.read_text(encoding="utf-8")) for p in paths}


def build_specs(cases: dict[str, dict], candidate: dict, protocol_version: int):
    specs = []
    for name, case in cases.items():
        for sample in range(SAMPLES):
            specs.append((name, render_prompt(
                case, candidate, sample_index=sample, protocol_version=protocol_version)))
    return specs


def parse_scores(text: str) -> dict | None:
    """Pull the JSON object out of a reply. None if it cannot be read.

    An unparseable reply is recorded as such and excluded, never coerced to
    a number — p02's own evaluation silently dropped its parse failures from
    a reported rate, and that is the defect this project exists to find.
    """
    match = re.search(r"\{.*\}", text, re.S)
    if not match:
        return None
    try:
        data = json.loads(match.group(0))
    except json.JSONDecodeError:
        return None
    if not isinstance(data.get("criteria"), list):
        return None
    return data


def summarise(cases, candidate, specs, responses) -> dict:
    """Per-case self-consistency, plus the executable layer for comparison."""
    by_case: dict[str, list[dict]] = {name: [] for name in cases}
    for (name, prompt), text in zip(specs, responses, strict=False):
        parsed = parse_scores(text) if text is not None else None
        by_case[name].append(parsed)

    out = {}
    for name, samples in by_case.items():
        good = [s for s in samples if s]
        totals = [int(s["total"]) for s in good if isinstance(s.get("total"), int)]
        executable = score(cases[name], candidate).total
        out[name] = {
            "samples_requested": len(samples),
            "samples_parsed": len(good),
            "samples_unparseable": len(samples) - len(good),
            "totals": totals,
            "identical": len(set(totals)) == 1 if totals else None,
            "spread": (max(totals) - min(totals)) if totals else None,
            "median": statistics.median(totals) if totals else None,
            "executable_layer_total": executable,
            "median_minus_executable": (statistics.median(totals) - executable) if totals else None,
        }
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true", help="cost the pass, spend nothing")
    ap.add_argument("--run-id", default=None)
    args = ap.parse_args(argv)

    config = load_config()
    candidate = load_candidate()
    cases = load_cases()
    specs = build_specs(cases, candidate, config.protocol_version)

    chars = sum(len(p) for _, p in specs)
    print(f"cases {len(cases)} x {SAMPLES} samples = {len(specs)} calls, budget {DECLARED_BUDGET}")
    print(f"model {config.model}  temperature {config.sampling.temperature}  "
          f"protocol {config.protocol_version}")
    print(f"prompt size: {chars // len(specs)} chars each, ~{chars // 4} tokens total "
          f"(input TPM limit {config.quota.input_tokens_per_minute:,})")

    if args.dry_run:
        from loop.cache import ResponseCache
        cache = ResponseCache(config.cache_dir)
        calls = build_calls(specs, config=config)
        hits = sum(1 for c in calls if cache.has(c.cache_key))
        print(f"cache: {hits} hit, {len(calls) - hits} would cost a request")
        print(f"distinct cache keys: {len({c.cache_key for c in calls})} (must equal {len(calls)})")
        return 0

    run_id = args.run_id or datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ") + "-agreement"
    result = run_pass(
        kind="agreement-probe", specs=specs, declared_budget=DECLARED_BUDGET,
        config=config, run_id=run_id,
        notes={
            "baseline": False,
            "what_this_measures": "same-model self-consistency, not human agreement",
            "label": "M1 pipeline smoke test; the baseline is measured at M2 over the full corpus",
            "samples_per_case": SAMPLES,
            "candidate": candidate["candidate"],
            "reviewer_prompt": "agents/reviewer/v1/prompt.md",
        },
    )

    ordered = [result.responses.get(c.cache_key) for c in build_calls(specs, config=config)]
    summary = summarise(cases, candidate, specs, ordered)
    out = config.runs_dir / result.run_id
    (out / "agreement.json").write_text(
        json.dumps({"baseline": False, "per_case": summary}, indent=2, sort_keys=True),
        encoding="utf-8")

    print(f"\nrequests {result.budget.requests_needed} planned, "
          f"{len([r for r in ordered if r])} responses\n")
    print(f"{'case':<10} {'totals':<18} {'spread':>6} {'median':>7} {'v0':>4} {'diff':>5}  unparseable")
    for name, s in summary.items():
        print(f"{name:<10} {str(s['totals']):<18} {str(s['spread']):>6} "
              f"{str(s['median']):>7} {s['executable_layer_total']:>4} "
              f"{str(s['median_minus_executable']):>5}  {s['samples_unparseable']}")
    print(f"\nNON-BASELINE. runs/{result.run_id}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
