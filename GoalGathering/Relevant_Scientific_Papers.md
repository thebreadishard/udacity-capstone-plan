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

*(Excluded: "Protein Spectra" (Ye et al., 2020) and "Isomer Clustering" (Fu & Hopkins, 2017) as they were explicitly identified in the review as unrelated to the overarching IR precision narrative.)*
