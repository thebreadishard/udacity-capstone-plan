# Dated note 2026-09-05 — probe M1 (frozen spaces) ran: what it measured and what it asks

**Status.** A dated note under the freeze of 2026-09-04: it names measurements (printed by
`probes/m1_frozen_spaces.py` and `probes/m1_canonical_truth.py`, results in `probes/results_m1/`)
and the design questions they raise. **It changes no frozen rule by itself.** Proposals are marked
*proposal* and wait for the user's decision. The τ the Q6 bias line would be judged against does not
exist yet (pilot note), so **no verdict is printed here either**; the numbers are given in cm⁻¹ so the
reader can hold them against any τ. All three benzene Δ₂,ii stay sealed: the note reports only
differences between local-CC arms and canonical CCSD(T), never a CC−DFT curvature.

## 1. What ran (WSL, `~/qc05`: pyscf 2.14.0, pyscf-forge 1.1.1; 8 threads; benzene at the dry-run B3LYP/6-31G* geometry)

| Run | Basis / LNO thresholds | Points | Wall | Result files |
|---|---|---|---|---|
| Smoke test (mode 12, q ∈ {−1, 0, 1}) | cc-pVDZ / normal [10⁻⁵, 10⁻⁶] | 3 | 21 min | `benzene_cc-pvdz_normal_smoke/` |
| First full run (arm A **without** semicanonicalisation) | cc-pVDZ / normal | 27 | 15:40–18:15 (killed with the WSL VM at 22 points), resumed 18:22–18:48 | `benzene_cc-pvdz_normal/` |
| Canonical CCSD(T) truth line, same 27 geometries | cc-pVDZ, frozen core, same DF-RHF reference | 27 | 20 min (44–48 s per point) | `canonical_truth_sealed.json` (copied into every M1 directory) |
| **Rerun, arm A semicanonicalised** (the numbers of §2) | cc-pVDZ / normal | 27 | 19:11–21:37 (≈ 5.5 min per point, three arms) | `benzene_cc-pvdz_normal_semican/` |
| Tight thresholds [10⁻⁶, 10⁻⁷] | cc-pVDZ / tight | 27 | started 2026-09-05 night, after the cc-pVTZ gradient attempt | `benzene_cc-pvdz_tight/` |

Modes (chosen by the script from the dry run's Hessian): **12** (1020 cm⁻¹, the totally symmetric
mode; dry-run family label CH-ip-bend), **18** (1357 cm⁻¹, a CC-stretch member of a degenerate pair),
**6** (865 cm⁻¹, CH out-of-plane, non-symmetric). Nine points q ∈ [−1, 1] per mode, the Q6 estimator's
grid. Arms as the Ladder §3 writes them: **A** frozen–frozen (transported occupied set and transported
LNO spaces, impurity solves only), **B** transported occupied set with fresh LNO spaces, **C** fresh
localiser and fresh LNO spaces.

## 2. What it measured

**2.1 The object exists and reloads.** Round trip E_A(0) − E_C(0) = 0.0000 µE_h in every run (target
≤ 10⁻³ µE_h). After the VM kill the run was resumed by **reloading** `frozen_spaces_reference.npz`
(not recomputing it): E_A(0) from the reloaded spaces − E_A(0) of the interrupted run = **+0.0000 µE_h**,
and the sha256 over the reloaded arrays reproduced the original hash. That is the pipeline's own
reload path, tested by accident and passed. (The reference construction itself is not
bit-reproducible between runs — thread order — so a resumed run must reload, never recompute; the
energies agree between runs to better than the 0.005 µE_h the tables show.)

**2.2 Smoothness and bias against canonical CCSD(T), cc-pVDZ, normal thresholds** (rerun; residual σ
about a degree-4 fit in q, the Q6 estimator with ν = 4; a₂ the q² coefficient of the even part of
E_arm − E_canonical, so **2·a₂ is the bias the arm puts on that mode's CC curvature**, E = ½ ω q²):

| mode | arm | σ, bare LNO-CCSD(T) (µE_h) | bias 2·a₂, bare (cm⁻¹) | σ, composite (µE_h) | bias 2·a₂, composite (cm⁻¹) | a₄ |
|---|---|---|---|---|---|---|
| 6 (865, CH-oop) | **A** | **0.002** | +27.6 | **0.003** | **+2.6** | ≈ 0 |
| | B | 6.6 | −10.1 | 1.4 | −1.6 | large |
| | C | 8.9 | +6.1 | 8.7 | +22.8 | large |
| 12 (1020, tot. sym.) | **A** | **0.005** | +5.3 | **0.005** | **+0.5** | ≈ 0 |
| | B | 7.4 | −22.0 | 1.6 | −5.2 | large |
| | C | 10.7 | +27.7 | 10.9 | +28.2 | large |
| 18 (1357, CC-stretch) | **A** | **0.059** | +12.1 | **0.059** | **+1.8** | ≈ 0 |
| | B | 10.5 | +28.0 | 3.4 | +5.5 | large |
| | C | 11.1 | +20.0 | 4.4 | +0.9 | large |

"Composite" is the energy the LNO literature reports: E_LNO-CCSD(T) + [E_MP2(full) − E_MP2(LNO)], the
canonical DF-MP2 correction for the truncated space (pyscf-forge's `e_corr_pt2corrected`); MP2(full) is
canonical and smooth, so it adds no roughness. The a₂ of arms B and C are ill-determined (their 7–11
µE_h of noise over nine points) and listed only for completeness.

Reading: **arm A is three orders of magnitude smoother than either re-selecting arm** (0.002–0.06
against 7–11 µE_h; the 7–11 µE_h is the LNO re-selection discontinuity the plan expected, and it is
five times the 2 µE_h mode E needs for the off-diagonals — dry-run note §2). **Arm A's bias is a clean
q² term** (a₄ ≈ 0, so it does not depend on the step size and is exactly a diagonal curvature bias):
5–28 cm⁻¹ on the bare energy, **0.5–2.6 cm⁻¹ on the composite** — the frozen space loses a
q²-proportional piece of correlation as the geometry moves, and the full-space MP2 recovers most of it.
The bias is largest where the transported virtual space loses most (mode 6: s_min vir 0.82 at |q| = 1,
pre-Löwdin off-diagonal 0.16).

**2.3 Continuity diagnostics** (all runs agree): s_min of the occupied overlap ≥ 0.986 at |q| = 1 on
every mode; s_min of the virtual (LNO) overlap 0.81–0.89 at |q| = 1, 0.95–0.97 at |q| = 0.25; largest
pre-Löwdin off-diagonal ≤ 0.018 (occupied), ≤ 0.16 (virtual). The map is nonsingular throughout
|q| ≤ 1, as the Ladder assumed, and the virtual half is the soft one.

**2.4 The localiser's landing is arbitrary and, on benzene, energetically silent.** The fresh PM
localiser's functional equals the transported set's to 0.1–2 % (7.084 vs 6.926 at mode 18, q = −1),
yet the best-match overlap between the fresh and the transported set drops to 0.67–0.84 on some
points — and **at the same geometry the two runs landed differently** (mode 6, q = +0.25: match 0.667
in the first run, 1.000 in the rerun) while arm C's energies agreed to < 0.005 µE_h. On a D₆h molecule
symmetry-equivalent landings cost nothing; on a lower-symmetry molecule they would not be equivalent.
Round-9 Pass B's finding 2 (re-localise-and-assign would mix) is what this column shows.

**2.5 An implementation fact that cost one run.** pyscf-forge's `make_las` semicanonicalises the
active occupied and virtual blocks, and `impurity_solve` relies on it: its MP2 start amplitudes and
its (T) use diagonal orbital energies. The first arm-A override returned the transported vectors as
they were; at displaced geometries they are not Fock-diagonal, the LNO-MP2 piece came out thousands
of µE_h off (5,670 µE_h at mode 6, q = 1) and the (T) was silently wrong — the first run's arm-A bias
read +23/+46/+147 cm⁻¹. The fix diagonalises the Fock matrix within each transported active block
(a rotation **inside** the frozen space; the space, and therefore the object, is unchanged). The
built-in check is now printed per point: the LNO-MP2 piece of A − C, which reads 5–65 µE_h after the
fix. The frozen-space object must be read as "the space, semicanonicalised at x" — proposal P7.

**2.6 Cost.** At cc-pVDZ, normal thresholds, one point with all three arms takes 240–450 s; arm A
costs the same as arm C (the impurity solves are identical; only the LNO construction is skipped).
Peak resident memory 1.3 GB. At cc-pVTZ a local-CC energy costs 2,087 s (probe 4), so the three-arm
scan is ≈ 2 days and the cc-pVTZ truth line 27 × 755 s ≈ 6 h — both fit the 24/7 laptop.

## 3. What it asks (proposals; the Ladder stays as written until the user decides)

- **P7 (definition, no new rule):** the Ladder §3 object bullet gains the words "the transported
  active blocks are semicanonicalised at the displaced geometry (a rotation within the frozen space)".
  Without them the stated object cannot be evaluated by pyscf-forge's solver.
- **P8 (energy definition for arm A):** the local-CC energy the pipeline probes is the **composite**
  E_LNO-CCSD(T) + [E_MP2(full) − E_MP2(LNO)], MP2(full) computed canonically at every point. Measured
  effect: the diagonal curvature bias of arm A falls from 5–28 to 0.5–2.6 cm⁻¹ at no cost to
  smoothness and at seconds (cc-pVDZ) to minutes (cc-pVTZ) per point. The Q6 bias line then judges the
  composite, and Q6's arm B is compared on the same footing.
- **P9 (next measurements, already scheduled or cheap):** (i) tight thresholds at cc-pVDZ against the
  same truth line (running tonight; the bias should shrink with the larger active space); (ii) the
  three-arm scan and the truth line at cc-pVTZ (≈ 2.5 days); (iii) the off-diagonal bias of arm A is
  unmeasured — single-mode scans see only Δ₂,ii — and is read from the R0 probe batch's two-mode pairs
  against canonical two-mode points, which the R0 pilot should include (a small deck number).

## 4. What did not change

The three arms, the Q6 estimator, the sealed-energy rule and stop 1 are as the Ladder writes them.
The candidate code can freeze spaces (stop 1 is not triggered). No Δ₂ number is readable from this
note or its result files; the canonical truth line is sealed alongside the arm energies.

Printed by `probes/m1_frozen_spaces.py` (REPORT.md per run) and `probes/m1_canonical_truth.py`
(CANONICAL_COMPARISON.md and its `_composite` twin per run). Commits: 21d937a (smoke test), 4872efb
(first run, truth line, resume, semicanonicalisation), this note's commit (rerun).
