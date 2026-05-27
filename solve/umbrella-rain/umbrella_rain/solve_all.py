"""Aggregate numerical answers for all scenes."""

from __future__ import annotations

from typing import Any

from umbrella_rain.constants import ARM_EXTEND_MAX, TAN_72
from umbrella_rain.scenes import (
    head_dry_analysis,
    height_c_above_ground,
    min_eg_for_dry_scene_c,
    scene_a,
    wet_length_scene_a,
    wet_length_scene_b,
)
from umbrella_rain.umbrella import UmbrellaPose


def solve_all() -> dict[str, Any]:
    pose_a = scene_a()
    pk_72 = wet_length_scene_a(72.0)
    head = head_dry_analysis(60.0)
    min_eg = min_eg_for_dry_scene_c(60.0)

    return {
        "scene_a": {
            "c_height_m": height_c_above_ground(pose_a),
            "pk_theta_72_m": pk_72,
            "pk_theta_72_approx_textbook": round(1.8 - 0.5 * TAN_72, 2),
        },
        "scene_b": {
            "theta_deg": 60,
            "y_at_x0_m": wet_length_scene_b(0.0, 60.0),
            "y_at_x025_m": wet_length_scene_b(0.25, 60.0),
            "y_at_x05_m": wet_length_scene_b(ARM_EXTEND_MAX, 60.0),
            "head_dry": head.any_head_dry_in_range,
            "head_dry_message": head.message,
            "formula": "y(x) = max(0, min(1.6, 1.8 - tan(60°)·(0.5 + x)))",
        },
        "scene_c": {
            "theta_deg": 60,
            "ac_perpendicular_at_default": UmbrellaPose.scene_c(0.0, 60.0).ac_perpendicular_to_rain(
                60.0
            ),
            "min_eg_exists": min_eg.exists,
            "min_eg_m": min_eg.min_eg,
            "min_eg_message": min_eg.message,
        },
    }


def format_report(results: dict[str, Any] | None = None) -> str:
    r = results or solve_all()
    lines = [
        "=== 雨天撑伞几何题 (umbrella-rain) ===",
        "",
        "【场景 A】OG 与 NP 共线，θ=72°",
        f"  (1) C 到地面距离: {r['scene_a']['c_height_m']:.2f} m",
        f"  (2) 淋湿长度 PK: {r['scene_a']['pk_theta_72_m']:.2f} m"
        f"（题面近似 {r['scene_a']['pk_theta_72_approx_textbook']:.2f} m）",
        "",
        "【场景 B】手臂前伸，θ=60°，OG ∥ NP",
        f"  y(0) = {r['scene_b']['y_at_x0_m']:.3f} m",
        f"  y(0.25) = {r['scene_b']['y_at_x025_m']:.3f} m",
        f"  y(0.5) = {r['scene_b']['y_at_x05_m']:.3f} m",
        f"  关系式: {r['scene_b']['formula']}",
        f"  头部不淋: {r['scene_b']['head_dry_message']}",
        "",
        "【场景 C】旋转至 AC⊥雨线，θ=60°",
        f"  AC⊥雨线: {r['scene_c']['ac_perpendicular_at_default']}",
        f"  {r['scene_c']['min_eg_message']}",
    ]
    return "\n".join(lines)
