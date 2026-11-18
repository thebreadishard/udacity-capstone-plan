"""Tests of the Spectrum Atlas export on three molecules of the real corpus (benzene, naphthalene, one A2 molecule) — no compute, seconds."""
import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import build_catalog as bc  # noqa: E402

# ATLAS_REPO: a worktree has the code but not the ignored corpus data; point the build at a checkout that has them
REPO = os.environ.get("ATLAS_REPO") or os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CORPUS = os.path.join(REPO, "plans", "05_delta-probed-ir-pipeline", "modules", "05_support_predictor", "corpus", "molecules")


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    out = tmp_path_factory.mktemp("atlas")
    summary = bc.build(REPO, str(out), limit=60)
    return out, summary


def test_heights_for_benzene_aligned_and_none_for_naphthalene(built):
    """TASKS 44 (10 Oct 2026): band heights from module 08's shape, aligned with the listed B3LYP positions; positions only without an APT."""
    out, summary = built
    def read(name):
        with open(os.path.join(out, "molecules", name), encoding="utf-8") as f:
            return json.load(f)
    b = read("A_8448043181.json")
    pos, h = b["frequencies_cm"]["b3lyp"]["vibrational"], b["intensities_km_mol"]["b3lyp"]
    assert len(h) == len(pos) == 30 and b["shape"]["n_ir_active"] == 7 and b["predicted_spectrum"] is None
    i = max(range(30), key=lambda k: h[k])
    assert abs(pos[i] - 694.6) < 0.5 and 70 < h[i] < 85                  # benzene's C–H out-of-plane band (a2u)
    n = read("A_01f3186607.json")
    assert n["intensities_km_mol"] is None and n["shape"] is None
    assert summary["n_with_intensities"] >= 1 and summary["shape_accuracy"]["holdouts"]["a"]["shape"]["corrected"]["spectrum_overlap"] > 0.9
    assert summary["licence"]["licensed_families"] == ["ring-ip", "CH-stretch", "CH-oop", "other"]   # v1.4, carried since 18 Nov 2026


def test_anchor_pages_carry_the_anchor_spectrum(built):
    """TASKS 45 (10 Oct 2026): benzene's anchor spectrum has heights from its own CC APT and a comparison that reproduces T3's zero-rule overlap;
    naphthalene's anchor is positions only; when T3's fold files exist, benzene's test series reproduces T3's own λ = 1 read (0.406/0.355/0.354)."""
    out, summary = built
    def read(name):
        with open(os.path.join(out, "molecules", name), encoding="utf-8") as f:
            return json.load(f)
    b = read("A_8448043181.json")
    assert b["anchor_spectrum"]["apt_level"].startswith("CCSD(T)") and abs(b["comparison"]["spectrum_overlap"] - 0.257) < 0.005
    n = read("A_01f3186607.json")
    assert n["anchor_spectrum"]["kind"] == "positions only" and n["comparison"]["spectrum_overlap"] is None and n["test_prediction"] is None
    assert summary["n_anchor_spectra"] >= 2
    tp = b["test_prediction"]
    if tp is not None:
        assert "not a served prediction" in tp["label"] and len(tp["seeds"]) == 3
        assert abs(tp["spectrum_overlap_mean"] - 0.372) < 0.01                 # T3's own read of the λ = 1 column, a second route


def test_heights_refused_when_positions_differ():
    sh = {"kind": "positions and heights", "sticks": [{"omega_cm": 100.0, "km_mol": 1.0}], "max_dev_from_listed_cm": 2.0, "vib_min_cm": 20.0}
    assert bc.heights_for(sh, [102.0]) is None
    assert bc.heights_for(dict(sh, max_dev_from_listed_cm=0.0), [100.0]) == [1.0]
    assert bc.heights_for(dict(sh, max_dev_from_listed_cm=0.0), [100.0, -4.66]) == [1.0, None]   # stilbene: a listed mode below the threshold
    assert bc.heights_for({"kind": "positions only"}, [100.0]) is None


def test_rung_counts_add_up(built):
    out, s = built
    cat = json.load(open(out / "catalog.json", encoding="utf-8"))
    assert sum(s["rung_counts"].values()) == len(cat) == s["n_molecules"]


def test_benzene_is_validated_with_evidence(built):
    out, _ = built
    cat = {r["id"]: r for r in json.load(open(out / "catalog.json", encoding="utf-8"))}
    b = cat["A_8448043181"]
    assert b["rung_label"] == "validated" and b["formula"] == "C6H6"
    for f in b["evidence"]:
        assert os.path.exists(os.path.join(REPO, "plans", "05_delta-probed-ir-pipeline", f))


def test_naphthalene_molecule_file(built):
    out, _ = built
    m = json.load(open(out / "molecules" / "A_01f3186607.json", encoding="utf-8"))
    assert m["formula"] == "C10H8" and m["n_atoms"] == 18
    for tag in ("b3lyp", "wb97x"):
        assert len(m["frequencies_cm"][tag]["all"]) == 54 and len(m["frequencies_cm"][tag]["vibrational"]) == 48
    assert any(r.startswith("layerA_") for r in m["releases"])


def test_second_route_flag_on_benzene(built):
    out, _ = built
    cat = {r["id"]: r for r in json.load(open(out / "catalog.json", encoding="utf-8"))}
    assert "second_route_disagrees" in cat["A_8448043181"]["flags"] and "replaced_by_second_route" in cat["A_8448043181"]["flags"]


def test_frequency_lengths_are_3N_everywhere(built):
    out, _ = built
    for p in (out / "molecules").glob("*.json"):
        m = json.load(open(p, encoding="utf-8"))
        for tag in ("b3lyp", "wb97x"):
            assert len(m["frequencies_cm"][tag]["all"]) == 3 * m["n_atoms"]


def test_changelog_reads_a_head_over_two_lines(tmp_path):
    """14 Oct 2026: entries whose bold head runs over two lines were dropped; the body is cut at the next item, heading or blank line."""
    md = tmp_path / "ledger.md"
    md.write_text("# Ledger\n\n- **14 Oct, 12:3x — a head that runs\nover two lines.** Body starts here\nand goes on.\n"
                  "- **13 Oct, 09:0x — one line.** Short.\n\n## Next\n- **12 Oct, 08:0x — no closing bold on this line\n", encoding="utf-8")
    got = bc.read_changelog(str(md))
    assert [(e["date"], e["title"]) for e in got] == [("2026-10-14", "a head that runs over two lines."), ("2026-10-13", "one line.")]
    assert got[0]["body"] == "Body starts here and goes on."
    md.write_text("- **24 Sep, 07:3x — a head never closed: the rest follows. More text.\n", encoding="utf-8")
    assert [(e["title"], e["body"]) for e in bc.read_changelog(str(md))] == [("a head never closed:", "the rest follows. More text.")]
    md.write_text("- **14 Oct, 12:3x — a `file.py` head.** **(1) Withdrawn:** see `x`.\n", encoding="utf-8")
    assert [(e["title"], e["body"]) for e in bc.read_changelog(str(md))] == [("a file.py head.", "(1) Withdrawn: see x.")]


def test_vib_only_drops_six():
    import numpy as np
    f = np.array([-30.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 100.0, 200.0])
    assert list(bc.vib_only(f)) == [-30.0, 100.0, 200.0]


def test_source_per_layer(built):
    out, summary = built
    catalog = json.load(open(os.path.join(out, "catalog.json"), encoding="utf-8"))
    assert all(r["source"] for r in catalog) and sum(summary["source_counts"].values()) == len(catalog)
    known = bc.source_of(dict(layer="G", note="source=generator v0.1+v0.2; list abc; system c1ccc2ccccc2c1; bare system; pubchem yes; rank 1"))
    new = bc.source_of(dict(layer="G", note="source=generator v0.1+v0.2; list abc; system c1ccncc1; most frequent molecule; pubchem no; rank 2"))
    assert known.endswith("known to PubChem") and new.endswith("not in PubChem")
    assert bc.source_of(dict(layer="C", note="")) == bc.SOURCES["C"]
    assert bc.source_of(dict(layer="R4", note="rung4 chrysene")) == bc.SOURCES["R4"]          # 15 Oct 2026: rung 4's rows, TASKS 61
    assert bc.source_of(dict(layer="T", note="")) == bc.SOURCES["T"] and bc.source_of(dict(layer="D", note="")) == bc.SOURCES["D"]
    with pytest.raises(KeyError):
        bc.source_of(dict(layer="Z", note=""))


def test_anchored_rows_follow_the_registry(built):
    out, _ = built
    cat = {r["id"]: r for r in json.load(open(out / "catalog.json", encoding="utf-8"))}
    ev, level = bc.anchored_from_registry(os.path.join(REPO, "plans", "05_delta-probed-ir-pipeline"))
    for mid, row in cat.items():
        if row["rung"] >= 4:
            assert row["evidence"][0] == ev[mid][0] and row["anchor_level"] == level[mid]
    assert level.get("A_8448043181") == "CCSD(T)/cc-pVTZ"


def test_anchor_readings_travel_with_the_registry_file(built):
    """8 Oct 2026: benzene's R0 diagonal reading stays in its evidence after the registry's Hessian (module 08's certificate reads it)."""
    out, _ = built
    b = {r["id"]: r for r in json.load(open(out / "catalog.json", encoding="utf-8"))}["A_8448043181"]
    assert any(f.endswith("R0_DIAGONAL_READING_2026-09-22.md") for f in b["evidence"][1:])


def test_an_analytic_only_folder_reads_its_analytic_hessians(built):
    """TASKS 49's large PAHs carry analytic labels only: no finite-difference Hessian, and an analytic check without corpus
    frequencies. The export reads the analytic files and states no second route; a finite-difference folder with such a check raises."""
    from m08 import spectrum                               # on the path once build() has run
    mdir = os.path.join(CORPUS, "T_94b3a9d13a")              # coronene
    if not os.path.isdir(mdir):
        pytest.skip("no corpus data in this checkout (set ATLAS_REPO)")
    from pathlib import Path
    assert spectrum.analytic_only(Path(mdir)) and spectrum.listed_hessian(Path(mdir), "wb97x").name == "hessian_wb97x_analytic.npz"
    benzene = Path(CORPUS) / "A_8448043181"                  # finite-difference labels beside an analytic second route
    assert not spectrum.analytic_only(benzene) and spectrum.listed_hessian(benzene).name == "hessian_b3lyp.npz"
    assert bc.second_route_of(mdir, True) is None
    with pytest.raises(ValueError, match="no corpus frequencies"):
        bc.second_route_of(mdir, False)


def test_summary_states_the_network_pair(built):
    """Decision 66: the summary says which networks print the spectra; errors and licence are the measurement networks'."""
    _, summary = built
    pair, acc = summary["networks"], summary["shape_accuracy"]
    assert pair["kind"] in ("release", "measurement") and pair["measurement_networks"] >= 1
    if pair["kind"] == "release":
        assert pair["trained_on_entries"] > 0 and pair["fitting"].startswith("each of the") and pair["held_back"] is None
    assert acc["version"] and set(summary["licence"]["licensed_families"]) <= set(acc["holdouts"]["a"]["product"])
    assert summary["licence"]["line_cm"] == 3 and summary["higher_level_name"] == "ωB97X/6-31G*"
    assert acc["higher_level"].startswith(summary["higher_level_name"])
    lo, hi = pair["pool_atoms"]
    assert 0 < lo < hi and (pair["kind"] != "release" or 0 < pair["distinct_entries"] <= pair["trained_on_entries"])


def test_pool_counts_rows_and_distinct_molecule_charge_pairs():
    rows = [dict(id="A_1", smiles="c1ccccc1", n_atoms="12", note=""), dict(id="B_1", smiles="c1ccccc1", n_atoms="12", note=""),
            dict(id="P3c_1", smiles="c1ccccc1", n_atoms="12", note="pool3 cation; charge 1 mult 2"),
            dict(id="A_2", smiles="c1ccc2ccccc2c1", n_atoms="18", note=""),
            dict(id="B_2", smiles="O=Cc1c[nH]cn1", n_atoms="11", note=""), dict(id="B_3", smiles="O=Cc1cnc[nH]1", n_atoms="11", note="")]
    assert bc.pool_of({"A_1", "B_1", "P3c_1", "A_2", "B_2", "B_3"}, rows) == dict(entries=6, distinct=5, atoms=[11, 18])   # tautomers apart
    with pytest.raises(ValueError, match="without a manifest row"):
        bc.pool_of({"A_1", "Z_9"}, rows)


def test_licence_line_refuses_mixed_lines():
    one = {"holdouts": {h: {"product": {"ring-ip": {"target": 3.0}, "other": {"target": 3.0}}} for h in "ab"}}
    assert bc.licence_line(one) == 3.0
    one["holdouts"]["b"]["product"]["other"]["target"] = 4.0
    with pytest.raises(ValueError, match="differ"):
        bc.licence_line(one)


def _analytic_folder(path, versions, grids):
    import numpy as np
    path.mkdir()
    check = {tag: {"software": {"pyscf": v}} for tag, v in zip(("b3lyp", "wb97x"), versions, strict=True)}
    (path / "analytic_check.json").write_text(json.dumps(check), encoding="utf-8")
    for tag, grid in zip(("b3lyp", "wb97x"), grids, strict=True):
        np.savez(path / f"hessian_{tag}_analytic.npz", grid=np.array(grid))
    return str(path)


def test_deck_of_refuses_two_pyscf_versions_or_grids(tmp_path):
    result = {"deck": {"deck": "v1", "hessian": "psi4 finite differences", "text_corrections": ["…"]}}
    good = _analytic_folder(tmp_path / "good", ("2.14.0", "2.14.0"), ((99, 590), (99, 590)))
    deck = bc.deck_of(result, good, True)
    assert deck["hessian"].startswith("pyscf 2.14.0 ") and "(99, 590)" in deck["hessian"] and "text_corrections" not in deck
    assert bc.deck_of(result, good, False) is result["deck"]
    for name, versions, grids in (("versions", ("2.14.0", "2.15.0"), ((99, 590),) * 2), ("grids", ("2.14.0",) * 2, ((99, 590), (75, 302)))):
        with pytest.raises(ValueError, match="one deck has one of each"):
            bc.deck_of(result, _analytic_folder(tmp_path / name, versions, grids), True)


ANALYTIC_ONLY = ("D_210c3076e6", "T_94b3a9d13a")   # PAHdb 284 (its APT passed its checks) and coronene (its APT failed the sum rule)


@pytest.fixture(scope="module")
def built_analytic(tmp_path_factory):
    if not os.path.isdir(os.path.join(CORPUS, ANALYTIC_ONLY[0])):
        pytest.skip("no corpus data in this checkout (set ATLAS_REPO)")
    out = tmp_path_factory.mktemp("atlas_analytic")
    return out, bc.build(REPO, str(out), ids=set(ANALYTIC_ONLY))


def test_analytic_only_molecules_go_through_the_real_loop(built_analytic):
    """The review of 4f985958: a D molecule gets heights from its analytic Hessian and its passed APT; coronene, whose APT failed,
    says so; both decks name the analytic route and neither carries a second route."""
    out, summary = built_analytic
    assert summary["n_molecules"] == 2 and summary["n_with_intensities"] == 1
    mols = []
    for mid in ANALYTIC_ONLY:
        with open(out / "molecules" / f"{mid}.json", encoding="utf-8") as f:
            mols.append(json.load(f))
    d, t = mols
    assert d["intensities_km_mol"] and d["shape"]["hessian_source"].endswith("hessian_b3lyp_analytic.npz") and d["heights_missing"] is None
    assert t["intensities_km_mol"] is None and "failed their own check" in t["heights_missing"]
    for m in (d, t):
        assert m["deck"]["hessian"].startswith("pyscf ") and m["deck"]["labels"] == "analytic_only" and m["second_route"] is None
        assert len(m["frequencies_cm"]["b3lyp"]["all"]) == 3 * m["n_atoms"]


def test_limit_and_ids_do_not_combine(tmp_path):
    with pytest.raises(ValueError, match="not both"):
        bc.build(REPO, str(tmp_path), limit=5, ids={"A_8448043181"})
    with pytest.raises(ValueError, match="no manifest row"):
        bc.build(REPO, str(tmp_path), ids={"Z_nothing"})
