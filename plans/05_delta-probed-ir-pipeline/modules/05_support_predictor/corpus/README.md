# Module 05 corpus factory — start it, stop it, start it again

A resumable queue that computes, molecule by molecule, the two DFT Hessians Module 05 needs
(B3LYP/6-31G* and ωB97X/6-31G*), in a fixed priority order, so that **any stop leaves a usable,
reproducible subset** and any start continues exactly where the last one ended. Design and molecule
lists: [DESIGN_2026-09-12.md](DESIGN_2026-09-12.md). No molecule has been computed yet (2026-09-12).

## Files

| file | role |
|---|---|
| `manifest.csv` | **the source of truth**: one row per molecule — id, layer, priority, name, SMILES or QM9 label, atom counts, status (`pending`, `running`, `done`, `failed`), machine, deck hash |
| `ledger.csv` | append-only log: id, layer, machine, deck hash, start, end, seconds per step, exit status |
| `STATUS.md` | printed by `status.py`: counts per layer and status, hours spent and estimated to go (from the ledger's own times) |
| `decks/deck_v1.json` | the psi4 settings for every molecule; its sha256 is stamped on each result |
| `molecules/<id>/` | per molecule: `geometry.json`, `hessian_b3lyp.npz`, `hessian_wb97x.npz`, `result.json` (git-ignored; large) |
| `releases/vX.Y/` | frozen snapshots (manifest + result hashes) that go to Zenodo |
| `build_manifest.py` | builds `manifest.csv` deterministically from the DESIGN lists (re-running never reorders existing rows) |
| `run_corpus.py` | the queue runner (Windows Python; calls `psi4_worker.py` in the conda env `qc`) |
| `psi4_worker.py` | one molecule: optimise (layers A/B) and two Hessians; runs inside `qc` |
| `status.py` | rewrites `STATUS.md` |

## Start, stop, start again

```bash
python build_manifest.py                      # once, and again whenever DESIGN adds molecules (appends only)
python run_corpus.py --max-molecules 5        # the timing test: five molecules of layer A, then stop
python run_corpus.py --max-hours 8            # "until tomorrow morning"
python run_corpus.py --layer B --max-hours 8  # only layer B
python status.py                              # refresh STATUS.md at any time
```

Rules the runner enforces: one runner at a time (lock file `corpus.lock`); **it refuses to start while a
plan-05 anchor job is running in WSL** (`--force` overrides, and says so in the ledger); a molecule left
`running` without a complete result folder is redone on the next start; results are written to a
temporary folder and renamed only when complete, so a hard stop (Ctrl-C, power off) never leaves a
half result; a progress line every hour (the hourly-log rule); `--max-hours` and `--max-molecules` stop it
cleanly.

Several machines may work on the same corpus: the manifest and ledger travel through git (small), the
`molecules/` folders through a shared disk or copy (large); every result carries the machine name and the
deck hash, so mixed decks are visible at once.

## What you get at any stop

`STATUS.md` says, per layer, how many are done and how many hours the rest will take at the measured
rate. Because the priority order inside a layer is fixed (a hash of the SMILES), "the first 300 of
layer B" is always the same 300 — the learning-curve points 300 / 600 / 1,200 are nested subsets, not
new runs. **Run order** (`run_corpus.queue_order`, dated addition 2026-09-12): layer A first (the five
timing-test molecules at the very front), then layers B and A′ (`A2` in the files) alternating one by one,
so the class axis and the size axis grow together, then layer C. A release freezes the manifest rows with status `done` and their result hashes; later releases
add, never change.

## Dated note 2026-09-23 14:5x — deck v1's finite-difference Hessians and the grid

Benzene's layer-A ωB97X Hessian (psi4 findif of analytic gradients, 3-point, 0.005 bohr, grid 75/302 as in `decks/deck_v1.json`) was wrong by up to 133 cm⁻¹
at a D6h geometry. `fd_grid_test_benzene.py` reproduces it exactly with the deck and removes it with grid 99/590 (8 cm⁻¹ from the analytic pyscf Hessian);
B3LYP with the deck is off by 23 cm⁻¹ on one degenerate pair. Mechanism: DFT quadrature noise in the gradients divided by the small step. A corpus-wide screen
(`check_results.py`: sorted-pair functional shift > 80 cm⁻¹) flags benzene alone above 100; of the three A2 molecules at 80–88, the two carbazole+SH
entries agree with their analytic second route to 4 and 10 cm⁻¹ (genuine S–H shifts), and biphenylene+CH3 agrees on every mode but its lowest: the deck's
ωB97X finite differences give an imaginary methyl torsion at −37 cm⁻¹ where the analytic route gives +97 (`analytic_check.json`, corrected 16:2x). Decisions: layers A and A2 stay as computed (screened; benzene's row carries the analytic second route,
`hessian_<tag>_analytic.npz`, used by `m05/build_release.py --prefer-analytic`); **every new layer uses analytic Hessians (`analytic_hessians.py`, pyscf) or
grid 99/590 where psi4 finite differences remain**, and every molecule with a point group above C2v gets the second route by default.

## Dated note 2026-09-23 16:2x — a second artefact class: spurious imaginary soft modes

Biphenylene+CH3's screen hit was not a functional shift but a sign flip of its softest mode (see above). The corpus holds 20 molecules with an imaginary
mode in deck v1's Hessians (17 in layer A2, 3 in A); in 16 of them exactly one soft mode between −21 and −110 cm⁻¹ is imaginary in **one** functional
only (12 B3LYP-only, 4 ωB97X-only) while the other functional has it at +28 to +88 — the signature of grid noise flipping a torsion (methyl, vinyl,
CF3, NO2 substituents), not of a saddle point. Four have it in both functionals (pyrene+vinyl, acenaphthylene+vinyl, diphenylacetylene with −592/−453
in ωB97X, 9-methylanthracene); those may be genuine. All 20 are being recomputed along the analytic second route (both functionals, grid 99/590) on
the CCX53 (`run_imag_lanes.sh`, four lanes; logs `out/analytic_hessians_imaginary_2026-09-23_lane*.log`). Consequence if the flips are artefacts:
the release rule "drop imaginary-mode molecules" was dropping good molecules — up to 20 more rows for module 05 and E6/E7, from the second route.
`analytic_hessians.py` now compares the 3N−6 vibrational entries of both lists by the corpus convention (`vib_only`; pyscf's harmonic analysis had
dropped one mode of an imaginary-mode molecule and crashed the comparison) and has `--compare-only` to rebuild `analytic_check.json` from saved files.

## Dated note 2026-09-24 11:4x — the twenty imaginary-mode molecules read along the second route

`corpus/read_imaginary_second_route.py` → `data/second_route/imaginary_second_route_2026-09-24.{md,json}`. **5 healed, 15 genuine.** Healed (the
deck's finite differences made a soft torsion imaginary, the analytic Hessian has it real at +32 to +97 cm⁻¹): phenanthrene+CH3, phenanthridine+CH3,
pyrene+CH3, biphenylene+CH3 — all ωB97X-only flips, i.e. the range-separated functional on the default grid, as with benzene — and fluorene+CF3
(B3LYP, −20.5 → +32.4). Genuine (the analytic route agrees within a few cm⁻¹ that the mode is imaginary): the 12 B3LYP-only cases (NO2, CF3, vinyl,
Cl substituents; the optimiser stopped at a torsional saddle of the substituent at B3LYP) and the three cases imaginary in both functionals; carbazole+vinyl
also gains an ωB97X imaginary mode the corpus did not have (+28 → −82). So the 23 September hypothesis "16 single-functional flips are mostly grid
noise" was **right for the ωB97X flips (4 of 4 healed) and wrong for the B3LYP flips (1 of 12)**: those geometries are saddle points, a corpus
*geometry* issue, not a Hessian one. Fix for them (later, not before the 28th): re-optimise from a twisted substituent and recompute both Hessians.
Release `layerA2_2026-09-24` (`build_release.py --prefer-analytic`, imaginary rule now read from the analytic frequencies): 229 molecules (+5), 15
skipped as genuine, analytic Hessians for the molecules that have them. Noise level of the deck on the real modes of these 23 molecules: max |Δω|
0.5–5.6 cm⁻¹ for B3LYP, 3–32 (phenazine+vinyl) for ωB97X — the ωB97X finite differences are the noisier route throughout.
