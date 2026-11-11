# Full-text read: Burger et al., HIP (arXiv 2509.21624)

Read 2026-11-11 from the local PDF `Papers/Burger_2026_HIP_Hessian_prediction_arXiv2509.21624.pdf`, which is
**arXiv v4, 20 Aug 2026** (p. 1 footer), 30 pages including the appendix (A.1–A.6.7, pp. 20–30). The Nature
Computational Science version (10.1038/s43588-026-01066-x) was not read; page numbers below are the PDF's.
Figure values marked "read from figure" were read off a 6× render of Fig. 3c–d; the paper gives no table of
them.

## 1. What HIP predicts and how the Hessian is built

- **Target: the full Cartesian Hessian, 3N × 3N, at ωB97X/6-31G\***, directly, not as a correction to a cheaper
  method and not by differentiating an energy (pp. 2, 5). It is not a Δ-model.
- **Backbone:** EquiformerV2, 4 transformer layers (p. 5), plus one extra Hessian-readout EquiformerV2 layer
  (p. 5); Table 6 (p. 27) lists "Hessian layers: 3 (1 for end-to-end)". Lmax = 4, Mmax = 2, 128 sphere
  channels (Table 6).
- **Blocks:** the Hessian is split into 3 × 3 blocks H_IJ. Diagonal blocks come from node features; off-diagonal
  blocks from the pair message v(h_I, h_J, r_IJ), kept per pair instead of being aggregated (eq. 5, p. 5).
  Each pair feature is projected to one 0e + 1e + 2e irrep set and turned into a 3 × 3 block with
  Clebsch–Gordan coefficients (eq. 6, p. 6); the result is symmetrised, H = H′ + H′ᵀ (p. 6).
- **The features are not local fragments.** h_I and h_J are node features after 4 (+1 to 3) message-passing
  layers over the whole molecule (pp. 5–6), so each block sees a receptive field of several cutoff radii. The
  only locality is that **blocks are built only for pairs within the Hessian cutoff**: pairs beyond it are zero
  (p. 6).
- **Cutoff: 12 Å for both the backbone radius and the Hessian blocks** (Table 6, p. 27). p. 6 says the Hessian
  cutoff "can be set independently of the backbone radius", justified by the sparsity of Hessians (citing
  Kussmann et al. 2015). Cost is O(N²) for small dense systems, O(N) at fixed density for large ones (p. 6).
  For the training molecules (≤ 22 atoms, below) a 12 Å cutoff spans essentially every pair, so in training the
  sparsity is nominal. For our PAHs: coronene (36 atoms), ovalene and HBC are about 10–14 Å across H to H
  (our estimate, not the paper's), so most or all pairs also fall inside 12 Å.
- **No translational sum rule is imposed.** The paper does not mention one; translation and rotation modes are
  explicitly *not* removed during training (p. 25).
- **Not integrable:** a directly predicted Hessian is not guaranteed to be the derivative of any force field
  (pp. 12–13, A.3.1 pp. 22–23).
- **Loss:** element-wise MAE plus a subspace loss on the k = 8 lowest eigenvectors of the reference Hessian,
  weight 1 : 1 (eq. 8, p. 6; eq. 43–44, p. 25). The 8 include the 5–6 near-zero translation and rotation
  modes. The aim is the lowest one or two modes that matter for transition-state search (p. 25).
- **Training data:** HORM (Cui et al. 2026): 1,725,362 training geometries from Transition1x (T1x), 50,844 T1x
  validation geometries, 60,000 HORM-RGD1 geometries kept for size generalisation (p. 7). Labels:
  ωB97X/6-31G\*, GPU4PySCF v1.3.0, analytic PySCF `Hessian()`, closed-shell neutrals, SCF to 1e-10 Eh (p. 7).
  Elements: CHNO (p. 30 for the PubChem set; T1x is CHNO by its source paper). The geometries are mostly off
  equilibrium: a 1,000-geometry validation sample is 44 % first-order TSs, 37 % minima and 19 % higher-order
  saddles (p. 11).
- **Training sizes:** the main text gives no atom-count range for T1x. Fig. 3c's dashed line, "the largest
  molecule size in the training set", sits at **22 atoms** (p. 10, read from figure). Figs. 3a–b and 5 cover
  about 5–21 atoms. The paper does not give a heavy-atom count; Transition1x is GDB7-based (≤ 7 heavy atoms),
  which is outside knowledge, not from this paper.
- **In the main experiments only the Hessian head is trained**; the backbone is frozen, pretrained on energies,
  forces and AD Hessians (p. 7). An end-to-end variant is marked * (Table 1).

## 2. Accuracy and every size-transfer test

**In-distribution (HORM-T1x validation, Table 1, p. 8):**

| Model | H MAE (eV/Å²) | λ MAE (eV/Å²) | cos v1 | λ1 MAE (eV/Å²) | ms |
|---|---|---|---|---|---|
| HIP-EquiformerV2 (head only) | 0.030 | 0.063 | 0.982 | 0.031 | 38.5 |
| HIP-EquiformerV2* (end-to-end) | 0.020 | 0.041 | 0.982 | 0.031 | 31.4 |
| AD-EquiformerV2 (Hessian-trained) | 0.077 | 0.070 | 0.916 | 0.104 | 562.3 |

Table 2 (p. 25, n = 1000) shows loss ablations. With MAE + Sub, H MAE is 0.030, λ MAE 0.063, Eckart-projected
λ1^E 0.031 and λ2^E 0.010, and cos v1^E 0.980.

**Size tests (Section 4.4.1, p. 8; Fig. 3c–d, p. 10; A.6.7, pp. 29–30).** These are the only larger-molecule
tests. The metric is the **MAE of the Eckart-projected, mass-weighted vibrational eigenvalues** in "eV/Å²"
(p. 8, p. 30), paired as the k-th predicted with the k-th reference value. The paper chooses this metric over the
element MAE because element MAE "lead[s] to misleadingly low errors" as most elements go to zero (p. 8).
**No frequency MAE in cm⁻¹, no eigenvector overlap and no per-mode statistics are reported for any size
test.** The unit label is loose: mass-weighted eigenvalues are in eV/(Å² amu).

- **(a) HORM-RGD1, about 10–33 atoms, 60,000 molecules** minus 72 outliers (p. 30). Labels are the published
  ωB97X/6-31G\* ones. Training max is 22 atoms (Fig. 3c, p. 10). HIP eigenvalue MAE, read from figure: ≈ 0.048
  at 10 atoms, ≈ 0.03 from 15 to 29 atoms (including 23–29, beyond the training max), ≈ 0.039 at 30–31,
  ≈ 0.033 at 32 and ≈ 0.02 at 33 atoms. AD is ≈ 0.10–0.14 across the range. **Flat. But the extrapolation
  is only from 22 to 33 atoms, a factor of 1.5.**
- **(b) PubChem CHNO, 30–100 atoms, 710 molecules (10 per atom count, 71 bins)** minus 10 outliers (pp. 8,
  29–30). References: ORCA 6, ωB97X/6-31G(d), analytic Freq **at fixed input geometries**: PubChem 3D
  conformers or RDKit ETKDGv3 + MMFF/UFF, **not DFT-optimised**. Bins without coverage were filled with
  "deterministic RDKit-generated CHNO conformers" (p. 30). HIP eigenvalue MAE, read from figure: **≈ 0.13 at
  30 atoms, ≈ 0.25 at 40, ≈ 0.4 at 60, ≈ 0.5 at 80, ≈ 0.68 at 100.** That is a roughly linear rise of
  about 5× over 30 → 100 atoms. Already at 30 atoms it is ≈ 4× the RGD1 level at the same size (0.13 vs
  0.03–0.04). AD rises from ≈ 2 to ≈ 8.5 over the same range. The text calls HIP's errors "relatively flat"
  (pp. 8 and 10); **that holds only relative to AD.**
- **Rough conversion (our estimate, assuming eigenvalues in eV/(Å² amu)):** ω[cm⁻¹] = 521.4·√λ, so
  δω ≈ 1.36·10⁵·δλ/ω. Under that assumption δλ = 0.03 gives about 4 cm⁻¹ at 1000 cm⁻¹ (20 cm⁻¹ at 200 cm⁻¹),
  and δλ = 0.68 gives about 90 cm⁻¹ at 1000 cm⁻¹. These are eigenvalue errors at non-stationary geometries,
  not frequencies at minima, so they are not comparable with our 7.9 cm⁻¹ rms. They are an order-of-magnitude
  guide only.
- **Composition:** the PubChem set is "neutral organic molecules containing only C, H, N, and O" (p. 29). The
  paper gives **no breakdown by class, aromaticity or ring content, and names no individual molecule.**
  Outliers (10 of 710; 72 of 60,000 on RGD1) were removed by a modified z-score > 10 on the per-molecule
  Hessian MAE. The union across methods was removed, and the outliers are not characterised (p. 30).
- **Aromatic / PAH / > 30 atoms:** **no PAH and no named aromatic test molecule appear anywhere.** Molecules
  above 30 atoms appear only in the anonymous PubChem set. The only named test molecules are glycine
  (Sec. 4.3, pp. 7–9; ωB97X-D3/6-31G(d)) and a C5H6O sample in Fig. 7 (p. 24, qualitative heat map).
- Downstream tests are all on T1x-size molecules: geometry optimisation on 80 geometries (Fig. 4a), ReactBench
  TS search on 960 reactions (Fig. 4b), ZPE on 80 pairs (HIP 0.0004 eV absolute, 0.0016 eV ΔZPE; Fig. 4c,
  Table 3) and extrema classification on 1,000 geometries (92 %, Table 5 "Accuracy All"; Fig. 4d labels it
  87 %) (pp. 10–12, 25–26).

## 3. Delocalised or low-frequency modes, long range, failure cases

- **Low modes:** the paper emphasises only the lowest one or two eigenpairs, for TS search and extrema
  classification (subspace loss, pp. 6, 25; glycine six lowest eigenvalues along the MEP, Fig. 2b, p. 9). Soft
  delocalised modes of large or conjugated molecules (ring breathing, out-of-plane bends, torsions) are
  **not discussed.**
- **Long range:** Limitations, p. 13: "the finite interaction cutoff may omit long-range curvature contributions
  in ionic, polar or extended systems." That is the only statement. There is no test of couplings beyond the
  cutoff, and with a 12 Å cutoff on ≤ 22-atom training molecules no such pair occurs in training.
- **Failure cases:** none are analysed. Outliers are removed silently before averaging (p. 30, see above).
  Non-integrability is discussed as a theoretical limitation (pp. 12–13, A.3.1). Accuracy "depends on the
  chemical and configurational coverage of the training data" (p. 13). Further validation on "broader chemical
  spaces and higher-fidelity electronic-structure methods" is left as future work (p. 13).
- **Relevance to our pieces → whole question:** HIP is a whole-molecule model with a distance cutoff, not an
  assembly from overlapping fragments. Its one >30-atom test shows error **growing roughly linearly with N**
  (30–100 atoms). This is the same qualitative size penalty we see (our 4.4× at 36–60 atoms vs corpus size).
  It is not a counter-example to it.
- Side note: HIP's label level is ωB97X/6-31G\* (p. 7). Whether that matches our ωB97X target depends on our
  basis, which was not checked here.

## 4. Check of our report (`reports/Grote PAK uit overlappende fragmenten.md`)

Report text found by grep:
- l. 48: "HIP predicts Hessians directly as symmetrised 3×3 atom-pair blocks within a message-passing cutoff, so
  a large Hessian is assembled from local pieces by construction ([…arXiv 2509.21624v2]). The journal version
  is said to show flat errors on molecules larger than the training set, but that test could not be found in
  the arXiv text and is unverified."
- l. 81 (open item 6): "Verify the 'flat across system sizes' claim before contrasting with it."
- l. 131: reference row (DOI 10.1038/s43588-026-01066-x, arXiv 2509.21624).

**CORRECTIONS TO THE REPORT:**
1. **The test is in the arXiv text.** v4 (20 Aug 2026) contains it: Sec. 4.4.1 (p. 8), Fig. 3c–d (p. 10) and
   A.6.7 (pp. 29–30). The report cited v2.
2. **"Flat across system sizes" holds only from about 10 to 33 atoms** (HORM-RGD1, training max 22). There HIP's
   eigenvalue MAE stays at ≈ 0.03–0.05 eV/Å² (Fig. 3c). **From 30 to 100 atoms (PubChem CHNO) it is not flat.**
   It rises roughly linearly from ≈ 0.13 to ≈ 0.68, about 5× (Fig. 3d, read from figure). The paper's own
   wording is "relatively flat" (pp. 8, 10), which is true only in comparison with AD Hessians (≈ 2 → 8.5).
   The reference geometries are force-field conformers, not minima, and the metric is eigenvalue MAE, not
   frequency error.
3. **"Assembled from local pieces by construction" overstates the locality.** Blocks exist only within a 12 Å
   cutoff, but every block is computed from whole-molecule message-passing features (4 + 1–3 layers, 12 Å
   radius; pp. 5–6, Table 6). The cutoff covers every pair of a ≤ 22-atom training molecule and most or all
   pairs of a 36–60-atom PAH. HIP does not assemble a Hessian from fragment calculations or fragment
   predictions.
4. Open item 6 can be closed with the above. There is nothing to contrast on PAHs: HIP has no aromatic, PAH or
   named > 30-atom test.

Suggested replacement for the l. 48 sentence (not applied): "HIP predicts the full ωB97X/6-31G\* Hessian as
symmetrised 3×3 blocks for atom pairs within a 12 Å cutoff, from whole-molecule equivariant features. Trained on
molecules of ≤ 22 atoms, its eigenvalue error stays flat to 33 atoms but grows about fivefold from 30 to 100
atoms on PubChem CHNO molecules (Burger et al., arXiv:2509.21624v4, Fig. 3c–d); no PAH was tested."
