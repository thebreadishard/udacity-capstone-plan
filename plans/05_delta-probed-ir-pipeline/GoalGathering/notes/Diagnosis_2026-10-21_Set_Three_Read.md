# Why anchor set three read negative — a night of diagnosis (21 October 2026, 00:20–05:00)

*Asked by the user on 21 Oct 00:1x: "Ligt het aan te weinig data? Ligt het aan de hyperparameters? Ligt het aan de kop, het aantal hidden
layers, het type netwerk? Aan het gebrek aan embedding? … Ga door met tenminste twintig ideeën." Exploratory: no registered line is tested
here, and every choice below was read on the same eleven anchors the registered read used — so these numbers motivate a registration, they
do not replace one.*

**Records.** `modules/05_support_predictor/out/set3_diagnosis_2026-10-21/` (git-ignored, mirrored to capstone-data): one
`rungC_cc_transfer.py` record per run, `diagnosis.{json,md}` (`probes/set3_diagnosis.py read`), `analyses.json`
(`probes/set3_analyses.py`), `decompose.json` (`probes/set3_decompose.py`). Every run holds each of the eleven carried TZ anchors out in
turn (pool 10), one fine-tune mode, chain 34's carried model, 300 epochs, lr 1e-3, 6 threads, on a copy of the eleven anchors' corpus
folders (validated: within 3.2e-6 cm⁻¹ of the set-three record, 8 threads there). Numbers are means over the held-out folds: corrected-ω
rms per family (cm⁻¹), matched intensity rel. rms over the anchors with a CC APT, ring-coupling ratio. Seed 0 unless "3 seeds" (mean ± sd).

## The answer in short

1. **The main cause is the transfer protocol, not the data.** The registered transfer trains only the head's last layer (+ α), pulled
   toward the proxy-trained weights (λ = 1). On the frozen penultimate features that last layer cannot represent the CC out-of-plane
   correction even on the anchors it is trained on: in-sample, CH-oop stays at 7.76 (W06), while the whole head fits it to 0.80 (E18).
   Held out, training the whole head halves the error (3 seeds): CH-oop 12.29 ± 0.21 → **6.54 ± 0.47**, 'other' 12.02 ± 0.25 → **6.35 ±
   0.25**, ring-ip 4.33 → 2.55, matched intensity 0.322 → **0.206**, ring-coupling ratio 0.94 → 0.51. Robust to epochs (100: 5.85), lr
   (3e-4: 6.16) and base model (n 972: 6.80; analytic labels: 6.70). A rank-4 adapter in the middle is in between (7.84).
2. **The λ = 1 pull costs, monotonically; where it pulls does not matter.** CH-oop 9.63 (λ 0), 10.98 (0.1), 11.52 (0.3), 12.18 (1), 12.82
   (3), 13.26 (10); 3 seeds: λ 0 9.61 ± 0.46 against λ 1 12.29 ± 0.21. Pulling toward the proxy's weights, toward zero or toward −0.6 ×
   the proxy's gives the same ~12.2 (W01–W04); at λ 0 the last layer's start does not matter either (9.55–9.63).
3. **Data: with the old protocol more anchors do not help; with the whole head they do.** Set three's R-A was flat (−2.6 %). With the whole
   head, on the original six (3 seeds): CH-oop 7.37 ± 0.88 with their own five as the pool (W15) against 6.22 ± 0.50 with ten (E16): −16 %,
   about two combined standard errors — at the edge; 'other' 8.31 ± 0.28 → 7.77 ± 0.17; intensity 0.107 ± 0.005 → 0.086 ± 0.007 (−20 %,
   clear). More proxy-pretraining data or other labels change little: at λ 1 the base models read 11.5–12.7 (n 972, analytic labels,
   coverage n 912, five rings n 972, hinge) against 12.18; at λ 0, 9.00–9.08 against 9.63; with the whole head 6.70–6.80 against 6.02.
4. **Network type, layers, embedding: no sign that the body limits.** The untuned network reproduces the proxy on these eleven molecules
   (CH-oop 1.81, 'other' 1.43 cm⁻¹ against ωB97X; A4), and with its head free it fits the CC correction in-sample to 0.8 cm⁻¹ (E18). What
   limited was the frozen head, not the encoder or its embeddings.
5. **The target is unlike the proxy where it matters.** In the out-of-plane families the CC/TZ correction is the small difference of two
   large parts — the method part (CC/DZ − B3LYP/6-31G*, rms 57–90 cm⁻¹ in CH-oop) and the composite's MP2 basis step (rms 56–73), of
   opposite signs (A7) — and it runs against the proxy: the least-squares factor on the proxy is −0.59 for every anchor (A2), the CC
   shifts correlate negatively with the proxy's in 'other' on 10 of 11 anchors (A3). The untuned network predicts the proxy (CH-oop 33.2,
   as the proxy itself, 32.8 — E07, A1). This is why the last layer alone, kept near the proxy, cannot get there.
6. **The anchors' own accuracy is near the new error.** Test 2's composite against the full CC/TZ anchor on benzene: CH-oop 7.30, 'other'
   3.32 (A5) — one molecule. The network's per-anchor error follows the size of the anchor's basis step (r +0.69 CH-oop, +0.77 'other';
   n 9, A8). Below ~6–7 cm⁻¹ in CH-oop the anchors may not tell a better model from a worse one.

**Caveats.** All choices were read on the eleven anchors the registered read used (no independent CC anchors exist before July 2027, decision
63); seeds 0–2 only for E01, E02, E16, W15; the floor is one molecule; the two five-ring anchors stay the worst with the whole head (azulene
CH-oop 9.8, acenaphthylene 10.2), and benzonitrile's 'other' (the CN modes, no other anchor has them) barely moves (25.2 against 26.1).

## The ideas, one by one

| # | idea (question) | run | result (CH-oop / other / ring-ip / CH-stretch / intensity) | reading |
|---|---|---|---|---|
| A1 | is the proxy itself a good guess for CC? (target) | proxy as prediction | 32.78 / 25.25 / 28.90 / 77.76 / 0.36 | far worse than the zero rule (14.83 / 16.08 / 15.93 / 34.76 / 0.333) |
| A2 | is CC a scaled proxy? (target) | c·proxy, leave-one-out | c = −0.59 (−0.58 to −0.66); 11.82 / 11.11 / 16.12 / 8.86 / 0.37 | one negative factor beats the tuned network in CH-oop and 'other' |
| A3 | do CC and proxy agree mode by mode? (target) | K_kk correlation per family | CH-oop −0.05 to −0.58 on 10 of 11; 'other' −0.13 to −0.77 on 9 of 11 | anti-aligned in the out-of-plane families |
| A4 | does the network know the proxy here? (network type, embedding) | untuned net vs ωB97X truth | 1.81 / 1.43 / 1.54 / 0.78 / 0.075 | yes: the pretraining worked |
| A5 | how exact are the anchors? (data quality) | test 2 composite vs CC/TZ, benzene | 7.30 / 3.32 / 3.29 / 4.37 | a floor of a few cm⁻¹ |
| A6 | how far does the basis step move each family? | CC/DZ read against TZ (9 anchors) | 56.0 / 40.0 / 30.2 / 132.4 | the TZ truth rests on the MP2 step |
| A7 | which part runs against the proxy? | method part vs basis step | method rms 57–90 (CH-oop), step 56–73, opposite signs; 'other': method −0.33 to −0.99 with the proxy, step +0.44 to +0.99 | a near-cancellation of two large terms |
| A8 | does the error follow the step? | per anchor, E01 | r(error, step rms) +0.69 / +0.77 (n 9) | larger step, larger error (confounded with size) |
| E01 | reference (λ 1, last layer) | 3 seeds | 12.29 ± 0.21 / 12.02 ± 0.25 / 4.33 / 2.78 / 0.322 | |
| — | zero rule; α scaling without a network | | 14.83 / 16.08 / 15.93 / 34.76 / 0.333; 12.90 / 7.46 / 7.29 / 6.34 / 0.333 | α scaling beats the network in 'other' |
| E02–E06 | λ 0, 0.1, 0.3, 3, 10 (hyperparameter) | | 9.63, 10.98, 11.52, 12.82, 13.26 (CH-oop) | monotone: less pull is better |
| E07 | no fine-tune | | 33.24 / 25.55 / 28.93 / 77.61 / 0.329 | the proxy, as A1 |
| E08 | α only | | 13.62 / 13.89 / 6.78 / 7.70 / 0.384 | |
| E09, E10 | lr 3e-4, 3e-3 (λ 1) | | 12.08 / 10.77; 12.41 / 14.31 | small |
| E11, E12 | 100, 1000 epochs (λ 1) | | 12.09 / 10.82; 12.77 / 14.54 (intensity 0.391) | 1000 epochs overfits a little |
| E13, E14 | aux weight 0, 3 (λ 1) | | 13.33 / 12.77; 11.56 / 10.83 | the auxiliary term helps a little |
| E15 | rank-4 adapter in the head's middle | | 7.84 / 7.00 / 3.74 / 2.72 / 0.213 | more trainable head, better |
| E16 | the whole head trainable (head) | 3 seeds | 6.54 ± 0.47 / 6.35 ± 0.25 / 2.55 / 2.27 / 0.206 | the best held-out read |
| E17 | in-sample, λ 1 (capacity) | | 11.65 / 9.83 | λ 1 cannot fit even the training anchors |
| W06 | in-sample, λ 0, last layer (capacity) | | 7.76 / 5.65 / 2.06 / 2.66 / 0.205 | the last layer cannot fit CH-oop in-sample |
| E18 | in-sample, whole head (capacity) | | 0.80 / 0.52 / 0.68 / 0.44 / 0.054 | the network can represent it |
| E19–E23 | other base models at λ 1: analytic labels, n 972, hinge, coverage n 912, five rings n 972 (data, labels, type) | | 11.98, 11.95, 11.52, 11.72, 12.65 | ±1 around 12.18 |
| W09, W10 | analytic labels, n 972 at λ 0 | | 9.00, 9.08 | ~0.6 better than chain 34 at λ 0 (seed 0) |
| W13, W14 | n 972, analytic labels with the whole head | | 6.80, 6.70 | no gain over chain 34 (6.02) |
| W11, W12 | whole head, 100 epochs; lr 3e-4 | | 5.85 / 6.23; 6.16 / 6.75 | robust |
| W01, W02 | last layer zeroed; × −0.6, λ 0 (prior direction) | | 9.55, 9.57 | the start does not matter |
| W03, W04 | × −0.6; zero, λ 1 (prior direction) | | 12.21, 12.18 | the pull's strength matters, not its target |
| W05 | untuned, last layer × −0.6 | | 18.66 / 20.50 | a reversed proxy is still poor |
| W15 | whole head, the original six alone (data) | 3 seeds | 7.37 ± 0.88 / 8.31 ± 0.28 / intensity 0.107 | against E16 on the same six: 6.22 ± 0.50 / 7.77 ± 0.17 / 0.086 |

## What this suggests registering (for the user's word)

- **The whole-head transfer as the candidate standard**, with lines fixed before its read: set three's R-A, R-B and arm-M reads repeated
  with `--head-all`, on fresh seeds (3–5). Honest label: a confirmatory read of a protocol chosen on the same anchors, not independent.
- **An independent check without CC anchors:** the same few-anchor fine-tune (whole head vs last layer, 10 molecules) on a second proxy
  correction, read on hundreds of held-out corpus molecules — the two-DFT proxy proof of decision 63. It tests whether the whole head
  generalises from ten examples where thousands can grade it.
- **The anchors' floor:** a second composite-vs-full-CC/TZ comparison would need new CC (frozen); until then, read CH-oop differences
  below ~2 cm⁻¹ as unresolved.
- **The pretraining target:** a proxy closer to the CC correction in the out-of-plane block (e.g. a basis-set step at the DFT level at
  the corpus geometry) is an idea, not tested here.

## The night's incidents

The cation run (P3-2) stopped itself at 01:40 after three failures in a row from commit-memory exhaustion; two of the three are mine (ledger
of 20 Oct 19:47 and 21 Oct 01:40). It waits for the user's word; nothing else ran beside the diagnosis after 01:43.
