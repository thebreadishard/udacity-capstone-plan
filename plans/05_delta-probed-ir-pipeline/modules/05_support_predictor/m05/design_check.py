"""Design check for a rung C body (28 September 2026; the user: "kunnen wij ook testen bij ontwerp vanaf nu?" → "implementeer de controle").

Two incidents in one week had the same shape: a setting or property that depends on the molecule travelled unexamined from where a method was
built to where it was applied (E8: benzene's frozen-core count on naphthalene; C2: a body pretrained at ≈ 11 neighbours per atom applied to
fused rings with 15–21). This script asks that question mechanically, before a run is queued:

1. **Target extremes.** Over the target molecules it finds the smallest and largest molecule, the sparsest and densest neighbourhood (mean and
   maximum neighbour count within the model's cutoff) and the heaviest element.
2. **Body probe.** The body (fresh, or a pretraining checkpoint) is run on those extremes; every raw output must be finite and below `--limit-abs`,
   and the per-atom feature scale may vary across the extremes by at most `--limit-ratio` (a fresh sum body: 1.5× between 7 and 23 neighbours,
   a fresh mean body: 1.0005×; the QM9-trained sum body of 27 Sep: 10¹⁸).
3. **Transfer table** (with `--source-qm9`): for every property, the source range against the target range, and whether the target lies inside
   it. A target outside the source range is not a failure by itself — the body probe is the test — but it is printed so the pre-registration
   can name the test that covers it.

Exit 0 = pass, 1 = fail; a Markdown and a JSON record beside `--out`. Stage scripts run it first and stop on failure.

    python m05/design_check.py corpus/molecules --aggregation mean --out out/design_check_rungC_mean_2026-09-28
    python m05/design_check.py corpus/molecules --checkpoint out/rungC_pretrained_mean_2026-09-28.pt --source-qm9 data/hessian_qm9 --out …
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))
from rungC_equivariant import AGGREGATION, AGGREGATIONS, CUTOFF_BOHR, DeltaHessianModel, console_utf8_safe, edges_within, load_molecules  # noqa: E402

from dpir.provenance import provenance  # noqa: E402

PROPERTIES = ("n_atoms", "mean_degree", "max_degree", "max_Z")
EXTREMES = (("n_atoms", "min"), ("n_atoms", "max"), ("mean_degree", "min"), ("mean_degree", "max"), ("max_degree", "max"), ("max_Z", "max"))


def molecule_stats(m: dict, cutoff: float = CUTOFF_BOHR) -> dict:
    """Size, neighbourhood density within the cutoff, heaviest element."""
    pos = torch.as_tensor(np.asarray(m["pos"]), dtype=torch.float32)
    n = pos.shape[0]
    i, _j = edges_within(pos, cutoff)
    deg = torch.bincount(i, minlength=n)
    Z = np.asarray(m["Z"], dtype=int)
    return {"n_atoms": int(n), "mean_degree": float(deg.float().mean()), "max_degree": int(deg.max()) if n else 0, "max_Z": int(Z.max()),
            "elements": sorted(int(z) for z in set(Z.tolist()))}


def extremes(stats: dict) -> dict:
    """{(property, which): molecule id} — the target molecules the body must survive."""
    out = {}
    for prop, which in EXTREMES:
        pick = min if which == "min" else max
        out[f"{prop}_{which}"] = pick(stats, key=lambda k: stats[k][prop])
    return out


def probe_body(body: torch.nn.Module, mols: dict, ids: list) -> dict:
    """Per molecule: worst raw |output| and the mean |s| feature scale after the body; nothing is trained."""
    out = {}
    body.eval()
    with torch.no_grad():
        for mid in ids:
            m = mols[mid]
            Z = torch.as_tensor(np.asarray(m["Z"]), dtype=torch.long)
            pos = torch.as_tensor(np.asarray(m["pos"]), dtype=torch.float32)
            H = torch.as_tensor(np.asarray(m["H_low"]), dtype=torch.float32)
            s = body.encode(Z, pos, H)[0]
            y = body(Z, pos, H)
            finite = bool(torch.isfinite(s).all() and torch.isfinite(y).all())
            out[mid] = {"feature_scale": float(s.abs().mean()) if finite else float("inf"),
                        "worst_output": float(y.abs().max()) if finite else float("inf"), "finite": finite}
    return out


def verdict(probe: dict, limit_abs: float, limit_ratio: float) -> dict:
    scales = [p["feature_scale"] for p in probe.values()]
    worst = max(p["worst_output"] for p in probe.values())
    ratio = (max(scales) / min(scales)) if min(scales) > 0 else float("inf")
    finite = all(p["finite"] for p in probe.values())
    return {"finite": finite, "worst_output": worst, "scale_ratio": ratio,
            "pass": bool(finite and worst <= limit_abs and ratio <= limit_ratio), "limit_abs": limit_abs, "limit_ratio": limit_ratio}


def ranges(stats: dict) -> dict:
    r = {p: [min(s[p] for s in stats.values()), max(s[p] for s in stats.values())] for p in PROPERTIES}
    r["elements"] = sorted({z for s in stats.values() for z in s["elements"]})
    return r


def transfer_table(source: dict, target: dict) -> list[dict]:
    """One row per property: source range, target range, inside? Elements: the target elements missing from the source."""
    rows = []
    for p in PROPERTIES:
        inside = source[p][0] <= target[p][0] and target[p][1] <= source[p][1]
        rows.append({"property": p, "source": source[p], "target": target[p], "inside": inside})
    missing = sorted(set(target["elements"]) - set(source["elements"]))
    rows.append({"property": "elements", "source": source["elements"], "target": target["elements"], "inside": not missing, "missing": missing})
    return rows


def load_body(checkpoint: str | None, aggregation: str, seed: int, target_elements: list[int] | None = None,
              pretrained_elements: list[int] | None = None, tensor_input: bool = False, body_blocks: int | None = None,
              body_width: int | None = None) -> tuple[torch.nn.Module, str]:
    """A fresh body, the checkpoint's body as stored, or (with `target_elements`) the checkpoint's body as the fine-tune will see it: through
    `rungC_train.load_pretrained_body`, untrained element embeddings reset to the trained mean."""
    if checkpoint:
        ck = torch.load(checkpoint, map_location="cpu", weights_only=False)
        agg = ck.get("aggregation", "sum")
        if target_elements is not None:
            from rungC_train import load_pretrained_body
            body = load_pretrained_body(checkpoint, reinit_head=False, aggregation=agg, target_elements=target_elements,
                                        pretrained_elements=pretrained_elements)
            return body, f"checkpoint {checkpoint} ({agg} aggregation) as the fine-tune sees it: element rows reset {body.reset_elements}"
        body = DeltaHessianModel(aggregation=agg)
        body.load_state_dict(ck["body_state"])
        return body, f"checkpoint {checkpoint} ({agg} aggregation, as stored)"
    torch.manual_seed(seed)
    kw = {k: v for k, v in (("n_blocks", body_blocks), ("n_s", body_width), ("n_v", body_width)) if v is not None}
    return (DeltaHessianModel(aggregation=aggregation, tensor_input=tensor_input, **kw),
            f"fresh body, {aggregation} aggregation{', rank-2 tensor input' if tensor_input else ''}"
            + (f", {body_blocks or 'default'} blocks × width {body_width or 'default'}" if kw else "") + f", seed {seed}")


def load_source_qm9(qm9_dir: str, sample: int) -> dict:
    from rungC_pretrain import iter_qm9
    shards = sorted(Path(qm9_dir).glob("data-*.arrow"))
    if not shards:
        raise SystemExit(f"no Arrow shards under {qm9_dir}")
    return {m["id"]: m for m in iter_qm9(shards, sample)}


def main(argv: list[str] | None = None) -> int:
    console_utf8_safe()
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("molecules", help="target corpus directory (every admitted molecule counts as target)")
    ap.add_argument("--out", required=True, help="record prefix (.md and .json)")
    ap.add_argument("--aggregation", default=AGGREGATION, choices=list(AGGREGATIONS), help="body to probe when no checkpoint is given")
    ap.add_argument("--tensor-input", action="store_true", help="probe the fresh body with the rank-2 pair-tensor input (30 Sep 2026)")
    ap.add_argument("--body-blocks", type=int, default=None, help="lever 2c (1 Oct 2026): probe a fresh body with this many interaction blocks")
    ap.add_argument("--body-width", type=int, default=None, help="lever 2c (1 Oct 2026): probe a fresh body with this many scalar/vector channels")
    ap.add_argument("--checkpoint", default=None, help="probe the body of a rungC_pretrain.py checkpoint instead of a fresh one")
    ap.add_argument("--as-finetune", action="store_true",
                    help="probe the checkpoint as the fine-tune will see it (element embeddings absent from pretraining reset to the trained mean)")
    ap.add_argument("--pretrained-elements", default=None, help="comma list of atomic numbers a pre-28-Sep checkpoint was trained on")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--limit-abs", type=float, default=1e3, help="largest raw |output| tolerated on any extreme (fresh bodies: 10–40)")
    ap.add_argument("--limit-ratio", type=float, default=3.0, help="largest feature-scale ratio tolerated across the extremes")
    ap.add_argument("--source-qm9", default=None, help="Hessian QM9 directory: adds the source-against-target transfer table")
    ap.add_argument("--source-sample", type=int, default=500)
    ap.add_argument("--threads", type=int, default=2)
    a = ap.parse_args(argv)
    torch.set_num_threads(a.threads)
    t0 = time.time()

    mols = load_molecules(Path(a.molecules))
    if not mols:
        print(f"no molecules under {a.molecules}")
        return 1
    stats = {k: molecule_stats(m) for k, m in mols.items()}
    ext = extremes(stats)
    target_elements = sorted({z for s in stats.values() for z in s["elements"]}) if a.as_finetune else None
    pre = [int(z) for z in a.pretrained_elements.split(",")] if a.pretrained_elements else None
    body, body_desc = load_body(a.checkpoint, a.aggregation, a.seed, target_elements, pre, tensor_input=a.tensor_input,
                                body_blocks=a.body_blocks, body_width=a.body_width)
    probe = probe_body(body, mols, sorted(set(ext.values())))
    v = verdict(probe, a.limit_abs, a.limit_ratio)
    rec = {"date": time.strftime("%Y-%m-%d %H:%M"), "provenance": provenance(), "molecules": a.molecules, "n_target": len(mols), "body": body_desc, "target_ranges": ranges(stats),
           "extremes": ext, "probe": probe, "verdict": v}
    lines = [f"# Design check — {a.out} ({rec['date']})", "", f"body: {body_desc}; target: {len(mols)} molecules under `{a.molecules}`", "",
             "| extreme | molecule | atoms | mean deg | max deg | max Z | feature scale | worst output |", "|---|---|---|---|---|---|---|---|"]
    for name, mid in ext.items():
        s, p = stats[mid], probe[mid]
        lines.append(f"| {name} | {mid} | {s['n_atoms']} | {s['mean_degree']:.1f} | {s['max_degree']} | {s['max_Z']} | "
                     f"{p['feature_scale']:.3g} | {p['worst_output']:.3g} |")
    lines += ["", f"verdict: **{'PASS' if v['pass'] else 'FAIL'}** — finite {v['finite']}, worst output {v['worst_output']:.3g} (limit {a.limit_abs:g}), "
                  f"feature-scale ratio across the extremes {v['scale_ratio']:.3g} (limit {a.limit_ratio:g})"]
    if a.source_qm9:
        src = load_source_qm9(a.source_qm9, a.source_sample)
        src_ranges = ranges({k: molecule_stats(m) for k, m in src.items()})
        rows = transfer_table(src_ranges, rec["target_ranges"])
        rec["source"] = {"dir": a.source_qm9, "n_sample": len(src), "ranges": src_ranges, "table": rows}
        lines += ["", f"## Transfer table — source `{a.source_qm9}` ({len(src)} sampled) → target", "",
                  "| property | source | target | target inside source? |", "|---|---|---|---|"]
        for r in rows:
            note = "" if r["inside"] else " ← outside: name the test that covers it"
            lines.append(f"| {r['property']} | {r['source']} | {r['target']} | {'yes' if r['inside'] else 'NO'}{note} |")
    rec["seconds"] = round(time.time() - t0, 1)
    lines += ["", f"{rec['seconds']} s"]
    Path(a.out + ".json").write_text(json.dumps(rec, indent=1), encoding="utf-8")
    Path(a.out + ".md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 0 if v["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
