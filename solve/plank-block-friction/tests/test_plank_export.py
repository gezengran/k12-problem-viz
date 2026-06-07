"""Tests for MP4 export."""

import pytest
from paths import ami_dir

from plank_block_friction.constants import (
    CASE_ID,
    CLASSIC_PRESET_ID,
    VIEW_BLOCK,
    VIEW_GROUND,
    VIEW_PLANK,
)
from plank_block_friction.export import (
    export_classic_preset1,
    export_view_mp4,
    view_output_stem,
)


@pytest.mark.slow
def test_export_classic_preset1_full():
    paths = export_classic_preset1()
    assert set(paths) == {VIEW_GROUND, VIEW_BLOCK, VIEW_PLANK}
    for view, path in paths.items():
        assert path.suffix == ".mp4"
        assert path.is_file()
        assert path.stat().st_size > 8000
        assert path.name == f"{view_output_stem(CLASSIC_PRESET_ID, view)}.mp4"


def test_export_view_mp4_smoke(tmp_path):
    for view in (VIEW_GROUND, VIEW_BLOCK, VIEW_PLANK):
        path = export_view_mp4(
            CLASSIC_PRESET_ID,
            view,
            tmp_path / f"preset-1-{view}.mp4",
            n_frames=12,
        )
        assert path.exists()
        assert path.stat().st_size > 800


def test_ami_dir_case_name():
    assert ami_dir(CASE_ID).name == CASE_ID
