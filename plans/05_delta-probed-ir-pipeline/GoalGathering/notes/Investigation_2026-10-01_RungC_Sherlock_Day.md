# Investigation log, 1 October 2026 — why does every rung-C head stop at a ring-coupling ratio ≈ 0.42?

*The user, 07:5x: "Wees Sherlock Holmes vandaag en onderzoek structureel, een voor een, alle opties die je veelbelovend lijken. Stop niet." This file
is the running log of that day: one hypothesis per row, the test that decides it, the number, the status. Each run is registered in
`PreRegistration_2026-09-25_RungC_Equivariant_vs_Pair_Model.md` before it starts (dated amendments); the ledger keeps the outcomes; this file keeps
the chain of reasoning. Read-outs as everywhere: (a) = hold-out of 10 scaffold cores, ring-coupling ratio against the zero rule, ω = corrected
frequency rms in cm⁻¹.*

## The fact to explain

| model | data | (a) ratio | ω | source |
|---|---|---|---|---|
| pair model, rung B (hand-made features) | 175 | 0.43 | 4.8 | 27 Sep |
| equivariant, Cartesian head (C1, C2) | 175 / 449 / 750 | 0.81 / 0.83 / 0.82 | — | 30 Sep |
| hybrid head, pattern (c), carried recipe | 175 / 750 | 0.43 / 0.431 | 4.44 / 4.30 | 1 Oct 05:0x, 06:1x |
| hybrid head, pattern (d) | 175 | 0.40 (0.39–0.42) | 4.7 (4.1–5.8) | 1 Oct 07:3x |

Three heads with different inductive biases, two data volumes, one recipe search: the same floor. Something shared stops them.

## Hypotheses and their tests

| # | hypothesis | test | number | status |
|---|---|---|---|---|
| H1 | the head cannot express the correction (pattern too narrow) | overfit one molecule, 5,000 steps: what remains is expressiveness | benzene: pattern c 0.15 → pattern d **0.02** (ΔH residual 0.079 → 0.007) | **ceiling confirmed and removed on benzene**; at 175 the gain is 0.43 → 0.40; 750 running |
| H2 | the targets are noise (finite-difference Hessians of the corpus deck) | 27 two-route molecules: FD ΔH read as a prediction of the analytic ΔH, `probes/rungC_target_noise_floor.py` | typical molecule **0.07–0.16** (ΔH residual 0.02–0.08); benzene 7.98, pyridine 0.50, one suspect 3.00 — all three carry analytic targets in training (`--use-analytic`) | **rejected as the 0.42**: the noise floor of a typical target is ≈ 0.1 |
| H3 | an input never reaches the network (ablation = dead wire) | sensitivity at initialisation, `tests/test_rungC_input_wiring.py` | H_low → 0 changes the output by 46 % (Cartesian) / 24 % (hybrid); rank-2 rows carry gradient | **rejected**: the ablations are learned indifference |
| H4 | the encoder is the floor: 171k parameters trained from 175–750 molecules cannot form the environment the head needs | (2a) QM9-pretrained mean body under the hybrid head vs a fresh mean body, pattern d, 175; (2b) the same pretraining for 20 epochs (running since 08:04 on six cores, ≈ 13:00); (2c) capacity | — | 2a queued behind lever 1; 2b pretraining running; 2c to build |
| H5 | the pattern ceiling is benzene-specific | overfit naphthalene, 2-methylnaphthalene, styrene with pattern d | — | registered 08:0x, queued behind lever 1 (`rungC_sherlock2_1001.sh`) |
| H6 | early stopping cuts the fit (decision 51) | best epoch vs the cap in every record | lever 1 at 175: best epochs 97 / 30 / 140 of the cap 200 (patience 20 on the inner validation) | **not binding** on the cap; seed 1's early stop (30) is the seed with the worse ω — patience is a lever to keep in view |
| H7 | the (a) read-out is dominated by one or two of its ten molecules | per-molecule ratio of the best model on hold-out (a) | — | every record since 07:5x carries `per_molecule` (test); first read from chain 2 |
| H8 | the loss is not the read-out quantity | lever 3: `--aux kring`, the term on the ring-mode block of K itself (tested against `k_of`), pattern d, 175, 3 seeds, against lever 1's 0.40 | — | built, registered 08:1x, queued behind chain 2 (`rungC_sherlock3_1001.sh`) |

## Decisions carried from the day

(filled as they fall)
