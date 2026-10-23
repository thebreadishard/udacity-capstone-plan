# Design note, 23 October 2026 — a UHF CCSD(T) gradient that fits in memory (TASKS 98)

*Desk work beside the cation run (the user, 23 Oct: 'Oké' to designing TASKS 98). Why: the anchor cover's 25 cation anchors (2,055 of its 7,045
CPX62 hours) cannot run, because pyscf's open-shell CCSD(T) gradient forms whole tensors no machine holds
(`Compute_Plan_2026-10-23_Remaining_DFT_CC.md` §4). This note reads the code, sizes the problem, and designs the fix on the pattern of our RHF
kernels (`Design_Note_2026-09-29_T_Density_C_Kernel.md`). Nothing is built; building waits for the user.*

## 1. What the open-shell gradient does (read 23 Oct, pyscf master 143946e35)

`pyscf.grad.uccsd_t` runs, after the UCCSD amplitudes and the explicit (T) lambda (`e8_cc_hessian_fd.py`, with our `install_uccsd_t_dvvvv_fix()`
for pyscf#3305/#3387 on 2.14.0):

| step | code | what it forms whole | size |
|---|---|---|---|
| (T) lambda | `cc/uccsd_t_lambda.py` `make_intermediates` | `w`, `v`, `d3`, `rw`, `wvd` as `ijkabc` arrays, four spin cases (aaa, bbb, baa, bba) | o³v³ each |
| (T) one-particle density | `cc/uccsd_t_rdm.py` `_gamma1_intermediates` | the same five arrays per spin case | o³v³ each |
| (T) two-particle density | `cc/uccsd_t_rdm.py` `_gamma2_intermediates` | the same five arrays per spin case | o³v³ each |
| UCCSD two-particle density | `cc/uccsd_rdm.py` `_gamma2_intermediates` (the UHF `_gamma2_outcore` of `uccsd_t_rdm` only calls it) | `gvvvv`, `gvVvV`, `gVVVV` from `einsum('ijab,ijcd->abcd')`, then `dvvvv`, `dvvVV`, `dVVVV` and their transposes | v⁴ each |

The RHF path has none of these: pyscf's `ccsd_t_rdm.py` loops over virtual blocks, `ccsd_rdm._gamma2_outcore` writes `dvvvv` to an HDF5 file
in blocks, and our C kernels (`probes/t_density_kernel/`) form one o³ buffer per virtual triple. The UHF gradient's AO back-transformation
(`grad/uccsd.py` `_rdm2_mo2ao`) is already blocked by `max_memory`; it only receives the whole arrays.

## 2. Sizes (8 bytes per double; frozen core; cc-pVDZ)

| molecule | o (α / β active) | v (α / β) | one o³v³ array | one v⁴ array |
|---|---|---|---|---|
| benzene⁺ (measured: OOM at 31.5 GB, 30 Sep) | 15 / 14 | 93 / 94 | ≈ 22 GB | 0.6 GB |
| acenaphthylene⁺ (208 functions) | 28 / 27 | 168 / 169 | ≈ 830 GB | 6.4 GB |
| fluoranthene+Cl⁺, the cover's largest cation (287 functions, 21 frozen) | 40 / 39 | 226 / 227 | ≈ 5.9 TB | ≈ 21 GB |

A single o³v³ array already exceeds any node above benzene⁺'s size, and the code holds several at once; the v⁴ blocks follow behind them.

## 3. Design

1. **(T) lambda and (T) densities: one fused C pass per spin case**, as `t_fused_intermediates` does for RHF: a loop over ordered virtual
   triples (a,b,c) — for the mixed cases (baa, bba) one β and two α virtuals, or the reverse — forming W and V of size o³ (o_α³, o_α²o_β,
   o_αo_β²) in thread-private buffers from the sorted integrals, dividing by D3, applying the spin case's permutation (`p6`/`r6` for
   same-spin, `r4` for mixed — the factors to be pinned on H₂O⁺ against the Python result, as the RHF factors were on water), and
   accumulating every contraction of the table above into its owner: l1_t and l2_t (lambda), goo/gvv/gvo (γ1), dovov, dooov, dovvv and
   their mixed-spin partners (γ2). The energy kernel `pyscf/lib/cc/uccsd_t.c` already builds W and V per triple for the same four cases;
   its sorting (`_sort_eri`-style per spin) is the input layout, so energy and densities agree on conventions by construction.
2. **Memory per thread:** a few o³ buffers. **Shared:** the o·v³ inputs (ovvv, ovVV, OVvv, OVVV) and outputs (dovvv, dovVV, dOVvv, dOVVV) —
   at 287 functions ≈ 3.7 GB each, eight of them ≈ 30 GB. Jobs own a slice of the first virtual index, so outputs accumulate without
   locks; the inputs can be read from the HDF5 `eris` in the same slices if eight arrays do not fit (the same question as TASKS 94 for RHF).
3. **The UCCSD v⁴ blocks: an out-of-core γ2**, on the pattern of the RHF `ccsd_rdm._gamma2_outcore`: form `gvvvv` in slices of its first
   index from `tau` and `l2`, symmetrise each slice, and write it to the HDF5 file the gradient already opens (`fdm2`); `_rdm2_mo2ao` reads
   it in its own blocks. This is Python, no C.
4. **Install like the RHF kernels:** `install_uhf()` swaps `uccsd_t_lambda.make_intermediates`, the two `uccsd_t_rdm` functions and the UHF
   `_gamma2_outcore` (the gradient module looks them up at call time); `check_uhf_against_pyscf()` is the second route on molecules where
   pyscf's Python still fits.

## 4. Checks (before any anchor)

- **Element-wise against pyscf's Python** on H₂O⁺, NO (doublet, the psi4 tests' molecule) and triplet water: every intermediate ≤ 1e-12.
- **Gradient against finite differences of the CCSD(T) energy** on H₂O⁺ and NO, frozen and all-electron (the check that found pyscf#3305 in
  the first place; its upstream test `pyscf/grad/test/test_uccsd_t.py` is the citation for the call).
- **Benzene⁺ cc-pVDZ, the molecule that failed:** the kernel's gradient against pyscf's Python on a 128 GB machine (it needs ≈ 22 GB per
  array there) — the one point where both routes run at a real size.
- Timing and peak memory on benzene⁺ and naphthalene⁺ before pricing the cover's cations (the cost rule of anchor set three is RHF's;
  the open-shell price per gradient is 2–3× by the spin cases, to be measured, not assumed).

## 5. Effort and what it decides

The RHF density kernel took one evening to write and a day to verify; the lambda kernel a morning. The UHF version has four spin cases in
each of lambda, γ1 and γ2, plus the out-of-core v⁴ step: about a week of work, mostly verification. It decides whether the cover keeps its
cation cells as CC anchors (benzene⁺ to fluoranthene⁺ size) or reads them through the proxy alone — a choice for the user and, after June
2027, the supervisor (decision 63). Upstream: none of this exists in pyscf or pyscf-forge (searched 23 Oct, TASKS 98); the out-of-core γ2
and the blocked densities would be a pull request once verified (software ledger row 52).
