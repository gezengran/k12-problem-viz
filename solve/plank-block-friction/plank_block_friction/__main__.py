"""CLI: export classic preset-1 MP4s and (on macOS) Live Photos."""

from __future__ import annotations

import platform

from plank_block_friction.export import export_classic_preset1, export_classic_preset1_live


def main() -> None:
    mp4_paths = export_classic_preset1()
    for view, path in mp4_paths.items():
        print(f"OK preset-1-{view}: {path}")

    if platform.system() == "Darwin":
        live_paths = export_classic_preset1_live()
        for view, path in live_paths.items():
            print(f"OK preset-1-{view} live: {path}")


if __name__ == "__main__":
    main()
