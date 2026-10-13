"""The out-of-plane block on the six-anchor baseline (13 Oct 2026, TASKS 51; exploratory, before any anchor of set three is read).

Two readings from files already on disk, no training:
- **R-C as a tool** (`m05/mode_blocks.pair_rotation`): per low-symmetry anchor with a CC APT, the rotation against the truth of the pair
  `mode_blocks.oop_pair` names (the strongest out-of-plane mode and its nearest out-of-plane neighbour of the same symmetry species), for the zero rule and for each seed's TZ standard (λ = 1). The check against the exploratory diagnosis of 12 Oct: pyridine's pair
  turned ≈ 16° by B3LYP and ≈ 19–20° by λ = 1, in the same direction.
- **The arm for R-A's fail branch** (`mode_blocks.oop_couplings_from_low`): the same saved folds with the couplings between out-of-plane modes
  taken from B3LYP. Read beside λ = 1 and the zero rule: frequencies per kind of motion (C–H stretch, in plane, out of plane; modes matched by
  eigenvector) and the matched intensity rel. rms with the CC APT. This is not the registered T3 read (that pairs ω in sorted order per corpus
  family, in `rungC_cc_transfer.py`); it says what the arm does before the registered read runs it.
- **The model arm** (`mode_blocks.oop_block_from_model`, R-A's fail branch): the out-of-plane diagonal from shift = a + b·ω/1000 + c·h,
  fitted leave-one-anchor-out on the other five anchors' truth; beside it the low level with only the model's diagonal (no network). The form
  was chosen here among five (constant; a + bω; a + bω + ch; bω; bω + chω), so these numbers are not evidence for it; anchor set three is.
- **The out-of-plane diagonal** (added after the arm's read showed the positions do not move without the couplings): per out-of-plane mode of
  the low level, the first-order frequency shift ΔH_kk / 2ω_k of the truth and of each seed's prediction, in cm⁻¹; per anchor the rms of the
  difference, the slope of predicted on true through the origin, and their correlation.

Inputs: the anchors of the 10 Oct folds run (`probes/runs/t3_folds_1010.json`, the single source), its saved folds
(`out/T3_tz_folds_c34_seed{0,1,2}_2026-10-10_fold_<id>.npz`, mode head_l2), the CC APTs of lever 6/6b and benzene's.

    python probes/oop_block_read.py   → probes/results_m1/oop_block_2026-10-13/oop_block_read.{json,md}
"""
import json
import sys
from pathlib import Path

import numpy as np

PLAN = Path(__file__).resolve().parents[1]
M05 = PLAN / "modules" / "05_support_predictor"
sys.path.insert(0, str(M05 / "m05"))
import mode_blocks as MB  # noqa: E402
from rungC_intensities import match_modes, mode_intensities  # noqa: E402

sys.path.insert(0, str(PLAN / "probes"))
from e8_symmetry import point_group_ops  # noqa: E402

SPEC = PLAN / "probes" / "runs" / "t3_folds_1010.json"
FOLD = "T3_tz_folds_c34_seed{seed}_2026-10-10_fold_{mid}.npz"
FIELD = PLAN / "probes" / "results_m1" / "cc_apt_field_2026-10-12"
APTS = {"A_6e858b26e5": FIELD / "pyridine_ccpvdz_field.npz", "B_8b12a55d3a": FIELD / "fluorobenzene_ccpvdz_field.npz",
        "A_3100da3761": FIELD / "benzonitrile_ccpvdz_field.npz",
        "A_8448043181": PLAN / "probes" / "results_m1" / "e8_benzene_ccpvtz_oop_2026-10-03" / "apt_ccsd_t.npz"}
LOW_SYMMETRY = ("A_6e858b26e5", "B_8b12a55d3a", "A_3100da3761")          # benzene's symmetry fixes its shapes (9 Oct)
NAMES = {"A_8448043181": "benzene", "A_01f3186607": "naphthalene", "A_6e858b26e5": "pyridine", "B_8b12a55d3a": "fluorobenzene",
         "A_3100da3761": "benzonitrile", "A_a1e6ec1862": "anthracene"}
OUT = PLAN / "probes" / "results_m1" / "oop_block_2026-10-13"


def anchors_from_spec() -> dict:
    argv = json.load(open(SPEC, encoding="utf-8"))["steps"][0]["argv"]
    return dict(argv[i + 1].split("=", 1) for i, x in enumerate(argv) if x == "--anchor")


def kind_rms(H_true, H_test, masses, coords) -> dict:
    """ω rms per kind (CH-str > 2500 cm⁻¹, oop, ip), test modes matched to the truth's by eigenvector."""
    ft, _, Lt = mode_intensities(H_true, masses, np.zeros((3, len(masses) * 3)), return_modes=True)
    fp, _, Lp = mode_intensities(H_test, masses, np.zeros((3, len(masses) * 3)), return_modes=True)
    d = fp[match_modes(Lt, Lp)] - ft
    oop = MB.plane_split(Lt, coords)
    kind = np.where(ft > 2500, "CH-str", np.where(oop, "oop", "ip"))
    return {k: float(np.sqrt(np.mean(d[kind == k] ** 2))) for k in ("CH-str", "ip", "oop") if (kind == k).any()}


def rel_rms_matched(H_true, H_test, masses, apt) -> float:
    ft, it, Lt = mode_intensities(H_true, masses, apt, return_modes=True)
    fp, ip, Lp = mode_intensities(H_test, masses, apt, return_modes=True)
    wgt = it / it.sum()
    return float(np.sqrt(np.sum(wgt * ((ip[match_modes(Lt, Lp)] - it) / np.maximum(it, 1.0)) ** 2)))   # the read-out's own terms


def oop_diagonal(H_low, dH_true, dH_pred, masses, coords) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """(ω_low, true shift, predicted shift) of the low level's out-of-plane vibrations, first order: ΔH_kk / (2 ω_k) in cm⁻¹."""
    w, V = np.linalg.eigh(MB.mass_weighted(H_low, masses))
    f = np.sign(w) * np.sqrt(np.abs(w)) * MB.HARTREE2CM
    vib = np.abs(f) > MB.VIB_MIN_CM
    Vv, fv = V[:, vib], f[vib]
    oop = MB.plane_split(Vv, coords)
    sh = [np.einsum("ik,ij,jk->k", Vv[:, oop], MB.mass_weighted(d, masses), Vv[:, oop]) * MB.HARTREE2CM ** 2 / (2 * fv[oop]) for d in (dH_true, dH_pred)]
    return fv[oop], sh[0], sh[1]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    res, lines = {}, ["# The out-of-plane block on the six-anchor baseline (exploratory, 13 Oct 2026)", "",
                      "Saved λ = 1 folds of 10 Oct; ω matched by eigenvector per kind (not the registered sorted-family read).", ""]
    rc_lines = ["## R-C: the strongest out-of-plane mode and its nearest partner of the same species", "",
                "| anchor | pair (cm⁻¹, truth) | θ zero rule | θ λ = 1 (seeds) | κ λ = 1 (cm⁻¹) | κ zero (cm⁻¹) | gap λ = 1 (cm⁻¹) | captured λ = 1 |",
                "|---|---|---|---|---|---|---|---|"]
    dg_lines = ["## The out-of-plane diagonal: first-order shifts ΔH_kk / 2ω_k (cm⁻¹), predicted (λ = 1) against true", "",
                "| anchor | oop modes | true shift rms | error rms (seeds) | slope pred/true (seeds) | correlation (seeds) |", "|---|---|---|---|---|---|"]
    arm_lines = ["## The arms: out-of-plane couplings from B3LYP; the out-of-plane block from the model", "",
                 "| anchor | read | zero rule | λ = 1 | λ = 1, oop couplings from B3LYP | B3LYP + model diagonal | λ = 1, oop block from the model |",
                 "|---|---|---|---|---|---|---|"]
    spec = anchors_from_spec()
    shift_rows = {}
    for mid, truth in spec.items():                                     # the model arm's training data: every anchor's true out-of-plane shifts
        g = json.load(open(M05 / "corpus" / "molecules" / mid / "geometry.json", encoding="utf-8"))
        H_low = np.load(M05 / "out" / FOLD.format(seed=0, mid=mid), allow_pickle=True)["H_low"]
        Vo, fo, h = MB.oop_modes(H_low, np.asarray(g["masses_amu"], float), np.asarray(g["coords_bohr"], float), g["symbols"])
        shift_rows[mid] = (fo, h, MB.oop_shifts(np.load(truth)["H_projected"] - H_low, Vo, fo, np.asarray(g["masses_amu"], float)))
    for mid, truth in spec.items():
        g = json.load(open(M05 / "corpus" / "molecules" / mid / "geometry.json", encoding="utf-8"))
        masses, coords = np.asarray(g["masses_amu"], float), np.asarray(g["coords_bohr"], float)
        H_true = np.load(truth)["H_projected"]
        folds = [np.load(M05 / "out" / FOLD.format(seed=s, mid=mid), allow_pickle=True) for s in (0, 1, 2)]
        if any(str(f["mode"]) != "head_l2" for f in folds):
            raise SystemExit(f"{mid}: a saved fold is not the TZ standard (head_l2)")
        H_low = folds[0]["H_low"]
        preds = [H_low + f["dH_pred"] for f in folds]
        arms = [H_low + MB.oop_couplings_from_low(f["dH_pred"], H_low, masses, coords) for f in folds]
        coef = MB.fit_oop_shift([v for k, v in shift_rows.items() if k != mid])
        models = [H_low + MB.oop_block_from_model(f["dH_pred"], H_low, masses, coords, g["symbols"], coef) for f in folds]
        model_only = H_low + MB.oop_block_from_model(np.zeros_like(H_low), H_low, masses, coords, g["symbols"], coef)
        r = {"name": NAMES.get(mid, mid)}
        dg = [oop_diagonal(H_low, H_true - H_low, f["dH_pred"], masses, coords) for f in folds]
        st = dg[0][1]
        r["oop_diagonal"] = {"omega_low": dg[0][0].tolist(), "true": st.tolist(), "pred": [d[2].tolist() for d in dg]}
        dg_lines.append(f"| {r['name']} | {len(st)} | {np.sqrt(np.mean(st ** 2)):.1f} | "
                        f"{' / '.join(f'{np.sqrt(np.mean((d[2] - st) ** 2)):.1f}' for d in dg)} | "
                        f"{' / '.join(f'{(d[2] @ st) / (st @ st):.2f}' for d in dg)} | {' / '.join(f'{np.corrcoef(d[2], st)[0, 1]:.2f}' for d in dg)} |")
        r["omega"] = {"zero": kind_rms(H_true, H_low, masses, coords), "lambda1": [kind_rms(H_true, p, masses, coords) for p in preds],
                      "arm": [kind_rms(H_true, a, masses, coords) for a in arms], "model": [kind_rms(H_true, x, masses, coords) for x in models],
                      "model_only": kind_rms(H_true, model_only, masses, coords)}
        r["oop_model_coef"] = [float(c) for c in coef]
        for k in r["omega"]["zero"]:
            arm_lines.append(f"| {r['name']} | ω rms {k} (cm⁻¹) | {r['omega']['zero'][k]:.2f} | "
                             f"{np.mean([x[k] for x in r['omega']['lambda1']]):.2f} | {np.mean([x[k] for x in r['omega']['arm']]):.2f} | "
                             f"{r['omega']['model_only'][k]:.2f} | {np.mean([x[k] for x in r['omega']['model']]):.2f} |")
        if mid in APTS:
            apt = np.asarray(np.load(APTS[mid])["apt"], float)
            r["intensity"] = {"zero": rel_rms_matched(H_true, H_low, masses, apt), "lambda1": [rel_rms_matched(H_true, p, masses, apt) for p in preds],
                              "arm": [rel_rms_matched(H_true, a, masses, apt) for a in arms], "model": [rel_rms_matched(H_true, x, masses, apt) for x in models],
                              "model_only": rel_rms_matched(H_true, model_only, masses, apt)}
            arm_lines.append(f"| {r['name']} | intensity rel. rms, matched (CC APT) | {r['intensity']['zero']:.3f} | "
                             f"{np.mean(r['intensity']['lambda1']):.3f} | {np.mean(r['intensity']['arm']):.3f} | {r['intensity']['model_only']:.3f} | "
                             f"{np.mean(r['intensity']['model']):.3f} |")
            if mid in LOW_SYMMETRY:
                pair = MB.oop_pair(H_true, masses, apt, coords, point_group_ops(g["symbols"], coords))
                if pair is None:
                    rc_lines.append(f"| {r['name']} | no partner of the strongest mode's species | | | | | | |")
                    res[mid] = r
                    continue
                k, l = pair
                z = MB.pair_rotation(H_true, H_low, masses, k, l)
                ps = [MB.pair_rotation(H_true, p, masses, k, l) for p in preds]
                r["pair"] = {"zero": z, "lambda1": ps}
                rc_lines.append(f"| {r['name']} | {z['freq_true'][0]} / {z['freq_true'][1]} | {z['theta_deg']:+.1f}° | "
                                f"{' / '.join(f'{p['theta_deg']:+.1f}°' for p in ps)} | {np.mean([p['kappa_cm'] for p in ps]):+.2f} | "
                                f"{z['kappa_cm']:+.2f} | {np.mean([p['gap_cm'] for p in ps]):+.1f} | {min(p['captured'] for p in ps):.3f} |")
        res[mid] = r
    lines += rc_lines + [""] + arm_lines + [""] + dg_lines + [""]
    (OUT / "oop_block_read.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    (OUT / "oop_block_read.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
