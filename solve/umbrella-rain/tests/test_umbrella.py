import pytest

from umbrella_rain.constants import FRONT_EDGE_X, HAND_HEIGHT
from umbrella_rain.geometry import wet_length_from_pose
from umbrella_rain.umbrella import UmbrellaPose


def test_scene_a_hand_and_center_heights():
    pose = UmbrellaPose.scene_a()
    gx, gy = pose.hand_position()
    assert gx == pytest.approx(FRONT_EDGE_X)
    assert gy == pytest.approx(HAND_HEIGHT)
    assert pose.height_c_above_ground() == pytest.approx(1.8)


def test_scene_a_og_collinear_with_np():
    pose = UmbrellaPose.scene_a()
    gx, _ = pose.hand_position()
    ox, _ = pose.point_o()
    assert gx == pytest.approx(ox)
    assert gx == pytest.approx(FRONT_EDGE_X)


def test_scene_b_arm_extend_parallel_og():
    pose = UmbrellaPose.scene_b(0.3)
    gx, gy = pose.hand_position()
    ox, oy = pose.point_o()
    assert gx == pytest.approx(ox)
    assert gx == pytest.approx(FRONT_EDGE_X + 0.3)
    assert oy - gy == pytest.approx(0.45)


def test_scene_c_ac_perpendicular_to_rain():
    pose = UmbrellaPose.scene_c(0.0, 60.0)
    assert pose.ac_perpendicular_to_rain(60.0)


def test_wet_length_from_pose_matches_manual():
    pose = UmbrellaPose.scene_a()
    pk = wet_length_from_pose(pose, 72.0)
    assert pk == pytest.approx(0.26, abs=0.03)
