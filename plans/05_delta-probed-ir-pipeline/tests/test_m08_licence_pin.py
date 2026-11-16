"""The carried network's stated error and its licence, pinned whole on the carried records (`m08/accuracy.py`, `m08/licence.py`): every
family's value on both hold-outs under both quantities, the licensed families and the statement as certificates print it. A change of the
quantity the licence reads, of a record or of the wording shows here first. The records are read as JSON; no model file is loaded.

Re-pinned on 16 Nov 2026 with the amendment of decision 65: the licence is read on the product's error (the product-error record),
so 'other' (first order 3.62 / 3.89, product 2.78 / 2.77) is licensed; the first-order values are unchanged and stay pinned."""
from __future__ import annotations

import sys

from pin_tools import PLAN

sys.path.insert(0, str(PLAN / "modules" / "08_industry_synthesis"))
from m08 import accuracy as A
from m08 import licence

V13_RECORDS = [f"E7_rungC_chain35_analytic_{kind}_seed{s}.json" for kind in ("eval_frozenb", "a8read") for s in range(3)]
FIRST_ORDER = {"a": {"ring-ip": (1.77, [1.95, 1.68, 1.7]), "CH-stretch": (1.19, [0.91, 1.74, 0.91]), "CH-oop": (2.17, [2.47, 2.06, 1.99]),
                     "other": (3.62, [4.09, 3.27, 3.51]), "coupling_ratio": (0.184, [0.193, 0.176, 0.183])},
               "b": {"ring-ip": (2.12, [2.25, 2.02, 2.11]), "CH-stretch": (2.5, [1.91, 3.51, 2.08]), "CH-oop": (2.7, [2.44, 2.95, 2.72]),
                     "other": (3.89, [3.65, 4.51, 3.52]), "coupling_ratio": (0.263, [0.282, 0.243, 0.265])}}
N_MOLECULES = {"a": 8, "b": 39}
PRODUCT_RECORD = "E7_rungC_chain35_analytic_product_error.json"
PRODUCT = {"a": {"ring-ip": (1.43, [1.13, 1.7], 199), "CH-stretch": (0.95, [0.39, 1.48], 73), "CH-oop": (1.64, [1.19, 1.97], 46),
                 "other": (2.78, [1.68, 3.76], 156)},
           "b": {"ring-ip": (1.91, [1.84, 2.0], 1164), "CH-stretch": (2.19, [1.8, 2.53], 401), "CH-oop": (1.88, [1.56, 2.16], 84),
                 "other": (2.77, [2.56, 2.97], 1225)}}
STATEMENT = ("licensed at the DFT proxy: ring-ip (1.43 / 1.91), CH-stretch (0.95 / 2.19), CH-oop (1.64 / 1.88), other (2.78 / 2.77); not "
             "licensed: none — error of the corrected band positions of the seed-mean correction on hold-outs (a) / (b) in cm⁻¹ against 3 "
             "(decision 65 as amended on 16 Nov 2026); other on hold-out (a) rests on 8 molecules: the 95 % interval of a bootstrap over "
             "molecules is 1.68–3.76 cm⁻¹ and crosses the line (70 % of the resamples lie under it); the first-order diagonal error of "
             "each seed's correction, averaged over the seeds, which the licence read until then: ring-ip (1.77 / 2.12), CH-stretch "
             "(1.19 / 2.5), CH-oop (2.17 / 2.7), other (3.62 / 3.89); no coupled-cluster licence")


def test_the_carried_versions_read_outs_per_seed_and_their_means():
    acc = A.carried_accuracy()
    assert acc["version"] == "1.3" and acc["sources"] == [*V13_RECORDS, PRODUCT_RECORD]
    for h, rows in FIRST_ORDER.items():
        got = acc["holdouts"][h]
        assert got["n_molecules"] == N_MOLECULES[h]
        assert {q: (r["mean"], r["seeds"]) for q, r in got["readouts"].items()} == rows
        assert {f: (p["rms"], p["interval"], p["n_modes"]) for f, p in got["product"].items()} == PRODUCT[h]
        assert all(p["n_molecules"] == N_MOLECULES[h] and p["within_target"] for p in got["product"].values())
    crossing = [(h, f) for h in PRODUCT for f, p in acc["holdouts"][h]["product"].items() if p["interval_crosses_line"]]
    assert crossing == [("a", "other")] and acc["licence_quantity"] == "product"


def test_the_carried_versions_licence():
    s = licence.state()
    assert s["licensed_families"] == ["ring-ip", "CH-stretch", "CH-oop", "other"] and s["line_cm"] == 3.0 and s["quantity"] == "product"
    assert s["errors"] == {f: {h: PRODUCT[h][f][0] for h in PRODUCT} for f in PRODUCT["a"]}
    assert s["first_order_errors"] == {f: {h: FIRST_ORDER[h][f][0] for h in FIRST_ORDER} for f in PRODUCT["a"]}
    assert s["statement"] == STATEMENT and len(s["caveats"]) == 1 and s["caveats"][0] in STATEMENT
    assert s["rule"].startswith("decision 65 (29 Oct 2026, amended 16 Nov 2026): a mode family is licensed where the error of what the "
                                "product delivers — the error of the corrected band positions of the seed-mean correction")
    assert s["rule_source"] == "README.md, decision 65 as amended on 16 Nov 2026"
