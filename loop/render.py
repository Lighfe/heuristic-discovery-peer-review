"""Render a case into a reviewer prompt, with the field order seeded.

This is where `protocol.seeded_field_order` finally does its job. Until now
it was tested in isolation, so "the cache key covers the shuffle" was design
intent rather than a demonstrated property (decision
`shuffle-checked-at-schema-gate`). It is demonstrated here, and in
`tests/test_render.py`: two samples of one case, identical in every field
value, must produce different prompt hashes.

Two rules from the schema decide what a reviewer sees:

  * **`value` and `basis`, never `evidence`.** No agent can open the files a
    locator points at, so locators would be noise; `basis` is the one field
    written to stand alone as a sentence. And no repository content beyond
    what a record already contains is sent to a free-tier provider.
  * **Every field, not only the ones the candidate reads.** Rendering the
    read-set would leak the mapping into the prompt and turn a fidelity
    measurement into a hint. The reviewer decides what matters; that
    decision is what the measurement is about.

`basis` text routinely cites file-path locators inline even though
`evidence` locators are never rendered (`deferred-to-m2.md` §3j) — a
reviewer cannot follow the pointer, and citation density could move a
score for reasons unrelated to content. `strip_locators` removes these
specifically from the copy sent to a reviewer prompt; the committed
record's `basis` (used for human re-verification) is untouched, since
nothing here writes back to `cases/records/`.
"""

from __future__ import annotations

import pathlib
import re

from loop.protocol import seeded_field_order

REPO = pathlib.Path(__file__).resolve().parent.parent
PROMPT = REPO / "agents" / "reviewer" / "v1" / "prompt.md"

# Matches a repo-relative path locator, followed by a line/cell reference:
# docs/eval.md:9-10, src/api/routes.py:52-55, notebooks/rag.ipynb:cell17,cell19.
# Deliberately requires the `:line`/`:cellN` suffix and never consumes a
# backtick itself: a bare filename with no locator suffix is at least as
# likely to be prose ("pyproject.toml declares...") or part of a backtick-
# wrapped shell command (`uv run python src/ingest.py`) as an evidence
# citation, and stripping backticks around a command produces a dangling
# unmatched backtick — corrupted markdown, not just a lost citation. Bare
# whole-file citations (no line number) are therefore not stripped; that is
# part of the residual risk named in `deferred-to-m2.md` §3j.
_LOCATOR_RE = re.compile(
    r"[\w][\w./-]*\.(?:py|md|ipynb|yaml|yml|txt|toml|json|cfg|dist|csv|sql)"
    r":(?:cell\d+|\d+)(?:[-,](?:cell)?\d+)*"
)


def strip_locators(text: str) -> str:
    """Remove path-shaped citations from `basis` text for reviewer prompts.

    A regex strip can miss an unusual citation style — this is named as a
    residual risk in `deferred-to-m2.md` §3j, not treated as a solved
    problem. Empty parens/brackets left behind by a stripped sole citation
    are cleaned up; everything else about the sentence is untouched.
    """
    stripped = _LOCATOR_RE.sub("", text)
    stripped = re.sub(r"\(\s*\)|\[\s*\]", "", stripped)
    stripped = re.sub(r"[ \t]{2,}", " ", stripped)
    stripped = re.sub(r"\s+([,.;:])", r"\1", stripped)
    return stripped.strip()


def flatten(fields: dict, prefix: str = "") -> dict[str, dict]:
    """Record fields -> {qualified name: leaf node}, technique blocks included."""
    out: dict[str, dict] = {}
    for name, node in fields.items():
        if isinstance(node, dict) and "value" in node:
            out[prefix + name] = node
        elif isinstance(node, dict):
            out.update(flatten(node, prefix + name + "."))
    return out


def render_record(case: dict, *, sample_index: int, protocol_version: int) -> str:
    leaves = flatten(case["fields"])
    order = seeded_field_order(
        list(leaves),
        case_id=case["case_id"],
        sample_index=sample_index,
        protocol_version=protocol_version,
    )
    lines = []
    for name in order:
        node = leaves[name]
        value = node.get("value")
        rendered = "not stated" if value is None else str(value)
        lines.append(f"- {name}: {rendered}")
        if node.get("basis"):
            lines.append(f"  ({strip_locators(node['basis'])})")
    return "\n".join(lines)


def render_criteria(candidate: dict) -> str:
    """The candidate's PROSE layer — the course's own text, verbatim.

    The reviewer sees the criteria as an author or reviewer would read them,
    never the executable tiers. Systematic disagreement between this and the
    executable layer is a defect in the candidate's prose, which is the whole
    point of measuring it (`plan.md`, prose-executable fidelity).
    """
    blocks = []
    for spec in candidate["criteria"]:
        blocks.append(f"id: {spec['id']}\n{spec['guidance_verbatim'].rstrip()}")
    return "\n\n".join(blocks)


def render_prompt(case: dict, candidate: dict, *, sample_index: int, protocol_version: int) -> str:
    template = PROMPT.read_text(encoding="utf-8")
    body = template.split("---\n", 2)[-1]  # drop the versioning preamble
    return body.format(
        criteria=render_criteria(candidate),
        record=render_record(case, sample_index=sample_index, protocol_version=protocol_version),
    )
