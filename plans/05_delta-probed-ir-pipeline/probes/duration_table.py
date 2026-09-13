"""Duration table (2026-09-13): how long every computation of plan 05 through Module 08 takes on the laptop, on the desktop of the hardware
note, and on Snellius — from measured prices where they exist (m) and labelled estimates where they do not (e). Printed, not asserted.

Two open places, filled from files when they exist:
  F   = the xtight/tight factor at naphthalene = (sum of fragment times of the running xtight energy) / 41,375 s. Until the run ends the
        script projects the sum from the checkpoint (fragments done + the mirror of their symmetry partners) and marks it PROVISIONAL.
  g   = the gradient-to-energy cost ratio (M2a). Not used in the baseline table (energies only); when results_m2a/ exists the script prints a
        second block: the R1 deck by 18 gradients (plan 06 X14) as 18·g energies.
Conventions: a deck under the symmetry prior costs 4M + 2E energies (M modes, E same-irrep pairs; naphthalene 4·48 + 2·141 = 474 = proposal §3.2);
E is measured for benzene (47) and naphthalene (141, plan 06 X13) and estimated as M²/(2|G|) above (that formula gives 144 at naphthalene).
Output: probes/results_timing/DURATION_TABLE.md and .json. Every number carries its (m)/(e) flag and its source."""
import json
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "results_timing"
DAY = 24.0

# ---- measured inputs (m), with sources
M = {
    "benzene_TZ_xtight_energy_h": (76 / 60, "results_m1/XTIGHT_READIN.md: 4,576 s per frozen-arm point"),
    "naphthalene_TZ_tight_energy_h": (41375 / 3600, "results_timing/naphthalene_cc-pvtz_tight.json"),
    "R0_deck_energies": (448, "dry run REPORT, mode E K at sigma_E = 1 uEh, c = 3"),
    "R1_deck_energies": (474, "proposal 3.2: 96 + 96 + 282; X13: 141 eligible pairs"),
    "sigma_run_energies": (10, "decision 35: 9 points + reference, tight, one mode"),
    "corpus_hessians": (11321, "Module 05 corpus factory candidates"),
    "corpus_min_per_hessian": ((3, 7), "Module 05 timing (B3LYP/6-31G*), P13 memo 4"),
    "benzene_B3LYP_hessian_s": (388, "dry run stageA.json timing (psi4, 8 threads)"),
}
# ---- estimates (e), with rules
E = {
    "desktop_speedup_vs_laptop": ((11.5 / 5, 11.5 / 3), "P13 memo: 3-5 h per naphthalene tight energy on 16 cores, from the core count; never timed"),
    "snellius_node_speedup_vs_laptop": ((11.5 / 2.5, 11.5 / 1.5), "Budget Snellius note: 1.5-2.5 h wall per naphthalene tight energy on one thin node"),
    "snellius_nodes_parallel": (4, "Small Compute application; decks are embarrassingly parallel over energies"),
    "R2_energy_factor_vs_naphthalene": ((5, 10), "Budget R2 row: per energy an unmeasured 5-10 x naphthalene"),
    "R3_energy_factor_vs_naphthalene": ((25, 100), "extrapolation: the R2 step applied twice (coronene 102 modes, 36 atoms); no measurement of any kind"),
    "modes": {"pyrene": 72, "chrysene": 84, "triphenylene": 84, "tetracene": 84, "coronene": 102},
    "group_order": {"pyrene": 8, "chrysene": 4, "triphenylene": 12, "tetracene": 8, "coronene": 24},
    "naphthalene_dft_stageA_h": ((2, 4), "two psi4 Hessians of 18 atoms at the dry run's grid; benzene took 388 s per Hessian"),
    "m2a_days": (0.3, "pre-registration: cells 0-4 in one evening"),
}


def provisional_F():
    """Sum of fragment times from the checkpoint; the 9 missing fragments mirrored from their symmetry partners (1..12 <-> 13..24 by observed pairs)."""
    ck = OUT / "naphthalene_cc-pvtz_xtight_fragments.json"
    if not ck.exists():
        return None, "no checkpoint"
    d = json.load(open(ck)); fr = {int(k): v for k, v in d["fragments"].items()}
    done = sum(v["t_s"] for v in fr.values())
    # observed pairing from the log: (1,3,6 big), (2,4), (5,7,11,14), (8 biggest), (9,13), (10,12,15) -> mirror missing by nearest LAS size class
    sizes = {k: v["n_mo_frag"] for k, v in fr.items()}
    by_size = {}
    for k, v in fr.items():
        by_size.setdefault(v["n_mo_frag"], []).append(v["t_s"])
    missing = 24 - len(fr)
    # remaining fragments assumed to follow the observed size distribution: average time per fragment so far
    avg = done / len(fr)
    total = done + missing * avg
    F = total / 41375
    return F, f"PROVISIONAL: {len(fr)} of 24 fragments done, sum {done/3600:.1f} h; remaining {missing} at the observed mean {avg/60:.0f} min -> total {total/3600:.1f} h -> F = {F:.2f}"


def rng(x):
    return x if isinstance(x, tuple) else (x, x)


def main():
    F, Fnote = provisional_F()
    F = F or 4.0
    t_ben = M["benzene_TZ_xtight_energy_h"][0]
    t_nap_tight = M["naphthalene_TZ_tight_energy_h"][0]; t_nap = t_nap_tight * F
    dsk = E["desktop_speedup_vs_laptop"][0]; sn = E["snellius_node_speedup_vs_laptop"][0]; P = E["snellius_nodes_parallel"][0]
    def days(hours_lo, hours_hi, fits_laptop=True):
        lap = (hours_lo / DAY, hours_hi / DAY) if fits_laptop else None
        pc = (hours_lo / dsk[1] / DAY, hours_hi / dsk[0] / DAY)
        sl = (hours_lo / sn[1] / DAY / P, hours_hi / sn[0] / DAY / P)
        return lap, pc, sl
    rows = []
    def add(step, calc, hours, fits=True, flag="m", note=""):
        lo, hi = rng(hours); lap, pc, sl = days(lo, hi, fits); rows.append({"step": step, "calc": calc, "laptop_d": lap, "pc_d": pc, "snellius_d": sl, "flag": flag, "note": note})
    # R0
    add("R0 pilot (benzene)", f"{M['R0_deck_energies'][0]} LNO-CCSD(T)/cc-pVTZ xtight energies at {t_ben*60:.0f} min (m)", M["R0_deck_energies"][0] * t_ben, flag="m")
    add("naphthalene DFT dry run, stage A", "two psi4 Hessians (B3LYP, BHHLYP) at 6-31G*", E["naphthalene_dft_stageA_h"][0], flag="e", note="B3LYP half exists (plan 02); psi4 runs on Windows, not on Snellius as installed")
    add("R1 smoothness sigma run (decision 35)", f"{M['sigma_run_energies'][0]} naphthalene tight energies at 11.5 h (m)", M["sigma_run_energies"][0] * t_nap_tight, flag="m")
    add("M2a (gradient cost ratio g)", "PySCFAD cells 0-4, benzene cc-pVDZ", E["m2a_days"][0] * DAY, flag="e", note="laptop only (installed there); decides whether M2 is built")
    add("R1 deck (naphthalene)", f"{M['R1_deck_energies'][0]} xtight energies at {t_nap:.0f} h = 11.5 h x F, F = {F:.2f} ({'provisional' if 'PROVISIONAL' in Fnote else 'measured'})", M["R1_deck_energies"][0] * t_nap, flag="m/F")
    # R2, R3
    tot2 = [0.0, 0.0]
    for mol in ("pyrene", "chrysene", "triphenylene", "tetracene"):
        Mm = E["modes"][mol]; Ee = Mm * Mm / (2 * E["group_order"][mol]); deck = 4 * Mm + 2 * Ee
        f = E["R2_energy_factor_vs_naphthalene"][0]
        hrs = (deck * t_nap * f[0], deck * t_nap * f[1]); tot2[0] += hrs[0]; tot2[1] += hrs[1]
        add(f"R2 {mol}", f"deck ~{deck:.0f} energies (4M + 2E, E ~ M^2/2|G| = {Ee:.0f}) at {f[0]}-{f[1]} x the naphthalene energy", hrs, fits=False, flag="e", note="does not fit the laptop's 25 GB")
    Mm = E["modes"]["coronene"]; Ee = Mm * Mm / (2 * E["group_order"]["coronene"]); deck = 4 * Mm + 2 * Ee; f = E["R3_energy_factor_vs_naphthalene"][0]
    add("R3 coronene", f"deck ~{deck:.0f} energies at {f[0]}-{f[1]} x the naphthalene energy (extrapolation)", (deck * t_nap * f[0], deck * t_nap * f[1]), fits=False, flag="e (extrapolated)", note="no measurement of any kind behind the factor")
    # Module 05 corpus
    cm = M["corpus_min_per_hessian"][0]; ch = (M["corpus_hessians"][0] * cm[0] / 60, M["corpus_hessians"][0] * cm[1] / 60)
    rows.append({"step": "Module 05 corpus factory", "calc": f"{M['corpus_hessians'][0]} B3LYP/6-31G* Hessians at {cm[0]}-{cm[1]} min (m, per Hessian)",
                 "laptop_d": (ch[0] / DAY, ch[1] / DAY), "pc_d": (ch[0] / DAY, ch[1] / DAY), "snellius_d": (ch[0] / DAY / (P * 16), ch[1] / DAY / (P * 16)), "flag": "m/e",
                 "note": "same per-Hessian time on laptop and desktop (8 threads each; the laptop is busy with the anchor); Snellius: 4 nodes x 16 concurrent jobs assumed"})
    for step, calc in (("Module 05 training", "the Transformer on the corpus (CPU/GPU)"), ("Module 06 generative proposer", "DFT-only corpora, no coupled-cluster cost"),
                       ("Module 07 campaign officer", "orchestration and cost record"), ("Module 08 assembly", "scoring R0-R3, no new energies"),
                       ("R6 fragment-probed C384H48 (if licensed)", "56 symmetry-unique fragments (Module 02) x an unmeasured per-fragment cost at that size")):
        rows.append({"step": step, "calc": calc, "laptop_d": None, "pc_d": None, "snellius_d": None, "flag": "not measured", "note": "hours, not days, for training/proposer/officer/assembly; R6 not estimable before R2-R3 fragment timings"})
    out = {"date": f"{datetime.now():%Y-%m-%d %H:%M}", "F": F, "F_note": Fnote, "measured": {k: v for k, v in M.items()}, "estimates": {k: (v if not isinstance(v, dict) else v) for k, v in E.items()}, "rows": rows}
    OUT.mkdir(exist_ok=True); json.dump(out, open(OUT / "duration_table.json", "w"), indent=1, default=str)
    fmt = lambda r: "does not fit" if r is None else (f"{r[0]:.1f}" if abs(r[0] - r[1]) < 0.05 * max(r[1], 1e-9) else f"{r[0]:.0f}-{r[1]:.0f}" if r[1] >= 10 else f"{r[0]:.1f}-{r[1]:.1f}")
    L = [f"# Duration table — plan 05 through Module 08 ({out['date']})", "",
         f"Naphthalene xtight factor F = {F:.2f} — {Fnote}. Desktop = the hardware note's 16-core machine, {dsk[0]:.1f}-{dsk[1]:.1f} x the laptop (e, from the core count); "
         f"Snellius = {P} thin nodes in parallel, each {sn[0]:.1f}-{sn[1]:.1f} x the laptop (e, Budget note). (m) measured, (e) estimated; every rule is in `probes/duration_table.py`.", "",
         "| step | computation | days on laptop | days on desktop | days on Snellius (4 nodes) | status | note |", "|---|---|---|---|---|---|---|"]
    for r in rows:
        if r["laptop_d"] is None and r["flag"] == "not measured":
            L.append(f"| {r['step']} | {r['calc']} | — | — | — | not measured | {r['note']} |")
        else:
            L.append(f"| {r['step']} | {r['calc']} | {fmt(r['laptop_d'])} | {fmt(r['pc_d'])} | {fmt(r['snellius_d'])} | {r['flag']} | {r['note']} |")
    # totals of the estimable rows
    def tot(key, skip_none=True):
        lo = hi = 0.0; miss = []
        for r in rows:
            v = r[key]
            if v is None:
                if r["flag"] != "not measured": miss.append(r["step"])
                continue
            lo += v[0]; hi += v[1]
        return lo, hi, miss
    for key, name in (("laptop_d", "laptop"), ("pc_d", "desktop"), ("snellius_d", "Snellius, 4 nodes")):
        lo, hi, miss = tot(key)
        L.append(f"| **total of estimable rows** | | " + ("" if key != "laptop_d" else "") + f"{'**' + f'{lo:.0f}-{hi:.0f}' + '**' if key == key else ''} | | | | " + (f"excluding rows that do not fit: {', '.join(miss)}" if miss else "") + " |") if False else None
    tl = tot("laptop_d"); tp = tot("pc_d"); ts = tot("snellius_d")
    L += ["", f"**Totals of the estimable rows (days):** laptop {tl[0]:.0f}-{tl[1]:.0f} for what fits (R2-R3 do not: {', '.join(tl[2])}); desktop {tp[0]:.0f}-{tp[1]:.0f}; Snellius on 4 nodes {ts[0]:.0f}-{ts[1]:.0f}. "
          f"The R3 row alone is {rows[[r['step'] for r in rows].index('R3 coronene')]['pc_d'][0]:.0f}-{rows[[r['step'] for r in rows].index('R3 coronene')]['pc_d'][1]:.0f} desktop-days on an extrapolated factor; without R3 the desktop total is "
          f"{tp[0] - rows[[r['step'] for r in rows].index('R3 coronene')]['pc_d'][0]:.0f}-{tp[1] - rows[[r['step'] for r in rows].index('R3 coronene')]['pc_d'][1]:.0f} days.", "",
          "Open places: F (final when the xtight run ends; this table re-runs itself), g (M2a; when `results_m2a/` exists a gradient block is printed: R1 by 18 gradients = 18 g energy-equivalents, plan 06 X14). "
          "Levers not in the table: tight thresholds instead of xtight (÷ F, decision 20 reversed), P25 (deck ÷ ~1.6, after its licence test), gradients (M2)."]
    m2a = OUT.parent / "results_m2a"
    if m2a.exists() and any(m2a.glob("m2a_*.json")):
        L.append("\n(gradient block: results_m2a present — extend here)")
    (OUT / "DURATION_TABLE.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L).encode("ascii", "replace").decode())


if __name__ == "__main__":
    main()
