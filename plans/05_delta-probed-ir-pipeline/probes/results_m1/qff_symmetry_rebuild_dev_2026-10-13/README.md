# The symmetry savings tried on an existing benzene force field (13 Oct 2026, 22:0x — development, before S1's numbers)

Input: the 61 pyscf analytic B3LYP Hessians of benzene from 21 Sep 2026 (`probes/results_vpt2/pyscf_hessians_d010_grid99_590/`: step 0.10,
grid 99/590 — S1's R settings, at psi4's corpus geometry rather than pyscf's own minimum). Tool: `probes/qff_symmetry_rebuild.py`. This is
not the registered test of the S1 amendment 2, step 4: that one runs on S1's own R Hessians.

| set | files replaced | route disagreement max (cm⁻¹) | Δ_anh vs direct, window 550–2000 (22 modes): rms / max (cm⁻¹) |
|---|---|---|---|
| direct | — | 0.4 | — |
| ± saving (H(−δq) from the image of H(+δq)) | 8 | 6.5 | 0.03 / 0.09 |
| pair saving (b's Hessians from a's images) | 20 | 20.8 | 0.56 / 1.06 (9.8 outside the window) |

Sources: `route_noise.txt`, `compare_direct_vs_rebuilt.json`, `rebuild_pm.json`, `rebuild_pairs.json`.

**The method is exact; the grid is not symmetric.**
- On exactly symmetric data (a Morse pair potential on staggered ethane, `tests/test_qff_symmetry_rebuild.py`) the ± rebuild reproduces the
  force field to 1e-8, and the pair rebuild to the finite-difference truncation the two routes share: below the direct set's own route
  spreads, falling as δ² (×4 from δ = 0.10 to 0.05).
- On the benzene set (`image_errors.json`): the measured H(−δq) against the images of H(+δq) differs by 3.0e-3 of the displacement signal
  (median, 14 images) for operations that map the laboratory-frame Lebedev grid onto itself (signed permutations; this geometry has four),
  and by 2.4e-2 (median, 82 images) for the others. The first is the noise floor of a DFT Hessian difference; the factor eight on top is the
  grid's lack of the molecule's symmetry. The pair saving needs the C₆ and C₃ rotations, which no octahedral grid has.

**Reading, before S1:** the ± saving holds on Δ_anh even with incompatible operations, and would be cleaner in the symmetry frame (molecule
axes on the laboratory axes, so that the D₂h subgroup's operations are grid-compatible). The pair saving fails the registered lines here
(rms ≤ 0.2, max ≤ 0.5 cm⁻¹); the registered test on S1's own R data decides, and the expectation is that it fails too.
