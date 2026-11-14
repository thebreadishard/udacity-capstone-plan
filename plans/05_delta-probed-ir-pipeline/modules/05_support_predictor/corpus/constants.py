"""The physical constants the label route and the vibrational arithmetic share, defined once (TASKS 216, 14 November 2026).

Both numbers were written out in some twenty files, and three of them carried 219474.6313632 for the hartree in cm-1 instead of
219474.6313705 — a difference of 3e-10 relative, harmless in a frequency but exactly what CLAUDE.md's rule about one implementation
of every constant exists to prevent. The four files of the label route and the vibrational arithmetic read them from here; the
remaining copies belong to the ruff sweep of TASKS 139.

CODATA 2018: the electron rest mass in atomic mass units is 5.485 799 090 65(16)e-4, so an amu is 1822.888 486 209 electron masses,
and a hartree is 219 474.631 3705 cm-1 (NIST ASD, E_h/hc).
"""
from __future__ import annotations

AMU2AU = 1822.888486209          # electron masses per atomic mass unit
HARTREE2CM = 219474.6313705      # cm-1 per hartree
