"""Module 03 — family labels by DFT mode vector for naphthalene (2026-09-13), in place of the frequency-window rule.

The scoreboard owed "family labels by DFT mode vector (naphthalene dry-run mode table)". The B3LYP/6-31G* half of that dry run exists in
plan 02's stored Hessian (git 57a7910; geometry identical to plan 05's `results_dryrun/naphthalene/geometry.json` within 5e-4 bohr, checked
2026-09-13), and families depend only on the low-level modes, so the table can be built now; the BHHLYP half changes nothing here.

Uses plan 06's X13 analysis unchanged (inertial frame, D2h characters, the dry run's `assign_families` rule) and adds what the scoreboard
needs: IR activity (in D2h only B1u, B2u, B3u modes carry a dipole derivative), the Module-03 frequency-window label the same mode would
have received, and where the two labels disagree. Output: `out/naphthalene_dft_modes.csv` and `.md`. Frequencies are unscaled harmonic
B3LYP/6-31G*; the scoreboard's band assignment must scale or match them explicitly (not done here).
Every number printed comes from the files; constants in CONSTANTS."""
import csv
import json
import sys
import tempfile
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path.insert(0, str(REPO / "plans/06_equivalent-faster-mathematics/experiments"))
from x13_naphthalene_mode_table import analyse, load_from_git, CONSTANTS as X13C  # noqa: E402
sys.path.insert(0, str(HERE))
from build_lab_tables import family as window_family  # noqa: E402

CONSTANTS = {"source": "plan 02 git 57a7910, probes/results_dft_locality/naphthalene.npz (B3LYP/6-31G*, psi4)", "ir_active_irreps_D2h": ["B1u", "B2u", "B3u"],
             "family_rule": "plan 05 dryrun_dft_delta_recovery.assign_families (frequency window + out-of-plane share + hydrogen share), via plan 06 X13",
             "window_rule": "Module 03 build_lab_tables.FAMILY_RULE applied to the unscaled harmonic frequency"}


def main():
    with tempfile.TemporaryDirectory() as tmp:
        r = analyse("naphthalene", load_from_git(X13C["files"]["naphthalene"], tmp))
    rows = []
    for m in r["modes"]:
        rows.append({"mode": m["k"], "freq_B3LYP_unscaled_cm": m["freq_cm"], "irrep_D2h": m["irrep"], "ir_active": m["irrep"] in CONSTANTS["ir_active_irreps_D2h"],
                     "family_mode_vector": m["family"], "family_window_rule": window_family(m["freq_cm"])})
    out = HERE / "out"; out.mkdir(exist_ok=True)
    with open(out / "naphthalene_dft_modes.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    fams = sorted(set(x["family_mode_vector"] for x in rows))
    summ = []
    for fam in fams:
        sel = [x for x in rows if x["family_mode_vector"] == fam]
        summ.append({"family": fam, "modes": len(sel), "ir_active": sum(x["ir_active"] for x in sel), "nu_min": min(x["freq_B3LYP_unscaled_cm"] for x in sel),
                     "nu_max": max(x["freq_B3LYP_unscaled_cm"] for x in sel), "irreps": ", ".join(sorted(set(x["irrep_D2h"] for x in sel)))})
    L = [f"# Naphthalene — family labels by DFT mode vector (B3LYP/6-31G*, unscaled; {datetime.now():%Y-%m-%d})", "",
         f"Source: {CONSTANTS['source']}; families by {CONSTANTS['family_rule']}; IR activity by D2h irrep ({', '.join(CONSTANTS['ir_active_irreps_D2h'])}). "
         f"{r['M']} modes, {r['n_imag']} imaginary, {sum(x['ir_active'] for x in rows)} IR-active.", "",
         "| family (mode vector) | modes | IR-active | ν range (cm⁻¹, unscaled) | irreps |", "|---|---|---|---|---|"]
    L += [f"| {s['family']} | {s['modes']} | {s['ir_active']} | {s['nu_min']:.0f}–{s['nu_max']:.0f} | {s['irreps']} |" for s in summ]
    dis = [x for x in rows if not (x["family_window_rule"].startswith(x["family_mode_vector"].split("-")[0]) or x["family_mode_vector"] in x["family_window_rule"])]
    L += ["", f"Window rule versus mode vector: the Module-03 frequency-window label differs in wording for every mode (different label sets); modes where the *physics* differs "
          f"(an out-of-plane mode inside an in-plane window, or the reverse) are listed in the CSV by comparing the two columns. Modes with imaginary frequency: {r['n_imag']}.", "",
          "| mode | ν (cm⁻¹) | irrep | IR | family (mode vector) | window label |", "|---|---|---|---|---|---|"]
    L += [f"| {x['mode']} | {x['freq_B3LYP_unscaled_cm']:.1f} | {x['irrep_D2h']} | {'yes' if x['ir_active'] else '—'} | {x['family_mode_vector']} | {x['family_window_rule']} |" for x in rows]
    L += ["", "Use in the scoreboard: assign an observed naphthalene band to the nearest IR-active mode of the same family after scaling (the scaling and the assignment "
          "rule are the pilot note's, not this table's); the C–H out-of-plane sub-families by hydrogen adjacency (Q9, decision 27) need the mode vectors themselves (in plan 02's npz), not this table.",
          "", "Constants: " + json.dumps(CONSTANTS)]
    (out / "naphthalene_dft_modes.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L[:14]).encode("ascii", "replace").decode())


if __name__ == "__main__":
    main()
