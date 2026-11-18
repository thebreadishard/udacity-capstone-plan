"""The error of what the pipeline delivers, on the licence's hold-outs, beside the error the evaluation records hold (TASKS 243; README
decision 65, amendment of 16 Nov 2026). Second route to `probes/results_m1/aromir_product_error_2026-11-16/` (the public package's own
code), made with this repository's functions only.

The evaluation records hold, per family, each seed's first-order diagonal error in the B3LYP mode basis (the trainer's `diag_rms`);
`m08.accuracy` averages the seeds. The pipeline's step 4 (`m08.pipeline.correction`) takes the seeds' mean ΔH, adds it to the B3LYP
Hessian and diagonalises. For the carried ΔH-network files of the registry, on the hold-outs `m08.accuracy` reads — the clean hold-out
(a) where the records carry it, and the frozen hold-out (b); never (b+), whose molecules have no analytic labels (TASKS 244) — this
script measures, per family, in cm⁻¹:

  first order   each seed's first-order diagonal error and the seeds' mean, with the families the evaluation records used (the corpus
                loader's, kept by mode index when the analytic Hessians replace the finite-difference ones). It must reproduce the
                records' seed means to FIRST_ORDER_TOL, or the script stops without a record. Also given with the certificate's families.
                The two are one rule (`learning_curve_layerA.molecule_features`) on two B3LYP Hessians, finite-difference and analytic,
                so a mode near a threshold can fall in another family: each hold-out's `family_differences` names those modes.
  product       the error of the corrected band positions of the seed-mean ΔH: every band of H_B3LYP + ΔH paired to its ωB97X band by
                mode overlap (`rungC_intensities.match_modes`) and counted in the family of its B3LYP partner by the rule the live
                certificate marks bands with (`learning_curve_layerA.molecule_features` on the analytic B3LYP Hessian); with a
                bootstrap over whole molecules (the package's seed and draws, so the intervals compare).

With --package the product's error must agree with the package's record to PACKAGE_TOL per family and set, or the script stops. No
quantum chemistry is run: stored analytic Hessians and three checkpoints.

With --models and --records the read is of named checkpoints instead of the registry's carried ones — a version's licence numbers
before it is carried (design note of 26 Oct 2026, §14): one `rungC_eval_saved.py` record per checkpoint, in the same order, each
naming its checkpoint; hold-out (a) is the records' clean set (`a8`, as for the carried version: the licence is read on the eight)
and a record without it is refused; hold-out (b) is the records'. Such a read needs --out and its record says `candidate`. A
checkpoint may be named by a pattern (`…_model_n*_seed0.pt`) that matches exactly one file under --m05, as in a chain's steps.

    python probes/product_error_read.py [--m05 <a module-05 folder holding corpus/molecules and the checkpoints under out/>]
                                        [--out <record.json>] [--package <the package's product_error.json>] [--threads 2]
                                        [--models <checkpoints, relative to --m05> --records <their evaluation records, likewise>]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import torch

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "modules" / "08_industry_synthesis"))
from m08 import accuracy as A  # noqa: E402  module 08 puts module 05's code and probes/ on the path
from m08 import pipeline as P  # noqa: E402

# isort: split
import chain_runner  # noqa: E402
import network_kind as NK  # noqa: E402
import rungC_intensities as RINT  # noqa: E402
from learning_curve_layerA import molecule_features, normal_modes  # noqa: E402
from promotion_read import FAMILIES, load_eval_arm  # noqa: E402

LABELS = ("hessian_b3lyp_analytic.npz", "hessian_wb97x_analytic.npz")
FIRST_ORDER_TOL = 0.005        # cm⁻¹: this read against the evaluation records' seed means
PACKAGE_TOL = 0.01             # cm⁻¹: this read against the package's record, per family and set
BOOTSTRAP_SEED = 20261116      # the package's (product_error.py), so the two intervals are the same draws
BOOTSTRAP_DRAWS = 4000
CANDIDATE = "candidate (read with --models; not a carried version)"
DEFINITIONS = {
    "first_order": "rms over the family's B3LYP modes of the first-order diagonal error of a seed's ΔH against the ωB97X − B3LYP "
                   "Hessian difference, per seed; 'seed_mean' is the mean of the seeds' values (the evaluation records' diag_rms, "
                   "which m08.accuracy averages)",
    "product": "rms over the family's bands of the corrected band position's error: H_B3LYP + the seeds' mean ΔH diagonalised, each "
               "band paired to its ωB97X band by mode overlap and counted in the family of its B3LYP partner (what the pipeline prints)",
    "record_families": "the evaluation records' families: the corpus loader's (finite-difference B3LYP modes), kept by mode index "
                       "when the analytic Hessians replace them (e7_rungB_reread_analytic.substitute)",
    "certificate_families": "the live certificate's families: learning_curve_layerA.molecule_features on the analytic B3LYP Hessian",
    "family_differences": "per hold-out, the B3LYP modes whose record family and certificate family differ — one rule on the "
                          "finite-difference and on the analytic Hessian, a mode near a threshold falling either side — by molecule, mode "
                          "index and analytic frequency; they are why a family's first_order and first_order_certificate_families (and "
                          "the product) can count different modes. The evaluation records keep the loader's families (the trainer's), "
                          "the live certificate has only the analytic Hessian",
    "interval": "2.5th and 97.5th percentile of the set's rms under resampling of whole molecules; a statement about this hold-out's "
                "molecules as a sample",
    "label_sha16": "per hold-out and molecule, the sha16 of the two label files that were read; stored so that a later reader can tell "
                   "whether the corpus still holds these labels — not compared when the record is read (the corpus is not in git)",
    "run": "this run on file: its start and end (local time), seconds and peak memory (this process; Windows: peak working set)",
}


@dataclass(frozen=True)
class Config:
    """Where the read finds its inputs and writes its record."""

    m05: Path                  # corpus/molecules and out/<checkpoints> are read under it
    out: Path | None           # None: <this checkout's module-05 out>/<carried stem>_product_error.json
    package: Path | None
    threads: int
    models: tuple[Path, ...] = ()     # empty: the registry's carried checkpoints
    records: tuple[Path, ...] = ()    # the evaluation record of each of `models`, in their order

    def __post_init__(self) -> None:
        if not (self.m05 / "corpus" / "molecules").is_dir():
            raise SystemExit(f"--m05 {self.m05}: no corpus/molecules under it")
        if len(self.models) != len(self.records):
            raise SystemExit(f"--models ({len(self.models)}) and --records ({len(self.records)}) go together: one evaluation record per "
                             "checkpoint, in the same order")
        if self.models and self.out is None:
            raise SystemExit("--models needs --out: a read of checkpoints that are not carried does not take a default record name")
        missing = [str(p) for p in (*self.models, *self.records) if not p.is_file()]
        if missing:
            raise SystemExit(f"--models/--records: no such file: {', '.join(missing)}")
        if self.package is not None and not self.package.is_file():
            raise SystemExit(f"--package {self.package}: no such file")
        if not 1 <= self.threads <= 8:
            raise SystemExit(f"--threads {self.threads}: 1 to 8 (the read runs beside other jobs)")


@dataclass(frozen=True)
class MoleculeRead:
    """One molecule's errors, cm⁻¹: per B3LYP mode the two family labels and each seed's first-order error; per corrected band of the
    seed-mean ΔH its B3LYP partner's family and its distance from its ωB97X partner."""

    record_family: np.ndarray
    family: np.ndarray
    first_order: np.ndarray    # (seeds, modes)
    band_family: np.ndarray
    band: np.ndarray
    freq: np.ndarray           # the analytic B3LYP frequencies, cm⁻¹, the modes' order of the two family labels


def label_hessians(folder: Path) -> tuple[np.ndarray, np.ndarray]:
    """The molecule's analytic B3LYP and ωB97X Hessians (projected, Cartesian); a folder without both is refused."""
    out = []
    for name in LABELS:
        if not (folder / name).is_file():
            raise SystemExit(f"{folder.name}: no {name}; the read is on analytic labels only")
        with np.load(folder / name) as z:
            out.append(np.array(z["H_projected"], float))
    return out[0], out[1]


def molecule_read(folder: Path, models: tuple[Path, ...]) -> MoleculeRead:
    lo, hi = label_hessians(folder)
    masses = np.asarray(json.loads((folder / "geometry.json").read_text(encoding="utf-8"))["masses_amu"], float)
    truth = molecule_features(folder, lo=lo, hi=hi)                    # the certificate's families and the true first-order shift
    record_family = np.array(molecule_features(folder)["family"])      # the loader's families, on the stored finite-difference Hessians
    family = np.array(truth["family"])
    if len(record_family) != len(family):
        raise SystemExit(f"{folder.name}: {len(record_family)} finite-difference modes, {len(family)} analytic ones")
    dH, dH_seeds = P.correction(models, folder)
    first = np.array([molecule_features(folder, lo=lo, hi=lo + d)["target"] - truth["target"] for d in dH_seeds], float)
    _, w_low, V_low, _ = normal_modes(lo, masses)
    _, w_ref, V_ref, _ = normal_modes(hi, masses)
    _, w_net, V_net, _ = normal_modes(lo + dH, masses)
    if np.abs(w_low - np.asarray(truth["freq"])).max() > 1e-6:
        raise SystemExit(f"{folder.name}: the family rule's modes are not the B3LYP normal modes")
    band = w_net - w_ref[RINT.match_modes(V_net, V_ref)]
    return MoleculeRead(record_family, family, first, family[RINT.match_modes(V_net, V_low)], band, np.asarray(truth["freq"], float))


def peak_memory_gb() -> float:
    """This process's peak resident memory, GB: the peak working set on Windows, the kernel's max RSS (kB on Linux) elsewhere."""
    if sys.platform == "win32":
        import psutil
        return psutil.Process().memory_info().peak_wset / 2 ** 30
    import resource
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 2 ** 20


def rms(parts: list[np.ndarray]) -> float | None:
    values = np.concatenate(parts) if parts else np.array([])
    return float(np.sqrt(np.mean(values ** 2))) if values.size else None


def bootstrap(per_molecule: list[np.ndarray], line: float) -> dict:
    """The set's rms under resampling of whole molecules (the modes of one molecule are not independent): the interval's two ends, the
    share of draws under the licence line and the largest single molecule's rms. Seeded, in the molecules' order of the records."""
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    sums = np.array([float(np.sum(e ** 2)) for e in per_molecule])
    counts = np.array([len(e) for e in per_molecule], float)
    picks = rng.integers(0, len(sums), size=(BOOTSTRAP_DRAWS, len(sums)))
    drawn = np.sqrt(sums[picks].sum(axis=1) / np.maximum(counts[picks].sum(axis=1), 1.0))
    return {"interval": [float(np.percentile(drawn, 2.5)), float(np.percentile(drawn, 97.5))],
            "share_below_line": float(np.mean(drawn < line)),
            "largest_single_molecule_rms": float(np.sqrt(np.max(sums / np.maximum(counts, 1.0))))}


def first_order_summary(reads: list[MoleculeRead], picks: list[np.ndarray]) -> dict:
    """A family's first-order error per seed and the seeds' mean; `picks` marks the family's modes in each molecule."""
    seeds = [rms([r.first_order[s][p] for r, p in zip(reads, picks, strict=True)]) for s in range(reads[0].first_order.shape[0])]
    return {"seeds": seeds, "seed_mean": None if None in seeds else float(np.mean(seeds)), "n_modes": int(sum(p.sum() for p in picks))}


def family_summary(reads: list[MoleculeRead], fam: str) -> dict:
    bands = [r.band[r.band_family == fam] for r in reads]
    product = {"rms": rms(bands), "n_modes": int(sum(len(b) for b in bands)), "n_molecules": len(reads),
               "n_molecules_with_modes": int(sum(len(b) > 0 for b in bands)), **bootstrap(bands, A.LICENCE_LINE_CM)}
    return {"first_order": first_order_summary(reads, [r.record_family == fam for r in reads]),
            "first_order_certificate_families": first_order_summary(reads, [r.family == fam for r in reads]), "product": product}


def family_differences(ids: list[str], reads: list[MoleculeRead]) -> dict:
    """The modes of these molecules whose record family and certificate family differ, with their count."""
    modes = [{"molecule": i, "mode": int(k), "freq_cm": float(r.freq[k]), "record_family": str(r.record_family[k]),
              "certificate_family": str(r.family[k])}
             for i, r in zip(ids, reads, strict=True) for k in np.flatnonzero(r.record_family != r.family)]
    return {"n_modes": len(modes), "modes": modes}


def holdout_sets(records: list[Path], clean: list[Path] | None) -> tuple[dict[str, tuple[str, list[str]]], dict[str, dict[str, float]],
                                                                         list[str]]:
    """(per licence hold-out its key in the records and its molecules; the records' seed-mean first-order error per hold-out and
    family, unrounded; the records' names) — from the models' evaluation records and, where they have them, their clean hold-out (a)
    reads: the sets and records `m08.accuracy.network_accuracy` reads for the carried models."""
    sources = {h: (records, h) for h in A.HOLDOUTS}
    if clean is not None:
        sources["a"] = (clean, A.CLEAN_SET)
    sets, recorded = {}, {}
    for h, (paths, key) in sources.items():
        ids = [list(json.loads(p.read_text(encoding="utf-8"))[key]["per_molecule"]) for p in paths]
        if any(i != ids[0] for i in ids):
            raise SystemExit(f"hold-out ({h}): the seeds' records list different molecules under '{key}'")
        arm = load_eval_arm(paths, holdouts=(key,))
        sets[h], recorded[h] = (key, ids[0]), {f: arm.mean(key, f) for f in FAMILIES}
    return sets, recorded, list(dict.fromkeys(p.name for p in (*records, *(clean or []))))


def table(title: str, rows: dict[str, dict[str, float]]) -> list[str]:
    lines = [f"{title:<58}" + "".join(f"{f:>12}" for f in FAMILIES)]
    return lines + [f"  {name:<56}" + "".join(f"{v[f]:>12.3f}" for f in FAMILIES) for name, v in rows.items()]


def check_first_order(holdouts: dict, recorded: dict[str, dict[str, float]]) -> dict:
    """This read's seed-mean first-order error against the evaluation records', per hold-out and family; stops past FIRST_ORDER_TOL."""
    cells, lines = {}, []
    for h, entry in holdouts.items():
        here = {f: entry["families"][f]["first_order"]["seed_mean"] for f in FAMILIES}
        cells[h] = {f: {"here": here[f], "evaluation_records": recorded[h][f], "difference": here[f] - recorded[h][f]} for f in FAMILIES}
        lines += table(f"first order, hold-out ({h}), seed means", {"this read": here, "evaluation records": recorded[h]})
    print("\n".join(lines), flush=True)
    worst = max(abs(c["difference"]) for row in cells.values() for c in row.values())
    if worst > FIRST_ORDER_TOL:
        raise SystemExit(f"STOP: the first-order error differs from the evaluation records by {worst:.4f} cm⁻¹ (> {FIRST_ORDER_TOL}); "
                         "no record written")
    return {"tolerance_cm": FIRST_ORDER_TOL, "largest_difference_cm": worst, "cells": cells}


def check_package(holdouts: dict, package: Path) -> dict:
    """This read against the package's record (its corpus atom order, which is this read's): the product's error and, under the
    certificate's families, the first-order seed mean; stops past PACKAGE_TOL in any cell."""
    theirs = json.loads(package.read_text(encoding="utf-8"))["sets"]
    cells, lines = {}, []
    for h, entry in holdouts.items():
        if entry["set"] not in theirs:
            raise SystemExit(f"--package {package.name}: no set '{entry['set']}' (it has {sorted(theirs)})")
        if theirs[entry["set"]]["ids"] != entry["ids"]:
            raise SystemExit(f"--package {package.name}: its set '{entry['set']}' lists other molecules than the evaluation records")
        t, fams = theirs[entry["set"]]["corpus"], entry["families"]
        rows = {"product": ({f: fams[f]["product"]["rms"] for f in FAMILIES}, {f: t["mean"][f]["band"] for f in FAMILIES}),
                "first_order_certificate_families": ({f: fams[f]["first_order_certificate_families"]["seed_mean"] for f in FAMILIES},
                                                     t["printed_quantity"])}
        cells[h] = {q: {f: {"here": here[f], "package": pack[f], "difference": here[f] - pack[f]} for f in FAMILIES}
                    for q, (here, pack) in rows.items()}
        cells[h]["product_interval"] = {f: {"here": fams[f]["product"]["interval"],
                                            "package": [t["mean_band_bootstrap"][f]["p2.5"], t["mean_band_bootstrap"][f]["p97.5"]]}
                                        for f in FAMILIES}
        for q, (here, pack) in rows.items():
            lines += table(f"{q}, hold-out ({h}, '{entry['set']}')", {"this read": here, "the package": pack})
    print("\n".join(lines), flush=True)
    worst = max(abs(c["difference"]) for row in cells.values() for q in ("product", "first_order_certificate_families") for c in row[q].values())
    if worst > PACKAGE_TOL:
        raise SystemExit(f"STOP: this read differs from the package's record by {worst:.4f} cm⁻¹ (> {PACKAGE_TOL}); no record written")
    return {"source": package.relative_to(PLAN).as_posix() if package.is_relative_to(PLAN) else package.name, "tolerance_cm": PACKAGE_TOL,
            "largest_difference_cm": worst, "cells": cells}


def read_holdouts(cfg: Config, models: tuple[Path, ...], sets: dict[str, tuple[str, list[str]]]) -> dict:
    """Every hold-out molecule read once, then per hold-out and family the summary."""
    total, done, out = sum(len(ids) for _, ids in sets.values()), 0, {}
    for h, (key, ids) in sets.items():
        reads, hashes = [], {}
        for i in ids:
            folder = cfg.m05 / "corpus" / "molecules" / i
            reads.append(molecule_read(folder, models))
            hashes[i] = {name: P.sha16(folder / name) for name in LABELS}
            done += 1
            print(f"product-error {done}/{total} ({h}) {i}", flush=True)
        out[h] = {"set": key, "n_molecules": len(ids), "ids": ids, "families": {f: family_summary(reads, f) for f in FAMILIES},
                  "family_differences": family_differences(ids, reads), "label_sha16": hashes}
    return out


def carried(m05: Path) -> tuple[tuple[Path, ...], str]:
    """(the registry's carried ΔH-network checkpoints as files under `m05`/out, the stem their records share)."""
    listed = P.carried_models(NK.MEASUREMENT)
    if not listed:
        raise SystemExit(f"the registry lists no carried {P.NETWORK} checkpoint")
    models = tuple(m05 / "out" / m.relative_to(P.MR.OUT) for m in listed)
    missing = [m.name for m in models if not m.is_file()]
    if missing:
        raise SystemExit(f"not under {m05 / 'out'}: {', '.join(missing)} (--m05 names the folder that holds the checkpoints)")
    return models, common_stem(models)


def model_keys(models: tuple[Path, ...], m05: Path) -> tuple[str, ...]:
    """The checkpoints' keys under `m05`/out, by which `m08.accuracy` finds their records beside them."""
    return tuple(m.relative_to(m05 / A.OUT_DIR).as_posix() for m in models)


def common_stem(models: tuple[Path, ...]) -> str:
    """The stem the checkpoints' records share (`<stem>_model_n<N>_seed<S>.pt`); checkpoints of several stems are not one version."""
    stems = {m.name.partition("_model_")[0] for m in models}
    if len(stems) != 1:
        raise SystemExit(f"the checkpoints are of {len(stems)} stems: {sorted(stems)}")
    return stems.pop()


@dataclass(frozen=True)
class Inputs:
    """What a read is made on: the checkpoints, their stem, their evaluation records, their clean hold-out (a) reads if any, and the
    version the record states."""

    models: tuple[Path, ...]
    stem: str
    records: list[Path]
    clean: list[Path] | None
    version: str


def inputs(cfg: Config) -> Inputs:
    """The registry's carried checkpoints with the records `m08.accuracy` finds for them, or --models with --records after each
    record is seen to name the checkpoint of its place and to hold the clean hold-out (a), which is then read from those records."""
    if not cfg.models:
        models, stem = carried(cfg.m05)
        keys = model_keys(models, cfg.m05)
        return Inputs(models, stem, A.evaluation_records(keys), A.clean_a_records(keys), A.carried_version())
    for model, record in zip(cfg.models, cfg.records, strict=True):
        evaluated = Path(str(json.loads(record.read_text(encoding="utf-8")).get("model", ""))).name
        if evaluated != model.name:
            raise SystemExit(f"--records: {record.name} evaluated {evaluated or 'no named model'}, not {model.name}")
        if A.CLEAN_SET not in json.loads(record.read_text(encoding="utf-8")):
            raise SystemExit(f"--records: {record.name} holds no set '{A.CLEAN_SET}' (hold-out (a) without its two trained twins): the "
                             f"licence is read on it; evaluate with --eval-ids-file {A.CLEAN_SET}=<the clean list>")
    return Inputs(cfg.models, common_stem(cfg.models), list(cfg.records), list(cfg.records), CANDIDATE)


def write_record(path: Path, record: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(record, indent=1, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, path)


def parse(argv: list[str] | None) -> Config:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--m05", type=Path, default=P.M05, help="the module-05 folder whose corpus/molecules and out/<checkpoints> are read")
    ap.add_argument("--out", type=Path, default=None, help=f"the record (default: <carried stem>{A.PRODUCT_SUFFIX} in the carried checkpoints' own folder "
                    "under this checkout's module-05 out/, beside their evaluation records)")
    ap.add_argument("--package", type=Path, default=None, help="the package's product_error.json: this read must agree with it")
    ap.add_argument("--threads", type=int, default=2)
    ap.add_argument("--models", type=Path, nargs="+", default=[], help="checkpoints to read instead of the registry's carried ones "
                    "(relative to --m05); with --records and --out")
    ap.add_argument("--records", type=Path, nargs="+", default=[], help="the rungC_eval_saved.py record of each of --models, in their order")
    a = ap.parse_args(argv)
    m05 = a.m05.resolve()
    try:                                # the chain runner's own expansion of a checkpoint pattern: exactly one file, or refused
        models = chain_runner._resolve([p.as_posix() for p in a.models], m05)
    except RuntimeError as e:
        raise SystemExit(f"--models: {e}") from None
    return Config(m05=m05, out=a.out.resolve() if a.out else None, package=a.package.resolve() if a.package else None,
                  threads=a.threads, models=tuple((m05 / p).resolve() for p in models), records=tuple((m05 / p).resolve() for p in a.records))


def main(argv: list[str] | None = None) -> int:
    cfg = parse(argv)
    started = time.time()
    torch.set_num_threads(cfg.threads)
    read = inputs(cfg)
    models, names = read.models, tuple(m.name for m in read.models)
    P.MR.require_measurement(models, "its product error on the hold-outs")   # decision 66, before any molecule is read
    out = cfg.out or A.product_error_path(model_keys(models, cfg.m05))
    sets, recorded, sources = holdout_sets(read.records, read.clean)
    holdouts = read_holdouts(cfg, models, sets)
    checks = {"first_order_reproduces_evaluation_records": check_first_order(holdouts, recorded)}
    if cfg.package is not None:
        checks["agrees_with_package"] = check_package(holdouts, cfg.package)
    record = {"kind": "product error read", "network": P.NETWORK, "network_version": read.version, NK.FIELD: NK.MEASUREMENT,
              "models": list(names),
              "model_sha16": {m.name: P.sha16(m) for m in models}, "labels": {"kind": "analytic", "files": list(LABELS)},
              "sets_from": sources, "line_cm": A.LICENCE_LINE_CM, "definitions": DEFINITIONS,
              "bootstrap": {"seed": BOOTSTRAP_SEED, "draws": BOOTSTRAP_DRAWS, "unit": "molecule"}, "holdouts": holdouts, "checks": checks,
              "data_root": str(cfg.m05), "provenance": P.provenance(),
              "run": {"started": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(started)), "ended": time.strftime("%Y-%m-%d %H:%M:%S"),
                      "seconds": round(time.time() - started, 1), "peak_memory_gb": round(peak_memory_gb(), 2), "threads": cfg.threads}}
    write_record(out, record)
    print(f"product error read: {sum(v['n_molecules'] for v in holdouts.values())} molecules, record {out}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
