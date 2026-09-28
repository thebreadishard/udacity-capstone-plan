# Pre-registration 2026-09-27 — the wide-candidate deck with a learned order and a stop rule (decision on the user's word, 27 Sep 08:3x: "Akkoord met alles")

*Written on 27 September 2026 before any code changes to `probes/dryrun_dft_delta_recovery.py build_deck`. Build and run after the supervisor conversation
of 28 September. Numbers quoted here come from the standout pattern proposer's experiments E1/E2 of 26–27 September
(`PreRegistration_2026-09-26_Standout_Pattern_Proposer.md`, outcomes; `modules/standout_pattern_proposer/out/sim/{band_p2,all_p2}_readout.md`).*

## Why

The Ladder's deck (`build_deck`: two-mode patterns for pairs within 200 cm⁻¹, plus 4M multi-mode patterns, hashed order) was designed on the band prior.
The proxy corpus (289 molecules, Δ = ωB97X − B3LYP couplings) says two things the deck did not know:

1. only ≈ 45 % of the off-diagonal coupling power lies inside the band (`out/inband_share_2026-09-26.json`); the other half sits between modes of very
   different frequency that move the same atoms;
2. consequently the band deck, measured **in full**, ends at a median ρ_off of 0.53 (parents) / 0.47 (A2/B), while a pool with two-mode patterns for
   every pair, consumed in the hashed order, ends at 0.08 / 0.14 and reaches ρ_off ≤ 0.3 on 38 of 41 parents and 43 of 56 A2/B molecules (band deck: 1 and 3).

Cost, median per molecule (energies; `modules/standout_pattern_proposer/out/sim/deck_cost_2026-09-27.md`): the whole band deck 1,360 (parents) / 1,686 (A2/B); the whole wide pool 6,614 / 8,448 (≈ 5×). Reaching ρ_off 0.3
on the wide pool costs 2,951 / 3,528 energies in the hashed order, **1,831 / 2,560 with the learned order P12** (≈ 1.35–1.5× the whole band deck),
608 / 1,120 with the oracle. Ordering on the wide pool pays 1.3–1.4× on K_off(0.3) and 1.8–2.5× on the halfway point; the deck change pays a factor
that the band deck cannot buy at any budget.

## What changes (to be built after the 28th)

- **Candidates:** two-mode patterns for every pair i < j (the band filter becomes a *prior* of the solver only, as in E2), plus the multi-mode patterns as now.
- **Order:** the learned order — P12 (z-score average of the hand scorer P1 and the learned embedding P2) or whatever the standout search has chosen by
  then on validation; P0 (hashed) is kept as the control column in every run.
- **Stop rule:** measurement stops when the held-out ρ_off (the probe's own read-out, computed from the held-out patterns at every checkpoint, no truth needed)
  falls below a target τ_stop for two consecutive checkpoints, or when the budget B_max is spent. τ_stop and B_max are per-rung constants of the Ladder:
  registered here as **τ_stop = 0.3 and B_max = 2 × (whole band deck)** for the first test; the pilot's noise class (ρ_noise ≈ 0.05) sets the floor τ can
  never sensibly go below.
- **Held-out patterns:** unchanged (the hashed 10 % of the deck) — they are what makes the stop rule truth-free.

## Pass lines and predictions (fixed now)

- **W1 (proxy, no new QC):** on the 97 evaluation molecules of E2, the deck with P12 and the stop rule reaches ρ_off ≤ 0.3 on ≥ 90 % of molecules within
  B_max, at a median cost ≤ 1.5× the whole band deck. Prediction: 1.35–1.5× (E2 numbers); if the stop rule's two-checkpoint hysteresis costs more than one
  stride per molecule the median moves to ≈ 1.6×.
- **W2 (proxy):** the stop rule never stops a molecule whose truth-based ρ_off is > 0.4 (a false stop) on more than 5 % of molecules. Prediction: ≤ 2 %
  (the held-out ρ_off tracked the truth-based Frobenius error on every E1/E2 curve).
- **W3 (CC level, after the 28th, one molecule):** on the anchor's naphthalene, with responses measured at the label level for the patterns the stop rule
  actually asks for, the same stop decision is reached as on the proxy within one checkpoint. This is the first real-cost test and the only one that costs
  quantum chemistry; its budget is set by the cation-price table (34,411 s per energy for the cation, ≈ 4,200 s for the neutral at DZ tight).
- **Fail:** W1 or W2 missed → the deck stays as it is and the finding is written as a limitation of the proxy; the band deck's end point (0.5) is then the
  honest number for the Ladder's cost table.

## Guards

- No number here is a claim about coupled-cluster responses; the proxy is DFT against DFT.
- The change touches the probe's deck builder (tier 1) first; promotion into `src/dpir` goes through the promotion checklist (decision 47).
- `readout.py` and the standout simulation are the read-out machinery; nothing new is written for W1/W2 beyond the stop rule itself and a false-stop counter.
- The run is a simulation on existing exports (`modules/standout_pattern_proposer/out/exports/`): desk-scale on hel1-23 or the laptop, no new corpus work.

## Amendment, 28 September 21:4x — written before any W1/W2 number (the user, 28 Sep: "Akkoord")

**Why.** The CC-level test of 28 September (`PreRegistration_2026-09-28_Standout_CC_Level_Test.md`, outcome 20:3x) found on benzene's real CCSD(T) − B3LYP
correction 4 % of the off-diagonal power inside the 200 cm⁻¹ band (proxy 52 %). The paragraph "What changes" above still makes the band the solver's prior.
That is a claim about the response and it failed on the one real response we have; the Ladder's default must not assume it.

1. **Solver prior.** The Ladder's default becomes the **band-free prior**: the same ℓ₁ recovery with the penalty on every off-diagonal pair (the probe's
   `band_weights` with w = 0: only the diagonal and exactly degenerate pairs are free), λ chosen on the held-out patterns from the registered grid. The band
   prior (w = 200) is kept as the registered comparison column. The CC test's "open prior" run of 20:3x used w = 5000 (no penalty anywhere, prior-free);
   it is relabelled so, and the band-free run (w = 0) of the same benzene test is added tonight so both settings stand on record at CC level.
2. **W1 and W2 are read twice.** (i) *As registered*, from the recorded wide-pool curves (`out/sim/all_p2s1_merged.json`: band prior, P2 = the stage-1
   recipe that the search kept, order P12 seeds 0–2, 97 evaluation molecules), with the stop rule applied at the recorded checkpoints (stride ≈ pool/60,
   ≈ 90–220 energies): no new compute, read first. (ii) *Under the band-free prior*, a new simulation on the laptop with the same molecules, checkpoints and
   orders (P0, P12 seeds 0–2, oracle). Both readings are judged on the registered lines; (ii) is the one that carries the Ladder's default.
3. **Conventions fixed now** (as in `deck_cost_readout.py`, whose numbers the predictions above were computed from): cost = energies beyond the single
   block at the stop checkpoint; "whole band deck" = the band curve's total energies per molecule (single block included, `band_p2s1A_merged.json`);
   B_max = 2 × that number, spent beyond the block; the stop fires at the second of two consecutive checkpoints with held-out ρ_off ≤ τ_stop; a molecule
   counts as reached under P12 when the seed-median cost is defined (two of three seeds), the cost is the seed median. W2's "truth-based ρ_off" is the
   recorded relative Frobenius error of the off-diagonal block against the truth (curve column 4, `frob_off`), read at the stop checkpoint.
4. **W3 (naphthalene).** The primary read uses the frozen-10 CCSD(T) Hessian through `pp.core.hi_override`, as the benzene test did: the response of every
   pattern the stop rule asks for follows from the Hessian, which is the very object Δ₂ targets. Label-level energies for the asked patterns are a spot check
   (a handful, ≈ 1.2 h each on the CCX53), on the user's word and budget; they are not needed for the stop decision. W3's pass line is unchanged.
5. **Prediction for the band-free prior (ii), on record.** The band prior helped the solver on the proxy (half the power in band); without it the early
   curve is slower and the end point the same. Median cost to the stop under P12: 1.1–1.3× the band-prior reading, W1 still within 1.5× of the whole band deck on
   the parents and at most 1.7× on A2/B; W2 unchanged (≤ 2 % false stops); the oracle's cost within 1.1× of its band-prior value. If the band-free reading
   misses W1 while the band-prior reading passes, the honest Ladder default is the band-free one and the line reads "target reached at n× the band deck";
   the band prior does not come back on proxy evidence.
6. **Code (tier 1).** `pp.core.stop_rule` (one function, used by the reader now and by the Ladder later), `stop_rule_readout.py` (W1/W2 from a wide-pool
   record and its band record), `run_simulation.py --w-cm` and `--only` (curves for a subset of orderings), and `probes/dryrun_dft_delta_recovery.py
   --deck-pool all` (two-mode patterns for every pair; the band remains a solver setting). Tests for each switch before the run.

## Outcome, reading (i) — 28 September 21:5x: as registered, band prior, from the record (`modules/standout_pattern_proposer/out/sim/stop_rule_band_prior_2026-09-28.{json,md}`; `stop_rule_readout.py` on `all_p2s1_merged.json` against `band_p2s1A_merged.json`, 97 molecules)

**W1 FAIL, W2 FAIL.** Under P12 the stop rule fires within B_max on **51 of 97 molecules (53 %)** — the line asked ≥ 90 %.
Among those that stop, the cost is 1650 energies beyond the block, 1.06× the whole band deck as a ratio of
medians (flattering, because it is conditional on stopping) and 1.36× as the median per-molecule ratio, which is the registered
prediction's range (1.35–1.5×); the 90 % line was the wrong part of the prediction: half the molecules need more than twice the band deck. P0 stops on 28 %,
the oracle on 75 % at 0.56× (parents 63 % / A2-B 45 % for P12).
**False stops: 15 of 51 (29 %) under P12** — the line allowed 5 %, the prediction said ≤ 2 %; P0 89 %, the oracle 3 %.
The hysteresis costs one stride (median 110 energies).

**Why the false stops.** The held-out set of the wide pool is the band deck's (benzene: 38 in-band two-mode patterns and 23 multi-mode patterns; it touches
52 % of the in-band pairs and 34 % of the out-of-band pairs). At the moment the held-out ρ_off crosses 0.3, the truth-based off-diagonal error sits at a
median 0.34 under P12 (P0 0.46, oracle 0.26) — the two scales meet near the line, and under an order that serves the band first the held-out set reads
ahead of the truth. It is a threshold relation, not blindness: over all recorded checkpoints, ρ_off ≤ 0.3 with frob_off > 0.4 occurs on 13 % (P0), 2 % (P12),
0 % (oracle), and at the end of the pool the two agree (0.11 / 0.08). The prediction "the held-out ρ_off tracked the truth on every curve" was true of the
curves as a whole and false at the crossing.

**Consequence, per the registered fail clause.** The deck stays as it is; the wide deck with *this* stop rule is not licensed on proxy evidence; the band
deck's end point remains the Ladder's honest number (median ρ_off 0.53 / 0.47 on proxy, 0.78 on benzene at CC). What would be tried next is a new registration,
not a rescue of this one: τ_stop set with a margin on the scorer's validation split (never on these 97 molecules), the held-out patterns drawn from the whole
wide pool, B_max reconsidered against the measured distribution of costs — to propose to the user. Reading (ii) (band-free prior, same molecules, P0 / P12 /
oracle) was launched at 21:57 on the laptop as committed above (8 shards, `out/sim/all_p2s1_w0_shard*`); it is read on the same lines when it lands.
Benzene at CC with the band-free prior (`out/cc/A_8448043181_cc_test_all_band0.md`): the oracle reaches 0.3 at 372 energies as with no prior, P0 at 558
(band prior 1,116; no prior 1,054) — on the one real response the band-free ℓ₁ halves the blind order's cost.
