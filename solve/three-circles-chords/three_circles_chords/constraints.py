"""Analytic/numeric constraints behind each MCQ option."""

from __future__ import annotations

import math
from dataclasses import dataclass

from three_circles_chords.constants import EPS
from three_circles_chords.geometry import (
    IntersectionKind,
    line_chord_state,
    maximize_sum_at_b_zero,
)

SUM_TARGET_C = 3.0


@dataclass(frozen=True)
class KScanAtB:
    """Fixed b: scan k from interior to a feasibility boundary."""

    b: float
    k_interior: float
    k_boundary: float
    tangent_circle: int | None  # index 0..2 at boundary


def k_triple_secant_intervals(
    b: float,
    *,
    k_min: float = -6.0,
    k_max: float = 6.0,
    steps: int = 4000,
    eps: float = EPS,
) -> list[tuple[float, float]]:
    """Maximal k-intervals where y = kx + b cuts all three circles in two points."""
    if steps < 2:
        return []
    step = (k_max - k_min) / (steps - 1)
    intervals: list[tuple[float, float]] = []
    in_run = False
    start = k_min
    prev_ok = False
    for i in range(steps):
        k = k_min + i * step
        ok = line_chord_state(k, b, eps=eps).all_secant
        if ok and not prev_ok:
            start = k
            in_run = True
        if not ok and prev_ok and in_run:
            intervals.append((start, k - step))
            in_run = False
        prev_ok = ok
    if in_run:
        intervals.append((start, k_max))
    return intervals


def _first_invalid_k(
    b: float,
    k_start: float,
    *,
    step: float,
    max_steps: int = 500,
    eps: float = EPS,
) -> float:
    """Step from a feasible k until triple-secant fails (tangent or miss)."""
    k = k_start
    for _ in range(max_steps):
        k += step
        if not line_chord_state(k, b, eps=eps).all_secant:
            return k
    return k


def k_scan_to_boundary(
    b: float,
    *,
    direction: float = 1.0,
    eps: float = EPS,
) -> KScanAtB:
    """Pick interior k and boundary k along one feasible branch (for option A)."""
    intervals = k_triple_secant_intervals(b, eps=eps)
    if not intervals:
        raise ValueError(f"no triple-secant k at b={b!r}")

    lo, hi = max(intervals, key=lambda pair: pair[1] - pair[0])
    if direction >= 0:
        k_interior = (lo + hi) / 2.0
        k_boundary = _first_invalid_k(b, hi, step=0.002, eps=eps)
    else:
        k_interior = (lo + hi) / 2.0
        k_boundary = _first_invalid_k(b, lo, step=-0.002, eps=eps)

    boundary_state = line_chord_state(k_boundary, b, eps=eps)
    tangent_idx = next(
        (i for i, c in enumerate(boundary_state.chords) if c.kind == IntersectionKind.TANGENT),
        None,
    )
    return KScanAtB(
        b=b,
        k_interior=k_interior,
        k_boundary=k_boundary,
        tangent_circle=tangent_idx,
    )


def equal_chord_solutions() -> tuple[tuple[float, float], ...]:
    """All (k, b) with s₁ = s₂ = s₃ and triple secant (exactly three lines)."""
    sqrt3 = math.sqrt(3.0)
    return (
        (0.0, sqrt3 / 2.0),  # horizontal: |b| = |b - √3|/... → b = √3/2
        (sqrt3, 0.0),
        (-sqrt3, 0.0),
    )


def chords_equal(k: float, b: float, *, eps: float = EPS) -> bool:
    state = line_chord_state(k, b, eps=eps)
    if not state.all_secant:
        return False
    s1, s2, s3 = state.lengths
    return abs(s1 - s2) <= eps and abs(s2 - s3) <= eps


def sum_equals(k: float, b: float, target: float = SUM_TARGET_C, *, tol: float = 0.05) -> bool:
    state = line_chord_state(k, b)
    if not state.all_secant:
        return False
    return abs(state.sum_lengths - target) <= tol


def sample_sum_locus(
    target: float = SUM_TARGET_C,
    *,
    tol: float = 0.04,
    min_count: int = 5,
) -> list[tuple[float, float]]:
    """Diverse (k, b) on s₁+s₂+s₃ ≈ target (option C family)."""
    buckets: dict[int, list[tuple[float, float]]] = {}
    for ki in range(-30, 31):
        k = ki * 0.15
        for bi in range(-25, 26):
            b = bi * 0.06
            if not sum_equals(k, b, target, tol=tol):
                continue
            state = line_chord_state(k, b)
            key = round(state.sum_lengths * 1000.0)
            buckets.setdefault(key, []).append((k, b))

    if not buckets:
        raise RuntimeError(f"no poses with sum ≈ {target}")

    best = max(buckets, key=lambda key: len(buckets[key]))
    raw = buckets[best]
    picked: list[tuple[float, float]] = []
    seen: set[tuple[float, float]] = set()
    for k, b in sorted(raw, key=lambda p: (abs(p[0]), abs(p[1]))):
        key = (round(k, 3), round(b, 3))
        if key in seen:
            continue
        seen.add(key)
        picked.append((k, b))
        if len(picked) >= min_count + 1:
            break
    if len(picked) < min_count:
        raise RuntimeError(f"need ≥{min_count} sum-locus poses, got {len(picked)}")
    return picked


@dataclass(frozen=True)
class BZeroPeak:
    """Option D: b = 0 and ∑sᵢ maximal."""

    k_peak: float
    sum_peak: float
    k_feasible_min: float  # |k| > √2 for triple secant when b=0
    k_low_sum: float  # comparison pose with smaller sum
    k_past_peak: float  # rotate k slightly past peak → sum drops


def b_zero_peak_info() -> BZeroPeak:
    k_peak, sum_peak = maximize_sum_at_b_zero()
    k_bound = math.sqrt(2.0)
    k_low = math.copysign(k_bound + 0.15, k_peak)

    # Past peak: tilt toward 0 (shallower) — sum strictly below max.
    k_past = k_peak + 0.35 if k_peak < 0 else k_peak - 0.35
    past_sum = line_chord_state(k_past, 0.0).sum_lengths
    if past_sum >= sum_peak - 0.005:
        k_past = k_peak + 0.5 if k_peak < 0 else k_peak - 0.5

    return BZeroPeak(
        k_peak=k_peak,
        sum_peak=sum_peak,
        k_feasible_min=k_bound,
        k_low_sum=k_low,
        k_past_peak=k_past,
    )


def sum_locus_poses_for_demo(
    target: float = SUM_TARGET_C,
    *,
    count: int = 6,
) -> list[tuple[float, float]]:
    """Visibly different lines on s₁+s₂+s₃ = target (option C carousel)."""
    return sample_sum_locus(target, min_count=count)[:count]
