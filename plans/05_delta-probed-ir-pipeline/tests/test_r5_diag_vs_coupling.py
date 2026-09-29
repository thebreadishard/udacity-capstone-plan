"""R5 desk test (anchor set two, 29 Sep 2026): on a synthetic molecule the diagonal-only correction removes all of the error when K is diagonal and
none of the off-diagonal part's effect when the diagonal is zero; the shares are bounded; the CLI runs on benzene's CC Hessian when present."""
import json
import sys
from pathlib import Path

import numpy as np
import pytest

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "modules" / "05_support_predictor" / "m05"))
pytest.importorskip("torch")
import r5_diag_vs_coupling as R5  # noqa: E402

MOLS = PLAN / "modules" / "05_support_predictor" / "corpus" / "molecules"
CC = PLAN / "probes" / "results_m1" / "e8_benzene_ccpvdz" / "hessian_ccsd_t.npz"


def _mol(K):
    M = K.shape[0]
    return {"freq": np.linspace(600, 1600, M), "family": ["ring-ip"] * (M // 2) + ["other"] * (M - M // 2), "K": K}


def test_diagonal_K_is_fully_removed_and_offdiagonal_only_is_not():
    rng = np.random.default_rng(1)
    M = 6
    d = np.diag(rng.normal(size=M) * 5)
    r = R5.read_molecule(_mol(d))
    assert all(abs(x["share_removed_by_diagonal"] - 1) < 1e-9 for x in r["families"].values())
    off = rng.normal(size=(M, M))
    off = 0.5 * (off + off.T)
    np.fill_diagonal(off, 0.0)
    r2 = R5.read_molecule(_mol(off))
    assert all(abs(x["share_removed_by_diagonal"]) < 1e-9 for x in r2["families"].values())   # diag-only = zero rule when the diagonal is zero
    assert r2["offdiag_over_diag_frobenius"] == float("inf") or r2["offdiag_over_diag_frobenius"] > 1e6


HAVE_BENZENE = CC.exists() and (MOLS / "A_8448043181" / "hessian_b3lyp_analytic.npz").exists()


@pytest.mark.skipif(not HAVE_BENZENE, reason="benzene CC Hessian or analytic pair not here")
def test_cli_on_benzene(tmp_path):
    out = tmp_path / "r5"
    assert R5.main([str(MOLS), str(out), "--pair", f"A_8448043181={CC}", "--use-analytic", "--label", "test"]) == 0
    r = json.load(open(str(out) + ".json"))
    fams = r["molecules"]["A_8448043181"]["families"]
    assert "ring-ip" in fams and fams["all"]["n"] == 30
    assert all(0 <= x["rms_diag_only"] and 0 <= x["rms_zero_rule"] for x in fams.values())
    assert (out.parent / "r5.md").read_text(encoding="utf-8").startswith("# R5")
