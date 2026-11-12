# Barone, Crisci, Mendolicchio, J. Chem. Theory Comput. 22, 7326–7343 (2026) — full text

"Multilevel Fragmentation and Boundary Corrections for Accurate Vibrational Spectra of Large Molecules".
DOI 10.1021/acs.jctc.6c00816, received 26 Apr 2026, published 7 Jul 2026 (p. 7326); not open access (UvA download). Read in full
on 12 Nov 2026 from the local PDF (18 pages, PyMuPDF text; equations are garbled in the extraction and were read from their
variable names and the surrounding text). **The paper cites no Supporting Information** (no "Supporting Information" section;
grep finds none). Gaussian, Inc. funded the work (p. 7341). Journal page = PDF page + 7325.

## Verdict for our claim

- **Nothing is assembled from separately computed fragments.** Every quantity comes from an ONIOM calculation on the **whole
  parent molecule** with one region at high level (p. 7330, eqs 12–18; p. 7329: "ONIOM calculations are performed on the entire
  parent system"). The authors avoid Hessian reconstruction on purpose (p. 7327, p. 7329). The question our idea asks (can a big
  molecule's ΔH be built from pieces computed once and reused?) is not addressed.
- **The "mode-resolved assembly" is a weighted average of two ONIOM harmonic frequency sets** (uridine, eq 32, p. 7338), weights =
  Gaussian's per-mode % model-system character. It is not an assembly of Hessians or of fragment corrections.
- **No PAH.** Systems: benzonitrile (13 atoms), tryptophan (27), uridine (29) (Table 1, p. 7335). The only fused aromatic is indole
  inside tryptophan. The abstract's "30−50 atom range" (p. 7326) is not reached by any test case.
- **No fragment result is checked against a full high-level calculation except benzonitrile**, where the high-level region is the 3
  CN atoms (Table 1). Uridine and tryptophan are compared only with the low level (HPCS2), so their numbers measure how far the
  ONIOM shifts the spectrum, not accuracy (Table 3, p. 7338; p. 7340).
- **Closest to us:** the boundary-bond patch (eqs 30–31, p. 7332): a high-minus-ONIOM force-constant difference in internal
  coordinates, calibrated on a small auxiliary molecule (propionitrile) and transferred to the target (benzonitrile). That is a
  transferred local ΔF element, one coordinate wide. Our claim survives this paper.

## 1. What is done (pp. 7329–7341)

**Levels** (p. 7333): low = HPCS2, B3LYP/6-31+G*; high = DPCS3, revDSD-PBEP86-D3BJ/3F12−. Notation "method 1//method 2" =
harmonic from 1, anharmonic shift from 2 (p. 7329). VPT2/GVPT2 with cubic and semidiagonal quartic constants from finite
differences of analytic Hessians along normal modes, 6N−11 Hessians without symmetry (pp. 7329–7330, p. 7333).

**Effective potential** (p. 7330, eqs 15–18): E_eff = Σ_k E^(k) − (M−1) E_LL, so H_eff = Σ_k H^(k) − (M−1) H_LL: the full molecule at
low level plus M high-minus-low ONIOM corrections, all in the parent's Cartesian space. Generalised with weights a_k (eq 21) and a
**coverage condition** Σ_k a_k = 1 for every local domain u (eq 22, p. 7331); overlaps allowed if weights compensate. The authors
call this "an operational interpretive scheme", not a theorem (p. 7331). Cost: C_LL(N) + M(N)·C_HL(n_f), near-linear for bounded
fragment size (eq 24, p. 7331). Eq 18 is written down but **no application uses M ≥ 2 at Hessian level** (benzonitrile and
tryptophan M = 1; uridine combines frequencies, Table 1).

**Regime 1, one dominant fragment** (p. 7331, eqs 25–27): ONIOM Hessians at displaced geometries give an ONIOM QFF; VPT2 on it.
Used only for benzonitrile (my reading of p. 7331 and Table 2 footnote b). Tryptophan uses ONIOM harmonic + HPCS2 anharmonic shift
(ONIOM//HPCS2, p. 7341).

**Regime 2, two fragments** (p. 7331, eq 28; uridine eq 32): ω_i^dual = (p_i^A ω_i^ONIOM,A + p_i^B ω_i^ONIOM,B)/(p_i^A + p_i^B)
(reconstructed from the extraction; consistent with the stated limit that a mode localised on A gets ω^ONIOM,A). Fundamentals:
ω_i^dual + (ω_i^LL,anh − ω_i^LL,harm) (eqs 29, 33). Justification given: eigenvectors are "significantly more stable" with level than
frequencies (p. 7332). Options named but not used: Cartesian block assembly, internal-coordinate assembly, concordant-mode approach
(refs 36–37) (p. 7331).

**Boundary patch** (p. 7332, eqs 30–31): s_XY = F^HL_XY,XY / F^ONIOM_XY,XY or ΔF_XY,XY = F^HL − F^ONIOM, computed on an auxiliary
molecule at both levels, via Wilson GF analysis from Gaussian outputs (ref 38); applied to the single diagonal stretch element "or,
when needed, the small local block including its strongest couplings" (p. 7332). Normal modes are recomputed and the same cubic and
quartic constants are re-expressed in the new basis (p. 7333). Which form (scaling or additive) was used for benzonitrile is not
stated (p. 7334).

**Fragment choice** is chemical, by hand; automated fragmentation is "outside the scope" (p. 7333).

## 2. Errors against reference

All in cm⁻¹. "Mine" = recomputed by me from Table 2 (script in the session scratchpad, not in the repo).

| Molecule | Quantity | Method | Reference | Number | Page |
|---|---|---|---|---|---|
| uracil (isolated) | harmonic, all modes | HPCS2 | DPCS3 | MAD ≈ 5.7; two highest XH modes ≈ 22, 29; 740−760 region ≈ 20 | 7335, Fig 5 |
| benzonitrile | CN stretch, harmonic | HPCS2 / ONIOM / ONIOM+patch | DPCS3 2261 | 2338 / 2245 / 2264 | 7334, Table 2 |
| benzonitrile | CN stretch, fundamental | HPCS2 / ONIOM / ONIOM+patch | DPCS3 2225, exp 2229 | 2304 / 2204 / 2223 | 7334, Table 2 |
| benzonitrile | 33 fundamentals, MAE | HPCS2 / MultiL / DPCS3 | experiment | 12 / 10 / 6 | 7336, Table 2 |
| benzonitrile | 33 fundamentals, max | HPCS2 / MultiL / DPCS3 | experiment | 75 / 45 / 36 | 7336, Table 2 |
| benzonitrile | 33 harmonic, MAE / max | HPCS2 / MultiL / DPCS3 | experiment | 45 / 43 / 44; 175 / 178 / 181 | 7336, Table 2 |
| benzonitrile | 33 harmonic, MAE / rms / max (mine) | MultiL (patched) | DPCS3 harmonic | 7.73 / 9.93 / 25 | Table 2 |
| benzonitrile | same (mine) | HPCS2 | DPCS3 harmonic | 8.97 / 16.12 / 77 | Table 2 |
| benzonitrile | 33 fundamentals, MAE / rms / max (mine) | MultiL (patched) | DPCS3 fundamentals | 8.12 / 10.86 / 32 | Table 2 |
| uridine | 81 harmonic, MAE, RMS/Max | ONIOM uracil HL | HPCS2 harmonic | 7.10, 9.97/43.41 | 7338, Table 3 |
| uridine | same | ONIOM sugar HL | HPCS2 harmonic | 8.20, 16.47/83.60 | Table 3 |
| uridine | same | weighted dual | HPCS2 harmonic | 7.31, 14.59/83.60 | Table 3 |
| uridine | 81 fundamentals | dual + HPCS2 shift | HPCS2 anharmonic | 7.31, 14.59/83.60 | Table 3 |
| indole (isolated) | harmonic | HPCS2 | DPCS3 | MAD ≈ 6.5, max ≈ 22.4 | 7340 |
| tryptophan | harmonic | ONIOM (indole HL) | HPCS2 | MAD ≈ 4.1, max ≈ 20.4 | 7340 |

Notes. The MultiL MAE of 10 matches the patched CN value (mine: 10.36 patched, 10.94 unpatched). The MultiL maximum of 45 is mode 24,
a CH stretch, 3072 vs 3027 (mine). The two tryptophan correction routes (p. 7340) are described but **no number is reported** for
either. No experiment is compared for uridine or tryptophan.

## 3. Method details that matter for us

- **Correction, not level.** Like our ΔH, everything is low-level full molecule plus high-minus-low corrections (eq 16). The patch is
  also a difference (eq 31). Their anharmonic step for uridine and tryptophan is our step: high-level-ish harmonic plus a low-level
  anharmonic shift (eqs 29, 33).
- **Where the fragmented QFF is shown, the molecule has 13 atoms** and the high-level region 3 atoms (Table 1). No evidence here that
  fragment-level cubic/quartic constants help for larger systems; uridine and tryptophan keep the HPCS2 anharmonicity.
- **Mode matching across two calculations is not described.** Eq 32 pairs "mode i" of two ONIOM runs; the paper says only that there
  are no "significant orientation ambiguities or pathological mode mixing" (p. 7338). My inference: pairing by index, which our E7
  experience says breaks wherever modes reorder.
- **Coverage condition (eq 22)** is the formal statement of our overlap bookkeeping: overlapping pieces need weights so that each local
  domain is counted once. Worth citing when we describe overlapping corpus pieces.
- **Boundary patch = smallest chemically complete auxiliary system** (p. 7332), transferred because the CN stretch is localised
  (p. 7333). Our E9 "parent block + own columns within two bonds" is the many-coordinate version of the same idea (my comparison).
- **Ref 51** (Barone, Lazzari, Di Grande, J. Phys. Chem. A 129, 2876 (2025), "CN-Substituted Polycyclic Hydrocarbons at DFT Cost")
  supplies the DPCS3 benzonitrile data (Table 2 footnote c). It treats polycyclic systems and is not yet in our search.

## 4. Pitfalls that matter for us

- **Link atoms across conjugated bonds.** The residual error sits in the boundary-bond curvature when the cut bond is conjugated or
  polarised (p. 7332); enlarging the HL region "does not necessarily solve the problem" (p. 7332). In a PAH every cut is through an
  aromatic C–C bond, so every boundary is this case (my inference). Size of the defect on one CN boundary: 19 cm⁻¹ harmonic
  (2245 → 2264, p. 7334).
- **Delocalised modes are declared out of scope.** The method needs modes with "a recognizable local character" (p. 7341); for
  delocalised or mixed modes a third fragment or a Hessian-level/internal-coordinate treatment is advised (p. 7327, p. 7338). PAH
  skeletal and CH out-of-plane modes are delocalised over fused rings (my inference), so this paper's frequency-level route would not
  transfer to our targets.
- **ONIOM QFF shifts modes far from the HL region.** Benzonitrile mode 3 (ring CH stretch): harmonic 3192 vs 3195, fundamental 3080
  vs 3040 (HPCS2 vs MultiL, Table 2); modes 11, 21, 22, 33 move 7–12 cm⁻¹ in the fundamental with ≤ 3 cm⁻¹ harmonic change (mine). The
  paper does not discuss this; my inference is resonance handling responding to small QFF changes. For us: a Δ_anh assembled from
  pieces can move resonant bands by tens of cm⁻¹.
- **No accuracy check where it matters.** For the two larger systems no full high-level reference exists (p. 7336), so "agreement" in
  Figs 6–7, 9 means similarity to the low level. A claim of ours must not cite this paper as validation of fragment assembly.
- **Fragment choice is manual and chemical** (p. 7333); no rule for systems without distinct subunits, such as a PAH.

## 5. Check of our report

Report: `reports/Grote PAK uit overlappende fragmenten.md`, grepped for Barone, JCTC, 7326, multilevel.

- **Line 3**, "A second assembles fragment harmonic corrections mode by mode for VPT2": partly wrong. It combines two whole-molecule
  ONIOM frequency sets by mode weights (eq 32, p. 7338); no fragment is computed on its own, and the VPT2 part is a transferred HPCS2
  shift. "Both are closed access and were read as abstracts only": outdated for this paper. The threat to the claim from this paper is
  low (Verdict).
- **Line 5**, "the closed Barone ones above all, are still read as abstracts only": outdated for this paper.
- **Line 41**: the quote "assembled at the frequency level through a mode-resolved combination" is correct (abstract, p. 7326).
  "Multilevel fragmentation for VPT2 of 30–50-atom molecules" repeats the abstract's motivation; the largest test is 29 atoms
  (Table 1). "Transferable boundary-bond correction" holds (eqs 30–31; one bond, propionitrile → benzonitrile). "One molecule
  partitioned ONIOM-style; benzonitrile, tryptophan, uridine; no PAH" holds; add that indole is the only fused aromatic, that only
  benzonitrile has a full high-level reference, and ref 51.
- **Line 79** (open questions): answered here: mode-resolved assembly = eq 32; boundary correction = +19 cm⁻¹ on CN; cm⁻¹ errors in
  §2; no SI exists, so no polycyclic case in an SI.
- **Line 99** ("closed", "none found"): a full text is now held locally (`Papers/Barone_2026_multilevel_fragmentation_boundary_corrections_JCTC22_7326.pdf`).
