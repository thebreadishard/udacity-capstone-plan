# Plan 06 — Reading note X0 (2026-09-12): what the complexity results exclude, and what locality leaves open

*Three papers read from their open arXiv versions (files in `Papers/plan06/`, git-ignored): Prodan &
Kohn 2005 in full (6 pp.); Schuch & Verstraete 2009 in full including the supplementary material
(8 pp.); Kempe, Kitaev & Regev 2006 sections 1–4 (definitions, the projection lemma, Kitaev's
construction) and the conclusion — the two proofs of the main theorem (sections 5–7) were not read
line by line. Published versions: Nature Physics 5, 732 (2009); SIAM J. Comput. 35, 1070 (2006); PNAS
102, 11635 (2005). This note records what each paper states, in its own terms, and then what it means
for plan 06's question. Nothing here is a plan-06 claim.*

## 1. Kempe, Kitaev & Regev (2006) — the local Hamiltonian problem is QMA-complete down to k = 2

**What the problem is (their Definition 3).** Given a Hamiltonian on n qubits that is a sum of
poly(n) terms, each acting on at most k qubits with polynomially bounded norm and polynomially many
bits, and two thresholds a < b at least an inverse polynomial apart, decide whether the lowest
eigenvalue is at most a or larger than b (a promise problem). **Theorem 1:** 2-LOCAL HAMILTONIAN is
QMA-complete; 1-local is in P; k ≥ 3 was known. QMA is the quantum analogue of NP: a positive
instance has a quantum witness a polynomial-time quantum verifier accepts. The main tool is the
projection lemma (their Lemma 1): adding a large penalty J on the complement of a subspace S moves
the lowest eigenvalue of H₁ + H₂ to within ‖H₁‖²/(J − 2‖H₁‖) of the lowest eigenvalue of H₁
restricted to S, which lets a non-local effective Hamiltonian be approximated by a local one. Their
introduction records, as "recent work", that Oliveira & Terhal extended the result to nearest-neighbour
qubits on a 2-D grid; their conclusion leaves open other uses of the perturbation technique, the
relation of QCMA to QMA, and whether the 2-local reduction can be made with every term near its own
ground state.

**What it says for plan 06.** The hardness is about *deciding a ground energy to inverse-polynomial
accuracy over all instances of a family*; it is a statement about the worst case in the family. It
says nothing about any single molecule. It rules out one thing exactly: an algorithm that is
polynomial in size and exact to inverse-polynomial accuracy on *every* 2-local Hamiltonian, unless
QMA = P.

## 2. Schuch & Verstraete (2009) — the electronic problem and the universal functional

**What they prove.** (i) The 2-D Hubbard model with local magnetic fields is QMA-complete, by a chain
of second-order perturbation "gadgets" from a known QMA-complete Pauli Hamiltonian through the
Heisenberg model to the half-filled Hubbard model (U/t growing polynomially; a 16-coupling chain per
Pauli term). (ii) That Hubbard model arises from the electronic Schrödinger Hamiltonian (their eq. 1:
kinetic + Coulomb + external electrostatic and magnetic potential) for an explicitly constructed
Kronig–Penney-type external potential, to 1/poly(N) precision, with N both the number of sites and
the number of electrons (supplementary section 5). (iii) Given an oracle for the Hohenberg–Kohn
universal functional F[ρ], the Hubbard ground energy is computable in polynomial time, because the
density lives in a convex set of 4N parameters and F is convex; hence **computing the universal
functional to polynomial accuracy is QMA-hard under Turing reductions**. The variant proved is
spin-density functional theory (magnetic field coupled to spin, not to orbit). (iv) Corollaries in the
text: the Levy pure-state functional is not convex but efficient computability would still collapse
QMA to NP; the two-electron-density (2-RDM) route is hard because N-representability is QMA-complete
(Liu, Christandl & Verstraete 2007, cited); and, in the appendix, **Hartree–Fock itself is
NP-complete** (reduction from Ising spin glasses on an L × L × 2 lattice). They add, in their own
words, that "this does not mean that DFT is not applicable in practice: much lower (e.g. constant)
accuracies will typically suffice".

**What it says for plan 06.** The QMA-hardness is transported into the *actual* electronic
Hamiltonian, not a toy — but through a designed external potential (delta-function lattice, tuned
magnetic fields) that encodes a computation. No molecule's nuclear potential is of that kind. What
is excluded: a universal, polynomial, inverse-polynomially accurate method for *all* external
potentials. What is not excluded, and what they themselves point at: methods that are exact or
certified for a *restricted class* of potentials or to *constant* accuracy. Plan 05's tolerance is a
constant accuracy (sub-wavenumber curvature, micro-hartree energies at a fixed size), not
inverse-polynomial in N. Two more consequences worth keeping: (a) since Hartree–Fock is already
NP-complete in the worst case, and Hartree–Fock is routine on real molecules, worst-case hardness is
clearly not what governs the cost on plan 05's class; (b) the 2-RDM route is not a free lunch —
its hardness sits in N-representability.

## 3. Prodan & Kohn (2005) — nearsightedness of electronic matter, quantified

**What they show.** For non-interacting fermions at fixed chemical potential, the change of a local
property (the density at r₀) caused by any perturbing potential of any strength outside a sphere of
radius R decays with R: as a power law for ordered gapless systems, exponentially for ordered gapped
systems, and exponentially for disordered systems whether gapped or not. The 1-D insulator result
(their eq. 5): Δn(x) ∝ e^{−2qx}, with q the imaginary part of the branch point connecting the highest
occupied and lowest unoccupied band — the same q that governs the exponential decay of the Wannier
function and of the density matrix; for small gap G, q = ½√(m*G). The nearsightedness range R(Δn)
grows only logarithmically in the accuracy for insulators (eq. 8: R → (1/2q) ln(ñ/Δn)) and as a
power of 1/Δn for metals (eq. 10, 18). Higher dimensions: analogous, with the decay set by the
slowest q₀ over the Brillouin zone (eq. 16, 19, 20). Interacting electrons: in the random-phase
approximation the range decreases in metals and increases in insulators (gap reduction); charged
perturbations are screened in metals but "classically farsighted" in insulators. Application: the
divide-and-conquer buffer thickness b is set by R, giving total CPU time linear in the number of
atoms with a factor (ln ñ/2Δn)^{(ν−1)d} for gapped systems (eq. 21).

**What it says for plan 06.** This is the theorem behind local correlation methods and behind plan
05's frozen spaces: for a gapped system, what happens beyond a distance R affects a local quantity by
an amount that falls exponentially, with a rate set by the gap. It is proved for non-interacting
fermions and argued for interacting ones; it is about local *density* response, not directly about
pair correlation energies — the step from "density is nearsighted" to "correlation energy
contributions are nearsighted" is the working assumption of every local-CC method and is checked
numerically, not proved, in that literature. Two consequences: (a) the decay constant is a property of
the *class* (gap, effective mass), so measuring it once on small aromatics (experiment X3) says
something about the whole ladder; (b) aromatic π-systems have small gaps compared with saturated
molecules, so their q is small and their nearsightedness range large — locality pays *later* in size
for PAHs than for alkanes. That is consistent with what plan 05 measured (see X3a below).

## 4. Synthesis for plan 06

1. **Level E1 "in general" is closed.** A polynomial-time method exact to inverse-polynomial accuracy
   for every external potential would put QMA in P (Schuch & Verstraete, from KKR). The plan must
   never claim it.
2. **Level E1/E2 "for this class" is open, and the class is what has to be characterised.** The
   relevant parameters are the gap and the resulting decay constant (Prodan & Kohn), the accuracy
   (constant, not inverse-polynomial), and the geometry (planar, conjugated). A structure theorem or a
   measured decay for that class is the only kind of result plan 06 can honestly aim at.
3. **Hartree–Fock's NP-completeness is a useful calibration.** A worst-case-hard method is routine on
   real molecules; worst-case complexity is not the quantity that prices plan 05's anchor. The price is
   set by the constants of the class — which is measurable.
4. **What a proposer may propose.** Reformulations that are exact for a class and come with a bound in
   the class parameters; not "faster exact solvers of the Schrödinger equation".

## 5. X3a — what LNO actually kept at naphthalene (from the existing timing log; no new compute)

Parsed from `probes/results_timing/naphthalene_ccpvtz_tight.log` (2026-09-11, 24 fragments, tight
thresholds, cc-pVTZ): per fragment the local active space kept **22–24 of 34 occupied orbitals**
(34 includes the 10 frozen 1s cores; of the 24 *active* occupied orbitals, 92–100 % were kept) and
**44–84 % of the 378 virtuals** (mean 56 %). Per-fragment CCSD correlation energies range from
−0.056 to −0.087 E_h and the (T) parts from −0.0022 to −0.0073 E_h. **Reading:** at naphthalene,
tight LNO thresholds truncate the occupied space hardly at all — every fragment still sees nearly the
whole molecule — and truncate the virtual space by about half. The 11.5-hour energy is therefore
priced by a molecule whose locality has not yet started to pay in the occupied space, exactly as the
small π-gap and Prodan–Kohn's logarithmic range predict. The *rate* at which it would start to pay
is experiment X3b (MP2 pair energies against LMO distance, `experiments/x3_pair_decay.py`), to run
after the current anchor job ends.
