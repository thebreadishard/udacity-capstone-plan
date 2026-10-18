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

## Amendment 1 (14 Oct 2026, 10:3x, before any S2 force field — 0 of 19 QFF reports exist) — the scale of the test

The user, 14 Oct ≈ 10:2x: *'laten we rekening blijven houden met de schaal van de testen. Als een test met beperkt aantal moleculen de 3 cm⁻¹
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

## Development note (14 Oct 2026, 18:5x, before any S2 force-field report was read) — the read's implementation

`probes/s2_read.py` (tests `tests/test_s2_read.py`: an exact linear shift recovered by (b), an unseen family, the 'still learning' rule,
the data-limited and flat readings, the loader on S1's benzene) implements the read above with amendment 1. Three choices the text left
open, fixed now:
1. **Training modes:** both routes are fitted on the training molecules' modes inside the window (550–2,000 cm⁻¹), the modes they are
   scored on. Below 550 cm⁻¹ are the torsions and methyl rotors, whose VPT2 shifts are not this read's object.
2. **The features h and o** are the family rule's own numbers (`e8_cc_locality.mode_shares`, factored out of `families` with identical
   output, checked on S1's three benzene settings and a non-planar variant); o is taken without the rule's planarity gate, so a methylated
   molecule keeps its out-of-plane feature (its family is still assigned by the rule as is).
3. **A family absent from a training subset** (possible only at small k): its held-out modes are predicted by the training window mean in
   both routes and counted in the output.
The learning-curve subsets are drawn with numpy `default_rng(0)` in the order k, subset, held-out scaffold, the same for both routes.
End-to-end dry run on S1's G/R/B benzene directories posing as three scaffolds (numbers meaningless by construction) and one missing
molecule, which the read names as excluded.

## Note (15 Oct 2026, 07:2x) — why styrene tripped the noise guard; a diagnosis of an excluded molecule, not a read

Styrene (A_8f6ed7c002) is excluded by the noise rule (route disagreement 10.7 cm⁻¹ against 10). `probes/qff_noise_diagnosis.py` on its report
(`probes/results_m1/qff_noise_styrene_2026-10-15/`; the script reproduces the report's ν exactly): all five worst constants couple mode 0, the
vinyl torsion (40 cm⁻¹, out-of-plane share 1.00, 77 % on the vinyl atoms) — with modes at 449, 1,714 (vinyl C=C), 1,038, 450 and 208 cm⁻¹.
Swapping route a for route b moves the window's fundamentals by at most 1.15 cm⁻¹ (rms 0.30). The literature's remedy for a large-amplitude
torsion — the mode decoupled from VPT2 (V30 benchmark's VPT2+R; HDCPT2's hindered rotors) — moves them by up to **4.6 cm⁻¹ (rms 1.24)**: how the
torsion is treated weighs more than the noise the guard saw, and the same holds, in some measure, for the molecules with rotatable
substituents that passed it. S2's read is unchanged (styrene stays excluded, nothing else is touched); a rotor policy is a question for the next
registration (TASKS 62).

## Outcome

*(appended after the run)*

## Note (18 Oct 2026, 13:xx — AFTER the read; two gaps in the read's rules, and the verdict the user chose)

S2 ended with 14 usable molecules in 9 scaffolds (5 NOISY, 1 FAILED; `probes/results_m1/s2_anharmonic_2026-10-18/`, FETCHED 3,758 files).
Pooled window rms at 'all': (b) 9.72, (c) 11.96 cm⁻¹; per family (b) ring-ip 3.15, CH-oop 5.67, other 18.85. Line 2 is missed by both routes.

**Gap 1 — degenerate k.** With 9 scaffolds every held-out scaffold has 8 training scaffolds, so k = 8 and k = 10 draw the full set: those
rows equalled 'all' to 1e-14, and 'the last step (k = 10 → all) still downward' compared 'all' with itself and passed on rounding. The first
read (`read/`) printed 'still learning — data-limited, next S2b' on that. `probes/s2_read.py` now gives no row to a k that equals the full set
and takes the last step from the largest real k (here 6 → all: 9.77 → 9.72, down by more than twice the SE).

**Gap 2 — a descent towards an asymptote above the line.** Verdict 2 sizes S2b by the fit rms(k) = a + b·k^(−c). S2's fit has a = 9.68 cm⁻¹,
above the 3.0 line, so no number of molecules reaches it and S2b has no size. The read now says so: a curve that still descends but whose
fitted asymptote is at or above the line reads as flat (verdict 3). The per-family curves (`read_v2/`, new in the read, the registered
quantities unchanged) are flat in the same way: k = 4 → 6 → all, (b) ring-ip 3.32 → 3.20 → 3.15, CH-oop 5.81 → 5.73 → 5.67, other
19.04 → 18.93 → 18.85.

**Verdict (the user, 18 Oct, 'Ja, akkoord met verdict 3 en de zoektocht'):** verdict 3 — no negative conclusion; the search (model class ×
features) first, its form registered before any of its numbers. These two rules were written after the numbers were seen; they are stated
here so that a reader can judge them, and they change no registered number.

## Amendment 2 (18 Oct 2026, 13:3x — after the read and step 0, before any number of the search or of the GVPT2 labels)

The user, 18 Oct: *'Ja, stel amendement 2 op en begin met GVPT2.'* Step 0 (exploratory, `probes/results_m1/s2_anharmonic_2026-10-18/`
`diagnose/` and `label_check/`, commits fada4c4a and f3339ef3) found that route (b)'s error is bias, not variance (in-sample ≈ held-out in
every family), and that part of it is in the labels, not the model: (i) ring-ip labels move by 1.95 cm⁻¹ rms between two legitimate
deperturbation settings (min K 0 and 1), 33 % of them are resonance-affected and the polyads are not diagonalised; (ii) the ethynyl ≡C–H
bends' labels are the small sum of four terms of 140–340 cm⁻¹ (VPT2 in rectilinear normal coordinates for a linear X–H bend); (iii) CH-oop
labels are clean (0.16), so CH-oop's 5.7 is the model's. This amendment fixes, in this order, the labels, the scope and the search.

**1. Labels: GVPT2.** Each molecule's fundamentals are recomputed from its stored force constants (no new force field): dpir.qff's χ with
Martin's threshold (min K 1 cm⁻¹, window 200 cm⁻¹ — pyVPT2's defaults, `FERMI_K_THRESH` and `FERMI_OMEGA_THRESH`), then the Fermi polyads
(fundamental with overtone, type 1; fundamental with combination band, type 2) diagonalised by pyVPT2's `fermi_solver` — the upstream
implementation, tested in pyVPT2's `tests/test_polyad.py`, `tests/test_fermi_solver.py` and, end to end with `GVPT2: True`,
`tests/test_h2co.py`. Overtone and combination energies from χ by the standard expressions pyVPT2's `process_vpt2` uses. The label is the
GVPT2 fundamental minus ω. **Validation before any S2 number:** (a) with no resonance the GVPT2 fundamental equals the DVPT2 one; (b) the
trace of every polyad is conserved; (c) H₂CO end to end: pyVPT2's own force constants of its `test_h2co` fed through our path reproduce
pyVPT2's GVPT2 fundamentals to 0.1 cm⁻¹ (the test's own tolerance). A resonance that involves an exactly degenerate mode (benzene) keeps
its DVPT2 label and is named (pyVPT2 leaves multiple degeneracies open). The label floor per family is reported beside every read:
|GVPT2 − DVPT2(K 1)| and the route difference.

**2. Scope.** Linear X–H bends — modes whose hydrogen kinetic-energy share sits mostly (≥ 0.5 of the mode's h) on hydrogens bonded to an
sp carbon (C–C ≤ 1.25 Å on that carbon) — leave the read: their label is not a property VPT2 in these coordinates can deliver to 3 cm⁻¹,
and the mandate's large PAHs carry no ethynyl group. Every read is reported with and without them. 3-ethynylstyrene stays excluded (NOISY).

**3. The search** (verdict 3), on the GVPT2 labels within the scope, per family (CH-oop, ring-ip, other), leave-one-scaffold-out as
registered: models {ridge as registered; kernel ridge, RBF; a one-hidden-layer network (32 units) with early stopping on an inner
validation split, decision 51} × features {as registered (family, ω/1000, h, o); + the mode's local environment (for its largest-amplitude
atoms: ring count, heteroatom neighbour, the C–H adjacency class solo/duo/trio/quartet); + resonance proximity (the smallest |2ω_j − ω_i| and
|ω_j + ω_k − ω_i| with its Martin K)}. **Nested**: each outer held-out scaffold's combination and hyper-parameters are chosen by an inner
leave-one-scaffold-out on its training scaffolds only; the outer score is pooled per family. Nine combinations on 14 molecules would
otherwise flatter the winner.

**4. Lines and readings.** Per family, line 2 (rms ≤ 3.0 cm⁻¹ at 'all') licenses that family; the learning-curve rules as amended (a curve
whose fitted asymptote is at or above the line reads as flat). A family whose label floor is itself near the line is read against it and
said so. Flat after the search → the next idea is registered before it runs: a cheap anharmonic input per mode (GFN2-xTB VPT2 Δ_anh) for
Δ-learning — the goal stays. Everything runs on the laptop; no new force field.

**Predictions.** GVPT2 lowers ring-ip's labels' spread and route (b)'s ring-ip rms to ≤ 3.0; CH-oop improves most from the adjacency class
(the C–H out-of-plane bands of PAHs are classified by it); 'other' without the ethynyl bends falls to the 3–5 cm⁻¹ of the other eleven
molecules before any model change.

## Amendment 2, §1–2 outcome (18 Oct 2026, 13:46 — before the search of §3)

**Validation passed.** (a) and (b) in `tests/test_gvpt2_labels.py`; (c) H₂CO end to end: our path reproduces pyVPT2's deperturbed and GVPT2
fundamentals to 5e-13 cm⁻¹ (`probes/results_m1/s2_anharmonic_2026-10-18/gvpt2_validation/`). **Upstream pyVPT2's polyad solver fails on S2's
molecules** (eigenvalue-to-state assignment raises KeyError when two eigenvectors peak on one state; an interaction bridging two polyads is
not merged — 7 of 14 molecules have such bridges): fixed in the fork, branch `polyad-assignment-and-merge` (eb353ab, two tests that fail on
the old code; the upstream suite passes); the labels name the solver file's sha256. Benzene's 16 resonances touch degenerate modes and
stay deperturbed, as §1 says.

**Reads (route (b) / (c) at 'all', cm⁻¹; `read_a2_*`):**

| labels, scope | pooled (b) | CH-oop (b) | ring-ip (b) | other (b) | other (c) |
|---|---|---|---|---|---|
| DVPT2, all (the registered read) | 9.72 | 5.67 | 3.15 | 18.85 | 19.76 |
| DVPT2, no linear X–H | 7.25 | 5.81 | **2.88** | 13.63 | 13.22 |
| GVPT2, all | 10.01 | 5.65 | 4.06 | 19.06 | 19.97 |
| GVPT2, no linear X–H | 7.68 | 5.78 | 3.90 | 14.00 | 13.61 |

**Predictions against outcome.** (1) 'GVPT2 lowers ring-ip to ≤ 3.0' — **wrong**: ring-ip rises from 2.88 to 3.90. The polyads move 6–19
fundamentals per molecule by up to 35 cm⁻¹; that push depends on how close a combination band happens to lie, which (b)'s features do not
see. GVPT2 is the label that corresponds to the observed band, so the harder target is the right one; the resonance-proximity features of
§3 are the registered answer. (2) ''other' falls to 3–5 without the ethynyl bends' — **wrong**: 18.85 → 13.63; five modes leave, most of
the error stays. (3) CH-oop's error is the model's — consistent (its labels barely move: 5.67 / 5.81 / 5.65 / 5.78). Noted in passing:
removing five modes moved ring-ip from 3.15 to 2.88 although no ring-ip mode left — the shared h and o coefficients of (b) were bent by the
outliers. The search of §3 runs on GVPT2 labels, no linear X–H, as registered.
