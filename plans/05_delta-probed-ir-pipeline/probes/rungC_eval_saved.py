"""Read a saved rung-C hybrid model (`rungC_train.py --save-model`) on the hold-outs without retraining — the registered read-outs, the per-molecule
field and, where an atomic polar tensor exists, the intensity read-outs (lever 5 step 2, registered 2 Oct 2026 06:5x). Built on 2 Oct 2026 so the ten
hold-out (a) APTs, which land after chain 24 has started, can be read against chain 24's models.

    python probes/rungC_eval_saved.py <model.pt> <out_prefix> [--molecules corpus/molecules] [--use-analytic] [--threads 4]

The inputs are built by the trainer's own `load_corpus` and `molecule_tensors`; the prediction by its `predictor`; nothing is recomputed differently.
"""
import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace

import torch

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "modules" / "05_support_predictor" / "m05"))
import rungC_intensities as RI  # noqa: E402
from rungC_equivariant import load_molecule  # noqa: E402
from rungC_train import load_corpus, load_hybrid_model, molecule_tensors, per_molecule_readouts, predictor, readouts, record_paths  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("model")
    ap.add_argument("out_prefix")
    ap.add_argument("--molecules", default=str(PLAN / "modules" / "05_support_predictor" / "corpus" / "molecules"))
    ap.add_argument("--use-analytic", action="store_true")
    ap.add_argument("--threads", type=int, default=4)
    a = ap.parse_args()
    torch.set_num_threads(a.threads)
    t0 = time.time()
    model, ck = load_hybrid_model(Path(a.model))
    cfg = SimpleNamespace(aux=ck["aux_mode"], head=ck["head"], pattern=ck["pattern"], aux_target=ck["aux_target"], ls_lam=ck["ls_lam"], zero_hlow=False)
    mols, test_a, test_b, _, pool, substituted = load_corpus(a.molecules, a.use_analytic)
    layers = ck["args"].get("pool_layers")
    if layers:                                                              # the trainer's --pool-layers filter, so `tr` is the training pool of the record
        pool = [i for i in pool if mols[i]["layer"] in set(layers.split(","))]
    tr = pool[: ck["n"]]
    tensors = {i: molecule_tensors(i, load_molecule(Path(a.molecules) / i, use_analytic=a.use_analytic), mols[i], Path(a.molecules) / i, cfg,
                                   Path(a.out_prefix).parent / "ls_targets") for i in test_a + test_b}
    model.eval()
    dF_of = predictor(model, tensors, mols)
    res = {"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "model": a.model, "model_record": {k: ck[k] for k in ("pattern", "aux_mode", "aux_target", "n", "seed")},
           "use_analytic": a.use_analytic, "substituted_analytic": substituted, "n_train_ids": len(tr), "apt_molecules": sorted(i for i in mols if "apt" in mols[i])}
    lines = [f"# Saved model read on the hold-outs ({res['date']})", "", f"Model `{Path(a.model).name}` ({res['model_record']}); APTs on {len(res['apt_molecules'])} molecules.", "",
             "| hold-out | n | ring-coupling ratio | ω rms (cm⁻¹) | ΔH residual | spectrum overlap (zero rule) | intensity rel. rms (zero rule) | with APT |", "|---|---|---|---|---|---|---|---|"]
    for h, ids in (("a", test_a), ("b", test_b)):
        r = readouts(mols, ids, tr, dF_of)
        r["per_molecule"] = per_molecule_readouts(mols, ids, tr, dF_of)
        r.update(RI.aggregate(r["per_molecule"]))
        res[h] = r
        so = f"{r['spectrum_overlap']:.3f} ({r['spectrum_overlap_zero_rule']:.3f})" if r.get("intensity_n") else "—"
        ir = f"{r['intensity_rel_rms']:.2f} ({r['intensity_rel_rms_zero_rule']:.2f})" if r.get("intensity_n") else "—"
        lines.append(f"| ({h}) | {len(ids)} | {r['coupling_ratio']:.3f} | {r['corrected_freq_rms']:.2f} | {r['dH_residual_ratio']:.3f} | {so} | {ir} | {r.get('intensity_n', 0)} |")
    lines += ["", "Per molecule with an APT:", "", "| molecule | ratio | ω rms | overlap | overlap zero rule | rel. rms | rel. rms zero rule | modes |", "|---|---|---|---|---|---|---|---|"]
    for h in ("a", "b"):
        for i, v in res[h]["per_molecule"].items():
            if v.get("spectrum_overlap") is not None:
                lines.append(f"| {i} ({h}) | {v['coupling_ratio'] if v['coupling_ratio'] is None else round(v['coupling_ratio'], 3)} | {v['corrected_freq_rms']:.2f} | "
                             f"{v['spectrum_overlap']:.3f} | {v['spectrum_overlap_zero_rule']:.3f} | {v['intensity_rel_rms']:.2f} | {v['intensity_rel_rms_zero_rule']:.2f} | {v['n_modes']} |")
    res["seconds"] = round(time.time() - t0)
    lines += ["", f"{res['seconds']} s."]
    out_json, out_md = record_paths(a.out_prefix)
    json.dump(res, open(out_json, "w"), indent=1)
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
