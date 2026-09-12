# Module 05 — provenance and status (project notes)

## What was verified on 2026-09-12 (no download made)

| item | record | verified via |
|---|---|---|
| Hessian QM9 paper | Williams, N. J., Kabalan, L., Stojanovic, L., Zolyomi, V., & Pyzer-Knapp, E. O. (2025). *Scientific Data*, DOI 10.1038/s41597-024-04361-2 (arXiv:2408.08006, 15 Aug 2024) | Crossref, arXiv |
| Hessian QM9 data | figshare, DOI 10.6084/m9.figshare.26363959 (v4, **6,294,531,943 bytes ≈ 6.29 GB**); 41,645 molecules, ωB97x/6-31G* Hessians in vacuum, water, THF, toluene | DataCite |
| Fixture | `probes/results_dryrun/benzene/stageA_hessians.npz` (B3LYP → BHHLYP, 6-31G*, M = 30; `D2_direct_Q`), sha256 `f6e4d4b3…`; `benzene_quick` is the same tensor | local |

## Download done (2026-09-12, user's permission given in chat)

Figshare file 49271011 `hessian_qm9_DatasetDict.zip`, 6,281,831,499 bytes, md5 `f3e36130e5cc47021ab403767a19ddf7`
(matches the figshare record), sha256 `ce595041d718b2df…`; fetched detached (`data/hessian_qm9/fetch_hessian_qm9.ps1`,
resumable curl). The archive holds four splits (vacuum, thf, toluene, water; 9.47 GB unpacked); **only `vacuum/`
is extracted** (2.37 GB, five Arrow stream shards, read with pyarrow). Inventory printed by
`m05/inspect_hessian_qm9.py` → `out/HESSIAN_QM9_SUMMARY.md/.json`: **41,645 molecules**; fields energy, positions,
atomic_numbers, forces, frequencies (n×2), normal_modes, hessian (N,3,N,3; symmetric), label (`dsgdb9nsd_…`, the QM9
index); heavy atoms 1–9 (36,027 molecules with nine); **aromatic-like composition proxy (n_C ≥ 6, n_H ≤ n_C): 2,120
molecules (5.1 %)**, labels saved — an upper bound for the recomputed B3LYP subset, not its size. Units and
conventions of the fields are to be taken from the paper before use (not yet read; owed). The record metadata is
kept in `out/figshare_record_26363959.json`; the archive and shards stay out of git.

The corpus itself does not exist yet. Its remaining halves are owed as follows.

## Owed, and by whom

1. ~~The download~~ — done 2026-09-12 (above). **Paper read the same day** (arXiv 2408.08006 text, 7 pp.; methods,
   data records, Table 1): NWChem, ωB97X/6-31G*, geometries optimised in vacuum with NWChem defaults, **numerical
   Hessians by finite differences with 0.01 a.u. displacement** (their test: 0.005/0.01/0.02 a.u. changed
   frequencies by < 15 cm⁻¹ on average — the numerical noise floor of these Hessians, to be remembered when Δ₂
   labels are thresholded); SCF converged to 10⁻⁶ eV; only H, C, N, O (fluorine dropped); 41,645 of the 133,885 QM9
   molecules chosen by UMAP + farthest-point sampling. **Units (Table 1):** positions Å, energy eV, forces eV/Å,
   Hessian eV/Å², frequencies cm⁻¹, normal modes dimensionless (3N × 3N). The file's `frequencies` field is 3N × 2,
   not the paper's 3N × 1 — **checked 2026-09-12 by reconstruction**: mass-weighting the stored Hessian (eV/Å²,
   isotopic masses) and diagonalising reproduces column 0 to within 0.4 cm⁻¹ (e.g. 3563.6 vs 3563.3) and gives
   negative eigenvalues exactly where column 1 is non-zero (109.9, 80.0, 67.6 cm⁻¹ imaginary in the example), so
   **column 0 = real frequency, column 1 = magnitude of an imaginary frequency**. The translations and rotations are
   *not* projected out: the example's six lowest modes are three imaginary (68–110 cm⁻¹) and three small real
   (12–117 cm⁻¹), the signature of an unprojected numerical Hessian. Any Δ₂ built from these Hessians must project
   out translation and rotation first, and the ~15 cm⁻¹ displacement sensitivity the paper reports is the noise
   floor for its labels. Ring detection is done from geometry (`m05/ring_survey.py`, bonds from covalent radii, cycle
   basis of the bond graph, planarity 0.1 Å RMS), so no QM9-SMILES download is needed. **Result
   (`out/HESSIAN_QM9_RINGS.md`, 2026-09-12): 36,760 molecules (88 %) contain a ring, but only 66 (0.2 %) contain an
   all-carbon aromatic six-ring — benzene itself once — while 6,055 (14.5 %) contain a planar conjugated five- or
   six-ring of C/N/O (pyridine-, pyrrole-, furan-like included).** Ring sizes in the cycle basis: 3: 18,884; 4: 11,305;
   5: 17,388; 6: 8,900; 7: 4,222; 8: 2,137; 9: 556. **Consequence for the plan's "aromatic-heavy subset"
   (Capstone_Mapping §M05):** with at most nine heavy atoms and a UMAP/farthest-point selection, Hessian QM9 holds
   almost no benzene-ring chemistry; the realistic over-represented class is *conjugated and heteroaromatic rings*,
   and the PAH held-out set is even further off-distribution than the mapping assumed. This goes to the user as a
   decision input (subset definition: 66 all-carbon rings + the 6,055 conjugated rings, or the conjugated class alone);
   it changes no frozen text by itself.
2. **The recomputed B3LYP subset** — laptop compute with the plan's psi4 deck; benzene took 388 s on the
   laptop (dry run 2026-09-05), QM9 molecules are smaller (≤ 9 heavy atoms), so the ~1,000-molecule
   figure in the memory notes is an order of magnitude, not a plan number. **The subset size is fixed by
   a dated note** after the naphthalene dry run prints its Hessian timing and the machine is decided (P13).
   Not while an anchor job runs.
3. **The Zenodo release** of the corpus (Δ₂ tensors, labels, deck hashes) — the user; before the module's
   official start.
4. **Reading-2 fallback** — a second public Hessian source, to be searched and verified; none named.
5. **The label threshold θ** and the P3 effect size — pilot-note item 5 (RECIPE gives θ = 0.1 as candidate).
6. The notebook (`deep_learning.ipynb`), the report in the APA template with the nine prescribed sections,
   the three required sentences (Capstone_Mapping §M05), and the student's pass.

## What the smoke test showed (code path only, not a result)

Fixture benzene: 30 modes, 435 possible pairs, 10 positive pairs at θ = 0.1; baseline network
117,569 parameters; twenty steps on one molecule bring the weighted BCE from 1.36 to 0.58 in 0.3 s on
CPU; the implied pattern count at recall 0.9 is printed. None of this generalises; it proves that
tokens, labels, model, loss and the K-metric run end to end.

## Files

- `RECIPE.md`, `README.md`, `m05/build_corpus.py`, `m05/model.py`, `m05/smoke_test.py`, `requirements.txt`.
- `data/` is git-ignored (fixture corpus and smoke-test JSON are regenerated by the two commands in the README).
