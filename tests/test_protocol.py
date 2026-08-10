"""The seeded shuffle and the cache key.

These are the two places where the cost model can fail *silently* — a run
that succeeds and simply costs a day's quota for nothing.
"""

from __future__ import annotations

import subprocess
import sys

from loop.protocol import (
    SAMPLING_KEYS,
    cache_key,
    seeded_field_order,
    shuffled_fields,
)

FIELDS = [
    "problem_statement_present",
    "knowledge_base_kind",
    "retrieval_eval_approaches",
    "llm_eval_approaches",
    "interface_kind",
    "ingestion_kind",
    "monitoring_charts",
    "containerization_kind",
    "reproducibility_versions_pinned",
]


def test_order_is_stable_for_the_same_seed():
    first = seeded_field_order(FIELDS, case_id="p01", sample_index=0, protocol_version=1)
    second = seeded_field_order(FIELDS, case_id="p01", sample_index=0, protocol_version=1)
    assert first == second


def test_order_is_a_permutation():
    order = seeded_field_order(FIELDS, case_id="p01", sample_index=2, protocol_version=1)
    assert sorted(order) == sorted(FIELDS)


def test_order_differs_across_samples_and_cases_and_protocol():
    base = seeded_field_order(FIELDS, case_id="p01", sample_index=0, protocol_version=1)
    assert base != seeded_field_order(
        FIELDS, case_id="p01", sample_index=1, protocol_version=1
    )
    assert base != seeded_field_order(
        FIELDS, case_id="p02", sample_index=0, protocol_version=1
    )
    assert base != seeded_field_order(
        FIELDS, case_id="p01", sample_index=0, protocol_version=2
    )


def test_order_is_stable_across_processes():
    """The guarantee that actually matters.

    An in-process check would pass even for `random.shuffle`, whose stream
    is not contractually stable. Re-deriving the order in a fresh
    interpreter is what tests the real property: the same prompt tomorrow,
    hence the same cache key, hence zero requests.
    """
    expected = seeded_field_order(
        FIELDS, case_id="p01", sample_index=1, protocol_version=1
    )
    script = (
        "from loop.protocol import seeded_field_order;"
        f"print(','.join(seeded_field_order({FIELDS!r},"
        "case_id='p01', sample_index=1, protocol_version=1)))"
    )
    out = subprocess.run(
        [sys.executable, "-c", script], capture_output=True, text=True, check=True
    )
    assert out.stdout.strip().split(",") == expected


def test_shuffled_fields_preserves_values():
    fields = {name: index for index, name in enumerate(FIELDS)}
    shuffled = shuffled_fields(
        fields, case_id="p01", sample_index=0, protocol_version=1
    )
    assert shuffled == {k: fields[k] for k in shuffled}
    assert list(shuffled) != FIELDS  # it did in fact shuffle


def test_cache_key_separates_everything_that_varies():
    base = dict(
        model="m", prompt="p", case_id="p01", protocol_version=1,
        sampling={"temperature": 0.7, "max_output_tokens": 2048},
    )
    key = cache_key(**base)
    assert key == cache_key(**base)
    assert key != cache_key(**{**base, "model": "other"})
    assert key != cache_key(**{**base, "prompt": "different"})
    assert key != cache_key(**{**base, "case_id": "p02"})
    assert key != cache_key(**{**base, "protocol_version": 2})


def test_sampling_params_are_in_the_cache_key():
    """Temperature reaches the provider as an API argument, not prompt text.

    Left out of the key, an edited temperature would serve responses
    generated under the old one, and a contaminated pass would be
    indistinguishable from a clean one in every artifact the run produces.
    Temperature is the variable G4 is *about*, so this is not a small hole.
    """
    base = dict(model="m", prompt="p", case_id="p01", protocol_version=1)
    hot = cache_key(**base, sampling={"temperature": 0.7, "max_output_tokens": 2048})
    cold = cache_key(**base, sampling={"temperature": 0.2, "max_output_tokens": 2048})
    longer = cache_key(**base, sampling={"temperature": 0.7, "max_output_tokens": 4096})
    assert len({hot, cold, longer}) == 3


def test_every_sampling_field_reaches_the_cache_key():
    """A knob added to `[gemini.sampling]` must reach `SAMPLING_KEYS` too.

    Otherwise the silent-staleness bug is reintroduced the next time
    somebody adds top_p, and no test would notice.
    """
    from dataclasses import fields

    from loop.config import Sampling

    assert set(SAMPLING_KEYS) == {f.name for f in fields(Sampling)}
    assert set(SAMPLING_KEYS) == set(Sampling(temperature=0.7, max_output_tokens=1).as_dict())
