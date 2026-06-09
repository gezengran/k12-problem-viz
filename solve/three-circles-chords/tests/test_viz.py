from pathlib import Path

import matplotlib.pyplot as plt
import pytest
from PIL import Image

from paths import ami_dir
from three_circles_chords.constants import CASE_ID
from three_circles_chords.viz import (
    count_chord_artists,
    portrait_aspect_ratio,
    render_frame,
    save_frame_png,
)


def test_render_frame_no_exception():
    fig = render_frame(0.5, 0.2)
    assert fig is not None
    w_in, h_in = fig.get_size_inches()
    assert h_in / w_in == pytest.approx(portrait_aspect_ratio(), rel=0.01)
    plt.close(fig)


def test_render_frame_portrait_aspect():
    assert portrait_aspect_ratio() == pytest.approx(4.0 / 3.0, rel=0.01)


def test_three_chords_drawn_for_secant_pose():
    fig = render_frame(-1.4, 0.2)
    assert count_chord_artists(fig) == 3
    plt.close(fig)


def test_save_frame_png_to_ami(tmp_path: Path):
    out = ami_dir(CASE_ID) / "test_frame.png"
    save_frame_png(0.5, 0.2, out)
    assert out.exists()
    assert out.stat().st_size > 500
    img = Image.open(out)
    w, h = img.size
    assert h / w == pytest.approx(4.0 / 3.0, rel=0.08)


def test_badge_rendered():
    fig = render_frame(0.5, 0.2, badge="B")
    texts = [t.get_text() for t in fig.axes[0].texts]
    assert "B" in texts
    plt.close(fig)


def test_coordinate_axes_visible():
    from three_circles_chords.viz import has_coordinate_axes

    fig = render_frame(-1.4, 0.2)
    assert has_coordinate_axes(fig)
    plt.close(fig)


def test_caption_rendered():
    fig = render_frame(0.5, 0.2, caption="test caption")
    texts = [t.get_text() for t in fig.axes[0].texts]
    assert "test caption" in texts
    plt.close(fig)
