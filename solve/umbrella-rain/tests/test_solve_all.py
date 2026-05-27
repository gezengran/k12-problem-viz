import subprocess
import sys
from pathlib import Path

import pytest

from umbrella_rain.solve_all import format_report, solve_all


def test_solve_all_structure():
    r = solve_all()
    assert "scene_a" in r
    assert "scene_b" in r
    assert "scene_c" in r
    assert r["scene_a"]["c_height_m"] == pytest.approx(1.8)
    assert r["scene_a"]["pk_theta_72_m"] == pytest.approx(0.26, abs=0.03)


def test_format_report_contains_key_values():
    text = format_report()
    assert "1.80" in text or "1.8" in text
    assert "72" in text
    assert "60" in text


def test_cli_main_runs():
    case_dir = Path(__file__).resolve().parents[1]
    env = {**dict(__import__("os").environ), "PYTHONPATH": str(case_dir)}
    proc = subprocess.run(
        [sys.executable, "-m", "umbrella_rain"],
        cwd=str(case_dir),
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0
    assert "场景 A" in proc.stdout
    assert "1.8" in proc.stdout
