"""probes/architecture_floor.py (TASKS 65, 15 Oct 2026), tested before its read: the oracle of the head's form keeps exactly what the head can
write (pairs within the cutoff, symmetric blocks, diagonal by the sum rule) and returns the correction untouched when nothing is restricted; its
mode basis is coupling_matrix's; the read pools exactly, lowers line 1's bound as registered and fits the power law; a changed input file
stops the read."""
import json
import sys
from pathlib import Path

import numpy as np
import pytest

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "probes"))
pytest.importorskip("torch")                       # learning_curve_layerA, which the probe reuses for modes and families, imports torch
import architecture_floor as AF  # noqa: E402

NOTHING = AF.Variant("nothing", cut=False, symmetric=False)
REAL = PLAN / "modules" / "05_support_predictor" / "corpus" / "molecules" / "A_014f8519af"   # a local folder with the analytic pair


def sum_rule_correction(n: int, seed: int = 0) -> tuple[np.ndarray, np.ndarray]:
    """A random symmetric Cartesian correction obeying the translational sum rule, on random coordinates (bohr) spread over ≈ 25 bohr."""
    rng = np.random.default_rng(seed)
    coords = rng.uniform(0, 25, size=(n, 3))
    A = rng.normal(size=(3 * n, 3 * n))
    H = A + A.T
    B = AF.to_blocks(H)
    idx = np.arange(n)
    B[idx, idx] = 0.0
    B[idx, idx] = -B.sum(axis=1)                      # ΔH_ii = −Σ_{j≠i} ΔH_ij
    H = AF.from_blocks(B)
    return 0.5 * (H + H.T), coords


def test_blocks_round_trip():
    H, _ = sum_rule_correction(4)
    assert np.array_equal(AF.from_blocks(AF.to_blocks(H)), H)


def test_an_oracle_that_restricts_nothing_returns_the_correction():
    H, coords = sum_rule_correction(7)
    assert np.allclose(AF.form_oracle(H, coords, 5.0, NOTHING), H, atol=1e-12)
    assert np.allclose(AF.form_oracle(H, coords, 1e6, AF.Variant("cut far", cut=True, symmetric=False)), H, atol=1e-12)


def test_the_form_keeps_near_symmetric_blocks_and_the_sum_rule():
    H, coords = sum_rule_correction(9, seed=1)
    F = AF.to_blocks(AF.form_oracle(H, coords, 5.0, AF.FORM))
    B = AF.to_blocks(H)
    dist = np.linalg.norm(coords[:, None] - coords[None], axis=-1) / AF.BOHR_PER_ANGSTROM
    off = ~np.eye(len(coords), dtype=bool)
    far, near = (dist > 5.0) & off, (dist <= 5.0) & off
    assert far.any() and near.any()                                       # the fixture exercises both
    assert np.all(F[far] == 0.0)
    assert np.allclose(F[near], 0.5 * (B[near] + B[near].transpose(0, 2, 1)))
    assert np.allclose(F[off], F[off].transpose(0, 2, 1))                 # every written block symmetric
    assert np.allclose(F.sum(axis=1), 0.0, atol=1e-10)                    # translational sum rule kept
    full = AF.from_blocks(F)
    assert np.allclose(full, full.T)


def test_records_pool_through_the_shared_lines():
    s = {"ring-ip": [5.0, 2], "CH-oop": [0.0, 0], "ring_coupling": [1.0, 4.0]}
    rec = {"n_atoms": 24, "variants": {"form": s}}
    assert AF.pooled_rms([rec, rec], "form", "ring-ip") == pytest.approx(np.sqrt(10 / 4))
    assert np.isnan(AF.pooled_rms([rec], "form", "CH-oop"))
    assert AF.pooled_rms([rec], "form", "ring_coupling") == pytest.approx(0.5)
    assert AF.line_1_bound([rec] * 30) == 24


def synthetic_records(scale: float) -> list[dict]:
    """Molecules whose ring-ip form floor is scale × (n/20); the other families' floor is zero (not fitted)."""
    recs = []
    for n in [12, 16, 20, 24, 26, 28] * 6:
        ring = [(scale * n / 20) ** 2 * 10, 10]
        var = {F: ([0.0, 5] if F != "ring-ip" else ring) for F in AF.FAMILIES} | {"ring_coupling": [1.0, 4.0]}
        recs.append({"id": f"m{len(recs)}", "n_atoms": n, "raw_vs_projected_max_cm": 0.0,
                     "variants": {v.name: var for v in AF.VARIANTS}, "sweep": {str(c): var for c in AF.SWEEP_ANGSTROM}})
    return recs


def test_the_read_applies_both_lines_and_reports_a_family_without_a_fit():
    big, small = AF.read(synthetic_records(1.0)), AF.read(synthetic_records(0.2))
    assert big["families"]["ring-ip"]["line_1_met"] and big["families"]["ring-ip"]["line_2_met"]
    assert big["families"]["ring-ip"]["line_2_floor_at_60_cm"] == pytest.approx(3.0, rel=1e-6)
    assert big["verdict"].startswith("the form costs in ring-ip")
    assert not small["families"]["ring-ip"]["line_1_met"] and small["verdict"].startswith("neither line met")
    assert big["families"]["CH-oop"]["line_2_interval_cm"] is None
    text = "\n".join(AF.report(big))
    assert "no fit (fewer than 3 molecules)" in text and "| ring-ip | 1." in text
    json.dumps(big)                                                       # the result is written as JSON


def test_a_changed_input_stops_the_read(tmp_path, monkeypatch):
    monkeypatch.setattr(AF, "PLAN", tmp_path)
    d = tmp_path / "root" / "X_1"
    d.mkdir(parents=True)
    for f in AF.LABEL_FILES:
        (d / f).write_bytes(f.encode())
    inputs = tmp_path / "inputs.tsv"
    assert AF.freeze([tmp_path / "root"], inputs) == 1
    assert AF.frozen_folders(inputs) == [d]
    (d / AF.LABEL_FILES[1]).write_bytes(b"changed")
    with pytest.raises(SystemExit, match="differs from the frozen sha256"):
        AF.frozen_folders(inputs)


def test_the_cutoff_is_the_model_s():
    import rungC_equivariant as RE
    assert AF.MODEL_CUTOFF_ANGSTROM * AF.BOHR_PER_ANGSTROM == pytest.approx(RE.CUTOFF_BOHR, rel=1e-6)


@pytest.mark.data
@pytest.mark.skipif(not (REAL / "hessian_wb97x_analytic.npz").exists(), reason="the analytic corpus folder is not present")
def test_on_a_real_molecule_the_mode_basis_is_coupling_matrix_s_and_raw_equals_projected():
    import embedding_skipgram_E5 as E5
    lo, hi = (np.load(REAL / f"hessian_{lvl}_analytic.npz") for lvl in ("b3lyp", "wb97x"))
    masses = np.asarray(json.loads((REAL / "geometry.json").read_text(encoding="utf-8"))["masses_amu"])
    w, _, V, _ = AF.LA.normal_modes(lo["H_projected"], masses)
    K_ref = E5.coupling_matrix(REAL, lo["H_projected"], hi["H_projected"])
    K_projected = AF.mode_correction(hi["H_projected"] - lo["H_projected"], masses, w, V)
    assert np.max(np.abs(K_projected - K_ref)) < 1e-3                     # K_ref is float32 (cm⁻¹ values up to ~10²)
    rec = AF.molecule_floor(REAL)
    assert rec["raw_vs_projected_max_cm"] < 1e-6
    form = rec["variants"]["form"]
    assert all(form[F][1] >= 0 for F in AF.FAMILIES) and sum(form[F][1] for F in AF.FAMILIES) == len(w)
