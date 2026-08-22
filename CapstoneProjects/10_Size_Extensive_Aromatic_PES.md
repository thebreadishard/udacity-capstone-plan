# Project 10 — Size-Extensive Aromatic PES (post-master’s)

**Not a Udacity module.** Not scored in Modules 02–09. Does not replace Module 08.

**Horizon role:** first wall between the master’s small-molecule field-PES experiment and chemically precise-enough IR of very large PAHs. Labels and size-extensivity. Without this project, Project 11 is DFT-IR in a nicer notebook.

**Depends on:** a finished master’s comparison of \(E=\mathcal{E}[\rho,R]\) vs an atomistic equivariant GNN on the **same** CCSD(T) splits (Distilled Plan §2; Workstream G1). Distilled Plan §5.1 is the methods ancestor of the theory ladder below.

**Hands to:** [Project 11](11_Anharmonic_IR_and_Intensities.md).

---

## 1. Question

Can a PES (field, atomistic, or hybrid) be **size-extensive** on aromatics while remaining **anchored** to CCSD(T) on systems that can actually be computed?

Canonical CCSD(T)/cc-pVTZ is ~\(N^7\). Benzene is already the master’s long pole. “Any size at that level” is not a longer campaign. It is a different electronic-structure theory.

---

## 2. Why more of Phases 0–5 is not this project

| Master’s object | Why it does not scale by repetition |
|---|---|
| Global \(N^3\) cube | Memory and FFT cost grow with box volume, not atom count |
| Canonical CCSD(T) labels | Infeasible past a few rings |
| 5000 more benzene configs | Does not test transfer to the next ring |
| Naphthalene as outlook | Must become a **scored** transfer step here |

---

## 3. Required work

### 3.1 Electronic-structure ladder (the real Project 10)

Never label C₂₄H₁₂ at canonical CCSD(T)/cc-pVTZ and call it the master’s method.

Write and **measure** a ladder, for example:

| Rung | Role | Rule |
|---|---|---|
| **Gold** | Canonical CCSD(T) (or a local-correlation method with a **measured** error vs canonical) | Benzene, naphthalene, a few substituted rings only |
| **Workhorse** | Local-correlation or range-separated method | Error vs gold published **per mode family**, not hoped |
| **Optional Δ-ML** | Learn \(E_{\mathrm{gold}}-E_{\mathrm{cheap}}\) on small aromatics | Apply on larger ones; validate on a **held-out medium** molecule, not the training ring |

Every row in the campaign manifest inherits Distilled Plan §5.1 tags (`theory_energy`, `theory_density`, `theory_force`, `rdm_*`, `pyscf_version` or successor, `wall_s`, `max_rss_gb`) plus `ladder_rung` and `error_vs_gold`.

Master’s shrink-ladder rung 3 (DFT density, CCSD(T) energy) is a degree exception. For large PAHs, a cheap **energy** with an unquantified gap is DFT-IR with extra steps.

### 3.2 Representation fork (decide with the master’s data)

After the field-vs-GNN test:

- **Field wins** on left-out modes / benzene π: keep \(\mathcal{E}[\rho]\) but **stop using one global cube**. Required: a size-extensive field — atomic-density superposition + learned remainder, overlapping local grids, or multi-resolution. The Distilled Plan’s naphthalene superposition is a prototype, not a result.
- **Field ties or loses:** the large-PAH PES is the GNN (or a hybrid: GNN energy, field only where delocalization matters). Forcing voxels to C₄₈ because they were the master’s novelty is how the program dies of RAM.

If the field loses and this project refuses to switch, **stop**. Project 11 will not save a non-extensive PES.

### 3.3 Scored molecule ladder

| Step | Molecule class | What is scored |
|---|---|---|
| 0 (inherited) | Benzene | Master’s Phase 5, if the §5.1 pilot allowed it |
| 1 | Naphthalene | Transfer: train smaller, evaluate here. No longer “discussion.” |
| 2 | Anthracene or phenanthrene | Next-ring transfer |
| 3 | One compact 4-ring | Stop or continue only if transfer error is still inside the band budget |

Each step includes a **charge-state** check (neutral vs cation). Astrophysical PAH IR is not only the 300 K neutral.

### 3.4 Data product

Not 5000 more benzene cubes. A **multi-size aromatic set** with documented theory tags. Public DOI. Without that, “any size” is a slide.

---

## 4. Exit criterion

You may say:

> On molecule class X, band-relevant PES errors are quantified against a gold rung, and zero-shot transfer to the next ring does not fall apart.

You may **not** yet say chemically precise IR. That is Project 11.

---

## 5. Forbidden

- Training on PAHdb / JWST spectra as a substitute for a PES (that is the 2020 high-throughput matcher; not chemically precise).
- Canonical-CCSD(T)-for-C₄₈ as a promise.
- Keeping a global cube after the field lost the master’s comparison.
- Calling this a Udacity module or a Module 08 stretch goal.

---

## 6. Deliverables

- Written theory ladder + measured gold-vs-workhorse table
- Representation decision memo (field / GNN / hybrid) citing the master’s comparison
- Public multi-size aromatic dataset (DOI) with §5.1-style manifest
- Transfer report: benzene → naphthalene → 3-ring → one 4-ring, neutrals and cations
- Go / no-go for Project 11
