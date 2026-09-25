# Pre-registration 2026-09-25, 07:1x — L2b: a cheaper correlation tier for the coupled-cluster label (the user: "Doe … de L2b-preregistratie maar")

**Why.** L2 (24–25 September) read the price of one LNO-CCSD(T)/cc-pVDZ energy of phenanthrene+CN (25 atoms) at the anchor's tight thresholds as
more than nine hours on eight threads of the CCX53 beside the naphthalene runs — four times the fail bar. An energy-only label of a substituted
molecule's neighbourhood (≈ 240 energies under E9/E10) is therefore out at that tier. The label does not have to be the anchor: the anchor is the
reference that a cheaper tier is measured against. L2b measures cheaper tiers on two things at once — how much curvature accuracy they lose,
and what they cost — and names the tier the labels use.

**Tiers (fixed).** All with DF-RHF/cc-pVDZ (conv 1e-11), the anchor's Pipek–Mezey recipe, frozen 1s cores, DF-MP2 for the composite:
- T0 — LNO-CCSD(T), tight [1e-6, 1e-7] (the anchor; the reference tier);
- T1 — LNO-CCSD(T), normal [1e-5, 1e-6];
- T2 — LNO-CCSD (no triples), tight;
- T3 — LNO-CCSD, normal;
- T4 — the MP2-anchored deck: composite = SCF + DF-MP2 only, with the beyond-MP2 increment **transferred** from the parent core's T0 value along
  the same mode (the M3 idea applied to the label; zero cost per point beyond MP2).

**Two measurements (fixed).**
1. **Accuracy on benzene** (small; each tier is minutes): the curvature along the three probed modes of the anchor (C–H out-of-plane, C–H in-plane
   bend, C–C stretch; benzene modes 6, 12, 18 as in `BASIS_SENSITIVITY_dz_tz.md`) from E(±q) at q = ±0.5, ±1 with the even-part fit of
   `m3_family_reading.py`, converted to ω′ = ω √(k/k_B3LYP), for every tier — against the canonical CCSD(T)/cc-pVDZ Hessian of E8
   (`results_m1/e8_benzene_ccpvdz/hessian_ccsd_t.npz`), which gives the exact curvature along any mode at the same level and basis. Read-out per tier:
   the largest |Δω′| over the three modes, and the beyond-MP2 increment per mode against T0's.
2. **Price on phenanthrene+CN** (the L2 molecule and geometry, mode 65 as L2): one energy per tier T1–T3 at the reference geometry, eight threads,
   16 GB, on the CCX53 when it has no other run (after naphthalene E8, or on a recreated CCX53); T0's price is L2's lower bound (> 9 h); T4 costs
   the DF-MP2 energy (seconds to minutes).

**Reading (fixed before any number).** A tier is **licensed for labels** if its largest |Δω′| on benzene against canonical CCSD(T) is ≤ 2.5 cm⁻¹
(the M3 margin) **and** its price is ≤ 30 min per energy at eight threads. Among licensed tiers the cheapest is the label tier. If no tier passes both:
the cheapest tier within 5 cm⁻¹ is reported as "between" with its price, and the label plan falls back to T4 with the transferred increment,
whose accuracy on benzene is then the number that goes into the error budget. Not registered: reading anything from ⟨T⟩ decomposition beyond the
two read-outs; the choice of a second test molecule.

**What it decides.** The cost line of the odds for the capstone horizon: with a licensed tier at ≤ 30 min, a 240-energy neighbourhood label is
≤ 5 days on eight threads and the E9/E10 savings apply at the coupled-cluster level; without one, labels for substituted molecules at CC level
wait for the asset horizon (Snellius, the PC), and v1 is licensed per family from the anchor's own points.

**Cost.** Benzene: 5 tiers × 3 modes × 4 points ≈ 60 energies of a 12-atom molecule at DZ ≈ a few hours on 16 threads. Phenanthrene+CN: three
energies, each ≤ the tier's price (T3 expected well under an hour). Scripts: `probes/l2b_tiers_benzene.py` and the L2 script with `--tier`, to be
written and smoke-tested on water before the run; nothing starts before the CCX53 is free of the naphthalene E8 processes.
