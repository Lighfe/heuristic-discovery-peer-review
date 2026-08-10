"""The measurement protocol: what varies between reviewer samples, and how.

Two rules live here and nowhere else.

**Reviewer independence.** Each reviewer call is stateless, sees one case,
sees no other reviewer's output, and receives the evidence fields in a
shuffled order so that a criterion cannot be answered from field position
(decision `reviewer-independence`).

**The shuffle is seeded, never random.** An unseeded shuffle would produce a
fresh prompt on every re-run, so every prompt hash would miss the cache and
the "a re-run costs zero requests" guarantee would fail silently — the worst
kind of failure, because the run still succeeds and just costs a day's quota.
The order is therefore a pure function of (case_id, sample_index,
protocol_version).

The permutation is derived from SHA-256 rather than `random.shuffle`.
`random`'s stream is not contractually stable across CPython versions, and a
Python upgrade silently reshuffling every prompt is exactly the failure this
module exists to prevent.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence

# Every sampling parameter that reaches the provider must appear here, or it
# will not reach the cache key either. Adding a knob to `[gemini.sampling]`
# without adding it here reintroduces exactly the silent-staleness bug this
# tuple exists to prevent; `tests/test_protocol.py` asserts the two agree.
SAMPLING_KEYS: tuple[str, ...] = ("temperature", "max_output_tokens")


def _digest(*parts: str) -> bytes:
    h = hashlib.sha256()
    for part in parts:
        h.update(part.encode("utf-8"))
        h.update(b"\x00")  # length-independent separator
    return h.digest()


def seeded_field_order(
    field_names: Sequence[str],
    *,
    case_id: str,
    sample_index: int,
    protocol_version: int,
) -> list[str]:
    """Return `field_names` in a deterministic, seed-dependent order.

    Deterministic across processes, machines and CPython versions. Distinct
    (case_id, sample_index, protocol_version) triples give unrelated orders;
    the same triple always gives the same one.
    """
    seed = f"{protocol_version}|{case_id}|{sample_index}"
    # Sorting on the digest yields a permutation; the trailing field name
    # breaks ties deterministically in the (astronomically unlikely) case of
    # a digest collision, so the result is a total order either way.
    return sorted(field_names, key=lambda name: (_digest(seed, name), name))


def shuffled_fields(
    fields: Mapping[str, object],
    *,
    case_id: str,
    sample_index: int,
    protocol_version: int,
) -> dict[str, object]:
    """`fields` re-keyed into seeded order, ready for prompt rendering."""
    order = seeded_field_order(
        list(fields.keys()),
        case_id=case_id,
        sample_index=sample_index,
        protocol_version=protocol_version,
    )
    return {name: fields[name] for name in order}


def prompt_hash(prompt: str) -> str:
    """Stable hash of a fully-rendered prompt."""
    return hashlib.sha256(prompt.encode("utf-8")).hexdigest()


def cache_key(
    *,
    model: str,
    prompt: str,
    case_id: str,
    protocol_version: int,
    sampling: Mapping[str, object],
) -> str:
    """The cache key: (model, prompt-hash, case-id, protocol-version, sampling).

    `model` is in the key because results from two models are not
    interchangeable measurements. `protocol_version` is in it because a
    protocol change must never silently reuse results measured under the old
    one. Both are stated in `plan.md` under reviewer independence.

    `sampling` is in it because temperature is not a free knob here — it is
    the variable the G4 self-consistency measurement is *about*. It reaches
    the provider as an API parameter rather than as prompt text, so it is
    invisible to `prompt_hash`; leaving it out would mean an edited
    temperature silently served responses generated under the old one, and
    a contaminated pass would be indistinguishable from a clean one in every
    artifact the run produces. Relying on a human to bump
    `protocol_version` alongside a temperature edit is not a mechanism.
    """
    material = json.dumps(
        {
            "model": model,
            "prompt_sha256": prompt_hash(prompt),
            "case_id": case_id,
            "protocol_version": protocol_version,
            "sampling": dict(sampling),
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(material.encode("utf-8")).hexdigest()
