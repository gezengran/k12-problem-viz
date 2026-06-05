"""Live Photo export guard (task 7 — optional packaging)."""

from __future__ import annotations

import platform
from pathlib import Path

import pytest
from PIL import Image

from live_photo_export import LiveExportError, export_live_photo_from_frames


@pytest.mark.skipif(platform.system() == "Darwin", reason="non-macOS strict failure")
def test_live_export_requires_macos(tmp_path: Path):
    frames = [Image.new("RGB", (540, 960), (200, 220, 240))]
    with pytest.raises(LiveExportError, match="macOS"):
        export_live_photo_from_frames(frames, tmp_path / "plank_preset1_live")
