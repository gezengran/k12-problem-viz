"""Tests for Xiaohongshu Live Photo (.pvt) export."""

from __future__ import annotations

import platform
from pathlib import Path
from unittest.mock import patch

import pytest
from PIL import Image

from live_photo_export import (
    LIVE_PHOTO_SIZE,
    LiveExportError,
    export_live_photo_from_frames,
    letterbox_image,
)


def _rgb_frames(n: int = 3, color: tuple[int, int, int] = (120, 80, 200)) -> list[Image.Image]:
    return [Image.new("RGB", (540, 960), color) for _ in range(n)]


def test_letterbox_image_default_size():
    img = Image.new("RGB", (720, 1280), (200, 200, 200))
    boxed = letterbox_image(img)
    assert boxed.size == LIVE_PHOTO_SIZE


def test_export_live_photo_rejects_empty_frames(tmp_path: Path):
    with pytest.raises(LiveExportError, match="at least one frame"):
        export_live_photo_from_frames([], tmp_path / "demo")


@pytest.mark.skipif(platform.system() == "Darwin", reason="non-macOS strict failure")
def test_export_live_photo_requires_macos(tmp_path: Path):
    with pytest.raises(LiveExportError, match="macOS"):
        export_live_photo_from_frames(_rgb_frames(), tmp_path / "demo")


@patch("live_photo_export._save_mov_from_frames")
@patch("live_photo_export._require_darwin")
@patch("live_photo_export.save_live_photo_pair_as_pvt")
def test_keep_intermediates_false_removes_jpg_mov(
    mock_pvt,
    _mock_darwin,
    mock_mov,
    tmp_path: Path,
):
    base = tmp_path / "stem"
    pvt_dir = tmp_path / "stem.pvt"
    pvt_dir.mkdir()
    mock_pvt.return_value = (None, pvt_dir)
    mock_mov.side_effect = lambda frames, path, fps: path

    result = export_live_photo_from_frames(
        _rgb_frames(2),
        base,
        fps=10,
        keep_intermediates=False,
    )

    assert result.pvt == pvt_dir
    assert not base.with_suffix(".jpg").exists()
    assert not base.with_suffix(".mov").exists()
    assert result.jpg is None
    assert result.mov is None


@patch("live_photo_export._save_mov_from_frames")
@patch("live_photo_export._require_darwin")
@patch("live_photo_export.save_live_photo_pair_as_pvt")
def test_keep_intermediates_true_keeps_jpg_mov(
    mock_pvt,
    _mock_darwin,
    mock_mov,
    tmp_path: Path,
):
    base = tmp_path / "stem"
    pvt_dir = tmp_path / "stem.pvt"
    pvt_dir.mkdir()
    mock_pvt.return_value = (None, pvt_dir)
    def _write_mov(frames, path, fps):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"mock-mov")
        return path

    mock_mov.side_effect = _write_mov

    result = export_live_photo_from_frames(
        _rgb_frames(2),
        base,
        fps=10,
        keep_intermediates=True,
    )

    assert base.with_suffix(".jpg").exists()
    assert base.with_suffix(".mov").exists()
    assert result.jpg == base.with_suffix(".jpg")
    assert result.mov == base.with_suffix(".mov")


@pytest.mark.slow
@pytest.mark.skipif(platform.system() != "Darwin", reason="Live Photo export needs macOS")
def test_export_live_photo_end_to_end(tmp_path: Path):
    result = export_live_photo_from_frames(
        _rgb_frames(3, (40, 120, 200)),
        tmp_path / "demo",
        fps=10,
    )
    assert result.pvt.suffix == ".pvt"
    assert result.pvt.is_dir()
    assert result.jpg is not None and result.jpg.exists()
    assert result.mov is not None and result.mov.exists()
