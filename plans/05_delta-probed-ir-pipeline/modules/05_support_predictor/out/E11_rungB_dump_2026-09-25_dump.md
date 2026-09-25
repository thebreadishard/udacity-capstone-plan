# E11 dump — seed-0 model at the full pool

**E11.2 symmetry:** {'n_molecules': 43, 'median_spread_ratio': 0.5975422995286684, 'mean_spread_ratio': 0.5857683857630108, 'pooled_ratio': 0.5203793223374152}

**E11.6 size slope:** {"a": {"slope": -0.04688166274371281, "n": 10, "n_atoms_range": [12, 26]}, "b": {"slope": 1.8568686828627015, "n": 39, "n_atoms_range": [23, 30]}}

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
