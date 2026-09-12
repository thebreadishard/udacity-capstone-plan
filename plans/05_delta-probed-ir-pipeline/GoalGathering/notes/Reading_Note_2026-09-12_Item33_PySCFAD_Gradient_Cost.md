# Reading note 2026-09-12 (evening) — item 33 read for the gradient-to-energy cost ratio g (step 1 of the "does plan 06 make plan 05 cheaper?" ladder)

*Zhang, Li, Ye, Berkelbach & Chan, "Performant automatic differentiation of local coupled cluster theories: response
properties and ab initio molecular dynamics", J. Chem. Phys. 161, 014109 (2024), DOI 10.1063/5.0212274; arXiv:2404.03129;
PDF held (`Papers/Zhang_2024_PySCFAD_local_CC_gradients.pdf`, 29 pp.), text extracted and read in full on 2026-09-12 for one
question: what does one LNO-CCSD(T) nuclear gradient cost relative to one energy in their engine (the "g" of decision 34 and
plan 06's S5)?*

## The answer: the paper does not print g

Read for it specifically — §III A (nuclear gradient and dipole moment), §IV D (AIMD), the supporting information S1 C
(performance optimisation), S2 A (performance of PySCFAD, Fig. S1), S2 B (Baker test set, Fig. S4) and S2 D (AIMD).
No sentence, table or caption gives the ratio of gradient time to energy time. What the paper does give, and what it
implies:

1. **Reverse-mode AD with recomputation.** The gradients are reverse-mode (one backward pass per gradient, "efficient
   when the number of objectives is less than the number of variables"); the (T) correction is recomputed on the fly in
   the backward pass, memory-intensive intermediates are recomputed rather than stored (`jax.checkpoint`), and the
   largest stored tensor is the ov|vv integral block. Consequence for g: the backward pass costs of the order of the
   forward pass plus the recomputations — a small constant, not stated.
2. **Fig. S1 (water clusters, cc-pVDZ):** wall times of "MP2 energy and nuclear gradient" together (a) and CCSD energy
   (b), PySCFAD against PySCF: "comparable performance … PySCFAD slightly falling behind" (JIT tracing). Energy-only
   and gradient-only bars are not separated; g is not readable from it.
3. **Fig. S4 (Baker set, cc-pVTZ):** "total wall time of computing energy, nuclear gradient, and dipole moment" for
   LNO-CCSD(T) at three cutoffs against canonical CCSD(T): "one to two orders of magnitude more efficient than canonical
   CCSD(T) even without parallelization over the fragments" at loose and moderate cutoffs (γ = 10⁻⁴, 10⁻⁵; accuracy
   ≈ 10⁻³ and 10⁻⁴ a.u. in gradients); tighter cutoffs can exceed canonical cost; the per-fragment wall time is
   "almost constant" across molecule sizes. Again the three quantities are summed; g is not separable.
4. **AIMD:** LNO-CCSD(T)/cc-pVTZ trajectories of the protonated water hexamer, 2.5 ps at 0.5 fs (5,000 gradient
   evaluations per trajectory, four conformers, plus multiple-time-step runs) at cutoff 5 × 10⁻⁶. No per-step time is
   printed. The existence of these trajectories shows that an LNO-CCSD(T) gradient of an 18-atom system at cc-pVTZ is
   affordable enough for thousands of evaluations on one node; it does not give g.
5. **Two remarks that matter more to plan 05 than g:** (a) "the LNO-CC method … neither yields a continuous energy
   function across the potential energy surface, nor preserves the molecular point-group symmetry", so LNO gradients
   "may inherently contain errors stemming from the energy discontinuity or the symmetry breaking"; **benzene is named
   as an outlier** (molecule 7 of the Baker set) with large gradient errors "likely due to symmetry breaking". This is
   exactly the discontinuity plan 05's frozen spaces remove (probe M1) — so a frozen-space gradient in PySCFAD would be
   both the cheap product decision 34 needs *and* the cure for their outlier. (b) The one-orbital fragment scheme is
   "nearly three times more expensive than the multi-orbital scheme" (S2 C) — plan 05 uses one fragment per LMO; a
   multi-orbital fragmentation is a cost lever the side project can test.

## What this means for the ladder

- Step 1 closes with **"not in the literature as a number"**. The honest statement for the proposal and the cover
  note stays what decision 34 already says: the substitution layer pays only with gradients; whether g is 2 or 20 is
  unknown until measured.
- The measurement is the side project's M2, and this paper is its engine and its warning: measure g on benzene at
  cc-pVDZ with *frozen* spaces (arm A), where the symmetry-breaking outlier should disappear. That is a stronger and
  cheaper first milestone than the general M2 text, and it is now step 4 of the ladder in the README's owed list.
- Nothing here changes a rule. Bibliography item 33: status "read in full for g on 2026-09-12; g not printed".

## Step 1b (same evening): is g priced anywhere else? What a verified search found

The user asked whether the ratio is priced "nowhere in the literature". Searched via Crossref (journal articles only)
and the open texts reachable tonight:

- **The general theorem exists and is citable; its constant was not read tonight.** The "cheap gradient" result of
  reverse-mode algorithmic differentiation — the gradient of a scalar function costs at most a small constant multiple
  of the function evaluation — goes back to Baur & Strassen, "The complexity of partial derivatives", *Theoretical
  Computer Science* 22(3), 317–330 (1983), DOI 10.1016/0304-3975(83)90110-X (record verified), and is the subject of
  Griewank & Walther, *Evaluating Derivatives*, 2nd ed., SIAM 2008, DOI 10.1137/1.9780898717761 (record verified).
  Both texts are paywalled; Griewank's open survey in Documenta Mathematica (2012) could not be fetched (three hosts,
  redirect chain ending in 404). **The constant is therefore not quoted here.** What it would give is an upper bound
  on g for an AD engine like PySCFAD, not a measurement in our engine — and PySCFAD's own recomputation
  (`jax.checkpoint`) trades memory for extra forward work, so the practical g sits above the theoretical bound.
- **Analytic gradients of local correlation methods in the literature:** DLPNO-MP2 (Pinski & Neese, *J. Chem. Phys.*
  148, 031101 (2018), DOI 10.1063/1.5011204; and 150, 164102 (2019), DOI 10.1063/1.5086544 — abstract read: largest
  gradient for crambin, 644 atoms, no cost ratio in the abstract); local MP2 with intrinsic bond orbitals (Dornbach &
  Werner, *Mol. Phys.* 117, 1252 (2019), DOI 10.1080/00268976.2018.1537529, record only). **No analytic-gradient paper
  for DLPNO-CCSD(T) or PNO-LCCSD(T) surfaced** in three Crossref searches; the Werner-group hits are energy methods
  (PNO-LCCSD, PNO-LCCSD-F12, 2017–2021). So at the CCSD(T) level the only published local-CC gradients found are the
  AD ones of item 33, which do not print g.

Conclusion of step 1 as a whole: **g is not in any text read or reachable tonight**; the theorem bounds it by a
constant that was not read; the two MP2-level gradient papers do not state a ratio in their abstracts (full texts not
opened). Step 4 — measuring g in our engine — remains the only source of the number.

