"""Problem constants from the textbook statement."""

from __future__ import annotations

import math

CASE_ID = "umbrella-rain"

# Body rectangle MNPQ (meters)
BODY_WIDTH = 0.2
BODY_HEIGHT = 1.6
FRONT_EDGE_X = BODY_WIDTH  # segment NP at x = 0.2

# Umbrella
CANOPY_WIDTH = 1.0
HANDLE_LENGTH = 0.45
HAND_HEIGHT = 1.35  # G above ground
CENTER_HEIGHT = HAND_HEIGHT + HANDLE_LENGTH  # O at 1.8 m

# Arm extension limit EG = x (meters), measured forward from the body front NP
ARM_EXTEND_MAX = 0.5

# World-x of hand G when fully extended (Q at x=0, front edge at 0.2)
MAX_HAND_X = FRONT_EDGE_X + ARM_EXTEND_MAX  # 0.7 m

# Rain reference values from the problem
TAN_72 = 3.08
TAN_60 = math.sqrt(3)
