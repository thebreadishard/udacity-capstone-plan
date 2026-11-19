# Frame / sign / order audit — 19 Nov 2026 (read-only)

Scope: code a run, the trainer (m05 rungC_train path), the pipeline (m08) or the product (aromir `main`) uses. R = rigid rotation,
M = mirror image, L = atom listing. "yes" = invariant, "no" = not, "amb" = derived but ambiguous for symmetric molecules.
Measured with the scripts in this folder on stored B3LYP geometries/analytic Hessians (no QC), v1.4 release networks, seed-mean:

- `input_invariance.py` -> `carried.txt` (v1.4 settings geometric/raw), `canonical_cos.txt` (v1.5 switches): per primitive kind,
  B-row sign flips/turns, value changes and 2π jumps, F entry changes, under R (4), M, L (4 random).
- `mirror_attribution.py` -> `mirror_attribution.txt`, `mirror_attribution_more.txt`: v1.4's mirror spread split into
  value slots (dihedral ±π / odd values) and gauge (B-row signs of odd primitives + signed F_pq the head reads).
- `spreads_ids.py` -> `spreads_ids.txt`: aromir's measure_invariance design on molecules outside the registered seven.
- `parity_rotated.py`, `xtb_frame_drift.py`, `plane_axis_scan.py`: parity classification under rotation, xtb minimum vs B3LYP frame,
  conditioning of the 'molecular normal'.

Key numbers (cm⁻¹, largest band change, v1.4 seed mean):

| molecule (id) | mirror full | value-slot part | gauge part | rotation | listing (aromir design) |
|---|---|---|---|---|---|
| 9-methylanthracene (A_78896cfe24) | **9.95** | 0.18 | **10.08** | 0.000 | **10.00** |
| diphenylacetylene (A_014f8519af) | 4.46 | 0.39 | 4.97 | 4.03 (11.20 over 8) | 11.03 |
| diphenyl ether (A_5a75c6c39e) | 1.00 | 2.37 | 3.01 | 0.000 | 1.40 |
| biphenyl (A_fdc27f1bd1, D2 chiral) | 2.67 | 2.43 | 2.64 | 0.000 | 2.85 |
| 4-phenylpyridine (A_0674939e7f) | 1.66 | 3.28 | 1.86 | 0.000 | 2.45 |
| nitrophenanthrene (A2_19eaf39036) | 0.76 | 0.76 | 0.01 | 0.000 | refused (TASKS 284) |
| benzonitrile (A_3100da3761) | 0.24 | 0.18 | 0.08 | 2.42 | 0.97 |
| benzene / phenol / 2-methylnaphthalene | 0.08 / 0.18 / 0.34 | same | 0.00 / 0.00 / 0.06 | 0.000 | 0.18 / 0.52 / 0.02 |

"ideal" (stored inputs carried through the reflection) is 0.000 for every molecule: the encoder is O(3)-equivariant; every spread
comes from the primitive-side inputs. The parts do not add (both must be fixed). 9-methylanthracene has no linear group, so
aromir's licence rule (record max without a linear group 2.85 < 3.0) licenses bands that move 10 cm⁻¹ under a mirror or re-listing.

## The table, by risk

| # | file:line | reference / sign / order used | R | M | L | test | reaches | risk |
|---|---|---|---|---|---|---|---|---|
| 1 | aromir `network/model.py:271-288`; m05 `rungC_hybrid.py` head (doc 6-15); `parity_odd` false in v1.4 (`releases/v1.4/seed-*.json`) | the head reads **signed F_low,pq** (and pair-feature extra `F_ij`, `network/pattern.py:212`) and predicts ΔF_pq from it with no sign covariance; a pair's sign depends on each primitive's B-row convention (odd under M; OOP neighbour order, LinearAngle a↔c under L) | yes (but #2) | **no** (9-methylanthracene gauge 10.08, diphenyl ether 3.01, biphenyl 2.64) | **no** (same gauge via OOP order / ties: 9-me-anthracene 10.0) | capstone strict xfails `tests/test_rungC_hybrid.py:157,171` (H2O2, ethylene); aromir strict xfail "mirrored biphenyl"; nothing on 9-methylanthracene-like molecules | network input → ΔH → **printed positions and licence** | **highest** |
| 2 | geomeTRIC `internal.py:1081-1094` (`LinearAngle.reset`), used by aromir `network/primitives.py:139-156`, m05 `e7_rungB_pairs.py:254`, `e7_t2_sqm.py:47-49` | **lab** Cartesian axis least parallel to a→c; X sign also flips with a↔c (listing) | **no** (diphenylacetylene 11.20) | **no** (gauge 4.97) | **no** | aromir strict xfail "turned nitrile"; capstone rotation tests use water only (`test_rungC_hybrid.py:41,93`) | network input, **training labels** (pattern LS target via the same B), printed positions | **highest** (known, TASKS 287) |
| 3 | aromir `network/pattern.py:107-113` (`_value_slots`, raw), `:139`; m05 `e7_rungB_pairs.py:140-152` (`_primitive_vector`) | raw primitive value: dihedral at ±π (planar rings: half of all dihedrals) takes an arbitrary sign; odd values flip under M | yes | **no** (12 of 24 benzene dihedrals jump 2π; value part 3.28 4-phenylpyridine, 2.43 biphenyl) | **no** (ties, tiny distortions) | capstone `test_internal_coords.py:113` (cos continuous; v1.5 switch); aromir xfail mirrored biphenyl (reason names only this cause, but gauge #1 is as large) | network input → printed positions | high (fix built: `cos`, not carried) |
| 4 | geomeTRIC `makePrimitives` angle choice by atom number (`internal.py:~2453-2503`); v1.4 `angle_choice=geometric` | which 2 of 3 angles at a planar centre, which OOP, by index | yes | yes | **no** (8–26 primitives differ per listing; F_angle-angle of common ones moves 0.14–0.35 au) | capstone `test_internal_coords.py:79,96` (canonical switch); aromir xfail listed biphenyl | network input | high, mitigated: aromir/m08 put atoms in canonical order first (ties remain, #5) |
| 5 | aromir `geometry.py:30-54` / `admission.py` canonical order; m08 `pipeline.py:426-441`, `reuse.py:158-184`; aromir `primitives.py:118-136` (breakTies) | RDKit output order; **graph-equivalent atoms (methyl H's, NO2 O's, ring flips) keep the input order** | yes | — | **amb** (a tie broken by an improper automorphism = a mirror for #1/#3: NO2 tie flips OOP rows, F_oop-dih 0.036 au, even under canonical+cos) | aromir `test_order_pins.py`, capstone `test_m08_xyz_listings.py`, `test_m08_reuse.py:154` (order only, not answer); TASKS 230 called it "not a defect" | network input → printed positions | high (same class as #1) |
| 6 | geomeTRIC `OutOfPlane.value` (`internal.py:1666-1712`) | torsion b-i-j-k: sign = handedness of neighbour order i,j,k | yes | no (pseudo-scalar) | **no** (B flips 2–9 per listing in carried; 1–6 under canonical) | none directly | via #1 and #3 | part of #1 |
| 7 | aromir `release.py:606-633`, `scripts/measure_invariance.py:52-66`; m08 `invariance.py:99-183` | licence read from a record of 4 molecules without a linear group (max 2.85) | — | — | — | aromir `test_linear_group_licence.py` | **licence printed** for 9-methylanthracene-like molecules that move 10 cm⁻¹ | high (record set too small for #1) |
| 8 | aromir `network/primitives.py:226-254` (`parities`), m05 `rungC_hybrid.py:48-73` | mirror through **lab z = 0**; classification of LinearAngle rows rests on lab e0 | passes 6 rotations (`parity_rotated.txt`) | — | — | `test_rungC_hybrid.py:203` | only with parity on (off in v1.4); the parity-odd fix of #1 depends on it | medium (re-check after #2's fix) |
| 9 | aromir `primitives.py:158-221` / m05 `e7_t2_sqm.py:74-79` (`np.linalg.pinv` default cutoff) | SVD null space; near-linear groups let a rotation in (diphenylacetylene 1.3e-7) | yes (count rule) / platform-dependent (m05) | yes | yes | aromir `test_network_pseudo_inverse.py`; TASKS 236 | network input (m05 trainer) | medium, known |
| 10 | m05 `e7_rungB_pairs.py:144-147` | `except Exception: val = 0.0` | — | — | — | TASKS 229 count script | network input (silent) | medium, known |
| 11 | aromir `families.py:54-66,116`; m05 `learning_curve_layerA.py:93-99`; probes `e8_cc_locality.py:69-82` | molecular normal = axis of largest inertia moment | yes | yes | yes | aromir `test_families.py` | family label → per-family error bars, licence per family; anharmonic step feature `o` (`s2_read.py:121`, not zeroed for non-planar) | low; **amb** only for diphenylacetylene (relative moment gap 0.0000, the one non-planar prolate case of 1,240; `plane_axis_scan.txt`) |
| 12 | aromir `spectrum.py:92-97`; m05 `rungC_intensities.py:30-33`; probes `s2_xtb_read.py:119-145` (set-wise, TASKS 255) | mode pairing by squared overlap (Hungarian), degenerate partners may swap / matched as a set | yes | yes | yes | aromir `test_spectrum.py:64` (intensities frame, water); `tests/test_s2_xtb_read.py:24`; `test_anharmonic_step.py` | seed ranges, heights, anharmonic Δ | low (quantities summed over 2D irreps are basis-free) |
| 13 | probes `xtb_hessians_for_qff.py:77-89` + `anharmonic_step.py:296-304` | xtb modes compared with B3LYP modes in Cartesian frames **without alignment** | holds: Kabsch angle ≤ 0.23°, median 0.003° over 41 stored pairs (`xtb_frame_drift.txt`) | — | same order | none | anharmonic partner match | low (unguarded assumption) |
| 14 | `src/dpir/qff.py:214-222` (`fix_mode_signs`), `:259-300` (degenerate alignment), `:434` principal axes | largest-magnitude component positive (ties ambiguous); degenerate basis aligned to displacements; ζ in principal frame | yes | yes | amb (sign) | `test_qff_synthetic.py:69,130,153`, `test_coriolis_frame.py` | QFF/VPT2 labels | low (VPT2 even in each mode; TASKS 174 fixed) |
| 15 | aromir `dft.py`, psi4 corpus (`run_corpus.py:201`, `psi4_worker.py:57`) | DFT grid in the input frame (psi4: nuclear-charge principal axes) | no (grid noise) | no | yes | TASKS 142(a) probe | low-level Hessian, labels | low, known (TASKS 142, 166) |
| 16 | aromir `response.py:255-280`, `spectrum.py:73`; m08 `reuse.py:217` | APT in the geometry's own frame; columns permuted with atoms | yes | yes | yes | `test_spectrum.py:64`, `test_m08_reuse.py:196` | heights | none found |
| 17 | m05 `e9_core_transfer.py:31-32` (Kabsch with det fix), `embedding_experiments_E.py:36-58` (principal frame), `e10_environment_once.py:54`, `mode_blocks.py:35-48` (SVD plane normal, refuses non-planar) | derived frames | yes | yes | yes | `test_mode_blocks.py:107,115` | diagnostics / research reads only | none for the product |
