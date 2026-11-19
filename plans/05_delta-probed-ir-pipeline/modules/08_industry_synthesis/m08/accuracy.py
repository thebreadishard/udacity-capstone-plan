"""The measured error of a ΔH-network version, under two named quantities. The first-order read-outs come from its own evaluation
records (`probes/rungC_eval_saved.py`, one JSON per seed): per mode family and hold-out against the 3 cm⁻¹ line, the coupling ratio, and
the spectral shape. The error of what the product delivers — the corrected band positions of the seed-mean correction — comes from its
product-error record (`probes/product_error_read.py`); the licence reads that one since 16 Nov 2026 (README decision 65, dated
amendment). One implementation for the licence, the live certificate and the export certificate."""
from __future__ import annotations

import json
import math
from pathlib import Path, PurePath, PurePosixPath, PureWindowsPath

from . import pipeline as P
from .spectrum import shape_accuracy

# isort: split
# probes/, on the path through m08.pipeline
import network_kind as NK
from chain35_read import T1_FAMILY_LINE, T1_RATIO_LINE
from promotion_read import FAMILIES, QUANTITIES, RATIO, Arm, load_eval_arm, reported
from rungC_settings_added import SETTINGS_ADDED  # module 05's code, on the path through m08.pipeline

OUT_DIR = "out"                        # module 05's checkpoint folder; a model's key is its path under it (the registry's keys)
M05_OUT = P.M05 / OUT_DIR
LICENCE_LINE_CM = T1_FAMILY_LINE        # decision 53's 3 cm⁻¹, every family's line under decision 65
TARGETS = {**dict.fromkeys(FAMILIES, LICENCE_LINE_CM), RATIO: T1_RATIO_LINE}
TARGET_SOURCE = ("3 cm⁻¹ per family — decision 53's line for ring-ip, CH-oop and 'other', every family's under decision 65 (the licence) — "
                 "and the coupling ratio ≤ 0.25 of chain 35's T1 line (probes/chain35_read.py)")
HOLDOUTS = {"a": "hold-out (a): layer-A molecules held out on 19 Sep 2026 (benzene, phenanthrene, fluoranthene, benzonitrile, benzophenone, …), never trained",
            "b": "hold-out (b): every substituted molecule of two scaffold cores, frozen on 8 Oct 2026 — scaffolds the measurement networks "
                 "never saw"}
CLEAN_SET = "a8"                       # probes/holdout_a_clean.sh's extra test set
TWINS_KEPT = "keep"                    # rungC_train --holdout-twins: the hold-out molecules' twins stayed in the training pool
CLEAN_A = ("hold-out (a) on its eight molecules never trained on in any version (the set fixed on 30 Oct 2026): eight layer-A molecules "
           "held out on 19 Sep 2026; this version trained on the other two, 2-naphthoic acid and benzonitrile, under layer-B ids")
CLEAN_A_TWINS_DROPPED = ("hold-out (a) on its eight molecules never trained on in any version (the set fixed on 30 Oct 2026): eight "
                         "layer-A molecules held out on 19 Sep 2026; this version's training left out the twins of the hold-out "
                         "molecules, so the other two, 2-naphthoic acid and benzonitrile, are clean too, and the eight are kept for "
                         "comparability with v1.3")
HIGHER_LEVEL_NAME = "ωB97X/6-31G*"    # the level the ΔH network predicts and is licensed against, by name
HIGHER_LEVEL = f"{HIGHER_LEVEL_NAME} (the DFT proxy: the network's ΔH is trained on ωB97X − B3LYP Hessians)"
FIRST_ORDER = "first_order"
PRODUCT = "product"
LICENCE_QUANTITY = PRODUCT             # README decision 65, amendment of 16 Nov 2026: the licence is read on what the product delivers
AMENDED = "16 Nov 2026"
QUANTITY_NAMES = {FIRST_ORDER: "first-order diagonal error of each seed's correction, averaged over the seeds",
                  PRODUCT: "error of the corrected band positions of the seed-mean correction"}
PRODUCT_SUFFIX = "_product_error.json"  # probes/product_error_read.py: <stem>_product_error.json beside the evaluation records
PRODUCT_COMMAND = "python tools/runspec.py launch probes/runspecs/product_error_read.json"
CC_NOTE = "not measured for this network version: the coupled-cluster reads (T3) were made on an earlier network (chain 34)"
DEFINITIONS = dict(
    family="rms over the family's B3LYP modes of the first-order diagonal error of a seed's ΔH against the higher level, per "
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


def model_key(path: str | PurePath) -> str:
    """A checkpoint's key under module 05's out/ — the registry's (`v14/…_model_n1082_seed0.pt`; the file name for one directly in out/)
    — from its path as any machine wrote it: what follows the last `05_support_predictor/out` in the path, or the leading `out/` of a
    path relative to module 05. Any other path is refused: its records could not be found."""
    parts = PureWindowsPath(str(path)).parts    # splits on both separators: an admission written on Windows reads alike on Linux
    anchor = (P.M05.name, OUT_DIR)
    starts = [i + 2 for i in range(len(parts) - 1) if parts[i:i + 2] == anchor] or ([1] if parts[:1] == (OUT_DIR,) else [])
    if not starts or starts[-1] >= len(parts):
        raise ValueError(f"{path}: not a checkpoint under module 05's {OUT_DIR}/ ({M05_OUT}), so its records cannot be found")
    return "/".join(parts[starts[-1]:])


def _folder(key: str) -> Path:
    """The folder of the model with this key, where its records lie beside it."""
    return M05_OUT / PurePosixPath(key).parent


def _name(key: str) -> str:
    return PurePosixPath(key).name


def evaluation_records(models: tuple[str, ...]) -> list[Path]:
    """Each model's evaluation record: the `rungC_eval_saved.py` JSON beside it that names it (…_model_n750_seed0.pt → …_eval_*seed0.json).
    `models` are keys under module 05's out/ (`model_key`). None or several is refused: the error stated is that of the files that ran."""
    out = []
    for key in models:
        name, folder = _name(key), _folder(key)
        stem, seed = _stem_seed(name)
        hits = [p for p in sorted(folder.glob(f"{stem}_eval_*{seed}.json")) if _model_of(p) == name]
        if len(hits) != 1:
            raise ValueError(f"{key}: {len(hits)} evaluation records in {folder} name it; exactly one is needed")
        out.append(hits[0])
    return out


def clean_a_records(models: tuple[str, ...]) -> list[Path] | None:
    """Each model's clean hold-out (a) read (`probes/holdout_a_clean.sh`: `<stem>_a8read_<seed>.json`), or None where no model has one;
    some models with one and some without is refused, since the error stated would mix two hold-outs."""
    hits = []
    for key in models:
        name = _name(key)
        stem, seed = _stem_seed(name)
        hits.append([p for p in sorted(_folder(key).glob(f"{stem}_a8read_{seed}.json")) if _model_of(p) == name])
    if not any(hits):
        return None
    if any(len(h) != 1 for h in hits):
        raise ValueError(f"clean hold-out (a) reads for some models only ({[len(h) for h in hits]}): one per model or none")
    return [h[0] for h in hits]


def _model_of(record: Path) -> str:
    with open(record, encoding="utf-8") as f:
        return Path(json.load(f)["model"]).name


def holdout_twins_setting(record: Path) -> str:
    """The --holdout-twins setting of the training an evaluation record's model comes from, read from that training's record
    (`<stem>.json` beside it); a training recorded before the setting existed kept the twins (`SETTINGS_ADDED`). A missing training
    record is refused: the description would be a guess."""
    stem, _ = _stem_seed(_model_of(record))
    training = record.parent / f"{stem}.json"
    if not training.is_file():
        raise FileNotFoundError(f"{record.name}: no training record {training.name} beside it, so whether its training kept the "
                                "hold-out twins cannot be read")
    with open(training, encoding="utf-8") as f:
        return json.load(f).get("holdout_twins", SETTINGS_ADDED["holdout_twins"])


def clean_a_description(clean: list[Path]) -> str:
    """Hold-out (a)'s description on its eight clean molecules, true for the version the records are of: whether its training kept
    the twins of the other two."""
    settings = {holdout_twins_setting(p) for p in clean}
    if len(settings) != 1:
        raise ValueError(f"the clean hold-out (a) reads come from trainings of {len(settings)} twin settings ({sorted(settings)}); one version has one")
    return CLEAN_A if settings.pop() == TWINS_KEPT else CLEAN_A_TWINS_DROPPED


def _records(paths: list[Path]) -> list[dict]:
    """The evaluation records; one of a release network (decision 66) is refused — it holds no hold-out error."""
    out = []
    for p in paths:
        with open(p, encoding="utf-8") as f:
            out.append(json.load(f))
        NK.refuse_release(NK.stated_kind(out[-1], p.name), p.name, "its read-outs on the hold-outs")
    return out


def version_record_path(models: tuple[str, ...], suffix: str) -> Path:
    """Where a record of the models' version lies: `<stem><suffix>` in their folder, beside their evaluation records. Models of several
    stems or folders are refused: such a record is one version's."""
    stems = {_stem_seed(_name(key))[0] for key in models}
    if len(stems) != 1:
        raise ValueError(f"the models are of {len(stems)} stems ({sorted(stems)}); a record beside them is one version's")
    folders = {_folder(key) for key in models}
    if len(folders) != 1:
        raise ValueError(f"the models lie in {len(folders)} folders ({sorted(map(str, folders))}); a record beside them is one version's")
    return folders.pop() / f"{stems.pop()}{suffix}"


def product_error_path(models: tuple[str, ...]) -> Path:
    """Where the models' product-error record lies: `<stem>_product_error.json` beside their evaluation records."""
    return version_record_path(models, PRODUCT_SUFFIX)


def product_error_record(models: tuple[str, ...], sha16: dict[str, str] | None = None) -> Path:
    """The models' product-error record, `<stem>_product_error.json` beside their evaluation records. A version without one is refused
    with the command that makes it: its licence is not read on the first-order quantity instead. The record names the checkpoints it
    was read on by file name and by hash; a record read on other files of the same names is refused. `sha16` gives the hashes of the
    files that ran, per file name (a pipeline record's admission), one for each model and no other — a missing hash would leave that
    file unchecked; without it the checkpoints beside the records are hashed where this machine has them, and where it has none (the
    model files are not in git) the names alone are compared. `models` are keys under module 05's out/ (`model_key`); the record names
    the files by file name."""
    path = product_error_path(models)
    names = tuple(_name(key) for key in models)
    if not path.is_file():
        raise NoProductError(f"no product-error record {path.name} in {path.parent}: the licence is read on the {QUANTITY_NAMES[PRODUCT]} "
                             f"(README decision 65, amendment of {AMENDED}), which is not measured for {', '.join(names)}; make the "
                             f"record with `{PRODUCT_COMMAND}` (it reads the registry's carried models)")
    with open(path, encoding="utf-8") as f:
        rec = json.load(f)
    NK.refuse_release(NK.stated_kind(rec, path.name), path.name, "its product error on the hold-outs")
    if sorted(rec["models"]) != sorted(names):
        raise ValueError(f"{path.name} was read on {rec['models']}, not on {list(names)}; make it again with `{PRODUCT_COMMAND}`")
    ran = {_name(k): P.sha16(M05_OUT / k) for k in models if (M05_OUT / k).is_file()} if sha16 is None else sha16
    if sha16 is not None and set(sha16) != set(names):
        raise ValueError(f"the hashes given must name exactly the models {list(names)}: missing for {sorted(set(names) - set(sha16))}, "
                         f"given for {sorted(set(sha16) - set(names))}, which are not among them")
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
    With `clean` (`clean_a_records`), hold-out (a) is read on the eight molecules never trained on in any version, described as the
    version's training record says (`clean_a_description`). `quantities` names both and `licence_quantity` the one the licence reads."""
    sources = {h: (load_eval_arm(records), _records(records), h) for h in HOLDOUTS}
    descriptions = dict(HOLDOUTS)
    if clean is not None:
        sources["a"] = (load_eval_arm(clean, holdouts=(CLEAN_SET, "b")), _records(clean), CLEAN_SET)
        descriptions["a"] = clean_a_description(clean)
    holdouts = {}
    for h, description in descriptions.items():
        arm, recs, key = sources[h]
        holdouts[h] = dict(description=description, n_molecules=len(recs[0][key]["per_molecule"]),
                           readouts=_readout_rows(arm, key), product=None, shape=shape_accuracy(recs, key))
    if product is not None:
        for h, rows in _product_rows(product, {h: (sources[h][2], holdouts[h]["n_molecules"]) for h in HOLDOUTS}).items():
            holdouts[h][PRODUCT] = rows
    return dict(higher_level=HIGHER_LEVEL, holdouts=holdouts, quantities={"readouts": QUANTITY_NAMES[FIRST_ORDER], PRODUCT: QUANTITY_NAMES[PRODUCT]},
                licence_quantity=LICENCE_QUANTITY, target_source=TARGET_SOURCE,
                sources=[p.name for p in records] + [p.name for p in clean or []] + ([product.name] if product is not None else []),
                definitions=DEFINITIONS, coupled_cluster=CC_NOTE)


def accuracy_of(models: tuple[str, ...], sha16: dict[str, str] | None = None) -> dict:
    """Both quantities for the model files of these keys (`model_key`): their evaluation records, the clean hold-out (a) where they carry it, and their
    product-error record — without which the version is refused (`NoProductError`), never read on the first-order quantity alone.
    `sha16`: the hashes of the files that ran by file name, which the record must have been read on (`product_error_record`)."""
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
    versions = {status[P.MR.checkpoint_key(m, P.MR.OUT)]["version"] for m in P.carried_models(NK.MEASUREMENT)}
    if len(versions) != 1:
        raise RuntimeError(f"the carried ΔH-network files are of {len(versions)} versions: {sorted(versions)}")
    return versions.pop()


def carried_accuracy() -> dict:
    """The error of the carried version, both quantities: the evaluation records and the product-error record of the registry's carried
    measurement networks (decision 66: an error is never read on the release networks). A carried version without a product-error
    record raises `NoProductError` with the command that makes it."""
    keys = tuple(P.MR.checkpoint_key(m, P.MR.OUT) for m in P.carried_models(NK.MEASUREMENT))
    return accuracy_of(keys) | {"version": carried_version()}
