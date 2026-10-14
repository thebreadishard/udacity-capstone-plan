"""S1-TZ's registered read (14 Oct 2026; `GoalGathering/notes/PreRegistration_2026-10-14_TZ_Anharmonic_Basis.md` with amendment 1): does
the anharmonic shift Δ_anh = ν − ω move when the basis goes from 6-31G* (G) to def2-TZVP (T) at the same grid?

    python s1tz_read.py --mol NAME=G_DIR,T_DIR [--mol ...] --reference benzene [--transfer NAME=G_DIR,T_DIR] --out <dir>

Each directory is a setting directory of probes/s1_anharmonic_level.sh (ref.json, qff_report.npz). Per molecule, per mode: d = Δ_anh(T) −
Δ_anh(G), modes matched by eigenvector overlap (s1_anharmonic_level.compare), families by the corpus rule on G's modes, over G's ω in
550–2,000 cm⁻¹. A NOISY force field stops the read (the registration re-runs it at 99/590 first).

Lines: (a) rms(d) ≤ 1.5 on each molecule and pooled CH-oop ≤ 1.5; (b) any molecule > 3.0 or pooled CH-oop > 3.0; (c) otherwise. The
decision is the branch of the molecules other than the reference molecule (benzene does not decide alone); the branch with benzene is
reported beside it. Scale clause: CH-oop mean d per molecule, spread > 1.5 → the solo class is measured first. Amendment 1: the per-family
correction d̄_f along k = 1, 2 molecules (every subset), e(k) ± SE; 'still learning' when e(2) < e(1) − 2·√(SE₁² + SE₂²); a transfer
molecule (--transfer) misses when a family's mean d lies outside d̄_f ± 1.5. Benzene's reference read: T against ν_MCP − ω_CCSD(T) with the
hybrid check's own matching, window and exclusions, line 6.89 cm⁻¹ rms.
"""
import argparse
import itertools
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "src"))
from s1_anharmonic_level import compare  # noqa: E402
from s2_read import FAMILIES, WINDOW, load_molecule  # noqa: E402

LINE_HOLDS, LINE_MATTERS = 1.5, 3.0
SPREAD = 1.5                    # cm⁻¹: CH-oop mean d differing by more between molecules → the adjacency class matters
TRANSFER = 1.5                  # cm⁻¹: a family's mean d outside d̄_f ± this is a transfer miss
REFERENCE_LINE = 6.89           # cm⁻¹ rms: B3LYP/TZ2P against the same reference (hybrid check outcome)
NEXT_MOLECULES = ("biphenylene (A_72b86c2331)", "azulene (A_d9139359ab)")


def rms(a):
    a = np.asarray(a, float)
    return float(np.sqrt(np.mean(a ** 2))) if a.size else None


def molecule_d(g_dir, t_dir):
    """Per G mode in the window: ω_G, d = Δ_anh(T) − Δ_anh(G), family; with the minimum mode overlap."""
    rec, why = load_molecule(g_dir)
    if rec is None:
        raise SystemExit(f"{g_dir}: {why} — the registration re-runs it before the read")
    res = compare(g_dir, [t_dir], WINDOW)["tests"][t_dir]
    if res["noisy"]:
        raise SystemExit(f"{t_dir}: NOISY — the registration re-runs it at 99/590 before the read")
    w = (rec["omega"] >= WINDOW[0]) & (rec["omega"] <= WINDOW[1])
    return {"omega": rec["omega"][w], "d": np.asarray(res["diff"])[w], "family": rec["family"][w], "min_overlap": res["min_overlap"]}


def stats(m):
    out = {"n": int(len(m["d"])), "rms": rms(m["d"]), "max": float(np.abs(m["d"]).max()), "mean": float(np.mean(m["d"])), "families": {}}
    for f in FAMILIES:
        s = m["family"] == f
        if s.any():
            out["families"][f] = {"n": int(s.sum()), "rms": rms(m["d"][s]), "mean": float(np.mean(m["d"][s]))}
    return out


def branch(mols):
    """The registered branch for a set of molecules {name: molecule_d}."""
    per = [rms(m["d"]) for m in mols.values()]
    oop = np.concatenate([m["d"][m["family"] == "CH-oop"] for m in mols.values()])
    pooled = rms(oop)
    holds = all(r <= LINE_HOLDS for r in per) and (pooled is None or pooled <= LINE_HOLDS)
    matters = any(r > LINE_MATTERS for r in per) or (pooled is not None and pooled > LINE_MATTERS)
    return ("b" if matters else "a" if holds else "c"), pooled


def family_means(mols):
    """d̄_f over the molecules' window modes, and the overall mean (the fallback for a family the molecules lack)."""
    d = np.concatenate([m["d"] for m in mols])
    fam = np.concatenate([m["family"] for m in mols])
    return {f: float(d[fam == f].mean()) for f in FAMILIES if (fam == f).any()}, float(d.mean())


def curve(mols):
    """Amendment 1: for k = 1, 2, every subset of k molecules predicts the per-mode d of the others by its d̄_f; e(k) ± SE over subsets."""
    names = sorted(mols)
    out = {}
    for k in (1, 2):
        errs, unseen = [], 0
        for sub in itertools.combinations(names, k):
            means, overall = family_means([mols[n] for n in sub])
            res = []
            for n in names:
                if n in sub:
                    continue
                m = mols[n]
                pred = np.array([means.get(f, overall) for f in m["family"]])
                unseen += int(sum(f not in means for f in m["family"]))
                res.append(pred - m["d"])
            errs.append(rms(np.concatenate(res)))
        out[str(k)] = {"e": float(np.mean(errs)), "se": float(np.std(errs, ddof=1) / np.sqrt(len(errs))) if len(errs) > 1 else 0.0,
                       "subsets": len(errs), "unseen_family_modes": unseen}
    out["still_learning"] = bool(out["2"]["e"] < out["1"]["e"] - 2 * np.hypot(out["1"]["se"], out["2"]["se"]))
    return out


def transfer(dbar, overall, m, learning):
    """Amendment 1's transfer read of one molecule outside the three."""
    fams = {}
    for f in FAMILIES:
        s = m["family"] == f
        if s.any():
            ref = dbar.get(f, overall)
            mean = float(np.mean(m["d"][s]))
            fams[f] = {"mean_d": mean, "dbar": ref, "miss": bool(abs(mean - ref) > TRANSFER)}
    miss = any(v["miss"] for v in fams.values())
    if not miss:
        reading = "transfers: every family's mean d within d̄_f ± 1.5"
    elif learning:
        reading = ("misses while the curve is still learning: not failed — data-limited; next one more fused hydrocarbon at T: "
                   + ", then ".join(NEXT_MOLECULES) + "; d̄_f re-estimated on four")
    else:
        reading = "misses with a flat curve: the search first (one family? one adjacency class? a Fermi-affected mode?), then route A at T"
    return {"families": fams, "miss": miss, "reading": reading}


def reference_read(t_dir):
    """Benzene's T against the semi-experimental shifts, with the hybrid check's own matching, window (S1's R ω) and exclusions."""
    import hybrid_check_benzene as hb
    pairs = hb.match_to_table(hb.load_table(), {"R": hb.our_modes(os.path.join(hb.RUN, "R")), "T": hb.our_modes(t_dir)})
    use = [(r, m) for r, m in pairs if hb.WINDOW[0] <= m["R"]["omega"] <= hb.WINDOW[1] and not r["fermi"]]
    diff = np.array([m["T"]["d_anh"] - (r["nu_mcp"] - r["omega_ccsdt"]) for r, m in use])
    modes = {r["mode"]: {"d_T": m["T"]["d_anh"], "d_semi": r["nu_mcp"] - r["omega_ccsdt"]} for r, m in pairs if r["mode"] in (9, 19)}
    return {"n_modes": len(use), "rms": rms(diff), "max": float(np.abs(diff).max()), "line": REFERENCE_LINE,
            "within_published_spread": bool(rms(diff) <= REFERENCE_LINE), "modes_9_19": modes}


def parse_pair(s):
    name, dirs = s.split("=", 1)
    g, t = dirs.split(",", 1)
    return name, g, t


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--mol", action="append", required=True, help="NAME=G_DIR,T_DIR")
    ap.add_argument("--reference", default="benzene", help="the molecule read against the semi-experimental shifts; it does not decide alone")
    ap.add_argument("--transfer", action="append", default=[], help="NAME=G_DIR,T_DIR: a molecule outside the three (tetracene, a solo-C–H one)")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    pairs = [parse_pair(s) for s in a.mol]
    mols = {n: molecule_d(g, t) for n, g, t in pairs}
    if len(mols) < 3:
        raise SystemExit(f"{len(mols)} molecules: the registration reads three, never fewer (scale clause)")
    deciding = {n: m for n, m in mols.items() if n != a.reference}
    b_all, pooled_all = branch(mols)
    b_dec, pooled_dec = branch(deciding)
    oop_means = {n: s["families"]["CH-oop"]["mean"] for n, s in ((n, stats(m)) for n, m in mols.items()) if "CH-oop" in s["families"]}
    spread = max(oop_means.values()) - min(oop_means.values()) if len(oop_means) > 1 else 0.0
    cur = curve(mols)
    dbar, overall = family_means(list(mols.values()))
    res = {"registration": "PreRegistration_2026-10-14_TZ_Anharmonic_Basis.md (+ amendment 1)", "window": WINDOW,
           "molecules": {n: {**stats(m), "min_overlap": m["min_overlap"]} for n, m in mols.items()},
           "branch_deciding": b_dec, "deciding_molecules": sorted(deciding), "pooled_ch_oop_deciding": pooled_dec,
           "branch_with_reference": b_all, "pooled_ch_oop_all": pooled_all, "reference_differs": b_all != b_dec,
           "ch_oop_mean_d": oop_means, "ch_oop_spread": spread, "solo_class_first": bool(spread > SPREAD),
           "dbar_f": dbar, "curve": cur,
           "transfers": {n: transfer(dbar, overall, molecule_d(g, t), cur["still_learning"]) for n, g, t in map(parse_pair, a.transfer)}}
    ref_dir = dict((n, t) for n, _g, t in pairs).get(a.reference)
    if ref_dir:
        res["reference_read"] = reference_read(ref_dir)
    os.makedirs(a.out, exist_ok=True)
    json.dump(res, open(os.path.join(a.out, "s1tz_read.json"), "w", encoding="utf-8"), indent=1)
    lines = ["# S1-TZ read — Δ_anh(T) − Δ_anh(G) per molecule", "", "| molecule | modes | rms | max | mean | CH-oop rms | min overlap |",
             "|---|---|---|---|---|---|---|"]
    for n, s in res["molecules"].items():
        co = s["families"].get("CH-oop", {}).get("rms")
        lines.append(f"| {n} | {s['n']} | {s['rms']:.2f} | {s['max']:.2f} | {s['mean']:+.2f} | {'—' if co is None else f'{co:.2f}'} | "
                     f"{s['min_overlap']:.3f} |")
    lines += ["", f"**Branch ({', '.join(res['deciding_molecules'])} decide): ({b_dec})** — with {a.reference}: ({b_all})"
              + (" — differs; the fused molecules' branch decides" if res["reference_differs"] else ""),
              "CH-oop mean d per molecule: " + ", ".join(f"{n} {v:+.2f}" for n, v in oop_means.items())
              + f" (spread {spread:.2f}{' > 1.5: the solo class is measured first' if res['solo_class_first'] else ''})",
              "d̄_f: " + ", ".join(f"{f} {v:+.2f}" for f, v in dbar.items()),
              f"curve: e(1) {cur['1']['e']:.2f} ± {cur['1']['se']:.2f}, e(2) {cur['2']['e']:.2f} ± {cur['2']['se']:.2f} → "
              + ("still learning" if cur["still_learning"] else "flat")]
    for n, t in res["transfers"].items():
        lines.append(f"transfer {n}: {t['reading']}")
    if "reference_read" in res:
        rr = res["reference_read"]
        lines.append(f"{a.reference} against ν_MCP − ω_CCSD(T): rms {rr['rms']:.2f}, max {rr['max']:.2f} over {rr['n_modes']} modes (line ≤ "
                     f"{rr['line']}: {'within' if rr['within_published_spread'] else 'outside'} the published routes' spread); "
                     + ", ".join(f"ν{k} T {v['d_T']:+.1f} vs {v['d_semi']:+d}" for k, v in sorted(rr["modes_9_19"].items())))
    open(os.path.join(a.out, "s1tz_read.md"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
