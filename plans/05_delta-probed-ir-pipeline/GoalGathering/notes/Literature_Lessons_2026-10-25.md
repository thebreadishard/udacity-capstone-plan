# What the literature scan of 25 October 2026 taught us

*One place for the knowledge gained from the October scan (items 112–121 of `GoalGathering/Relevant_Scientific_Papers.md`) and the two
papers read in full the same day. Details and numbers: `Reading_Note_2026-10-25_Mai2026_ML-DH_Dataset.md` and
`Reading_Note_2026-10-25_Vats2026_5-6um_CHoop_Overtones.md`. Each lesson ends with what it changes and the TASKS row that carries it.*

## 1. The field's largest PAH spectra still rest on scaled B3LYP — our gap is real and current

Mai, Lu & Wang (arXiv:2610.21205, 15 Oct 2026) built 144,111 harmonic spectra of 48,037 benzenoid PAHs (C6–C44; neutral, cation,
anion) with a machine-learned force field and dipole model trained on **B3LYP/4-31G**, frequencies **scaled with the PAHdb factors
0.960 / 0.952 / 0.956**; validation in Jensen–Shannon divergence only (0.143 / 0.212 / 0.304 for neutral / cation / anion against 59
matrix spectra), no error in cm⁻¹; no nitrogen, no substituents, no anharmonicity; the authors themselves name heteroatom PAHs and higher
levels of theory as future work. Cost: 45,492 CPU-hours for the library against 1.64 million for the same spectra by DFT.
*Changes:* our novelty statement stands and gains its newest, largest counterpart; the proposal and paper D cite it (TASKS 114). Their
archive (CC BY-NC-SA 4.0) is on disk (TASKS 108) and allows three measurements (TASKS 111–113).

## 2. The 5–6 µm bands are a hidden window on C–H out-of-plane modes — our hardest family

Vats, Mattioda & Ricca (ACS Earth Space Chem. 10, 1685, 2026) show with GVPT2 on B3LYP-D3/N07D and argon-matrix spectra of 27 PAHs and
PANHs that the 2000–1650 cm⁻¹ bands are combinations and overtones of CHoop fundamentals; the upper part comes from CHoop modes at
990–940 cm⁻¹ that are IR-inactive or very weak as fundamentals. Positions agree within 0.15–0.17 % (~3 cm⁻¹); intensities ~45 % off.
N substitution shifts these bands ~10 cm⁻¹ on average, more at bay sites. Their set contains naphthalene, quinoline and isoquinoline —
three of our CC anchors — with all band positions tabulated (Supporting Information, on disk).
*Changes:* a CH-oop error doubles in a combination band, so these positions are a measured test of whether the network learned CH-oop at
CC level — the family our proxy check of 21–22 Oct found hardest (TASKS 110). Band positions, not intensities, are the robust observable.

## 3. Force accuracy does not predict Hessian accuracy

Bhatia, Krejci & Rinke (arXiv:2605.22367, 2026), five message-passing potentials on small organic molecules: harmonic-frequency MAE
2.8 cm⁻¹ (SO3Net) to 7.6 cm⁻¹ (PaiNN), and PaiNN's low force error does not carry over; MD-derived spectra average such errors away.
*Changes:* an external argument for module 05's choice to predict the Hessian (correction) directly rather than differentiate a learned
energy twice, and for keeping our metrics at the Hessian level (TASKS 117).

## 4. Cheap-Hessian pretraining and Hessian losses are becoming standard

Yin et al. (arXiv:2603.25373) pretrain a potential on GFN2-xTB Hessians before fine-tuning; Rodriguez et al. (arXiv:2603.04523) supervise
curvature with projected Hessians at low cost; the Bannwarth group (item 91) predicts Hessian blocks from xTB features. *Changes:* our
proxy-then-anchor scheme is in line with where the field moves; the projected-Hessian loss could cut the cost of our Hessian labels —
read and judge (TASKS 116).

## 5. Report in cm⁻¹ per family, show a spectral metric as a second view

Mai et al. and others judge spectra by JSD or similar shape metrics; a JSD of ~0.1 can hide a systematic few-cm⁻¹ shift per family, which
is exactly what our correction removes. *Changes:* keep decision 53's cm⁻¹-per-family metrics as the claim, and add a JSD view so our
results can be read next to theirs (TASKS 118).

## 6. Smaller lessons

- **Licences matter for reuse:** their data is CC BY-NC-SA 4.0, their code has no licence; Vats et al. is CC BY-NC-ND 4.0. Nothing of
  theirs goes into our CC BY 4.0 mirror or the product repository (TASKS 108, 115).
- **Per-spectrum reliability by nearest neighbour** (Mai et al.: the JSD of the most similar validated molecule) is a cheap uncertainty
  label the Atlas could adopt beside our own error model (TASKS 119).
- **Search snippets misattribute authors:** item 114 was 'Esposito et al.' in the snippets and is Vats, Mattioda & Ricca — every record
  says how much was read, and no citation rests on a snippet.
- **The Mai/Wang group publishes fast** (four PAH-ML papers in 2026); the monthly scan follows them (scheduled task
  `monthly-literature-scan-plan05`).
