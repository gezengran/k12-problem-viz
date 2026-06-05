"""9:16 dual-panel frames: ground frame (top) and block co-moving (bottom)."""

from __future__ import annotations

import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle
from mpl_locale import setup_matplotlib_chinese

from plank_block_friction.constants import (
    BLOCK_HEIGHT,
    BLOCK_WIDTH,
    FIG_HEIGHT,
    FIG_WIDTH,
    PLANK_HEIGHT,
    PLANK_LENGTH,
    VIEW_X_SPAN,
)
from plank_block_friction.scene_layout import GROUND_Y, SceneLayout, build_scene_layout
from plank_block_friction.simulation import SimSample

_USE_CHINESE = setup_matplotlib_chinese()

LAB_X_MIN = -0.5
LAB_X_MAX = LAB_X_MIN + VIEW_X_SPAN

BLOCK_ANCHOR_X = 2.0
BLOCK_VIEW_X_MIN = BLOCK_ANCHOR_X - 2.0
BLOCK_VIEW_X_MAX = BLOCK_VIEW_X_MIN + VIEW_X_SPAN

ARROW_COLOR_BLOCK = "#1f78b4"
ARROW_COLOR_PLANK = "#ff7f00"
ARROW_COLOR_REL = "#d62728"
VELOCITY_ARROW_SCALE = 0.32
FRICTION_ARROW_SCALE = 0.45


def _label_ground_frame() -> str:
    return "地面系" if _USE_CHINESE else "Ground frame"


def _label_block_view() -> str:
    return "滑块视角" if _USE_CHINESE else "Block view"


def _sync_caption() -> str:
    if _USE_CHINESE:
        return r"$v_{\mathrm{rel}}=0$ → 动摩擦消失"
    return r"$v_{\mathrm{rel}}=0$ → kinetic friction ends"


def portrait_figsize() -> tuple[float, float]:
    return FIG_WIDTH, FIG_HEIGHT


def portrait_aspect_ratio() -> float:
    return FIG_HEIGHT / FIG_WIDTH


def lab_view_xlim() -> tuple[float, float]:
    return LAB_X_MIN, LAB_X_MAX


def block_view_xlim() -> tuple[float, float]:
    return BLOCK_VIEW_X_MIN, BLOCK_VIEW_X_MAX


def block_anchor_x() -> float:
    return BLOCK_ANCHOR_X


def lab_to_block_screen_x(lab_x: float, x_block_lab: float) -> float:
    return BLOCK_ANCHOR_X + (lab_x - x_block_lab)


def _physics_content_y_range() -> tuple[float, float]:
    """Vertical extent of bodies (ground hatch sits slightly below GROUND_Y)."""
    y_lo = GROUND_Y - 0.35
    y_hi = GROUND_Y + BLOCK_HEIGHT + PLANK_HEIGHT + 0.55
    return y_lo, y_hi


def _apply_equal_meter_scale(ax: plt.Axes, x_min: float, x_max: float) -> None:
    """1 m horizontally equals 1 m vertically so a square block draws square."""
    span_x = x_max - x_min
    y_lo, y_hi = _physics_content_y_range()
    y_mid = (y_lo + y_hi) / 2.0
    half_y = span_x / 2.0
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_mid - half_y, y_mid + half_y)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xticks([])
    ax.set_yticks([])


def _draw_ground_lab(ax: plt.Axes, x_min: float, x_max: float) -> None:
    ax.axhline(GROUND_Y, color="#5c4033", linewidth=2.5, zorder=1)
    stripe_w = 0.35
    x = math.floor(x_min / stripe_w) * stripe_w
    while x < x_max:
        ax.plot(
            [x, x + stripe_w * 0.5],
            [GROUND_Y - 0.08, GROUND_Y - 0.18],
            color="#888888",
            linewidth=1.2,
            zorder=0,
        )
        x += stripe_w


def _draw_ground_block_frame(ax: plt.Axes, x_min: float, x_max: float, x_block_lab: float) -> None:
    ax.axhline(GROUND_Y, color="#5c4033", linewidth=2.5, zorder=1)
    stripe_w = 0.35
    lab_lo = x_block_lab + (x_min - BLOCK_ANCHOR_X) - stripe_w
    lab_hi = x_block_lab + (x_max - BLOCK_ANCHOR_X) + stripe_w
    x_lab = math.floor(lab_lo / stripe_w) * stripe_w
    while x_lab < lab_hi:
        x_screen = lab_to_block_screen_x(x_lab, x_block_lab)
        if x_min - stripe_w <= x_screen <= x_max + stripe_w:
            ax.plot(
                [x_screen, x_screen + stripe_w * 0.5],
                [GROUND_Y - 0.08, GROUND_Y - 0.18],
                color="#888888",
                linewidth=1.2,
                zorder=0,
            )
        x_lab += stripe_w


def _draw_block(ax: plt.Axes, x_center: float, bottom_y: float) -> None:
    ax.add_patch(
        Rectangle(
            (x_center - BLOCK_WIDTH / 2, bottom_y),
            BLOCK_WIDTH,
            BLOCK_HEIGHT,
            facecolor="#6baed6",
            edgecolor="black",
            linewidth=1.5,
            zorder=5,
        )
    )


def _draw_plank(ax: plt.Axes, x_left: float) -> None:
    ax.add_patch(
        Rectangle(
            (x_left, GROUND_Y),
            PLANK_LENGTH,
            PLANK_HEIGHT,
            facecolor="#deb887",
            edgecolor="black",
            linewidth=1.5,
            zorder=4,
        )
    )


def _arrow(
    ax: plt.Axes,
    x: float,
    y: float,
    vx: float,
    *,
    color: str,
    label: str | None = None,
    scale: float = VELOCITY_ARROW_SCALE,
    label_dy: float = 0.1,
) -> None:
    if abs(vx) < 0.05:
        return
    dx = vx * scale
    ax.annotate(
        "",
        xy=(x + dx, y),
        xytext=(x, y),
        arrowprops=dict(arrowstyle="->", color=color, lw=2.5),
    )
    if label:
        ax.text(
            x + dx * 0.55,
            y + label_dy,
            label,
            color=color,
            fontsize=9,
            ha="center",
            va="bottom",
        )


def _draw_lab_panel(ax: plt.Axes, scene: SceneLayout, sample: SimSample) -> None:
    _draw_ground_lab(ax, LAB_X_MIN, LAB_X_MAX)
    _draw_plank(ax, scene.x_plank)
    _draw_block(ax, scene.x_block, scene.block_bottom_y)

    _arrow(
        ax,
        scene.x_block,
        scene.block_center_y,
        sample.v_block,
        color=ARROW_COLOR_BLOCK,
        label=r"$v_{\mathrm{块}}$",
    )
    _arrow(
        ax,
        scene.plank_center_x,
        scene.plank_center_y,
        sample.v_plank,
        color=ARROW_COLOR_PLANK,
        label=r"$v_{\mathrm{板}}$",
    )
    if sample.show_ground_friction and not sample.block_plank_kinetic:
        _arrow(
            ax,
            scene.plank_center_x,
            GROUND_Y + PLANK_HEIGHT * 0.35,
            -math.copysign(1.0, sample.v_plank) if abs(sample.v_plank) > 0.05 else 0.0,
            color="#9467bd",
            label=r"$f_{\mathrm{地}}$",
            scale=0.42,
            label_dy=0.06,
        )
    ax.text(
        0.02,
        0.96,
        _label_ground_frame(),
        transform=ax.transAxes,
        fontsize=11,
        fontweight="bold",
        va="top",
    )


def _draw_block_panel(ax: plt.Axes, scene: SceneLayout, sample: SimSample) -> None:
    x_block_lab = sample.x_block
    plank_left = lab_to_block_screen_x(scene.x_plank, x_block_lab)
    block_x = BLOCK_ANCHOR_X
    plank_cx = lab_to_block_screen_x(scene.plank_center_x, x_block_lab)
    contact_x = lab_to_block_screen_x(scene.contact_x, x_block_lab)

    _draw_ground_block_frame(ax, BLOCK_VIEW_X_MIN, BLOCK_VIEW_X_MAX, x_block_lab)
    _draw_plank(ax, plank_left)
    _draw_block(ax, block_x, scene.block_bottom_y)

    _arrow(
        ax,
        block_x,
        scene.block_center_y,
        sample.v_block,
        color=ARROW_COLOR_BLOCK,
        label=r"$v_{\mathrm{块}}$",
    )
    _arrow(
        ax,
        plank_cx,
        scene.plank_center_y,
        sample.v_plank - sample.v_block,
        color=ARROW_COLOR_PLANK,
        label=r"$v_{\mathrm{板}}$",
    )

    if scene.show_block_plank_friction:
        _arrow(
            ax,
            contact_x,
            scene.contact_y,
            sample.friction_block_direction * 2.0,
            color=ARROW_COLOR_REL,
            label=r"$f$",
            scale=FRICTION_ARROW_SCALE,
            label_dy=0.08,
        )
        _arrow(
            ax,
            contact_x,
            scene.contact_y,
            sample.v_rel,
            color=ARROW_COLOR_REL,
            label=r"$v_{\mathrm{rel}}$",
            scale=VELOCITY_ARROW_SCALE,
            label_dy=0.22,
        )

    ax.text(
        0.02,
        0.96,
        _label_block_view(),
        transform=ax.transAxes,
        fontsize=11,
        fontweight="bold",
        va="top",
    )


def render_dual_frame(
    sample: SimSample,
    *,
    highlight_sync: bool = False,
    ax_top: plt.Axes | None = None,
    ax_bottom: plt.Axes | None = None,
) -> Figure:
    """Draw one synchronized dual-panel frame."""
    scene = build_scene_layout(sample)
    if ax_top is None or ax_bottom is None:
        fig, (ax_top, ax_bottom) = plt.subplots(
            2,
            1,
            figsize=portrait_figsize(),
            gridspec_kw={"height_ratios": [1, 1], "hspace": 0.08},
        )
    else:
        fig = ax_top.figure

    _apply_equal_meter_scale(ax_top, *lab_view_xlim())
    _apply_equal_meter_scale(ax_bottom, *block_view_xlim())

    _draw_lab_panel(ax_top, scene, sample)
    _draw_block_panel(ax_bottom, scene, sample)

    if highlight_sync:
        fig.text(
            0.5,
            0.5,
            _sync_caption(),
            ha="center",
            va="center",
            fontsize=13,
            fontweight="bold",
            color=ARROW_COLOR_REL,
            bbox=dict(boxstyle="round", facecolor="white", alpha=0.92),
        )

    fig.legend(
        handles=[
            plt.Line2D([0], [0], color=ARROW_COLOR_BLOCK, lw=2, label=r"$v_{\mathrm{块}}$"),
            plt.Line2D([0], [0], color=ARROW_COLOR_PLANK, lw=2, label=r"$v_{\mathrm{板}}$"),
            plt.Line2D(
                [0],
                [0],
                color=ARROW_COLOR_REL,
                lw=2,
                label=r"$v_{\mathrm{rel}}$, $f$",
            ),
        ],
        loc="lower center",
        ncol=3,
        fontsize=9,
        framealpha=0.9,
    )
    fig.subplots_adjust(left=0.06, right=0.94, top=0.96, bottom=0.06, hspace=0.12)
    return fig


def export_dual_frame_png(sample: SimSample, path: Path) -> Path:
    """Write one dual-panel PNG (smoke / debug)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig = render_dual_frame(sample)
    fig.savefig(path, dpi=80, bbox_inches=None, pad_inches=0.08)
    plt.close(fig)
    return path


def friction_opposes_v_rel(sample: SimSample) -> bool:
    """True when kinetic friction on block opposes v_rel (public check for tests)."""
    if not sample.block_plank_kinetic:
        return True
    if abs(sample.v_rel) < 1e-6:
        return True
    rel_sign = 1 if sample.v_rel > 0 else -1
    return sample.friction_block_direction == -rel_sign
