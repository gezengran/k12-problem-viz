"""Growing curves animation for compound-growth demo."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from compound_growth.constants import BASE, FPS, N_FRAMES
from compound_growth.math_model import plot_x_max, primary_crossing, x_progress_for_frame
from live_photo_export import export_live_photo_from_matplotlib
from mpl_locale import setup_matplotlib_chinese

FIGSIZE = (9.0, 16.0)
DPI = 80

_USE_CHINESE = setup_matplotlib_chinese()


def _title() -> str:
    if _USE_CHINESE:
        return "日积月累：1.01^x 在远处再次超过 x²"
    return "Compound growth: 1.01^x overtakes x² again"


def _intersection_label(x_star: float) -> str:
    if _USE_CHINESE:
        return f"反超交点 x≈{x_star:.0f}"
    return f"Overtake at x≈{x_star:.0f}"


def _progress_label(x_end: float) -> str:
    if _USE_CHINESE:
        return f"绘制至 x={x_end:.0f}"
    return f"Drawn to x={x_end:.0f}"


def _draw_frame(i: int, ax: plt.Axes) -> None:
    x_max = plot_x_max()
    x_end = x_progress_for_frame(i, N_FRAMES, x_max)
    # Follow the draw progress so early frames are not a tiny strip on a huge axis.
    if x_end >= x_max * 0.88:
        x_view_max = x_max
    else:
        x_view_max = min(x_max, max(x_end * 1.1, x_max * 0.08))
    xs = np.linspace(0.0, max(x_end, 1.0), 240)
    y_quad = xs * xs
    y_exp = BASE**xs

    ax.set_xlim(0, x_view_max)
    y_top = max(float(np.max(y_quad)), float(np.max(y_exp)), 1.0)
    ax.set_ylim(0, y_top * 1.12)
    ax.set_aspect("auto")
    ax.grid(True, alpha=0.3)
    ax.plot(xs, y_quad, color="#1f78b4", linewidth=2.5, label=r"$y=x^2$")
    ax.plot(xs, y_exp, color="#e31a1c", linewidth=2.5, label=rf"$y={BASE}^x$")

    x_star = primary_crossing()
    y_star = x_star * x_star
    show_highlight = x_end >= x_star * 0.92
    if show_highlight:
        ax.plot(x_star, y_star, "o", color="gold", markersize=14, zorder=5)
        ax.axvline(x_star, color="orange", linestyle="--", alpha=0.75, linewidth=1.5)
        text_x = max(x_max * 0.02, x_star - x_max * 0.22)
        text_y = y_star * 1.08
        ax.annotate(
            _intersection_label(x_star),
            xy=(x_star, y_star),
            xytext=(text_x, text_y),
            fontsize=11,
            arrowprops=dict(arrowstyle="->", color="orange"),
        )

    ax.set_title(_title(), fontsize=12, fontweight="bold")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.legend(loc="upper left", fontsize=10)
    ax.text(
        0.04,
        0.96,
        _progress_label(x_end),
        transform=ax.transAxes,
        fontsize=10,
        va="top",
        bbox=dict(boxstyle="round", facecolor="white", alpha=0.8),
    )


def export_live_demo(ami_dir: Path) -> Path:
    """Export compound-growth Live Photo to ami_dir."""
    ami_dir = Path(ami_dir)
    result = export_live_photo_from_matplotlib(
        _draw_frame,
        N_FRAMES,
        ami_dir / "compound_growth_live",
        figsize=FIGSIZE,
        dpi=DPI,
        fps=FPS,
    )
    return result.pvt
