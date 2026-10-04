"""Lever 2, dated amendment 4 Oct 2026 13:4x: the carried ΔH-network against CC/DZ and CC/TZ on benzene's three measured cc-pVTZ coordinates. For each
coordinate k of `cc_basis_oop_check`'s json, H_kk(B3LYP) + ΔH_kk(network, mean of the carried seeds) beside H_kk(B3LYP), CC/DZ and CC/TZ, and which of
DZ and TZ the network's value is closer to. A read of existing models on existing numbers; one minute; nothing else is read from it.

    python probes/cc_basis_network_check.py <cc_basis_oop_check json> <mol_id> <out_prefix> --models <carried .pt> [<carried .pt> ...] [--threads 2]
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace

import numpy as np

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "modules" / "05_support_predictor" / "m05"))
import model_registry as MR  # noqa: E402
from rungC_equivariant import load_molecule  # noqa: E402
from rungC_train import load_corpus, load_hybrid_model, molecule_tensors  # noqa: E402


def network_delta(mol_id: str, molecules: Path, models: list[Path], cache_dir: Path) -> tuple[np.ndarray, list[dict]]:
    import torch
    mol_dir = molecules / mol_id
    mols, *_ = load_corpus(str(molecules), True, log=lambda *_: None)
    m = mols[mol_id]
    preds, notes = [], []
    for mp in models:
        st = MR.require_carried(mp)
        model, ck = load_hybrid_model(mp)
        cfg = SimpleNamespace(aux=ck["aux_mode"], head=ck["head"], pattern=ck["pattern"], aux_target=ck["aux_target"], ls_lam=ck["ls_lam"], zero_hlow=False)
        t = molecule_tensors(mol_id, load_molecule(mol_dir, use_analytic=True), m, mol_dir, cfg, cache_dir)
        model.eval()
        with torch.no_grad():
            preds.append(model(t["Z"], t["pos"], t["H_low"], t).numpy().astype(float))
        notes.append({"path": str(mp), "status": st["status"], "version": st.get("version", "")})
    return np.mean(preds, axis=0), notes


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("check_json")
    ap.add_argument("mol_id")
    ap.add_argument("out_prefix")
    ap.add_argument("--models", nargs="+", required=True)
    ap.add_argument("--molecules", default=str(PLAN / "modules" / "05_support_predictor" / "corpus" / "molecules"))
    ap.add_argument("--threads", type=int, default=2)
    a = ap.parse_args()
    import torch
    torch.set_num_threads(a.threads)
    chk = json.loads(Path(a.check_json).read_text(encoding="utf-8"))
    dH, notes = network_delta(a.mol_id, Path(a.molecules), [Path(p) for p in a.models], Path(a.out_prefix).parent / "ls_targets")
    rows = []
    for r in chk["rows"]:
        k = int(r["k"])
        h_net = r["H_b3lyp"] + float(dH[k, k])
        d_dz, d_tz = abs(h_net - r["H_cc_dz"]), abs(h_net - r["H_cc_tz"])
        rows.append(dict(k=k, atom=r["atom"], xyz=r["xyz"], oop=round(r["oop_fraction"], 2), H_b3lyp=r["H_b3lyp"], H_cc_dz=r["H_cc_dz"], H_cc_tz=r["H_cc_tz"],
                         dH_net=float(dH[k, k]), H_net=h_net, dist_dz=d_dz, dist_tz=d_tz, closer_to="TZ" if d_tz < d_dz else "DZ"))
    n_tz = sum(r["closer_to"] == "TZ" for r in rows)
    md = [f"# The carried network against CC/DZ and CC/TZ on {a.mol_id}'s measured coordinates — {datetime.now():%Y-%m-%d %H:%M}", "",
          f"Models: {', '.join(Path(n['path']).name + ' (' + n['status'] + (' v' + n['version'] if n['version'] else '') + ')' for n in notes)}; "
          f"source {Path(a.check_json).name}.", "",
          "| k | atom xyz | oop | H B3LYP | H CC/DZ | H CC/TZ | ΔH network | H B3LYP+network | |net−DZ| | |net−TZ| | closer to |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    md += [f"| {r['k']} | {r['atom']} {r['xyz']} | {r['oop']:.2f} | {r['H_b3lyp']:.5f} | {r['H_cc_dz']:.5f} | {r['H_cc_tz']:.5f} | {r['dH_net']:+.5f} | "
           f"{r['H_net']:.5f} | {r['dist_dz']:.5f} | {r['dist_tz']:.5f} | **{r['closer_to']}** |" for r in rows]
    md += ["", f"Closer to TZ on **{n_tz} of {len(rows)}** coordinates (reading rule: ≥ 2 of 3 → the DZ anchors overstated the network's error on these families)."]
    Path(a.out_prefix + ".md").write_text("\n".join(md), encoding="utf-8")
    Path(a.out_prefix + ".json").write_text(json.dumps(dict(date=datetime.now().strftime("%Y-%m-%d %H:%M"), check_json=a.check_json, mol_id=a.mol_id,
                                                            models=notes, rows=rows, n_closer_to_tz=n_tz), indent=1), encoding="utf-8")
    print("\n".join(md))
    return 0


if __name__ == "__main__":
    sys.exit(main())
