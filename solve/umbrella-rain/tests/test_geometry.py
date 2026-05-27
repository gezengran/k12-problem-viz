import math

import pytest

from umbrella_rain.geometry import wet_length_pk


def test_pk_scene_a_golden_72_degrees():
    pk = wet_length_pk(0.7, 1.8, 72.0)
    expected = 1.8 - 0.5 * math.tan(math.radians(72.0))
    assert pk == pytest.approx(expected, abs=0.02)
    assert pk == pytest.approx(0.26, abs=0.03)


def test_pk_zero_when_intersection_below_ground():
    pk = wet_length_pk(0.7, 0.1, 72.0)
    assert pk == 0.0


def test_pk_clamped_to_body_height():
  pk = wet_length_pk(0.7, 5.0, 60.0)
  assert pk == 1.6


def test_pk_60_degrees_at_initial_c():
  pk = wet_length_pk(0.7, 1.8, 60.0)
  assert pk == pytest.approx(1.8 - 0.5 * math.sqrt(3), abs=0.01)
