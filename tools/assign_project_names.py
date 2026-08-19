"""Assign the synthetic `project_name` field to every record.

`project_name` is not extracted — see `cases/schema.md` group K and
`agents/extractor/v2`'s note on it. It exists only so the cosmetic-rename
no-change twin kind has a field to mutate, and it must never carry real
information about a repository: a value invented per-repo by a model risks
leaking the real project or repo name, which the extractor's anonymity rule
exists to prevent.

Deterministic and plain Python for the same reason `tools/generate_twins.py`
is: a name that could change between runs, or that a person chose by hand,
is not a fact the rest of the pipeline can treat as fixed.

    uv run python tools/assign_project_names.py
"""

from __future__ import annotations

import pathlib
import re

import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
RECORDS = REPO / "cases" / "records"

# 24 letters; p01-p23 uses the first 23, one spare for corpus growth.
GREEK = [
    "Alpha", "Beta", "Gamma", "Delta", "Epsilon", "Zeta", "Eta", "Theta",
    "Iota", "Kappa", "Lambda", "Mu", "Nu", "Xi", "Omicron", "Pi", "Rho",
    "Sigma", "Tau", "Upsilon", "Phi", "Chi", "Psi", "Omega",
]


def name_for(case_id: str) -> str:
    n = int(re.fullmatch(r"p(\d+)", case_id).group(1))
    if not 1 <= n <= len(GREEK):
        raise ValueError(f"{case_id}: no Greek letter reserved for this index; extend GREEK")
    return f"Project {GREEK[n - 1]}"


def main() -> int:
    paths = sorted(RECORDS.glob("p*.yaml"))
    changed = 0
    for path in paths:
        case_id = path.stem
        text = path.read_text(encoding="utf-8")
        doc = yaml.safe_load(text)
        if "project_name" in doc["fields"]:
            continue  # already assigned; do not overwrite silently
        name = name_for(case_id)
        doc["fields"]["project_name"] = {
            "value": name,
            "evidence": [],
            "basis": (
                "Synthetic label, assigned by tools/assign_project_names.py from case_id. "
                "Not derived from the repository and carries no real information about it."
            ),
        }
        header_lines = []
        for line in text.splitlines(keepends=True):
            if line.startswith("#"):
                header_lines.append(line)
            else:
                break
        new_text = "".join(header_lines) + yaml.safe_dump(
            doc, sort_keys=False, allow_unicode=True, default_flow_style=False, width=4096
        )
        path.write_text(new_text, encoding="utf-8")
        changed += 1
        print(f"{case_id}: assigned {name!r}")

    print(f"done: {changed} record(s) updated, {len(paths) - changed} already had project_name")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
