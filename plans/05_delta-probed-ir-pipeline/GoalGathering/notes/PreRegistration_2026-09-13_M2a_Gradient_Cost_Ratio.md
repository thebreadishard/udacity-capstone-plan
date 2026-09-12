# Pre-registration 2026-09-13 — M2a: measuring the gradient-to-energy cost ratio g (step 4 of the evidence ladder), written before any number exists

*Side project of plan 05 (`Side_Project_2026-09-04_ModeG_Gradients.md`, milestones M2–M5). M2 as pre-registered on 4 September is the correctness milestone (an AD gradient of the frozen-space LNO energy against central finite differences, at cc-pVTZ). This note adds a cheaper milestone in front of it, **M2a: the cost ratio**, because the evidence ladder of 12 September ("does plan 06 make plan 05 cheaper?") showed that every gradient-based lever — decision 34's substitution layer, plan 06's X11 (8 gradients per benzene correction against 448 energies), mode G itself — stands or falls with one number that no paper prints: g, the cost of one gradient in units of one energy. Decided by the user on 13 September ("stap 1, 2 en 3 nu, de rest na de run"). Rules of the house: the protocol is fixed here; the runs follow after the naphthalene xtight timing has finished (one anchor job at a time); every number will be printed by `probes/m2a_gradient_cost_ratio.py`.*

## 1. The quantity

For a method X in engine E on machine H at basis B with settings S:

  g_X = t_grad / t_E,

where t_E is the wall time of one energy evaluation and t_grad the wall time of one full nuclear gradient (all 3N components), **both in the same engine, on the same machine, with the same thread count, from the same SCF starting point, measured by the same code path** (`time.perf_counter()` around the call; the SCF excluded from both, since both need it once and a gradient needs its derivative once — the SCF derivative's own time is reported separately). Peak resident memory of each call is recorded (`resource.getrusage`). Three repeats per cell; the median is g, the spread is printed. A "gradient" means the analytic or automatically differentiated gradient — never a finite-difference one; the finite-difference cost (6N energies by central differences, 72 at benzene) is the reference line g_FD every measured g is compared with.

## 2. The cells, in the order they run

| cell | engine | method | molecule, basis | what it tells |
|---|---|---|---|---|
| 0 (smoke) | PySCFAD | RHF | benzene, cc-pVDZ | the AD gradient agrees with PySCF's analytic RHF gradient to 10⁻⁶ E_h/bohr; timing pipeline works |
| 1 | PySCFAD | MP2 (canonical) | benzene, cc-pVDZ | g at the cheapest correlated level; the reference against the AD literature's "c < 6, typically 2–3" (Baydin et al. 2018) |
| 2 | PySCFAD | CCSD(T) (canonical) | benzene, cc-pVDZ | g at the anchor's canonical level; compared with PySCF's own analytic CCSD(T) gradient timing (1,399 s, 13.9 GB, measured 2026-09-10) |
| 3 | PySCFAD | LNO-CCSD(T) as shipped (`pyscfad.lno.LNOCCSD_T`), PySCFAD's default thresholds | benzene, cc-pVDZ | **the number the ladder needs first:** g for a local CC(T) gradient by reverse-mode AD — the quantity Zhang et al. 2024 demonstrate but do not print |
| 4 | PySCFAD | LNO-CCSD(T) at thresholds matching plan 05's *tight* | benzene, cc-pVDZ | does g depend on the truncation level |
| 5 (only if 3 ≤ 20) | PySCFAD | LNO-CCSD(T) | benzene, cc-pVTZ | the anchor's basis; memory is the question here (the canonical gradient needed 13.9 GB at DZ) |

Cells 0–4 are laptop work of an evening once installed; cell 5 may not fit 25 GB and is then reported as "does not fit", which is itself a number for P13. **Frozen spaces (plan 05's arm A) are not in any cell**: that is M2 proper (weeks of work in JAX); M2a measures the shipped engine, so its g is an estimate of the frozen-space g, not the frozen-space g — printed with that label.

## 3. Pre-stated reading

- **g ≤ 6** at cell 3: within the AD literature's constant; substitution and mode G both pay by an order of magnitude (X11: 8 g ≈ 48 energies against 448); M2 proper is worth its weeks.
- **6 < g ≤ 20**: substitution still pays (8 g ≤ 160 < 448 at benzene; grows in favour with size, X8), mode G marginally (108 g at naphthalene against 474); M2 proper is worth it for the substitution branch alone.
- **g > 20**: the gradient levers do not change plan 05's order of magnitude at benzene size; decision 34's items stay as pre-registered (energies-only, measured once), M2 proper is deferred, and the cost question returns to the machine (P13) and to the element count (P25). This outcome is recorded, not argued with.
- **Memory** is reported beside every g; a gradient that needs more than the laptop's 25 GB at cc-pVTZ moves the whole gradient branch to the desktop or the cluster regardless of g.

## 4. What is fixed now and cannot move after the numbers

The definition (§1), the cells and their order (§2), the thresholds of §3, the engine version (below), the machine (this laptop, 8 threads, WSL, nothing else running), the molecule and geometry (plan 05's benzene dry-run geometry, `results_dryrun/benzene/stageA.json`), the repeats (three), and the script. What may be added afterwards: more cells (naphthalene, other thresholds), never a change to these.

## 5. The engine, pinned (verified 2026-09-13, before installation)

- **PySCFAD 0.3.3** (PyPI release of 2026-06-29; `pip install pyscfad`), Apache-2.0; depends on `jax >= 0.9.1, < 0.11`, `pyscfadlib >= 0.3.3`, `pyscf >= 2.3`, `pyscf-properties`. Home: github.com/fishjojo/pyscfad. The `pyscfad.lno` package exports `LNOMP2`, `LNOCCSD`, `LNOCCSD_T` (files `lno_base.py`, `ccsd.py`, `ccsd_t.py`, `mp2.py`, `_checkpointed.py`, MPI variants). The paper behind it is bibliography item 33 (Zhang, Li, Ye, Berkelbach & Chan 2024, DOI 10.1063/5.0212274).
- Installed, when the user allows the download, in a **separate WSL environment `~/qcad`** so that plan 05's `qc05` engine (pyscf 2.14.0 + patched pyscf-forge 1.1.1) is untouched; CPU JAX only; versions of jax, jaxlib, pyscf, pyscfad, pyscfadlib printed into the results file. Software ledger row 9.
- Not yet checked (to be recorded at install): whether PySCFAD's LNO uses its own thresholds convention (γ of the paper) or pyscf-forge's `lno_thresh` pair, and whether its `_checkpointed.py` is the recomputation (`jax.checkpoint`) the paper describes — both matter for comparing cell 4 with plan 05's "tight".

## 6. Bookkeeping

`probes/m2a_gradient_cost_ratio.py` (written today, numpy self-test only until the run ends); results to `probes/results_m2a/`; a result note the day the cells run; Budget dated note with g; the evidence ladder's step 4 in the README points here. Nothing in the Ladder or the proposal changes until g exists.
