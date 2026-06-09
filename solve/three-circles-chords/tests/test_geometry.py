import math

import pytest

from three_circles_chords.constants import EPS
from three_circles_chords.geometry import (
    IntersectionKind,
    line_chord_state,
    maximize_sum_at_b_zero,
)


def test_chord_lengths_at_k_sqrt3_b_zero_equal():
    """Symmetric pose: s1 = s2 = s3 = 1."""
    state = line_chord_state(math.sqrt(3.0), 0.0)
    s1, s2, s3 = state.lengths
    assert s1 == pytest.approx(1.0, abs=1e-4)
    assert s2 == pytest.approx(1.0, abs=1e-4)
    assert s3 == pytest.approx(1.0, abs=1e-4)


def test_tangent_circle_has_zero_chord_length():
    """At envelope boundary one circle is tangent → chord length 0."""
    k = 0.0
    # b where C1 is tangent: |b| = 1 for horizontal line.
    state = line_chord_state(k, 1.0)
    assert state.chords[0].kind == IntersectionKind.TANGENT
    assert state.chords[0].length == pytest.approx(0.0, abs=EPS)


def test_line_through_center_gives_diameter_chord():
    """Horizontal through C1 center (-1,0): chord length 2."""
    state = line_chord_state(0.0, 0.0)
    assert state.chords[0].kind == IntersectionKind.SECANT
    assert state.chords[0].length == pytest.approx(2.0, abs=1e-4)


def test_all_three_secant_in_interior_pose():
    state = line_chord_state(math.sqrt(3.0), 0.0)
    assert state.all_secant
    assert all(c.endpoints is not None for c in state.chords)


def test_b_zero_sum_has_numerical_maximum():
    k_star, max_sum = maximize_sum_at_b_zero()
    assert abs(k_star) > math.sqrt(2.0)
    assert max_sum == pytest.approx(2.0 * math.sqrt(21.0) / 3.0, abs=0.02)
    # Nearby k should not exceed the peak.
    for delta in (-0.3, -0.1, 0.1, 0.3):
        nearby = line_chord_state(k_star + delta, 0.0)
        if nearby.all_secant:
            assert nearby.sum_lengths <= max_sum + 0.02
