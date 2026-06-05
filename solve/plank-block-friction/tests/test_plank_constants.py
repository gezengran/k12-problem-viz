from plank_block_friction.constants import CASE_ID, G, MASS_RATIO, V0


def test_case_id():
    assert CASE_ID == "plank-block-friction"


def test_default_physical_constants():
    assert G == 10.0
    assert V0 == 4.0
    assert MASS_RATIO == 15.0
