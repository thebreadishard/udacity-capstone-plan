# Does more data still pay? The data-volume curve at fixed composition (15 Oct 2026, TASKS 58, desk only)

*The 30 Sep verdict 'data volume moves neither rung' was withdrawn on 14 Oct (read on curves held at a target floor). TASKS 58: refit the post-fix
curves per family and per hold-out, and price a further decade. No new training: existing records, `probes/rungC_learning_curve_fit.py
--families` (15 Oct: per-family read-outs and a pool-composition check, tests in `tests/test_rungC_learning_curve_fit.py`).*

## The curve

The carried recipe of 2 Oct (pattern f, projected target, kring 0.3; FD labels; 200-epoch cap, best epochs 29–94) at three nested pool sizes of
one hashed order of the mixed pool: 175 (chain 20, `E7_rungC_carried_mixed175_2026-10-01`), 449 (chain 18), 750 (chain 17,
`E7_rungC_lever3b_fproj_kw0.3_750_2026-10-01`). **Layer shares 175: A2 0.21 / B 0.79; 449: A 0.03 / A2 0.19 / B 0.78; 750: A 0.04 / A2 0.19 / B
0.77 — spread 0.04, a count curve at fixed composition.** Fit `mixed_fixed_composition.{md,json}` (seed bootstrap, 68 % bands).

| hold-out | read-out | 175 → 449 → 750 | factor per decade | at 7,500 (one decade on) |
|---|---|---|---|---|
| (a) | corrected ω rms (cm⁻¹) | 5.75 → 4.58 → 3.50 | 2.13 | 1.7 (1.4–2.2) |
| (a) | ring-coupling ratio | 0.275 → 0.235 → 0.216 | 1.46 | 0.148 (0.140–0.157) |
| (a) | CH-oop diagonal | 6.07 → 4.53 → 3.84 | 2.06 | 1.9 (1.5–2.2) |
| (a) | other | 7.97 → 7.29 → 5.02 | 1.95 | 2.8 (2.3–3.3) |
| (a) | ring-ip | 2.87 → 2.44 → 2.37 | 1.36 | 1.7 (1.5–2.0) |
| (a) | CH-stretch | 7.51 → 4.14 → 3.46 | 3.51 | 0.9 (0.5–2.0) |
| (b) | corrected ω rms | 6.70 → 5.17 → 4.41 | 1.93 | 2.3 (2.0–2.7) |
| (b) | ring-coupling ratio | 0.367 → 0.347 → 0.333 | 1.17 | 0.286 (0.272–0.301) |
| (b) | CH-oop diagonal | 6.76 → 5.93 → 3.94 | 2.20 | 2.0 (1.6–2.4) |
| (b) | other | 10.42 → 7.55 → 8.49 | 1.47 | 5.3 (3.7–7.4) |
| (b) | ring-ip | 3.37 → 2.90 → 2.80 | 1.35 | 2.0 (1.8–2.3) |
| (b) | CH-stretch | 9.85 → 5.30 → 5.09 | 3.02 | 1.6 (1.0–2.4) |

**Reading.** Data volume still pays, steeply, on the frequencies: ω falls by about a factor two per decade on both hold-outs, and the two open
families of decision 53 respond — CH-oop on both hold-outs (≈ 2.1× per decade, under 3 cm⁻¹ well before a decade), 'other' on seen scaffolds
(a). 'Other' on unseen scaffolds (b) is the exception: shallow and noisy (the 449 → 750 step goes up), the coverage gap of 3 Oct, which count
alone does not close. The ring-coupling ratio falls on (a) (1.46 per decade) and barely on (b) (1.17).

**The 2 Oct fit was not a count curve.** It put chain 14b's 175 (A + A2 only, layer A 0.19) beside the B-heavy 449/750 (composition spread 0.78
on layer B) and read factor 1.17 / 1.69; chain 20 then withdrew the mixed curve as 'count conflated with composition', but chain 20's own 175 point
is the fixed-composition one, and the curve through it was never fitted. Chain 21's 'fixed composition' A + A2 curve (45 / 100 / 175) is not fixed
either — layer A goes 0 → 0.13 → 0.19 (`aa2_fixed_composition.{md,json}`, flagged by the new check).

## The price of a decade (750 → 7,500 at the same composition)

Labels by the analytic route, priced on the labels server's own lane fit (`probes/price_large_labels.py`, 387 lane times, 100–307 basis functions;
the pool's molecules sit inside that range: layer B mean 185, A2 mean 249 functions → 1.29 and 3.10–3.13 lane-hours per molecule): **≈ 10,700
lane-hours ≈ 111 days of the CCX53 (4 lanes) ≈ €2,290** at its rental price. Not enough candidates exist at this composition: it needs ≈ 5,200
B and ≈ 1,280 A2 rows; 3,610 and 605 are pending. A desktop of the CCX53's class runs the same decade in about the same months; its own throughput
is not measured.

## Caveats (stated, not resolved)

- Three points over 0.63 of a decade, three seeds; the extrapolation is one decade further.
- The recipe is the 2 Oct one on FD labels; the carried model of chain 34 is better at 750 (`E7_rungC_chain34_kdfamily_750_2026-10-05`: ω 2.48 on
  (a), 3.52 on (b), seed means, against 3.50 / 4.41 here), so today's curve sits lower; its slope is not measured.
- Layer A (the parents, hold-out (a)'s kind) grows 0 → 4 %; hold-out (b) is not of that kind and shows the same ω slope.
- Proxy level (B3LYP → ωB97X), not CC; what volume buys at the CC level runs through T3.
