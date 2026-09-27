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
