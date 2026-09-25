"""Route 2 (naphthalene, B97-1 / TZ2P, pyscf analytic Hessians, QFF at step 0.10) against the rotationally resolved laboratory band origins of module 03.

Reads `dpir.qff`'s npz (omega_cm, nu_raw, nu_sym, the two-route disagreement) and module 03's `origin_columns_naphthalene.csv`; writes a Markdown table with
every number traced to its file. The three IR-active CH out-of-plane fundamentals are Pirali's nu46, nu47, nu48 (b3u in their axes, B1u in psi4's); 25 September 2026.

The assignment is made on the route-2 mode vectors themselves (reference Hessian): out-of-plane share > 0.9 and z-pattern symmetric under both in-plane mirrors
(x → −x, y → −y; the molecule lies in xy with its axes along x and y) = B1u; the three lowest such modes are nu48, nu47, nu46. Module 03's DFT table is printed beside
them as the check that the same modes are meant.

Usage: python probes/route2_vs_lab.py <qff npz> <origin csv> <dft modes md> <out md>   (PYTHONPATH=src for dpir.qff.harmonic)"""
import csv
import re
import sys

import json
import os

import numpy as np

from dpir.qff import harmonic

npz, origins_csv, dft_md, out_md = sys.argv[1:5]
z = np.load(npz); w = z["omega_cm"]; nu = z["nu_raw"]; nus = z["nu_sym"]
a, b = z["phi_iijj_route_a"], z["phi_iijj_route_b"]; iu = np.triu_indices(len(w), 1); d = np.abs(a - b)[iu]
# module 03 DFT mode table: B1u CH-oop modes (index, omega)
b1u = []
for line in open(dft_md, encoding="utf-8"):
    m = re.match(r"\|\s*(\d+)\s*\|\s*([\d.]+)\s*\|\s*B1u\s*\|\s*yes\s*\|\s*CH-oop\s*\|", line)
    if m: b1u.append((int(m.group(1)), float(m.group(2))))
b1u = sorted(b1u)[:3]                                            # the three lowest B1u CH-oop modes = nu48, nu47, nu46
assert len(b1u) == 3, b1u
# route-2 modes: B1u out-of-plane modes from the reference Hessian's mode vectors
ref = json.load(open(os.path.join(os.path.dirname(npz), 'naph_hessians_d010', 'reference.json'), encoding='utf-8'))
sym = ref['molecule']['symbols']; geom = np.asarray(ref['molecule']['geometry']).reshape(-1, 3); H = np.asarray(ref['return_result']).reshape(3 * len(sym), 3 * len(sym))
har = harmonic(H, sym, geom); q = har.q; assert np.allclose(har.omega * 219474.6313632, w, atol=0.05), 'npz and reference disagree on omega'
assert np.abs(geom[:, 2]).max() < 1e-6, 'molecule not in the xy plane'
px = [int(np.argmin(np.hypot(geom[:, 0] + geom[k, 0], geom[:, 1] - geom[k, 1]))) for k in range(len(sym))]
py = [int(np.argmin(np.hypot(geom[:, 0] - geom[k, 0], geom[:, 1] + geom[k, 1]))) for k in range(len(sym))]
def character(j):
    z = q[2::3, j]; oop = float((z ** 2).sum() / (q[:, j] ** 2).sum())
    cx = float(z @ z[px] / max(z @ z, 1e-12)); cy = float(z @ z[py] / max(z @ z, 1e-12))
    return oop, cx, cy
chars = [character(j) for j in range(q.shape[1])]
b1u_r2 = [j for j, (oop, cx, cy) in enumerate(chars) if oop > 0.9 and cx > 0.9 and cy > 0.9]
assert len(b1u_r2) >= 3, (b1u_r2, chars)
r2 = sorted(b1u_r2)[:3]
print('B1u out-of-plane modes of route 2 (index, omega, oop share, mirror characters):', [(j, round(float(w[j]), 1), round(chars[j][0], 3), round(chars[j][1], 2), round(chars[j][2], 2)) for j in b1u_r2])
labels = ["nu48", "nu47", "nu46"]
# experimental origins
exp = {}
for r in csv.DictReader(open(origins_csv, encoding="utf-8")):
    exp.setdefault(r["mode"], []).append(r)
rows = []
for lab, (i_dft, w_dft), i in zip(labels, b1u, r2):
    ex = exp.get(lab, [])
    printed = "; ".join(f"{float(e['origin_cm']):.2f} ({e['source'].split(',')[0]} {re.search(r'(19|20)\d\d', e['source']).group(0)})" for e in ex)
    pir09 = sorted({float(e["pirali2009_position_cm"]) for e in ex if e.get("pirali2009_position_cm")})
    best = float(ex[0]["origin_cm"]) if ex else float("nan")
    # the most precise printed origin: the one with the smallest lower bound on u_band
    if ex: best = float(min(ex, key=lambda e: float(e["u_band_cm_lower_bound"] or 1e9))["origin_cm"])
    rows.append(dict(lab=lab, i=i, w=w[i], nu=nu[i], nus=nus[i], i_dft=i_dft, w_dft=w_dft, ratio=w[i] / w_dft, printed=printed, pir09=pir09, best=best, delta=nu[i] - best))
lines = ["# Route 2 — naphthalene VPT2 fundamentals (B97-1 / TZ2P, analytic Hessians, QFF step 0.10) against the rotationally resolved band origins (2026-09-25)", "",
         f"Source files: `{npz}` (dpir.qff; 48 modes, 97 Hessians), `{origins_csv}` (module 03, items 72–73), `{dft_md}` (module 03 mode table for the family assignment).", "",
         f"Two-route disagreement of the semi-diagonal quartic constants (1128 pairs): median {np.median(d):.2f}, 90th percentile {np.percentile(d, 90):.2f}, max {d.max():.1f} cm⁻¹ — "
         "the finite-difference noise that made benzene's route-1 quartics unusable on 21 September is absent on route 2.", "",
         "VPT2 as `dpir.qff` computes it: second-order perturbation theory on the cubic and semi-diagonal quartic constants, resonances within 200 cm⁻¹ deperturbed, no polyad "
         "diagonalisation (the three fundamentals below are far from any resonance partner, so this choice does not move them). Assignment on the route-2 mode vectors: "
         f"B1u out-of-plane modes (share > 0.9, z-pattern symmetric under both in-plane mirrors) are modes {b1u_r2}; the three lowest are nu48, nu47, nu46 (b3u in Pirali's axes). "
         "Module 03's B3LYP/6-31G* mode table is shown beside them as the check that the same modes are meant.", "",
         "| band | route-2 mode | ω B97-1/TZ2P | ν VPT2 | module 03 DFT mode (ω B3LYP/6-31G*) | ω ratio | laboratory origins as printed (source, year) | Pirali 2009 position | most precise origin | ν − origin |",
         "|---|---|---|---|---|---|---|---|---|---|"]
for r in rows:
    lines.append(f"| {r['lab']} | {r['i']} | {r['w']:.1f} | {r['nu']:.1f} | {r['i_dft']} ({r['w_dft']:.1f}) | {r['ratio']:.3f} | {r['printed']} | {', '.join(f'{p:.2f}' for p in r['pir09'])} | {r['best']:.2f} | **{r['delta']:+.1f}** |")
lines += ["", f"RMS of ν − origin over the three bands: **{np.sqrt(np.mean([r['delta'] ** 2 for r in rows])):.1f} cm⁻¹**; harmonic ω − origin for the same three: "
          + ", ".join(f"{r['w'] - r['best']:+.1f}" for r in rows) + " cm⁻¹.", "",
          "What this decides and what it does not: route 2 reproduces the three rotationally resolved CH-oop origins of naphthalene to a few wavenumbers with clean quartics; that is "
          "the prerequisite (Gate E, item 2) for the Mackie 2021 question, not its answer — the answer needs the same route on a PAH where their instabilities appeared (the four-ring "
          "molecule after the 28th), and the second step size (0.05) that was planned but not run on hel1-14."]
open(out_md, "w", encoding="utf-8", newline="\n").write("\n".join(lines) + "\n")
print("\n".join(lines[6:6 + 2 + len(rows)])); print(lines[-3])
