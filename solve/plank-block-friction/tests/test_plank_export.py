"""Tests for MP4 export."""

import pytest
from paths import ami_dir

from plank_block_friction.constants import CASE_ID
from plank_block_friction.export import export_mp4


@pytest.mark.slow
def test_export_preset1_mp4_full():
    path = export_mp4("preset-1")
    assert path.suffix == ".mp4"
    assert path.is_file()
    assert path.stat().st_size > 10_000


def test_export_preset1_mp4_smoke(tmp_path):
    path = export_mp4("preset-1", tmp_path / "short.mp4", n_frames=12)
    assert path.exists()
    assert path.stat().st_size > 1000


def test_export_all_presets_smoke(tmp_path):
    # Redirect by passing paths via individual exports in tmp
    paths = {}
    for pid in ("preset-1", "preset-2", "preset-3"):
        paths[pid] = export_mp4(pid, tmp_path / f"{pid}.mp4", n_frames=10)
    assert len(paths) == 3
    for p in paths.values():
        assert p.stat().st_size > 500


def test_ami_dir_case_name():
    assert ami_dir(CASE_ID).name == CASE_ID
