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

# Nuclear refinement. Corrected 2026-09-01: the old "h~a0/Z" gave 1.0 a0 at
# hydrogen, five times COARSER than the outer spacing, on every promised rung.
REFINEMENT_RULE = "h(r)~OUTER_SPACING_A0/Z near nuclei; h capped at OUTER_SPACING_A0 outside"

# Teacher time step and learner stride.
DT_TEACHER_AU = 0.05
LEARNER_K = 1

# Box is hashed with the molecule; this is the vacuum recipe, not a size.
BOX_RULE = "molecule + >= 6 a0 vacuum + absorbing rim if ionising"

# Channels packed in this order everywhere. ELEVEN, not twelve: 2 densities
# + 3 current + 3 electric + 3 magnetic. len(CHANNEL_ORDER) is the only count.
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

N_CHANNELS = len(CHANNEL_ORDER)

PLUS_CHANNEL = "frozen point nuclei; rho_plus is bookkeeping zeros / smear diagnostic"

# Teacher box is finite vacuum + rim, so the baseline stencil is NOT periodic.
PERIODIC_BOX = False

# Explicit 3-D Maxwell stability limit is c*ds/h <= 1/sqrt(3); this is the
# safety factor applied to it when the baseline sub-cycles a teacher step.
MAXWELL_COURANT_SAFETY = 0.5

# P0 / P2 horizon in teacher steps.
T0_STEPS = 200
P2_STEPS = 200
