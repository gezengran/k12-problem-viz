"""Rain–body intersection and wet length PK."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

from umbrella_rain.constants import BODY_HEIGHT, FRONT_EDGE_X

if TYPE_CHECKING:
    from umbrella_rain.umbrella import UmbrellaPose


def rain_line_height_at_x(
    canopy_edge_x: float,
    canopy_edge_y: float,
    x: float,
    theta_deg: float,
) -> float:
    """Height on a rain line through (canopy_edge_x, canopy_edge_y), left-down rain."""
    theta_rad = math.radians(theta_deg)
    tan_theta = math.tan(theta_rad)
    return canopy_edge_y + tan_theta * (x - canopy_edge_x)


def wet_length_pk(
    canopy_edge_x: float,
    canopy_edge_y: float,
    theta_deg: float,
    front_x: float = FRONT_EDGE_X,
) -> float:
    """Wet length PK on the front vertical edge from ground to intersection K."""
    y_k = rain_line_height_at_x(canopy_edge_x, canopy_edge_y, front_x, theta_deg)
    if y_k <= 0.0:
        return 0.0
    if y_k >= BODY_HEIGHT:
        return BODY_HEIGHT
    return y_k


def wet_length_from_pose(pose: UmbrellaPose, theta_deg: float) -> float:
    cx, cy = pose.point_c()
    return wet_length_pk(cx, cy, theta_deg)


def rain_intersect_horizontal(
    px: float,
    py: float,
    y_target: float,
    theta_deg: float,
) -> tuple[float, float]:
    """x where the rain line through (px, py) crosses the horizontal y=y_target."""
    tan_theta = math.tan(math.radians(theta_deg))
    x_hit = px + (y_target - py) / tan_theta
    return x_hit, y_target


def rain_intersect_top_mn(
    px: float,
    py: float,
    theta_deg: float,
) -> tuple[float, float] | None:
    """Intersection H of rain through (px, py) with the top of the body (y=BODY_HEIGHT)."""
    from umbrella_rain.constants import BODY_WIDTH

    x_h, y_h = rain_intersect_horizontal(px, py, BODY_HEIGHT, theta_deg)
    if -1e-9 <= x_h <= BODY_WIDTH + 1e-9:
        return x_h, y_h
    return None
