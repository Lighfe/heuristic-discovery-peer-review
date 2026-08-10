"""The response cache.

Structural, not an optimisation (CLAUDE.md, cost model): a re-run must cost
zero requests for anything already seen, or iteration stops being possible
on a 500-requests-a-day budget.

The cache write is also the checkpoint. A pass that dies mid-way has already
persisted every response it paid for, so resuming re-reads them for free and
only the unseen remainder costs anything.

`.cache/` is gitignored: it is large and it holds generated text about other
people's repositories.
"""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class CachedResponse:
    """One model response, plus everything needed to audit where it came from."""

    key: str
    model: str
    case_id: str
    protocol_version: int
    prompt_sha256: str
    text: str
    input_tokens: int
    output_tokens: int
    requested_at: str  # ISO-8601 UTC
    run_id: str
    # The prompt itself is stored so a cached result can be re-read and
    # audited without reconstructing the prompt from a since-changed
    # renderer. Claims have to be traceable to an artifact.
    prompt: str
    # The sampling parameters this response was generated under. They reach
    # the provider as API arguments rather than as prompt text, so without
    # this field a cached response could not be audited for what produced
    # it. Also part of the cache key — see `protocol.cache_key`.
    sampling: dict


class ResponseCache:
    def __init__(self, root: Path) -> None:
        self.root = root

    def _path(self, key: str) -> Path:
        # Two-character fan-out: a full corpus pass over many protocol
        # versions puts thousands of files here.
        return self.root / key[:2] / f"{key}.json"

    def get(self, key: str) -> CachedResponse | None:
        path = self._path(key)
        if not path.exists():
            return None
        data = json.loads(path.read_text(encoding="utf-8"))
        return CachedResponse(**data)

    def put(self, response: CachedResponse) -> None:
        """Persist atomically.

        A half-written cache entry read back as a hit would silently poison
        a measurement, so the write goes to a temp file in the same
        directory and is renamed into place.
        """
        path = self._path(response.key)
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(asdict(response), indent=2, sort_keys=True)
        fd, tmp_name = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                handle.write(payload)
            os.replace(tmp_name, path)
        except BaseException:
            Path(tmp_name).unlink(missing_ok=True)
            raise

    def has(self, key: str) -> bool:
        return self._path(key).exists()
