"""Physical and export defaults for plank-block-friction."""

from __future__ import annotations

CASE_ID = "plank-block-friction"

G = 10.0
V0 = 4.0
MASS_RATIO = 15.0  # M/m

# Relative speed below this: treat as co-moving (no block–plank kinetic friction).
V_REL_EPS = 1e-3

# Ground friction magnitude uses normal load mu1 * M * g (see simulation tests).
GROUND_FRICTION_USES_PLANK_MASS_ONLY = True

# Playback: stretch physics timeline to ~5 s wall time for easier viewing.
EXPORT_FPS = 10
PLAYBACK_SECONDS = 5.0
FPS = EXPORT_FPS

# 4:3 landscape — one view per figure; axes fill the canvas edge-to-edge.
FIG_WIDTH = 12.0
FIG_HEIGHT = 9.0
DPI = 80

CLASSIC_PRESET_ID = "preset-1"
VIEW_GROUND = "ground"
VIEW_BLOCK = "block"
VIEW_PLANK = "plank"

PRESET_IDS = ("preset-1", "preset-2", "preset-3")

# Schematic body sizes (meters) — shared by viz and contact checks.
BLOCK_WIDTH = 0.45
BLOCK_HEIGHT = BLOCK_WIDTH  # square block
PLANK_LENGTH = 2.5
PLANK_HEIGHT = 0.10
BLOCK_CENTER_OFFSET_MIN = BLOCK_WIDTH / 2
BLOCK_CENTER_OFFSET_MAX = PLANK_LENGTH - BLOCK_WIDTH / 2

# Initial pose: block near plank center (not hugging the left edge).
BLOCK_INITIAL_OFFSET_FRAC = 0.50
BLOCK_INITIAL_CENTER_OFFSET = BLOCK_CENTER_OFFSET_MIN + BLOCK_INITIAL_OFFSET_FRAC * (
    BLOCK_CENTER_OFFSET_MAX - BLOCK_CENTER_OFFSET_MIN
)

# Ground panel: fixed wide lab window [0, LAB_VIEW_X_SPAN].
LAB_X_MIN = 0.0
LAB_VIEW_X_SPAN = 8.0

# Co-moving views: same 8 m span as ground frame.
BLOCK_VIEW_X_SPAN = LAB_VIEW_X_SPAN
BLOCK_ANCHOR_X = BLOCK_VIEW_X_SPAN / 2
PLANK_ANCHOR_X = BLOCK_ANCHOR_X

# Backward-compatible alias.
VIEW_X_SPAN = BLOCK_VIEW_X_SPAN
