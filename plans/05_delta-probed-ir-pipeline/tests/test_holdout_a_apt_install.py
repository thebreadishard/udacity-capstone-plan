"""probes/holdout_a_apt_install.py (1 Nov 2026, TASKS 146): the clean hold-out (a)'s refined files go into the corpus only when every
molecule passes the pipeline's own reuse check on a staged copy; without --apply nothing changes; the originals are kept, and a second
install keeps the first originals; a new Hessian far from the old one is refused. Built on the reuse tests' frozen-corpus folders."""
from __future__ import annotations

import json
import shutil
import sys

import numpy as np
import pytest

from pin_tools import PLAN, require_frozen_corpus
from test_m08_reuse import BENZENE, PHEN_CANONICAL, PHENANTHRENE, SMILES, mutate_npz, write_source

sys.path.insert(0, str(PLAN / "probes"))
import holdout_a_apt_install as I
from m08 import reuse as R
from m08.pipeline import REUSE_SETTINGS


def drop_fields(path, *names) -> None:
    with np.load(path) as z:
        kept = {k: z[k] for k in z.files if k not in names}
    np.savez(path, **kept)


@pytest.fixture
def folders(tmp_path):
    """A corpus as before the run (phenanthrene's APT route B; benzene's also, and its Hessian without charge and spin) and the run's outputs."""
    require_frozen_corpus()
    corpus, run = tmp_path / "corpus" / "molecules", tmp_path / "run"
    for mol_id in (BENZENE, PHENANTHRENE):
        write_source(run / mol_id, mol_id=mol_id, canonical=PHEN_CANONICAL if mol_id == PHENANTHRENE else SMILES)
        shutil.copytree(run / mol_id, corpus / mol_id)
        mutate_npz(corpus / mol_id / R.APT, route="cphf")
    drop_fields(corpus / BENZENE / R.HESSIAN, "charge", "spin")
    for mol_id in (BENZENE, PHENANTHRENE):
        for f in R.SOURCE_FILES:
            if f not in I.NEW_FILES["hessian" if mol_id == BENZENE else "apt"]:
                (run / mol_id / f).unlink()
    (run / "ids.tsv").write_text(f"# test\n{PHENANTHRENE}\tapt\t24\n{BENZENE}\thessian\t12\n", encoding="utf-8")
    return run, corpus


def run_main(monkeypatch, *argv) -> None:
    monkeypatch.setattr(sys, "argv", ["holdout_a_apt_install.py", *map(str, argv)])
    I.main()


def test_the_corpus_folders_are_refused_before_and_pass_after_the_install(folders, monkeypatch):
    run, corpus = folders
    assert R.settings_refusals(corpus / BENZENE, REUSE_SETTINGS) and R.settings_refusals(corpus / PHENANTHRENE, REUSE_SETTINGS)
    run_main(monkeypatch, run, corpus, "--apply")
    assert not R.settings_refusals(corpus / BENZENE, REUSE_SETTINGS) and not R.settings_refusals(corpus / PHENANTHRENE, REUSE_SETTINGS)
    assert [r["id"] for r in json.loads((run / "install.json").read_text(encoding="utf-8"))] == [PHENANTHRENE, BENZENE]


def test_without_apply_nothing_changes(folders, monkeypatch, capsys):
    run, corpus = folders
    before = {p: p.read_bytes() for p in corpus.rglob("*") if p.is_file()}
    run_main(monkeypatch, run, corpus)
    assert {p: p.read_bytes() for p in corpus.rglob("*") if p.is_file()} == before and "dry: not installed" in capsys.readouterr().out
    assert not (run / "install.json").exists() and not (corpus.parent / I.SUPERSEDED).exists()


def test_one_failing_molecule_stops_every_install(folders, monkeypatch):
    run, corpus = folders
    mutate_npz(run / BENZENE / R.APT, passed=False)
    before = (corpus / PHENANTHRENE / R.APT).read_bytes()
    with pytest.raises(SystemExit, match="the APT failed its checks"):
        run_main(monkeypatch, run, corpus, "--apply")
    assert (corpus / PHENANTHRENE / R.APT).read_bytes() == before


def test_a_new_hessian_far_from_the_old_one_is_refused(folders):
    run, corpus = folders
    with np.load(run / BENZENE / R.HESSIAN) as z:
        moved = z["H_projected"] + 10 * I.HESSIAN_TOL
    mutate_npz(run / BENZENE / R.HESSIAN, H_projected=moved)
    assert any("new Hessian differs" in r for r in I.refusals(run, corpus, BENZENE, "hessian"))


def test_the_originals_are_kept_and_a_second_install_keeps_them(folders, monkeypatch):
    run, corpus = folders
    original = (corpus / PHENANTHRENE / R.APT).read_bytes()
    run_main(monkeypatch, run, corpus, "--apply")
    run_main(monkeypatch, run, corpus, "--apply")
    assert (corpus.parent / I.SUPERSEDED / PHENANTHRENE / R.APT).read_bytes() == original


def test_an_unknown_step_is_refused(tmp_path):
    (tmp_path / "ids.tsv").write_text("A_1\tfield\t3\n", encoding="utf-8")
    with pytest.raises(ValueError, match="neither apt nor hessian"):
        I.rows(tmp_path)
