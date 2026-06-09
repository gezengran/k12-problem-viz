import math

import pytest

from three_circles_chords.constraints import (
    SUM_TARGET_C,
    b_zero_peak_info,
    chords_equal,
    equal_chord_solutions,
    k_scan_to_boundary,
    k_triple_secant_intervals,
    sample_sum_locus,
)
from three_circles_chords.constants import OPTION_A_B
from three_circles_chords.geometry import (
    IntersectionKind,
    line_chord_state,
    maximize_sum_at_b_zero,
)


def test_equal_chord_solutions_are_exactly_three():
    sols = equal_chord_solutions()
    assert len(sols) == 3
    for k, b in sols:
        assert chords_equal(k, b)
    assert not chords_equal(1.0, 0.0)


def test_equal_chord_analytic_horizontal_solution():
    sqrt3 = math.sqrt(3.0)
    k, b = 0.0, sqrt3 / 2.0
    assert chords_equal(k, b)
    s1, s2, s3 = line_chord_state(k, b).lengths
    assert s1 == pytest.approx(s2, abs=1e-4)
    assert s2 == pytest.approx(s3, abs=1e-4)


def test_k_scan_reaches_tangent_boundary():
    scan = k_scan_to_boundary(OPTION_A_B, direction=1.0)
    assert line_chord_state(scan.k_interior, scan.b).all_secant
    boundary = line_chord_state(scan.k_boundary, scan.b)
    kinds = {c.kind for c in boundary.chords}
    assert IntersectionKind.TANGENT in kinds or IntersectionKind.NONE in kinds


def test_sum_locus_has_multiple_distinct_poses():
    poses = sample_sum_locus(SUM_TARGET_C)
    assert len(poses) >= 5
    sums = {round(line_chord_state(k, b).sum_lengths, 3) for k, b in poses}
    assert len(sums) == 1
    ks = {round(k, 2) for k, _ in poses}
    assert len(ks) >= 3


def test_b_zero_peak_matches_geometry_scan():
    info = b_zero_peak_info()
    _, ref = maximize_sum_at_b_zero()
    assert info.sum_peak == pytest.approx(ref, abs=0.02)
    assert info.sum_peak == pytest.approx(2.0 * math.sqrt(21.0) / 3.0, abs=0.03)
    peak_state = line_chord_state(info.k_peak, 0.0)
    low_state = line_chord_state(info.k_low_sum, 0.0)
    past_state = line_chord_state(info.k_past_peak, 0.0)
    assert peak_state.sum_lengths > low_state.sum_lengths
    assert past_state.sum_lengths < peak_state.sum_lengths - 0.01


def test_k_intervals_nonempty_at_option_a_b():
    assert len(k_triple_secant_intervals(OPTION_A_B)) >= 1
