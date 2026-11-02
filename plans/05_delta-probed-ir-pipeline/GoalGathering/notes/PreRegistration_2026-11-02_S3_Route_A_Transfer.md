# Pre-registration S3: does the learned anharmonic shift carry to tetracene and coronene? (2 Nov 2026)

**Status: REGISTERED 2 Nov 2026, 08:2x**, before any route A computation on a target and before any S2b label existed. The read script `probes/s3_read.py` passed its synthetic tests first (`tests/test_s3_read.py`, 8). The benzene gate was already running on `routea` under S1 amendment 2's line, which this registration takes over. The user chose S2b together with route A on 2 Nov 2026: 'Eerst S2b met route A'. They created the CCX53 `routea` (ubuntu-128gb-hel1-6) and later said 'Ga je gang met route A'. Peropyrene was left out: ≈ €118 more and a second CCX53.

## Why

S2 and S2b learn a per-mode anharmonic shift Δ_anh = ν − ω on molecules of at most about 23 atoms. The product needs Δ_anh at 30–60
atoms, where full GVPT2 costs ≈ €800 for HBC at G (design note §2). The design note named the open question: does a model trained small
transfer large? The harmonic correction did not transfer well (chain 39's size penalty). S3 measures this directly. Route A computes the
full GVPT2 of two targets at the level the training labels have (G), and the S2/S2b models predict the same modes without seeing them.

- **Tetracene** (C18H12, 30 atoms, D2h): the design note's validation molecule. It is also in PAHdb's anharmonic library, which carries
  the Mackie et al. spectra of the supervisor's line.
- **Coronene** (C24H12, 36 atoms, D6h): a size step beyond tetracene, with 34 degenerate pairs. It is not in PAHdb's anharmonic library
  (the largest species there has 18 carbons), so it reads the transfer only.

## Computation

GVPT2 at G (B3LYP/6-31G*, grid 75,302), step 0.10, `dpir.qff` with its noise guard, labels from the same solver as S2/S2b
(`probes/gvpt2_labels.py`, pyVPT2 fork eb353ab). This is route A as S1's amendment 2 fixed it for tetracene, coronene and peropyrene,
with the first Hessian re-timed on the target. The runner is `probes/s1_anharmonic_level.sh`, with two additions that are off by default:

- **The ± saving** (`PM_SAVING=1`). The optimised reference is averaged over its point group. For every displaced geometry x₀ + d whose
  negative is the image of an operation (D d = −d within the rebuild's 1e-2 relative tolerance), the Hessian at x₀ − d is written as
  D H(x₀ + d) Dᵀ instead of being computed. Operations that map the laboratory-frame Lebedev grid onto itself (signed permutations) are
  preferred. On benzene the ± saving moved Δ_anh by 0.03 cm⁻¹ rms and 0.09 max (S1's development, 13 Oct). The pair saving failed there
  (0.56 / 1.06) and is not used. Counts with the ± saving: tetracene 100 Hessians, coronene 109 at most. A degenerate-pair member with no
  operation mapping it to its negative is computed both ways.
- **Lanes** (`LANES=4`). One molecule's displaced Hessians are split over four processes of 8 threads each. The optimisation and the
  reference Hessian use all 32 threads. PYSCF_MAX_MEMORY is 24,000 MB per lane: coronene's label Hessian peaked at 25 GB at the label
  settings (31 Oct).

Inputs:
- **tetracene:** the ideal D2h geometry of `probes/qff_symmetry_count.py` (`tetracene_ideal`).
- **coronene:** the geometry of the large-PAH labels, T_94b3a9d13a (`probes/results_m1/l5b_2026-11-01/l5b/molecules/T_94b3a9d13a/geometry.json`).

Both are copied under `probes/results_m1/routea_2026-11-02/` with their sha256 and optimised at G. They run one molecule at a time,
tetracene first.

**Stop rule.** A lane's first displaced Hessian takes longer than 1.5 × S2's per-Hessian fit, exp(−4.92) · n^3.89 s (measured at 5
threads on a CPX62). That gives 6,000 s for tetracene and 12,200 s for coronene. The molecule then stops and is re-priced.

**Noise rule.** As S2: a NOISY molecule is excluded and named, and the read reports it without a verdict.

**Gate before the targets.** Benzene at G with `PM_SAVING=1 LANES=4` on `routea`, against S1's directly computed G set
(`probes/results_m1/s1_anharmonic_benzene_2026-10-13/s1_benzene/G`). The line is S1 amendment 2's: Δ_anh rms ≤ 0.2 cm⁻¹ and max
≤ 0.5 cm⁻¹. A miss stops route A before tetracene and goes to the user.

**GFN2-xTB force fields** of the two targets are computed on the laptop from their G minima (`probes/xtb_anharmonic.sh`), for the x
models.

## Price and time

| | value | source |
|---|---|---|
| CCX53 price | €0.855 per hour | console, 3 Oct |
| tetracene | 100 Hessians × ≈ 4,006 s ÷ 4 lanes ≈ 28 h | S2's fit at 5 threads |
| coronene | 109 × ≈ 8,135 s ÷ 4 ≈ 62 h | S2's fit at 5 threads |
| with the references and the benzene gate | ≈ 4 days ≈ €82 | 89 h of displaced Hessians plus the references |
| idle time before the launch | ≈ €20 | |

The threads per lane rise from 5 to 8, so these are upper estimates. Launched by 9 Nov, the run ends before the stop date of 15 Nov.

## Read (fixed now)

`probes/s3_read.py --sets <S2/S2b sets.json> --s2b-read <s2b_read.json> --targets <targets set.json> --out <dir>`.

The training molecules are S2's and S2b's, read exactly as `probes/s2b_read.py` reads them, in its main scope 'no-large-amplitude'. The
targets are read by the same loader: G labels from `gvpt2_labels.py`, xtb partners from `s2_xtb_read`. Only window modes
(550–2000 cm⁻¹) count. A degenerate pair (ω within 0.5 cm⁻¹) counts once, as the mean of its two members, so coronene's pairs do not
count double.

**Models**, each fitted once on all training molecules:
- (c), the family mean;
- (b);
- x1;
- x2*, at the configuration S2b's read chose for the family;
- x0 (Δ_xtb alone).

The nested search is not applied, because it has no single fitted model. **The verdict model per family** is S2b's `best_curve_model`
for that family in the main scope.

**Lines per family**, pooled over the two targets:
1. **Transfer holds** when the verdict model's rms on the targets is ≤ 3.0 cm⁻¹ (line 2) and below (c)'s rms on the same modes.
2. **No verdict** for a family with fewer than 6 target modes. Its numbers are reported.

Also reported, without a line:
- the size penalty, i.e. the target rms ÷ the same model's leave-one-scaffold-out rms at 'all' in S2b's read;
- every model's rms per family and per molecule;
- the modes that a polyad moved, or whose resonance `gvpt2_labels.py` skipped next to a degenerate mode.

**What follows.**
- **Holds in a family:** that family's anharmonic step for S4's five large PAHs is the verdict model. Its error bar is the target rms.
- **Fails:** S4 uses route A's own values where they exist (tetracene, coronene). The others carry (c)'s error bar, stated, and the
  route A price of each goes to the user.

**Outside the verdict: the comparison with the supervisor's spectra.** Our G-level GVPT2 fundamentals of tetracene go beside PAHdb's
anharmonic library v1.00 (the Mackie line). The rule for matching our modes to theirs is fixed in an amendment before that file is read
against our numbers.

**Predictions (before any number).**

| prediction | odds |
|---|---|
| ring-ip: the verdict model's target rms within 1.5 × its S2b rms at 'all' | one in two |
| CH-oop: worse on the targets than at small size (out-of-plane motion couples across the whole ring system) | two in three |
| coronene's rms above tetracene's in most families (degenerate resonances are left deperturbed) | one in two |
| line 1 holds in at least one family | one in four |

## Risks named now

- pyVPT2 treats degeneracy only for linear molecules. A resonance that touches one of coronene's degenerate modes is left deperturbed and
  named (`gvpt2_labels.py`). The training set holds few degenerate molecules (benzene), so coronene also tests the labels.
- Memory above 307 basis functions at G is measured here for the first time (coronene has 384). Four lanes of 24 GB fit the CCX53's
  122 GB.
- The S3 read depends on S2b's read. If S2b ends late, the S3 read waits for it; route A's GVPT2 values are kept either way.
