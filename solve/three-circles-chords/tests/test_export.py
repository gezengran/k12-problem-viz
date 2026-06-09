import platform

import pytest
from live_photo_export import LiveExportError

from paths import ami_dir
from three_circles_chords.constants import CASE_ID
from three_circles_chords.export import (
    capture_timeline_frames,
    export_all_options,
    export_option_live,
    still_aspect_ratio,
)
from three_circles_chords.scenes import OPTION_LETTERS, export_basename
from three_circles_chords.timeline import build_option_frames
from three_circles_chords.viz import portrait_aspect_ratio


def test_capture_option_timeline_produces_portrait_frames():
    frames = capture_timeline_frames(build_option_frames("A")[:3])
    assert len(frames) == 3
    w, h = frames[0].size
    assert h / w == pytest.approx(portrait_aspect_ratio(), rel=0.08)


@pytest.mark.skipif(platform.system() == "Darwin", reason="non-macOS contract")
def test_export_option_live_raises_on_non_macos():
    with pytest.raises(LiveExportError, match="macOS"):
        export_option_live("A")


@pytest.mark.slow
@pytest.mark.skipif(platform.system() != "Darwin", reason="Live Photo export requires macOS")
@pytest.mark.skipif(
    platform.system() == "Darwin" and __import__("os").getenv("CI") == "true",
    reason="makelive integration flaky in CI sandbox",
)
def test_export_all_options_to_ami():
    outputs = export_all_options()
    assert set(outputs) == set(OPTION_LETTERS)
    root = ami_dir(CASE_ID)
    for letter in OPTION_LETTERS:
        pvt = outputs[letter]
        assert pvt.suffix == ".pvt"
        assert pvt.name == f"{export_basename(letter)}.pvt"
        assert pvt.parent == root
        assert still_aspect_ratio(pvt) == pytest.approx(4.0 / 3.0, rel=0.05)
