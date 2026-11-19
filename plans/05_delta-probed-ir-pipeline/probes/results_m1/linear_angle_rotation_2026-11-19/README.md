# Why v1.4 is not rotation-invariant for molecules with a linear group (TASKS 287, 19 Nov 2026)

Read-only probe on stored B3LYP geometries and analytic Hessians (no quantum chemistry; peak 385 MB).

**Cause.** geomeTRIC 1.1.1 represents each linear centre a–b–c by two `LinearAngle` primitives (X, Y). Their bending axes are built
from a reference vector `e0` chosen in `LinearAngle.reset` (`geometric/internal.py` 1081–1094) as the *lab* Cartesian axis least
parallel to a–c. So the two bend rows of B, and every F_low = B⁺ᵀ H B⁺ entry that involves them, turn with the molecule's
orientation. m05 (`e7_rungB_pairs.py:254`, `e7_t2_sqm.py:47–49`) and aromir (`network/primitives.py:139–156`) take `e0` as it comes;
the head's docstring (`rungC_hybrid.py:6–8`) assumes B transforms with the frame, which fails for these rows.

**Measured change under 5 random rotations (seed 7)** — B rows of the linear bends: relative error 1.90–1.99 (turned through a
large angle); F_low entries with a linear primitive: 3.2e-2 to 5.8e-2 (comparable to the force constants 0.04–0.10); every other
input: rounding (≤ 1e-7). Molecules without a linear group: rounding only.

**Fix tested** (`invariant_axis.py`, a monkeypatch of `LinearAngle.reset`): `e0` from the molecule — the principal axis of the
perpendicular second moment of the off-axis atoms (weight 1/r² from b), sign from the third moment. With v1.4's release networks
and aromir's measure_invariance design: rotation spread diphenylacetylene 11.20 → 1.5e-5 cm⁻¹, benzonitrile 2.38 → 7e-6,
phenylacetylene 1.52 → 1.3e-5; molecules without a linear group identical to every digit. The listing spread only partly falls
(diphenylacetylene 11.03 → 5.52): a sign ambiguity of `e0` for symmetric molecules (third moment zero), the parity class of TASKS 52;
a sign rule from the lowest-ranked off-axis atom is untested.

**Blast radius.** 217 of 1,240 corpus molecules have linear primitives (207 of the 1,154 the trainer admits; `linear_count.csv`).
Their inputs change (an orthogonal rotation of each X/Y pair); the other ≈ 947 are bit-identical. With v1.4's weights the fixed
input moves bands at the stored orientation by 0.97 (benzonitrile), 1.24 (phenylacetylene), 6.87 cm⁻¹ (diphenylacetylene), so a
retrain is needed. Second, known defect: diphenylacetylene's B has one direction beyond 3N−6 at 1.3e-7 (angles of 179.9999°);
the trainer's default-cutoff `pinv` keeps it (F_low ≈ 1e9) — TASKS 236.

Scripts: `rotation_probe.py`, `svd_probe.py`, `invariant_axis.py`, `network_spreads.py` (+ `run_spreads.sh`), `band_shift.py`
(+ `run_shift.sh`), `count_linear.py` → `linear_count.csv`.
