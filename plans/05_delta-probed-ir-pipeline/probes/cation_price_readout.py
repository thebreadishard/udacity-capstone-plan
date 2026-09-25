"""Read-out of a cation price file (`l3_ulno_price.py` → `l3_price.json`), 25 September 2026 — obstacle 9, pre-registration of 24 September.

    python probes/cation_price_readout.py probes/results_m1/cations/benzene/l3_price.json [--neutral-s 164]

Prints one line per point (wall, ULNO-CCSD(T) share, ⟨S²⟩, peak RSS), the mean price, the indicative cost ratio against a neutral price given on the
command line (default 164 s: benzene LNO-CCSD(T)/cc-pVDZ tight on the laptop, 15 September; a different machine, so the ratio is indicative, as the
pre-registration says), and — second route for the script's own curvature line — the curvature ratio recomputed here from the three composite energies
and ω_B3LYP, against the value the price script stored. Nothing is judged; the pre-registration registers these as sanity lines."""
from __future__ import annotations

import argparse
import json
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HARTREE2CM = 219474.6313632


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("price_json")
    ap.add_argument("--neutral-s", type=float, default=164.0, help="neutral price per energy in seconds for the indicative ratio (default 164, benzene 15 Sep)")
    a = ap.parse_args()
    d = json.load(open(a.price_json, encoding="utf-8"))
    pts = [p for p in d["points"] if "e_tot_composite" in p]
    print(f"{d['row']}⁺  {d['basis']} {d['thresh']}  threads {d['threads']}  mode {d['mode']}  ω_B3LYP {d['omega_b3lyp_cm']:.1f} cm⁻¹  frozen {d['frozen']}")
    for p in pts:
        print(f"  {p['tag']}: wall {p['wall_s']:7.1f} s  ULNO-CCSD(T) {p['stages_s']['ulno_ccsd_t']:7.1f} s  fragments {p['n_fragments']}  ⟨S²⟩ {p['s2']:.3f}  "
              f"RSS {p['rss_gb']['ulno_ccsd_t']:.2f} GB  E_composite {p['e_tot_composite']:.8f}")
    if not pts:
        print("  no finished point")
        return 1
    mean_wall = sum(p["wall_s"] for p in pts) / len(pts)
    mean_ulno = sum(p["stages_s"]["ulno_ccsd_t"] for p in pts) / len(pts)
    print(f"  price: {mean_wall:.0f} s per point ({mean_wall / 60:.1f} min; {100 * mean_ulno / mean_wall:.0f} % ULNO-CCSD(T)) over {len(pts)} point(s); "
          f"indicative c = {mean_wall / a.neutral_s:.1f} × the neutral's {a.neutral_s:.0f} s (different machines)")
    E = {round(p["q"], 3): p["e_tot_composite"] for p in pts}
    if {0.0, 1.0, -1.0} <= set(E):
        omega_au = d["omega_b3lyp_cm"] / HARTREE2CM
        ratio = (E[1.0] + E[-1.0] - 2 * E[0.0]) / omega_au  # ½ω′q² at q = ±1 → second difference = ω′; divided by ω_B3LYP
        omega_prime = d["omega_b3lyp_cm"] * abs(ratio) ** 0.5
        stored = d.get("curvature_ratio_cc_over_b3lyp")
        line = f"  curvature: ratio {ratio:.3f} → ω′ {omega_prime:.0f} cm⁻¹ vs ω_B3LYP {d['omega_b3lyp_cm']:.0f} (second route, from the energies)"
        if stored is not None:
            agree = abs(stored - ratio) <= 1e-3 * max(1.0, abs(ratio))
            line += f"; stored {stored:.3f} — {'agrees' if agree else 'DISAGREES'}"
        print(line)
        grad = (E[1.0] - E[-1.0]) / 2
        print(f"  gradient term at the UKS geometry: (E₊ − E₋)/2 = {grad * 1e3:+.3f} mE_h (cancels in the curvature)")
    else:
        print(f"  curvature: waiting for points {sorted({0.0, 1.0, -1.0} - set(E))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
