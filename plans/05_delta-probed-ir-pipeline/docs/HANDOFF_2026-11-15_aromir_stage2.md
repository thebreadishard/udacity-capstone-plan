# Handoff — aromir, stage 2 (the network's code), 15 November 2026

Follows `HANDOFF_2026-11-15_aromir_stage1.md`. Written from the same cloud session; the laptop was not reachable. TASKS 73.

## What was added to `thebreadishard/aromir` (commit 27f0d3f, branch `main`)

`src/aromir/network/`: `graph` (bond graph, rings, atom and hinge classes), `primitives` (geomeTRIC's primitives, Wilson B, the
canonical angle choice, parities), `pattern` (the pair pattern and rung B's pair features), `inputs` (the tensors of one molecule),
`model` (the PaiNN-type encoder and the pair head), `weights` (safetensors with a JSON recipe that carries the tensor file's sha256),
`convert` (a trainer checkpoint to those files). 156 tests, 99.8 % branch coverage.

**No trained weights are in it**: v1.3's checkpoints are on the laptop only. The pipeline therefore does not call the network yet.

## Validation (number and counterpart)

`probes/aromir_network_golden.py` (this branch) runs this repository's own inference path — `rungC_infer.input_tensors_of` and
`delta_H` on `HybridDeltaFModel` — on seeded random models and RDKit geometries, with a seeded random symmetric matrix as the low-level
Hessian, and writes the pins aromir's tests read. Three configurations (the carried recipe's switches at a small size; canonical + cos;
the parity-odd factor with mean pooling and pattern d), eight molecules, 16 pins, torch 2.15.0:

- pattern pairs, pair classes, hinge classes and parities: identical in all 16;
- ΔH: at worst 2.7e-7 of its largest element (single precision); aromir's test bound is 1e-5.

Not validated here: the carried v1.3 weights themselves. That needs the three checkpoints.

## What the laptop has to do for 0.1

1. Convert the carried checkpoints (in an environment with aromir installed):
   `python -m aromir.network.convert modules/05_support_predictor/out/E7_rungC_chain35_analytic_model_n750_seed0.pt <folder> v1.3-seed0 --network-version 1.3`
   (and seeds 1, 2). The converter refuses a checkpoint it cannot run and says why.
2. On one corpus molecule, compare aromir's ΔH from the converted weights with `rungC_infer.delta_H` on the checkpoint — the same
   comparison as the pins, on the real model. Write the number down.
3. Compare one `geometry.json`'s `masses_amu` with `aromir.constants.ELEMENTS` (stage 1, finding 3).

## Findings

1. **The body needs as many vector as scalar channels.** `Interaction.forward` adds `asv * (Uv * Vv).sum(1)` — n_v wide — to the
   scalars, so `n_s != n_v` raises a shape error. Every model so far has 64 and 64; aromir makes it one setting, and its converter
   refuses a checkpoint where they differ. The trainer's constructor accepts both without a check.
2. **`_primitive_vector`'s `except Exception` around `p.value(xyz)` was not hit** on any of the eight molecules, the nitrile's linear
   angles included. aromir has no such fallback; a primitive whose value cannot be computed raises.
3. **Order invariance under canonical + cos holds only up to the canonical ranks' ties.** With a random matrix as the Hessian, a
   molecule with graph-equivalent atoms (toluene, biphenyl, 4-chlorophenol) gives a different ΔH for another atom order (up to the
   size of ΔH itself); 2-chlorophenol, whose graph has no symmetry, agrees to 6e-7. For a real Hessian the equivalent atoms are
   equivalent in the Hessian too, so this is the expected limit of the argument in `internal_coords.py`, not a defect — but it means
   v1.5's read (≤ 0.01 cm⁻¹ across orders) should include a molecule whose geometry is less symmetric than its bond graph (a
   twisted biphenyl, a methyl rotor), where the Hessian does not share the graph's symmetry exactly.

## Next stages, in order

1. The weights (above), then the network in the pipeline: `aromir spectrum` with the seed mean and each seed's range.
2. The family rule and the certificate, numbers read from the evaluation records.
3. The printed anharmonic position (`PreRegistration_2026-11-14_Printed_Band_Position.md`; TASKS 211, 219).
4. The low-mode repair in the label route (TASKS 216).
5. The model card and release 0.1.
