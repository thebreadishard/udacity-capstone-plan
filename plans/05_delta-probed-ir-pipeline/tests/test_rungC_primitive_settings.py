"""v1.5's primitive settings through the trainer (TASKS 149): the config and its refusal, the saved record and its reading (records before
the switches are the carried construction), the target cache's folder, the hybrid head's parities in the canonical row order, the loader
and pair-builder guard, and the inference loader. The features themselves: `test_internal_coords.py`."""
from __future__ import annotations

import json
import sys

import numpy as np
import pytest

torch = pytest.importorskip("torch")
from pin_tools import M05, PIN_CORPUS  # noqa: E402

sys.path.insert(0, str(M05))
import e7_t2_sqm as T2  # noqa: E402
import internal_coords as IC  # noqa: E402
import rungC_hybrid as RH  # noqa: E402
import rungC_infer as RI  # noqa: E402
import rungC_train as RT  # noqa: E402
from rungC_config import TrainConfig, config_from_argv  # noqa: E402

torch.set_num_threads(1)
PHENANTHRENE = PIN_CORPUS / "molecules" / "A_541c53d1a5"
V15 = IC.PrimitiveSettings(angle_choice="canonical", dihedral_encoding="cos")
HYBRID = dict(molecules="m", out_prefix="o", head="hybrid", aux="pattern", pair_features=True)


def test_the_config_defaults_to_the_carried_construction() -> None:
    assert TrainConfig(molecules="m", out_prefix="o").primitives == IC.CARRIED


def test_the_command_line_sets_both_switches() -> None:
    cfg = config_from_argv(["m", "o", "--head", "hybrid", "--aux", "pattern", "--pair-features", "--angle-choice", "canonical",
                            "--dihedral-encoding", "cos"])
    assert cfg.primitives == V15


def test_a_dihedral_encoding_without_pair_features_is_refused() -> None:
    with pytest.raises(ValueError, match="--dihedral-encoding"):
        TrainConfig(molecules="m", out_prefix="o", head="hybrid", aux="pattern", dihedral_encoding="cos")


def test_the_angle_choice_combines_with_every_head() -> None:
    assert TrainConfig(molecules="m", out_prefix="o", angle_choice="canonical").primitives.angle_choice == "canonical"


@pytest.mark.parametrize("record, expected", [({}, IC.CARRIED), ({"angle_choice": "canonical", "dihedral_encoding": "cos"}, V15)])
def test_record_primitives(record: dict, expected: IC.PrimitiveSettings) -> None:
    assert RT.record_primitives(record) == expected


def test_a_record_with_one_primitive_setting_is_refused() -> None:
    with pytest.raises(ValueError, match="without the other"):
        RT.record_primitives({"angle_choice": "canonical"})


def test_the_saved_model_carries_its_settings_only_when_they_are_not_the_carried_ones(tmp_path) -> None:
    model = RH.HybridDeltaFModel(aggregation="sum", n_pair_features=66)
    loss = RT.LossSettings(mode="pattern", kring_weight=0.3, kdiag_weight=0.0, kdiag_mode="all", class_scale=torch.ones(RH.N_PAIR_CLASSES))
    base = dict(aggregation="sum", tensor_input=False, sqm_scale=False, pattern="f", aux_target="projected", ls_lam=1e-3, head="hybrid")
    for args, expected in ((base, IC.CARRIED), ({**base, "angle_choice": "canonical", "dihedral_encoding": "cos"}, V15)):
        path = tmp_path / f"{expected.angle_choice}.pt"
        RT.save_hybrid_model(model, loss, path, args, n=1, seed=0)
        _m, ck = RT.load_hybrid_model(path)
        assert RT.tensor_config(ck).primitives == expected
        assert set(RT.PRIMITIVE_KEYS) & ck.keys() == (set() if expected == IC.CARRIED else set(RT.PRIMITIVE_KEYS))


def test_the_target_cache_keeps_the_angle_choices_apart() -> None:
    assert RT.cache_pattern(TrainConfig(molecules="m", out_prefix="o", pattern="f")) == "f"
    assert RT.cache_pattern(TrainConfig(molecules="m", out_prefix="o", pattern="f", angle_choice="canonical")) == "f-canonical"


@pytest.fixture(scope="module")
def phenanthrene() -> tuple[list[str], np.ndarray]:
    g = json.loads((PHENANTHRENE / "geometry.json").read_text(encoding="utf-8"))
    return list(g["symbols"]), np.asarray(g["coords_bohr"], float)


def test_the_parities_follow_the_canonical_rows(phenanthrene) -> None:
    symbols, x = phenanthrene
    S = np.diag([1.0, 1.0, -1.0])
    B0 = T2.internals(symbols, x, V15)[0]
    B1 = T2.internals(symbols, x @ S, V15)[0]                       # the same canonical order: the bond graph does not see the reflection
    ref = (B0.reshape(len(B0), -1, 3) @ S).reshape(len(B0), -1)
    odd = (B1 * ref).sum(1) < 0
    np.testing.assert_array_equal(RH.primitive_parity(symbols, x, V15)[0], odd)


def test_a_loader_built_another_way_is_refused(phenanthrene) -> None:
    symbols, x = phenanthrene
    with np.load(PHENANTHRENE / "hessian_b3lyp_analytic.npz") as z:
        H = np.asarray(z["H_projected"], float)
    B, _ = T2.internals(symbols, x)                                   # the carried construction
    m = {"B": B, "F_low": T2.to_internal(H, B)[0]}
    with pytest.raises(ValueError, match="differ from the loader's B"):
        RT.pattern_classes(PHENANTHRENE, m, "f", V15)


def test_the_inference_loader_builds_the_model_s_primitives(phenanthrene) -> None:
    symbols, x = phenanthrene
    _m, mol = RI.low_level(PHENANTHRENE, V15)
    np.testing.assert_allclose(mol["B"], T2.internals(symbols, x, V15)[0], atol=1e-12)
