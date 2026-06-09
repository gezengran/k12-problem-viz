"""CLI: export per-option Live Photos for three-circles-chords."""

from __future__ import annotations

import argparse
import platform
import sys

from three_circles_chords.export import export_all_options, export_option_live
from three_circles_chords.scenes import OPTION_LETTERS, OptionLetter


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export 3:4 Live Photos — one animation per MCQ option (A–D).",
    )
    parser.add_argument(
        "--option",
        choices=OPTION_LETTERS,
        help="Export a single option (default: export all four).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    if platform.system() != "Darwin":
        print(
            "Live Photo (.pvt) export requires macOS. "
            "Run geometry/viz tests on any platform.",
            file=sys.stderr,
        )
        return 1

    args = _parse_args(argv)
    if args.option:
        letter: OptionLetter = args.option
        pvt = export_option_live(letter)
        print(pvt)
        return 0

    outputs = export_all_options()
    for letter in OPTION_LETTERS:
        print(f"{letter}: {outputs[letter]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
