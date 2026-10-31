# Pre-registration — the first-order geometry term beyond benzene (TASKS 156 (d))

31 October 2026, 16:1x. Written before any run on the 18 molecules (the water smoke ran first; its numbers are below, as the smoke).
TASKS 156 (d), TASKS 53 (the anharmonic step), decision 48 (the geometry term as a fixed step, 22 Sep 2026). Code:
`probes/geometry_term_check.py` (`run` in WSL with pyscf, `read` without); tests `tests/test_geometry_term_check.py` (synthetic records:
the term found exactly through the true displacement and the Newton step, 18 such molecules pass every line, cubic constants of the
wrong sign fail A and C, a missing run, a run on another force field and a reference whose ω are not the force field's are refused).
The optimiser is S1's (`probes/s1_anharmonic_level.py`: `newton_polish`, now with the functional as a setting, B3LYP by default).

## Why

An anchor's Hessian is computed at the B3LYP/6-31G* geometry, not at its own level's minimum, and the network learns the same: its target
is the higher level's Hessian at the B3LYP geometry. A band then sits where a spring stretched to the wrong length would ring. To first
order the shift to the higher level's minimum is Δω_i = ½ Σ_k φ_iik Δq_k, with φ the cubic constants and Δq the displacement in reduced
normal coordinates. On benzene (22 Sep) the rule held to about 10 % against HF's own minimum and took the C–H stretches from 52 to 14 cm⁻¹
against CCSD(T). It has not been tried on another molecule. The product needs it per molecule, with that molecule's cubic constants.

## The design

The 18 molecules whose quartic force fields exist at the anharmonic level G (S2, `probes/results_m1/s2_anharmonic_2026-10-18/s2/*/G`:
B3LYP/6-31G*, grid 75/302, pyscf exact integrals, at G's own minimum x0): naphthalene, acenaphthylene, biphenylene, quinoxaline, styrene,
indene, phenylacetylene, quinazoline, azulene and nine layer-B molecules (12–20 atoms). The higher level is ωB97X/6-31G* at grid 99/590
(the proxy's labels). Per molecule (`run`): ωB97X's energy, gradient and analytic Hessian at x0, then Newton steps in the internal space
with that Hessian held (gradients only) to its own minimum x_T (max |g| ≤ 1e-6 E_h/bohr), and its Hessian at x_T: two Hessians a
molecule (pipeline 0.4's phenanthrene Hessian took about an hour on the laptop at six threads, so ≈ 18–36 h for the 18).

The read (`read`), per mode of G at x0:
- **measured** Δω = ω_ωB97X(x_T) − ω_ωB97X(x0), ωB97X's modes paired across the two geometries by overlap, then to G's modes;
- **predicted** ½ Σ_k φ_iik Δq_k with G's cubic constants and Δq from (i) the true displacement x_T − x0, (ii) the first Newton step at x0
  (ωB97X's gradient and Hessian there — what a product could compute without optimising), (iii) ωB97X's gradient over G's curvature
  (printed, not read).

Modes the geometry moves by less than 1 cm⁻¹ are not read. Windows by G's ω: below 1000, 1000–1900, 1900–2700, X–H stretch above 2700.

## The lines (read by `geometry_term_check.py read`, all 18 molecules required)

- **A — the rule carries:** pooled over the modes read, rms(measured − predicted (i)) ≤ 0.30 × rms(measured).
- **B — the product's estimate carries:** the same with (ii), ≤ 0.35 × rms(measured).
- **C — no window made worse:** in every window with ≥ 10 modes read, rms(measured − predicted (i)) ≤ rms(measured).
- **D — per molecule:** the term lowers the rms in at least 16 of the 18 molecules.

All four hold → the geometry term is validated at DFT scale on 18 molecules beyond benzene, with the numbers, and enters the product's
design (TASKS 53) with each molecule's cubic constants and a gradient estimate. A fails → the rule does not transfer to another level with
B3LYP's cubics, and the benzene result stays one molecule. B fails with A holding → the rule holds but the one-step estimate of the
displacement does not; the product would need the optimisation. C or D failing names where the term misleads.

## Prediction

**All four hold.** The shift is dominated by the X–H stretches (shorter bonds at ωB97X), where the semi-diagonal cubics are large and
smooth; the rule is first order in a displacement of a few thousandths of an ångström. Expected residual 5–15 % of the shift pooled, larger
below 1000 cm⁻¹, where the shifts are small and G's cubics for soft rotors are the noisiest (the vinyl rotor's grid noise at 75/302, TASKS
156 (c)); the 1 cm⁻¹ floor keeps most of those out. The Newton estimate within a few percent of the true displacement: x0 is close to x_T.

## The smoke (water, before the registration)

`probes/results_m1/geometry_term_2026-10-31/smoke/water` on S2's water force field at G: three steps on the held Hessian (2 Hessians,
19 s at two threads); measured shifts 14.9 (bend) and 64.8 cm⁻¹ rms (O–H stretches); residual after the term 0.48 cm⁻¹ (true Δq), 0.55 (Newton Δq),
1.75 (G's curvature). Read only as a check that the code runs end to end and that the shifts are of the expected sign and size.

## Outcome

(after the run)
