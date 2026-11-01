# The public product repository — design

1 November 2026. TASKS 73. The user (16 Oct 2026): at the end, a separate public repository holds only the result. That means the pipeline,
the final model with open weights and the code that is relevant, so that others can use and fork it ("een beetje zoals pyscf"). This note
fixes the design so that the build in 2027 is mechanical. The build starts after the final model choice; nothing is built now.

## What goes in and what stays out

**In:** the pipeline (geometry → low-level Hessian and APT → ΔH network → frequencies, intensities, spectrum, certificate), the carried
network's weights with a model card, the training code and its recipe, tests, CI and documentation. **Out:** the chat, the Udacity modules,
`plans/`, the ledgers, `probes/`, the run directories, the website, module 07's steward and module 08's replay worker and prices. The
repository starts with a fresh git history: no filtered copy of this one (decided 16 Oct).

## Where things live (provisional choice, the user 16 Oct: 'Ja!')

| what | where | form |
|---|---|---|
| code | GitHub, released to PyPI and conda-forge | the package `dpir` (the name `src/dpir` already uses) |
| weights | Hugging Face Hub, a model repository, pinned by revision | safetensors, one file per seed, plus a JSON recipe; the loader checks sha256 |
| data | Hugging Face Hub, a dataset repository (the same as paper D's Zenodo deposit) | Parquet; the CC anchors as their own split |
| showcase | optional: a Hugging Face Space showing recorded certificates | no live computation (the Hessian step is too heavy for a free Space) |

v1.3's weights are 1.26 MB per seed (`E7_rungC_chain35_analytic_model_n750_seed{0,1,2}.pt`), so a copy inside the wheel would also fit.
The Hub stays the source; the package downloads a pinned revision on first use.

**Licences:** MIT for code; CC BY 4.0 for weights and data, as on the data mirror (27 Sep). The required dependencies are compatible with
MIT: pyscf (Apache-2.0), geomeTRIC (BSD-3), RDKit (BSD-3), PyTorch (BSD-3), NumPy, pydantic. psi4 (LGPL-3) is an optional extra only.

## The package

One module per pipeline step. Each settings object is one validated pydantic config, and every refusal happens before the first
computation (CLAUDE.md, 'Python code'):

```
dpir/
  geometry.py     SMILES → canonical order → RDKit ETKDG + MMFF → B3LYP/6-31G* optimisation (pyscf + geomeTRIC)
  lowlevel.py     analytic B3LYP Hessian and APT (pyscf), with the CPHF residual guard
  families.py     the band-family rule (one implementation; today in probes/promotion_read.py and module 03)
  network/        the equivariant body and the hybrid head (from m05/rungC_equivariant.py and rungC_hybrid.py), the inference
                  loader, the weights download
  spectrum.py     H_low + ΔH → positions; double-harmonic heights; broadening; the scaled-B3LYP baseline beside it
  certificate.py  per-band licence, seed spread, the error from the version's own evaluation records, training-set membership, provenance
  provenance.py   from src/dpir (promoted 21 Sep)
  qff.py          from src/dpir (promoted 21 Sep), for the anharmonic step once it is carried
  train/          the training code and recipe (from m05/rungC_train.py), early stopping by decision 51
  cli.py          `dpir spectrum "c1ccc2ccccc2c1"` → a result folder with spectrum, certificate and provenance
```

Today these modules read from five places through `sys.path` edits: `probes/` (`promotion_read`, `learning_curve_layerA`, `apt`,
`anchor_registry`, `scale_factor_baseline`), module 05's `m05/`, module 08's `m08/`, `corpus/` and `src/dpir`. In the product each
function has one home and is imported from there. Each module enters through the promotion checklist (QUALITY_POLICY.md, decisions
47/57): pure functions, a known-answer test, an invariance test, a negative control for the incident behind it, reproduction of the
probe's arrays, provenance, review and green CI.

## Three open design points

**1. One engine: pyscf + geomeTRIC instead of psi4 + pyscf.** The pipeline today optimises in psi4 1.11 under Windows conda and computes the
Hessian in pyscf 2.14.0 under WSL (`m08/pipeline.py`). A public package needs one engine that installs with pip. pyscf runs on Linux and
macOS; on Windows it runs through WSL, and the README says so. The switch waits for a check, registered before it runs. On the
hold-out (a) set, compare a pyscf-optimised geometry with the corpus deck's psi4 geometry: the largest coordinate difference, the B3LYP
frequencies and the network's corrected band positions. Proposed pass line: corrected positions within 0.3 cm⁻¹ at most, a tenth of
decision 53's 3 cm⁻¹. psi4 stays an optional route that reproduces the corpus deck bit for bit (deck v1, sha16 9e27bf8e934893f3).

**2. The CPHF guard ships until upstream fixes the solver.** pyscf 2.14.0's Krylov solver stops before its CPHF solution satisfies its
equations (software ledger row 44, issue #2702). Our `refine_response` checks the residual and refines it; the APT depends on this guard.
jeanwsr's fix, pyscf#3384, was approved on 1 Nov 2026 but is not merged. The product pins a pyscf range. The guard stays and checks every
solution until a released pyscf passes our two cases (B_127dd8c4ed and the labels case); after that it stays only as the check.

**3. The answer does not depend on how the molecule is written.** v1.3 moves bands by up to 2.9 cm⁻¹ between two SMILES writings of
phenanthrene and by up to 10 cm⁻¹ under arbitrary atom orders (TASKS 149). The pipeline fixes one order per molecule; the product must
also be invariant for an xyz input. Either the network becomes invariant, or the canonical order is applied to every input, including
xyz. This is a release condition, with a test that permutes the atoms.

## The model card

All numbers are read from the carried version's evaluation records, never typed in (the way `m08/licence.py` reads them). For v1.3
today, the seed-mean error on hold-outs (a) / (b) against the ωB97X labels, in cm⁻¹:

| family | ring-ip | CH-stretch | CH-oop | other |
|---|---|---|---|---|
| (a) / (b) | 1.77 / 2.12 | 1.19 / 2.50 | 2.17 / 2.70 | 3.62 / 3.89 |
| decision 65 | licensed | licensed | licensed | not licensed |

Source: `E7_rungC_chain35_analytic_eval_frozenb_seed{0,1,2}.json` and `…_a8read_seed{0,1,2}.json`, through `m08.licence.state()`, 1 Nov
2026. The card states the limits and how the certificate refuses or marks each one:

- the level is the DFT proxy (ωB97X), and there is no coupled-cluster licence;
- neutral closed-shell molecules from the elements in the training set only (cations: TASKS 121);
- the measured reach is about 40 atoms (findings of 8–9 Oct; chain 42);
- the positions are harmonic (the anharmonic step is TASKS 53);
- the 'other' family is not licensed.

## Reproducibility as a release test

- **The weights.** A clean clone retrains one seed from the Hub dataset with the shipped recipe, on a rented Linux machine (the publication
  freeze, QUALITY_POLICY.md). It must reproduce the published evaluation record within the seeds' own spread. A bit-for-bit match is not
  promised across hardware.
- **The pipeline.** The certificates of the demonstration molecules are reproduced: benzene, phenanthrene and module 06's candidate (the
  pipeline record in `modules/PIPELINE.md`).

## Order of the build (2027, after the final model choice)

1. Run the engine check (point 1) and settle the atom order (point 3); both are recorded here before the build.
2. Write the package skeleton, CI (Linux and macOS, small water and benzene tests) and the licence files.
3. Promote module by module through the checklist, each with its regression test against this repository's output on the same molecules.
4. Convert the weights (safetensors and the recipe) and publish the Hub dataset with paper D.
5. Write the model card, README, CITATION.cff and the paper D DOI.
6. Run the publication freeze: a fresh clone on a clean machine. Then the first release (v1.0 = the version submitted with module 08,
   `PIPELINE_BUILD_NOTE_2026-10-29.md`).

## Decisions for the user

- The repository's name. The import name stays `dpir` unless the user chooses another.
- The pass line of the engine check (proposed: 0.3 cm⁻¹).
- Whether a copy of the weights also ships inside the wheel. Proposed: no, the Hub only.
