"""The proxy check's mechanics (`m05/proxy_transfer_check.py`): id files, the draws of k molecules, the step budget, the base's record and
recipe for the scratch control, and the refusals before the corpus is loaded."""
import json
import sys
from pathlib import Path

import pytest

pytest.importorskip("torch")
M05 = Path(__file__).resolve().parents[1] / "modules" / "05_support_predictor" / "m05"
sys.path.insert(0, str(M05))
import proxy_transfer_check as P  # noqa: E402

CHAIN34 = ("rungC_train.py corpus/molecules out/E7_rungC_chain34_kdfamily_750_2026-10-05 --use-analytic --pool-layers A,A2,B --sizes all "
           "--seeds 0,1,2 --inner-val 0.15 --threads 8 --aggregation sum --head hybrid --aux both --kring-weight 0.3 --kdiag-weight 0.1 "
           "--kdiag-mode family --sqm-scale --pair-features --aux-weight 1.0 --epochs 200 --patience 20 --lr 3e-4 --hybrid-hidden 256 "
           "--pattern f --save-model")


def test_id_files(tmp_path):
    p = tmp_path / "ids.txt"
    p.write_text("# reservoir\nA_1\n\nA_2\n", encoding="utf-8")
    assert P.read_ids(p) == ["A_1", "A_2"]
    p.write_text("A_1\nA_1\n", encoding="utf-8")
    with pytest.raises(SystemExit, match="twice"):
        P.read_ids(p)
    p.write_text("# nothing\n", encoding="utf-8")
    with pytest.raises(SystemExit, match="no ids"):
        P.read_ids(p)


def test_draws_are_distinct_reproducible_and_order_free():
    pool = [f"m{i:02d}" for i in range(20)]
    a = P.draw_subsets(pool, 5, 4)
    assert len(a) == 4 and len(set(a)) == 4 and all(len(d) == 5 and list(d) == sorted(d) for d in a)
    assert P.draw_subsets(list(reversed(pool)), 5, 4) == a
    assert P.draw_subsets(pool, 20, 5) == [tuple(sorted(pool))]                       # k = the reservoir: one draw
    with pytest.raises(ValueError, match="only 2 subsets"):
        P.draw_subsets(pool[:2], 1, 5)
    with pytest.raises(ValueError, match="a subset of 21"):
        P.draw_subsets(pool, 21, 1)


def test_the_step_budget():
    assert P.epochs_for(3000, 10) == 300 and P.epochs_for(3000, 7) == 429 and P.epochs_for(3000, 200) == 15 and P.epochs_for(3, 10) == 1


def test_the_base_record_beside_a_saved_model():
    assert P.base_record_path(Path("out/x_model_n750_seed2.pt")) == Path("out/x.json")
    with pytest.raises(SystemExit, match="not a model the trainer saved"):
        P.base_record_path(Path("out/x.pt"))


def test_the_scratch_control_trains_the_base_recipe_on_the_true_label():
    cfg = P.scratch_config({"provenance": {"command": CHAIN34 + " --family-scale CH-oop=-0.43"}}, "corpus/molecules", "out/s", 1)
    assert cfg.family_scale is None and not cfg.save_model and cfg.seeds == "1" and cfg.epochs == 200
    assert (cfg.head, cfg.pattern, cfg.lr, cfg.inner_val, cfg.patience, cfg.kdiag_mode) == ("hybrid", "f", 3e-4, 0.15, 20, "family")


def _args(**kw):
    return P.build_parser().parse_args(["m", "x_model_n750_seed0.pt", "out/p", "--reservoir", "r", "--read", "q", "--k", "2",
                                        *[s for k, v in kw.items() for s in (f"--{k}", str(v))]])


def test_refusals_before_loading():
    with pytest.raises(SystemExit, match="unknown mode 'lora'"):
        P.check_args(_args(modes="head,lora"), ["a", "b"], ["c"])
    with pytest.raises(SystemExit, match="read ids are in the reservoir"):
        P.check_args(_args(), ["a", "b"], ["b", "c"])
    with pytest.raises(SystemExit, match="--head-l2 must be positive"):
        P.check_args(_args(**{"head-l2": 0}), ["a", "b"], ["c"])
    P.check_args(_args(**{"head-l2": 0, "modes": "head,head_all"}), ["a", "b"], ["c"])  # no pull asked: fine
    with pytest.raises(SystemExit, match="scratch needs --k 2"):
        P.check_args(_args(k=1), ["a", "b"], ["c"])


def test_the_report_names_every_column():
    read = {"family_mean": {"ring-ip": 1.0, "CH-stretch": 2.0, "CH-oop": 3.0, "other": 4.0}, "intensity_matched_mean": 0.2, "n_intensity": 2}
    res = {"k": 2, "seed": 0, "model": "x_model_n750_seed0.pt", "n_read": 3, "n_reservoir": 4, "steps": 3000, "zero_rule": read, "none": read,
           "draws": [{"modes": {"head_all": {"read": read, "seconds": 5.0}}}]}
    text = "\n".join(P.report(res))
    assert "| head_all | 0 | 1.00 | 2.00 | 3.00 | 4.00 | 0.200 | 5 |" in text and "base as is" in text
    json.dumps(res)


def test_refusals_of_the_early_stopped_modes():
    with pytest.raises(SystemExit, match="need --k 2"):
        P.check_args(_args(k=1, modes="head_all_es"), ["a", "b"], ["c"])
    with pytest.raises(SystemExit, match="--es-val must lie"):
        P.check_args(_args(modes="body1_es", **{"es-val": 0.6}), ["a", "b"], ["c"])
    with pytest.raises(SystemExit, match="must be positive"):
        P.check_args(_args(modes="body1_es", **{"es-patience": 0}), ["a", "b"], ["c"])
    P.check_args(_args(k=1, modes="head_all", **{"es-val": 0.6}), ["a", "b"], ["c"])     # no early-stopped mode asked: not checked
