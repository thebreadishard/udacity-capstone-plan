"""TASKS 288 in module 08, as aromir's certificate: while a version's invariance
record shows a spread above the licence line for molecules with a linear group, no band of such a molecule is licensed, each band and
the statement say why, and the positions are those printed without the rule; with no record such a molecule is 'not measured'; a
molecule without a linear group keeps its licence. The detector on the frozen corpus's geometries, the rule on made-up records, the
certificate on the frozen corpus's benzene after a zero correction with the detector's answer given. aromir's rule and sentences are
those of 07b215d (`tests/test_linear_group_licence.py` there for the cases ported)."""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
from pathlib import Path

import numpy as np
import pytest

from pin_tools import PIN_CORPUS, PLAN, require_frozen_corpus

sys.path.insert(0, str(PLAN / "modules" / "08_industry_synthesis"))
from m08 import accuracy as A
from m08 import invariance as INV
from m08 import licence
from m08 import live_certificate as LC
from m08 import pipeline as P

# isort: split
import e7_t2_sqm as T2  # module 05's code, on the path through m08.pipeline
import internal_coords as IC

BENZENE = "A_8448043181"
WITH_LINEAR = {"A_a848c04a21": "phenylacetylene", "B_17f1611949": "pyridine+CH3+ethynyl", "B_18c473d7dd": "naphthalene+F+CN",
               "A2_02f13355a2": "acridine+CN"}
WITHOUT_LINEAR = {BENZENE: "benzene", "A_fdc27f1bd1": "biphenyl", "A_8f6ed7c002": "styrene"}
V14 = "E7_rungC_v14s3clean_c00_control"
RELEASE = tuple(f"{V14}_release_model_n1132_seed{s}.pt" for s in range(3))
MEASUREMENT = tuple(f"{V14}_model_n1082_seed{s}.pt" for s in range(3))
V13 = tuple(f"E7_rungC_chain35_analytic_model_n750_seed{s}.pt" for s in range(3))
LINE = A.LICENCE_LINE_CM

# aromir's certificate.py at 07b215d, word for word
TOO_HIGH_NOTE = ("the molecule has a linear group, and molecules with one moved by up to 3.01 cm⁻¹ under a rotation, a mirror image or "
                 "another xyz listing, more than the licence line")
TOO_HIGH_REASON = ("the molecule has a linear group (an angle near 180°, as in a nitrile or an alkyne), and the measured spread under a "
                   "rotation, a mirror image or another xyz listing of the atoms for molecules with one (3.01 cm⁻¹, from the release's "
                   "invariance record) exceeds the licence line of 3 cm⁻¹, so the network's correction for this molecule is not licensed; "
                   "the corrected positions are still printed")
NOT_MEASURED_NOTE = ("the molecule has a linear group, and the spread of molecules with one under a rotation, a mirror image or another "
                     "xyz listing was not measured for this release")
NOT_MEASURED_REASON = ("the molecule has a linear group (an angle near 180°, as in a nitrile or an alkyne), and the spread under a "
                       "rotation, a mirror image or another xyz listing of the atoms was not measured for this release on a molecule with "
                       "one, so the network's correction for this molecule is not licensed; the corrected positions are still printed")


def geometry(mol_id: str) -> tuple[list[str], np.ndarray]:
    g = json.loads((PIN_CORPUS / "molecules" / mol_id / "geometry.json").read_text(encoding="utf-8"))
    return g["symbols"], np.asarray(g["coords_bohr"], float)


@pytest.mark.parametrize("mol_id", [*WITH_LINEAR, *WITHOUT_LINEAR])
def test_a_linear_group_is_a_linear_angle_among_the_networks_internal_coordinates(mol_id):
    symbols, x = geometry(mol_id)
    assert INV.has_linear_group(symbols, x) == (mol_id in WITH_LINEAR)
    canonical = T2.internals(symbols, x, IC.PrimitiveSettings(angle_choice="canonical"))[1]
    assert any(t[0] == "linear" for t in canonical) == (mol_id in WITH_LINEAR)          # the angle choice does not change the answer


def spread(with_linear: float | None, without: float | None = 0.5) -> dict:
    return {INV.WITH: with_linear, "n_with_linear_group": 0 if with_linear is None else 3, INV.WITHOUT: without,
            "n_without_linear_group": 0 if without is None else 4, "n_trials": 8}


def made_up(rotation: float | None, mirror: float | None = 1.0, listing: float | None = 1.0, without: float = 0.5) -> dict:
    return {"network_version": "x", "rotation": spread(rotation, without), "mirror_image": spread(mirror, without),
            "xyz_atom_order": spread(listing, without)}


def record_with(*, linear_group: bool, rotation: float | None, mirror: float | None, listing: float | None) -> dict:
    """A record whose group of the molecule has the given spreads and whose other group stays at 0.5 cm⁻¹."""
    def change(value: float | None) -> dict:
        return spread(value, 0.5) if linear_group else spread(0.5, value)
    return {"network_version": "x", "rotation": change(rotation), "mirror_image": change(mirror), "xyz_atom_order": change(listing)}


def test_the_licence_stands_at_the_line_and_is_withheld_above_it_word_for_word():
    assert INV.withheld_by_spread(made_up(3.0, 3.0, 3.0), LINE, linear_group=True) is None
    got = INV.withheld_by_spread(made_up(3.01), LINE, linear_group=True)
    assert got == INV.Withheld(spread_cm=3.01, note=TOO_HIGH_NOTE, reason=TOO_HIGH_REASON)
    assert INV.withheld_by_spread(made_up(3.01), LINE, linear_group=False) is None


@pytest.mark.parametrize(("mirror", "listing", "change"), [(3.5, 2.5, "a mirror image"), (2.5, 3.5, "another xyz listing")])
@pytest.mark.parametrize("linear_group", [True, False], ids=["with", "without"])
def test_a_change_other_than_the_rotation_above_the_line_withholds_the_licence(mirror, listing, change, linear_group):
    got = INV.withheld_by_spread(record_with(linear_group=linear_group, rotation=2.5, mirror=mirror, listing=listing), LINE,
                                 linear_group=linear_group)
    assert got is not None and got.spread_cm == 3.5
    if not linear_group:
        assert got.note == f"molecules without a linear group moved by up to 3.50 cm⁻¹ under {change}, more than the licence line"
        assert got.reason == (f"the molecule has no linear group, and the measured spread under {change} for molecules without one "
                              "(3.50 cm⁻¹, from the release's invariance record) exceeds the licence line of 3 cm⁻¹, so the network's "
                              "correction for this molecule is not licensed; the corrected positions are still printed")


def test_a_tie_names_the_first_change():
    assert INV.group_spread(record_with(linear_group=False, rotation=1.0, mirror=3.5, listing=3.5), linear_group=False) == \
        INV.GroupSpread(spread_cm=3.5, change="a mirror image", complete=True)


def test_a_linear_group_not_measured_is_not_licensed_word_for_word():
    for record in (None, made_up(None), made_up(1.0, None, 1.0)):
        assert INV.withheld_by_spread(record, LINE, linear_group=True) == INV.UNMEASURED
    expected = INV.Withheld(spread_cm=None, note=NOT_MEASURED_NOTE, reason=NOT_MEASURED_REASON)
    assert expected == INV.UNMEASURED
    assert INV.withheld_by_spread(made_up(3.01, None, 1.0), LINE, linear_group=True).spread_cm == 3.01   # over the line on what was measured


@pytest.mark.parametrize("record", [None, "no molecule without one listed"])
def test_a_molecule_without_a_linear_group_keeps_its_licence_where_it_was_not_measured(record):
    given = None if record is None else record_with(linear_group=False, rotation=0.0, mirror=2.5, listing=None)
    assert INV.withheld_by_spread(given, LINE, linear_group=False) is None


def test_the_rule_reads_every_change_of_the_record():
    four = made_up(1.0) | {"a fourth change": spread(1.0)}
    with pytest.raises(ValueError, match="a fourth change"):
        INV.group_spread(four, linear_group=True)


def test_the_licence_rule_states_the_condition_in_aromirs_words():
    assert ("molecules with a linear group moved by no more than the licence line under a rotation, a mirror image or another xyz "
            "listing of the atoms in the release's invariance record") in licence.RULE
    assert "molecules without a linear group moved by no more than the licence line" in licence.RULE


def test_the_v14_record_is_aromirs_beside_the_release_networks_it_measured():
    record = json.loads(INV.record_path(tuple(f"v14/{n}" for n in RELEASE)).read_text(encoding="utf-8"))
    assert record["network_version"] == "1.4" and record["provenance"]["aromir_commit"].startswith("331c87f")
    assert sorted(record["provenance"]["networks"]) == list(RELEASE)
    assert INV.group_spread(record, linear_group=True) == INV.GroupSpread(spread_cm=11.2, change="a rotation", complete=True)
    assert INV.group_spread(record, linear_group=False) == INV.GroupSpread(spread_cm=2.85, change="another xyz listing", complete=True)
    for name, digest in record["provenance"]["networks"].items():
        path = A.M05_OUT / "v14" / name
        if path.is_file():                                                   # the checkpoints are not in git
            assert hashlib.sha256(path.read_bytes()).hexdigest() == digest
    assert INV.record_path(tuple(f"v14/{n}" for n in MEASUREMENT)).is_file() is False


def test_a_record_of_other_networks_is_refused():
    keys = tuple(f"v14/{n}" for n in RELEASE)
    record = json.loads(INV.record_path(keys).read_text(encoding="utf-8"))
    right = {n: record["provenance"]["networks"][n][:16] for n in RELEASE}
    assert INV.load_record(keys, right) == record
    with pytest.raises(ValueError, match="other files"):
        INV.load_record(keys, right | {RELEASE[0]: "0" * 16})
    with pytest.raises(ValueError, match="ran"):
        INV.load_record(keys[:2], right)


class NoCatalog:
    def find(self, smiles: str) -> None:
        return None

    def u_band(self, species: str) -> dict:
        return {}


def benzene_folder(tmp_path: Path, admission: dict, n_models: int) -> Path:
    """Benzene's folder as the pipeline leaves it after a zero correction by the admission's models."""
    require_frozen_corpus()
    d = tmp_path / BENZENE
    shutil.copytree(PIN_CORPUS / "molecules" / BENZENE, d)
    zero = np.zeros((36, 36))
    names = tuple(Path(m["path"]).name for m in admission["models"])
    P.save_correction(d, zero, [zero] * n_models, tuple(Path(n) for n in names))
    P.write_json(d / "pipeline.json", {"pipeline_version": P.PIPELINE_VERSION, "name": "benzene", "spectra": P.spectra(d, zero, [zero] * n_models),
                                       "admission": {"smiles": "c1ccccc1", "formula": "C6H6", "n_atoms": 12, "elements": ["C", "H"],
                                                     "training_atoms": [6, 40], "inside_training_sizes": True} | admission,
                                       "seconds": {"low_level": 60.0}, "provenance": {"host": "laptop", "commit": "0" * 40, "dirty": False},
                                       "deck": {"sha16": "d" * 16}, "low_level": {"b3lyp": {"software": {"pyscf": "2.15.0"}}}})
    return d


def entries(names: tuple[str, ...], hashes: dict[str, str], version: str, folder: str = "") -> list[dict]:
    return [{"path": f"out/{folder}{n}", "sha16": hashes[n], "network": P.NETWORK, "version": version, "status": "carried"} for n in names]


@pytest.fixture
def v14_release(monkeypatch) -> dict:
    """v1.4's release networks that ran, with the hashes the invariance record names, and its measurement networks for the error bars.
    The checkpoints are not in git, so the training ids and the inner-validation share are given."""
    keys = tuple(f"v14/{n}" for n in RELEASE)
    measured = json.loads(INV.record_path(keys).read_text(encoding="utf-8"))["provenance"]["networks"]
    with open(A.product_error_path(tuple(f"v14/{n}" for n in MEASUREMENT)), encoding="utf-8") as f:
        product = json.load(f)["model_sha16"]
    monkeypatch.setattr(P, "train_ids", lambda models: set())
    monkeypatch.setattr(P, "inner_validation_share", lambda models: 0.15)
    released = [e | {P.NK.FIELD: P.NK.RELEASE} for e in entries(RELEASE, {n: h[:16] for n, h in measured.items()}, "1.4", "v14/")]
    return {"models": released, "measurement_models": entries(MEASUREMENT, product, "1.4", "v14/")}


def test_benzene_under_v14s_release_networks_keeps_its_licence(tmp_path, v14_release):
    c = LC.certificate(benzene_folder(tmp_path, v14_release, 3), NoCatalog())
    assert any(b["licensed"] for b in c["bands"]) and not any("licence_note" in b for b in c["bands"])
    assert "withheld" not in c["licence"] and "linear group" not in c["statement"]


def test_a_linear_group_under_v14s_release_networks_is_withheld_with_its_record(tmp_path, v14_release, monkeypatch):
    plain = LC.certificate(benzene_folder(tmp_path / "plain", v14_release, 3), NoCatalog())
    monkeypatch.setattr(INV, "has_linear_group", lambda symbols, coords: True)
    c = LC.certificate(benzene_folder(tmp_path / "linear", v14_release, 3), NoCatalog())
    note = TOO_HIGH_NOTE.replace("3.01", "11.20")
    reason = TOO_HIGH_REASON.replace("3.01", "11.20")
    assert c["licence"]["withheld"] == {"spread_cm": 11.2, "note": note, "reason": reason}
    assert c["statement"] == f"{plain['statement']} {reason[0].upper()}{reason[1:]}."
    assert not any(b["licensed"] for b in c["bands"]) and all(b["licence_note"] == note for b in c["bands"])
    unchanged = ("network_cm", "printed_cm", "b3lyp_cm", "baseline_cm", "km_mol", "seed_range_cm", "family")
    assert [{k: b[k] for k in unchanged} for b in c["bands"]] == [{k: b[k] for k in unchanged} for b in plain["bands"]]
    assert f"| no: {note} |" in LC.to_markdown(c)


def test_a_linear_group_of_a_version_without_a_record_is_not_measured(tmp_path, monkeypatch):
    with open(A.M05_OUT / f"E7_rungC_chain35_analytic{A.PRODUCT_SUFFIX}", encoding="utf-8") as f:
        hashes = json.load(f)["model_sha16"]
    monkeypatch.setattr(P, "train_ids", lambda models: set())
    monkeypatch.setattr(INV, "has_linear_group", lambda symbols, coords: True)
    c = LC.certificate(benzene_folder(tmp_path, {"models": entries(V13, hashes, "1.3")}, 3), NoCatalog())
    assert c["licence"]["withheld"] == {"spread_cm": None, "note": NOT_MEASURED_NOTE, "reason": NOT_MEASURED_REASON}
    assert not any(b["licensed"] for b in c["bands"]) and c["statement"].endswith(f"{NOT_MEASURED_REASON[0].upper()}{NOT_MEASURED_REASON[1:]}.")


@pytest.mark.parametrize("value", [3.0, 3.01])
def test_the_switch_at_the_line_on_the_certificates_bands(tmp_path, v14_release, monkeypatch, value):
    plain = LC.certificate(benzene_folder(tmp_path / "plain", v14_release, 3), NoCatalog())
    monkeypatch.setattr(INV, "has_linear_group", lambda symbols, coords: True)
    monkeypatch.setattr(INV, "load_record", lambda models, sha16: made_up(value, value, value))
    c = LC.certificate(benzene_folder(tmp_path / "linear", v14_release, 3), NoCatalog())
    if value == LINE:
        assert c["bands"] == plain["bands"] and c["statement"] == plain["statement"] and "withheld" not in c["licence"]
    else:
        assert not any(b["licensed"] for b in c["bands"]) and {b["licence_note"] for b in c["bands"]} == {TOO_HIGH_NOTE}
        assert [b["network_cm"] for b in c["bands"]] == [b["network_cm"] for b in plain["bands"]]
