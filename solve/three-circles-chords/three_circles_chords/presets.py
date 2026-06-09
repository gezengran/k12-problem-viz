"""Segment presets — derived from constraints.py and validated by tests."""

from __future__ import annotations

from dataclasses import dataclass

from three_circles_chords.constraints import (
    SUM_TARGET_C,
    b_zero_peak_info,
    equal_chord_solutions,
    sample_sum_locus,
)
SegmentId = str


@dataclass(frozen=True)
class SegmentPose:
    k: float
    b: float


@dataclass(frozen=True)
class SegmentCPreset:
    frames: tuple[SegmentPose, ...]


def _segment_b_poses() -> tuple[SegmentPose, ...]:
    return tuple(SegmentPose(k=k, b=b) for k, b in equal_chord_solutions())


def _segment_b_pose() -> SegmentPose:
    return _segment_b_poses()[0]


def _segment_c_frames() -> tuple[SegmentPose, ...]:
    return tuple(SegmentPose(k=k, b=b) for k, b in sample_sum_locus(SUM_TARGET_C))


def _segment_d_pose() -> SegmentPose:
    info = b_zero_peak_info()
    return SegmentPose(k=info.k_peak, b=0.0)


_PRESETS: dict[SegmentId, object] = {
    "segment-B": _segment_b_pose(),
    "segment-C": SegmentCPreset(frames=_segment_c_frames()),
    "segment-D": _segment_d_pose(),
}


def preset(segment_id: SegmentId):
    if segment_id not in _PRESETS:
        raise KeyError(f"unknown segment_id: {segment_id!r}")
    return _PRESETS[segment_id]


def segment_b_pose() -> SegmentPose:
    return preset("segment-B")  # type: ignore[return-value]


def segment_b_poses() -> tuple[SegmentPose, ...]:
    return _segment_b_poses()


def segment_c_frames() -> tuple[SegmentPose, ...]:
    return preset("segment-C").frames  # type: ignore[union-attr]


def segment_d_pose() -> SegmentPose:
    return preset("segment-D")  # type: ignore[return-value]
