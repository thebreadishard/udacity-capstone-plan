# Pre-registration — chain 42: the mandate's four shape molecules as a size test, and six large PAHs in the corpus (12 October 2026)

*Registered before any of the ten molecules was optimised or labelled. Lever 5 of the odds of 12 Oct; the user, 12 Oct: 'prijs hefboom 5 maar
en zet het sowieso op de takenlijst', 'Akkoord op de servertijd voor hefboom 5', 'Schrijf de registratie voor hefboom 5 maar'. TASKS 49.*

## Why

The mandate wants spectra of large PAHs: the jet-cooled shape molecules coronene, peropyrene, ovalene and hexa-peri-hexabenzocoronene (HBC)
have 36–60 atoms. The corpus stops at 30 atoms. Chain 39 (9 Oct) found a steep size penalty: trained on ≤ 20 atoms, the network's
ring-coupling ratio on the ≥ 27-atom molecules was 0.690, against 0.352 for a same-size control (q = 1.96). Size and ring count were confounded
there. Chain 41 (registered 11 Oct, runs ≈ 23–25 Oct) separates them at 32–40 atoms on pool 3's five-ring neutrals. This chain asks the
question the mandate asks, on the mandate's own molecules, at DFT level:

1. **How far does the network carry the correction to the four?** This is the size penalty measured on the evaluation molecules themselves.
2. **Do six large PAHs in the corpus reduce that penalty?** This is the lever: put the target sizes in the cheap corpus.

The level is the DFT–DFT proxy: ωB97X − B3LYP at 6-31G*, analytic Hessians. It is not CC. The four are never anchors, and at CC level they
remain out of reach (the top-rung estimate of 8 Oct).

## Sets — frozen now

Rule and selection: `probes/large_pah_select.py` → `probes/results_m1/large_labels_price_2026-10-12/selection.json`, from PAHdb v4.00
(theoretical, B3LYP/4-31G geometries).

**Test set T, layer T, never trained (`E6.splits` refuses it):** the four, each matched to PubChem's structure by its carbon skeleton. Each has
exactly one PAHdb entry:

| molecule | PubChem CID | PAHdb uid | formula | atoms |
|---|---|---|---|---|
| coronene | 9115 | 18 | C24H12 | 36 |
| peropyrene | 9103 | 2294 | C26H14 | 40 |
| ovalene | 67446 | 4 | C32H14 | 46 |
| HBC | 136001 | 105 | C42H18 | 60 |

**Training set D, layer D:** one molecule per target size (34, 38, 42, 44, 48, 54 atoms). The candidates must be:
- neutral and closed-shell (RB3LYP);
- carbon and hydrogen, with no CH2 or CH3;
- free of a coronene skeleton, because three of the four test molecules contain coronene;
- not one of the four.

The first candidate by the sha1 of its uid is taken:

| atoms | PAHdb uid | formula | candidates |
|---|---|---|---|
| 34 | 284 | C22H12 | 3 |
| 38 | 538 | C24H14 | 13 |
| 42 | 2281 | C26H16 | 40 |
| 44 | 2221 | C28H16 | 55 |
| 48 | 1931 | C30H18 | 96 |
| 54 | 1021 | C34H20 | 309 |

Ids are the layer plus the first 10 hex digits of the sha1 of the skeleton (`probes/large_pah_jobs.py`). The test ids go to the id file for
`rungC_eval_saved --eval-ids-file`.

## Labels

1. **Geometry:** the corpus deck's own optimisation (psi4, B3LYP/6-31G*, deck v1) from the PAHdb geometry, through `corpus/psi4_worker.py` with
   `"hessians": false`. The water smoke passed on 12 Oct.
2. **Hessians:** `corpus/analytic_hessians.py` at the labels route's settings (both functionals, grid (99, 590), Cartesian d). This includes
   the residual-checked APT (TASKS 44 a).
3. **Folders:** each folder is marked `labels: analytic_only` and enters only under `--use-analytic` (`E6.load_corpus(analytic_only_ok)`;
   12 Oct, the existing corpus loads bit-identically).
4. **Guard on minima:** a molecule with a vibrational frequency below −20 cm⁻¹ in either analytic Hessian is not used as it stands. It is
   re-optimised once with pyscf at the label settings; the record names it. Owed before the run: `result.json` must carry
   `n_imaginary_b3lyp/wb97x` from the analytic frequencies, because the loader reads its imaginary flag there and the psi4 step writes none
   without Hessians.

## Arms — chain 34's carried recipe (v1.1), `--use-analytic`, `--sizes all`, seeds 0, 1, 2

Both arms train on the whole pool as it stands at run time: layers A, A2, B, after chain 40's merge. The pool's size and sha256 of its id list
are recorded. Pool 3's ids are excluded as in chain 41.

- **Arm 0:** `--pool-layers A,A2,B`.
- **Arm D:** `--pool-layers A,A2,B,D`. The same pool plus the six; nothing else differs.

## Read and lines

`rungC_eval_saved.py` per checkpoint, `--eval-ids-file T=<test ids>` beside hold-out (a), seed means. The metric is the registered rung C read-out,
the ring-coupling ratio r.

**Line 1 — the size penalty on the four:** q_T = r₀(T) / r₀(a), arm 0's ratio on T against its ratio on hold-out (a). The latter is a set of
unseen corpus molecules at corpus sizes. The thresholds are the same as chains 39 and 41:
- **q_T ≤ 1.3 carries.** The network takes the correction to the mandate's molecules at modest cost.
- **q_T ≥ 1.8 is steep.** The mandate's spectra then need the target sizes in the corpus, or another route.
- **Between** is noted.

**Line 2 — the lever:** g = r_D(T) / r₀(T).
- **g ≤ 0.85:** six large molecules measurably reduce the error on the four, and the lever works. The next step is a larger layer D, priced
  per molecule.
- **g ≥ 0.95:** six do not move it. This is **not** read as 'the lever fails'. Six molecules in a pool of about 1,000 is one point on a
  curve, and a null at six calls for a second point (≈ 20) before any conclusion (the standing rule: no verdict on tiny data).
- **Between** is noted.

**Reported beside, without lines:**
- per molecule of T, the corrected ω rms, the four families' rms, and the zero rule;
- the same on hold-out (a) and (b) for both arms, as a check that the six do not cost the corpus anything;
- with the four's refined APTs, the spectrum overlap and the intensity rel. rms (matched by eigenvector) against the zero rule.

## Order, cost and stop rules

- **When:** on the CCX53 after its labels (≈ 22–26 Oct). Price: `probes/price_large_labels.py`, from the server's 387 lane times, t ∝
  nbas^3.4. In total ≈ 355 lane-hours ≈ 3.7 days on four lanes ≈ €75 (the user's word of 12 Oct).
- **Order:** coronene first, alone. It is the measurement of time and memory beyond the 307 basis functions the price model has seen
  (coronene has 384).
- **Stop rule:** coronene's lane time above 30 h (twice the 15 h predicted), or peak memory above 100 GB, stops the chain. It is re-priced
  before any further molecule, and the user decides again. The rest then follows by size, HBC (666 functions) last.
- **Optimisations:** they need psi4 where they run. Either the qc env on the CCX53 (bootstrap script) or the pool 3 box once it is free;
  decided at the switch, recorded.
- **Training and reads:** six trainings, about the time of chain 40's.

## Owed before the run

- `n_imaginary_*` in `result.json` from the analytic frequencies (see Labels).
- A smoke of the whole folder path on one small molecule: psi4 optimisation without Hessians, then `analytic_hessians.py`, the loader under
  `--use-analytic`, and `rungC_eval_saved --eval-ids-file`.
- The run as a chain-runner spec (`probes/runs/chain42.json`, dry-run).

## Outcome

*(appended after the run)*
