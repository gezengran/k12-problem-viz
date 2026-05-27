from umbrella_rain.constants import (
    ARM_EXTEND_MAX,
    BODY_HEIGHT,
    BODY_WIDTH,
    CANOPY_WIDTH,
    CASE_ID,
    CENTER_HEIGHT,
    FRONT_EDGE_X,
    HAND_HEIGHT,
    HANDLE_LENGTH,
    MAX_HAND_X,
)


def test_case_id():
    assert CASE_ID == "umbrella-rain"


def test_body_and_umbrella_constants():
    assert BODY_WIDTH == 0.2
    assert BODY_HEIGHT == 1.6
    assert CANOPY_WIDTH == 1.0
    assert HANDLE_LENGTH == 0.45
    assert HAND_HEIGHT == 1.35
    assert CENTER_HEIGHT == 1.8
    assert MAX_HAND_X == FRONT_EDGE_X + ARM_EXTEND_MAX == 0.7
