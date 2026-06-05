"""2D layout for drawing: contact, centroids, fall to ground."""

from __future__ import annotations

from dataclasses import dataclass

from plank_block_friction.constants import (
    BLOCK_CENTER_OFFSET_MAX,
    BLOCK_CENTER_OFFSET_MIN,
    BLOCK_HEIGHT,
    PLANK_HEIGHT,
    PLANK_LENGTH,
)
from plank_block_friction.contact import display_block_center, is_block_on_plank
from plank_block_friction.simulation import SimSample

GROUND_Y = 0.0


@dataclass(frozen=True)
class SceneLayout:
    """Positions for one animation frame (laboratory x, schematic y)."""

    on_plank: bool
    x_block: float
    x_plank: float
    block_bottom_y: float
    block_center_y: float
    plank_center_x: float
    plank_center_y: float
    contact_x: float
    contact_y: float
    show_block_plank_friction: bool


def build_scene_layout(sample: SimSample) -> SceneLayout:
    """Place block on plank or on bare ground; vectors attach to centroids / contact."""
    on_plank = is_block_on_plank(sample.x_block, sample.x_plank)
    if on_plank:
        x_block = display_block_center(sample.x_block, sample.x_plank)
        block_bottom_y = GROUND_Y + PLANK_HEIGHT
    else:
        x_block = sample.x_block
        block_bottom_y = GROUND_Y

    plank_center_x = sample.x_plank + PLANK_LENGTH / 2
    plank_center_y = GROUND_Y + PLANK_HEIGHT / 2
    contact_y = GROUND_Y + PLANK_HEIGHT
    contact_x = max(
        sample.x_plank + BLOCK_CENTER_OFFSET_MIN,
        min(x_block, sample.x_plank + BLOCK_CENTER_OFFSET_MAX),
    )
    show_f = on_plank and sample.block_plank_kinetic

    return SceneLayout(
        on_plank=on_plank,
        x_block=x_block,
        x_plank=sample.x_plank,
        block_bottom_y=block_bottom_y,
        block_center_y=block_bottom_y + BLOCK_HEIGHT / 2,
        plank_center_x=plank_center_x,
        plank_center_y=plank_center_y,
        contact_x=contact_x,
        contact_y=contact_y,
        show_block_plank_friction=show_f,
    )
