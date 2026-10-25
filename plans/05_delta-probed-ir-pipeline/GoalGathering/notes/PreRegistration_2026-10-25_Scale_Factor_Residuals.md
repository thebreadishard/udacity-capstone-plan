# Pre-registration: what a scale factor leaves, per mode family (TASKS 112 and 111)

Written 25 Oct 2026, before any of the numbers below were computed (the user, the same evening: "begin met 112, 111 en 74 … maak zelfstandig
beslissingen"). The scripts named here are written after this note and committed with it or after it; their outputs are read only after
this note is in git.

## Why

The project replaces the empirical scale factor with a learned correction of the Hessian (memory rule: the scale factor is only ever the
baseline, never an option). Two numbers make that case concrete: how much a scale factor leaves per mode family on the task the network
learns, and how the scaled spectra of the largest recent library (Mai, Lu & Wang 2026: 144,111 spectra on B3LYP/4-31G with the PAHdb
factors 0.960 above 2500 cm⁻¹, 0.952 for 1111–2500 cm⁻¹ and 0.956 below 1111 cm⁻¹) compare with experiment, mode by mode, where we also have
coupled-cluster anchors.

## Reading 1 (TASKS 112): the scale factor on the proxy task, against the carried network

**Task.** The proxy task of the capstone (decision 63): from the B3LYP/6-31G* Hessian to the ωB97X/6-31G* one. The quantity is the one the
carried network is read on: per mode i of the B3LYP Hessian, the first-order frequency shift K_ii (cm⁻¹; `e7_t2_sqm` / `E6.readout`'s
`diag_rms`), split by the four families of `learning_curve_layerA.molecule_features` (CH-stretch, CH-oop, ring-ip, other).

**Data.** The corpus exactly as the network's evaluation loads it: `rungC_train.load_corpus(molecules, use_analytic=True)` (analytic
second-route Hessians where both exist, molecules with an imaginary mode dropped), with E6's hold-outs (a) and (b) and its pool.

**Baselines.** A scale factor predicts K_ii = (f − 1) ω_i, with ω_i the B3LYP harmonic frequency of mode i. The factors are fitted once, by
least squares of K_ii on (f − 1) ω_i over every mode of every pool molecule — generous to the baseline, which sees more molecules than any
single network training:
- S1: one factor for all modes;
- S3: three factors on the PAHdb regions (above 2500, 1111–2500, below 1111 cm⁻¹ of ω_i);
- SF: one factor per family — the best any family-aware scaling could do.
The prediction enters `E6.readout` as a diagonal matrix, so its `diag_rms` is computed by the same code as the network's.

**Network.** The carried model (chain 34, v1.1, decision 57): the seed mean of `diag_rms` per family in its three evaluation records
`out/E7_rungC_chain34_eval_analytic_2026-10-05_seed{0,1,2}.json`. The baselines are read on the molecules of those records (their
`per_molecule` ids); if the current loader's hold-out differs, the difference is reported and the records' ids are used.

**Lines (pass or fail as written):**
- L1. On hold-out (a), the network's `diag_rms` is below S3's in each of the four families.
- L2. On hold-out (a), the network's `diag_rms` is below SF's in each of the four families.
- L3. On hold-out (b), the network's `diag_rms` is below S3's in each of the four families.

**Reported without a line:** the fitted factors; S1; the share of S3's residual the network removes per family, 1 − network / S3; the same
on (b).

**What this reading is not.** It is the proxy task, B3LYP → ωB97X at one basis. A scale factor's real use is B3LYP → experimental
fundamentals, where it also absorbs anharmonicity; that is reading 3.

## Reading 2 (TASKS 112): Mai 2026's teacher on our molecules

**Match.** Our neutral corpus molecules made of C and H with both analytic labels, against Mai's `charge_0` entries: the same formula and
the same connectivity (RDKit bonds determined from each xyz, canonical SMILES compared). Their data stay outside git and capstone-data
(CC BY-NC-SA 4.0); only our statistics are written.

**Pairing.** Their 3N − 6 frequencies (scaled and unscaled = scaled / factor) with our B3LYP/6-31G* analytic frequencies by sorted order
(the same functional; a pair more than 50 cm⁻¹ apart is counted and reported, not dropped). Each of their modes takes the family of our
paired mode.

**Reported (descriptive, no line):** the number matched; per family the RMS of (their unscaled − our B3LYP/6-31G*), i.e. what their basis
(4-31G) and their learned potential add, and of (their scaled − our B3LYP/6-31G* scaled with the same three factors).

## Reading 3 (TASKS 111): benzene and naphthalene, mode by mode

**Experiment.** Benzene: the fundamentals and the harmonic frequencies derived from experiment in
`probes/data/benzene_benchmark_goodman1991_miani2000.json` (Goodman et al. 1991; Miani et al. 2000), as mapped to Wilson modes in
`probes/results_vpt2/benzene_benchmark_2026-09-22_harmonic_refs.json`. Naphthalene: the 48 fundamentals with D2h labels of Martin,
El-Yazal & François, J. Phys. Chem. 100, 15358 (1996), as listed by NIST CCCBDB (exp2x.asp?casno=91203, read 25 Oct 2026), stored with that
source in `probes/data/naphthalene_fundamentals_martin1996.json`.

**Our levels.** The carried coupled-cluster anchors (`m05/anchor_registry.py`): benzene CCSD(T)/cc-pVTZ, naphthalene CCSD(T)/cc-pVDZ +
[MP2/cc-pVTZ − MP2/cc-pVDZ]; and our analytic B3LYP/6-31G* of the corpus folders A_8448043181 and A_01f3186607.

**Mode identity.** Irreducible representations from the mode vectors: benzene D6h with `dryrun_symmetry_prior.assign_irreps`, naphthalene
D2h from the characters under the operations of `e8_symmetry.point_group_ops`. Martin's axis convention is fixed from the structure alone:
x normal to the plane (their in-plane gerade species are Ag and B3g), and z the in-plane axis whose C2 leaves the three-mode out-of-plane
gerade set symmetric (their B1g has three modes, B2g four). Within an irrep, computed and experimental modes are paired by frequency order;
pairs whose neighbours in the irrep lie within 15 cm⁻¹ in either list are flagged as possible crossings. Mai's modes, which have no vectors,
take the irrep of our B3LYP/6-31G* mode paired by sorted order (as in reading 2). Families are those of our B3LYP mode of the same irrep and
rank.

**Reported (descriptive, no line):** per molecule, per mode and per family: their scaled frequency − experimental fundamental; our CC
harmonic − experimental fundamental (positive by the anharmonicity, which our pipeline adds separately); for benzene, our CC harmonic −
the harmonic frequency derived from experiment (Miani's ω_exp), the like-for-like test of the anchor; and our B3LYP/6-31G* scaled with
the same three factors − experimental fundamental, to separate their factor from their basis and learned potential.

## Use

The three readings go into the proposal's motivation and paper D's introduction with these numbers and their caveats, and into a lay-level
blog draft (publishing is the user's word). A failed line is reported as failed; nothing here is re-run with other settings after reading.
