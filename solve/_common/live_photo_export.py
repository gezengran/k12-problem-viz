"""Xiaohongshu / iOS Live Photo (.pvt) export from PIL frame sequences."""

from __future__ import annotations

import platform
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from PIL import Image

try:
    from makelive import save_live_photo_pair_as_pvt
except ImportError:  # pragma: no cover - strict failure at export time
    save_live_photo_pair_as_pvt = None  # type: ignore[misc, assignment]

# 3:4 portrait canvas for Live still/video (letterbox from 9:16 diagrams).
LIVE_PHOTO_SIZE = (720, 960)

class LiveExportError(RuntimeError):
    """Live Photo export cannot proceed (platform, deps, or invalid input)."""


@dataclass(frozen=True)
class LiveExportResult:
    """Paths produced by a Live Photo export."""

    pvt: Path
    jpg: Path | None = None
    mov: Path | None = None


def letterbox_image(
    img: Image.Image,
    size: tuple[int, int] = LIVE_PHOTO_SIZE,
) -> Image.Image:
    """Scale to fit inside size, pad with white."""
    target_w, target_h = size
    src_w, src_h = img.size
    scale = min(target_w / src_w, target_h / src_h)
    new_w = max(1, int(src_w * scale))
    new_h = max(1, int(src_h * scale))
    resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", size, (255, 255, 255))
    canvas.paste(resized, ((target_w - new_w) // 2, (target_h - new_h) // 2))
    return canvas


def _require_darwin() -> None:
    if platform.system() != "Darwin":
        raise LiveExportError(
            "Live Photo (.pvt) export requires macOS. "
            "Run export on Darwin with makelive and ffmpeg installed."
        )


def _require_ffmpeg() -> None:
    if shutil.which("ffmpeg") is None:
        raise LiveExportError(
            "MOV export requires ffmpeg on PATH. "
            "Install with: conda install -n math -c conda-forge ffmpeg"
        )


def _require_makelive() -> None:
    if save_live_photo_pair_as_pvt is None:
        raise LiveExportError(
            "Live Photo export requires the makelive package. "
            "On macOS: pip install -r requirements-macos.txt"
        )


def _save_mov_from_frames(frames: list[Image.Image], path: Path, *, fps: int) -> Path:
    _require_ffmpeg()
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        for i, frame in enumerate(frames):
            frame.save(tmp_dir / f"frame_{i:04d}.png")
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-framerate",
                str(fps),
                "-i",
                str(tmp_dir / "frame_%04d.png"),
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p",
                "-movflags",
                "+faststart",
                str(path),
            ],
            check=True,
            capture_output=True,
        )
    return path


def export_live_photo_from_frames(
    frames: list[Image.Image],
    base_path: Path,
    *,
    fps: int = 10,
    size: tuple[int, int] = LIVE_PHOTO_SIZE,
    jpeg_quality: int = 95,
    keep_intermediates: bool = True,
) -> LiveExportResult:
    """Letterbox frames, write JPEG+MOV, package as .pvt for AirDrop / Photos."""
    if not frames:
        raise LiveExportError("export_live_photo_from_frames requires at least one frame")

    _require_darwin()
    _require_makelive()

    base_path = Path(base_path)
    base_path.parent.mkdir(parents=True, exist_ok=True)
    jpg_path = base_path.with_suffix(".jpg")
    mov_path = base_path.with_suffix(".mov")

    letterbox_image(frames[0], size=size).save(jpg_path, format="JPEG", quality=jpeg_quality)
    xhs_frames = [letterbox_image(frame, size=size) for frame in frames]
    _save_mov_from_frames(xhs_frames, mov_path, fps=fps)

    _, pvt_path = save_live_photo_pair_as_pvt(jpg_path, mov_path)

    if not keep_intermediates:
        jpg_path.unlink(missing_ok=True)
        mov_path.unlink(missing_ok=True)
        return LiveExportResult(pvt=pvt_path)

    return LiveExportResult(pvt=pvt_path, jpg=jpg_path, mov=mov_path)


def capture_matplotlib_frames(
    frames_builder: Callable[[int, object], None],
    n_frames: int,
    *,
    figsize: tuple[float, float] = (9.0, 16.0),
    dpi: int = 80,
) -> list[Image.Image]:
    """Render n_frames by calling frames_builder(i, ax) on a reused Figure."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    frames: list[Image.Image] = []
    try:
        for i in range(n_frames):
            ax.clear()
            frames_builder(i, ax)
            fig.canvas.draw()
            width, height = fig.canvas.get_width_height()
            buffer = fig.canvas.buffer_rgba()
            frames.append(Image.frombytes("RGBA", (width, height), buffer).convert("RGB"))
    finally:
        plt.close(fig)
    return frames


def export_live_photo_from_matplotlib(
    frames_builder: Callable[[int, object], None],
    n_frames: int,
    base_path: Path,
    *,
    figsize: tuple[float, float] = (9.0, 16.0),
    dpi: int = 80,
    fps: int = 10,
    size: tuple[int, int] = LIVE_PHOTO_SIZE,
    jpeg_quality: int = 95,
    keep_intermediates: bool = True,
) -> LiveExportResult:
    """Matplotlib adapter: frames_builder(i, ax) → Live Photo export."""
    frames = capture_matplotlib_frames(
        frames_builder,
        n_frames,
        figsize=figsize,
        dpi=dpi,
    )
    return export_live_photo_from_frames(
        frames,
        base_path,
        fps=fps,
        size=size,
        jpeg_quality=jpeg_quality,
        keep_intermediates=keep_intermediates,
    )
