# Pre-registration M2b — can PySCFAD's shipped LNO stand in for the plan's frozen-space energies? (written 17 September 2026, 19:2x, before any run)

## Why this is the next test

Everything measured this week makes the gradient route the coupling route: 2k + 1 = 19 gradients at
naphthalene (X14/X21), exact recovery, noise damped (X20), g = 5.71–7.19 for LNO-CCSD(T) (M2a cell 3),
the energies-only route closed by the amplitude test, the diagonal-only route closed on shape outside the
C–H stretch family. One thing stands between that route and a deck: **the gradients exist only in
PySCFAD's LNO** (IAO auto-fragments, thresh 1e-4 default), while the plan's energies come from **its own
frozen-space construction on pyscf-forge's LNO** (Pipek–Mezey LMOs, one fragment per localised occupied
orbital, tight thresholds 1e-6/1e-7, spaces frozen at the equilibrium geometry and transported). Either the
shipped engine can replace ours for the deck, or in-house gradients (M2, estimated 2–3 weeks) are needed.
That is a measurement, not a preference, and it is cheap.

## What is compared

The quantity the deck uses is the **response**, not the absolute energy:
R_s(i) = ½[ΔE(+q eᵢ) + ΔE(−q eᵢ)] − ΔE(0), with ΔE = E(LNO-CCSD(T)) − E(low level), at q = 1.0 along
benzene's three probe modes (the M1/M3 modes 12, 20, 6 in the plan's numbering; frequencies and families
as `probes/m1_frozen_spaces.py` prints them). Benzene, cc-pVDZ — the basis in which the plan's own
frozen-space energies are measured (180 s each, 14 September) — if PySCFAD's energy-only LNO fits under
a 12 GB cgroup cap there; otherwise 6-31G* for both, stated as such.

Two arms, same geometry, same low level, same basis:
- **A (ours):** `m1_frozen_spaces.py` arm A — frozen spaces from the reference, tight thresholds.
- **B (PySCFAD):** `pyscfad.lno.LNOCCSD_T` energy only, no gradient, at (i) its defaults and (ii)
  `thresh_occ, thresh_vir = 1e-6, 1e-7` (the plan's tight pair, as M2a cell 4 sets them), fragments
  as it auto-builds them.

Three modes × three points (−q, 0, +q) × two arms = 18 LNO energies, plus the shared low-level ones.

## Pre-registered reading (fixed now)

The frozen spaces' own noise at benzene is ≈ 2 µE_h on R_s (the plan's measured figure).

- **STAND-IN:** |R_s^B − R_s^A| ≤ 6 µE_h (3 × the noise) on all three modes at setting (ii), and the sign
  of every R_s agrees. Then PySCFAD's LNO is the engine for the gradient deck at naphthalene, the
  fragmentation difference is recorded as a stated deviation, and M2 is not built.
- **PARTIAL:** setting (ii) passes on the C–H stretch and out-of-plane modes but not the C–C stretch (the
  family where locality is hardest, X9). Then the deck is mixed: PySCFAD gradients for the families that
  pass, frozen-space energies for the rest — priced before adoption.
- **FAIL:** any mode off by more than 6 µE_h at setting (ii). Then the shipped engine does not compute
  the plan's quantity and M2 (in-house frozen-space gradients) goes on the schedule with its 2–3 weeks.

Setting (i) is reported beside (ii) but not scored: it tells us how much of any gap is the threshold and
how much is the fragmentation.

## What this does not decide

Whether g measured at 6-31G holds at cc-pVDZ (the laptop cannot run that AD gradient; a machine with
64–128 GB can); the quartic contamination of the gradient-difference read at q = 1 for the real
correction (mode G's 0.05–0.21 cm⁻¹ is the DFT stand-in); anything about naphthalene's own R_s, which
transfers only if benzene passes and X9's locality profile holds.

## Cost and when

About 18 LNO energies at benzene: ≈ 1 h of the `qc05` environment for arm A (or reuse the sealed M1
values where the geometry is identical) and ≈ 1 h of `qcad` for arm B, each under a cgroup cap, neither
touching the Windows side. **Not before the user has read this note**; runnable beside the anchor run if
the cap is 12 GB or less (WSL ceiling 20 GB, anchor 3–7 GB).
