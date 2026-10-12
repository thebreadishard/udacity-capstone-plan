"""Where does the λ = 1 fine-tune spoil the mode shapes? (12–13 Oct 2026; exploratory, post hoc, input for the λ chain's registration — not a
registered result.) Lever 6b found that the TZ standard (head tuned, λ = 1) gives worse intensities than B3LYP's own Hessian on pyridine,
fluorobenzene and benzonitrile, while the positions improve.

Inputs, all already on disk:
- the leave-one-anchor-out ΔH of the standard mode saved by the 10 Oct T3 run (`out/T3_tz_folds_c34_seed{0,1,2}_2026-10-10_fold_<id>.npz`,
  `--save-fold-predictions`, the same models and arguments as lever 6b's read);
- the carried composite CC Hessians (the anchors' truth);
- the CC APTs by the field route (`probes/results_m1/cc_apt_field_2026-10-12/`).

The read-out's own arithmetic is used (`m05/rungC_intensities.py`: `mode_intensities`, `match_modes`; weights = truth intensities). Per mode of
the truth, matched by eigenvector, it reports:
- the squared overlap of the prediction's and the zero rule's eigenvector with the truth's;
- each mode's share of the weighted squared relative intensity error;
- the mode's kind: C–H stretch (> 2500 cm⁻¹), out of plane (> 50 % of the mass-weighted displacement along the plane's normal), in plane.

    python probes/l6_mode_shape_diagnosis.py   → probes/results_m1/cc_apt_field_2026-10-12/mode_shape_diagnosis.{json,md}
"""
import json
import sys
from pathlib import Path

import numpy as np

PLAN = Path(__file__).resolve().parents[1]
M05 = PLAN / "modules" / "05_support_predictor"
sys.path.insert(0, str(M05 / "m05"))
from rungC_intensities import match_modes, mode_intensities  # noqa: E402

RES = PLAN / "probes" / "results_m1" / "cc_apt_field_2026-10-12"
ANCHORS = {"A_6e858b26e5": ("pyridine", "composite_full_pyridine_2026-10-07.npz"),
           "B_8b12a55d3a": ("fluorobenzene", "composite_full_fluorobenzene_2026-10-07.npz"),
           "A_3100da3761": ("benzonitrile", "composite_full_benzonitrile_2026-10-07.npz")}


def plane_normal(coords):
    x = coords - coords.mean(axis=0)
    return np.linalg.svd(x)[2][-1]


def kinds(freq, L, masses, normal):
    """'CH-str', 'oop' or 'ip' per mode (columns of the mass-weighted eigenvectors L)."""
    disp = (L / np.sqrt(np.repeat(masses, 3))[:, None]).reshape(len(masses), 3, -1)
    w = np.repeat(masses, 1)[:, None] * (disp ** 2).sum(axis=1)                     # mass-weighted squared displacement per atom
    along = (masses[:, None] * np.einsum("aim,i->am", disp, normal) ** 2).sum(axis=0) / w.sum(axis=0)
    return np.where(freq > 2500, "CH-str", np.where(along > 0.5, "oop", "ip"))


def molecule(mid, name, comp_file, seed):
    g = json.load(open(M05 / "corpus" / "molecules" / mid / "geometry.json", encoding="utf-8"))
    masses, coords = np.asarray(g["masses_amu"]), np.asarray(g["coords_bohr"])
    fold = np.load(M05 / "out" / f"T3_tz_folds_c34_seed{seed}_2026-10-10_fold_{mid}.npz", allow_pickle=True)
    if str(fold["mode"]) != "head_l2":
        raise SystemExit(f"{mid} seed {seed}: fold mode {fold['mode']}, not the TZ standard")
    H_low, dH = fold["H_low"], fold["dH_pred"]
    H_true = np.load(M05 / "out" / comp_file, allow_pickle=True)["H_projected"]
    apt = np.load(RES / f"{name}_ccpvdz_field.npz")["apt"]
    ft, it, Lt = mode_intensities(H_true, masses, apt, return_modes=True)
    fp, ip, Lp = mode_intensities(H_low + dH, masses, apt, return_modes=True)
    f0, i0, L0 = mode_intensities(H_low, masses, apt, return_modes=True)
    mp, m0 = match_modes(Lt, Lp), match_modes(Lt, L0)
    wgt = it / it.sum()
    err = lambda i: wgt * ((i - it) / np.maximum(it, 1.0)) ** 2                    # noqa: E731 — the read-out's own terms
    ep, e0 = err(ip[mp]), err(i0[m0])
    kind = kinds(ft, Lt, masses, plane_normal(coords))
    rows = [{"freq_true": round(float(ft[k]), 1), "kind": str(kind[k]), "I_true": round(float(it[k]), 2), "I_pred": round(float(ip[mp][k]), 2),
             "I_zero": round(float(i0[m0][k]), 2), "overlap_pred": round(float((Lt[:, k] @ Lp[:, mp[k]]) ** 2), 3),
             "overlap_zero": round(float((Lt[:, k] @ L0[:, m0[k]]) ** 2), 3), "err_pred": float(ep[k]), "err_zero": float(e0[k])} for k in range(len(ft))]
    by_kind = {kd: {"err_pred": float(ep[kind == kd].sum()), "err_zero": float(e0[kind == kd].sum()), "n": int((kind == kd).sum())}
               for kd in ("CH-str", "oop", "ip")}
    return {"rel_rms_pred": float(np.sqrt(ep.sum())), "rel_rms_zero": float(np.sqrt(e0.sum())), "by_kind": by_kind, "modes": rows}


def main():
    out, lines = {}, ["# Where λ = 1 spoils the mode shapes (exploratory, post hoc; input for the λ chain's registration)", ""]
    for mid, (name, comp) in ANCHORS.items():
        per_seed = [molecule(mid, name, comp, s) for s in (0, 1, 2)]
        out[name] = per_seed
        lines += [f"## {name}", "",
                  f"rel. rms matched: λ = 1 {np.mean([p['rel_rms_pred'] for p in per_seed]):.3f}, zero rule {per_seed[0]['rel_rms_zero']:.3f} "
                  "(check against lever 6b's read)", "", "| kind | modes | share of λ = 1 error² (seed mean) | zero rule error² |", "|---|---|---|---|"]
        for kd in ("CH-str", "oop", "ip"):
            lines.append(f"| {kd} | {per_seed[0]['by_kind'][kd]['n']} | {np.mean([p['by_kind'][kd]['err_pred'] for p in per_seed]):.4f} | "
                         f"{per_seed[0]['by_kind'][kd]['err_zero']:.4f} |")
        top = sorted(range(len(per_seed[0]["modes"])), key=lambda k: -np.mean([p["modes"][k]["err_pred"] for p in per_seed]))[:4]
        lines += ["", "| ω true | kind | I true | I λ=1 (seeds) | I zero | overlap λ=1 (seeds) | overlap zero |", "|---|---|---|---|---|---|---|"]
        for k in top:
            m = per_seed[0]["modes"][k]
            lines.append(f"| {m['freq_true']} | {m['kind']} | {m['I_true']} | {' / '.join(str(p['modes'][k]['I_pred']) for p in per_seed)} | "
                         f"{m['I_zero']} | {' / '.join(str(p['modes'][k]['overlap_pred']) for p in per_seed)} | {m['overlap_zero']} |")
        lines.append("")
    (RES / "mode_shape_diagnosis.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    (RES / "mode_shape_diagnosis.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
