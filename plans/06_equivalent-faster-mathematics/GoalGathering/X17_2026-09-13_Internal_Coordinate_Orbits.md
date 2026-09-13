# X17 (2026-09-13) — lead D's first desk test: the stand-in correction in symmetry orbits of internal coordinates

*The reflection of 13 September proposed under lead D "a B-matrix transform of the benzene stand-in tensor today"; the user said "door met de reflectie" the same afternoon. Script `experiments/x17_internal_coordinate_orbits.py`, output `experiments/x17_benzene.md/.json`. Stand-in tensor as in every desk experiment (BHHLYP − B3LYP at benzene, plan 05 `stageA_hessians.npz`); a CC tensor replaces it at R0. Reading fixed in the script header before the run.*

## 1. What was asked

X8 showed the correction is not sparse in Cartesian atom blocks; X15 that it has no low-rank far field. Lead D asks the scaled-quantum-mechanical (SQM) lineage's question (Pulay et al. 1983; Rauhut & Pulay 1995; Baker, Jarzecki & Pulay 1998; Crossref-verified 13 September): written as corrections to force constants in a declared redundant **internal** set — 6 C–C and 6 C–H stretches, 6 C–C–C and 12 C–C–H bends, 6 C–H wags, 6 ring torsions (42 coordinates) — grouped into **orbits** under the molecule's 24 point-group operations (found numerically from the geometry, with the sign every out-of-plane coordinate picks up under improper operations — without that sign the fit is wrong by 14 cm⁻¹, which is how the first version failed), how many orbit parameters reproduce the per-mode correction, and do the σ skeleton (C–H stretch, C–C–H bend, wag) and the π-related ring part (C–C stretch, C–C–C bend, torsion) separate?

Fit: linear least squares of Lᵀ M^{-1/2} Bᵀ ΔF B M^{-1/2} L against Δ₂ in the B3LYP mode basis; only residuals are unique under redundancy, so no parameter is reported as physics. 61 symmetry-allowed pair orbits (33 forbidden orbits dropped); nested sets by graph reach.

## 2. Result (benzene stand-in; measured first-order RMS 48.96 cm⁻¹ over 30 modes; largest correction the B2u Kekulé mode at 1357 cm⁻¹, −35.6 cm⁻¹)

| parameter set | params | RMS first-order error (cm⁻¹) | max | Kekulé-mode residual | families that fail |
|---|---|---|---|---|---|
| S0 diagonal only (the SQM scale-factor limit) | 6 | **18.46** | 49.3 | +49.3 | all but C–H stretch (0.76) |
| S1 + couplings between internals sharing an atom | 35 | **6.32** | 18.6 | +11.4 | C–C stretch 5.5, C–H in-plane 8.0, ring in-plane 15.8 |
| S2 + couplings one bond apart | 51 | **0.03** | 0.07 | 0.00 | none |
| S3 all allowed orbits | 61 | 0.01 | 0.04 | 0.00 | — |
| σ-type orbits only | 24 | 14.30 | 50.6 | +50.6 | C–C stretch 21.7, C–H oop 18.5 |
| π-type orbits only | 15 | 42.03 | 83.6 | −13.7 | everything |
| σ + π without σπ cross couplings | 39 | 13.85 | 48.6 | −1.6 | **C–H out-of-plane 25.3**; in-plane families ≤ 1.5 |

Verdict under the pre-registered reading: **S1 = 6.3 cm⁻¹ → not compact** at 0.5 or at 2.5 cm⁻¹. The correction is not a few scale factors and not a nearest-neighbour valence field.

## 3. What it means

1. **The reach of the correction in internal coordinates is exactly one bond, and then it stops.** Couplings between internals one bond apart are indispensable (S1 → S2 takes the error from 6.3 to 0.03 cm⁻¹; the Kekulé mode needs them: +11.4 → 0.00), and everything beyond (the 10 orbits two and three bonds apart) contributes < 0.05 cm⁻¹. This is the internal-coordinate face of X9 (meta/para C–C pairs carry 19–26 % of the correction in Cartesian terms) and it is *sharper*: in a topology-aware basis the correction terminates at second neighbours, where the Cartesian picture (X8, X12) never terminated. That is a genuine structure the repository did not have.
2. **But it is not a compression at benzene.** S2 has 51 parameters against 61 allowed orbits; the plan's own symmetry prior already reduces the mode-basis object to a comparable count. The value of the finding is not fewer numbers at one molecule but **transferable types**: S2's orbits are local coordinate-pair classes (bond–adjacent bond, bond–angle sharing an atom, one apart) that exist in every PAH, with more inequivalent instances. That is lead D's real test and it needs naphthalene's stand-in Hessian (plan 05 machine queue item 5): fit S2 on benzene, predict naphthalene's Δ₂ by type, read per mode against the 2.5 cm⁻¹ margin (the T-1 form).
3. **The σ/π split is real for the C–H stretches and false for the out-of-plane modes.** C–H stretch corrections are σ-internal (0.03 cm⁻¹ from σ orbits alone — the same uniformity T-1 found, 0.17 cm⁻¹). The in-plane ring families need both classes but not their cross couplings (≤ 1.5 cm⁻¹ without them). The **C–H out-of-plane family cannot be split at all** (25 cm⁻¹ without σπ couplings): wags and ring torsions correct together. For lead D's programme this means the σ part that transfers is the C–H stretch block; the ring in-plane block is a joint σ+π object; and the astronomically most important family (C–H oop, the 11.2 µm carrier) is the one where the split idea fails outright.
4. **For lead A** (functional, not matrix): a correction that terminates at one bond in internal coordinates is what a *local* functional error produces; it neither confirms nor refutes A, but it is consistent with it and gives A's test a second reading — a tuned or double-hybrid functional should remove the S2 orbits' constants roughly uniformly, not mode by mode.

## 4. What is not established

Stand-in, not CC (the BHHLYP−B3LYP difference is a functional-shaped difference by construction, which may favour compactness in internal coordinates — the CC tensor at R0 is the real test and could be less compact). One molecule; no transfer yet. The internal set is one declared choice (Baker–Jarzecki–Pulay primitives without linear bends); another set changes parameters, not residuals, but the graph-reach classes S1/S2 depend mildly on the set. The SQM literature's own transfer residuals (Rauhut & Pulay 1995; Bock et al. 1990) have not been read (abstracts only) and are the yardstick for point 2.

## 5. Next for lead D (no compute now)

- After machine queue item 5 (naphthalene BHHLYP Hessian): `x17 --molecule naphthalene` (needs a stageA-style npz for naphthalene, or a small adapter to plan 02's B3LYP + the new BHHLYP Hessian), then the **type transfer** benzene → naphthalene (new script, T-1 form, 2.5 cm⁻¹).
- At R0: rerun X17 on the probed CC tensor; the pre-registered reading applies unchanged.
