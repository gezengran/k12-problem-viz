"""Matplotlib adapter for Live Photo export."""

from __future__ import annotations

import platform
from pathlib import Path
from unittest.mock import patch

import pytest

from live_photo_export import LiveExportError, export_live_photo_from_matplotlib


def test_matplotlib_adapter_rejects_zero_frames(tmp_path: Path):
    with pytest.raises(LiveExportError, match="at least one frame"):
        export_live_photo_from_matplotlib(lambda i, ax: None, 0, tmp_path / "x")


@pytest.mark.skipif(platform.system() == "Darwin", reason="non-macOS strict failure")
def test_matplotlib_adapter_requires_macos(tmp_path: Path):
    def draw(_i: int, ax) -> None:
        ax.plot([0, 1], [0, 1])

    with pytest.raises(LiveExportError, match="macOS"):
        export_live_photo_from_matplotlib(draw, 3, tmp_path / "demo")


@patch("live_photo_export.export_live_photo_from_frames")
def test_matplotlib_adapter_passes_n_frames(mock_export, tmp_path: Path):
    pvt = tmp_path / "out.pvt"
    pvt.mkdir()
    mock_export.return_value = type("R", (), {"pvt": pvt, "jpg": None, "mov": None})()

    def draw(i: int, ax) -> None:
        ax.plot([0, i], [0, i])

    export_live_photo_from_matplotlib(draw, 5, tmp_path / "stem", fps=12)
    frames_arg = mock_export.call_args[0][0]
    assert len(frames_arg) == 5
    assert mock_export.call_args[1]["fps"] == 12
