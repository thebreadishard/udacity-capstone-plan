# Opponent atlas — theoretical library version 0.00-synthetic (2026-09-10, full=false) — 2026-09-10 18:06

This table is parsed from the public NASA Ames PAHdb v4.00 computed library (DOI 10.3847/1538-4365/ae1c38). It is computed science data, not AI-generated, and it is the *opponent* of this project's pipeline, not its training data.

Source `_synthetic_test.xml`, sha256 `c9555dea09e4b1bec4e4b72282de880d5e1adeefebbefa87d4486acd9e248efd`, 1,704 bytes. Root attributes: {"database": "theoretical", "version": "0.00-synthetic", "date": "2026-09-10", "full": "false"}.

**Species: 2** (2 neutral) · **bands: 3** · tag inventory: {'comment': 3, 'comments': 2, 'reference': 1, 'references': 2, 'formula': 2, 'charge': 2, 'symmetry': 5, 'weight': 2, 'total_e': 2, 'vib_e': 2, 'method': 2, 'n_solo': 2, 'n_duo': 2, 'n_trio': 2, 'n_quartet': 2, 'n_quintet': 2, 'n_ch2': 2, 'n_chx': 2, 'x': 1, 'y': 1, 'z': 1, 'position': 1, 'type': 1, 'atom': 1, 'geometry': 2, 'frequency': 3, 'intensity': 3, 'mode': 3, 'transitions': 2, 'specie': 2, 'species': 1, 'pahdatabase': 1}

Charge: {'0': 2} · basis (from the route comment): {'6-31g*': 1, '4-31g': 1} · smallest 4-31G species n_c = 384 · largest 6-31G* species n_c = 6

| n_c bin | species | basis sets |
|---|---|---|
| 1–20 | 1 | [('6-31g*', 1)] |
| 21–50 | 0 | [] |
| 51–100 | 0 | [] |
| 101–200 | 0 | [] |
| 201–400 | 1 | [('4-31g', 1)] |
| 401–10000 | 0 | [] |

| ladder rung | looked for | entries | first hits (uid, formula, charge) |
|---|---|---|---|
| R0 | ['C6H6'] | 1 | [('1', 'C6H6', '0')] |
| R1 | ['C10H8'] | 0 | [] |
| R2 | ['C16H10', 'C18H12'] | 0 | [] |
| R3 | ['C24H12'] | 0 | [] |
| R4-R5 class | 54 <= n_c <= 216 | 0 | [] |
| R6 class | n_c >= 300 | 1 | [('2', 'C384H48', '0')] |

**Debt 6 (C₃₈₄H₄₈-class, 300 ≤ n_c ≤ 400): 1 species**; C384H48 itself: [('2', 'C384H48', '0', '1-A1G', '4-31g')]. Full list in `c384_class.csv`.

Scale factors seen: [(0.975, 2), (0.964, 1)]

Family labels are a frequency-range rule printed in the script (pilot-note candidate); nothing is trained here.
