# X9 at naphthalene — the correction's range beyond one ring (run 16 September 2026)

*The decision rule's pending row "the correction's profile beyond one ring (X9 on naphthalene)". Script `experiments/x9_dft_vs_correction_profiles.py --molecule naphthalene_sym --cuts 1,2,3,4,5,6`, outputs `experiments/x9_dft_vs_correction_profiles_naphthalene_sym.{md,json}`. Input: plan 05's symmetrised naphthalene stage A of 15 September (B3LYP and BHHLYP/6-31G* Hessians; the stand-in correction Δ = H_BHHLYP − H_B3LYP, mass-weighted). The benzene run of 12 September is reproduced bit-for-bit by the patched script (regression check before this run). The cuts 4–6 were added today for the longer molecule (naphthalene's bond-graph distance reaches 7; benzene's 3); the pre-stated losing condition of T3′ is unchanged: the ratio ‖Δ[A,B]‖/‖H_low[A,B]‖ does not fall with distance, and Δ's far-block dependence at band level is not a small fraction of H_low's.*

## Norm level (median 3×3 block norm per bond-graph distance)

| graph distance | pairs | median ‖H_low‖ | median ‖Δ‖ | median ratio Δ/H_low | max ratio |
|---|---|---|---|---|---|
| 0 | 18 | 4.64e-05 | 1.61e-06 | **0.035** | 0.035 |
| 1 | 19 | 1.91e-05 | 9.48e-07 | **0.050** | 0.082 |
| 2 | 30 | 4.96e-06 | 2.54e-07 | **0.051** | 0.210 |
| 3 | 38 | 1.57e-06 | 1.11e-07 | **0.070** | 0.464 |
| 4 | 32 | 2.79e-07 | 2.22e-08 | **0.080** | 0.361 |
| 5 | 22 | 1.54e-07 | 1.55e-08 | **0.101** | 0.331 |
| 6 | 10 | 6.44e-08 | 1.28e-08 | **0.198** | 0.255 |
| 7 | 2 | 3.58e-08 | 7.51e-09 | **0.210** | 0.236 |

By pair type the picture splits exactly as X18 did: **C–C pairs** carry the far correction (median ratio 0.18 at d = 2, 0.27 at d = 3, 0.36 at d = 4, 0.33 at d = 5), **C–H and H–H pairs** stay at 0.03–0.10 out to d = 5.

## Band level (zero every block of one object at graph distance ≥ d*, largest exact harmonic shift)

| blocks kept | H_low alone: max shift (cm⁻¹) | Δ alone: max shift (cm⁻¹) | bands > 0.5 cm⁻¹ (Δ) of 48 | ratio Δ/H_low |
|---|---|---|---|---|
| d < 1 | 398.7 | 88.2 | 48 | 0.22 |
| d < 2 | 260.7 | 32.4 | 39 | 0.12 |
| d < 3 | 461.5 | 18.6 | 39 | 0.04 |
| d < 4 | 28.7 | 10.5 | 25 | 0.36 |
| d < 5 | 20.9 | 5.4 | 19 | 0.26 |
| d < 6 | 2.9 | 0.4 | 0 | 0.13 |

## Reading

- **T3′ loses at two rings as it lost at one.** The norm ratio *rises* monotonically with distance (0.035 → 0.21); the correction is the longer-ranged object relative to the Hessian at every distance, and the band-level far-block dependence of Δ is not a small fraction of H_low's once the near blocks are kept (0.26–0.36 at d < 4–5). To hold every band of the correction to 0.5 cm⁻¹, blocks out to graph distance 5 are needed — of a maximum of 7: essentially the whole molecule.
- **The range sits in the ring skeleton.** C–C pair blocks carry the far correction; C–H and H–H blocks do not. This is the same split X18 found from the other side (the C–H stretch correction transfers by local type, the ring families do not), now seen in the correction's own real-space structure on a second molecule.
- **For the main plan:** a fragment-probed correction (plan 05's R6 route) or any real-space truncation must be judged on the ring-skeleton families with the whole molecule as the reference; for the C–H families a local treatment is supported by both X9 and X18. Whether the *coupled-cluster* correction shares this structure is the question the naphthalene deck answers; nothing here goes beyond the DFT stand-in.
- The decision rule's row is filled (§2b); no branch changes state — T3′ was already closed at benzene, and this confirms it does not reopen at naphthalene.
