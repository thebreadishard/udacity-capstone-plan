# Design note 2026-09-13 — M2: the frozen-space LNO-CCSD(T) gradient in JAX (what would have to be built, where the derivative goes, what it costs to build)

*Written on 13 September, before M2a has produced a number, so that the decision after M2a is between two costed options and not between a number and a blank page. Sources: plan 05's frozen-space engine (`probes/m1_frozen_spaces.py`: `transport`, `lno_classes`, arm A), the side-project note (`Side_Project_2026-09-04_ModeG_Gradients.md`, M2's correctness criteria), the item-33 reading note, and PySCFAD 0.3.3 as installed in `~/qcad` on 13 September (introspected, not run: `pyscfad.lno.lno_base.kernel_1frag`, `make_fpno1`, `pyscfad.lno.ccsd.impurity_solve`, `_checkpointed.make_mp2_rdm1_ie`). No number in this note is a measurement; the work estimates are estimates and say so.*

## 1. The object

Plan 05's anchor energy along a probed direction is the **frozen-space** local-CC energy (probe M1, arm A): the occupied LMOs and every fragment's local active space (LAS: fragment orbitals `orbfrag`, frozen list `frzfrag`) are computed once at the reference geometry x₀ and *transported* to a displaced geometry x by projection onto the span of the current occupied (or virtual) space followed by Löwdin orthonormalisation:

  V(x) = C_space(x) · [C_space(x)ᵀ S(x) C₀],  Ṽ(x) = Löwdin_{S(x)}(V(x))

(`transport` in `m1_frozen_spaces.py`). The energy E_A(x) = E_LNO-CCSD(T)(x; Ṽ(x)) is a smooth function of x because nothing discrete happens between x₀ and x: the selection is frozen, only the vectors follow the geometry. M1 measured that smoothness (σ 0.003–0.044 µE_h at benzene, tight and xtight). **M2 is the gradient of exactly this function**, ∂E_A/∂x, by reverse-mode AD, with the projection inside the graph.

## 2. What PySCFAD already differentiates, and what it does differently

PySCFAD's `LNOCCSD_T` builds each fragment's space at the *current* geometry (`make_fpno1`: fragment-projected occupied/virtual spaces by `projection_construction`, semicanonicalisation, an MP2 one-particle density in the fragment (`_checkpointed.make_mp2_rdm1_ie`, under `jax.checkpoint`), its eigenvectors as PNOs, a threshold cut). The linear algebra is traced (`jnp`), so the *vectors* are differentiated; the *selection* (which PNOs pass `thresh_occ`/`thresh_vir`, the `lovir` test) is under `stop_grad` and is discrete. That is precisely the source of the discontinuities and the benzene symmetry-breaking outlier the paper reports: between two geometries the selection can change; at one geometry the gradient is that of a function whose selection is held fixed — which is, locally, a frozen-space gradient of *their* space. Plan 05's arm A makes that local statement global along the probed path: one selection, one set of reference vectors, transported.

So M2 is not "add AD to plan 05's engine" (pyscf-forge's LNO is NumPy, not traceable) and not "use PySCFAD as is" (its spaces are rebuilt per geometry). It is: **PySCFAD's differentiable LNO machinery with plan 05's frozen, transported spaces substituted for the per-geometry construction.**

## 3. The build, in pieces

| piece | what | depends on | estimate |
|---|---|---|---|
| A. reference spaces from plan 05's engine | run plan 05's `Recording` arm once at x₀ (pyscf-forge, `qc05`): store `lo0` (PM LMOs), and per fragment `orbfrag0`, `frzfrag0`, the active-occupied slice — the same objects `frozen_spaces_reference.npz` already holds for M1 | exists (M1's stage 0) | 0 (reuse); a loader: hours |
| B. transported spaces in JAX | `transport(C0, C_space(x), S(x))` rewritten with `jnp`: projection, Löwdin (an `eigh` of the small overlap — differentiable; guard against degenerate overlaps the way M1's `offdiag_max` diagnostic does) | A | a day |
| C. a `FrozenLNOCCSD_T` in PySCFAD | subclass of `pyscfad.lno.LNOCCSD_T` whose fragment loop skips `make_fpno1` and feeds `impurity_solve(mf, orbfrag_x, orbfragloc_x, frozen=frzfrag0, ccsd_t=True)` the transported `orbfrag_x` and the transported LMOs; the occupied LMOs come from B applied to `lo0`, the fragment spaces from B applied to `orbfrag0` within the current occupied/virtual spans | B; PySCFAD's `impurity_solve` (traced CCSD(T) with `_checkpointed` recomputation) | 2–4 days, most of it in matching PySCFAD's conventions (frozen-core mask, DF integrals `_make_df_eris_incore`, semicanonical energies inside the fragment) |
| D. the energy check | E_A(x) from C against plan 05's arm A at the same x, same basis, same thresholds, same reference spaces: agreement to the level of the two engines' DF and convergence settings (target ≤ 10⁻⁷ E_h; the gap between engines is itself printed) | C, plan 05's stored M1 points | a day |
| E. the gradient and M2's correctness criterion | `jax.grad` of D's energy w.r.t. the traced coordinates; against central finite differences of the **re-projected** frozen-space energy (M2's pre-registered test: component-wise, 6N = 72 re-projected energies at benzene, max deviation ≤ 10⁻⁵ E_h/bohr); the projection term measured by repeating with the transport under `stop_grad` | C, D | 2 days of compute-and-compare (the 72 energies are cc-pVDZ arm-A points, minutes each in `qc05`) |
| F. the frozen-space g | M2a's protocol (§1 of the pre-registration) applied to C: the number the ladder wants, on plan 05's own object | E | an evening |
| G. memory and cc-pVTZ | the backward pass of CCSD(T) stores or recomputes the amplitudes; PySCFAD's `jax.checkpoint` trades memory for time; at cc-pVTZ the anchor's basis, whether it fits 25 GB decides laptop vs desktop/cluster | F | unknown until F; the P13 memo's question |

Total: **two to three working weeks** for A–F if PySCFAD's conventions cooperate, more if `impurity_solve` needs changes for transported (non-semicanonical) fragment spaces — the semicanonicalisation inside the fragment is a differentiable `eigh` and can be redone on the transported space, so this is expected to be a convention, not a wall. The estimate is the author's; nothing has been timed.

## 4. Where `stop_gradient` goes, and where it must not

- **Must be in the graph:** the transport (B). The gradient plan 05 needs is of E_A(x) as defined — the vectors move with x. Leaving the projection outside the graph gives the derivative of an energy whose spaces do not follow the geometry: a different, wrong function.
- **Diagnostic only (M2's "projection term measured"):** the same gradient with B under `stop_grad`; the difference between the two gradients is the projection term, printed per component. The side-project note asked for this on 4 September; it costs one extra gradient.
- **Discrete and therefore outside:** `frzfrag0`, the active-occupied slice, the fragment assignment — frozen by construction, no derivative exists or is wanted.
- **Never:** the threshold tests of `make_fpno1` — they are not called at all in the frozen arm.

## 5. What could make this fail, stated now

1. PySCFAD's fragment solver assumes semicanonical fragment orbitals built its own way; transported vectors may need a re-semicanonicalisation step that changes the fragment energy's definition slightly against plan 05's engine — then D's agreement is not 10⁻⁷ but a printed, understood offset, and the *gradient* is still of the right function. Acceptable if printed.
2. Löwdin on a near-degenerate overlap: the derivative of `eigh` blows up when singular values of the transport overlap cluster; M1's diagnostic (`sv_occ`, `offdiag_max`) shows how close the benzene points come. A symmetric-orthogonalisation via Cholesky (also differentiable, no degeneracy issue) is the fallback.
3. Memory at cc-pVTZ (G). If the backward pass does not fit, M2's number is measured at cc-pVDZ and the TZ gradient becomes a desktop/cluster job — a P13 fact, not a defeat.
4. g itself (M2a) above 26 at R1 size (X14's bar): then M2 is not built; this note is filed as the record of what it would have been.

## 6. The decision after M2a, pre-stated

- M2a cell 3 gives **g ≤ 20** → build A–F (this note is the plan); the user decides the calendar.
- **20 < g ≤ 26** → build only if X14's row (a) is the route (symmetry prior, 18 gradients at R1); marginal; the user decides with the P13 memo in hand.
- **g > 26** → do not build; record; the cost branch of plan 06 rests on P25 and the machine.

Nothing here changes the Ladder, the Budget or the side-project note's milestones; it details M2 and adds the M2a → M2 decision rule. Software ledger: no row until code exists.
