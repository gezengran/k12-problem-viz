"""Case identifiers and animation defaults."""

CASE_ID = "compound-growth"
N_FRAMES = 48
FPS = 10
BASE = 1.01
# x-axis extends to primary_crossing * margin (see math_model.plot_x_max).
X_PLOT_MAX_MARGIN = 1.08
# Animation pacing: fast early segment, slow band around primary crossing.
FAST_PHASE_FRAC = 0.28
SLOW_PHASE_FRAC = 0.50
CROSSING_U_MARGIN = 0.055
