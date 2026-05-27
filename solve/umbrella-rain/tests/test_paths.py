from paths import ami_dir, project_root, solve_case_dir

from umbrella_rain.constants import CASE_ID


def test_project_root_exists():
    assert project_root().is_dir()


def test_ami_dir_for_umbrella_rain():
    d = ami_dir(CASE_ID)
    assert d.name == CASE_ID
    assert d.parent.name == "ami"
    assert d.is_dir()


def test_solve_case_dir():
    d = solve_case_dir(CASE_ID)
    assert d.name == CASE_ID
    assert "solve" in d.parts
