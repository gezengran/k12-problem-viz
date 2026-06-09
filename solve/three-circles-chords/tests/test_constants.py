import math

import pytest

from three_circles_chords.constants import (
    CASE_ID,
    CIRCLE_CENTERS,
    CIRCLE_RADIUS,
    PORTRAIT_ASPECT,
)


def test_case_id():
    assert CASE_ID == "three-circles-chords"


def test_circle_centers_match_problem_statement():
    assert CIRCLE_CENTERS == (
        (-1.0, 0.0),
        (1.0, 0.0),
        (0.0, math.sqrt(3.0)),
    )
    assert CIRCLE_RADIUS == 1.0


def test_portrait_aspect_ratio_is_three_to_four():
    assert PORTRAIT_ASPECT == pytest.approx(4.0 / 3.0, rel=1e-6)
