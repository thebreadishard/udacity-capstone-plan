# Spectrum Atlas export — data contract (version 1, 24 September 2026)

Produced by `build_catalog.py` from the pipeline repository; consumed by the site. Every value comes from a file in the repository; the script
exits non-zero when an invariant breaks. Numbers in the site's templates never come from anywhere else.

## `catalog.json` — one object per manifest molecule (11,321 today)

| field | type | source | notes |
|---|---|---|---|
| `id` | string | `corpus/manifest.csv` | e.g. `A_01f3186607`; stable |
| `name` | string | manifest | corpus name (`fluoranthene+COOH` style for substituted entries) |
| `smiles` | string | manifest | |
| `formula`, `inchikey` | string or null | RDKit from `smiles` | null when the SMILES is absent or does not parse — today all 6,055 layer-C rows (QM9 entries carry a `qm9_label` and no SMILES yet) |
| `layer` | `A` / `A2` / `B` / `C` | manifest | |
| `n_heavy`, `n_atoms` | int | manifest, else RDKit | pending rows of B/C carry no counts in the manifest |
| `rung` | 0–5 | derived | see the ladder below |
| `rung_label` | string | derived | `listed`, `cheap_level_done`, `correction_predicted`, `spectrum_predicted`, `anchored`, `validated` |
| `flags` | list of strings | derived | `imaginary_mode_under_review`, `screen_flagged`, `second_route_agrees`, `second_route_disagrees`, `replaced_by_second_route` |
| `releases` | list of strings | `data/corpus_release/*_manifest.json` | release names containing the molecule |
| `manifest_status` | string | manifest | `pending` / `done` / `failed` |
| `evidence` | list of paths | the fixed lists in the script | only for rungs 4 and 5; paths relative to plan 05 |

**The ladder.** 0 listed (manifest row only) · 1 cheap level done (`result.json` with status done and both Hessian files) · 2 correction predicted
(reserved: the learned layer has produced ΔH) · 3 spectrum predicted (reserved) · 4 anchored (a coupled-cluster read-out exists; fixed list with
evidence files) · 5 validated (compared with a laboratory spectrum; fixed list). A molecule holds the highest rung it reaches.

## `molecules/<id>.json` — per computed molecule (244 today)

`id, name, smiles, formula, layer, n_atoms, geometry` (the corpus `geometry.json`: symbols, coords_bohr, masses_amu), `deck` (the corpus deck
record), `timings_s`, `energies {b3lyp, wb97x}`, `n_imaginary {b3lyp, wb97x}`, `frequencies_cm {b3lyp, wb97x: {all: 3N values, vibrational: 3N−6
values by the corpus convention — six entries nearest zero dropped, imaginary negative}}`, `releases`, `ledger` (the run's ledger row: machine, deck,
start, end, seconds, peak memory), `second_route` (per functional: `max_abs_dfreq_cm`, `dH_max`; null when no analytic check exists).

## `summary.json`

`built_utc`, `n_molecules`, `rung_counts` (sum = n_molecules — checked), `layer_counts`, `rungs`, `sources` (SHA-256 of manifest and ledger),
`releases`.

## Invariants the build enforces

- every catalog id has a manifest row; rung counts add up to the catalog length;
- a computed molecule has both Hessian files and frequency lists of length 3N; its manifest atom count equals the SMILES count;
- every evidence file of the anchored / validated lists exists.

## Not yet in the contract (added when the pipeline produces them)

Predicted corrections and spectra (rungs 2–3) with ensemble spread; intensities; laboratory band tables from module 03; the run queue.
