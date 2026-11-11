# Bos et al. 2025, "Ethereal AI" — full-text read of the PDF (11 Nov 2026)

Source: `Papers/Bos_2025_ML_scaling_PAH_IR_ACSOmega10_62282.pdf` (local, gitignored), 9 pages = journal pp. 62282–62290.
The text was extracted with PyMuPDF and read whole. Page numbers below are journal pages (p. 62282 = PDF page 1).
**The PDF holds no Supporting Information.** The SI is a set of separate files: "PAHdb-SVR (XLSX), Training (XLSX), Machine
(ZIP), Scripts (ZIP), Inputs (ZIP), Coordinates (TXT)" and a PDF of methodological detail (p. 62287). The molecule list,
the matching details and the predictions for the PAHdb theoretical set are all there, and **none of them was read**.
Pages 62288–62290 are references only.

Builds on `closest_competitors.md` §Bos (lines ~194–237). Items that correct or sharpen those notes or the report are
marked **[CORRECTION]**.

## 1. Molecules, levels, reference data

- **Experimental reference: argon-matrix spectra, not gas phase.** "The PAHdb includes 84 experimental IR spectra taken in
  argon matrices" (p. 62282). The cited data sources (refs 15, 17, 62–73; p. 62287) are the Hudgins/Sandford/Mattioda
  matrix-isolation series: neutral PAHs with 2–4 rings and with 5+ rings, fluoranthene and the benzofluoranthenes, PAH
  cations (the series "through coronene", the polyacenes up to pentacene, chrysene/benz[a]anthracene), PAHs with a
  cyclopentadienyl ring, and nitrogen heterocycles (acridine series, phenazine) (pp. 62289–62290). **No matrix-shift
  correction is applied or discussed anywhere in the paper.** **[CORRECTION]** This answers the notes' gap "Whether
  matrix-isolation shifts were treated": they were not. The notes and the report say "PAHdb experimental bands" / "PAHdb
  experiment" without saying "Ar matrix"; that should be added.
- Whether the cations and nitrogen heterocycles from those sources are among the 465 training/test pairs is not said in
  the main text. The paper calls the whole set "over 80 PAHs" (p. 62287) and points to the SI for "the specific
  identities of the PAHs" (p. 62287). **No molecule names and no sizes appear in the main text.** "Over 80" out of 84
  PAHdb lab spectra means essentially the whole PAHdb laboratory set was used (inference).
- 465 band pairs from 80+ molecules is about 5.8 matched bands per molecule (p. 62287; my arithmetic). Only the
  observable, matchable bands enter, not full mode sets (inference).
- Bands were matched automatically by a custom Python script up to 1590 cm⁻¹ and by hand above it (p. 62287).
- DFT: B3LYP/4-31G in Gaussian 16. Start geometries came from the PAHdb computational entries, then reoptimised
  (p. 62287).
- **The PAHdb three-factor scheme was derived on gas-phase naphthalene** (Bauschlicher 2018), "a departure from their
  previous work using argon-matrix data" (p. 62283). The factors for 4-31G are 0.956 (0–1111.1 cm⁻¹), 0.952
  (1111.1–2500 cm⁻¹) and 0.960 (> 2500 cm⁻¹) (p. 62283). Bauschlicher's own figures for the three-factor scheme with
  B3LYP/4-31G are **MAE 7.8 and max 26.9 cm⁻¹** (p. 62283), against **10.41 / 23.49** on Bos's test set (Table 3).
  So the PAHdb baseline here is a gas-phase-derived scheme scored against Ar-matrix bands (inference: part of its
  14.66 cm⁻¹ mid-region MAE may be this mismatch; the paper does not test this).
- The "NIST scaling" is the CCCBDB factor **0.962 for B3LYP/6-31G**, used because CCCBDB has no entry for 4-31G (p. 62285).

## 2. Results not in the notes

### Model choice (Table 1, p. 62284; test set, cm⁻¹)
| model | RMSE | MAE | max |
|---|---|---|---|
| SVR (linear) | 6.10 | 5.07 | 13.17 |
| elastic net | 6.14 | 5.05 | 14.28 |
| lasso | 6.13 | 5.05 | 14.38 |
| ridge | 6.09 | 4.99 | 14.55 |
| gradient boosting | 8.31 | 5.82 | 35.73 |
| MLP | 19.44 | 13.64 | 66.52 |
| k-NN | 39.64 | 27.16 | 144.15 |
| random forest | 25.59 | 8.45 | 223.36 |
| XGBoost | 115.84 | 31.71 | 798.53 |

- **Ridge has the best RMSE and MAE.** SVR was chosen only because it has the lowest max error, "the most important to
  minimize in this application" (p. 62284). Every nonlinear model is far worse. With 372 training bands, the working
  model is a regularised linear map of five standardised features (inference).
- SVR coefficients on the standardised features (Table 2, p. 62284): frequency 788.26, relative intensity −2.16,
  intensity 0.82, reduced mass 0.41, force constant 0.17. In effect it is an affine rescaling of the frequency with
  corrections of a few cm⁻¹ (inference: the coefficients are in cm⁻¹ per feature SD, so one SD of relative intensity shifts a band by about 2 cm⁻¹, and the other features shift it by less than 1 cm⁻¹).
- Training set: absolute errors up to **18.19 cm⁻¹**, with probability density below 0.025 there (Fig. 3, p. 62284).
  The maximum errors in both sets sit in the C–H stretch region (> 3000 cm⁻¹), "only slightly larger" than the maximum
  below 1650 cm⁻¹ (Figs. 1–2, p. 62284).

### Versus the scale factors, by region (test set, cm⁻¹; Tables 3–6, pp. 62286–62287)
Bands are binned by the experimental wavenumber (p. 62286).

| quantity | region | NIST 0.962 | PAHdb 3 factors | SVR |
|---|---|---|---|---|
| MAE | all | 6.40 | 10.41 | 5.07 |
| MAE | 0–1111.1 | 4.23 | **3.03** | 4.03 |
| MAE | 1111.1–2500 | **3.23** | 14.66 | 4.31 |
| MAE | > 2500 | 14.47 | 10.26 | **7.53** |
| median | all | **3.81** | 10.75 | 4.13 |
| median | 0–1111.1 | 3.76 | **1.97** | 3.88 |
| median | 1111.1–2500 | **2.06** | 15.31 | 3.43 |
| median | > 2500 | 15.16 | 8.72 | **8.08** |
| max | all | 29.92 | 23.49 | **13.17** |
| max | 0–1111.1 | 9.14 | 11.63 | **8.65** |
| max | 1111.1–2500 | 12.15 | 22.60 | **11.75** |
| max | > 2500 | 29.92 | 23.49 | **13.17** |

The overall RMSE is 9.56 / 12.41 / 6.10 and the share of bands > 10 cm⁻¹ is 18.3% / 52.7% / 8.6% (Table 3, p. 62286).

**[CORRECTION / sharpening of the notes and the report]**
- **The SVR wins on mean and median only in the C–H stretch region.** Below 1111 cm⁻¹ the PAHdb three-factor scheme has a
  lower MAE (3.03 vs 4.03) and a lower median (1.97 vs 3.88). In 1111–2500 cm⁻¹ the single NIST factor has a lower MAE
  (3.23 vs 4.31) and a lower median (2.06 vs 3.43). Overall, NIST's median (3.81) beats the SVR's (4.13). The authors
  say so for the median (p. 62285) and for the similar MAEs below 1111 cm⁻¹ (p. 62286).
- The SVR's clear gains are the **maximum error** (all regions) and the **C–H stretch** (MAE at 52% of NIST and 73% of
  PAHdb; p. 62286). The headline "5.07 vs 10.41" is against a scheme that does badly in the mid region (14.66). Against
  a single plain factor the MAE gain is 6.40 → 5.07.
- For our use (fingerprint and low modes, excluding C–H stretch), this paper shows **no mean-error gain over a plain scale
  factor below 2500 cm⁻¹**.
- The notes' sentence "In 1111–2500 cm⁻¹ it is 4.31 (SVR) against 14.66 (PAHdb) and 3.23 (NIST)" is correct, but it
  should say that NIST is the best there. The notes give no figure for 0–1111 cm⁻¹; add 4.03 / 3.03 / 4.23.

### Per molecule, largest molecules
- **There is no per-molecule result and no result by molecule size anywhere in the main text.** No molecule is named in
  the results.
- The trained SVR was applied to "the vast majority" / "almost all of the 4000+" PAHdb theoretical spectra, and the
  predictions are given in the SI (pp. 62284, 62287). **No error figure exists for those predictions.** There is no
  experiment to compare against, and they include molecules far larger than the training set (inference from p. 62283,
  "many systems in PAHdb with hundreds of atoms").

### Methodological caveats seen in the full text
- The split: 80/20, 372/93, "random sampling all portions of the spectrum and from all molecules" (p. 62287). This
  confirms the notes: bands of the same molecule fall in both training and test sets.
- "We standardized the features in both the training and testing partitions" (p. 62287). The text does not say whether
  the test set used the training-set mean and SD. If it used its own, that is a mild leak (inference; check the
  notebook in the SI if it matters).
- There is no cross-validation, no repeated splits and no error bars. All numbers come from one 93-band test set
  (pp. 62284–62287).
- ChatGPT and Gemini assisted with the coding (p. 62287).

## 3. Size transfer, fragments, delocalised and low-frequency modes

- **Size, the only statements:**
  - The abstract claims the approach "shows promise for enabling higher quality predictions on larger systems" (p. 62282).
  - The conclusion says it "could serve to enable consideration of larger compounds than those currently in the PAHdb"
    (p. 62287).
  - The limitations paragraph says the data "are biased toward small PAHs, and therefore, our confidence is stronger for
    small PAHs than for larger systems" (p. 62287). Retraining on more experiments might raise "confidence in the
    extension of our model to larger PAHs and PAHs of more diverse geometries" (p. 62287).
  - **None of these claims is tested.**
- Context sizes given by the authors (p. 62283): the Merrick/Moran/Radom benchmarks reach 10 atoms, VIBFREQ1295 reaches
  14 atoms, naphthalene has 18, and PAHdb holds "many systems ... with hundreds of atoms".
- **Geometry scope:** the data are "dominated by planar systems", with "a small number of slightly nonplanar systems"
  (p. 62287).
- **Fragments:** none. The word appears only in the title of ref 56 (Meng et al. 2023, ML identification of molecular
  fragments responsible for PAH emission features, an interpretation paper), which is not used (p. 62289).
- **Delocalised modes:** no mention.
- **Low-frequency modes:** there is no separate treatment. The lowest bin is 0–1111.1 cm⁻¹, and the PAHdb scheme is best
  there on MAE and median (Tables 4–5). The lower limit of the matched bands is not stated in the main text.
- The authors' method claims (p. 62287):
  - Innovations: ML-derived, per-band ("individualized") scale factors, with reduced mass and force constant as inputs.
  - Scope: "We make no claims ... beyond PAHs or to methodological approaches beyond B3LYP/4-31G".
  - Future work: a "more general set of chemical systems", and the functional and basis set as input variables.

## 4. Checks against the existing notes and the report

Notes (`closest_competitors.md` lines ~194–237), item by item:
- Correct: the bibliographic data; B3LYP/4-31G in Gaussian 16; 465 pairs from "over 80 PAHs"; the five features; nine
  regressors; the 80/20 split of 372/93 from all molecules; the Table 3 figures (RMSE, MAE, max, outliers); the
  > 2500 cm⁻¹ and 1111–2500 cm⁻¹ MAEs.
- **[CORRECTION]** "Nine regressors were compared and linear SVR was chosen": add that **ridge had the better RMSE/MAE
  (6.09/4.99)**. SVR was chosen on max error alone (Table 1, p. 62284).
- **[CORRECTION]** The gap "Whether matrix-isolation shifts were treated" is closed. The reference is Ar-matrix (p. 62282),
  there is no shift correction, and the PAHdb factors it is compared with were fitted on gas-phase naphthalene (p. 62283).
- **[CORRECTION]** "Molecule names and sizes are in the SI, which was not read": still true, but **the SI is not in the
  local PDF**. It is a set of separate XLSX/ZIP/TXT/PDF files on the ACS page (p. 62287).
- The notes' Table 3 should gain the median row (3.81 / 10.75 / 4.13), and the regional comparison should note that
  **SVR is not best on MAE or median below 2500 cm⁻¹** (Tables 4–5).
- The Inference "random splits that leak molecules" is confirmed (p. 62287). "Does not address size transfer at all" is
  confirmed. The only size statements are untested claims and a caveat (p. 62287).

Report (`reports/Grote PAK uit overlappende fragmenten.md`, line 46; the line 138 table row is fine):
- "MAE 5.07 cm⁻¹ against 10.41 for PAHdb's three-factor scaling" is correct as a number. **[CORRECTION, emphasis]**
  - It omits that a single plain factor (0.962) gives MAE 6.40 and median 3.81, which beats SVR's median of 4.13.
  - It omits that the SVR's mean/median advantage lies only in the C–H stretch region.
  - Suggested addition: "against a single 0.962 factor the MAE gain is 6.40 → 5.07 and comes from the C–H stretch; below
    2500 cm⁻¹ a plain factor matches or beats it on mean error (Tables 3–5)".
- "against PAHdb experiment" should be "against PAHdb argon-matrix experiment (no matrix-shift correction)".
- "random over 465 bands from 80+ small-biased PAHs, so molecules leak ... no size test and no fragments" is confirmed.

## 5. Relevance to our question (inference)

- Their errors (RMSE 6.10 cm⁻¹ on a random 93-band test set of small, mostly planar PAHs, against Ar-matrix bands) are
  not comparable to our size-transfer figure: four large PAHs at 36–60 atoms, 22.8 → 7.9 cm⁻¹ rms against the proxy
  reference.
  - They measure interpolation over molecules already seen in training.
  - Their reference is experiment.
  - Only ~6 strong bands per molecule are scored.
- The paper is the scale-factor baseline in ML form. Under our rules it can only ever be a baseline, never an option.
- It gives no evidence of size transfer that a reviewer could set against our approach.
