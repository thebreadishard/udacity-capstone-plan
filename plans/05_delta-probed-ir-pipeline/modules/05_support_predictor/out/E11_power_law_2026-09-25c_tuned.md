# E11.5 — power-law predictions for the layer-B curve (2026-09-25 20:55); fixed before the 300-table

Fit log(metric) = a + b·log(n) on the existing points; 68 % band from a seed bootstrap. 'factor per decade' = 10^(−b): how much the metric shrinks per tenfold data.

| curve | metric | fitted points | slope b | factor per decade | predicted at 300 | 600 | 1,200 |
|---|---|---|---|---|---|---|---|
| E7 hold-out (a) bare parents | ring_coupling_ratio | 45: 0.42, 100: 0.42, 175: 0.39 | -0.041 [-0.063, -0.021] | 1.10× | 0.39 [0.38, 0.40] | 0.38 [0.36, 0.39] | 0.37 [0.35, 0.39] |
| E7 hold-out (a) bare parents | corrected_freq_rms | 45: 4.58, 100: 4.38, 175: 3.75 | -0.141 [-0.172, -0.112] | 1.38× | 3.57 [3.43, 3.73] | 3.24 [3.05, 3.44] | 2.94 [2.71, 3.18] |
| E7 hold-out (b) unseen scaffolds | ring_coupling_ratio | 45: 0.45, 100: 0.51, 175: 0.42 | -0.039 [-0.071, -0.005] | 1.09× | 0.44 [0.42, 0.47] | 0.43 [0.40, 0.46] | 0.42 [0.38, 0.46] |
| E7 hold-out (b) unseen scaffolds | corrected_freq_rms | 45: 4.94, 100: 5.48, 175: 4.20 | -0.103 [-0.144, -0.064] | 1.27× | 4.29 [3.99, 4.58] | 3.99 [3.61, 4.36] | 3.72 [3.28, 4.17] |
| size split: > 26 atoms | ring_coupling_ratio | 45: 0.66, 100: 0.62, 161: 0.59 | -0.088 [-0.104, -0.073] | 1.22× | 0.56 [0.54, 0.57] | 0.52 [0.51, 0.54] | 0.49 [0.47, 0.51] |
| size split: > 26 atoms | corrected_freq_rms | 45: 6.61, 100: 6.01, 161: 5.76 | -0.110 [-0.124, -0.096] | 1.29× | 5.36 [5.27, 5.46] | 4.97 [4.83, 5.10] | 4.60 [4.44, 4.77] |
| size split control: ≤ 26 scaffolds | ring_coupling_ratio | 45: 0.40, 100: 0.39, 161: 0.36 | -0.066 [-0.077, -0.054] | 1.16× | 0.35 [0.35, 0.36] | 0.34 [0.33, 0.35] | 0.32 [0.31, 0.34] |
| size split control: ≤ 26 scaffolds | corrected_freq_rms | 45: 5.68, 100: 4.92, 161: 4.45 | -0.191 [-0.229, -0.148] | 1.55× | 3.96 [3.79, 4.15] | 3.47 [3.24, 3.73] | 3.04 [2.77, 3.37] |

Reading aid: the proof-of-learning pre-registration asks ≥ 1.5× per decade on the bare-parent and size hold-outs; the factors above say what the short curves extrapolate to if nothing changes.
