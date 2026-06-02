"""Shared utilities across mathSol cases."""

from live_photo_export import (
    LIVE_PHOTO_SIZE,
    LiveExportError,
    LiveExportResult,
    export_live_photo_from_frames,
    export_live_photo_from_matplotlib,
    letterbox_image,
)
from mpl_locale import setup_matplotlib_chinese
from paths import ami_dir, project_root, solve_case_dir

__all__ = [
    "LIVE_PHOTO_SIZE",
    "LiveExportError",
    "LiveExportResult",
    "ami_dir",
    "export_live_photo_from_frames",
    "export_live_photo_from_matplotlib",
    "letterbox_image",
    "project_root",
    "setup_matplotlib_chinese",
    "solve_case_dir",
]
