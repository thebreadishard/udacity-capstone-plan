"""The training chemistry in module 08 (`modules/08_industry_synthesis/m08/domain.py`, TASKS 279; aromir's `tests/test_domain.py` and
`tests/test_certificate.py` at commit 52cf119): a molecule with a kind of charged atom or a size of aromatic ring the networks'
training molecules lack is admitted with the caveat, printed, and no band of it is licensed; the training list is read from the
networks that run. The rule on given lists, the carried networks' own lists where their checkpoints are present, the certificate on
the frozen corpus's benzene after a zero correction with the caveat given."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

from pin_tools import DATA, PLAN
from test_m08_own_spread import CONDITION, NoCatalog, benzene_folder, v14_release  # noqa: F401  the fixture is used by name

sys.path.insert(0, str(PLAN / "modules" / "08_industry_synthesis"))
from m08 import domain as DOMAIN
from m08 import live_certificate as LC
from m08 import pipeline as P
from m08 import seen as S

PIN_MODEL = DATA / "rungC_cc_pin_model.pt"
ZWITTERION = "[NH3+]c1ccccc1C(=O)[O-]"
ZWITTERION_CAVEAT = ("charge separation of a kind no training molecule holds: C[O-], c[NH3+] (the charged atoms of the training "
                     "molecules: [n+][O-], c[N+](=O)[O-], c[n+]([O-])c)")       # aromir's, against v1.4's list
DEMO_CANDIDATES = {"pyrazine": "c1cnccn1", "pyrimidine": "c1cncnc1", "thiophene": "c1ccsc1", "1,3,5-trifluorobenzene": "Fc1cc(F)cc(F)c1",
                   "benzoxazole": "c1ccc2ocnc2c1", "benzimidazole": "c1ccc2[nH]cnc2c1", "2,6-dimethylphenol": "Cc1cccc(C)c1O",
                   "N,N-dimethylaniline": "CN(C)c1ccccc1"}
"""TASKS 271's eight demo candidates."""
NITRO_LIST = ("O=[N+]([O-])c1ccccc1", "[O-][n+]1ccccc1", "c1ccc2ccccc2c1", "c1ccc2cccc2cc1", "c1ccc2c(c1)-c1ccccc1-2", "c1ccoc1")
"""A training list of aromir's three kinds of charged atom and rings of 4 to 7 aromatic atoms."""


def carried(kind: str) -> tuple[Path, ...]:
    models = P.carried_models(kind)
    if not models or not all(p.is_file() for p in models):
        pytest.skip(f"the carried {kind} networks' checkpoints are not on this machine")
    return models


@pytest.fixture(scope="module", params=[P.NK.RELEASE, P.NK.MEASUREMENT])
def trained(request) -> tuple[str, ...]:
    """The training list of the carried networks of each kind (`seen.trained_smiles`)."""
    return S.trained_smiles(carried(request.param))


def test_the_carried_training_list_holds_nitro_groups_an_n_oxide_and_rings_of_4_to_7(trained):
    kinds = {site for smiles in trained for site in DOMAIN.charge_sites(smiles)}
    assert {(element, charge) for element, charge, *_ in kinds} == {("N", 1), ("O", -1)} and len(kinds) == 3
    assert set().union(*(DOMAIN.aromatic_ring_sizes(smiles) for smiles in trained)) == {4, 5, 6, 7}


def test_no_training_molecule_is_outside_its_own_training_chemistry(trained):
    assert [s for s in trained if DOMAIN.outside_training_chemistry(s, trained)] == []


def test_a_zwitterion_is_outside_the_carried_training_chemistry(trained):
    assert DOMAIN.outside_training_chemistry(ZWITTERION, trained) == (ZWITTERION_CAVEAT,)


@pytest.mark.parametrize("smiles", ["[N-]=[N+]=Nc1ccccc1", "C[S+]([O-])c1ccccc1"])
def test_an_azide_or_a_sulfoxide_is_outside_a_list_of_nitro_groups(smiles):
    (caveat,) = DOMAIN.outside_training_chemistry(smiles, NITRO_LIST)
    assert caveat.startswith("charge separation of a kind no training molecule holds")


def test_tropone_is_inside_a_list_with_azulene():
    assert DOMAIN.aromatic_ring_sizes("c1ccc2cccc2cc1") == {5, 7}
    assert DOMAIN.outside_training_chemistry("O=c1cccccc1", NITRO_LIST) == ()


def test_a_seven_membered_ring_is_outside_a_list_without_one():
    without = [s for s in NITRO_LIST if 7 not in DOMAIN.aromatic_ring_sizes(s)]
    assert DOMAIN.outside_training_chemistry("O=c1cccccc1", without) == (
        "an aromatic ring of 7 atoms, a size no training molecule has (theirs: 4, 5, 6)",)


@pytest.mark.parametrize("smiles", ["O=[N+]([O-])c1ccccc1", "[O-][n+]1ccccc1", "c1ccc2ccccc2c1", "c1ccoc1"])
def test_the_kinds_the_training_list_holds_are_inside(smiles):
    assert DOMAIN.outside_training_chemistry(smiles, NITRO_LIST) == ()


def test_a_release_trained_on_more_chemistry_admits_more():
    assert DOMAIN.outside_training_chemistry("Cc1cccc(=O)cc1", ["O=c1cccccc1"]) == ()


def test_a_string_that_is_no_smiles_is_refused():
    with pytest.raises(ValueError, match="does not parse as a SMILES"):
        DOMAIN.charge_sites("c1ccccc")


@pytest.fixture
def pin_admission(monkeypatch):
    """The pin model counts as carried; its five training molecules are the training list."""
    monkeypatch.setattr(P.MR, "require_carried", lambda p, kind=None: {"status": "carried", "network": P.NETWORK, "version": "pin"})
    monkeypatch.setattr(P, "training_set", lambda models: (("C", "H", "N", "O"), (6, 40)))


def config(tmp_path: Path, smiles: str) -> P.PipelineConfig:
    return P.PipelineConfig(name="mol", out_root=tmp_path, smiles=smiles, models=(PIN_MODEL,), psi4_python=Path(sys.executable))


def test_admission_reads_the_running_networks_list_and_records_the_caveat(tmp_path, pin_admission):
    trained = S.trained_smiles((PIN_MODEL,))
    adm = P.admit(config(tmp_path, ZWITTERION))
    assert adm.outside_training_chemistry == DOMAIN.outside_training_chemistry(adm.smiles, trained) != ()
    assert adm.record()["outside_training_chemistry"] == adm.outside_training_chemistry


def test_a_molecule_inside_the_training_chemistry_records_nothing_new(tmp_path, pin_admission):
    adm = P.admit(config(tmp_path, "c1ccccc1"))
    assert adm.outside_training_chemistry == () and "outside_training_chemistry" not in adm.record()


def test_check_only_says_why_no_band_will_be_licensed(tmp_path, pin_admission, monkeypatch, capsys):
    monkeypatch.setattr(P, "carried_models", lambda kind: (PIN_MODEL,) if kind == P.NK.MEASUREMENT else ())
    monkeypatch.setattr(P, "default_psi4_python", lambda: Path(sys.executable))
    caveats = P.admit(config(tmp_path, ZWITTERION)).outside_training_chemistry
    assert caveats
    assert P.main(["--name", "z", "--smiles", ZWITTERION, "--out", str(tmp_path / "out"), "--check-only"]) == 0
    out = capsys.readouterr().out
    assert all(f"[pipeline] outside the training chemistry, so no band of it will be licensed: {c}\n" in out for c in caveats)


def test_a_molecule_outside_the_training_chemistry_is_printed_and_not_licensed(tmp_path, v14_release):  # noqa: F811  the fixture imported from test_m08_own_spread
    plain = LC.certificate(benzene_folder(tmp_path / "plain", v14_release, 3), NoCatalog())
    c = LC.certificate(benzene_folder(tmp_path / "out", v14_release | {"outside_training_chemistry": [ZWITTERION_CAVEAT]}, 3), NoCatalog())
    n = len(c["bands"])
    reason = f"{DOMAIN.OUTSIDE_CHEMISTRY}: {ZWITTERION_CAVEAT}"
    assert c["licence"]["outside_training_chemistry"] == {"note": DOMAIN.OUTSIDE_CHEMISTRY, "caveats": [ZWITTERION_CAVEAT],
                                                          "n_bands": n, "reason": reason}
    assert not any(b["licensed"] for b in c["bands"]) and {b["licence_note"] for b in c["bands"]} == {DOMAIN.OUTSIDE_CHEMISTRY}
    unchanged = ("network_cm", "printed_cm", "b3lyp_cm", "baseline_cm", "km_mol", "seed_range_cm", "family")
    assert [{k: b[k] for k in unchanged} for b in c["bands"]] == [{k: b[k] for k in unchanged} for b in plain["bands"]]
    families = ", ".join(c["licence"]["licensed_families"])
    own = f"where a band's {CONDITION.format(n='1 ')}"
    said = (f"0 of {n} bands are licensed: the version's harmonic positions ω are licensed for {families} (decision 65) {own}, and for "
            f"this molecule that licence is withheld — {reason} — each band marked; at ")
    assert said in c["statement"] and c["statement"] == plain["statement"].replace(
        f"harmonic positions ω are licensed for {families} (decision 65) {own}, each band marked; at ", said)
    page = LC.to_markdown(c)
    assert f"- Outside the training chemistry: {ZWITTERION_CAVEAT}: no band is licensed.\n" in page
    assert f"| no: {DOMAIN.OUTSIDE_CHEMISTRY} |" in page
    assert f"For this molecule it is withheld: {reason[0].upper()}{reason[1:]}." in page
    assert LC.withheld_reason(c["licence"]) == reason


def test_the_spread_goes_first_where_both_withhold(tmp_path, v14_release):  # noqa: F811  the imported fixture
    admission = v14_release | {"outside_training_chemistry": [ZWITTERION_CAVEAT]}
    c = LC.certificate(benzene_folder(tmp_path / "unmeasured", admission, 3, None), NoCatalog())
    assert {b["licence_note"] for b in c["bands"]} == {c["licence"]["withheld"]["note"]}
    moved = LC.certificate(benzene_folder(tmp_path / "moved", admission, 3, 3.01), NoCatalog())
    assert {b["licence_note"] for b in moved["bands"]} == {"its position moved by 3.01 cm⁻¹ under rotation 1 of this molecule, more than "
                                                           "the licence line"}
    assert LC.withheld_reason(moved["licence"]) == f"{DOMAIN.OUTSIDE_CHEMISTRY}: {ZWITTERION_CAVEAT}"
    assert LC.withheld_reason(c["licence"]) == c["licence"]["withheld"]["reason"]
    assert f"- Outside the training chemistry: {ZWITTERION_CAVEAT}: no band is licensed." in LC.to_markdown(c)


def test_a_benzene_certificate_says_nothing_of_the_training_chemistry(tmp_path, v14_release):  # noqa: F811  the fixture imported from test_m08_own_spread
    c = LC.certificate(benzene_folder(tmp_path, v14_release, 3), NoCatalog())
    assert "outside_training_chemistry" not in c["licence"] and LC.withheld_reason(c["licence"]) is None
    assert "Outside the training chemistry" not in LC.to_markdown(c)


def test_a_molecule_outside_the_training_sizes_is_printed_and_not_licensed(tmp_path, v14_release):  # noqa: F811  the imported fixture
    plain = LC.certificate(benzene_folder(tmp_path / "plain", v14_release, 3), NoCatalog())
    c = LC.certificate(benzene_folder(tmp_path / "out", v14_release | {"inside_training_sizes": False}, 3), NoCatalog())
    n = len(c["bands"])
    assert c["licence"]["outside_training_sizes"] == {"note": DOMAIN.OUTSIDE_SIZES, "n_bands": n, "reason": DOMAIN.OUTSIDE_SIZES}
    assert not any(b["licensed"] for b in c["bands"]) and {b["licence_note"] for b in c["bands"]} == {DOMAIN.OUTSIDE_SIZES}
    assert [b["network_cm"] for b in c["bands"]] == [b["network_cm"] for b in plain["bands"]]
    assert f"licence is withheld — {DOMAIN.OUTSIDE_SIZES} — each band marked; at " in c["statement"]
    page = LC.to_markdown(c)
    assert "atoms: OUTSIDE: no band is licensed\n" in page and f"| no: {DOMAIN.OUTSIDE_SIZES} |" in page


def test_the_sizes_go_before_the_chemistry(tmp_path, v14_release):  # noqa: F811  the imported fixture
    admission = v14_release | {"inside_training_sizes": False, "outside_training_chemistry": [ZWITTERION_CAVEAT]}
    c = LC.certificate(benzene_folder(tmp_path, admission, 3), NoCatalog())
    assert {b["licence_note"] for b in c["bands"]} == {DOMAIN.OUTSIDE_SIZES} and LC.withheld_reason(c["licence"]) == DOMAIN.OUTSIDE_SIZES
    assert f"- Outside the training chemistry: {ZWITTERION_CAVEAT}: no band is licensed." in LC.to_markdown(c)


def test_the_demo_candidates_are_inside_the_release_networks_training_sizes():
    low, high = P.training_set(carried(P.NK.RELEASE))[1]
    from rdkit import Chem

    sizes = {name: Chem.AddHs(Chem.MolFromSmiles(s)).GetNumAtoms() for name, s in DEMO_CANDIDATES.items()}
    assert (low, high) == (8, 40) and all(low <= n <= high for n in sizes.values()), sizes
