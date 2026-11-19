"""The live certificate (`modules/08_industry_synthesis/m08/live_certificate.py`, TASKS 146 build step 4) without the website export: the
evaluation records of the network that ran, its first-order read-outs as chain 35's read reports them and the product's error its
licence and bands state (the records are read as JSON; no carried model's file is loaded), and the band table on the frozen corpus's
benzene with the transfer pin's model. The whole certificate against the export's is in module 08's own tests, which read the export."""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import numpy as np
import pytest

from pin_tools import DATA, PIN_CORPUS, PLAN, require_frozen_corpus
from test_m08_own_spread import UNMOVED

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
    return A.accuracy_of(V13)


def test_each_model_has_its_one_evaluation_record():
    assert [p.name for p in A.evaluation_records(V13)] == [f"E7_rungC_chain35_analytic_eval_frozenb_seed{s}.json" for s in range(3)]


@pytest.mark.parametrize("name, match", [("rungC_cc_pin_model.pt", "not a rung-C model file name"),
                                         ("E7_rungC_nochain_model_n750_seed0.pt", "0 evaluation records")])
def test_a_model_without_exactly_one_record_is_refused(name, match):
    with pytest.raises(ValueError, match=match):
        A.evaluation_records((name,))


def test_the_first_order_read_outs_are_chain_35s_read():
    """The seed means of `out/E7_rungC_chain35_read.md` (28 Oct 2026), which the model registry's note for v1.3 repeats: the first-order
    quantity on hold-out (a) as stored (ten molecules), which no licence is read on."""
    accuracy = A.network_accuracy(A.evaluation_records(V13))
    mean = {h: {q: v["mean"] for q, v in accuracy["holdouts"][h]["readouts"].items()} for h in ("a", "b")}
    assert mean["a"] == {"ring-ip": 1.66, "CH-stretch": 1.15, "CH-oop": 1.99, "other": 3.35, "coupling_ratio": 0.172}
    assert mean["b"] == {"ring-ip": 2.12, "CH-stretch": 2.5, "CH-oop": 2.7, "other": 3.89, "coupling_ratio": 0.263}
    a = accuracy["holdouts"]["a"]["readouts"]
    assert a["other"]["within_target"] is False and a["ring-ip"]["within_target"] is True and a["CH-stretch"]["target"] == 3.0
    assert len(a["other"]["seeds"]) == 3 and accuracy["holdouts"]["a"]["shape"]["n_molecules"] == 10
    with pytest.raises(A.NoProductError):
        licence.state(accuracy)


def test_the_licence_follows_the_product_error_of_the_files_that_ran(accuracy):
    """Decision 65 as amended on 16 Nov 2026: a family is licensed where the error of the corrected band positions of the seed-mean
    correction is within 3 cm⁻¹ on both hold-outs."""
    s = licence.state(accuracy)
    assert s["licensed_families"] == ["ring-ip", "CH-stretch", "CH-oop", "other"] and "other (2.78 / 2.77); not licensed: none" in s["statement"]
    assert "other on hold-out (a) rests on 8 molecules" in s["statement"] and "1.68–3.76 cm⁻¹" in s["statement"]


def test_the_clean_hold_out_a_replaces_a_in_both_quantities(accuracy):
    """TASKS 157 (the user, 30 Oct 2026): hold-out (a) read on the eight molecules never trained on under any id."""
    clean = A.clean_a_records(V13)
    assert [p.name for p in clean] == [f"E7_rungC_chain35_analytic_a8read_seed{s}.json" for s in range(3)]
    acc = A.network_accuracy(A.evaluation_records(V13), clean)
    mean = {h: {q: v["mean"] for q, v in acc["holdouts"][h]["readouts"].items() if q != "coupling_ratio"} for h in ("a", "b")}
    assert mean["a"] == {"ring-ip": 1.77, "CH-stretch": 1.19, "CH-oop": 2.17, "other": 3.62}
    assert mean["b"] == {"ring-ip": 2.12, "CH-stretch": 2.5, "CH-oop": 2.7, "other": 3.89}
    assert acc["holdouts"]["a"]["n_molecules"] == 8 and acc["holdouts"]["a"]["description"] == A.CLEAN_A
    assert accuracy["holdouts"]["a"]["readouts"] == acc["holdouts"]["a"]["readouts"] and accuracy["holdouts"]["a"]["description"] == A.CLEAN_A
    assert {v["n_molecules"] for v in accuracy["holdouts"]["a"]["product"].values()} == {8}


def test_clean_reads_for_some_models_only_are_refused():
    assert A.clean_a_records(("E7_rungC_nochain_model_n750_seed0.pt",)) is None
    with pytest.raises(ValueError, match="some models only"):
        A.clean_a_records((V13[0], "E7_rungC_nochain_model_n750_seed1.pt"))


@pytest.mark.parametrize("path, key", [
    ("C:\\Users\\x\\plans\\05_delta-probed-ir-pipeline\\modules\\05_support_predictor\\out\\v14\\m_model_n1_seed0.pt", "v14/m_model_n1_seed0.pt"),
    ("/home/x/plans/05_delta-probed-ir-pipeline/modules/05_support_predictor/out/m_model_n1_seed0.pt", "m_model_n1_seed0.pt"),
    ("out/v14/m_model_n1_seed0.pt", "v14/m_model_n1_seed0.pt"),
    (A.M05_OUT / "v14" / "m_model_n1_seed0.pt", "v14/m_model_n1_seed0.pt")])
def test_a_models_key_is_its_path_under_module_05s_out(path, key):
    assert A.model_key(path) == key


@pytest.mark.parametrize("path", ["m_model_n1_seed0.pt", "C:\\elsewhere\\m_model_n1_seed0.pt", str(A.M05_OUT)])
def test_a_path_outside_module_05s_out_has_no_key(path):
    with pytest.raises(ValueError, match="not a checkpoint under module 05's out/"):
        A.model_key(path)


def test_the_carried_version_is_read_by_the_registrys_key_under_out(monkeypatch):
    """v1.4's registry keys carry their folder (`v14/…_seed0.pt`); a look-up by file name alone raised KeyError (TASKS 264)."""
    keys = [f"v14/E7_rungC_x_model_n1_seed{s}.pt" for s in range(3)]
    monkeypatch.setattr(P, "carried_models", lambda kind: tuple(P.MR.OUT / k for k in keys))
    monkeypatch.setattr(P.MR, "read_status", lambda path: {k: {"version": "1.4"} for k in keys})
    assert A.carried_version() == "1.4"


@pytest.fixture
def v13_files() -> list[Path]:
    """v1.3's evaluation, clean hold-out (a) and product-error records as they lie in module 05's out/."""
    return [*A.evaluation_records(V13), *A.clean_a_records(V13), A.product_error_path(V13)]


def test_a_model_in_a_subfolder_finds_its_records_beside_it(tmp_path, monkeypatch, v13_files):
    """TASKS 264: v1.4's checkpoints lie in out/v14/, and their records beside them; a model directly in out/ reads out/ as before."""
    sub = tmp_path / "v14"
    sub.mkdir()
    for p in v13_files:
        shutil.copy(p, sub / p.name)
    shutil.copy(v13_files[0], tmp_path / v13_files[0].name)                    # a stray copy in out/ is not the subfolder model's record
    monkeypatch.setattr(A, "M05_OUT", tmp_path)
    keys = tuple(f"v14/{n}" for n in V13)
    assert A.evaluation_records(keys) == [sub / p.name for p in v13_files[:3]]
    assert A.clean_a_records(keys) == [sub / p.name for p in v13_files[3:6]]
    assert A.product_error_path(keys) == A.product_error_record(keys) == sub / v13_files[6].name
    assert A.evaluation_records(V13[:1]) == [tmp_path / v13_files[0].name]
    with pytest.raises(ValueError, match=r"0 evaluation records in .*v14"):
        A.evaluation_records(("v14/E7_rungC_nochain_model_n750_seed0.pt",))
    shutil.copy(v13_files[0], sub / v13_files[0].name.replace("_eval_", "_eval_again_"))
    with pytest.raises(ValueError, match=r"2 evaluation records in .*v14"):
        A.evaluation_records(keys[:1])
    with pytest.raises(ValueError, match="some models only"):
        A.clean_a_records((keys[0], "v14/E7_rungC_nochain_model_n750_seed1.pt"))
    with pytest.raises(ValueError, match="lie in 2 folders"):
        A.product_error_path((keys[0], V13[1]))


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
    rows = LC.bands(LC.load_result(result), accuracy, {}, ["ring-ip"], UNMOVED)
    assert len(rows) == 30 and all(b["network_cm"] == b["b3lyp_cm"] for b in rows)
    assert [b["network_cm"] for b in rows] == sorted(b["network_cm"] for b in rows)
    assert all(b["licensed"] == (b["family"] == "ring-ip") for b in rows)
    assert sum(b["family"] == "CH-stretch" for b in rows) == 6 and {b["family"] for b in rows} <= {"ring-ip", "CH-stretch", "CH-oop", "other"}
    assert all(b["error_cm"] == {h: accuracy["holdouts"][h]["product"][b["family"]]["rms"] for h in ("a", "b")} for b in rows)
    baseline = json.loads((result / "pipeline.json").read_text(encoding="utf-8"))["spectra"]["baseline"]["sticks"]
    assert [b["baseline_cm"] for b in rows] == [s["omega_cm"] for s in baseline]


def test_the_bands_carry_the_recorded_positions_and_seed_ranges(result, accuracy):
    dH, seeds = P.correction((PIN_MODEL, PIN_MODEL), result)
    record(result, dH, seeds)
    r = LC.load_result(result)
    rows = LC.bands(r, accuracy, {"CH-stretch": {"u_band": 9.9}}, [], UNMOVED)
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
    rows = LC.bands(LC.load_result(result), accuracy, {}, [], UNMOVED)
    lifted = [b for b in rows if b["baseline_cm"] is None]
    assert len(rows) == 30 and len(lifted) == 1
    assert lifted[0]["b3lyp_cm"] == 10.0 and lifted[0]["network_cm"] == round(float(np.sqrt((37.0 ** 2 + 19.0 ** 2) / 2)), 1)
    assert lifted[0]["seed_range_cm"] == [19.0, 37.0]
    assert lifted[0]["family"] == "other" and lifted[0]["error_cm"]["a"] == accuracy["holdouts"]["a"]["product"]["other"]["rms"]
    assert all(b["seed_range_cm"][0] == b["seed_range_cm"][1] == b["network_cm"] for b in rows if b is not lifted[0])
    # a record without the anharmonic step (pipeline 0.11, TASKS 211): every band harmonic, and the table says so in its columns
    lines = LC._band_lines({"bands": rows, "licence": {"quantity_name": A.QUANTITY_NAMES[A.PRODUCT]},
                            "positions": {"anharmonic": LC.POS.summary_of({})}})
    assert "— (B3LYP under 20 cm⁻¹)" in "\n".join(lines)
    assert ("| ω licensed | own spread of ω (cm⁻¹), under | error of the corrected band positions of the seed-mean correction of ω on "
            "(a) / (b), cm⁻¹ |") in lines[0]
    assert all("| no | 0.00, rotation 1 |" in line for line in lines[2:])


def test_a_record_that_is_not_its_correction_is_refused(result, accuracy):
    record(result, ZERO, [ZERO])
    rec = json.loads((result / "pipeline.json").read_text(encoding="utf-8"))
    rec["spectra"]["network"]["sticks"][5]["omega_cm"] += 1.0
    P.write_json(result / "pipeline.json", rec)
    with pytest.raises(RuntimeError, match="not the one H_low"):
        LC.bands(LC.load_result(result), accuracy, {}, [], UNMOVED)


def test_a_correction_of_other_models_is_refused(result):
    record(result, ZERO, [ZERO])
    P.save_correction(result, ZERO, [ZERO], (Path("other_model.pt"),))
    with pytest.raises(RuntimeError, match="names other models"):
        LC.load_result(result)


def test_hold_out_a_s_clean_description_is_the_version_s_own(tmp_path):
    """Demo review 4: the text said the two twins were trained on, which v1.4 (twins dropped) never did. The training record's
    --holdout-twins decides; v1.3's record predates the setting and kept them."""
    clean = A.clean_a_records(V13)
    assert {A.holdout_twins_setting(p) for p in clean} == {"keep"} and A.clean_a_description(clean) == A.CLEAN_A
    copies = [Path(shutil.copy(p, tmp_path / p.name)) for p in clean]
    with pytest.raises(FileNotFoundError, match="no training record"):
        A.clean_a_description(copies)
    stem = A._stem_seed(A._model_of(copies[0]))[0]
    (tmp_path / f"{stem}.json").write_text(json.dumps({"holdout_twins": "drop-any-charge"}), encoding="utf-8")
    assert A.clean_a_description(copies) == A.CLEAN_A_TWINS_DROPPED
    assert "clean too" in A.CLEAN_A_TWINS_DROPPED and "comparability with v1.3" in A.CLEAN_A_TWINS_DROPPED
    assert "TASKS" not in A.CLEAN_A + A.CLEAN_A_TWINS_DROPPED + A.CC_NOTE and "November 2026" not in A.CC_NOTE
    assert "measurement networks" in A.HOLDOUTS["b"]


def test_the_catalogue_line_names_the_export_s_source_and_the_analytic_row_beside_it():
    """Demo review 8: benzene's export lists the corpus's psi4 Hessian, 22.8 cm⁻¹ from the analytic route this run took; the line said
    'its export's B3LYP positions' without saying which, and nothing set the analytic row beside them."""
    mol = {"deck": {"engine": "psi4 1.11 (conda env qc, Windows)"}, "shape": {"hessian_source": "corpus/molecules/A_1/hessian_b3lyp.npz"}}
    source = LC.export_b3lyp_source(mol)
    assert source == "psi4 1.11 (conda env qc, Windows), corpus/molecules/A_1/hessian_b3lyp.npz" and LC.export_b3lyp_source({}) == "the export does not say"
    listed = {"id": "A_1", "name": "benzene", "rung": 5, "source": "website export", "export_b3lyp_source": source, "b3lyp_max_abs_diff_cm": 22.8,
              "analytic_b3lyp_max_abs_diff_cm": 0.0, "analytic_b3lyp_source": "corpus/molecules/A_1/hessian_b3lyp_analytic.npz"}
    line = LC._catalogue_line(listed)
    assert f"the export's B3LYP positions ({source}) lie within 22.8 cm⁻¹ of this run's" in line
    assert "the corpus's analytic B3LYP Hessian (corpus/molecules/A_1/hessian_b3lyp_analytic.npz), the route step 3 computes, within 0.0 cm⁻¹" in line
    older = {k: v for k, v in listed.items() if not k.startswith(("analytic", "export"))}
    assert "source not recorded in this certificate" in LC._catalogue_line(older) and "analytic" not in LC._catalogue_line(older)
    assert LC._catalogue_line(None) == "- catalogue: not listed"
    assert LC._max_abs_diff([1.0, 3.0], [2.9, 1.2]) == 0.2 and LC._max_abs_diff([1.0], [1.0, 2.0]) is None


@pytest.mark.parametrize("seconds, text", [(1.4, "1.4 s"), (754.0, "754 s = 13 min"), (4694.7, "4695 s = 1.30 h")])
def test_the_run_s_time_reads_with_sensible_precision(seconds, text):
    assert LC._duration(seconds) == text


def test_a_host_missing_from_the_price_table_is_not_priced_rather_than_refused():
    unpriced = {"steps_s": {"reuse": 0.5}} | LC.prices.price_of_run(0.5, "some-new-host")
    assert LC._cost_line(unpriced) == "- some-new-host (unknown): 0.5 s, not priced (machine not in the price table); steps reuse 0.5 s"
    priced = {"steps_s": {"low_level": 1261.5}} | LC.prices.price_of_run(1261.5, "Asus18")
    assert LC._cost_line(priced).startswith("- Asus18 (laptop): 1262 s = 21 min, € 0.00 ex VAT")


def test_the_cation_clause_says_the_cation_layer_was_left_out():
    from m08 import seen as S

    text = S.TEXT["cation_trained"]
    assert "training without the cation layer (about 50 cations, benzene's among them)" in text and "from 5.4 to 1.5" in text
    assert "training on benzene's cation raised" not in text
