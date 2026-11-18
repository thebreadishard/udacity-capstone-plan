"""The carried network's stated error and its licence, pinned whole on the carried records (`m08/accuracy.py`, `m08/licence.py`): every
family's value on both hold-outs under both quantities, the licensed families and the statement as certificates print it. A change of the
quantity the licence reads, of a record or of the wording shows here first. The records are read as JSON; no model file is loaded.

Pinned on version 1.4, carried since 17 Nov 2026 (chain v14_clean's three seeds; the registry says which version is carried), read on
the product's error as decision 65 has since its amendment of 16 Nov 2026; hold-out (b) holds 40 molecules for this version."""
from __future__ import annotations

import json
import sys

from pin_tools import PLAN

sys.path.insert(0, str(PLAN / "modules" / "08_industry_synthesis"))
from m08 import accuracy as A
from m08 import licence

VERSION = "1.4"
RECORDS = [f"E7_rungC_v14s3clean_c00_control_{kind}_seed{s}.json" for kind in ("eval_clean", "a8read") for s in range(3)]
FIRST_ORDER = {"a": {"ring-ip": (1.55, [1.77, 1.52, 1.37]), "CH-stretch": (1.15, [1.34, 1.19, 0.92]), "CH-oop": (2.22, [2.22, 2.1, 2.35]),
                     "other": (2.91, [2.79, 3.1, 2.84]), "coupling_ratio": (0.147, [0.15, 0.147, 0.143])},
               "b": {"ring-ip": (1.64, [1.53, 1.49, 1.89]), "CH-stretch": (2.02, [2.32, 2.2, 1.55]), "CH-oop": (1.72, [1.8, 1.96, 1.41]),
                     "other": (3.68, [3.2, 4.15, 3.7]), "coupling_ratio": (0.17, [0.168, 0.164, 0.177])}}
N_MOLECULES = {"a": 8, "b": 40}
PRODUCT_RECORD = "E7_rungC_v14s3clean_c00_control_product_error.json"
WITH_BANDS = {"a": {"ring-ip": 8, "CH-stretch": 8, "CH-oop": 5, "other": 8}, "b": {"ring-ip": 40, "CH-stretch": 40, "CH-oop": 8, "other": 40}}
PRODUCT = {"a": {"ring-ip": (1.17, [0.9, 1.41], 199), "CH-stretch": (0.8, [0.44, 1.2], 73), "CH-oop": (1.86, [0.93, 3.2], 46),
                 "other": (2.38, [1.45, 3.19], 156)},
           "b": {"ring-ip": (1.22, [1.09, 1.34], 1194), "CH-stretch": (1.67, [1.37, 1.95], 410), "CH-oop": (1.26, [0.98, 1.59], 84),
                 "other": (2.1, [1.88, 2.34], 1258)}}
CROSSING = [("a", "CH-oop"), ("a", "other")]
STATEMENT = ("licensed at the DFT proxy: ring-ip (1.17 / 1.22), CH-stretch (0.8 / 1.67), CH-oop (1.86 / 1.26), other (2.38 / 2.1); not "
             "licensed: none — error of the corrected band positions of the seed-mean correction on hold-outs (a) / (b) in cm⁻¹ against 3 "
             "(decision 65 as amended on 16 Nov 2026); CH-oop on hold-out (a) rests on 5 of the hold-out's 8 molecules (the others have no "
             "such band): the 95 % interval of a bootstrap over molecules is 0.93–3.2 cm⁻¹ and crosses the line (96 % of the resamples lie "
             "under it); other on hold-out (a) rests on 8 molecules: the 95 % interval of a bootstrap over molecules is 1.45–3.19 cm⁻¹ and "
             "crosses the line (93 % of the resamples lie under it); the first-order diagonal error of each seed's correction, averaged over "
             "the seeds, which the licence read until then: ring-ip (1.55 / 1.64), CH-stretch (1.15 / 2.02), CH-oop (2.22 / 1.72), other "
             "(2.91 / 3.68); no coupled-cluster licence")


def test_the_carried_versions_read_outs_per_seed_and_their_means():
    acc = A.carried_accuracy()
    assert acc["version"] == VERSION and acc["sources"] == [*RECORDS, PRODUCT_RECORD]
    for h, rows in FIRST_ORDER.items():
        got = acc["holdouts"][h]
        assert got["n_molecules"] == N_MOLECULES[h]
        assert {q: (r["mean"], r["seeds"]) for q, r in got["readouts"].items()} == rows
        assert {f: (p["rms"], p["interval"], p["n_modes"]) for f, p in got["product"].items()} == PRODUCT[h]
        assert all(p["n_molecules"] == N_MOLECULES[h] and p["within_target"] for p in got["product"].values())
        assert {f: p["n_molecules_with_modes"] for f, p in got["product"].items()} == WITH_BANDS[h]
    crossing = [(h, f) for h in PRODUCT for f, p in acc["holdouts"][h]["product"].items() if p["interval_crosses_line"]]
    assert crossing == CROSSING and acc["licence_quantity"] == "product"


def test_the_carried_versions_licence():
    s = licence.state()
    assert s["licensed_families"] == ["ring-ip", "CH-stretch", "CH-oop", "other"] and s["line_cm"] == 3.0 and s["quantity"] == "product"
    assert s["errors"] == {f: {h: PRODUCT[h][f][0] for h in PRODUCT} for f in PRODUCT["a"]}
    assert s["first_order_errors"] == {f: {h: FIRST_ORDER[h][f][0] for h in FIRST_ORDER} for f in PRODUCT["a"]}
    assert s["statement"] == STATEMENT and len(s["caveats"]) == len(CROSSING) and all(c in STATEMENT for c in s["caveats"])
    assert s["rule"].startswith("decision 65 (29 Oct 2026, amended 16 Nov 2026): a mode family is licensed where the error of what the "
                                "product delivers — the error of the corrected band positions of the seed-mean correction")
    assert s["rule_source"] == "README.md, decision 65 as amended on 16 Nov 2026"


def carried_record() -> dict:
    """The carried version's product-error record, found where accuracy finds it: beside the registry's carried checkpoints."""
    path = A.product_error_path(tuple(A.model_key(m) for m in A.P.carried_models(A.NK.MEASUREMENT)))
    if path.name != PRODUCT_RECORD:
        raise AssertionError(f"the carried version's record is {path.name}, the pin's {PRODUCT_RECORD}")
    return json.loads(path.read_text(encoding="utf-8"))


def test_the_carried_record_names_what_it_was_read_on():
    """The checkpoints by hash, every label file by hash, and the run itself: its start, end, seconds and peak memory."""
    rec = carried_record()
    assert sorted(rec["model_sha16"]) == sorted(rec["models"]) and all(len(h) == 16 for h in rec["model_sha16"].values())
    assert rec["labels"] == {"kind": "analytic", "files": ["hessian_b3lyp_analytic.npz", "hessian_wb97x_analytic.npz"]}
    for h, n in N_MOLECULES.items():
        hashes = rec["holdouts"][h]["label_sha16"]
        assert list(hashes) == rec["holdouts"][h]["ids"] and len(hashes) == n
        assert all(sorted(v) == rec["labels"]["files"] and all(len(x) == 16 for x in v.values()) for v in hashes.values())
    assert set(rec["run"]) == {"started", "ended", "seconds", "peak_memory_gb", "threads"} and 0 < rec["run"]["peak_memory_gb"] < 3.0
    assert rec["checks"]["first_order_reproduces_evaluation_records"]["largest_difference_cm"] < 0.005


def test_the_carried_record_agrees_with_the_package():
    """The second route: aromir's own code on the stored Hessians with v1.4's measurement networks, in the corpus atom order
    (probes/results_m1/aromir_v14_release_2026-11-18/product_error.py, 18 Nov 2026), agrees with the carried read."""
    rec = carried_record()
    package = rec["checks"]["agrees_with_package"]
    assert package["source"] == "probes/results_m1/aromir_v14_release_2026-11-18/product_error.json"
    assert package["largest_difference_cm"] < 0.01
