# Opponent atlas — experimental library version 3.10 (2023-04-13, full=true) — 2026-09-10 18:17

This table is parsed from the public NASA Ames PAHdb v4.00 computed library (DOI 10.3847/1538-4365/ae1c38). It is computed science data, not AI-generated, and it is the *opponent* of this project's pipeline, not its training data.

Source `pahdb-complete-experimental-v3.10_upv89lcujbt3bHDzVfY.xml`, sha256 `b8b487777bd584a7d4fa6f9f1cf490c49cd8b7e1840bef3f39d1303a32243e1e`, 6,980,395 bytes. Root attributes: {"{http://www.w3.org/2001/XMLSchema-instance}schemaLocation": "http://www.astrochemistry.org/pahdb/theoretical https://www.astrochemistry.org/pahdb/schemas/experimental.xsd", "database": "experimental", "version": "3.10", "date": "2023-04-13", "full": "true"}.

**Species: 84** (50 neutral) · **bands: 3,896** · tag inventory: {'comment': 99, 'comments': 84, 'reference': 71, 'references': 71, 'formula': 84, 'charge': 84, 'position': 3253, 'x': 3253, 'y': 3253, 'z': 3253, 'type': 3253, 'atom': 3253, 'geometry': 84, 'frequency': 3932, 'intensity': 3932, 'mode': 3896, 'transitions': 84, 'specie': 84, 'laboratory': 36, 'species': 1, 'pahdatabase': 1}

Charge: {'0': 50, '-1': 6, '1': 28} · basis (from the route comment): {'?': 84} · smallest 4-31G species n_c = None · largest 6-31G* species n_c = None

| n_c bin | species | basis sets |
|---|---|---|
| 1–20 | 44 | [('?', 44)] |
| 21–50 | 40 | [('?', 40)] |
| 51–100 | 0 | [] |
| 101–200 | 0 | [] |
| 201–400 | 0 | [] |
| 401–10000 | 0 | [] |

| ladder rung | looked for | entries | first hits (uid, formula, charge) |
|---|---|---|---|
| R0 | ['C6H6'] | 0 | [] |
| R1 | ['C10H8'] | 1 | [('330', 'C10H8', '0')] |
| R2 | ['C16H10', 'C18H12'] | 5 | [('334', 'C16H10', '0'), ('387', 'C16H10', '0'), ('282', 'C18H12', '0'), ('291', 'C18H12', '0'), ('280', 'C18H12', '0')] |
| R3 | ['C24H12'] | 1 | [('18', 'C24H12', '0')] |
| R4-R5 class | 54 <= n_c <= 216 | 0 | [] |
| R6 class | n_c >= 300 | 0 | [] |

**Debt 6 (C₃₈₄H₄₈-class, 300 ≤ n_c ≤ 400): 0 species**; C384H48 itself: absent. Full list in `c384_class.csv`.

Scale factors seen: [(nan, 1), (nan, 1), (nan, 1), (nan, 1), (nan, 1), (nan, 1), (nan, 1), (nan, 1)]

Family labels are a frequency-range rule printed in the script (pilot-note candidate); nothing is trained here.
