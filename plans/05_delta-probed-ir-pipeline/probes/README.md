# Probes — Plan 05

Conventions, carried from plans 01–04:

- A number that is not printed by a script in this folder is not a result.
- Probes that need inputs which do not exist yet print `NOT_RUN` and exit cleanly.
- A probe is not a plan and does not get a plan number.
- Pre-registered comparisons (frozen lines, ladder rungs) are scored by scripts here, never
  by hand in a document.
- **[05]** A pattern set is a versioned, ordered input: its hash, the amplitude q_s, the
  hold-out seed and f_h are printed by every recovery probe that uses it. K and K_off are
  printed, never typed. Every Q6 line prints its formula, its inputs and its verdict.

## Probes that exist

None under plan 05 yet. Plan 04's NIST gas-phase coverage probe and its raw cache exist in
`plans/04_cc-anchored-ir-pipeline/probes/` and are re-run under this plan's hash as owed
probe 2 below; their measured result (gas IR present for benzene, naphthalene, pyrene,
chrysene, triphenylene; tetracene solid-only; coronene absent; R2 gas grids ~4 cm⁻¹) is
carried as provenance and already re-shaped the R2 row (Ladder §2, dated note).

## Probes owed (in the order they decide things; Compute_Budget §4 gives the timing order)

**Before the pilot note** (DFT-only work, probe M1, a run/no-run gradient check at equilibrium,
single-mode scatter with sealed means, and timings; no local-CC Δ₂ number may be readable):

1. **Zero-CC dry run, both modes** (`dryrun_dft_delta_recovery.py`): Δ between B3LYP and a
   high-exact-exchange functional at R0 and at the largest molecules the laptop's DFT Hessian
   affords; recover Δ₂ with the banded structural prior from a hashed, ordered pattern set with
   seeded hold-out, from energies and from DFT gradients; print the residual curves ρ(n), the
   dry-run K and K_off per mode at a declared ρ, the off-diagonal blocks flagged large, the
   recovered-vs-direct frequency error per family for the diagonal-only and the full recovery,
   the band width w and weights by the Ladder §3 rule, and the per-molecule DFT Hessian
   wall-clock on the B2 laptop; then the **noise-injection column**: the same recoveries with
   Gaussian noise at a grid of σ added to every response, K and ρ per σ (the source of the
   stopping constant c and of K_cap). Feeds pilot-note items 8, 9 (both modes), 13, and the M05
   subset-size note.
1a. **Canonical feasibility probe** (`r0_canonical_feasibility.py`): one canonical CCSD(T)
   energy of benzene in the anchor basis on the B2 laptop; wall-clock and peak memory printed
   and extrapolated to the R0 Hessian count; decides the basis of the Q6 bias line (Ladder §3).
1b. **Probe M1 — frozen spaces** (`m1_frozen_spaces.py`): the candidate local-CC code
   (pyscf-forge LNO-CC; whether the release is CCSD or CCSD(T) is printed) stores fragment
   list, localized orbitals and LNO vectors at the reference geometry and, at displaced
   geometries, maps occupied orbitals by maximal overlap and projects/orthonormalises the stored
   virtual spaces (the Ladder §3 object); prints the reference-energy reproduction (target
   10⁻⁹ E_h) and, along one totally symmetric, one degenerate and one non-symmetric benzene
   mode, the assignment permutation and E(displaced, frozen) − E(displaced, fresh) per point,
   **without a verdict** (the τ it would be judged against does not exist yet). Fails → Ladder
   stop 1.
2. **Lab-scoreboard re-read and u_band** (`m03_band_uncertainty.py`): regenerate the plan-02
   band table (PAHdb experimental uids, NIST JCAMP) and the plan-04 NIST coverage scan under
   this plan's hash; per gas-phase band print the source's stated resolution (from its
   documentation, never `DELTAX`), the centroid precision from the signal-to-noise, the
   temperature term (declared hot-band shift or the labelled hot-vapour uncertainty), their
   quadrature sum **u_band**, and the decidability verdict per family (feeds pilot-note item 1).
3. **Gradient availability, run/no-run at equilibrium** (`anchor_gradient_availability.py`):
   per candidate code, does an analytic gradient at the anchor level run **at the equilibrium
   geometry** of benzene and naphthalene with frozen spaces? Prints code, version, run/no-run,
   wall-clock, peak memory. No displaced geometry before the pilot note. K_cap(G) comes from
   the dry run regardless; the side project's M2–M5 later answer per rung.
4. **R0 pilot**: geometry → DFT Hessian → harmonic bands, **timed**; one timed local-CC
   single point with frozen spaces (timing only). Produces **no local-CC Δ₂ and no
   pipeline-vs-lab number**.
5. **R1 smoothness probe** (`q6_smoothness.py`): naphthalene, three modes (a C–C stretch, a C–H
   stretch, a CH-oop), nine points each at q ∈ [−1, 1], TightPNO, with and without frozen
   spaces, plus one totally symmetric mode; **σ_E = the RMS residual of ΔE(q) about a degree-4
   least-squares polynomial** per mode and arm (σ_g about a degree-3 fit where a gradient runs)
   is printed against 0.82·τ·q_s² (2.8·τ·q_s) for each q_s ∈ {0.25, 0.5, 1.0}; the fit
   coefficients (which contain the diagonal Δ₂ elements) are written to a hashed, sealed file
   that the script refuses to open before the pilot note's commit hash exists. Fixes the pattern
   amplitude (item 13). ≈ 40 local-CC energies.

**After the pilot note is committed:**

6. **R0 probe batch and Q7** (`q7_probing_licence.py`): the R0 responses in hashed order,
   K(R0) and K_off at ρ\*, the cost record; then the references (numerical local-CC Hessian
   with frozen spaces; canonical CCSD(T) Hessian) and the Q7 table (i)–(iv) — the recovered
   Δ₂ printed as a matrix in the DFT mode basis, for the diagonal-only and the full recovery,
   the discriminability factor, the shuffled-probe null, and Q8(a/b) on reference vs
   recovered (R0's only Q8 read). Also the **diagonal-cubic bonus probe** (φ_iii along each
   scored mode, four energies per mode; a reported number), the opening of the sealed
   smoothness fits, and side-project **M2** (`sp_m2_gradient_benzene.py`: AD gradient with the
   projection inside the graph vs finite differences of the **re-projected** frozen-space
   energy; the mode-G noise line σ_g ≤ 2.8·τ·q_s along the Q6 modes; and the third number,
   AD(projection inside) − AD(projection under stop_gradient) per Q6 mode).
7. **Anchor-licence probes** (Q6, `q6_anchor_licence.py`): the bias line at R0 (frozen vs
   canonical Δ₂ per mode); local CC vs canonical and TightPNO vs NormalPNO harmonic-frequency
   deltas at the licence molecule; the CPS decision.
8. **R1**: canonical feasibility at R1 on the B2 laptop; R1 probe batch under the noise-aware
   stopping rule; Q7 twice (with the "tests the recovery, not the freezing" sentence if no
   canonical arm); Q8(a/b) on the reference Hessian (`q8_locality.py`); side-project **M3**
   (naphthalene: the three M2 printouts, wall-clock, peak memory ≤ 28 GB).
9. **Anthracene locality probe** (dated bonus between R1 and R2, ≈ 133 frozen-space local-CC
   energies): full numerical Δ₂ minus B3LYP; Q8(a) per pair and the mode-basis matrix per
   family; fail-closed reading pre-written in the dated note.
10. **Resonance probe** (before any R2 spectrum, DFT level is enough): pyrene CH-stretch
    family via GVPT2 vs raw VPT2 vs MD-ACF; the resonance-closed family set printed.
11. **Classification probe** per rung: `wall_clock_per_probe × K_cap × c_CPS` against the
    168 h checkpoint (Compute_Budget §2).
12. **R2**: the pyrene canonical diagonal check (Q6 bias at R2 size); the **direct-coupling
    probe** (`q8_direct_couplings.py`: deck-chosen π-system pairs at near, mid, far distances;
    per pair and scored family the family-projected coupling ∂²ΔE/∂u_A∂u_B by four-point
    differences at step h — four energies per (pair, family); the full 3×3 block for the near
    pair only; pairs below 3σ_coupling reported "at noise"); the Q6 noise grid at the R2-size
    family in the mode(s) used; probe batches in mode E (and G if licensed) — the structural
    recovery, and the prior-assisted recovery on the same responses
    (`licence_prior_vs_structural.py`: per-family agreement within τ₇, couplings within η₈·S,
    the structural recovery's own Q8(a/b) passed); Q8(a/b) on direct couplings with the
    recovered couplings beside; Q8(c) R1→R2 per mode; side-project **M4**.
13. **R3**: direct-coupling probe; batch (both modes where licensed; both recoveries;
    licence-earning comparison); **fragment-vs-whole** (`fragment_licence.py`: coronene's Δ₂
    from capped fragments at the smallest passing radius r_f vs whole, per family within τ₇;
    r_f printed against the molecule's radius); Q8(a/b); Q8(c) R2→R3 per mode; side-project
    **M5** (gradient at coronene: run/no-run, AD-vs-FD along the Q6 modes, σ_g at R3 size); the
    cost records side by side.
14. **R4 (fragment licence, parts b′ and c, first instance)**: `fragment_licence.py` on
    circumcoronene — whole vs fragments, conditional on B3 classification of the whole batch;
    `fragment_convergence.py` — direct couplings on the central ring from fragments of radius
    r_f and r_f + one ring, agreement within η₈·S.
15. **R6 (fragment licence, part c)** (`fragment_convergence.py` on the flake): deck-chosen
    interior and edge pairs, direct couplings from fragments of radius r_f and r_f + one ring
    carved from the R6 DFT geometry, agreement within η₈·S; whole-flake direct couplings where
    B3 allows.
