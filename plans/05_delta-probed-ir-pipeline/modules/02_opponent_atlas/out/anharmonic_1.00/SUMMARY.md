# Opponent atlas — anharmonic library version 1.00 (2026-07-01, full=true) — 2026-09-10 18:17

This table is parsed from the public NASA Ames PAHdb v4.00 computed library (DOI 10.3847/1538-4365/ae1c38). It is computed science data, not AI-generated, and it is the *opponent* of this project's pipeline, not its training data.

Source `pahdb-complete-anharmonic-v1.00_g871h1cj39nl1WzxE4I.xml`, sha256 `2fb7a77608d57169d8b561f0b8ade073618b8e26f381e6c7c83d19c481506071`, 10,080,649 bytes. Root attributes: {"{http://www.w3.org/2001/XMLSchema-instance}schemaLocation": "http://www.astrochemistry.org/pahdb/anharmonic https://www.astrochemistry.org/pahdb/schemas/anharmonic.xsd", "database": "anharmonic", "version": "1.00", "date": "2026-07-01", "full": "true"}.

**Species: 45** (42 neutral) · **bands: 95,189** · tag inventory: {'comment': 48, 'comments': 45, 'formula': 45, 'charge': 45, 'symmetry': 45, 'weight': 45, 'total_e': 45, 'vib_e': 45, 'method': 45, 'n_solo': 45, 'n_duo': 45, 'n_trio': 45, 'n_quartet': 45, 'n_quintet': 45, 'n_ch': 45, 'n_ch2': 45, 'n_ch3': 45, 'position': 1022, 'x': 1022, 'y': 1022, 'z': 1022, 'type': 1022, 'atom': 1022, 'geometry': 45, 'frequency': 95189, 'intensity': 95189, 'mode': 95189, 'transitions': 45, 'specie': 45, 'reference': 44, 'references': 44, 'species': 1, 'pahdatabase': 1}

Charge: {'0': 42, '1': 3} · basis (from the route comment): {'?': 45} · smallest 4-31G species n_c = None · largest 6-31G* species n_c = None

| n_c bin | species | basis sets |
|---|---|---|
| 1–20 | 45 | [('?', 45)] |
| 21–50 | 0 | [] |
| 51–100 | 0 | [] |
| 101–200 | 0 | [] |
| 201–400 | 0 | [] |
| 401–10000 | 0 | [] |

| ladder rung | looked for | entries | first hits (uid, formula, charge) |
|---|---|---|---|
| R0 | ['C6H6'] | 1 | [('100000', 'C6H6', '0')] |
| R1 | ['C10H8'] | 1 | [('330', 'C10H8', '0')] |
| R2 | ['C16H10', 'C18H12'] | 2 | [('334', 'C16H10', '0'), ('282', 'C18H12', '0')] |
| R3 | ['C24H12'] | 0 | [] |
| R4-R5 class | 54 <= n_c <= 216 | 0 | [] |
| R6 class | n_c >= 300 | 0 | [] |

**Debt 6 (C₃₈₄H₄₈-class, 300 ≤ n_c ≤ 400): 0 species**; C384H48 itself: absent. Full list in `c384_class.csv`.

Scale factors seen: [(nan, 1), (nan, 1), (nan, 1), (nan, 1), (nan, 1), (nan, 1), (nan, 1), (nan, 1)]

Family labels are a frequency-range rule printed in the script (pilot-note candidate); nothing is trained here.
