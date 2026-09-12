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
new runs. A release freezes the manifest rows with status `done` and their result hashes; later releases
add, never change.
