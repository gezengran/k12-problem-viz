"""Drawing primitives for pedagogy figures: full rain lines, labels, markers."""

from __future__ import annotations

import math
from matplotlib.axes import Axes
from matplotlib.patches import Arc, FancyArrowPatch

from umbrella_rain.constants import BODY_HEIGHT, BODY_WIDTH, MAX_HAND_X

# Default viewport for 9:16 figures (meters)
DEFAULT_XLIM = (-0.3, 1.4)
DEFAULT_YLIM = (-0.2, 2.2)


def rain_line_segment_through_point(
    px: float,
    py: float,
    theta_deg: float,
    xlim: tuple[float, float] = DEFAULT_XLIM,
    ylim: tuple[float, float] = DEFAULT_YLIM,
) -> tuple[tuple[float, float], tuple[float, float]]:
    """Clip the infinite rain line through (px, py) to the axes rectangle."""
    tan_t = math.tan(math.radians(theta_deg))
    x_min, x_max = xlim
    y_min, y_max = ylim
    candidates: list[tuple[float, float]] = []

    def add(x: float, y: float) -> None:
        if x_min - 1e-9 <= x <= x_max + 1e-9 and y_min - 1e-9 <= y <= y_max + 1e-9:
            candidates.append((x, y))

    add(x_min, py + tan_t * (x_min - px))
    add(x_max, py + tan_t * (x_max - px))
    if abs(tan_t) > 1e-12:
        add(px + (y_min - py) / tan_t, y_min)
        add(px + (y_max - py) / tan_t, y_max)
    else:
        add(x_min, py)
        add(x_max, py)

    if len(candidates) < 2:
        return (px, py), (px - 2.0, py - 2.0 * tan_t)

    best_pair = candidates[0], candidates[1]
    best_dist = 0.0
    for i, p1 in enumerate(candidates):
        for p2 in candidates[i + 1 :]:
            d = (p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2
            if d > best_dist:
                best_dist = d
                best_pair = p1, p2
    return best_pair


def rain_line_ground_x(px: float, py: float, theta_deg: float) -> float:
    """x-coordinate where rain line through (px, py) meets the ground y=0."""
    tan_t = math.tan(math.radians(theta_deg))
    if abs(tan_t) < 1e-12:
        return px
    return px - py / tan_t


def draw_rain_line_through(
    ax: Axes,
    px: float,
    py: float,
    theta_deg: float,
    *,
    color: str = "#4a90d9",
    linewidth: float = 1.5,
    linestyle: str = "-",
    alpha: float = 0.85,
    zorder: int = 2,
) -> None:
    p1, p2 = rain_line_segment_through_point(px, py, theta_deg)
    ax.plot(
        [p1[0], p2[0]],
        [p1[1], p2[1]],
        color=color,
        linewidth=linewidth,
        linestyle=linestyle,
        alpha=alpha,
        zorder=zorder,
        solid_capstyle="round",
    )


def draw_rain_arrow_field(
    ax: Axes,
    theta_deg: float,
    *,
    n_arrows: int = 7,
    y_start: float = 2.05,
    x_span: tuple[float, float] = (0.0, 1.2),
    color: str = "#6eb5ff",
    zorder: int = 1,
) -> None:
    """Parallel rain arrows across the top of the figure."""
    theta_rad = math.radians(theta_deg)
    dx = -0.35 * math.cos(theta_rad)
    dy = -0.35 * math.sin(theta_rad)
    xs = [x_span[0] + (x_span[1] - x_span[0]) * i / (n_arrows - 1) for i in range(n_arrows)]
    for x0 in xs:
        arrow = FancyArrowPatch(
            (x0, y_start),
            (x0 + dx, y_start + dy),
            arrowstyle="-|>",
            mutation_scale=12,
            color=color,
            linewidth=1.2,
            alpha=0.75,
            zorder=zorder,
        )
        ax.add_patch(arrow)


def draw_right_angle_mark(
    ax: Axes,
    corner: tuple[float, float],
    arm1: tuple[float, float],
    arm2: tuple[float, float],
    size: float = 0.06,
    **kwargs: object,
) -> None:
    """Small square mark at corner for perpendicular."""
    cx, cy = corner
    v1x, v1y = arm1[0] - cx, arm1[1] - cy
    v2x, v2y = arm2[0] - cx, arm2[1] - cy
    len1 = math.hypot(v1x, v1y) or 1.0
    len2 = math.hypot(v2x, v2y) or 1.0
    u1x, u1y = v1x / len1 * size, v1y / len1 * size
    u2x, u2y = v2x / len2 * size, v2y / len2 * size
    xs = [cx, cx + u1x, cx + u1x + u2x, cx + u2x, cx]
    ys = [cy, cy + u1y, cy + u1y + u2y, cy + u2y, cy]
    ax.plot(xs, ys, color=kwargs.get("color", "green"), linewidth=1.5, zorder=6)


def draw_parallel_ticks(ax: Axes, x: float, y0: float, y1: float, **kwargs: object) -> None:
    """Two short ticks suggesting vertical parallel lines."""
    tick = 0.04
    for y in (y0, y1):
        ax.plot([x - tick, x + tick], [y, y], color=kwargs.get("color", "gray"), lw=1.2, zorder=5)


def label_point(
    ax: Axes,
    x: float,
    y: float,
    text: str,
    offset: tuple[float, float] = (0.04, 0.04),
    **kwargs: object,
) -> None:
    ax.text(
        x + offset[0],
        y + offset[1],
        text,
        fontsize=11,
        fontweight="bold",
        zorder=10,
        **kwargs,
    )


def draw_ground_angle_theta(
    ax: Axes,
    theta_deg: float,
    *,
    vertex: tuple[float, float] | None = None,
    ref_on_rain: tuple[float, float] | None = None,
) -> None:
    """Draw θ between the ground (+x) and the rain line at a ground vertex.

    The arc is placed at ``vertex`` (default: front foot P). If ``ref_on_rain`` is
    given (e.g. canopy point C), the vertex is where that rain line meets y=0.
    """
    if vertex is not None:
        ox, oy = vertex
    elif ref_on_rain is not None:
        px, py = ref_on_rain
        ox = rain_line_ground_x(px, py, theta_deg)
        oy = 0.0
    else:
        from umbrella_rain.constants import FRONT_EDGE_X

        ox, oy = FRONT_EDGE_X, 0.0

    radius = 0.32
    arc = Arc(
        (ox, oy),
        2 * radius,
        2 * radius,
        angle=0,
        theta1=0,
        theta2=theta_deg,
        color="navy",
        linewidth=1.8,
        zorder=8,
    )
    ax.add_patch(arc)
    mid_rad = math.radians(theta_deg / 2)
    label_r = radius * 1.25
    lx = ox + label_r * math.cos(mid_rad)
    ly = oy + label_r * math.sin(mid_rad)
    ax.text(lx, ly, f"θ={int(theta_deg)}°", fontsize=10, color="navy", ha="center")


def draw_max_arm_reach_line(
    ax: Axes,
    *,
    x_line: float | None = None,
    extension_label: str = "0.5",
    color: str = "#7b4a9e",
) -> None:
    """Vertical dashed line at max reach of G (x=0.7 from Q), labeled with extension x."""
    if x_line is None:
        x_line = MAX_HAND_X

    y_top = BODY_HEIGHT + 0.45
    ax.plot(
        [x_line, x_line],
        [0, y_top],
        color=color,
        linewidth=2.0,
        linestyle=(0, (5, 4)),
        alpha=0.95,
        zorder=5,
    )
    ax.text(
        x_line + 0.04,
        y_top - 0.02,
        f"max x={extension_label}",
        fontsize=10,
        color=color,
        ha="left",
        va="top",
    )


def draw_body_with_labels(ax: Axes) -> None:
    ax.plot(
        [0, BODY_WIDTH, BODY_WIDTH, 0, 0],
        [0, 0, BODY_HEIGHT, BODY_HEIGHT, 0],
        "k-",
        linewidth=2.5,
        zorder=4,
    )
    label_point(ax, 0, 0, "Q", offset=(-0.12, -0.12))
    label_point(ax, BODY_WIDTH, 0, "P", offset=(0.05, -0.12))
    label_point(ax, BODY_WIDTH, BODY_HEIGHT, "N", offset=(0.05, 0.03))
    label_point(ax, 0, BODY_HEIGHT, "M", offset=(-0.12, 0.03))


def draw_arm_extension(
    ax: Axes,
    shoulder_x: float,
    hand_x: float,
    hand_y: float,
) -> None:
    """EG horizontal segment when hand is forward of the body front."""
    if hand_x > shoulder_x + 1e-6:
        ax.plot(
            [shoulder_x, hand_x],
            [hand_y, hand_y],
            "magenta",
            linewidth=2.5,
            zorder=5,
        )
        mid_x = (shoulder_x + hand_x) / 2
        ax.text(mid_x, hand_y + 0.08, "x", fontsize=11, color="magenta", ha="center")
