"""Tests for block–plank contact geometry."""

from plank_block_friction.constants import (
    BLOCK_CENTER_OFFSET_MIN,
    BLOCK_INITIAL_CENTER_OFFSET,
    BLOCK_WIDTH,
    PLANK_LENGTH,
)
from plank_block_friction.contact import (
    block_center_offset,
    display_block_center,
    first_leave_plank_time,
    is_block_on_plank,
)
from plank_block_friction.presets import sim_config_for_preset
from plank_block_friction.simulation import run_simulation


def test_block_starts_at_plank_center():
    traj = run_simulation(sim_config_for_preset("preset-1"), 0.01)
    s0 = traj.samples[0]
    assert abs(block_center_offset(s0.x_block, s0.x_plank) - BLOCK_INITIAL_CENTER_OFFSET) < 1e-6
    assert abs(BLOCK_INITIAL_CENTER_OFFSET - PLANK_LENGTH / 2) < 1e-6


def test_block_is_square():
    from plank_block_friction.constants import BLOCK_HEIGHT

    assert BLOCK_HEIGHT == BLOCK_WIDTH


def test_leave_happens_before_co_speed_for_preset1():
    cfg = sim_config_for_preset("preset-1")
    traj = run_simulation(cfg, 5.0)
    t_leave = first_leave_plank_time(traj)
    assert traj.t_sync is not None
    assert t_leave < traj.t_sync
    assert 0.02 < t_leave < 0.5


def test_display_keeps_center_while_on_plank():
    x_plank = 0.0
    x_block = BLOCK_INITIAL_CENTER_OFFSET
    assert display_block_center(x_block, x_plank) == x_block


def test_on_plank_span():
    x_p = 1.0
    assert is_block_on_plank(x_p + BLOCK_CENTER_OFFSET_MIN, x_p)
    assert is_block_on_plank(x_p + PLANK_LENGTH - BLOCK_WIDTH / 2, x_p)
    assert not is_block_on_plank(x_p - 0.1, x_p)
