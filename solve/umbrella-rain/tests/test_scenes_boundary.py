import pytest

from umbrella_rain.constants import ARM_EXTEND_MAX, BODY_HEIGHT, FRONT_EDGE_X
from umbrella_rain.geometry import rain_intersect_top_mn, rain_line_height_at_x
from umbrella_rain.scenes import (
    scene_b_arm_x_no_foot,
    scene_b_arm_x_no_head,
    scene_b_boundary_no_foot,
    scene_b_boundary_no_head,
    wet_length_scene_b,
)


def test_arm_x_no_head_rain_through_a_at_m():
    pose = scene_b_boundary_no_head()
    a_x, a_y = pose.point_a()
    h = rain_intersect_top_mn(a_x, a_y, 60.0)
    assert h is not None
    assert h[0] == pytest.approx(0.0, abs=0.05)
    assert h[1] == pytest.approx(BODY_HEIGHT)


def test_arm_x_no_foot_k_at_p():
    pose = scene_b_boundary_no_foot()
    cx, cy = pose.point_c()
    y_k = rain_line_height_at_x(cx, cy, FRONT_EDGE_X, 60.0)
    assert y_k == pytest.approx(0.0, abs=0.03)
    assert wet_length_scene_b(scene_b_arm_x_no_foot(), 60.0) == pytest.approx(0.0, abs=0.03)


def test_no_head_x_in_valid_range():
    x = scene_b_arm_x_no_head(60.0)
    assert 0 <= x <= ARM_EXTEND_MAX


def test_no_foot_x_beyond_arm_max_is_ideal_boundary():
    x = scene_b_arm_x_no_foot(60.0)
    assert x > ARM_EXTEND_MAX
