"""9:16 vertical figures, boundary statics, and animations."""

from __future__ import annotations

import math
from pathlib import Path
from typing import Callable

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

from umbrella_rain.constants import BODY_HEIGHT, BODY_WIDTH, FRONT_EDGE_X
from umbrella_rain.geometry import rain_intersect_top_mn, rain_line_height_at_x
from umbrella_rain.umbrella import UmbrellaPose
from umbrella_rain.viz_layers import (
    DEFAULT_XLIM,
    DEFAULT_YLIM,
    draw_arm_extension,
    draw_body_with_labels,
    draw_ground_angle_theta,
    draw_max_arm_reach_line,
    draw_parallel_ticks,
    draw_rain_arrow_field,
    draw_rain_line_through,
    draw_right_angle_mark,
    label_point,
    rain_line_ground_x,
    rain_line_segment_through_point,
)

FIG_WIDTH = 9.0
FIG_HEIGHT = 16.0
DPI = 80


def portrait_figsize() -> tuple[float, float]:
    return FIG_WIDTH, FIG_HEIGHT


def portrait_aspect_ratio() -> float:
    return FIG_HEIGHT / FIG_WIDTH


def _setup_axes(ax: plt.Axes) -> None:
    ax.set_aspect("equal")
    ax.set_xlim(*DEFAULT_XLIM)
    ax.set_ylim(*DEFAULT_YLIM)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.axhline(0, color="saddlebrown", linewidth=2.5, zorder=3)


def _draw_wet_segment(
    ax: plt.Axes,
    theta_deg: float,
    pose: UmbrellaPose,
    *,
    show_pk_triangle: bool = False,
) -> None:
    """Wet on NP (PK), top MN/MH from rain through C / A."""
    cx, cy = pose.point_c()
    a_x, a_y = pose.point_a()
    y_k = rain_line_height_at_x(cx, cy, FRONT_EDGE_X, theta_deg)
    pk = max(0.0, min(BODY_HEIGHT, y_k))
    head_wet_right = y_k >= BODY_HEIGHT - 1e-6

    wet_kw = dict(color="crimson", linewidth=6, zorder=6, solid_capstyle="round")

    h_pt = rain_intersect_top_mn(a_x, a_y, theta_deg)
    if h_pt is not None:
        x_h, y_h = h_pt
        if x_h > 1e-6:
            ax.plot([0, x_h], [y_h, y_h], **wet_kw)
            ax.plot(x_h, y_h, "o", color="crimson", markersize=9, zorder=7)
            label_point(ax, x_h, y_h, "H", offset=(0.05, 0.04))
        elif abs(x_h) <= 1e-6:
            label_point(ax, 0, BODY_HEIGHT, "M", offset=(-0.12, 0.03))

    if pk > 1e-6:
        ax.plot([FRONT_EDGE_X, FRONT_EDGE_X], [0, pk], **wet_kw)
        ax.plot(FRONT_EDGE_X, pk, "o", color="crimson", markersize=9, zorder=7)
        if pk < BODY_HEIGHT - 1e-6 or not head_wet_right:
            label_point(ax, FRONT_EDGE_X, pk, "K", offset=(0.06, 0.02))
    elif y_k <= 1e-6 and h_pt is None and not head_wet_right:
        label_point(ax, FRONT_EDGE_X, 0, "P", offset=(0.06, -0.12))

    if head_wet_right:
        if pk < BODY_HEIGHT - 1e-6:
            ax.plot([FRONT_EDGE_X, FRONT_EDGE_X], [pk, BODY_HEIGHT], **wet_kw)
        if h_pt is None or h_pt[0] < BODY_WIDTH - 1e-6:
            ax.plot([max(0, h_pt[0] if h_pt else 0), BODY_WIDTH], [BODY_HEIGHT, BODY_HEIGHT], **wet_kw)
        ax.plot(FRONT_EDGE_X, BODY_HEIGHT, "o", color="crimson", markersize=9, zorder=7)
        label_point(ax, FRONT_EDGE_X, BODY_HEIGHT, "N", offset=(0.06, 0.02))

    if show_pk_triangle and 0 < y_k <= BODY_HEIGHT and abs(pose.phi_rad) < 1e-9:
        pk_leg = min(pk, BODY_HEIGHT)
        ax.plot(
            [FRONT_EDGE_X, cx],
            [pk_leg, pk_leg],
            color="orange",
            linewidth=1.8,
            linestyle=":",
            zorder=5,
        )
        ax.text((FRONT_EDGE_X + cx) / 2, pk_leg + 0.06, "0.5 m", fontsize=9, color="orange", ha="center")


def _draw_construction_rain_lines(
    ax: plt.Axes,
    pose: UmbrellaPose,
    theta_deg: float,
    *,
    highlight_c: bool = True,
) -> None:
    a_x, a_y = pose.point_a()
    cx, cy = pose.point_c()
    draw_rain_line_through(ax, a_x, a_y, theta_deg, color="#5a9fd4", linewidth=1.8, alpha=0.7)
    draw_rain_line_through(
        ax,
        cx,
        cy,
        theta_deg,
        color="#1a5fb4" if highlight_c else "#5a9fd4",
        linewidth=2.2 if highlight_c else 1.8,
        alpha=0.9 if highlight_c else 0.7,
    )
  # Ground hits B / D (optional faint)
    for px, py in ((a_x, a_y), (cx, cy)):
        gx = rain_line_ground_x(px, py, theta_deg)
        if DEFAULT_XLIM[0] <= gx <= DEFAULT_XLIM[1]:
            ax.plot(gx, 0, "s", color="#5a9fd4", markersize=4, alpha=0.6, zorder=3)


def render_frame(
    pose: UmbrellaPose,
    theta_deg: float,
    *,
    ax: plt.Axes | None = None,
    boundary_style: bool = False,
    animation_style: bool = False,
    boundary_caption: str = "",
    show_pk_triangle: bool = False,
) -> plt.Figure:
    """Draw one frame; boundary_style adds labels and full rain lines."""
    if ax is None:
        fig, ax = plt.subplots(figsize=portrait_figsize())
    else:
        fig = ax.figure

    _setup_axes(ax)
    draw_rain_arrow_field(ax, theta_deg)

    if boundary_style:
        draw_body_with_labels(ax)
    else:
        ax.plot(
            [0, BODY_WIDTH, BODY_WIDTH, 0, 0],
            [0, 0, BODY_HEIGHT, BODY_HEIGHT, 0],
            "k-",
            linewidth=2,
            zorder=4,
        )

    gx, gy = pose.hand_position()
    a_x, a_y = pose.point_a()
    cx, cy = pose.point_c()
    ox, oy = pose.point_o()

    ax.plot([a_x, cx], [a_y, cy], "c-", linewidth=4, zorder=8)
    ax.plot([ox, gx], [oy, gy], "b-", linewidth=2.5, zorder=8)
    ax.plot(gx, gy, "bo", markersize=7, zorder=9)

    if boundary_style:
        label_point(ax, a_x, a_y, "A", offset=(-0.1, 0.05))
        label_point(ax, cx, cy, "C", offset=(0.05, 0.05))
        label_point(ax, gx, gy, "G", offset=(0.05, -0.12))
        label_point(ax, ox, oy, "O", offset=(-0.12, 0.03))
        draw_arm_extension(ax, FRONT_EDGE_X, gx, gy)
        if abs(gx - ox) < 1e-6:
            draw_parallel_ticks(ax, gx, 0.2, BODY_HEIGHT)
        draw_right_angle_mark(ax, (ox, oy), (gx, gy), (cx, cy))
        draw_ground_angle_theta(ax, theta_deg, vertex=(FRONT_EDGE_X, 0.0))
        draw_max_arm_reach_line(ax)

    if animation_style:
        draw_max_arm_reach_line(ax)

    _draw_construction_rain_lines(ax, pose, theta_deg)
    _draw_wet_segment(ax, theta_deg, pose, show_pk_triangle=show_pk_triangle)

    if boundary_caption:
        ax.text(0.04, 2.12, boundary_caption, fontsize=11, fontweight="bold")
    elif not boundary_style:
        ax.set_title(f"θ={theta_deg}°", fontsize=11)
    fig.tight_layout()
    return fig


def render_boundary_frame(
    pose: UmbrellaPose,
    theta_deg: float,
    scene: str,
    *,
    caption: str = "",
) -> plt.Figure:
    """Full boundary diagram for scene B or C with connected lines."""
    fig, ax = plt.subplots(figsize=portrait_figsize())
    render_frame(
        pose,
        theta_deg,
        ax=ax,
        boundary_style=True,
        boundary_caption=caption or f"Scene {scene.upper()} boundary",
    )

    if scene == "c" and pose.ac_perpendicular_to_rain(theta_deg):
        a_x, a_y = pose.point_a()
        cx, cy = pose.point_c()
        rx, ry = -math.cos(math.radians(theta_deg)), -math.sin(math.radians(theta_deg))
        draw_right_angle_mark(
            ax,
            (cx, cy),
            (cx + rx, cy + ry),
            (a_x, a_y),
            color="darkgreen",
        )
        ax.text(0.05, 2.05, "AC perp rain", fontsize=10, color="darkgreen")

    fig.tight_layout()
    return fig


def export_static(
    pose: UmbrellaPose,
    theta_deg: float,
    path: Path,
    *,
    dpi: int = DPI,
    boundary: bool = False,
    scene: str = "b",
) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if boundary:
        fig = render_boundary_frame(pose, theta_deg, scene, caption="")
    else:
        fig, ax = plt.subplots(figsize=portrait_figsize())
        render_frame(pose, theta_deg, ax=ax)
    fig.savefig(path, dpi=dpi, bbox_inches=None, pad_inches=0.05)
    plt.close(fig)
    return path


def export_boundary_static_suite(ami_dir: Path) -> dict[str, Path]:
    """Export scene-B critical boundaries (no head / no foot) and scene-C boundary."""
    from umbrella_rain.scenes import (
        min_eg_for_dry_scene_c,
        scene_b_boundary_no_foot,
        scene_b_boundary_no_head,
        scene_c,
    )

    static_dir = Path(ami_dir) / "static"
    static_dir.mkdir(parents=True, exist_ok=True)

    outputs: dict[str, Path] = {}

    def save_b(pose: UmbrellaPose, name: str, caption: str) -> None:
        fig = render_boundary_frame(pose, 60.0, "b", caption=caption)
        path = static_dir / name
        fig.savefig(path, dpi=DPI, bbox_inches=None, pad_inches=0.05)
        plt.close(fig)
        outputs[name.replace(".png", "")] = path

    save_b(
        scene_b_boundary_no_head(),
        "b_boundary_no_head.png",
        "B boundary: rain via A along MQ (just misses head)",
    )
    save_b(
        scene_b_boundary_no_foot(),
        "b_boundary_no_foot.png",
        "B boundary: K at P (just misses feet)",
    )

    min_eg = min_eg_for_dry_scene_c(60.0)
    eg = min_eg.min_eg if min_eg.min_eg is not None else 0.25
    fig = render_boundary_frame(
        scene_c(eg, 60.0),
        60.0,
        "c",
        caption="C boundary: rotated, min EG for dry",
    )
    path_c = static_dir / "c_boundary.png"
    fig.savefig(path_c, dpi=DPI, bbox_inches=None, pad_inches=0.05)
    plt.close(fig)
    outputs["c_boundary"] = path_c
    return outputs


def export_animation(
    frames_builder: Callable[[int], tuple[UmbrellaPose, float]],
    n_frames: int,
    path: Path,
    *,
    fps: int = 10,
    dpi: int = DPI,
) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=portrait_figsize())

    def update(i: int) -> None:
        ax.clear()
        pose, theta = frames_builder(i)
        render_frame(pose, theta, ax=ax, animation_style=True)

    anim = FuncAnimation(fig, update, frames=n_frames, interval=1000 // fps)
    suffix = path.suffix.lower()
    if suffix == ".gif":
        anim.save(path, writer=PillowWriter(fps=fps), dpi=dpi)
    else:
        anim.save(path, writer="ffmpeg", fps=fps, dpi=dpi)
    plt.close(fig)
    return path


def export_all_media(ami_dir: Path) -> dict[str, Path]:
    """Boundary PNGs for B/C and enhanced animations."""
    from umbrella_rain.scenes import scene_b, scene_c

    outputs = export_boundary_static_suite(ami_dir)

    def frame_b(i: int) -> tuple[UmbrellaPose, float]:
        x = 0.5 * i / 29
        return scene_b(x), 60.0

    outputs["scene_b"] = export_animation(
        frame_b, 30, Path(ami_dir) / "scene_b.gif", fps=10
    )

    from umbrella_rain.scenes import build_scene_c_eg_timeline

    eg_timeline = build_scene_c_eg_timeline(30, slow_factor=0.25)

    def frame_c(i: int) -> tuple[UmbrellaPose, float]:
        e = eg_timeline[i]
        return scene_c(e, 60.0), 60.0

    outputs["scene_c"] = export_animation(
        frame_c, len(eg_timeline), Path(ami_dir) / "scene_c.gif", fps=10
    )
    return outputs


def rain_segment_span(pose: UmbrellaPose, theta_deg: float) -> float:
    """Public helper: length of rain line through C (for tests)."""
    cx, cy = pose.point_c()
    p1, p2 = rain_line_segment_through_point(cx, cy, theta_deg)
    return math.hypot(p2[0] - p1[0], p2[1] - p1[1])
