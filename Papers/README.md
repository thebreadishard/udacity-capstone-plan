# Literature Papers

Reference PDFs. **Filenames carry their own numbering, which no longer matches plan 03's bibliography**
— plan 03 renumbered from scratch, so its “item 10” is a missing voxel corpus while `10_Meng2023_...` here
is a PAH-charges paper, and its “item 4” is stored as `16_Li2020_...`. Cite by *filename* when you mean a
PDF and by *item number* only inside the plan whose bibliography you are reading.

**This folder is a shared literature dump** (see [`../plans/README.md`](../plans/README.md)).
It is not owned by any plan. Plan 03's bibliography is the index of what the **last written** plan
cites; plan 04 is incoming and will replace 03, so do not treat this dump as already re-indexed for 04.
Items 1–25 were cited by the deleted earlier plans as well; items 26–36 were cited only by plan 02,
and items 16/17/19 were scoped to plan 02's dipole-surface leg. The annotations below therefore
describe each paper's role in the **last written** plan (03). Plan 04 is incoming and has no bibliography yet.

**Updated 2026-08-23:** 15 PDFs retrieved for items 21–24 and 26–36. Every file in this folder was
verified to begin with the `%PDF` signature. **37 PDFs, one gap (item 25, paywalled).** *Count corrected
2026-09-01: the folder holds 37 files; `37_the_hydrogen_molecular_ion_revisited.pdf` was present but
unlisted and does not follow the `NN_FirstAuthorYear_Topic.pdf` convention.*

## ✅ Available (37 papers)

| File | Paper |
|------|-------|
| `01_Ramakrishnan2014_QM9.pdf` | Ramakrishnan et al. (2014) — QM9 dataset. DOI:10.1038/sdata.2014.22 |
| `02_Schutt2017_SchNet.pdf` | Schütt et al. (2017) — SchNet continuous-filter CNN. arXiv:1706.08566 |
| `03_Gastegger2017_MLMD_IR.pdf` | Gastegger et al. (2017) — Machine Learning MD for IR spectra. arXiv:1705.05907 |
| `04_Kaser2021_TransferLearning_CCSDT.pdf` | Käser, Boittier, Upadhyay & Meuwly (2021) — *MP2 Is Not Good Enough: Transfer Learning ML Models for Accurate VPT2 Frequencies*. arXiv:2103.05491, *JCTC*. ⚠️ **This file was right and the bibliography was wrong:** `Relevant_Scientific_Papers.md` item 4 attributed it to "Nandi et al." with a paraphrased title until 2026-08-23. |
| `05_Dral2025_ANI-1ccx-gelu.pdf` | Dral et al. (2025) — ANI-1ccx-gelu universal interatomic potential. ChemRxiv:2024-c8s16 / DOI:10.1021/acs.jpclett.4c03031 |
| `06_NequIP_Equivariant.pdf` | Batzner et al. (2022) — E(3)-equivariant NNPs. arXiv:2101.03164 |
| `07_NewtonNet.pdf` | Haghighatlari et al. (2021) — NewtonNet. arXiv:2108.02913 |
| `08_ApJ2020_HighThroughputPAH.pdf` | Kovács et al. (2020) — High-throughput PAH spectra. DOI:10.3847/1538-4357/abb5b6 |
| `09_Zhu2021_PAH_EmpiricalMapping.pdf` | Zhu/Meng et al. (2021) — PAH emission feature mapping. DOI:10.3847/1538-4357/ac2c78 |
| `10_Meng2023_PAH_Charges_OUP.pdf` | Meng et al. (2023) — ML fragments for PAH IR features. MNRAS Letters slad089 |
| `11_Zakuskin2025_PAH_ChargeModels.pdf` | Zakuskin et al. (2025) — PAH charge model refinement. ACS JCIM |
| `12_Mai2025_MLMD_PAHs.pdf` | Mai et al. (2025) — MLMD meets PAHs. MNRAS staf1156 |
| `13_Fortenberry2025_CN_PAHs.pdf` | Fortenberry et al. (2025) — Vibrational spectra for CN-PAHs. ACS Earth Space Chem |
| `14_ACSomega2025_DFT_Scaling.pdf` | ACS Omega (2025) — ML DFT scaling factors for PAHs |
| `15a_AA2026_JWST_Study1.pdf` | A&A (2026) — JWST application (aa59248-26) |
| `15b_AA2026_JWST_Study2.pdf` | A&A (2026) — JWST application (aa59999-26) |
| `16_Li2020_FourierNeuralOperator.pdf` | Li et al. (2020) — Fourier Neural Operator for Parametric PDEs. arXiv:2010.08895 — core method underpinning the FNO half of the hybrid FNO-NCA architecture |
| `17_Jin2026_V2Rho-FNO.pdf` | Jin et al. (2026) — V2Rho-FNO: Fourier Neural Operator for Electronic Density Prediction. arXiv:2603.15669 — closest prior-art competitor identified in the literature-novelty check (external-potential→density mapping, no MD/forces/spectra) |
| `18_Boersma2014_PAHdb.pdf` | Boersma et al. (2014) — The NASA Ames PAH IR Spectroscopic Database. ApJS 211, 8 — matrix-shift correction reference for gas-phase-vs-matrix-isolation comparisons |
| `19_Mordvintsev2020_GrowingNCA.pdf` | Mordvintsev et al. (2020) — Growing Neural Cellular Automata. Distill, DOI:10.23915/distill.00023 — stabilization techniques (stochastic cell updates, gradient clipping) for the NCA half of the hybrid architecture |
| `20_Dral2025_Aitomia_MLatom.pdf` | Hu, Dral et al. (2025/2026) — Aitomia: Intelligent Assistant for AI-Driven Atomistic and Quantum Chemical Simulations. arXiv:2505.08195 — background on the MLatom platform, cited as an example of the conventional atom-centric NN approach (GNN/element-specific subnetworks) the project explicitly departs from |

### Machine-learned density functionals — items 21–25 (retrieved 2026-08-23)

| File | Paper |
|------|-------|
| `21_Snyder2012_ML_DensityFunctionals.pdf` | Snyder, Rupp, Hansen, Müller & Burke (2012) — Finding Density Functionals with Machine Learning. arXiv:1112.5441, *PRL* 108, 253002 |
| `22_Brockherde2017_BypassingKohnSham.pdf` | Brockherde, Vogt, Li, Tuckerman, Burke & Müller (2017) — By-passing the Kohn–Sham equations with machine learning. arXiv:1609.02815, *Nat. Commun.* 8, 872 |
| `23_Li2021_KS_Regularizer.pdf` | Li, Hoyer, Pederson, Sun, Cubuk, Riley & Burke (2021) — Kohn–Sham equations as regularizer. arXiv:2009.08551, *PRL* 126, 036401 |
| `24_Zhang2024_M-OFDFT.pdf` | Zhang et al. (2024) — M-OFDFT: orbital-free DFT for molecules via deep learning. arXiv:2309.16578, *Nat. Comput. Sci.* |
| *(25 — missing)* | Teller (1962) — On the Stability of Molecules in the Thomas–Fermi Theory. *Rev. Mod. Phys.* 34, 627. **Paywalled**, see below. |

### The R3 evidence base — items 26–36 (retrieved 2026-08-23)

| File | Paper |
|------|-------|
| `26_Kotaru2026_MLP_QFF_VPT2.pdf` | Kotaru, Qu, Nandi, Houston & Bowman (2026) — VPT2 from a machine-learned potential, 21-atom aspirin in ~1 min. arXiv:2604.20040 — **the enabler for R3's nuclear-motion method** |
| `27_Kaser2021_FormicAcid_TL_VPT2.pdf` | Käser & Meuwly (2021) — Transfer-learned PESs: anharmonic dynamics and dissociation energies for formic acid. arXiv:2109.08407, *PCCP* |
| `28_Kaser2023_TL_PES_CCSDT_MD.pdf` | Käser & Meuwly (2023) — Transfer-learned PESs towards microsecond MD at CCSD(T) quality; ~100 high-level points suffice. arXiv:2303.11685, *JCP* 158 |
| `29_Kumar2020_DLPNO_CCSDT_F12_OpenShell.pdf` | Kumar, Neese & Valeev (2020) — DLPNO-CCSD(T)-F12 for open-shell systems with hundreds of atoms. arXiv:2008.03237, *JCP* 153, 094105 — **why a gold rung on PAH cations is a workstation job** |
| `30_Sylvetsky2020_LocalCC_Porphyrins.pdf` | Sylvetsky, Banerjee, Alonso & Martin (2020) — localized CC in a strong-correlation regime. arXiv:2001.08641, *JCTC* 16, 3641 — **the delocalized-π caveat that makes gate G1 a measurement** |
| `31_Tang2025_PyreneCation_AnharmonicIR.pdf` | Tang, Doktor, Jaganathan, Palotás, Oomens, Hornekaær & Hammer (2025) — anharmonic IR of cationic pyrene vs IRMPD. arXiv:2504.11898, *JCP* 163, 044304 |
| `32_Ji2025_DetaNet_IR_Raman.pdf` | Ji, Zhang, Zou, Jiang, Jiang, Luo & Hu (2025) — DetaNet universal force field, IR/Raman from MLMD and RPMD. arXiv:2510.04227 |
| `33_Chen2026_Cyanonaphthalene_Cascade.pdf` | Chen, Li & Li (2026) — anharmonic IR cascade emission of cyanonaphthalenes (VPT2 at B3LYP/N07D). arXiv:2607.20015, *A&A* — **the excitation-model template, and the DFT gap R3 fills** |
| `34_Batatia2022_MACE.pdf` | Batatia, Kovács, Simm, Ortner & Csányi (2022) — MACE. arXiv:2206.07697, *NeurIPS* — selected production architecture (code MIT) |
| `35_Kovacs2023_MACE-OFF.pdf` | Kovács et al. (2023, rev. 2025) — MACE-OFF transferable organic force fields. arXiv:2312.15211 — fallback PES start; **neutral organics only** (ASL weights) |
| `36_Batatia2026_MACE-POLAR-1.pdf` | Batatia et al. (2026) — MACE-POLAR-1 polarisable electrostatic foundation model, OMol25, variable charge **and spin**. arXiv:2602.19411 — **the DMS-tensor leg of the dipole-surface bake-off** |
| `37_the_hydrogen_molecular_ion_revisited.pdf` | *Provenance not recorded.* Added without a bibliography entry and not following the `NN_FirstAuthorYear_Topic.pdf` convention. Not cited by plan 03. Fetch a landing page before citing it anywhere. |

## Source notes

| File | Source used |
|------|-------------|
| `01_Ramakrishnan2014_QM9.pdf` | [Nature Scientific Data PDF](https://www.nature.com/articles/sdata201422.pdf) (open access) |
| `04_Kaser2021_TransferLearning_CCSDT.pdf` | [arXiv preprint](https://arxiv.org/pdf/2103.05491) (published in *JCTC* 2021) |
| `05_Dral2025_ANI-1ccx-gelu.pdf` | [ChemRxiv preprint](https://chemrxiv.org/engage/chemrxiv/article-details/6703551351558a15ef5007a9) (published in *JPCL* 2025) |
| `16_Li2020_FourierNeuralOperator.pdf` | [arXiv PDF](https://arxiv.org/pdf/2010.08895) (open access) |
| `17_Jin2026_V2Rho-FNO.pdf` | [arXiv PDF](https://arxiv.org/pdf/2603.15669) (open access) |
| `18_Boersma2014_PAHdb.pdf` | Manually added by user (NASA ADS / ApJS 211, 8: https://ui.adsabs.harvard.edu/abs/2014ApJS..211....8B) |
| `19_Mordvintsev2020_GrowingNCA.pdf` | Manually added by user (printed/saved from https://distill.pub/2020/growing-ca/ — the article is web-native, no canonical PDF is published) |
| `20_Dral2025_Aitomia_MLatom.pdf` | [arXiv PDF](https://arxiv.org/pdf/2505.08195) (open access) |
| `21`–`24`, `26`–`36` | Batch-retrieved 2026-08-23 from `https://arxiv.org/pdf/<id>` (all open access). Every file verified to start with the `%PDF` signature; sizes 0.28–6.8 MB. |

## ⚠️ Identified but NOT retrieved (paywalled)

Also explicitly named in the chats as literature the design "MUST be built on," but no legitimate open-access copy was found:

| Paper | Why not retrieved | URL |
|---|---|---|
| Lopata & Govind (2011) — "Modeling Fast Electron Dynamics with Real-Time Time-Dependent Density Functional Theory" | Paywalled *JCTC*/ACS article. | https://pubs.acs.org/doi/10.1021/ct200137z (DOI: 10.1021/ct200137z) |
| Teller (1962) — "On the Stability of Molecules in the Thomas–Fermi Theory" (bibliography item 25) | Paywalled *Rev. Mod. Phys.* 34, 627. Pre-arXiv. | DOI: 10.1103/RevModPhys.34.627 |

If you'd rather grab these yourself, the URLs above are the direct/best-known sources.

## Items with no PDF for another reason

| Bibliography item | Why |
|---|---|
| 6 — "E(3)-Equivariant Neural Network Potentials" | Not a single paper; `06_NequIP_Equivariant.pdf` stands in for the family (Batzner et al., arXiv:2101.03164). |
| MACE-OMOL-0, MACE-MP, PolarMACE **checkpoints** | Model weights, not papers. Released on GitHub under the ASL; see bibliography items 34–36 for the method papers. |
