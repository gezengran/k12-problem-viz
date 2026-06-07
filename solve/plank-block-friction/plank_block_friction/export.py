"""MP4 export: one view per file (ground, block, or plank reference)."""

from __future__ import annotations

import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from live_photo_export import export_live_photo_from_matplotlib
from paths import ami_dir

from plank_block_friction.constants import (
    CASE_ID,
    CLASSIC_PRESET_ID,
    DPI,
    EXPORT_FPS,
    PLAYBACK_SECONDS,
    VIEW_BLOCK,
    VIEW_GROUND,
    VIEW_PLANK,
)
from plank_block_friction.contact import sample_for_display
from plank_block_friction.presets import animation_duration, sim_config_for_preset
from plank_block_friction.simulation import run_simulation, sample_at_time
from plank_block_friction.viz import (
    figure_figsize,
    render_block_frame,
    render_ground_frame,
    render_plank_frame,
)

SYNC_HIGHLIGHT_WINDOW = 1.0
VALID_VIEWS = (VIEW_GROUND, VIEW_BLOCK, VIEW_PLANK)


def view_output_stem(preset_id: str, view: str) -> str:
    if view not in VALID_VIEWS:
        raise ValueError(f"view must be one of {VALID_VIEWS}, got {view!r}")
    return f"{preset_id}-{view}"


def _frame_times(
    physics_duration: float,
    *,
    fps: int,
    n_frames: int | None,
    playback_seconds: float | None,
) -> list[float]:
    if n_frames is not None:
        if n_frames < 2:
            return [0.0] * max(1, n_frames)
        return [physics_duration * i / (n_frames - 1) for i in range(n_frames)]
    wall = playback_seconds if playback_seconds is not None else physics_duration
    n = max(2, int(math.ceil(wall * fps)))
    return [physics_duration * i / (n - 1) for i in range(n)]


def _should_highlight_sync(t: float, t_sync: float | None) -> bool:
    if t_sync is None:
        return False
    return t_sync <= t <= t_sync + SYNC_HIGHLIGHT_WINDOW


def export_view_mp4(
    preset_id: str,
    view: str,
    path: Path | None = None,
    *,
    fps: int = EXPORT_FPS,
    n_frames: int | None = None,
    playback_seconds: float | None = PLAYBACK_SECONDS,
) -> Path:
    """Render one preset + one reference frame to MP4."""
    if view not in VALID_VIEWS:
        raise ValueError(f"view must be one of {VALID_VIEWS}, got {view!r}")

    config = sim_config_for_preset(preset_id)
    duration = animation_duration(preset_id)
    traj = run_simulation(config, duration)
    t_sync = traj.t_sync

    if path is None:
        path = ami_dir(CASE_ID) / f"{view_output_stem(preset_id, view)}.mp4"
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    times = _frame_times(
        duration,
        fps=fps,
        n_frames=n_frames,
        playback_seconds=playback_seconds if n_frames is None else None,
    )

    from matplotlib import animation as mpl_animation

    if not mpl_animation.writers.is_available("ffmpeg"):
        raise RuntimeError(
            "Video export requires ffmpeg on PATH. "
            "Install with: conda install -n math -c conda-forge ffmpeg"
        )

    fig, ax = plt.subplots(1, 1, figsize=figure_figsize())

    def update(i: int) -> None:
        ax.clear()
        t = times[i]
        sample = sample_for_display(sample_at_time(traj, t))
        highlight = _should_highlight_sync(t, t_sync)
        _render_view_frame(view, sample, highlight=highlight, ax=ax)

    anim = FuncAnimation(fig, update, frames=len(times), interval=1000 // fps)
    try:
        anim.save(path, writer="ffmpeg", fps=fps, dpi=DPI)
    finally:
        plt.close(fig)
    return path


def live_output_stem(preset_id: str, view: str) -> str:
    return f"{view_output_stem(preset_id, view)}_live"


def _render_view_frame(
    view: str,
    sample,
    *,
    highlight: bool,
    ax,
) -> None:
    if view == VIEW_GROUND:
        render_ground_frame(sample, highlight_sync=highlight, ax=ax)
    elif view == VIEW_BLOCK:
        render_block_frame(sample, highlight_sync=highlight, ax=ax)
    else:
        render_plank_frame(sample, highlight_sync=highlight, ax=ax)


def export_view_live(
    preset_id: str,
    view: str,
    base_path: Path | None = None,
    *,
    fps: int = EXPORT_FPS,
    n_frames: int | None = None,
    playback_seconds: float | None = PLAYBACK_SECONDS,
    keep_intermediates: bool = False,
) -> Path:
    """Render one preset + one reference frame to Live Photo (.pvt). macOS only."""
    if view not in VALID_VIEWS:
        raise ValueError(f"view must be one of {VALID_VIEWS}, got {view!r}")

    config = sim_config_for_preset(preset_id)
    duration = animation_duration(preset_id)
    traj = run_simulation(config, duration)
    t_sync = traj.t_sync

    if base_path is None:
        base_path = ami_dir(CASE_ID) / live_output_stem(preset_id, view)
    base_path = Path(base_path)

    times = _frame_times(
        duration,
        fps=fps,
        n_frames=n_frames,
        playback_seconds=playback_seconds if n_frames is None else None,
    )

    def frames_builder(i: int, ax) -> None:
        t = times[i]
        sample = sample_for_display(sample_at_time(traj, t))
        highlight = _should_highlight_sync(t, t_sync)
        _render_view_frame(view, sample, highlight=highlight, ax=ax)

    result = export_live_photo_from_matplotlib(
        frames_builder,
        len(times),
        base_path,
        figsize=figure_figsize(),
        dpi=DPI,
        fps=fps,
        keep_intermediates=keep_intermediates,
    )
    return result.pvt


def export_classic_preset1_live(
    ami_root: Path | None = None,
    *,
    n_frames: int | None = None,
    keep_intermediates: bool = False,
) -> dict[str, Path]:
    """Export preset-1 ground, block, and plank views as Live Photos."""
    root = ami_root or ami_dir(CASE_ID)
    return {
        VIEW_GROUND: export_view_live(
            CLASSIC_PRESET_ID,
            VIEW_GROUND,
            root / live_output_stem(CLASSIC_PRESET_ID, VIEW_GROUND),
            n_frames=n_frames,
            keep_intermediates=keep_intermediates,
        ),
        VIEW_BLOCK: export_view_live(
            CLASSIC_PRESET_ID,
            VIEW_BLOCK,
            root / live_output_stem(CLASSIC_PRESET_ID, VIEW_BLOCK),
            n_frames=n_frames,
            keep_intermediates=keep_intermediates,
        ),
        VIEW_PLANK: export_view_live(
            CLASSIC_PRESET_ID,
            VIEW_PLANK,
            root / live_output_stem(CLASSIC_PRESET_ID, VIEW_PLANK),
            n_frames=n_frames,
            keep_intermediates=keep_intermediates,
        ),
    }


def export_classic_preset1(
    ami_root: Path | None = None,
    *,
    n_frames: int | None = None,
) -> dict[str, Path]:
    """Export preset-1 ground, block, and plank views as separate MP4 files."""
    root = ami_root or ami_dir(CASE_ID)
    return {
        VIEW_GROUND: export_view_mp4(
            CLASSIC_PRESET_ID,
            VIEW_GROUND,
            root / f"{view_output_stem(CLASSIC_PRESET_ID, VIEW_GROUND)}.mp4",
            n_frames=n_frames,
        ),
        VIEW_BLOCK: export_view_mp4(
            CLASSIC_PRESET_ID,
            VIEW_BLOCK,
            root / f"{view_output_stem(CLASSIC_PRESET_ID, VIEW_BLOCK)}.mp4",
            n_frames=n_frames,
        ),
        VIEW_PLANK: export_view_mp4(
            CLASSIC_PRESET_ID,
            VIEW_PLANK,
            root / f"{view_output_stem(CLASSIC_PRESET_ID, VIEW_PLANK)}.mp4",
            n_frames=n_frames,
        ),
    }


# Backward-compatible aliases used in older tests.
def export_mp4(
    preset_id: str,
    path: Path | None = None,
    *,
    fps: int = EXPORT_FPS,
    n_frames: int | None = None,
    playback_seconds: float | None = PLAYBACK_SECONDS,
) -> Path:
    """Export preset-1 block view (default single-view product)."""
    if preset_id != CLASSIC_PRESET_ID:
        return export_view_mp4(
            preset_id,
            VIEW_GROUND,
            path,
            fps=fps,
            n_frames=n_frames,
            playback_seconds=playback_seconds,
        )
    if path is None:
        return export_view_mp4(
            preset_id,
            VIEW_BLOCK,
            fps=fps,
            n_frames=n_frames,
            playback_seconds=playback_seconds,
        )
    return export_view_mp4(
        preset_id,
        VIEW_BLOCK,
        path,
        fps=fps,
        n_frames=n_frames,
        playback_seconds=playback_seconds,
    )


def export_all_presets(
    ami_root: Path | None = None,
    *,
    n_frames: int | None = None,
) -> dict[str, Path]:
    """Export classic preset-1 as three separate view MP4s."""
    return export_classic_preset1(ami_root, n_frames=n_frames)
