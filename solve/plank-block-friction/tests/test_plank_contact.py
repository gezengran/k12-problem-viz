"""Tests for block–plank contact geometry."""

from plank_block_friction.constants import (
    BLOCK_CENTER_OFFSET_MAX,
    BLOCK_CENTER_OFFSET_MIN,
    BLOCK_INITIAL_CENTER_OFFSET,
    BLOCK_INITIAL_OFFSET_FRAC,
)
from plank_block_friction.contact import (
    block_center_offset,
    display_block_center,
    is_block_on_plank,
)
from plank_block_friction.presets import animation_duration, sim_config_for_preset
from plank_block_friction.simulation import run_simulation


def test_block_starts_right_of_plank_left_edge():
    traj = run_simulation(sim_config_for_preset("preset-1"), 0.01)
    s0 = traj.samples[0]
    expected = BLOCK_CENTER_OFFSET_MIN + BLOCK_INITIAL_OFFSET_FRAC * (
        BLOCK_CENTER_OFFSET_MAX - BLOCK_CENTER_OFFSET_MIN
    )
    assert abs(BLOCK_INITIAL_CENTER_OFFSET - expected) < 1e-6
    assert abs(block_center_offset(s0.x_block, s0.x_plank) - expected) < 1e-6
    mid = (BLOCK_CENTER_OFFSET_MIN + BLOCK_CENTER_OFFSET_MAX) / 2
    assert BLOCK_INITIAL_CENTER_OFFSET >= mid


def test_block_is_square():
    from plank_block_friction.constants import BLOCK_HEIGHT, BLOCK_WIDTH

    assert BLOCK_HEIGHT == BLOCK_WIDTH


def test_block_stays_on_plank_through_full_animation():
    for pid in ("preset-1", "preset-2", "preset-3"):
        cfg = sim_config_for_preset(pid)
        dur = animation_duration(pid)
        traj = run_simulation(cfg, dur)
        for sample in traj.samples:
            assert is_block_on_plank(sample.x_block, sample.x_plank)


def test_display_keeps_center_while_on_plank():
    x_plank = 0.0
    x_block = BLOCK_INITIAL_CENTER_OFFSET
    assert display_block_center(x_block, x_plank) == x_block


def test_on_plank_span():
    from plank_block_friction.constants import BLOCK_WIDTH, PLANK_LENGTH

    x_p = 1.0
    assert is_block_on_plank(x_p + BLOCK_CENTER_OFFSET_MIN, x_p)
    assert is_block_on_plank(x_p + PLANK_LENGTH - BLOCK_WIDTH / 2, x_p)
    assert not is_block_on_plank(x_p - 0.1, x_p)
