# Plan 06 — `lean/`: the formal route (Lean 4 + Mathlib)

Created 2026-09-12 after reading note X4 (`../GoalGathering/Reading_Note_2026-09-12_X4_Mathlib_Survey.md`)
and the user's decision the same day to install Lean and set up the first formal target.

## What is here

- `lakefile.toml`, `lean-toolchain`, `lake-manifest.json` — a Lake project generated with
  `lake +leanprover-community/mathlib4:lean-toolchain new plan06 math`; Mathlib pinned by tag
  (`rev = "v4.34.0-rc2"`, commit `85e3a25e…` in the manifest), Lean `v4.34.0-rc2`. The pin is the
  reference for every Lean name quoted in X4; do not `lake update` without a dated note.
- `Plan06/T1/MeasurementAlgebra.lean` — **T1**, the measurement algebra of plan 05's probing deck
  (direction S5): pattern, column-intersection graph, colour-class probes, and the theorem that a
  matrix respecting a known pattern is recovered exactly from one matrix–vector product per colour
  (Curtis–Powell–Reid 1974 / Coleman–Moré 1983). **Proved (no `sorry`):** T1a (`recover_probe`,
  `eq_of_probes_eq`), T1c the greedy `Δ + 1` colouring bound (`exists_proper_on_finset`,
  `colorable_maxDegree_succ`; not in Mathlib on 2026-09-12) and their corollary
  `exists_coloring_recover` (`Δ + 1` probes determine every matrix respecting the pattern). **Owed:**
  T1b, the symmetric refinement of Powell & Toint (1979), stated with `sorry`.
- `Plan06/Basic.lean`, `Plan06.lean` — the template root module, importing T1.

## How to build

```bash
# once per machine: elan (installed 2026-09-12 in ~/.elan; adds lean/lake to PATH)
lake exe cache get      # downloads Mathlib's compiled oleans (several GB) — never build Mathlib from source here
lake build              # builds Plan06; a `sorry` prints a warning, an error stops the build
```

Everything under `.lake/` (Mathlib source and compiled files) is git-ignored and re-creatable.

Measured footprint on 2026-09-12 (PowerShell `Measure-Object`): `~/.elan` (elan 4.2.4 + Lean v4.34.0-rc2)
3.06 GB / 17,756 files; `lean/.lake` (Mathlib source + compiled oleans + this build) 6.9 GB / 141,550 files;
`~/.cache/mathlib` (the downloaded cache archives) 0.41 GB / 8,747 files — about 10.4 GB in all. First
`lake build` of `Plan06` with `import Mathlib`: 91 s for the T1 file, 32 s for the root module.

## Rules (plan 06 protocol, Orientation §6)

- A statement is either a theorem in this folder or it is not claimed. `sorry` marks an owed proof and is
  listed in the file header.
- Nothing here changes plan 05; a proved statement transfers only through a plan-05 dated note.
- Names from Mathlib are checked against the pinned version, never quoted from memory.
