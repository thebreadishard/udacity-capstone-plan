# Pre-registration — how true the anchors are out of plane (TASKS 184)

*5 November 2026, 07:5x, before any number of either check. The user, 5 Nov: 'Ja, prijs eerst de toets van het anker', then 'Doe beide, met
een uitzondering op decision 63' — decision 63 freezes new CC work until after June 2027; this check is the user's exception to it.*

## Why

Every CH-oop number the project reports is read against the carried anchors. Ten of the eleven are composites, CCSD(T)/cc-pVDZ +
[MP2/cc-pVTZ − MP2/cc-pVDZ]; only benzene has a full CCSD(T)/cc-pVTZ Hessian. The composite was tested once, on benzene (test 2, 6 Oct): it
sits 3.29 / 4.37 / 7.30 / 3.32 cm⁻¹ (ring-ip / CH-stretch / CH-oop / other) from full CC/TZ, so CH-oop is its weakest family, on one molecule.
And full CC/TZ itself sits 19.1 cm⁻¹ rms from Goodman's experiment-derived harmonics in CH-oop on benzene (TASKS 111, four modes), against 5.5
in ring-ip; the cc-pVDZ → cc-pVTZ step is large out of plane (CC/DZ was 70 cm⁻¹ off), and the step past TZ was never measured. The question
came up while deciding TASKS 183 (2), a network pretrained on MP2/6-31G* labels for CH-oop: its read would follow anchors whose CH-oop truth is
the least certain of the four families.

## (a) A second molecule for the composite: pyridine at CCSD(T)/cc-pVTZ out of plane

**Computation.** `probes/e8_cc_hessian_fd.py` on pyridine's plane-frame geometry (`cc_composite_full_check.py planeframe`: normal on z, max
|z| 2.2e-5 bohr), cc-pVTZ, frozen core by the element rule, step 0.005 bohr, `--symmetry`, the seven out-of-plane displacements (Cartesian 2,
5, 8, 11, 20, 23, 26; `--ks` positions 2, 5, 8, 11, 14, 17, 20 of the runner's own symmetry-unique list), explicit (T) lambda, both (T) C
kernels, the inline two-route check: benzene's 4 Oct settings. 14 gradients, ≈ 1.8 h each on 8 threads (benzene's run), ≈ 25 h, peak ≈ 12 GB
(benzene: 11.9 GB at max_memory 10,000 MB). The production route is the one gate 1 vouches for (`tests/test_acceptance_water.py`: the CCSD(T)
gradient against finite differences of its energy, frequencies against CCCBDB); its upstream counterpart is pyscf's
`grad/test/test_ccsd_t.py`. The runner now writes pyscf's own log (`<run>/pyscf.log`); the gradient is the same with and without it
(`tests/test_e8_pyscf_log.py`, 2.1e-12 a.u.).

**The truth of the check.** The carried pyridine composite rotated into the plane frame, its out-of-plane block (z × z) replaced by the CC/TZ
block reconstructed from the seven z rows by symmetry (`e8_symmetry.reconstruct`, test 3's path), the in-plane block and the couplings (zero by
symmetry, checked ≤ 1e-6 a.u.) kept, rotated back (`cc_composite_full_check.oop_block_replaced`). Only out-of-plane modes can differ.

**Read.** `probes/anchor_oop_check.py pyridine`: test 2's family read (corrected-ω rms per family on the analytic B3LYP modes,
`anchor_deck_rehearsal.readout`) of the composite against this truth. The same function reproduces test 2 on benzene to 1.4e-12 cm⁻¹
(`anchor_oop_check.py pin`, run today before any pyridine number).

**Line (CH-oop rms of the composite against CC/TZ):** ≤ 10 cm⁻¹ *holds* (as on benzene); 10–20 *weaker* — the CH-oop anchors carry an error
of that size; > 20 *fails* in CH-oop.

**Beside it, descriptive (one molecule, no verdict):** the CH-oop rms of truth − s·candidate on pyridine for ωB97X, MP2/cc-pVDZ and MP2/6-31G*,
s fitted on the other ten anchors as in the 5 Nov read's leave-one-out, against the composite truth (which must reproduce the 5 Nov record,
checked) and against the CC/TZ truth.

**Prediction.** *Holds*: two in three.

## (b) The basis limit: how far CH-oop moves past cc-pVTZ (MP2 step on benzene)

**Computation.** `cc_composite_full_check.py compute` on benzene's plane-frame geometry (normal on z; the corpus geometry is tilted 1.6°), MP2
frozen core, spherical, step 0.005 bohr, the two out-of-plane displacements (Cartesian 2 and 20, the orbit representatives' z), at cc-pVTZ and
cc-pVQZ: 8 gradients, ≈ 14 h on 8 threads (scaled N⁵ from the 850 s TZ gradient at 4 threads; a rough price). MP2, not CC: this measures how
far the basis is from converged out of plane, not the CC value there.

**The truth of the check.** Benzene's full CC/TZ anchor with [MP2/QZ − MP2/TZ] added on the out-of-plane block (test 3's formula,
`oop_step_added`). Second routes: the plane-frame MP2/TZ out-of-plane block against test 2's corpus-frame MP2/TZ rows rotated (≤ 1e-5 a.u.); the
CC/TZ CH-oop rms against Goodman reproduces TASKS 111's 19.10 cm⁻¹ (to 1e-6) before the step is read.

**Read.** `probes/anchor_oop_check.py qz`: test 2's family read of CC/TZ against CC/TZ + step; per out-of-plane mode (D6h a2u, b2g, e1g, e2u)
the harmonic ω of both against Goodman's estimated harmonics, and the CH-oop rms against Goodman with and without the step (descriptive).

**Line (CH-oop rms of CC/TZ against CC/TZ + step):** ≤ 3 cm⁻¹ *converged* at the target's scale; 3–10 *basis error* of that size in CH-oop;
> 10 *not the truth* out of plane.

**Prediction.** *Basis error* (3–10): one in two; the step raises the CH-oop frequencies (the small-basis arene artefact shrinks).

## What each outcome means

- (a) holds and (b) converged: the CH-oop anchors stand within ≈ 7–10 cm⁻¹ of CC/TZ and TZ is enough; TASKS 183 (2) is decided on that ground.
- (a) weaker or fails: the CH-oop anchors carry an error bar of that size; every CH-oop read against them is reported with it, and how the
  composites are built out of plane comes to the user (a CC/TZ out-of-plane block per anchor is ≈ 25 h of laptop per small molecule).
- (b) basis error or not the truth: the TZ tier is itself uncertain out of plane; an MP2 QZ step on the composites' out-of-plane block (cheap,
  MP2 only) is proposed to the user.
- Either way: a check on two molecules (a) and one (b); no tuning of anything on the anchors (the user's rule of 29 Oct).

## Run

`probes/anchor_oop_checks.sh probes/results_m1/anchor_oop_checks_2026-11-05` (run spec `anchor_oop_checks`, laptop WSL, (a) then (b)), smoked on
water first (`A_MOL=water B_MOL=water`, the same script).

## Correction (5 November 2026, 09:2x — before any number; the run is in its reference gradient)

Under (a) the computation says "the inline two-route check: benzene's 4 Oct settings". That is wrong in one point: benzene's 4 Oct run deferred
its kernel checks to a separate run (`--two-route-check separate`, reference 7,986 s; the (T) lambda check then took 10,085 s on 6 Oct). This run
makes them inline: the C kernels against pyscf's Python route on pyridine's reference gradient, before the first displaced gradient. Kept, since
it is the second route on this molecule itself (gate 1 checks the kernels on water only), at the price of hours of a silent phase once (the watch
sees no pyscf log growth there); the run's end moves to ≈ 7–8 Nov. Nothing else changes.

## Amendment (10 November 2026, 07:1x — before any (b) number; the user: 'Oké' on option 1)

(b)'s conventional MP2/cc-pVQZ gradient does not fit the laptop: on 10 Nov at 01:22 the cgroup killed it at 18.9 GB of anonymous memory in pyscf's
'mp2 rdm1 intermediates', with max_memory 10,000 MB, and WSL has 20 GB. (b) therefore takes the step by psi4's analytic DF-MP2 gradient at both
bases (`probes/dfmp2_rows.py`, the route adopted for the anchors' composite step on 20 Oct: water check W 4.9e-8 Eh/bohr; swap test max |Δω|
0.42 and 0.46 cm⁻¹; upstream psi4 tests dfmp2-grad1 and dfmp2-grad5), on the plan of the conventional TZ file already computed (plane frame,
displacements 2 and 20, step 0.005 bohr, frozen 6, spherical): DF-MP2/cc-pVTZ (cc-pvtz-jkfit / cc-pvtz-ri) and DF-MP2/cc-pVQZ (cc-pvqz-jkfit /
cc-pvqz-ri). The step is [DF-MP2/QZ − DF-MP2/TZ].

**The DF check, before the step is read.** CC/TZ with its out-of-plane block shifted by [DF-MP2/TZ − conventional MP2/TZ] against CC/TZ: max |Δω|
≤ 0.5 cm⁻¹ (the 20 Oct adopt line). Above it (b) is not read and that is reported. The plane-frame second route (the conventional MP2/TZ rows
against test 2's, ≤ 1e-5 a.u.) and the Goodman pin stay as registered; the read's lines and prediction do not change. Read:
`probes/anchor_oop_check.py qz <conventional TZ rows> <DF QZ rows> <planeframe> <out> --df-tz <DF TZ rows>`; run spec `anchor_oop_dfmp2`,
after the kernel check (it runs alone), with check W on water as its smoke.

## Amendment 2 (10 November 2026, 09:0x — before any (a) number; the user: 'Energieroute')

(a)'s second route on pyridine itself was the C kernels against pyscf's Python route on the reference gradient (the correction of 5 Nov). The
(T) lambda kernel passed on 10 Nov at 03:44 (max |kernel − pyscf| 2.3e-17, limit 1e-10). The (T) density check against pyscf's slow route does
not fit the laptop: the cgroup killed it four times, three times at 12,800 MB (5–6 Nov) and on 10 Nov at 08:25 at 18,500 MB (anon-rss 18.9 GB).
The density part is therefore replaced by the energy route of `probes/e8_cc_hessian_fd.py --two-route-check energy` (built 6 Oct 2026 for
benzene/cc-pVTZ, whose density check ran out of 20 GB): the stored reference gradient against central differences of the stored displaced
energies, coordinate by coordinate over the seven out-of-plane displacements, limit 2e-5 a.u. (`ENERGY_GRAD_LIMIT`). It checks the gradient
as a whole — lambda, density and contraction together — and needs no quantum chemistry. It writes `two_route_check.json` (route `energy_fd`),
which the read of (a) requires. Above the limit (a) is not read and that is reported. The read's lines and prediction do not change.
