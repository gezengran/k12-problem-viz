"""4:3 full-bleed single-view frames: ground, block, or plank reference."""

from __future__ import annotations

import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from mpl_locale import setup_matplotlib_chinese

from plank_block_friction.constants import (
    BLOCK_ANCHOR_X,
    BLOCK_HEIGHT,
    BLOCK_VIEW_X_SPAN,
    BLOCK_WIDTH,
    DPI,
    FIG_HEIGHT,
    FIG_WIDTH,
    LAB_VIEW_X_SPAN,
    LAB_X_MIN,
    PLANK_ANCHOR_X,
    PLANK_HEIGHT,
    PLANK_LENGTH,
)
from plank_block_friction.scene_layout import GROUND_Y, SceneLayout, build_scene_layout
from plank_block_friction.simulation import SimSample

_USE_CHINESE = setup_matplotlib_chinese()

LAB_X_MAX = LAB_X_MIN + LAB_VIEW_X_SPAN
BLOCK_VIEW_X_MIN = 0.0
BLOCK_VIEW_X_MAX = BLOCK_VIEW_X_SPAN

ARROW_COLOR_BLOCK = "#1f78b4"
ARROW_COLOR_PLANK = "#ff7f00"
ARROW_COLOR_REL = "#d62728"
VELOCITY_ARROW_SCALE = 0.32
FRICTION_ARROW_SCALE = 0.45
ARROW_LW = 3.0
LABEL_FONTSIZE = 10

GROUND_STRIPE_COLOR = "#444444"
GROUND_STRIPE_LW = 2.0
PLANK_TEXTURE_COLOR = "#8b6914"
CONTACT_HINT_COLOR = ARROW_COLOR_REL


def _label_ground_frame() -> str:
    return "地面系" if _USE_CHINESE else "Ground frame"


def _label_block_view() -> str:
    return "滑块视角" if _USE_CHINESE else "Block view"


def _label_plank_view() -> str:
    return "木板视角" if _USE_CHINESE else "Plank view"


def _sync_caption() -> str:
    if _USE_CHINESE:
        return r"$v_{\mathrm{rel}}=0$ → 动摩擦消失"
    return r"$v_{\mathrm{rel}}=0$ → kinetic friction ends"


def figure_figsize() -> tuple[float, float]:
    return FIG_WIDTH, FIG_HEIGHT


def portrait_figsize() -> tuple[float, float]:
    return figure_figsize()


def figure_aspect_ratio() -> float:
    return FIG_HEIGHT / FIG_WIDTH


def portrait_aspect_ratio() -> float:
    return figure_aspect_ratio()


def lab_view_xlim(sample: SimSample | None = None) -> tuple[float, float]:
    """Fixed ground-frame window — stripes and bodies use laboratory x."""
    del sample
    return LAB_X_MIN, LAB_X_MAX


def block_view_xlim(sample: SimSample | None = None) -> tuple[float, float]:
    """Co-moving screen window — same span as ground frame, block pinned at center."""
    del sample
    return BLOCK_VIEW_X_MIN, BLOCK_VIEW_X_MAX


def plank_view_xlim(sample: SimSample | None = None) -> tuple[float, float]:
    """Co-moving screen window — same span as ground frame, plank pinned at center."""
    del sample
    return BLOCK_VIEW_X_MIN, BLOCK_VIEW_X_MAX


def block_anchor_x() -> float:
    return BLOCK_ANCHOR_X


def plank_anchor_x() -> float:
    return PLANK_ANCHOR_X


def plank_center_lab(x_plank: float) -> float:
    return x_plank + PLANK_LENGTH / 2


def lab_to_block_screen_x(lab_x: float, x_block_lab: float) -> float:
    return BLOCK_ANCHOR_X + (lab_x - x_block_lab)


def lab_to_plank_screen_x(lab_x: float, x_plank_lab: float) -> float:
    return PLANK_ANCHOR_X + (lab_x - plank_center_lab(x_plank_lab))


def _physics_content_y_range() -> tuple[float, float]:
    y_lo = GROUND_Y - 0.35
    y_hi = GROUND_Y + BLOCK_HEIGHT + PLANK_HEIGHT + 0.55
    return y_lo, y_hi


def _apply_equal_meter_scale(ax: plt.Axes, x_min: float, x_max: float) -> None:
    span_x = x_max - x_min
    y_lo, y_hi = _physics_content_y_range()
    y_mid = (y_lo + y_hi) / 2.0
    # Y span matches figure aspect so 1 m x == 1 m y and the scene fills 4:3.
    span_y = span_x * (FIG_HEIGHT / FIG_WIDTH)
    half_y = span_y / 2.0
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_mid - half_y, y_mid + half_y)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xticks([])
    ax.set_yticks([])


def _configure_full_bleed(fig: Figure, ax: plt.Axes) -> None:
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    ax.set_position([0, 0, 1, 1])


def _draw_ground_stripes(
    ax: plt.Axes,
    x_min: float,
    x_max: float,
    *,
    enhanced: bool = False,
) -> None:
    """Hatch anchored to laboratory x (fixed on ground frame; scrolls in block view)."""
    ax.axhline(GROUND_Y, color="#5c4033", linewidth=2.8, zorder=1)
    stripe_w = 0.30
    color = GROUND_STRIPE_COLOR if enhanced else "#666666"
    lw = GROUND_STRIPE_LW if enhanced else 1.4
    x = math.floor(x_min / stripe_w) * stripe_w
    while x < x_max + stripe_w:
        ax.plot(
            [x, x + stripe_w * 0.55],
            [GROUND_Y - 0.10, GROUND_Y - 0.22],
            color=color,
            linewidth=lw,
            zorder=0,
            solid_capstyle="round",
        )
        x += stripe_w


def _draw_scrolling_ground_stripes(
    ax: plt.Axes,
    x_min: float,
    x_max: float,
    *,
    lab_lo: float,
    lab_hi: float,
    lab_to_screen,
) -> None:
    stripe_w = 0.30
    x_lab = math.floor(lab_lo / stripe_w) * stripe_w
    ax.axhline(GROUND_Y, color="#5c4033", linewidth=2.8, zorder=1)
    while x_lab < lab_hi:
        x_screen = lab_to_screen(x_lab)
        if x_min - stripe_w <= x_screen <= x_max + stripe_w:
            ax.plot(
                [x_screen, x_screen + stripe_w * 0.55],
                [GROUND_Y - 0.10, GROUND_Y - 0.22],
                color=GROUND_STRIPE_COLOR,
                linewidth=GROUND_STRIPE_LW,
                zorder=0,
                solid_capstyle="round",
            )
        x_lab += stripe_w


def _draw_ground_block_frame(
    ax: plt.Axes,
    x_min: float,
    x_max: float,
    x_block_lab: float,
) -> None:
    lab_lo = x_block_lab + (x_min - BLOCK_ANCHOR_X) - 0.30
    lab_hi = x_block_lab + (x_max - BLOCK_ANCHOR_X) + 0.30
    _draw_scrolling_ground_stripes(
        ax,
        x_min,
        x_max,
        lab_lo=lab_lo,
        lab_hi=lab_hi,
        lab_to_screen=lambda x_lab: lab_to_block_screen_x(x_lab, x_block_lab),
    )


def _draw_ground_plank_frame(
    ax: plt.Axes,
    x_min: float,
    x_max: float,
    x_plank_lab: float,
) -> None:
    center = plank_center_lab(x_plank_lab)
    lab_lo = center + (x_min - PLANK_ANCHOR_X) - 0.30
    lab_hi = center + (x_max - PLANK_ANCHOR_X) + 0.30
    _draw_scrolling_ground_stripes(
        ax,
        x_min,
        x_max,
        lab_lo=lab_lo,
        lab_hi=lab_hi,
        lab_to_screen=lambda x_lab: lab_to_plank_screen_x(x_lab, x_plank_lab),
    )


def _draw_block(ax: plt.Axes, x_center: float, bottom_y: float) -> None:
    ax.add_patch(
        Rectangle(
            (x_center - BLOCK_WIDTH / 2, bottom_y),
            BLOCK_WIDTH,
            BLOCK_HEIGHT,
            facecolor="#6baed6",
            edgecolor="black",
            linewidth=1.8,
            zorder=5,
        )
    )


def _draw_plank(
    ax: plt.Axes,
    x_left: float,
    *,
    x_min: float | None = None,
    x_max: float | None = None,
) -> None:
    left = x_left
    right = x_left + PLANK_LENGTH
    if x_min is not None:
        left = max(left, x_min)
    if x_max is not None:
        right = min(right, x_max)
    if right <= left:
        return
    ax.add_patch(
        Rectangle(
            (left, GROUND_Y),
            right - left,
            PLANK_HEIGHT,
            facecolor="#deb887",
            edgecolor="black",
            linewidth=1.8,
            zorder=4,
        )
    )


def _draw_plank_sliding_texture(
    ax: plt.Axes,
    plank_left: float,
    contact_y: float,
    v_rel: float,
) -> None:
    if abs(v_rel) < 0.05:
        return
    sign = 1.0 if v_rel > 0 else -1.0
    y = contact_y + 0.015
    dash_len = 0.12
    gap = 0.18
    x = plank_left + 0.08
    plank_right = plank_left + PLANK_LENGTH
    while x < plank_right - 0.08:
        x1 = x
        x2 = x + sign * dash_len
        ax.plot(
            [x1, x2],
            [y, y],
            color=PLANK_TEXTURE_COLOR,
            linewidth=1.6,
            linestyle="-",
            zorder=4.5,
            solid_capstyle="round",
        )
        x += gap


def _draw_contact_sliding_hint(
    ax: plt.Axes,
    contact_x: float,
    contact_y: float,
    v_rel: float,
) -> None:
    if abs(v_rel) < 0.05:
        return
    sign = 1.0 if v_rel > 0 else -1.0
    tick_len = 0.10
    for offset in (-0.12, 0.0, 0.12):
        x0 = contact_x + offset
        ax.plot(
            [x0, x0 + sign * tick_len],
            [contact_y, contact_y],
            color=CONTACT_HINT_COLOR,
            linewidth=1.8,
            linestyle="--",
            zorder=6,
            solid_capstyle="round",
        )


def _draw_contact_highlight(ax: plt.Axes, contact_x: float, contact_y: float) -> None:
    glow = Rectangle(
        (contact_x - BLOCK_WIDTH * 0.55, contact_y - 0.04),
        BLOCK_WIDTH * 1.1,
        BLOCK_HEIGHT + 0.12,
        facecolor=ARROW_COLOR_REL,
        edgecolor=ARROW_COLOR_REL,
        linewidth=1.5,
        alpha=0.18,
        zorder=3,
    )
    ax.add_patch(glow)


def _arrow(
    ax: plt.Axes,
    x: float,
    y: float,
    vx: float,
    *,
    color: str,
    label: str | None = None,
    scale: float = VELOCITY_ARROW_SCALE,
    label_dy: float = 0.12,
) -> None:
    if abs(vx) < 0.05:
        return
    dx = vx * scale
    ax.annotate(
        "",
        xy=(x + dx, y),
        xytext=(x, y),
        arrowprops=dict(arrowstyle="->", color=color, lw=ARROW_LW),
    )
    if label:
        ax.text(
            x + dx * 0.55,
            y + label_dy,
            label,
            color=color,
            fontsize=LABEL_FONTSIZE,
            ha="center",
            va="bottom",
        )


def _draw_lab_panel(ax: plt.Axes, scene: SceneLayout, sample: SimSample) -> None:
    x_min, x_max = lab_view_xlim(sample)
    _draw_ground_stripes(ax, x_min, x_max, enhanced=False)
    _draw_plank(ax, scene.x_plank, x_min=x_min, x_max=x_max)
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
            label_dy=0.08,
        )
    ax.text(
        0.03,
        0.97,
        _label_ground_frame(),
        transform=ax.transAxes,
        fontsize=11,
        fontweight="bold",
        va="top",
    )


def _draw_block_panel(
    ax: plt.Axes,
    scene: SceneLayout,
    sample: SimSample,
    *,
    highlight_sync: bool = False,
) -> None:
    x_block_lab = sample.x_block
    plank_left = lab_to_block_screen_x(scene.x_plank, x_block_lab)
    block_x = BLOCK_ANCHOR_X
    contact_x = lab_to_block_screen_x(scene.contact_x, x_block_lab)

    _draw_ground_block_frame(ax, BLOCK_VIEW_X_MIN, BLOCK_VIEW_X_MAX, x_block_lab)
    _draw_plank(
        ax,
        plank_left,
        x_min=BLOCK_VIEW_X_MIN,
        x_max=BLOCK_VIEW_X_MAX,
    )
    _draw_block(ax, block_x, scene.block_bottom_y)

    if highlight_sync:
        _draw_contact_highlight(ax, contact_x, scene.contact_y)

    if scene.show_block_plank_friction:
        _draw_plank_sliding_texture(ax, plank_left, scene.contact_y, sample.v_rel)
        _draw_contact_sliding_hint(ax, contact_x, scene.contact_y, sample.v_rel)
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
            scene.contact_y + BLOCK_HEIGHT * 0.35,
            sample.v_rel,
            color=ARROW_COLOR_REL,
            label=r"$v_{\mathrm{rel}}$",
            scale=VELOCITY_ARROW_SCALE,
            label_dy=0.18,
        )

    ax.text(
        0.03,
        0.97,
        _label_block_view(),
        transform=ax.transAxes,
        fontsize=11,
        fontweight="bold",
        va="top",
    )


def _draw_plank_panel(
    ax: plt.Axes,
    scene: SceneLayout,
    sample: SimSample,
    *,
    highlight_sync: bool = False,
) -> None:
    x_plank_lab = sample.x_plank
    plank_left = PLANK_ANCHOR_X - PLANK_LENGTH / 2
    block_x = lab_to_plank_screen_x(scene.x_block, x_plank_lab)
    contact_x = lab_to_plank_screen_x(scene.contact_x, x_plank_lab)

    _draw_ground_plank_frame(ax, BLOCK_VIEW_X_MIN, BLOCK_VIEW_X_MAX, x_plank_lab)
    _draw_plank(
        ax,
        plank_left,
        x_min=BLOCK_VIEW_X_MIN,
        x_max=BLOCK_VIEW_X_MAX,
    )
    _draw_block(ax, block_x, scene.block_bottom_y)

    if highlight_sync:
        _draw_contact_highlight(ax, contact_x, scene.contact_y)

    if scene.show_block_plank_friction:
        _draw_plank_sliding_texture(ax, plank_left, scene.contact_y, sample.v_rel)
        _draw_contact_sliding_hint(ax, contact_x, scene.contact_y, sample.v_rel)
        _arrow(
            ax,
            contact_x,
            scene.contact_y,
            -sample.friction_block_direction * 2.0,
            color=ARROW_COLOR_REL,
            label=r"$f$",
            scale=FRICTION_ARROW_SCALE,
            label_dy=0.08,
        )
        _arrow(
            ax,
            contact_x,
            scene.contact_y + BLOCK_HEIGHT * 0.35,
            sample.v_rel,
            color=ARROW_COLOR_REL,
            label=r"$v_{\mathrm{rel}}$",
            scale=VELOCITY_ARROW_SCALE,
            label_dy=0.18,
        )

    ax.text(
        0.03,
        0.97,
        _label_plank_view(),
        transform=ax.transAxes,
        fontsize=11,
        fontweight="bold",
        va="top",
    )


def _add_ground_legend(fig: Figure) -> None:
    fig.legend(
        handles=[
            Line2D([0], [0], color=ARROW_COLOR_BLOCK, lw=2.5, label=r"$v_{\mathrm{块}}$"),
            Line2D([0], [0], color=ARROW_COLOR_PLANK, lw=2.5, label=r"$v_{\mathrm{板}}$"),
        ],
        loc="lower right",
        bbox_to_anchor=(0.98, 0.02),
        fontsize=9,
        framealpha=0.85,
        ncol=2,
        handlelength=1.4,
    )


def _add_contact_legend(fig: Figure) -> None:
    fig.legend(
        handles=[
            Line2D(
                [0],
                [0],
                color=ARROW_COLOR_REL,
                lw=2.5,
                label=r"$v_{\mathrm{rel}}$, $f$",
            ),
        ],
        loc="lower right",
        bbox_to_anchor=(0.98, 0.02),
        fontsize=9,
        framealpha=0.85,
        handlelength=1.4,
    )


def _add_block_legend(fig: Figure) -> None:
    _add_contact_legend(fig)


def _add_sync_subtitle_bar(fig: Figure) -> None:
    fig.text(
        0.5,
        0.03,
        _sync_caption(),
        ha="center",
        va="center",
        fontsize=11,
        fontweight="bold",
        color=ARROW_COLOR_REL,
        bbox=dict(
            boxstyle="round,pad=0.35",
            facecolor="#fff8f8",
            edgecolor=ARROW_COLOR_REL,
            alpha=0.96,
        ),
        zorder=20,
    )


def render_ground_frame(
    sample: SimSample,
    *,
    highlight_sync: bool = False,
    ax: plt.Axes | None = None,
) -> Figure:
    """Single ground-frame panel (fixed lab window)."""
    scene = build_scene_layout(sample)
    if ax is None:
        fig, ax = plt.subplots(1, 1, figsize=figure_figsize())
    else:
        fig = ax.figure

    _apply_equal_meter_scale(ax, *lab_view_xlim(sample))
    _draw_lab_panel(ax, scene, sample)
    _configure_full_bleed(fig, ax)
    _add_ground_legend(fig)
    if highlight_sync:
        _add_sync_subtitle_bar(fig)
    return fig


def render_block_frame(
    sample: SimSample,
    *,
    highlight_sync: bool = False,
    ax: plt.Axes | None = None,
) -> Figure:
    """Single block co-moving panel."""
    scene = build_scene_layout(sample)
    if ax is None:
        fig, ax = plt.subplots(1, 1, figsize=figure_figsize())
    else:
        fig = ax.figure

    _apply_equal_meter_scale(ax, *block_view_xlim())
    _draw_block_panel(ax, scene, sample, highlight_sync=highlight_sync)
    _configure_full_bleed(fig, ax)
    _add_block_legend(fig)
    if highlight_sync:
        _add_sync_subtitle_bar(fig)
    return fig


def render_plank_frame(
    sample: SimSample,
    *,
    highlight_sync: bool = False,
    ax: plt.Axes | None = None,
) -> Figure:
    """Single plank co-moving panel (plank fixed at center, ground scrolls)."""
    scene = build_scene_layout(sample)
    if ax is None:
        fig, ax = plt.subplots(1, 1, figsize=figure_figsize())
    else:
        fig = ax.figure

    _apply_equal_meter_scale(ax, *plank_view_xlim())
    _draw_plank_panel(ax, scene, sample, highlight_sync=highlight_sync)
    _configure_full_bleed(fig, ax)
    _add_contact_legend(fig)
    if highlight_sync:
        _add_sync_subtitle_bar(fig)
    return fig


def render_dual_frame(
    sample: SimSample,
    *,
    highlight_sync: bool = False,
    ax_left: plt.Axes | None = None,
    ax_right: plt.Axes | None = None,
    ax_top: plt.Axes | None = None,
    ax_bottom: plt.Axes | None = None,
) -> Figure:
    """Compose ground + block frames side by side (legacy / debug)."""
    if ax_left is None:
        ax_left = ax_top
    if ax_right is None:
        ax_right = ax_bottom

    if ax_left is None or ax_right is None:
        fig, (ax_left, ax_right) = plt.subplots(1, 2, figsize=figure_figsize())
    else:
        fig = ax_left.figure

    render_ground_frame(sample, highlight_sync=highlight_sync, ax=ax_left)
    render_block_frame(sample, highlight_sync=highlight_sync, ax=ax_right)
    return fig


def export_frame_png(sample: SimSample, view: str, path: Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if view == "ground":
        fig = render_ground_frame(sample)
    elif view == "block":
        fig = render_block_frame(sample)
    elif view == "plank":
        fig = render_plank_frame(sample)
    else:
        raise ValueError(f"unknown view: {view!r}")
    fig.savefig(path, dpi=DPI, bbox_inches=None, pad_inches=0)
    plt.close(fig)
    return path


def friction_opposes_v_rel(sample: SimSample) -> bool:
    if not sample.block_plank_kinetic:
        return True
    if abs(sample.v_rel) < 1e-6:
        return True
    rel_sign = 1 if sample.v_rel > 0 else -1
    return sample.friction_block_direction == -rel_sign
