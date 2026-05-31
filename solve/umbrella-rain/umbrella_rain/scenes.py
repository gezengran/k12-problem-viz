"""Scene-specific builders and analysis helpers."""

from __future__ import annotations

import math
from dataclasses import dataclass

from umbrella_rain.constants import ARM_EXTEND_MAX, BODY_HEIGHT, FRONT_EDGE_X
from umbrella_rain.geometry import rain_intersect_top_mn, wet_length_from_pose
from umbrella_rain.umbrella import UmbrellaPose


def scene_a() -> UmbrellaPose:
    return UmbrellaPose.scene_a()


def scene_b(arm_extend_x: float) -> UmbrellaPose:
    return UmbrellaPose.scene_b(arm_extend_x)


def scene_c(arm_extend_x: float, theta_deg: float = 60.0) -> UmbrellaPose:
    return UmbrellaPose.scene_c(arm_extend_x, theta_deg)


def height_c_above_ground(pose: UmbrellaPose | None = None) -> float:
    pose = pose or scene_a()
    return pose.height_c_above_ground()


def wet_length_scene_a(theta_deg: float = 72.0) -> float:
    return wet_length_from_pose(scene_a(), theta_deg)


def wet_length_scene_b(arm_extend_x: float, theta_deg: float = 60.0) -> float:
    return wet_length_from_pose(scene_b(arm_extend_x), theta_deg)


def wet_length_scene_c(arm_extend_x: float, theta_deg: float = 60.0) -> float:
    return wet_length_from_pose(scene_c(arm_extend_x, theta_deg), theta_deg)


def scene_b_arm_x_no_head(theta_deg: float = 60.0) -> float:
    """Arm extension x so rain through A passes through M (top-left), i.e. along MQ."""
    tan_theta = math.tan(math.radians(theta_deg))
    canopy_y = 1.8  # HAND_HEIGHT + HANDLE_LENGTH
    # Rain through A(ax, ay) hits M at x=0: ax = 0 - (BODY_HEIGHT - ay) / tan
    a_x = -(BODY_HEIGHT - canopy_y) / tan_theta
    x = a_x - FRONT_EDGE_X + 0.5
    return max(0.0, min(ARM_EXTEND_MAX, x))


def scene_b_arm_x_no_foot(theta_deg: float = 60.0) -> float:
    """Arm extension x so rain through C meets P: wet length PK = 0 (K at feet)."""
    tan_theta = math.tan(math.radians(theta_deg))
    canopy_y = 1.8
    x = canopy_y / tan_theta - 0.5
    return x


def scene_b_boundary_no_head(theta_deg: float = 60.0) -> UmbrellaPose:
    return scene_b(scene_b_arm_x_no_head(theta_deg))


def scene_b_boundary_no_foot(theta_deg: float = 60.0) -> UmbrellaPose:
    """Uses exact x for K=P; may exceed ARM_EXTEND_MAX (ideal boundary)."""
    return scene_b(scene_b_arm_x_no_foot(theta_deg))


@dataclass(frozen=True)
class HeadDryResult:
    """Whether the head (y=1.6) stays dry for some arm extension in [0, ARM_EXTEND_MAX]."""

    any_head_dry_in_range: bool
    message: str


def head_dry_analysis(theta_deg: float = 60.0) -> HeadDryResult:
    """Head dry when rain through A hits MN at/left of M (left-side criterion)."""
    tan_theta = math.tan(math.radians(theta_deg))
    canopy_y = 1.8
    # Why this boundary: top wetness is controlled by the left boundary rain line through A.
    # Let H be where that rain line intersects MN (y=BODY_HEIGHT):
    #   x_H = a_x + (BODY_HEIGHT - canopy_y) / tan(theta)
    # Head stays dry iff H is at M or left of M, i.e. x_H <= 0.
    # With scene-B geometry a_x = x - 0.3 (A is 0.5 m left of O, and O at FRONT_EDGE_X + x),
    # the maximal allowed extension is:
    x_max = -(BODY_HEIGHT - canopy_y) / tan_theta + 0.3
    if x_max >= 0.0:
        return HeadDryResult(
            any_head_dry_in_range=True,
            message=f"头部不淋湿要求前伸量 x <= {x_max:.3f} m（在 [0, {ARM_EXTEND_MAX}] 内可行）",
        )
    return HeadDryResult(
        any_head_dry_in_range=False,
        message=f"在 x∈[0, {ARM_EXTEND_MAX}] 内无法使头部不淋湿（需 x <= {x_max:.3f} m）",
    )


@dataclass(frozen=True)
class MinEgResult:
    """Minimum arm extension for full dry (PK=0) in scene C."""

    exists: bool
    min_eg: float | None
    message: str


def min_eg_for_dry_scene_c(theta_deg: float = 60.0) -> MinEgResult:
    """Find smallest e in [0, ARM_EXTEND_MAX] with wet_length_scene_c(e) == 0."""
    tan_theta = math.tan(math.radians(theta_deg))
    def c_position(e: float) -> tuple[float, float]:
        pose = scene_c(e, theta_deg)
        return pose.point_c()

    # Binary search / scan
    best: float | None = None
    for step in range(10001):
        e = ARM_EXTEND_MAX * step / 10000
        cx, cy = c_position(e)
        y_k = cy + tan_theta * (FRONT_EDGE_X - cx)
        if y_k <= 1e-9:
            best = e
            break

    if best is None:
        return MinEgResult(
            exists=False,
            min_eg=None,
            message=f"在 e∈[0, {ARM_EXTEND_MAX}] 内无法全身不淋湿",
        )

    # Refine with analytic formula for horizontal... use numeric refine
    lo, hi = 0.0, best
    for _ in range(50):
        mid = (lo + hi) / 2
        cx, cy = c_position(mid)
        y_k = cy + tan_theta * (FRONT_EDGE_X - cx)
        if y_k <= 1e-9:
            hi = mid
        else:
            lo = mid
    min_e = hi

    if min_e > ARM_EXTEND_MAX + 1e-9:
        return MinEgResult(
            exists=False,
            min_eg=None,
            message=f"在 e∈[0, {ARM_EXTEND_MAX}] 内无法全身不淋湿",
        )

    return MinEgResult(
        exists=True,
        min_eg=min_e,
        message=f"最小前伸量 EG ≈ {min_e:.3f} m（在允许范围内）",
    )


def scene_c_eg_k_at_foot(theta_deg: float = 60.0) -> float:
    """Smallest arm extension e with PK = 0 (rain through C meets P)."""
    if wet_length_scene_c(0.0, theta_deg) <= 1e-9:
        return 0.0
    lo, hi = 0.0, ARM_EXTEND_MAX
    for _ in range(60):
        mid = (lo + hi) / 2
        if wet_length_scene_c(mid, theta_deg) <= 1e-9:
            hi = mid
        else:
            lo = mid
    return hi


def scene_c_eg_h_at_m(theta_deg: float = 60.0) -> float:
    """Arm extension e where rain through A is closest to M (top-left corner)."""
    best_e = 0.0
    best_abs_x = float("inf")
    for step in range(10001):
        e = ARM_EXTEND_MAX * step / 10000
        pose = scene_c(e, theta_deg)
        hit = rain_intersect_top_mn(*pose.point_a(), theta_deg)
        if hit is None:
            continue
        abs_x = abs(hit[0])
        if abs_x < best_abs_x:
            best_abs_x = abs_x
            best_e = e
    return best_e


def build_scene_c_eg_timeline(
    n_frames: int,
    *,
    eg_min: float = 0.0,
    eg_max: float = ARM_EXTEND_MAX,
    theta_deg: float = 60.0,
    slow_factor: float = 0.25,
) -> list[float]:
    """EG samples for scene C animation; slow_factor=0.25 => 4× frames between K=P and H≈M."""
    if n_frames < 2:
        return [eg_min]

    e_k = scene_c_eg_k_at_foot(theta_deg)
    e_h = max(e_k, scene_c_eg_h_at_m(theta_deg))

    len1 = max(0.0, e_k - eg_min)
    len2 = max(0.0, e_h - e_k)
    len3 = max(0.0, eg_max - e_h)
    slow_scale = 1.0 / slow_factor if slow_factor > 0 else 1.0

    w1, w2, w3 = len1, len2 * slow_scale, len3
    total_w = w1 + w2 + w3
    if total_w <= 1e-12:
        return [eg_min + (eg_max - eg_min) * i / (n_frames - 1) for i in range(n_frames)]

    values: list[float] = []
    for i in range(n_frames):
        t = i / (n_frames - 1)
        d = t * total_w
        if d <= w1:
            eg = eg_min + d
        elif d <= w1 + w2:
            eg = e_k + (d - w1) * slow_factor
        else:
            eg = e_h + (d - w1 - w2)
        values.append(min(eg_max, max(eg_min, eg)))
    return values


def full_dry_scene_b_in_range(theta_deg: float = 60.0) -> bool:
    """Scene B: any x in [0, ARM_EXTEND_MAX] with PK=0?"""
    tan_theta = math.tan(math.radians(theta_deg))
    x_needed = 1.8 / tan_theta - 0.5
    return 0.0 <= x_needed <= ARM_EXTEND_MAX
