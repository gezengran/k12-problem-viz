"""Shared path helpers for all problem cases."""

from __future__ import annotations

from pathlib import Path

_CASE_ROOT = Path(__file__).resolve().parents[2]


def project_root() -> Path:
    return _CASE_ROOT


def ami_dir(case_id: str) -> Path:
    directory = project_root() / "ami" / case_id
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def solve_case_dir(case_id: str) -> Path:
    return project_root() / "solve" / case_id
