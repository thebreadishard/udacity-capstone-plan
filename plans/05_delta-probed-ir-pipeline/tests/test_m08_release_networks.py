"""Decision 66 (17 Nov 2026) in the pipeline and the live certificate: step 4 runs the carried version's release networks once their
checks record has passed for exactly those files; the error bars, the licence and the seen index of the measurement networks stay
those of the measurement networks; the certificate carries design note §3's sentence and the release networks' seen line. With no
release network — today — the admission's record, the statement and the whole certificate are what they were.

On made-up registries and tiny checkpoint files, v1.3's committed records, and the frozen corpus's benzene with a zero correction."""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import numpy as np
import pytest

torch = pytest.importorskip("torch")
from pin_tools import PIN_CORPUS, PLAN, require_frozen_corpus  # noqa: E402

sys.path.insert(0, str(PLAN / "modules" / "08_industry_synthesis"))
from m08 import accuracy as A  # noqa: E402
from m08 import live_certificate as LC  # noqa: E402
from m08 import pipeline as P  # noqa: E402
from m08 import seen as S  # noqa: E402

NK = P.NK
BENZENE = "A_8448043181"
V13 = tuple(f"E7_rungC_chain35_analytic_model_n750_seed{s}.pt" for s in range(3))
LIC = {"quantity_name": "error of the corrected band positions of the seed-mean correction", "licensed_families": ["ring-ip"], "caveats": []}
ADMISSION_KEYS = {"smiles", "formula", "elements", "n_atoms", "training_elements", "training_atoms", "models", "inside_training_sizes"}


def checkpoint(path: Path, kind: str, train_ids: tuple[str, ...] = ("A_x",)) -> Path:
    torch.save({"args": {NK.FIELD: kind} if kind == NK.RELEASE else {}, "train_ids": list(train_ids)}, path)
    return path


@pytest.fixture
def version(tmp_path, monkeypatch):
    """A carried version as a pair of two seeds each, in a folder that stands for the registry: `carried_models` and `require_carried`
    answer from it. Returns (measurement files, release files, a function that writes the release checks record)."""
    measurement = tuple(checkpoint(tmp_path / f"V_meas_model_n19_seed{s}.pt", NK.MEASUREMENT) for s in (0, 1))
    release = tuple(checkpoint(tmp_path / f"V_rel_model_n21_seed{s}.pt", NK.RELEASE, ("A_x", BENZENE)) for s in (0, 1))
    listed = {NK.MEASUREMENT: measurement, NK.RELEASE: release}
    entered = {p.name: {"status": "carried", "network": P.NETWORK, "version": "1.4"} | ({NK.FIELD: NK.RELEASE} if p in release else {})
               for p in (*measurement, *release)}
    monkeypatch.setattr(P, "carried_models", lambda kind: listed[kind])
    monkeypatch.setattr(P.MR, "require_carried", lambda p, kind=None: entered[Path(p).name])

    def checks(passed: bool = True, **changed) -> None:
        record = {"passed": passed, "refusals": [] if passed else ["check 4 (early_stopping): 1 release seed(s) stopped by the cap"],
                  NK.RELEASE: [p.name for p in release], NK.MEASUREMENT: [p.name for p in measurement],
                  "model_sha16": {p.name: P.sha16(p) for p in (*measurement, *release)}} | changed
        (tmp_path / f"V_rel{P.RELEASE_CHECKS_SUFFIX}").write_text(json.dumps(record), encoding="utf-8")

    return measurement, release, checks, listed, entered


def test_today_the_product_is_the_carried_measurement_networks():
    """The committed registry: no version has release networks, so step 4's default models are what they were."""
    product = P.product_networks()
    assert product == P.ProductNetworks(P.carried_models(NK.MEASUREMENT), NK.MEASUREMENT, None) and len(product.models) == 3
    assert tuple(p.name for p in product.models) == V13


def test_release_networks_are_the_product_only_after_their_checks_passed_for_these_files(version, tmp_path):
    measurement, release, checks, listed, _ = version
    assert P.product_networks() == P.ProductNetworks(measurement, NK.MEASUREMENT, "no checks record V_rel_release_checks.json beside them "
                                                     "(python probes/release_checks.py makes it)")
    checks(passed=False)
    held = P.product_networks()
    assert held.kind == NK.MEASUREMENT and held.held_back == ("V_rel_release_checks.json refused them: check 4 (early_stopping): 1 release "
                                                              "seed(s) stopped by the cap")
    checks(**{NK.MEASUREMENT: ["other_model_n19_seed0.pt"]})
    assert "checked other measurement networks (other_model_n19_seed0.pt)" in P.product_networks().held_back
    checks(model_sha16={p.name: "0" * 16 for p in (*measurement, *release)})
    assert "checked other files of the same names: V_rel_model_n21_seed0.pt" in P.product_networks().held_back
    checks()
    assert P.product_networks() == P.ProductNetworks(release, NK.RELEASE, None)
    assert P.PipelineConfig(name="mol", out_root=tmp_path, smiles="c1ccccc1", psi4_python=Path(sys.executable)).models == release
    listed[NK.RELEASE] = ()                                                   # and a version without release networks: as always
    assert P.product_networks() == P.ProductNetworks(measurement, NK.MEASUREMENT, None)


def test_measurement_networks_are_admitted_with_the_record_they_always_had(version):
    measurement, _, _, listed, _ = version
    listed[NK.RELEASE] = ()
    admitted, reasons = P.admitted_models(measurement)
    assert reasons == [] and admitted.measurement == () and admitted.held_back is None
    assert all(set(e) == {"path", "sha16", "network", "version", "status"} for e in admitted.entries)
    adm = P.Admission("c1ccccc1", "C6H6", ("C", "H"), 12, ("C", "H"), (6, 40), admitted.entries, admitted.measurement, admitted.held_back)
    assert set(adm.record()) == ADMISSION_KEYS                                 # no new key in pipeline.json's admission


def test_release_networks_are_admitted_with_the_measurement_networks_beside_them(version):
    measurement, release, checks, _, _ = version
    checks()
    admitted, reasons = P.admitted_models(release)
    assert reasons == [] and all(e[NK.FIELD] == NK.RELEASE for e in admitted.entries) and admitted.held_back is None
    assert [Path(e["path"]).name for e in admitted.measurement] == [p.name for p in measurement]
    assert all(NK.FIELD not in e and e["sha16"] == P.sha16(p) for e, p in zip(admitted.measurement, measurement, strict=True))
    adm = P.Admission("c1ccccc1", "C6H6", ("C", "H"), 12, ("C", "H"), (6, 40), admitted.entries, admitted.measurement, admitted.held_back)
    assert set(adm.record()) == ADMISSION_KEYS | {"measurement_models"}
    held, reasons = P.admitted_models(measurement)                             # the measurement networks, asked for by name
    assert reasons == [] and held.held_back == "this run was given the measurement networks"
    assert set(P.Admission("c", "C", (), 1, (), (1, 1), held.entries, held.measurement, held.held_back).record()) == ADMISSION_KEYS | {"release_held_back"}


def test_release_networks_without_a_passed_record_or_against_their_checkpoints_are_refused(version):
    measurement, release, checks, _, entered = version
    _, reasons = P.admitted_models(release)
    assert reasons == ["release networks run only after their checks have passed (decision 66): no checks record V_rel_release_checks.json "
                       "beside them (python probes/release_checks.py makes it)"]
    checks(passed=False)
    assert "V_rel_release_checks.json refused them" in P.admitted_models(release)[1][0]
    checks()
    assert "the models are of both kinds, measurement and release" in P.admitted_models((measurement[0], release[0]))[1][0]
    entered[release[0].name].pop(NK.FIELD)                                     # the registry forgot that this one is a release network
    _, reasons = P.admitted_models(measurement + release[:1])
    assert reasons == ["V_rel_model_n21_seed0.pt is entered in the registry as a measurement network and its checkpoint says release (decision 66)"]
    entered[release[0].name] |= {NK.FIELD: NK.RELEASE, "version": "1.5"}
    entered[release[1].name] |= {"version": "1.5"}
    assert any("of version ['1.5'] and the carried measurement networks, whose records give the error bars, of ['1.4']" in r
               for r in P.admitted_models(release)[1])


def test_the_statement_without_release_networks_is_word_for_word_what_it_was():
    """The sentence as `statement` built it before decision 66, written out here."""
    old = (f"benzene: the infrared spectrum of {P.NETWORK} v1.3 (3 seeds) — B3LYP/6-31G* corrected "
           f"toward {A.HIGHER_LEVEL.split(' (')[0]} — with the {LIC['quantity_name']} measured on molecules the network never saw; the "
           f"harmonic positions ω are licensed for ring-ip (decision 65), each band marked; at "
           f"the coupled-cluster level {A.CC_NOTE}. The scaled B3LYP spectrum is shown as the baseline only. This molecule and the "
           f"ΔH network: held out.")
    assert LC.statement("benzene", "1.3", 3, LIC, "held out") == old == LC.statement("benzene", "1.3", 3, LIC, "held out", LC.MadeBy())


def test_the_statement_under_release_networks_carries_the_design_notes_sentence():
    sentence = ("The spectrum is made by the release networks of version 1.4, trained on all 1132 molecules with labels. Its error bars were "
                "measured on the measurement networks of the same version — the same recipe trained without the hold-out molecules — on "
                "molecules those networks never saw; the release networks themselves have seen every molecule we hold labels for, so they have "
                "no held-out error of their own.")
    s = LC.statement("benzene", "1.4", 3, LIC, S.TEXT["release_trained"], LC.MadeBy(release_trained_on=1132))     # no inner validation
    fitted = LC.statement("benzene", "1.4", 3, LIC, S.TEXT["release_trained"], LC.MadeBy(release_trained_on=1132, inner_validation=0.15))
    assert ("trained on all 1132 molecules with labels: each of the 3 networks is fitted on a random 85 % of the molecules and stopped "
            "on the other 15 %, a different 15 % per seed, so not every molecule is fitted by every network (with 3 networks about "
            "0.15³ ≈ 0.3 % by none). Its error bars were measured on the measurement networks of the same version") in fitted
    assert fitted.replace(": " + NK.fitting_sentence(3, 0.15), "") == s           # and nothing else moves
    assert sentence in s and "measured on molecules the network never saw" not in s
    assert f"The error stated is the measurement networks' {LIC['quantity_name']}; the harmonic positions ω are licensed for ring-ip" in s
    assert s.endswith("This molecule and the ΔH network: in the release networks' training data: the error bars are not an out-of-sample "
                      "error for this molecule; expect it to be smaller.")
    held = LC.statement("benzene", "1.4", 3, LIC, "held out", LC.MadeBy(held_back="no checks record"))
    assert "measured on molecules the network never saw" in held and held.endswith(
        "Version 1.4 has release networks, and they did not make this spectrum: no checks record. It is made by the measurement networks, "
        "whose error was measured on molecules they never saw.")


SMILES = {"A_naph": "c1ccc2ccccc2c1", "A_benz": "c1ccccc1", "B_tol": "Cc1ccccc1"}
SEEN = S.build({"A_naph"}, {"a": {"A_benz"}, "b": set()}, SMILES)


def test_the_seen_line_of_a_molecule_the_release_networks_trained_on():
    index = S.build({"A_naph", "A_benz"}, {}, SMILES)
    for smiles, ids in (("C1=CC=CC=C1", ["A_benz"]), ("c1ccc2ccccc2c1", ["A_naph"])):       # held out and pool alike, to the measurement networks
        got = S.status(smiles, SEEN, None, index)
        assert got == {"role": "release_trained", "ids": ids, "text": "in the release networks' training data: the error bars are not an "
                                                                      "out-of-sample error for this molecule; expect it to be smaller"}
    assert S.status("Cc1ccccc1", SEEN, "B_tol", index) == S.status("Cc1ccccc1", SEEN, "B_tol")          # any other molecule: as always
    assert S.status("c1ccccc1", SEEN, "A_benz")["role"] == "a" == S.status("c1ccccc1", SEEN, "A_benz", None)["role"]


def test_the_release_index_keeps_the_cation_rows_apart(tmp_path, monkeypatch):
    manifest = tmp_path / "manifest.csv"
    manifest.write_text("id,smiles,layer\nA_benz,c1ccccc1,A\nB_tol,Cc1ccccc1,B\nP3c_benz,c1ccccc1,P3c\n", encoding="utf-8")
    monkeypatch.setattr(S, "MANIFEST", manifest)
    monkeypatch.setattr(P, "train_ids", lambda models: {"A_benz", "B_tol", "P3c_benz"})
    index = S.release_index(())
    assert (index.trained, index.holdout, index.cations) == ({"c1ccccc1": ["A_benz"], "Cc1ccccc1": ["B_tol"]}, {}, {"c1ccccc1": ["P3c_benz"]})
    got = S.status("c1ccccc1", SEEN, "A_benz", index)
    assert (got["role"], got["cation_trained"]) == ("release_trained", ["P3c_benz"]) and "radical cation (P3c_benz)" in got["text"]


def test_the_share_a_network_is_stopped_on_is_its_checkpoints_own(tmp_path):
    models = []
    for name, share in (("a.pt", 0.15), ("b.pt", 0.15), ("c.pt", 0.0)):
        torch.save({"args": {"inner_val": share}}, tmp_path / name)
        models.append(tmp_path / name)
    assert P.inner_validation_share(tuple(models[:2])) == 0.15
    with pytest.raises(ValueError, match="2 inner-validation shares"):
        P.inner_validation_share(tuple(models))


class NoCatalog:
    """A catalogue that lists nothing and knows no laboratory tolerance: the certificate's other parts do not read it."""

    def find(self, smiles: str) -> None:
        return None

    def u_band(self, species: str) -> dict:
        return {}


def result_folder(tmp_path: Path, ran: tuple[str, ...], admission: dict) -> Path:
    """Benzene's folder as the pipeline leaves it after a zero correction by the named models."""
    require_frozen_corpus()
    d = tmp_path / BENZENE
    shutil.copytree(PIN_CORPUS / "molecules" / BENZENE, d)
    zero = np.zeros((36, 36))
    P.save_correction(d, zero, [zero] * len(ran), tuple(Path(n) for n in ran))
    P.write_json(d / "pipeline.json", {"pipeline_version": P.PIPELINE_VERSION, "name": "benzene", "spectra": P.spectra(d, zero, [zero] * len(ran)),
                                       "admission": {"smiles": "c1ccccc1", "formula": "C6H6", "n_atoms": 12, "elements": ["C", "H"],
                                                     "training_atoms": [6, 40], "inside_training_sizes": True} | admission,
                                       "seconds": {"low_level": 60.0}, "provenance": {"host": "laptop", "commit": "0" * 40, "dirty": False},
                                       "deck": {"sha16": "d" * 16}, "low_level": {"b3lyp": {"software": {"pyscf": "2.15.0"}}}})
    return d


@pytest.fixture
def v13(monkeypatch):
    """v1.3's three measurement networks as registry entries with the hashes its product-error record was read on. The checkpoints
    are not in git, so the training ids are given: none for the measurement networks, benzene for a release network."""
    with open(A.M05_OUT / f"E7_rungC_chain35_analytic{A.PRODUCT_SUFFIX}", encoding="utf-8") as f:
        hashes = json.load(f)["model_sha16"]
    monkeypatch.setattr(P, "train_ids", lambda models: {"A_8448043181"} if "V_rel" in models[0].name else set())
    monkeypatch.setattr(P, "inner_validation_share", lambda models: 0.15)
    return [{"path": f"out/{name}", "sha16": hashes[name], "network": P.NETWORK, "version": "1.3", "status": "carried"} for name in V13]


def test_a_certificate_of_measurement_networks_says_what_it_said(tmp_path, v13):
    c = LC.certificate(result_folder(tmp_path, V13, {"models": v13}), NoCatalog())
    assert c["molecule"]["seen"]["role"] == "a" and "held out, hold-out (a)" in c["molecule"]["seen"]["text"]
    assert set(c["network"]) == {"name", "version", "models", "predicts"} and c["network"]["models"] == v13
    assert f"with the {c['licence']['quantity_name']} measured on molecules the network never saw; the harmonic positions" in c["statement"]
    assert "release" not in c["statement"] and "release" not in LC.to_markdown(c)
    assert c["accuracy"] == A.accuracy_of(V13)


def test_a_certificate_of_release_networks_takes_its_error_bars_from_the_measurement_networks(tmp_path, v13):
    ran = ("V_rel_model_n1132_seed0.pt", "V_rel_model_n1132_seed1.pt", "V_rel_model_n1132_seed2.pt")
    released = [{"path": f"out/{name}", "sha16": "f" * 16, "network": P.NETWORK, "version": "1.3", "status": "carried", NK.FIELD: NK.RELEASE}
                for name in ran]
    c = LC.certificate(result_folder(tmp_path, ran, {"models": released, "measurement_models": v13}), NoCatalog())
    assert c["accuracy"] == A.accuracy_of(V13) and c["licence"]["licensed_families"]            # the measurement networks' records, unchanged
    assert c["molecule"]["seen"] == {"role": "release_trained", "ids": [BENZENE], "text": S.TEXT["release_trained"]}
    assert c["network"]["kind"] == NK.RELEASE and c["network"]["trained_on_molecules"] == 1 and c["network"]["measurement_models"] == v13
    assert LC.release_sentence("1.3", 3, LC.MadeBy(1, None, 0.15)) in c["statement"] and "the network never saw" not in c["statement"]
    assert "each of the 3 networks is fitted on a random 85 % of the molecules" in c["statement"] and c["network"]["inner_validation"] == 0.15
    md = LC.to_markdown(c)
    assert "- the ΔH network: in the release networks' training data: the error bars are not an out-of-sample error for this molecule" in md
    assert (f"- the models above are release networks, trained on 1 molecules: {NK.fitting_sentence(len(c['network']['models']), 0.15)}; "
            "the error bars are those of the measurement networks: " + V13[0]) in md
    whole = LC._measurement_lines(c["network"] | {"inner_validation": 0.0})[0]          # no inner validation: nothing was stopped on
    assert "fitted on all of the molecules" in whole and "stopped" not in whole
    with pytest.raises(ValueError, match="evaluation records"):                 # and never from records under the release networks' names
        A.accuracy_of(ran)


def test_the_design_notes_sentence_is_the_one_the_certificate_prints():
    note = (PLAN / "GoalGathering" / "notes" / "Design_2026-11-17_Measurement_and_Release_Networks.md").read_text(encoding="utf-8")
    quoted = " ".join(line[2:] for line in note.splitlines() if line.startswith("> "))
    assert f"with labels: {NK.fitting_sentence(3, 0.15)}. Its error bars" in quoted and "fitted by most" not in note
