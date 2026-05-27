"""Umbrella rigid body: local geometry, rotation, and world coordinates."""

from __future__ import annotations

import math
from dataclasses import dataclass

from umbrella_rain.constants import (
    CANOPY_WIDTH,
    FRONT_EDGE_X,
    HAND_HEIGHT,
    HANDLE_LENGTH,
)


def _rotate(x: float, y: float, phi_rad: float) -> tuple[float, float]:
    c = math.cos(phi_rad)
    s = math.sin(phi_rad)
    return x * c - y * s, x * s + y * c


@dataclass(frozen=True)
class UmbrellaPose:
    """Umbrella pose: center O, rotation phi (rad), radians CCW from +x."""

    ox: float
    oy: float
    phi_rad: float

    @classmethod
    def with_hand_at(
        cls,
        hand_x: float,
        hand_y: float = HAND_HEIGHT,
        phi_rad: float = 0.0,
    ) -> UmbrellaPose:
        """Build pose from hand position G; O is HANDLE_LENGTH above G along canopy normal."""
        dgx, dgy = _rotate(0.0, HANDLE_LENGTH, phi_rad)
        return cls(ox=hand_x + dgx, oy=hand_y + dgy, phi_rad=phi_rad)

    @classmethod
    def scene_a(cls) -> UmbrellaPose:
        """Initial: OG collinear with NP (hand on front edge)."""
        return cls.with_hand_at(FRONT_EDGE_X, HAND_HEIGHT, phi_rad=0.0)

    @classmethod
    def scene_b(cls, arm_extend_x: float, phi_rad: float = 0.0) -> UmbrellaPose:
        """Arm extended: OG parallel to NP (vertical), hand shifts forward."""
        return cls.with_hand_at(FRONT_EDGE_X + arm_extend_x, HAND_HEIGHT, phi_rad)

    @classmethod
    def scene_c(cls, arm_extend_x: float, theta_deg: float = 60.0) -> UmbrellaPose:
        """Rotated until AC is perpendicular to rain (clockwise from horizontal)."""
        phi_rad = math.radians(theta_deg - 90.0)
        return cls.scene_b(arm_extend_x, phi_rad=phi_rad)

    def hand_position(self) -> tuple[float, float]:
        dgx, dgy = _rotate(0.0, -HANDLE_LENGTH, self.phi_rad)
        return self.ox + dgx, self.oy + dgy

    def _local_to_world(self, lx: float, ly: float) -> tuple[float, float]:
        wx, wy = _rotate(lx, ly, self.phi_rad)
        return self.ox + wx, self.oy + wy

    def point_a(self) -> tuple[float, float]:
        return self._local_to_world(-CANOPY_WIDTH / 2, 0.0)

    def point_c(self) -> tuple[float, float]:
        return self._local_to_world(CANOPY_WIDTH / 2, 0.0)

    def point_o(self) -> tuple[float, float]:
        return self.ox, self.oy

    def is_og_vertical(self) -> bool:
        gx, gy = self.hand_position()
        return math.isclose(gx, self.ox, abs_tol=1e-9)

    def ac_perpendicular_to_rain(self, theta_deg: float) -> bool:
        """AC direction dot rain travel direction is zero."""
        theta_rad = math.radians(theta_deg)
        ac_x, ac_y = _rotate(1.0, 0.0, self.phi_rad)
        rain_x, rain_y = -math.cos(theta_rad), -math.sin(theta_rad)
        dot = ac_x * rain_x + ac_y * rain_y
        return math.isclose(dot, 0.0, abs_tol=1e-9)

    def height_c_above_ground(self) -> float:
        return self.point_c()[1]
