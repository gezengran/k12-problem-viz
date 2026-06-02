"""Matplotlib Chinese font setup with English fallback."""

from __future__ import annotations

import platform

_CJK_CONFIGURED: bool | None = None

# macOS / Windows / Linux common CJK-capable families (first match wins).
_CJK_FONT_CANDIDATES: tuple[str, ...] = (
    "PingFang SC",
    "Heiti SC",
    "STHeiti",
    "Arial Unicode MS",
    "Hiragino Sans GB",
    "Noto Sans CJK SC",
    "Noto Sans SC",
    "Source Han Sans SC",
    "Microsoft YaHei",
    "SimHei",
    "WenQuanYi Micro Hei",
)

_CJK_NAME_KEYWORDS: tuple[str, ...] = (
    "PingFang",
    "Heiti",
    "Noto Sans CJK",
    "Noto Sans SC",
    "Source Han",
    "YaHei",
    "SimHei",
    "WenQuanYi",
    "Arial Unicode",
)


def _available_font_names() -> set[str]:
    from matplotlib import font_manager

    return {entry.name for entry in font_manager.fontManager.ttflist}


def _pick_cjk_font(available: set[str]) -> str | None:
    for name in _CJK_FONT_CANDIDATES:
        if name in available:
            return name
    for name in sorted(available):
        if any(keyword in name for keyword in _CJK_NAME_KEYWORDS):
            return name
    return None


def setup_matplotlib_chinese() -> bool:
    """Prefer a CJK font for matplotlib; return True if one was configured."""
    global _CJK_CONFIGURED
    if _CJK_CONFIGURED is not None:
        return _CJK_CONFIGURED

    import matplotlib.pyplot as plt

    font = _pick_cjk_font(_available_font_names())
    if font is None:
        _CJK_CONFIGURED = False
        return False

    # DejaVu Sans remains fallback for math glyphs in labels like $y=x^2$.
    plt.rcParams["font.sans-serif"] = [font, "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False
    _CJK_CONFIGURED = True
    return True


def cjk_font_probe_summary() -> str:
    """Short diagnostic string for logs (platform + chosen font or none)."""
    setup_matplotlib_chinese()
    from matplotlib import pyplot as plt

    family = plt.rcParams["font.sans-serif"]
    primary = family[0] if family else "DejaVu Sans"
    ok = _CJK_CONFIGURED is True
    return f"{platform.system()}: cjk={'yes' if ok else 'no'} primary={primary!r}"
