# Pre-registration — S1: can the anharmonic step run at a cheaper DFT setting? (13 October 2026, before the run)

*Step S1 of `Design_2026-10-13_Spectral_Shape_Anharmonic_Step.md` (TASKS 53). The user agreed with the design (13 Oct 08:0x: 'Eens met
voorstel') and gave the day's standing word ('beslis beredeneerd zelf'). Decisions below are mine on that word.*

## Question

The registered shape test needs DFT anharmonic positions for five molecules of 30–60 atoms. At the labels settings that is ≈ €2,750. If the
anharmonic shift Δ_anh = ν − ω barely moves at a cheaper setting, every price in the design note drops by the setting's speed-up.

## Molecule and settings (fixed)

**Molecule: benzene, not naphthalene.** The design note said naphthalene; benzene is chosen instead, for three reasons:
- it is the molecule on which the analytic-Hessian GVPT2 route was validated against the laboratory (decision 46: 851 / 1004 / 1324 cm⁻¹
  against 849 / 992 / 1310);
- its 61 Hessians per setting cost about a fifth of naphthalene's 97, at about a fifth of the time each;
- the question is the method's sensitivity to the setting, not a size effect. S2 and S3 carry the size.

Naphthalene follows only if benzene's answer is borderline (within 30 % of a line).

**Settings.** All are B3LYP (pyscf's definition), at each setting's own minimum, with reduced-coordinate step 0.10 and Fermi window 200 cm⁻¹
(dpir.qff defaults):

| setting | basis | grid (radial, angular; unpruned) |
|---|---|---|
| **R** (reference) | 6-31G* | 99, 590 — the labels and decision-46 setting |
| **G** | 6-31G* | 75, 302 |
| **B** | 6-31G | 99, 590 |

**Minimum.** Each setting has its own minimum, because VPT2 assumes a stationary point and pyscf's B3LYP and grids move psi4's corpus
geometry. The optimisation is BFGS, then Newton steps in the internal space, to max |g_internal| ≤ 1e-6 E_h/bohr (`probes/s1_anharmonic_level.py
optimise`). Translations and rotations are projected out because without grid response the analytic gradient carries a small net force.
Water smoke: 1.5e-9 at R.

## Quantity and lines (fixed)

Δ_anh per mode: GVPT2 `nu_sym − omega_cm` from `python -m dpir.qff`. Each setting's modes are matched to R's by eigenvector overlap. The
window is the modes with ω_R in 550–2000 cm⁻¹, the shape score's range.

A setting **passes** when both hold:
1. dpir.qff's force-field noise guard passes: the two finite-difference routes of the quartic constants agree within 10 cm⁻¹. A setting that
   trips it fails, whatever its Δ_anh.
2. Against R over the window: rms of the Δ_anh difference ≤ **1.0 cm⁻¹** and max ≤ **3.0 cm⁻¹**.

**Consequence:**
- the cheapest passing setting becomes the anharmonic level of S2 and S3;
- if both G and B pass, the combined setting (6-31G, 75/302) is registered next and read on the same molecule;
- if neither passes, R stays. The design note's prices stand, and route (b) (a learned shift) is the only lever on them.

**My prediction, before the run:**
- G passes. Grid errors in the Hessian largely cancel between the ± displacements, so Δ_anh should move by ≲ 0.5 cm⁻¹. R's own route noise on
  benzene was 0.4 cm⁻¹ quartic.
- B fails on the max line through the out-of-plane modes. Polarisation functions matter for out-of-plane curvature, and so plausibly for its
  quartic terms.

## Smoke (done before this note)

`probes/s1_anharmonic_level.sh` on water, 2 threads (`/home/thebreadishard/s1_smoke_water_e`):
- R's noise guard passed;
- G (75/302) and B (6-31G) tripped it: 14.8 and 10.5 cm⁻¹ quartic route disagreement against the 10 cm⁻¹ limit. Their numbers were
  assembled with `--allow-noisy` for the record only, as the runner now does by rule.

Water's O–H quartics are large, so part of that may be finite-difference truncation rather than noise. Benzene decides.

## Cost, place and stop

- Benzene, 61 Hessians per setting, 4 WSL threads on the laptop. The runner prints each Hessian's time, and the first one prices the run
  before the rest follows. Expected ≈ 5–8 min per Hessian at R, so ≈ 12–20 h for the three settings.
- **Stop rule:** if R's first displaced Hessian takes > 15 min, the run is stopped and re-priced.
- **Start:** when the five-ring pool's laptop runner ends (≈ 16 Oct), so that S1 takes no threads from it. Launched outside the app with a
  wait on F5's end marker.
- The watch follows the markers `=== (S1)`.

## Amendment 1 (13 Oct 2026, 20:0x, before any benzene number) — place and threads

The run moves from the laptop to a CPX62 rented for it (the user created `ubuntu-32gb-hel1-6`, host `s1` in `tools/hosts.tsv`). On the laptop
it would have waited for the five-ring runner until ≈ 25–28 Oct; the anharmonic level decides the price of the whole shape test, so two
weeks matter. The three settings run in parallel, 5 threads each (`PARALLEL=1`, new in `probes/s1_anharmonic_level.sh`), instead of one
after another at 4. Settings, step, lines, prediction and the stop rule (R's first displaced Hessian > 15 min: stop and re-price) are
unchanged. The server first repeats the water smoke in the parallel mode (`probes/bootstrap_s1_cpx62.sh`); the laptop's waiting S1 was
stopped before it started.

## Amendment 2 (13 Oct 2026, 21:5x, before any benzene Δ_anh) — what each outcome costs, and a second symmetry saving

At the time of writing no QFF of benzene has run: R has 22 of its 60 displaced Hessians, G 50, B 33. The level rule above stands unchanged.
This amendment fixes, before the numbers, what follows from each outcome for the five large molecules.

**Measured cost per displaced Hessian on benzene** (s1, 5 threads per setting, the three settings in parallel; median interval between
Hessian files): R 234 s, G 112 s, B 162 s. G is 2.1× and B 1.4× cheaper than R — not the 3–5× that the design note's route (a) needed to
make the five affordable. These are benzene's ratios; the grid's share of a Hessian falls as the basis grows, so G's saving on the large
molecules is likely smaller.

**A second symmetry saving** (`probes/qff_symmetry_count.py`, counts and prices in `probes/results_m1/qff_symmetry_count_2026-10-13/`).
Of a degenerate pair (a, b) only the +δa Hessian is computed: with a chosen as an eigenvector of eigenvalue −1 of an operation restricted to
the pair, its images under the group come in ± pairs on at least three lines, which give ∂H/∂q_a, ∂H/∂q_b and Q_aa, Q_ab, Q_bb by least
squares. Hessians per molecule (± saving → ± and pair saving): benzene 33 → 23, coronene 109 → 75, HBC 192 → 134 (PAHdb's geometry, D3d;
more if our optimised geometry is D6h); tetracene 100, peropyrene 135 and ovalene 156 have no degenerate modes. The five at R:
€2,715 → €2,157; at G €1,300 → €1,032; at B €1,880 → €1,493 (lane-hours of the design note §2 × benzene's setting ratio × €0.21).

**Decision rule, fixed now:**
1. The level is the cheapest passing setting of the consequence above.
2. Route A — full GVPT2 at that level, with the ± and, once step 4 passes, the pair saving — for tetracene, coronene and peropyrene:
   €418 at R, €200 at G, €289 at B with pairs. These three are S3's validation set. The first Hessian of each is timed on the target before
   the rest runs, and the price is restated from that time.
3. Ovalene and HBC (€1,739 at R, €832 at G, €1,204 at B, with pairs) are not started by this rule. They go to the user with their re-timed
   price, beside routes (b) and (c) validated on the three molecules of step 2.
4. The pair saving enters production only after it reproduces the direct result on benzene, at no extra cost: from S1's own R Hessians,
   rebuild each pair's second-partner Hessians from the first by the group, and compare GVPT2 Δ_anh over the window with the direct one.
   Lines: rms ≤ 0.2 cm⁻¹ and max ≤ 0.5 cm⁻¹, below R's quartic route noise on benzene (0.4 cm⁻¹, prediction section). If it fails, the
   prices without the pair saving stand.

*Note (22:0x, still before any S1 number; development, not the registered test).* `probes/qff_symmetry_rebuild.py` was tried on the 21 Sep
benzene set at R's settings (`probes/results_m1/qff_symmetry_rebuild_dev_2026-10-13/README.md`): the ± saving moves Δ_anh by rms 0.03 / max
0.09 cm⁻¹, the pair saving by 0.56 / 1.06 — it fails step 4's lines there. On exactly symmetric model data both rebuilds are exact up to the
shared finite-difference truncation, so the method is sound; the DFT images under operations that do not map the Lebedev grid onto itself
differ by 2.4e-2 of the displacement signal against 3.0e-3 for those that do. The pair saving needs C₆/C₃, which no octahedral grid has.
My expectation for step 4 on S1's data: the ± saving passes, the pair saving fails, and the prices without it stand (€2,715 at R, €1,300
at G). The test runs as registered.

## Outcome

*(appended after the run)*
