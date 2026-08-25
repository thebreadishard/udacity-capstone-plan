# Project 12 — Astrophysical PAH Identification (post-master’s)

> **ABSORBED 2026-08-23 — PROVENANCE ONLY, NOT A ROADMAP.**
> Per [Overarching_Goal.md](../GoalGathering/Overarching_Goal.md) section 3.C, this project's exit is
> now **Module 08's** exit: pre-registered, fail-closed identification against one frozen JWST/PAHdb
> product, with the negative control and the isomer-degeneracy rule. Section 2's "why Module 08 is not
> this project" table is therefore **obsolete and inverted**. Everything else — the pre-registration
> requirements (3.2), the verdict vocabulary (3.4) and the forbidden list (6) — is binding.

**Not a Udacity module.** Not scored in Modules 02–09. Module 08’s JWST framing is **motivation only**; this is the first project allowed to confront an observation as a *scientific* claim, and only after [Project 11](11_Anharmonic_IR_and_Intensities.md) exits.

**Horizon role:** use the Project 11 anharmonic band families (positions + relative intensities, named sizes and charge states) under an **astrophysical excitation / environment model**, and attempt identification against a **frozen** observational product (JWST spectrum or a PAHdb-style catalog). This is the remainder of the original “decode PAHs in space” title.

**Depends on:** Project 11 exit (stated cm⁻¹ + intensity tolerances, four-term error budget). Project 10 PES underneath.

---

## 1. Question

Can the diagnostic IR band families of **named** PAH sizes and charge states, computed with a gold-anchored PES and GVPT2-class nuclear motion, be used to **support or reject** identification of those species in a frozen astrophysical dataset — with the error budget still visible?

This is **not** “we identified every PAH in a JWST cube.” It is a fail-closed identification experiment on a pre-registered target list.

---

## 2. Why Module 08 is not this project

| Module 08 | Project 12 |
|---|---|
| Industry frame: JWST / astrochemistry as *why it would matter* | One frozen observational product as *data* |
| Reliability-gated **small-molecule** envelopes | Large-PAH band families from 11 |
| 300 K NVE dipole ACF | Isolated-PAH emission is not 300 K thermal MD |
| Must not claim a capability that was not built | May claim identification **only** inside the pre-registered list and tolerances |

Papers 8–15 in [Relevant_Scientific_Papers.md](../GoalGathering/Relevant_Scientific_Papers.md) already live in this world (charge-aware PAH features, ML-MD on PAHs, JWST applications). This project must **cite them as prior art**, not rediscover “PAHs have IR bands.”

---

## 3. Required work

### 3.1 Excitation and environment (or you compare the wrong spectrum)

Isolated PAH emission in photodissociation regions is not a 300 K NVE dipole ACF. Choose and **document** one:

- a temperature / microcanonical energy after a stated UV energy dump, or
- a published Poincaré / cascade model, or
- a stated thermal distribution with a justification that it matches the chosen observation

Plus, if comparing to matrix catalogs: the **same** matrix-shift model frozen in Project 11. Do not retune the shift to make a match.

### 3.2 Pre-registration (required)

Before touching the observational product, write down:

- the target species / charge list (subset of Project 11)
- the band families used (3 μm, 6–9 μm, 11–12 μm — name which)
- the match metric (band-center window, relative-intensity χ², or equivalent)
- the PASS / FAIL / UNIDENTIFIED rule, including what happens when two isomers fit

Changing the list after seeing JWST is a fail.

### 3.3 Observational product

One frozen dataset, versioned:

- a named JWST spectrum / aperture (papers 15a/15b class), **or**
- a named PAHdb / laboratory subset, if the claim is method validation rather than a new astronomical ID

Do not shop surveys until one matches.

### 3.4 Fail-closed identification

Reuse the master’s 07 discipline: cite measured value vs the pre-registered threshold. Allowed outputs:

- **Supported** (all scored bands inside tolerance; no equally good confounder)
- **Rejected**
- **Unidentified / degenerate** (two or more species fit; report both)

A slide that says “consistent with PAHs” without a species list is a fail.

---

## 4. What “arbitrarily large” is allowed to mean after 10+11+12

The defensible sentence:

> A size-extensive PES, gold-anchored on small aromatics, plus GVPT2-class anharmonicity, predicts **the diagnostic IR band families** of PAHs **up to a measured size / charge**, and those families can be used in a fail-closed identification against [named dataset].

It is **not**:

> one model, any Cₙ, chemically precise rovibrational lines and intensities, all JWST PAHs identified.

“Any size” in practice means: **transfer until the measured error exceeds the band tolerance**, then stop or change theory. A universal PAH Hamiltonian is not Project 12. It is a career.

---

## 5. Exit criterion

- Pre-registration document dated before the observational analysis
- Identification table: species × band family × metric × verdict
- Error budget from Project 11 **plus** excitation / environment term
- A limitations section that names every species the method **cannot** reach (size, charge, missing DMS, GVPT2 breakdown)

---

## 6. Forbidden

- Using JWST as a training set
- Claiming line-list precision
- Claiming “any size”
- Treating Module 08’s industry paragraph as if this work were already done
- Calling this a Udacity module

---

## 7. Deliverables

- Excitation / environment methods note
- Pre-registration + frozen observational product citation
- Identification table and verdict
- Negative-control: at least one species that **must** fail (wrong charge or wrong size)
- Final horizon statement: what is now scientifically allowed, and what remains a career
