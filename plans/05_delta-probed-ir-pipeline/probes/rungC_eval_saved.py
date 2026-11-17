"""Read a saved rung-C hybrid model (`rungC_train.py --save-model`) on the hold-outs without retraining — the registered read-outs, the per-molecule
field and, where an atomic polar tensor exists, the intensity read-outs (lever 5 step 2, registered 2 Oct 2026 06:5x). Built on 2 Oct 2026 so the ten
hold-out (a) APTs, which land after chain 24 has started, can be read against chain 24's models.

    python probes/rungC_eval_saved.py <model.pt> <out_prefix> [--molecules corpus/molecules] [--use-analytic] [--threads 4] [--holdout-b-file F]
                                      [--eval-ids-file NAME=FILE ...]

--holdout-b-file (8 Oct 2026): hold-out (b) is derived from the corpus (the A2 molecules of two scaffold cores), so a merge that brings new children
of those cores enlarges it. With a frozen list (one id per line, '#' comments) (b) is read on that list — ids the loader does not admit are dropped
as the trainer drops them — and the derived (b) ids outside it are read separately as (b+).

--eval-ids-file NAME=FILE (12 Oct 2026; chain 41's size and scaffold sets, TASKS 49's large-PAH test): an explicit test set, read as hold-out
(NAME) with the same read-outs. Ids the loader does not admit are dropped and counted; a set that shares an id with the model's training ids is
refused (a read on trained molecules is not a test); NAME may not be a, b or b+. Repeatable. With --use-analytic each set records how many of its
molecules carry analytic labels.

--insample-read (decision 66, 17 Nov 2026): the checkpoint's own saved arguments say whether it is a measurement or a release network
(`m05/network_kind.py`). A release network trained on the hold-outs, so a read of it on (a) or (b) is refused; its one read here is this
flag — the in-sample read of the design note's check 3 — which reads hold-outs (a), (b) and every --eval-ids-file set as
`insample_<set>` (`insample_a8`, never `a8`), refuses a set with a molecule the network did not train on, reads no (b+), and is
itself refused for a measurement network. The record states `network_kind`.

The inputs are built by the trainer's own `load_corpus` and `molecule_tensors`; the prediction by its `predictor`; nothing is recomputed differently.
"""
import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

import torch

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "modules" / "05_support_predictor" / "m05"))
import holdout_twins as HT  # noqa: E402
import model_registry as MR  # noqa: E402
import network_kind as NK  # noqa: E402
import rungC_intensities as RI  # noqa: E402
from rungC_equivariant import load_molecule  # noqa: E402
from rungC_train import (  # noqa: E402
    load_corpus,
    load_hybrid_model,
    molecule_tensors,
    per_molecule_readouts,
    predictor,
    readouts,
    record_paths,
    tensor_config,
)


def training_ids(ck: dict, pool: list, admitted) -> tuple[list, str]:
    """The model's training pool: the ids saved in the checkpoint (since 8 Oct 2026), restricted to admitted molecules; for older checkpoints the
    first n of today's pool, which equals the training pool only while the corpus has not grown since the model was trained."""
    if ck.get("train_ids"):
        return [i for i in ck["train_ids"] if i in admitted], "checkpoint"
    return pool[: ck["n"]], "pool order (checkpoint without training ids)"


def split_holdout_b(test_b: list, frozen: list, admitted) -> tuple[list, list]:
    """(b) on the frozen list (restricted to admitted ids, in the loader's order where it has one), and (b+) = derived (b) ids not in the list."""
    keep = set(frozen)
    if not keep & set(admitted):
        raise SystemExit("--holdout-b-file: none of its ids is an admitted molecule")
    return sorted(i for i in keep if i in admitted), [i for i in test_b if i not in keep]


def read_ids(path: str) -> list[str]:
    """The ids of a list file: one per line, '#' comments."""
    with open(path, encoding="utf-8") as f:
        return [s.strip() for s in f if s.strip() and not s.startswith("#")]


def listed_sets(specs: list) -> dict[str, tuple[str, list[str]]]:
    """{NAME: (FILE, its ids)} from --eval-ids-file's NAME=FILE specs; a malformed spec and a name that is taken are refused."""
    out: dict[str, tuple[str, list[str]]] = {}
    for spec in specs:
        name, sep, path = spec.partition("=")
        if not sep or not name or not path:
            raise SystemExit(f"--eval-ids-file {spec!r}: expected NAME=FILE")
        if name in ("a", "b", "b+") or name in out:
            raise SystemExit(f"--eval-ids-file: the name {name!r} is taken")
        out[name] = (path, read_ids(path))
    return out


def refuse_trained(label: str, listed: list, trained: set, keys: dict) -> None:
    """A set with a molecule the model trained on, by id or as a twin of any charge (`keys`: `holdout_twins.manifest_keys`), is no
    test (TASKS 157, 253)."""
    overlap = sorted(set(listed) & trained)
    if overlap:
        raise SystemExit(f"{label}: {len(overlap)} ids are in the model's training set ({', '.join(overlap[:5])}) — not a test")
    twins = HT.twins(sorted(trained), listed, keys, any_charge=True)
    if twins:
        raise SystemExit(f"{label}: the training set holds {len(twins)} of its molecules under other ids or charges "
                         f"({', '.join(twins[:5])}) — not a test (TASKS 157, 253)")


def eval_sets(specs: list, admitted, train_ids, keys: dict, substituted=()) -> dict:
    """{NAME: {"ids", "dropped", "file", "n_analytic"}} from NAME=FILE specs (one id per line, '#' comments); see --eval-ids-file.
    Each set passes `refuse_trained`."""
    out = {}
    trained, analytic = set(train_ids), set(substituted)
    for name, (path, listed) in listed_sets(specs).items():
        refuse_trained(f"--eval-ids-file {name}", listed, trained, keys)
        ids = [i for i in listed if i in admitted]
        if not ids:
            raise SystemExit(f"--eval-ids-file {name}: none of its {len(listed)} ids is an admitted molecule")
        out[name] = {"ids": ids, "dropped": [i for i in listed if i not in admitted], "file": path, "n_analytic": sum(i in analytic for i in ids)}
    return out


def release_sets(a: argparse.Namespace, mols: dict, held: dict[str, list], tr: list, substituted: list) -> list[tuple[str, list, dict]]:
    """--insample-read: hold-outs (a) and (b) — (b) on the frozen list when given — and every --eval-ids-file set, each under its in-sample
    name. A set with a molecule the network did not train on is refused: its number would mix an in-sample error with a held-out one."""
    test_b = split_holdout_b(held["b"], read_ids(a.holdout_b_file), mols)[0] if a.holdout_b_file else held["b"]
    named = {"a": (held["a"], {}), "b": (test_b, {})}
    analytic = set(substituted)
    for name, (file, listed) in listed_sets(a.eval_ids_file).items():
        ids = [i for i in listed if i in mols]
        named[name] = (ids, {"file": file, "dropped": [i for i in listed if i not in mols], "n_analytic": sum(i in analytic for i in ids)})
    trained = set(tr)
    for name, (ids, _) in named.items():
        outside = [i for i in ids if i not in trained]
        if not ids:
            raise SystemExit(f"--insample-read ({name}): the set has no admitted molecule")
        if outside:
            raise SystemExit(f"--insample-read ({name}): {len(outside)} of its {len(ids)} molecules are not in the network's training data "
                             f"({', '.join(outside[:5])}) — not an in-sample read; name the sets the release pool took in "
                             "(--holdout-b-file for the frozen hold-out (b))")
    return [(NK.insample_name(name), ids, meta) for name, (ids, meta) in named.items()]


def measurement_sets(a: argparse.Namespace, mols: dict, held: dict[str, list], tr: list, substituted: list) -> list[tuple[str, list, dict]]:
    """Hold-outs (a) and (b) — (b) on the frozen list when given, the derived ids outside it apart as (b+) — and every --eval-ids-file
    set; none, built in or listed, shares a molecule with the training set by id or as a twin of any charge (`refuse_trained`). Each
    as (name, ids, what the record says about the set)."""
    keys = HT.manifest_keys(a.molecules)
    for name in ("a", "b"):
        refuse_trained(f"hold-out ({name})", held[name], set(tr), keys)
    test_b, b_plus = held["b"], []
    if a.holdout_b_file:
        test_b, b_plus = split_holdout_b(test_b, read_ids(a.holdout_b_file), mols)
    extra = eval_sets(a.eval_ids_file, mols, tr, keys, substituted)
    return ([("a", held["a"], {}), ("b", test_b, {})] + ([("b+", b_plus, {})] if b_plus else [])
            + [(name, s["ids"], {k: s[k] for k in ("file", "dropped", "n_analytic")}) for name, s in extra.items()])


def read_kind(ck: dict, model: str, insample: bool) -> str:
    """The checkpoint's kind, from its own saved arguments, with the two refusals: a release network read as a hold-out read, and
    --insample-read on a measurement network (its read on a hold-out is a hold-out read)."""
    kind = NK.kind_of_checkpoint(ck, model)
    if insample and kind != NK.RELEASE:
        raise SystemExit(f"--insample-read is the release networks' read (design note of 17 Nov 2026, §4, check 3); {model} is a "
                         "measurement network, whose read on a hold-out is a hold-out read: drop the flag")
    if not insample:
        try:
            NK.refuse_release(kind, model, "its error on hold-outs (a) and (b)")
        except NK.ReleaseNetworkError as e:
            raise SystemExit(f"{e}; the one read it has here is --insample-read, written under '{NK.INSAMPLE_PREFIX}<set>'") from None
    return kind


def read_sets(sets: list[tuple[str, list, dict]], mols: dict, tr: list, dF_of) -> tuple[dict, list[str]]:
    """({set name: its read-outs}, the table's rows): the registered read-outs, the per-molecule field and the intensity read-outs."""
    res, lines = {}, []
    for h, ids, meta in sets:
        r = readouts(mols, ids, tr, dF_of)
        r["per_molecule"] = per_molecule_readouts(mols, ids, tr, dF_of)
        r.update(RI.aggregate(r["per_molecule"]))
        r.update(meta)
        res[h] = r
        so = f"{r['spectrum_overlap']:.3f} ({r['spectrum_overlap_zero_rule']:.3f})" if r.get("intensity_n") else "—"
        ir = f"{r['intensity_rel_rms']:.2f} ({r['intensity_rel_rms_zero_rule']:.2f})" if r.get("intensity_n") else "—"
        lines.append(f"| ({h}) | {len(ids)} | {r['coupling_ratio']:.3f} | {r['corrected_freq_rms']:.2f} | {r['dH_residual_ratio']:.3f} | {so} | {ir} | "
                     f"{r.get('intensity_n', 0)} |")
    return res, lines


def apt_lines(res: dict, names: list[str]) -> list[str]:
    """One row per molecule with an atomic polar tensor."""
    lines = ["", "Per molecule with an APT:", "", "| molecule | ratio | ω rms | overlap | overlap zero rule | rel. rms | rel. rms zero rule | modes |",
             "|---|---|---|---|---|---|---|---|"]
    for h in names:
        for i, v in res[h]["per_molecule"].items():
            if v.get("spectrum_overlap") is not None:
                lines.append(f"| {i} ({h}) | {v['coupling_ratio'] if v['coupling_ratio'] is None else round(v['coupling_ratio'], 3)} | "
                             f"{v['corrected_freq_rms']:.2f} | {v['spectrum_overlap']:.3f} | {v['spectrum_overlap_zero_rule']:.3f} | "
                             f"{v['intensity_rel_rms']:.2f} | {v['intensity_rel_rms_zero_rule']:.2f} | {v['n_modes']} |")
    return lines


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("model")
    ap.add_argument("out_prefix")
    ap.add_argument("--molecules", default=str(PLAN / "modules" / "05_support_predictor" / "corpus" / "molecules"))
    ap.add_argument("--use-analytic", action="store_true")
    ap.add_argument("--threads", type=int, default=4)
    ap.add_argument("--holdout-b-file", default=None, help="frozen hold-out (b) ids; derived (b) ids outside it are read as (b+)")
    ap.add_argument("--eval-ids-file", action="append", default=[], metavar="NAME=FILE", help="an explicit test set read as hold-out (NAME); repeatable")
    ap.add_argument("--allow-any-model", action="store_true",
                    help="decision 55 (3 Oct 2026): use a model whose registry status is not 'carried' — name it in the record")
    ap.add_argument("--insample-read", action="store_true",
                    help=f"decision 66: a release network's read on molecules it trained on, each set written as '{NK.INSAMPLE_PREFIX}<set>' "
                         "(never a hold-out's name); refused for a measurement network, and without it a release network is refused")
    return ap


def write_record(out_prefix: str, res: dict, lines: list[str]) -> None:
    """The JSON record and its markdown table, each written to a temporary file and moved over the target."""
    for path, content in zip(record_paths(out_prefix), (json.dumps(res, indent=1), "\n".join(lines) + "\n"), strict=True):
        tmp = path.with_name(path.name + ".tmp")
        tmp.write_text(content, encoding="utf-8")
        os.replace(tmp, path)


def main() -> int:
    a = build_parser().parse_args()
    torch.set_num_threads(a.threads)
    t0 = time.time()
    MR.require_carried(Path(a.model), allow=a.allow_any_model, kind=None)          # decision 55; the kind is read_kind's, from the checkpoint
    model, ck = load_hybrid_model(Path(a.model))
    kind = read_kind(ck, Path(a.model).name, a.insample_read)                      # decision 66: before the corpus is loaded
    cfg = tensor_config(ck)
    mols, test_a, test_b, _, pool, substituted = load_corpus(a.molecules, a.use_analytic, settings=cfg.primitives)   # B as the model built it
    layers = ck["args"].get("pool_layers")
    if layers:                                                              # the trainer's --pool-layers filter, so `tr` is the training pool of the record
        pool = [i for i in pool if mols[i]["layer"] in set(layers.split(","))]
    tr, tr_source = training_ids(ck, pool, mols)
    sets = (release_sets if kind == NK.RELEASE else measurement_sets)(a, mols, {"a": test_a, "b": test_b}, tr, substituted)
    tensors = {i: molecule_tensors(i, load_molecule(Path(a.molecules) / i, use_analytic=a.use_analytic), mols[i], Path(a.molecules) / i, cfg,
                                   Path(a.out_prefix).parent / "ls_targets") for i in dict.fromkeys(i for _, ids, _ in sets for i in ids)}
    model.eval()
    res = {"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "model": a.model, NK.FIELD: kind,
           "model_record": {k: ck[k] for k in ("pattern", "aux_mode", "aux_target", "n", "seed")},
           "holdout_b_file": a.holdout_b_file, "use_analytic": a.use_analytic, "substituted_analytic": substituted, "n_train_ids": len(tr),
           "train_ids_source": tr_source, "apt_molecules": sorted(i for i in mols if "apt" in mols[i])}
    title = (f"# Release network read on molecules it trained on ({res['date']}) — in-sample, not a hold-out error (decision 66)"
             if kind == NK.RELEASE else f"# Saved model read on the hold-outs ({res['date']})")
    lines = [title, "", f"Model `{Path(a.model).name}` ({res['model_record']}); APTs on {len(res['apt_molecules'])} molecules.", "",
             "| hold-out | n | ring-coupling ratio | ω rms (cm⁻¹) | ΔH residual | spectrum overlap (zero rule) | intensity rel. rms (zero rule) | with APT |",
             "|---|---|---|---|---|---|---|---|"]
    read, rows = read_sets(sets, mols, tr, predictor(model, tensors, mols))
    res |= read
    lines += rows + apt_lines(res, [name for name, _, _ in sets])
    res["seconds"] = round(time.time() - t0)
    lines += ["", f"{res['seconds']} s."]
    write_record(a.out_prefix, res, lines)
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
