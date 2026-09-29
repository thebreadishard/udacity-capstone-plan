# Pre-registration 2026-09-29, 03:4x — anchor set two: four coupled-cluster Hessians that each answer one open question

*Written before any number. The user's decision of 29 September (≈ 03:2x): "laten we dan zsm meer ankers bouwen"; server `ubuntu-32gb-hel1-23`
(CPX62, 16 shared vCPU, 157.180.32.149) created by the user ≈ 03:4x because the dedicated-vCPU quota (32/32) admits no second CCX53; credit raised to
€400 the same hour (usage €309.88), which bounds the whole fleet to about two days — the CCX53 goes after naphthalene's assembly. Method and
guards are those of E8 (`PreRegistration_2026-09-23_E8_CC_Correction_Locality.md`; `probes/e8_cc_hessian_fd.py --symmetry`, frozen core derived from
the elements, pair check of every coordinate as it lands, self-check before any read-out — the incident rules of 27 September).*

## Why

Everything the project knows about the real coupled-cluster correction rests on one molecule (benzene, 24 September) and, from Tuesday evening, two
(naphthalene, frozen-10 rerun). The band prior failed on benzene (4 % of the off-diagonal power in band, CC-level test of 28 September); the core-transfer
rule E9 (25 % of the gradients suffice for a substituted molecule) is proxy evidence; the cation gap (obstacle 9) has no CC row at all; whether a
nitrogen in the ring carries benzene's correction is untested. Each anchor below is chosen for one of these questions, all four together cost about
80 CPX62-hours (≈ €17 at €0.208/h) — the same molecules on a CCX53 would have cost four times as much for the same wall time, because pyscf's CCSD(T)
gradient does not scale past 16 threads.

## The anchors, in run order, each with its question

| # | molecule | corpus row | point group | frozen core | question | ≈ gradients | ≈ CPX62 hours |
|---|---|---|---|---|---|---|---|
| 1 | benzonitrile C₆H₅CN | A_3100da3761 (done) | C2v | 8 | E9 at CC: does the parent block plus two-bond columns reproduce the substituted molecule | 54 | 33 |
| 2 | fluorobenzene C₆H₅F | B_8b12a55d3a (pending → corpus step on the anchor server) | C2v | 7 | E9 for a second substituent type (halogen; layer B carries F, Cl) | 42 | 26 |
| 3 | pyridine C₅H₅N | A_6e858b26e5 (new row, corpus step on the anchor server) | C2v | 6 | element transfer: benzene's ring block carried onto an N-ring — the size of the residual | 42 | 7 |
| 4 | benzene cation C₆H₆⁺ | obstacle-9 row (`probes/results_m1/cations/benzene`, UKS-B3LYP Jahn–Teller minimum) | D2h | 6 | the first CC-level cation: obstacle 9, and the certificate ladder's "anchored" rung for a cation | 24 | 15 |

Deferred, to decide after naphthalene's read: azulene (topology, module 08's refused molecule; ≈ 230 dedicated hours). Gradient counts are the
symmetry-unique displacements × 2; hours are scaled from the measured benzene (11 min per gradient at 16 threads, 114 basis functions) and naphthalene
(4.25 h, 180 functions) with the sixth-to-seventh-power rule; the cation's UHF-UCCSD(T) gradient is taken at three times the closed-shell price.
Predictions on record: **total ≤ 100 hours**; no anchor exceeds twice its estimate.

## Gates (before the chain spends hours)

- **G1 smokes.** Water (RHF, the validated path) and the water cation (`--charge 1 --spin 1`: UHF with up to three stability rounds, ⟨S²⟩ within 0.05 of
  0.75, UCCSD(T) gradient, pyscf 2.14) both produce a valid Hessian with the pair checks and the self-check passing. Run first on the laptop (WSL) and
  again on the server; a failure stops the chain before benzonitrile.
- **G2 corpus steps.** Fluorobenzene and pyridine get their B3LYP geometry and both DFT Hessians with the corpus deck v1 on the anchor server (psi4,
  minutes); the anchor runs at that geometry, as every anchor does. Layer-B shards may compute fluorobenzene independently; the deck is the same, and the
  merge keeps one row.
- **G3 validity per anchor** (E8 rules, unchanged): pair check ≤ 1e-4 a.u. at every coordinate, FD asymmetry ≤ 2e-3 a.u. (symmetry spread for the
  reduced runs), translational–rotational null space within the limit, no imaginary frequency; an invalid Hessian is written as such and read by nothing.

## Read-outs and lines (fixed now)

- **R1 — in-band share of the CC − B3LYP off-diagonal power** (200 cm⁻¹; the CC-level test's `delta2.inband_share_cc`, computed with
  `pp.core.export_molecule(..., hi_override=…)` for the corpus rows, and directly from the two Hessians for the cation). Prediction: ≤ 15 % on each of the
  three neutrals (benzene 4 %). Reading rule: naphthalene plus at least two of these three below 15 % → "the band prior fails on the CC correction" is a
  rule of the correction, no longer a benzene statement; the module 08 plan line and the Ladder's default prior are written accordingly.
- **R2 — E9 at CC (benzonitrile, fluorobenzene).** The E9 probe's transfer step run with ΔH = H_CCSD(T) − H_B3LYP in place of the proxy: benzene's CC
  block carried onto the parent core, the columns of atoms within two bonds of the substituent taken from the molecule's own CC Hessian, the rest zero;
  corrected harmonic frequencies against the full CC Hessian's. Lines as registered for E9: RMS ≤ 3.3 cm⁻¹ and residual ratio ≤ 0.5 against the
  uncorrected B3LYP error. Prediction: pass on both, RMS 2–4 cm⁻¹ (the CC correction was one bond less local than the proxy on benzene), so the first
  line is at risk on one of the two; the ratio line passes. Script: the E9 probe's read-out adapted to a CC ΔH input, written before the read and
  smoke-tested on the proxy export where it must reproduce the E9 numbers.
- **R3 — element transfer (pyridine).** Benzene's CC block mapped atom by atom onto pyridine (N in place of one C, hydrogens likewise), no columns probed:
  RMS of the corrected frequencies against pyridine's own CC Hessian, split by modes with and without dominant N participation. No pass line; the number
  sets the question for rung C. Prediction: 6–12 cm⁻¹ overall, worst on the N-participating modes; if it comes out ≤ 3.3 cm⁻¹ the element is a detail and
  the corpus's heteroatom rows are cheap to label.
- **R4 — the cation.** Frobenius ratio of the cation's off-diagonal CC correction to the neutral's, the diagonal correction's RMS in cm⁻¹ for both, and
  R1 for the cation. Prediction: a larger diagonal correction than the neutral's (open shell), in-band share still ≤ 15 %, no imaginary frequency at the
  UKS minimum. A CC-level cation row then exists for module 08's ladder and for the proposal's obstacle 9.
- **R5 — diagonal against couplings, all anchors and naphthalene** (desk test, hours): the harmonic frequency error of B3LYP against CC removed by the
  diagonal of the correction alone, against the full correction, per family. Prediction: the diagonal removes ≥ 70 % of the in-plane RMS error and
  less out of plane (the R0 reading of 22 September). This number decides how much of the plan must be about couplings.

## What is not claimed

Four small molecules, three of them one ring. Nothing here trains or retrains anything; the learned layer's licence stays with the layer-B curve. The
anchors are inputs to module 08's ladder (rung "anchored", family coverage from the evidence file) and to the standout's CC-level tests, under those
tests' own pre-registrations. Prices are recorded as measured, not as estimated, in the module 08 price table when the chain ends.

## Guards

Frozen core derived per molecule (the 27 September rule); every gradient file written as it lands so a broken run resumes; the poller reports every pair
check and every ANCHOR … DONE/FAILED line; the chain stops on the first failure. Chain: `probes/run_anchors_hel23.sh`; logs `/root/e8/anchors.log`,
`/root/e8/results/<name>/e8_fd.log`. Server deleted by the user when the results are fetched and verified per file.

## Amendment, 29 September 05:1x — the low level of every read is the analytic route (before any anchor number exists)

Found while building R2's read-out (`m05/e9_cc_readout.py`, the E9 construction with a CC ΔH) and checking it on the proxy: benzene's corpus row
(A_8448043181, psi4 finite-difference Hessians, grid 75/302, the 15 September grid rerun) is noise-dominated — against the pyscf analytic
Hessians of the same geometry (grid 99/590, `corpus/analytic_hessians.py`, which recorded the fact on 23 September) its ωB97X frequencies are off by
up to 132 cm⁻¹ (RMS 35; degenerate pairs split by 42 cm⁻¹) and its B3LYP ones by up to 23 cm⁻¹ (RMS 5), so its proxy correction ΔH is 106 % noise
relative to the analytic ΔH. Benzonitrile's row is clean (analytic B3LYP within 0 cm⁻¹, ωB97X within 3). The E9 proxy check benzene → benzonitrile
reads FAIL with the psi4 pair (r = 2: corrected ω RMS 21.9 cm⁻¹, ring coupling ratio 3.7) and PASS with the analytic pair (0.88 cm⁻¹, 0.06;
residual ratio 0.015) — the same construction, the same molecules, only the noise removed.

Consequences, fixed now:

1. **R1–R5 use ΔH = H_CCSD(T) − H_B3LYP with the pyscf analytic B3LYP Hessian** (6-31G* Cartesian d, grid 99/590, at the corpus geometry), for
   the anchors and for benzene and naphthalene, never the corpus psi4 FD file. `e9_cc_readout.py --use-analytic`, `cc_level_test.py --use-analytic`
   (with `run_export.py --use-analytic --only <id>` for the matching proxy export); the E8 locality read already computed its own analytic pair.
   Analytic pairs exist for benzene (23 Sep) and benzonitrile (29 Sep, hel1-23, niced beside the CC run); fluorobenzene and pyridine follow in the
   same job; the cation needs the UKS variant of `analytic_hessians.py` before R4.
2. **R2's proxy prediction is now on record with the clean pair:** transfer + probe at r = 2 gives 0.88 cm⁻¹ / ratio 0.06 on the DFT proxy; the CC
   lines stay as registered (≤ 3.3 cm⁻¹, ≤ 0.5). The prediction "RMS 2–4 cm⁻¹ at CC" stands.
3. **The 28 September CC-level test on benzene** (`Standout_CC_Level_Test`) read Δ_CC against the noisy psi4 B3LYP and compared with the noisy proxy
   (its "proxy 52 % in band" is the noise's share; the analytic proxy export gives 30 %). It is rerun with `--use-analytic` and its outcome section
   is corrected separately; nothing built on it (band-free prior default, reading (ii)) is judged until that rerun is read.

## Proxy numbers on record with the analytic pairs, 29 September 05:4x (before any CC number of the set)

`m05/e9_cc_readout.py --use-analytic` on the DFT proxy (ωB97X − B3LYP, pyscf analytic pairs at the corpus geometries), outputs in
`modules/05_support_predictor/out/e9_cc/`:

| read | pair | construction | ΔH residual ratio | ring coupling ratio | corrected ω RMS (zero rule) |
|---|---|---|---|---|---|
| R2 | benzene → benzonitrile | transfer + probe, r = 2 (5 of 13 atoms) | 0.015 | 0.06 | 0.88 cm⁻¹ (24.2) |
| R2 | benzene → fluorobenzene | transfer + probe, r = 2 (4 of 12 atoms) | 0.014 | 0.07 | 0.76 cm⁻¹ (23.2) |
| R3 | benzene → pyridine | transfer only, element map (11 of 12 core atoms mapped, the lost H unmapped) | 0.128 | 0.18 | 2.03 cm⁻¹ (25.0); N-participating modes (2) 2.83, other (25) 1.95 |

Both R2 pairs pass the registered lines on the proxy at every radius from r = 0. R3 on the proxy reads 2.0 cm⁻¹ — below the 3.3 cm⁻¹ mark that would
make the element a detail — against the prediction of 6–12 cm⁻¹ written for the CC level above; the CC number decides, the prediction is kept as
written. Side finding: pyridine's psi4 FD corpus row (computed today) is off its analytic pair by up to 12 cm⁻¹ (B3LYP; the 670 cm⁻¹ mode) and 17 cm⁻¹
(ωB97X), RMS 2.3 / 5.4 — larger than benzonitrile's (0 / 3) and fluorobenzene's (0 / 5); one more reason the reads take the analytic pair.
