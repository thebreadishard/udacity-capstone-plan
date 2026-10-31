"""The corpus's Hessian and APT reused by the pipeline (`modules/08_industry_synthesis/m08/reuse.py`, TASKS 150), without a machine: source
folders built from the frozen corpus with today's APT fields, every refusal one field at a time, the canonical order derived from a folder
stored in another SMILES writing's order, the network's spectrum of a reused folder equal to the source's and unchanged by a rotation of
the frame (the pin model), the pipeline's switch, and the runtime fit that leaves reused runs out."""
from __future__ import annotations

import csv
import json
import shutil
import sys
from pathlib import Path

import numpy as np
import pytest

from pin_tools import DATA, PIN_CORPUS, PLAN, require_frozen_corpus

sys.path.insert(0, str(PLAN / "modules" / "08_industry_synthesis"))
from m08 import pipeline as P
from m08 import reuse as R
from m08 import runtime as RT

PIN_MODEL = DATA / "rungC_cc_pin_model.pt"
BENZENE, PHENANTHRENE = "A_8448043181", "A_541c53d1a5"
SMILES = "c1ccccc1"
PHEN_CANONICAL, PHEN_OTHER = "c1ccc2c(c1)ccc1ccccc12", "c1ccc2c3ccccc3ccc2c1"


def pipeline_start(canonical: str) -> R.Start:
    xyz, _optimise = P.RC.start_geometry({"layer": "A", "smiles": canonical})
    return R.Start(np.asarray([row[1:] for row in xyz], float), P.RC.opt_options_for({"smiles": canonical}))


def other_writing_order(written: str, canonical: str) -> np.ndarray:
    """perm[i] = the canonical AddHs atom at position i of `written`'s AddHs order (an RDKit match: one of the symmetry's choices)."""
    from rdkit import Chem

    return np.asarray(Chem.AddHs(Chem.MolFromSmiles(canonical)).GetSubstructMatch(Chem.AddHs(Chem.MolFromSmiles(written))), int)


def write_source(d: Path, mol_id: str = BENZENE, canonical: str = SMILES, perm: np.ndarray | None = None, **apt_over) -> None:
    """A frozen-corpus folder (canonical SMILES, AddHs order) as a folder of today's corpus: refined APT fields, the Hessian's charge, spin
    and grid, its analytic check and the job that started it from the pipeline's own start — atoms optionally stored in another order
    (perm[i] = the original atom at position i)."""
    src = PIN_CORPUS / "molecules" / mol_id
    d.mkdir(parents=True)
    g = json.loads((src / R.GEOMETRY).read_text(encoding="utf-8"))
    p = np.arange(len(g["symbols"])) if perm is None else perm
    c = (3 * p[:, None] + np.arange(3)[None, :]).ravel()
    (d / R.GEOMETRY).write_text(json.dumps({**g, **{k: [g[k][i] for i in p] for k in ("symbols", "coords_bohr", "masses_amu")}}), encoding="utf-8")
    with np.load(src / R.HESSIAN) as z:
        h = {k: z[k] for k in z.files}
    h.update(H_projected=h["H_projected"][np.ix_(c, c)], charge=np.array(0), spin=np.array(0), grid=np.array(P.LOW_GRID))
    h["H_raw"] = h["H_raw"][np.ix_(c, c)] if "H_raw" in h else h["H_projected"]
    np.savez(d / R.HESSIAN, **h)
    with np.load(src / R.APT) as z:
        a = {k: z[k] for k in z.files}
    a.update(apt=a["apt"][:, c], route=np.array(R.APT_ROUTE), cphf_residual_after=np.array(1e-7), passed=np.array(True),
             grid=np.array(P.LOW_GRID), sum_rule_max=np.array(5e-5), xc=np.array("b3lyp"), basis=np.array("6-31g*"))
    a.update({k: np.array(v) for k, v in apt_over.items()})
    np.savez(d / R.APT, **a)
    shutil.copy(src / R.RESULT, d / R.RESULT)
    (d / R.CHECK).write_text(json.dumps({"b3lyp": {"freq_analytic": [1.0]}}), encoding="utf-8")
    start = pipeline_start(canonical)
    (d / R.JOB).write_text(json.dumps({"xyz_angstrom": [[s, *map(float, r)] for s, r in zip(g["symbols"], start.xyz_angstrom[p], strict=True)]}),
                           encoding="utf-8")


def corpus(tmp_path: Path, rows: tuple[tuple[str, str], ...] = ((BENZENE, SMILES),), folder_kw: dict | None = None, **apt_over) -> Path:
    root = tmp_path / "corpus"
    for i, _smiles in rows:
        write_source(root / "molecules" / i, **(folder_kw or {}), **apt_over)
    with (root / "manifest.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["id", "layer", "smiles", "status"])
        w.writerows([i, "A", smiles, "done"] for i, smiles in rows)
    return root


@pytest.fixture
def frozen():
    require_frozen_corpus()


def test_a_folder_at_the_pipelines_settings_is_reused(tmp_path, frozen):
    rec = R.assess(SMILES, pipeline_start(SMILES), corpus(tmp_path), P.REUSE_SETTINGS)
    assert rec["reused"] and rec["order"] == list(range(12)) and rec["start_rmsd_angstrom"] < 1e-9


def mutate_npz(path: Path, **over) -> None:
    with np.load(path) as z:
        a = {k: z[k] for k in z.files}
    a.update({k: np.array(v) for k, v in over.items()})
    np.savez(path, **a)


def edit_json(path: Path, **over) -> None:
    path.write_text(json.dumps(json.loads(path.read_text(encoding="utf-8")) | over), encoding="utf-8")


@pytest.mark.parametrize("change, reason", [
    (lambda d: mutate_npz(d / R.APT, route="cphf"), "computed before the residual check"),
    (lambda d: mutate_npz(d / R.APT, cphf_residual_after=2e-6), "CPHF residual"),
    (lambda d: mutate_npz(d / R.APT, sum_rule_max=6e-4), "APT sum rule"),
    (lambda d: mutate_npz(d / R.APT, passed=False), "failed its checks"),
    (lambda d: mutate_npz(d / R.APT, grid=[75, 302]), "not B3LYP/6-31G*"),
    (lambda d: mutate_npz(d / R.HESSIAN, charge=1), "not neutral closed shell"),
    (lambda d: mutate_npz(d / R.HESSIAN, grid=[75, 302]), "not neutral closed shell"),
    (lambda d: (d / R.CHECK).unlink(), "lacks analytic_check.json"),
    (lambda d: edit_json(d / R.RESULT, n_imaginary_b3lyp=1), "imaginary"),
    (lambda d: edit_json(d / R.RESULT, deck={"deck": "v1", "dft_radial_points": 99}), "numerics"),
    (lambda d: edit_json(d / R.JOB, opt_options={"x": 1}), "optimised with options"),
])
def test_each_mismatch_is_refused_with_its_reason(tmp_path, frozen, change, reason):
    root = corpus(tmp_path)
    change(root / "molecules" / BENZENE)
    rec = R.assess(SMILES, pipeline_start(SMILES), root, P.REUSE_SETTINGS)
    assert not rec["reused"] and any(reason in w for w in rec["why"]), rec["why"]


def test_another_start_geometry_is_refused(tmp_path, frozen):
    start = pipeline_start(SMILES)
    far = R.Start(start.xyz_angstrom + np.linspace(0, 0.2, start.xyz_angstrom.size).reshape(start.xyz_angstrom.shape), start.opt_options)
    rec = R.assess(SMILES, far, corpus(tmp_path), P.REUSE_SETTINGS)
    assert not rec["reused"] and "may reach another minimum" in rec["why"][0]


def test_atoms_outside_their_smiles_order_are_refused(tmp_path, frozen):
    root = corpus(tmp_path, folder_kw={"perm": np.roll(np.arange(12), 1)})       # an H first: not the AddHs order
    rec = R.assess(SMILES, pipeline_start(SMILES), root, P.REUSE_SETTINGS)
    assert not rec["reused"] and "not in its SMILES's AddHs order" in rec["why"][0]


def test_no_folder_and_the_first_passing_of_several(tmp_path, frozen):
    assert R.assess("c1ccncc1", pipeline_start(SMILES), corpus(tmp_path), P.REUSE_SETTINGS)["why"] == ["the corpus has no folder of this molecule"]
    root = corpus(tmp_path / "two", rows=(("A_1", SMILES), ("B_2", SMILES)))
    mutate_npz(root / "molecules" / "A_1" / R.HESSIAN, charge=1)          # a cation row carries its parent's SMILES
    rec = R.assess(SMILES, pipeline_start(SMILES), root, P.REUSE_SETTINGS)
    assert rec["reused"] and rec["source"].endswith("B_2")


def bonds(d: Path) -> set[frozenset[int]]:
    g = json.loads((d / R.GEOMETRY).read_text(encoding="utf-8"))
    return R._geometry_bonds(g["symbols"], np.asarray(g["coords_bohr"], float))


def test_a_folder_in_another_writings_order_is_written_in_the_canonical_order(tmp_path, frozen):
    from rdkit import Chem

    perm = other_writing_order(PHEN_OTHER, PHEN_CANONICAL)
    assert not np.array_equal(perm, np.arange(24))
    root = corpus(tmp_path, rows=((PHENANTHRENE, PHEN_OTHER),), folder_kw={"mol_id": PHENANTHRENE, "canonical": PHEN_CANONICAL, "perm": perm})
    out = tmp_path / "out"
    out.mkdir()
    rec = R.reuse(PHEN_CANONICAL, pipeline_start(PHEN_CANONICAL), out, root, P.REUSE_SETTINGS)
    assert rec["reused"] and rec["start_rmsd_angstrom"] < 1e-9 and set(rec["sha256"]) == set(R.SOURCE_FILES)
    can = Chem.AddHs(Chem.MolFromSmiles(PHEN_CANONICAL))
    assert bonds(out) == {frozenset((b.GetBeginAtomIdx(), b.GetEndAtomIdx())) for b in can.GetBonds()}
    masses = np.asarray(json.loads((out / R.GEOMETRY).read_text(encoding="utf-8"))["masses_amu"], float)
    straight = PIN_CORPUS / "molecules" / PHENANTHRENE
    m0 = np.asarray(json.loads((straight / R.GEOMETRY).read_text(encoding="utf-8"))["masses_amu"], float)
    with np.load(out / R.HESSIAN) as h, np.load(out / R.APT) as a, np.load(straight / R.HESSIAN) as h0, np.load(straight / R.APT) as a0:
        f, i = P.mode_intensities(h["H_projected"], masses, a["apt"])
        f0, i0 = P.mode_intensities(h0["H_projected"], m0, a0["apt"])
    assert np.allclose(np.sort(f), np.sort(f0), atol=1e-8) and np.allclose(np.sort(i), np.sort(i0), atol=1e-8)


def network_spectrum(d: Path) -> list[float]:
    dH, seeds = P.correction((PIN_MODEL,), d)
    return [s["omega_cm"] for s in P.spectra(d, dH, seeds)["network"]["sticks"]]


def rotate(src: Path, dst: Path, Rm: np.ndarray) -> None:
    shutil.copytree(src, dst)
    g = json.loads((src / R.GEOMETRY).read_text(encoding="utf-8"))
    g["coords_bohr"] = (np.asarray(g["coords_bohr"]) @ Rm.T).tolist()
    (dst / R.GEOMETRY).write_text(json.dumps(g), encoding="utf-8")
    big = np.kron(np.eye(len(g["symbols"])), Rm)
    with np.load(src / R.HESSIAN) as z:
        h = {k: z[k] for k in z.files}
    h["H_projected"], h["H_raw"] = big @ h["H_projected"] @ big.T, big @ h["H_raw"] @ big.T
    np.savez(dst / R.HESSIAN, **h)
    with np.load(src / R.APT) as z:
        a = {k: z[k] for k in z.files}
    a["apt"] = Rm @ a["apt"] @ big.T
    np.savez(dst / R.APT, **a)


def test_the_networks_spectrum_of_a_reused_folder_is_the_sources_and_does_not_depend_on_the_frame(tmp_path, frozen):
    root = corpus(tmp_path)
    out = tmp_path / "out"
    out.mkdir()
    R.reuse(SMILES, pipeline_start(SMILES), out, root, P.REUSE_SETTINGS)
    assert network_spectrum(out) == network_spectrum(root / "molecules" / BENZENE)
    c, s = np.cos(0.7), np.sin(0.7)
    rotate(out, tmp_path / "rot", np.array([[c, -s, 0.0], [s, c, 0.0], [0.0, 0.0, 1.0]]) @ np.array([[1.0, 0, 0], [0, c, -s], [0, s, c]]))
    assert np.allclose(network_spectrum(tmp_path / "rot"), network_spectrum(out), atol=1e-4)


def config(tmp_path: Path, **kw) -> P.PipelineConfig:
    base = dict(name="mol", out_root=tmp_path / "out", smiles=SMILES, models=(PIN_MODEL,), psi4_python=Path(sys.executable))
    return P.PipelineConfig(**(base | kw))


def test_the_switch_and_an_xyz_input_compute(tmp_path):
    xyz = tmp_path / "b.xyz"
    xyz.write_text("1\n\nH 0 0 0\n", encoding="utf-8")
    assert P.from_corpus(config(tmp_path, reuse_corpus=False), [], None)["why"] == ["switched off (--no-reuse)"]
    assert P.from_corpus(config(tmp_path, smiles=None, xyz=xyz), [], None)["why"] == ["an xyz input is optimised from its own geometry"]


def test_a_reused_run_skips_the_optimisation_and_the_low_level(tmp_path, frozen, monkeypatch):
    cfg = config(tmp_path, corpus=corpus(tmp_path))
    cfg.folder.mkdir(parents=True)
    monkeypatch.setattr(P, "optimise", lambda *a: pytest.fail("optimised although the corpus holds the molecule"))
    monkeypatch.setattr(P, "low_level", lambda *a: pytest.fail("computed the low level although the corpus holds it"))
    seconds: dict[str, float] = {}
    psi4, check, reused = P.low_level_files(cfg, seconds)
    assert reused["reused"] and list(seconds) == ["reuse"] and psi4["status"] == "done" and "b3lyp" in check
    assert (cfg.folder / P.RI.LOW_HESSIAN).is_file() and P.cheap_apt(cfg.folder) is not None


def test_a_refused_corpus_computes_and_says_why(tmp_path, frozen, monkeypatch, capsys):
    cfg = config(tmp_path, corpus=corpus(tmp_path, route="cphf"))
    monkeypatch.setattr(P, "optimise", lambda *a: {"status": "done"})
    monkeypatch.setattr(P, "low_level", lambda cfg: {"b3lyp": {}})
    seconds: dict[str, float] = {}
    _, _, reused = P.low_level_files(cfg, seconds)
    assert not reused["reused"] and set(seconds) == {"optimise", "low_level"}
    assert "computed, not reused" in capsys.readouterr().out


def test_the_runtime_fit_leaves_reused_runs_out(tmp_path, monkeypatch):
    monkeypatch.setattr(RT, "host_class", lambda host: "laptop")
    monkeypatch.setattr(RT.AP, "basis_functions", lambda smiles, table: 100)
    for name, reuse in (("computed", {"reused": False, "why": ["x"]}), ("old", None), ("reused", {"reused": True})):
        d = tmp_path / "pipeline_x" / name
        d.mkdir(parents=True)
        rec = {"provenance": {"host": "h"}, "settings": {"threads": 4}, "input": {"smiles": SMILES}, "seconds": {"a": 10.0}}
        if reuse is not None:                     # records before 0.5 carry no reuse entry
            rec["reuse"] = reuse
        (d / "pipeline.json").write_text(json.dumps(rec), encoding="utf-8")
    assert sorted(f for _, _, f in RT.timed_runs(4, tmp_path)) == ["pipeline_x/computed", "pipeline_x/old"]


@pytest.mark.skipif(sys.platform != "win32", reason="the WSL step's command names the laptop's Windows paths")
def test_the_low_level_command_names_the_grid_reuse_compares():
    assert f"--grid {P.LOW_GRID[0]},{P.LOW_GRID[1]}" in P.low_level_command(config(Path.cwd() / "x"))[4]
