# Opponent atlas — cheap line, Bos et al. 2025 (ML-corrected scaling) — 2026-09-10 18:30

Sources `ao5c10225_si_001.xlsx` sha256 `2d86b3f783f9c5d0…`, `ao5c10225_si_002.xlsx` sha256 `ed392d14bd0d3ea2…` (Europe PMC copy of the ACS Supporting Information, CC BY-NC-ND 4.0).

**Species with ML-scaled spectra in the SI: 81** (all PAHdb theoretical uids; n_C 10–50); **bands: 6,591**; conventional scale factor in the file: {0.962: 6591} (uniform, on the authors' own B3LYP/4-31G frequencies, not PAHdb's stored values); rows per species equal PAHdb's mode count for 5 of 81 species (the SI lists the authors' own harmonic sets, which differ in count from PAHdb's for most species).

SVR − conventional shift: mean -0.40 cm⁻¹, MAD 3.91, range -17.7 … +21.1.

Training instances (sheet `training`): 465 rows, columns ['Difference (cm^-1)', 'Computational Frequency (cm^-1)', 'Scaled Computational Frequency (cm^-1)', 'Selected Experimental Frequency (cm^-1)', 'Computational Intensity', 'Computational Relative Intensity', 'Computational Reduced Mass', 'Computational Frequency Constant']; no species identifier, so the molecule-level leakage question cannot be checked from the SI.

Ladder: R0: absent; R1: [['330', 'C10H8', '0']]; R2: [['280', 'C18H12', '0'], ['282', 'C18H12', '0'], ['291', 'C18H12', '0'], ['334', 'C16H10', '0'], ['387', 'C16H10', '0']]; R3: [['18', 'C24H12', '0']]

Family labels by the SVR-predicted position with the atlas' frequency-range rule (pilot-note candidate). Nothing is trained; the pickled models are not run.
