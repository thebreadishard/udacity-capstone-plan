# S2 — can a per-mode anharmonic shift be learned? (registered 14 Oct 2026, before any S2 computation)

*TASKS 53; design note `Design_2026-10-13_Spectral_Shape_Anharmonic_Step.md` §3 (b) and (c), §5. The user, 14 Oct 07:0x: 'Akkoord' to S2
on the server `s1` for a few days. S1 (registration `PreRegistration_2026-10-13_S1_Anharmonic_Level.md`, outcome 14 Oct 00:1x) made G
(B3LYP/6-31G*, grid 75/302) the anharmonic level.*

## Question

The spectral shape of a large PAH needs Δ_anh = ν − ω per mode. Full GVPT2 (route A) costs ≈ €32 for tetracene but ≈ €811 for HBC at G, and
cannot be run for every molecule the pipeline is asked about. Can Δ_anh be predicted per mode from the mode's own description — route (b) —
well enough for the shape, and better than one constant per family — route (c)?

## Training set (fixed by rule before any molecule was looked at)

`probes/s2_select.py`, output `probes/results_m1/s2_training_set_2026-10-14/selection.json`: corpus molecules done, ≤ 20 atoms, neutral,
C/H/N, not in hold-out (b) — 73 molecules in 14 Murcko scaffolds. All 10 hydrocarbons are taken; 10 nitrogen-containing molecules follow,
breadth first over scaffolds (decision 52). The 20 span 13 scaffolds. Benzene's GVPT2 at G is S1's; the other 19 are computed.

## Computation

GVPT2 at G for each molecule at its own G minimum, full ± displacements along every mode (no symmetry saving: most of these molecules have
low symmetry, and the full sets give the ± saving a second test), step 0.10, `python -m dpir.qff` with its noise guard. Runner
`probes/s2_batch.sh` → `probes/s1_anharmonic_level.sh`, three molecules at a time, 5 threads each, on `s1`.

**Stop rule per molecule:** the first displaced Hessian takes > 1,800 s → that molecule stops ('STOPPED') and is re-priced; the others go on.
**Noise rule:** a molecule whose force field trips the noise guard (quartic route disagreement > 10 cm⁻¹) is excluded from training and read,
and named in the outcome.

## The two predictors (fixed now)

Per mode: ω (cm⁻¹), the family by the corpus rule (`e8_cc_locality.families`: CH-stretch, CH-oop, ring-ip, other), the hydrogen share h and the
out-of-plane share o of the mass-weighted mode.
- **(c) family constants:** Δ_anh = mean of the training modes of the mode's family.
- **(b) per-mode model:** Δ_anh = a_f + b_f · ω/1000 + c · h + d · o, a_f and b_f per family, least squares with a ridge of 1e-3 on all
  coefficients (features as given, no scaling).
Degenerate pairs enter with dpir.qff's symmetry-averaged ν (`nu_sym`), each mode once.

## Read

Leave one scaffold out: for each of the 13 scaffolds, (b) and (c) are fitted on the molecules of the other scaffolds and predict the held-out
scaffold's modes. The figure of merit is the rms of predicted − GVPT2 Δ_anh over all held-out modes with ω in 550–2000 cm⁻¹ (the shape
score's window), pooled over the scaffolds; the per-family rms is reported beside it.

**Lines:**
1. **(b) is built further** if its pooled rms ≤ 0.8 × (c)'s. Otherwise (b) stops and (c) is the learned route.
2. **A route is licensed for the large PAHs** if its pooled rms ≤ 3.0 cm⁻¹ — a third of the shape score's Gaussian FWHM at 1,000 cm⁻¹
   (1 % of ν, fixed 14 Sep). The license is confirmed on tetracene in S3: route-A GVPT2 against the licensed route's prediction, same line.
3. If neither route passes line 2, ovalene and HBC get the anharmonic step only by route A (priced, on the user's word), or none — the
   certificate then says 'harmonic, scaled'.

**My prediction, before any number:** (b) beats (c) by more than 20 % (Δ_anh within a family runs with ω, benzene's ring-ip modes span −11 to
−40 cm⁻¹ at R); whether (b) reaches 3.0 cm⁻¹ I rate as even odds.

## Outcome

*(appended after the run)*
