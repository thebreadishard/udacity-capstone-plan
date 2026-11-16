"""The carried network's stated error and its licence, pinned whole on the carried records (`m08/accuracy.py`, `m08/licence.py`): every
family's value on both hold-outs, the licensed families and the statement as certificates print it. A change of the quantity the licence
reads, of a record or of the wording shows here first. The records are read as JSON; no model file is loaded."""
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


def test_the_carried_versions_read_outs_per_seed_and_their_means():
    acc = A.carried_accuracy()
    assert acc["version"] == "1.3" and acc["sources"] == V13_RECORDS
    for h, rows in FIRST_ORDER.items():
        got = acc["holdouts"][h]
        assert got["n_molecules"] == N_MOLECULES[h]
        assert {q: (r["mean"], r["seeds"]) for q, r in got["readouts"].items()} == rows


def test_the_carried_versions_licence():
    s = licence.state()
    assert s["licensed_families"] == ["ring-ip", "CH-stretch", "CH-oop"] and s["line_cm"] == 3.0
    assert s["errors"] == {"ring-ip": {"a": 1.77, "b": 2.12}, "CH-stretch": {"a": 1.19, "b": 2.5}, "CH-oop": {"a": 2.17, "b": 2.7},
                           "other": {"a": 3.62, "b": 3.89}}
    assert s["statement"] == ("licensed at the DFT proxy: ring-ip (1.77 / 2.12), CH-stretch (1.19 / 2.5), CH-oop (2.17 / 2.7); not licensed: "
                              "other (3.62 / 3.89) — seed-mean error on hold-outs (a) / (b) in cm⁻¹ against 3; no coupled-cluster licence")
    assert s["rule"].startswith("decision 65 (29 Oct 2026): a mode family is licensed where the carried ΔH network's seed-mean error")
