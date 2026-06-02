"""Tests for curve intersection and animation schedule."""

from compound_growth.math_model import (
    all_crossings,
    ease_out_power,
    frame_near_crossing,
    gap,
    plot_x_max,
    primary_crossing,
    progress_schedule,
    small_crossing,
    x_progress_for_frame,
)


def test_two_crossings_exist():
    roots = all_crossings()
    assert len(roots) >= 2


def test_small_crossing_near_one():
    x_small = small_crossing()
    assert 0.5 < x_small < 2.0
    assert abs(gap(x_small)) < 1e-4


def test_primary_crossing_is_large_overtake_point():
    x_small = small_crossing()
    x_large = primary_crossing()
    assert x_large > 500.0
    assert x_large > x_small * 100
    assert abs(gap(x_large)) < 1e-2


def test_plot_x_max_frames_primary_crossing():
    assert plot_x_max() > primary_crossing()


def test_ease_out_power_monotonic():
    values = [ease_out_power(i / 20) for i in range(21)]
    for prev, curr in zip(values, values[1:]):
        assert curr >= prev


def test_early_segment_covers_range_quickly():
    x_max = plot_x_max()
    n = 48
    x_early = x_progress_for_frame(int(n * 0.28), n, x_max)
    assert x_early > x_max * 0.55


def test_progress_schedule_monotonic():
    x_max = plot_x_max()
    u_cross = primary_crossing() / x_max
    schedule = progress_schedule(48, u_cross)
    assert len(schedule) == 48
    assert schedule[0] == 0.0
    assert schedule[-1] == 1.0
    for prev, curr in zip(schedule, schedule[1:]):
        assert curr >= prev


def test_many_frames_in_slow_crossing_band():
    x_max = plot_x_max()
    x_star = primary_crossing()
    n = 48
    in_band = 0
    for i in range(n):
        x_end = x_progress_for_frame(i, n, x_max)
        if x_star * 0.94 <= x_end <= x_star * 1.04:
            in_band += 1
    assert in_band >= 10


def test_some_frames_cluster_near_primary_crossing():
    near = [i for i in range(48) if frame_near_crossing(i, 48)]
    assert len(near) >= 2
