"""Per-option scene recipes: map MCQ text → animation strategy."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

OptionLetter = Literal["A", "B", "C", "D"]

OPTION_LETTERS: tuple[OptionLetter, ...] = ("A", "B", "C", "D")


@dataclass(frozen=True)
class OptionScene:
    letter: OptionLetter
    slug: str
    summary: str
    strategy: str


OPTION_SCENES: dict[OptionLetter, OptionScene] = {
    "A": OptionScene(
        letter="A",
        slug="option-a",
        summary="k 的取值范围（三圆均有弦）",
        strategy="固定 b 增大 k，直至某圆相切/弦消失并定格。",
    ),
    "B": OptionScene(
        letter="B",
        slug="option-b",
        summary="s₁ = s₂ = s₃ 的直线约束",
        strategy="逐条展示 3 条解析解（心到直线距离相等，恰 3 条）。",
    ),
    "C": OptionScene(
        letter="C",
        slug="option-c",
        summary="s₁+s₂+s₃ = 3 的直线族",
        strategy="1 方程 2 未知数 → 无穷多直线；快切 ≥4 条不同直线证 >3。",
    ),
    "D": OptionScene(
        letter="D",
        slug="option-d",
        summary="b = 0 时 ∑sᵢ 极大",
        strategy="总和由低升高 → 峰值定格 → 再转 k 总和下降。",
    ),
}


def scene_for(letter: OptionLetter) -> OptionScene:
    return OPTION_SCENES[letter]


def export_basename(letter: OptionLetter) -> str:
    return f"{OPTION_SCENES[letter].slug}-live"
