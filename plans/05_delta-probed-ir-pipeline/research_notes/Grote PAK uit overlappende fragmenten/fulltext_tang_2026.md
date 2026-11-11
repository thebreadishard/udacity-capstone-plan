# Full-text read: Tang, He, Wang, Qiu (2026), arXiv:2602.12560v1

Title on the PDF: "Graph Neural Network Prediction of Infrared Spectra of Interstellar Polycyclic Aromatic
Hydrocarbons" (astro-ph.GA, 13 Feb 2026). Local copy: `Papers/Tang_2026_PAH_spectra_size_extrapolation_arXiv2602.12560.pdf`.
The PDF has **9 pages, no appendix and no supplementary tables**; pages 8–9 end in the reference list. Read whole
(text extracted with PyMuPDF; Figs 7a/7b rendered at 400 dpi and read off the axes, since the text gives no Fig 7
numbers). Page numbers below are the PDF's printed page numbers. Read on 11 Nov 2026.

## 1. What is predicted, from what, with what model, on which data

- **Target: a whole binned, max-normalised IR absorption spectrum per molecule**, not frequencies, not per-mode
  values, not a Hessian. Spectra are histograms with bin width **18.23 cm⁻¹** (Knuth's rule), **309 bins from 0.21 to
  5603.63 cm⁻¹**; bins past the 308th (5585.49 cm⁻¹) dropped (p. 3, "Dataset"). Each spectrum normalised to its own
  maximum (p. 3); split at the 128th bin into low (0.21–2339.50 cm⁻¹) and high (2339.50–5585.49 cm⁻¹) parts, trained as
  separate outputs (pp. 3–4). Fig 5 overlays use Gaussian broadening, FWHM 10 cm⁻¹ (p. 7, Fig 5 caption).
- **Input: topology only.** Canonical SMILES → RDKit graph; atom features = 11-way element one-hot + degree (12-dim);
  bond features = 4-way one-hot (single/double/triple/aromatic) (p. 4, "Molecular Representation"). "do not
  incorporate 3D geometries or vibrational features" (p. 2).
- **Models:** AttentiveFP (AFP), GAT, GCN, MPNN, plus a learned-fingerprint MFP baseline and their earlier ECFP+MLP
  (Kovács 2020) (pp. 2, 4). AFP: three attention message-passing layers, GRU attention readout to one molecule
  embedding H_mol, linear layer to the spectrum (p. 3, Fig 1 caption). Losses: EMD primary; JSD, HD, TVD, SIS compared
  (p. 4; Table II p. 5). Best reported: AFP+JSD (p. 2 step 3; Table III p. 7, JSD average rank 1.75 in the low region).
  **But the ECFP+MLP baseline beats all five graph models** on validation loss (p. 5, Fig 2) and is "the most reliable
  overall" (p. 5) — the abstract's "AFP ... best overall performance" means best among the GNNs.
- **Data:** PAHdb computational spectra. Training/validation: **1,570 neutral PAHs from PAHdb v3.2, ≤ 47 C**. Size
  test: **997 neutral PAHs from PAHdb v4.0α, 50–100 C** (p. 3, "Dataset"). Level of theory: "Most of the spectra were
  computed via density functional theory at the B3LYP level" (p. 3); the DFT timing comparison is at **B3LYP/4-31G**
  (p. 7, Fig 6 caption). Basis, scaling factor and harmonic-vs-anharmonic status of the reference spectra are not stated.
  Fig 3 caption calls the reference "high-level DFT" (p. 5) — it is B3LYP/4-31G-class PAHdb data.
- **Split by size:** not a cut chosen inside one set; it is **by database version** (v3.2 ≤ 47 C for training,
  v4.0α 50–100 C for testing) (p. 3). Validation split fraction not given; the loss comparison uses 5-fold CV (p. 6).
  **The effective training ceiling is ~34 C, not 47 C:** the Fig 7b inset (p. 8) shows the training-size histogram
  peaking at N_C ≈ 33 (~360 molecules), essentially nothing between 35 and 46, and one small bin near 47. Charge: neutrals
  only (p. 3). Sizes are given in carbons only, no atom counts.
- **Bin-width sensitivity (Table I, p. 3, JSD):** 18.23 cm⁻¹ bins → 0.029 high / 0.097 low; 10 cm⁻¹ → 0.051 / 0.186;
  5 cm⁻¹ → 0.121 / 0.308; lower limit 100 cm⁻¹ instead of 0.21 → 0.030 / 0.102. (Table I labels JSD "(cm⁻¹)"; JSD is
  dimensionless.) The model gets worse as the bins shrink toward a resolution that would test band positions.

## 2. Errors on unseen large molecules vs training size

- **Metric is JSD between normalised binned spectra, never cm⁻¹.** No frequency, band-position or per-mode error is
  reported anywhere in the paper.
- Text: AFP has "low, stable errors" for **N_C 21–34** (p. 8); for **N_C > 40** errors increase "in both spectral
  regions", and "the model should not be applied to astronomical PAHs outside the training domain" (p. 8). MLP: "more
  gradual error increase" (p. 8). Abstract: best for 20–40 C, accuracy decreases for larger (p. 1). Conclusions: reduced
  accuracy above ~40 C, attributed to "limited coverage of current datasets" (p. 8).
- **Fig 7a (AFP, p. 8), read off the axis (±0.01):**
  - training-size bins N_C ≈ 25–34: low-frequency JSD ≈ 0.075–0.13; high-frequency JSD ≈ 0.022–0.03;
  - smallest molecules (N_C ≈ 10–14, few samples): low 0.40–0.71, high 0.33–0.49 — also bad, i.e. error tracks
    training density, not size as such;
  - size test, first bin (just under 50 C): low ≈ 0.13, high ≈ 0.03;
  - size test, N_C ≈ 50–100: **low ≈ 0.23–0.30, high ≈ 0.28–0.39**, flat across 50–100 with wide error bars.
  - Ratio test/training: low-frequency ≈ **2.5–3×**; high-frequency (C–H stretch region) ≈ **10–15×**.
- **Fig 7b (ECFP+MLP, p. 8):** training-size bins low ≈ 0.07–0.15, high ≈ 0.02–0.09; test 50–100 C low ≈ 0.16–0.26,
  high ≈ 0.21–0.43.
- So the error does not grow smoothly with N_C beyond the training range: it jumps between ~34 and ~50 C and then
  plateaus at JSD ≈ 0.3 (Fig 7a). With 18.23 cm⁻¹ bins and per-spectrum max normalisation, a high-region JSD jump can come
  from intensity redistribution as much as from shifted bands; the paper does not separate the two.
- Speed (p. 7, Fig 6): t_GNN ∝ N_C^0.21, t_DFT ∝ N_C^4.18; > 10,000× faster than DFT above ~40 C.

## 3. Fragments, substructures, local environments?

- **No assembly of any kind.** Each molecule's whole spectrum is predicted from one molecule-level embedding (p. 3,
  Fig 1 caption). No fragments, no overlap, no capping, no Hessian or force constants, no assembly-vs-full comparison.
  The only "local" ingredient is the three-layer message passing (p. 3) and the remark that ECFP's fixed-radius circular
  fingerprints "capture local aromatic environments more robustly" and may extrapolate better (p. 5).
- **Low-frequency / delocalised modes: discussed qualitatively only.** Low-frequency modes are "more sensitive to subtle
  chemical environments and long-range interactions"; they "involve collective motions, torsions, and lattice-like
  vibrations that are strongly influenced by long-range couplings and anharmonic effects" (p. 5, Fig 3 discussion, citing
  McGill 2021). Low-frequency errors exceed high-frequency ones overall (p. 5 Fig 3; p. 8 "complex, delocalized
  low-frequency vibrations"). No test isolates long-range coupling or conjugation length.
- Aromaticity of fragments: not discussed (only an "aromatic" bond-type flag, p. 4). Sextets, edge types, cations: not
  analysed.

## 4. Bearing on the report's claims

Report lines checked (grep, 11 Nov): line 50 (the "Only one paper..." paragraph, which also summarises Tang), line 60
(fifth pitfall, long-range couplings, cites Tang), line 135 (reference table: "not in notes").

- **Claim "a fused PAH's Hessian or correction assembled from overlapping PAH pieces and benchmarked against the full
  molecule has not been found": not contradicted.** Tang builds nothing from pieces and works on spectra, not Hessians
  or corrections (§3).
- **Claim "only one paper tests frequencies from small to large PAHs against DFT" (line 50): survives, but only in its
  strict wording.** Tang is a small-to-large test against DFT (≤ 47 C, effectively ≤ ~34 C → 50–100 C, 997 molecules,
  p. 3, Fig 7) — much larger in test count and size ratio than Laurens — but of **binned normalised spectra in JSD**,
  not frequencies in cm⁻¹. Its 18.23 cm⁻¹ bins (p. 3) are coarser than the 7.9 cm⁻¹ rms we need to compare against.
  Suggested wording: "Only one paper reports a small-to-large PAH frequency error in cm⁻¹ against DFT (Laurens 2021);
  Tang 2026 and Mai 2025 test spectra (JSD, intensity RMSE), not frequencies."
- **Line 50's summary of Tang is accurate** (≤ 47 C training, 997 PAHs of 50–100 C, rise above N_C = 40, three
  explanations). Two precisions: (a) the effective training ceiling is ~34 C (Fig 7b inset, p. 8), so "≤ 47 C" overstates
  the training range; (b) the "long-range couplings" quote is the authors' general explanation of low-frequency error
  (p. 5), not their explanation of the size rise, which they blame on data scarcity (pp. 1, 8) and topology-only input
  (pp. 2, 8).
- **CORRECTION to line 60 (fifth pitfall, long-range couplings):** the report cites Tang as evidence that errors "rise
  ... above 40 C in PAH spectrum models" because of long-range couplings. Tang does not support that reading. (i) The
  authors attribute the >40 C rise to scarce training data (abstract p. 1; p. 8; conclusions p. 8), not to long-range
  couplings. (ii) Their own Fig 7a (p. 8) shows the **largest relative degradation in the high-frequency region**
  (JSD ≈ 0.025 → ≈ 0.28–0.39, ~10–15×), which they themselves describe as the localised, C–H-stretch region (p. 8),
  while the low-frequency region degrades only ~2.5–3× (≈ 0.09 → ≈ 0.23–0.30). (iii) Error is equally high for the
  smallest, sparsely-sampled molecules (N_C ≈ 10–14: JSD 0.33–0.71, Fig 7a). This pattern points to a training-density
  / domain effect of a topology-only whole-spectrum model, not to long-range vibrational coupling. Tang should be
  dropped as support for the long-range-coupling pitfall, or cited only for the qualitative statement on p. 5.
- **Reference table, line 135:** "not in notes" can now point to this file. DOI: none given on the PDF (arXiv only).

## Relevance to our size test

Not a like-for-like comparator for our 22.8 → 7.9 cm⁻¹ (4.4× corpus error) result: different target (whole spectrum
vs per-mode Δω correction), different metric (JSD vs cm⁻¹ rms), different input (2D graph vs 3D geometry). What carries
over: a whole-molecule readout trained mostly at 30–34 C loses most accuracy by 50 C and then plateaus (Fig 7a, p. 8);
the authors expect geometry, equivariant message passing or physics priors to help (p. 8). Internal inconsistencies
noted: Fig 1 caption says EMD is the primary loss while the final model uses JSD (pp. 2–3); Table III's caption refers to
"Table 1" for the losses, which are in Table II (p. 7); "five GNN models" includes the non-GNN MFP (p. 4, Fig 2).
