# Where λ = 1 spoils the mode shapes (exploratory, post hoc; input for the λ chain's registration)

## pyridine

rel. rms matched: λ = 1 0.310, zero rule 0.262 (check against lever 6b's read)

| kind | modes | share of λ = 1 error² (seed mean) | zero rule error² |
|---|---|---|---|
| CH-str | 5 | 0.0005 | 0.0001 |
| oop | 8 | 0.0919 | 0.0644 |
| ip | 14 | 0.0040 | 0.0042 |

| ω true | kind | I true | I λ=1 (seeds) | I zero | overlap λ=1 (seeds) | overlap zero |
|---|---|---|---|---|---|---|
| 757.8 | oop | 22.94 | 6.57 / 6.84 / 5.62 | 9.04 | 0.891 / 0.897 / 0.873 | 0.927 |
| 717.7 | oop | 35.06 | 51.35 / 51.12 / 52.31 | 48.91 | 0.891 / 0.896 / 0.873 | 0.927 |
| 1041.0 | ip | 6.65 | 5.17 / 4.94 / 5.03 | 5.0 | 0.988 / 0.984 / 0.986 | 0.981 |
| 1090.1 | ip | 2.39 | 3.09 / 3.18 / 3.05 | 2.69 | 0.996 / 0.995 / 0.996 | 0.999 |

## fluorobenzene

rel. rms matched: λ = 1 0.172, zero rule 0.104 (check against lever 6b's read)

| kind | modes | share of λ = 1 error² (seed mean) | zero rule error² |
|---|---|---|---|
| CH-str | 5 | 0.0002 | 0.0003 |
| oop | 9 | 0.0278 | 0.0096 |
| ip | 16 | 0.0016 | 0.0010 |

| ω true | kind | I true | I λ=1 (seeds) | I zero | overlap λ=1 (seeds) | overlap zero |
|---|---|---|---|---|---|---|
| 669.7 | oop | 4.49 | 11.28 / 10.96 / 10.88 | 8.28 | 0.97 / 0.974 / 0.971 | 0.987 |
| 768.6 | oop | 74.0 | 66.49 / 66.12 / 66.75 | 68.94 | 0.977 / 0.98 / 0.979 | 0.991 |
| 504.2 | oop | 5.08 | 6.24 / 6.3 / 6.64 | 5.88 | 0.996 / 0.997 / 0.996 | 0.998 |
| 1173.9 | ip | 8.44 | 6.7 / 6.74 / 6.94 | 7.28 | 0.974 / 0.992 / 0.998 | 0.999 |

## benzonitrile

rel. rms matched: λ = 1 0.443, zero rule 0.258 (check against lever 6b's read)

| kind | modes | share of λ = 1 error² (seed mean) | zero rule error² |
|---|---|---|---|
| CH-str | 5 | 0.0008 | 0.0006 |
| oop | 10 | 0.1956 | 0.0655 |
| ip | 18 | 0.0002 | 0.0002 |

| ω true | kind | I true | I λ=1 (seeds) | I zero | overlap λ=1 (seeds) | overlap zero |
|---|---|---|---|---|---|---|
| 682.9 | oop | 17.12 | 35.42 / 34.52 / 33.06 | 26.9 | 0.923 / 0.933 / 0.936 | 0.966 |
| 770.9 | oop | 46.53 | 26.0 / 26.33 / 27.62 | 34.48 | 0.922 / 0.927 / 0.934 | 0.967 |
| 543.2 | oop | 10.96 | 14.7 / 15.05 / 15.67 | 13.58 | 0.941 / 0.928 / 0.944 | 0.994 |
| 371.2 | oop | 0.7 | 0.02 / 0.02 / 0.03 | 0.44 | 0.673 / 0.701 / 0.847 | 0.995 |

## Reading (22:5x, 12 Oct; exploratory, not a registered result)

**The check holds.** The seed means reproduce lever 6b's read exactly: pyridine 0.310 / 0.262, fluorobenzene 0.172 / 0.104, benzonitrile
0.443 / 0.258.

**Where the error is.** The whole intensity error of the λ = 1 standard sits in the **out-of-plane block**.

| molecule | error² in out-of-plane modes, λ = 1 | zero rule | in plane, λ = 1 | in plane, zero rule | C–H stretch, λ = 1 | C–H stretch, zero rule |
|---|---|---|---|---|---|---|
| pyridine | 0.092 | 0.064 | 0.004 | 0.004 | 0.0005 | 0.0001 |
| fluorobenzene | 0.028 | 0.010 | 0.002 | 0.001 | 0.0002 | 0.0003 |
| benzonitrile | 0.196 | 0.066 | 0.0002 | 0.0002 | 0.0008 | 0.0006 |

**What happens there.** The two strongest out-of-plane bands of each molecule, near 680–770 cm⁻¹, are a pair of nearby modes that mix:
- pyridine 718/758: the gap is about 40 cm⁻¹, and both modes have the same overlap with the truth, 0.89 under λ = 1 against 0.93 for B3LYP;
- fluorobenzene 670/769;
- benzonitrile 683/771.

Equal overlaps on both members mean the predicted pair is rotated inside its own two-dimensional space. Intensity then moves from one member
to the other. Pyridine's 758 band falls from 22.9 to about 6 km/mol while the 718 band rises from 35 to 51. Benzonitrile's 683 rises from 17 to
34 while the 771 falls from 47 to 26.

B3LYP's own pair is already rotated the same way. λ = 1 rotates it further: pyridine's angle from about 16° to about 19–20°.

**What it suggests,** to be registered and not assumed:
- the error is in the network's **coupling between nearby out-of-plane modes**, the off-diagonal ΔH in the out-of-plane block, not in the
  diagonal frequencies. A small coupling error turns such a pair a long way when the gap is small;
- this fits the earlier signs that out-of-plane is the network's weak family (R0's out-of-plane rows, pyridine's CH-oop 10.6 against 5.4
  cm⁻¹ under λ = 1).

For the λ chain this means three things:
1. The intensity read should name the out-of-plane pairs.
2. A mixing-angle error per pair is a direct metric of what goes wrong.
3. An arm that keeps the network's out-of-plane diagonal but takes the out-of-plane couplings from B3LYP is a candidate beside λ = 0.
