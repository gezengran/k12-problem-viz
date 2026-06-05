"""Fixed scenario presets from PRD."""

from __future__ import annotations

from dataclasses import dataclass

from plank_block_friction.constants import END_HOLD_SECONDS, PRESET_IDS
from plank_block_friction.contact import first_leave_plank_time
from plank_block_friction.simulation import SimConfig, run_simulation


@dataclass(frozen=True)
class Preset:
    """One export scenario."""

    preset_id: str
    mu1: float
    mu2: float
    tail_seconds: float
    title: str


_PRESETS: dict[str, Preset] = {
    "preset-1": Preset(
        preset_id="preset-1",
        mu1=0.0,
        mu2=0.2,
        tail_seconds=1.0,
        title="基准：板–地光滑",
    ),
    "preset-2": Preset(
        preset_id="preset-2",
        mu1=0.0,
        mu2=0.6,
        tail_seconds=1.0,
        title="强耦合：高 μ₂",
    ),
    "preset-3": Preset(
        preset_id="preset-3",
        mu1=0.15,
        mu2=0.2,
        tail_seconds=2.0,
        title="地面耗散：有 μ₁",
    ),
}


def get_preset(preset_id: str) -> Preset:
    if preset_id not in _PRESETS:
        raise KeyError(f"unknown preset_id: {preset_id!r}")
    return _PRESETS[preset_id]


def sim_config_for_preset(preset_id: str) -> SimConfig:
    p = get_preset(preset_id)
    return SimConfig(mu1=p.mu1, mu2=p.mu2)


def animation_duration(preset_id: str) -> float:
    """End when the block falls off the plank; if it never does, end at co-speed."""
    config = sim_config_for_preset(preset_id)
    traj = run_simulation(config, 12.0)
    t_leave = first_leave_plank_time(traj)
    # Simulation ran full horizon without leaving → block stayed on board (e.g. preset-2).
    if t_leave >= 11.5 and traj.t_sync is not None:
        return traj.t_sync + END_HOLD_SECONDS
    return t_leave + END_HOLD_SECONDS


def all_preset_ids() -> tuple[str, ...]:
    return PRESET_IDS
