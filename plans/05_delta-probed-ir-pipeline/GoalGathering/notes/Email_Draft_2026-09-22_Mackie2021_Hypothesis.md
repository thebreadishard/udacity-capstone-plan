# Draft message to the supervisor — a hypothesis for the "cause not known" of Mackie et al. 2021 (22 September 2026, for the student to send)

*Context. The sentence is in Mackie, Candian, Lee & Tielens, Theor. Chem. Acc. 140, 124 (2021), DOI 10.1007/s00214-021-02807-z — the 11.2 µm
cascade paper. The supervisor is not a co-author of that paper; she is a co-author of the 2015 paper whose method (B971/TZ2P quartic force field
from Gaussian 09, analytic Hessians differentiated numerically along the normal modes) the 2021 statement refers to (Mackie, Candian, Huang,
Maltseva, Petrignani, Oomens, Buma, Lee & Tielens, JCP 143, 224314, 2015). The message says so. Evidence behind every number: the pre-registration
note `probes/results_vpt2/PREREGISTRATION_2026-09-21_FD_noise_demonstration.md`, the R0 reading `probes/results_m1/R0_DIAGONAL_READING_2026-09-22.md`,
pyVPT2 issue #57 / PR #58. Tone: a hypothesis with a cheap test, not a claim.*

---

Subject: a testable hypothesis for the "cause not known" in the 2021 cascade paper

Dear [name],

Thank you again for the papers. One sentence in Mackie, Candian, Lee & Tielens (Theor. Chem. Acc. 140, 124, 2021) has stayed with me — I know
you are not an author of that one, but it concerns the quartic-force-field method of the 2015 paper you co-authored. In the conclusions they write
that anharmonic computations of larger PAHs were largely unsuccessful because of numerical instabilities, with anharmonic corrections of several
hundreds of wavenumbers in out-of-plane bending modes, and that the cause is not known. Last week I ran into something that looks like a
smaller cousin of this on benzene, and I think it suggests a hypothesis and a cheap test.

**What I saw.** With pyVPT2 on 61 displaced psi4 Hessians of benzene (B3LYP/6-31G*), the VPT2 fundamentals were unusable: the ring-breathing
mode shifted by −217 cm⁻¹ where about −17 is expected, and exactly degenerate pairs split by tens of wavenumbers. The programme's own consistency
check reported nothing. The reason it saw nothing is structural: every semi-diagonal quartic constant φ_iijj can be obtained by two independent
finite-difference routes (displace j and read H_ii, or displace i and read H_jj), and the standard check compares φ_ij with φ_ji only *after* the
two routes have been averaged. When I kept the two routes apart, their disagreement was 22 cm⁻¹ in the median and 1,265 at worst — the
constants were noise with a signal inside. In my case the noise came from psi4's own finite-difference Hessians (a difference of a difference);
with analytic Hessians on the same 61 geometries the disagreement fell to 0.1 cm⁻¹ median and the breathing shift to −17, and benzene's three
test bands landed at 851, 1004 and 1324 against 847, 993 and 1309 measured. I pre-registered the two tests before running them, and both
came out as predicted.

**The hypothesis.** Your Hessians were analytic, so my exact mechanism is not yours. But three things specific to the out-of-plane bends of
large PAHs amplify whatever numerical error the differentiated Hessians do carry:

1. Those modes have the lowest frequencies in the molecule, and the VPT2 expressions divide by them — 1/ω_k in the diagonal terms and
   1/(ω_i + ω_j − ω_k), 1/(4ω_i² − ω_k²) in the couplings. A quartic constant that is wrong by a few wavenumbers becomes a shift of
   hundreds once divided by a frequency of a hundred.
2. The potential along an out-of-plane coordinate is strongly quartic. In my coupled-cluster deck on benzene the quartic-to-quadratic ratio
   is about five per cent for the C–H out-of-plane modes and below half a per cent in-plane. With a fixed displacement step, the finite-difference
   quartic constants of such modes depend on the step, and a step chosen for the stiff modes is far out on the flat, quartic modes of a large PAH.
3. Near-degeneracies multiply with size, and for symmetric tops (triphenylene) there is a further trap I fell into myself: inside an exactly
   degenerate pair any rotated basis is a valid normal-mode basis, and if the displacements and the analysis use different ones, the constants
   come out wrong by amounts that are identical for both partners — which looks like physics and is not.

None of these requires anything to be wrong with the electronic structure; they are all properties of the numerical differentiation and of the
denominators, and all three predict that the failure concentrates in the low-frequency out-of-plane family, which is what the paper reports.

**The test is cheap.** For one of the molecules that failed, the displaced Hessians presumably still exist. Assembling the force field twice,
keeping the two routes of every φ_iijj separate, gives a disagreement per constant at no extra cost; if the instability is numerical, the
disagreement will sit in the out-of-plane constants, and repeating the assembly at a second step size tells which of the two mechanisms it is
(finite-difference noise falls with the square of the step, quartic contamination grows with it). I have a small, tested open-source script that
does this from a directory of Hessians and prints both routes and the degenerate-partner differences, and I have proposed the same check to the
pyVPT2 maintainers (issue #57, pull request #58). I would be glad to run it on any set of Hessians you or Cameron Mackie could share, or to send
the script.

I should say plainly what this does not show: I have not tested it on your molecules or with Gaussian, and the two-route disagreement is a
diagnostic, not a proof — it can only say whether the constants are numerically trustworthy, not whether the physics beyond them is.

With best regards,
[student's name]

---

*For the student before sending: (1) check that Cameron Mackie's name is appropriate to mention or replace with "the authors"; (2) the numbers are
the T1/T2 results of 21 September and the R0 quartic ratios of 22 September; (3) attach nothing — offer the script; (4) send from the address the
supervisor has replied to.*
