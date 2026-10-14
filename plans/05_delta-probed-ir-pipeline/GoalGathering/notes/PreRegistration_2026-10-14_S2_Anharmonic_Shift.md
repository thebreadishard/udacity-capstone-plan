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

## Amendment 1 (14 Oct 2026, 09:0x, before any S2 force field — 0 of 19 QFF reports exist) — the scale of the test

The user, 14 Oct 08:5x: *'laten we rekening blijven houden met de schaal van de testen. Als een test met beperkt aantal moleculen de 3 cm⁻¹
niet haalt maar wel aantoonbaar nog aan het leren is (validatie fouten dalen nog), dan is de test niet gefaald.'* This is the standing rule
of 19 Sep (no verdict on tiny data; scale along a curve) and of 25 Sep (no negative conclusion without the search). The registration above
lacked both; they are added now, before any number.

**Learning curve.** Inside the leave-one-scaffold-out read, for every held-out scaffold the training molecules are subsampled by scaffold:
k ∈ {4, 6, 8, 10, all} training scaffolds, 20 random subsets per k (numpy seed 0, the same subsets for (b) and (c)). For each k: the pooled
window rms of (b) and of (c), as the mean over the subsets, with the standard error of that mean.

**'Still learning'**, fixed now: the pooled rms at 'all' is below the rms at k = 6 by more than twice the combined standard error, and the
last step (k = 10 → all) is still downward.

**Verdicts, replacing lines 1–3's consequences:**
1. **Line 2 met** (pooled rms ≤ 3.0 cm⁻¹ at 'all'): the route is licensed, to be confirmed on tetracene in S3 (unchanged).
2. **Line 2 missed, the curve still learning: not failed — data-limited.** Next step, registered now: S2b, the next molecules of the same
   universe by the same breadth-first rule (`probes/s2_select.py` continued), as many as a fit rms(k) = a + b·k^(−c) to the curve says are
   needed to reach 3.0 cm⁻¹, priced from S2's own per-Hessian times and put to the user with that price. If the universe (73 molecules) is
   too small for the extrapolated need, it is widened by one rule step (≤ 24 atoms, then O/F/Cl), stated before the selection.
3. **Line 2 missed, the curve flat:** no negative conclusion yet. First the search: the model class (ridge as registered; kernel ridge; a
   small network with early stopping) × the features (as registered; plus the mode's local environment, e.g. the bond orders and ring
   membership of its largest-amplitude atoms), each at this size, the read the same. Only a curve that stays flat after the search reads
   as 'route (b) does not learn Δ_anh from these features'; the next idea is then registered (e.g. a cheap anharmonic input such as a
   semi-empirical force field's own Δ_anh per mode) — the goal stays.
4. **Line 1** ((b) ≤ 0.8 × (c)) is read the same way: if (b) misses it while its curve still descends faster than (c)'s, (b) is not
   stopped; the comparison is repeated at S2b's size.

**Prediction, unchanged and added to:** (b) beats (c); (b) at 'all' reaches 3.0 cm⁻¹ at even odds; if it does not, I expect the curve to
be still learning rather than flat (most of the spread within a family runs with ω, which (b) has and (c) has not).

## Outcome

*(appended after the run)*
