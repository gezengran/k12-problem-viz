"""1D block-on-plank dynamics with kinetic friction at interfaces."""

from __future__ import annotations

import math
from dataclasses import dataclass

from plank_block_friction.constants import (
    BLOCK_CENTER_OFFSET_MAX,
    BLOCK_CENTER_OFFSET_MIN,
    BLOCK_INITIAL_CENTER_OFFSET,
    G,
    MASS_RATIO,
    V0,
    V_REL_EPS,
)


def _sign(v: float, *, eps: float = 1e-12) -> int:
    if v > eps:
        return 1
    if v < -eps:
        return -1
    return 0


@dataclass(frozen=True)
class SimConfig:
    """Inputs for one simulation run."""

    mu1: float
    mu2: float
    v0: float = V0
    g: float = G
    mass_ratio: float = MASS_RATIO
    v_rel_eps: float = V_REL_EPS


@dataclass(frozen=True)
class SimSample:
    """Observable state at one instant."""

    t: float
    x_block: float
    x_plank: float
    v_block: float
    v_plank: float
    v_rel: float
    block_plank_kinetic: bool
    friction_block_direction: int
    show_ground_friction: bool


@dataclass(frozen=True)
class Trajectory:
    """Time series plus first co-speed time (if reached)."""

    samples: tuple[SimSample, ...]
    t_sync: float | None


def _accelerations(
    v_block: float,
    v_plank: float,
    *,
    config: SimConfig,
    m: float,
    M: float,
) -> tuple[float, float, bool, int, bool]:
    """Return (a_block, a_plank, kinetic_active, friction_block_dir, show_ground)."""
    v_rel = v_block - v_plank
    kinetic = abs(v_rel) > config.v_rel_eps

    if kinetic:
        rel_sign = _sign(v_rel, eps=config.v_rel_eps)
        f_dir = -rel_sign
        a_block = f_dir * config.mu2 * config.g
        a_plank = -f_dir * config.mu2 * config.g * m / M
        if config.mu1 > 0 and _sign(v_plank, eps=config.v_rel_eps) != 0:
            a_plank += -_sign(v_plank) * config.mu1 * config.g
        show_ground = config.mu1 > 0 and _sign(v_plank, eps=config.v_rel_eps) != 0
        return a_block, a_plank, True, f_dir, show_ground

    v_common = v_block
    friction_dir = 0
    if config.mu1 > 0 and _sign(v_common, eps=config.v_rel_eps) != 0:
        a_common = (
            -_sign(v_common) * config.mu1 * config.g * M / (M + m)
        )
        show_ground = True
        return a_common, a_common, False, friction_dir, show_ground

    return 0.0, 0.0, False, friction_dir, False


def run_simulation(
    config: SimConfig,
    duration: float,
    *,
    dt: float = 0.001,
) -> Trajectory:
    """Integrate from t=0 (rest) with plank impulse to v0 at t=0+."""
    if duration < 0:
        raise ValueError("duration must be non-negative")

    m = 1.0
    M = config.mass_ratio * m
    t = 0.0
    x_plank = 0.0
    x_block = BLOCK_INITIAL_CENTER_OFFSET
    v_block = 0.0
    v_plank = config.v0

    samples: list[SimSample] = []
    t_sync: float | None = None

    def record() -> None:
        nonlocal t_sync
        v_rel = v_block - v_plank
        kinetic = abs(v_rel) > config.v_rel_eps
        _, _, _, f_dir, show_ground = _accelerations(
            v_block, v_plank, config=config, m=m, M=M
        )
        if not kinetic and t_sync is None and t > 0:
            t_sync = t
        samples.append(
            SimSample(
                t=t,
                x_block=x_block,
                x_plank=x_plank,
                v_block=v_block,
                v_plank=v_plank,
                v_rel=v_rel,
                block_plank_kinetic=kinetic,
                friction_block_direction=f_dir,
                show_ground_friction=show_ground,
            )
        )

    record()
    steps = max(0, int(math.ceil(duration / dt)))
    for _ in range(steps):
        a_b, a_p, _, _, _ = _accelerations(
            v_block, v_plank, config=config, m=m, M=M
        )
        x_block += v_block * dt
        x_plank += v_plank * dt
        v_block += a_b * dt
        v_plank += a_p * dt
        # Teaching model: block stays on the plank segment (no fall-off).
        offset = x_block - x_plank
        if offset < BLOCK_CENTER_OFFSET_MIN:
            x_block = x_plank + BLOCK_CENTER_OFFSET_MIN
        elif offset > BLOCK_CENTER_OFFSET_MAX:
            x_block = x_plank + BLOCK_CENTER_OFFSET_MAX
        t += dt
        record()

    if t_sync is None and samples:
        if not samples[-1].block_plank_kinetic:
            t_sync = samples[-1].t

    return Trajectory(samples=tuple(samples), t_sync=t_sync)


def first_sync_time(config: SimConfig, *, max_time: float = 10.0) -> float:
    """Time of first |v_rel| <= eps; raises if not reached within max_time."""
    traj = run_simulation(config, max_time)
    if traj.t_sync is None:
        raise ValueError("co-speed not reached within max_time")
    return traj.t_sync


def sample_at_time(traj: Trajectory, t_query: float) -> SimSample:
    """Nearest sample at or after t_query (clamped to last sample)."""
    if not traj.samples:
        raise ValueError("empty trajectory")
    for s in traj.samples:
        if s.t >= t_query - 1e-12:
            return s
    return traj.samples[-1]
