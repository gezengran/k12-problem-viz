"""Problem constants from the exam statement."""

from __future__ import annotations

import math

CASE_ID = "three-circles-chords"

# Unit circles C1, C2, C3 (centers, radius = 1).
CIRCLE_CENTERS: tuple[tuple[float, float], ...] = (
    (-1.0, 0.0),  # C1: (x+1)^2 + y^2 = 1
    (1.0, 0.0),  # C2: (x-1)^2 + y^2 = 1
    (0.0, math.sqrt(3.0)),  # C3: x^2 + (y - sqrt(3))^2 = 1
)
CIRCLE_RADIUS = 1.0

# 3:4 portrait canvas (matches solve/_common LIVE_PHOTO_SIZE 720×960).
FIG_WIDTH = 9.0
FIG_HEIGHT = 12.0
DPI = 80
PORTRAIT_ASPECT = FIG_HEIGHT / FIG_WIDTH  # height / width = 4/3

EPS = 1e-6

EXPORT_FPS = 10
OPTION_SECONDS = 6.0

# Option A: fixed b, scan k until a circle becomes tangent.
OPTION_A_B = 0.25
