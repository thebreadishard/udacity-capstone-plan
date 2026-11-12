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

## Amendment 1 (2 Nov 2026, 08:3x, before any computation on a target): coronene's Hessian count

'Coronene 109 at most' above was S1's count, which assumed that every mode of a degenerate pair has an operation that maps it to its negative. The runner's rule is stricter. A degenerate pair's basis comes from the reference Hessian, so it is arbitrary inside the pair's plane, and for E2g-type pairs no operation acts as −1 on the whole plane. Those members are computed both ways.

The same rule applied to a random group-averaged Hessian (scratch `pm_counts.py`) gives:

| molecule | Hessians | of which images |
|---|---|---|
| benzene | 41 | 20 |
| tetracene | 100 | 69 |
| coronene | 132 | 73 |

Benzene's 41 equals what the gate actually computes on `routea` (61 stubs, 41 computed, 20 images), so the count is measured, not assumed. Coronene then needs ≈ 132 × 8,135 s ÷ 4 ≈ 75 h. Both targets with their references take ≈ 108 h, ≈ €92, and still end before 15 Nov if launched on 2 Nov.

Aligning each pair's basis with a reflection would save about one Hessian per E2g pair (≈ 7 h). It is not built: it would be a new step in a runner the gate has just measured. The read is unchanged.

## Amendment 2 (2 Nov 2026, 08:5x, after the first gate and before any computation on a target): images from grid-compatible operations only

The first benzene gate (`/root/routea_gate`, 07:19–07:47 UTC) missed the line before its read: its force field failed the noise guard. The quartic route disagreement was 61.1 cm⁻¹ at most, against 1.1 in S1's direct G set (`probes/results_m1/routea_2026-11-02/gate/benzene/G`). Every large disagreement involved a mode whose −d Hessian was an image made by an operation that does not map the Lebedev grid onto itself. There were five such images (modes 5, 6, 7, 10, 19: C6, C3 or oblique mirrors), and the twelve worst pairs all hold one of them. Pairs whose images came from grid-compatible operations stay below 1 cm⁻¹. This is S1's measured image error of 13 Oct (2.4e-2 against 3.0e-3 of the displacement signal). The runner had preferred grid-compatible operations without requiring them.

The rule now admits only grid-compatible operations (`probes/qff_pm_saving.py`). A mode without one is computed both ways.

| molecule | Hessians before | Hessians now |
|---|---|---|
| benzene | 41 | 46 |
| tetracene | 100 | 100 (all 69 of its images were grid-compatible) |
| coronene | 132 | 133 |

The time and price stay as amendment 1 has them, to within an hour.

The gate is rerun from scratch in fresh folders (`/root/dpir_routea2`, `/root/routea_gate2`), under the same line. A pass launches the targets, because the miss had a measured cause in the runner and not in the method. A second miss stops route A and goes to the user.

## Amendment 3 (2 Nov 2026, 10:0x, after the second gate and before any computation on a target): route A without the ± saving

The rerun gate missed too: Δ_anh rms 0.294 and max 1.285 cm⁻¹ against S1's direct G, with 15 grid-compatible images. Computing those 15 Hessians directly split the miss in two:

| comparison | rms | max |
|---|---|---|
| S1 direct ↔ the gate's direct set (the reference and the lanes) | 0.003 | 0.008 cm⁻¹ |
| images ↔ direct (the saving) | 0.294 | 1.286 cm⁻¹ |

The reference Hessian is invariant under the one grid-compatible operation of the tilted corpus benzene (the inversion) only to 1.9e-5 of max |H|, the order of the images' differences. The ledger has the detail. The user chose option B: 'Akkoord voor optie B'. Route A runs without the ± saving (`PM_SAVING` off), all ±d Hessians directly, four lanes of 8 threads, as S2 and S2b computed their labels.

| molecule | Hessians (2M + 1) | time on four lanes |
|---|---|---|
| tetracene | 169 | ≈ 47 h |
| coronene | 205 | ≈ 116 h |

With the references that is ≈ 168 h, ≈ €145, ending ≈ 9–10 Nov, before 15 Nov. The stop rule, the noise rule and the read are unchanged. The ± saving stays in the runner, off by default; it is not used for a registered result.

## Amendment 4 (2 Nov 2026, 14:0x, before any target force field exists): tetracene's stop was the runner's thread count

Tetracene's four lanes took 7,775–7,814 s for their first displaced Hessians, so the stop rule (6,000 s) stopped it at 13:02 UTC. The cause was the runner, not the molecule. runspec exports OPENBLAS/MKL_NUM_THREADS as the spec's total (32), every lane's pyscf process inherited it, and the CCX53 ran 4 × (8 + 32) threads on 32 cores, at load 128. `s1_anharmonic_level.sh` now caps BLAS per process (45d5da46; water in WSL with an inherited 32: the child sees its own 2, and ω equals the reference to 1e-8).

With the user's word ('Akkoord met allebei'), `routea_targets` was stopped (coronene's optimisation had just begun) and is relaunched with the fixed runner and the same stop rule, which now applies to the next Hessian each lane computes. Tetracene keeps its optimised minimum, its reference and the four displaced Hessians already written. The S2b servers received the same runner for every molecule they start from now on; molecules already running keep the script they read.

## Risks named now

- pyVPT2 treats degeneracy only for linear molecules. A resonance that touches one of coronene's degenerate modes is left deperturbed and
  named (`gvpt2_labels.py`). The training set holds few degenerate molecules (benzene), so coronene also tests the labels.
- Memory above 307 basis functions at G is measured here for the first time (coronene has 384). Four lanes of 24 GB fit the CCX53's
  122 GB.
- The S3 read depends on S2b's read. If S2b ends late, the S3 read waits for it; route A's GVPT2 values are kept either way.


**Dated note, 4 November 2026 08:4x (TASKS 174).** The Coriolis term of `src/dpir/qff.py` paired lab-frame ζ with the sorted principal rotational constants until 4 Nov (TASKS 174, fixed in 648a001e). Every stored force-field report and GVPT2 label was rebuilt and every stored read of this registration rerun (`probes/results_m1/coriolis_redo_2026-11-04/compare.md`): no verdict changed, scores moved ≤ 0.04 cm⁻¹. The read of this registration that is still to come uses the fixed code.

## Amendment 5 (4 Nov 2026, 17:4x — before PAHdb's tetracene is read against our numbers): the matching rule for the Mackie line

**What the library holds.** Looked at on benzene's entries only: PAHdb's anharmonic library v1.00 (sha256 `2fb7a776…`, module 02's copy)
lists every VPT2 transition of a species — fundamentals, overtones and combinations — as a frequency and an intensity. It gives no
assignment and no symmetry. Tetracene is uid 282 (C18H12, named tetracene in the library), computed at B3LYP/N07D. That is another basis
than our 6-31G*, so a mean offset between the two carries the basis difference. The rms about the mean is the closer measure of whether
the anharmonic pattern agrees. Route A's data carry no IR intensities, so our side cannot be chosen by intensity.

**The rule** (`probes/pahdb_anharmonic_match.py`, tested on synthetic values first: `tests/test_pahdb_anharmonic_match.py`, 5):
- **Ours:** tetracene's GVPT2 fundamentals as `gvpt2_labels.py` computes them, in 550–2000 cm⁻¹, IR-active only. The modes are labelled
  b1u, b2u or b3u in D2h from the signs of their characters, as `probes/hot_band_desk_naphthalene.py` labels them; a character below 0.9
  in size stops the read.
- **Theirs:** uid 282's transitions at or above 0.5 km/mol, in the same window widened by 25 cm⁻¹ on each side.
- **Pairing:** one to one, with the least total |Δν| (`linear_sum_assignment`). A pair more than 25 cm⁻¹ apart is left unpaired.
- **Reported:** the pairs, the mean and rms of Δν = ours − theirs, the rms about the mean, and the unpaired on both sides. The
  thresholds 0.1 and 2.0 km/mol are reported beside the main read, to show how much the threshold decides.
- No line and no verdict, as registered.

**Rehearsal before tetracene.** Naphthalene is not a target. Its uid 330 entry goes against S2's naphthalene at G
(`probes/results_m1/s2_anharmonic_2026-10-18/s2/A_01f3186607/G`, the force field of TASKS 180) with the same script. If the rule changes
after the rehearsal, the change is dated here before tetracene is read.

**Prediction (before any number).** At 0.5 km/mol, tetracene's rms about the mean is at most 10 cm⁻¹: one in two.

**Rehearsal outcome, 4 Nov 2026 17:4x** (`probes/results_m1/pahdb_match_2026-11-04/pahdb_match_330.json`; WSL `vpt2` environment with the S2 labels' pyVPT2 worktree): naphthalene, uid 330, against S2's naphthalene at G. 13 IR-active fundamentals of ours in the window. At ≥ 0.5 km/mol 11 pair: Δν mean +5.96, rms 8.89, about the mean 6.60, max 15.5 cm⁻¹; the two weakest of ours (799.3, 1169.1) stay unpaired. At ≥ 0.1 all 13 pair (mean +5.94, about the mean 4.90). At ≥ 2.0, 11 pair, and two partners change (1226.5 → 1243.9, 1531.0 → 1518.9; about the mean 9.21). The positive mean is the expected sign for 6-31G* against N07D. The script runs end to end and pairs plausibly at the main threshold. Where the threshold changes a partner, a combination band lies near a fundamental, which is what the two side thresholds are reported for. **The rule is unchanged** for tetracene.

## Amendment 6 (12 Nov 2026, 15:0x — before the read): degenerate pairs from the point group

probes/gvpt2_labels.py treated two modes as degenerate when their ω lay within 0.5 cm⁻¹ (`dpir.qff.degenerate_groups`): it averaged their semi-diagonal quartic constants (the builder's `phi_iijj_sym`, with overlapping pairs along a chain) and left every resonance touching them deperturbed. Degeneracy is a property of the point group: an asymmetric top has none, and a symmetric top's pair stays a pair however far the quadrature splits it. Found on 12 Nov while looking at tetracene's skipped resonances (tetracene is D2h). The labels now take the pairs from the group (`e8_symmetry.degenerate_pairs`: a mode's images under the operations span a plane, its partner is the other mode in that plane; tests/test_e8_symmetry_pairs.py) and average the raw `phi_iijj` over those pairs only. Every set was relabelled by `probes/relabel_sets.py` into `probes/results_m1/labels_symmetry_2026-11-12/` (force fields and selections unchanged; the old labels kept). Window fundamentals (550–2000 cm⁻¹), new minus old GVPT2: S2 G 12 of 432 modes changed by more than 0.05 cm⁻¹, rms 0.31, max 5.08; S2 X rms 4.50, max 64.4 (A_a848c04a21: two modes at 669.6 cm⁻¹ had 726.9 and 603.2, now 662.5 and 667.6); S2b G 43 of 959, rms 1.79, max 34.8 (A_cce0ad25a5); S2b X rms 1.37, max 18.7; S3 G tetracene max 0.67, coronene 11 of 70 modes, max 8.93 (its G labels had 31 pairs by the gap, one true pair split by 0.70 cm⁻¹ missed and a non-degenerate mode 0.2 cm⁻¹ from a pair averaged into it; now 34 pairs on G and X alike); S3 X tetracene 18 of 54, max 6.52. Benzene keeps 10 pairs.

For the read: the training sets and targets are the relabelled ones (`labels_symmetry_2026-11-12/sets.json` and `targets.json`); the S2b read used is its repeat on those labels (S2b amendment 2); a degenerate pair counts once when it is a pair of the point group named in the target's label file (`degenerate_pairs`), not when two modes lie within 0.5 cm⁻¹ — tetracene then has no pair and coronene 34. The models, the line and the verdict rule are unchanged.
