# Pre-registration 2026-09-24, 22:0x — E9: transfer the core, probe the substituent (lever 1 of the evening odds)

**Why.** The evening re-estimate (PI assessment, 21:4x) put the whole remaining risk on cost: sparse probing bought 1.2–1.5× on benzene, symmetry
buys 6× but substituted molecules have none, and canonical CC Hessians are out as labels above naphthalene. E7 and E8 read the correction ΔH as
local. If locality holds in the plain sense that a substituent changes ΔH only near itself, then the label of a substituted molecule need not
probe all 3N Cartesian directions: the parent core's ΔH block can be carried over, and only the Hessian columns of the atoms near the substituent
have to be measured. That would price a substituted label at the size of a neighbourhood instead of the molecule. This is testable today on the
DFT–DFT proxy (ωB97X − B3LYP, the same target as E6/E7) with no new compute: the corpus has 199 finished mono-substituted layer-A2 molecules and all
fourteen of their parent cores in layer A.

**Data (fixed).** `modules/05_support_predictor/corpus/molecules/` as it stands on 24 September (deck v1; the eight analytic second-route rows are
not needed here: the test is proxy-internal). Molecules with an imaginary mode in either functional are excluded, as in E6/E7, and so is any
substituted molecule whose core is excluded. Atom order of the corpus geometries is the RDKit `AddHs(MolFromSmiles)` order (that is how the factory
builds them); the script asserts the element sequence agrees and skips a molecule if it does not.

**Construction (fixed).** For a substituted molecule S with parent core C:
1. Heavy-atom map C → S by RDKit substructure match; core hydrogens map to the nearest free hydrogen on the mapped heavy atom after a Kabsch
   alignment of the mapped heavy atoms (the hydrogen that the substituent replaced stays unmapped). Substituent atoms = atoms of S outside the image.
2. Neighbourhood N_r = substituent atoms plus the atoms of S whose graph distance to the nearest substituent atom is ≤ r (bond graph of S with
   hydrogens). r runs over 0, 1, 2, 3, 4; **r = 2 is the registered decision point** ("within two bonds of the substituent").
3. Reconstruction ΔH_rec of the Cartesian ΔH_S (projected Hessians, as E7 uses): every row and column belonging to an atom of N_r is taken from
   ΔH_S itself (these are the probed columns — what a finite-difference label would measure); the remaining block (far × far, both atoms in the
   mapped core outside N_r) is carried over from ΔH_C, each 3 × 3 atom block rotated into the frame of S with the Kabsch rotation. Nothing is fitted.
4. Comparisons at every r: (a) transfer + probe (the claim); (b) probe only (far block zero); (c) transfer only (neighbourhood rows and columns zero);
   the zero rule and the exact ΔH_S as the two ends.

**Read-outs (fixed; the E6/E7 ones, pooled over all admitted A2 molecules, no training so no hold-out):** the corrected-frequency RMS from the
same-family blocks against the ωB97X truth (`basis_free`), the ring coupling ratio to the zero rule (`E6.readout`), the ring diagonal RMS, the
Duschinsky overlap median, and the Cartesian ΔH residual ratio. Cost read-out: the mean fraction of Hessian columns probed, 3|N_r| / 3N, i.e. the
fraction of gradients a finite-difference label would need (symmetry not counted; it does not apply to these molecules).

**Reading (fixed before any number), at r = 2, variant (a):**
- **Pass:** corrected-frequency RMS ≤ 3.3 cm⁻¹ and ring coupling ratio ≤ 0.5 → the label of a substituted molecule costs its neighbourhood, and
  lever 2 (the LNO-CC label price) is run along the neighbourhood directions only.
- **Fail:** corrected-frequency RMS > 6 cm⁻¹ or ring coupling ratio > 0.8 → a substituent changes ΔH beyond two bonds; the label of a substituted
  molecule costs the molecule, and the cost line of the odds stays where it is.
- **Between:** anything else → the curve over r says at which radius the pass bars are met, and that radius sets the label price instead.
- Variant (b) against (a) says what the transferred core block is worth; (c) against (a) says what the probed columns are worth. Both are reported,
  neither carries the verdict.

**Not registered:** any per-core or per-substituent breakdown (printed for reading), and an internal-coordinate version of the same transfer (a
follow-up if the Cartesian one is between).

**Cost.** One Python run of minutes on the laptop, on files already on disk, two threads (the decision-45 densification runs beside it).

Script: `modules/05_support_predictor/m05/e9_core_transfer.py`; output `modules/05_support_predictor/data/e9/e9_core_transfer_2026-09-24.{json,md}`.

## Outcome — 24 September 2026, 21:5x: PASS at r = 2

Run: `python m05/e9_core_transfer.py corpus/molecules data/e9/e9_core_transfer_2026-09-24` (19 s, laptop, two threads). 182 substituted molecules
admitted (199 finished minus the imaginary-mode ones and those whose core is excluded), 0 skipped, 14 cores; atom order and substructure match
held for every molecule.

| r | columns probed | ΔH residual ratio | ring coupling ratio | corrected ω RMS (cm⁻¹; zero rule 23.09) |
|---|---|---|---|---|
| 0 (substituent atoms only, 3.1 of 24.6 atoms) | 0.12 | 0.103 | 0.19 | 2.19 |
| 1 | 0.17 | 0.075 | 0.17 | 2.01 |
| **2 (registered)** | **0.25** | **0.061** | **0.13** | **1.72** |
| 3 | 0.41 | 0.043 | 0.11 | 1.47 |
| 4 | 0.58 | 0.027 | 0.10 | 1.31 |

Both halves are needed: at r = 2, probe only gives residual 0.78 / corrected RMS 18.7, transfer only 0.63 / 10.0; together 0.061 / 1.72. The
pass bars (≤ 3.3 cm⁻¹, ratio ≤ 0.5) are met at every radius including r = 0. Per core the corrected RMS runs 1.3 (anthracene) to 2.5 cm⁻¹
(carbazole, acenaphthylene); per substituent 1.3 (ethynyl, F) to 2.1 (Cl, SH) — nothing hides behind the pooled number (table in the .md).

**What it means, within its scope.** On the DFT–DFT proxy, a substituent changes the correction only near itself: with the parent core's block
carried over, probing the Hessian columns of six atoms out of twenty-five reproduces the corrected frequencies to 1.7 cm⁻¹. The label of a
substituted molecule then costs a quarter of the gradients of the molecule (an eighth if only the substituent's own atoms are probed), with no
symmetry needed. This is proxy evidence; the coupled-cluster confirmation is lever 2 (the LNO-CC label price of one substituted molecule along
its neighbourhood directions, after naphthalene E8) and, for core-to-core transfer, naphthalene E8 itself. Not tested here: transfer between
cores (E8), di-substitution, and the geometry term of decision 48 (the probe measures ΔH at the low-level geometry, as the pipeline does).

## Post-hoc (NOT pre-registered), 24 September 2026, 22:2x — the energy-only variant

Coupled-cluster gradients do not exist for LNO methods, so an energy-only label can measure the near × near block of ΔH (directional second
differences inside the neighbourhood) but not whole columns. `m05/e9_posthoc_block.py`, same 182 molecules and read-outs:

| r | (d) near×near probed + the core's ΔH wherever both atoms are mapped | (e) near×near probed + far×far from the core, near×far zero | (a) registered columns |
|---|---|---|---|
| 0 | 2.56 cm⁻¹, ratio 0.25 | 2.56, 0.25 | 2.19, 0.19 |
| **2** | **1.91 cm⁻¹, ratio 0.15, residual 0.085** | 5.37, 0.53 | 1.72, 0.13 |
| 4 | 1.48, 0.12 | 5.36, 0.51 | 1.31, 0.10 |

Variant (d) meets the registered bars at r = 2: the near × far couplings can come from the core as well, so an energy-only route keeps the E9
saving — the label then needs the near × near block (≈ 240 energies for five atoms) and nothing else. Variant (e) shows the near × far couplings
matter (5.4 cm⁻¹ without them). Read on the proxy; lever 2 (L2, registered 22:2x) prices one such energy at the coupled-cluster level.
