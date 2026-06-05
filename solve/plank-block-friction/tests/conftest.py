"""Pytest configuration for plank-block-friction case."""

from __future__ import annotations

import sys
from pathlib import Path

_CASE_DIR = Path(__file__).resolve().parents[1]
if str(_CASE_DIR) not in sys.path:
    sys.path.insert(0, str(_CASE_DIR))

_COMMON = _CASE_DIR.parents[1] / "_common"
if str(_COMMON) not in sys.path:
    sys.path.insert(0, str(_COMMON))
