"""probes/fundamentals_vs_experiment.py (TASKS 111, reading 3): the symmetry labels reproduce the species counts of the experimental tables on
our tracked CC Hessians, degenerate pairs merge only for e species, the pairing goes by frequency order inside an irrep and refuses a count or
species mismatch, and Mai's archive gives exactly one neutral entry per formula."""
import sys
import zipfile
from pathlib import Path

import numpy as np
import pytest

pytest.importorskip("torch")
PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "probes"))
import fundamentals_vs_experiment as F  # noqa: E402, RUF100  (after the sys.path insert: pre-commit's pinned ruff flags it, the newer one not)

MASS = {"C": 12.0, "H": 1.00782503207}


def modes_of(npz: str, symbols: list[str]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    z = np.load(PLAN / npz)
    masses = np.array([MASS[s] for s in symbols])
    _, freq, V, _ = F.normal_modes(z["H_projected"], masses)
    return freq, V, z["coords_bohr"]


def test_naphthalene_d2h_labels_have_martins_species_counts():
    symbols = ["C"] * 10 + ["H"] * 8
    freq, V, coords = modes_of("probes/results_m1/e8_naphthalene_ccpvdz_tlambda_2026-10-02/hessian_ccsd_t.npz", symbols)
    labels = F.d2h_irreps(V, freq, symbols, coords)
    assert {s: labels.count(s) for s in F.D2H_SPECIES} == F.D2H_SPECIES


def test_benzene_d6h_labels_cover_the_twenty_wilson_modes():
    symbols = ["C"] * 6 + ["H"] * 6
    freq, V, coords = modes_of("probes/results_m1/e8_benzene_ccpvtz_oop_2026-10-03/hessian_ccsd_t.npz", symbols)
    groups = F.groups(freq, F.d6h_irreps(V, freq, symbols, coords))
    assert len(groups) == 20 and sorted({g.irrep for g in groups}) == sorted({e.irrep for e in F.benzene_experiment()})


def test_only_e_species_merge_into_one_mode():
    freq = np.array([100.0, 100.2, 300.0, 300.1])
    out = F.groups(freq, ["e2u", "e2u", "b1u", "b1u"])
    assert [g.idx for g in out] == [(0, 1), (2,), (3,)]


def test_pairing_goes_by_frequency_order_and_flags_close_neighbours():
    computed = [F.Group((0,), 1000.0, "Ag"), F.Group((1,), 1010.0, "Ag"), F.Group((2,), 3100.0, "Ag")]
    exp = [F.Exp("Ag", 3060.0), F.Exp("Ag", 990.0), F.Exp("Ag", 1050.0)]
    pairs = F.pair_by_irrep(computed, exp)
    assert [(g.freq, e.nu, flag) for g, e, flag in pairs] == [(1000.0, 990.0, True), (1010.0, 1050.0, True), (3100.0, 3060.0, False)]


@pytest.mark.parametrize(("computed", "words"), [
    ([F.Group((0,), 1000.0, "Ag")], "1 computed modes, 2 experimental"),
    ([F.Group((0,), 1000.0, "Ag"), F.Group((1,), 900.0, "Au")], "species differ"),
])
def test_pairing_refuses_a_mismatch(computed, words):
    with pytest.raises(ValueError, match=words):
        F.pair_by_irrep(computed, [F.Exp("Ag", 990.0), F.Exp("Ag", 1500.0)])


def test_the_same_mode_overlaps_itself_fully():
    V = np.linalg.qr(np.random.default_rng(0).normal(size=(9, 3)))[0]
    assert F.subspace_overlap(V, (0, 1), V, (0, 1)) == pytest.approx(1.0)
    assert F.subspace_overlap(V, (0,), V, (2,)) == pytest.approx(0.0, abs=1e-12)


def _entry(formula: str) -> str:
    return f"3\nSource=COMPAS1 Formula={formula} Charge=0 JSD=0.01\nC 0 0 0\nH 0 0 1\nH 0 1 0\n\nscaled_Freq(cm^-1) Inten(KM/mol) scale_factor\n" \
           "1000.0 1.0 0.956\n3000.0 2.0 0.960\n"


def test_mai_gives_one_neutral_entry_per_formula(tmp_path):
    z = tmp_path / "m.zip"
    with zipfile.ZipFile(z, "w") as w:
        w.writestr("IR_COMPAS/charge_0/C1M000001.xyz", _entry("C6H6"))
        w.writestr("IR_COMPAS/charge_1/C1M000001.xyz", _entry("C6H6"))          # a cation of the same molecule is not read
        w.writestr("IR_COMPAS/charge_0/C1M000002.xyz", _entry("C10H8"))
    out = F.mai_spectra(z, ["C6H6", "C10H8"])
    name, scaled, factor = out["C6H6"]
    assert name == "C1M000001" and scaled.tolist() == [1000.0, 3000.0] and factor.tolist() == [0.956, 0.960]
    with zipfile.ZipFile(z, "a") as w:
        w.writestr("IR_COMPAS/charge_0/C1M000003.xyz", _entry("C10H8"))
    with pytest.raises(ValueError, match="C10H8: 2 neutral entries"):
        F.mai_spectra(z, ["C10H8"])


def test_stats_per_family_and_all():
    out = F.stats({"CH-oop": [1.0, -3.0], "ring-ip": [2.0]})
    assert out["CH-oop"] == {"n": 2, "mean": -1.0, "rms": pytest.approx(np.sqrt(5.0))}
    assert out["other"]["n"] == 0 and out["all"]["n"] == 3
