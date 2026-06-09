import pytest

from three_circles_chords.constants import EPS
from three_circles_chords.envelope import b_envelope, tangent_circle_index_at_boundary
from three_circles_chords.geometry import IntersectionKind, line_chord_state


def test_envelope_has_positive_width():
    env = b_envelope(0.5)
    assert env.b_min < env.b_max


def test_b_min_boundary_is_tangent():
    env = b_envelope(0.5)
    state = line_chord_state(env.k, env.b_min)
    kinds = {c.kind for c in state.chords}
    assert IntersectionKind.TANGENT in kinds
    assert state.chords[tangent_circle_index_at_boundary(env, at_min=True)].length == pytest.approx(
        0.0,
        abs=EPS,
    )


def test_interior_samples_are_triple_secant():
    env = b_envelope(0.5)
    for b in env.sample(7):
        state = line_chord_state(env.k, b)
        assert state.all_secant


def test_uniform_samples_stay_inside_envelope():
    env = b_envelope(1.0)
    for b in env.sample(10):
        assert env.contains(b)
