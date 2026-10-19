"""probes/dfmp2_rows.py without psi4: a stand-in psi4 returns the exact gradient of a quadratic energy, so the central rows must give its
Hessian to round-off; the conventional file's settings are taken over, the output has its format, an interrupted run resumes without
recomputing a row, the psi4 options name the fitting bases and the frozen count, and a corpus geometry of another molecule is refused."""
import json
import sys
import types
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "probes"))
R = pytest.importorskip("dfmp2_rows")

H_TRUE = np.diag(np.linspace(0.2, 0.9, 9))
H_TRUE[0, 3] = H_TRUE[3, 0] = 0.05             # one coupling, so a row is more than its diagonal
X0 = np.array([[0.0, 0.0, 0.0], [0.0, 1.43, 1.11], [0.0, -1.43, 1.11]])


class FakePsi4(types.SimpleNamespace):
    """Records options and calls; gradient('mp2') = H (x − x0) at the geometry parsed from the molecule string."""
    def __init__(self, fail_after=None):
        super().__init__(__version__="fake", options={}, calls=0, fail_after=fail_after, core=types.SimpleNamespace(clean=lambda: None))

    def set_output_file(self, *_a):
        pass

    def set_num_threads(self, *_a):
        pass

    def set_memory(self, *_a):
        pass

    def set_options(self, opts):
        self.options.update(opts)

    def geometry(self, text):
        return text

    def gradient(self, _name, molecule, dertype=None):
        if self.fail_after is not None and self.calls >= self.fail_after:
            raise RuntimeError("stand-in crash")
        self.calls += 1
        lines = [ln.split() for ln in molecule.splitlines()[1:] if len(ln.split()) == 4]
        x = np.array([[float(v) for v in ln[1:]] for ln in lines]).ravel()
        return (H_TRUE @ (x - X0.ravel())).reshape(-1, 3)


def setup(tmp_path, monkeypatch, fake):
    like = tmp_path / "conv.npz"
    np.savez(like, ks=np.array([0, 3, 8]), reps=np.array([0, 1]), step=0.005, basis="cc-pvdz", frozen=1, cart=False, coords_bohr=X0,
             row_00=np.zeros(9), row_03=np.zeros(9), row_08=np.zeros(9))
    geom = tmp_path / "geometry.json"
    geom.write_text(json.dumps({"symbols": ["o", "h", "h"], "coords_bohr": (X0 + 2.0).tolist()}), encoding="utf-8")
    monkeypatch.setitem(sys.modules, "psi4", fake)
    return like, geom, tmp_path / "df.npz"


def test_rows_recover_a_quadratic_hessian_in_the_conventional_format(tmp_path, monkeypatch):
    fake = FakePsi4()
    like, geom, out = setup(tmp_path, monkeypatch, fake)
    assert R.main(["rows", "--like", str(like), "--symbols-from", str(geom), "--out", str(out)]) == 0
    z = np.load(out)
    for k in (0, 3, 8):
        assert np.allclose(z[f"row_{k:02d}"], H_TRUE[k], atol=1e-12)
    assert str(z["basis"]) == "cc-pvdz" and int(z["frozen"]) == 1 and float(z["step"]) == 0.005 and np.allclose(z["coords_bohr"], X0)
    assert fake.options["df_basis_mp2"] == "cc-pvdz-ri" and fake.options["df_basis_scf"] == "cc-pvdz-jkfit"
    assert fake.options["num_frozen_docc"] == 1 and fake.options["puream"] is True and fake.options["mp2_type"] == "df"


def test_an_interrupted_run_resumes_without_recomputing(tmp_path, monkeypatch):
    like, geom, out = setup(tmp_path, monkeypatch, FakePsi4(fail_after=3))      # row 0 (2 gradients) done, the crash inside row 3
    with pytest.raises(RuntimeError, match="stand-in crash"):
        R.main(["rows", "--like", str(like), "--symbols-from", str(geom), "--out", str(out)])
    assert sorted(k for k in np.load(out).files if k.startswith("row_")) == ["row_00"]
    again = FakePsi4()
    monkeypatch.setitem(sys.modules, "psi4", again)
    R.main(["rows", "--like", str(like), "--symbols-from", str(geom), "--out", str(out)])
    assert again.calls == 4 and np.allclose(np.load(out)["row_08"], H_TRUE[8], atol=1e-12)


def test_another_molecule_is_refused(tmp_path, monkeypatch):
    like, geom, out = setup(tmp_path, monkeypatch, FakePsi4())
    geom.write_text(json.dumps({"symbols": ["o", "h", "h"], "coords_bohr": (X0 * 1.1).tolist()}), encoding="utf-8")
    with pytest.raises(SystemExit, match="same atom order"):
        R.main(["rows", "--like", str(like), "--symbols-from", str(geom), "--out", str(out)])


def test_a_level_out_of_range_is_refused():
    with pytest.raises(ValueError, match="out of range"):
        R.Level("cc-pvdz", -1, False)
