# Contextual Scientific Bibliography

This document captures the relevant scientific papers discussed during the goal gathering phase. This bibliography traces the explicit computational track record of achieving chemically precise infrared spectra for molecules, culminating in the goal of decoding Polycyclic Aromatic Hydrocarbons (PAHs).

## Foundational Quantum Machine Learning
1. **Quantum chemistry structures and properties of 134 kilo molecules** (Ramakrishnan et al., *Scientific Data*, 2014)
   - *Significance:* Introduces the baseline QM9 dataset used extensively for molecular ML training.
2. **SchNet: A continuous-filter convolutional neural network for modeling quantum interactions** (Schütt et al., *NeurIPS*, 2017)
   - *Significance:* Defined the requirement for continuous-filter architectures to ensure PES mathematical smoothness.
3. **Machine Learning Molecular Dynamics** (Gastegger et al., *Chemical Science*, 2017)
   - *URL:* [Machine-learning molecular dynamics](https://pubs.rsc.org/sc/article/8/10/6924/584158/Machine-learning-molecular-dynamics-for-the)
   - *Significance:* Bypassed stationary static derivatives by running MLMD simulations over time.

## Solving Exact Calculus (Chemical Precision)
4. **Transfer Learning to CCSD(T): Accurate Anharmonic Frequencies from Machine Learning Models** (Nandi et al., *JCTC*, 2021)
   - *Significance:* Demonstrated that neural networks *could* extract true CCSD(T)-level second/third derivatives for precise structural mapping using transfer learning.
5. **ANI-1ccx-gelu Universal Interatomic Potential and Its Fine-Tuning: Toward Accurate and Efficient Anharmonic Vibrational Frequencies** (Dral et al., *JPCL*, 2025)
   - *Significance:* The capstone architectural fix. Exchanged standard activation functions for GELU, completely resolving the "wrinkly PES" issue to allow error-free extraction of the Hessian/VPT2 highest-order derivatives.

## Equivariant Neural Networks (The Analytical Hessian Solution)
6. **E(3)-Equivariant Neural Network Potentials** (e.g., NequIP, Allegro)
   - *Significance:* Rather than just ensuring mathematical smoothness via activation functions, these architectures explicitly preserve 3D rotational and translational symmetries. They require significantly less training data than standard continuous-filter models to achieve CCSD(T)-level accuracy when modeling complex PES features.
7. **NewtonNet: A Newtonian Message Passing Network**
   - *Significance:* Distinctly built to be efficiently differentiated to construct analytical Hessians. This provides an alternative structural solution by deriving exact vibrational frequencies orders of magnitude faster than traditional mathematical extraction methods.

## Astrochemical PAH Progress
8. **Early High-Throughput PAH Approximations** (*ApJ*, 2020)
   - *URL:* [High-Throughput Approximations](https://iopscience.iop.org/article/10.3847/1538-4357/abb5b6/meta)
   - *Significance:* Applied standard ML to PAH IR spectra matching (without true chemical quantum precision).
9. **Empirical Mapping of PAH Emissions** (Zhu et al., *ApJ*, 2021)
   - *URL:* [Empirical Mapping](https://iopscience.iop.org/article/10.3847/1538-4357/ac2c78/meta)
   - *Significance:* Interpreted correlations between observed PAH emission features to prioritize target extraction.
10. **Charge/Ionization Awareness** (Meng et al., *MNRAS Letters*, 2023)
   - *URL:* [Ionization Awareness](https://academic.oup.com/mnrasl/article/525/1/L29/7216507)
   - *Significance:* Introduced deep space charge-aware states (anions/cations/neutrals) crucial for mapping shifting PAH IR frequencies.
11. **Refining PAH Charge Models** (Zakuskin et al., *JCIM*, 2025)
   - *URL:* [Refining Charge Models](https://pubs.acs.org/doi/full/10.1021/acs.jcim.5c00372)
   - *Significance:* Implemented deep learning architectures bridging the gap between classical prediction and deep space charge demands.
12. **MLMD Meets PAHs** (Mai et al., *MNRAS*, 2025)
    - *URL:* [MLMD Meets PAHs](https://academic.oup.com/mnras/article/541/4/3073/8206142)
    - *Significance:* Brought the 2017 Gastegger MLMD methodology specifically to complex aromatic systems.
13. **Targeting Cyanated PAHs** (Fortenberry et al., *ACS Earth Space Chem.*, 2025)
    - *URL:* [Targeting CN-PAHs](https://pubs.acs.org/doi/full/10.1021/acsearthspacechem.5c00249)
    - *Significance:* Expanded reference dataset generation to handle astrochemical targets like recently discovered CN-PAHs.
14. **The Pragmatic DFT Scaling Solution** (*ACS Omega*, 2025)
    - *URL:* [Pragmatic Scaling Solution](https://pubs.acs.org/doi/full/10.1021/acsomega.5c10225)
    - *Significance:* Used ML to systematically correct cheap DFT harmonic scaling factors to achieve a 5 cm⁻¹ MAE without massive perturbation overhead.
        
## Cosmic Application
15. **Observational Application to Current JWST Data** (*A&A*, 2026)
    - *URLs:* 
      - [JWST A&A Study 1](https://www.aanda.org/articles/aa/abs/2026/04/aa59248-26/aa59248-26.html)
      - [JWST A&A Study 2](https://www.aanda.org/articles/aa/abs/2026/06/aa59999-26/aa59999-26.html)
    - *Significance:* Armed with mathematically unwrinkled models, researchers directly identify the isotopic makeup of deep space PAHs using live observational astronomy.

## Architecture and Prior Art (PDFs 16–20)
16. **Fourier Neural Operator for Parametric Partial Differential Equations** (Li et al., *arXiv:2010.08895*, 2020)
    - *Significance:* The core method underpinning the FNO half of the hybrid FNO-NCA architecture.
17. **V2Rho-FNO: Fourier Neural Operator for Electronic Density Prediction** (Jin et al., *arXiv:2603.15669*, 2026)
    - *Significance:* Closest prior art identified in the original novelty check — external-potential → density mapping, with none of the MD / force / spectral machinery. **Note:** it is *not* the closest prior art overall; see the density-functional lineage below, which the original check missed.
18. **The NASA Ames PAH IR Spectroscopic Database** (Boersma et al., *ApJS* 211, 8, 2014)
    - *Significance:* Matrix-shift correction reference for gas-phase vs matrix-isolation comparisons.
19. **Growing Neural Cellular Automata** (Mordvintsev et al., *Distill*, 2020, DOI:10.23915/distill.00023)
    - *Significance:* Stabilization techniques (stochastic cell updates, gradient clipping) for the NCA half of the hybrid architecture.
20. **Aitomia: Intelligent Assistant for AI-Driven Atomistic and Quantum Chemical Simulations** (Hu, Dral et al., *arXiv:2505.08195*, 2025)
    - *Significance:* Background on the MLatom platform; cited as an example of the conventional atom-centric NN approach this project departs from.

## Machine-Learned Density Functionals — the lineage this thesis actually sits in

Added 2026-08-22 to close [round-2](Professor_Review_2026-08-22_Round2.md) blocking issue 9. The Distilled Plan's \(E=E_{\mathrm{es}}[\rho]+\int\varepsilon_\theta\,dV\) **is** machine-learned orbital-free DFT. Positioning against this lineage is in Distilled Plan §2.1.

21. **Finding Density Functionals with Machine Learning** (Snyder, Rupp, Hansen, Müller & Burke, *Phys. Rev. Lett.* 108, 253002, 2012)
    - *URL:* [arXiv:1112.5441](https://arxiv.org/abs/1112.5441) · DOI:10.1103/PhysRevLett.108.253002
    - *Significance:* Origin of the field. Machine-learns the kinetic-energy functional for 1D non-interacting fermions and confronts the functional-derivative problem — the same derivative this plan obtains by autograd.
22. **By-passing the Kohn–Sham equations with machine learning** (Brockherde, Vogt, Li, Tuckerman, Burke & Müller, *Nature Communications* 8, 872, 2017)
    - *URL:* [arXiv:1609.02815](https://arxiv.org/abs/1609.02815) · DOI:10.1038/s41467-017-00839-3
    - *Significance:* **The closest functional prior art to Route B.** Learns the density–potential *and* energy–density maps directly, then reproduces energies across geometries generated by molecular dynamics. That is \(\mathbf{R}\to\rho\to E\) plus MD — this plan's pipeline, at DFT label quality.
23. **Kohn–Sham equations as regularizer: building prior knowledge into machine-learned physics** (Li, Hoyer, Pederson, Sun, Cubuk, Riley & Burke, *Phys. Rev. Lett.* 126, 036401, 2021)
    - *URL:* [arXiv:2009.08551](https://arxiv.org/abs/2009.08551) · DOI:10.1103/PhysRevLett.126.036401
    - *Significance:* Embedding the physics solve inside training acts as an implicit regularizer and greatly improves generalization — direct evidence that *how much physics is fixed vs learned* is the variable that controls transferability, which is exactly this thesis's §2 question.
24. **Overcoming the Barrier of Orbital-Free Density Functional Theory for Molecular Systems Using Deep Learning (M-OFDFT)** (Zhang, Liu, You, Liu, Zheng, Lu, Wang, Zheng, Shao et al., *Nature Computational Science*, 2024)
    - *URL:* [arXiv:2309.16578](https://arxiv.org/abs/2309.16578) · DOI:10.1038/s43588-024-00605-8
    - *Significance:* Both the sharpest warning and the sharpest encouragement. Warning: they state that building **essential non-locality** into the functional was required, using density expansion coefficients in an atomic basis — a *local* \(\varepsilon_\theta(\rho,\lvert\nabla\rho\rvert)\) is the form the field already found insufficient. Encouragement: their model **extrapolates to molecules much larger than those seen in training**, i.e. part of the “density representations size-extend” claim is already demonstrated — which sharpens what this thesis may still claim as its own.
25. **On the Stability of Molecules in the Thomas–Fermi Theory** (Teller, *Rev. Mod. Phys.* 34, 627, 1962)
    - *URL:* DOI:10.1103/RevModPhys.34.627
    - *Significance:* Teller's theorem — in pure Thomas–Fermi theory, a purely *local* functional of \(\rho\), molecules do not bind at all. The historical boundary condition on any local kinetic-energy functional, and the reason §2.1 treats \(\varepsilon_\theta\) as a narrow-manifold interpolator rather than a universal KEDF.

*(Excluded: "Protein Spectra" (Ye et al., 2020) and "Isomer Clustering" (Fu & Hopkins, 2017) as they were explicitly identified in the review as unrelated to the overarching IR precision narrative.)*
