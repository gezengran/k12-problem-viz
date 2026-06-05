"""Block–plank contact geometry for drawing and clip length."""

from __future__ import annotations

from plank_block_friction.constants import (
    BLOCK_CENTER_OFFSET_MAX,
    BLOCK_CENTER_OFFSET_MIN,
)
from plank_block_friction.simulation import SimSample, Trajectory


def block_center_offset(x_block: float, x_plank: float) -> float:
    """Block center minus plank left edge (laboratory x)."""
    return x_block - x_plank


def is_block_on_plank(x_block: float, x_plank: float, *, eps: float = 1e-4) -> bool:
    """True while block center lies above the plank segment (not past left/right edge)."""
    if x_block + eps < x_plank + BLOCK_CENTER_OFFSET_MIN:
        return False
    if x_block - eps > x_plank + BLOCK_CENTER_OFFSET_MAX:
        return False
    return True


def display_block_center(x_block: float, x_plank: float) -> float:
    """Clamp block center onto the plank span while still in contact."""
    if not is_block_on_plank(x_block, x_plank):
        return x_block
    offset = block_center_offset(x_block, x_plank)
    clamped = max(BLOCK_CENTER_OFFSET_MIN, min(offset, BLOCK_CENTER_OFFSET_MAX))
    return x_plank + clamped


def first_leave_plank_time(traj: Trajectory, *, max_time: float = 15.0) -> float:
    """First time the block center is no longer above the plank."""
    for sample in traj.samples:
        if sample.t > max_time:
            break
        if not is_block_on_plank(sample.x_block, sample.x_plank):
            return sample.t
    return traj.samples[-1].t if traj.samples else 0.0


def sample_for_display(sample: SimSample) -> SimSample:
    """Pass-through; layout (on-plank vs on-ground) is handled in scene_layout."""
    return sample
