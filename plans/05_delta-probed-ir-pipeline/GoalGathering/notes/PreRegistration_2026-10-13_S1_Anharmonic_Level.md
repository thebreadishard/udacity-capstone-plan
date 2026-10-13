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

## Outcome

*(appended after the run)*
