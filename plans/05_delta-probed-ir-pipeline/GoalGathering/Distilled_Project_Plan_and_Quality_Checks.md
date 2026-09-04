# Distilled project plan and quality checks — Plan 05

Agrees with [Overarching_Goal.md](Overarching_Goal.md), whose glossary defines every symbol
used here; the Goal file wins on drift. Revised 2026-09-04 after Round-8 (A, B), Round-9 (A, B)
and Round-10 Pass A. Opponents: [Frozen_Lines_to_Beat.md](Frozen_Lines_to_Beat.md).
Rungs, licences and stop conditions: [Frozen_Ladder_and_Tolerances.md](Frozen_Ladder_and_Tolerances.md).
Costs: [Compute_Budget_2026-09-03.md](Compute_Budget_2026-09-03.md). Modules:
[Capstone_Mapping.md](Capstone_Mapping.md) (Pass 6 not done). Side project:
[Side_Project_2026-09-04_ModeG_Gradients.md](Side_Project_2026-09-04_ModeG_Gradients.md).

**Status.** Draft, 2026-09-03; revised the same day after Round-7 Pass A and Pass B; amended
2026-09-04 by the user's decisions and revised the same day after Round-8, Round-9 and Round-10
(both passes each). Not complete as a plan. Nothing here is a result.

---

## §1 Claim

A per-molecule pipeline — DFT geometry, analytic DFT Hessian and dipole derivatives, DFT cubic
and semi-diagonal quartic constants on a resonance-closed family set, plus a **probed
coupled-cluster correction Δ₂ to the harmonic force constants**, recovered with the structural
prior from K local-CC responses with frozen spaces (mode E on every rung; mode G in addition
where licensed) — produces IR **band positions** that, on the gas-phase rungs — R0 unconditionally, R1 per family under the Ladder §2 rule, its C–C families expected inconclusive by construction on the hot-vapour NIST sources unless a hot-band correction is pinned — **agree with
the known truth within the stated margin (primary) and beat the frozen lines under the
pre-registered paired comparison (secondary)**; on R2–R3 the beat comparison runs per family
under the Ladder §2 decidability rule (measured band-centre uncertainty against the beat
margin), and only where the Q6 noise line of the mode used passed at that size class, all
others pre-declared inconclusive — **the R2 C–C families are expected inconclusive by
construction on the NIST gas scoreboard, and the plan says so before the pilot note**. On reach
rung R6 — as fragment-probed Δ₂ under the Ladder §3 fragment licence, conditional on B3 — it
produces a labelled theory-vs-theory spectrum with an uncertainty statement that is explicitly
an extrapolation. **For every rung and mode that ran, the cost record (Ladder §1) is part of the
claim.** A size sentence is written only under Ladder §1's conditions. No CC correction to
anharmonic constants is claimed. Intensities are reported, not part of this claim.

If a gate fails, the claim is the fail-closed sentence of §8, not a quieter product.

## §2 Question and positioning

> What does a coupled-cluster correction to the harmonic force constants buy, per band, on
> top of the best available DFT-level IR prediction — and how many coupled-cluster evaluations
> did that correction need, per rung (K_off in mode E on every rung; K in mode G where licensed)?

| Neighbour | Already does | This plan still asks |
|---|---|---|
| PAHdb v4.00 (line A) | scaled-harmonic breadth to C₃₈₆ | quantify and beat its per-band error |
| Mai 2025 (line C) | MLMD anharmonic to C₂₁₆, T-dependent | beat its *teacher* where lab data exists; meet it theory-vs-theory on reach rungs |
| Lam 2020 (bib 13) | QM harmonic + ML anharmonic, 37 small molecules, RMSD 21–23 cm⁻¹ | CC-anchored, per molecule, at PAH sizes, without relaxing tolerances |
| Ethereal AI (bib 7) | ML-corrected scale factors | reproduce as M04; anharmonicity must beat *corrected* harmonic |
| **Concordant Mode Approach** (bib 42–43) | CCSD(T) diagonal force constants in a low-level (B3LYP/MP2) normal-mode basis from single-point energies, off-diagonals selected by a cheap diagnostic (CMA-2); canonical CC, molecules to ~17 atoms; diagonal-only fails on aromatic ring modes by ±20–28 cm⁻¹ | the same object as a **difference** (Δ₂ = CC − DFT), with **local CC and frozen spaces** at PAH sizes; the off-diagonal block by **banded** sparse recovery from multi-mode patterns; the recovery licensed against direct references; locality and K_off measured |
| Sanders et al. (bib 24); O1NumHess (bib 23); mode-tracking (bib 46) | full-Hessian recovery from random multi-mode displacements by ℓ₁ in a cheap-method eigenbasis (Sanders — off-diagonals included); few-gradient recovery via off-diagonal low rank (O1NumHess; conjugated polyenes its worst covalent case); selected high-level modes by few gradients | the **frequency-banded** regulariser on a **difference** Hessian with a frozen local-CC anchor — not found in the 2026-09-03 search or by two reviewers; state it in those words, never as "sparse recovery of off-diagonals", which is Sanders |
| PySCFAD LNO-CC gradients (bib 33, 49) | AD nuclear gradients of LNO-CCSD(T) to ~29 atoms, fixed LNO spaces, validated against canonical gradients only | the frozen-space version at PAH sizes, validated against finite differences of its own surface (the side project) |
| Hybrid CC/DFT QFFs (bib 14, 27, 45) | CC harmonic + DFT anharmonic on small molecules and naphthalene | the same allocation, with the CC harmonic part obtained by probing rather than a full CC Hessian; whether the allocation holds for PAH families is what the diagonal-cubic bonus probe and P4(a) report |
| Plan 04 (in the tree, superseded) | the same criterion with a learned per-molecule surface | the same claim at a cost that is measured |

**Not novel:** running DFT/local CC; compressed sensing; CMA-style diagonal constants; GVPT2.
**Scored:** the frozen evaluation contract on a Δ₂-probed per-molecule pipeline across a
declared size ladder, with the probe count as a reported quantity.

## §3 Levels, anchors and the Δ-probing object (frozen intent; deck hashes at Q0 per rung)

| Item | Choice |
|---|---|
| Geometry, harmonic Hessian, dipole derivatives | DFT, **B3LYP-class** (the same functional family as line A, so that P1's unscaled harmonic cross-check and P2's per-band comparison compare like with like — the reason under the inheritance rule), basis per rung, analytic, on the B2 laptop's CPU through R3 (no CUDA GPU; any GPU Hessian is rented B3 time). The *baseline level* and the global part of every spectrum. At R6 a B3 object unless a timed probe at the R4 species shows otherwise |
| DFT anharmonic constants (cubic, semi-diagonal quartic) | finite differences of the analytic DFT Hessian along the modes of the **resonance-closed family set at closure depth one** — every scored family mode plus its partners found by the r₃/r₄ resonance search; partners' own diagonal anharmonicity from their 1-D cut only; bounded by the polyad cap; the pilot note prints the set's size and Hessian count per rung (pilot-note item 7); reduced-dimensionality precedent bib 28 |
| Anchor level and basis | local CC = **LNO-CCSD(T) in the pyscf-forge LNO code** (bib 48: `lnoccsd_t.py` and open-shell variants present — fetched 2026-09-04), the candidate in which spaces can be frozen (probe M1) and gradients pursued (side project); DLPNO-CCSD(T) remains the named alternative if M1 fails there. Basis: **cc-pVTZ at R0–R1**, deck number per rung above, same basis on both arms of every comparison (Ladder §3). Deck field `PNO extrapolation: none | CPS(6/7)` (bib 44); **spaces frozen at the reference geometry for every displaced evaluation** as Ladder §3 defines them; **licensed by measured deltas against frozen formulas, not by trust** (Q6) |
| **Patterns** | a hashed, ordered set in which every pattern p appears as the pair ±p (consumed together), whose first block in mode E is the 2M single-mode ±q_s energies (the CMA-0 block), followed by ± pairs of simultaneous multi-atom displacements built so every atom's local displacement space is complete (O1NumHess-class construction, bib 23), plus explicit two-mode patterns for every off-diagonal block the dry run flags as large (the CMA-2 diagnostic as a pattern rule, bib 43). Amplitude q_s from the Q6 step grid (Ladder §3) |
| **Responses** | mode E: the **symmetric combination** over the pattern pair ±p, R_s(p) = ½[ΔE(+p) + ΔE(−p)] − ΔE(0) = ½ pᵀΔ₂p + O(p⁴), which cancels the first-order term Δ₁·p (the CC−DFT force at the DFT geometry, several times the Δ₂ signal per bond) and the cubic term; the antisymmetric combination R_a is a free by-product (Δ₁; φ_iii with a second amplitude); mode G: the components of the gradient difference Δ(∇E)(p) − Δ(∇E)(0), which removes Δ₁ by construction. Every response is local CC minus DFT, both with frozen spaces. ΔE(0) is one shared reference per rung whose offset c₀ is identified from the two-amplitude read on the scored modes and subtracted before the recovery (a fitted constant would be collinear with a uniform diagonal shift; Ladder §3), so σ(R_s) = σ_E/√2; the scored harmonic part is Δ₂ + Σ_j φ_iij^DFT δq_j, the first-order corrected-surface-minimum term from Δ₁ (Ladder §3), printed per band; the Δ₁·p size is the Round-9 reviewer's recalled order of magnitude, measured by R_a |
| **Structural prior** (the promised accuracy route) | sparse recovery of Δ₂ in the DFT normal-mode basis with a **frequency-banded** regulariser: off-diagonal elements between modes closer than w are unpenalised (the DFT–CC mode-rotation block the near-diagonal model gets wrong on aromatics, bib 43); outside the band an ℓ₁ penalty; plus an off-diagonal low-rank term. **w and the weights are fixed from the dry run by the Ladder §3 rule** (w = the smallest band width reproducing the direct DFT−DFT Δ₂ within τ₇ on every family at the largest dry-run size; weights by the held-out ρ minimum on the noise-injected column) — printed, not chosen. "Structural" means it contains no learned parameters |
| **Learned prior** (M05) | replaces the banded term by a Transformer-predicted support. **Earned on R2–R3, spent on R4–R6** (Ladder §3): on R0–R3 the scored spectrum is always the structural recovery; on R2 and R3 both recoveries run on the same responses and must agree per family within τ₇ (direct couplings within η₈, absolute form; the structural recovery's own Q8(a/b) passed); on R4–R6 the prior-assisted recovery may be the only full recovery once the licence is earned at both R2 and R3, and the certificate says the spectrum depends on it and carries the rung's direct-coupling agreement |
| **Dry run** | Δ between **B3LYP and a functional with markedly more exact exchange** (BHLYP-class or HF), so that the calibration Δ contains mode rotations of the kind the CC Δ will; run in **both modes** (DFT gradients exist); and run **with a noise-injection column**: Gaussian noise **injected per energy, not per response** — ε(+p), ε(−p) ~ N(0, σ_E²) independently for every displaced energy and one ε₀ ~ N(0, σ_E²) per dry-run molecule for the shared reference, drawn once, R_s formed from the noisy energies; in mode G ε ~ N(0, σ_g²) per gradient component — at a grid of σ_E values bracketing the expected local-CC floor, K and ρ printed per σ_E (the column is indexed by σ_E and read at the R1 probe's σ_E, so c and K_cap are read at the noise the real run has); the dry run also prints its own DFT-arm floor from the noiseless single-mode block — the column from which the stopping constant c and K_cap are taken, never from the noiseless run (Round-8 Pass B finding 2). Never two functionals of one family |
| **Hold-out and residual ρ; the noise floor** | a fraction f_h of ± pairs (the pair is the hold-out unit, one deck index per pair), chosen by the seeded deck rule before any response exists, never enters the recovery. **ρ(n)** = RMS over held-out patterns of (symmetric response R_s predicted by the recovered Δ₂ − computed R_s) ÷ RMS of the computed held-out R_s; dimensionless; per mode. **ρ_noise** = σ_resp/RMS_resp(rung), σ_resp = σ(R_s) = σ_E/√2 in mode E and σ_g in mode G, from the pooled Q6 estimator of the largest noise measurement at or below the rung's size that exists before the rung's first probe (Ladder §3; which one, printed), RMS_resp the rung's own held-out response RMS. ρ is the error-budget term and the P3 metric |
| **K** | measured with the **noise-aware stopping rule**: the smallest count n — energies in mode E (a ± pair counts 2; ρ(n) evaluated after each complete pair), gradients in mode G — in hashed order, at which ρ(n) ≤ ρ\* = c·ρ_noise (c ≥ 1, pilot-note item 8) — equivalently the held-out χ² per response with σ(R_s) or σ_g as the sigma first falling to c² — under the **two guards of Ladder §3**: the rule is void when c·ρ_noise ≥ ρ_max = 0.5 (responses "at noise", K = NOT_RUN(at noise), no Δ₂ in that mode), and it is evaluated only for n > 2M in mode E (the deck's first block is the 2M single-mode ±q_s patterns) and for n ≥ n_min(G) in mode G (item 9); K_off = K − 2M ≥ 2 in mode E (one ± pair). Reported in the cost record. Capped by K_cap (pilot note item 9, from the noise-injected dry run, per mode). A residual that never reaches c·ρ_noise by K_cap is "not recovered at cap" |
| **Modes** | **E** (energies; the guaranteed route; **runs on every rung R1–R3 that runs**) and **G** (gradients; the aimed-for route, built in the side project — engine present in released code, bib 48–49; milestones M2–M5 with both checks license R0–R3). Where mode G is licensed it runs **in addition** to mode E; the rung carries two cost records; Q8(c) is computed per mode over the rungs that mode ran |
| **Diagonal-cubic bonus probe** | Δ₃ along each scored family's mode (φ_iii from the antisymmetric combinations of the single-mode ± block plus one further amplitude — two extra energies per scored mode, mandatory on the scored family modes at every rung because the same energies identify the reference constant c₀ and remove the quartic term, Ladder §3): a reported number, no gate, no entry into any spectrum |
| Anharmonic machinery | route (a) **GVPT2** on DFT anharmonic constants with the Δ₂-corrected harmonic part — named r₃/r₄ thresholds, polyad cap, CH-stretch dropped from scored families if the cap is exceeded; route (b) **MD-ACF** on the **defined DFT-plus-Δ potential**: a deck-named DFT-trained potential (its residual printed) plus Δ₂ applied as the quadratic correction in DFT normal coordinates, valid within the probed amplitude, CH-stretch labelled classical — **unavailable unless the deck names that potential**; route (c) CH-stretch never scored at that rung. Raw VPT2 without resonance treatment is forbidden on any promised family |
| Intensities | DFT dipole derivatives; no charge-flux shortcut; **no CC correction to dipoles promised** (bib 30, full text: fixed-dimension PNO spaces did not remove field-derivative discontinuities); **reported, not scored, and now on a measured basis**: the NIST/EPA gas-phase spectra carry no concentration ("molar absorptivity values cannot be derived", species page, verified 2026-09-04) and matrix intensities never score |
| Scale factors | **none on anharmonic output.** A harmonic fallback declares its factor + fit set |
| Emission | tier 1 = published cascade model on our bands, labelled inherited |

## §4 Deviations

A deviation exists only as a dated note committed **before** the affected quantity is measured.
Forbidden without one:

- Loosening any pilot-note number or margin, in either direction, after it is frozen.
- **Writing or amending the pilot note after any local-CC Δ₂ number is readable or any
  pipeline-vs-lab number exists** (the smoothness probe's sealed fits count as unreadable until
  the note is committed; a displaced-geometry local-CC gradient before the note is a deviation
  in itself).
- Re-windowing or re-classing a lab band after a pipeline number for that molecule exists;
  **declaring a family decidable from a point spacing rather than from M03's measured u_band**.
- **Adding, removing or re-weighting patterns after any residual is known; choosing held-out
  members after responses exist; writing K before it is measured; raising c, K_cap or q_s;
  taking c or K_cap from a noiseless dry run; dropping CPS once mandatory; using unfrozen
  spaces for a probe; computing a Q8 verdict on recovered couplings alone above R1; running a
  rung R1–R3 without mode E.**
- Any lab scoreboard value entering training, validation, stopping, sampling or **pattern
  design** decisions of the pipeline. The **M04 calibrated baseline** is the single declared
  exception (trains on lab residuals by design; leave-molecule-out; recipe frozen; outputs
  appear only as a P2 opponent column and the P5 empirical uncertainty layer).
- Weakening the M04 baseline after the pilot note.
- **The learned prior in a scored spectrum on R0–R3; the learned prior on R4–R6 without the
  licence earned at both R2 and R3 (Ladder §3)**; a Q8 ratio or an R6 sentence that mixes
  priors or modes.
- Swapping or re-versioning an opponent line after a comparison against it is scored.
- "Beat" language on a reach rung, or from a mode whose Q6 noise line did not pass at the
  rung's size class; a scale factor on anharmonic output; a cost sentence outside Ladder §1's
  two forms; a CC correction to anharmonic constants entering a spectrum.
- Starting a B3 job without the budget file's preconditions; starting any reach rung before
  R3 is scored; wording a size sentence before Q8(c) has printed at R1→R2 and R2→R3; starting
  R6 as a whole-molecule probe, or as a fragment probe before the fragment licence (Ladder §3)
  has passed parts (a), (b) (passed, or pending resolved by a passing (b′)), (b′ where
  classified affordable) and (c).

## §5 Architecture and the one comparison axis

- **Promised accuracy path (R0–R3):** the sparse-recovery solver with the banded structural
  prior — classical convex optimisation; **no neural network in any R0–R3 scored spectrum**.
- **Model family for Module 05: Transformer** (equivariant attention over atom / DFT-mode
  tokens) predicting the **support of Δ₂ in the DFT mode basis** — which off-diagonal blocks
  are large — from DFT-level features: CMA-2's diagnostic, learned instead of computed. Anything
  outside CNN/RNN/Transformer returns to the user before training.
- **The controlled comparison (frozen): learned prior vs structural prior at matched K, on the
  dry-run corpus (primary), with the effect size reported on the PAH held-out tensors as
  well (informational; the licence itself requires K_prior < K_struct on real responses at R2
  and R3, Ladder §3).** Same patterns, same held-out set, same solver, ≥3 seeds for the prior: does the prior
  lower ρ at fixed K, or reach ρ\* at lower K? The effect size is pilot-note item 5. **No R0–R3
  scored spectrum depends on its outcome.** On R2–R3 the comparison is repeated on real
  responses as the licence-earning check (Ladder §3); on R4–R6 a spent licence makes the prior
  load-bearing for the spectrum and the cost record, and the certificate says so.
- Baselines in every comparison table: line A (scaled harmonic), M04 calibrated harmonic, and
  the null rows (§7, P4).

## §6 Training discipline

- **The M05 corpus** (decision 4): the public **Hessian QM9** set (bib 47: 41,645 molecules,
  ωB97x/6-31G* Hessians; QM9 molecules have at most nine heavy atoms, so the corpus contains no
  PAH larger than benzene — recalled by the Round-8 reviewer, to be verified when the corpus is
  built) plus B3LYP/6-31G* Hessians recomputed on an **aromatic-heavy subset** (benzene
  derivatives and conjugated rings over-represented), giving Δ₂ = ωB97x − B3LYP per molecule
  with the exact-exchange contrast the dry run needs. **The subset's size is fixed by a dated
  note after the zero-CC dry run has printed the B2 laptop's per-molecule Hessian timing** — no
  size appears in a frozen document before that. The PAH dry-run tensors and the probed local-CC
  Δ₂ tensors from the rungs that have run are a **held-out test set only**, never training data,
  and **P3's effect size is reported on them** because the corpus is off-distribution from every
  rung. Published (Zenodo DOI, deck hashes) before Module 05 starts. Success is the P3 saving
  and the Ladder §3 licence, not accuracy for its own sake. Splits by molecule and by pattern
  batch, hashed (Q3). Stopping on validation only. Test touched once per pre-registered
  evaluation. The reading-2 fallback source (a public Hessian set other than Hessian QM9) is a
  **named debt** to be searched and verified before Module 05 starts; none is named from recall.
- The lab scoreboard is outside all of it (Q4).
- ≥3 seeds; mean ± SD; tuning parity between the learned prior and any alternative prior. The
  M04 baseline has its own frozen recipe.
- The M06 generative pattern-proposer (mapping) trains on the **QM9-subset dry-run
  pattern-response records only** (the PAH dry-run tensors stay M05's test set — no
  cross-module overlap); every accepted pattern enters the hashed, ordered set **before** any
  response for that rung is computed, never after.

## §7 Quality checks and gates

Scripts under `probes/`. A number not printed by a script is not a result.

### Q (integrity, per rung)

| ID | Check | Pass |
|---|---|---|
| Q0 | deck hash: levels, **basis per rung**, local-CC code + commit + thresholds + CPS field, **DFT integration grid and SCF/CC convergence thresholds** (both arms' numerical noise enters σ_E), **frozen-space hash (probe M1), ordered pattern set and amplitude q_s per mode, banded-prior w and weights with the rule's printout, hold-out seed and f_h, stopping constant c and K_cap per mode, direct-coupling pair list and step h** frozen per rung | SHA256 reproducible |
| Q1 | scoreboard reproduction: lab band table regenerated under this plan's hash, **with M03's u_band per band** | matches the pilot note's band list and decidability column |
| Q2 | timed probes exist for every budget-governed step (machine, date, settings, wall-clock, peak memory for gradient probes) | printed |
| Q3 | split overlap (molecule and pattern batch) | prints 0 |
| Q4 | lab-leak check: no scoreboard value reachable from any training artifact or pattern-design input of the pipeline; M04 checked for leave-molecule-out instead | prints 0 |
| Q5 | minimum check: converged geometry, 0 imaginary frequencies, 3N−6 modes | pass/fail |
| **Q6** | **anchor licence against frozen formulas** (Ladder §3, numbers at item 13), with the **one estimator** (σ = √(SSR/(n − p)); one σ per arm pooled over the four modes, per-mode values and studentised residuals printed; σ_g pooled over all 3N components; Ladder §3): along each probe mode — a C–C stretch, a C–H stretch, a CH-oop mode and one totally symmetric mode — nine points on q ∈ [−1, 1] per freezing arm; **σ_E = RMS residual of ΔE(q) about a degree-4 least-squares polynomial**, **σ_g = RMS residual of the gradient-difference component about a degree-3 polynomial**. **Noise, mode E**: σ_E ≤ 0.82·τ·q_s² for each q_s ∈ {0.25, 0.5, 1.0}, at R1 and at the R2-size family; **noise, mode G**: σ_g ≤ 2.8·τ·q_s, same grid, wherever a local-CC gradient runs; **bias**: |Δ₂(frozen) − Δ₂(canonical)| per mode at R0 in the same basis (feasibility measured by the canonical probe before the note), and diagonal-only along one mode per family at pyrene (two canonical energies per mode); **threshold**: TightPNO−NormalPNO frequency deltas at the licence molecule and the R2-size family, and local CC vs canonical harmonic-frequency deltas at the licence molecule. Before the pilot note the R1 probe prints σ only; its polynomial fits are sealed | each line printed with its verdict; noise breach in a mode at a size class ⇒ no "beat" from that mode there; bias or threshold breach ⇒ Ladder stop 4 (threshold breach ⇒ CPS mandatory) |
| **Q7** | **probing licence for Δ₂** at R0 and R1, run **after** the pilot note: (i) recovered Δ₂ (structural prior, at the measured K) vs a directly computed reference Δ₂ — full numerical local-CC Hessian minus DFT Hessian with the same frozen spaces, and at R0 also canonical CCSD(T) minus DFT in the same basis (the only reference independent of the freezing; if the feasibility probe placed the full canonical Hessian on B3, this arm waits for B3 and Q7(i) at R0 compares to the local-CC reference only — sentence printed); metric: per-family RMS harmonic-frequency difference; **printed twice — for the diagonal-only recovery (CMA-0 on Δ) and for the full banded recovery**, with the recovered Δ₂ shown as a matrix in the DFT mode basis against the reference; (ii) **discriminability**: the full recovery must be closer to the reference than Δ₂ = 0 is, by at least d₇; (iii) **shuffled-probe null**: responses randomly permuted across patterns, recovered by the same solver, must fail (i)–(ii); (iv) Q8(a/b) computed on the reference Δ₂ (the local-CC arm's reference Hessian; the canonical one beside it where it exists) and on the recovered Δ₂ side by side, with the absolute agreement metric (this is R0's only Q8 read; R1's counts as the first rung read). A **dry-run column** (B3LYP-vs-high-exchange Δ at R0 and at the largest affordable size, both modes, noiseless and noise-injected, reference = direct DFT−DFT Hessian difference) is printed before the pilot note as the estimator check | (i) ≤ τ₇ per family for the full recovery (the diagonal-only result is reported, not gated); (ii) holds; (iii) fails; (iv) agrees within ε₈ (share) and η₈·S on resolved pairs; breach is Ladder stop 4. **At R1 without a canonical arm, Q7 tests the recovery, not the freezing** — that sentence is printed with the result |
| **Q8** | **locality and saturation on directly measured couplings**, form frozen in Ladder §3: (a) per (pair, family), the family-projected coupling ∂²ΔE/∂u_A∂u_B by four-point differences at Cartesian step h (four energies per pair per family; the full 3×3 block for the deck's near pair only), fitted against distance to A·exp(−r/r_c), r_c printed as a measurement, pairs beyond r_max carrying ≤ ε₈ of Σ coupling² — on the reference Hessian at R0–R1 and on the **direct probe** at R2–R3, with the recovered couplings printed beside; agreement in the **absolute form**: |recovered − direct| ≤ η₈·S_class with S_class = √(Σ direct²/n_class) over the pair's bond-count class (near = bonded, mid = 2–3 bonds, far = ≥ 4 bonds; equal frozen counts, item 12); pairs below 3σ_coupling = 3σ_E/(2h²) (Ladder §3) reported "at noise" and entering the fit with their uncertainty; (b) per scored family, the share of the family's Δ-shift carried by pairs beyond r_max ≤ ε₈, with the direct far couplings substituted into the recovered Δ₂; (c) K_off(R_{n+1}) ≤ γ·K_off(R_n) (mode E, every rung) and K(R_{n+1}) ≤ γ·K(R_n) (mode G, over the rungs it ran), same prior, both counts read from the stored ρ(n) curves at the common threshold ρ\*_common = max(ρ\*(R_n), ρ\*(R_{n+1})) (Ladder §3), for R1→R2 and R2→R3 | (a), (b) per rung R1–R3; disagreement > η₈·S on a resolved pair is a Q7-class breach; (c) per pair of rungs and per mode; breach is Ladder stop 4 |

### P (science, fail-closed)

| Gate | What | Language allowed |
|---|---|---|
| P0 | pipeline sanity at the rung (Q5 + end-to-end spectrum produced + cost record(s) printed) | "ran" |
| P1 | harmonic cross-check at R0: our unscaled DFT harmonic bands vs line A's unscaled values, within a declared convention window | "consistent" |
| P2 | **the beat comparison** (accuracy rungs): paired per-band \|error\| on positions vs lab, pipeline vs line A, M04 baseline, and line B where present; per family; margins from the pilot note; decidability per Ladder §2 (u_band, never point spacing); only where the Q6 noise line of the mode used passed at the size class. Intensities reported alongside; scored only where the pilot note names a gas-phase intensity scoreboard with concentration data | "beat / lost / inconclusive" |
| P3 | the §5 axis: learned prior vs structural prior at matched K, dry-run corpus, ≥3 seeds, effect size from the pilot note, reported also on the PAH held-out tensors; repeated on real responses at R2 and R3 as the licence-earning check | "the prior buys X" |
| P4 | **null rows, mandatory.** (a) **Δ₂ = 0** (DFT harmonic + DFT anharmonic, no CC correction), scored by the same script, bands, windows, seeds and aggregation as the P2 claim it nullifies: on every family where the pipeline claims "beat", the Δ₂=0 arm's family mean \|error\| must exceed the pipeline's by at least that family's beat margin. (b) a noise-input run must fail Q5/P0. (c) the shuffled-probe null must fail Q7 | — |
| P5 | reach certificate (R4–R6): end-to-end run + error budget (empirical component = M04 uncertainty layer; labelled **an extrapolation from R0–R3**) + theory-vs-theory table + **the cost record(s), in the same table as R3's** + the fragment licence's parts (a), (b), (b′) and (c) with their numbers + the learned-prior licence's two earning rungs and the rung's direct-coupling agreement if the prior was spent + the certificate or refusal | "reached", never "beat" |

Consequence sentences, pre-authorised and identical here and in §8:

- If **P4(a)** fails on a family: **"The coupled-cluster correction did not improve on the
  DFT-anharmonic arm at Rn on family F; the coupled-cluster claim for F is void and the result
  is reported as explained by DFT-level anharmonicity."** (Losing to the M04 calibrated
  harmonic baseline is a different outcome — a P2 loss — with §8's second sentence.)
- If **P4(b)** passes where it should fail: **"The sanity gates at Rn are void; no P2 result at
  Rn is interpreted until the gate is repaired by dated note and re-run."**
- If **P4(c)** passes where it should fail: **"Q7 is not discriminating at Rn at the frozen
  tolerance; Δ₂ is not licensed at Rn"** — Ladder stop 4 applies.

If P0 fails at a rung, P2 is not interpreted there.

## §8 Fail-closed sentences (pre-written)

- "Rung Rn did not run: [cap/precondition/binary/option] — see the dated note."
- "Rung Rn ran and lost to [line] on [families]: paired table attached."
- "The coupled-cluster correction did not improve on the DFT-anharmonic arm at Rn on family F;
  the coupled-cluster claim for F is void and the result is reported as explained by DFT-level
  anharmonicity."
- "The sanity gates at Rn are void; no P2 result at Rn is interpreted until the gate is
  repaired by dated note and re-run."
- "Q7 is not discriminating at Rn at the frozen tolerance; Δ₂ is not licensed at Rn."
- "Mode [E|G] at the Rn size class is above its noise line (Q6: σ = … vs … at q_s = …); no
  'beat' language is written for that mode's results there; the cost record is attached."
- "Family [F] at Rn is **inconclusive by construction on the gas scoreboard**: M03's measured
  band-centre uncertainty (resolution …, centroid …, temperature term …) is not smaller than
  the beat margin. No beat, no loss." (Expected for the R2 C–C families on the NIST source.)
- "Family [F] at Rn is **pre-declared inconclusive on matrix**: the M03-measured |matrix−gas|
  delta is not smaller than the beat margin. No beat, no loss."
- "Reach rung Rn produced a spectrum with the attached error budget; no accuracy claim is made
  because no laboratory spectrum exists."
- "At R6, families [F…] are withdrawn from the certificate: the fragment licence failed for
  them (part [a|b|b′|c], numbers attached); the certificate covers the remaining families."
- "R6 is not reached: the fragment licence failed for **all** scored families ([which parts],
  numbers attached) / B3 did not exist — the refusal is the Module 08 result for R6."
- "The fragment licence is **pending (b′)**: part (b) failed at one shell at coronene, where two
  shells are untestable, and (b′) — the only two-shell test — did not run because B3 did not
  exist; R6 is not fragment-probed and the licence is neither earned nor failed; (c)'s R4
  fragment instance [ran / did not run] under the pending licence and does not resolve it."
- "The R0 canonical arm did not fit the B2 laptop in the anchor basis (feasibility probe:
  …); the bias line was measured in [cc-pVDZ] with both arms in that basis / is the first B3
  request; the full canonical reference Hessian [fit / is the first B3 request, so Q7(i) at R0
  compared to the local-CC reference only and Q7(iv) read the reference from the local-CC arm]
  — see the dated note."
- "Probe M1 failed: no code froze the local-CC spaces at the anchor level ([codes tried]);
  stop 1 — no local-CC probe ran."
- "Δ₂ was not recovered at Rn within K_cap (ρ = … against c·ρ_noise = …); the rung's Δ₂ is
  absent and the fallback of Ladder §5.4 was scored instead."
- "Mode [E|G] at Rn is **at noise**: c·ρ_noise = … ≥ ρ_max = 0.5 (σ = …, RMS_resp = …); no Δ₂
  was recovered in that mode; K = NOT_RUN(at noise); the cost record is attached."
- "Mode [E|G] fails Q6 at Rn at q_s = 1.0 (σ = … vs the line …); no smaller step is tried; no
  Δ₂ is recovered in that mode at Rn."
- "Δ₂ is not local at Rn on family F: Q8(a/b) on direct couplings breached with the attached
  decay curve and long-range share; no accuracy claim finer than that share is made for F."
- "[K_off|K] did not saturate between R1 and R3 (Q8c breached, ratios attached); no size
  sentence is written."
- "The side project stopped at milestone M[n] on [date] (kill criterion); mode E ran on every
  rung; no mode-G size sentence is written."

## §9 Claim ladder (keyed to gates)

1. P0+P1 at R0 → "the pipeline exists and is convention-clean."
2. Q6 noise at R1 under the line (per mode) → "frozen-space local-CC [energies|gradients] are
   smooth enough at step q_s for mode [E|G] to resolve a τ correction" — or its negation, printed.
3. Q7 at R0–R1 → "the probed Δ₂ reproduces a direct CC force-constant correction within
   tolerance at the measured K, beats the zero correction by d₇, and the diagonal-only
   recovery [does / does not] suffice on the C–C families."
4. Agreement within margin at R0–R1 + P2 win + P4 clean → "a probed CC correction reproduces
   known truth on small PAHs against gas-phase data — and beats the lines, secondary to
   agreement."
5. Q8(a/b) on direct couplings at R1–R3 → "the correction decays with distance with fitted
   length r_c, and the scored families' corrections are carried by pairs within r_max" — per
   family.
6. P2 at R2–R3 on decidable families with the mode's noise line passed → "…and it holds where
   PAHdb's anharmonic front ends, on the families the lab data can decide" — with the
   inconclusive-by-construction families named as such.
7. Q8(c) at R1→R2 and R2→R3 → the size sentence, numeric form only, per mode that ran on all
   three rungs.
8. Learned-prior licence earned at R2 and R3 → "the learned prior reproduces the structural
   recovery at both medium rungs and saves X patterns; it is spent on R4–R6."
9. Fragment licence parts (b) and (b′) → "coronene probed in fragments of radius r_f reproduces
   coronene probed whole, per family; and so does [the R4 species] where whole-molecule probing
   was affordable."
10. P5 at R6 → "the pipeline reaches a C₃₈₄H₄₈-class species from the atlas by fragment-probed
    Δ₂ under the licence of steps 5 and 9 and the R6 fragment-radius convergence test, with the
    attached cost record beside R3's: a labelled theory-vs-theory spectrum plus an uncertainty
    statement that is explicitly an extrapolation from R0–R3" — or the refusal.
11. Tier-1 emission on any of the above → "and here is what JWST would see, via the inherited
    cascade model."

Each step cites only the gates above it. A missing gate truncates the ladder; it never
re-words it.
