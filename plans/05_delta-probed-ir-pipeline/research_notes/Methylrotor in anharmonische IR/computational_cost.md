# Computational cost of methyl-rotor treatments in anharmonic IR prediction, counted in electronic-structure calculations

Notation: N atoms, M = 3N-6 vibrational modes, g = grid points per mode, n_theta = torsion angles, k = active modes.
Reference sizes: 12 atoms (methylimidazole, M = 30), 30 atoms (M = 84), 45 atoms (M = 129).
"[inference]" marks a count derived here from a method's description. It is not a published number.

## Q1. How many electronic-structure calculations does each method need (12-, 30-, 45-atom methyl aromatics)?

### Takeaway
Full semi-numerical VPT2 needs 2M+1 Hessians: 61 / 169 / 259 for 12 / 30 / 45 atoms. A methyl-specific add-on costs much less than that. It is about 12-36 single points for a 1D rotor, 2 extra Hessians to displace only the torsion, n_theta Hessians (about 4-12) for an adiabatic scan, and a few dozen relaxed points for a 2D variational model. Grid-based n-mode VSCF/VCI over all modes is the outlier: about 10^5 single points already at 12 atoms with a 2-mode grid. It is affordable only in reduced dimension, with the torsion plus its coupled partners.

### Cited Findings

**Plain semi-numerical VPT2/GVPT2 (finite differences of analytic Hessians)**
- ORCA VPT2 first computes the Hessian, then generates "two displaced geometries for each degree of freedom" and computes a Hessian at each. These give the cubic and semi-diagonal quartic force field, so the count is 1 + 2M Hessians. The manual calls VPT2 "costly due to the number of calculations required for the numerical derivatives" and "very sensitive to numerical noise". The default `AnharmDisp` is 0.05. — [ORCA 6.1 manual, VPT2](https://www.faccts.de/docs/orca/6.1/manual/contents/spectroscopyproperties/vpt2.html)
- Gaussian Freq=Anharmonic by default makes two displacements per coordinate (TwoPoint). FourPoint "gives better accuracy and less sensitivity to step size at the cost of doing twice as many calculations", which is about 4M+1 Hessians [inference]. The default step is 0.025 Å. The option needs analytic second derivatives (HF, DFT, CIS, MP2). — [Gaussian Freq keyword](https://gaussian.com/freq/)
- Gaussian `SelectAnharmonicModes` "selects which modes are used for differentiation in anharmonic analysis". `DataMod` `SkipPT2=Modes` removes the derivatives with respect to listed modes. `RedDim` sets Active/Inactive/Frozen mode lists. So displacing only k modes costs 2k+1 Hessians. — [Gaussian Freq keyword](https://gaussian.com/freq/)
- Reduced-dimensionality VPT2, in which only a subset of modes is displaced, is studied for large systems (ruthenium carbonyl complexes) by Fusè et al., Spectrochim. Acta A 2024. Its limits are tested first on a smaller model. — [IRIS UniBS record](https://iris.unibs.it/handle/11379/593765) (the PDF returned 403, so the counts in that paper were not read)
- An energy-only QFF (no analytic Hessians) needs "1+2f, 1+6f^2 and 1+6f^2+8f(f-1)(f-2)/6 single point calculations" for 1MR, 2MR and 3MR, with f the number of modes. — [iGVPT2, Allouche, arXiv 1704.02144](https://ar5iv.arxiv.org/html/1704.02144)
- The V30 dimer benchmark uses a default displacement of 0.05 in reduced normal coordinates. Its step-size test moved a large-amplitude frequency from 98 to 57 cm-1 between steps of 0.01 and 0.1. Low-frequency modes are therefore step-sensitive, and a step scan multiplies the Hessian count. — [V30 benchmark, arXiv 2209.04392](https://arxiv.org/html/2209.04392v2)

**Counts for the reference sizes [inference from 2M+1]**

| Molecule | M | Normal-mode VPT2, 2M+1 Hessians | Cartesian central differences, 6N+1 | FourPoint, 4M+1 |
|---|---|---|---|---|
| 12 atoms | 30 | 61 | 73 | 121 |
| 30 atoms | 84 | 169 | 181 | 337 |
| 45 atoms | 129 | 259 | 271 | 517 |

- **Symmetry [inference].** In a Cs methyl aromatic, the +q and -q Hessians of a non-totally-symmetric (a'') mode are mirror images of each other, so each such mode costs one Hessian, not two. The count is then 1 + 2·n(a') + n(a''). For 1-methylimidazole (10 atoms in the plane and 2 methyl H out of it), the mode count is 20 a' + 10 a''. That gives 1 + 40 + 10 = 51 Hessians instead of 61. For a planar-framework molecule the saving is about n(a'') ≈ N/3 Hessians.
- **Torsion only [inference].** Displacing only the torsion t (k = 1) gives every phi_tjk and phi_ttjk for 2 extra Hessians beyond the harmonic one. That is the cheapest way to get the couplings between the torsion and the other modes.

**VPT2 with the torsion decoupled**
- Gaussian supports removing a mode from the PT2 treatment (`SkipPT2=Modes`, `RedDim` Inactive/Frozen) with no extra calculations. — [Gaussian Freq keyword](https://gaussian.com/freq/)
- In the V30 benchmark, decoupled pure rotations are treated as rotors. Modes with significant centre-of-mass motion are decoupled and keep their harmonic value. — [arXiv 2209.04392](https://arxiv.org/html/2209.04392v2)
- [inference] Decoupling costs nothing extra. If the torsion is also left undisplaced, the count drops from 2M+1 to 2(M-1)+1, i.e. 59 / 167 / 257 Hessians.

**1D hindered rotor (scan + Fourier fit + reduced moment of inertia)**
- In the V30 benchmark, the rotor potential is a rigid rotation in steps of 10° followed by "a subsequent CCSD(T)/haQZ single point calculation", fitted by least squares to a Fourier series of the lowest order k that captures the shape. For barriers below 2 kJ/mol (170 cm-1) the 1D Schrödinger equation is solved numerically; otherwise the frequency comes from the curvature at the minimum. — [arXiv 2209.04392](https://arxiv.org/html/2209.04392v2)
- [inference] Over a full 360° turn, steps of 10° / 15° / 30° give 36 / 24 / 12 points. With the methyl's C3 periodicity, 120° is enough: 12 / 8 / 4 points. For V6-dominated toluene-type tops (60° period), 6 / 4 / 2 points. A relaxed scan replaces each single point with a constrained optimisation. I found no published gradient count per constrained optimisation.
- [inference] The reduced moment of inertia (Pitzer, Kilpatrick–Fitter, or Wilson-G) needs only the geometry, so it costs no electronic-structure calculation.
- Gaussian `Freq=HinderedRotor` "requests the identification of internal rotation modes during the harmonic vibrational analysis" and corrects the thermodynamic functions. The keyword documentation states no extra scans or calculations. `ReadHinderedRotor` takes a barrier cutoff, periodicity and symmetry number. — [Gaussian Freq keyword](https://gaussian.com/freq/)
- The method behind it is Ayala & Schlegel, J. Chem. Phys. 108, 2314 (1998). It identifies rotors from redundant internal coordinates, with "no user intervention", by solving a constrained vibrational problem with stretches and bends frozen. The kinetic factor comes from the constrained Wilson G matrix or Kilpatrick–Fitter, and an analytic 1D hindered-rotor partition function reproduces tabulated values within about ±0.4%. — [Ayala & Schlegel record](https://data.zhenzhi.com/details/1/913087463)
- HDCPT2 (Bloino, Biczysko, Barone, JCTC 2012) mixes VPT2 and degeneracy-corrected PT2 and "includes an automatic treatment of internal rotations through the hindered-rotor model". Its target is anharmonic partition functions and thermochemistry. A 2021 review says HDCPT2 so far gives only frequencies; intensities are still under study. — [CNR record of the HDCPT2 paper](https://iris.cnr.it/handle/20.500.14243/238271), via search summary; full text not read

**Torsion-dependent (adiabatic, reaction-path-Hamiltonian style)**
- Methanol (1+11D) in the harmonic adiabatic approximation (HADA; Blasco & Lauvergnat 2003): the torsion is separated from the 11 other modes, which are treated harmonically along the torsional path. The torsional levels differ noticeably from 1D models. — [record](https://ouci.dntb.gov.ua/works/4OAwq3p9)
- Nitric acid (9D; Lauvergnat & Nauts, PCCP 12, 8405, 2010): the torsion is separated adiabatically from the other 8 modes, with the potential expanded to second order along the torsional path (ElVibRot/Tnum). — [UCLouvain record](https://research.dial.uclouvain.be/entities/publication/6b29c7bf-1a1d-43f0-8dbf-17c1a01abc42)
- For toluene, adiabatic separation of the methyl rotation "does not apply" because of strong coupling to other vibrations (PCCP 2008). — [Glasgow eprints 37065](https://eprints.gla.ac.uk/37065). Torsion–vibration coupling is widespread in substituted toluenes. — [Aust. J. Chem. CH23122](https://publish.csiro.au/CH/CH23122)
- [inference] Cost: n_theta constrained optimisations plus n_theta Hessians. With C3 symmetry, 4-7 angles over 0-60° are typical (6-12 over a full period). That is about 4-12 Hessians, independent of M. VPT2 at every angle would cost n_theta·(2M+1) Hessians: 732 / 2,028 / 3,108 for 12 angles.

**Hybrid VPT2 + 2D/3D variational treatment (ENEDIM, DVR)**
- CH3OCH2 radical (8 atoms; Yazidi, Senent, Gámez, Carvajal, arXiv 1905.09506): full-dimensional VPT2 from an MP2 anharmonic force field, plus a 2D variational model of the methyl torsion and CH2 wagging solved with ENEDIM. The 2D PES used "a total number of 32 geometries … for eight different values of the α coordinate … and four values of the H4C3O1C2 dihedral angle", with "16 curvilinear internal coordinates … allowed to be relaxed in all the geometries". It was fitted to a symmetry-adapted Fourier series at RCCSD(T)-F12. A zero-point correction V_ZPVE(θ,α) was "determined at the MP2 level of theory within the harmonic approximation". — [arXiv 1905.09506](https://arxiv.org/pdf/1905.09506)
- [inference] From that recipe: 32 constrained optimisations + 32 high-level single points + 32 harmonic Hessians (for the ZPVE term) + one full VPT2 (2M+1 Hessians). The torsional part is independent of M. A direct-product DVR grid such as 24 × 16 × 16 = 6,144 rigid single points is much more expensive than such a Fourier-fitted relaxed surface. I found no published methyl-aromatic example that uses a direct-product 3D grid.
- One study combines a variational approach with fast-VSCF on an ab initio PES for methyl torsion: validated on a 2D model, applied to methanol. — [Hull repository, Scribano](https://hull-repository.worktribe.com/output/399986), via search summary; counts not read

**Grid-based n-mode VSCF/VCI (MOLPRO SURF, MidasCpp ADGA)**
- On a static grid the number of single points is N_SP = sum over k = 1..n of C(M,k)·g^k. — [Artiukhin et al., GPR-ADGA, arXiv 2303.15188](https://arxiv.org/pdf/2303.15188)
- MOLPRO SURF: `NGRID` (even) sets equidistant points per dimension, default 16. The levels can differ per n-body term (e.g. CCSD(T) 1D, MP4(SDQ) 2D, MP2 3D), and the manual calls SURF calculations "very demanding". — [Molpro 2008 manual, SURF](https://wild.life.nctu.edu.tw/~jsyu/compchem/molpro.2008/manual/node584.html). A 3D term needs 2^3 ab initio points per term per batch, and 2D/3D surfaces usually need 2-3 batches. — [molpro-user list, Rauhut 2017](https://www.molpro.net/pipermail/molpro-user/2017-October/007095.html)
- ADGA (adaptive grid) on a 2M surface: "about 179, 121, 63, 81, and 58 SPs per 2M-cut" for water, formaldehyde, ethylene, imidazole and pyrimidine. For pyrimidine (10 atoms, 24 modes) the reference ADGA needs 16,022 SPs at "normal" thresholds and 33,836 at "extra tight". GPR-ADGA cuts the SP count by up to 68-80% (4-57% for pyrimidine at normal thresholds). With HF single points it is no faster overall, because of VSCF and hyperparameter overhead; with CCSD(F12*)(T) it is about twice as fast. — [arXiv 2303.15188](https://arxiv.org/pdf/2303.15188)
- [inference] Counts for full 2M grids with g = 16: 1M = 16M; 2M = C(M,2)·256. That gives 111,360 + 480 for M = 30, 889,056 + 1,344 for M = 84, and 2,113,536 + 2,064 for M = 129. With about 81 SPs per 2M cut (imidazole ADGA), M = 30 gives 435 × 81 ≈ 35,000 SPs.
- [inference] In reduced dimension, with k active modes on full 1M + 2M grids, the count is k·g + C(k,2)·g². For the torsion plus 2 partners at g = 16 that is 48 + 768 = 816 SPs. For the torsion coupled pairwise to every other mode it is about M·g + (M-1)·g²: 7,904 / 22,592 / 34,880 SPs. A 3D term torsion × 2 partners at 24 × 16 × 16 adds 6,144.

**Machine-learned and low-level surfaces with a high-level correction**
- Δ-ML (Nandi, Qu, Houston, Conte, Bowman, JCP 2021): V_LL→CC = V_LL + ΔV_CC-LL, with the low-level PES a PIP fit to B3LYP/6-31+G(d) energies and gradients. The 12-atom N-methylacetamide correction was trained on 4,696 CCSD(T) energies; small molecules needed as few as about 200. — [arXiv 2011.11601](https://arxiv.org/abs/2011.11601)
- Hybrid force fields (harmonic at a high level, cubic/quartic at a cheaper level) are standard in the Barone/Bloino/Biczysko line. Example: uracil, anharmonic terms by Hessian differentiation at B3PW91-D3(BJ)/jun-cc-pVTZ with a step of 0.01; no counts or timings reported. — [Xu, Yang, Bloino, Biczysko, JPCA 2025](https://pmc.ncbi.nlm.nih.gov/articles/PMC12235615/)

### Inferences
- For a methyl rotor added to a VPT2 pipeline that already runs 2M+1 Hessians, the cheapest physically motivated additions are:
  - 1D rotor (relaxed scan over 120° at 10-15°): 8-12 constrained optimisations plus single points.
  - Torsion-only displacement: 2 Hessians.
  - Adiabatic scan: about 4-12 Hessians.
  - 2D Senent-type model: about 32 relaxed points plus 32 Hessians.
  Each adds 3-50% to a 12-atom budget of 61 Hessians, and less at larger N.
- Grid-based VSCF over all modes costs 10^4-10^6 single points at 12-45 atoms. It is only realistic in reduced dimension (torsion plus a few partners: about 10^3 SPs), or with an ML or low-level surface plus a high-level correction.

### Gaps
- No published Hessian or single-point counts, and no wall times, for any method applied to toluene, methylimidazole, picolines, xylenes or methylnaphthalenes. Lee & Tielens (PCCP 2018) ran VPT2 (SPECTRO) on 9-methyl- and 9,10-dimethylanthracene but report no cost. — [Leiden repository](https://scholarlypublications.universiteitleiden.nl/access/item%3A2946703/download); [arXiv 1802.01497](https://arxiv.org/pdf/1802.01497)
- Barone's 2005 JCP paper (the original 2N+1 semi-numerical GVPT2 scheme) was not fetched. The 2M+1 count rests on the ORCA and Gaussian manual text above.
- The Gaussian documentation does not say whether HinderedRotor or HDCPT2's rotor treatment runs any extra scan. Ayala–Schlegel's barrier estimate was not read in full.
- No published gradient count for a constrained (relaxed-scan) optimisation was found.

## Q2. Which methods scale with the number of methyl groups only, and which with N?

### Takeaway
How many calculations a method needs is fixed by the number of methyl groups only for the torsion-specific add-ons: the 1D rotor scan, the adiabatic Hessians at n_theta angles, and the 2D/3D variational grids. Full VPT2 and grid-based VSCF/VCI scale with M = 3N-6, and the latter with M² or worse. In every method the cost of each calculation still grows steeply with N.

### Cited Findings
- VPT2 needs one Hessian plus two per degree of freedom: linear in M. — [ORCA 6.1 manual](https://www.faccts.de/docs/orca/6.1/manual/contents/spectroscopyproperties/vpt2.html)
- n-mode grid PES: N_SP = sum C(M,k)·g^k, i.e. about M²g²/2 at 2M and about M³g³/6 at 3M. — [arXiv 2303.15188](https://arxiv.org/pdf/2303.15188). An energy-based QFF needs 1+6f² at 2MR and an extra 8f(f-1)(f-2)/6 at 3MR. — [arXiv 1704.02144](https://ar5iv.arxiv.org/html/1704.02144)
- The 1D rotor scan's point count is set by the step and the periodicity (10° steps in the V30 benchmark), not by N. — [arXiv 2209.04392](https://arxiv.org/html/2209.04392v2)
- The 2D torsion-wagging grid is set by the coordinates chosen (32 geometries for CH3OCH2), not by N. — [arXiv 1905.09506](https://arxiv.org/pdf/1905.09506)
- Δ-ML training-set size grew from about 200 CCSD(T) points for small molecules to 4,696 for 12-atom NMA (full-dimensional PES). — [arXiv 2011.11601](https://arxiv.org/abs/2011.11601)

### Inferences
- With n_Me methyl groups (each treated separately) [inference]:

| Method | Calculations for n_Me methyls |
|---|---|
| 1D rotor | n_Me × (4-12) points |
| Torsion-only VPT2 displacement | 2·n_Me Hessians |
| Adiabatic scan | n_Me × n_theta Hessians |
| Coupled 2D rotor-rotor (e.g. o-xylene) | n_theta² points, e.g. 12 × 12 = 144 rigid, or fewer with C3 × C3 symmetry |

- Scaling with N: full VPT2 (2M+1), symmetry-reduced VPT2 (1 + 2n(a') + n(a'')), full-dimensional n-mode VSCF/VCI (M² at 2M), and full-dimensional ML PES training sets (grow with dimension).
- Wall-clock cost per calculation grows with N in every case. With the measured pyscf scaling (about atoms^3.9 per Hessian), a fixed-count method still gets about 30× more expensive per point from 12 to 30 atoms.

### Gaps
- No source compares methyl-count scaling across these methods directly. The classification above is inference from the formulas.

## Q3. Published wall times and Hessian : gradient : energy cost ratios at DFT

### Takeaway
I found no published wall times for anharmonic or rotor treatments of methyl aromatics at B3LYP or ωB97X-D with double-zeta bases. The only concrete VPT2 wall time found is energy-based GVPT2 on GlyGlyH+ at B3LYP/def2-TZVPP: about 110,000 CPU hours. I found no clean published Hessian : gradient ratio either; the ratio is code- and grid-dependent.

### Cited Findings
- iGVPT2: GVPT2 of protonated GlyGlyH+ at B3LYP/def2-TZVPP with ORCA on 2,000 cores at three centres took 56 hours of wall time. "The total CPU time needed for this calculation is about 109888 hours." A hybrid run (B3LYP/def2-TZVPP harmonic, MMFF94 anharmonic) took "only 0.5 hour (6 seconds for third and fourth derivatives)". The wall time of the cubic and quartic step can be divided by about f³ with about f³ cores. — [arXiv 1704.02144](https://ar5iv.arxiv.org/html/1704.02144)
- GPR-ADGA reports wall and CPU times for HF, RI-MP2-F12 and CCSD(F12*)(T) single points in its SI (Sec. S6), not in the main text. — [arXiv 2303.15188](https://arxiv.org/pdf/2303.15188)
- An analytic DFT Hessian "requires second functional derivatives d²Exc/dq² whereas energy and gradient calculations require only first derivatives", and coupled-perturbed equations with an O(N_basis² N_atoms) memory footprint. Finite differences "parallelize trivially". — [Liu, Liu, Herbert, J. Comput. Chem. 38, 1678 (2017)](https://www.asc.ohio-state.edu/herbert.44/reprints/JCC_38_1678.pdf)
- A finite-difference DFT Hessian from analytic gradients needs 6N gradients (central differences); the analytic Hessian solves 3N-6 (or 3N) CP-SCF equations. — [Liu, Liu, Herbert 2017](https://www.asc.ohio-state.edu/herbert.44/reprints/JCC_38_1678.pdf); [KTH eChem, Molecular Hessians](https://kthpanor.github.io/echem/docs/mol_struct/hessians.html)
- ADF (vendor claim): the analytic Hessian "can be up to 3 to 5 times quicker" than the numerical one, depending on molecule, integration grid and basis. — [SCM ADF docs](https://www.scm.com/doc.2022/ADF/Input/Vibrational_Spectroscopy.html), via search summary

### Inferences
- [inference] If ADF's numerical Hessian is 6N gradients, its 3-5× claim puts one analytic Hessian at about 1.2N-2N gradients: about 15-25 gradients at 12 atoms, 35-60 at 30 atoms. A DFT gradient typically costs about 1-2 SCF energies. That is an order-of-magnitude rule; it should be measured in pyscf with the same grid (75/302) rather than taken from the literature.
- [inference] GlyGlyH+ (18 atoms, f = 48): 1 + 6f² + 8f(f-1)(f-2)/6 ≈ 152,000 energies for 109,888 CPU h, which is about 0.7 CPU h per B3LYP/def2-TZVPP energy. The run may not have used the full 3MR count, so this is a rough figure.
- [inference] Wall-clock prices from the measured pyscf Hessian times (114 s at 12 atoms, about 4,000 s at 30 atoms, about 19,400 s at 45 atoms extrapolated with atoms^3.9):

| Method | 12 atoms | 30 atoms | 45 atoms |
|---|---|---|---|
| Full VPT2, 2M+1 Hessians | 61 → 1.9 h | 169 → 188 h | 259 → about 1,400 h |
| Cs symmetry, 12 atoms (51 Hessians) | 1.6 h | — | — |
| Torsion-only add-on (+2 Hessians) | +4 min | +2.2 h | +11 h |
| Adiabatic scan (+12 Hessians, optimisations excluded) | +23 min | +13 h | +65 h |
| 2D model ZPVE (+32 Hessians) | +1 h | +36 h | +170 h |

### Gaps
- No measured Hessian : gradient : energy ratio from a paper for B3LYP/6-31G*-class calculations, and none for pyscf.
- No wall times for methyl aromatics at any level.
- The full texts of the Ayala–Schlegel, HDCPT2 (2012) and Fusè (2024) papers were not read (403 or no access). Their exact counts or timings remain unverified.
