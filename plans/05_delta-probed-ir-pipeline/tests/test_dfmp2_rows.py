"""probes/dfmp2_rows.py without psi4: a stand-in psi4 returns the exact gradient of a quadratic energy, so the central rows must give its
Hessian to round-off; the conventional file's settings are taken over, the output has its format, an interrupted run resumes without
recomputing a row, the psi4 options name the fitting bases and the frozen count, and a corpus geometry of another molecule is refused.
The geometry mode: pyridine's plan from its corpus geometry equals its 7 Oct conventional file's (the registered check), the mode runs end to
end on a symmetric water, and options that do not combine are refused."""
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


PLAN = Path(__file__).resolve().parents[1]
PYRIDINE_GEOMETRY = PLAN / "modules/05_support_predictor/corpus/molecules/A_6e858b26e5/geometry.json"
PYRIDINE_ROWS = PLAN / "probes/results_m1/composite_rows_2026-10-07/mp2_rows_pyridine_ccpvdz.npz"


@pytest.mark.skipif(not (PYRIDINE_GEOMETRY.is_file() and PYRIDINE_ROWS.is_file()), reason="needs the git-ignored corpus and the 7 Oct rows")
def test_the_geometry_mode_plans_pyridine_as_its_conventional_file():
    g = R.plan_from_geometry(str(PYRIDINE_GEOMETRY), "cc-pvdz")
    c = R.plan_from_like(str(PYRIDINE_ROWS), str(PYRIDINE_GEOMETRY))
    assert (g.ks, g.reps, g.step, g.frozen, g.cart, g.basis, g.symbols) == (c.ks, c.reps, c.step, c.frozen, c.cart, c.basis, c.symbols)
    assert np.array_equal(g.coords_bohr, c.coords_bohr)


def test_the_geometry_mode_runs_on_a_symmetric_water(tmp_path, monkeypatch):
    water = np.array([[0.0, 0.0, -0.12], [0.0, 1.43, 0.98], [0.0, -1.43, 0.98]])
    geom = tmp_path / "geometry.json"
    geom.write_text(json.dumps({"symbols": ["o", "h", "h"], "coords_bohr": water.tolist(), "masses_amu": [15.995, 1.008, 1.008]}),
                    encoding="utf-8")
    fake = FakePsi4()
    monkeypatch.setitem(sys.modules, "psi4", fake)
    monkeypatch.setattr(sys.modules[__name__], "X0", water)
    out = tmp_path / "df.npz"
    assert R.main(["rows", "--geometry", str(geom), "--basis", "cc-pvtz", "--out", str(out)]) == 0
    z = np.load(out)
    ks = [int(k) for k in z["ks"]]
    assert 0 < len(ks) < 9 and int(z["frozen"]) == 1 and float(z["step"]) == R.ANCHOR_STEP and str(z["basis"]) == "cc-pvtz"
    for k in ks:
        assert np.allclose(z[f"row_{k:02d}"], H_TRUE[k], atol=1e-12)
    assert fake.options["df_basis_mp2"] == "cc-pvtz-ri"


@pytest.mark.parametrize("args", [
    ["--like", "a.npz", "--symbols-from", "g.json", "--basis", "cc-pvtz"],     # the file names its basis
    ["--like", "a.npz"],                                                          # no symbols
    ["--geometry", "g.json"],                                                     # no basis
    ["--geometry", "g.json", "--basis", "cc-pvtz", "--symbols-from", "g.json"],   # symbols come from the geometry
    ["--like", "a.npz", "--geometry", "g.json", "--basis", "cc-pvtz"],           # one source only
    ["--geometry", "g.json", "--basis", "cc-pvtz", "--other-basis", "cc-pvqz"],  # --other-basis goes with --like
])
def test_options_that_do_not_combine_are_refused(args):
    with pytest.raises(SystemExit):
        R.main(["rows", *args, "--out", "x.npz"])


def test_other_basis_keeps_the_conventional_plan_at_another_basis(tmp_path):
    like = tmp_path / "conv.npz"
    np.savez(like, ks=np.array([1, 4]), reps=np.array([0, 1]), step=0.005, basis="cc-pvtz", frozen=1, cart=False, coords_bohr=X0)
    geometry = tmp_path / "geometry.json"
    geometry.write_text(json.dumps({"symbols": ["O", "H", "H"], "coords_bohr": X0.tolist()}), encoding="utf-8")
    own = R.plan_from_like(str(like), str(geometry))
    qz = R.plan_from_like(str(like), str(geometry), "cc-pvqz")
    assert qz.basis == "cc-pvqz" and own.basis != "cc-pvqz"
    assert (qz.ks, qz.reps, qz.step, qz.frozen, qz.cart) == (own.ks, own.reps, own.step, own.frozen, own.cart)
    assert np.array_equal(qz.coords_bohr, own.coords_bohr)


def test_a_level_out_of_range_is_refused():
    with pytest.raises(ValueError, match="out of range"):
        R.Level("cc-pvdz", -1, False)


CLOSED_SHELL_OPTIONS = {"basis": "cc-pvdz", "df_basis_scf": "cc-pvdz-jkfit", "df_basis_mp2": "cc-pvdz-ri", "scf_type": "df", "mp2_type": "df",
                        "num_frozen_docc": 1, "puream": True, "guess": "sad", "e_convergence": 1e-10, "d_convergence": 1e-10}
CLOSED_SHELL_KEYS = {"ks", "reps", "step", "basis", "frozen", "cart", "coords_bohr", "method", "row_00", "row_03", "row_08"}


def test_the_closed_shell_path_is_pinned(tmp_path, monkeypatch):
    """The neutral anchors' rows were made this way (20 Oct): every option, the '0 1' header and the file's keys stay as they were."""
    fake = FakePsi4()
    headers = []
    gradient = fake.gradient
    fake.gradient = lambda name, molecule, dertype=None: headers.append(molecule.splitlines()[0]) or gradient(name, molecule, dertype)
    like, geom, out = setup(tmp_path, monkeypatch, fake)
    assert R.main(["rows", "--like", str(like), "--symbols-from", str(geom), "--out", str(out)]) == 0
    assert fake.options == CLOSED_SHELL_OPTIONS
    assert set(headers) == {"0 1"}
    assert set(np.load(out).files) == CLOSED_SHELL_KEYS


def test_an_open_shell_runs_uhf_through_dfocc_and_says_so_in_the_file(tmp_path, monkeypatch):
    fake = FakePsi4()
    headers = []
    gradient = fake.gradient
    fake.gradient = lambda name, molecule, dertype=None: headers.append(molecule.splitlines()[0]) or gradient(name, molecule, dertype)
    like, geom, out = setup(tmp_path, monkeypatch, fake)
    argv = ["rows", "--like", str(like), "--symbols-from", str(geom), "--out", str(out), "--charge", "1", "--multiplicity", "2"]
    assert R.main(argv) == 0
    assert fake.options == {**CLOSED_SHELL_OPTIONS, "reference": "uhf", "qc_module": "occ"}
    assert set(headers) == {"1 2"}
    z = np.load(out)
    assert set(z.files) == CLOSED_SHELL_KEYS | {"charge", "multiplicity"} and (int(z["charge"]), int(z["multiplicity"])) == (1, 2)
    assert "UHF via DFOCC" in str(z["method"])


def test_a_closed_shell_cation_stays_restricted():
    fake = FakePsi4()
    R.configure(fake, R.Level("cc-pvdz", 1, False, charge=2, multiplicity=1), Path("x.log"))
    assert "reference" not in fake.options and "qc_module" not in fake.options


def test_a_multiplicity_below_one_is_refused():
    with pytest.raises(SystemExit):
        R.main(["water", "--out", "x.json", "--multiplicity", "0"])
    with pytest.raises(ValueError, match="out of range"):
        R.Level("cc-pvdz", 1, False, multiplicity=0)


def test_the_fitting_sets_can_be_named_and_the_file_says_which(tmp_path, monkeypatch):
    """An ANO basis has no JKFIT/RI set of its own name: the call names them, each alone or both."""
    fake = FakePsi4()
    like, geom, out = setup(tmp_path, monkeypatch, fake)
    argv = ["rows", "--like", str(like), "--symbols-from", str(geom), "--other-basis", "ano-pvqz", "--out", str(out)]
    assert R.main([*argv, "--df-basis-scf", "cc-pvqz-jkfit", "--df-basis-mp2", "cc-pvqz-ri"]) == 0
    assert fake.options == {**CLOSED_SHELL_OPTIONS, "basis": "ano-pvqz", "df_basis_scf": "cc-pvqz-jkfit", "df_basis_mp2": "cc-pvqz-ri"}
    z = np.load(out)
    assert str(z["basis"]) == "ano-pvqz" and "(cc-pvqz-jkfit / cc-pvqz-ri, frozen 1)" in str(z["method"])
    assert set(z.files) == CLOSED_SHELL_KEYS
    one = R.Fitting.named_after("cc-pwcvtz", scf="cc-pvtz-jkfit")
    assert (one.scf, one.mp2) == ("cc-pvtz-jkfit", "cc-pwcvtz-ri")


def test_the_frozen_count_can_be_set_to_all_electrons(tmp_path, monkeypatch):
    fake = FakePsi4()
    like, geom, out = setup(tmp_path, monkeypatch, fake)
    assert R.main(["rows", "--like", str(like), "--symbols-from", str(geom), "--out", str(out), "--frozen-core", "0"]) == 0
    z = np.load(out)
    assert fake.options["num_frozen_docc"] == 0 and int(z["frozen"]) == 0 and "frozen 0)" in str(z["method"])
    with pytest.raises(SystemExit):
        R.main(["rows", "--like", str(like), "--symbols-from", str(geom), "--out", str(tmp_path / "y.npz"), "--frozen-core", "-1"])


def test_only_the_named_rows_are_computed_and_the_rest_follow_on_a_second_call(tmp_path, monkeypatch, capsys):
    fake = FakePsi4()
    like, geom, out = setup(tmp_path, monkeypatch, fake)
    argv = ["rows", "--like", str(like), "--symbols-from", str(geom), "--out", str(out)]
    assert R.main([*argv, "--only-row", "3"]) == 0
    assert fake.calls == 2 and sorted(k for k in np.load(out).files if k.startswith("row_")) == ["row_03"]
    said = capsys.readouterr().out
    assert "DF ROWS PARTIAL" in said and "(1 of 3 rows" in said and "DF ROWS DONE" not in said
    assert R.main(argv) == 0
    assert fake.calls == 6 and "DF ROWS DONE" in capsys.readouterr().out
    with pytest.raises(SystemExit, match="not among the plan's displacements"):
        R.main([*argv, "--only-row", "5"])


@pytest.mark.parametrize("change", [
    ["--df-basis-mp2", "cc-pv5z-ri"],        # another fitting set
    ["--df-basis-scf", "cc-pv5z-jkfit"],
    ["--frozen-core", "0"],                  # another correlation space
    ["--other-basis", "cc-pvtz"],            # another orbital basis
])
def test_a_file_made_at_another_level_is_not_resumed(tmp_path, monkeypatch, change):
    fake = FakePsi4()
    like, geom, out = setup(tmp_path, monkeypatch, fake)
    argv = ["rows", "--like", str(like), "--symbols-from", str(geom), "--out", str(out)]
    assert R.main([*argv, "--only-row", "0"]) == 0
    before = out.read_bytes()
    with pytest.raises(SystemExit, match="holds rows of"):
        R.main([*argv, *change])
    assert fake.calls == 2 and out.read_bytes() == before


def test_a_file_at_another_geometry_or_step_is_not_resumed(tmp_path, monkeypatch):
    fake = FakePsi4()
    like, geom, out = setup(tmp_path, monkeypatch, fake)
    argv = ["rows", "--like", str(like), "--symbols-from", str(geom), "--out", str(out)]
    assert R.main([*argv, "--only-row", "0"]) == 0
    for moved in ({"coords_bohr": X0 + 0.01}, {"step": 0.01}):
        z = dict(np.load(like))
        np.savez(like, **{**z, **moved})
        geom.write_text(json.dumps({"symbols": ["o", "h", "h"], "coords_bohr": np.asarray(moved.get("coords_bohr", X0)).tolist()}),
                        encoding="utf-8")
        with pytest.raises(SystemExit, match="holds rows of"):
            R.main(argv)
        np.savez(like, **z)
    assert fake.calls == 2
