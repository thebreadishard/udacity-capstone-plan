"""Set-three diagnosis, the analyses that train nothing (21 Oct 2026, beside probes/set3_diagnosis.py's runs). Each puts a 'prediction' of
the CC correction through the T3 read-out (`rungC_cc_transfer.read`: corrected-ω rms per family, ring-coupling ratio, matched intensity
with the CC APT) on the eleven carried TZ anchors, from the copied corpus:

  A1 proxy      — ΔH = ωB97X − B3LYP itself (analytic, the network's pretraining target): what a perfect proxy model would read
  A2 proxy × c  — one factor c on it, least squares on the other ten anchors (leave-one-out)
  A3 alignment  — per anchor, in the low level's mode basis: the CC and the proxy shifts K_kk of the CH-oop and 'other' modes — their
                  correlation, the slope of CC on proxy, and the CC/proxy rms ratio
  A4 network vs proxy — the carried network as it is, read against the proxy (ωB97X) truth: does it know the proxy on these molecules?
  A6 DZ → TZ    — the CC/DZ Hessian read against the TZ anchor: how far the basis step moves each family (the anchors' own sensitivity)
  A5 (benzene)  — the composite against the full CC/TZ anchor, from test 2's record (the anchors' accuracy at the composite level)

    python probes/set3_analyses.py <out_dir>          → <out_dir>/analyses.{json,md}
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np

PLAN = Path(__file__).resolve().parents[1]
M05 = PLAN / "modules" / "05_support_predictor"
sys.path.insert(0, str(M05 / "m05"))
sys.path.insert(0, str(PLAN / "probes"))
import anchor_set3_read as S3  # noqa: E402
import e7_rungB_reread_analytic as RR  # noqa: E402
import e7_t2_sqm as T2  # noqa: E402
import rungC_cc_transfer as CT  # noqa: E402
import set3_diagnosis as D  # noqa: E402
from rungC_train import load_hybrid_model, predictor  # noqa: E402

FAMS = ("CH-oop", "other", "ring-ip", "CH-stretch")
OOP_FAMS = ("CH-oop", "other")
TEST2 = M05 / "out" / "composite_test2_benzene_2026-10-06.json"
BENZENE_DZ = PLAN / "probes" / "results_m1" / "e8_benzene_ccpvdz_dip_2026-10-03" / "hessian_ccsd_t.npz"


def projected(path: Path) -> np.ndarray:
    with np.load(path) as z:
        return np.asarray(z["H_projected"], float)


def internal(m: dict, dH: np.ndarray) -> np.ndarray:
    Bp = np.linalg.pinv(m["B"])
    return Bp.T @ dH @ Bp


def anchors_with(mdir: Path, high: str) -> CT.Anchors:
    """The eleven anchors with the CC ('cc') or the analytic ωB97X ('proxy') Hessian as their truth, the analytic B3LYP as the low level."""
    files = D.anchors()
    mols = T2.load(mdir)
    for i in files:
        RR.substitute(mols[i], mdir / i)                      # the analytic pair: low B3LYP, high ωB97X
        if high == "cc":
            CT.substitute_cc(mols[i], CT.low_level_file(mdir / i), Path(files[i]))
    apts = {i: CT.load_cc_apt(S3.APTS[i], mdir / i) for i in files if i in S3.APTS}
    ids = sorted(files)
    return CT.Anchors(mols=mols, tensors={}, ids=ids, low_files={}, apts=apts, geoms={i: CT._geometry(mdir / i) for i in ids})


def mean_read(an: CT.Anchors, dF_of, ids: list[str] | None = None) -> dict:
    """The anchors (default all) read with `dF_of` (no fold training here: the train list only names the others); means as
    set3_diagnosis.summary."""
    rec = {"folds": {}}
    for held in ids or an.ids:
        tr = [i for i in an.ids if i != held]
        rec["folds"][held] = {"x": CT.read(an, held, tr, dF_of), "zero_rule": CT.read(an, held, tr, CT.zero(an))}
    return D.summary(rec, "x"), rec


def proxy_dF(an: CT.Anchors, mdir: Path, scale: dict | None = None):
    def f(i):
        dH = projected(mdir / i / "hessian_wb97x_analytic.npz") - an.mols[i]["H_low"]
        return internal(an.mols[i], dH * (scale[i] if scale else 1.0))
    return f


def loo_scales(an: CT.Anchors, mdir: Path) -> dict[str, float]:
    """Per held-out anchor, c = Σ⟨ΔH_cc, ΔH_proxy⟩ / Σ‖ΔH_proxy‖² over the other ten (mass-weighted Cartesian blocks)."""
    num, den = {}, {}
    for i in an.ids:
        m = an.mols[i]
        w = 1 / np.sqrt(np.repeat(m["masses"], 3))
        p = (projected(mdir / i / "hessian_wb97x_analytic.npz") - m["H_low"]) * np.outer(w, w)
        c = m["dH_true"] * np.outer(w, w)
        num[i], den[i] = float((c * p).sum()), float((p * p).sum())
    return {i: sum(num[j] for j in an.ids if j != i) / sum(den[j] for j in an.ids if j != i) for i in an.ids}


def alignment(an_cc: CT.Anchors, an_px: CT.Anchors) -> dict:
    """Per anchor, on the CH-oop and 'other' modes of the low level: corr and slope of the CC shifts on the proxy shifts, and their rms ratio."""
    out = {}
    for i in an_cc.ids:
        fam = np.array(an_cc.mols[i]["family"])
        kc, kp = np.diag(an_cc.mols[i]["K"]).astype(float), np.diag(an_px.mols[i]["K"]).astype(float)
        row = {}
        for f in OOP_FAMS:
            sel = fam == f
            if sel.sum() >= 3:
                row[f] = {"n": int(sel.sum()), "corr": float(np.corrcoef(kc[sel], kp[sel])[0, 1]),
                          "slope": float((kc[sel] @ kp[sel]) / (kp[sel] @ kp[sel])),
                          "rms_ratio": float(np.sqrt(np.mean(kc[sel] ** 2)) / np.sqrt(np.mean(kp[sel] ** 2)))}
        out[i] = row
    return out


def dz_files() -> dict[str, Path]:
    """Each anchor's CC/DZ Hessian: the composite record's source anchor (benzene's full TZ anchor: its DZ run), skipping invalid ones."""
    out = {}
    for i, tz in D.anchors().items():
        if i == "A_8448043181":
            out[i] = BENZENE_DZ
            continue
        rec = json.loads(Path(tz).with_suffix(".json").read_text(encoding="utf-8"))
        src = Path(rec["anchor"])
        if "INVALID" not in src.name and "IMAGINARY" not in src.name:
            out[i] = src if src.is_absolute() else PLAN / src
    return out


def network_vs_proxy(an_px: CT.Anchors, mdir: Path) -> dict:
    """The carried chain-34 seed-0 network as it is, read against the ωB97X truth."""
    model, ck = load_hybrid_model(M05 / D.MODEL.format(chain=D.CHAIN34, seed=0))
    cfg = SimpleNamespace(aux=ck["aux_mode"], head=ck["head"], pattern=ck["pattern"], aux_target=ck["aux_target"], ls_lam=ck["ls_lam"], zero_hlow=False)
    with_tensors = CT.prepare_anchors(mdir, {i: str(mdir / i / "hessian_wb97x_analytic.npz") for i in an_px.ids}, [], cfg,
                                      mdir.parent.parent / "ls_targets_proxy")
    return mean_read(an_px, predictor(model, with_tensors.tensors, with_tensors.mols))[0]


def benzene_test2() -> dict:
    res = json.loads(TEST2.read_text(encoding="utf-8"))["results"]
    return {k: {f: res[k].get(f) for f in (*FAMS, "all")} for k in ("comp", "dz", "low")}


def main(out_dir: Path) -> int:
    mdir = out_dir / "corpus" / "molecules"
    an_cc, an_px = anchors_with(mdir, "cc"), anchors_with(mdir, "proxy")
    res = {"A1 proxy as the prediction": mean_read(an_cc, proxy_dF(an_cc, mdir))[0]}
    scales = loo_scales(an_cc, mdir)
    res["A2 proxy x c (leave-one-out)"] = mean_read(an_cc, proxy_dF(an_cc, mdir, scales))[0]
    res["A2 scales"] = scales
    res["A3 alignment"] = alignment(an_cc, an_px)
    dz = dz_files()
    res["A6 CC/DZ read against TZ"] = mean_read(an_cc, lambda i: internal(an_cc.mols[i], projected(dz[i]) - an_cc.mols[i]["H_low"]),
                                               sorted(dz))[0]
    res["A6 DZ files"] = {i: str(p) for i, p in dz.items()}
    res["A5 benzene composite vs full CC/TZ (test 2)"] = benzene_test2()
    res["A4 network as is vs the proxy truth"] = network_vs_proxy(an_px, mdir)
    (out_dir / "analyses.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in res.items() if k not in ("A3 alignment", "A6 DZ files")}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(Path(sys.argv[1]).resolve()))
