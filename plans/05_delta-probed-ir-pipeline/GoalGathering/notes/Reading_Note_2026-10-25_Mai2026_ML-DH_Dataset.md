# Reading note, 25 October 2026 — Mai, Lu & Wang 2026: 144,111 machine-learned PAH spectra (TASKS 107)

*Read in full (arXiv:2610.21205v1, A&A manuscript of 16 Oct 2026; local copy `Papers/Mai_2026_arXiv_2610.21205_ML-DH_144k_PAH_IR_spectra.pdf`,
text `Papers/_txt/mai2026.txt`). The user, 25 Oct: 'Lees Mai 2026 volledig en werk TASKS 107 uit.' Every number below is the paper's.*

## 1. What they did

- **Model.** A machine-learning double-harmonic (ML-DH) framework: a neural force field (spherical Bessel descriptors + a four-layer
  ResNet; the Madsen/Carrete line) gives energies and forces, the Hessian by automatic differentiation of that potential, geometry
  optimisation by BFGS (≈ 400 steps per molecule, the dominant cost); a charge-conserving message-passing network (EPNN, Metcalf et al.
  2021) gives dipoles, their Cartesian derivatives by finite differences. Separate models for neutral, cation and anion.
- **Teacher and scaling.** B3LYP/4-31G single points in Gaussian 16 on 16,275 conformations (classical MD + Gaussian perturbations of
  651 PAHdb parents from Mai et al. 2025); frequencies scaled with Bauschlicher et al. 2018's factors **0.960 (> 2500 cm⁻¹), 0.952
  (1111–2500), 0.956 (< 1111)**. A 200-molecule check at B3LYP/6-31G(d): force MAE 8.3·10⁻⁴ E_h/bohr, dipole 0.038 D.
- **Product.** 144,111 harmonic spectra of 48,037 closed-shell, even-carbon benzenoid PAHs (C6–C44; 96 % at 35 < N_C < 45) from COMPAS-3
  (80.7 %), COMPAS-1 (17.7 %), COMPAS-2 (1.6 %), each in three charge states, four-membered rings removed; geometries, frequencies,
  intensities and a per-spectrum reliability (the JSD of the nearest validation molecule by ECFP similarity; mean 0.051) on Zenodo
  10.5281/zenodo.21506061; code and trained models on GitHub `zwAstroChem/ML-DH-PAH-IR` (no licence file, checked 25 Oct).
- **Validation, in Jensen–Shannon divergence only — no frequency error in cm⁻¹ anywhere:** vs 5,166 own-level DFT spectra 0.051;
  vs 4,579 PAHdb theoretical spectra 0.107 (neutral 0.098, cation 0.122, anion 0.108; 0.071 within N_C < 45); vs 59 PAHdb experimental
  spectra 0.179 (neutral 0.143, cation 0.212, anion 0.304), the gap to experiment put down to anharmonicity and matrix effects.
- **Cost.** 57 GPU-hours training; 45,492 CPU-hours for the whole library, against 1,637,028 CPU-hours estimated for the same spectra by
  DFT (36×).
- **What they say is missing:** nitrogen-containing PAHs (named as carriers of the 6.2 µm band; 'no carrier attribution attempted'),
  PAHs with N_C > 50 (the 16.4 / 17.4 µm bands), open-shell species, and 'higher levels of theory' (future work).

## 2. Where it stands against this project

| | Mai, Lu & Wang 2026 | this project |
|---|---|---|
| level the spectra rest on | B3LYP/4-31G + three PAHdb scale factors | DFT corrected towards CCSD(T) by a learned Hessian correction; no scale factor (the goal; memory: the scale factor is only ever the baseline) |
| what is learned | the low-level potential and dipole themselves | the high-minus-low correction (Δ), per family block |
| chemistry | benzenoid hydrocarbons only | + aza (N in rings), substituents, five-membered rings, radical cations |
| anharmonicity | none (double harmonic) | the S-series anharmonic step (S1/S2/S2b) |
| error reported as | JSD of spectra | cm⁻¹ per mode family against CC anchors and experiment |
| scale | 48,037 molecules | ~7,800 corpus rows; the network applies to any size |

The two are complementary rather than rival: their library is the scale-factor baseline made as large as it has ever been; ours asks
what that baseline gets wrong and corrects it.

## 3. Positioning text (for the proposal rewrite and paper D)

> The largest PAH infrared library to date (Mai, Lu & Wang 2026; 144,111 spectra of 48,037 benzenoid PAHs) learns B3LYP/4-31G
> potentials and dipoles and keeps the empirical PAHdb scale factors; its error is stated as spectral similarity, not in cm⁻¹, and the
> authors name nitrogen-bearing PAHs and higher levels of theory as missing. We address exactly that step: a network that learns the
> correction from DFT towards CCSD(T) on the Hessian itself, family by family, so that frequencies need no empirical scaling, for
> nitrogen-containing, substituted and cationic PAHs as well as benzenoid ones.

(For the reading copy and the supervisor: this is a record, re-checked against the published A&A version before citing.)

## 4. An external evaluation set — what it can and cannot give us

- **Overlap with our CC anchors** is small: of the eleven carried anchors only benzene and naphthalene are closed-shell benzenoid
  (anthracene's CC Hessian is invalid; quinoline, isoquinoline, quinoxaline, pyridine, benzonitrile, fluorobenzene, azulene and
  acenaphthylene are outside their domain). For those two, their scaled ML-DFT frequencies, our CC anchors and the gas-phase
  experiment can stand side by side per mode — a small but exact cm⁻¹ comparison their paper does not make.
- **Overlap with our corpus**: our benzenoid rows (layers A, A2, B parents and fused hydrocarbons up to ~44 C) can be matched by
  canonical SMILES to their 48,037; where both exist, our analytic B3LYP/ωB97X labels and their scaled 4-31G spectra measure what the
  scale factor hides per family — the gap the network is meant to close.
- **Their 48,037 geometries** are a ready candidate pool for applying our network to unseen benzenoid PAHs at scale (Atlas, module 08).
- **Blocked / to check:** Zenodo refused this machine's requests on 25 Oct ('unusual traffic'), so the data's size and licence are not
  yet known; the GitHub code carries no licence file, so reuse of the code needs the authors' permission — the data alone may suffice.

## 5. Two lessons for our own work

1. **Report cm⁻¹, not only shape metrics.** A JSD of 0.1 hides a few-cm⁻¹ systematic shift per family, which is exactly what our
   correction removes; our claims stay per mode family in cm⁻¹ (decision 53), with a spectral metric only as a second view.
2. **Item 116 (Bhatia, Krejci & Rinke 2026, arXiv:2605.22367; abstract, discussion and conclusions read):** among five message-passing
   potentials on small organic molecules, harmonic-frequency MAE ranges from 2.8 cm⁻¹ (SO3Net) to 7.6 cm⁻¹ (PaiNN), and PaiNN's low
   force error does not carry over to the Hessian — second derivatives are more sensitive than force metrics show; MD-derived spectra
   average this away. This supports module 05's design of predicting the Hessian correction directly instead of differentiating a
   learned energy twice, and it is the reference for why our Hessian-level metrics are the strict ones.
