"""The pipeline's first version (`modules/08_industry_synthesis/m08/pipeline.py`, TASKS 146) without a machine: the settings and every
refusal before any computation, the external steps' commands and failure paths (the commands are captured, not run), and steps 4–5 on
the frozen corpus's benzene with the transfer pin's model (`tests/data/rungC_cc_pin_model.pt`, never a carried model's file)."""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import numpy as np
import pytest

from pin_tools import DATA, PIN_CORPUS, PLAN, require_frozen_corpus

sys.path.insert(0, str(PLAN / "modules" / "08_industry_synthesis"))
from m08 import pipeline as P
from m08.spectrum import series

PIN_MODEL = DATA / "rungC_cc_pin_model.pt"
BENZENE = "A_8448043181"
TRAINING = (("C", "H", "N", "O"), (6, 40))


def config(tmp_path: Path, **kw) -> P.PipelineConfig:
    base = dict(name="mol", out_root=tmp_path, smiles="c1ccccc1", models=(PIN_MODEL,), psi4_python=Path(sys.executable))
    return P.PipelineConfig(**(base | kw))


@pytest.fixture
def pin_registry(monkeypatch):
    """The pin model counts as carried and the training set is fixed, so the refusals are tested without the registry's files."""
    monkeypatch.setattr(P.MR, "require_carried", lambda p: {"status": "carried", "network": P.NETWORK, "version": "pin"})
    monkeypatch.setattr(P, "training_set", lambda models: TRAINING)


@pytest.mark.parametrize("kw, match", [
    (dict(smiles=None), "exactly one of smiles and xyz"),
    (dict(xyz=Path(__file__)), "exactly one of smiles and xyz"),
    (dict(charge=1), "neutral closed-shell"),
    (dict(multiplicity=2), "neutral closed-shell"),
    (dict(name="a b"), "pattern"),
    (dict(psi4_python=Path("no_such_python.exe")), "CORPUS_QC_PYTHON"),
    (dict(models=()), "no model"),
    (dict(threads=0), "greater than or equal"),
    (dict(unknown=1), "Extra inputs"),
])
def test_settings_that_do_not_combine_are_refused_when_built(tmp_path, kw, match):
    with pytest.raises(ValueError, match=match):
        config(tmp_path, **kw)


def test_the_default_models_are_the_carried_seeds_of_one_version():
    models = P.carried_models()
    status = P.MR.read_status(P.MR.STATUS_FILE)
    assert len(models) == 3 and len({status[m.name]["version"] for m in models}) == 1
    assert all(status[m.name]["network"] == P.NETWORK and status[m.name]["status"] == "carried" for m in models)


@pytest.mark.parametrize("smiles, reason", [
    ("C1CCCCC1", "no aromatic ring"),
    ("[CH2]c1ccccc1", "unpaired electrons"),
    ("c1cc[nH+]cc1", "net formal charge"),
    ("Brc1ccccc1", "element(s) BR outside"),
    ("c1ccccc1(", "does not parse"),
])
def test_a_molecule_outside_the_models_reach_is_refused(tmp_path, pin_registry, smiles, reason):
    with pytest.raises(P.Refused, match=reason.replace("(", r"\(").replace(")", r"\)")):
        P.admit(config(tmp_path, smiles=smiles))


def test_a_model_that_is_not_carried_is_refused(tmp_path):
    superseded = PLAN / "modules" / "05_support_predictor" / "out" / "E7_rungC_chain34_kdfamily_750_2026-10-05_model_n750_seed0.pt"
    with pytest.raises(P.Refused, match="superseded"):
        P.admit(config(tmp_path, models=(superseded,)))


def test_a_used_output_folder_is_refused_and_nothing_runs(tmp_path, pin_registry, monkeypatch):
    (tmp_path / "mol").mkdir()
    (tmp_path / "mol" / "pipeline.json").write_text("{}", encoding="utf-8")
    monkeypatch.setattr(P, "start_geometry", lambda cfg: pytest.fail("a step ran after a refusal"))
    with pytest.raises(P.Refused, match="never overwritten"):
        P.run(config(tmp_path))


def test_benzene_is_admitted_with_its_size_against_the_training_range(tmp_path, pin_registry):
    adm = P.admit(config(tmp_path))
    assert adm.elements == ("C", "H") and adm.n_atoms == 12 and adm.inside_training_sizes
    assert adm.smiles == "c1ccccc1" and adm.formula == "C6H6"


def test_the_xyz_input_is_read_as_given(tmp_path, pin_registry):
    g = json.loads((PIN_CORPUS / "molecules" / BENZENE / "geometry.json").read_text(encoding="utf-8"))
    b = 0.529177210903
    rows = [f"{s} {x * b:.8f} {y * b:.8f} {z * b:.8f}" for s, (x, y, z) in zip(g["symbols"], g["coords_bohr"], strict=True)]
    xyz = tmp_path / "benzene.xyz"
    xyz.write_text(f"{len(rows)}\nbenzene\n" + "\n".join(rows) + "\n", encoding="utf-8")
    cfg = config(tmp_path, smiles=None, xyz=xyz)
    assert P.admit(cfg).elements == ("C", "H")
    atoms, options = P.start_geometry(cfg)
    assert options is None and [a[0] for a in atoms] == g["symbols"] and abs(atoms[0][1] - g["coords_bohr"][0][0] * b) < 1e-7


def test_the_optimisation_job_is_deck_v1_without_hessians(tmp_path, monkeypatch):
    cfg = config(tmp_path, threads=3, psi4_memory_gb=5)
    cfg.folder.mkdir()
    seen = {}

    def fake_run(argv, log, what):
        seen["argv"] = argv
        (cfg.folder / "result.json").write_text(json.dumps({"status": "done", "e_opt": -1.0}), encoding="utf-8")
        (cfg.folder / "geometry.json").write_text("{}", encoding="utf-8")
        return 0

    monkeypatch.setattr(P, "_run", fake_run)
    P.optimise(cfg, [["H", 0.0, 0.0, 0.0]], None)
    job = json.loads((cfg.folder / "job.json").read_text(encoding="utf-8"))
    deck = json.loads(P.RC.DECK.read_text(encoding="utf-8"))
    assert job["hessians"] is False and job["optimise"] is True and "opt_options" not in job
    assert job["deck"] == deck | {"threads": 3, "memory_gb": 5}
    assert seen["argv"] == [str(cfg.psi4_python), str(P.PSI4_WORKER), str(cfg.folder / "job.json")]


def test_a_failed_optimisation_raises_with_psi4s_error(tmp_path, monkeypatch):
    cfg = config(tmp_path)
    cfg.folder.mkdir()

    def fake_run(argv, log, what):
        (cfg.folder / "result.json").write_text(json.dumps({"status": "failed", "error": "optking did not converge"}), encoding="utf-8")
        return 1

    monkeypatch.setattr(P, "_run", fake_run)
    with pytest.raises(RuntimeError, match="optking did not converge"):
        P.optimise(cfg, [], None)


@pytest.mark.skipif(sys.platform != "win32", reason="the WSL step's command names the laptop's Windows paths")
def test_the_low_level_runs_b3lyp_alone_under_the_cap(tmp_path):
    cfg = config(tmp_path, wsl_cap_mb=8192, threads=6)
    argv = P.low_level_command(cfg)
    assert argv[:4] == ["wsl.exe", "-e", "bash", "-lc"]
    inner = argv[4]
    assert "--functionals b3lyp" in inner and f"--max-memory {8192 - P.PYSCF_HEADROOM_MB}" in inner and "wsl_capped.sh 8192 --" in inner
    assert P.wsl_path(cfg.folder) in inner and "OMP_NUM_THREADS=6" in inner


@pytest.mark.parametrize("rc, match", [(137, "WSL cap"), (143, "WSL cap"), (3, "APT failed"), (1, "analytic Hessian failed")])
def test_a_failed_low_level_raises_with_the_reason(tmp_path, monkeypatch, rc, match):
    cfg = config(tmp_path)
    cfg.folder.mkdir()
    monkeypatch.setattr(P, "low_level_command", lambda cfg: ["wsl.exe"])
    monkeypatch.setattr(P, "_run", lambda argv, log, what: rc)
    with pytest.raises(RuntimeError, match=match):
        P.low_level(cfg)


def test_an_imaginary_mode_stops_the_spectrum(tmp_path, monkeypatch):
    cfg = config(tmp_path)
    cfg.folder.mkdir()
    (cfg.folder / P.RI.LOW_HESSIAN).write_bytes(b"")
    (cfg.folder / "result.json").write_text(json.dumps({"n_imaginary_b3lyp": 1}), encoding="utf-8")
    monkeypatch.setattr(P, "low_level_command", lambda cfg: ["wsl.exe"])
    monkeypatch.setattr(P, "_run", lambda argv, log, what: 0)
    with pytest.raises(RuntimeError, match="not a minimum"):
        P.low_level(cfg)


def test_wsl_paths():
    assert P.wsl_path("C:\\Users\\x\\a b") == "/mnt/c/Users/x/a b"
    with pytest.raises(ValueError, match="not an absolute Windows drive path"):
        P.wsl_path("relative\\x")


def test_the_baseline_scales_each_region_by_pahdbs_factor():
    sticks = [dict(omega_cm=w, km_mol=1.0) for w in (800.0, 1600.0, 3000.0)]
    assert [s["omega_cm"] for s in P.scaled_baseline(sticks)] == [round(800 * 0.956, 1), round(1600 * 0.952, 1), round(3000 * 0.960, 1)]


@pytest.fixture
def benzene(tmp_path) -> Path:
    require_frozen_corpus()
    d = tmp_path / BENZENE
    shutil.copytree(PIN_CORPUS / "molecules" / BENZENE, d)
    return d


def test_the_correction_is_the_seeds_mean_and_each_seeds_range(benzene):
    dH, seeds = P.correction((PIN_MODEL, PIN_MODEL), benzene)
    assert len(seeds) == 2 and np.array_equal(dH, seeds[0]) and np.abs(dH).max() > 0
    out = P.spectra(benzene, dH, seeds)
    sticks = out["network"]["sticks"]
    assert len(sticks) == 30 and all(s["seed_range_cm"] == [s["omega_cm"]] * 2 for s in sticks)
    assert out["baseline"]["sticks"] != sticks and "baseline only" in out["baseline"]["label"]


def test_a_zero_correction_gives_the_b3lyp_spectrum(benzene):
    zero = np.zeros((36, 36))
    out = P.spectra(benzene, zero, [zero])
    masses = np.asarray(json.loads((benzene / "geometry.json").read_text(encoding="utf-8"))["masses_amu"], float)
    b3lyp = series(benzene / P.RI.LOW_HESSIAN, masses, P.cheap_apt(benzene))
    assert [{k: s[k] for k in ("omega_cm", "km_mol")} for s in out["network"]["sticks"]] == b3lyp["sticks"]


@pytest.fixture
def pin_defaults(monkeypatch):
    monkeypatch.setattr(P, "carried_models", lambda: (PIN_MODEL,))
    monkeypatch.setattr(P, "default_psi4_python", lambda: Path(sys.executable))


def test_check_only_admits_and_writes_nothing(tmp_path, pin_registry, pin_defaults, capsys):
    argv = ["--name", "benzene", "--smiles", "c1ccccc1", "--out", str(tmp_path / "out"), "--check-only"]
    assert P.main(argv) == 0
    assert "[pipeline] admitted: benzene, 12 atoms (C, H)" in capsys.readouterr().out and not (tmp_path / "out").exists()


def test_a_refusal_exits_2_with_its_reasons(tmp_path, pin_registry, pin_defaults, capsys):
    assert P.main(["--name", "x", "--smiles", "C1CCCCC1", "--out", str(tmp_path), "--check-only"]) == 2
    out = capsys.readouterr().out
    assert "REFUSED" in out and "no aromatic ring" in out


def test_the_output_folder_is_absolute(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert config(Path("rel")).out_root == (tmp_path / "rel").resolve()
