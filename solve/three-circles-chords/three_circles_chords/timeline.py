"""Per-option frame sequences driven by explicit geometric constraints."""

from __future__ import annotations

from dataclasses import dataclass

from three_circles_chords.constants import EXPORT_FPS, OPTION_A_B, OPTION_SECONDS
from three_circles_chords.constraints import (
    SUM_TARGET_C,
    b_zero_peak_info,
    equal_chord_solutions,
    k_scan_to_boundary,
    sum_locus_poses_for_demo,
)
from three_circles_chords.scenes import OPTION_LETTERS, OptionLetter

CAPTION_A = r"固定 $b$，增大 $k$ $\rightarrow$ 某圆相切（弦消失）"
CAPTION_B_RULE = r"$s_1=s_2=s_3$ $\Leftrightarrow$ 三圆心到直线距离相等"
CAPTION_B_ONLY3 = r"仅 3 条直线满足"
CAPTION_C_FAMILY = r"$s_1+s_2+s_3=3$：1 个方程、2 个未知数 $\Rightarrow$ 无穷多直线"
CAPTION_C_LINE_N = r"满足条件的第 {n} 条直线（$k,b$ 不同）"
CAPTION_C_GT3 = r"已出现 4 条以上，仍满足同一总和"
CAPTION_D_RULE = r"$b=0$（直线过原点）"
CAPTION_D_RISE = r"倾斜增大 $\rightarrow$ $\sum s_i$ 升高"
CAPTION_D_PEAK = r"$\sum s_i$ 达到极大"
CAPTION_D_FALL = r"再转一点 $\rightarrow$ $\sum s_i$ 下降（非极大）"


@dataclass(frozen=True)
class FrameSpec:
    k: float
    b: float
    badge: str | None = None
    polyline: bool = False
    caption: str | None = None
    highlight_peak: bool = False


def _seconds_to_frames(seconds: float, fps: int = EXPORT_FPS) -> int:
    return max(2, int(round(seconds * fps)))


def _lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def _scan_values(start: float, end: float, n: int) -> list[float]:
    if n <= 1:
        return [start]
    return [_lerp(start, end, i / (n - 1)) for i in range(n)]


def _badge(letter: OptionLetter) -> str:
    return letter


def build_option_a_frames(
    *,
    fps: int = EXPORT_FPS,
    seconds: float = OPTION_SECONDS,
) -> list[FrameSpec]:
    scan = k_scan_to_boundary(OPTION_A_B, direction=1.0)
    n = _seconds_to_frames(seconds, fps=fps)
    scan_n = max(2, int(n * 0.75))
    hold_n = n - scan_n
    badge = _badge("A")
    frames: list[FrameSpec] = []
    for i, k in enumerate(_scan_values(scan.k_interior, scan.k_boundary, scan_n)):
        cap = CAPTION_A if i == 0 else None
        frames.append(FrameSpec(k=k, b=scan.b, badge=badge, caption=cap))
    for _ in range(hold_n):
        frames.append(
            FrameSpec(k=scan.k_boundary, b=scan.b, badge=badge, caption=CAPTION_A),
        )
    return frames


def build_option_b_frames(
    *,
    fps: int = EXPORT_FPS,
    seconds: float = OPTION_SECONDS,
) -> list[FrameSpec]:
    """B: only the 3 analytic equal-chord lines."""
    badge = _badge("B")
    solutions = equal_chord_solutions()
    n = _seconds_to_frames(seconds, fps=fps)
    per = max(2, n // len(solutions))
    labels = (r"水平 $b=\frac{\sqrt{3}}{2}$", r"$k=+\sqrt{3}$", r"$k=-\sqrt{3}$")
    frames: list[FrameSpec] = []
    for idx, ((k, b), label) in enumerate(zip(solutions, labels)):
        cap = f"{CAPTION_B_ONLY3} · {label}"
        if idx == 0:
            cap = f"{CAPTION_B_RULE}\n{cap}"
        for j in range(per):
            frames.append(
                FrameSpec(
                    k=k,
                    b=b,
                    badge=badge,
                    caption=cap if j == 0 else None,
                ),
            )
    while len(frames) < n:
        k, b = solutions[-1]
        frames.append(FrameSpec(k=k, b=b, badge=badge))
    return frames[:n]


def build_option_c_frames(
    *,
    fps: int = EXPORT_FPS,
    seconds: float = OPTION_SECONDS,
) -> list[FrameSpec]:
    """C: carousel ≥4 distinct lines on s₁+s₂+s₃=3 — shows >3 solutions."""
    badge = _badge("C")
    poses = sum_locus_poses_for_demo(SUM_TARGET_C, count=6)
    n = _seconds_to_frames(seconds, fps=fps)
    per = max(2, n // (len(poses) + 1))
    frames: list[FrameSpec] = []

    frames.extend(
        FrameSpec(
            k=poses[0][0],
            b=poses[0][1],
            badge=badge,
            polyline=True,
            caption=CAPTION_C_FAMILY,
        )
        for _ in range(per)
    )

    for i, (k, b) in enumerate(poses):
        cap = CAPTION_C_LINE_N.format(n=i + 1)
        if i == 3:
            cap = f"{cap}\n{CAPTION_C_GT3}"
        for j in range(per):
            frames.append(
                FrameSpec(
                    k=k,
                    b=b,
                    badge=badge,
                    polyline=True,
                    caption=cap if j == 0 else None,
                ),
            )

    while len(frames) < n:
        k, b = poses[-1]
        frames.append(
            FrameSpec(k=k, b=b, badge=badge, polyline=True, caption=CAPTION_C_GT3),
        )
    return frames[:n]


def build_option_d_frames(
    *,
    fps: int = EXPORT_FPS,
    seconds: float = OPTION_SECONDS,
) -> list[FrameSpec]:
    """D: low sum → rise to peak → hold → tilt past peak (sum falls)."""
    info = b_zero_peak_info()
    badge = _badge("D")
    n = _seconds_to_frames(seconds, fps=fps)
    low_n = max(2, n // 7)
    rise_n = max(2, int(n * 0.38))
    peak_n = max(2, n // 6)
    fall_n = max(2, n - low_n - rise_n - peak_n)

    frames: list[FrameSpec] = [
        FrameSpec(k=info.k_low_sum, b=0.0, badge=badge, caption=CAPTION_D_RULE)
        for _ in range(low_n)
    ]
    for i, k in enumerate(_scan_values(info.k_low_sum, info.k_peak, rise_n)):
        frames.append(
            FrameSpec(
                k=k,
                b=0.0,
                badge=badge,
                caption=CAPTION_D_RISE if i == 0 else None,
            ),
        )
    for _ in range(peak_n):
        frames.append(
            FrameSpec(
                k=info.k_peak,
                b=0.0,
                badge=badge,
                caption=CAPTION_D_PEAK,
                highlight_peak=True,
            ),
        )
    for i, k in enumerate(_scan_values(info.k_peak, info.k_past_peak, fall_n)):
        frames.append(
            FrameSpec(
                k=k,
                b=0.0,
                badge=badge,
                caption=CAPTION_D_FALL if i == 0 else None,
            ),
        )
    return frames


_BUILDERS = {
    "A": build_option_a_frames,
    "B": build_option_b_frames,
    "C": build_option_c_frames,
    "D": build_option_d_frames,
}


def build_option_frames(
    letter: OptionLetter,
    *,
    fps: int = EXPORT_FPS,
    seconds: float = OPTION_SECONDS,
) -> list[FrameSpec]:
    if letter not in _BUILDERS:
        raise KeyError(f"unknown option letter: {letter!r}")
    return _BUILDERS[letter](fps=fps, seconds=seconds)


def build_all_option_frames(
    *,
    fps: int = EXPORT_FPS,
    seconds: float = OPTION_SECONDS,
) -> dict[OptionLetter, list[FrameSpec]]:
    return {letter: build_option_frames(letter, fps=fps, seconds=seconds) for letter in OPTION_LETTERS}


build_segment_a_frames = build_option_a_frames
build_segment_b_frames = build_option_b_frames
build_segment_c_frames = build_option_c_frames
build_segment_d_frames = build_option_d_frames
