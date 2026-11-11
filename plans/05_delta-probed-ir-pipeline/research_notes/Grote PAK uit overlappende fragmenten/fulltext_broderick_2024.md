# Broderick & Herbert 2024: full-text notes

D. R. Broderick, J. M. Herbert, "Delocalization error poisons the density-functional many-body expansion",
Chem. Sci. 15 (2024) 19893–19906, DOI 10.1039/d4sc05955g, CC-BY 4.0. Read in full on 11 Nov 2026 from the local PDF
(`Papers/Broderick_Herbert_2024_delocalisation_error_MBE_ChemSci.pdf`, 14 pages: article pp. 1–8, references pp. 8–14).
**The ESI is not in the PDF**: Table S1 (n-body statistics), Table S2 (BH&H-LYP vs B3LYP on GMTKN55) and Figs S1–S9 were not
seen. Page numbers below are PDF pages (journal page = 19892 + PDF page). Numbers marked "(fig.)" are read off a plot and
are approximate; all others are stated in the text.

## 1. What is shown

**Systems** (all non-covalent clusters, one molecule or ion per fragment; no covalent, conjugated or aromatic system):
- ten F⁻(H₂O)₁₅ clusters (main set; p. 2, Fig. 1); F⁻(H₂O)_N, N = 5–25, cut from an MD run of F⁻(H₂O)₁₂₈ (p. 3, Fig. 3;
  N up to 25 only in ESI Figs S5–S7);
- 11 structures each of F⁻(H₂O)₁₄, neutral (H₂O)₁₅ and Na⁺(H₂O)₁₄ (p. 4, Fig. 4).

**Property**: only the interaction energy ΔE_int of the ion (or of one central water) with the rest, eqn (3), p. 7. The
error of MBE(n) is measured against a counterpoise-corrected supersystem calculation **at the same level of theory**
(p. 2, §2; p. 7, §5). So every error in the paper is a fragment-assembly error of one method, not a method error.

**MBE order**: n = 2–6 (Figs 1, 5, 6, 7); n = 3–5 in Fig. 4; MBE(4) with screening in Fig. 8. Code FRAGME∩T + Q-Chem;
generalised MBE with inclusion–exclusion coefficients that "can handle overlapping fragments", eqns (4)–(7), p. 7–8.

**Basis sets**: aug-cc-pVXZ, X = D, T, Q (Fig. 1); 6-31G for the full-cluster-basis test (Fig. 5); aTZ in Fig. 4; aDZ in
Figs 6–7.

**What goes wrong** (numbers):
- PBE, F⁻(H₂O)₁₅: "wild oscillations that grow worse as n increases; the expansion appears to be divergent" (p. 2).
  Errors (fig., Fig. 1a–c) ≈ −50 (n=2), +50 (n=3), −80 (n=4), +100 to +190 (n=5), −150 to −270 kcal/mol (n=6), nearly the
  same for aDZ, aTZ, aQZ, so basis incompleteness is not the cause (p. 4, §3.1). HF at aQZ: five-body terms negligible,
  n ≥ 4 errors ≈ 0 (p. 2; Fig. 1f).
- Decomposition (PBE/aQZ, p. 2): fluoride-containing n-body terms sum to **−115.9 kcal/mol (n=4) and +193.0 kcal/mol
  (n=5)**; water-only terms −4.0 and +1.8; HF water-only terms −0.6 and +0.1 kcal/mol. Individual |ΔE_IJ…| still shrink
  with n (Fig. 2), but PBE four- and five-body terms carry systematic negative and positive biases (p. 3).
- Convergence criterion, eqn (2), p. 3: for alternating signs, MBE(n) converges only if
  N_F(n)·|⟨ΔE_n⟩| / (N_F(n−1)·|⟨ΔE_{n−1}⟩|) < 2. The number of subsystems N_F(n) grows combinatorially, so a small
  per-term bias still diverges.
- Size dependence, PBE/aDZ, Fig. 3 (p. 3): error per monomer falls with n only up to F⁻(H₂O)₈; for larger N, MBE(4) is
  worse than MBE(3), and by F⁻(H₂O)₁₆ MBE(2) has the smallest error. (fig.) at N = 15: MBE(2) ≈ 2.4, MBE(3) ≈ 2.35,
  MBE(4) ≈ 4.1, MBE(5) > 4.5 kcal/mol/monomer; at N = 5, MBE(5) ≈ 0.2. HF per-monomer errors are size-independent (p. 3).
  Abstract: the problem appears for N ≳ 15 (p. 1).
- Neutral (H₂O)₁₅: oscillations "quite small … albeit still largest with the PBE functional", reduced but not removed by
  hybrids (p. 4). (fig., Fig. 4b) PBE MBE(3) up to +1.8, MBE(4) ≈ −1.3 kcal/mol; PBE0 MBE(3) ≤ ≈ +0.9; HF within ≈ −1 to 0.
- Na⁺(H₂O)₁₄: "MBE(n) diverges using any of the aforementioned functionals except for HF" (p. 4): PBE, PBE0 (α = 0.25)
  and the range-separated LRC-ωPBE (α = 0 short range → 1 long range). (fig., Fig. 4c) MBE(5) spread ≈ −12 to +18 (PBE),
  −9 to +14 (PBE0), −9 to +15 kcal/mol (LRC-ωPBE); HF ≈ 0. "Cationic systems are clearly not immune" (p. 4).

**Functionals** (p. 4–6, Figs 4, 6, 7, S8):
- GGA (PBE, BLYP): divergent. BLYP/aDZ (fig., Fig. 6a) n=5 ≈ +150, n=6 ≈ −200 to −300 kcal/mol.
- **B3LYP (α = 0.2): "divergent behavior … persists"** (p. 5). (fig., Fig. 6b, aDZ) n=2 ≈ −25 to −50, n=3 ≈ +5 to +20,
  n=4 ≈ −15 to −20, n=5 ≈ +5 to +25, n=6 ≈ −25 to +10 kcal/mol: no convergence through n = 6.
- PBE0 (α = 0.25), LRC-ωPBE: much smaller oscillations than PBE for F⁻(H₂O)₁₄ (fig., Fig. 4a: within ≈ ±10 kcal/mol at
  n = 3–5, against +55 to +90 for PBE at n=5) but not converged; both diverge for Na⁺(H₂O)₁₄ (above). The range-separated
  hybrid therefore does not fix it.
- SCAN, SCAN0 (α = 0.25), ωB97X-V (α = 0.167 short range): divergent (Fig. 7a–b, S8b; p. 5–6). (fig.) SCAN and SCAN0 n=6
  spreads reach ≈ ±150–200 kcal/mol.
- BH&H-LYP (α = 0.5): "results appear to converge" (p. 5); (fig., Fig. 6c) n ≥ 4 within ≈ ±10–15 kcal/mol, n=6 still
  scattered ≈ −15 to +8. HF-LYP (α = 1): "oscillations disappear completely" (p. 5). Conclusion: α ≳ 50% needed (p. 1, p. 7).
- HF: converges in every test (Figs 1, 4, 5).

**Mechanism** (p. 1–2, §3.1 p. 4–5): self-interaction (= delocalisation) error gives a driving force to delocalise charge
even in closed-shell systems; "the mere presence of a distant (therefore, non-interacting) subsystem has a stabilizing
effect on the total energy" (p. 5). In MBE(n) near and distant subsystems are added and removed as n changes, so
higher-order terms are over-stabilised. SIE and BSSE are coupled: a subsystem basis confines density to the monomers
present (aQZ functions reach only ≈ 3 Å beyond the nuclei, p. 5). Full-cluster basis (CP) dampens but does not remove it:
PBE/6-31G with full-cluster basis still ≈ 20 kcal/mol errors at n = 3 and 5, opposite sign at n = 4 and 6, whereas
CP-corrected HF/6-31G converges by n = 4 (p. 4–5, Fig. 5); the subsystem basis alone gives a −50 kcal/mol shift for both
HF and PBE (p. 4). Charged fragments dominate the error (Fig. 2, p. 2). The paper links it to "charge-sloshing" oscillations
in MBE(n) of proteins with ionic side chains (ref. 105, p. 5).

## 2. Energies only?

**Energies only.** Every result is an interaction energy ΔE_int (eqn 3). No gradient, Hessian, frequency or geometry is
computed anywhere in the article. "Gradient" appears only in "generalized gradient approximation" and in the title of
ref. 164 (MP2/CCSD gradients by Khire et al.). Nothing in the paper measures how the oscillation carries into second
derivatives; any statement about Hessians is our extrapolation.

## 3. Difference schemes, π systems, charged fragments, capping

- **No QM:QM difference (high − low on fragments) is tested.** The only two-level idea is in the outlook (p. 7): the
  "safest approach" is MBE(n) on post-HF correlation atop an SIE-free HF calculation; MP2 has been done with "a small-basis
  HF calculation for the entire system … to recover long-range polarization, with short-range MBE(3) calculations to
  describe electron correlation" (ref. 145), to be extended to coupled cluster. That is the same architecture as our ΔH
  scheme (full low level + fragment correction), but **with HF, not a DFT functional, as the full-system level**.
- **Inherit or cancel? (our inference, not in the paper.)** The paper's error is exactly the fragment-assembly error of the
  low-level method. In ΔH = Σᵢ cᵢ (H_high,i − H_B3LYP,i) added to a whole-molecule H_B3LYP, the residual is
  [H_high(full) − Σcᵢ H_high,i] − [H_B3LYP(full) − Σcᵢ H_B3LYP,i]. The B3LYP assembly error enters with weight one and is
  cancelled only to the extent that the high level has the same non-additivity. A wavefunction high level (MP2, CCSD(T))
  has no SIE, and HF-based MBE converges in every test here (Figs 1d–f, 4, 5c), so the SIE-driven part would be inherited,
  not cancelled. The paper shows B3LYP itself does not converge for F⁻(H₂O)₁₅ (Fig. 6b), so B3LYP is no safe low level
  in the regime where the problem appears. The whole-molecule B3LYP Hessian removes the problem only for the part of
  B3LYP's delocalisation the fragments never see; it cannot repair the B3LYP fragment terms we subtract.
- **Why the paper's numbers do not transfer directly to us** (our reading): (i) its divergence is a high-order,
  combinatorial effect (eqn 2; N ≳ 15 fragments, n ≥ 4), while an overlapping-piece scheme for a 36–60-atom PAH has tens
  of pieces combined by inclusion–exclusion, not thousands of n-body subsystems; (ii) neutral closed-shell clusters show
  only small oscillations (Fig. 4b), and a neutral PAH is closed-shell; (iii) the fragments are whole molecules with no
  bonds cut. Against that: (iv) a capped PAH piece cuts a delocalised π system, where B3LYP's delocalisation error lives
  inside the fragment, a regime the paper never tests; (v) PAH radical cations have a delocalised hole, the case where
  charged-fragment terms dominated (Fig. 2) and where every functional short of HF diverged for a cation (Fig. 4c).
- **π-conjugated or aromatic fragments: none.** The only π mention is ref. 135 (Rana, Beran & Herbert 2023, "Correcting
  π-delocalisation errors in conformational energies using density-corrected DFT"), cited among DC-DFT papers on p. 6
  without discussion.
- **Charged fragments**: anion F⁻ (severe), cation Na⁺ (diverges for PBE, PBE0, LRC-ωPBE; p. 4). Both closed-shell; no
  radical or open-shell fragment is computed (radical cations appear only in the SIE background refs 58–71, p. 1).
- **Capping / link atoms: not addressed** (no covalent bond is cut). Overlapping fragments are supported by the formalism
  (eqns 4–7) and mentioned as used elsewhere for clusters (p. 7), but not tested here.

## 4. Remedies tested or proposed

| Remedy | Result | Where |
|---|---|---|
| Larger basis (aDZ → aQZ) | no change in oscillations | p. 4, Fig. 1 |
| Full-cluster basis (CP) | dampens; PBE still ≈ 20 kcal/mol at n = 3, 5 | p. 4–5, Fig. 5 |
| Hybrid, α = 0.2–0.25 (B3LYP, PBE0, SCAN0) | reduces, does not remove | p. 5, Figs 4, 6b, 7b |
| Range-separated hybrid (LRC-ωPBE, ωB97X-V) | does not remove; diverges for Na⁺ | Fig. 4, Fig. S8b, p. 6 |
| α ≥ 0.5 (BH&H-LYP), HF-LYP | appears to converge / no oscillation | p. 5, Fig. 6c–d |
| DC-DFT (SCAN@HF) | fails for SCAN; DC-PBE reduces, does not remove | p. 6, Fig. 7c, Fig. S5 |
| PCM ε = 4 boundary | fails here; worked for proteins with amino-acid fragments (ref. 105) | p. 6, Fig. 7d |
| Energy-based screening (GFN2-xTB, τ₃, M = 1) | works: PBE/aQZ MBE(4) error (fig.) ≈ 80–90 kcal/mol at τ₃ = 0 → ≈ 5–15 at τ₃ ≈ 0.1–0.2 kcal/mol; minimum near ≈ 250 subsystems, then grows with more (to ≈ 70–85 at ≈ 1100); HF: acceptable at τ₃ ≈ 0.1, plateau from ≈ 500 subsystems | p. 6–7, Fig. 8 |
| Larger fragments | "may help", shown before for proteins | p. 7 |
| HF + post-HF MBE (full HF, fragment correlation) | "the safest approach" | p. 7 |

BH&H-LYP on GMTKN55 is "only marginally worse" than B3LYP (Table S2, not in PDF; p. 5). The "Goldilocks point" of screening
(p. 7) is not codified: "Whether this balance can be codified in an unambiguous way remains an important issue" (p. 7).

## 5. Check of our report (`reports/Grote PAK uit overlappende fragmenten.md`)

Grep hits: line 60 (text) and line 130 (source table). Line 25's "a few cm⁻¹ per Herbert" refers to Herbert 2019, not this
paper. The sixth pitfall (cations, line 62) does not cite this paper.

**Line 60** reads: *Delocalisation error also "poisons" density-functional many-body expansions ([Broderick & Herbert 2024]).*

- Quote: correct; it is the paper's title (p. 1).
- **CORRECTION (use):** the sentence sits under the "2D conjugation" pitfall and so reads as evidence about fragmenting π
  systems. The paper has no π, aromatic, covalent or capped system: it studies non-covalent water clusters with one
  molecule or ion per fragment, interaction energies only, MBE up to n = 6. Its severe effect is for ions (F⁻, Na⁺); neutral
  clusters show only small oscillations (Fig. 4b). It says nothing about Hessians or frequencies.
- **CORRECTION (omission that matters for us):** the report does not say that B3LYP itself is among the failing
  functionals (Fig. 6b, p. 5), which bears on our B3LYP fragment terms, nor that the paper's "safest" scheme is a full-system
  low level plus fragment correlation correction, i.e. our architecture with HF as the low level (p. 7).
- Suggested replacement text: *In non-covalent water clusters, delocalisation error makes density-functional many-body
  expansions of ion–water interaction energies oscillate and diverge from four-body terms on (F⁻(H₂O)₁₅, PBE: ±100–200
  kcal/mol at n = 5–6; B3LYP still ±20–50 kcal/mol), and for Na⁺(H₂O)₁₄ every functional tried except HF diverges; neutral
  clusters oscillate only slightly ([Broderick & Herbert 2024]). Only energies of non-covalent fragments were tested. For us it
  is a warning about the B3LYP terms we subtract on pieces, strongest for charged pieces, not a measurement on π systems.*
  A second clause could go under the sixth pitfall (cations): every functional short of HF diverged for a hydrated cation.
- **Line 130 (sources table):** "not in notes" is now out of date; full reference Chem. Sci. 15, 19893–19906 (2024),
  DOI 10.1039/d4sc05955g; notes in this file.
