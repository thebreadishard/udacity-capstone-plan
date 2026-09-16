# X18 — type transfer of the internal-coordinate correction, benzene → naphthalene (run 16 September 2026)

*Lead D's real test (README item 29, prepared 13 September; mandate ledger obstacle 2 / idea I4). Script `experiments/x18_type_transfer.py`, outputs `experiments/x18_benzene_to_naphthalene_sym.{md,json}`. Stand-in correction: BHHLYP − B3LYP at 6-31G*, first order per mode, both molecules from plan 05's stage A (`probes/results_dryrun/benzene/` and `probes/results_dryrun/naphthalene_sym/` — the symmetrised, irrep-projected naphthalene set of 15 September; its B3LYP/BHHLYP pair is the one the source constants were fitted on). Pre-registered rule (13 September): per family, RMS of predicted − measured first-order shift ≤ 2.5 cm⁻¹; judged families C–H stretch and C–C stretch; losing condition: either fails.*

## The result

| family | modes | RMS error (cm⁻¹) | max | RMS with no transfer (zero rule) | fraction of the RMS removed | judged | passes 2.5 |
|---|---|---|---|---|---|---|---|
| C–H stretch | 8 | **0.27** | 0.60 | 25.11 | 99 % | yes | **yes** |
| C–C stretch | 9 | **17.82** | 38.90 | 41.22 | 57 % | yes | no |
| C–H in-plane bend | 9 | 5.76 | 14.81 | 35.82 | 84 % | — | no |
| ring in-plane | 7 | 6.42 | 11.92 | 22.02 | 71 % | — | no |
| C–H out-of-plane | 15 | 64.48 | 85.15 | 64.48 | 0 % (not modelled: in-plane block only) | — | no |

**Verdict under the pre-registered rule: LOSE** — the C–C stretch family fails. Per family the picture is sharp: a correction that lives in σ-local internal coordinates (the C–H stretch) transfers by local type from one ring to two rings essentially exactly, 0.27 cm⁻¹ against a 25 cm⁻¹ correction; the ring-skeleton families do not — the C–C stretch keeps an 18 cm⁻¹ residual that no assignment of one constant per local pair type removes. On the DFT stand-in this is the same ordering the physics argument of 14 September gave for the coupled-cluster correction (C–H families transfer, the C–C stretch of a delocalised π system is the doubtful one), now measured.

Source fit (benzene, type-constrained, 29 types, rank 24): in-plane first-order residual 0.031 cm⁻¹; the benzene → benzene self-test reproduces every in-plane family to 0.01–0.05 cm⁻¹ (unchanged from 13 September).

## A defect found and fixed before the number was read

The first run printed "errors" of 10⁹ cm⁻¹ on every in-plane family. The cause was the source fit, not the transfer: the type design matrix on benzene has 24 real directions and five null ones (the redundancy of the 42 internal coordinates — singular values 2.4 × 10⁻³ … 6.3 × 10⁻⁵, then 2 × 10⁻¹⁰, 3 × 10⁻¹¹, 7 × 10⁻¹⁶, 3 × 10⁻¹⁹, 2 × 10⁻¹⁹). NumPy's default cutoff kept the 10⁻¹⁰ directions, and three C–C/C–C–C coupling types received constants of 2.7 × 10⁶ that cancel on benzene (the self-test could not see them) and not on naphthalene. Truncating at 10⁻³ of the largest singular value removes exactly the five null directions: the source residual is unchanged (0.031 → 0.031 cm⁻¹) and the largest constant falls from 2.7 × 10⁶ to 0.0125. Recorded in the script's `CONSTANTS["why_rcond"]`; the singular values and the rank are written to the JSON of every run. Lesson for every fit on redundant coordinates in this project: print the singular values and the rank before the residual.

The run against plan 05's factory naphthalene set (`results_dryrun/naphthalene/`, ωB97X as the high arm) is not a test of this source — different correction — and its output was discarded.

## What follows

- **For plan 06, lead D:** closed as a route to the *whole* correction (the losing condition fires on the C–C stretch), open as a route to the C–H stretch family — where a network is not needed at all: one constant per local type carries the family across size. Whether that holds for the coupled-cluster correction is the per-family transfer test T-1/T-2 of plan 05 (P26), which this result now motivates family by family.
- **For plan 05:** the per-family go/no-go of P27 (rung R2a) should read the C–H stretch first — the family the stand-in already shows to be type-local — and treat the C–C stretch as the family most likely to need the network's non-local input. The out-of-plane family has no type model yet (orientation signs; X17's caveat), which matters because it is the astrophysical 11–13 µm band.
- The DFT stand-in's numbers here are 6-31G*, B3LYP → BHHLYP; the coupled-cluster increment differs in size and possibly in locality. No claim beyond the stand-in.
