# Plan 06 — result note X5 (2026-09-12): where the benzene correction lives in real space

*Printed by `experiments/x5_atom_pair_structure.py` on plan 05's sealed benzene dry-run tensor (B3LYP → BHHLYP,
6-31G*; the stand-in with the algebraic form of CC − DFT). Full table in `experiments/x5_atom_pair_structure.md`.
First data test of S1 (locality) in real space rather than in pair energies, and a second test of S2 (low rank)
after X1's "full rank in mode space".*

## Method

The dry run displaces `x = x0 + Minv ⊙ (L q/√ω)`, so the probed mode-space curvature `D_q` maps to the
mass-weighted Cartesian correction `H_y = L diag(√ω) D_q diag(√ω) Lᵀ` (36 × 36, rank ≤ 30). **Validation:** the
stored full Hessian difference `H_high − H_low` of the same run, mass-weighted with the file's `Minv` and projected
on the vibrational subspace, agrees with the probed matrix to a relative residual of **2.4 × 10⁻¹⁵** (the
unweighted reading gives 9 × 10³, so the stored Hessians are plain Cartesian and the transform is right). The
matrix is then cut into 3 × 3 atom-pair blocks. Noise floor per block: X2's per-element noise (σ_E/2 = 0.25 µE_h
per q² element, 200 draws) pushed through the same transform.

## Result

**Rank.** Numerical rank 30 of 30 (as in mode space). Frobenius fraction in the top k eigen-directions:
k = 1: 0.07, 3: 0.21, 5: 0.34, 10: 0.59, 15: 0.82, 20: 0.96. No low-rank structure in real space either.

**Atom-pair blocks** (fraction of ‖Δ‖²_F; 12 atoms, 78 distinct blocks):

| pair type | blocks | fraction of ‖Δ‖²_F | median block norm / median noise floor |
|---|---|---|---|
| on-atom | 12 | **0.719** | 670 |
| C–H bonded | 6 | **0.170** | 450 |
| C–C non-bonded (meta, para) | 9 | 0.054 | 300 |
| C–C bonded | 6 | 0.046 | 335 |
| C–H non-bonded | 30 | 0.009 | 36 |
| H–H non-bonded | 15 | 0.003 | 22 |

On-atom plus bonded blocks carry **93.5 %** of the norm; everything beyond a bond carries 6.5 %. Yet **all 78
blocks lie above three times the noise floor** (the smallest by a factor 20): nothing is zero at plan 05's
noise. Distance profile of the off-atom blocks (median norm, bohr): 2.1 (C–H bond) 1.8e-6; 2.6 (C–C bond)
9.3e-7; 4.6 (C–C meta) 8.1e-7; 5.3 (C–C para) 8.4e-7; 4.1 and 6.4 (C···H) 2.4e-7 and 1.4e-7; 7.3–9.4 (H···H,
far C···H) 0.5–1.2e-7.

## Reading

1. **Real-space locality is real but not sharp.** Ninety-three per cent of the correction sits on atoms and
   bonds; the rest is small but everywhere measurable. That is the same shape X3b found in the pair energies
   (λ = 0.75 Å, but 2.3 % of E_corr beyond 3 Å): a fast decay with a floor above the noise. A real-space
   truncation of the correction is therefore an *approximation with a controllable error*, not an exact
   shortcut — E2/E3, not E1 — and the error it makes at benzene (6.5 % of the norm, spread over 60 blocks)
   would have to be scored in band positions before it is used.
2. **The ring does not decay like a chain.** The C–C meta and para blocks (4.6 and 5.3 bohr) are as large as
   the C–C bonded blocks (2.6 bohr) — the distance profile is flat across the carbon ring and drops only for
   pairs involving hydrogen. For a conjugated π-system the correction is a *ring* property, not a bond
   property. That is the structural reason X3b found nothing droppable at naphthalene, and it is the first
   real-space hint of what S3 (quasi-1D π-systems) would have to exploit: the nonlocality is confined to the
   π-skeleton, which is one-dimensional-ish along the ring.
3. **S2 is now negative twice** (mode space in X1, real space here): the correction is not low-rank on this
   tensor. What remains for S2 is only the possibility that the *true* CC − DFT tensor behaves differently from
   the DFT − DFT stand-in; that test waits for the R0 pilot's Δ₂.
4. **For S1 the useful object is now visible:** a σ-frame (on-atom + bonded, 93.5 %) plus a π-ring correction
   (the flat carbon-ring profile). If that split holds at naphthalene, the locality question becomes "does the
   π-ring part stay confined to rings" — a question about the graph of rings, not about distance.

## Ledger changes

S1: alive; next test = the same block table on the naphthalene tensor when it exists (does the flat carbon
profile stay ring-confined?). S2: **unlikely** (negative in mode space and real space on the stand-in); one
test left, on the R0 pilot's real Δ₂. S3: the ring-confined nonlocality is its first data-side motivation;
still literature first. X5 done.
