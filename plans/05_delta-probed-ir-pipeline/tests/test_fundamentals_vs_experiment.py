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
    labels, notes = F.d2h_irreps(V, freq, symbols, coords)
    assert notes == []
    assert {s: labels.count(s) for s in F.D2H_SPECIES} == F.D2H_SPECIES


def test_benzene_d6h_labels_cover_the_twenty_wilson_modes():
    symbols = ["C"] * 6 + ["H"] * 6
    freq, V, coords = modes_of("probes/results_m1/e8_benzene_ccpvtz_oop_2026-10-03/hessian_ccsd_t.npz", symbols)
    labels, notes = F.d6h_irreps(V, freq, symbols, coords)
    groups = F.groups(freq, labels)
    assert notes == []                       # CC/TZ benzene has no mixed pair
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


def _ring(n_c: int) -> tuple[list[str], np.ndarray]:
    """A planar CnHn ring in bohr (C–C 1.40 Å, C–H 1.08 Å) — benzene for n = 6, a different skeleton for n = 8."""
    r_c = 1.40 / (2 * np.sin(np.pi / n_c)) / F.BOHR
    t = 2 * np.pi * np.arange(n_c) / n_c
    ring = np.stack([np.cos(t), np.sin(t), 0 * t], 1)
    return ["C"] * n_c + ["H"] * n_c, np.concatenate([r_c * ring, (r_c + 1.08 / F.BOHR) * ring])


def _entry(formula: str, n_c: int, first: float = 1000.0) -> str:
    symbols, coords = _ring(n_c)
    block = F.xyz_block(symbols, coords).replace("\n\n", f"\nSource=COMPAS1 Formula={formula} Charge=0 JSD=0.01\n", 1)
    return block + f"\nscaled_Freq(cm^-1) Inten(KM/mol) scale_factor\n{first} 1.0 0.956\n3000.0 2.0 0.960\n"


def test_mai_entries_are_chosen_by_formula_and_skeleton(tmp_path):
    benzene = F.skeleton(F.xyz_block(*_ring(6)))
    z = tmp_path / "m.zip"
    with zipfile.ZipFile(z, "w") as w:
        w.writestr("IR_COMPAS/charge_0/C1M000001.xyz", _entry("C6H6", 6))
        w.writestr("IR_COMPAS/charge_1/C1M000001.xyz", _entry("C6H6", 6))       # a cation of the same molecule is not read
        w.writestr("IR_COMPAS/charge_0/C1M000009.xyz", _entry("C6H6", 8))       # same formula label, another skeleton: not ours
    name, scaled, factor = F.mai_spectra(z, {"C6H6": benzene})["C6H6"]
    assert name == "C1M000001" and scaled.tolist() == [1000.0, 3000.0] and factor.tolist() == [0.956, 0.960]


def test_duplicates_of_one_molecule_must_agree(tmp_path):
    benzene = F.skeleton(F.xyz_block(*_ring(6)))
    z = tmp_path / "m.zip"
    with zipfile.ZipFile(z, "w") as w:
        w.writestr("IR_COMPAS/charge_0/C1M000001.xyz", _entry("C6H6", 6))
        w.writestr("IR_COMPAS/charge_0/C2M000001.xyz", _entry("C6H6", 6, first=1000.4))
    assert F.mai_spectra(z, {"C6H6": benzene})["C6H6"][0] == "C1M000001, C2M000001"
    with zipfile.ZipFile(z, "a") as w:
        w.writestr("IR_COMPAS/charge_0/C3M000001.xyz", _entry("C6H6", 6, first=1004.0))
    with pytest.raises(ValueError, match="disagree by more than"):
        F.mai_spectra(z, {"C6H6": benzene})


def test_stats_per_family_and_all():
    out = F.stats({"CH-oop": [1.0, -3.0], "ring-ip": [2.0]})
    assert out["CH-oop"] == {"n": 2, "mean": -1.0, "rms": pytest.approx(np.sqrt(5.0))}
    assert out["other"]["n"] == 0 and out["all"]["n"] == 3


def test_a_mixed_pair_is_resolved_one_to_one_from_the_vectors():
    """Rotate benzene's (CC/TZ) a1g breathing mode and a b1u mode into each other by 30°: the projector weights give the larger share back."""
    symbols = ["C"] * 6 + ["H"] * 6
    freq, V, coords = modes_of("probes/results_m1/e8_benzene_ccpvtz_oop_2026-10-03/hessian_ccsd_t.npz", symbols)
    labels, _ = F.d6h_irreps(V, freq, symbols, coords)
    i, j = labels.index("a1g"), labels.index("b1u")
    c, s = np.cos(np.pi / 6), np.sin(np.pi / 6)
    mixed = V.copy()
    mixed[:, i], mixed[:, j] = c * V[:, i] + s * V[:, j], -s * V[:, i] + c * V[:, j]
    chosen, note = F.resolve_mixed(mixed, [i, j], ["A1g", "B1u"], symbols, coords)
    assert chosen == {i: "A1g", j: "B1u"} and "A1g 0.75" in note
