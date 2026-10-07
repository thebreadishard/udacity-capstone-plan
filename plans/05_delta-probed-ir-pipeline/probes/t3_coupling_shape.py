"""Amendment (B) of 7 Oct 2026 21:3x (rung C pre-registration): are the ring couplings at the TZ tier immaterial (B1, size), and does the proxy teach
their shape (B2)? No training: targets and records only.

B2 — per anchor, the ring-coupling correction in the B3LYP normal modes, exactly as the T3 read-out selects it (`e6_learning_curve.readout`: the
upper-triangle pairs of the ring family): the proxy's (analytic ωB97X − B3LYP; the corpus target after `e7_rungB_reread_analytic.substitute`) and the
CC one (the anchor Hessian minus B3LYP, through `rungC_cc_transfer.substitute_cc` — the code T3 itself uses). Cosine, Pearson r, the least-squares slope
of CC on proxy, and both rms sizes; for the TZ tier (the carried entries of the anchor registry) and, beside it, the cc-pVDZ tier where a VALID cc-pVDZ
entry exists. B1 — pooled over the TZ-tier T3 records (seed means), the network's coupling rms against the zero rule's, per column.

    python probes/t3_coupling_shape.py modules/05_support_predictor/out/t3_coupling_shape_2026-10-07
"""
from __future__ import annotations

import copy
import glob
import json
import sys
from datetime import datetime
from pathlib import Path

import numpy as np

PLAN = Path(__file__).resolve().parents[1]
M05 = PLAN / "modules" / "05_support_predictor"
sys.path.insert(0, str(M05 / "m05"))
COS_SHARED, COS_DIFFERENT, SIZE_MARGIN = 0.5, 0.3, 0.5          # the lines of amendment (B)
T3_TZ = "T3_tz_anchors_c34_seed*_2026-10-07.json"


def ring_pairs(K: np.ndarray, family, ring_label: str) -> np.ndarray:
    """The upper-triangle ring-ring elements of a mode-basis matrix, in the order the T3 read-out uses."""
    r = np.where(np.asarray(family) == ring_label)[0]
    if len(r) < 2:
        return np.zeros(0)
    iu = np.triu_indices(len(r), 1)
    return np.asarray(K)[np.ix_(r, r)][iu]


def shape_stats(x: np.ndarray, y: np.ndarray) -> dict:
    """x = proxy coupling correction, y = CC coupling correction (same pairs). Cosine, Pearson r, slope of y on x through the origin, sizes."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    nx, ny = float(np.linalg.norm(x)), float(np.linalg.norm(y))
    return dict(n=int(x.size), cos=float(x @ y / (nx * ny)) if nx and ny else float("nan"),
                r=float(np.corrcoef(x, y)[0, 1]) if x.size > 2 and x.std() and y.std() else float("nan"),
                slope=float(x @ y / (x @ x)) if nx else float("nan"), rms_proxy=float(np.sqrt(np.mean(x ** 2))) if x.size else float("nan"),
                rms_cc=float(np.sqrt(np.mean(y ** 2))) if y.size else float("nan"))


def pooled_rms(values) -> float:
    v = np.asarray(list(values), float)
    return float(np.sqrt(np.mean(v ** 2)))


def size_check(pattern: str) -> dict:
    """B1: seed means per held-out anchor, then the rms over anchors, per column (coupling error and the zero rule's)."""
    recs = [json.loads(Path(f).read_text(encoding="utf-8")) for f in sorted(glob.glob(str(M05 / "out" / pattern)))]
    out = {}
    for col in ("network_alpha", "network_head_l2"):
        net, zero = [], []
        for a in recs[0]["folds"]:
            net.append(np.mean([r["folds"][a][col]["coupling_rms"] for r in recs]))
            zero.append(np.mean([r["folds"][a][col]["coupling_zero_rms"] for r in recs]))
        out[col] = dict(net=pooled_rms(net), zero=pooled_rms(zero), immaterial=bool(pooled_rms(net) <= pooled_rms(zero) + SIZE_MARGIN))
    return out


def anchor_files() -> dict:
    """{mol_id: {"TZ": path, "DZ": path or None}} from the anchor registry: the carried TZ entry and a VALID cc-pVDZ full entry (newest)."""
    import anchor_registry as AR
    entries = AR.load()
    out = {}
    for e in entries:
        if e["status"] == "carried" and e["tier"] == "TZ":
            out.setdefault(e["mol_id"], {})["TZ"] = PLAN / e["path"]
    for mol in out:
        dz = sorted((e for e in entries if e["mol_id"] == mol and e["tier"] == "DZ" and e["kind"] == "full" and e["status"] in ("superseded", "carried")),
                    key=lambda e: e["date"])
        out[mol]["DZ"] = PLAN / dz[-1]["path"] if dz else None
    return out


def main() -> int:
    import e7_rungB_reread_analytic as RR
    import e7_t2_sqm as T2
    from e6_learning_curve import RING
    from rungC_cc_transfer import substitute_cc
    out = Path(sys.argv[1])
    mdir = M05 / "corpus" / "molecules"
    mols = T2.load(mdir)
    rows, per_tier = [], {"TZ": ([], []), "DZ": ([], [])}
    for mol, files in sorted(anchor_files().items()):
        d = mdir / mol
        m = mols[mol]
        if (d / "hessian_b3lyp_analytic.npz").exists() and (d / "hessian_wb97x_analytic.npz").exists():
            RR.substitute(m, d)
        lo = d / "hessian_b3lyp_analytic.npz" if (d / "hessian_b3lyp_analytic.npz").exists() else d / "hessian_b3lyp.npz"
        x = ring_pairs(m["K"], m["family"], RING)
        row = {"mol_id": mol, "n_ring_pairs": int(x.size)}
        for tier in ("TZ", "DZ"):
            if files.get(tier) is None:
                continue
            mc = substitute_cc(copy.deepcopy(m), lo, files[tier])
            y = ring_pairs(mc["K"], m["family"], RING)
            row[tier] = shape_stats(x, y)
            per_tier[tier][0].append(x)
            per_tier[tier][1].append(y)
        rows.append(row)
    pooled = {t: shape_stats(np.concatenate(xs), np.concatenate(ys)) for t, (xs, ys) in per_tier.items() if xs}
    b1 = size_check(T3_TZ)
    c = pooled["TZ"]["cos"]
    b2 = ("shared: the proxy teaches the shape, the fine-tune sets the size" if c >= COS_SHARED else
          "different: the proxy teaches another coupling" if c < COS_DIFFERENT else "between the lines: noted, no lever")
    b1v = b1["network_head_l2"]["immaterial"]
    md = [f"# Amendment (B): ring couplings at the TZ tier — {datetime.now():%Y-%m-%d %H:%M}", "",
          "Ring-coupling corrections in the B3LYP normal modes (upper-triangle ring pairs, as the T3 read-out): proxy = analytic ωB97X − B3LYP; CC = "
          "the anchor minus B3LYP (`substitute_cc`). Cosine, Pearson r, slope of CC on proxy (through 0), rms sizes in cm⁻¹.", "",
          "| anchor | ring pairs | TZ: cos | r | slope | rms proxy | rms CC | DZ: cos | slope | rms CC |", "|---|---|---|---|---|---|---|---|---|---|"]
    for row in rows:
        tz, dz = row.get("TZ", {}), row.get("DZ")
        md.append(f"| {row['mol_id']} | {row['n_ring_pairs']} | {tz.get('cos', float('nan')):.2f} | {tz.get('r', float('nan')):.2f} | "
                  f"{tz.get('slope', float('nan')):.2f} | {tz.get('rms_proxy', float('nan')):.2f} | {tz.get('rms_cc', float('nan')):.2f} | "
                  + (f"{dz['cos']:.2f} | {dz['slope']:.2f} | {dz['rms_cc']:.2f} |" if dz else "— | — | — |"))
    for t, s in pooled.items():
        md.append(f"| **pooled {t}** | {s['n']} | **{s['cos']:.2f}** | {s['r']:.2f} | {s['slope']:.2f} | {s['rms_proxy']:.2f} | {s['rms_cc']:.2f} | | | |")
    md += ["", "**B1 (size), pooled over the six held-out anchors (seed means):** " + "; ".join(
        f"{k.replace('network_', '')}: network {v['net']:.2f} vs zero rule {v['zero']:.2f} cm⁻¹" for k, v in b1.items())
           + f" → head-tuned {'within' if b1v else 'beyond'} the zero rule + {SIZE_MARGIN} cm⁻¹: couplings "
           + ("**immaterial** at the TZ tier" if b1v else "**a target of their own**") + ".",
           f"**B2 (shape):** pooled TZ cosine {c:.2f} → **{b2}**."]
    out.with_suffix(".md").write_text("\n".join(md) + "\n", encoding="utf-8")
    out.with_suffix(".json").write_text(json.dumps(dict(date=datetime.now().strftime("%Y-%m-%d %H:%M"), rows=rows, pooled=pooled, b1=b1, b2=b2,
                                                        lines=dict(cos_shared=COS_SHARED, cos_different=COS_DIFFERENT, size_margin=SIZE_MARGIN)),
                                                   indent=1), encoding="utf-8")
    print("\n".join(md))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
