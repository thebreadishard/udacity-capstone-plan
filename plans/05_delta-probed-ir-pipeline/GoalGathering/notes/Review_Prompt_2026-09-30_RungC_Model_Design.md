# Review prompt — the Δ-Hessian model design (rung B pair model and rung C equivariant model), 30 September 2026

*For an external reviewer (a strong LLM or a person). Written by the student's assistant on the student's request; the repository is public. Paste
everything below the line.*

---

You are reviewing the machine-learning design of a small research project and are asked for concrete, prioritised improvements that can be tested on
a 16-core CPU laptop within hours each. Be direct; a ranked list of changes with the expected effect and a cheap test for each is worth more than a
survey. Point out red flags in the code where you see them. Everything you need is in one public repository:

`https://github.com/thebreadishard/udacity-capstone-plan` (branch `master`), directory `plans/05_delta-probed-ir-pipeline/`. Paths below are relative
to that directory; raw files are at `https://raw.githubusercontent.com/thebreadishard/udacity-capstone-plan/master/plans/05_delta-probed-ir-pipeline/<path>`.

## 1. The task

Predict the **correction to a cheap DFT Hessian** of an aromatic molecule: ΔH = H_high − H_B3LYP (Cartesian, 3N × 3N), from the B3LYP geometry and the
B3LYP Hessian. Today's labels use ωB97X as the "high" level (a proxy, ≈ 800 molecules); the real target is the CCSD(T) correction, for which a few
"anchor" molecules exist (benzene at CCSD(T)/cc-pVDZ, more to come) and which will be learned by transfer from the proxy. The quantity that matters
downstream is the harmonic spectrum of large polycyclic aromatic hydrocarbons (PAHs): band positions to ≈ 1–3 cm⁻¹, which is why off-diagonal
force constants (couplings between ring coordinates) matter as much as the diagonal.

Corpus (`modules/05_support_predictor/corpus/README.md`, `manifest.csv`): layer A = 46 bare PAH parents (benzene … five rings), layer A2 = 199 substituted
PAHs, layer B = 559 smaller, mostly heteroaromatic and substituted rings (median 18 atoms, 80 % with N/O/S in a ring). B3LYP/6-31G* geometries and
Hessians, ωB97X/6-31G* Hessians at the same geometry (psi4, finite differences of analytic gradients; for 27 molecules pyscf analytic Hessians replace
noisy files). Also available for pretraining: Hessian-QM9 (≈ 41 k DFT Hessians of small molecules, H/C/N/O/F).

## 2. The two models

**Rung B — pair model** (`modules/05_support_predictor/m05/e7_rungB_pairs.py`, 431 lines). ΔH is transformed to redundant internal coordinates (geomeTRIC
primitives: bonds, angles, dihedrals), ΔF = B⁺ᵀ ΔH B⁺ (minimum norm), and only a pattern of elements is learned: the diagonal, pairs of primitives
sharing an atom, and bond–bond pairs inside a ring. Each element is one training row with 66 hand-made features (primitive class, elements, ring
flags, the B3LYP force constant F_low of the same element and of the two diagonals, environment classes of the atoms, ring-path distance…). Model B1:
MLP 66 → 128 → 128 → 1 (GELU, AdamW, targets standardised per pair class, three seeds); B2: gradient-boosted trees as a non-neural control. Prediction:
ΔF_pred → ΔH_pred = Bᵀ ΔF_pred B.

**Rung C — equivariant model** (`modules/05_support_predictor/m05/rungC_equivariant.py`, 319 lines; training driver `rungC_train.py`; pretraining on
Hessian-QM9 `rungC_pretrain.py`; a pre-run "design check" `design_check.py`). Own PyTorch code, no library. Inputs: atomic numbers, coordinates, and the
B3LYP Hessian **as pair scalars only** — per atom pair the three invariants of its 3 × 3 block (trace, r̂ᵀ B r̂, ‖B‖_F), per atom the trace and norm of its
diagonal block. Body: three PaiNN-type interaction blocks, 64 scalar + 64 vector channels, 20 Gaussians, cosine cutoff 5 Å, no cross products (so
O(3)- and permutation-equivariant by construction); messages pooled by mean (a "sum" variant exists). Head: per atom pair within the cutoff
ΔH_ij = a_ij I + b_ij r̂_ij r̂_ijᵀ + Σ_k c_ij^k (u_i^k u_j^kᵀ + u_j^k u_i^kᵀ), with a, b, c invariant read-outs of symmetric pair features and u a linear
map of the vector channels to 16 tensor channels; ΔH_ii = −Σ_j ΔH_ij (translational invariance); each off-diagonal block is constrained symmetric.
Loss: mass-weighted MSE on the Cartesian ΔH + 0.1–1.0 × MSE on the internal ΔF (so the read-out quantity is trained directly). 171,554 parameters.
Recipe after a registered search (learning rate, epochs, loss weight, capacity): lr 1e-3, 200 epochs with early stopping (patience 20, inner
validation 15 %), aux weight 1.0.

## 3. Read-outs and hold-outs (fixed before any run)

Pre-registrations: `GoalGathering/notes/PreRegistration_2026-09-23_E7_Couplings_in_Local_Coordinates.md` (rung B),
`GoalGathering/notes/PreRegistration_2026-09-25_RungC_Equivariant_vs_Pair_Model.md` (rung C, with the search and all outcomes as dated sections),
`GoalGathering/notes/PreRegistration_2026-09-25_Proof_of_Learning_Layer_B.md` (the data-growth curve).

Hold-outs: (a) bare PAH parents never in training (10 or 43 molecules depending on the split), (b) 39 molecules with two ring scaffolds
(fluoranthene, fluorene) never in training, (c) molecules larger than the largest training molecule. Read-outs on a hold-out: the **ring coupling
ratio** = RMS of the remaining error on the ring–ring coupling constants after adding ΔH_pred, divided by the same RMS with ΔH_pred = 0 (1.0 = nothing
learned, 0 = perfect); and the **corrected-frequency RMS** in cm⁻¹ after diagonalising H_B3LYP + ΔH_pred against H_high (the "zero rule" baseline is
≈ 23 cm⁻¹).

## 4. What has been measured (all numbers in the pre-registration outcome sections and `modules/05_support_predictor/out/*.md`)

| model | training pool | (a) ratio / ω cm⁻¹ | (b) ratio / ω cm⁻¹ | record |
|---|---|---|---|---|
| rung B pair MLP | 175 (A + A2) | 0.43 / 4.7 | 0.47 / 5.2 | `out/E7_rungB_A2B_point0_2026-09-27.md` |
| rung B pair MLP | 750 (A + A2 + B) | 0.42 / 4.8 | 0.45 / 4.7 | `out/E7_rungB_A2B_2026-09-30.md` |
| rung B pair MLP, layer B alone | 274 → 574 | 0.61 → 0.63 / 6.2 → 6.1 | 0.64 → 0.70 / 5.6 → 5.3 | `out/E7_rungB_layerB_2026-09-30.md` |
| rung C, from scratch, fixed recipe (60 epochs) | 175 | ≈ 0.98 / ≈ 11 | ≈ 0.98 / ≈ 11 | `out/E7_rungC_2026-09-27.md` |
| rung C after the search (lr, epochs, aux weight) | 175 | 0.81 / 9.4 | 0.84 / 8.5 | `out/E7_rungC_s2_lr1e-3_e200_2026-09-27.md` |
| rung C + Hessian-QM9 pretraining (element rows reset) | 175 | 0.81 / 9.6 | 0.84 / 8.9 | `out/E7_rungC_C2sum_elemreset_2026-09-28.md` |
| rung C curve 45 → 100 → 175 | | falling ≈ 0.06 per doubling | | `out/E7_rungC_2026-09-27.md` |

So: the simple pair model on hand-made internal-coordinate features beats the equivariant model by a factor two on the couplings, and is **flat** with
4.3× more data; the equivariant model is worse but was still improving with data at 175. Tonight's run (`probes/rungC_scale_0930.sh`) trains rung C at 449
and 750 molecules with and without QM9 pretraining; its outcome will be appended to the rung-C pre-registration.

Two facts that may matter for your diagnosis: (i) the pair model sees the low-level force constant F_low of the very element it corrects, the
equivariant model sees only three invariants per block; (ii) QM9 pretraining moved the equivariant model by 0.00–0.03 — two incidents on the way
(a pretraining input channel that was zero at fine-tune time; sum-pooled bodies exploding on denser fused rings; untrained element rows for S/Cl) are
documented in the pre-registration and fixed.

## 5. Constraints

CPU only (a 16-core laptop; a workstation with 16 cores / 128 GB may follow if the data-scaling test tonight says data helps); runs of hours, not days;
own code preferred over heavy new dependencies (the project's rule: use existing software where it meets the requirement, otherwise write and test our
own); every change is pre-registered with a prediction and a pass line before it runs; three seeds; the read-outs above are fixed.

## 6. What we ask

1. **Diagnosis.** Why does an equivariant model with the full geometry lose to an MLP on internal-coordinate pair features by 2× on the couplings? Is
   the input representation (invariants only) throwing away what the pair model uses? Is the head (a I + b r̂r̂ᵀ + Σ c u uᵀ, symmetric blocks) too
   restrictive for coupling blocks? Is the loss (Cartesian mass-weighted MSE + internal ΔF term) pointed at the right quantity?
2. **Ranked improvements** for rung C, each with: the change, why it should help, the expected size of the effect on the ring coupling ratio, and a
   cheap test (hours on CPU). Candidates we have thought of and want your judgement on: feeding the low-level Hessian blocks as rank-2 equivariant
   features (Cartesian tensor channels) instead of invariants; predicting ΔF in internal coordinates with an equivariant encoder (a hybrid of the two
   rungs); a per-pair-class target normalisation as in rung B; a larger head (more tensor channels) versus a larger body; edge features from the
   bonding topology; pretraining on the *low-level* Hessians of the same corpus (self-supervised) instead of QM9; predicting the full H_high and
   subtracting; curriculum by molecule size.
3. **Data.** Given that more mixed heteroaromatic molecules (layer B) did not help the PAH hold-outs at all, what data would (composition, size,
   count), and how would you test that cheaply before computing it?
4. **Comparison with the literature.** What do the closest published models (Hessian prediction with MACE/NequIP/Allegro-type networks, learned SQM
   scaling, Δ-learning on force constants, Hessian-QM9 baselines) do differently that we should copy, and what of ours is fine as it is?
5. **Code review.** Anything in `rungC_equivariant.py` / `rungC_train.py` that could silently break equivariance, leak hold-out information, mis-weight
   the loss, or bias the read-out. The unit tests are in `tests/test_rungC_*.py`.

Please answer in English, be specific (file, function, formula), and separate "certain" from "worth trying". We will pre-register the changes you rank
highest and report the outcomes.
