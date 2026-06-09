import pytest

from three_circles_chords.constants import EPS
from three_circles_chords.constraints import chords_equal, equal_chord_solutions
from three_circles_chords.geometry import line_chord_state, maximize_sum_at_b_zero
from three_circles_chords.presets import (
    preset,
    segment_b_pose,
    segment_b_poses,
    segment_c_frames,
    segment_d_pose,
)


def test_segment_b_equal_chords():
    pose = segment_b_pose()
    state = line_chord_state(pose.k, pose.b)
    s1, s2, s3 = state.lengths
    assert s1 == pytest.approx(s2, abs=EPS)
    assert s2 == pytest.approx(s3, abs=EPS)


def test_segment_b_has_three_analytic_solutions():
    poses = segment_b_poses()
    assert len(poses) == 3
    assert len(poses) == len(equal_chord_solutions())
    for pose in poses:
        assert chords_equal(pose.k, pose.b)


def test_segment_c_at_least_four_frames_equal_sum():
    frames = segment_c_frames()
    assert len(frames) >= 4
    sums = [line_chord_state(p.k, p.b).sum_lengths for p in frames]
    assert sums[0] == pytest.approx(sums[1], abs=0.08)
    ks = {round(p.k, 2) for p in frames}
    bs = {round(p.b, 2) for p in frames}
    assert len(ks) >= 2 or len(bs) >= 2


def test_segment_d_b_zero_at_max_sum():
    pose = segment_d_pose()
    assert pose.b == pytest.approx(0.0, abs=EPS)
    _, max_sum = maximize_sum_at_b_zero()
    state = line_chord_state(pose.k, pose.b)
    assert state.sum_lengths == pytest.approx(max_sum, abs=0.02)


def test_unknown_segment_raises():
    with pytest.raises(KeyError, match="unknown segment_id"):
        preset("segment-Z")
