"""9:16 vertical figures, boundary statics, and animations."""

from __future__ import annotations

import math
import platform
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Callable

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from PIL import Image

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
# Live Photo still/video frame size (3:4, fits 9:16 diagram with letterboxing).
LIVE_PHOTO_SIZE = (720, 960)


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


def render_scene_c_single_boundary(theta_deg: float, *, boundary: str) -> plt.Figure:
    """Render one scene-C boundary: no_foot(K=P) or no_head(H=M)."""
    from umbrella_rain.scenes import scene_c, scene_c_eg_h_at_m, scene_c_eg_k_at_foot

    x_left = scene_c_eg_k_at_foot(theta_deg)
    x_right = max(x_left, scene_c_eg_h_at_m(theta_deg))

    if boundary == "no_foot":
        x_val = x_left
        caption = "C no-foot boundary: K at P"
        line_color = "#1f78b4"
    elif boundary == "no_head":
        x_val = x_right
        caption = "C no-head boundary: H at M"
        line_color = "#33a02c"
    else:
        raise ValueError("boundary must be 'no_foot' or 'no_head'")

    pose = scene_c(x_val, theta_deg)
    fig = render_boundary_frame(pose, theta_deg, "c", caption=caption)
    ax = fig.axes[0]

    # Highlight the active boundary rain line for this single-boundary figure.
    if boundary == "no_foot":
        cx, cy = pose.point_c()
        draw_rain_line_through(ax, cx, cy, theta_deg, color=line_color, linewidth=2.8, alpha=0.95)
        ax.text(0.56, BODY_HEIGHT + 0.55, f"x_no_foot={x_val:.3f}", fontsize=10, color=line_color)
    else:
        a_x, a_y = pose.point_a()
        draw_rain_line_through(ax, a_x, a_y, theta_deg, color=line_color, linewidth=2.8, alpha=0.95)
        ax.text(0.56, BODY_HEIGHT + 0.55, f"x_no_head={x_val:.3f}", fontsize=10, color=line_color)

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
    """Export B no-head and split C no-foot/no-head boundary figures."""
    from umbrella_rain.scenes import (
        scene_b_boundary_no_head,
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

    fig_c_no_foot = render_scene_c_single_boundary(60.0, boundary="no_foot")
    path_c_no_foot = static_dir / "c_boundary_no_foot.png"
    fig_c_no_foot.savefig(path_c_no_foot, dpi=DPI, bbox_inches=None, pad_inches=0.05)
    plt.close(fig_c_no_foot)
    outputs["c_boundary_no_foot"] = path_c_no_foot

    fig_c_no_head = render_scene_c_single_boundary(60.0, boundary="no_head")
    path_c_no_head = static_dir / "c_boundary_no_head.png"
    fig_c_no_head.savefig(path_c_no_head, dpi=DPI, bbox_inches=None, pad_inches=0.05)
    plt.close(fig_c_no_head)
    outputs["c_boundary_no_head"] = path_c_no_head
    return outputs


def _fig_to_rgb(fig: plt.Figure) -> Image.Image:
    fig.canvas.draw()
    width, height = fig.canvas.get_width_height()
    buffer = fig.canvas.buffer_rgba()
    return Image.frombytes("RGBA", (width, height), buffer).convert("RGB")


def letterbox_image(img: Image.Image, size: tuple[int, int] = LIVE_PHOTO_SIZE) -> Image.Image:
    """Scale to fit inside size, pad with white (Live Photo / Xiaohongshu 3:4)."""
    target_w, target_h = size
    src_w, src_h = img.size
    scale = min(target_w / src_w, target_h / src_h)
    new_w = max(1, int(src_w * scale))
    new_h = max(1, int(src_h * scale))
    resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", size, (255, 255, 255))
    canvas.paste(resized, ((target_w - new_w) // 2, (target_h - new_h) // 2))
    return canvas


def _capture_animation_frames(
    frames_builder: Callable[[int], tuple[UmbrellaPose, float]],
    n_frames: int,
    *,
    dpi: int = DPI,
) -> list[Image.Image]:
    fig, ax = plt.subplots(figsize=portrait_figsize(), dpi=dpi)
    frames: list[Image.Image] = []
    try:
        for i in range(n_frames):
            ax.clear()
            pose, theta = frames_builder(i)
            render_frame(pose, theta, ax=ax, animation_style=True)
            frames.append(_fig_to_rgb(fig))
    finally:
        plt.close(fig)
    return frames


def _save_animated_gif(frames: list[Image.Image], path: Path, *, fps: int) -> Path:
    duration_ms = max(1, 1000 // fps)
    path.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(
        path,
        save_all=True,
        append_images=frames[1:],
        duration=duration_ms,
        loop=0,
    )
    return path


def _save_mov_from_frames(frames: list[Image.Image], path: Path, *, fps: int) -> Path:
    if shutil.which("ffmpeg") is None:
        raise RuntimeError(
            "MOV export requires ffmpeg on PATH. "
            "Install with: conda install -n math -c conda-forge ffmpeg"
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        for i, frame in enumerate(frames):
            frame.save(tmp_dir / f"frame_{i:04d}.png")
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-framerate",
                str(fps),
                "-i",
                str(tmp_dir / "frame_%04d.png"),
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p",
                "-movflags",
                "+faststart",
                str(path),
            ],
            check=True,
            capture_output=True,
        )
    return path


def _try_export_live_photo(
    frames: list[Image.Image],
    base_path: Path,
    *,
    fps: int,
) -> Path | None:
    """Package JPEG+MOV as .pvt for Photos / AirDrop (macOS + makelive)."""
    if platform.system() != "Darwin":
        return None
    try:
        from makelive import save_live_photo_pair_as_pvt
    except ImportError:
        return None

    jpg_path = base_path.with_suffix(".jpg")
    mov_path = base_path.with_suffix(".mov")
    letterbox_image(frames[0]).save(jpg_path, format="JPEG", quality=95)
    xhs_frames = [letterbox_image(frame) for frame in frames]
    _save_mov_from_frames(xhs_frames, mov_path, fps=fps)
    # .pvt bundles still+video+metadata; AirDrop the package, not loose JPG/MOV files.
    _, pvt_path = save_live_photo_pair_as_pvt(jpg_path, mov_path)
    return pvt_path


def export_animation_bundle(
    stem: str,
    frames_builder: Callable[[int], tuple[UmbrellaPose, float]],
    n_frames: int,
    ami_dir: Path,
    *,
    fps: int = 10,
) -> dict[str, Path]:
    """Render once; export Live Photo (.pvt) first, then GIF fallback."""
    ami_dir = Path(ami_dir)
    frames = _capture_animation_frames(frames_builder, n_frames)

    outputs: dict[str, Path] = {}
    live_pvt = _try_export_live_photo(frames, ami_dir / f"{stem}_live", fps=fps)
    if live_pvt is not None:
        outputs[f"{stem}_live"] = live_pvt
    outputs[f"{stem}_gif"] = _save_animated_gif(frames, ami_dir / f"{stem}.gif", fps=fps)
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
    suffix = path.suffix.lower()
    frames = _capture_animation_frames(frames_builder, n_frames, dpi=dpi)
    if suffix == ".gif":
        return _save_animated_gif(frames, path, fps=fps)
    if suffix in {".mp4", ".mov", ".webm"}:
        from matplotlib import animation as mpl_animation

        if not mpl_animation.writers.is_available("ffmpeg"):
            raise RuntimeError(
                "Video export requires ffmpeg on PATH. "
                "Install with: conda install -n math -c conda-forge ffmpeg"
            )
        fig, ax = plt.subplots(figsize=portrait_figsize())

        def update(i: int) -> None:
            ax.clear()
            pose, theta = frames_builder(i)
            render_frame(pose, theta, ax=ax, animation_style=True)

        anim = FuncAnimation(fig, update, frames=n_frames, interval=1000 // fps)
        anim.save(path, writer="ffmpeg", fps=fps, dpi=dpi)
        plt.close(fig)
        return path
    raise ValueError(f"Unsupported animation format: {path.suffix}")


def export_all_media(ami_dir: Path) -> dict[str, Path]:
    """Boundary PNGs for B/C and enhanced animations."""
    from umbrella_rain.scenes import scene_b, scene_c

    outputs = export_boundary_static_suite(ami_dir)

    def frame_b(i: int) -> tuple[UmbrellaPose, float]:
        x = 0.5 * i / 29
        return scene_b(x), 60.0

    outputs.update(export_animation_bundle("scene_b", frame_b, 30, ami_dir, fps=10))

    from umbrella_rain.scenes import build_scene_c_eg_timeline

    eg_timeline = build_scene_c_eg_timeline(30, slow_factor=0.25)

    def frame_c(i: int) -> tuple[UmbrellaPose, float]:
        e = eg_timeline[i]
        return scene_c(e, 60.0), 60.0

    outputs.update(
        export_animation_bundle("scene_c", frame_c, len(eg_timeline), ami_dir, fps=10)
    )
    return outputs


def rain_segment_span(pose: UmbrellaPose, theta_deg: float) -> float:
    """Public helper: length of rain line through C (for tests)."""
    cx, cy = pose.point_c()
    p1, p2 = rain_line_segment_through_point(cx, cy, theta_deg)
    return math.hypot(p2[0] - p1[0], p2[1] - p1[1])
