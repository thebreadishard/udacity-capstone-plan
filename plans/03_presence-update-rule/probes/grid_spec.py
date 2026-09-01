"""Frozen grid generator constants for Plan 03 Q0.

This module *is* the hashed generator until a real Octopus mesh script
replaces it. Changing any constant after Q0 is a Distilled §4 deviation.

Units are Hartree atomic units unless noted.
"""

from __future__ import annotations

# Outer Cartesian spacing. Frozen 2026-09-01.
OUTER_SPACING_A0 = 0.20

# Vacuum padding around the molecule, then absorbing rim if ionising.
VACUUM_A0 = 6.0

# Nuclear refinement: h(r) ~ a0/Z near nuclei, outer spacing as cap.
REFINEMENT_RULE = "h(r)~a0/Z near nuclei; h capped at OUTER_SPACING_A0 outside"

# Teacher time step and learner stride.
DT_TEACHER_AU = 0.05
LEARNER_K = 1

# Box is hashed with the molecule; this is the vacuum recipe, not a size.
BOX_RULE = "molecule + >= 6 a0 vacuum + absorbing rim if ionising"

# Channels packed in this order everywhere.
CHANNEL_ORDER = (
    "rho_plus",
    "rho_minus",
    "j_x",
    "j_y",
    "j_z",
    "E_x",
    "E_y",
    "E_z",
    "B_x",
    "B_y",
    "B_z",
)

PLUS_CHANNEL = "frozen point nuclei; rho_plus is bookkeeping zeros / smear diagnostic"

# P0 / P2 horizon in teacher steps.
T0_STEPS = 200
P2_STEPS = 200
