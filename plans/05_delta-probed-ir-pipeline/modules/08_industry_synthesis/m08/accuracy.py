"""The measured error of a ΔH-network version, under two named quantities. The first-order read-outs come from its own evaluation
records (`probes/rungC_eval_saved.py`, one JSON per seed): per mode family and hold-out against the 3 cm⁻¹ line, the coupling ratio, and
the spectral shape. The error of what the product delivers — the corrected band positions of the seed-mean correction — comes from its
product-error record (`probes/product_error_read.py`); the licence reads that one since 16 Nov 2026 (README decision 65, dated
amendment). One implementation for the licence, the live certificate and the export certificate."""
from __future__ import annotations

import json
import math
from pathlib import Path

from . import pipeline as P
from .spectrum import shape_accuracy

# isort: split
# probes/, on the path through m08.pipeline
from chain35_read import T1_FAMILY_LINE, T1_RATIO_LINE
from promotion_read import FAMILIES, QUANTITIES, RATIO, Arm, load_eval_arm, reported

M05_OUT = P.M05 / "out"
LICENCE_LINE_CM = T1_FAMILY_LINE        # decision 53's 3 cm⁻¹, every family's line under decision 65
TARGETS = {**dict.fromkeys(FAMILIES, LICENCE_LINE_CM), RATIO: T1_RATIO_LINE}
TARGET_SOURCE = ("3 cm⁻¹ per family — decision 53's line for ring-ip, CH-oop and 'other', every family's under decision 65 (the licence) — "
                 "and the coupling ratio ≤ 0.25 of chain 35's T1 line (probes/chain35_read.py)")
HOLDOUTS = {"a": "hold-out (a): layer-A molecules held out on 19 Sep 2026 (benzene, phenanthrene, fluoranthene, benzonitrile, benzophenone, …), never trained",
            "b": "hold-out (b): every substituted molecule of two scaffold cores, frozen on 8 Oct 2026 — scaffolds the network never saw"}
CLEAN_SET = "a8"                       # probes/holdout_a_clean.sh's extra test set
CLEAN_A = ("hold-out (a) without its two trained twins (2-naphthoic acid and benzonitrile were trained on as layer-B molecules; TASKS 157): "
           "eight layer-A molecules held out on 19 Sep 2026, never trained on under any id")
HIGHER_LEVEL = "ωB97X/6-31G* (the DFT proxy: the network's ΔH is trained on ωB97X − B3LYP Hessians)"
FIRST_ORDER = "first_order"
PRODUCT = "product"
LICENCE_QUANTITY = PRODUCT             # README decision 65, amendment of 16 Nov 2026: the licence is read on what the product delivers
AMENDED = "16 Nov 2026"
QUANTITY_NAMES = {FIRST_ORDER: "first-order diagonal error of each seed's correction, averaged over the seeds",
                  PRODUCT: "error of the corrected band positions of the seed-mean correction"}
PRODUCT_SUFFIX = "_product_error.json"  # probes/product_error_read.py: <stem>_product_error.json beside the evaluation records
PRODUCT_COMMAND = "python tools/runspec.py launch probes/runspecs/product_error_read.json"
CC_NOTE = ("not measured for this network version: the coupled-cluster reads (T3) were made on chain 34, and tests on the 9–11 existing "
           "anchors wait for the anchor decision of November 2026")
DEFINITIONS = dict(
    family="the read-outs: rms over the family's B3LYP modes of the first-order diagonal error of a seed's ΔH against the higher level, per "
           "seed, and the seeds' mean (cm⁻¹); families by module 05's rule (m05/learning_curve_layerA.molecule_features)",
    product="rms over the family's bands of the corrected band position's error against the higher level (cm⁻¹): the seeds' mean ΔH added "
            "to the B3LYP Hessian and diagonalised, each corrected band paired to its higher-level band by mode overlap and counted in the "
            "family of its B3LYP partner — what the pipeline prints; with the 95 % interval of a bootstrap over whole molecules",
    coupling_ratio="rms of the predicted mode couplings' error over the rms of the couplings themselves; 0 = exact, 1 = no better than none",
    spectrum_overlap="cosine similarity of the two Lorentzian-broadened spectra (FWHM 10 cm⁻¹, 500–3500 cm⁻¹); 1 = identical shape",
    intensity_error="intensity-weighted rms of the relative height error per band, bands paired by the shape of the motion (eigenvector "
                    "overlap); 0 = identical heights")
APT_OPEN = "the APT itself is computed at the cheap level; its CC-minus-B3LYP difference (≈ 20 % on benzene) is not corrected by any rung yet"


class NoProductError(LookupError):
    """A network version has no product-error record: the quantity the licence reads is not measured for it."""


def _stem_seed(name: str) -> tuple[str, str]:
    """(stem, seed tag) of a rung-C model file name: …_model_n750_seed0.pt → (…, seed0)."""
    stem, sep, tail = name.partition("_model_")
    if not sep:
        raise ValueError(f"{name}: not a rung-C model file name (…_model_…)")
    return stem, tail.removesuffix(".pt").rsplit("_", 1)[-1]


def evaluation_records(models: tuple[str, ...]) -> list[Path]:
    """Each model's evaluation record: the `rungC_eval_saved.py` JSON beside it that names it (…_model_n750_seed0.pt → …_eval_*seed0.json).
    None or several is refused: the error stated is that of the files that ran."""
    out = []
    for name in models:
        stem, seed = _stem_seed(name)
        hits = [p for p in sorted(M05_OUT.glob(f"{stem}_eval_*{seed}.json")) if _model_of(p) == name]
        if len(hits) != 1:
            raise ValueError(f"{name}: {len(hits)} evaluation records in {M05_OUT} name it; exactly one is needed")
        out.append(hits[0])
    return out


def clean_a_records(models: tuple[str, ...]) -> list[Path] | None:
    """Each model's clean hold-out (a) read (`probes/holdout_a_clean.sh`: `<stem>_a8read_<seed>.json`), or None where no model has one;
    some models with one and some without is refused, since the error stated would mix two hold-outs."""
    hits = []
    for name in models:
        stem, seed = _stem_seed(name)
        hits.append([p for p in sorted(M05_OUT.glob(f"{stem}_a8read_{seed}.json")) if _model_of(p) == name])
    if not any(hits):
        return None
    if any(len(h) != 1 for h in hits):
        raise ValueError(f"clean hold-out (a) reads for some models only ({[len(h) for h in hits]}): one per model or none")
    return [h[0] for h in hits]


def _model_of(record: Path) -> str:
    with open(record, encoding="utf-8") as f:
        return Path(json.load(f)["model"]).name


def _records(paths: list[Path]) -> list[dict]:
    out = []
    for p in paths:
        with open(p, encoding="utf-8") as f:
            out.append(json.load(f))
    return out


def product_error_record(models: tuple[str, ...], sha16: dict[str, str] | None = None) -> Path:
    """The models' product-error record, `<stem>_product_error.json` beside their evaluation records. A version without one is refused
    with the command that makes it: its licence is not read on the first-order quantity instead. The record names the checkpoints it
    was read on by file name and by hash; a record read on other files of the same names is refused. `sha16` gives the hashes of the
    files that ran, per file name (a pipeline record's admission); without it the checkpoints beside the records are hashed where this
    machine has them, and where it has none (the model files are not in git) the names alone are compared."""
    stems = {_stem_seed(name)[0] for name in models}
    if len(stems) != 1:
        raise ValueError(f"the models are of {len(stems)} stems ({sorted(stems)}); a product-error record is one version's")
    path = M05_OUT / f"{stems.pop()}{PRODUCT_SUFFIX}"
    if not path.is_file():
        raise NoProductError(f"no product-error record {path.name} in {M05_OUT}: the licence is read on the {QUANTITY_NAMES[PRODUCT]} "
                             f"(README decision 65, amendment of {AMENDED}), which is not measured for {', '.join(models)}; make the "
                             f"record with `{PRODUCT_COMMAND}` (it reads the registry's carried models)")
    with open(path, encoding="utf-8") as f:
        rec = json.load(f)
    if sorted(rec["models"]) != sorted(models):
        raise ValueError(f"{path.name} was read on {rec['models']}, not on {list(models)}; make it again with `{PRODUCT_COMMAND}`")
    ran = {n: P.sha16(M05_OUT / n) for n in models if (M05_OUT / n).is_file()} if sha16 is None else sha16
    if not set(ran) <= set(models):
        raise ValueError(f"hashes given for {sorted(set(ran) - set(models))}, which are not among the models {list(models)}")
    differ = [f"{n} (record {rec['model_sha16'][n]}, file {h})" for n, h in sorted(ran.items()) if rec["model_sha16"][n] != h]
    if differ:
        raise ValueError(f"{path.name} was read on other files than these models, whose names it shares: sha16 differs for "
                         f"{'; '.join(differ)}; make it again with `{PRODUCT_COMMAND}`")
    return path


def _product_row(p: dict, family: str) -> dict:
    """One family's product error as reported: the rms, what it rests on — its bands, the hold-out's molecules and how many of them
    have such bands — the molecule-level bootstrap's 95 % interval and whether that interval reaches above the line. A value that is
    not a finite, non-negative number is refused: a negative rms would pass the line and a NaN bound would hide a crossing interval."""
    if p["rms"] is None:
        raise ValueError(f"the product-error record has no {family} band on a hold-out, so the family has no error there")
    values = [p["rms"], *p["interval"]]
    if len(values) != 3 or not all(isinstance(v, (int, float)) and math.isfinite(v) and v >= 0 for v in values):
        raise ValueError(f"the product-error record's {family} rms and interval must be three finite numbers ≥ 0, not {values}; "
                         f"make it again with `{PRODUCT_COMMAND}`")
    rms, interval = reported(p["rms"], family), [reported(x, family) for x in p["interval"]]
    return dict(rms=rms, n_modes=p["n_modes"], n_molecules=p["n_molecules"], n_molecules_with_modes=p["n_molecules_with_modes"],
                interval=interval,
                share_below_line=round(p["share_below_line"], 2), target=LICENCE_LINE_CM, within_target=rms <= LICENCE_LINE_CM,
                interval_crosses_line=interval[1] > LICENCE_LINE_CM)


def _product_rows(product: Path, sets: dict[str, tuple[str, int]]) -> dict[str, dict[str, dict]]:
    """Per hold-out and family the product's error (`_product_row`). The record must be read on the set of molecules the read-outs are
    (`sets`: per hold-out its key in the evaluation records and its number of molecules)."""
    with open(product, encoding="utf-8") as f:
        rec = json.load(f)
    out = {}
    for h, (key, n) in sets.items():
        entry = rec["holdouts"][h]
        if (entry["set"], entry["n_molecules"]) != (key, n):
            raise ValueError(f"{product.name}: hold-out ({h}) was read on '{entry['set']}' ({entry['n_molecules']} molecules), the "
                             f"evaluation records on '{key}' ({n}); make it again with `{PRODUCT_COMMAND}`")
        out[h] = {f: _product_row(entry["families"][f][PRODUCT], f) for f in FAMILIES}
    return out


def _readout_rows(arm: Arm, key: str) -> dict[str, dict]:
    rows = {}
    for q in QUANTITIES:
        mean = reported(arm.mean(key, q), q)
        rows[q] = dict(mean=mean, seeds=[reported(x, q) for x in arm.values[key][q]], target=TARGETS[q], within_target=mean <= TARGETS[q])
    return rows


def network_accuracy(records: list[Path], clean: list[Path] | None = None, product: Path | None = None) -> dict:
    """Per hold-out, each quantity under its own name. `readouts` is the first-order quantity of the evaluation records: each read-out's
    seed mean and seed values as reported, its target and whether the mean is within it. `product` is the error of what the product
    delivers, per family, from the product-error record (`product_error_record`); None without one, and then no licence can be read
    (`stated_errors`). With them the spectral shape (overlap and height error, uncorrected → corrected) over the molecules with an APT.
    With `clean` (`clean_a_records`), hold-out (a) is read on the molecules never trained on under any id. `quantities` names both and
    `licence_quantity` the one the licence reads."""
    sources = {h: (load_eval_arm(records), _records(records), h) for h in HOLDOUTS}
    if clean is not None:
        sources["a"] = (load_eval_arm(clean, holdouts=(CLEAN_SET, "b")), _records(clean), CLEAN_SET)
    holdouts = {}
    for h, description in HOLDOUTS.items():
        arm, recs, key = sources[h]
        holdouts[h] = dict(description=CLEAN_A if key == CLEAN_SET else description, n_molecules=len(recs[0][key]["per_molecule"]),
                           readouts=_readout_rows(arm, key), product=None, shape=shape_accuracy(recs, key))
    if product is not None:
        for h, rows in _product_rows(product, {h: (sources[h][2], holdouts[h]["n_molecules"]) for h in HOLDOUTS}).items():
            holdouts[h][PRODUCT] = rows
    return dict(higher_level=HIGHER_LEVEL, holdouts=holdouts, quantities={"readouts": QUANTITY_NAMES[FIRST_ORDER], PRODUCT: QUANTITY_NAMES[PRODUCT]},
                licence_quantity=LICENCE_QUANTITY, target_source=TARGET_SOURCE,
                sources=[p.name for p in records] + [p.name for p in clean or []] + ([product.name] if product is not None else []),
                definitions=DEFINITIONS, coupled_cluster=CC_NOTE)


def accuracy_of(models: tuple[str, ...], sha16: dict[str, str] | None = None) -> dict:
    """Both quantities for the named model files: their evaluation records, the clean hold-out (a) where they carry it, and their
    product-error record — without which the version is refused (`NoProductError`), never read on the first-order quantity alone.
    `sha16`: the hashes of the files that ran, which the record must have been read on (`product_error_record`)."""
    return network_accuracy(evaluation_records(models), clean_a_records(models), product_error_record(models, sha16))


def stated_errors(accuracy: dict) -> tuple[str, dict[str, dict[str, float]]]:
    """(the quantity, per family and hold-out its value) that this accuracy's licence and per-band errors are stated in: the product's
    where the accuracy carries it. An accuracy stored before the amendment of 16 Nov 2026 (a certificate file on disk) knows the
    first-order read-outs only, and those are returned under their own name. One made since then without a product-error record has
    no licence quantity and is refused."""
    holdouts = accuracy["holdouts"]
    if "licence_quantity" not in accuracy:
        return FIRST_ORDER, {f: {h: holdouts[h]["readouts"][f]["mean"] for h in HOLDOUTS} for f in FAMILIES}
    if any(holdouts[h][PRODUCT] is None for h in HOLDOUTS):
        raise NoProductError(f"this accuracy holds the first-order read-outs only; the licence is read on the {QUANTITY_NAMES[PRODUCT]} "
                             f"(README decision 65, amendment of {AMENDED}): give network_accuracy the product-error record "
                             f"(`{PRODUCT_COMMAND}` makes the carried version's)")
    return PRODUCT, {f: {h: holdouts[h][PRODUCT][f]["rms"] for h in HOLDOUTS} for f in FAMILIES}


def carried_version() -> str:
    status = P.MR.read_status(P.MR.STATUS_FILE)
    versions = {status[m.name]["version"] for m in P.carried_models()}
    if len(versions) != 1:
        raise RuntimeError(f"the carried ΔH-network files are of {len(versions)} versions: {sorted(versions)}")
    return versions.pop()


def carried_accuracy() -> dict:
    """The error of the carried version, both quantities: the evaluation records and the product-error record of the registry's carried
    ΔH-network files. A carried version without a product-error record raises `NoProductError` with the command that makes it."""
    names = tuple(m.name for m in P.carried_models())
    return accuracy_of(names) | {"version": carried_version()}
