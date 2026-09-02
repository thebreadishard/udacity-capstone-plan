# Professor review — 2026-09-01, Round 5, Pass B (adversarial domain)

**Scope.** TDDFT / Maxwell–TDDFT / ML-propagator physics, per
[Review_Brief_2026-09-01_Round5_PassB.md](Review_Brief_2026-09-01_Round5_PassB.md). Internal
document consistency is Pass A's job and is not re-litigated here. Numbering is **Round 5, Pass B,
issues 1–12**, independent of Pass A's 1–15. Issue 12 was added after the rest, from the author's
own objection; it is flagged as such where it appears.

**Primed on.** [Professor_Review_2026-09-01_Round5_PassA.md](Professor_Review_2026-09-01_Round5_PassA.md),
whose findings 2–4 are taken as given: the state is **eleven** channels; the P4 baseline is now
non-periodic so P0 on it can fail; the baseline Maxwell is now leapfrogged with 119 CFL sub-steps.
Pass A finding 4 closed with the sentence *"The teacher-side question is left for Pass B on purpose."*
Issue 2 below is that question, answered.

**Method note.** Six claims are checked by arithmetic executed against the repository's own
`grid_spec.py` and `linear_stencil.py`, and by a 1-D grid-TDSE null model. Commands and outputs are
quoted. Four claims are checked against Octopus's **own current documentation** (fetched
2026-09-01, pages stamped "Last modified on September 1, 2026 at 17:01 UTC. Based on Octopus branch
'main'"). Two are marked **RECALLED** and must not be cited until fetched.

---

Verdict: **No green light for the scope as frozen.** The three-way freeze
\((h=0.20\,a_0,\ \Delta t=0.05\ \text{au},\ 3{\times}3{\times}3\ \text{kernel})\) plus a
**Maxwell–TDDFT teacher** is not merely expensive — it is arithmetically inconsistent, and the
inconsistency is the *same number* Pass A found in the baseline (\(c\Delta t/h = 34.26\)), which
binds the teacher and the learner as hard as it bound the stencil. Separately, and independently
fatal to the evaluation contract: **every promised gate on H₂ is passed by a network that outputs
its input** (issue 3, measured).

**Conditional green light** for a reduced scope, stated so it is not a mystery: **matter-only
RT-TDDFT** (drop \(\mathbf{E},\mathbf{B}\) from the promised state), a metric scored on the
*update* rather than on the state, and a pre-registered do-nothing null alongside the linear
stencil. Under that scope the frozen \(\Delta t\) and \(h\) become ordinary, a \(3\times3\times3\)
stencil becomes structurally capable, the 168 h cap becomes arguable, and the scientific question
survives intact.

**Was the pivot to plan 03 a mistake?** No. The pivot is sound and I would not reopen plan 01's IR
product or plan 02's pyrene promise. What was a mistake is the **Maxwell teacher**, adopted in the
2026-09-01 contradiction pass as the left-hand column of a coin-flip ("Teacher Maxwell–TDDFT" vs
"Poisson reconstruction") without any arithmetic on what \(c\) does to a grid frozen for electrons.
The measurement that settles it is in issue 5 and costs a web page and one install attempt, not a
compute campaign.

---

## Blocking findings

### 1. A \(3\times3\times3\) stencil cannot carry a Maxwell step at the frozen \((h,\Delta t)\). This is CFL, not training.

**Where:** [Distilled_Project_Plan_and_Quality_Checks.md](Distilled_Project_Plan_and_Quality_Checks.md)
§5.2 (kernel 3, \(k=1\), one forward pass = one teacher step);
[Frozen_Ladder_and_Tolerances.md](Frozen_Ladder_and_Tolerances.md) "Time and grid".

**What:** the brief's attack 1 asks whether a local stencil can compress the *nonlocal Hartree*
operator. That is the wrong worry, and answering it would have missed a harder one. The binding
constraint is the **domain of dependence** of the \(\mathbf{E},\mathbf{B}\) channels. In one teacher
step light travels \(c\,\Delta t = 6.85\,a_0\) — **34.26 cells** of the frozen grid. A
\(3\times3\times3\) kernel at \(k=1\) reaches **one** cell. An explicit scheme whose numerical
domain of dependence does not contain the physical one cannot converge to the physical solution,
however it is trained; this is Courant–Friedrichs–Lewy, and it is a statement about the *operator
family*, not about optimisation.

**Evidence:**

```
> python passb_checks2.py      (reads grid_spec.py and linear_stencil.py directly)
== 4. domain of dependence per ONE teacher step ==
physical (light) domain of dependence  6.85 a0 = 34.26 cells
learner kernel 3x3x3, k=1: reach 1 cell(s) = 0.20 a0; short by 34.3x
learner kernel 5x5x5, k=1: reach 2 cell(s) = 0.40 a0; short by 17.1x
kernel needed to contain the light cone: 71^3 (half-width 35 cells)
max signal speed a 3x3x3 k=1 stencil can carry: 4.00 au = c/34.3
```

The Module 05 controlled comparison is \(3\times3\times3\) vs \(5\times5\times5\). Both are inside
the light cone by a factor of 34 and 17. The comparison is therefore between two operators that are
provably wrong on the same channels, in the same direction.

Note the number: **34.26** is Pass A finding 4's Courant ratio. Pass A read it as a *stability*
property of the baseline and repaired the baseline by sub-cycling. The learner cannot sub-cycle —
one conv is one teacher step by §5.2 — so for the learner the same number reappears as a
*representability* bound, which no repair inside the frozen constants can touch.

**Why it matters:** this is the structural P1-passes/P2-fails mechanism the brief anticipated, but
worse: because of issue 4, the channels that are structurally impossible are exactly the channels no
gate ever scores, so the failure will not appear as a failed gate. It will appear as a passed thesis.

**What would close it — as science:** one of, chosen and written *before* Q0 is hashed:
(a) **drop \(\mathbf{E},\mathbf{B}\) from the promised state** and make the thesis matter-only (this
is my recommendation, and it is not the §4 "drop-\(B\)" clause — it is a scope change to the Goal
file); (b) keep Maxwell but declare a learner receptive field \(\ge 35\) cells, which means an FNO
or a deep stack, i.e. abandoning "one tiny local conv" as the thesis object; (c) keep the kernel and
reduce \(\Delta t\) below \(h/c = 1.46\times10^{-3}\) au, which makes the 200-step P2 horizon
\(0.29\) au \(= 0.007\) fs and makes P2 meaningless. There is no fourth branch.

---

### 2. \(\Delta t = 0.05\) au at \(h = 0.20\,a_0\) is not a legal Maxwell–TDDFT setting in the named teacher

**Where:** [Compute_Budget_2026-09-01.md](Compute_Budget_2026-09-01.md) §3 ("Teacher \(\Delta t\) |
0.05 au", "Outer spacing | 0.20 \(a_0\)", "H₂ / H₂O physics | Real-time TDDFT + Maxwell–TDDFT
fields"); [Frozen_Ladder_and_Tolerances.md](Frozen_Ladder_and_Tolerances.md) "Time and grid".

**What:** Octopus states its own Maxwell stability criterion in the Maxwell input-file tutorial:

> "`TDTimeStep` should be equal or smaller than the Courant criterion, which is here
> `S_Courant = 1 / (sqrt(c^2/dx_mx^2 + c^2/dx_mx^2 + c^2/dx_mx^2))`"

and, for the leapfrog propagator,
\(\Delta t \le \frac{1}{c\,\max|\eta|}\left(\sum_j \Delta x_j^{-2}\right)^{-1/2}\) with
\(\max|\eta| = 1.7306\) for the **default 8th-order** finite-difference curl stencil. Evaluated at
the frozen spacing:

**Evidence:**

```
> python passb_checks.py
== 1. teacher-side Maxwell CFL (Octopus's own criterion) ==
dt_courant_ideal_au      8.426257e-04
dt_courant_leapfrog8_au  4.868980e-04
frozen_dt_over_ideal     59.34
frozen_dt_over_leapfrog8 102.69
maxwell_substeps_per_teacher_step 103
maxwell_steps_over_P2_horizon     20539
```

Source verified 2026-09-01:
`https://www.octopus-code.org/documentation/main/tutorial/maxwell/maxwellinputfile/`.

So the freeze names a teacher time step **59× to 103× past the teacher's own stability limit** on
the frozen grid. Only three things can be true, and the plan must say which:

1. The Maxwell subsystem runs on a **coarser grid** than the matter subsystem. This is what the
   plan's own bibliography item 2 describes — Bonafé et al., arXiv:2409.08959v2, verified
   2026-09-01: *"The implementation in the open-source Octopus code is designed for
   massively-parallel multiscale simulations considering **different grid spacings for the Maxwell
   and matter subsystems**."* Then \(\mathbf{E},\mathbf{B}\) **are not native quantities on the
   frozen \(0.20\,a_0\) grid**, and five of the eleven hashed channels are an interpolation the Q0
   digest does not describe.
2. The Maxwell subsystem is sub-cycled ~103× per matter step. Then one 200-step P2 window is
   **20,539** Maxwell propagations of six field components on \(67^3\) — see issue 10 for what that
   does to the 168 h cap — and the learner is being asked to compress 103 sub-steps into one
   \(3\times3\times3\) conv (issue 1, ×103 instead of ×34).
3. \(\Delta t\) drops to \(\sim5\times10^{-4}\) au. Then \(T=200\) steps is \(0.1\) au \(=0.0024\)
   fs and P2 measures nothing.

**Why it matters:** \(\Delta t\) and \(h\) are **frozen constants hashed into Q0**, and Q0 is the
plan's earliest irreversible act (Module 05, before any training window is cut). Hashing a
grid/\(\Delta t\) pair that the named teacher cannot emit an 11-channel state on means the least
deviable object in the plan is wrong at the moment it is frozen, and every repair afterwards is a
§4 deviation on the definition of the state — the exact failure Pass A finding 2 escaped by one day.

**What would close it — in spec:** a dated pre-Q0 note that names which of the three branches is
taken, and if branch 1, states the Maxwell spacing, the interpolation operator onto the matter grid,
and hashes both into Q0. **As science:** one Octopus run that prints its accepted `TDTimeStep` for
each subsystem at the frozen spacing, before Q0.

---

### 3. Every promised H₂ gate is passed by a network that outputs its input

**Where:** [Compute_Budget_2026-09-01.md](Compute_Budget_2026-09-01.md) §4;
[Distilled_Project_Plan_and_Quality_Checks.md](Distilled_Project_Plan_and_Quality_Checks.md) §7.2;
[Frozen_Ladder_and_Tolerances.md](Frozen_Ladder_and_Tolerances.md) "Tests and tolerances".

**What:** P1 is "one-step **relative \(L^2\) on \(\rho_-\)** \(< 5\times10^{-3}\)"; P2 is "same
after \(T=200\) steps \(< 5\times10^{-2}\)"; P0 is \(|N(t)-N(0)|/N(0) < 10^{-3}\). All three are
**ratios whose denominator is the full ground-state density**. At \(\Delta t = 0.05\) au the density
barely moves in one step, so the *persistence* (identity) predictor — output = input, expressible
exactly by a \(3\times3\times3\) kernel with a single non-zero centre tap — scores near zero on all
three, and conserves \(N\) exactly, so it passes P0 by construction.

**Evidence.** A 1-D soft-core grid TDSE at the **frozen** \(h=0.20\,a_0\) and \(\Delta t=0.05\) au,
split-operator, ground state by imaginary time, then a linear-response kick. **This is a model, not
the teacher** — its purpose is the order of magnitude and the mechanism, both of which are
dimension-independent because the denominator is the static density either way. If anything 3-D H₂
is *worse*: more of \(\|\rho_-\|_2\) sits in the static core and tail.

```
> python passb_checks.py
== 3. identity-map null on the P1/P2 metric ==
soft-core a=1.0 (H-like)  E0 -0.6698 au  kick 0.01: identity_P1_max 3.614e-04  identity_P2_200 7.579e-03
soft-core a=1.0 (H-like)  E0 -0.6698 au  kick 0.1 : identity_P1_max 3.613e-03  identity_P2_200 7.506e-02
soft-core a=0.5 (deeper)  E0 -0.8909 au  kick 0.01: identity_P1_max 4.574e-04  identity_P2_200 3.714e-03
soft-core a=0.5 (deeper)  E0 -0.8909 au  kick 0.1 : identity_P1_max 4.463e-03  identity_P2_200 3.725e-02

P1 gate 5.0e-03   P2 gate 5.0e-02
```

At the standard linear-response kick strength (0.01 au) **doing nothing passes P1 by 14× and P2 by
6.6×**. At a ten-times-stronger kick, doing nothing still passes P1, and P2 only just fails. On the
**field-free** windows — one of the plan's three declared kick protocols, and the protocol that
*defines* P0 — doing nothing is exact.

This is Pass A finding 3 one level up. Pass A found a gate that random noise passes and repaired it.
This is a gate that the *global minimum of the stated training objective* passes: a one-step MSE at
\(\Delta t = 0.05\) au has its optimum within \(\sim10^{-4}\) relative of the identity, so the loss
in §6.1 does not merely permit the degenerate solution, it rewards it.

**Why it matters:** P1 and P2 are the only numerical gates the thesis owns on H₂, and P3's zero-shot
number is "P1-style". Three seeds and mean ± SD cannot detect this — an identity map has zero seed
variance. Nowhere in the plan is a **null / persistence baseline** pre-registered; P4's only
comparator is the linear stencil, which is a *worse* comparator than doing nothing (issue 8). As
written, a passed P0/P1/P2 is compatible with a network that has learned nothing whatsoever, and the
Module 08 verdict sentence ("P0 and P1 passed on H₂") would be literally true.

**What would close it — in spec, before the 8 h pilot, because §4 forbids moving a gate afterwards:**

1. Score the **update**, not the state: relative \(L^2\) of
   \(\hat\rho(t+\Delta t)-\rho(t)\) against \(\rho^{\text{teacher}}(t+\Delta t)-\rho(t)\). This is
   the same measurement the teacher itself is doing and it has no degenerate solution.
2. Add **persistence** as a mandatory pre-registered row in P1, P2, P3 and P4, reported beside the
   learned rule and the linear stencil in every table. A skill score
   \(1 - \varepsilon_{\text{learned}}/\varepsilon_{\text{persistence}}\) makes the claim ladder
   honest at no cost.
3. Restate the P1/P2 numbers in the new metric. They will not be \(5\times10^{-3}\).

---

### 4. Nine of eleven channels are trained and never gated — and they are exactly the impossible ones

**Where:** [Distilled_Project_Plan_and_Quality_Checks.md](Distilled_Project_Plan_and_Quality_Checks.md)
§6.1 (loss) vs §7.2 (gates).

**What:** §6.1 puts **equal weight** on the four groups \(\{\rho_-\},\{\mathbf j\},\{\mathbf
E\},\{\mathbf B\}\). §7.2 defines P1, P2 and P3 as "relative \(L^2\) **on \(\rho_-\)**" and P0 on
\(N\). So \(\mathbf j\), \(\mathbf E\) and \(\mathbf B\) — nine of the eleven channels, three
quarters of the loss — never enter a pass/fail criterion, and \(\rho_+\) is not even in the loss.

**Why it matters:** compose this with issue 1. The channels a local stencil provably cannot
represent at the frozen constants are \(\mathbf E,\mathbf B\); those are precisely the channels that
no gate scores. The plan's evaluation contract is therefore blind in exactly the direction its
architecture is broken. A referee who asks "what did the network do to the magnetic field" gets no
number from the frozen contract at all. It also makes the whole Maxwell apparatus — the teacher
choice that drives issues 1, 2, 5, 6 and 10, and the entire cost of the plan — carry **zero** weight
in the thesis's own verdict sentence.

**What would close it — in spec:** either gate \(\mathbf j,\mathbf E,\mathbf B\) (declare per-group
relative \(L^2\) targets, report-only is acceptable, silence is not), or take them out of the loss
and out of the promised state. Do not keep a channel that is trained, unscored, and structurally
unreachable.

---

### 5. The named teacher's coupled Maxwell + electronic capability is documented as not-yet-available, and Windows has no supported production path

**Where:** [Compute_Budget_2026-09-01.md](Compute_Budget_2026-09-01.md) §3 "Install" and §7 rung 1;
[Distilled_Project_Plan_and_Quality_Checks.md](Distilled_Project_Plan_and_Quality_Checks.md) §3.1.

**What.** Verified against Octopus's own documentation, branch `main`, fetched 2026-09-01:

- Maxwell tutorial index
  (`https://www.octopus-code.org/documentation/main/tutorial/maxwell/`): "Currently, different types
  of classical linear media, as well as external current densities, incoming plane wave boundaries
  and absorbing boundaries can be used. **In future versions, this will be coupled to matter
  systems**, to go beyond the usual forward-only coupling between the fields, electrons and nuclei."
  The five Maxwell lessons are: input file, plane waves in vacuum, external currents + PML,
  non-dispersive media, dispersive media. **None couples Maxwell to an electronic system.**
- Maxwell input-file page, list of multisystem system types: "**electronic: An electronic system.
  (only partly implemented)**", and the Maxwell system requires `ExperimentalFeatures = yes`.
- The Multisystem tutorial's four lessons are: introduction, celestial dynamics, interaction graph,
  Verlet propagation. There is no Maxwell–Kohn–Sham lesson there either.
- The capability the plan is actually assuming is bibliography item 2 (Bonafé et al. 2024),
  described by its own abstract as "designed for **massively-parallel** multiscale simulations".
  That is a cluster paper, and the plan cites it as the definition of its teacher.
- **Windows:** the manual's install page offers Spack (HPC-oriented; "compiling Octopus and
  dependencies … on the order of 1 hour") and a manual CMake/Ninja Fortran+MPI build. Neither
  mentions Windows. There *is* a Windows path — the official Docker images, which the docs say run
  on Windows — but the same page states: "**The images do not provide optimised builds for CPU (no
  vector instructions are used). Therefore, they are best suited for small calculations such as in a
  workshop or tutorial.**"

**Why it matters:** the plan's escalation rung 1 is "Octopus+Maxwell cannot be installed inside the
caps → **stop**." That rung is answerable **today**, from documentation, before any of the 80 h is
spent — and the honest reading is that a coupled Maxwell + electronic H₂ run is a research-code
exercise on an experimental, partly-implemented system type with no worked example, undertaken by
one person at 10 h/week on a Windows laptop whose only turnkey path is a container the vendor
describes as tutorial-grade. The plan's own text calls the install "**unmeasured**", which is
honest, but it then budgets 80 h of human I/O against it and writes the whole thesis downstream of
it.

Also: the plan's bibliography cites items 1 (Octopus 2020) and 2 (Bonafé 2024) for the teacher, but
**not** the paper Octopus's own Maxwell documentation points at — Jestädt, Ruggenthaler, Oliveira,
Rubio, Appel, *Adv. Phys.* (2019), DOI 10.1080/00018732.2019.1695875, "Light–matter interactions
within the Ehrenfest–Maxwell–Pauli–Kohn–Sham framework". That is the implementation reference for
the thing being frozen.

**What would close it — as science, and it is cheap:** a **spike**, time-boxed to 20 h human and
committed as a dated note *before* Q0: install Octopus (Docker or WSL), run the vacuum plane-wave
Maxwell lesson, run an ordinary H₂ RT-TDDFT, then attempt one coupled Maxwell + electronic H₂ deck.
Record the version string, `octopus --config`, and whether the coupled deck is accepted. If it is
not, rung 1 has fired, and it has fired for 20 h instead of 320.

---

### 6. At this box and this \(\Delta t\), "Maxwell, not Poisson" is a distinction the teacher cannot resolve

**Where:** [Frozen_Ladder_and_Tolerances.md](Frozen_Ladder_and_Tolerances.md) contradiction table
("Teacher Maxwell–TDDFT … Poisson is forbidden mid-study"); Distilled §3.1, §4.

**What:** the frozen box is molecule \(+ \ge 6\,a_0\) vacuum, i.e. \(\sim13.4\,a_0\) for H₂.

**Evidence:**

```
> python passb_checks.py
== 2. does light stay in the frozen box? ==
H2_box_a0 13.40  cells_per_edge 67  light_crossing_au 0.0978  = 1.96 teacher steps
H2O_box_a0 15.00  cells_per_edge 75  light_crossing_au 0.1095  = 2.19 teacher steps
light_travel_over_P2_horizon_a0 1370  = 102 box crossings
```

Light crosses the entire simulation box in **two teacher steps**, and over the whole P2 horizon it
crosses it **102 times**. Retardation across an H₂ molecule is therefore below the time resolution
of the scored window: to anything the gates can see, the field in the box is instantaneous. The
physical content that "Maxwell" buys over "Poisson" at this box size, at this \(\Delta t\), on a
neutral two-electron molecule with frozen nuclei, is not resolvable by the frozen tests.

There is also an unresolved fork that the plan must answer before Q0, and either branch hurts:

- **If \(\mathbf E\) carries the static Coulomb field of the frozen point nuclei**, then the
  \(\mathbf E\) channel *is* a Poisson reconstruction of a charge distribution, under a different
  name, and the freeze's prohibition is being satisfied by wording.
- **If it does not** — i.e. the Maxwell subsystem is sourced by the current only, which is what the
  documentation's "external current densities" and the minimal-coupling formulation both suggest —
  then no channel in the 11-channel state carries \(v_{\text{ext}}\) or \(v_H\), the state is not
  closed (issue 7), and on the **field-free P0 window** \(\mathbf E \approx \mathbf B \approx 0\),
  so six of eleven channels are identically zero on the window that defines the plan's first gate.

The second branch also disposes of the brief's drop-\(B\) worry: for a bound electron
\(|B|/|E| \sim v/c \sim Z\alpha \sim 10^{-2}\text{–}10^{-3}\), so `b_numerically_zero.py` will print
a small number on the ladder and three channels will be dropped — legitimately, under a §4 note,
and the gate will have worked. But it will have worked by revealing that the magnetic channel was
never carrying anything, which is a verdict on the teacher choice, not a discovery.

**What would close it — in spec:** state, before Q0, exactly what the \(\mathbf E\) channel
contains (transverse/radiated only, or total field including the nuclear and Hartree longitudinal
parts), and justify the \(\ge 6\,a_0\) vacuum against a Maxwell PML requirement — Octopus's Maxwell
box needs an absorbing region whose width is "the derivative order (default is 4) times the
spacing" plus `MaxwellABWidth`, which eats a large fraction of \(6\,a_0\) before any physics happens.

---

### 7. \((\rho_+,\rho_-,\mathbf j,\mathbf E,\mathbf B)\) is not a closed state, so the promised map is not a function — and on ALDA the honest result is a measured failure

**Where:** [Overarching_Goal.md](Overarching_Goal.md) prime directive; Distilled §1, §2, §5.1.

**What:** the prime directive promises a map from the neighbourhood of a cell to the same quantities
one step later. Octopus does not propagate \((\rho,\mathbf j)\); it propagates Kohn–Sham **orbitals**.
Two KS states with identical \((\rho,\mathbf j)\) evolve to different \(\rho(t+\Delta t)\), so as
stated the map is not single-valued. Runge–Gross (bibliography item 6) rescues it only in the weak
form the plan cannot use: the density *history*, together with a fixed initial state, fixes the
potential — a memory functional, not an instantaneous local map. The exact equation of motion for
\(\rho\) closes only through a stress tensor that is a functional of the orbitals / pair density.
This is the real content of the brief's attack 1, and it is not fixed by a bigger kernel.

Two consequences the plan should say out loud rather than discover:

- **Which operator would actually be learned.** Under ALDA the exchange–correlation potential is a
  *pointwise* function of the local density; the kinetic operator is a stencil. The only genuinely
  nonlocal pieces of the KS Hamiltonian are the **Hartree** term (Poisson, global) and the
  **nonlocal pseudopotential projectors** Octopus uses for O — so the KS Hamiltonian on the grid is
  not a local operator even in principle. A local stencil that succeeded would have to be
  reproducing Poisson inside a three-cell neighbourhood.
- **Is a successful ALDA H₂→H₂O transfer a result or a tautology?** As currently framed, a referee
  will read it as close to tautological: ALDA *asserts* that the xc response is local in the
  density, so demonstrating that the local part transfers between two closed-shell hydrides
  demonstrates the assumption. The non-tautological content is the **Hartree/nonlocal residual**,
  and the interesting outcome is therefore a *measured failure* — "the local rule reproduces the
  kinetic + ALDA part to \(X\) and misses the Hartree part by \(Y\), and \(Y\) is what a local
  surrogate costs." Pre-register that decomposition as the headline and the thesis is not empty. Do
  not pre-register "transfer worked" as the headline; that claim is cheap and a referee will say so.

Exiling exact 2-e H₂ to Horizon 10 is correct and is not the problem. The problem is the framing.

**RECALLED, NOT VERIFIED — do not cite until fetched:** Vignale & Kohn (PRL, 1996) on why a local
approximation must be formulated in the **current** rather than the density, and Dobson's
harmonic-potential theorem (PRL, 1994) on why the density-local approximation fails. If issue 7 is
answered in the report, both belong in
[Relevant_Scientific_Papers.md](Relevant_Scientific_Papers.md) as new numbered, verified entries.
They also happen to *support* the plan's choice to carry \(\mathbf j\) as a state channel, which is
worth saying.

**What would close it — in spec:** replace the prime directive's "the rule maps … to the same
quantities one step later" with an explicit closure statement: the map is defined **on the
trajectory manifold generated by the hashed decks from a fixed initial state**, is not claimed to be
a universal functional, and its residual against the teacher is the measurement. One paragraph, and
the claim becomes defensible.

---

### 8. The repaired P4 baseline is simultaneously a straw man and a super-human, on different channels

**Where:** [probes/linear_stencil.py](../probes/linear_stencil.py); Distilled §5.3; the brief's
attack 5.

**What:** taking Pass A's repairs as given and going further, as instructed.

*Super-human on \(\mathbf E,\mathbf B\).* The repair gives the baseline 119 Maxwell sub-steps per
teacher step, each a central difference reaching one cell:

```
> python passb_checks2.py
baseline sub-steps 119; baseline reach 119 cells = 23.8 a0
frozen H2 box 13.40 a0 -> baseline reach is 1.8x the whole box
```

Per teacher step the baseline's numerical domain of dependence is **1.8× the entire simulation box**
— effectively global — against the learner's **one cell** (issue 1). P4 therefore compares a
globally-coupled integrator to a strictly local map on channels the learner provably cannot
represent. A learner loss on \(\mathbf E,\mathbf B\) is guaranteed and carries no information.

*Straw man on \(\rho_-,\mathbf j\).* Read the equations, per the brief. `step()` does
\(\rho_- \leftarrow \rho_- - \Delta t\,\nabla\!\cdot\!\mathbf j\), then **holds \(\mathbf j\) fixed**
("j held (no constitutive update)"). There is no constitutive law at all: no Ohm, no Drude, no
pressure, no ALDA, no Hartree force. The docstring calls "j is an independent channel" a
constitutive closure; it is the *absence* of one. So the baseline transports a frozen current
forward in time with a first-order-in-time explicit update — it is a discretisation of vacuum
Maxwell plus continuity bookkeeping, exactly as the brief suspected. Its \(\rho_-\) will drift
monotonically and a learner win on \(\rho_-\) is guaranteed and carries no information.

Since P1/P2/P3/P4 are all scored on \(\rho_-\) (issue 4), the *reported* comparison is the straw-man
half. The plan will report a win it cannot lose, against a baseline that is unbeatable on the
channels it does not report.

**What a fair linear baseline would contain.** The canonical linear closure for exactly this state
is **linearised quantum hydrodynamics**: continuity for \(\rho\), plus an Euler/force equation for
\(\mathbf j\) driven by (i) the Hartree force from a Poisson solve, (ii) the frozen-nuclei external
field, and (iii) a pressure term from a Thomas–Fermi (+ von Weizsäcker) functional — optionally a
Drude/Ohm damping term. That is linear, has no learned coefficients, uses precisely \((\rho,\mathbf
j)\), and is what a computational-EM or plasmonics referee will name within thirty seconds. It is
also what makes P4 a real test: it can actually propagate a plasma oscillation, so beating it means
something.

**Why it matters — and this one has a deadline:** Distilled §4 forbids "Editing the frozen linear
baseline in `probes/linear_stencil.py` after Q0." Q0 has **not** been hashed. So the window to make
P4 a fair test is open **now** and closes permanently at Q0. If the baseline is frozen as written,
the plan's flagship comparison is decided before it runs, in opposite directions on different
channels, forever.

**What would close it:** before Q0, either upgrade the baseline to a declared hydrodynamic closure
(and add bibliography item 15 as a real, fetched reference — see issue 11), or **rename P4 honestly**
as "learned rule vs vacuum-Maxwell-plus-continuity bookkeeping" and remove any language implying it
is a constitutive model. Both are acceptable. Freezing the current object while calling it "a
declared constitutive closure" is not.

---

### 9. Module 05's rubric shield protects the grade only by permitting the module to stop, and the missing approval is not about "synthetic"

**Where:** [Capstone_Mapping.md](Capstone_Mapping.md) Module 05 (A1/A2/A3), §5.5;
[Relevant_Scientific_Papers.md](Relevant_Scientific_Papers.md) item 10;
[Rubrics/05_Deep_Learning_Systems.md](../../../Rubrics/05_Deep_Learning_Systems.md).

**What:** Pass A's issue 6 is taken as given — the ladder is no longer circular, and A2 is a genuine
independent branch. Going further, on the domain-side question the brief asks: **does the Task A /
Task B split actually protect the grade?**

Partly, and not in the way the plan thinks. The plan's stated risk is "a mentor treats self-run
TDDFT cubes as *synthetic*". That is the weaker risk: rubric 1.5.1's clause is aimed at
generated/simulated stand-ins for real data, and cubes from a named third-party ab initio code with
a hashed deck are a *computational experiment*, which the mapping already argues correctly. The
stronger risk is the other rubric word: Module 05 requires a dataset with **access instructions**,
i.e. something a grader can obtain. Self-run cubes are not public until the student publishes them.
That is a solvable problem (Zenodo, DOI, before submission) and the plan does not name it anywhere.

Meanwhile A3 — "Module 05 stops and the stop is reported" — is honest governance and a poor
deliverable: it removes the plan's only deep-learning module. And since Module 06 inherits the same
source, and Module 08 integrates {03, 05, 07}, A3 propagates into three graded submissions.

Round 3 issue 3 (mentor approval for 04–06) has been open across three plans. It is the single
oldest unclosed item in the repository.

**What written mentor approval would have to say** — get these four sentences, dated, before Q0:

1. Volumetric data generated by a named third-party ab initio code (Octopus, version string, hashed
   input deck) is a **computational experiment**, not "synthetic or AI-generated", for rubric 1.5.1
   in Modules 05 and 06.
2. A dataset the student **publishes with a DOI before submission** satisfies "publicly available /
   access instructions" for Module 05.
3. Whether **Task B alone** may serve as the Module 05 dataset if A1 and A2 both fail — i.e.
   whether the shield is needed at all.
4. Whether Module 03's "Accepted Sources" list is read literally (Pass A issue 5). Ask in the same
   message; it is the same mentor and the same clause family.

---

### 10. The row most wrong in the 840 h is the 80 h grid-and-teacher bucket — and it is plan 01's failure mode wearing a new substrate

**Where:** [Capstone_Mapping.md](Capstone_Mapping.md) §6;
[Compute_Budget_2026-09-01.md](Compute_Budget_2026-09-01.md) §5;
[Overarching_Goal.md](Overarching_Goal.md) "Hours".

**What:** the brief asks which row is most wrong. It is **"Frozen grid + teacher I/O — 80 h"**, and
it is wrong by a lot, for reasons issues 2 and 5 establish rather than assert. That bucket has to
contain: install a Fortran/MPI research code on Windows via a container the vendor calls
tutorial-grade or via an unstated WSL toolchain; get a coupled Maxwell + electronic run working on a
system type the code's own documentation labels "only partly implemented", with `ExperimentalFeatures
= yes` and no worked example anywhere in the tutorial set; resolve the Maxwell-grid-vs-matter-grid
question (issue 2) well enough to hash it; write and hash decks for three species and three kick
protocols; and convert the output to 11-channel npz.

The plan's own diagnosis of plan 01 is that **two-thirds of the budget went into making the
substrate behave instead of producing the result**, and that plan 03 exists to forbid that. Plan 03
has reproduced the pattern with a different substrate. The 80 h cap is not a defence — a cap is only
a defence if the work can plausibly fit inside it, otherwise it is a stop rule that fires after the
hours are gone.

**Second most wrong: the 168 h wall-clock**, which is a cap over an unmeasured object whose step
count is 103× larger than the plan believes (issue 2 branch 2): 20,539 Maxwell propagations per
200-step window, before the KS side, before three kick protocols, before held-out windows, before
H₂O. Third: the mapping has no **storage** row at all —

```
> python passb_checks2.py
H2:  67^3 = 300763 cells; one 11-channel float64 frame 25.2 MB; 200-step window 4.95 GB
H2O: 75^3 = 421875 cells; one 11-channel float64 frame 35.4 MB; 200-step window 6.95 GB
```

~5–7 GB **per window**, times protocols and splits, on a laptop, with 80 h of human "cube I/O" to
move it.

**Is the calendar evaluable while T0 is blank?** No, and the plan says so correctly. But T0 is not
the binding problem: **Q0 is**. Q0 must precede every Module 05 B window, and issue 2 shows Q0
cannot be hashed honestly until a coupled Maxwell teacher has printed its accepted \(\Delta t\) and
grid. So the plan's earliest irreversible act is blocked on its most expensive unmeasured object,
which is the same topology as plan-01 issue 15 ("Module 03 gated on the hardest unfunded infra"),
carried as R3-6 and still open.

**Is H-atom + one H₂ window the honest primary plan?** Yes — and it should be promoted from safety
net to **primary**, matter-only (issue 1 branch a). H atom is analytic and free; one matter-only
RT-TDDFT H₂ window at \(0.20\,a_0\), \(67^3\), 4 orbitals, 200 steps is minutes on this laptop, not
a cap. Everything the thesis actually scores — P0, P1, P2, P3, P4, the identity null, the
hydrodynamic baseline — fits in that. Maxwell then becomes what it should have been from the
beginning: a **Horizon** item, next to phase and pair density.

---

### 11. The thesis comparator has no verified reference, and the teacher's implementation paper is missing

**Where:** [Relevant_Scientific_Papers.md](Relevant_Scientific_Papers.md) items 15 and 1–2.

**What:** item 15 — "Continuity + Maxwell as linear baseline: Jackson, *Classical Electrodynamics*,
or a modern computational EM citation" — is marked **NOT FETCHED** and sits in the list next to the
pedagogy items (8) and the cusp item (7). But item 15 is not pedagogy: it is the reference for
**P4**, the thesis comparison, the object §4 freezes at Q0 and the object issue 8 says is not a
constitutive model. The plan currently intends to freeze its flagship comparator against a citation
that is "Jackson, or something".

Missing entirely: Jestädt, Ruggenthaler, Oliveira, Rubio, Appel, *Adv. Phys.* (2019),
DOI 10.1080/00018732.2019.1695875 — the Ehrenfest–Maxwell–Pauli–Kohn–Sham paper that Octopus's own
Maxwell documentation cites twice as *the* reference for the implementation being frozen as teacher.
(DOI as printed on the Octopus tutorial pages fetched 2026-09-01; **fetch the landing page before
citing**, per this file's own rule.)

**What would close it:** fetch and pin item 15 as a specific edition or a specific paper for
whatever baseline survives issue 8; add Jestädt 2019 as a new numbered entry before any deck is
hashed; and if issue 7's decomposition becomes the headline, add the two RECALLED entries named
there.

---

### 12. The prime directive says phase is mandatory; the technical plan exiles it to Horizon 10

*Added after the review was first written, from the author's own objection. It is the finding this
pass should have caught and did not: issue 7 diagnosed the closure problem from the TDDFT side and
never checked it against the Goal file, where the answer was already written down.*

**Where:** [Overarching_Goal.md](Overarching_Goal.md) "What this is", third bullet;
[Distilled_Project_Plan_and_Quality_Checks.md](Distilled_Project_Plan_and_Quality_Checks.md) §5.1.

**What:** the Goal states, as physical content and not as an aspiration:

> "The complex \(\psi\) is a packaging of presence and phase; **phase is not optional if the next
> step is to be determined**."

Distilled §5.1 states: "Packing \(z=\rho_++i\rho_-\) is bookkeeping, not \(\psi\). **Phase is not a
promised channel (Horizon 10).**" Distilled's own header says "Agrees with `Overarching_Goal.md`. If
they drift, the Goal file wins." They drift, on the definition of the state, and the Goal wins — so
by the plan's own precedence rule the frozen 11-channel state is **not** the state the plan promises.

**Why it matters:** this is not a wording clash. The Goal's sentence is a correct statement of the
physics and it is *why* issue 7 exists: \((\rho_\pm,\mathbf j,\mathbf E,\mathbf B)\) does not
determine the next step precisely because the phase has been dropped. Pass A found four objects that
said something different from what they are; this is a fifth, and it is the load-bearing one, because
it means the plan diagnosed its own fatal flaw in its first section and then froze the flaw anyway.

**What would close it — and neither branch is small:**

- **Admit the closure.** Rename the promised object: not "the update rule" but "a local *closure* of
  the density–current dynamics, with the phase/orbital information deliberately discarded, and the
  resulting residual as the measurement." Then the Goal sentence must be edited, because it currently
  promises something the plan does not build.
- **Carry the phase.** A single complex field per cell, \(\psi=\sqrt{\rho}\,e^{iS}\), is the
  Madelung / quantum-hydrodynamic representation. It is genuinely local, genuinely one number per
  cell, and it is exactly the physical picture the Goal describes. But it carries only an
  *irrotational* current, \(\mathbf j = \rho\nabla S\), so it cannot represent the multi-orbital
  Kohn–Sham current or the Pauli kinetic pressure — which means the missing term becomes the learned
  object, and that term is the **orbital-free kinetic energy functional**. That is a real and famous
  open problem, it is a better thesis than the one written, and it is emphatically not an ALDA
  Kohn–Sham imitation task. If this branch is taken, **Octopus RT-TDDFT is the wrong teacher** and
  the whole freeze is reopened.
- Carrying a phase *per occupied orbital* is the third option and it is the one Horizon 10 assumed.
  It breaks P3: H₂ has one occupied KS orbital and H₂O has four, so the channel count becomes
  molecule-dependent and "the same weights for every molecule on the ladder" — the sentence the whole
  transfer test rests on — cannot be written.

---

## Non-blocking findings

### 12. The receptive field is not frozen, and it is the number that matters most

[Frozen_Ladder_and_Tolerances.md](Frozen_Ladder_and_Tolerances.md) freezes the **kernel** (3×3×3)
and the **stride** (\(k=1\)), and Distilled §4 now names promoting 5×5×5 as a deviation. Neither
freezes **depth**. The plan variously says "one 3-D convolution" (Distilled §5), "one 3-D stencil /
small conv-net" ([README.md](../README.md)) and "one 3-D stencil / small conv-net" (root README). An
\(L\)-layer stack of 3×3×3 convs has a receptive field of \(L\) cells — so "small conv-net" silently
contains the axis that issue 1 says decides the thesis. Freeze **effective receptive field in
cells** as the hashed quantity, and make increasing it (by depth, dilation, stride or kernel) the
same §4 deviation that promoting 5×5×5 already is.

### 13. `b_numerically_zero.py` prints an absolute number and cannot decide anything

The script prints `max_abs_B` and `rms_B` in atomic units and then unconditionally prints
`drop_B_forbidden 1`. There is no threshold, no reference scale, and no comparison. "Numerically
zero" for a field in au is meaningless without a denominator. Print \(\max|B| / \max|E|\) and
\(\max|B|\) against the teacher's own output precision; expect \(\sim v/c \sim 10^{-2}\text{–}10^{-3}\)
(issue 6). Then the drop-\(B\) gate is a decision rather than a ritual.

### 14. "Conservation penalty off" is right, and is not what threatens P2

The brief asks whether turning the penalty off dooms P2 by charge leakage. It does not, and the
reasoning in Distilled §6.1 (do not train P0 into a tautology) is correct and should be kept. Issue 3
supersedes the worry from the other direction: the one-step MSE optimum is so close to the identity
that the learned rule's default failure mode is *too little* dynamics, not runaway leakage. Leave
the penalty off; fix the metric.

### 15. `teacher_cost.py` still demands an Octopus number for an analytic rung

Pass A finding 14 noted it; still true. `SPECIES = ("H", "H2", "H2O")` and the script refuses to run
without an `"H"` entry, while the ladder defines rung 0 as "Analytic 1-e / exact grid TDSE" — a rung
with no Octopus in it — and §2 counts that window inside the Octopus 168 h cap. Under issue 10's
recommendation (H atom + one matter-only H₂ window as primary), this script becomes the plan's most
important probe and should distinguish diagnostic cost from teacher cost in its output keys.

### 16. The freeze file's amendment mechanism is now visibly weaker than the plan believes

Pass A finding 14 flagged that [Frozen_Ladder_and_Tolerances.md](Frozen_Ladder_and_Tolerances.md)
has no date in its filename, is stamped "Frozen date 2026-08-29", and contains a table of edits made
to it. It now contains **two** such tables. Plan 02's convention was a new dated file. If Pass B's
findings are absorbed, that will be a third block, and a freeze amended three times inside four days
by its own author is the loophole Pass A ranked first ("every gate is loosenable by a note the
author writes") expressed as a filename. Supersede with a dated file, and keep the old one unedited
so the reductions stay visible — exactly as plan 02 did.

---

## What passed

Named so a Round 6 does not re-litigate it.

- **Pass A's four repairs hold up under domain scrutiny.** Non-periodic boundaries, the leapfrog
  Maxwell, the 11-channel correction and the \(0.20\,a_0/Z\) refinement are all correct as far as
  they go; I re-derived the 119 sub-steps from `linear_stencil.maxwell_substeps` and the Courant
  ratio from `grid_spec` and both reproduce. Every criticism in issues 1, 2 and 8 above is about
  what those repairs *imply* for the teacher and the learner, not about the repairs.
- **The refusal structure is real.** The probes decline to invent numbers; `teacher_cost.py` prints
  `NOT_RUN`; the Compute Budget refuses to type a wall-clock. It is because the plan holds that line
  that issue 2 could be found by arithmetic instead of by discovering it in month fourteen.
- **The bibliography's verify pass is the reason issue 2 is provable.** Item 2's "different grid
  spacings for the Maxwell and matter subsystems" is a sentence the plan itself fetched and recorded;
  it just was not read against the frozen grid.
- **Carrying \(\mathbf j\) as a state channel is the right instinct**, and the TDDFT literature
  supports it more strongly than the plan claims (issue 7). Do not drop it when \(\mathbf E,\mathbf B\)
  go.
- **The claim-language discipline is genuinely protective.** The forbidden-quotes list, "mean-field
  / ALDA, not chemical accuracy", and "inconclusive is publishable" are the reason this review can
  recommend a scope reduction rather than a retraction: nothing that has been promised would have to
  be un-promised except the Maxwell channels.
- **Not reopening plan 01 or 02.** Nothing found here argues for the IR product or the pyrene
  promise. The pivot's core — one local rule, a frozen evaluation contract, H₂ → H₂O — survives
  issues 1–11 and is affordable once the Maxwell teacher is off. Issue 12 is the exception: it
  reaches the definition of the state itself, and it is not repaired by any scope reduction.

---

## The one paragraph to act on first

Q0 has not been hashed, so every fix above is still free. In order: settle issue 12 first, because it
decides what the state *is* and nothing else can be frozen before it; run the 20 h Octopus spike
(issue 5) — it decides issues 1, 2, 6 and 10 at once and it decides them before any budget is
committed; fix the metric and add the persistence null (issue 3), which costs an afternoon and
without which no P-gate means anything; decide the fate of \(\mathbf E,\mathbf B\) (issues 1, 4, 6)
and write it into the Goal file, not into a §4 note; and either upgrade or honestly rename the P4
baseline (issue 8) **before** Q0 closes that door permanently. Then hash Q0.
