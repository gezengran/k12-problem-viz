import pytest

from plank_block_friction.presets import (
    animation_duration,
    get_preset,
    sim_config_for_preset,
)
from plank_block_friction.simulation import run_simulation


def test_preset1_parameters():
    p = get_preset("preset-1")
    assert p.mu1 == 0.0
    assert p.mu2 == 1.0
    assert p.tail_seconds == 1.0


def test_preset2_parameters():
    p = get_preset("preset-2")
    assert p.mu2 == 1.5
    assert p.tail_seconds == 1.0


def test_preset3_parameters():
    p = get_preset("preset-3")
    assert p.mu1 == 0.15
    assert p.mu2 == 0.2
    assert p.tail_seconds == 2.0


def test_unknown_preset_raises():
    with pytest.raises(KeyError):
        get_preset("preset-99")


def test_animation_duration_is_sync_plus_tail():
    for pid in ("preset-1", "preset-2", "preset-3"):
        preset = get_preset(pid)
        cfg = sim_config_for_preset(pid)
        traj = run_simulation(cfg, 12.0)
        assert traj.t_sync is not None
        dur = animation_duration(pid)
        assert abs(dur - (traj.t_sync + preset.tail_seconds)) < 0.02


def test_preset2_sync_sooner_than_preset1():
    t1 = run_simulation(sim_config_for_preset("preset-1"), 12.0).t_sync
    t2 = run_simulation(sim_config_for_preset("preset-2"), 12.0).t_sync
    assert t1 is not None and t2 is not None
    assert t2 < t1
