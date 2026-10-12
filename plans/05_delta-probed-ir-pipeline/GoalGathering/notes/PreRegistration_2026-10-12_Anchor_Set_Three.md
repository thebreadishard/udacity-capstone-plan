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

## Outcome

*(appended after the reads)*
