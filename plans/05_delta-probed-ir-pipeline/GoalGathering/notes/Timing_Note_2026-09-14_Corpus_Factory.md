# Timing note 2026-09-14 — the corpus factory measured on six molecules (12–24 atoms), the corpus price that follows, and the grid check

*Module 05's corpus (`modules/05_support_predictor/corpus/`, DESIGN of 12 September) produces one proxy label per molecule: the difference of two DFT Hessians (ωB97X − B3LYP, 6-31G*) at the B3LYP-optimised geometry. Before the corpus runs, its price had to be measured, not asserted: this note records the timing test of 14 September (psi4 1.11 on Windows, conda `qc`, 8 threads, corpus grid (75, 302), `--grid-check` repeating the B3LYP Hessian on a (99, 590) grid). Files: `corpus/ledger.csv` (one row per molecule), `corpus/timing_test_2026-09-14.log` (the runner's log with the two relaunches), `corpus/molecules/<id>/result.json` (git-ignored; timings, frequencies, grid check). Printed numbers below come from those files (script in the 16:2x log entry of the mandate ledger).*

## 1. Measured

| molecule | atoms | optimisation s | B3LYP Hessian s | ωB97X Hessian s | dense-grid B3LYP Hessian s | total s | peak RSS GB | grid max abs Δν cm⁻¹ |
|---|---|---|---|---|---|---|---|---|
| benzene | 12 | 6.8 | 195.4 | 240.7 | 398.4 | 842.0 | 2.16 | **21.44** |
| quinoline | 17 | 36.3 | 830.0 | 1060.4 | 1670.7 | 3598.2 | 3.92 | 0.45 |
| azulene | 18 | 45.2 | 776.7 | 1195.9 | 1706.7 | 3725.2 | 4.16 | 0.56 |
| naphthalene | 18 | 32.7 | 707.4 | 1040.7 | 1638.4 | 3419.9 | 4.15 | 0.40 |
| biphenyl | 22 | 67.5 | 1343.2 | 1883.7 | 2673.1 | 5968.2 | 5.42 | 0.55 |
| diphenylacetylene | 24 | 54.6 | 1783.2 | 2997.5 | 3877.1 | 8713.0 | 5.70 | **28.34** |

The run itself: the 08:25 launch died with its PowerShell session; relaunched 08:35 from a persistent shell; benzene, azulene and biphenyl first failed *after* their Hessians on a worker bug (`float()` of the Hessian matrix; fixed 10:0x, rows reset); the runner's ordering rule then skipped naphthalene at 12:51 (its note had become "timing-test redone-after-crash" and the rule matched the note exactly; fixed 12:5x with `startswith`, the fix itself broke the file with an inline comment and was repaired 15:2x after `py_compile` and a dry run) — so the fifth molecule of the 08:35 runner was diphenylacetylene and naphthalene ran alone 15:17–16:15.

## 2. The scaling and the corpus price

Power-law fits over the six molecules (least squares in log–log; N = atoms):

- B3LYP Hessian: t = 0.094 · N^3.11 s
- ωB97X Hessian: t = 0.045 · N^3.49 s (range-separated exchange costs more per gradient and grows faster)
- both Hessians: **t = 0.121 · N^3.33 s** → 31 min at 18 atoms, 81 min at 24, 2.8 h at 30, 5.2 h at 36 (the last two are extrapolations)

Applied to the manifest as it stands (status ≠ done; optimisation added as 2 %; no grid check in production):

| layer | molecules | atoms (median) | laptop-hours | laptop-days | desktop-days (÷ 2.3–3.8, plan 05's untimed core-count rule) |
|---|---|---|---|---|---|
| A (aromatic cores, remaining) | 39 | 13–27 (21) | 35 | 1.5 | 0.4–0.6 |
| A2 (larger cores) | 868 | 16–30 (25) | 1,335 | 56 | 15–24 |
| B (substituted cores) | 4,353 | 8–26 (18) | 2,884 | 120 | 32–52 |
| **A + A2 + B** | **5,260** | | **4,254** | **177** | **47–77 ≈ 1.6–2.6 desktop-months** |
| C (Hessian-QM9 conjugated subset) | 6,055 | not in the manifest yet | — | — | cheapest per molecule (≤ 9 heavy atoms), priced when its atom counts are filled in; DESIGN §"layer C" already says it is computed only if the module needs it |

So the corpus of layers A + A2 + B is **a laptop half-year or two to three desktop-months** of DFT, in line with the estimate the mandate ledger carried ("2–3 desktop-months") and now measured at the low end. The learning-curve subsets of layer B (300 / 600 / 1,200 molecules, DESIGN) cost 8 / 17 / 33 laptop-days — the 300-subset is affordable on the laptop before any desktop exists, which is what the support predictor's first learning curve needs.

## 3. The grid check (mandate ledger obstacle 16)

Four of the six molecules agree between the corpus grid (75, 302) and the dense grid (99, 590) to **0.40–0.56 cm⁻¹** in the worst mode; naphthalene, the first molecule whose per-mode list was stored (worker patched 13:0x), has RMS 0.11 cm⁻¹ over its 48 modes and its largest difference (0.41) in a 517 cm⁻¹ out-of-plane mode. The two exceptions are benzene (21.4) and diphenylacetylene (28.3) — the two molecules with **degenerate or near-zero-frequency modes** (benzene's E irreps; diphenylacetylene's phenyl torsion and the two-fold C≡C bends), where a coarse grid splits a degenerate pair or shifts a mode near zero. The per-mode lists of those two are not stored (they ran on the old worker); a ten-minute benzene rerun on the new worker prints them. *Reading for the corpus:* the (75, 302) grid stands for production; the corpus's proxy label is a *difference* of two Hessians on the same grid, and degenerate-pair splits are removed by the family assignment (both members land in one family). The benzene rerun is queued behind M2a to close the obstacle with the mode named.

## 4. What this fixes in the plan

- The corpus price is measured at the molecule level (six points, 12–24 atoms, N^3.3); the P26 block's "2–3 desktop-months for the corpus" stands and is now **m** in the cost sense of the plan-06 ladder.
- Peak memory 2.2–5.7 GB: the corpus runs beside nothing (the rule: no psi4 beside an anchor job) but needs no machine beyond the laptop; on the desktop it can run two molecules at once if the anchor job is on Snellius.
- The worker now stores the dense-grid frequency list and projected Hessian; every future `--grid-check` answers the per-mode question itself.
