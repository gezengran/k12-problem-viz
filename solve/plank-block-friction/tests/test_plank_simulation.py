"""Tests for 1D block–plank simulation."""

from plank_block_friction.constants import G, V0
from plank_block_friction.simulation import SimConfig, first_sync_time, run_simulation


def _cfg(mu1: float, mu2: float) -> SimConfig:
    return SimConfig(mu1=mu1, mu2=mu2, v0=V0, g=G)


def test_kinetic_friction_opposes_v_rel():
    config = _cfg(0.0, 0.2)
    traj = run_simulation(config, 0.2)
    sliding = [s for s in traj.samples if s.block_plank_kinetic and s.t > 0]
    assert sliding
    for s in sliding:
        assert s.friction_block_direction == -_sign(s.v_rel)


def _sign(v: float) -> int:
    if v > 1e-6:
        return 1
    if v < -1e-6:
        return -1
    return 0


def test_after_sync_v_rel_stays_small():
    config = _cfg(0.0, 0.2)
    t_sync = first_sync_time(config)
    traj = run_simulation(config, t_sync + 0.5)
    after = [s for s in traj.samples if s.t >= t_sync - 1e-9]
    assert after
    for s in after:
        assert abs(s.v_rel) < 0.05


def test_higher_mu2_reaches_sync_sooner():
    t_slow = first_sync_time(_cfg(0.0, 0.2))
    t_fast = first_sync_time(_cfg(0.0, 0.6))
    assert t_fast < t_slow


def test_preset1_sync_time_in_expected_band():
    t_sync = first_sync_time(_cfg(0.0, 0.2))
    # M=15m, mu2=0.2, v0=4 => t_sync = v0 / (mu2*g*(1+m/M)) ≈ 1.875 s
    assert 1.6 <= t_sync <= 2.1


def test_preset3_plank_decelerates_after_sync():
    config = _cfg(0.15, 0.2)
    t_sync = first_sync_time(config)
    traj = run_simulation(config, t_sync + 1.0)
    post = [s for s in traj.samples if t_sync <= s.t <= t_sync + 0.8]
    assert len(post) >= 2
    v_planks = [s.v_plank for s in post]
    for prev, curr in zip(v_planks, v_planks[1:]):
        assert curr <= prev + 1e-6
