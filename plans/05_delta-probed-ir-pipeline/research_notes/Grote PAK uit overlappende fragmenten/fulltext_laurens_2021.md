# Laurens et al. 2021: full-text read

Source: Laurens, Rabary, Lam, Peláez, Allouche, "Infrared spectra of neutral polycyclic aromatic hydrocarbons by
machine learning", arXiv:2010.13686v1 (26 Oct 2020); published Theor. Chem. Acc. 2021, doi 10.1007/s00214-021-02773-6.
Local copy `Papers/Laurens_2021_NN_PAH_frequencies_size_TCA_arXiv2010.13686.pdf`, 13 pages, read whole on 11 Nov 2026.
Page numbers below are the arXiv PDF's. **The supplementary material (Figs. S1–S5: structures, all spectra) is not in
this PDF**; it is cited on p. 2, 6 and 7 only.

Per-molecule numbers marked *(digitised)* were read from the vector bars of Fig. 2 (p. 8) and Fig. 4 (p. 10) with
pymupdf (scale 2.713 pt per cm⁻¹ from the tick labels). The method reproduces the printed 30×30 harmonic set values
(18.3 / 22.1 / 20.0, p. 5 and Table 4) to 0.1 cm⁻¹, and pooling the digitised per-molecule RMSDs with 3N−6 weights
gives 18.3 / 22.2 / 20.0. Scripts: `digitise.py`, `pooled.py` in the session scratchpad (not kept).
Atom counts are ours; the paper gives no formulas. Benzofluorene is read as C17H12 and benzopyrene as C20H12 (Fig. S1
missing); the weighted pooling reproducing the set RMSDs supports that reading weakly.

## 1. Molecules, split, level of theory

- 17 neutral PAHs (p. 2, twice; Fig. 2 has 17 rows, p. 8).
- **Training, 11** (p. 2): naphthalene 18, fluorene 23, phenalene 23, anthracene 24, phenanthrene 24, pyrene 26,
  benzofluorene 29, chrysene 30, corannulene 30, perylene 32, coronene 36 atoms. Range 18–36.
- **Test ("validation set"), 6** (p. 2): tetracene 30, triphenylene 30, benzopyrene 32, benzoperylene 34,
  pentacene 36, ovalene 46 atoms. Range 30–46.
- **The split is not by size, and no criterion is given** (p. 2). Five of the six test molecules lie inside the
  training size range (30–36 atoms; chrysene and corannulene are 30, perylene 32, coronene 36). Only ovalene (46) is
  larger than any training molecule. The test is mainly one of unseen topology (linear acenes, triphenylene), plus one
  size step of 10 atoms.
- Training data (p. 2): optimised geometries, then each atom displaced along x, y, z by ±0.01, ±0.02, ±0.2, ±0.3,
  ±0.5 Å, single points for energies, forces, charges, dipoles. In total 8,863 energies and 735,447 forces (p. 9).
  (Our arithmetic: 295 training atoms × 30 displacements + 11 minima = 8,861, matching the energy count, so each
  configuration has one atom displaced. The ±0.01/0.02 Å sets carry what amounts to finite-difference Hessian columns
  of the training molecules.) 80/20 split of configurations for the fit (p. 3), not of molecules.
- Level: **B3LYP/N07D, Gaussian 09** (p. 2), for training data and for the reference harmonic and GVPT2 frequencies
  (p. 2, §2). The network emulates the same level it is checked against; no higher-level target.
- Model: Behler–Parrinello network in n2p2, two hidden layers of 15, 20 or 30 nodes, tanh, Kalman-filter training
  (p. 2–3). A second network gives atomic charges for the dipole, μ = Σ qᵢ rᵢ (Eq. 4, p. 3). Frequencies: geometry
  optimised on the ANN surface, harmonic Hessian, then QFF by Yagi's numerical scheme and GVPT2 in their iGVPT2 code
  (p. 4).
- Fit quality (Table 3, p. 5): energy RMSD 0.69 / 0.41 / 0.55 meV, forces 59.8 / 51.0 / 45.5 meV/Å for 15×15 / 20×20 /
  30×30.

## 2. Errors against full DFT (B3LYP/N07D)

### Harmonic (Table 4, p. 6; text p. 5; Fig. 2, p. 8)

| Net | All RMSD / MAE | Low ≤ 2000 cm⁻¹ RMSD | High > 2000 RMSD | UMAX | Train RMSD | Test RMSD |
|---|---|---|---|---|---|---|
| 15×15 | 23.5 / 17.8 | 23.6 | 22.7 | 139.7 | 22.6 | 24.7 |
| 20×20 | 21.0 / 15.3 | 21.7 | 15.8 | 102.5 | 19.0 | 23.4 |
| 30×30 | 20.0 / 14.7 | 20.6 | 15.3 | 95.3 | 18.3 | 22.1 |

Train/test values from the text, p. 5. Test/train ratio 1.09 / 1.23 / 1.21. 86–92 % of all frequency errors lie within
±30 cm⁻¹; 50.8 % (15×15) to 60.8 % (30×30) within ±10 cm⁻¹ (p. 5). High (C–H stretch) frequencies are too low in the
ANN, ASE +4.8 to +8.6 cm⁻¹ (p. 5; Table 4: 7.0 / 4.8 / 8.6, with ASE read as DFT − ANN from the text).

Per molecule, 30×30 harmonic RMSD / MAE *(digitised, Fig. 2)*:
- Training: phenanthrene 15.3/11.4, benzofluorene 15.0/11.9, pyrene 15.6/11.9, naphthalene 16.3/11.6,
  phenalene 16.7/12.9, anthracene 16.9/12.8, chrysene 17.6/12.3, fluorene 18.3/13.2, perylene 20.7/13.2,
  coronene 20.8/15.6, **corannulene 23.2/18.3** (worst training molecule).
- Test: benzopyrene 18.2/14.2, benzoperylene 18.5/13.5, tetracene 19.1/15.3, pentacene 23.4/18.2,
  **ovalene 25.1/19.9, triphenylene 25.9/16.5**.
- Ovalene / training set: 25.1 / 18.3 = 1.37×; ovalene / coronene: 25.1 / 20.8 = 1.21×. Triphenylene (30 atoms, the
  size of chrysene) is as bad as ovalene.
- 15×15: worst ovalene 29.3, triphenylene 27.0; 20×20: worst pentacene 31.5 (all digitised).

Worst molecules and the authors' reason (p. 5): "generally the ovalene, the pentacene, and the triphenylene
independently from the considered ANN system". Their stated reason: these "have large structures, and have not been
included in the training database". The figure does not support "large" for triphenylene (30 atoms) or as a
distinction for pentacene (36 = coronene); a training molecule (corannulene, 23.2) is about as bad as pentacene.

### Anharmonic / fundamentals (GVPT2; Table 5, p. 8; text p. 6; Fig. 4, p. 10)

- **Coronene and ovalene are excluded**: "due to technical problems in DFT calculations and due to the consequent
  computational time, we were not able to calculate correctly the fundamental frequencies" (p. 6). So the anharmonic
  test set has **no molecule larger than the training set**; 15 molecules (10 train, 5 test).
- Table 5 (p. 8), all RMSD / MAE: 22.7 / 17.6 (15×15), 22.0 / 17.5 (20×20), 19.8 / 15.0 (30×30). Low ≤ 2000: 23.0 /
  22.1 / 20.4; high: 21.0 / 21.5 / 15.6. High ASE +13.6 / +15.4 / +10.5; low ASE −5.6 / −4.3 / 0.0 (p. 6).
- Text p. 6: training RMSD "22.6 to 19.1 and 18.3 cm⁻¹". **These are the harmonic numbers, and Fig. 4's "All Mol."
  bars are identical to Fig. 2's** (22.6/24.7/23.5, 19.1/23.4/21.0, 18.3/22.1/20.0, digitised), although the
  fundamental set differs (no coronene, ovalene) and Table 5 gives All = 19.8, not 20.0, for 30×30. Pooling the
  digitised per-molecule fundamental RMSDs (3N−6 weights) gives **train 18.7, test 21.5, all 19.8** for 30×30; the 19.8
  matches Table 5. So the paper's printed fundamental train/test split is a copy of the harmonic one; our
  reconstruction is 18.7 / 21.5 (ratio 1.15).
- Per molecule, 30×30 fundamental RMSD *(digitised, Fig. 4)*: worst benzoperylene 27.6 (test), perylene 23.9 (train),
  triphenylene 23.2 (test); pentacene 19.2, tetracene 17.5, benzopyrene 17.8. The authors tie perylene and
  benzoperylene to a "special hexagonal aromatic ring found also in coronene and ovalene which make the DFT
  calculations difficult" (p. 6), i.e. they blame the DFT reference, not the network.

### Other stated limits
- Pentagon-containing molecules "such as the corannulene or the benzofluorene" are "not as well described" (p. 10).
  Fig. 2 supports this for corannulene (23.2, worst training) but not for benzofluorene (15.0, among the best).
- Text p. 5–6 says low frequencies are better predicted than high ones; Table 4 shows the opposite for every net
  (30×30: low 20.6 vs high 15.3). Internal contradiction.
- Speed (p. 8–9, Fig. 6): ~10⁴× faster harmonic, ~10³× anharmonic; corannulene GVPT2 > 142 CPU-days in DFT vs 3 h 40 min
  with the ANN (training cost excluded).

## 3. Locality, fragments, long range

- **No fragment assembly.** The whole molecule is evaluated with the ANN; harmonic frequencies come from the full
  ANN Hessian of the whole molecule (p. 4). Nothing is built from pieces, and no Hessian blocks are transferred.
- Locality is implicit in the Behler–Parrinello form V = Σⱼ Eⱼ(Gⱼ) (p. 2–3): every atomic energy depends only on
  neighbours within **rc = 12.0 Bohr = 6.35 Å**, the same cutoff for all 16 radial and 8 angular symmetry functions
  (Tables 1–2, p. 4); cutoff function tanh³(1 − r/rc) (p. 3). Our inference, not in the paper: a Hessian element
  between atoms i and j can be non-zero only when some atom k has both within 6.35 Å, so the coupling range is
  ≤ 2rc ≈ 12.7 Å, which spans all of ovalene. The model is therefore local in its energy but not truncated in its
  couplings at the sizes tested.
- No long-range term: no electrostatics, no dispersion, no charge equilibration. The dipole network uses the same
  local symmetry functions (p. 4).
- **Not discussed anywhere in the text**: delocalised modes, low-frequency (skeletal, < 500 cm⁻¹) modes as a class,
  long-range couplings, size scaling of the error, or a size limit. "Low" in their tables means ≤ 2000 cm⁻¹, i.e.
  almost every mode. The only remark near the low end is that the ANN spectra "overestimate some satellite peaks below
  500 cm⁻¹" (p. 7), about intensities. The conclusion claims promise "to extrapolate towards larger and more complex
  ones" (p. 10) without a size test beyond ovalene.

## 4. Check of our report (`reports/Grote PAK uit overlappende fragmenten.md`, lines 50 and 52)

| Report claim | Paper | Verdict |
|---|---|---|
| "Only one paper tests frequencies from small to large PAHs against DFT" | The paper cites Kovács, Zhu, Carrete, Madsen, Wang, ApJ 902, 100 (2020), ref. 64, as ML for IR spectra (p. 2). | Not decidable from this paper. **Lead: check Kovács 2020 before keeping "only one".** |
| BP network, 11 PAHs up to coronene (36 atoms) | p. 2–3; coronene is the largest training molecule (36 atoms, our count) | Correct |
| Tested on six others incl. ovalene (46), all B3LYP/N07D | p. 2 | Correct |
| Harmonic RMSD 18.3 train, 22.1 test | p. 5 | Correct, **for the 30×30 net only** (15×15: 22.6 / 24.7). Worth saying which net. |
| Worst on ovalene, pentacene, triphenylene | p. 5; Fig. 2 | Correct as the authors state it. Digitised 30×30: triphenylene 25.9, ovalene 25.1, pentacene 23.4, with training corannulene at 23.2. |
| DFT VPT2 "failed" for coronene and ovalene | p. 6: "technical problems ... and ... computational time" | Correct in substance; cost is part of the reason. |
| **"8 in the abstract, 6 in the methods, 19 in the conclusions"** test molecules | Abstract: 8 large PAHs (p. 1). Methods: 6 (p. 2). Conclusions: "vibrational frequencies of 19 PAH molecules are compared with DFT" (p. 9). | **CORRECTION.** The 19 is the total compared, not the test count. The inconsistencies are: test molecules 8 (p. 1) vs 6 (p. 2, Fig. 2); total molecules 17 (p. 2, Fig. 2) vs 19 (p. 9). |
| Test molecules "barely larger" (46 vs 36, coronene in training) | p. 2; atom counts ours | Supported, and stronger than written: **five of six test molecules are 30–36 atoms, inside the training range; the split is not by size and no criterion is given** (p. 2). Only ovalene is a size step. |
| ~20 cm⁻¹ is a full B3LYP frequency from an MLIP, not a correction | p. 2: the ANN reproduces B3LYP/N07D, checked against the same | Correct. |
| Ratio 22.1/18.3 ≈ 1.2× | p. 5 | Correct for the set. The only true size step, ovalene, is 25.1/18.3 = 1.37× *(digitised)*. |

**Addition the report may want (not a correction):** the anharmonic comparison excludes coronene and ovalene (p. 6),
so it contains no molecule larger than the training set, and the paper's printed fundamental train value (18.3, p. 6;
Fig. 4) is a copy of the harmonic value. Reconstructed from Fig. 4: train 18.7, test 21.5 cm⁻¹ (30×30).

**For our own size argument:** Laurens's error barely depends on size inside the training range (naphthalene 16.3,
coronene 20.8) and their one real size step (36 → 46 atoms) costs 1.21× against coronene. Their test is not a
small-to-large test of the kind ours is (≤ ~30 atoms → 36–60 atoms, four molecules all outside the training range),
and they report no analysis of where the extra error sits (mode class, delocalisation). Their numbers neither support
nor contradict a fragment approach; the paper has no fragment component.
