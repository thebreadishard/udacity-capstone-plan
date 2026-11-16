# Handoff — aromir, stage 3 (the spectrum and its certificate), 15 November 2026

Follows `HANDOFF_2026-11-15_aromir_stage1.md` and `…_stage2.md`. Written from the same cloud session; the laptop was not reachable.
TASKS 73.

## What was added to `thebreadishard/aromir` (commit 363e1ed, branch `main`)

- `families.py` — module 05's family rule (`learning_curve_layerA.molecule_features`), on the low level's modes.
- `release.py` — a network release as a folder: `seed-<n>.safetensors` / `.json` per seed, `evaluation.json`, `training.json`; refused
  when a part is missing, the parts are of different versions, the seeds differ in settings, or there are fewer than two seeds.
- `certificate.py` — per band: position, height, the seeds' range, the B3LYP partner by eigenvector overlap (plain and scaled), family,
  the family's measured error per hold-out, licensed or not (decision 65's rule: within the line on every hold-out); the molecule's
  size against the training range; whether the network has seen it (trained / hold-out / unseen, by canonical SMILES); a warning when
  a corrected band is imaginary. JSON and Markdown.
- `aromir spectrum "<SMILES>" --out <folder> --release <folder>`.
- 198 tests, 99.8 % branch coverage.

Left out of the product's certificate, on purpose: the laboratory tolerance (`catalog.u_band`), the run's price, the website
catalogue's listing and the truth set beside the network — all of them read this repository's data.

## The two record files, and where they come from

`probes/aromir_model_card.py` (this branch) writes both from this repository's records, so that nothing is typed:

- `evaluation` — `m08.accuracy.network_accuracy` on the named models' evaluation records. Runs anywhere the records are; **run here
  for v1.3** (the records of chain 35 are in git): ring-ip 1.77 / 2.12, CH-stretch 1.19 / 2.50, CH-oop 2.17 / 2.70, other 3.62 / 3.89
  cm⁻¹ on hold-outs (a, clean, 8 molecules) / (b, 39 molecules) — the numbers of `docs/product_repo_design.md`. The file is in aromir
  as `tests/data/release/evaluation_v1.3.json`.
- `training` — the checkpoints' train_ids through `m08.pipeline.training_set` and `m08.seen.load`. **Needs the checkpoints and the
  corpus: laptop only, not run.** Written without being executed; run it once and read its output before trusting it.

## Validation (number and counterpart)

- The family rule against `molecule_features` on benzene's computed B3LYP Hessian (stage 1's run) and on toluene, biphenyl and
  phenanthrene with a force-field Hessian: 0 mismatches in 30 + 39 + 60 + 66 modes; frequencies equal to 9e-12 cm⁻¹.
- The certificate's arithmetic (partners, seed ranges, licence) is tested on synthetic inputs; a trial certificate was rendered from
  benzene's computed low level with a random two-seed release (its corrections mean nothing).
- **Not validated:** any corrected spectrum of a trained network. That needs the weights.

## What the laptop has to do to make release v1.3 (in this order)

1. `pip install git+https://github.com/thebreadishard/aromir` into an environment with torch (WSL `~/qc215` has pyscf 2.15).
2. Convert the three carried checkpoints into one folder, named as a release expects:
   `python -m aromir.network.convert modules/05_support_predictor/out/E7_rungC_chain35_analytic_model_n750_seed0.pt <release> seed-0 --network-version 1.3`
   and likewise `seed-1`, `seed-2`.
3. `python probes/aromir_model_card.py evaluation <release>/evaluation.json --version 1.3 --models <the three file names>` and
   `… training <release>/training.json …`.
4. Compare on one corpus molecule: aromir's ΔH from the release against `rungC_infer.delta_H` on the checkpoint, and aromir's band
   positions against pipeline 0.9's `pipeline.json` for benzene (`pipeline_benzene_computed_2026-11-03`). Expect differences from the
   engine (pyscf geometry instead of psi4's, TASKS 73's engine check) and from the listed soft modes; write the numbers down.
5. `aromir spectrum "c1ccccc1" --out <folder> --release <release>` — the first real certificate.

## Differences from pipeline 0.9's live certificate, to carry into the model card

- Every one of the 3N−6 modes is a band; 0.9 lists modes above 20 cm⁻¹.
- The seeds' range pairs bands by rank among all modes, as 0.9 does; the B3LYP partner is by eigenvector overlap, as 0.9's.
- A corrected band below zero is listed with a warning instead of leaving the list.
- Elements outside the release's training elements are refused before the first SCF; a size outside the training range is marked.

## Still to build for 0.1

1. The printed anharmonic position (`PreRegistration_2026-11-14_Printed_Band_Position.md`; TASKS 211, 219).
2. The low-mode repair in the label route (TASKS 216; `corpus/grid_response_blocked.py`, pyscf 2.15).
3. The release itself: where the weights live (the design: in the wheel and on the Hub) and the model card's text.
