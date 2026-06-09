import pytest

from three_circles_chords.constants import EPS, EXPORT_FPS, OPTION_A_B, OPTION_SECONDS
from three_circles_chords.constraints import (
    SUM_TARGET_C,
    b_zero_peak_info,
    chords_equal,
    equal_chord_solutions,
)
from three_circles_chords.geometry import IntersectionKind, line_chord_state
from three_circles_chords.timeline import (
    build_all_option_frames,
    build_option_a_frames,
    build_option_b_frames,
    build_option_c_frames,
    build_option_d_frames,
)
from three_circles_chords.viz import polyline_length


def test_each_option_has_expected_duration():
    for letter, frames in build_all_option_frames().items():
        expected = int(round(OPTION_SECONDS * EXPORT_FPS))
        assert len(frames) == pytest.approx(expected, abs=3), letter


def test_option_a_scans_to_invalid_k():
    frames = build_option_a_frames()
    assert all(abs(f.b - OPTION_A_B) < EPS for f in frames)
    last = frames[-1]
    state = line_chord_state(last.k, last.b)
    kinds = {c.kind for c in state.chords}
    assert IntersectionKind.TANGENT in kinds or IntersectionKind.NONE in kinds
    assert any(f.caption for f in frames)


def test_option_b_only_three_equal_chord_lines():
    frames = build_option_b_frames()
    sol_set = {(round(k, 3), round(b, 3)) for k, b in equal_chord_solutions()}
    for f in frames:
        assert chords_equal(f.k, f.b)
    hit = {(round(f.k, 3), round(f.b, 3)) for f in frames}
    assert hit == sol_set
    assert any("仅 3 条" in (f.caption or "") for f in frames)


def test_option_c_shows_more_than_three_distinct_lines():
    frames = build_option_c_frames()
    locus_frames = [f for f in frames if f.polyline]
    assert len(locus_frames) >= 4
    unique = {(round(f.k, 2), round(f.b, 2)) for f in locus_frames}
    assert len(unique) >= 4
    sums = {round(line_chord_state(f.k, f.b).sum_lengths, 2) for f in locus_frames}
    assert all(s == pytest.approx(SUM_TARGET_C, abs=0.08) for s in sums)
    assert any("无穷多" in (f.caption or "") for f in frames)
    assert any("4 条以上" in (f.caption or "") for f in frames)
    lengths = [polyline_length(line_chord_state(f.k, f.b)) for f in locus_frames[:4]]
    assert lengths[0] == pytest.approx(lengths[1], abs=0.15)


def test_option_d_peak_then_past_peak_sum_decreases():
    info = b_zero_peak_info()
    frames = build_option_d_frames()
    assert all(abs(f.b) < EPS for f in frames)
    peak_frames = [f for f in frames if f.highlight_peak]
    assert len(peak_frames) >= 2
    assert peak_frames[-1].k == pytest.approx(info.k_peak, abs=0.05)
    peak_sum = line_chord_state(info.k_peak, 0.0).sum_lengths
    past_sum = line_chord_state(info.k_past_peak, 0.0).sum_lengths
    assert past_sum < peak_sum - 0.01
    assert frames[-1].k == pytest.approx(info.k_past_peak, abs=0.05)
    assert any("极大" in (f.caption or "") for f in frames)
    assert any("下降" in (f.caption or "") for f in frames)
