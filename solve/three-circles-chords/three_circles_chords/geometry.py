"""Line–circle intersection and chord geometry for three unit circles."""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum

from three_circles_chords.constants import CIRCLE_CENTERS, CIRCLE_RADIUS, EPS


class IntersectionKind(Enum):
    """How a line meets one circle."""

    NONE = "none"
    TANGENT = "tangent"
    SECANT = "secant"


@dataclass(frozen=True)
class ChordGeometry:
    """Chord on one circle for line y = kx + b (or vertical x = x0)."""

    kind: IntersectionKind
    length: float
    endpoints: tuple[tuple[float, float], tuple[float, float]] | None


@dataclass(frozen=True)
class LineChordState:
    """All three chords for one (k, b) pose."""

    k: float
    b: float
    chords: tuple[ChordGeometry, ChordGeometry, ChordGeometry]

    @property
    def lengths(self) -> tuple[float, float, float]:
        return tuple(c.length for c in self.chords)

    @property
    def sum_lengths(self) -> float:
        return sum(self.lengths)

    @property
    def all_secant(self) -> bool:
        return all(c.kind == IntersectionKind.SECANT for c in self.chords)


def _distance_point_to_line(
    cx: float,
    cy: float,
    k: float | None,
    b: float,
    *,
    x_const: float | None = None,
) -> float:
    """Signed distance magnitude from (cx, cy) to the line."""
    if x_const is not None:
        return abs(cx - x_const)
    denom = math.hypot(k, 1.0)  # type: ignore[arg-type]
    return abs(k * cx - cy + b) / denom  # type: ignore[operator]


def _chord_endpoints(
    cx: float,
    cy: float,
    k: float | None,
    b: float,
    half_len: float,
    *,
    x_const: float | None = None,
) -> tuple[tuple[float, float], tuple[float, float]]:
    """Endpoints of the chord segment inside the circle (half_len = length/2)."""
    if half_len <= 0.0:
        px = x_const if x_const is not None else 0.0
        py = b if x_const is None else k * px + b  # type: ignore[operator]
        return (px, py), (px, py)

    if x_const is not None:
        # Vertical line x = x_const; chord is vertical segment through foot.
        return (x_const, cy - half_len), (x_const, cy + half_len)

    assert k is not None
    # Unit direction along the line (dx, dy) with dy = k*dx, |d| = 1.
    inv_norm = 1.0 / math.hypot(1.0, k)
    dx = inv_norm
    dy = k * inv_norm
    # Closest point on y=kx+b to (cx,cy).
    denom = 1.0 + k * k
    x_foot = (cx + k * (cy - b)) / denom
    y_foot = k * x_foot + b
    return (
        (x_foot - dx * half_len, y_foot - dy * half_len),
        (x_foot + dx * half_len, y_foot + dy * half_len),
    )


def chord_on_circle(
    cx: float,
    cy: float,
    radius: float,
    k: float | None,
    b: float,
    *,
    x_const: float | None = None,
    eps: float = EPS,
) -> ChordGeometry:
    """Chord length and endpoints for one circle."""
    d = _distance_point_to_line(cx, cy, k, b, x_const=x_const)
    if d > radius + eps:
        return ChordGeometry(IntersectionKind.NONE, 0.0, None)
    if abs(d - radius) <= eps:
        if x_const is not None:
            pt = (x_const, cy)
        else:
            assert k is not None
            denom = 1.0 + k * k
            x_foot = (cx + k * (cy - b)) / denom
            pt = (x_foot, k * x_foot + b)
        return ChordGeometry(IntersectionKind.TANGENT, 0.0, (pt, pt))
    half = math.sqrt(radius * radius - d * d)
    eps_pair = _chord_endpoints(cx, cy, k, b, half, x_const=x_const)
    return ChordGeometry(IntersectionKind.SECANT, 2.0 * half, eps_pair)


def line_chord_state(
    k: float,
    b: float,
    *,
    eps: float = EPS,
) -> LineChordState:
    """Public API: (k, b) → three chord geometries."""
    chords: list[ChordGeometry] = []
    for cx, cy in CIRCLE_CENTERS:
        chords.append(
            chord_on_circle(cx, cy, CIRCLE_RADIUS, k, b, eps=eps),
        )
    return LineChordState(k=k, b=b, chords=tuple(chords))


def line_chord_state_vertical(x0: float, *, eps: float = EPS) -> LineChordState:
    """Vertical line x = x0 (infinite slope)."""
    chords: list[ChordGeometry] = []
    for cx, cy in CIRCLE_CENTERS:
        chords.append(
            chord_on_circle(cx, cy, CIRCLE_RADIUS, None, 0.0, x_const=x0, eps=eps),
        )
    # Represent as k=inf surrogate: store k=math.inf, b=x0 for traceability.
    return LineChordState(k=math.inf, b=x0, chords=tuple(chords))


def sum_lengths_at(k: float, b: float) -> float:
    return line_chord_state(k, b).sum_lengths


def maximize_sum_at_b_zero(
    *,
    eps: float = EPS,
) -> tuple[float, float]:
    """Return (k*, max sum) for b=0 over k where all three circles are secant."""
    best_k = 0.0
    best_sum = -1.0
    # Feasible |k| > sqrt(2) for C3; scan numerically.
    for i in range(400):
        k = math.sqrt(2.0) + (8.0 - math.sqrt(2.0)) * i / 399.0
        for sign in (-1.0, 1.0):
            kk = sign * k
            state = line_chord_state(kk, 0.0, eps=eps)
            if not state.all_secant:
                continue
            s = state.sum_lengths
            if s > best_sum:
                best_sum = s
                best_k = kk
    return best_k, best_sum
