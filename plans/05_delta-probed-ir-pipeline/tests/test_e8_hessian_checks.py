"""The split Hessian self-check (probes/e8_hessian_checks.py, 30 Sep 2026): INVALID (the computation is wrong) versus IMAGINARY (computed
correctly, not a minimum) versus VALID. Synthetic Hessians with known frequencies, each failure mode on its own and combined, invariances,
and the three real CC Hessians that motivated it (probes/results_m1/e8_selfcheck_cases/)."""
import sys
from pathlib import Path

import numpy as np
import pytest

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "probes"))
import e8_hessian_checks as HC  # noqa: E402

CASES = PLAN / "probes" / "results_m1" / "e8_selfcheck_cases"
X5 = np.array([[0.0, 0.0, 0.0], [2.1, 0.3, -0.2], [-0.4, 1.9, 0.5], [0.6, -0.7, 2.2], [-1.8, -0.9, -0.6]])   # bohr, non-planar
M5 = np.array([12.0, 1.00782503, 14.00307401, 15.99491462, 1.00782503])


def synthetic(x, m, freqs_cm, seed=0):
    """A Cartesian Hessian with exactly these 3N−6 vibrational frequencies and exact translational/rotational invariance."""
    q = HC.tr_basis(x, m)
    n3 = 3 * len(m)
    u, _, _ = np.linalg.svd(np.eye(n3) - q @ q.T)
    qv = u[:, : n3 - 6]                                             # orthonormal basis of the vibrational space
    rot = np.linalg.qr(np.random.default_rng(seed).standard_normal((n3 - 6, n3 - 6)))[0]
    qv = qv @ rot
    lam = np.sign(freqs_cm) * (np.asarray(freqs_cm) / HC.HARTREE2CM) ** 2
    Hmw = qv @ np.diag(lam) @ qv.T
    sm = np.sqrt(np.repeat(m * HC.AMU2AU, 3))
    return Hmw * np.outer(sm, sm)


FREQS = np.array([410.0, 690.0, 880.0, 1020.0, 1150.0, 1300.0, 1480.0, 3050.0, 3120.0])   # 3N − 6 = 9 for five atoms


def test_valid_synthetic_recovers_the_frequencies():
    r = HC.classify_hessian(synthetic(X5, M5, FREQS), X5, M5)
    assert r["status"] == "VALID" and r["reasons"] == []
    np.testing.assert_allclose(r["vib_cm"], np.sort(FREQS), rtol=1e-9)
    assert r["tr_max_cm"] < 1e-3 and r["trans_sum_rule"] < 1e-12
    assert len(r["freq_cm"]) == 15


def test_one_imaginary_mode_is_imaginary_not_invalid():
    f = FREQS.copy()
    f[0] = -50.0
    r = HC.classify_hessian(synthetic(X5, M5, f), X5, M5)
    assert r["status"] == "IMAGINARY"
    np.testing.assert_allclose(r["imaginary_cm"], [-50.0], rtol=1e-9)
    assert "not a minimum" in r["reasons"][0]


def test_two_imaginary_modes_among_small_frequencies_do_not_look_like_translations():
    """The benzonitrile pattern: imaginary vibrations that the old 'six lowest |ω|' rule mistook for a broken null space."""
    f = FREQS.copy()
    f[0], f[1] = -87.0, -81.9
    r = HC.classify_hessian(synthetic(X5, M5, f), X5, M5)
    assert r["status"] == "IMAGINARY" and len(r["imaginary_cm"]) == 2
    assert r["tr_max_cm"] < 1e-3
    old_rule = np.abs(np.sort(r["freq_cm"])[:6]).max()
    assert old_rule > HC.NULL_SPACE_LIMIT_CM          # the old rule would have called this a computational failure


@pytest.mark.parametrize("f0, status", [(-5.0, "VALID"), (-9.9, "VALID"), (-10.5, "IMAGINARY"), (5.0, "VALID")])
def test_imaginary_limit_boundary(f0, status):
    f = FREQS.copy()
    f[0] = f0
    assert HC.classify_hessian(synthetic(X5, M5, f), X5, M5)["status"] == status


def test_translational_sum_rule_violation_is_invalid():
    H = synthetic(X5, M5, FREQS)
    H[0, 0] += 1e-2                                                  # one atom's force no longer cancels on a rigid shift
    r = HC.classify_hessian(H, X5, M5)
    assert r["status"] == "INVALID" and any("translational sum rule" in s for s in r["reasons"])
    assert r["trans_sum_rule"] == pytest.approx(1e-2, rel=1e-6)


@pytest.mark.parametrize("asym", [3e-3, float("nan")])
def test_asymmetry_above_limit_or_nan_is_invalid(asym):
    r = HC.classify_hessian(synthetic(X5, M5, FREQS), X5, M5, asym=asym)
    assert r["status"] == "INVALID" and any("asymmetry" in s for s in r["reasons"])


def test_asymmetry_below_limit_is_fine():
    assert HC.classify_hessian(synthetic(X5, M5, FREQS), X5, M5, asym=1.9e-3)["status"] == "VALID"


def test_non_finite_element_is_invalid():
    H = synthetic(X5, M5, FREQS)
    H[3, 7] = np.inf
    r = HC.classify_hessian(H, X5, M5)
    assert r["status"] == "INVALID" and "non-finite" in r["reasons"][0]


def test_invalid_takes_precedence_over_imaginary():
    f = FREQS.copy()
    f[0] = -300.0
    H = synthetic(X5, M5, f)
    H[0, 0] += 1e-2
    r = HC.classify_hessian(H, X5, M5)
    assert r["status"] == "INVALID"


def test_linear_molecule_is_refused():
    x = np.array([[0.0, 0.0, -2.2], [0.0, 0.0, 0.0], [0.0, 0.0, 2.2]])
    with pytest.raises(ValueError, match="linear"):
        HC.tr_basis(x, np.array([16.0, 12.0, 16.0]))


def test_rigid_rotation_and_translation_leave_the_result_unchanged():
    R = np.linalg.qr(np.random.default_rng(3).standard_normal((3, 3)))[0]
    f = FREQS.copy()
    f[2] = -120.0
    H = synthetic(X5, M5, f)
    x2 = X5 @ R.T + np.array([1.5, -2.0, 0.7])
    big = np.kron(np.eye(len(M5)), R)                                # rotates every atom's Cartesian block
    H2 = big @ H @ big.T
    a, b = HC.classify_hessian(H, X5, M5), HC.classify_hessian(H2, x2, M5)
    assert a["status"] == b["status"] == "IMAGINARY"
    np.testing.assert_allclose(a["vib_cm"], b["vib_cm"], rtol=1e-9, atol=1e-6)


def test_atom_permutation_leaves_the_result_unchanged():
    perm = np.array([3, 0, 4, 1, 2])
    H = synthetic(X5, M5, FREQS)
    idx = np.concatenate([np.arange(3 * p, 3 * p + 3) for p in perm])
    r1 = HC.classify_hessian(H, X5, M5)
    r2 = HC.classify_hessian(H[np.ix_(idx, idx)], X5[perm], M5[perm])
    np.testing.assert_allclose(r1["vib_cm"], r2["vib_cm"], rtol=1e-9)


def test_energy_route_consistent_passes_and_is_reported():
    H = synthetic(X5, M5, FREQS)
    r = HC.classify_hessian(H, X5, M5, energy_diag={k: H[k, k] + 5e-5 for k in range(0, 15, 2)})
    assert r["status"] == "VALID" and r["energy_diag_n"] == 8 and r["energy_diag_max"] == pytest.approx(5e-5, rel=1e-6)


def test_energy_route_mismatch_is_invalid_even_when_row_sums_hold():
    """The lambda-incident class: gradients translation-invariant (sum rule fine) but not dE/dx — only the energy route sees it."""
    H = synthetic(X5, M5, FREQS)
    r = HC.classify_hessian(H, X5, M5, energy_diag={0: H[0, 0] + 2.5e-3, 4: H[4, 4]})
    assert r["trans_sum_rule"] < 1e-12
    assert r["status"] == "INVALID" and any("not dE/dx" in s for s in r["reasons"])


def test_energy_route_nan_is_invalid_and_absent_is_neutral():
    H = synthetic(X5, M5, FREQS)
    assert HC.classify_hessian(H, X5, M5, energy_diag={2: float("nan")})["status"] == "INVALID"
    r = HC.classify_hessian(H, X5, M5)
    assert r["status"] == "VALID" and r["energy_diag_n"] == 0 and np.isnan(r["energy_diag_max"])


def _finish_bash(tmp_path, rc, files):
    """Run the chain script's finish() with a fake say and the given result files present; returns (exit status, logged line)."""
    import re
    import shutil
    import subprocess
    bash = shutil.which("bash")
    if bash is None:
        pytest.skip("bash not available")
    src = (PLAN / "probes" / "run_anchors_hel23_parallel.sh").read_text(encoding="utf-8")
    fn = re.search(r"^finish\(\) \{.*?^\}", src, re.S | re.M).group(0)
    for f in files:
        (tmp_path / f).write_bytes(b"")
    (tmp_path / "e8_fd.log").write_text("symmetry: test\nFD asymmetry max 1e-5 a.u.;\n")
    script = f"say() {{ echo \"$*\"; }}\n{fn}\nfinish mol '{tmp_path.as_posix()}' {rc}\n"
    p = subprocess.run([bash, "-c", script], capture_output=True, text=True, check=False)
    return p.returncode, p.stdout.strip()


@pytest.mark.parametrize("rc, files, status, word", [
    (0, ["hessian_ccsd_t.npz"], 0, "DONE"),
    (4, ["hessian_ccsd_t_IMAGINARY.npz"], 0, "IMAGINARY"),
    (2, ["hessian_ccsd_t_INVALID.npz"], 1, "FAILED"),
    (2, ["hessian_ccsd_t.npz"], 1, "FAILED"),              # a stale VALID file must not turn a failed run into DONE
    (2, ["hessian_ccsd_t_IMAGINARY.npz"], 1, "FAILED"),    # nor into IMAGINARY
    (0, [], 1, "FAILED"),                                  # exit 0 without a file is not success
])
def test_chain_finish_goes_by_exit_code(tmp_path, rc, files, status, word):
    code, line = _finish_bash(tmp_path, rc, files)
    assert code == status and word in line, (code, line)


def _case(name):
    z = np.load(CASES / f"{name}.npz")
    return HC.classify_hessian(z["H"], z["coords_bohr"], z["masses_amu"], float(z["asym"]))


@pytest.mark.data
def test_real_benzene_corrected_route_is_valid():
    r = _case("benzene_valid")
    assert r["status"] == "VALID", r["reasons"]
    assert r["vib_cm"][0] == pytest.approx(361.9, abs=0.1) and r["vib_cm"][1] == pytest.approx(361.9, abs=0.1)
    assert r["trans_sum_rule"] < 1e-4


@pytest.mark.data
def test_real_naphthalene_frozen_core_incident_is_invalid_for_both_reasons():
    r = _case("naphthalene_frozen6_invalid")
    assert r["status"] == "INVALID"
    assert any("asymmetry" in s for s in r["reasons"]) and any("translational sum rule" in s for s in r["reasons"])
    assert r["trans_sum_rule"] == pytest.approx(6.8e-2, rel=0.05)


@pytest.mark.data
def test_real_benzonitrile_is_imaginary_with_the_two_bends():
    r = _case("benzonitrile_imaginary")
    assert r["status"] == "IMAGINARY", r["reasons"]
    np.testing.assert_allclose(r["imaginary_cm"], [-87.0, -81.9], atol=0.1)
    assert r["trans_sum_rule"] < 1e-4 and r["tr_max_cm"] < 1e-2


def test_probe_and_chain_are_wired_to_the_split_check():
    probe = (PLAN / "probes" / "e8_cc_hessian_fd.py").read_text(encoding="utf-8")
    assert "chk = HC.classify_hessian(H, x0, masses, asym, ediag)" in probe
    assert 'np.save(os.path.join(a.out, f"ener_{k:02d}_{sign}.npy"), np.array(e))' in probe         # energies stored for the energy route
    assert '"IMAGINARY": "hessian_ccsd_t_IMAGINARY.npz"' in probe and "raise SystemExit(4)" in probe
    assert "SELF-CHECK FAILED" in probe and "raise SystemExit(2)" in probe
    assert 'os.path.join(_HERE, "e8_hessian_checks.py")' in probe                       # in the gate-1 fingerprint
    assert "NULL_SPACE_LIMIT_CM = " not in probe and "ASYM_LIMIT = " not in probe          # the limits live in one place
    chain = (PLAN / "probes" / "run_anchors_hel23_parallel.sh").read_text(encoding="utf-8")
    assert 'finish "$name" "$out" "$rc"' in chain and '|| rc=$?' in chain                              # the verdict comes from the exit code
    assert 'rm -f "$out/hessian_ccsd_t.npz" "$out/hessian_ccsd_t_INVALID.npz" "$out/hessian_ccsd_t_IMAGINARY.npz"' in chain   # no stale file
