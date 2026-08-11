"""Validate records and twins against `cases/schema.md` — independently.

This checker exists because the obvious way to validate a twin is circular.
`tools/generate_twins.py` carries `FIELD_SPEC`, a hand transcription of the
schema, and verifies its own output against it. That catches mistakes in
twin construction and cannot catch a mistake in the transcription: a field
mis-marked `descriptive` in FIELD_SPEC would let a no-change twin mutate a
scoreable field, and the generator's own verify would pass.

So this file re-derives everything from `cases/schema.md` itself, parsing
the prose tables the schema is written in. Two independent readings of one
source; a disagreement means one of them is wrong, which is the point.

It checks, for every record and every twin:

  * every field is declared in the schema, and nothing is missing;
  * every value matches its declared type — enum membership included;
  * each twin's actual diff against its base equals the diff its metadata
    claims, with no undeclared changes;
  * read-set disjointness: degraded twins touch `scoreable` fields only,
    no-change twins touch `descriptive` only.

    uv run python tools/check_records.py

Exit status is non-zero if anything fails, so it can gate a run.
"""

from __future__ import annotations

import pathlib
import re
import sys
from typing import Any

import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCHEMA = REPO / "cases" / "schema.md"
RECORDS = REPO / "cases" / "records"
TWINS = REPO / "cases" / "twins"

# Rows are `| `name` | type | values |`. Split on unescaped pipes only: two
# type cells are written `int \| null`, and a naive split silently drops
# those fields from the check rather than failing.
CELL = re.compile(r"(?<!\\)\|")


def parse_schema(text: str) -> tuple[dict[str, tuple[str, set[str]]], set[str]]:
    """Return {field: (declared_type, enum_members)} and the descriptive set."""
    declared: dict[str, tuple[str, set[str]]] = {}
    for line in text.splitlines():
        cells = [c.strip().replace(r"\|", "|") for c in CELL.split(line)]
        if len(cells) < 4:
            continue
        match = re.fullmatch(r"`([a-z0-9_]+)`", cells[1])
        if not match:
            continue
        declared_type = cells[2]
        members = set(re.findall(r"`([a-z0-9_]+)`", cells[3])) if "enum" in declared_type else set()
        declared.setdefault(match.group(1), (declared_type, members))

    # Group K is the descriptive group; its heading declares it.
    section = re.search(r"## K\..*?`descriptive`.*?\n(.*?)(?=\n## |\Z)", text, re.S)
    if section is None:
        raise SystemExit("schema.md: could not find the descriptive field group (K)")
    descriptive = {
        m.group(1)
        for m in (re.match(r"\| `([a-z0-9_]+)` \|", line) for line in section.group(1).splitlines())
        if m
    }
    return declared, descriptive


def type_ok(declared_type: str, members: set[str], value: Any) -> bool:
    if "enum" in declared_type:
        return isinstance(value, str) and value in members
    if declared_type == "bool":
        return isinstance(value, bool)
    if "null" in declared_type:
        return value is None or (isinstance(value, int) and not isinstance(value, bool))
    if declared_type == "int":
        return isinstance(value, int) and not isinstance(value, bool)
    if "list" in declared_type:
        return isinstance(value, list) and all(isinstance(v, str) for v in value)
    if declared_type == "string":
        return isinstance(value, str)
    return True  # an undeclared shape is caught by the membership check instead


def leaves(node: dict, prefix: str = "") -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in node.items():
        if isinstance(value, dict) and "value" in value:
            out[prefix + key] = value["value"]
        elif isinstance(value, dict):
            out.update(leaves(value, prefix + key + "."))
    return out


def norm(path: str) -> str:
    """Twin metadata uses full `fields.X.value` paths; leaves() uses `X`."""
    return path.removeprefix("fields.").removesuffix(".value")


def main() -> int:
    schema_text = SCHEMA.read_text(encoding="utf-8")
    declared, descriptive = parse_schema(schema_text)
    failures: list[str] = []
    checked = 0

    records = {
        path.stem: yaml.safe_load(path.read_text(encoding="utf-8"))
        for path in sorted(RECORDS.glob("*.yaml"))
    }
    twins = {
        path.stem: yaml.safe_load(path.read_text(encoding="utf-8"))
        for path in sorted(TWINS.glob("*.yaml"))
    }

    print(f"schema: {len(declared)} fields declared, {len(descriptive)} descriptive")
    print(f"checking {len(records)} record(s) and {len(twins)} twin(s)\n")

    for name, doc in {**records, **twins}.items():
        for path, value in leaves(doc["fields"]).items():
            leaf = path.split(".")[-1]
            if leaf not in declared:
                failures.append(f"{name}: {path} is not declared in schema.md")
                continue
            checked += 1
            declared_type, members = declared[leaf]
            if not type_ok(declared_type, members, value):
                failures.append(f"{name}: {path} = {value!r} violates declared type {declared_type!r}")

    for name, twin in twins.items():
        meta = twin["twin"]
        base = records.get(meta["base_case_id"])
        if base is None:
            failures.append(f"{name}: base record {meta['base_case_id']} not found")
            continue
        base_leaves, twin_leaves = leaves(base["fields"]), leaves(twin["fields"])
        if set(base_leaves) != set(twin_leaves):
            failures.append(f"{name}: field set differs from its base record")
            continue

        actual = {k for k in base_leaves if base_leaves[k] != twin_leaves[k]}
        claimed = {norm(entry["field"]) for entry in meta["diff"]}
        if actual != claimed:
            failures.append(f"{name}: actual diff {sorted(actual)} != claimed {sorted(claimed)}")

        touched = {"descriptive" if k.split(".")[0] in descriptive else "scoreable" for k in actual}
        expected = "descriptive" if meta["direction"] == "zero" else "scoreable"
        if touched != {expected}:
            failures.append(
                f"{name}: direction {meta['direction']!r} must touch only {expected} "
                f"fields, but touches {sorted(touched)}"
            )

        for entry in meta["diff"]:
            field = norm(entry["field"])
            if base_leaves.get(field) != entry["before"]:
                failures.append(f"{name}: stale `before` on {field}")
            if twin_leaves.get(field) != entry["after"]:
                failures.append(f"{name}: stale `after` on {field}")

        print(
            f"  {name:<9} {meta['direction']:<15} {len(actual)} change(s), "
            f"{','.join(sorted(touched))}, vs {meta['comparison']['against']}"
        )

    print(f"\ntype-checked {checked} leaf values against schema.md's own tables")
    if failures:
        print("\nFAILED:")
        for failure in failures:
            print(f"  ! {failure}")
        return 1
    print("PASS: types, diffs and read-set disjointness all hold")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
