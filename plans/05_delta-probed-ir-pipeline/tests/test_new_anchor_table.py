"""The new anchors' read (`probes/new_anchor_table.py`) on synthetic anchors: what counts as finished, the table per milestone, the
read-outs beside it and the hand-over to the registered rule; and `product_error_read.corrected_bands`, which it shares with the licence."""
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

pytest.importorskip("torch")
pytest.importorskip("rdkit")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "probes"))
import new_anchor_read as R
import new_anchor_table as T
import product_error_read as PE
import rungC_intensities as RINT
from learning_curve_layerA import normal_modes


def entry(mol_id, tier="TZ", status="carried"):
    return {"mol_id": mol_id, "tier": tier, "status": status, "path": f"p/{mol_id}.npz", "sha16": "0" * 16, "level": "composite"}


def test_finished_means_a_carried_entry_on_the_composite_tier():
    entries = [entry("a"), entry("b", tier="DZ"), entry("c", status="superseded"), entry("c", tier="TZ", status="invalid")]
    done, left = T.finished_anchors(["a", "b", "c", "d"], entries)
    assert list(done) == ["a"]
    assert "MP2 basis step is missing" in left["b"] and left["c"] == left["d"] == "no carried anchor yet"


def test_family_points_pool_bands_over_molecules_and_skip_a_family_without_bands():
    fam = np.array(["ring-ip", "ring-ip", "CH-oop"])
    reads = {"m1": (np.array([3.0, 4.0, 1.0]), fam), "m2": (np.array([0.0, 0.0, 1.0]), fam)}
    points = T.family_points(reads)
    assert sorted(points) == ["CH-oop", "ring-ip"]
    assert points["ring-ip"]["mean"] == pytest.approx(np.sqrt(25 / 4)) and points["ring-ip"]["n_bands"] == 4
    assert points["CH-oop"]["mean"] == pytest.approx(1.0) and points["CH-oop"]["n_molecules_with_bands"] == 2
    assert points["ring-ip"]["lo"] <= points["ring-ip"]["mean"] <= points["ring-ip"]["hi"]


def test_largest_quarter_takes_the_largest_by_atoms_and_at_least_one():
    atoms = {"a": 12, "b": 24, "c": 18, "d": 18, "e": 10, "f": 11, "g": 13, "h": 14}
    assert T.largest_quarter(list(atoms), atoms) == ["b", "c"]            # 2 of 8; the tie between c and d goes to the id
    assert T.largest_quarter(["e"], atoms) == ["e"]


def test_curves_for_rule_turn_the_table_around_and_keep_a_gap_a_gap():
    p = {"mean": 2.0, "lo": 1.5, "hi": 2.5}
    table = {20: {"ring-ip": p, "other": p}, 40: {"ring-ip": p}}
    curves = T.curves_for_rule(table)
    assert curves["ring-ip"] == {20: R.Point(2.0, 1.5, 2.5), 40: R.Point(2.0, 1.5, 2.5)} and list(curves["other"]) == [20]


def test_corrected_bands_is_the_overlap_paired_band_error_in_the_low_level_partner_s_family():
    rng = np.random.default_rng(3)
    masses = np.array([12.0, 1.008, 14.003, 12.0])
    a = rng.normal(size=(12, 12))
    lo = a @ a.T + 5 * np.eye(12)
    b = rng.normal(size=(12, 12)) * 0.05
    hi = lo + b @ b.T
    dH = 0.6 * (hi - lo)
    _, w_low, V_low, _ = normal_modes(lo, masses)
    family = np.array([f"f{j % 3}" for j in range(len(w_low))])
    got = PE.corrected_bands(PE.Hessians(lo, hi, masses), dH, family)
    _, w_ref, V_ref, _ = normal_modes(hi, masses)
    _, w_net, V_net, _ = normal_modes(lo + dH, masses)
    assert np.allclose(got.error, w_net - w_ref[RINT.match_modes(V_net, V_ref)])
    assert list(got.family) == list(family[RINT.match_modes(V_net, V_low)]) and np.allclose(got.low_freq, w_low)
    exact = PE.corrected_bands(PE.Hessians(lo, hi, masses), hi - lo, family)
    assert np.abs(exact.error).max() < 1e-6                                # the true correction leaves no error


FAMILY = np.array(["ring-ip", "CH-stretch", "CH-oop", "other"])
FITTED: list[list[str]] = []          # the ids of every fit the fake fine-tune was given


def fake_problem(n_train, n_test):
    train = [f"t{j:03d}" for j in range(n_train)]
    test = [f"x{j:03d}" for j in range(n_test)]
    mols = {i: {"H_low": np.zeros((4, 4)), "dH_true": np.zeros((4, 4)), "masses": np.ones(3 + j % 5), "B": np.eye(4)}
            for j, i in enumerate([*train, *test])}
    an = SimpleNamespace(mols=mols, tensors={i: {"id": i} for i in mols})
    nets = [SimpleNamespace(model={"k": 0, "seed": s}, loss_cfg=None, cfg=None, seed=s, path=Path(f"m{s}.pt")) for s in (0, 1, 2)]
    return T.Problem(an, nets, train, test, Path("molecules"))


@pytest.fixture
def fakes(monkeypatch):
    """A stand-in physics: a network fine-tuned on k anchors predicts a ΔH whose every band is off by 60 / k cm⁻¹ (5 as it is); the
    α scaling by 4; the zero rule by 30."""
    def finetune_es(model, loss_cfg, train, recipe, run, log=print):
        model["k"] = len(train)
        FITTED.append(list(train))
        log("fitted")
        return {"final_loss": 0.1, "best_epoch": 3, "epochs_run": 13, "val_loss": 0.2, "n_fit": len(train) - 3, "n_val": 3,
                "recipe": recipe, "split_seed": run.es.seed}

    monkeypatch.setattr(T.CT, "finetune_es", finetune_es)
    monkeypatch.setattr(T.CT, "predict_cartesian", lambda model, t: np.full((4, 4), 60.0 / model["k"] if model["k"] else 5.0))
    monkeypatch.setattr(T.CT, "alpha_scaling_baseline", lambda mols, tensors, train_ids, i: np.full((4, 4), 4.0))
    FITTED.clear()
    monkeypatch.setattr(T, "molecule_features", lambda folder, lo, hi: {"family": list(FAMILY), "freq": np.zeros(4)})
    monkeypatch.setattr(T.PE, "corrected_bands",
                        lambda h, dH, family: PE.CorrectedBands(np.full(4, dH[0, 0] if dH.any() else 30.0), family, np.zeros(4)))


def test_run_read_builds_every_milestone_and_hands_the_table_to_the_rule(fakes):
    logs = []
    rec = T.run_read(fake_problem(40, 32), 122, logs.append)
    assert rec["milestones"] == [20, 40]
    assert {f: rec["curves"][20][f]["mean"] for f in R.FAMILIES} == dict.fromkeys(R.FAMILIES, pytest.approx(3.0))
    assert rec["curves"][40]["other"]["mean"] == pytest.approx(1.5)
    assert rec["zero_rule"]["ring-ip"]["mean"] == pytest.approx(30.0) and rec["proxy_as_is"]["ring-ip"]["mean"] == pytest.approx(5.0)
    assert rec["alpha_scaling"][20]["CH-oop"]["mean"] == pytest.approx(4.0)
    assert sorted(rec["fits"][40]) == ["0", "1", "2"] and rec["fits"][40]["2"]["split_seed"] == 2 and rec["fits"][40]["0"]["recipe"] == "body1_es"
    assert rec["outcome"]["verdict"] == "REACHED" and rec["outcome"]["k"] == 20          # 3.0 at 20 and 1.5 at 40
    size = rec["size_readout"]
    assert size["k"] == 40 and len(size["ids"]) == 8 and min(size["atoms"]) == 6 and size["families"]["other"]["mean"] == pytest.approx(1.5)
    assert any("k 40:" in line for line in logs) and any("[k 20 seed 1] fitted" in line for line in logs)


def test_run_read_without_a_milestone_reads_the_baselines_and_gives_no_reading(fakes):
    rec = T.run_read(fake_problem(0, 32), 122, lambda s: None)
    assert rec["milestones"] == [] and rec["curves"] == {} and rec["size_readout"]["families"] is None
    assert rec["proxy_as_is"]["other"]["mean"] == pytest.approx(5.0)
    assert rec["outcome"]["verdict"] == "NO READING"


def test_run_read_with_too_few_test_anchors_gives_no_reading(fakes):
    rec = T.run_read(fake_problem(40, 12), 122, lambda s: None)
    assert rec["outcome"]["verdict"] == "NO READING" and "at least 30" in rec["outcome"]["reason"]


def test_the_record_is_written_once_and_its_table_names_the_outcome(fakes, tmp_path):
    rec = {"date": "2026-11-21 23:00", "networks": ["m0.pt"], "n_train_order": 122, "n_train_finished_in_order": 45, "n_test_listed": 49,
           "test_read": [f"x{j}" for j in range(32)], "test_left_out": {"A_x": "no carried anchor yet"}, "seconds": 5,
           **T.run_read(fake_problem(40, 32), 122, lambda s: None)}
    T.write_record(tmp_path / "read", rec)
    text = (tmp_path / "read.md").read_text(encoding="utf-8")
    assert "**Outcome: REACHED at k = 20**" in text and "| R2 on k = 40 |" in text and "A_x (no carried anchor yet)" in text
    assert json.loads((tmp_path / "read.json").read_text(encoding="utf-8"))["curves"]["40"]["other"]["mean"] == pytest.approx(1.5)
    with pytest.raises(SystemExit, match="written once"):
        T.main(["--out", str(tmp_path / "read")])


def test_every_fit_sees_exactly_the_first_k_training_anchors_and_never_a_test_anchor(fakes):
    pr = fake_problem(40, 32)
    T.run_read(pr, 122, lambda s: None)
    assert [pr.train[:20]] * 3 + [pr.train[:40]] * 3 == FITTED
    assert not set(pr.test) & {i for ids in FITTED for i in ids}


def test_band_read_refuses_family_labels_that_are_not_the_low_level_modes(fakes, monkeypatch):
    monkeypatch.setattr(T, "molecule_features", lambda folder, lo, hi: {"family": list(FAMILY), "freq": np.ones(4)})
    with pytest.raises(SystemExit, match="not the B3LYP normal modes"):
        T.run_read(fake_problem(0, 32), 122, lambda s: None)


def test_training_head_is_cut_to_a_milestone_and_names_what_holds_the_order():
    order = [f"t{j:03d}" for j in range(60)]
    done = {i: {} for i in order if i != "t045"}
    head, info = T.training_head(order, done, {"t045": "carried on tier DZ, not TZ: its MP2 basis step is missing"})
    assert head == order[:40] and info["n_train_finished_in_order"] == 45
    assert info["order_held_by"] == {"position": 46, "id": "t045", "why": "carried on tier DZ, not TZ: its MP2 basis step is missing",
                                     "finished_behind_it": 14}
    head, info = T.training_head(order, {i: {} for i in order}, {})
    assert head == order and info["order_held_by"] is None


def test_verify_files_refuses_an_anchor_file_changed_since_it_was_registered(tmp_path):
    import anchor_registry as AR
    f = tmp_path / "p" / "a.npz"
    f.parent.mkdir()
    f.write_bytes(b"first")
    e = {**entry("a"), "sha16": AR.sha16(f)}
    T.verify_files({"a": e}, [e], root=tmp_path)
    f.write_bytes(b"fetched again")
    with pytest.raises(SystemExit, match="changed since it was registered"):
        T.verify_files({"a": e}, [e], root=tmp_path)


def test_a_test_anchor_in_the_training_order_is_refused_before_anything_is_loaded(tmp_path):
    (tmp_path / "train_ids.txt").write_text("a\nb\n")
    (tmp_path / "test_ids.txt").write_text("b\nc\n")
    with pytest.raises(SystemExit, match="never trained on"):
        T.build_problem(SimpleNamespace(lists=tmp_path), [])
