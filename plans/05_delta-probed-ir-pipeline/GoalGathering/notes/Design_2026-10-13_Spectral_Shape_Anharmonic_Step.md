# Design note, 13 October 2026 — the spectral shape at 30–60 atoms: the anharmonic step, the drawn widths, and what stays out (TASKS 53)

*Written at the user's request (13 Oct 07:1x: 'begin met 1 en 2. Daarna 3'). Desk work; no run is started by this note. Every price below is an
estimate from measured lane times (stated where it comes from) and is to be replaced by a measurement before money is spent: time first.*

## 1. What the goal asks, and what exists

The mandate (13 Sep): a large PAH goes in, a **spectral shape** comes out — positions, intensities, drawn widths — better than the existing
predictions on R4–R6, or with a measured, smaller error budget. The shape is judged by a test fixed on 14 September, before any network
output existed (`PreRegistration_2026-09-14_Shape_Score_Cold_Spectra.md`):
- five molecules with jet-cooled gas-phase spectra: tetracene C₁₈H₁₂, coronene C₂₄H₁₂, peropyrene C₂₆H₁₄, ovalene C₃₂H₁₄, hexa-peri-
  hexabenzocoronene (HBC) C₄₂H₁₈;
- the score: earth mover's distance per family on a 10 cm⁻¹ grid, 550–2000 cm⁻¹, plus the family-weight error;
- the columns: PAHdb scaled harmonic (A), PAHdb anharmonic (B), the public ML model (D), **this pipeline with Δ₂ = 0 (DFT harmonic + DFT
  anharmonic + DFT intensities) — the null column (0)**, and the network (N);
- the winning condition requires N to beat A and D *and* the null column 0 not to: the improvement must be the correction's, not the
  anharmonic step's.

So the test needs a **DFT anharmonic step at 30–60 atoms** in two columns. What exists:

| piece | state | where |
|---|---|---|
| harmonic positions, CC-corrected | the network (v1.1) + T3 transfer; out-of-plane block under test (TASKS 51) | `m05/rungC_cc_transfer.py` |
| double-harmonic intensities | APT with every analytic label (route C, residual-checked); CC APT on anchors (field route) | `corpus/apt.py`, `probes/cc_apt_field.py` |
| GVPT2 on analytic pyscf Hessians | validated on benzene: 851 / 1004 / 1324 cm⁻¹ against the laboratory's 849 / 992 / 1310 (decision 46, 21 Sep) | `src/dpir/qff.py` |
| temperature shift | Σ_k X_ik n̄_k ± 30 % (decision 29) | Ladder §2 |
| hot bands | reported, unscored; benzene's signs failed 0/3 (28 Sep) | `PreRegistration_2026-09-28_Hot_Band_Lines.md` |
| drawn widths | the score's convolution: a Gaussian of FWHM 1 % of ν on both sides (amendment of 14 Sep); the Atlas draws a 10 cm⁻¹ Lorentzian | shape-score note §7; `m05/rungC_intensities.py` |

**The gap is the anharmonic step at scale.** Nothing else in the shape is missing in kind.

## 2. The price of the straightforward route

A semi-diagonal quartic force field needs one analytic Hessian at the reference and two per normal mode (±δq_k): 2M + 1 Hessians, M = 3N − 6.
Symmetry saves the −δq_k Hessian of every mode that is not totally symmetric (H(−δq) = D(g) H(+δq) D(g)ᵀ for an operation g with χ_k(g) = −1),
so the count falls to ≈ M + 1 + n_sym. For these D2h/D6h molecules n_sym is about M/8, so the count is ≈ 0.55 of the full one.

One B3LYP/6-31G* analytic Hessian at the labels settings (grid 99/590), on one 8-thread CCX53 lane: half of the measured lane time for the pair
of Hessians (B3LYP + ωB97X, `probes/results_m1/large_labels_price_2026-10-12/`; ≥ 34 atoms from the t ∝ nbas^3.4 fit, the 10 % optimisation
allowance removed). At ≈ €0.21 per lane-hour (a CCX53 day ≈ €20 for four lanes):

| molecule | atoms | M | one Hessian (lane-h) | Hessians, ± symmetry | lane-hours | ≈ € |
|---|---|---|---|---|---|---|
| tetracene | 30 | 84 | 3.2 (measured, 4 molecules of 30 atoms) | ≈ 96 | ≈ 310 | ≈ 65 |
| coronene | 36 | 102 | 6.6 | ≈ 116 | ≈ 770 | ≈ 160 |
| peropyrene | 40 | 114 | 8.7 | ≈ 130 | ≈ 1,130 | ≈ 240 |
| ovalene | 46 | 132 | 17 | ≈ 150 | ≈ 2,550 | ≈ 535 |
| HBC | 60 | 174 | 42 | ≈ 197 | ≈ 8,300 | ≈ 1,750 |

**≈ €2,750 for the five, more than half of it HBC.** Above 307 basis functions the Hessian time and memory are extrapolated (TASKS 49's
caveat). This route does not fit the mandate's budget. It fits for tetracene, and perhaps coronene.

*Addition, 13 Oct 2026 21:5x (S1 registration, amendment 2).* The Hessian counts are now exact (`probes/qff_symmetry_count.py`): tetracene
100, coronene 109, peropyrene 135, ovalene 156, HBC 192 with the ± saving. A second saving uses the degenerate pairs (one Hessian per pair):
coronene 75, HBC 134. The five then cost €2,157 at R. S1's own timing on benzene puts G at 0.48 and B at 0.69 of R per Hessian, not the
3–5× route (a) below assumed; at G with both savings the five cost ≈ €1,030, HBC ≈ €570 of it. Route (a) alone does not make the five
affordable; it does make the three of S3's validation set cheap (≈ €200 at G).

## 3. Four cheaper routes, and what each must show

**(a) A cheaper level for the anharmonic part only.** The anharmonic shift Δ_anh = ν − ω is a difference of derivatives. Hybrid schemes
(CC harmonic + DFT anharmonic) rest on its being less sensitive to the level than ω itself. The pipeline already uses that split. Candidate
cheaper settings:
- the default grid instead of 99/590;
- 6-31G instead of 6-31G*;
- a larger step δ with fewer points.

If Δ_anh in 550–2000 cm⁻¹ moves by ≤ 1 cm⁻¹ rms under a setting that is 3–5× cheaper, every row of the table drops by that factor. Ovalene would
then cost ≈ €110–180. Measured on naphthalene first (§5, S1).

**(b) A learned per-mode anharmonic shift.** Train a small model of Δ_anh per mode on GVPT2 results of corpus molecules of ≤ 20 atoms, and apply
it to the large ones.
- Inputs: the mode's own description — family, hydrogen share, ring/edge location, ω — the features the corpus already computes.
- Cost per training molecule at the reference level: 0.15–0.8 lane-h per Hessian at 12–20 atoms, so ≈ 6–80 lane-h. Twenty molecules
  ≈ €60–150, less if (a) holds.
- What it must show: on held-out molecules, and then on tetracene against route-A GVPT2, Δ_anh within a line fixed before the read, and
  better than (c).
- The literature on learned anharmonic corrections (Lam et al. 2020, 37 molecules incl. benzene; README line 597) worked on small molecules.
  Transfer to 30–60 atoms is the open question, and tetracene is where it is read.

**(c) Family constants — the baseline to beat.** One Δ_anh per family (C–H stretch, ring, C–H out of plane, other), from the same training set.
Zero extra cost. If (b) does not beat it on held-out molecules, (b) is not built further.

**(d) Reduced-dimensional VPT2.** Displace only along the IR-active modes of the window: about a third of M for these molecules. Not exact: the
χ_ij of an active mode needs cubic constants φ_jjk from displacements along the inactive j and k. The neglected terms would need their own
measurement on tetracene against the full force field. Listed for completeness, not proposed: (a) and (b) are simpler to validate.

**Recommendation:** measure (a) first; build (b) and (c) on the training set at the level (a) licenses; route A only on tetracene (the
validation) and, if (a) passes, on coronene. Ovalene, peropyrene and HBC get the anharmonic step from (b) or (c). The certificate says which,
per molecule.

## 4. Intensities, widths, and what stays out

- **Intensities.** Double harmonic, from the APT. The CC APT term (≈ 20 % on benzene) applies where an anchor exists, and the network's
  out-of-plane shapes follow TASKS 51's outcome. A free extra: route C delivers an APT with every analytic Hessian, so the displaced Hessians
  of a QFF also give the dipole's second derivatives along each mode. That is what GVPT2 needs for the intensities of combination bands and
  overtones. These matter for the family-weight term: PAHdb's anharmonic column puts 14.1 % of tetracene's intensity in the combination
  region (shape-score note §7). For molecules on route A it costs nothing; under (b)/(c) there are no combination bands, and the certificate
  says so.
- **Widths.** Drawn, not computed. The score's own convolution is a Gaussian, FWHM 1 % of ν (14 Sep); the Atlas and certificate draw a
  10 cm⁻¹ Lorentzian. An emission profile for astronomy (temperature-dependent shift and width from the χ_ij and n̄_k, decision 29) is a
  *presentation* option, never scored: jet-cooled absorption is not emission (shape-score note §6).
- **Out of scope, stated:**
  - the 3 µm C–H stretch polyads (Fermi resonances among stretches and bend combinations, Mackie et al. 2015/16): outside 550–2000 cm⁻¹,
    and their treatment needs resonance-polyad methods this plan does not build;
  - any coupled-cluster correction to anharmonic constants (README, the promised deliverable).

## 5. Steps, with what each decides

| step | what | where, cost | decides |
|---|---|---|---|
| **S1** | naphthalene GVPT2 at the reference settings and at two cheaper ones (default grid; 6-31G); time per Hessian printed; Δ_anh per mode in 550–2000 cm⁻¹ against the reference | laptop when the five-ring pool ends (≈ 16 Oct), or a CCX53 lane after the labels; ≈ 50 lane-h reference + ≈ 20–30 for the cheaper two | route (a): the level for every later step |
| **S2** | GVPT2 of ≈ 20 corpus molecules ≤ 20 atoms (families and scaffolds of the training pool, selection rule fixed first); (b) and (c) fitted, read on held-out molecules | after S1, at S1's level; ≈ €30–150 | whether (b) is built further |
| **S3** | tetracene GVPT2 (route A, with symmetry) — the validation of (b)/(c) at 30 atoms; also its combination bands from the displaced APTs; **and our VPT2 beside the published anharmonic spectra of the supervisor's line** (§6) | CCX53, ≈ €65 (or ≈ €15–25 at a level S1 licenses) | the anharmonic column for the five; (b)'s line |
| **S4** | the shape score run for all five, columns 0 and N, with the anharmonic step from the route S3 chose | desk + the large-PAH labels (TASKS 49, chain 42) | the goal sentence's shape clause |

Each step gets its registration (lines, prediction) before its run; S1's line is proposed here as **Δ_anh rms ≤ 1 cm⁻¹ and max ≤ 3 cm⁻¹
against the reference, over the modes in 550–2000 cm⁻¹**. Timeline: S1 this month; S2–S3 in November, after the labels server and beside the
anchor waves; S4 when chain 42's large-PAH labels and the out-of-plane outcome of TASKS 51 are in. This is the stage the supervisor
conversation in November should see as planned and priced, not as done.

## 6. The supervisor's workflow, and the comparison it suggests (added 13 Oct 2026, 13:xx; the user: 'Idee en voorstel akkoord')

Read from the papers she co-authored:
- **2015–2016:** Maltseva, Petrignani et al. (ApJ 2015; arXiv:1510.04948) and Mackie et al. (JCP 143, 224314, 2015; JCP 145, 084313, 2016):
  - anharmonic force constants from Gaussian 09;
  - VPT2 with simultaneous treatment of multiple resonances (polyads within 200 cm⁻¹, Fermi and 1-1/2-2 couplings) in a modified version of
    SPECTRO (Martin et al. 1995);
  - double-harmonic intensities.

  The arXiv text prints the level as "B9-71/TZ2P", presumably B97-1/TZ2P (unconfirmed); the later Mackie line uses B3LYP/N07D.
- **2022:** Wiersma, Candian, Bakker & Petrignani (MNRAS 516, 5216; arXiv:2111.08592):
  - Gaussian 16 rev. C.01;
  - harmonic B3LYP/6-311++G(2d,p), scaled 0.96;
  - anharmonic B3LYP/N07D. The method is not named in the text; Gaussian's built-in VPT2/GVPT2 is the natural reading.
- **SPECTRO is not open source.** It originates with Gaw, Willetts, Green and Handy (1991) and circulates as locally modified copies between
  groups; no public repository or licence was found. We compare against its published results, not its code.

**The comparison (the user agreed, 13 Oct).** S3 puts our VPT2 (`src/dpir/qff.py`, Mills' expressions, polyad deperturbation within 200 cm⁻¹)
beside the anharmonic spectra of the Mackie line for naphthalene, anthracene and tetracene. Those are in PAHdb's anharmonic library v1.00,
already frozen in module 02 as the shape score's column B (tetracene: 3,651 transitions).

What is compared:
- fundamental positions in 550–2000 cm⁻¹, mode by mode;
- the shape score's own read on the cold spectra (tetracene).

Differences to expect and to name, not to tune away:
- level and basis (B3LYP/6-31G* against B97-1/TZ2P or B3LYP/N07D) — S1 measures our side's basis sensitivity;
- their resonance treatment (wider polyads, intensity sharing in later work) against ours.

The supervisor reads this comparison without translation: it is her own reference set.

## 7. Risks named now

- Δ_anh may not transfer from ≤ 20 atoms to 30–60 the way the harmonic correction struggled to (chain 39's size penalty). S3 is the read.
  If (b) fails it, the shape claim for ovalene and HBC carries (c)'s larger error bar, stated.
- The 99/590 grid was chosen for clean finite differences of *Hessians* (decision 46). A coarser grid may bring the noise of 21 September
  back into the cubic and quartic constants. S1 measures exactly that, with the two-route check on the force field (`qff.py`) as the noise read.
- Memory above 307 basis functions is unmeasured (TASKS 49). Coronene's first Hessian is also the memory measurement for S3's sequel.
