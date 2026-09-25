# E11 dump — seed-0 model at the full pool

**E11.2 symmetry (coarse rank-tuple key — superseded 25 Sep 09:3x: the target has the same spread under it):** {'n_molecules': 43, 'median_spread_ratio': 0.5975422363345033, 'mean_spread_ratio': 0.585768382476168, 'pooled_ratio': 0.5203793409206349}

**E11.2 symmetry (orbit key, same-parity pairs; rigid = target within-orbit ratio < 0.15):** {"n_all": 43, "n_rigid": 22, "rigid_means_target_ratio_below": 0.15, "rigid": {"pred_ratio": 0.06604632390793441, "target_ratio": 0.10311078491007214, "error_antisymmetric_fraction": 0.3865978056317317, "median_pred_ratio": 0.04746116147058009}, "all": {"pred_ratio": 0.28095631085815514, "target_ratio": 0.36746379518515404, "error_antisymmetric_fraction": 0.5718170738880888}}

| molecule | h | orbits | pred ratio | target ratio | error antisym. fraction |
|---|---|---|---|---|---|
| benzene | a | 56 | 0.025 | 0.026 | 0.125 |
| benzonitrile | a | 255 | 0.404 | 0.432 | 0.662 |
| benzophenone | a | 369 | 0.481 | 0.505 | 0.441 |
| biphenyl | a | 329 | 0.029 | 0.083 | 0.307 |
| biphenylene | a | 454 | 0.081 | 0.072 | 0.442 |
| fluoranthene | a | 1184 | 0.040 | 0.144 | 0.488 |
| fluorene | a | 860 | 0.072 | 0.084 | 0.301 |
| phenanthrene | a | 903 | 0.104 | 0.096 | 0.390 |
| fluoranthene+CF3 | b | 80 | 0.281 | 0.589 | 0.742 |
| fluoranthene+CF3 | b | 82 | 0.366 | 0.600 | 0.635 |
| fluoranthene+CH3 | b | 82 | 0.055 | 0.135 | 0.637 |
| fluoranthene+CH3 | b | 80 | 0.053 | 0.176 | 0.586 |
| fluoranthene+CH3 | b | 73 | 0.085 | 0.129 | 0.797 |
| fluoranthene+CN | b | 9 | 0.594 | 0.655 | 0.843 |
| fluoranthene+CN | b | 9 | 0.591 | 0.628 | 0.744 |
| fluoranthene+CN | b | 9 | 0.600 | 0.663 | 0.803 |
| fluoranthene+CONH2 | b | 42 | 0.104 | 0.117 | 0.419 |
| fluoranthene+NH2 | b | 61 | 0.197 | 0.254 | 0.329 |
| fluoranthene+NH2 | b | 72 | 0.179 | 0.323 | 0.502 |
| fluoranthene+OCH3 | b | 39 | 0.106 | 0.192 | 0.722 |
| fluoranthene+ethynyl | b | 16 | 0.585 | 0.615 | 0.703 |
| fluoranthene+ethynyl | b | 16 | 0.591 | 0.713 | 0.746 |
| fluoranthene+vinyl | b | 42 | 0.036 | 0.097 | 0.432 |
| fluorene+CF3 | b | 265 | 0.252 | 0.394 | 0.774 |
| fluorene+CH3 | b | 276 | 0.044 | 0.155 | 0.548 |
| fluorene+CH3 | b | 265 | 0.060 | 0.127 | 0.545 |
| fluorene+CH3 | b | 262 | 0.060 | 0.206 | 0.663 |
| fluorene+CN | b | 203 | 0.537 | 0.642 | 0.760 |
| fluorene+CONH2 | b | 1093 | 0.066 | 0.118 | 0.395 |
| fluorene+COOH | b | 1073 | 0.070 | 0.188 | 0.577 |
| fluorene+Cl | b | 194 | 0.013 | 0.016 | 0.060 |
| fluorene+Cl | b | 194 | 0.013 | 0.013 | 0.054 |
| fluorene+Cl | b | 192 | 0.014 | 0.021 | 0.074 |
| fluorene+F | b | 936 | 0.072 | 0.086 | 0.301 |
| fluorene+F | b | 191 | 0.013 | 0.017 | 0.075 |
| fluorene+NH2 | b | 252 | 0.150 | 0.147 | 0.151 |
| fluorene+NH2 | b | 266 | 0.150 | 0.359 | 0.670 |
| fluorene+NH2 | b | 255 | 0.153 | 0.268 | 0.434 |
| fluorene+NO2 | b | 194 | 0.015 | 0.010 | 0.055 |
| fluorene+OCH3 | b | 1023 | 0.071 | 0.141 | 0.442 |
| fluorene+SH | b | 192 | 0.013 | 0.017 | 0.077 |
| fluorene+ethynyl | b | 956 | 0.305 | 0.324 | 0.550 |
| fluorene+vinyl | b | 234 | 0.027 | 0.068 | 0.210 |

**E11.6 size slope:** {"a": {"slope": -0.04688206291241831, "n": 10, "n_atoms_range": [12, 26]}, "b": {"slope": 1.8568681842270205, "n": 39, "n_atoms_range": [23, 30]}}

## E11.7 error per pair class (RMS of prediction error / RMS of the true ΔF entries)

| hold-out | class | n | rms error | rms true | ratio |
|---|---|---|---|---|---|
| a | diag_bond | 222 | 0.0012 | 0.0110 | 0.11 |
| a | diag_angle | 238 | 0.0028 | 0.0086 | 0.33 |
| a | diag_dihedral | 526 | 0.0002 | 0.0006 | 0.31 |
| a | diag_other | 117 | 0.0006 | 0.0031 | 0.21 |
| a | off_bondbond | 553 | 0.0009 | 0.0043 | 0.20 |
| a | off_other | 24909 | 0.0003 | 0.0007 | 0.48 |
| b | diag_bond | 1133 | 0.0017 | 0.0111 | 0.15 |
| b | diag_angle | 1318 | 0.0027 | 0.0064 | 0.42 |
| b | diag_dihedral | 2867 | 0.0002 | 0.0006 | 0.34 |
| b | diag_other | 575 | 0.0007 | 0.0039 | 0.18 |
| b | off_bondbond | 2951 | 0.0014 | 0.0042 | 0.33 |
| b | off_other | 152525 | 0.0004 | 0.0006 | 0.69 |

## E11.3 ring bond–bond pair terms (mean ΔF predicted / true, and B3LYP F_low for orientation; hartree/bohr² units of the internal ΔF)

- **benzene:** ortho: pred +0.00574 true +0.00481 F_low +0.0352 (n=6); meta: pred -0.00721 true -0.00644 F_low -0.0174 (n=6); para: pred +0.00660 true +0.00652 F_low +0.0462 (n=3)
