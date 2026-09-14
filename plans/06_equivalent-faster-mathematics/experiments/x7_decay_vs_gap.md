# X7 — pair-energy decay length λ against the HOMO–LUMO gap (cc-pvdz MP2; B3LYP/6-31G* gap; 2026-09-14 08:23)

| molecule | C | λ (Å) | DFT gap (eV) | HF gap (eV) | λ·gap_DFT | correlation beyond 3 Å | pair-sum check |
|---|---|---|---|---|---|---|---|
| benzene | 6 | **0.667** | 6.80 | 12.79 | **4.535** | 1.9 % | -2.6e-15 |
| naphthalene | 10 | **0.702** | 4.83 | 10.23 | **3.390** | 3.8 % | 1.8e-15 |
| pyrene | 16 | **0.750** | 3.84 | 8.67 | **2.882** | 5.5 % | 8.9e-15 |

λ·gap max/min across the three: **1.57** — losing condition (> 2) not met.

Losing condition (pre-stated): lambda*gap varies by more than a factor 2 across benzene, naphthalene, pyrene. Rate ∝ gap predicts λ ∝ 1/gap, i.e. constant λ·gap.

Constants: {"basis_default": "cc-pvdz", "dft_functional": "b3lyp", "dft_basis": "6-31g*", "R_MIN_A": 1.0, "shell_width_A": 0.5, "far_cut_A": 3.0, "git_commit_pyrene": "57a7910", "pyrene_file": "plans/02_coupled-cluster-anharmonic-ir/probes/batch_results/06_freq_pyrene.npz", "losing_condition": "lambda*gap varies by more than a factor 2 across benzene, naphthalene, pyrene"}