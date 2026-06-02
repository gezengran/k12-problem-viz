"""Viz smoke tests for compound-growth."""

from __future__ import annotations

import platform
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pytest

from compound_growth.constants import N_FRAMES
from compound_growth import viz as compound_viz
from compound_growth.viz import _draw_frame, export_live_demo


def test_title_english_when_no_cjk_font(monkeypatch):
    monkeypatch.setattr(compound_viz, "_USE_CHINESE", False)
    assert "Compound growth" in compound_viz._title()
    assert compound_viz._intersection_label(1465.0).startswith("Overtake")


def test_draw_frame_no_crash():
    fig, ax = plt.subplots()
    _draw_frame(N_FRAMES // 2, ax)
    plt.close(fig)


@pytest.mark.slow
@pytest.mark.skipif(platform.system() != "Darwin", reason="Live Photo export needs macOS")
def test_export_live_demo(tmp_path: Path):
    pvt = export_live_demo(tmp_path)
    assert pvt.suffix == ".pvt"
    assert pvt.is_dir()
