"""Feasible b-interval for triple secant intersection at fixed k."""

from __future__ import annotations

import math
from dataclasses import dataclass

from three_circles_chords.constants import CIRCLE_CENTERS, CIRCLE_RADIUS, EPS
from three_circles_chords.geometry import IntersectionKind, line_chord_state


@dataclass(frozen=True)
class BEnvelope:
    """b range where all three unit circles meet the line in two points."""

    k: float
    b_min: float
    b_max: float

    def contains(self, b: float, *, eps: float = EPS) -> bool:
        return self.b_min - eps <= b <= self.b_max + eps

    def sample(self, n: int, *, eps: float = EPS) -> list[float]:
        """Uniform samples strictly inside [b_min, b_max] (avoids tangent endpoints)."""
        if n < 1:
            return []
        margin = max(eps, (self.b_max - self.b_min) * 0.05)
        lo = self.b_min + margin
        hi = self.b_max - margin
        if n == 1:
            return [(lo + hi) / 2.0]
        step = (hi - lo) / (n - 1)
        return [lo + i * step for i in range(n)]


def _circle_b_interval(
    cx: float,
    cy: float,
    k: float,
    radius: float,
) -> tuple[float, float]:
    """b interval for secant intersection with circle at fixed k."""
    denom = math.hypot(k, 1.0)
    offset = radius * denom
    center_term = cy - k * cx
    return center_term - offset, center_term + offset


def b_envelope(k: float) -> BEnvelope:
    """Intersection of per-circle feasible b intervals."""
    lows: list[float] = []
    highs: list[float] = []
    for cx, cy in CIRCLE_CENTERS:
        lo, hi = _circle_b_interval(cx, cy, k, CIRCLE_RADIUS)
        lows.append(lo)
        highs.append(hi)
    b_min = max(lows)
    b_max = min(highs)
    if b_min > b_max:
        raise ValueError(f"no triple-secant feasible b for k={k!r}")
    return BEnvelope(k=k, b_min=b_min, b_max=b_max)


def assert_triple_secant(k: float, b: float, *, eps: float = EPS) -> None:
    state = line_chord_state(k, b, eps=eps)
    if not state.all_secant:
        raise ValueError(f"({k}, {b}) is not in triple-secant feasible set")


def tangent_circle_index_at_boundary(
    env: BEnvelope,
    *,
    at_min: bool,
    eps: float = EPS,
) -> int:
    """Which circle is tangent at b_min or b_max."""
    b = env.b_min if at_min else env.b_max
    state = line_chord_state(env.k, b, eps=eps)
    for i, chord in enumerate(state.chords):
        if chord.kind == IntersectionKind.TANGENT:
            return i
    raise ValueError("expected a tangent circle at envelope boundary")
