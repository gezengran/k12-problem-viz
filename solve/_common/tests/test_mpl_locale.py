"""Tests for matplotlib CJK font setup."""

from __future__ import annotations

from unittest.mock import patch

from mpl_locale import setup_matplotlib_chinese


def test_setup_matplotlib_chinese_returns_bool():
    # Idempotent; result depends on host fonts.
    first = setup_matplotlib_chinese()
    second = setup_matplotlib_chinese()
    assert isinstance(first, bool)
    assert first == second


@patch("mpl_locale._pick_cjk_font", return_value=None)
def test_setup_false_when_no_cjk_font(_mock_pick):
    import mpl_locale

    mpl_locale._CJK_CONFIGURED = None
    assert setup_matplotlib_chinese() is False


@patch("mpl_locale._pick_cjk_font", return_value="PingFang SC")
def test_setup_true_when_font_found(_mock_pick):
    import mpl_locale

    mpl_locale._CJK_CONFIGURED = None
    assert setup_matplotlib_chinese() is True
