"""The shuffle, finally wired into a prompt.

`decisions.md` `shuffle-checked-at-schema-gate` recorded that
`seeded_field_order` was tested in isolation while nothing rendered a
prompt, so "the cache key covers the shuffle" was intent, not a property.
These tests are the discharge of that.
"""

from __future__ import annotations

import pathlib
import sys

import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "candidates" / "v0"))

from loop.protocol import cache_key, prompt_hash  # noqa: E402
from loop.render import flatten, render_prompt, render_record  # noqa: E402

CASE = yaml.safe_load((REPO / "cases" / "records" / "p01.yaml").read_text())
CANDIDATE = yaml.safe_load((REPO / "candidates" / "v0" / "criteria.yaml").read_text())


def test_two_samples_of_one_case_differ_in_prompt_hash():
    """The property the schema gate asked for.

    Same case, same field values, different sample index -> a different
    prompt, hence a different cache key. Without this the three samples
    G4 needs would be three identical requests, and the second and third
    would be served from cache: perfect agreement, measured on nothing.
    """
    a = render_prompt(CASE, CANDIDATE, sample_index=0, protocol_version=1)
    b = render_prompt(CASE, CANDIDATE, sample_index=1, protocol_version=1)
    assert a != b
    assert prompt_hash(a) != prompt_hash(b)

    keys = {
        cache_key(model="m", prompt=p, case_id="p01", protocol_version=1,
                  sampling={"temperature": 0.7, "max_output_tokens": 2048})
        for p in (a, b)
    }
    assert len(keys) == 2


def test_the_same_sample_is_byte_identical():
    """Otherwise a re-run costs a full pass instead of zero requests."""
    a = render_prompt(CASE, CANDIDATE, sample_index=2, protocol_version=1)
    b = render_prompt(CASE, CANDIDATE, sample_index=2, protocol_version=1)
    assert a == b


def test_a_protocol_bump_changes_the_prompt():
    a = render_prompt(CASE, CANDIDATE, sample_index=0, protocol_version=1)
    b = render_prompt(CASE, CANDIDATE, sample_index=0, protocol_version=2)
    assert a != b


def test_every_field_is_rendered_exactly_once():
    """Rendering the read-set only would leak the mapping into the prompt."""
    rendered = render_record(CASE, sample_index=0, protocol_version=1)
    names = [line[2:].split(":")[0] for line in rendered.splitlines() if line.startswith("- ")]
    assert sorted(names) == sorted(flatten(CASE["fields"]))


def test_the_evidence_list_is_never_rendered():
    """The `evidence` field is for human re-verification, never for scoring.

    Note what this does NOT claim. Repo paths still reach the prompt, because
    `basis` sentences cite them inline — `(docs/evaluation.md:19 states ...)`.
    Stripping those would mangle the one field written to stand alone as a
    sentence, so they stay, and the consequence is recorded in
    `docs/deferred-to-m2.md` rather than papered over here: a reviewer sees
    pointers it cannot follow, and a densely-cited basis may read as
    better-evidenced than a sparse one, which is a confound in any fidelity
    measurement built on these prompts.
    """
    rendered = render_record(CASE, sample_index=0, protocol_version=1)
    # The synthetic-evidence marker exists only in the `evidence` list of a
    # mutated twin field, so its absence proves the list itself is not rendered.
    twin = yaml.safe_load((REPO / "cases" / "twins" / "p01-t01.yaml").read_text())
    assert "<synthetic>" in str(twin["fields"]["retrieval_best_approach_shipped"]["evidence"])
    assert "<synthetic>" not in render_record(twin, sample_index=0, protocol_version=1)
    assert "evidence:" not in rendered


def test_prompt_carries_the_courses_own_criterion_text():
    prompt = render_prompt(CASE, CANDIDATE, sample_index=0, protocol_version=1)
    assert "Multiple retrieval approaches are evaluated, and the best one is used" in prompt
    assert "retrieval_evaluation" in prompt
    # ...and never the executable tiers.
    assert "fallback" not in prompt
    assert "when:" not in prompt
