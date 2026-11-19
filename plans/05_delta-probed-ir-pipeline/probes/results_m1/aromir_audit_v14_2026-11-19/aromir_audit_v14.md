# Adversarial audit of aromir at 42a8956 (bundled release v1.4), 19 November 2026

Clone: `https://github.com/thebreadishard/aromir`, branch main, HEAD `42a8956`. Read-only: nothing changed in aromir,
nothing pushed, no issue opened. No quantum chemistry was run.

## What was run

- Fast suite: `pytest -m "not quantum"` from the clone (`PYTHONPATH=src`) with the WSL interpreter `~/aromir_dev`
  (pyscf 2.15.0, torch 2.14.0+cpu, RDKit 2026.09.2, numpy 2.5.4, scipy 1.18.1, geomeTRIC 1.1.1; `aromir.__file__`
  confirmed to be the clone): **457 passed, 3 xfailed (the v1.3 invariance xfails), 17 deselected (quantum)**, 32 s,
  max RSS 437 MB. The quantum tests were not run. Windows' system Python lacks safetensors and pyscf, and nothing was
  downloaded.
- Probe scripts (scratchpad): `audit_admission.py` (53 SMILES edge cases through `admission`), `audit_atom_maps.py`,
  `audit_xyz_route.py` (SMILES route against the xyz route on 13 molecules), `audit_v14_probe.py` (v1.4 and v1.3 on
  the stored Hessians of `tests/data/release`: rotation, mirror, xyz listings; the 'seen' statement; the card against
  `MODEL_CARD.md`; the records), runner `run_probe.sh`. Largest process: 420 MB, 12 s.
- Checked by hand and found correct: the units chain (hartree/bohr² → mass-weighted with mₑ → cm⁻¹ through
  219474.63; √m in amu for dμ/dQ), the intensity constant (recomputed from SI: N_A·e²/(12 ε₀ c² amu) = 974.87 km/mol
  per (e/√amu)², code 974.8802), the rigid-motion basis and projection, the step off a saddle point
  (½|k|q², mass-weighted length per bohr), central-difference columns and their insertion
  (`with_measured_columns`), the first-order shift (W²·Δc / 2|ν|), the scaling regions (<1111.1 → 0.979,
  [1111.1, 2500] → 0.969, >2500 → 0.960, edges in the middle region as documented), the licence lookup (reads
  `release.evaluation`, the measurement networks' record; the family comes from the partner low-level mode exactly
  as in `aromir evaluate`), the size gate (release and measurement records both 8–40 atoms, elements identical), the
  hash binding of `release.json`, card = `MODEL_CARD.md` (byte-equal), the README's install commands against
  `pyproject.toml` entry points, the cited sources of the v1.4 records (tracked and pushed in the capstone repository).
  No claim of accuracy against coupled cluster or experiment anywhere.

## Counts

| severity | n | findings |
|---|---|---|
| wrong result | 2 | F1, F2 |
| wrong refusal / acceptance | 2 | F3, F4 |
| provenance | 3 | F5, F6, F7 |
| quality | 3 | F8, F9, F10 |
| text | 6 | F11–F16 |
| **total** | **16** | |

---

## Wrong result

### F1. Atom-map numbers in a SMILES change the atom order the network reads, and the 'seen' statement (RAN)

- `src/aromir/admission.py:58-61` (parse) and `:163` (`Chem.MolToSmiles(without_hydrogens(molecule))`): map numbers
  are kept, so they enter the admitted "canonical" SMILES, RDKit's canonical ranking, and through
  `geometry.start_from_smiles` the atom order.
- Scenario (`audit_atom_maps.py`): `Cc1ccc(O)cc1Cl` → `Cc1ccc(O)cc1Cl`, but `[CH3:5]c1ccc(O)cc1Cl` →
  `Oc1ccc([CH3:5])c(Cl)c1`, another numbering of the same molecule; quinoline with `[n:1]` likewise (2 of 5 pairs
  tried). The network is not order-free: five xyz listings of biphenyl move v1.4's bands by up to 2.85 cm⁻¹
  (`audit_v14_probe.py`). So two writings of one molecule get two spectra — against CHANGELOG "one order for every
  SMILES of a molecule".
- Same input, wrong statement (`audit_v14_probe.py`): `[cH:1]1ccccc1` is admitted as `c1cc[cH:1]cc1` and the
  certificate says "not in the training set or a hold-out: the network has not seen it", while benzene is in the
  release networks' training data (`c1ccccc1` gets `RELEASE_TRAINED`). The certificate's title carries the map number.
  Mapped SMILES are what reaction tools and many exports produce.
- Fix: in `parse_smiles` set every atom's map number to 0 (or refuse a mapped SMILES with the reason); a test that a
  mapped and an unmapped SMILES give the same admitted SMILES and start geometry.

### F2. The xyz route perceives other Lewis structures than the SMILES route: another atom order, another 'seen' (RAN)

- `src/aromir/admission.py:80` (`DetermineBonds(molecule, charge=0)`) then `:163`.
- Scenario (`audit_xyz_route.py`, xyz written from the SMILES's own MMFF geometry): phenyl azide `[N-]=[N+]=Nc1ccccc1`
  comes back from its xyz as `N#[N+]N=c1cccc[cH-]1`; methyl phenyl sulfoxide `CS(=O)c1ccccc1` as
  `C[S@+]([O-])c1ccccc1`, with a stereocentre the SMILES route does not have. Both are admitted. The canonical
  heavy-atom order then differs between the routes (network input, W2-type spread of up to ~3 cm⁻¹), the
  certificate prints a non-standard structure, and the 'seen' lookup compares a string the training list cannot hold
  (`_a_stereoisomer_of` drops stereo but not the charge-separated form). 11 of 13 molecules agreed (nitro,
  N-oxide, nitrile, 2-pyridone, sulfone, acid, indole …). No sulfoxide or azide is in v1.4's training list, so the
  practical 'seen' error is small today; the order difference is not.
- Fix: standardise the perceived molecule (`rdMolStandardize` charge parent / a fixed resonance form) before the
  canonical SMILES and order, drop 3D-perceived stereo where the SMILES route would have none, or compare 'seen' by a
  standard InChIKey; test both routes give the same admitted SMILES on a list like the one above.

## Wrong refusal / acceptance

### F3. `aromir check` says "admitted" for molecules `aromir spectrum` refuses (READ)

- `src/aromir/cli.py:45-47, 177-180`: `check` runs only `pipeline.admit`; the release's gates
  (`pipeline._untrained_elements`, `_untrained_size`, `_no_network_inputs`, `pipeline.py:583-622`) are not applied.
- Scenario: hexabenzocoronene (C42H18, 60 atoms) or any aromatic above 40 atoms: `check` prints "admitted …",
  `spectrum` then refuses it ("the network was trained on 8 to 40"); a molecule whose start geometry the network
  cannot read is "admitted" too. The help says `check` tells "whether a molecule is supported".
- Fix: `check` loads the bundled (or `--release`) release and prints each gate's verdict — admitted / outside the
  training sizes (needs `--outside-training-sizes`) / unreadable by the network.

### F4. Charge-separated and unusual aromatics outside the training chemistry are admitted, and nothing checks that the optimisation kept the molecule (RAN admission, REASONED consequence)

- `src/aromir/admission.py:145-150`: "neutral" is a net charge of 0, "aromatic" is any RDKit-aromatic atom.
- Scenario (`audit_admission.py`): `[NH3+]c1ccccc1C(=O)[O-]` (a zwitterion) and tropone `O=c1cccccc1` are admitted.
  v1.4's 1,078 training SMILES hold 81 with a `+`, every one a nitro/N-oxide-type pair; no zwitterion, no
  seven-membered aromatic ring. In the gas phase the zwitterion's proton moves back during the B3LYP optimisation,
  so the molecule computed is anthranilic acid while the certificate names the zwitterion; nothing compares the
  optimised geometry's bond graph with the admitted molecule (`pipeline._compute`, `pipeline.py:438-472`), so a
  proton transfer or ring opening goes unnoticed.
- Fix: (a) after the optimisation, perceive bonds on the minimum (`DetermineBonds`, or the feature bond graph) and
  refuse/flag a result whose heavy-atom graph or H placement differs from the start; (b) refuse formal-charge
  patterns absent from the training set's (the record lists them), or name them on the certificate as outside the
  training chemistry.

## Provenance

### F5. A certificate does not say which weights made it (READ)

- `src/aromir/certificate.py:438-445` records `network.version`, the seed numbers and the measurement checkpoints;
  `records.provenance()` (`records.py:33-41`) records package versions only. `Release.tensor_sha256` is loaded
  (`release.py:985`) but written only into the card.
- Scenario: a fork retrains and ships a folder labelled 1.4 with its own `release.json` (the loader only checks
  internal consistency); its certificates are indistinguishable from the official ones. Two users comparing
  certificates cannot tell whether they used the same weights.
- Fix: put each seed's tensor SHA-256, the `release.json` content hash and the release folder (or "bundled") into
  `certificate["network"]` and `correction.npz`.

### F6. CI never loads the bundled release from an installed wheel (READ)

- `.github/workflows/ci.yml` job `package`: builds, installs the wheel, runs `aromir --version` only. All tests run on
  the editable install.
- Scenario: a hatch include/exclude change (or a `.gitignore` line such as `*.safetensors`) that drops the weights or
  records from the wheel passes CI; the first `aromir spectrum` after `pip install git+…` would fail after the start
  geometry.
- Fix: after installing the wheel run `aromir card > /dev/null` (it loads the release and verifies every hash), from a
  directory outside the checkout.

### F7. A resumed run may mix steps of different aromir versions without saying so (READ)

- `src/aromir/pipeline.py:167-177` (`_asked`): the identity of a run is command, SMILES, start-geometry hash and
  level; not the aromir version (nor the release, which matters only for the last step).
- Scenario: a run killed under 0.1.0.dev0 at commit A is taken up after `pip install -U` at commit B whose
  optimisation criteria, repair rule or saddle step changed; the saved geometry/Hessian of A are reused as if B had
  made them. Each step's `made_with` does record its versions, so it is recoverable, but nothing compares them.
- Fix: include `aromir.__version__` plus the git describe/commit in `_asked`, or refuse/flag a resume whose step files
  name another aromir version.

## Quality

### F8. The intensity test is tautological, and no absolute intensity is tested (READ)

- `tests/test_spectrum.py:15-22` recomputes `KM_PER_MOL_PER_SQUARED_DIPOLE_DERIVATIVE * |P L/√m|²` with the same
  constant and the same mass convention; it would pass with a wrong constant, amu/mₑ mix-up or a missing factor. The
  frame test and the polar-tensor-vs-finite-difference test (`test_lowlevel.py:50`) do not pin km/mol either.
- I recomputed the constant from SI (974.87) and the formula, so no wrong number today; the guard is missing.
- Fix: one quantum test pinning water's B3LYP/6-31G* intensities in km/mol against another program (psi4 or the
  capstone's stored APT-based rows), to ~1 %.

### F9. Broad exception sets turn code bugs into "damaged run; delete it to start over" (READ)

- `src/aromir/pipeline.py:79-95` (`_UNREADABLE` includes `TypeError`, `KeyError`, `ValueError`, `RuntimeError`)
  around blocks that also *construct* objects: `:255-266` (`optimisation.Optimisation(minimum, **stored[...])`,
  `Geometry(...)`), `:331-365` (`lowlevel.LowLevel(...)`, `repair.Repair(...)`).
- Scenario: a field renamed in `Optimisation` between versions (see F7) raises `TypeError` on resume; the user is told
  the folder "holds a damaged run; delete it to start over" and deletes hours of DFT that were intact.
- Fix: keep the try around the reading/parsing only; let construction errors propagate, or word the refusal "cannot
  be read by this version of aromir (… ); keep the folder" when the file's own checksum is fine.

### F10. Dead code: the broadening path (READ)

- `src/aromir/spectrum.py:26-30, 95-112` (`FWHM`, `GRID`, `grid`, `broadened`) are called by no command; only tests use
  them (CHANGELOG admits "no command writes a curve yet"). The prompt's "certificate with an IR spectrum" is a stick
  table.
- Fix: write the broadened curve into the result folder (it is cheap) or remove it with its tests until it is used.

## Text

### F11. v1.4's certificate says the invariance spreads were "not measured"; they take seconds and are near the line (RAN)

- `src/aromir/releases/v1.4/` has no `invariance.json` and `evaluation.json` no `atom_order_spread`;
  `certificate.py:306-311` and the card (`MODEL_CARD.md:68-69`) say "not measured for this release". The statement's
  "Not in that error … more than the licence line" sentence (`certificate.py:343-347`) therefore never appears under
  v1.4, and `tests/test_v13_on_stored_hessians.py:46` holds its strict xfails on v1.3 only — the shipped release has no
  invariance test.
- Measured here with the package's own test helpers on the stored Hessians (`audit_v14_probe.py`), v1.4 / v1.3:
  benzonitrile under 8 rotations **2.38** / 4.24 cm⁻¹; biphenyl mirrored **2.67** / 2.60; five xyz listings of biphenyl
  **2.85** / 3.06; biphenyl rotated 0.0000 / 0.0000; benzonitrile mirrored 0.24 / 0.09. Three molecules only, so no
  verdict, but each v1.4 spread is larger than the licensed error of three of the four families on both test sets.
  The v1.4 recipe is the same geometric/raw design as v1.3 (`seed-*.json`), so the cause is unchanged.
- Fix: measure v1.4 over invariance.json's molecules and ship it (and the atom-order spread); move the strict xfails to
  the bundled release, keeping v1.3's beside them.

### F12. `dft.py` misstates where the training Hessians come from (READ, sources checked)

- `src/aromir/dft.py:3-6`: "Those Hessians were computed with psi4 (density-fitted, grid (75, 302)) at psi4's minima".
  The card says "The training Hessians were used as pyscf's analytic Hessians" (`card.py:214`, `MODEL_CARD.md:59`).
  The capstone's producer (`modules/05_support_predictor/corpus/analytic_hessians.py`, docstring) computes pyscf
  analytic Hessians, 6-31G* Cartesian d, grid (99, 590), *at the psi4 corpus geometry*. So the geometries are psi4's
  (DF, (75, 302)); the Hessians are pyscf's at aromir's own level. The sentence came in with the 18 Nov answer to the
  first audit's K6 and inverts what K6 found.
- Fix: "trained on pyscf analytic B3LYP/6-31G* Hessians (grid (99, 590)) at geometries optimised with psi4
  (density-fitted, grid (75, 302)); aromir optimises with pyscf; the effect of the different minima has not been
  measured end to end on v1.4."

### F13. Reader text says "hold-out" throughout; the capstone's rule since 17 Nov is "test set" (READ)

- "hold-out" 9× in `README.md`, 16× in `MODEL_CARD.md` (from `card.py`), in the certificate's statement
  (`certificate.py:361` "on every hold-out"), table text (`:560-575`), `UNSEEN` (`:184`), `_met` (`:202-206`),
  `release.made_by` (`release.py:489-510`), `Evaluation.caveats` (`release.py:291-306`) and the `evaluate` help
  (`cli.py:87-93`); "test set" 0×.
- Fix: reader-facing strings "test set (a): unseen molecules" / "test set (b): unseen scaffolds"; identifiers, record
  keys and `evaluate` file layout keep `holdout`. Regenerate `MODEL_CARD.md` (its equality test will force it).

### F14. A spurious "unassigned double bond" for an azide (RAN)

- `src/aromir/admission.py:97-108` counts every `Chem.FindPotentialStereo` double bond left unspecified.
- Scenario: `[N-]=[N+]=Nc1ccccc1` is admitted with `unassigned_stereo=('1 double bond',)`; the certificate then says
  "the input leaves 1 double bond unassigned: one isomer was computed", though the cumulated azide has no E/Z isomer.
- Fix: skip potential double-bond stereo whose atom is sp/cumulated (two double bonds or a formal-charge pair on a
  linear centre), or cross-check with `Chem.AssignStereochemistry(..., flagPossibleStereoCenters=True)`; a test on
  phenyl azide.

### F15. "The heights are B3LYP's" is not quite what is computed (READ)

- `certificate.py:34` (`HEIGHTS_NOTE`) and the card; but `certificate.py:141` computes heights as B3LYP's polar tensor
  on the *corrected* eigenvectors, so the correction moves heights (mode mixing between near-degenerate bands can move
  them a lot).
- Fix: "the dipole derivatives are B3LYP's (not corrected); the heights use the corrected modes".

### F16. The certificate lacks the card's "not against experiment" sentence (READ)

- The card says "The errors above are against that level, not against experiment" (`card.py:305`); the certificate's
  statement (`certificate.py:331-369`) names the higher level and "harmonic positions" but not that the corrected
  positions lie above measured bands (by ~4 % for CH stretches), while the scaled B3LYP column beside them is the one
  aimed at experiment. A reader comparing the corrected column with a measured spectrum reads a better method as a
  worse one.
- Fix: one sentence in the statement: corrected positions are harmonic ωB97X/6-31G* estimates, not predictions of a
  measured spectrum; compare with experiment through the scaled column until the anharmonic step exists.

---

## The eight findings of 16 November left open

The 16 Nov audit's 31 findings: 23 closed that day (TASKS 245). The eight not closed then were K2, K6, K8, K9, P1, P4,
T1, T2; the 18 Nov audit and its answers handled several. Status at 42a8956:

| finding | status | evidence |
|---|---|---|
| K2 (b+ not mentioned) | **closed** | `MODEL_CARD.md:36` names the 30 b+ children, why they are not read, and 9-nitrofluorene |
| K6 (corpus geometries are not aromir's) | **open, and worse in one place** | still no end-to-end run with v1.4 (README:9 names v1.3 runs only); the 18 Nov answer put a false sentence into `dft.py` (F12) |
| K8 (sources cannot be followed) | **closed** | `measured.json` ships and is bound; cited capstone paths checked tracked in udacity-capstone-plan (master = origin/master) |
| K9 ('seen' by string equality) | **closed for the lists, a new hole on the input side** | the 798 list strings are canonical; mapped SMILES (F1) and xyz resonance forms (F2) break the equality |
| P1 (only pyscf pinned) | **closed** | upper bounds on geometric, numpy, pyscf, rdkit, scipy, torch; `tests/test_order_pins.py` |
| P4 (fresh `pip install git+…`) | **closed in text, not re-verified** | README Install; a fresh install needs downloads (hatchling, torch), not attempted |
| T1 (tests worth adding) | **partly open** | T1.1–T1.3 exist for v1.3 only — v1.4 has no invariance test (F11); T1.5 (a quantum test of the real chain with shipped weights) still absent |
| T2 (tests that pass broken) | **closed** as listed; F8 is a new instance | |

Not re-reported (closed by the 16 and 18 Nov answers): W1–W6, S1–S6, C1–C4, K1, K3–K5, K7, P2, P3, and the 18 Nov audit's
S1–S3, K1–K6, T1.

## Not found

No broad `except Exception`, no bare `except`, no runtime `assert` in `src/`. The licence, the family and the error bar
are read from the measurement networks' record, on the same partner rule as `aromir evaluate`. Sizes outside 8–40 are
refused by `spectrum` and never licensed with `--outside-training-sizes`. Charges, radicals (bracket atoms), isotopes,
fragments, unsupported elements, dummy atoms, reaction SMILES, trailing text and non-ASCII are refused with reasons
(`audit_admission.py`). The weights' SHA-256 is verified at every load and `release.json` binds the records. The longest
packaged path is short (`aromir/releases/v1.4/seed-0.safetensors`); the 260-character pitfall is torch's, stated in the
README.
