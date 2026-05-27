from pathlib import Path

import pytest
from PIL import Image

from paths import ami_dir
from umbrella_rain.constants import BODY_HEIGHT, CASE_ID, FRONT_EDGE_X
from umbrella_rain.geometry import rain_line_height_at_x
from umbrella_rain.scenes import scene_a, scene_b
from umbrella_rain.viz import (
    export_all_media,
    export_boundary_static_suite,
    export_static,
    portrait_aspect_ratio,
    rain_segment_span,
    render_frame,
)
from umbrella_rain.viz_layers import rain_line_segment_through_point


def test_portrait_aspect_ratio():
    assert portrait_aspect_ratio() == pytest.approx(16 / 9, rel=0.01)


def test_render_frame_no_exception():
    fig = render_frame(scene_a(), 72.0)
    assert fig is not None
    w_in, h_in = fig.get_size_inches()
    assert h_in / w_in == pytest.approx(16 / 9, rel=0.01)
    import matplotlib.pyplot as plt

    plt.close(fig)


def test_rain_line_through_c_spans_viewport_and_hits_body():
    pose = scene_b(0.0)
    cx, cy = pose.point_c()
    p1, p2 = rain_line_segment_through_point(cx, cy, 60.0)
    span = ((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2) ** 0.5
    assert span > 1.8
    y_k = rain_line_height_at_x(cx, cy, FRONT_EDGE_X, 60.0)
    assert 0 < y_k < BODY_HEIGHT


def test_rain_segment_longer_than_old_default():
    pose = scene_b(0.25)
    assert rain_segment_span(pose, 60.0) > 1.5


def test_head_wet_when_intersection_above_body_top():
    pose = scene_b(0.0)
    cx, cy = pose.point_c()
    y_k = rain_line_height_at_x(cx, cy, FRONT_EDGE_X, 15.0)
    assert y_k >= BODY_HEIGHT


def test_render_animation_style_no_crash():
    fig = render_frame(scene_b(0.3), 60.0, animation_style=True)
    import matplotlib.pyplot as plt

    plt.close(fig)


def test_export_boundary_static_b_and_c(tmp_path: Path):
    outputs = export_boundary_static_suite(tmp_path)
    assert outputs["b_boundary_no_head"].exists()
    assert outputs["b_boundary_no_foot"].exists()
    assert outputs["c_boundary"].exists()
    assert outputs["b_boundary_no_head"].stat().st_size > 1000


def test_export_static_boundary_aspect(tmp_path: Path):
    out = export_static(
        scene_b(0.25),
        60.0,
        tmp_path / "b.png",
        boundary=True,
        scene="b",
    )
    img = Image.open(out)
    w, h = img.size
    assert h / w == pytest.approx(16 / 9, rel=0.05)


@pytest.mark.slow
def test_export_all_media_to_ami():
    out_dir = ami_dir(CASE_ID)
    outputs = export_all_media(out_dir)
    assert outputs["b_boundary_no_head"].exists()
    assert outputs["b_boundary_no_foot"].exists()
    assert outputs["c_boundary"].exists()
    assert outputs["scene_b"].suffix == ".gif"
    assert outputs["scene_c"].suffix == ".gif"
    assert outputs["scene_b"].stat().st_size > 5000
    assert "scene_a" not in outputs
    assert "b_boundary" not in outputs
