"""S2 label check, step 0 of the search (18 Oct 2026, after verdict 3; exploratory, no line): is a mode's Δ_anh label a property of the
molecule, or of choices inside the VPT2 step?

    python s2_label_check.py <s2_root> --selection <selection.json> [--extra ID=DIR ...] --out <dir>

dpir.qff's labels deperturb every Fermi term inside 200 cm⁻¹ with no strength threshold (min K 0; 2,630 terms for one 16-atom molecule) and do
not diagonalise the resonance polyads. For every usable molecule the script first recomputes the stored ν (raw and symmetry-averaged
quartics) with dpir.qff.vpt2 from the stored force constants and stops if it does not reproduce them to 1e-6 cm⁻¹ — the recomputation is then
the label's own. It then recomputes Δ_anh = ν − ω per mode under
  - K0: the label as stored (window 200, min K 0);
  - K1: Martin's threshold, min K 1 cm⁻¹ (Martin et al. 1995, the usual DVPT2 setting);
  - none: no deperturbation (plain VPT2);
  - route a / route b: the stored setting with the quartic constants of one finite-difference route each instead of their mean,
and reports per mode |K0 − K1| (settings sensitivity: two legitimate DVPT2 settings), whether |K0 − none| > 3 cm⁻¹ (resonance-affected:
plain VPT2 diverges there by construction, so 'none' is a marker, not an alternative label) and |Δ(a) − Δ(b)| (numerical noise), per family.
A label whose settings sensitivity exceeds the 3 cm⁻¹ line cannot be learned to that line by any model: it is a choice, not a property.
For the largest labels it also names the partner modes that carry them: Δ_i recomputed with every force constant that involves partner k
set to zero, one k at a time; the drop is k's share (not additive across partners — a pointer, not a decomposition).
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "src"))
from s2_read import FAMILIES, LINE_LICENSE, WINDOW, load_selection, options_from_args, rms, write_atomic  # noqa: E402

from dpir.qff import coriolis_zeta, degenerate_groups, rotational_constants, symmetry_average, vpt2  # noqa: E402

FERMI_WINDOW = 200.0     # cm⁻¹, dpir.qff's default and the stored labels' setting
REPRODUCE_TOL = 1e-6     # cm⁻¹


def molecule_inputs(setting_dir):
    """Force constants, harmonic data, rotational constants and Coriolis ζ of one molecule, from its report and reference record."""
    from s1_anharmonic_level import harmonic_modes
    with open(os.path.join(setting_dir, "ref.json"), encoding="utf-8") as fh:
        ref = json.load(fh)
    symbols = ref["molecule"]["symbols"]
    geom = np.array(ref["molecule"]["geometry"], float).reshape(-1, 3)
    _omega, q = harmonic_modes(os.path.join(setting_dir, "ref.json"))
    with np.load(os.path.join(setting_dir, "qff_report.npz")) as z:
        arrays = {k: z[k] for k in z.files}
    return arrays, rotational_constants(geom, symbols), coriolis_zeta(q, symbols)


def treatments(arrays, B, zeta):
    """Δ_anh per mode under every treatment; raises when the stored ν are not reproduced."""
    w, p3 = arrays["omega_cm"], arrays["phi_ijk"]
    nu_raw, _c, _f = vpt2(w, p3, arrays["phi_iijj"], B, zeta, FERMI_WINDOW, 0.0)
    nu_sym, _c, _f = vpt2(w, p3, arrays["phi_iijj_sym"], B, zeta, FERMI_WINDOW, 0.0)
    worst = max(np.abs(nu_raw - arrays["nu_raw"]).max(), np.abs(nu_sym - arrays["nu_sym"]).max())
    if worst > REPRODUCE_TOL:
        raise ValueError(f"stored ν not reproduced (max difference {worst:.2e} cm⁻¹)")
    p4 = arrays["phi_iijj_sym"]
    out = {"K0": nu_sym - w,
           "K1": vpt2(w, p3, p4, B, zeta, FERMI_WINDOW, 1.0)[0] - w,
           "none": vpt2(w, p3, p4, B, zeta, 0.0, 0.0)[0] - w}
    pairs = [tuple(g) for g in degenerate_groups(w) if len(g) == 2]     # the pairs the report averaged over
    for route in ("a", "b"):
        p4r = symmetry_average(arrays[f"phi_iijj_route_{route}"], pairs)
        out[f"route_{route}"] = vpt2(w, p3, p4r, B, zeta, FERMI_WINDOW, 0.0)[0] - w
    return out


def partners(arrays, B, zeta, i, top=3):
    """The partner modes k whose force constants carry Δ_i: Δ_i minus Δ_i with every φ involving k zeroed, largest first."""
    w, p3, p4 = arrays["omega_cm"], arrays["phi_ijk"], arrays["phi_iijj_sym"]
    full = vpt2(w, p3, p4, B, zeta, FERMI_WINDOW, 0.0)[0][i] - w[i]
    shares = []
    for k in range(len(w)):
        if k == i:
            continue
        q3, q4 = p3.copy(), p4.copy()
        q3[k, :, :] = q3[:, k, :] = q3[:, :, k] = 0.0
        q4[k, :] = q4[:, k] = 0.0
        shares.append((k, float(w[k]), float(full - (vpt2(w, q3, q4, B, zeta, FERMI_WINDOW, 0.0)[0][i] - w[i]))))
    return sorted(shares, key=lambda s: -abs(s[2]))[:top]


def check_molecule(rec, n_partner_modes=2):
    """Per window mode of one molecule: ω, family, the label, its settings sensitivity, resonance marker and route difference; for the
    molecule's n_partner_modes largest window labels, the partners that carry them."""
    arrays, B, zeta = molecule_inputs(rec["dir"])
    t = treatments(arrays, B, zeta)
    w = arrays["omega_cm"]
    win = np.where((w >= WINDOW[0]) & (w <= WINDOW[1]))[0]
    largest = set(sorted(win, key=lambda i: -abs(t["K0"][i]))[:n_partner_modes])
    rows = []
    for i in win:
        row = {"id": rec["id"], "omega": float(w[i]), "family": str(rec["family"][i]), "label": float(t["K0"][i]), "K1": float(t["K1"][i]),
               "none": float(t["none"][i]), "settings_diff": float(abs(t["K0"][i] - t["K1"][i])),
               "resonance_affected": bool(abs(t["K0"][i] - t["none"][i]) > LINE_LICENSE),
               "route_diff": float(abs(t["route_a"][i] - t["route_b"][i]))}
        if i in largest:
            row["partners"] = partners(arrays, B, zeta, i)
        rows.append(row)
    return rows


def summarise(modes):
    """Per family: modes, share with settings sensitivity above the line, rms settings difference, share resonance-affected, rms route
    difference."""
    out = {}
    for fa in FAMILIES:
        sel = [m for m in modes if m["family"] == fa]
        if sel:
            sd = np.array([m["settings_diff"] for m in sel])
            out[fa] = {"n": len(sel), "share_settings_over_line": float((sd > LINE_LICENSE).mean()), "rms_settings_diff": rms(sd),
                       "share_resonance_affected": float(np.mean([m["resonance_affected"] for m in sel])),
                       "rms_route_diff": rms(np.array([m["route_diff"] for m in sel]))}
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("root")
    ap.add_argument("--selection", required=True)
    ap.add_argument("--extra", nargs="*", default=[])
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    by_scaf, _used, _excluded = load_selection(a.root, a.selection, options_from_args(a))
    modes, skipped = [], {}
    for rec in (m for ms in by_scaf.values() for m in ms):
        try:
            modes += check_molecule(rec)
        except ValueError as e:
            skipped[rec["id"]] = str(e)
    per_family = summarise(modes)
    res = {"fermi_window": FERMI_WINDOW, "modes": modes, "per_family": per_family, "skipped": skipped}
    lines = [f"# S2 label check — {len({m['id'] for m in modes})} molecules, {len(modes)} window modes", "",
             "| family | modes | |K0 − K1| > 3 cm⁻¹ | rms |K0 − K1| | resonance-affected | rms route difference |", "|---|---|---|---|---|---|"]
    lines += [f"| {fa} | {v['n']} | {v['share_settings_over_line']:.0%} | {v['rms_settings_diff']:.2f} | {v['share_resonance_affected']:.0%} | "
              f"{v['rms_route_diff']:.2f} |" for fa, v in per_family.items()]
    lines += ["", "| molecule | ω | family | label (K0) | K1 | |K0 − K1| | resonance-affected | route diff | partners (k: ω, share) |",
              "|---|---|---|---|---|---|---|---|---|"]
    lines += [f"| {m['id']} | {m['omega']:.0f} | {m['family']} | {m['label']:.1f} | {m['K1']:.1f} | {m['settings_diff']:.1f} | "
              f"{'yes' if m['resonance_affected'] else ''} | {m['route_diff']:.2f} | "
              + "; ".join(f"{k}: {wk:.0f}, {s:+.1f}" for k, wk, s in m["partners"]) + " |"
              for m in sorted((m for m in modes if "partners" in m), key=lambda m: -abs(m["label"]))[:20]]
    lines += [""] + [f"- skipped {i}: {why}" for i, why in skipped.items()]
    os.makedirs(a.out, exist_ok=True)
    write_atomic(os.path.join(a.out, "s2_label_check.json"), json.dumps(res, indent=1))
    write_atomic(os.path.join(a.out, "s2_label_check.md"), "\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
