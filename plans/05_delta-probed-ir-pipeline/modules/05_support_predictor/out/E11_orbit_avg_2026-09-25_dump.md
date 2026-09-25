# E11 dump — seed-0 model at the full pool

**E11.2 symmetry (coarse rank-tuple key — superseded 25 Sep 09:3x: the target has the same spread under it):** {'n_molecules': 43, 'median_spread_ratio': 0.568966582507437, 'mean_spread_ratio': 0.5023970707218673, 'pooled_ratio': 0.46928499644540195}

**E11.2 symmetry (orbit key, same-parity pairs; rigid = target within-orbit ratio < 0.15):** {"n_all": 43, "n_rigid": 43, "rigid_means_target_ratio_below": 0.15, "rigid": {"pred_ratio": 0.15563973492605382, "target_ratio": 2.2936315563646572e-17, "error_antisymmetric_fraction": 0.4561924099332921, "median_pred_ratio": 0.051033413855249274}, "all": {"pred_ratio": 0.15563973492605382, "target_ratio": 2.2936315563646572e-17, "error_antisymmetric_fraction": 0.4561924099332921}}

| molecule | h | orbits | pred ratio | target ratio | error antisym. fraction |
|---|---|---|---|---|---|
| benzene | a | 56 | 0.019 | 0.000 | 0.201 |
| benzonitrile | a | 255 | 0.050 | 0.000 | 0.208 |
| benzophenone | a | 369 | 0.430 | 0.000 | 0.671 |
| biphenyl | a | 329 | 0.024 | 0.000 | 0.117 |
| biphenylene | a | 454 | 0.085 | 0.000 | 0.354 |
| fluoranthene | a | 1184 | 0.035 | 0.000 | 0.128 |
| fluorene | a | 860 | 0.078 | 0.000 | 0.318 |
| phenanthrene | a | 903 | 0.100 | 0.000 | 0.506 |
| fluoranthene+CF3 | b | 80 | 0.043 | 0.000 | 0.133 |
| fluoranthene+CF3 | b | 82 | 0.053 | 0.000 | 0.104 |
| fluoranthene+CH3 | b | 82 | 0.038 | 0.000 | 0.271 |
| fluoranthene+CH3 | b | 80 | 0.041 | 0.000 | 0.152 |
| fluoranthene+CH3 | b | 73 | 0.042 | 0.000 | 0.282 |
| fluoranthene+CN | b | 9 | 0.100 | 0.000 | 0.326 |
| fluoranthene+CN | b | 9 | 0.101 | 0.000 | 0.264 |
| fluoranthene+CN | b | 9 | 0.087 | 0.000 | 0.202 |
| fluoranthene+CONH2 | b | 42 | 0.057 | 0.000 | 0.277 |
| fluoranthene+NH2 | b | 61 | 0.061 | 0.000 | 0.163 |
| fluoranthene+NH2 | b | 72 | 0.074 | 0.000 | 0.175 |
| fluoranthene+OCH3 | b | 39 | 0.055 | 0.000 | 0.245 |
| fluoranthene+ethynyl | b | 16 | 0.073 | 0.000 | 0.157 |
| fluoranthene+ethynyl | b | 16 | 0.033 | 0.000 | 0.058 |
| fluoranthene+vinyl | b | 42 | 0.026 | 0.000 | 0.144 |
| fluorene+CF3 | b | 265 | 0.038 | 0.000 | 0.160 |
| fluorene+CH3 | b | 276 | 0.035 | 0.000 | 0.109 |
| fluorene+CH3 | b | 265 | 0.032 | 0.000 | 0.114 |
| fluorene+CH3 | b | 262 | 0.032 | 0.000 | 0.104 |
| fluorene+CN | b | 203 | 0.053 | 0.000 | 0.077 |
| fluorene+CONH2 | b | 1093 | 0.064 | 0.000 | 0.297 |
| fluorene+COOH | b | 1073 | 0.068 | 0.000 | 0.311 |
| fluorene+Cl | b | 194 | 0.021 | 0.000 | 0.048 |
| fluorene+Cl | b | 194 | 0.018 | 0.000 | 0.043 |
| fluorene+Cl | b | 192 | 0.016 | 0.000 | 0.035 |
| fluorene+F | b | 936 | 0.068 | 0.000 | 0.336 |
| fluorene+F | b | 191 | 0.017 | 0.000 | 0.037 |
| fluorene+NH2 | b | 252 | 0.051 | 0.000 | 0.121 |
| fluorene+NH2 | b | 266 | 0.068 | 0.000 | 0.168 |
| fluorene+NH2 | b | 255 | 0.052 | 0.000 | 0.143 |
| fluorene+NO2 | b | 194 | 0.018 | 0.000 | 0.041 |
| fluorene+OCH3 | b | 1023 | 0.070 | 0.000 | 0.338 |
| fluorene+SH | b | 192 | 0.018 | 0.000 | 0.039 |
| fluorene+ethynyl | b | 956 | 0.070 | 0.000 | 0.200 |
| fluorene+vinyl | b | 234 | 0.024 | 0.000 | 0.074 |

**E11.6 size slope:** {"a": {"slope": -0.16123384819182449, "n": 10, "n_atoms_range": [12, 26]}, "b": {"slope": 1.1257207029036775, "n": 39, "n_atoms_range": [23, 30]}}

## E11.7 error per pair class (RMS of prediction error / RMS of the true ΔF entries)

| hold-out | class | n | rms error | rms true | ratio |
|---|---|---|---|---|---|
| a | diag_bond | 222 | 0.0012 | 0.0110 | 0.11 |
| a | diag_angle | 238 | 0.0029 | 0.0086 | 0.34 |
| a | diag_dihedral | 526 | 0.0002 | 0.0006 | 0.31 |
| a | diag_other | 117 | 0.0003 | 0.0020 | 0.16 |
| a | off_bondbond | 553 | 0.0008 | 0.0043 | 0.18 |
| a | off_other | 24909 | 0.0004 | 0.0006 | 0.69 |
| b | diag_bond | 1133 | 0.0018 | 0.0111 | 0.16 |
| b | diag_angle | 1318 | 0.0024 | 0.0064 | 0.39 |
| b | diag_dihedral | 2867 | 0.0002 | 0.0006 | 0.33 |
| b | diag_other | 575 | 0.0006 | 0.0026 | 0.23 |
| b | off_bondbond | 2951 | 0.0013 | 0.0042 | 0.31 |
| b | off_other | 152525 | 0.0004 | 0.0005 | 0.68 |

## E11.3 ring bond–bond pair terms (mean ΔF predicted / true, and B3LYP F_low for orientation; hartree/bohr² units of the internal ΔF)

- **benzene:** ortho: pred +0.00573 true +0.00481 F_low +0.0352 (n=6); meta: pred -0.00741 true -0.00644 F_low -0.0174 (n=6); para: pred +0.00651 true +0.00652 F_low +0.0462 (n=3)
