# The anharmonic step's two design questions, read on the data in hand (16 Nov 2026, TASKS 211)

Read-only: no quantum chemistry was run. Every table comes from a script in this folder and its `.json`
(`inventory.py`, `refit.py`, `marks.py`, `modes.py`, `structural_rule.py`; each under 40 s). Written by the
session from the reading agent's report; the numbers are the scripts'.

## Q1 — which modes carry the model's inputs for a new molecule

**Training used the G modes** — pyscf B3LYP/6-31G* at its own minimum: ω, family, h, o, label and marks come
from G's `ref.json` (`probes/s2_read.py:116-150`, `load_molecule`); the xtb modes are matched to them
one-to-one by squared overlap and refused below 0.5 (`probes/s2_xtb_read.py:51-79`). The pipeline's B3LYP
modes are the same modes: overlap median 0.99997, ω rms 1.08 cm⁻¹ on 38 molecules.

**B3LYP modes against corrected modes** (corrected = the ωB97X corpus Hessian, i.e. a perfect ΔH; 38
molecules, 2,160 modes; tetracene has no corpus row): |overlap| median 0.998, p10 0.925, min 0.552; 13 modes
(0.6 %) below 0.5; 395 modes (18 %) change rank; ω moves 24.5 cm⁻¹ rms; the xtb partner is lost on 81
corrected modes against 21 B3LYP modes. The trainer's record agrees (`E7_rungC_chain35_analytic.json`,
`zero_rule`): hold-out (a) 0.998 / p10 0.914, (b) 0.989 / p10 0.836.

x2* error against the VPT2 label, scaffold left out (cm⁻¹):

| family | n | inputs on B3LYP modes | inputs on corrected modes | rms between the two |
|---|---|---|---|---|
| CH-stretch | 299 | 8.94 | 9.49 | 5.11 |
| CH-oop | 255 | 5.85 | 6.65 | 3.04 |
| ring-ip | 737 | 3.12 | 3.19 | 0.85 |
| other | 315 | 3.37 | 3.49 | 0.55 |
| all | 1,606 | 5.20 | 5.55 | 2.59 |

B3LYP inputs are better in 31 of 38 molecules. Caveat: the label is a B3LYP-mode quantity, so this score
favours the B3LYP modes by construction.

**Decision (16 Nov 2026):** the B3LYP modes carry the inputs, as in training. Δ_anh is carried to the
corrected band by overlap assignment, never by rank; a corrected band whose best B3LYP partner overlaps below
0.5 gets no step and says so.

## Q2 — marking a mode of a new molecule as outside VPT2's domain

The xtb mark alone does not catch the G marks: 2 of 6, and neither of coronene's (39 molecules, 2,244 modes;
all marks fall in family 'other'):

| | G and xtb | G only | xtb only | neither |
|---|---|---|---|---|
| other | 2 | 4 | 0 | 747 |
| CH-stretch / CH-oop / ring-ip | 0 | 0 | 0 | 322 / 296 / 873 |

- Coronene mode 24: G strain 0.103, xtb strain 0.014, xtb share 0.001, xtb overlap 0.964 — not marked by xtb.
- Coronene mode 36: G strain 0.222, xtb strain 0.010, xtb share 0.002, xtb overlap 0.903 — not marked by xtb.
- The other two G-only modes: B_0603418c5b mode 11 (xtb strain 0.004), B_410ac0fb2f mode 8 (no xtb partner, 0.458).
- Lower xtb thresholds do not help: at 0.02 still 2 of 5 caught, with 658 false marks.

**What a miss costs:** x2* prints ω − 9.1 and ω − 11.6 on coronene's two modes where the VPT2 label says
+66.2 and +179.1 — but that label is the number VPT2 cannot state, so the true cost is not on disk. What is
certain: an error bar of 3.84 would be printed on a band whose error was never measured.
**What a false mark costs:** none occurred (0 of 2,238). Per mode it is the step forgone (harmonic → with the
step): ring-ip 26.67 → 3.04, other 10.17 → 3.31, CH-oop 13.26 → 5.74, CH-stretch 136.46 → 8.79.

Rules compared:

| rule for a new molecule | G marks caught | sound modes that lose the step |
|---|---|---|
| label-free flag (large-amplitude: `linear_xh_share` with `LABILE_PARTNERS`) or no xtb partner or xtb partner marked | 4 of 6 (misses coronene 24, 36) | 0 |
| structural: family 'other' with o ≥ 0.8 | 6 of 6 | 118 (11.73 → 4.67 forgone) |

**Decision (16 Nov 2026), the session's, open to the user's overruling:** the first rule decides where no step
is applied. The structural mark is not a refusal but a wording: a band in family 'other' with o ≥ 0.8 gets the
step printed as the best estimate and the certificate says for that band that the step's error is not measured
for this kind of mode (the two coronene modes are of this kind). Reason: the registered choice of 14 Nov is to
print the best estimate and claim only what was measured; refusing 118 sound modes to catch 2 costs 7 cm⁻¹ on
each of them, and silence about the 2 would print a bar nobody measured.

## Can x2* be refitted for an acceptance test?

Git is not enough; the disk is. Git holds all 78 label files, but of the force fields the read loads only
benzene's G pair and no xtb force field (missing from git: 7.8 MB of `ref.json`, 157 MB of `qff_report.npz`).
On disk all 39 molecules are complete on both sides. Refit through the repository's own
`s3_read.load_scope` + `read_targets`, 37 training force fields:

| family | training modes | target rows | refit | registered |
|---|---|---|---|---|
| ring-ip | 760 | 56 | 3.3694 | 3.37 |
| other | 302 | 23 | 3.8387 | 3.84 |
| CH-oop | 248 | 22 | 8.3809 | 8.38 |
| CH-stretch | 288 | 20 | 6.2143 | 6.21 |

## Not established, with the cheapest measurement for each

1. Whether a missed mark is an error: a variational solve of coronene's modes 24 and 36 on the quartic
   constants already in its G `qff_report.npz` (TASKS 209), plus one B3LYP scan along mode 36.
2. The miss rate beyond one D6h molecule: both marks on the next compact PAH with both force fields.
3. The right shift for a strongly mixed corrected mode: one ωB97X QFF + GVPT2 on naphthalene.
4. Q1 with the network's own ΔH rather than the exact ωB97X Hessian: `modes.py` on `H_low + ΔH`.
5. Whether the public data mirror holds the 78 force-field folders (`tools/backup_data.py:41` lists
   `probes/results_m1`; the mirror was not opened).
6. Tetracene in Q1: no corpus Hessians (`R4_cc63e78416` is pending).
