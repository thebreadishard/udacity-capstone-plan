"""The live certificate (`modules/08_industry_synthesis/m08/live_certificate.py`, TASKS 146 build step 4) without the website export: the
evaluation records of the network that ran, its measured error as chain 35's read reports it (the records are read as JSON; no carried
model's file is loaded), and the band table on the frozen corpus's benzene with the transfer pin's model. The whole certificate against the
export's is in module 08's own tests, which read the export."""
from __future__ import annotations

import copy
import json
import shutil
import sys
from pathlib import Path

import numpy as np
import pytest

from pin_tools import DATA, PIN_CORPUS, PLAN, require_frozen_corpus

sys.path.insert(0, str(PLAN / "modules" / "08_industry_synthesis"))
from m08 import accuracy as A
from m08 import licence
from m08 import live_certificate as LC
from m08 import pipeline as P

PIN_MODEL = DATA / "rungC_cc_pin_model.pt"
BENZENE = "A_8448043181"
V13 = tuple(f"E7_rungC_chain35_analytic_model_n750_seed{s}.pt" for s in range(3))
ZERO = np.zeros((36, 36))


@pytest.fixture(scope="module")
def accuracy() -> dict:
    return A.network_accuracy(A.evaluation_records(V13))


def test_each_model_has_its_one_evaluation_record():
    assert [p.name for p in A.evaluation_records(V13)] == [f"E7_rungC_chain35_analytic_eval_frozenb_seed{s}.json" for s in range(3)]


@pytest.mark.parametrize("name, match", [("rungC_cc_pin_model.pt", "not a rung-C model file name"),
                                         ("E7_rungC_nochain_model_n750_seed0.pt", "0 evaluation records")])
def test_a_model_without_exactly_one_record_is_refused(name, match):
    with pytest.raises(ValueError, match=match):
        A.evaluation_records((name,))


def test_the_measured_error_is_chain_35s_read(accuracy):
    """The seed means of `out/E7_rungC_chain35_read.md` (28 Oct 2026), which the model registry's note for v1.3 repeats."""
    mean = {h: {q: v["mean"] for q, v in accuracy["holdouts"][h]["readouts"].items()} for h in ("a", "b")}
    assert mean["a"] == {"ring-ip": 1.66, "CH-stretch": 1.15, "CH-oop": 1.99, "other": 3.35, "coupling_ratio": 0.172}
    assert mean["b"] == {"ring-ip": 2.12, "CH-stretch": 2.5, "CH-oop": 2.7, "other": 3.89, "coupling_ratio": 0.263}
    a = accuracy["holdouts"]["a"]["readouts"]
    assert a["other"]["within_target"] is False and a["ring-ip"]["within_target"] is True and a["CH-stretch"]["target"] == 3.0
    assert len(a["other"]["seeds"]) == 3 and accuracy["holdouts"]["a"]["shape"]["n_molecules"] == 10


def test_the_licence_follows_the_error_of_the_files_that_ran(accuracy):
    """Decision 65: a family is licensed where its seed-mean error is within 3 cm⁻¹ on both hold-outs."""
    s = licence.state(accuracy)
    assert s["licensed_families"] == ["ring-ip", "CH-stretch", "CH-oop"] and "not licensed: other (3.35 / 3.89)" in s["statement"]


def test_the_clean_hold_out_a_replaces_a_and_keeps_the_licence():
    """TASKS 157 (the user, 30 Oct 2026): hold-out (a) read on the eight molecules never trained on under any id."""
    clean = A.clean_a_records(V13)
    assert [p.name for p in clean] == [f"E7_rungC_chain35_analytic_a8read_seed{s}.json" for s in range(3)]
    acc = A.network_accuracy(A.evaluation_records(V13), clean)
    mean = {h: {q: v["mean"] for q, v in acc["holdouts"][h]["readouts"].items() if q != "coupling_ratio"} for h in ("a", "b")}
    assert mean["a"] == {"ring-ip": 1.77, "CH-stretch": 1.19, "CH-oop": 2.17, "other": 3.62}
    assert mean["b"] == {"ring-ip": 2.12, "CH-stretch": 2.5, "CH-oop": 2.7, "other": 3.89}
    assert acc["holdouts"]["a"]["n_molecules"] == 8 and acc["holdouts"]["a"]["description"] == A.CLEAN_A
    assert licence.state(acc)["licensed_families"] == ["ring-ip", "CH-stretch", "CH-oop"]


def test_clean_reads_for_some_models_only_are_refused():
    assert A.clean_a_records(("E7_rungC_nochain_model_n750_seed0.pt",)) is None
    with pytest.raises(ValueError, match="some models only"):
        A.clean_a_records((V13[0], "E7_rungC_nochain_model_n750_seed1.pt"))


def test_a_family_on_the_line_is_licensed_and_one_above_it_is_not(accuracy):
    acc = copy.deepcopy(accuracy)
    for h in ("a", "b"):
        acc["holdouts"][h]["readouts"]["other"]["mean"] = 3.0
    acc["holdouts"]["b"]["readouts"]["CH-oop"]["mean"] = 3.01
    assert licence.state(acc)["licensed_families"] == ["ring-ip", "CH-stretch", "other"]


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
    rows = LC.bands(LC.load_result(result), accuracy, {}, ["ring-ip"])
    assert len(rows) == 30 and all(b["network_cm"] == b["b3lyp_cm"] for b in rows)
    assert [b["network_cm"] for b in rows] == sorted(b["network_cm"] for b in rows)
    assert all(b["licensed"] == (b["family"] == "ring-ip") for b in rows)
    assert sum(b["family"] == "CH-stretch" for b in rows) == 6 and {b["family"] for b in rows} <= {"ring-ip", "CH-stretch", "CH-oop", "other"}
    assert all(b["error_cm"]["a"] == accuracy["holdouts"]["a"]["readouts"][b["family"]]["mean"] for b in rows)
    baseline = json.loads((result / "pipeline.json").read_text(encoding="utf-8"))["spectra"]["baseline"]["sticks"]
    assert [b["baseline_cm"] for b in rows] == [s["omega_cm"] for s in baseline]


def test_the_bands_carry_the_recorded_positions_and_seed_ranges(result, accuracy):
    dH, seeds = P.correction((PIN_MODEL, PIN_MODEL), result)
    record(result, dH, seeds)
    r = LC.load_result(result)
    rows = LC.bands(r, accuracy, {"CH-stretch": {"u_band": 9.9}}, [])
    assert [b["network_cm"] for b in rows] == [s["omega_cm"] for s in r.record["spectra"]["network"]["sticks"]]
    assert all(b["seed_range_cm"] == [b["network_cm"]] * 2 for b in rows)
    assert {b["u_band_cm"] for b in rows if b["lab_region"] == "CH-stretch"} == {9.9}


def with_mode_at(H: np.ndarray, masses: np.ndarray, k: int, cm: float) -> np.ndarray:
    """H with its k-th vibrational mode (ascending) moved to `cm`, its shape kept."""
    import rungC_intensities as RINT

    s = np.sqrt(np.repeat(masses * RINT.AMU2AU, 3))
    lam, V = np.linalg.eigh(H / np.outer(s, s))
    vib = np.flatnonzero(np.abs(np.sign(lam) * np.sqrt(np.abs(lam)) * RINT.HARTREE2CM) > 1.0)
    lam[vib[k]] = (cm / RINT.HARTREE2CM) ** 2
    return np.outer(s, s) * ((V * lam) @ V.T)


def test_a_mode_lifted_over_the_line_keeps_its_partner(result, accuracy):
    """Module 06's candidate: a B3LYP rotor under the 20 cm⁻¹ line that the network lifts over it, and one seed leaves under it."""
    masses = np.asarray(json.loads((result / "geometry.json").read_text(encoding="utf-8"))["masses_amu"], float)
    hessian = result / P.RI.LOW_HESSIAN
    with np.load(hessian) as z:
        arrays = {k: z[k] for k in z.files}
    H = with_mode_at(arrays["H_projected"], masses, 0, 10.0)
    np.savez(hessian, **(arrays | {"H_projected": H}))
    seeds = [with_mode_at(H, masses, 0, cm) - H for cm in (37.0, 19.0)]
    record(result, np.mean(seeds, 0), seeds)
    rows = LC.bands(LC.load_result(result), accuracy, {}, [])
    lifted = [b for b in rows if b["baseline_cm"] is None]
    assert len(rows) == 30 and len(lifted) == 1
    assert lifted[0]["b3lyp_cm"] == 10.0 and lifted[0]["network_cm"] == round(float(np.sqrt((37.0 ** 2 + 19.0 ** 2) / 2)), 1)
    assert lifted[0]["seed_range_cm"] == [19.0, 37.0]
    assert lifted[0]["family"] == "other" and lifted[0]["error_cm"]["a"] == accuracy["holdouts"]["a"]["readouts"]["other"]["mean"]
    assert all(b["seed_range_cm"][0] == b["seed_range_cm"][1] == b["network_cm"] for b in rows if b is not lifted[0])
    assert "— (B3LYP under 20 cm⁻¹)" in "\n".join(LC._band_lines({"bands": rows}))


def test_a_record_that_is_not_its_correction_is_refused(result, accuracy):
    record(result, ZERO, [ZERO])
    rec = json.loads((result / "pipeline.json").read_text(encoding="utf-8"))
    rec["spectra"]["network"]["sticks"][5]["omega_cm"] += 1.0
    P.write_json(result / "pipeline.json", rec)
    with pytest.raises(RuntimeError, match="not the one H_low"):
        LC.bands(LC.load_result(result), accuracy, {}, [])


def test_a_correction_of_other_models_is_refused(result):
    record(result, ZERO, [ZERO])
    P.save_correction(result, ZERO, [ZERO], (Path("other_model.pt"),))
    with pytest.raises(RuntimeError, match="names other models"):
        LC.load_result(result)
