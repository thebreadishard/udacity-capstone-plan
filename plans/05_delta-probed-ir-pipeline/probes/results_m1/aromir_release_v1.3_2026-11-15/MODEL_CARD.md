---
license: cc-by-4.0
library_name: aromir
tags:
  - chemistry
  - infrared-spectroscopy
  - hessian
  - equivariant
model_name: aromir ΔH network v1.3
---

# aromir ΔH network v1.3

A correction to the Hessian of an aromatic molecule. The network reads a cheap B3LYP/6-31G* Hessian and returns ΔH, the difference to ωB97X/6-31G* (the DFT proxy: the network's ΔH is trained on ωB97X − B3LYP Hessians). The corrected Hessian gives harmonic infrared band positions closer to that level at the cost of the cheap one.

- **Seeds:** 3 (0, 1, 2); the applied correction is their mean, and their spread is reported per band.
- **Licensed families:** ring-ip, CH-stretch, CH-oop.
- **Not licensed:** other.
- **Use it through:** [aromir](https://github.com/thebreadishard/aromir), which builds the inputs, applies the correction and writes a certificate for every band.

## How well it is known

The rms error of the corrected band positions against ωB97X/6-31G*, in cm⁻¹, on molecules the network never trained on. The seed mean, with each seed's value in brackets.

| family | (a), 8 molecules | (b), 39 molecules | licensed |
|---|---|---|---|
| ring-ip | 1.77 (1.95, 1.68, 1.70) | 2.12 (2.25, 2.02, 2.11) | yes |
| CH-stretch | 1.19 (0.91, 1.74, 0.91) | 2.50 (1.91, 3.51, 2.08) | yes |
| CH-oop | 2.17 (2.47, 2.06, 1.99) | 2.70 (2.44, 2.95, 2.72) | yes |
| other | 3.62 (4.09, 3.27, 3.51) | 3.89 (3.65, 4.51, 3.52) | no |

- (a): eight molecules set aside on 19 September 2026, before any network was trained, and never trained on in any form (two more molecules of that set, 2-naphthoic acid and benzonitrile, are left out of this read because the network had trained on them under another identifier)
- (b): every substituted molecule of two ring scaffolds, set aside on 8 October 2026; the network trained on no molecule of either scaffold

A family is licensed when its seed-mean error is within 3 cm⁻¹ on every hold-out. aromir's certificate marks each band with its family, that family's error and whether it is licensed.

Coupled cluster: not measured for this network version.

Sources: E7_rungC_chain35_analytic_eval_frozenb_seed0.json; E7_rungC_chain35_analytic_eval_frozenb_seed1.json; E7_rungC_chain35_analytic_eval_frozenb_seed2.json; E7_rungC_chain35_analytic_a8read_seed0.json; E7_rungC_chain35_analytic_a8read_seed1.json; E7_rungC_chain35_analytic_a8read_seed2.json.

## What it was trained on

- 749 molecules, neutral and closed-shell, each with an aromatic ring.
- Elements: C, Cl, F, H, N, O, S.
- Sizes: 8 to 30 atoms.
- Held out and never trained on: 39 in (b); 8 in (a), not counting 2 the network also trained on.
- The training Hessians were used as pyscf's analytic Hessians, without the soft-mode repair; aromir prepares a molecule's Hessian the same way before the network reads it.

## Where it stops being known

- **The level is ωB97X/6-31G*.** The errors above are against that level, not against experiment.
- **Positions are harmonic.** No anharmonic shift is applied.
- **Neutral, closed-shell, aromatic molecules only**, of the elements C, Cl, F, H, N, O, S. aromir refuses anything else before computing.
- **Sizes outside 8 to 30 atoms are extrapolation.** aromir computes them and marks the certificate.
- **Not licensed: other.** Bands of an unlicensed family are printed with their measured error and marked.
- **The answer depends on how the molecule's atoms are numbered**: the internal coordinates are chosen by atom number, and a dihedral near ±180° enters by its raw value. aromir therefore puts every input, SMILES or xyz, into one canonical atom order first. Do not feed the network a molecule in another order. Measured: band positions move by up to 10.73 cm⁻¹ between atom orders (3 molecules, 5 orders each; order_spread_smiles.json).
- **Band heights are the cheap level's.** The dipole derivatives are not corrected.

## What it is

An equivariant message-passing encoder (PaiNN type) over the atoms, and a head that predicts one number per pair of internal coordinates: an entry of ΔF. The Cartesian correction is ΔH = Bᵀ ΔF B with B the Wilson matrix, so it is symmetric, free of translations and rotations, and turns with the molecule by construction.

- Encoder: 3 blocks, 64 scalar and 64 vector channels, sum pooling.
- Head: hidden width 256, with the pair features, a learned share of the low level's own force constant.
- Pair pattern f; primitives by the geometric angle choice, dihedrals raw.
- 292,546 parameters per seed.

## Files

| file | seed | sha256 |
|---|---|---|
| seed-0.safetensors | 0 | `bc1bbd91fc80068ac4fa16b6aeb9fcaa34429ca2f09a5c0284c924bfb3907094` |
| seed-1.safetensors | 1 | `96a15a89b6ac129c527fa643de07f51c7bf075b8de05a7898b9b9382dba2958e` |
| seed-2.safetensors | 2 | `4a3fda6248785ee6dc198095342ebb19cc66bb47c40823834c9ba9f4ff6a91d8` |

Each `seed-<n>.json` beside its tensors holds the recipe and that sha256; `evaluation.json` and `training.json` hold the records this card is written from.

## Use

```console
$ pip install git+https://github.com/thebreadishard/aromir
$ aromir spectrum "c1ccc2ccccc2c1" --out results/naphthalene --release <this folder>
```

## Licence

Weights and records: CC BY 4.0. Code: MIT, at https://github.com/thebreadishard/aromir.

This card was written by `aromir card` from release v1.3's own files.
