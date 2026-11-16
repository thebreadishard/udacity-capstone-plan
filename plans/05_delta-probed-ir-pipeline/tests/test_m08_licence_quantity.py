"""The quantity the licence reads (README decision 65, amendment of 16 Nov 2026): the error of what the product delivers, from the
product-error record, with the first-order read-outs beside it under their own name. On a synthetic product-error record the two
quantities differ and the licence follows the product's; a version without the record is refused with the command that makes it; a
licensed family whose bootstrap interval crosses the line is named with the interval and its molecules. And the read script's own
summary (`probes/product_error_read.py`) on synthetic molecules and on the frozen corpus's benzene with the network replaced by a
perfect and by a zero correction. Evaluation records are read as JSON; no model file is loaded."""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import numpy as np
import pytest

from pin_tools import PIN_CORPUS, PLAN, require_frozen_corpus

sys.path.insert(0, str(PLAN / "modules" / "08_industry_synthesis"))
sys.path.insert(0, str(PLAN / "probes"))
import product_error_read as PE
from m08 import accuracy as A
from m08 import licence

V13 = tuple(f"E7_rungC_chain35_analytic_model_n750_seed{s}.pt" for s in range(3))
FAMILIES = ("ring-ip", "CH-stretch", "CH-oop", "other")
SETS = {"a": ("a8", 8), "b": ("b", 39)}
BENZENE = "A_8448043181"


def product_record(folder: Path, rms: dict[str, dict[str, float]], interval: dict[tuple[str, str], list[float]] | None = None,   # noqa: PLR0913  a record's fields
                   models: tuple[str, ...] = V13, sets: dict[str, tuple[str, int]] = SETS,
                   with_modes: dict[tuple[str, str], int] | None = None, sha16: dict[str, str] | None = None) -> Path:
    """A product-error record as `probes/product_error_read.py` writes it, with the given rms per hold-out and family; the interval is
    ±0.1 around the rms unless given, every molecule has the family's bands unless `with_modes` says how many do, and the models'
    hashes are `sha16` or sixteen zeros."""
    holdouts = {}
    for h, (key, n) in sets.items():
        fams = {}
        for f in FAMILIES:
            x = rms[h][f]
            lo, hi = (interval or {}).get((h, f), [x - 0.1, x + 0.1])
            fams[f] = {"product": {"rms": x, "n_modes": 40, "n_molecules": n, "n_molecules_with_modes": (with_modes or {}).get((h, f), n),
                                   "interval": [lo, hi],
                                   "share_below_line": 0.8, "largest_single_molecule_rms": hi}}
        holdouts[h] = {"set": key, "n_molecules": n, "ids": [], "families": fams}
    path = folder / "synthetic_product_error.json"
    hashes = {m: "0" * 16 for m in models} | (sha16 or {})
    path.write_text(json.dumps({"models": list(models), "model_sha16": hashes, "holdouts": holdouts}), encoding="utf-8")
    return path


def accuracy_with(product: Path) -> dict:
    return A.network_accuracy(A.evaluation_records(V13), A.clean_a_records(V13), product)


FLAT = {h: dict.fromkeys(FAMILIES, 2.0) for h in SETS}


def test_the_two_quantities_differ_and_the_licence_follows_the_products(tmp_path):
    """v1.3's first-order read-outs put 'other' above the line (3.62 / 3.89) and CH-stretch under it (1.19 / 2.5); the synthetic product
    error says the opposite, and the licence says what the product error says."""
    rms = {"a": {**FLAT["a"], "other": 2.9}, "b": {**FLAT["b"], "other": 2.9, "CH-stretch": 3.2}}
    acc = accuracy_with(product_record(tmp_path, rms))
    assert acc["licence_quantity"] == A.PRODUCT and set(acc["quantities"]) == {"readouts", A.PRODUCT}
    assert acc["holdouts"]["a"]["readouts"]["other"]["mean"] == 3.62 and acc["holdouts"]["a"][A.PRODUCT]["other"]["rms"] == 2.9
    assert acc["holdouts"]["b"][A.PRODUCT]["CH-stretch"] == dict(rms=3.2, n_modes=40, n_molecules=39, n_molecules_with_modes=39,
                                                                 interval=[3.1, 3.3], share_below_line=0.8, target=3.0, within_target=False,
                                                                 interval_crosses_line=True)
    s = licence.state(acc)
    assert s["licensed_families"] == ["ring-ip", "CH-oop", "other"] and s["quantity"] == A.PRODUCT
    assert s["errors"]["other"] == {"a": 2.9, "b": 2.9} and s["first_order_errors"]["other"] == {"a": 3.62, "b": 3.89}
    assert "not licensed: CH-stretch (2.0 / 3.2) — error of the corrected band positions of the seed-mean correction" in s["statement"]
    assert "first-order diagonal error of each seed's correction, averaged over the seeds, which the licence read until then: " in s["statement"]
    assert "other (3.62 / 3.89); no coupled-cluster licence" in s["statement"] and "amended on 16 Nov 2026" in s["statement"]
    assert A.stated_errors(acc) == (A.PRODUCT, s["errors"])


def test_a_family_on_the_line_is_licensed_and_one_above_it_is_not(tmp_path):
    rms = {"a": {**FLAT["a"], "other": 3.0}, "b": {**FLAT["b"], "other": 3.0, "CH-oop": 3.01}}
    assert licence.state(accuracy_with(product_record(tmp_path, rms)))["licensed_families"] == ["ring-ip", "CH-stretch", "other"]


def test_an_interval_that_crosses_the_line_is_stated_for_a_licensed_family_only(tmp_path):
    """ring-ip is licensed on an interval that reaches above the line on (b); CH-oop's interval ends on the line; 'other' crosses it
    but is not licensed, so its error already says what the reader needs."""
    rms = {"a": dict(FLAT["a"]), "b": {**FLAT["b"], "other": 3.4}}
    interval = {("b", "ring-ip"): [1.5, 3.4], ("b", "CH-oop"): [1.2, 3.0], ("b", "other"): [2.9, 3.9]}
    s = licence.state(accuracy_with(product_record(tmp_path, rms, interval)))
    sentence = ("ring-ip on hold-out (b) rests on 39 molecules: the 95 % interval of a bootstrap over molecules is 1.5–3.4 cm⁻¹ and "
                "crosses the line (80 % of the resamples lie under it)")
    assert s["caveats"] == [sentence] and f"; {sentence}; the first-order" in s["statement"]
    assert licence.state(accuracy_with(product_record(tmp_path, FLAT)))["caveats"] == []


def test_a_version_without_a_product_error_record_is_refused_with_the_command(tmp_path, monkeypatch):
    with pytest.raises(A.NoProductError, match=r"python tools/runspec\.py launch probes/runspecs/product_error_read\.json"):
        A.product_error_record(("E7_rungC_nochain_model_n750_seed0.pt",))
    for p in [*A.evaluation_records(V13), *A.clean_a_records(V13)]:
        shutil.copy(p, tmp_path / p.name)
    monkeypatch.setattr(A, "M05_OUT", tmp_path)
    with pytest.raises(A.NoProductError, match=r"no product-error record E7_rungC_chain35_analytic_product_error\.json"):
        A.carried_accuracy()


def test_first_order_read_outs_alone_give_no_licence():
    acc = A.network_accuracy(A.evaluation_records(V13), A.clean_a_records(V13))
    assert acc["holdouts"]["a"][A.PRODUCT] is None and acc["holdouts"]["a"]["readouts"]["other"]["mean"] == 3.62
    with pytest.raises(A.NoProductError, match="first-order read-outs only"):
        licence.state(acc)


def test_an_accuracy_stored_before_the_amendment_names_its_quantity_and_gives_no_licence():
    acc = A.network_accuracy(A.evaluation_records(V13), A.clean_a_records(V13))
    stored = {k: v for k, v in acc.items() if k not in ("licence_quantity", "quantities")}
    quantity, errors = A.stated_errors(stored)
    assert quantity == A.FIRST_ORDER and errors["other"] == {"a": 3.62, "b": 3.89}
    with pytest.raises(ValueError, match="stored before the amendment of 16 Nov 2026"):
        licence.state(stored)


def test_a_record_of_other_models_or_another_set_is_refused(tmp_path, monkeypatch):
    with pytest.raises(ValueError, match=r"hold-out \(a\) was read on 'a8' \(8 molecules\), the evaluation records on 'a' \(10\)"):
        A.network_accuracy(A.evaluation_records(V13), None, product_record(tmp_path, FLAT))
    with pytest.raises(ValueError, match="one version's"):
        A.product_error_record((V13[0], "E7_rungC_other_model_n750_seed1.pt"))
    monkeypatch.setattr(A, "M05_OUT", tmp_path)
    product_record(tmp_path, FLAT, models=V13[:2]).rename(tmp_path / f"E7_rungC_chain35_analytic{A.PRODUCT_SUFFIX}")
    with pytest.raises(ValueError, match="was read on"):
        A.product_error_record(V13)


def test_a_family_without_bands_on_a_hold_out_has_no_error_there(tmp_path):
    path = product_record(tmp_path, FLAT)
    rec = json.loads(path.read_text(encoding="utf-8"))
    rec["holdouts"]["a"]["families"]["CH-oop"]["product"]["rms"] = None
    path.write_text(json.dumps(rec), encoding="utf-8")
    with pytest.raises(ValueError, match="no CH-oop band"):
        accuracy_with(path)


def test_a_caveat_counts_the_molecules_that_have_the_familys_bands(tmp_path):
    """CH-oop: five of hold-out (a)'s eight molecules have such a band; the sentence names those five, not the eight."""
    acc = accuracy_with(product_record(tmp_path, FLAT, {("a", "CH-oop"): [1.0, 3.2], ("a", "other"): [1.0, 3.2]}, with_modes={("a", "CH-oop"): 5}))
    assert acc["holdouts"]["a"][A.PRODUCT]["CH-oop"]["n_molecules_with_modes"] == 5
    oop, other = licence.state(acc)["caveats"]
    assert oop.startswith("CH-oop on hold-out (a) rests on 5 of the hold-out's 8 molecules (the others have no such band): the 95 % interval")
    assert other.startswith("other on hold-out (a) rests on 8 molecules: the 95 % interval")


@pytest.mark.parametrize(("field", "value"), [("rms", -1.0), ("rms", float("nan")), ("rms", float("inf")), ("interval", [1.0, float("nan")]),
                                              ("interval", [-0.5, 2.0]), ("interval", [1.0]), ("interval", [1.0, None])])
def test_a_value_that_is_not_a_finite_non_negative_number_is_refused(tmp_path, field, value):
    """A negative rms would be licensed; a NaN upper bound compares false with the line and would drop the caveat."""
    path = product_record(tmp_path, FLAT)
    rec = json.loads(path.read_text(encoding="utf-8"))
    rec["holdouts"]["b"]["families"]["other"]["product"][field] = value
    path.write_text(json.dumps(rec), encoding="utf-8")
    with pytest.raises(ValueError, match="other rms and interval must be three finite numbers ≥ 0"):
        accuracy_with(path)


def test_a_record_read_on_other_files_of_the_same_names_is_refused(tmp_path, monkeypatch):
    """The record is tied to the checkpoints by hash: the files beside the records where this machine has them, or the hashes a
    pipeline record names; names alone only where no file and no hash is at hand."""
    monkeypatch.setattr(A, "M05_OUT", tmp_path)
    (tmp_path / V13[0]).write_bytes(b"a checkpoint")
    own = A.P.sha16(tmp_path / V13[0])
    record = tmp_path / f"E7_rungC_chain35_analytic{A.PRODUCT_SUFFIX}"
    product_record(tmp_path, FLAT).rename(record)
    with pytest.raises(ValueError, match=rf"sha16 differs for {V13[0]} \(record 0000000000000000, file {own}\)"):
        A.product_error_record(V13)
    product_record(tmp_path, FLAT, sha16={V13[0]: own}).replace(record)
    assert A.product_error_record(V13) == record                         # seed 0 hashed and equal; seeds 1 and 2 not on this machine
    assert A.product_error_record(V13, {m: "0" * 16 for m in V13[1:]} | {V13[0]: own}) == record
    with pytest.raises(ValueError, match=rf"sha16 differs for {V13[2]} \(record 0000000000000000, file ffff\)"):
        A.product_error_record(V13, {V13[2]: "ffff"})
    with pytest.raises(ValueError, match="not among the models"):
        A.product_error_record(V13, {"E7_rungC_other_model_n750_seed0.pt": own})


# ------------------------------------------------------------------------------------------------ the read script
def test_the_read_stores_the_label_files_hashes_and_can_state_its_peak_memory(tmp_path, monkeypatch):
    require_frozen_corpus()
    folder = tmp_path / "corpus" / "molecules" / BENZENE
    shutil.copytree(PIN_CORPUS / "molecules" / BENZENE, folder)
    monkeypatch.setattr(PE.P, "correction", lambda models, d: (np.zeros((36, 36)), [np.zeros((36, 36))]))
    cfg = PE.Config(m05=tmp_path, out=None, package=None, threads=1)
    out = PE.read_holdouts(cfg, (), {"a": ("a8", [BENZENE])})
    assert out["a"]["label_sha16"] == {BENZENE: {name: PE.P.sha16(folder / name) for name in PE.LABELS}}
    assert len(out["a"]["label_sha16"][BENZENE]) == 2 and 0.0 < PE.peak_memory_gb() < 64.0
    assert {"label_sha16", "run"} <= set(PE.DEFINITIONS)


def synthetic_read(first: list[list[float]], band: list[float], families: list[str], band_families: list[str] | None = None) -> PE.MoleculeRead:
    fam = np.array(families)
    return PE.MoleculeRead(fam, fam, np.array(first, float), fam if band_families is None else np.array(band_families), np.array(band, float))


def test_the_summary_counts_modes_and_molecules_and_averages_the_seeds_rms():
    """Two molecules, two seeds; the second molecule has no CH-oop mode, and one band of the first has moved to another family."""
    one = synthetic_read([[3.0, 4.0, 1.0], [0.0, 0.0, 1.0]], [1.0, 1.0, 2.0], ["other", "other", "CH-oop"], ["other", "CH-oop", "CH-oop"])
    two = synthetic_read([[0.0], [5.0]], [3.0], ["other"])
    other, oop = PE.family_summary([one, two], "other"), PE.family_summary([one, two], "CH-oop")
    assert other["first_order"]["seeds"] == pytest.approx([np.sqrt(25 / 3), np.sqrt(25 / 3)]) and other["first_order"]["n_modes"] == 3
    assert other["first_order"]["seed_mean"] == pytest.approx(np.sqrt(25 / 3))
    assert other["product"]["rms"] == pytest.approx(np.sqrt(5.0)) and other["product"]["n_modes"] == 2
    assert (oop["product"]["n_modes"], oop["product"]["n_molecules"], oop["product"]["n_molecules_with_modes"]) == (2, 2, 1)
    assert oop["product"]["rms"] == pytest.approx(np.sqrt(2.5)) and oop["first_order"]["n_modes"] == 1
    assert PE.family_summary([one, two], "ring-ip")["product"]["rms"] is None


def test_the_bootstrap_resamples_whole_molecules_and_repeats():
    quiet, loud = np.full(10, 1.0), np.full(10, 5.0)
    boot = PE.bootstrap([quiet, loud, np.array([])], line=3.0)
    assert boot == PE.bootstrap([quiet, loud, np.array([])], line=3.0)                    # seeded
    assert boot["interval"] == [pytest.approx(0.0, abs=1e-12), pytest.approx(5.0)]         # a draw of the empty molecule alone is 0
    assert boot["largest_single_molecule_rms"] == pytest.approx(5.0) and 0.0 < boot["share_below_line"] < 1.0
    assert PE.bootstrap([quiet, quiet], line=3.0)["interval"] == [pytest.approx(1.0), pytest.approx(1.0)]


@pytest.fixture
def benzene() -> Path:
    require_frozen_corpus()
    return PIN_CORPUS / "molecules" / BENZENE


def test_a_perfect_correction_has_no_error_and_a_zero_correction_has_the_levels_distance(benzene, monkeypatch):
    lo, hi = PE.label_hessians(benzene)
    monkeypatch.setattr(PE.P, "correction", lambda models, folder: (hi - lo, [hi - lo, np.zeros_like(lo)]))
    perfect = PE.molecule_read(benzene, ())
    assert np.abs(perfect.band).max() < 1e-6 and np.abs(perfect.first_order[0]).max() < 1e-3
    assert sorted(perfect.band_family) == sorted(perfect.family) and len(perfect.band) == 30
    truth = PE.molecule_features(benzene, lo=lo, hi=hi)["target"]
    assert np.abs(perfect.first_order[1] + truth).max() < 1e-3                             # the zero seed is off by the whole shift
    monkeypatch.setattr(PE.P, "correction", lambda models, folder: (np.zeros_like(lo), [np.zeros_like(lo)]))
    zero = PE.molecule_read(benzene, ())
    assert list(zero.band_family) == list(zero.family)                                     # each B3LYP mode is its own partner
    off = np.sqrt(np.mean(zero.band ** 2))
    assert off > 5.0 and np.sqrt(np.mean((zero.band + truth) ** 2)) < 0.5 * off             # first order explains most of it, not all


def test_a_read_that_misses_the_evaluation_records_or_the_package_stops(tmp_path, capsys):
    fams = {f: {"first_order": {"seed_mean": 2.0}, "first_order_certificate_families": {"seed_mean": 2.0},
                "product": {"rms": 1.5, "interval": [1.0, 2.0]}} for f in FAMILIES}
    holdouts = {"a": {"set": "a8", "ids": ["x"], "families": fams}}
    recorded = {"a": dict.fromkeys(FAMILIES, 2.004)}
    assert PE.check_first_order(holdouts, recorded)["largest_difference_cm"] == pytest.approx(0.004)
    with pytest.raises(SystemExit, match="STOP: the first-order error differs"):
        PE.check_first_order(holdouts, {"a": {**recorded["a"], "other": 2.006}})
    table = {"mean": {f: {"band": 1.5} for f in FAMILIES}, "printed_quantity": dict.fromkeys(FAMILIES, 2.0),
             "mean_band_bootstrap": {f: {"p2.5": 1.0, "p97.5": 2.0} for f in FAMILIES}}
    package = tmp_path / "product_error.json"
    package.write_text(json.dumps({"sets": {"a8": {"ids": ["x"], "corpus": table}}}), encoding="utf-8")
    assert PE.check_package(holdouts, package)["largest_difference_cm"] == 0.0
    table["mean"]["other"]["band"] = 1.52
    package.write_text(json.dumps({"sets": {"a8": {"ids": ["x"], "corpus": table}}}), encoding="utf-8")
    with pytest.raises(SystemExit, match=r"STOP: this read differs from the package's record by 0\.0200"):
        PE.check_package(holdouts, package)
    package.write_text(json.dumps({"sets": {"a8": {"ids": ["y"], "corpus": table}}}), encoding="utf-8")
    with pytest.raises(SystemExit, match="lists other molecules"):
        PE.check_package(holdouts, package)
    assert "first order, hold-out (a), seed means" in capsys.readouterr().out


def eval_record(path: Path, model: str, ids: dict[str, list[str]], shift: float = 0.0) -> Path:
    """A `rungC_eval_saved.py` record on the frozen hold-out (b) with the given molecules per hold-out."""
    path.write_text(json.dumps({"model": model, "holdout_b_file": "corpus/holdout_b_frozen_2026-10-08.txt", "substituted_analytic": [],
                                **{h: {"diag_rms": dict.fromkeys(FAMILIES, 2.0 + shift), "coupling_ratio": 0.2,
                                       "per_molecule": {k: {} for k in i}} for h, i in ids.items()}}), encoding="utf-8")
    return path


def test_named_checkpoints_are_read_with_their_own_records_before_they_are_carried(tmp_path):
    (tmp_path / "corpus" / "molecules").mkdir(parents=True)
    (tmp_path / "out" / "v14").mkdir(parents=True)
    ids = {"a": [f"A_{k}" for k in range(10)], "a8": [f"A_{k}" for k in range(8)], "b": ["B_1"]}
    models = [f"out/v14/E7_new_model_n1082_seed{s}.pt" for s in range(3)]
    records = [f"out/v14/eval_data_seed{s}.json" for s in range(3)]
    for s, (m, r) in enumerate(zip(models, records, strict=True)):
        (tmp_path / m).write_bytes(b"x")
        eval_record(tmp_path / r, m, ids, shift=0.1 * s)
    argv = ["--m05", str(tmp_path), "--threads", "1", "--models", *models, "--records", *records]
    with pytest.raises(SystemExit, match="--models needs --out"):                   # never the carried version's record name
        PE.parse(argv)
    cfg = PE.parse([*argv, "--out", str(tmp_path / "x_product_error.json")])
    read = PE.inputs(cfg)
    assert [m.name for m in read.models] == [Path(m).name for m in models] and read.stem == "E7_new"
    assert read.version == PE.CANDIDATE and read.clean == read.records and [r.name for r in read.records] == [Path(r).name for r in records]
    sets, recorded, sources = PE.holdout_sets(read.records, read.clean)
    assert sets == {"a": ("a8", ids["a8"]), "b": ("b", ids["b"])}                   # the eight, not the ten the records also hold
    assert len(sets["a"][1]) == 8 and sources == [Path(r).name for r in records]
    assert recorded["b"] == pytest.approx(dict.fromkeys(FAMILIES, 2.1))             # the records' seed mean, which the read must reproduce
    with pytest.raises(SystemExit, match="go together"):
        PE.parse([*argv[:-1], "--out", str(tmp_path / "x.json")])                   # two records for three checkpoints
    patterns = [f"out/v14/E7_new_model_n*_seed{s}.pt" for s in range(3)]            # the pool size in the name left open, as in a chain
    by_pattern = PE.parse(["--m05", str(tmp_path), "--out", str(tmp_path / "x.json"), "--models", *patterns, "--records", *records])
    assert by_pattern.models == cfg.models
    with pytest.raises(SystemExit, match="matches 3 files, expected 1"):
        PE.parse(["--m05", str(tmp_path), "--out", str(tmp_path / "x.json"), "--models", "out/v14/E7_new_model_n*.pt", "--records", records[0]])
    with pytest.raises(SystemExit, match="matches 0 files, expected 1"):
        PE.parse(["--m05", str(tmp_path), "--out", str(tmp_path / "x.json"), "--models", "out/v14/E7_none_*.pt", "--records", records[0]])
    with pytest.raises(SystemExit, match="no such file"):
        PE.parse(["--m05", str(tmp_path), "--out", str(tmp_path / "x.json"), "--models", "out/v14/none.pt", "--records", records[0]])
    eval_record(tmp_path / records[1], models[2], ids)                              # a record of another checkpoint in the second place
    with pytest.raises(SystemExit, match=r"eval_data_seed1\.json evaluated E7_new_model_n1082_seed2\.pt, not E7_new_model_n1082_seed1\.pt"):
        PE.inputs(cfg)
    eval_record(tmp_path / records[1], models[1], {**ids, "a8": ["A_1"]})           # the seeds' records on different molecules
    with pytest.raises(SystemExit, match="list different molecules under 'a8'"):
        PE.holdout_sets(PE.inputs(cfg).records, PE.inputs(cfg).clean)
    eval_record(tmp_path / records[1], models[1], {"a": ids["a"], "b": ids["b"]})   # an older record: the ten only
    with pytest.raises(SystemExit, match=r"eval_data_seed1\.json holds no set 'a8'"):
        PE.inputs(cfg)
    other = tmp_path / "out" / "v14" / "E7_old_model_n750_seed0.pt"
    other.write_bytes(b"x")
    with pytest.raises(SystemExit, match="are of 2 stems"):
        PE.common_stem((other, *read.models[1:]))


def test_the_v14_run_spec_reads_the_candidates_of_chain_v14_data():
    sys.path.insert(0, str(PLAN / "tools"))
    import runspec
    spec = runspec.RunSpec.model_validate_json((PLAN / "probes" / "runspecs" / "product_error_read_v14.json").read_text(encoding="utf-8"))
    chain = json.loads((PLAN / "probes" / "runs" / "v14_data.json").read_text(encoding="utf-8"))
    words = spec.command.split()
    models, records = (words[words.index(flag) + 1:words.index(flag) + 4] for flag in ("--models", "--records"))
    evals = [s["argv"] for s in chain["steps"] if s["label"].startswith("eval eval_data_seed")]
    assert records == [f"{a[3]}.json" for a in evals]                               # the chain's own eval records
    assert models == [a[2] for a in evals]                                          # … of the checkpoints it evaluated, by its patterns
    assert "--out" in words and "--package" not in words                           # the package's record is version 1.3's
