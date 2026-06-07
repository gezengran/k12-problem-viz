"""Live Photo export for preset-1 views."""

from __future__ import annotations

import platform
from pathlib import Path

import pytest
from PIL import Image

from live_photo_export import LiveExportError, export_live_photo_from_frames
from plank_block_friction.constants import CLASSIC_PRESET_ID, VIEW_BLOCK, VIEW_GROUND, VIEW_PLANK
from plank_block_friction.export import export_view_live, live_output_stem


@pytest.mark.skipif(platform.system() == "Darwin", reason="non-macOS strict failure")
def test_live_export_requires_macos(tmp_path: Path):
    frames = [Image.new("RGB", (540, 960), (200, 220, 240))]
    with pytest.raises(LiveExportError, match="macOS"):
        export_live_photo_from_frames(frames, tmp_path / "plank_preset1_live")


@pytest.mark.slow
@pytest.mark.skipif(platform.system() != "Darwin", reason="Live Photo export needs macOS")
def test_export_view_live_smoke(tmp_path: Path):
    pvt = export_view_live(
        CLASSIC_PRESET_ID,
        VIEW_GROUND,
        tmp_path / live_output_stem(CLASSIC_PRESET_ID, VIEW_GROUND),
        n_frames=8,
    )
    assert pvt.suffix == ".pvt"
    assert pvt.is_dir()


@pytest.mark.slow
@pytest.mark.skipif(platform.system() != "Darwin", reason="Live Photo export needs macOS")
def test_export_view_live_drops_intermediates(tmp_path: Path):
    stem = tmp_path / live_output_stem(CLASSIC_PRESET_ID, VIEW_BLOCK)
    pvt = export_view_live(
        CLASSIC_PRESET_ID,
        VIEW_BLOCK,
        stem,
        n_frames=8,
        keep_intermediates=False,
    )
    assert pvt.suffix == ".pvt"
    assert not stem.with_suffix(".jpg").exists()
    assert not stem.with_suffix(".mov").exists()


@pytest.mark.slow
@pytest.mark.skipif(platform.system() != "Darwin", reason="Live Photo export needs macOS")
def test_export_classic_preset1_live_all_views(tmp_path: Path):
    from plank_block_friction.export import export_classic_preset1_live

    paths = export_classic_preset1_live(tmp_path, n_frames=8)
    assert set(paths) == {VIEW_GROUND, VIEW_BLOCK, VIEW_PLANK}
    for view, pvt in paths.items():
        assert pvt.suffix == ".pvt"
        assert pvt.is_dir()
        assert pvt.name == f"{live_output_stem(CLASSIC_PRESET_ID, view)}.pvt"
