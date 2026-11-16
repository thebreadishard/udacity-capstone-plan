# Audit of aromir 0.1.0.dev0 with release v1.3

Read at `~/aromir-src` between commits bcc4c00 and 8a0afa7 (another session was committing to
`network/primitives.py`; line numbers there are of bcc4c00). Read-only: nothing in the clone was changed.
No quantum chemistry was run. Experiments are the scripts beside this file (`e0`–`e7`, helper `common.py`),
run as `OMP_NUM_THREADS=3 ~/aromir_dev/bin/python <script>` (Python 3.12.14, numpy 2.5.4, torch 2.14.0+cpu,
rdkit 2026.9.2, geometric 1.1.1, pyscf 2.15.0), on stored corpus Hessians (`hessian_*_analytic.npz`, `H_projected`/`H_raw`).

Severity counts: WRONG-NUMBER 6 · SILENT-ACCEPT 6 · CRASH 4 · CLAIM 9 · PACKAGING 4 · TEST-GAP 2 (seven tests named).
Not reported again: the default-cutoff pseudo-inverse of the Wilson B.

---

## WRONG-NUMBER

### W1. The correction does not turn with the molecule when it has a linear group (RAN)
- Where: `network/primitives.py:128-146` (geomeTRIC `LinearAngle`, measured against a fixed laboratory axis); claimed in
  `card.py:228-231` / `MODEL_CARD.md:61` ("turns with the molecule by construction") and `README.md:102-103`.
- What happens: geometry and Hessian rotated rigidly (x → xRᵀ, H → (1⊗R)H(1⊗R)ᵀ), bundled release, seed-mean ΔH.
  Largest change of any corrected band over 8 random rotations: benzonitrile **4.30 cm⁻¹**, phenylacetylene **2.16**,
  diphenylacetylene **5.34**; benzene, biphenyl, phenol, 2-methylnaphthalene 0.000. The orientation that reaches the
  network is whatever RDKit's embedding and the optimiser leave, so the printed spectrum of a nitrile or alkyne has an
  arbitrary component larger than the 3 cm⁻¹ licence line. 151 of the 749 training SMILES contain a triple bond.
- Shown by: `e3_invariance.py` (column "8 rotations").
- Smallest fix: build the primitives (at least the linear angles) in a molecule-fixed frame — rotate to the principal
  axes with a deterministic sign/tie rule before `_geometric_coordinates` — measure the remaining spread, and until the
  network is retrained with frame-free linear bends take the sentence out of the card and state the measured spread.

### W2. "One canonical atom order" is not one order: the same xyz with its atoms listed differently gives another spectrum (RAN)
- Where: `geometry.py:30-54, 82-85`. Atoms the bond graph cannot tell apart are ordered by the file (RDKit breaks
  canonical ties by input index; hydrogens on one heavy atom "keep their input order"). Graph-equivalent is not
  geometry-equivalent for v1.3, whose primitives are chosen by atom number with raw dihedrals.
- What happens: one stored geometry written as 12 shuffled xyz files, each through `parse_xyz` + `canonical_order`,
  Hessian permuted accordingly: benzene 8 distinct orders (0.09 cm⁻¹), benzonitrile 2 (1.39), biphenyl 7 (**3.07**),
  diphenylacetylene 6 (**5.27**), phenol 2 (0.55), phenylacetylene 2 (0.39), 2-methylnaphthalene 5 (0.006). Heavy-atom
  order differed in all but the last.
- Contradicts `README.md:21`, `CHANGELOG.md:13` ("one canonical atom order for every writing"), `card.py:175-178`
  ("puts every input, SMILES or xyz, into one canonical atom order").
- Shown by: `e3_invariance.py` (column "12 shuffled xyz").
- Smallest fix: break ties by geometry (e.g. sort tied atoms by their coordinates in the principal-axis frame), or ship
  the order-free recipe (`canonical` + `cos`). Until then say it in the certificate.
- Checked and fine: for 42 of 47 hold-out molecules aromir's order equals the corpus order the network was trained and
  evaluated in; where it differs the bands move ≤ 0.09 cm⁻¹ (`e2_holdout.py`).

### W3. A molecule and its mirror image get different spectra (RAN)
- Where: raw signed dihedrals in the pair features (`network/pattern.py:125-131`, recipe `dihedral_encoding: raw`).
- What happens: coordinates and Hessian reflected through z = 0: biphenyl **2.60 cm⁻¹**, diphenylacetylene **5.22**,
  phenylacetylene 0.49, phenol 0.47, benzene 0.18. Two enantiomeric conformers of a twisted molecule (which one the
  embedding gives is an accident of RDKit's version and seed) are physically the same spectrum.
- Shown by: `e3_invariance.py` (column "mirror image"). Fix: as W2 (`cos` encoding), and a mirror test.

### W4. A band's printed position can lie outside its own "seeds' range" (RAN)
- Where: `spectrum.py:124-135` with `certificate.py:63-79`. The position is an eigenvalue of H + mean ΔH; the range is
  min/max over the seeds' own spectra at equal rank.
- What happens: on 60 random corpus molecules, 17 of 3,840 bands are printed outside their range, by up to 0.9 cm⁻¹.
- Shown by: `e5_release_cert.py` (last line). Fix: widen the range to include the printed position, or name the column
  for what it is.

### W5. The scaled-B3LYP baseline uses rounded factors, and factors of another basis set (RAN arithmetic, source REASONED)
- Where: `spectrum.py:32-36`: (0.956, 0.952, 0.960). As I recall Bauschlicher et al. 2018 (PAHdb 3.x): 0.9563, 0.9523,
  0.9595, fitted for B3LYP/4-31G, not 6-31G*. Verify against the paper.
- What happens: a 3200 cm⁻¹ mode is printed at 3072.0 instead of 3070.4 (1.6 cm⁻¹); the "scaled B3LYP" column and
  `baseline.json` carry it. The docstring calls them "the NASA Ames PAH database's B3LYP scale factor of each region".
- Fix: the four-digit factors, and one sentence that they were fitted for 4-31G.

### W6. Isotope labels are accepted and computed with the wrong masses; a labelled hydrogen also breaks the atom order (RAN)
- Where: `admission.py:69-87` (no isotope check), `constants.py:38-46`, `geometry.py:70`.
- What happens: `aromir check "[2H]c1c([2H])c([2H])c([2H])c([2H])c1[2H]"` → `admitted: [2H]c1c… (C6H6, 12 atoms)`, same
  for `[13cH]1ccccc1` and `[3H]c1ccccc1`. The result is named after the isotopologue and computed with ¹H/¹²C masses
  (C–D stretches near 2300 cm⁻¹ would be printed near 3200). `[2H]c1ccccc1` starts as `HCCCCCCHHHHH`: the "heavy atoms
  first" order the network needs is broken too.
- Shown by: `e4_inputs.py`, `e5_release_cert.py` ("orders"). Fix: refuse any atom with `GetIsotope() != 0`.

---

## SILENT-ACCEPT

### S1. A corrected spectrum with an imaginary band exits 0 as "done", and the band can count as licensed (RAN)
- Where: `certificate.py:122-132` (warning only), `cli.py:97-102`. Only the seed-mean is looked at, not the seeds.
- What happens: 1 of 60 random corpus molecules gets an imaginary corrected band from v1.3. The low level refuses a
  non-minimum (`NotAMinimumError`); the corrected Hessian, which is the product, does not.
- Shown by: `e5_release_cert.py`. Fix: exit non-zero (or a distinct code) and never mark such a band licensed.

### S2. The release's records are not checked against each other or for sense (RAN)
- Where: `release.py:69-139, 192-206`; the sha256 covers the tensors only.
- Accepted without complaint in a copy of v1.3: `licence_line_cm: 100` (card: all four families licensed); an error of
  −1.0 and NaN (card prints `-1.00`, `nan`); `elements: [C, H, Xx]`, `min_atoms 40 > max_atoms 3`; a hold-out in
  training.json that evaluation.json does not have, `n_molecules: 3900` for a list of 39; `seed-0.json` declaring seed
  7 (card then lists a file `seed-7.safetensors` that does not exist).
- Shown by: `e5_release_cert.py`. Fix: validators (errors ≥ 0 and finite; elements ⊆ ELEMENTS; min ≤ max; hold-out
  names equal; counts explained; seed equals file name) and a manifest hash over all release files.

### S3. Unspecified stereochemistry and conformers (RAN admit, REASONED consequence)
- `C(=Cc1ccccc1)c1ccccc1` and `CC(N)c1ccccc1` are admitted; the embedding picks an isomer and one conformer (seed 0) and
  the certificate says neither. `acquaintance` (`certificate.py:90-97`) compares the stereo-free string with a training
  list that holds stereo-specific ones, so it can print "the network has not seen it" for a trained molecule.
- Fix: refuse or name unassigned double bonds; state in the certificate that one conformer was computed.

### S4. Text after the SMILES is dropped (RAN)
- `aromir check "c1ccccc1 benzene"` and `"c1ccccc1é"` → `admitted: c1ccccc1`. Fix: refuse a string RDKit did not consume
  whole (compare with `.strip()` and reject whitespace or a trailing name).

### S5. `aromir card --out` overwrites an existing file (RAN)
- `cli.py:77`; the pipeline's rule is "a result is never overwritten" (`pipeline.py:3`, CONTRIBUTING). `e5_release_cert.py`.

### S6. Sizes far outside training are computed, and `check` is not "compute nothing" (RAN)
- No upper size: `check` on C60 ran ETKDG for 28 s (then a traceback, C1). A 60-atom request to `spectrum` would start
  days of DFT whose every band is still marked by family licence (K3). Fix: a size above which `spectrum` needs
  an explicit flag.

---

## CRASH

### C1. Tracebacks instead of reasons (RAN)
- Where: `cli.py:108-122` catches `ValidationError` and `AromirError` only.
- `ValueError: no 3D embedding found` (`geometry.py:76`): benzyne `C1#CC=CC=C1`, [2.2]paracyclophane (5 s), C60 (28 s).
- `NotADirectoryError`: `--out` names an existing file (`pipeline.py:84`), for `baseline` and `spectrum`.
- `UnicodeDecodeError`: an xyz whose comment line is Latin-1; a release JSON that is not UTF-8.
- Release loader: `ValueError` on a truncated weight file (the message is good, the exit is a traceback,
  `weights.py:104-106`), `FileNotFoundError` on a missing one, `SafetensorError` when the hash matches a damaged file.
- `FileNotFoundError`: `card --out` in a folder that does not exist.
- By reading: `ValueError` from `primitives.parities`, `vibrations.rigid_basis`, `Geometry`; `LinAlgError`; `OSError`.
- Shown by: `e4_inputs.py`, `e5_release_cert.py`. Fix: raise `RefusedError` at those sites, and a last
  `except (OSError, ValueError)` in `main` that prints one line and returns 1.
- Wrong reasons, not crashes: empty SMILES and empty xyz → "no aromatic ring"; a duplicated atom → "unpaired electrons;
  no aromatic ring"; an xyz in bohr → "no neutral bonding pattern".

### C2. Hours of DFT are thrown away by failures that come after it, and a failed run cannot be resumed (REASONED)
- `pipeline.py:100-106`: `NotAMinimumError` is raised before `lowlevel.npz` is written, so the Hessian is lost.
- `pipeline.py:209`: everything the network can refuse (`InternalCoordinatesError`, a parity `ValueError`) happens after
  the optimisation and Hessian although most of it is decidable on the start geometry. `repair.py:104`: the memory
  refusal comes after the full Hessian. The module's first line, "Every refusal comes before the first computation", is
  not true for these.
- A failed run leaves `pyscf.log` and `geometry.json`; the same `--out` is then refused as "not empty"
  (`pipeline.py:82-86`), and no command reads `geometry.json`/`lowlevel.npz` back.
- Fix: write `lowlevel.npz` before the minimum check; build the network inputs on the start geometry as a dry run
  before the DFT; check the repair's memory before the Hessian; `--resume <folder>`.

### C3. With v1.3, `spectrum` refuses molecules that only have a grid-artefact soft mode (REASONED, rate RAN)
- `training.json: soft_mode_repair false` → `pipeline.py:206-208` skips the repair, then `pipeline.py:100-103` refuses
  any imaginary mode. `repair.py:3-6` itself says the analytic Hessian can make a soft mode "imaginary when it is not".
- Rate: of 1,154 corpus molecules with an analytic B3LYP Hessian, **41 (3.6 %)** have an imaginary lowest mode at the
  stored geometry (−8 to −87 cm⁻¹; some are real saddle points such as planar 2-phenylpyridine, some rotors) and 53 a
  mode below 20 cm⁻¹ (`e7_soft.py`). There is no step along the mode and re-optimisation, so those requests end in
  "failed" after the full cost. One such molecule (diphenylacetylene, −22 cm⁻¹) is in the training set.
- `README.md:78-92` ("Two checks and a repair guard every result") is not true of `spectrum` with the shipped release.
- Fix: decide the minimum on the repaired Hessian even when the network reads the unrepaired one; displace along a real
  imaginary mode and re-optimise once.

### C4. A run that fails leaves a folder that blocks the next one — see C2 (kept separate because it is what a user meets first).

---

## CLAIM

### K1. The "measured error" per family is not the error of the corrected band positions, and not of what is shipped (RAN)
- Text: `certificate.py:229-231` "Seed-mean rms error of the corrected positions against …"; `card.py:88-92` "The rms
  error of the corrected band positions"; `release.py:77-78`.
- What the numbers are: `diag_rms` of the six source records — per seed, the rms over modes of the *diagonal of the ΔH
  error in the B3LYP mode basis* (first-order shifts; trainer `e6_learning_curve.py:128-144`), then the mean of the
  three seeds' values. The product applies the seed-mean ΔH and diagonalises.
- Reproduced with aromir's own code on the 8 molecules of (a): per-seed first-order values 1.95/1.68/1.70 (ring-ip),
  0.91/1.74/0.91, 2.47/2.06/1.99, 4.09/3.27/3.51 — exactly evaluation.json. The error of the corrected positions of
  the seed-mean ΔH on the same molecules: ring-ip **1.43**, CH-stretch **0.95**, CH-oop **1.64**, other **2.78**
  (printed: 1.77, 1.19, 2.17, 3.62). On 35 of (b) (4 skipped by my loader, symbol "CL"): 1.90, 2.08, 1.93, 2.78.
- So the printed numbers are conservative here, but they are a different quantity, and "other" is unlicensed on a
  number the product does not have. Shown by: `e1b_sources.py`, `e2_holdout.py`.
- Fix: evaluate the release with aromir itself (seed-mean ΔH, diagonalised, per family) and store that, or word the
  certificate as "each seed's first-order error, averaged".

### K2. "Licensed … on every hold-out" leaves out a third never-trained set on which CH-oop fails (RAN, read from the sources)
- The same six source records hold a set `b+` (30 molecules, fluoranthene children added to the scaffold hold-out after
  it was frozen; none in `trained_smiles`, none in `held_out_smiles`). Its `diag_rms`: CH-oop 3.70 / 3.13 / 4.01 (mean
  **3.61 > 3**), other 4.60 / 5.02 / 4.76, ring-ip 2.39, CH-stretch 1.29. With it CH-oop loses the licence.
- Caveat: the three `b+` molecules I opened have no `hessian_*_analytic.npz`, so their labels may be the noisier
  semi-numerical ones. Either way the record does not say that a third read exists.
- Fix: list `b+` as a hold-out, or state in `evaluation.json` why it is excluded.

### K3. A band is "licensed" whatever the molecule (REASONED; `certificate.py:83, 100-119`)
- The licence is a property of the family only. A 60-atom molecule is marked "OUTSIDE" and every ring-ip band still
  reads "licensed: yes"; `cli.py:98-101` counts them. Hold-out (b) is two scaffolds (fluoranthene, fluorene), 23–30
  atoms; (a) is 8 molecules. The statement "Licensed for ring-ip, CH-stretch, CH-oop" carries none of that.
- Fix: no licence outside the training sizes; one line on what the hold-outs are made of.

### K4. The family names promise more than the rule (RAN; `families.py:71-82`)
- "CH-stretch" is any mode above 2800 cm⁻¹ with most motion on hydrogens: phenol's O–H stretch is printed
  `3789.3 | CH-stretch | licensed: yes`, 2-naphthylamine's two N–H stretches and 2-naphthoic acid's O–H likewise; 49
  such bands in 60 random corpus molecules.
- "CH-oop" does not exist in a molecule with one atom 0.5 bohr off the plane: biphenyl, 2-methylnaphthalene and
  2-naphthylamine have 0 CH-oop bands; their aromatic C–H wags are "other" (unlicensed) or, between 950 and 1050,
  "ring-ip" (licensed).
- "ring-ip" is everything between 950 and 1750 cm⁻¹ that is not out of plane: C=O stretches, CH₃ deformations, and in
  a non-planar molecule every mode in the window.
- The evaluation used the same rule (K1 reproduces it), so the numbers fit the rule; the names in `README.md:66`,
  the certificate and the card do not. Shown by: `e5_release_cert.py`. Fix: names such as "XH-stretch", "window
  950–1750, in-plane", and a sentence on non-planar molecules.

### K5. The certificate omits the one limit that is larger than its licence line (REASONED)
- The card states a measured atom-order spread of **10.73 cm⁻¹** (3 molecules, 5 orders); the licence line is 3. The
  certificate (`certificate.py:198-237`) says nothing about atom order, orientation (W1) or mirror image (W3), nor that
  the heights are the low level's, nor which conformer was computed. A reader of `certificate.md` alone is told
  "licensed, 2.12 cm⁻¹" for a band that W1–W3 move by 3–5 cm⁻¹.

### K6. "Trained on Hessians of exactly this level" (`dft.py:3-5`) — the corpus geometries are not of this level (RAN read, effect REASONED)
- Corpus `job.json` deck: geometries optimised with psi4 1.11, density-fitted B3LYP, grid (75, 302), e/d convergence
  1e-8. aromir optimises with pyscf, no density fitting, (99, 590), GAU_TIGHT. The training and hold-out Hessians were
  taken at psi4 minima; aromir's are at pyscf minima. No number in the release was measured through aromir's own chain.
- Fix: one hold-out molecule run end to end through `aromir spectrum` and compared with its stored ωB97X Hessian, the
  number written into the card.

### K7. Statements that are false or stale
- `card.py:230`, `README.md:102`: "turns with the molecule by construction" — W1.
- `README.md:21`, `CHANGELOG.md:13`, `card.py:177`: one canonical order — W2.
- `README.md:78`: "Two checks and a repair guard every result" — C3.
- `README.md:25` ("→ band positions, heights, spectrum"), `CHANGELOG.md:18-19` ("Lorentzian broadening"):
  `spectrum.broadened` and `spectrum.grid` are called by nothing in `src/`; no curve is written anywhere.
- `README.md:34-36`: "the baseline the learned correction will be compared with" — the correction ships.
- `README.md:6`: "The whole chain is in the package and tested" — no test runs the real chain with a release;
  `tests/test_pipeline.py` replaces the optimisation and the low level by a spring model.
- `CONTRIBUTING.md:64`: "`pytest -m "not quantum"` runs the rest in under a second" — 232 tests, 4.9 s here.
- `pipeline.py:3`: "Every refusal comes before the first computation" — C2.
- `CHANGELOG.md:10-12`: "refused … unless it is one neutral, closed-shell aromatic molecule" — isotopologues (W6).

### K8. Sources that cannot be followed (RAN)
- `evaluation.json` names six `E7_rungC_chain35_*.json` files and `order_spread_smiles.json`. None ships with the
  package or is linked; the six exist in the private capstone `out/` folder, and I could not find
  `order_spread_smiles.json` under module 05 outside `corpus/`. "Every number comes from the release's records" is
  true of the copying, not checkable by a user. Fix: ship the source records (they are small) or their hashes.

### K9. "has not seen it" rests on string equality (RAN, REASONED)
- `certificate.py:90-97` compares RDKit canonical SMILES. All 749 + 49 strings round-trip under rdkit 2026.9.2 (`e0_look.py`),
  but rdkit is required only as `>=2023.9` and canonical SMILES change between releases; see also S3.

Checked and found consistent: every number of `evaluation.json` against its six sources (to rounding); the mean-of-seeds
arithmetic; hold-out counts (39; 10 of which 2 trained, stated); training sizes 8–30 and elements against the 749 SMILES;
no hold-out molecule in the training list, also ignoring stereo; MODEL_CARD.md equals what `aromir card` writes (test).

---

## PACKAGING

### P1. Only pyscf is pinned; the packages that decide the atom order and the primitives are open-ended
- `pyproject.toml:27-36`: `rdkit>=2023.9` (canonical order, embedding, MMFF), `geometric>=1.1` (which primitives),
  `numpy>=1.26`, `torch>=2.2`, `scipy>=1.11`, no upper bounds. With W2 the answer depends on RDKit's tie-breaking; the
  pseudo-inverse incident was specific to one numpy build. Fix: tested upper bounds, and a pinned test of the
  canonical order and primitive list of several molecules.

### P2. `--threads` and `--max-memory-mb` bound pyscf only (RAN, observed)
- torch and numpy's BLAS take every core: a 20 s network run here used 2 min 21 s of CPU on 16 cores. `max_memory` is
  pyscf's soft target. Fix: `torch.set_num_threads(resources.threads)` and say what the memory flag does.

### P3. Tooling drift
- `.pre-commit-config.yaml`: `check-added-large-files --maxkb=500` against three committed 1.18 MB weight files; ruff
  pinned at v0.6.9 there, `ruff>=0.6` with `select = ["ALL"]` in CI (0.17.5 in the local cache) — a new ruff rule
  breaks CI without a code change.
- CI tests Python 3.11 and 3.13; the classifiers also claim 3.12 (the dev environment is 3.12, so it works here).

### P4. A fresh `pip install git+…`
- Pulls PyPI's default torch wheel with CUDA on Linux (the CI works around it, `ci.yml:16-17`; the README does not say).
- Installs and declares everything it imports (wheel checked: weights, records, both licences, `py.typed`; no tests).
- Licence metadata `MIT AND CC-BY-4.0` with both files: fine.

---

## TEST-GAP

### T1. The five tests most worth adding
1. **Rotation with a linear group, bundled release**: benzonitrile's stored geometry and Hessian, rotated; corrected
   bands equal to 1e-3 cm⁻¹. Fails today by 4.3 cm⁻¹ (W1).
2. **Shuffled xyz**: one biphenyl geometry in 10 atom orders → identical canonical `Geometry` and identical ΔH; and the
   mirror image. Fails today (W2, W3).
3. **The release's numbers from the package**: bundled release on stored Hessians of hold-out molecules (three small
   ones as test data) reproduces evaluation.json's per-seed values, and the seed-mean's corrected-position error is
   recorded. Today nothing in the package ties `families.classify` + the network to the numbers the certificate prints.
4. **Every CLI failure is one line and an exit code**: embedding failure, `--out` a file, damaged/missing/truncated
   weight file, non-UTF-8 input, isotope label; parametrised, asserting no exception leaves `main`.
5. **After a failure**: a non-minimum keeps `lowlevel.npz`; the same `--out` can be used again (or resumed); a corrected
   imaginary band gives a non-zero exit. Plus one `quantum` test that runs the real chain with the bundled release on a
   9-atom aromatic (furan) — the only place `release.corrections` meets a pyscf Hessian.

### T2. Tests that pass with the feature broken
- `tests/test_network_model.py:59` (turns with the molecule): biphenyl only — no linear angle — and random weights.
- `tests/test_geometry.py:64` (canonical order): benzene, and asserts only that consecutive carbons are bonded; any
  ring walk passes.
- `tests/test_network_model.py:72` (one answer for every atom order): tests the `canonical`/`cos` settings, which v1.3
  does not use, on a molecule chosen to have no symmetry.
- `tests/test_pipeline.py:140` (saddle point): asserts `baseline.json` is absent; the leftover folder and the lost
  Hessian are not looked at.
- `tests/test_certificate.py`, `test_pipeline.py:163`: synthetic two-seed release and spring Hessians; no assertion
  that a position lies in its seed range, or on a real family assignment.
- Platform: one pinned molecule (4-cyanobiphenyl) carries the Linux/Windows/macOS agreement of the bundled release;
  the 16 trainer pins use small test networks, not the shipped weights.

---

## Checked, nothing found
- Constants: mₑ per amu, cm⁻¹ per hartree, bohr, 974.8802 km/mol per (e/√amu)² (4.80320² × 42.2561); isotope masses of
  H, C, N, O, F, S, Cl against NIST; identical to the corpus's `masses_amu`.
- Mass-weighting, projection of the six rigid motions, signed wavenumbers, intensities; aromir's projection of a
  corpus `H_raw` equals the corpus `H_projected` to 2e-16, and the network gives the same bands fed either.
- Linear molecules and single atoms cannot pass admission (an aromatic atom is required).
- The applied correction is the plain mean of the seeds; float32 → float64 hand-off; the tensor sha256 is verified on load.
- Charged species, radicals, unsupported elements, fragments, wrong atom counts, blank lines, lowercase symbols,
  atomic numbers, NaN coordinates in an xyz, paths with spaces, CRLF: refused with a reason or handled.
- `--threads 0`, `--max-memory-mb 10`, a non-empty `--out`, a missing release folder, invalid JSON: refused, exit 2.
