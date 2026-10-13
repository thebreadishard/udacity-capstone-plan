# Pre-registration — anchor set three: more CC anchors as the lever (12 October 2026, before any of them is computed)

*The user, 12 Oct ≈ 23:0x, after lever 6b: 'Nee, laten we vol op 4 gaan. Meer ankers.' That means more anchors, rather than a structured
replacement of λ. The user created the CPX62 `ubuntu-32gb-hel1-4` (`anchors3` in tools/hosts.tsv). The anchor server was bootstrapped with
`probes/bootstrap_anchors_cpx62.sh`, and gate 1 passed there on both paths (RHF, UHF) in 43 s. Decisions in this note were taken alone on the
user's standing word of the same night ('zelfstandig beredeneerde beslissingen … succes van het project en code kwaliteit').*

## Why

T3 transfers the network's correction to CC level with six anchors. Lever 6b found three things:
- with the TZ standard (head tuned, λ = 1), the mode shapes of all three low-symmetry anchors give worse intensities than B3LYP's own Hessian;
- the error sits in the strongest out-of-plane pair, which is rotated inside itself (`probes/results_m1/cc_apt_field_2026-10-12/`);
- what the fine-tune does with the out-of-plane couplings is decided by one knob, because six anchors do not pin it down.

More anchors is the lever that constrains the couplings directly, instead of choosing a knob.

**The six-anchor baseline** (T3, 10 Oct, chain 34's three models, leave-one-anchor-out, mean over 6 anchors × 3 seeds,
`out/T3_tz_folds_c34_seed{0,1,2}_2026-10-10.log`):

| family | zero rule (cm⁻¹) | λ = 1, the standard | λ = 0 |
|---|---|---|---|
| ring-ip | 15.63 | 4.55 | 3.39 |
| CH-stretch | 35.08 | 2.55 | 4.94 |
| CH-oop | 15.01 | 14.05 | 10.65 |
| other | 16.45 | 13.52 | 10.01 |

So λ = 0 is better on three of four families in frequencies too; λ = 1 wins only on the C–H stretches. Recorded here before any new number.

## The anchors, in a fixed order

All are corpus layer-A molecules with B3LYP geometry and analytic labels (on the labels server). The criteria are:
- low symmetry, so that modes mix within symmetry blocks;
- aromatic, and relevant to the mandate: aza-PAHs, five- and seven-membered rings;
- no methyl rotor and no NH₂ inversion.

The number of symmetry-unique displacements comes from `probes/e8_symmetry.py`.

| wave | molecule | id | atoms | group | gradients for the FD Hessian |
|---|---|---|---|---|---|
| 1 | quinoxaline | A_7aa232d4e9 | 16 | C2v | 48 |
| 1 | azulene | A_d9139359ab | 18 | C2v | 66 |
| 1 | acenaphthylene | A_45187bb7c8 | 20 | C2v | 66 |
| 2 | quinoline | A_ff98e1160d | 17 | Cs | 102 |
| 2 | isoquinoline | A_d09f8d1ef8 | 17 | Cs | 102 |
| 3 | indole | A_76e053ce6a | 16 | Cs | 96 |
| 3 | benzofuran | A_fead28d796 | 15 | Cs | 90 |
| 3 | quinazoline | A_d295f2fa80 | 16 | Cs | 96 |

Wave 1 goes first: three C2v molecules, the cheapest in gradients, with a five-ring (acenaphthylene, the family that carries hold-out (b))
and a 5–7 ring (azulene). Within a wave the order is the table's.

## Per anchor, the pipeline

1. **CCSD(T)/cc-pVDZ FD Hessian.** `probes/e8_cc_hessian_fd.py` through `probes/run_anchors_hel23_parallel.sh` (parallel partial runs,
   assembling run). It carries:
   - the explicit (T) lambda and the C kernels (gate 1);
   - frozen core by the element rule;
   - the energy-route two-route check on the reference gradient;
   - the probe's own pair and symmetry checks.

   An IMAGINARY result is excluded, as before.
2. **CC APT by the field route** (`probes/cc_apt_field.py`, six gradients, F = 1e-3). Line: sum rule ≤ 1e-6 (`probes/cc_apt_field_check.py`).
3. **Composite TZ tier.**
   - The MP2/cc-pVTZ − MP2/cc-pVDZ basis step: `probes/cc_composite_full_check.py compute`, then `build`.
   - Promotion by chain 33c's rule: `probes/composite_promote.py promote`, VALID, and soft modes within 40 cm⁻¹ of ωB97X when the DZ anchor
     is imaginary.
   - Registered in the anchor registry (decision 62).

## Reads — lines fixed now

The final read comes after wave 3, or after the last wave that finishes if the budget stops the set early. That is declared before the read.
Waves 1 and 2 are read and reported without lines, so that no line is tested three times.

**R-A — do more anchors move T3?**
- The effect is isolated on the **original six anchors**: their leave-one-anchor-out errors with the fine-tune pool of 5 (as now) against
  5 + k (the new carried anchors added to every fold's pool).
- Same models, arguments and seeds as the 10 Oct run.
- Mean over the six anchors and three seeds, per family, the standard column (λ = 1) and λ = 0 both read.
- **Line on CH-oop, standard column:**
  - **≥ 20 % lower** with the new anchors → more anchors move T3 where it is weakest.
  - **< 5 % lower** → anchors are not the lever for the out-of-plane block; a structural change (block-wise treatment of the couplings) is
    registered next.
  - **Between** → noted.
- The same reading applies to 'other', reported without a line.

**R-B — do more anchors repair the mode shapes?**
- Matched intensity rel. rms with the CC APT on the three original low-symmetry anchors (pyridine, fluorobenzene, benzonitrile), with the
  enlarged pool, against the zero rule.
- **Line:**
  - λ = 1 below the zero rule on **at least 2 of 3** → anchors repair the shapes.
  - Otherwise the λ question stands: a chain to re-choose λ on frequencies and intensities together is registered.
- The new anchors' own intensity numbers are reported. Each is a held-out fold.

**R-C — the out-of-plane pairs.** Reported, no line. Per low-symmetry anchor, the strongest out-of-plane pair's rotation against the truth,
for the prediction and for the zero rule (`probes/l6_mode_shape_diagnosis.py` generalised).

## Cost and stop rules

- One CCSD(T) gradient of quinoline is being timed on `anchors3`: at 5 threads, as one of three parallel partial runs, and at 16 threads.
  The price per anchor follows from that number times the gradients above, and is recorded before wave 1 starts.
- The CPX62 costs €0.208 per hour.
- **Stop rule:** if wave 1's measured wall time exceeds twice its estimate, wave 2 does not start until it is re-priced.
- The CCX53 can take waves 2–3 after its labels (≈ 22–26 Oct) if one CPX62 is too slow; that needs the user's word.
- A server is deleted by the user after the full fetch.

## Price and launch (12 Oct 23:5x; before any anchor number)

**Measured on `anchors3`** (`probes/anchor_gradient_timing.py`, quinoline, 17 atoms, 175 basis functions, (T) C kernels). One CCSD(T)
gradient took:
- 2,318 s at 5 threads;
- 917 s at 16 threads;
- 8.6 GB peak memory either way.

Three partial runs of 5 threads would need about 26 GB on a 30 GB box. **Two partial runs of 8 threads** give about the same throughput
(≈ 4.6 gradients per hour) for 17 GB, and that is the setting.

**Estimates.** Gradients ÷ 4.6 per hour, scaled by (basis functions ÷ 175)⁵ for size, plus the reference gradient and the CC APT's six
gradients at 16 threads:

| molecule | estimate |
|---|---|
| quinoxaline | ≈ 13 h |
| azulene | ≈ 17 h |
| acenaphthylene | ≈ 40 h |
| **wave 1** | **≈ 70 h ≈ 2.9 days ≈ €15** |
| wave 2 | ≈ 50 h |
| wave 3 | ≈ 60 h |
| **all eight** | **≈ 7.5 days ≈ €38**, before the composite MP2 step |

The stop rule's threshold for wave 1 is therefore 140 h.

**A second route for every APT, free.** Since 3 Oct the FD run writes its own CC APT from the captured relaxed dipoles (`apt_ccsd_t.npz`).
`probes/anchor_wave.sh` compares the field route against it with F2's line, max |ΔP| ≤ 1e-3 e.

**The wave script's smoke on water** (on `anchors3`, its own log) passed every step:
- Hessian DONE, FD asymmetry 6e-13;
- field-route sum rule 1.5e-12;
- field against FD 1.6e-5 e.

**Wave 1 launched** 21:58 UTC (`/root/dpir/anchors.log`, markers `=== (AS3)`, followed by `probes/watch.sh` `check_anchors3`).

## Amendment (13 Oct 03:4x, before any anchor number)

**The two-route check of the reference gradient moves to the energy route.**
- Quinoxaline's reference ran pyscf's slow (T) route inline: 6 h on 3 of 16 cores, with the partial runs waiting behind it.
- The (T)-lambda kernel check had passed on quinoxaline itself (2.8e-17, 4,508 s); the density check would have taken ≈ 6 h more.
- The runner gains `TWO_ROUTE=energy`, the default in `probes/anchor_wave.sh`. The reference is marked unchecked; after the partial runs it
  is checked against central differences of the stored displaced energies (`e8_cc_hessian_fd.py --two-route-check energy`, the route of
  6 Oct for anthracene). The assembly refuses without that passing file.
- Water smoke on anchors3: 3.5e-6 a.u. against the 2e-5 limit, then the assembly and the APT.

**Restart.** The inline quinoxaline run was stopped before its reference was written; its logs are kept in
`results/quinoxaline_ccpvdz_inline_stopped/`. Wave 1b (`/root/dpir/wave1b.txt`: quinoxaline, azulene, acenaphthylene) runs in the energy mode.
Lost: ≈ 6 h of wall time on the first anchor; saved: ≈ 5 h on it and more on the larger two.

## Amendment (13 Oct 07:3x, before any anchor of set three is read): R-C as a tool, two arms for the final read

*On the user's word (13 Oct 07:1x: 'begin met 1 en 2'): (2) the R-C reading as a tool, (1) the arm for R-A's fail branch prepared before the read.*

**R-C, now code.** `m05/mode_blocks.py`:
- the pair is `oop_pair`: the out-of-plane mode with the largest truth intensity, and its nearest out-of-plane neighbour of the same symmetry
  species (characters from `probes/e8_symmetry.point_group_ops`);
- the angle is `pair_rotation`: the rotation that diagonalises the test Hessian's 2 × 2 block on the truth's two modes, signed on the truth's
  axes; beside it κ, the coupling in cm⁻¹ (tan 2θ = 2κ/Δω), and the share of the test's two matched modes inside the pair's plane.

A first rule ('the two strongest out-of-plane modes') picked fluorobenzene's 769/902 (gap 142 cm⁻¹, barely turned) instead of the 670/769
pair the diagnosis named. It was replaced before any set-three number. Mixing scales as κ/gap and only one species mixes, so the partner is
chosen by species and gap, from the truth alone.

**The baseline, exploratory** (`probes/oop_block_read.py` on the saved λ = 1 folds of 10 Oct → `probes/results_m1/oop_block_2026-10-13/`):

| anchor | pair (cm⁻¹) | θ zero rule | θ λ = 1 (seeds) | κ λ = 1 / zero (cm⁻¹) | captured |
|---|---|---|---|---|---|
| pyridine | 717.7 / 757.8 | −15.7° | −19.5 / −18.9 / −21.1° | +15.4 / +11.5 | 0.999 |
| fluorobenzene | 669.7 / 768.6 | −5.5° | −9.1 / −8.7 / −8.8° | +10.4 / +6.7 | 0.995 |
| benzonitrile | 682.9 / 770.9 | −10.7° | −15.4 / −14.0 / −14.0° | +19.1 / +13.3 | 0.984 |

On all three, λ = 1 turns the pair further in B3LYP's own direction: the network adds 4–6 cm⁻¹ of coupling. Pyridine reproduces the 12 Oct
diagnosis (≈ 16° → 19–20°).

**What the baseline says about the out-of-plane block** (same files; exploratory):
- **The couplings carry no position.** Remove every coupling that involves an out-of-plane mode:
  - the out-of-plane ω move by ≤ 0.8 cm⁻¹;
  - the matched heights return to the zero rule's: pyridine 0.310 → 0.262, fluorobenzene 0.172 → 0.107, benzonitrile 0.443 → 0.258.
- **The network's out-of-plane diagonal does not follow the truth.**
  - Measured as first-order shifts ΔH_kk/2ω_k per out-of-plane mode of B3LYP, predicted against true: slopes 0.03–0.19, benzonitrile −0.34 to
    −0.50; correlations −0.49 to 0.32.
  - The truth lowers most out-of-plane modes by 10–50 cm⁻¹. The prediction moves them by −11 to +5, apart from benzonitrile's lowest, which it
    raises.
- **The prediction breaks σ_h.** It couples in-plane and out-of-plane modes by up to 2.4 cm⁻¹, where the truth has ≤ 0.19. When the model
  below moved an out-of-plane mode next to an in-plane one, they mixed (benzonitrile's heights went to 0.64). Both arms therefore take every
  coupling that involves an out-of-plane mode from the low level, where σ_h makes the in-plane/out-of-plane ones zero. TASKS 52.
- **A three-number model of the out-of-plane shift**, a + b·ω/1000 + c·h (h the mode's mass-weighted share on hydrogen), fitted
  leave-one-anchor-out on the other five anchors' truth:
  - out-of-plane ω rms 13.3 / 9.8 / 15.5 / 10.3 / 7.0 / 13.5 cm⁻¹ against λ = 1's 19.6 / 19.7 / 11.0 / 10.1 / 24.6 / 21.9 (benzene,
    naphthalene, pyridine, fluorobenzene, benzonitrile, anthracene);
  - means 11.5 against 17.8; worse on pyridine.
  - Five forms were tried and this one is fixed here, so these numbers are not evidence for it.

**Two arms in the final read.**
- In the code: `m05/rungC_cc_transfer.py --oop-couplings-low --oop-diagonal-model`, with the columns `network_head_l2_ooplow`,
  `oop_model_only` and `network_head_l2_oopmodel` (and the λ = 0 twins).
- The model's three numbers are fitted per fold on the training anchors only.
- Tests: `tests/test_mode_blocks.py` and `tests/test_rungC_cc_transfer.py`; smoke on pyridine, fluorobenzene and benzonitrile with 2 epochs.
- The arms are judged **only on the new anchors' folds** of the final all-anchor run, each new anchor held out. The six original anchors' values
  are reported, not judged, because they shaped the design.
- 'CH-oop' and 'other' are the registered read's families. The intensity read uses each new anchor's CC APT, field route.

**Arm M** — the out-of-plane block from the model, the network's in-plane block. This is R-A's fail branch, prepared, and it is read whatever
R-A says. Means over the new carried anchors and the three seeds:
- **adopt** when all three hold:
  - CH-oop ω rms is ≥ 20 % below λ = 1's;
  - 'other' is ≤ 10 % above λ = 1's;
  - the matched intensity rel. rms is at or below λ = 1's on at least two thirds of the new anchors.

  The standard's out-of-plane block then becomes the model's, and the certificate says so.
- **fails out of sample** when CH-oop is < 5 % below λ = 1's;
- **between:** noted.

If R-B passes (the network's own shapes beat B3LYP's), arm M is not adopted as it stands, because it would throw those shapes away. A variant
with the model's diagonal and the network's couplings is registered then.

**Arm C** — the couplings that involve an out-of-plane mode come from the low level. This is R-B's fallback, read only when R-B fails and arm M
is not adopted. It is adopted when:
- its matched intensity rel. rms is below λ = 1's on at least two thirds of the new anchors; and
- its CH-oop ω rms is within 1.0 cm⁻¹ of λ = 1's.

## Outcome

*(appended after the reads)*
