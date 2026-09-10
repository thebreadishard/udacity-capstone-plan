# Opponent atlas — theoretical library version 4.00 (2024-06-27, full=true) — 2026-09-10 18:19

This table is parsed from the public NASA Ames PAHdb v4.00 computed library (DOI 10.3847/1538-4365/ae1c38). It is computed science data, not AI-generated, and it is the *opponent* of this project's pipeline, not its training data.

Source `pahdb-complete-theoretical-v4.00_fevj3bdlnookcPYsGjJ.xml`, sha256 `0d8cb460b8c13b9a960cded92b1d5fe641fdaf8edcae46b25380a42bd0f50ed8`, 503,336,201 bytes. Root attributes: {"{http://www.w3.org/2001/XMLSchema-instance}schemaLocation": "http://www.astrochemistry.org/pahdb/theoretical http://www.astrochemistry.org/pahdb/schemas/theoretical.xsd", "database": "theoretical", "version": "4.00", "date": "2024-06-27", "full": "true"}.

**Species: 10,749** (4,479 neutral) · **bands: 2,517,399** · tag inventory: {'comment': 10750, 'comments': 10749, 'formula': 10749, 'charge': 10749, 'symmetry': 2528148, 'weight': 10749, 'total_e': 10749, 'vib_e': 10749, 'method': 10749, 'n_solo': 10749, 'n_duo': 10749, 'n_trio': 10749, 'n_quartet': 10749, 'n_quintet': 10749, 'n_ch': 10749, 'n_ch2': 10749, 'n_ch3': 10749, 'position': 860631, 'x': 860631, 'y': 860631, 'z': 860631, 'type': 860631, 'atom': 860631, 'geometry': 10749, 'frequency': 2517399, 'intensity': 2517399, 'mode': 2517399, 'transitions': 10749, 'specie': 10749, 'reference': 7255, 'references': 7161, 'species': 1, 'pahdatabase': 1}

Charge: {'0': 4479, '1': 2162, '2': 2868, '-1': 1231, '3': 9} · basis (from the route comment): {'6-31g*': 10703, '?': 32, '4-31g': 14} · smallest 4-31G species n_c = 212 · largest 6-31G* species n_c = 294

| n_c bin | species | basis sets |
|---|---|---|
| 1–20 | 359 | [('6-31g*', 359)] |
| 21–50 | 5044 | [('6-31g*', 5030), ('?', 14)] |
| 51–100 | 4572 | [('6-31g*', 4554), ('?', 18)] |
| 101–200 | 750 | [('6-31g*', 750)] |
| 201–400 | 24 | [('4-31g', 14), ('6-31g*', 10)] |
| 401–10000 | 0 | [] |

| ladder rung | looked for | entries | first hits (uid, formula, charge) |
|---|---|---|---|
| R0 | ['C6H6'] | 0 | [] |
| R1 | ['C10H8'] | 1 | [('330', 'C10H8', '0')] |
| R2 | ['C16H10', 'C18H12'] | 7 | [('387', 'C16H10', '0'), ('334', 'C16H10', '0'), ('2355', 'C18H12', '0'), ('291', 'C18H12', '0'), ('282', 'C18H12', '0'), ('280', 'C18H12', '0'), ('211', 'C18H12', '0')] |
| R3 | ['C24H12'] | 1 | [('18', 'C24H12', '0')] |
| R4-R5 class | 54 <= n_c <= 216 | 5110 | [('46', 'C54H18-', '-1'), ('48', 'C54H19-', '-1'), ('47', 'C54H19-', '-1'), ('3178', 'C54H20-', '-1'), ('3921', 'C54H22-', '-1'), ('3920', 'C54H22-', '-1'), ('3919', 'C54H22-', '-1'), ('3918', 'C54H22-', '-1'), ('3902', 'C54H24-', '-1'), ('3901', 'C54H24-', '-1'), ('3900', 'C54H24-', '-1'), ('3899', 'C54H24-', '-1')] |
| R6 class | n_c >= 300 | 2 | [('617', 'C384H48', '0'), ('4447', 'C384H48+2', '2')] |

**Debt 6 (C₃₈₄H₄₈-class, 300 ≤ n_c ≤ 400): 2 species**; C384H48 itself: [('617', 'C384H48', '0', '1-A1G', '4-31g')]. Full list in `c384_class.csv`.

Scale factors seen: [(0.9794, 1407844), (0.9691, 875211), (0.9597, 210279), (0.9563, 10731), (0.9523, 6982), (0.9097, 2488), (0.9595, 1158), (0.9908, 583)]

Family labels are a frequency-range rule printed in the script (pilot-note candidate); nothing is trained here.
