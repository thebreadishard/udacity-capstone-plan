"""Lever 5 of the 12 Oct odds (the user, 12 Oct: 'prijs hefboom 5 maar'): what analytic DFT labels (B3LYP + ωB97X Hessians, the labels
route's `analytic_hessians.py`) cost for PAHs of 34–60 atoms, from the labels server's own lane times (387 molecules, 8–30 atoms, four lanes
of 8 threads on the CCX53). Time is fitted as a power of the number of basis functions (6-31G*, Cartesian d), over all molecules and over the
larger half; the prediction is the band between the two exponents (+ 10 % for a pyscf geometry optimisation, an allowance, not measured).

    python probes/price_large_labels.py     (reads probes/results_m1/large_labels_price_2026-10-12/labels_lane_times.json, writes price.json)
"""
import json
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "results_m1", "large_labels_price_2026-10-12")
NBAS = {"H": 2, "C": 15, "N": 15, "O": 15, "F": 15, "S": 19, "Cl": 19}      # 6-31G*, Cartesian d
CCX53_EUR_PER_H = 0.855                                                     # console price, 3 Oct 2026 (memory 'Hetzner servers')
LANES = 4                                                                   # the labels server's lanes of 8 threads on 32 vCPU
OPT_ALLOWANCE = 1.10
# The mandate's four shape molecules (jet-cooled spectra, Lemmens et al. 2021) are evaluation molecules: a held-out size test, never training.
TEST = {"coronene": (24, 12), "peropyrene": (26, 14), "ovalene": (32, 14), "hexa-peri-hexabenzocoronene": (42, 18)}
# A size grid for training molecules of other scaffolds (examples by formula; the selection rule comes with the registration).
TRAIN = {"benzo[ghi]perylene C22H12": (22, 12), "dibenzopyrene C24H14": (24, 14), "benzo[a]coronene C28H14": (28, 14),
         "tribenzoperylene C28H16": (28, 16), "dibenzocoronene C32H16": (32, 16), "circumbiphenyl C38H16": (38, 16)}


def nbas(symbols):
    return sum(NBAS[s.capitalize()] for s in symbols)


def fit(n, t):
    """log t = p log n + c; returns (p, c)."""
    p, c = np.polyfit(np.log(n), np.log(t), 1)
    return float(p), float(c)


def main():
    rows = json.load(open(os.path.join(OUT, "labels_lane_times.json")))
    n = np.array([nbas(r["symbols"]) for r in rows], float)
    t = np.array([r["seconds"] for r in rows], float)
    fits = {"all": fit(n, t), "larger_half": fit(n[n >= np.median(n)], t[n >= np.median(n)])}
    out = {"molecules": len(rows), "nbas_range": [int(n.min()), int(n.max())], "fits": {k: {"exponent": v[0]} for k, v in fits.items()},
           "lane_hours": {}, "notes": "lane = 8 threads on the CCX53 with three other lanes busy; + 10 % optimisation allowance"}

    def hours(nb):
        return sorted(float(np.exp(p * np.log(nb) + c)) / 3600 * OPT_ALLOWANCE for p, c in fits.values())

    for group, mols in (("test", TEST), ("train", TRAIN)):
        for name, (c, h) in mols.items():
            nb = 15 * c + 2 * h
            out["lane_hours"][name] = {"group": group, "atoms": c + h, "nbas": nb, "hours": [round(x, 1) for x in hours(nb)]}
    for group in ("test", "train"):
        lo = sum(v["hours"][0] for v in out["lane_hours"].values() if v["group"] == group)
        hi = sum(v["hours"][1] for v in out["lane_hours"].values() if v["group"] == group)
        out[f"{group}_total"] = {"lane_hours": [round(lo), round(hi)], "ccx53_days": [round(lo / LANES / 24, 1), round(hi / LANES / 24, 1)],
                                 "eur": [round(lo / LANES * CCX53_EUR_PER_H), round(hi / LANES * CCX53_EUR_PER_H)]}
    json.dump(out, open(os.path.join(OUT, "price.json"), "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
