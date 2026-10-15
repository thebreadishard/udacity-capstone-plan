"""probes/hybrid_form_floor.py (TASKS 65, 15 Oct 2026), tested before its read: the molecule is loaded as the trainer holds an analytic one; the
best fit on the pattern is exact when the truth lies in the form and never worse than the trained target; the pattern is the carried recipe's;
the read's verdict follows the registered order (form, then target, then data)."""
import json
import sys
from pathlib import Path

import numpy as np
import pytest

PLAN = Path(__file__).resolve().parents[1]
pytest.importorskip("torch")                                              # module 05's loaders import torch
sys.path.insert(0, str(PLAN / "probes"))
import hybrid_form_floor as HF  # noqa: E402

MOLECULES = PLAN / "modules" / "05_support_predictor" / "corpus" / "molecules"
REAL = MOLECULES / "A_014f8519af"                                          # has the FD pair and the analytic pair
needs_real = pytest.mark.skipif(not (REAL / "hessian_wb97x_analytic.npz").exists(), reason="the analytic corpus folder is not present")


def test_the_pattern_is_the_carried_recipe_s():
    import chain_runner
    recipe = chain_runner.RECIPE_V11
    assert recipe[recipe.index("--pattern") + 1] == HF.PATTERN and "hybrid" == recipe[recipe.index("--head") + 1]


@pytest.mark.data
@needs_real
def test_the_loader_matches_the_trainer_s_analytic_path(tmp_path):
    """T2.load reads a whole folder of molecules, so the one molecule is copied into a folder of its own first."""
    import shutil

    import e7_rungB_reread_analytic as RR
    import e7_t2_sqm as T2
    shutil.copytree(REAL, tmp_path / REAL.name)
    ref = RR.substitute(T2.load(tmp_path)[REAL.name], REAL)
    m = HF.analytic_molecule(REAL)
    assert np.allclose(m["B"], ref["B"]) and np.allclose(m["F_low"], ref["F_low"]) and np.allclose(m["dH_true"], ref["dH_true"])
    assert np.allclose(m["K"], ref["K"], atol=1e-3)                        # the trainer stores K as float32
    assert m["family"] == list(ref["family"])


@pytest.mark.data
@needs_real
def test_the_best_fit_is_exact_inside_the_form_and_never_worse_than_the_target():
    m = HF.analytic_molecule(REAL)
    pairs = HF.pattern_pairs(m)
    import e7_t2_posthoc as PH
    rng = np.random.default_rng(0)
    inside = dict(m, K=PH.k_of(m, HF.on_pattern(rng.normal(size=len(pairs)) * 1e-3, pairs, m["B"].shape[0])))
    assert np.allclose(PH.k_of(inside, HF.best_form_fit(inside, pairs)), inside["K"], atol=1e-6 * np.abs(inside["K"]).max())
    iu = np.triu_indices(m["K"].shape[0])
    form = PH.k_of(m, HF.best_form_fit(m, pairs))[iu] - m["K"][iu]
    target = PH.k_of(m, HF.target_on_pattern(m, pairs))[iu] - m["K"][iu]
    assert np.sum(form ** 2) <= np.sum(target ** 2) * (1 + 1e-9)


@pytest.mark.data
@needs_real
def test_a_record_carries_both_quantities():
    rec = HF.molecule_record(REAL)
    assert set(HF.QUANTITIES) <= set(rec) and rec["n_pattern_pairs"] > 0
    assert sum(rec["form"][F][1] for F in HF.FL.FAMILIES) == rec["n_modes"]
    json.dumps(rec)


def synthetic(form_scale: float, target_scale: float) -> list[dict]:
    """Records whose ring-ip floor grows as scale × n/20, every other read-out zero."""
    recs = []
    for n in [12, 16, 20, 24, 26, 28] * 6:
        def block(scale, n=n):
            return {F: ([(scale * n / 20) ** 2 * 10, 10] if F == "ring-ip" else [0.0, 5]) for F in HF.FL.FAMILIES} | {"ring_coupling": [0.0, 4.0]}
        recs.append({"id": f"m{len(recs)}", "n_atoms": n, "form": block(form_scale), "target": block(target_scale)})
    return recs


def test_the_verdict_follows_the_registered_order():
    assert HF.read(synthetic(1.0, 1.0))["verdict"].startswith("the form costs (ring-ip")
    assert HF.read(synthetic(0.1, 1.0))["verdict"].startswith("the form holds it but the trained target does not (ring-ip")
    res = HF.read(synthetic(0.1, 0.2))
    assert res["verdict"].startswith("neither line met") and res["quantities"]["form"]["ring-ip"]["line_2"] == pytest.approx(0.3)
    assert "no fit" in "\n".join(HF.report(res))                          # a read-out with no non-zero point is reported, not fitted
    json.dumps(res)


def two_regimes() -> list[dict]:
    """Below 15 atoms the form fits exactly (floors of 1e-10, the exact-fit regime); from 15 atoms on the ring-ip floor grows as 0.1·(n/20)."""
    recs = []
    for n in [8, 10, 12, 14] * 5 + [16, 20, 24, 28, 32] * 5:
        value = 1e-10 if n < 15 else 0.1 * n / 20
        block = {F: ([value ** 2 * 10, 10] if F == "ring-ip" else [0.0, 5]) for F in HF.FL.FAMILIES} | {"ring_coupling": [0.0, 4.0]}
        recs.append({"id": f"m{len(recs)}", "n_atoms": n, "form": block, "target": block})
    return recs


def test_the_amended_rule_reads_through_an_exact_fit_regime_and_the_original_does_not():
    """TASKS 69 (amendment of 15 Oct 21:2x): the first read forecast 10^10 cm^-1 because numerically-zero floors entered the fit."""
    amended = HF.read(two_regimes(), HF.FL.AMENDED)["quantities"]["form"]["ring-ip"]
    original = HF.read(two_regimes(), HF.FL.ORIGINAL)["quantities"]["form"]["ring-ip"]
    assert amended["forecast_at_60"] == pytest.approx(0.3, rel=1e-6) and amended["n_fit"] == 25
    assert original["forecast_at_60"] > 1e3                                  # the failure the amendment removes
    assert HF.read(two_regimes())["line_2_rule"]["name"] == "amended"      # the default for every read from now on


def test_a_stored_record_re_reads_without_recomputing(tmp_path):
    stored = tmp_path / "floor.json"
    stored.write_text(json.dumps({"records": two_regimes()}), encoding="utf-8")
    assert HF.main(["--from-record", str(stored), "--out", str(tmp_path / "again"), "--line-2-rule", "amended"]) == 0
    again = json.loads((tmp_path / "again.json").read_text(encoding="utf-8"))
    assert again["quantities"]["form"]["ring-ip"]["forecast_at_60"] == pytest.approx(0.3, rel=1e-6)



def test_amendment_2_reads_line_2_directly_on_the_large_molecules():
    """Lever 5's re-read: line 2 is the pooled value over the molecules of >= 34 atoms; with fewer than five such molecules there is no read."""
    recs = two_regimes()
    for n in (36, 40, 44, 50, 58):
        block = {F: ([0.5 ** 2 * 10, 10] if F == "ring-ip" else [0.0, 5]) for F in HF.FL.FAMILIES} | {"ring_coupling": [0.0, 4.0]}
        recs.append({"id": f"big{n}", "n_atoms": n, "form": block, "target": block})
    x = HF.read(recs, HF.FL.AMENDED, direct_min_atoms=34)["quantities"]["form"]["ring-ip"]
    assert x["line_2"] == pytest.approx(0.5) and not x["line_2_met"] and x["line_2_kind"].startswith("direct on 5 molecules")
    few = HF.read(recs[:-1], HF.FL.AMENDED, direct_min_atoms=34)["quantities"]["form"]["ring-ip"]
    assert np.isnan(few["line_2"]) and not few["line_2_met"]
