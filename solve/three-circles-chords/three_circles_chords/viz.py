"""3:4 portrait frames: coordinate plane, circles, dashed line, colored chords."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from three_circles_chords.constants import (
    CIRCLE_CENTERS,
    CIRCLE_RADIUS,
    DPI,
    FIG_HEIGHT,
    FIG_WIDTH,
    PORTRAIT_ASPECT,
)
from mpl_locale import setup_matplotlib_chinese

from three_circles_chords.geometry import IntersectionKind, line_chord_state

setup_matplotlib_chinese()

CHORD_COLORS = ("#e41a1c", "#377eb8", "#4daf4a")
CIRCLE_EDGE = "#bbbbbb"
AXIS_COLOR = "#666666"
GRID_ALPHA = 0.25
LINE_STYLE = dict(color="#888888", linestyle="--", linewidth=1.2, alpha=0.95)
POLYLINE_STYLE = dict(color="#aaaaaa", linewidth=0.9, alpha=0.4, linestyle="-")
PEAK_RING_STYLE = dict(edgecolor="#ff7f00", linewidth=2.5, linestyle="-", fill=False)

POLYLINE_ORDER = (0, 1, 2)


def portrait_aspect_ratio() -> float:
    return PORTRAIT_ASPECT


def portrait_figsize() -> tuple[float, float]:
    return FIG_WIDTH, FIG_HEIGHT


def _view_limits() -> tuple[float, float, float, float]:
    xs = [cx for cx, _ in CIRCLE_CENTERS]
    ys = [cy for _, cy in CIRCLE_CENTERS]
    pad = 0.9
    return min(xs) - 1 - pad, max(xs) + 1 + pad, min(ys) - 1 - pad, max(ys) + 1 + pad


def _draw_coordinate_plane(ax: plt.Axes, xlim: tuple[float, float], ylim: tuple[float, float]) -> None:
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    ax.set_aspect("equal", adjustable="box")
    ax.axhline(0.0, color=AXIS_COLOR, linewidth=0.9, zorder=0)
    ax.axvline(0.0, color=AXIS_COLOR, linewidth=0.9, zorder=0)
    ax.grid(True, color="#cccccc", alpha=GRID_ALPHA, linewidth=0.6)
    ax.set_xlabel("x", fontsize=11, color=AXIS_COLOR)
    ax.set_ylabel("y", fontsize=11, color=AXIS_COLOR)
    ax.tick_params(labelsize=9, colors=AXIS_COLOR)


def _draw_line(ax: plt.Axes, k: float, b: float, xlim: tuple[float, float]) -> None:
    x0, x1 = xlim
    if abs(k) > 1e6:
        x_const = b
        ax.axvline(x_const, **LINE_STYLE)
        return
    y0 = k * x0 + b
    y1 = k * x1 + b
    ax.plot([x0, x1], [y0, y1], **LINE_STYLE, zorder=2)


def _polyline_points(state) -> list[tuple[float, float]]:
    pts: list[tuple[float, float]] = []
    for idx in POLYLINE_ORDER:
        chord = state.chords[idx]
        if chord.endpoints is None:
            continue
        p1, p2 = chord.endpoints
        pts.extend([p1, p2])
    return pts


def polyline_length(state) -> float:
    pts = _polyline_points(state)
    if len(pts) < 2:
        return 0.0
    total = 0.0
    for a, b in zip(pts, pts[1:]):
        total += ((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2) ** 0.5
    return total


def render_frame(
    k: float,
    b: float,
    *,
    badge: str | None = None,
    polyline: bool = False,
    caption: str | None = None,
    highlight_peak: bool = False,
    ax: plt.Axes | None = None,
) -> Figure:
    """Render one 3:4 frame with coordinate axes."""
    state = line_chord_state(k, b)
    x_min, x_max, y_min, y_max = _view_limits()

    if ax is None:
        fig, ax = plt.subplots(figsize=portrait_figsize(), dpi=DPI)
    else:
        fig = ax.figure
        ax.clear()

    _draw_coordinate_plane(ax, (x_min, x_max), (y_min, y_max))

    for cx, cy in CIRCLE_CENTERS:
        circle = plt.Circle(
            (cx, cy),
            CIRCLE_RADIUS,
            fill=False,
            edgecolor=CIRCLE_EDGE,
            linewidth=1.4,
            zorder=1,
        )
        ax.add_patch(circle)

    _draw_line(ax, k, b, (x_min, x_max))

    for idx, chord in enumerate(state.chords):
        if chord.kind == IntersectionKind.SECANT and chord.endpoints is not None:
            p1, p2 = chord.endpoints
            ax.plot(
                [p1[0], p2[0]],
                [p1[1], p2[1]],
                color=CHORD_COLORS[idx],
                linewidth=4.0,
                solid_capstyle="round",
                zorder=4,
            )
        elif chord.kind == IntersectionKind.TANGENT and chord.endpoints is not None:
            pt = chord.endpoints[0]
            ax.plot(pt[0], pt[1], "o", color=CHORD_COLORS[idx], markersize=5, zorder=4)

    if polyline:
        pts = _polyline_points(state)
        if len(pts) >= 2:
            xs, ys = zip(*pts)
            ax.plot(xs, ys, **POLYLINE_STYLE, zorder=3)

    if highlight_peak:
        ax.plot(0.0, 0.0, "o", color="#ff7f00", markersize=10, zorder=5)
        ring = plt.Circle((0.0, 0.0), 0.22, **PEAK_RING_STYLE, zorder=5)
        ax.add_patch(ring)

    if badge:
        ax.text(
            0.03,
            0.97,
            badge,
            transform=ax.transAxes,
            fontsize=26,
            fontweight="bold",
            va="top",
            ha="left",
            color="#222222",
            zorder=6,
        )

    if caption:
        ax.text(
            0.5,
            0.04,
            caption,
            transform=ax.transAxes,
            fontsize=11,
            ha="center",
            va="bottom",
            color="#333333",
            zorder=6,
            bbox=dict(boxstyle="round,pad=0.35", facecolor="white", alpha=0.85, edgecolor="#dddddd"),
        )

    fig.subplots_adjust(left=0.12, right=0.96, top=0.96, bottom=0.10)
    return fig


def save_frame_png(
    k: float,
    b: float,
    path: Path,
    *,
    badge: str | None = None,
    polyline: bool = False,
    caption: str | None = None,
    highlight_peak: bool = False,
) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig = render_frame(
        k,
        b,
        badge=badge,
        polyline=polyline,
        caption=caption,
        highlight_peak=highlight_peak,
    )
    fig.savefig(path, dpi=DPI)
    plt.close(fig)
    return path


def count_chord_artists(fig: Figure) -> int:
    count = 0
    for ax in fig.axes:
        for line in ax.lines:
            if line.get_linewidth() >= 3.5 and line.get_linestyle() == "-":
                count += 1
    return count


def has_coordinate_axes(fig: Figure) -> bool:
    ax = fig.axes[0]
    return ax.get_xlabel() == "x" and ax.get_ylabel() == "y"
