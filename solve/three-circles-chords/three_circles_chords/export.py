"""Live Photo export — one .pvt per option (A/B/C/D)."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from live_photo_export import (
    LIVE_PHOTO_SIZE,
    export_live_photo_from_matplotlib,
    letterbox_image,
)
from paths import ami_dir
from PIL import Image

from three_circles_chords.constants import CASE_ID, DPI, EXPORT_FPS, FIG_HEIGHT, FIG_WIDTH
from three_circles_chords.scenes import OPTION_LETTERS, OptionLetter, export_basename
from three_circles_chords.timeline import FrameSpec, build_option_frames
from three_circles_chords.viz import portrait_figsize, render_frame


def render_timeline_frame(spec: FrameSpec, ax) -> None:
    render_frame(
        spec.k,
        spec.b,
        badge=spec.badge,
        polyline=spec.polyline,
        caption=spec.caption,
        highlight_peak=spec.highlight_peak,
        ax=ax,
    )


def capture_timeline_frames(timeline: list[FrameSpec]) -> list[Image.Image]:
    frames: list[Image.Image] = []
    fig, ax = plt.subplots(figsize=portrait_figsize(), dpi=DPI)
    try:
        for spec in timeline:
            render_timeline_frame(spec, ax)
            fig.canvas.draw()
            w, h = fig.canvas.get_width_height()
            buf = fig.canvas.buffer_rgba()
            frames.append(Image.frombytes("RGBA", (w, h), buf).convert("RGB"))
    finally:
        plt.close(fig)
    return frames


def export_option_live(
    letter: OptionLetter,
    path: Path | None = None,
    *,
    fps: int = EXPORT_FPS,
    keep_intermediates: bool = True,
) -> Path:
    """Export one option scene as .pvt under ami/three-circles-chords/."""
    slug = export_basename(letter)
    out_base = path or (ami_dir(CASE_ID) / slug)
    out_base = Path(out_base)
    timeline = build_option_frames(letter, fps=fps)

    def _builder(i: int, ax) -> None:
        render_timeline_frame(timeline[i], ax)

    result = export_live_photo_from_matplotlib(
        _builder,
        len(timeline),
        out_base,
        figsize=(FIG_WIDTH, FIG_HEIGHT),
        dpi=DPI,
        fps=fps,
        size=LIVE_PHOTO_SIZE,
        keep_intermediates=keep_intermediates,
    )
    return result.pvt


def export_all_options(
    *,
    fps: int = EXPORT_FPS,
    keep_intermediates: bool = True,
) -> dict[OptionLetter, Path]:
    """Export four standalone Live Photos (A, B, C, D)."""
    outputs: dict[OptionLetter, Path] = {}
    for letter in OPTION_LETTERS:
        outputs[letter] = export_option_live(
            letter,
            fps=fps,
            keep_intermediates=keep_intermediates,
        )
    return outputs


def export_live(
    path: Path | None = None,
    *,
    fps: int = EXPORT_FPS,
    keep_intermediates: bool = True,
) -> Path:
    """Backward-compatible alias: exports option A only."""
    return export_option_live("A", path=path, fps=fps, keep_intermediates=keep_intermediates)


def export_debug_png_sequence(
    letter: OptionLetter,
    dest: Path | None = None,
) -> list[Path]:
    """Write one option's frames as PNGs for HITL review."""
    slug = export_basename(letter)
    root = dest or (ami_dir(CASE_ID) / f"{slug}_debug")
    root.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    from three_circles_chords.viz import save_frame_png

    for i, spec in enumerate(build_option_frames(letter)):
        out = root / f"frame_{i:04d}.png"
        save_frame_png(
            spec.k,
            spec.b,
            out,
            badge=spec.badge,
            polyline=spec.polyline,
            caption=spec.caption,
            highlight_peak=spec.highlight_peak,
        )
        paths.append(out)
    return paths


def still_aspect_ratio(pvt_path: Path) -> float:
    """Height/width of letterboxed still inside the Live pair."""
    jpg = pvt_path.with_suffix(".jpg")
    if not jpg.exists():
        raise FileNotFoundError(f"missing still image: {jpg}")
    img = Image.open(jpg)
    boxed = letterbox_image(img, size=LIVE_PHOTO_SIZE)
    w, h = boxed.size
    return h / w
