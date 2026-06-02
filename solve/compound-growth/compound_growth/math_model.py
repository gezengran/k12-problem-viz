"""Curve comparison y=x² vs y=1.01^x and animation timing."""

from __future__ import annotations

from compound_growth.constants import (
    BASE,
    CROSSING_U_MARGIN,
    FAST_PHASE_FRAC,
    SLOW_PHASE_FRAC,
    X_PLOT_MAX_MARGIN,
)


def gap(x: float) -> float:
    """x² − base^x; zero at intersections."""
    return x * x - BASE**x


def bisect_root(low: float, high: float, *, tol: float = 1e-6) -> float:
    """Find a root of gap on [low, high] where signs differ."""
    f_low, f_high = gap(low), gap(high)
    if f_low == 0:
        return low
    if f_high == 0:
        return high
    if f_low * f_high > 0:
        raise ValueError(f"no sign change on [{low}, {high}]")

    while high - low > tol:
        mid = (low + high) / 2
        f_mid = gap(mid)
        if f_mid == 0:
            return mid
        if f_mid * f_low <= 0:
            high = mid
        else:
            low = mid
    return (low + high) / 2


def all_crossings(*, scan_hi: float = 5000.0, n_scan: int = 1200) -> list[float]:
    """All positive x where x² = base^x (scan + bisection)."""
    roots: list[float] = []
    prev_x = 1e-6
    prev_g = gap(prev_x)
    for k in range(1, n_scan + 1):
        x = scan_hi * k / n_scan
        g = gap(x)
        if prev_g * g < 0:
            roots.append(bisect_root(prev_x, x))
        prev_x, prev_g = x, g
    return roots


def small_crossing() -> float:
    """First crossing: parabola overtakes exponential at small x."""
    roots = all_crossings()
    if not roots:
        raise ValueError("no crossings found")
    return min(roots)


def primary_crossing() -> float:
    """Main story crossing: exponential eventually overtakes x² again at large x."""
    roots = all_crossings()
    if len(roots) < 2:
        raise ValueError(f"expected two crossings, found {len(roots)}")
    return max(roots)


def plot_x_max() -> float:
    """X-axis upper bound so the primary crossing is in frame with margin."""
    return primary_crossing() * X_PLOT_MAX_MARGIN


def ease_out_power(t: float, power: float = 2.5) -> float:
    """Fast at the start of a segment (0→1)."""
    t = max(0.0, min(1.0, t))
    return 1.0 - (1.0 - t) ** power


def progress_schedule(n_frames: int, u_cross: float) -> list[float]:
    """Fast early, slow through crossing band, short finish to x_max."""
    if n_frames < 2:
        return [1.0] * max(1, n_frames)

    n_fast = max(2, int(n_frames * FAST_PHASE_FRAC))
    n_slow = max(2, int(n_frames * SLOW_PHASE_FRAC))
    n_finish = max(1, n_frames - n_fast - n_slow)
    if n_fast + n_slow + n_finish != n_frames:
        n_finish = n_frames - n_fast - n_slow

    margin = CROSSING_U_MARGIN
    u_fast_end = max(0.68, u_cross - margin * 2.4)
    u_slow_lo = max(u_fast_end, u_cross - margin)
    u_slow_hi = min(1.0, u_cross + margin * 0.75)

    schedule: list[float] = []
    for i in range(n_frames):
        if i < n_fast:
            t = i / (n_fast - 1) if n_fast > 1 else 1.0
            u = u_fast_end * ease_out_power(t, power=2.8)
        elif i < n_fast + n_slow:
            t = (i - n_fast) / (n_slow - 1) if n_slow > 1 else 1.0
            u = u_slow_lo + (u_slow_hi - u_slow_lo) * t
        else:
            idx = i - n_fast - n_slow
            t = idx / (n_finish - 1) if n_finish > 1 else 1.0
            u = u_slow_hi + (1.0 - u_slow_hi) * (t**1.4)
        schedule.append(u)

    schedule[0] = 0.0
    schedule[-1] = 1.0
    for j in range(1, len(schedule)):
        schedule[j] = max(schedule[j], schedule[j - 1])
    return schedule


def x_progress_for_frame(
    frame_index: int,
    n_frames: int,
    x_max: float | None = None,
) -> float:
    """Right endpoint of visible curve at this frame."""
    if x_max is None:
        x_max = plot_x_max()
    x_star = primary_crossing()
    u_cross = x_star / x_max
    schedule = progress_schedule(n_frames, u_cross)
    return schedule[frame_index] * x_max


def frame_near_crossing(
    frame_index: int,
    n_frames: int,
    *,
    relative_tolerance: float = 0.055,
) -> bool:
    """True when animation is near the primary intersection."""
    x_star = primary_crossing()
    x_max = plot_x_max()
    x_end = x_progress_for_frame(frame_index, n_frames, x_max)
    tol = max(60.0, x_star * relative_tolerance)
    return abs(x_end - x_star) <= tol


# Backward-compatible alias (tests / imports).
def first_crossing_in_plot() -> float:
    return primary_crossing()
