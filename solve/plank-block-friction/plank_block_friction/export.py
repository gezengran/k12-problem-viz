"""MP4 export and optional Live Photo packaging."""

from __future__ import annotations

import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from paths import ami_dir

from plank_block_friction.constants import CASE_ID, DPI, EXPORT_FPS, PLAYBACK_SECONDS
from plank_block_friction.contact import sample_for_display
from plank_block_friction.presets import animation_duration, get_preset, sim_config_for_preset
from plank_block_friction.simulation import run_simulation, sample_at_time
from plank_block_friction.viz import _USE_CHINESE, portrait_figsize, render_dual_frame

_ENGLISH_TITLES = {
    "preset-1": "Baseline: smooth ground",
    "preset-2": "Strong coupling: high mu2",
    "preset-3": "Ground drag: mu1 > 0",
}


def _display_title(preset_id: str, chinese_title: str) -> str:
    if _USE_CHINESE:
        return chinese_title
    return _ENGLISH_TITLES.get(preset_id, preset_id)

SYNC_HIGHLIGHT_WINDOW = 0.25


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
    return abs(t - t_sync) <= SYNC_HIGHLIGHT_WINDOW * 0.5


def export_mp4(
    preset_id: str,
    path: Path | None = None,
    *,
    fps: int = EXPORT_FPS,
    n_frames: int | None = None,
    playback_seconds: float | None = PLAYBACK_SECONDS,
) -> Path:
    """Render preset animation to MP4 under ami/plank-block-friction/."""
    preset = get_preset(preset_id)
    config = sim_config_for_preset(preset_id)
    duration = animation_duration(preset_id)
    traj = run_simulation(config, duration)
    t_sync = traj.t_sync

    if path is None:
        path = ami_dir(CASE_ID) / f"{preset_id}.mp4"
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

    fig, (ax_top, ax_bottom) = plt.subplots(
        2,
        1,
        figsize=portrait_figsize(),
        gridspec_kw={"height_ratios": [1, 1], "hspace": 0.08},
    )

    def update(i: int) -> None:
        ax_top.clear()
        ax_bottom.clear()
        t = times[i]
        sample = sample_for_display(sample_at_time(traj, t))
        highlight = _should_highlight_sync(t, t_sync)
        render_dual_frame(
            sample,
            highlight_sync=highlight,
            ax_top=ax_top,
            ax_bottom=ax_bottom,
        )
        if i == 0:
            fig.suptitle(
                _display_title(preset_id, preset.title),
                fontsize=12,
                fontweight="bold",
                y=0.98,
            )

    anim = FuncAnimation(fig, update, frames=len(times), interval=1000 // fps)
    try:
        anim.save(path, writer="ffmpeg", fps=fps, dpi=DPI)
    finally:
        plt.close(fig)
    return path


def export_all_presets(
    ami_root: Path | None = None,
    *,
    n_frames: int | None = None,
) -> dict[str, Path]:
    """Export MP4 for preset-1, preset-2, preset-3."""
    root = ami_root or ami_dir(CASE_ID)
    out: dict[str, Path] = {}
    for pid in ("preset-1", "preset-2", "preset-3"):
        out[pid] = export_mp4(pid, root / f"{pid}.mp4", n_frames=n_frames)
    return out
