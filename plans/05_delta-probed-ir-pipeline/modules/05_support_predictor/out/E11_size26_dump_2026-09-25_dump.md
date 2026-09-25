# E11 dump — seed-0 model at the full pool

**E11.2 symmetry:** {'n_molecules': 54, 'median_spread_ratio': 0.5920024830630398, 'mean_spread_ratio': 0.6000127567783833, 'pooled_ratio': 0.5214902756305853}

**E11.6 size slope:** {"a": {"slope": 0.05683103169601718, "n": 45, "n_atoms_range": [27, 30]}, "b": {"slope": 0.6727404274578852, "n": 18, "n_atoms_range": [23, 26]}}

## E11.7 error per pair class (RMS of prediction error / RMS of the true ΔF entries)

| hold-out | class | n | rms error | rms true | ratio |
|---|---|---|---|---|---|
| a | diag_bond | 1368 | 0.0018 | 0.0115 | 0.15 |
| a | diag_angle | 1532 | 0.0031 | 0.0079 | 0.39 |
| a | diag_dihedral | 3379 | 0.0002 | 0.0007 | 0.32 |
| a | diag_other | 711 | 0.0005 | 0.0030 | 0.18 |
| a | off_bondbond | 3583 | 0.0013 | 0.0041 | 0.32 |
| a | off_other | 174568 | 0.0005 | 0.0007 | 0.65 |
| b | diag_bond | 481 | 0.0016 | 0.0108 | 0.15 |
| b | diag_angle | 581 | 0.0028 | 0.0069 | 0.40 |
| b | diag_dihedral | 1214 | 0.0002 | 0.0007 | 0.30 |
| b | diag_other | 228 | 0.0009 | 0.0033 | 0.26 |
| b | off_bondbond | 1229 | 0.0010 | 0.0042 | 0.23 |
| b | off_other | 64411 | 0.0003 | 0.0005 | 0.59 |

## E11.3 ring bond–bond pair terms (mean ΔF predicted / true, and B3LYP F_low for orientation; hartree/bohr² units of the internal ΔF)

