import pytest

from umbrella_rain.constants import ARM_EXTEND_MAX, BODY_HEIGHT
from umbrella_rain.geometry import rain_intersect_top_mn
from umbrella_rain.scenes import (
    build_scene_c_eg_timeline,
    scene_c,
    scene_c_eg_h_at_m,
    scene_c_eg_k_at_foot,
    wet_length_scene_c,
)


def test_scene_c_eg_k_at_foot():
    e = scene_c_eg_k_at_foot(60.0)
    assert wet_length_scene_c(e, 60.0) == pytest.approx(0.0, abs=0.02)
    if e > 0.03:
        assert wet_length_scene_c(e - 0.03, 60.0) > 0.01


def test_scene_c_eg_h_at_m():
    e = scene_c_eg_h_at_m(60.0)
    pose = scene_c(e, 60.0)
    hit = rain_intersect_top_mn(*pose.point_a(), 60.0)
    assert hit is not None
    assert hit[0] == pytest.approx(0.0, abs=0.01)
    assert hit[1] == pytest.approx(BODY_HEIGHT)


def test_scene_c_k_before_h_in_timeline():
    assert scene_c_eg_k_at_foot(60.0) < scene_c_eg_h_at_m(60.0)


def test_scene_c_timeline_endpoints_and_monotonic():
    eg = build_scene_c_eg_timeline(30, slow_factor=0.25)
    assert eg[0] == pytest.approx(0.0)
    assert eg[-1] == pytest.approx(ARM_EXTEND_MAX)
    for a, b in zip(eg, eg[1:]):
        assert a <= b + 1e-12


def test_scene_c_timeline_slow_zone_has_higher_frame_density():
    e_k = scene_c_eg_k_at_foot(60.0)
    e_h = scene_c_eg_h_at_m(60.0)
    eg = build_scene_c_eg_timeline(60, slow_factor=0.25)
    in_slow = sum(1 for e in eg if e_k - 1e-6 <= e <= e_h + 1e-6)
    out_slow = len(eg) - in_slow
    span_slow = max(e_h - e_k, 1e-9)
    span_fast = max((e_k - 0.0) + (ARM_EXTEND_MAX - e_h), 1e-9)
    density_slow = in_slow / span_slow
    density_fast = out_slow / span_fast
    assert density_slow > density_fast * 2.5
