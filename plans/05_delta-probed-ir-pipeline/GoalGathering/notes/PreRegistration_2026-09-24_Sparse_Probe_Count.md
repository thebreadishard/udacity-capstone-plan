# Pre-registration — sparse-probe count under the locality prior (24 September 2026, morning; lever 1 of the odds re-estimate)

**Why now.** E8 read the coupled-cluster correction ΔH of benzene as a force-constant correction ΔF supported on a local pairwise pattern in
primitive internal coordinates: 92 % on pattern (c), 98 % on pattern (d) = (c) + pairs two bonds apart. E8 also priced the label: one canonical
CCSD(T) gradient of naphthalene takes hours on a CPX62. Plan 06's X22 (19 September) counted how many gradients a *symmetry* prior saves for the
finite-difference Hessian: linear in the mode count, 2M + 1 without symmetry, 0.35–0.45 M at D2h. The locality prior is a different prior. The
question here is what it saves, by count, on the corpus — before any of it is claimed in the cost table of the 28th. The user asked for it
("Als je daaraan kunt beginnen zonder een run te schaden, graag"); no run is touched: seconds of numpy on geometries already on disk.

**Question.** If ΔF lives on pattern (d) with m_d free entries, each probe (one displacement direction, two gradients) yields 3N linear equations,
so p_d = ⌈m_d / 3N⌉ probes determine ΔF by count. How does p_d compare with the plain finite-difference count 3N over the 245 corpus molecules
(N = 12 … 30 atoms), and what do the fits say for N = 50, 100, 200?

**Method.** `probes/e8_sparse_probe_count.py`: primitives from the bond graph (bonds, angles, dihedrals — an over-count of any non-redundant set,
so p is an upper bound); m_c, m_d as E8 defines the patterns; p_c, p_d; the saving 3N / p_d; linear fits of m_d and of the saving against N;
extrapolations by the fits, labelled as count-only. Conditioning, noise and the choice of directions are *not* addressed here — that is plan 06's
recovery theory and a later test with real gradients.

**Predictions (fixed before the run).**
1. m_d grows linearly with N (≈ 100 N by benzene's 1,365 / 12), while the number of independent ΔH entries grows as 9N²/2; so the saving grows
   linearly with N: ≈ 0.1 N.
2. Break-even (saving 1) near N ≈ 10–15: **for the corpus molecules the locality prior alone saves little or nothing** (≤ 3× at N = 30).
3. At N = 100 the count-only saving is ≈ 8–12×; at N = 200 ≈ 15–25×. That is where the lever matters — the large PAHs of the mandate — and it
   multiplies with the symmetry saving where a molecule has symmetry.

**What it decides.** Nothing about noise; only whether the lever is worth engineering. If prediction 2 holds, the cost table of the 28th says:
symmetry for the anchors, locality for the large targets, LNO-CC energies for the labels in between — and the next test is a recovery of benzene's
ΔH_CC from a pattern-chosen subset of its 72 gradients *with* a sparsity prior (plan 06's formulation), which is not a count but a reconstruction.
If the saving is much larger than predicted, the label plan changes before the 28th; if much smaller, the lever is dropped from the table.

## Outcome (06:5x; `probes/results_m1/e8_benzene_ccpvdz/sparse_probe_count_2026-09-24.{md,json}`, 244 molecules, seconds of numpy)

| size class (N) | molecules | with dihedrals (geomeTRIC-like primitives): p_d median, saving | bonds + angles only: p_d median, saving |
|---|---|---|---|
| 10–15 | 5 | 40, **0.9** | 11, 3.3 |
| 16–20 | 26 | 54, 0.9 | 14, 3.7 |
| 21–25 | 129 | 71, 1.0 | 16, 4.3 |
| 26–30 | 84 | 76, 1.1 | 17, 4.9 |

Fits: with dihedrals m_d ≈ 352 N − 3,169 and saving ≈ 0.011 N + 0.72 (N = 100 → 1.9, N = 200 → 3.0); bonds + angles saving ≈ 0.112 N + 1.76
(N = 50 → 7.4, N = 100 → 13, N = 200 → 24). Benzene: 38 probes with dihedrals (3N = 36 — no saving), 11 without; naphthalene 61 / 15; pyrene 90 / 19.

**Against the predictions.** (1) linear growth of the saving: yes, but with a slope ten times smaller than predicted when the primitive set includes
dihedrals, and as predicted (0.11 N) without them. (2) little or nothing on the corpus: **true with dihedrals** (saving ≈ 1), **false without** (3–5×).
(3) 8–12× at N = 100: between the two counts (1.9 and 13). So the pre-registered question has a conditional answer: **the locality prior saves
probes only in a compact local basis.** The redundant primitive set that E7/E8 used for the *representation* (fine there: the masks and the
learning do not care about redundancy) is the wrong object for *probe economy*: pattern (d) over 5,000 dihedral-heavy primitives has more free
entries than the Hessian at every corpus size. In a bonds + angles set the count says 3–5× on the corpus and an order of magnitude at N ≈ 100 —
before conditioning, noise and the choice of directions, which the count does not see.

**What it decides.** The lever stays in the cost table of the 28th as *conditional*: "an order of magnitude at N ≈ 100 if the local basis is
compact and the recovery is well-conditioned — count only, reconstruction not yet tested." Next test (no compute): reconstruct benzene's ΔH_CC
from a subset of its 72 gradients with ΔF restricted to pattern (d) in a bonds + angles basis (11 probes by count, 36 available) — plan 06's
recovery formulation on real data; the same test tells whether out-of-plane physics survives without dihedrals (benzene's out-of-plane modes are
the sharp check). Not today's lane; it goes to the desk list after the naphthalene read-outs.
