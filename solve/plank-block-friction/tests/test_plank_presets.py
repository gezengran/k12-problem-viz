import pytest

from plank_block_friction.presets import (
    animation_duration,
    get_preset,
    sim_config_for_preset,
)


def test_preset1_parameters():
    p = get_preset("preset-1")
    assert p.mu1 == 0.0
    assert p.mu2 == 0.2
    assert p.tail_seconds == 1.0


def test_preset2_parameters():
    p = get_preset("preset-2")
    assert p.mu2 == 0.6
    assert p.tail_seconds == 1.0


def test_preset3_parameters():
    p = get_preset("preset-3")
    assert p.mu1 == 0.15
    assert p.mu2 == 0.2
    assert p.tail_seconds == 2.0


def test_unknown_preset_raises():
    with pytest.raises(KeyError):
        get_preset("preset-99")


def test_animation_duration_ends_after_block_leaves_plank():
    from plank_block_friction.constants import END_HOLD_SECONDS
    from plank_block_friction.contact import first_leave_plank_time
    from plank_block_friction.simulation import run_simulation

    for pid in ("preset-1", "preset-2", "preset-3"):
        cfg = sim_config_for_preset(pid)
        traj = run_simulation(cfg, 12.0)
        dur = animation_duration(pid)
        assert dur < 2.0
        assert END_HOLD_SECONDS == 0.0
        if pid in ("preset-1", "preset-3"):
            t_leave = first_leave_plank_time(traj)
            assert abs(dur - t_leave) < 0.02
        if pid == "preset-2":
            assert traj.t_sync is not None
            assert abs(dur - traj.t_sync) < 0.05
