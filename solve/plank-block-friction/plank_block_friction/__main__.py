"""CLI: export all preset MP4s to ami/plank-block-friction/."""

from __future__ import annotations

from plank_block_friction.export import export_all_presets


def main() -> None:
    paths = export_all_presets()
    for preset_id, path in paths.items():
        print(f"OK {preset_id}: {path}")


if __name__ == "__main__":
    main()
