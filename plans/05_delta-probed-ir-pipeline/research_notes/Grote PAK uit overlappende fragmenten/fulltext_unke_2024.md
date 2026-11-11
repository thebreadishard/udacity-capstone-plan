# Unke et al. 2024 (GEMS) — full-text notes

Source: O. T. Unke et al., "Biomolecular dynamics with machine-learned quantum-mechanical force fields trained on diverse
chemical fragments", Sci. Adv. 10, eadn4397 (2024), doi:10.1126/sciadv.adn4397, CC BY 4.0. Local PDF
`Papers/Unke_2024_GEMS_fragments_proteins_SciAdv10_eadn4397.pdf`: 15 article pages + 1 erratum page (p16, 27 Sep 2024).
**The SI (sections S1–S6, figs. S1–S26) is NOT in this PDF**; everything cited to an S-figure below is what the main text says
about it, not read. Read in full on 2026-11-11 (text via PyMuPDF; figs. 3, 4, 7 viewed as rendered images, values marked
"read off the plot" are mine, ±10 %).

Page numbers are the journal's ("p5" = "5 of 15").

## 1. How the fragments are made

- **Principle (p2):** fragments "do not form a partition of the larger system; rather, they can be overlapping pieces, or even
  just be structurally related"; "The fragments are not used directly when evaluating the MLFF, but only during the training
  process". Schematic: Fig. 1A, Fig. 2.
- **Top-down (p3, Fig. 2A; Methods p10):** from an MD snapshot sampled with a *conventional* FF (AMBER99SB-ILDN, GROMACS; p10–11),
  delete all atoms outside a sphere of **8 Å** around a central atom, solvent included. Capping: dangling *single* bonds on heavy
  atoms get H; valences on H atoms or double bonds are removed by pulling the bonded atom from outside the cutoff back in, repeated
  until saturated (method of Gastegger et al. 2017, ref. 27). Different centres give partially overlapping fragments from one
  snapshot (p10).
  - **Atom count per top-down fragment: not stated in the main text** — only the radius (8 Å) and "interatomic distances up to
    18 Å" (p4). The size histogram is fig. S25 (SI, not in PDF). My estimate, not the paper's: an 8 Å sphere of water-density
    matter (≈0.1 atom/Å³) holds ≈200 atoms, consistent with a median PBE0/def2-TZVPP run of 47.4 h on 4 cores (p11).
  - Caveat they state (p10): FF-sampled snapshots can bias the "interaction motifs"; for non-biological systems they suggest
    semi-empirical sampling instead.
- **Bottom-up (p3–4, Fig. 2B; Methods p10):** chemical graphs of **1 to 8 heavy atoms** grown atom by atom, kept only if they
  occur as substructures of the target, H-saturated, 3D by Open Babel; conformers by high-T MD or normal-mode sampling. **2307
  graphs** (≤ 8 heavy atoms) cover all local bonding patterns of proteins from the 20 amino acids incl. protonation states and
  disulfides (p10, from ref. 19). Re-used from the earlier "solvated protein fragments" set (ref. 63), incl. micro-solvated
  structures and bulk water. Bottom-up interatomic distances "below 1 Å to about 12 Å" (p4).
- **Level of theory (p4, p11):** PBE0/def2-TZVPP + MBD, Psi4. Fitted to energies, forces and dipole moments (p11).
- **Data sizes:**
  - 2,713,986 bottom-up structures, shared by all three models (p4, p11).
  - Top-down: **45,948** (polyalanine model), **5624** (crambin model), **129,942** (ACE2/RBD "CoV" model) (p11; crambin 5624 also p4).
  - ≈60 million atomic forces in total (650,000 for S to 37.6 million for H), ≈5 million water molecules (p4); "∼3 million
    DFT+MBD computations" (p9).
  - Cost (p11): up to 20,000 CPU cores; 4-core/32 GB VMs; median ≈48 h per fragment; of "2292 crambin fragments" 120 (5 %)
    failed, 2172 finished, median 47.4 h, mean 50.7 h, 33 took > 4 days; successful runs ≈110,000 core-hours (the paper says
    "compute hours"). Note the paper's own mismatch: 2292 crambin DFT jobs (p11) vs 5624 crambin top-down fragments in training
    (p4, p11) — not explained in the main text.
  - Training: top-down oversampled so that each batch draws equal numbers from bottom-up and top-down (p11); 1–2 weeks on one V100.

## 2. Evaluation on the large system and its errors

- **Evaluation is always on the whole system with one MLFF** (p2; for solvated crambin "a single MLFF to describe all
  (solute-solvent and solvent-solvent) interactions", p12). No fragment assembly at inference.
- **The only quantitative test against the reference on a system larger than the fragments: AceAla15Nme, gas phase (p5–6, Fig. 1B).**
  1554 + 1000 structures (dense and sparse = rare-event regions) from 100 × 250 ps GEMS NVT trajectories at 300 K (25 ns), vs
  PBE0/def2-TZVPP+MBD:
  - GEMS: energy MAE **0.450 meV/atom**, force MAE **36.704 meV/Å**, R² 0.996 (E), 0.998 (F) (p6; also p2).
  - AmberFF for scale: 2.274 meV/atom, 329.328 meV/Å, R² 0.928 / 0.876 (p6); energies mean-shifted before MAE (p6).
  - Bottom-up-only model: errors "much larger" (fig. S8; **no number in the main text**).
  - Size of this test system (my count, not stated): AceAla15Nme = 162 atoms. With 8 Å top-down spheres and fragment distances up
    to 18 Å (p4) against a ~22 Å helix (≈1.5 Å/residue), the test system is only modestly larger than the training cut-outs —
    it is not a test far outside the fragment size.
- **Size series, Fig. 3A (p5):** ΔΔE(n) = ΔE(n) − ΔE(n−1), ΔE = E(α-helix) − E(fully extended) for AceAla_nLys+H⁺, n ≈ 4–20,
  GEMS vs PBE0+MBD. Text: "closely agrees" (p4). **No error numbers given**; read off the plot: ΔΔE runs from ≈−1.5 to −7.5
  kcal/mol, GEMS on top of the reference across n, deviations ≲0.3 kcal/mol. At n = 20 the molecule is ≈230 atoms (my count).
  **No plot or table of error versus system size exists in the main text**; the paper gives no size-dependence of errors.
- **Crambin in water (25,257 atoms, 8205 waters; p3, p6, p12): no ab initio reference at all.** Only comparisons with experiment
  (THz IR, Fig. 7; NMR ensemble, Fig. 1D, figs. S22–S23 — RMSD to the NMR ensemble "agree similarly well" for GEMS and AmberFF, p6)
  and with AmberFF. So there is no energy/force/frequency error for the truly large system.
- ACE2/RBD binding curves (Fig. 9, p10): gas phase, rigid bodies, GEMS binds SARS-CoV-2 vs -1 more strongly than AmberFF by
  ΔΔE = −1.11 eV; no reference, "preliminary and should not be overinterpreted".

## 3. Long-range effects and transfer

- **Architecture: SpookyNet (p2, p11)** with explicit physically-motivated electrostatics and dispersion terms whose parameters are
  learned, an empirical short-range nuclear repulsion, and a mechanism for non-local charge transfer (p2).
- **Cutoffs (p11):** short-range (message-passing) cutoff 10 a₀ ≈ **5.29 Å** for all models. Crambin and CoV models additionally cut
  the analytical electrostatics/dispersion at 20 a₀ ≈ **10.58 Å** "to achieve sub-quadratic scaling"; the polyalanine model has no
  such long-range cutoff stated (by implication all pairs). Crambin model shrunk to T = 3 interaction modules, F = 64 features (vs
  T = 6, F = 128) for GPU memory (p11).
- **Evidence that fragment training transfers, all ablations of the top-down set ("bottom-up only" models):**
  - AceAla15Nme: bottom-up-only model never folds to a helix on the simulated time scale, stays near the extended structure (p5,
    fig. S10); errors "much larger" (p6, fig. S8).
  - AceAla15Lys+H⁺: GEMS helical to 700 K, random coil at 800 K, vs experiment helical to ∼725 K (p4, Fig. 3B); bottom-up-only
    model predicts reduced thermal stability (p4, fig. S12B).
  - Crambin GEMS* (bottom-up only): short-time fluctuations equal GEMS, long-time fluctuations smaller and AmberFF-like (fig. S17B),
    extra cysteine χ1 modes vanish (Fig. 5), ARG17 torsions in between (fig. S18) (p8).
  - Conclusion stated: "a sufficient number of larger fragments are needed to learn long-range effects necessary to generalize to
    larger systems" (p2).
- **Failure cases / limits stated:** top-down fragments are system-specific (p3, p10); FF-sampling bias (p10); 5 % of crambin DFT
  jobs failed (p11); MLFFs "may lead to unphysical dynamics, if not properly trained" — trajectories must be checked for bond
  breaking and distortion (p10); ≈500 ms per MD step for crambin on an A100 vs ≈2 ms for GROMACS (p10); memory limits system size
  (p10); erratum: Fig. 4D and fig. S17B y-axis was downscaled by 1/√3, corrected, conclusions unchanged (p16). No case is shown
  where GEMS fails on the large system, but none of the large-system claims is checked against the reference method either.

## 4. Vibrational content

- **Power spectrum, crambin in water (p6, Fig. 4A):** 125 ps unconstrained MD, 2.5 fs resolution (0.5 fs time step, p12). GEMS peaks
  red-shifted relative to AmberFF and close to experimental water bands (∼1600 and ∼3500 cm⁻¹); AmberFF water peaks blue-shifted
  "several hundreds of wave numbers"; GEMS peaks broader. Gray lines: gas-phase harmonic PBE0+MBD peaks. **No per-mode frequency
  errors, no comparison of GEMS frequencies with PBE0+MBD frequencies of the same system.** Read off the plot: GEMS bend ≈1580,
  AmberFF ≈2080; GEMS stretch ≈3500 (broad), AmberFF ≈3830 cm⁻¹.
- **THz IR spectrum, crambin (p6, p8, Fig. 7; Methods p12):** quasi-harmonic analysis — mass-weighted covariance matrix of the
  water-stripped, aligned protein over 4 × 500,000 frames (2.5 fs); eigenvectors = quasi-normal modes, eigenvalues → frequencies;
  intensity = dipole of the average structure displaced along each mode (amplitude ∝ 1/ω), with 3D-RISM solvent screening to
  3.3 Å; Gaussians of 4 cm⁻¹. The 3.3 Å screening range was chosen because "greater or lesser range was found to obscure the
  features" (p12) — a post-hoc tuned parameter. Experiment (ref. 48) is a partially solvated crambin sample with organic salts, so
  "one cannot expect quantitative agreement" (p8). Claim: GEMS "reproduce[s] most experimentally observed features rather well",
  AmberFF "largely featureless" (p6, p8). No numbers; read off the plot: 170–240 cm⁻¹ main peak GEMS ≈208 vs experiment ≈202 cm⁻¹;
  20–100 cm⁻¹ GEMS maxima ≈50 and ≈92 vs experiment ≈38 and ≈90 cm⁻¹; GEMS rises at < 30 cm⁻¹ where experiment falls.
- **Low-frequency / delocalised modes:** qualitative only. Introduction (p3): empirical FFs give "a smear-out of peak structure and
  an exaggeration of amplitude over the 25 to 150 cm⁻¹ spectral region" (ref. 23); "Low-frequency vibrational modes largely determine
  the free energy of proteins" (p3); long-range interactions "may particularly influence" the low-frequency part (p6); the
  double-well toy model (Eq. 1, Fig. 8, p8–9, p12) argues GEMS has low barriers for large conformational changes. Nothing on
  harmonic normal modes or Hessians of the large system.

## 5. Relevance to our problem (large PAH ΔH/Δω from ≤ 30-atom pieces)

- GEMS is the closest ML precedent for **"train on cut-outs of the target, evaluate the whole"**, i.e. it is our current
  whole-molecule transformer route plus *target-specific capped cut-outs added to training*, not an assembly of a ΔH from piece
  Hessians. The lesson for our 4.4× size penalty: in GEMS the generic small set (≤ 8 heavy atoms) alone gives "much larger" errors
  and wrong long-time physics; adding a few thousand system-specific cut-outs (5624 for crambin, 45,948 for polyalanine) fixes it.
  For us the analogue is capped ≤ 30-atom cut-outs of the four large PAHs themselves in the training set.
- Weaknesses as evidence: the target is a total-energy MLFF at DFT level (not a Δ-correction to a cheaper method); the only
  reference-checked large system is 162 atoms, barely beyond the 8 Å/18 Å fragments; no frequency or Hessian accuracy is reported
  for any system; the explicit long-range terms (learned electrostatics + dispersion, 10.58 Å or no cutoff) carry the non-local
  part, which our ≤ 30-atom-trained transformer has no counterpart for. PAH delocalisation is through-bond π conjugation, not the
  through-space electrostatics/dispersion that GEMS's long-range terms model, so its transfer argument does not carry over directly.

## 6. Check of the report's wording

Grep of `reports/Grote PAK uit overlappende fragmenten.md` (2026-11-11): two hits.

- **Line 50:** "GEMS trains a protein force field on overlapping top-down cut-outs plus small bottom-up graphs, but drops the
  fragments at evaluation". **Correct as far as it goes** (p2: fragments used only in training; p3–4, p10: overlapping 8 Å
  cut-outs + ≤ 8-heavy-atom graphs). **Suggested precision (CORRECTION, by omission):** add that (i) the whole system is evaluated by
  one MLFF with explicit learned electrostatics and dispersion (SpookyNet, 5.29 Å short-range cutoff, 10.58 Å long-range cutoff in
  the crambin model, p11); (ii) the only check against the reference on a larger system is AceAla15Nme (162 atoms, our count):
  0.450 meV/atom and 36.704 meV/Å (p6), and removing the top-down cut-outs makes errors "much larger" and breaks folding (p5–6);
  (iii) the 25,257-atom crambin has no ab initio check, and nothing vibrational is compared with a reference — only a power spectrum
  and a THz IR spectrum against experiment, qualitatively (Figs. 4A, 7). Without (iii) a reader may take GEMS as size-transfer
  evidence for frequencies, which it is not.
- **Line 132 (table):** "not in notes | OA | https://pmc.ncbi.nlm.nih.gov/articles/PMC11809612/". **CORRECTION:** now in notes
  (`research_notes/Grote PAK uit overlappende fragmenten/fulltext_unke_2024.md`). OA confirmed (CC BY 4.0, p1). The PMC ID was not
  checked here (offline); the DOI 10.1126/sciadv.adn4397 is the safe link. The erratum (Sci. Adv. 10, eadt0518, p16) concerns only
  Fig. 4D / fig. S17B scaling.
