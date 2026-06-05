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
FIG_WIDTH = 9.0
FIG_HEIGHT = 16.0
DPI = 80

PRESET_IDS = ("preset-1", "preset-2", "preset-3")

# Schematic body sizes (meters) — shared by viz and contact checks.
BLOCK_WIDTH = 0.45
BLOCK_HEIGHT = BLOCK_WIDTH  # square block
PLANK_LENGTH = 3.0
PLANK_HEIGHT = 0.10
BLOCK_CENTER_OFFSET_MIN = BLOCK_WIDTH / 2
BLOCK_CENTER_OFFSET_MAX = PLANK_LENGTH - BLOCK_WIDTH / 2
# Initial pose: block center at plank midpoint.
BLOCK_INITIAL_CENTER_OFFSET = PLANK_LENGTH / 2

# Both panels use the same horizontal span (meters) so plank length looks identical.
VIEW_X_SPAN = 7.0

# No extra tail after the block falls to the ground.
END_HOLD_SECONDS = 0.0
