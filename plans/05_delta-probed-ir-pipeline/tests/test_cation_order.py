"""probes/cation_order.py (19 Oct 2026): the cation run's order, smallest basis first. The 6-31G* Cartesian table is checked against
pyscf's mol.nao for every element the cations carry (in WSL; skipped without pyscf); the order and the skip of finished molecules run
anywhere on a scratch shard."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "probes"))
import cation_order as C


@pytest.mark.parametrize("atom", ["H", "C", "N", "O", "F", "S", "Cl"])
def test_the_table_matches_pyscf(atom):
    gto = pytest.importorskip("pyscf.gto")
    spin = 1 if atom in ("H", "N", "F", "Cl") else 0
    mol = gto.M(atom=f"{atom} 0 0 0", basis="6-31g*", cart=True, spin=spin + (2 if atom in ("C", "O", "S") else 0), verbose=0)
    assert C.basis_functions([atom]) == mol.nao


def test_an_element_outside_the_table_is_refused():
    with pytest.raises(ValueError, match="Br"):
        C.basis_functions(["C", "Br"])


def test_pending_is_smallest_first_and_skips_finished_molecules(tmp_path):
    shard = tmp_path / "a"
    rows = {"P3c_big": ["C"] * 10 + ["H"] * 8, "P3c_small": ["C"] * 6 + ["H"] * 6, "P3c_done": ["C"] * 2, "P3c_half": ["C"] * 8 + ["H"] * 6}
    for mid, symbols in rows.items():
        d = shard / "molecules" / mid
        d.mkdir(parents=True)
        (d / "geometry.json").write_text(json.dumps({"symbols": symbols}), encoding="utf-8")
    for f in C.FUNCTIONALS:
        (shard / "molecules" / "P3c_done" / f"hessian_{f}_analytic.npz").write_bytes(b"")
    (shard / "molecules" / "P3c_half" / "hessian_b3lyp_analytic.npz").write_bytes(b"")
    (shard / "pool3_a.log").write_text("".join(f"[t] [a] done {m} x\n" for m in rows), encoding="utf-8")
    assert [m for _, _, m in C.pending(shard)] == ["P3c_small", "P3c_half", "P3c_big"]
    assert C.pending(shard)[0][:2] == (6 * 15 + 6 * 2, 12)
