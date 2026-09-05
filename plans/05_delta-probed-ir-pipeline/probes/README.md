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
probe 2a below; their measured result (gas IR present for benzene, naphthalene, pyrene,
chrysene, triphenylene; tetracene solid-only; coronene absent; R2 JCAMP point spacing ~4 cm⁻¹) is
carried as provenance and already re-shaped the R2 row (Ladder §2, dated note).

## Probes owed (in the order they decide things; Compute_Budget §4 gives the timing order)

**Before the pilot note** (DFT-only work, probe M1, a run/no-run gradient check at equilibrium,
single-mode scatter with sealed fit coefficients, and timings; no local-CC Δ₂ number may be readable):

1. **Zero-CC dry run, both modes** (`dryrun_dft_delta_recovery.py`): Δ between B3LYP and a
   high-exact-exchange functional at R0 and at the largest molecules the laptop's DFT Hessian
   affords; recover Δ₂ with the banded structural prior from a hashed, ordered pattern set with
   seeded hold-out (the pair ±p is the hold-out unit), from energies — as symmetric combinations
   R_s over ± pairs — and from DFT gradients; print the residual curves ρ(n), the dry-run K and
   K_off per mode at a declared ρ (**K in energies, a ± pair counting 2, exactly as probe 6**), the off-diagonal blocks flagged large, the
   recovered-vs-direct frequency error per family for the diagonal-only and the full recovery,
   the band width w and weights by the Ladder §3 rule, and the per-molecule DFT Hessian
   wall-clock on the B2 laptop; then the **noise-injection column**: the same recoveries with
   Gaussian noise injected **per energy** (independent on every displaced energy, one shared ε₀
   per molecule for the reference; per component in mode G) at a grid of σ_E, R_s formed from the
   noisy energies, K and ρ per σ_E, the reference constant c₀ identified from the two-amplitude
   modes and printed, and the noiseless block's **DFT-arm floor** printed (the source of the
   stopping constant c and of K_cap). Feeds pilot-note items 8, 9 (both modes), 13, and the M05
   subset-size note.
1b. **Canonical feasibility probe** (`r0_canonical_feasibility.py`): one canonical CCSD(T)
   energy of benzene in the anchor basis on the B2 laptop; wall-clock and peak memory printed
   and extrapolated to the bias-line count (61 energies) and the full canonical reference-Hessian
   count (72 canonical gradients — one canonical CCSD(T) gradient is also run and timed where
   the code has it, `pyscf/grad/ccsd_t.py` fetched 2026-09-04 — else 1,801 energies); "fits" = ≤ 168 h and ≤ 31.3 GB per object; `max_memory` = 28,000 MB set explicitly, peak RSS
   and the disk high-water mark printed (PySCF blocks the (T) lambda and density over virtual
   triples, so time, not memory, is expected to bind); decides the basis of the Q6 bias
   line and whether the R0 canonical reference Hessian is R0 work or the first B3 request
   (Ladder §3; Budget §4.1b).
2. **Probe M1 — frozen spaces** (`m1_frozen_spaces.py`): the candidate local-CC code
   (pyscf-forge LNO-CCSD(T), item 48; version pinned and printed) stores fragment
   list, localized orbitals and LNO vectors at the reference geometry and, at displaced
   geometries, transports the occupied and the virtual vectors by projection and
   Löwdin-orthonormalises them (the Ladder §3 object; no localiser, no assignment); prints the
   reference-energy reproduction (target 10⁻⁹ E_h) and, along one totally symmetric, one
   degenerate and one non-symmetric benzene mode, the continuity diagnostics (smallest singular
   value of the occupied overlap, largest pre-Löwdin off-diagonal, both halves; arm C's
   localiser functional and its overlap with the transported set) and E(A) − E(B), E(A) − E(C)
   per point (arms per Ladder §3; the arm-A override's commit hash printed), **without a verdict**; the raw displaced energies are written
   to the hashed, sealed file of probe 5, never printed (the τ it would be judged against does not exist yet). Fails → Ladder
   stop 1.
2a. **Lab-scoreboard re-read and u_band** (`m03_band_uncertainty.py`): regenerate the plan-02
   band table (PAHdb experimental uids, NIST JCAMP) and the plan-04 NIST coverage scan under
   this plan's hash; per gas-phase band print the source class (cell / vapour cell / GC-IRD),
   the stated temperature, the source's stated resolution (from its documentation, never
   `DELTAX`), the centroid precision from the signal-to-noise, the temperature term (pinned
   hot-band correction with ±30 % and the temperature uncertainty, or the Ladder §2 floor
   χ_max·(T_source − 296 K) + u_296; T_source from the record, else from the series'
   documentation — item 56 for the NIST Quantitative IR series, items 57 and 59 for the PNNL/NWIR
   naphthalene record; for the jet-cooled band lists of items 61–62 the FEL bandwidth as the
   resolution term and "cold" as the class — else hot; u_296 per molecule per Ladder §2: 1 / 3 / 5 cm⁻¹, recalled), their quadrature sum **u_band**, and the decidability
   verdict per family (feeds pilot-note item 1). Expected: R0 and R1 decidable throughout on their room-temperature
   sources (the hot WebBook naphthalene entries as labelled extra columns); R2 C–C families
   inconclusive by construction unless the correction is pinned.
3. **Gradient availability, run/no-run at equilibrium** (`anchor_gradient_availability.py`):
   per candidate code, does an analytic gradient at the anchor level run **at the equilibrium
   geometry** of benzene and naphthalene with frozen spaces? Prints code, version, run/no-run,
   wall-clock, peak memory. No displaced geometry before the pilot note. K_cap(G), n_min(G) and c(G) come from
   the noise-injected dry run regardless, read at σ_g^assumed (Ladder §4 item 8); the side
   project's M2–M5 later answer per rung.
4. **R0 pilot**: geometry → DFT Hessian → harmonic bands, **timed**; one timed local-CC
   single point with frozen spaces (timing only). Produces **no local-CC Δ₂ and no
   pipeline-vs-lab number**.
5. **R1 smoothness probe** (`q6_smoothness.py`): naphthalene, four modes (a C–C stretch, a C–H
   stretch, a CH-oop mode and one totally symmetric mode), nine points each at q ∈ [−1, 1],
   TightPNO, arms A and B of the Ladder §3 object (never arm C); **σ_E = the RMS residual of ΔE(q) about a degree-4
   least-squares polynomial**, σ_E = √(SSR/(n − p)) with n = 9, p = 5, per mode and arm and
   **pooled over the four modes per arm** (ν = 16) with studentised residuals per point, is
   printed against 0.82·τ·q_s² (2.8·τ·q_s) for each q_s ∈ {0.25, 0.5, 1.0} — the pooled value
   gates, the per-mode values are flagged above twice the pooled; the fit
   coefficients (which contain the diagonal Δ₂ elements) are written to a hashed, sealed file
   that the script refuses to open before the pilot note's commit hash exists. Fixes the pattern
   amplitude (item 13). 72 local-CC energies (4 × 9 × 2).

**After the pilot note is committed:**

6. **R0 probe batch and Q7** (`q7_probing_licence.py`): the R0 responses (symmetric combinations over ± pairs) in hashed order,
   K(R0) and K_off at ρ\* (energies, evaluated per complete pair), the cost record with σ(R_s),
   c₀, RMS_resp, ρ_noise, c, ρ(K), the q₂ block count and the stored ρ(n) curve (the ρ\*_common column NOT_RUN until the
   Q8(c) probe re-prints it); then the references (numerical local-CC Hessian
   with frozen spaces; the canonical CCSD(T) Hessian where the feasibility probe placed it at
   R0, else the local-CC arm's) and the Q7 table (i)–(iv) — the recovered
   Δ₂ printed as a matrix in the DFT mode basis, for the diagonal-only and the full recovery,
   the discriminability factor, the shuffled-probe null, and Q8(a/b) on reference vs
   recovered (R0's only Q8 read). Also the **diagonal-cubic bonus probe** (φ_iii along each
   scored mode from the antisymmetric combinations of the single-mode block plus one further
   amplitude — two extra energies per scored mode, mandatory because the same energies identify
   c₀, Ladder §3; printed in the cost record as the q₂ block, outside K), the opening of the sealed
   smoothness fits, and side-project **M2** (`sp_m2_gradient_benzene.py`: AD gradient with the
   projection inside the graph vs finite differences of the **re-projected** frozen-space
   energy; the mode-G noise line σ_g ≤ 2.8·τ·q_s from nine gradients per Q6 mode, σ_g pooled over all
   3N components; and the third number,
   AD(projection inside) − AD(projection under stop_gradient) per Q6 mode).
7. **Anchor-licence probes** (Q6, `q6_anchor_licence.py`): the bias line at R0 (frozen vs
   canonical Δ₂ per mode); local CC vs canonical and TightPNO vs NormalPNO harmonic-frequency
   deltas at the licence molecule; the CPS decision.
8. **R1**: canonical feasibility at R1 on the B2 laptop; R1 probe batch under the noise-aware
   stopping rule; Q7 twice (with the "tests the recovery, not the freezing" sentence if no
   canonical arm); Q8(a/b) on the reference Hessian (`q8_locality.py`); side-project **M3**
   (naphthalene: the three M2 printouts, wall-clock, peak memory ≤ 28 GB).
9. **Anthracene direct-coupling probe** (dated bonus between R1 and R2; `q8_direct_couplings.py`
   on anthracene with a deck-chosen pair list, four frozen-space energies per (pair, family),
   count printed): Q8(a) per pair against distance; fail-closed reading pre-written in the dated
   note.
10. **Resonance probe** (before any R2 spectrum, DFT level is enough): pyrene CH-stretch
    family via GVPT2 vs raw VPT2 vs MD-ACF; the resonance-closed family set printed.
11. **Classification probe** per rung: `wall_clock_per_probe × K_cap × c_CPS` against the
    168 h checkpoint (Compute_Budget §2).
12. **R2**: the pyrene canonical diagonal check (Q6 bias at R2 size); the **direct-coupling
    probe** (`q8_direct_couplings.py`: deck-chosen π-system pairs at near, mid, far distances;
    per pair and scored family the family-projected coupling ∂²ΔE/∂u_A∂u_B by four-point
    differences at step h — four energies per (pair, family); the full 3×3 block for the near
    pair only; equal frozen counts per bond-count class (near = bonded, mid = 2–3 bonds, far = ≥ 4),
    S_class, n_class and σ_coupling printed; pairs below 3σ_coupling = 3σ_E/(2h²)
    reported "at noise"; agreement within η₈·S_class); the Q6 noise grid at the R2-size
    family in the mode(s) used; probe batches in mode E (and G if licensed) — the structural
    recovery, and the prior-assisted recovery on the same responses
    (`licence_prior_vs_structural.py`: per-family agreement within τ₇, couplings within η₈·S,
    the structural recovery's own Q8(a/b) passed); Q8(a/b) on direct couplings with the
    recovered couplings beside; Q8(c) R1→R2 per mode at the common threshold ρ\*_common (both K_off values printed);
    side-project **M4** (nine gradients per Q6 mode, 36, classified by Budget §2).
13. **R3**: direct-coupling probe; batch (both modes where licensed; both recoveries;
    licence-earning comparison); **fragment-vs-whole** (`fragment_licence.py`: coronene's Δ₂
    from ring-closed, H-capped, unrelaxed fragments at one shell vs whole, per family within τ₇ —
    one comparison, scored per family on the pairs carrying that family's Δ-shift (interior for
    C–C, edge pieces for the CH families); verdict "passed at one shell" / "pending (b′)"); Q8(a/b);
    Q8(c) R2→R3 per mode at the common threshold; side-project **M5** (36 gradients at coronene:
    run/no-run, AD-vs-FD along the four Q6 modes, σ_g pooled at R3 size; classified by Budget §2); the
    cost records side by side.
14. **R4 (fragment licence, parts b′ and c, first instance)**: `fragment_licence.py` on
    circumcoronene — whole vs fragments, conditional on B3 classification of the whole batch
    (the (c) instance below may run under a pending licence; it does not resolve it);
    `fragment_convergence.py` — direct couplings on the central ring from fragments of radius
    r_f and r_f + one shell, agreement within η₈·S; energy count printed and classified by
    Budget §2.
15. **R6 (fragment licence, part c)** (`fragment_convergence.py` on the flake): deck-chosen
    interior and edge pairs, direct couplings from fragments of radius r_f (Ladder §3's rule:
    R3's value, or (b′)'s if larger) and r_f + one shell carved from the R6 DFT geometry,
    agreement within η₈·S; run once, the passing radius printed in the certificate; energy count
    printed (72 × families; ≈ 360 for five) and classified by Budget §2 — expected B3 at two
    shells; whole-flake direct couplings where
    B3 allows.
