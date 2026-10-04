# Estimate, 4 October 2026, 11:1x — how many molecules, how many anchors, and how many computed points per anchor the full mandate needs (compute set aside)

*The user's questions of 4 October 11:0x: "als je geen rekening houdt met compute, en ervan uitgaat dat we de PC hebben en een aantal jaren, hoeveel
ankers … en hoeveel moleculen zou je nodig hebben om bij het volledige mandaat te komen?" and "hoeveel punten per anker … is x afhankelijk van de grootte
van het molecuul?". An estimate with its assumptions and the three measurements that sharpen it; numbers that are measured carry their source.*

## 1. Two layers, two counts

| layer | what it learns | needed per scaffold family | families | total |
|---|---|---|---|---|
| cheap corpus (B3LYP → the corpus high level) | the whole correction, millions of parameters | ≈ 30 children cover a family, ≈ 60 finish it (decision 52, measured on the error map of 3 Oct) | 25–40 (ring count, aza, five-rings, cations, substituents) | **2,000–3,000 molecules**; 843 computed on 4 Oct (`corpus/STATUS.md`) |
| CC anchors (corpus high level → CCSD(T)) | a smoother, systematic residual; the tuning touches α and the head only | 3–5, one per size rung (2, 3, 4, 5+ rings) | the same 25–40 | **100–200 anchors**; 4 valid on 4 Oct, the fifth (anthracene) lands 5 Oct |

Assumptions and what tests them:
- *3–5 per family, not 30:* three anchors took naphthalene from 0.99 to 0.25 (T3, 2 Oct, head-tuned); the slope beyond three is the registered anchor curve 3 → 5 → 8 (TASKS), known within two weeks. A flat slope makes 100–200 into 300.
- *Transfer between families halves the count:* chain 33 (anthracene held out, five anchors) is the first measurement of a larger, related family.
- *Size extrapolation is required:* the mandate's targets (30+ carbon) are never anchors, and the error follows scaffold size (error map, 2–3 Oct); hence a size ladder per family up to pyrene/perylene canonically and LNO anchors above (dossier question 7).
- *The level of the anchors:* the TZ read (`probes/cc_basis_oop_check.py`) decides whether cc-pVDZ anchors are the truth or need a basis correction; that changes the price per anchor, not the count.
- *Not delivered by anchors:* the spectral shape (anharmonic shifts, widths, temperature) is a third layer calibrated on the gas-phase laboratory spectra of module 03, not on CC anchors.

## 2. Points per anchor: x = 6 × (symmetry-representative atoms) gradients + 1 reference

An anchor is a finite-difference Hessian from analytic CCSD(T) gradients (`probes/e8_cc_hessian_fd.py`, the (T)-lambda kernel): every symmetry-unique
Cartesian displacement is computed twice (+h and −h), each computation is one CCSD + lambda + (T) gradient, and one reference gradient is added for
the pair check. Symmetry removes every displacement that an operation maps onto a computed one, so

    x = 2 × 3 × n_rep + 1,   n_rep = atoms not related to another by a symmetry operation (N without symmetry, so x = 6N + 1 at worst).

x grows linearly with the number of atoms and shrinks with the point group — and the cost *per point* grows as about N⁷, which is where the size
really bites. Measured anchors:

| molecule | atoms N | point group | n_rep | unique displacements | gradient points (+1 reference) | source |
|---|---|---|---|---|---|---|
| benzene | 12 | D6h | 2 | 6 | 12 (+1) | `results_m1/e8_benzene_ccpvtz_oop_2026-10-03` (the raw counter in its log says 72 = 6N) |
| pyridine | 11 | C2v | 7 | 21 | 42 (+1) | `results_m1/e8_pyridine_ccpvdz_2026-09-30` |
| fluorobenzene | 12 | C2v | 8 | 24 | 48 (+1) | `results_m1/e8_fluorobenzene_ccpvdz_2026-09-30` |
| benzonitrile | 13 | C2v | 9 | 27 | 54 (+1) | `results_m1/e8_benzonitrile_ccpvdz_2026-09-30` |
| naphthalene | 18 | D2h | 5 | 15 | 30 (+1) | `results_m1/e8_naphthalene_ccpvdz_tlambda_2026-10-02` |
| anthracene | 24 | D2h | 7 | 21 | 42 (+1) | CCX53 run, `ccx53_watch.log` ("21 symmetry-unique displacements") |

Reading the table: a substituted molecule (C2v or C1) needs more points than a bare PAH twice its size — naphthalene+COOH (21 atoms, no
symmetry) would need 126 gradients; coronene (36 atoms, D6h, 4 representative atoms) only 24. Energies alone instead of gradients would need of
the order of (6N)²/2 points, which is why the gradient route and the (T)-lambda kernel exist (software ledger rows 20–35).

Reducing x below 6 n_rep is the deck question of decision 58: the rehearsal of 4 Oct showed that network-predicted rows cannot stand in for
measured ones today (third line), so a full deck remains the price of an anchor; the P1 order helps only where a deck is partial for another reason.

## 3. What sharpens this estimate, already scheduled

1. **Chain 33** (5 Oct): transfer to a held-out larger family with five anchors — line naphthalene ≤ 4 cm⁻¹.
2. **The anchor curve 3 → 5 → 8** (benzene⁺ as the sixth; α and head only, after the rank-r overfit of 3 Oct) — the slope of the anchor count.
3. **The TZ read** (4 Oct ≈ 13:15): basis or level — the price per anchor point.
