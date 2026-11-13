# VPT2's domain: which fundamentals our labels may state — 13 November 2026

Registered before the marks are used anywhere. It fixes two diagnostics and their thresholds, so that no later read can choose them
after seeing its own outcome. The code is `src/dpir/vpt2_domain.py`; the label writer `probes/gvpt2_labels.py` stores the result under
`vpt2_domain` in every label.

## 1. Why

VPT2 states a fundamental as the harmonic frequency plus a second-order correction. The correction is a measurement only while it stays
small against the frequency it corrects.

Coronene shows the failure. Its modes 24 (642.9 cm⁻¹) and 36 (807.1) are purely out of plane and in no degenerate pair. D6h forbids
φ_iii and almost every φ_iik for such a mode, so the cubic terms that normally cancel the quartic one are absent and the whole quartic
term lands on the fundamental: for mode 36, 2x_ii = 2·711.1/16 = +88.75 cm⁻¹ (the quartic constant to the second digit) beside +90.45
from its partners, of which +34.9 from mode 24 alone (x(24,36) = +69.8). The label reads +179.2 cm⁻¹, 22 % of ω.

This is neither a grid artefact nor a resonance. Two DFT grids give φ_iiii within 0.7 % (`mode_quartic_coronene_2026-11-13/scan.json`);
GVPT2 equals DVPT2 for both modes, the one near-resonant triple (ν36 ≈ ν24 + ν3, gap −3.58 cm⁻¹) has φ = 0 by symmetry, and no triple in
the whole force field has |φ| > 20 cm⁻¹ with a gap under 60.

What it costs: S3's 'other' family reads rms 41.18 cm⁻¹ against the 3.0 line, and the other 23 of its 25 modes give **3.84**. CH-oop's
two worst modes (823.1 and 780.4, errors −23.0 and −21.8) are the partners mode 36 couples to.

## 2. The diagnostics

Per mode i, each a ratio to that mode's own harmonic frequency:

| name | definition | threshold |
|---|---|---|
| strain | \|ν_i − ω_i\| / ω_i, on the fundamental the label states (after any variational resonance step) | > 0.10 |
| partner share | max_{j≠i} \|x_ij\| / ω_i, on the deperturbed anharmonicity matrix of the same VPT2 call | > 0.10 |

A frequency below 1.0 cm⁻¹ is not a denominator; such a mode is marked outright.

## 3. Why 0.10

From the labels in hand on 13 November 2026 — 2,028 modes in 36 force fields, measured on `nu_gvpt2` beside each force field's
`chi_sym`:

- the strain's median is 0.018 and its 99th percentile 0.052;
- the CH stretches, where a −170 cm⁻¹ correction is sound VPT2, sit at 0.054 to 0.056, and nothing else reaches 0.09;
- above that the distribution is empty until four modes at 0.166 (B_0603418c5b, 564.5 cm⁻¹), 0.193 and 0.222 (B_410ac0fb2f, 518.1 and
  593.7) and 0.388 (B_78f8233b4c, 509.4 cm⁻¹, a shift of −197.7).

0.10 therefore separates sound anharmonicity from breakdown with a wide margin on both sides. It marks 8 modes in 5 of those 36 force
fields, beside coronene's 24 (strain 0.103, partner share 0.109) and 36 (0.222, 0.086 — marked by the strain alone). The partner share
marks conservatively, on purpose: it catches a mode whose correction rests on one coupling even where the total stays small, and a
marked mode is not discarded but solved without perturbation theory (TASKS 209).

## 4. What a mark means

A marked mode is a measurement this method cannot make. Nothing is dropped and nothing is silently kept: the marks travel in the label,
and a reader that cannot treat a marked mode calls `require_unmarked`, which raises and names the modes. A reader that can treat them
says so in its own words. A label written before this check carries no `vpt2_domain` record, and `require_unmarked` refuses that too
rather than reading it as clean.

## 5. What is still open

φ_iiii(36) itself is not pinned: the displaced-Hessian QFF has 711.1 cm⁻¹ where the energy stencil at h = 0.5 has 456.6, 36 % apart.
The run `mode_quartic_steps_coronene` (h = 0.25, 0.5, 1.0 at route A's own grid) says whether the energy route is converged in the step.
If it is not, the quartic truncation itself is the limit and a sextic term along these modes is the next question, with a cost.
