"""E8 probe, 2 Oct 2026: the two-route checks of the (T) kernels can run beside the production lanes instead of before them, without being skipped.
Driven through the probe's main with a fake gradient (no quantum chemistry; the probe imports pyscf, so this runs where pyscf is installed — WSL,
like test_acceptance_water.py — and is skipped elsewhere)."""
import json
import os
import sys
from pathlib import Path

import numpy as np
import pytest

pytest.importorskip("pyscf")
PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "probes"))
import e8_cc_hessian_fd as E  # noqa: E402

WATER = {"symbols": ["O", "H", "H"], "coords_bohr": [[0.0, 0.0, 0.2217], [0.0, 1.4309, -0.8867], [0.0, -1.4309, -0.8867]],
         "masses_amu": [15.995, 1.008, 1.008]}


def _fake_gradient(record):
    def gradient(symbols, coords_bohr, basis, frozen, log, charge=0, spin=0, max_memory=26000, fast=None, check_fast=False):
        record.append(check_fast)
        return -76.0, np.zeros((len(symbols), 3)), np.array([0.0, 0.0, -0.76])   # energy, gradient, relaxed dipole (3 Oct 2026)
    return gradient


def _run(tmp_path, monkeypatch, record, *args):
    geom = tmp_path / "geometry.json"
    geom.write_text(json.dumps(WATER))
    monkeypatch.setattr(E, "gradient", _fake_gradient(record))
    monkeypatch.setattr(E, "gate1_problem", lambda *a, **k: None)
    monkeypatch.setattr(sys, "argv", ["e8", str(geom), str(tmp_path / "out"), "--threads", "1", *args])
    return E.main()


def test_separate_marks_the_reference_unchecked_and_skips_the_slow_route(tmp_path, monkeypatch):
    rec = []
    _run(tmp_path, monkeypatch, rec, "--only-reference", "--two-route-check", "separate")
    assert rec == [False]                                                   # no slow-route comparison in the reference
    ref = np.load(tmp_path / "out" / "reference.npz")
    assert bool(ref["two_route_checked"]) is False
    assert "dipole" in ref.files and ref["dipole"].shape == (3,)                 # the reference carries the relaxed dipole


def test_inline_is_the_registered_default(tmp_path, monkeypatch):
    rec = []
    _run(tmp_path, monkeypatch, rec, "--only-reference")
    assert rec == [True]
    assert bool(np.load(tmp_path / "out" / "reference.npz")["two_route_checked"]) is True


def test_assembly_refuses_an_unchecked_reference_until_the_check_passes(tmp_path, monkeypatch):
    rec = []
    _run(tmp_path, monkeypatch, rec, "--only-reference", "--two-route-check", "separate")
    with pytest.raises(SystemExit) as e:
        _run(tmp_path, monkeypatch, rec, "--symmetry")                      # assembling run: no --ks, reference unchecked, no file
    assert "unchecked" in str(e.value)
    assert _run(tmp_path, monkeypatch, rec, "--two-route-check", "only") is None   # the check lane: recompute with the checks, compare, write the file
    chk = json.load(open(tmp_path / "out" / "two_route_check.json"))
    assert chk["passed"] is True and chk["max_grad_diff"] == 0.0 and rec[-1] is True
    with pytest.raises(SystemExit) as e2:                                   # now the assembly passes the gate and runs into the fake gradient's zero
        _run(tmp_path, monkeypatch, rec, "--symmetry")                      # Hessian downstream (not a two-route refusal)
    assert "unchecked" not in str(e2.value)
    apt = np.load(tmp_path / "out" / "apt_ccsd_t.npz")                      # 3 Oct 2026: the APT is assembled from the stored dipoles before the verdict
    assert apt["apt"].shape == (3, 9) and float(apt["sum_rule_max"]) == 0.0  # a constant fake dipole → zero APT, sum rule exact


def test_only_without_a_reference_refuses(tmp_path, monkeypatch):
    with pytest.raises(SystemExit) as e:
        _run(tmp_path, monkeypatch, [], "--two-route-check", "only")
    assert "needs an existing reference" in str(e.value)
    assert not os.path.exists(tmp_path / "out" / "two_route_check.json")
