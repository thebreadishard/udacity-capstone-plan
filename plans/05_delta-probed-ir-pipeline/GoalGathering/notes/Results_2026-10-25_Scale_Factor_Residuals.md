# Results: what a scale factor leaves, per mode family (TASKS 112 and 111, 25 Oct 2026)

Pre-registration: `PreRegistration_2026-10-25_Scale_Factor_Residuals.md` (commit 08c594fe, before any number). Records:
`modules/05_support_predictor/out/scale_factor_baseline_2026-10-25.{json,md}`, `…/fundamentals_vs_experiment_2026-10-25.{json,md}`,
`…/mai_teacher_overlap_2026-10-25.{json,md}`; scripts `probes/scale_factor_baseline.py`, `probes/fundamentals_vs_experiment.py`,
`probes/mai_teacher_overlap.py`, each committed with its tests before its run. Mai et al. 2026 enter as statistics only (CC BY-NC-SA 4.0).

## 1. The proxy task: the carried network against the best scale factor (reading 1)

Quantity: the rms error of the first-order frequency shift B3LYP/6-31G* → ωB97X/6-31G* per mode family, read by `E6.readout` for the
network and for the scale factors alike. Factors fitted by least squares on all 1,073 pool molecules (generous to the baseline); network =
carried chain 34 (v1.1), seed mean of its three analytic records.

| cm⁻¹ | CH-stretch | CH-oop | ring-ip | other |
|---|---|---|---|---|
| (a), 10 molecules — one factor (S1) | 2.46 | 13.44 | 16.09 | 8.63 |
| (a) — three PAHdb-region factors (S3) | 2.02 | 9.21 | 15.47 | 8.58 |
| (a) — one factor per family (SF) | 2.04 | 6.61 | 15.31 | 8.46 |
| (a) — **network** | **1.25** | **2.36** | **1.82** | **3.35** |
| (b), 39 molecules — S3 | 3.86 | 9.96 | 14.19 | 14.63 |
| (b) — **network** | **2.57** | **3.81** | **2.62** | **6.03** |

Lines: L1 (network < S3 on (a), every family) **PASS**; L2 (network < SF on (a)) **PASS**; L3 (network < S3 on (b)) **PASS**. The network
removes 38 / 74 / 88 / 61 % of S3's residual on (a) and 33 / 62 / 82 / 59 % on (b). A second route (`probes/scale_factor_baseline_second_route.py`: direct (f − 1) ω − K_ii, no
`E6.readout`; log `probes/results_m1/scale_factor_baseline_second_route_2026-10-25.log`) gives the S3 numbers to 0.01 cm⁻¹. Why scaling fails where it does: inside ring-ip the shift averages +11.6 cm⁻¹ with a spread
of 16.0 cm⁻¹ between modes, so no single factor follows it; the C–H stretches shift +43.6 ± 1.5 cm⁻¹ and a factor does almost as well as
the network there.

## 2. Benzene and naphthalene against experiment (reading 3)

Mean / rms in cm⁻¹ over the experimental fundamentals (benzene 20 Wilson modes; naphthalene 48 modes, Martin et al. 1996 via NIST CCCBDB).

| | benzene, all | benzene ring-ip | naphthalene, all | naphthalene CH-oop |
|---|---|---|---|---|
| Mai 2026 scaled − experiment | −15.3 / 22.5 | −24.6 / 28.9 | +1.5 / 15.4 | −1.0 / 8.9 |
| our B3LYP/6-31G* × the PAHdb factors − experiment | −17.2 / 21.3 | −24.3 / 25.0 | −13.3 / 20.2 | −25.3 / 26.9 |
| our CC harmonic − experimental fundamental | +29.3 / 45.4 | +21.5 / 24.0 | +27.0 / 45.5 | −0.6 / 11.7 |
| our CC harmonic − experimental harmonic (benzene, Miani 2000) | −9.2 / 21.1 | **+2.1 / 5.5** | — | — |

- **The anchor, like for like** (benzene CCSD(T)/cc-pVTZ against the harmonic frequencies derived from experiment): the in-plane ring modes
  agree to 5.5 cm⁻¹ rms. The C–H stretches are 38.5 cm⁻¹ low and some out-of-plane modes up to 35 cm⁻¹ off (b2g −35, a2u +22): the first
  most likely comes from the project's convention — the CC Hessian is taken at the B3LYP/6-31G* geometry, whose C–H bonds are a little long: first check (`probes/cc_ch_bond_force.py`, log `probes/results_m1/cc_ch_bond_force_2026-10-25.log`): at the B3LYP geometry (C–H 1.0871 Å) the CCSD(T)/cc-pVTZ force pulls every hydrogen towards its carbon, a first-order shortening of 0.0040 Å — the direction the explanation needs; its size in cm⁻¹ needs the cubic force constants (TASKS 127) — and the second the
  known basis sensitivity of benzene's out-of-plane CC frequencies (R0 read of 22 Sep 2026: "out-of-plane worse", C–H low).
- **Against fundamentals the anharmonicity dominates**: CC harmonic − fundamental is +90 cm⁻¹ on the C–H stretches. A scale factor folds that
  in empirically; our pipeline must add it explicitly (the anharmonic shift, S2/S2b). Harmonic CC alone is not closer to experiment than
  scaled DFT — the CC correction and the anharmonic step belong together.
- **Scaled spectra carry family biases**: Mai's benzene sits −25 cm⁻¹ low in ring-ip (their reliability index in the header of their benzene entry
  hc_c6h6_0pent_1 is JSD 0.309, against a mean of 0.051 in their paper); their naphthalene is good overall (15.4 rms). Our B3LYP/6-31G* with the same factors is 13–17 cm⁻¹ low on
  average: the PAHdb factors belong to the 4-31G basis.

Checks: CC and B3LYP modes paired through the same irrep and rank overlap ≥ 0.92 (eigenvectors); no Mai–B3LYP pair is more than 50 cm⁻¹
apart; two naphthalene pairs flagged as possible crossings; B3LYP/6-31G* benzene's accidental a1g/b1u mix resolved from the projector weights
(1.00/0.00 after resolution). Largest single outlier: naphthalene B1u 753 cm⁻¹, computed near 797 (CC) at both levels — worth a look at the
assignment before it is quoted.

## 3. Mai's teacher on our molecules (reading 2)

Four of our 34 neutral carbon-skeleton molecules are in their benzenoid set (benzene, naphthalene, anthracene, phenanthrene; the others carry
methyl or vinyl groups or five-membered rings). Their unscaled frequencies (B3LYP/4-31G through a learned potential) lie above our analytic
B3LYP/6-31G* by +13.8 / 19.3 cm⁻¹ (mean / rms, 210 modes): CH-oop +23.0, ring-ip +15.1, other +13.8, CH-stretch +1.1. Descriptive, n = 4.

## 4. What it means for the proposal and paper D

1. On the task the network learns, it beats the best scale factor in every family, by 38–88 % of the factor's residual on known scaffolds
   and 33–82 % on unseen ones, and it beats even a factor fitted per family. Ring in-plane modes are where scaling is weakest and the network
   strongest.
2. Against experiment, the honest picture has two parts: a coupled-cluster Hessian is accurate for in-plane ring modes (benzene 5.5 cm⁻¹ rms
   like for like), and the anharmonic step is not optional. The geometry convention (CC Hessian at the B3LYP geometry) costs about −38 cm⁻¹
   on C–H stretches — a known, systematic term the end product has to carry; the first-order geometry term that removes it was validated on 22 Sep 2026 (ledger; `probes/r0_geometry_check_oop.py`: benzene's C–H stretches MAE 52 → 14 against CCSD(T)), so TASKS 127 is about carrying it into the end product, not inventing it.
3. The largest recent library (Mai 2026) reaches 15–23 cm⁻¹ rms on these two molecules after scaling, with family-dependent offsets; that is
   the bar a scale-factor-free pipeline should clear on fundamentals.

Caveats: reading 1 is the proxy task (B3LYP → ωB97X), not experiment; reading 3 rests on two molecules and reading 2 on four; the phase of
Martin's naphthalene fundamentals is not stated on the CCCBDB page.
