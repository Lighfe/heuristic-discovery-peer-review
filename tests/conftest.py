"""Shared fixtures. No test in this suite touches a provider."""

from __future__ import annotations

import shutil
from datetime import UTC, datetime
from pathlib import Path

import pytest

from loop.config import DEFAULT_CONFIG_PATH, load_config
from loop.gemini import ModelUnavailable, RateLimited, TransportResponse


@pytest.fixture
def repo_root(tmp_path: Path) -> Path:
    """A throwaway repo root with the real config.toml copied in.

    The real config is used deliberately: a test suite against a synthetic
    config would pass while the shipped configuration was unusable.
    """
    loop_dir = tmp_path / "loop"
    loop_dir.mkdir()
    shutil.copy(DEFAULT_CONFIG_PATH, loop_dir / "config.toml")
    return tmp_path


@pytest.fixture
def config(repo_root: Path):
    return load_config(path=repo_root / "loop" / "config.toml", repo_root=repo_root)


class FakeTransport:
    """Scripted provider. Records every call it receives."""

    def __init__(self, *, responses=None, failures=None) -> None:
        self.calls: list[dict] = []
        self._responses = list(responses or [])
        # `failures` is a list of exceptions raised, in order, before any
        # response is served.
        self._failures = list(failures or [])

    def generate(self, *, model, prompt, temperature, max_output_tokens):
        self.calls.append(
            {
                "model": model,
                "prompt": prompt,
                "temperature": temperature,
                "max_output_tokens": max_output_tokens,
            }
        )
        if self._failures:
            raise self._failures.pop(0)
        if self._responses:
            text = self._responses.pop(0)
        else:
            text = f"response-{len(self.calls)}"
        return TransportResponse(
            text=text,
            input_tokens=len(prompt) // 4,
            output_tokens=len(text) // 4,
        )


@pytest.fixture
def fake_transport():
    return FakeTransport


@pytest.fixture
def frozen_clock():
    moment = datetime(2026, 8, 10, 12, 0, 0, tzinfo=UTC)
    return lambda: moment


@pytest.fixture
def no_sleep():
    """Collects requested sleeps instead of performing them."""
    slept: list[float] = []
    return slept, slept.append


__all__ = ["FakeTransport", "ModelUnavailable", "RateLimited"]
