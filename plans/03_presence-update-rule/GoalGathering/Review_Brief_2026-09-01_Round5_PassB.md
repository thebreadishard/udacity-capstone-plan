# Review brief — Round 5, Pass B: adversarial domain review

**Give this only after Pass A’s findings are written down.** Pass A was unprimed on purpose. This
one is primed, because the remaining questions are specific and expensive to find by wandering.

---

## Your role

A hostile examiner who does computational chemistry / TDDFT / scientific ML for a living. You are
not trying to help. You are trying to find the thing that makes this project fail in month fourteen.

The student would rather learn now that the plan is wrong than defend it later.

## Standing context

Same as Pass A: master’s capstone, one person, ~10 h/week, nothing executed, consumer hardware.
Plan 03 replaced plan 02 on 2026-08-29 after plan 02 died as a *label factory* (coupled-cluster rung
blocked on measurement; a published PAH band family already broke a locality assumption). Plan 01
had already died on discretisation spend for a PES-to-IR product.

**A legitimate outcome of this review is “the pivot to plan 03 was a mistake.”** Say so if you
believe it, and say which measurement would settle it. Do not rehabilitate plan 01’s IR product or
plan 02’s pyrene promise unless you can name an affordable measurement that reopens them.

You are **not** reviewing PAH anharmonic IR. Do not spend this pass on GVPT2, MLIPs, or JWST.

## What to read

This review runs in a **VS Code chat on the CapstonePlan workspace**. Read the files **in this
workspace**. Do not fetch GitHub; the remote is a public copy and may lag.

Read **after** Pass A's findings exist as a written file in this folder — they do:
[Professor_Review_2026-09-01_Round5_PassA.md](Professor_Review_2026-09-01_Round5_PassA.md), and its
findings were addressed in spec on 2026-09-01. Read it before you start; findings 2–4 change the premise
of attack 5 below. Same corpus as Pass A. Folders for plans 01 and 02 are **not in this workspace**; do
not fetch git history or GitHub to reconstruct them. Use the inheritance map when a Pass A finding names
a source issue.

0. [README.md](../../../README.md) and [plans/README.md](../../README.md) — status banners
1. [../README.md](../README.md)
2. [Overarching_Goal.md](Overarching_Goal.md)
3. [Frozen_Ladder_and_Tolerances.md](Frozen_Ladder_and_Tolerances.md)
4. [Compute_Budget_2026-09-01.md](Compute_Budget_2026-09-01.md)
5. [Distilled_Project_Plan_and_Quality_Checks.md](Distilled_Project_Plan_and_Quality_Checks.md)
6. [Capstone_Mapping.md](Capstone_Mapping.md)
7. [Relevant_Scientific_Papers.md](Relevant_Scientific_Papers.md)
8. [Inheritance_of_Reviews.md](Inheritance_of_Reviews.md)
9. [../probes/README.md](../probes/README.md) and, for attack 5, [../probes/linear_stencil.py](../probes/linear_stencil.py)

Pass A findings, once written, live next to this brief. Ignore [Horizon/](Horizon/) and any `Uitleg/`.

## The plan in one paragraph

Learn **one** translation-equivariant local update

\[
(\rho_+,\rho_-,\mathbf{j},\mathbf{E},\mathbf{B})_{\mathcal{N}(x)}
\;\longmapsto\;
(\rho_+,\rho_-,\mathbf{j},\mathbf{E},\mathbf{B})_{x}^{t+\Delta t}
\]

as a 3-D conv stencil (default \(3\times 3\times 3\), \(k=1\)) on a **frozen** real-space grid
(\(0.20\,a_0\) outer, nuclear refinement \(\sim 0.20\,a_0/Z\), non-periodic finite box). Teacher: **Octopus RT-TDDFT, ALDA**, with
\(\mathbf{E},\mathbf{B}\) from **Maxwell–TDDFT** (Poisson reconstruction of \(\mathbf{E}\) from
\(\rho\) is forbidden unless Distilled §4). Nuclei are frozen point charges. Train on **H₂**;
zero-shot transfer to **H₂O**. Gates P0 (fixed point), P1 (one-step), P2 (200-step rollout),
P3 (water, vs linear stencil), P4 (learned vs frozen linear Maxwell+continuity). Conservation
penalty **off**. Infrared, JWST, and C₃₈₄H₄₈ are **not** Module 08. Caps: 840 h human, 80 h
grid+teacher I/O, 168 h wall-clock for the promised teacher set. Stop if Octopus+Maxwell cannot run.

## The six attacks, in order of how much damage they do

### 1. A local \(3\times 3\times 3\) stencil cannot imitate a KS + Maxwell step

The Kohn–Sham Hartree potential is nonlocal (Poisson / FFT). The KS kinetic piece is not an 11-channel
neighbourhood of \((\rho_\pm,\mathbf{j},\mathbf{E},\mathbf{B})\). Maxwell itself is local in the
curl, but the *constitutive* response of the electrons is not.

If the teacher step is dominated by the nonlocal Hartree / XC piece, the learned rule is being asked
to compress a global operator into a 3-cell stencil. That can pass P1 (one step, small \(\Delta t\))
and fail P2 (200 steps) for a structural reason, not a training reason.

**What to do:** argue from TDDFT / Maxwell–TDDFT practice, not from PAH IR. Is ALDA RT-TDDFT on H₂
even a fair teacher for a *local* rule, or does the plan need an explicit Hartree channel / larger
receptive field / FNO, which Distilled already treats as a *comparison axis* rather than the thesis?
If the local rule is the wrong operator family, say so, and say whether that kills plan 03 or only
kills the 3×3×3 default.

### 2. Octopus + Maxwell on a Windows laptop vs 168 h

The plan cites Octopus as the teacher and caps the promised set at 168 h wall-clock and 80 h human
I/O. `probes/teacher_cost.py` prints `NOT_RUN`. There is no measured H₂ Maxwell–TDDFT window.

**What to do:** from published Octopus / Maxwell–TDDFT timings you can **verify** (cite DOI or
arXiv; do not recall), is a real-time Maxwell–TDDFT H₂ trajectory on a frozen \(0.20\,a_0\) grid
with nuclear refinement a consumer-hardware object or a cluster object? Does Windows even have a
supported path, or is WSL/Linux implied and unstated? If 168 h is fantasy, which rung survives
(H-atom analytic only? no Maxwell, electrostatics only? stop)? Name the first measurement that
would force a stop under Distilled §3.3.

This is the single most likely place the plan breaks, and the author knows it.

### 3. ALDA mean-field vs the claim sentence

Overarching Goal already says many-electron correlation is **not** promised and that the 3-D field
is a closed mean-field / TDDFT-like world. Distilled still trains on ALDA.

**What to do:** is the claim sentence honest enough, or does “presence-update rule” still read as
if the network learned interacting electrons? Would a referee treat a successful H₂→H₂O transfer of
an ALDA surrogate as a result or as tautological (the teacher is already local-density)? If ALDA
is too weak a teacher to be interesting and exact 2-e H₂ is exiled to Horizon 10, is the thesis
empty?

### 4. Module 05 Task A still has no public voxel DOI

Bibliography item 10 is an honest **FAIL**: DeepDFT is a model, Cuevas-Zuviría is analytic
wavefunctions, Rackers is atom-centered — none is a cube dump. Rubrics 1.5.1: Modules 02–06 must
not be synthetic / AI-generated; M04 is Kaggle/UCI/Data.gov only. Round 3 issue 3 (mentor approval
for 04–06) is **still open**.

**What to do:** does the Task A / Task B split actually protect the grade, or does a grader treat
self-run Octopus cubes as synthetic the moment they appear in Module 05? Is the fallback (“Task A
ships without cubes”) a real Module 05 deep-learning project or a dodge? Name what written mentor
approval would have to say.

### 5. The linear stencil is either too weak or too strong

P4 compares the learned rule to frozen finite-difference continuity + Maxwell with a declared
constitutive closure, current held. If that baseline already rolls out H₂ for 200 steps, the
learned stencil has nothing to beat. If it immediately violates P0, the comparison is against a
straw man and a “win” is uninformative.

**Pass A already measured part of this** (its findings 3 and 4): the baseline was periodic, so P0 on it
could not fail — random noise passed at \(4\times10^{-15}\) — and its Maxwell update was forward Euler at
\(c\Delta t/h = 34.26\), 59× the 3-D limit, reaching NaN inside the P2 horizon. Both were repaired on
2026-09-01 (non-periodic; leapfrog with 119 CFL sub-steps). Take that as given and go further.

**What to do:** without running code, from the equations in `probes/linear_stencil.py` / Distilled
§5.3, is this baseline a serious constitutive model or a discretisation of vacuum Maxwell plus
bookkeeping? What would a *fair* linear baseline include (Ohm, Drude, KS-like local XC) and does
the plan forbid adding it after seeing numbers?

### 6. 840 h at 10 h/week still does not close

Mapping §6 budgets 840 h; T0 is **not** a calendar date in the mapping draft. Plan 01 issue 15 and
plan 02 R4B-6 were the same class. The 80 h teacher-I/O bucket is a cap, not a measurement.

**What to do:** which row is most wrong? At 10 h/week, does Octopus install + Maxwell decks + cube
I/O + stencil training + P0–P4 + Modules 02–04 public tables + 06–09 actually finish? Is H-atom +
one H₂ window the honest primary plan rather than the safety net? Say whether the calendar is
evaluable at all while T0 is blank.

## Also worth your attention

- **Drop-\(B\).** `b_numerically_zero.py` exists; dropping the magnetic channel stays forbidden
  until it prints ~0 **and** a Distilled §4 note. Is that gate real, or will \(B\sim 0\) on H₂
  electrostatics be used to quietly drop three channels?
- **Conservation off.** Intended so P0 is not trained into a tautology. Does that make P2
  structurally doomed (charge leaks every step)?
- **Kernel 5×5×5** is a Module 05 comparison axis, not the thesis. Can the author promote it to
  the thesis after 3×3×3 fails, without calling it a §4 deviation?
- **Anything Pass A flagged** that you think is worse than Pass A judged it.

## Output format

Plan 01 reached issue 15 plus a separate Round-3 list. Plan 02 used **Round 4, issues 1–N**.
Use **Round 5, issues 1–N**.

```
Verdict: [green light / conditional / no green light — and for what scope]

## Blocking findings
N. [Title]
   Where: [file, section]
   What: [the problem]
   Evidence: [what you verified, and what you are recalling rather than verifying]
   Why it matters: [consequence]
   What would close it: [in spec / as science — the repository distinguishes these]
```

A valid verdict is that plan 03 should not proceed. Write that if you believe it.
