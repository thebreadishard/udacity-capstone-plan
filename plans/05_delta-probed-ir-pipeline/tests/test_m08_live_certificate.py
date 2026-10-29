"""The live certificate (`modules/08_industry_synthesis/m08/live_certificate.py`, TASKS 146 build step 4) without the website export: the
evaluation records of the network that ran, its measured error as chain 35's read reports it (the records are read as JSON; no carried
model's file is loaded), and the band table on the frozen corpus's benzene with the transfer pin's model. The whole certificate against the
export's is in module 08's own tests, which read the export."""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import numpy as np
import pytest

from pin_tools import DATA, PIN_CORPUS, PLAN, require_frozen_corpus

sys.path.insert(0, str(PLAN / "modules" / "08_industry_synthesis"))
from m08 import live_certificate as LC
from m08 import pipeline as P

PIN_MODEL = DATA / "rungC_cc_pin_model.pt"
BENZENE = "A_8448043181"
V13 = tuple(f"E7_rungC_chain35_analytic_model_n750_seed{s}.pt" for s in range(3))
ZERO = np.zeros((36, 36))


@pytest.fixture(scope="module")
def accuracy() -> dict:
    return LC.network_accuracy(LC.evaluation_records(V13))


def test_each_model_has_its_one_evaluation_record():
    assert [p.name for p in LC.evaluation_records(V13)] == [f"E7_rungC_chain35_analytic_eval_frozenb_seed{s}.json" for s in range(3)]


@pytest.mark.parametrize("name, match", [("rungC_cc_pin_model.pt", "not a rung-C model file name"),
                                         ("E7_rungC_nochain_model_n750_seed0.pt", "0 evaluation records")])
def test_a_model_without_exactly_one_record_is_refused(name, match):
    with pytest.raises(ValueError, match=match):
        LC.evaluation_records((name,))


def test_the_measured_error_is_chain_35s_read(accuracy):
    """The seed means of `out/E7_rungC_chain35_read.md` (28 Oct 2026), which the model registry's note for v1.3 repeats."""
    mean = {h: {q: v["mean"] for q, v in accuracy["holdouts"][h]["readouts"].items()} for h in ("a", "b")}
    assert mean["a"] == {"ring-ip": 1.66, "CH-stretch": 1.15, "CH-oop": 1.99, "other": 3.35, "coupling_ratio": 0.172}
    assert mean["b"] == {"ring-ip": 2.12, "CH-stretch": 2.5, "CH-oop": 2.7, "other": 3.89, "coupling_ratio": 0.263}
    a = accuracy["holdouts"]["a"]["readouts"]
    assert a["other"]["within_target"] is False and a["ring-ip"]["within_target"] is True and a["CH-stretch"]["target"] is None
    assert len(a["other"]["seeds"]) == 3 and accuracy["holdouts"]["a"]["shape"]["n_molecules"] == 10


@pytest.fixture
def result(tmp_path) -> Path:
    require_frozen_corpus()
    d = tmp_path / BENZENE
    shutil.copytree(PIN_CORPUS / "molecules" / BENZENE, d)
    return d


def record(d: Path, dH: np.ndarray, seeds: list[np.ndarray]) -> None:
    """The folder as the pipeline leaves it: the correction saved and its spectrum recorded (the record's other fields are not read here)."""
    P.save_correction(d, dH, seeds, (PIN_MODEL,) * len(seeds))
    P.write_json(d / "pipeline.json", {"admission": {"models": [{"path": str(PIN_MODEL)}] * len(seeds)}, "spectra": P.spectra(d, dH, seeds)})


def test_a_zero_correction_pairs_each_band_with_its_own_b3lyp_mode(result, accuracy):
    record(result, ZERO, [ZERO])
    rows = LC.bands(LC.load_result(result), accuracy, {})
    assert len(rows) == 30 and all(b["network_cm"] == b["b3lyp_cm"] for b in rows)
    assert [b["network_cm"] for b in rows] == sorted(b["network_cm"] for b in rows)
    assert sum(b["family"] == "CH-stretch" for b in rows) == 6 and {b["family"] for b in rows} <= {"ring-ip", "CH-stretch", "CH-oop", "other"}
    assert all(b["error_cm"]["a"] == accuracy["holdouts"]["a"]["readouts"][b["family"]]["mean"] for b in rows)
    baseline = json.loads((result / "pipeline.json").read_text(encoding="utf-8"))["spectra"]["baseline"]["sticks"]
    assert [b["baseline_cm"] for b in rows] == [s["omega_cm"] for s in baseline]


def test_the_bands_carry_the_recorded_positions_and_seed_ranges(result, accuracy):
    dH, seeds = P.correction((PIN_MODEL, PIN_MODEL), result)
    record(result, dH, seeds)
    r = LC.load_result(result)
    rows = LC.bands(r, accuracy, {"CH-stretch": {"u_band": 9.9}})
    assert [b["network_cm"] for b in rows] == [s["omega_cm"] for s in r.record["spectra"]["network"]["sticks"]]
    assert all(b["seed_range_cm"] == [b["network_cm"]] * 2 for b in rows)
    assert {b["u_band_cm"] for b in rows if b["lab_region"] == "CH-stretch"} == {9.9}


def test_a_record_that_is_not_its_correction_is_refused(result, accuracy):
    record(result, ZERO, [ZERO])
    rec = json.loads((result / "pipeline.json").read_text(encoding="utf-8"))
    rec["spectra"]["network"]["sticks"][5]["omega_cm"] += 1.0
    P.write_json(result / "pipeline.json", rec)
    with pytest.raises(RuntimeError, match="not the one H_low"):
        LC.bands(LC.load_result(result), accuracy, {})


def test_a_correction_of_other_models_is_refused(result):
    record(result, ZERO, [ZERO])
    P.save_correction(result, ZERO, [ZERO], (Path("other_model.pt"),))
    with pytest.raises(RuntimeError, match="names other models"):
        LC.load_result(result)
