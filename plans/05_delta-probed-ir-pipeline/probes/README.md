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

**Before the pilot note** (DFT-only, single-mode second differences and timings; no local-CC Δ₂
recovery may exist yet):

1. **Zero-CC dry run** (`dryrun_dft_delta_recovery.py`): Δ between B3LYP and a high-exact-
   exchange functional at R0 and at the largest molecules the laptop's DFT Hessian affords;
   recover Δ₂ with the banded structural prior from a hashed, ordered pattern set with seeded
   hold-out; print the residual curve ρ(n), the dry-run K and K_off at a declared ρ, the
   off-diagonal blocks flagged large, and the recovered-vs-direct frequency error per family
   for the diagonal-only and the full recovery. Feeds pilot-note items 8, 9, 13.
2. **Lab-scoreboard re-read**: regenerate the plan-02 band table (PAHdb experimental uids,
   NIST JCAMP) and the plan-04 NIST coverage scan under this plan's hash; print the gas grid
   per molecule and family (feeds the decidability rule).
3. **Gradient availability** (`anchor_gradient_availability.py`): per candidate code, does an
   analytic gradient at the anchor level run at R0, at naphthalene/cc-pVTZ, and at pyrene,
   with frozen domains? Prints code, version, yes/no, wall-clock, peak memory. Decides mode E
   vs G per rung; K_cap(G) reads NOT_RUN where the answer is no.
4. **R0 pilot**: geometry → DFT Hessian → harmonic bands, **timed**; one timed local-CC
   single point with frozen domains (timing only). Produces **no local-CC Δ₂ and no
   pipeline-vs-lab number**.
5. **R1 smoothness probe** (`q6_smoothness.py`): naphthalene, three modes (a C–C stretch, a C–H
   stretch, a CH-oop), nine points each at q ∈ [−1, 1], TightPNO, with and without frozen
   pair lists / domains / PNO counts; second-difference scatter σ_E printed against
   0.82·τ·q_s² on the grid q_s ∈ {0.25, 0.5, 1.0}. Fixes the pattern amplitude (item 13).
   ≈ 30 local-CC energies.

**After the pilot note is committed:**

6. **R0 probe batch and Q7** (`q7_probing_licence.py`): the R0 responses in hashed order,
   K(R0) and K_off at ρ\*, the cost record; then the references (numerical local-CC Hessian
   with frozen domains; canonical CCSD(T) Hessian) and the Q7 table (i)–(iv) — the recovered
   Δ₂ printed as a matrix in the DFT mode basis, for the diagonal-only and the full recovery,
   the discriminability factor, the shuffled-probe null, and Q8(a/b) on reference vs
   recovered. Also the **diagonal-cubic bonus probe** (φ_iii along each scored mode, four
   energies per mode; a reported number).
7. **Anchor-licence probes** (Q6, `q6_anchor_licence.py`): the bias line at R0 (frozen vs
   canonical Δ₂ per mode); local CC vs canonical and TightPNO vs NormalPNO harmonic-frequency
   deltas at the licence molecule; the CPS decision.
8. **R1**: canonical feasibility on the new machine; R1 probe batch; Q7 twice (with the "tests
   the recovery, not the freezing" sentence if no canonical arm); Q8(a/b) on the reference
   Hessian (`q8_locality.py`).
9. **Anthracene locality probe** (dated bonus between R1 and R2, ≈ 133 frozen-domain local-CC
   energies): full numerical Δ₂ minus B3LYP; Q8(a) per pair and the mode-basis matrix per
   family; fail-closed reading pre-written in the dated note.
10. **Resonance probe** (before any R2 spectrum, DFT level is enough): pyrene CH-stretch
    family via GVPT2 vs raw VPT2 vs MD-ACF; the resonance-closed family set printed.
11. **Classification probe** per rung: `wall_clock_per_probe × K_cap × c_CPS` against the
    168 h checkpoint (Compute_Budget §2).
12. **R2**: the pyrene canonical diagonal check (Q6 bias at R2 size); the **direct-block
    probe** (`q8_direct_blocks.py`: deck-chosen π-system pairs at near, mid, far distances,
    each 3×3 Δ₂ block by four-point finite differences of ΔE, ≈12 energies per pair); the
    Q6 noise grid at the R2-size family; probe batches; Q8(a/b) on direct blocks with the
    recovered blocks beside; Q8(c) R1→R2 on K_off.
13. **R3**: direct-block probe; batch; Q8(a/b); Q8(c) R2→R3; the cost records side by side.
