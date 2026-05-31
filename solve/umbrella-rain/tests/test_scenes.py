import math

import pytest

from umbrella_rain.constants import ARM_EXTEND_MAX
from umbrella_rain.scenes import (
    head_dry_analysis,
    height_c_above_ground,
    min_eg_for_dry_scene_c,
    scene_a,
    wet_length_scene_a,
    wet_length_scene_b,
    wet_length_scene_c,
)


def test_height_c_above_ground_scene_a():
    assert height_c_above_ground(scene_a()) == pytest.approx(1.8)


def test_wet_length_scene_a_72():
    assert wet_length_scene_a(72.0) == pytest.approx(0.26, abs=0.03)


def test_wet_length_scene_b_at_zero():
    y0 = wet_length_scene_b(0.0, 60.0)
    assert y0 == pytest.approx(1.8 - 0.5 * math.sqrt(3), abs=0.01)


def test_wet_length_scene_b_decreases_with_x():
    y0 = wet_length_scene_b(0.0, 60.0)
    y1 = wet_length_scene_b(0.25, 60.0)
    y2 = wet_length_scene_b(ARM_EXTEND_MAX, 60.0)
    assert y0 > y1 > y2


def test_wet_length_scene_b_at_quarter():
    y = wet_length_scene_b(0.25, 60.0)
    assert y == pytest.approx(1.8 - math.sqrt(3) * 0.75, abs=0.01)


def test_head_dry_exists_in_arm_range():
    result = head_dry_analysis(60.0)
    assert result.any_head_dry_in_range is True
    assert "x <=" in result.message


def test_min_eg_scene_c_exists_in_range():
    result = min_eg_for_dry_scene_c(60.0)
    assert result.exists is True
    assert result.min_eg is not None
    assert 0.0 <= result.min_eg <= ARM_EXTEND_MAX
    assert result.min_eg == pytest.approx(0.20, abs=0.03)


def test_scene_c_dry_at_min_eg():
    result = min_eg_for_dry_scene_c(60.0)
    assert result.min_eg is not None
    pk = wet_length_scene_c(result.min_eg, 60.0)
    assert pk == pytest.approx(0.0, abs=0.02)
