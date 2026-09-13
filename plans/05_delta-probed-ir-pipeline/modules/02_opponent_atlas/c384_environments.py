"""Module 02 — the symmetry-unique local-environment count of C384H48 (PAHdb v4.00 uid 617), the R6 input the atlas owed (2026-09-13).

Plan 05's local-CC deck is fragment-based (one fragment per localised occupied orbital, i.e. per bond and per pi-type orbital); fragments
related by a symmetry operation of the molecule give identical energies (the naphthalene xtight timing showed symmetry-equivalent fragments
agreeing to 1e-8 E_h), so the cost of a fragment-probed rung scales with the number of symmetry-UNIQUE fragments, not with the total.
This script reads the geometry block of uid 617 from the PAHdb theoretical v4.00 XML (streamed; the file is 503 MB), builds the bond graph
(C-C < 1.7 A, C-H < 1.2 A), detects the in-plane point-group operations numerically (rotations by multiples of 60 deg about the plane normal
and reflections through in-plane axes at multiples of 30 deg, each accepted if it maps every atom onto an atom of the same element within
TOL), and counts orbits of atoms, C-C bonds, C-H bonds and depth-one environments (an atom with its bonded neighbours - the same orbits as
the atoms for a connected symmetric graph). The ideal D6h honeycomb flake with the same formula (plan 06's X8 generator, n = 8) is counted
the same way as a cross-check. Output: out/theoretical_4.00/c384_environments.{md,json}. Every number from the files; constants in CONSTANTS."""
import json
import sys
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path.insert(0, str(REPO / "plans/06_equivalent-faster-mathematics/experiments"))
from x8_size_scaling_substitution import honeycomb, hex_flake  # noqa: E402

CONSTANTS = {"uid": "617", "xml": "data/pahdb-complete-theoretical-v4.00_fevj3bdlnookcPYsGjJ.xml (block for uid 617 extracted with sed to data/_uid617_specie.xml, lines 18873934-18883435)", "bond_A": {"CC": 1.7, "CH": 1.2}, "TOL_A": 0.05,
             "candidate_rotations_deg": [60 * k for k in range(6)], "candidate_reflection_axes_deg": [30 * j for j in range(6)], "BOHR_TO_A": 0.529177210903}
Z2SYM = {"6": "C", "1": "H", "7": "N", "8": "O", "C": "C", "H": "H"}


def _ln(tag):
    return tag.rsplit("}", 1)[-1]


def _child(el, name):
    return next((c for c in el if _ln(c.tag) == name), None)


def _text(el, name):
    c = _child(el, name); return (c.text or "").strip() if c is not None else None


def geometry_from_xml(path, uid):
    for ev, el in ET.iterparse(str(path), events=("end",)):
        if _ln(el.tag) == "specie":
            if el.attrib.get("uid") == uid:
                atoms = []
                for at in _child(el, "geometry"):
                    if _ln(at.tag) != "atom": continue
                    t = _text(at, "type") or ""      # schema as stored: <atom><position>i</position><x/><y/><z/><type/></atom>
                    atoms.append((Z2SYM.get(t, t), float(_text(at, "x")), float(_text(at, "y")), float(_text(at, "z"))))
                meta = {k: _text(el, k) for k in ("formula", "symmetry", "method")}
                el.clear(); return [a[0] for a in atoms], np.array([a[1:] for a in atoms]), meta
            el.clear()
    raise RuntimeError(f"uid {uid} not found")


def bonds(sym, X):
    D = np.linalg.norm(X[:, None] - X[None], axis=2); n = len(sym); B = []
    for i in range(n):
        for j in range(i + 1, n):
            key = "".join(sorted(sym[i] + sym[j])); cut = CONSTANTS["bond_A"].get(key, 0.0)
            if D[i, j] < cut: B.append((i, j))
    return B


def plane_frame(X):
    c = X.mean(0); Y = X - c; w, V = np.linalg.eigh(Y.T @ Y)
    R = V[:, np.argsort(w)[::-1]]              # largest variance first; the normal is last
    return Y @ R


def operations(sym, Y):
    """In-plane operations (as 2x2 matrices acting on x, y) that map the atom set onto itself within TOL."""
    tol = CONSTANTS["TOL_A"]; ops = []
    def perm_of(M):
        Yt = Y[:, :2] @ M.T; perm = []
        for a in range(len(sym)):
            d = np.linalg.norm(Y[:, :2] - Yt[a], axis=1); b = int(np.argmin(d))
            if d[b] > tol or sym[b] != sym[a]: return None
            perm.append(b)
        return perm
    for deg in CONSTANTS["candidate_rotations_deg"]:
        t = np.deg2rad(deg); M = np.array([[np.cos(t), -np.sin(t)], [np.sin(t), np.cos(t)]]); p = perm_of(M)
        if p is not None: ops.append((f"C{deg}", p))
    for deg in CONSTANTS["candidate_reflection_axes_deg"]:
        t = np.deg2rad(deg); M = np.array([[np.cos(2 * t), np.sin(2 * t)], [np.sin(2 * t), -np.cos(2 * t)]]); p = perm_of(M)
        if p is not None: ops.append((f"sigma{deg}", p))
    return ops


def orbits(items, ops):
    """items: hashable atom indices or frozensets of indices; ops: list of permutations."""
    seen = set(); count = 0
    for it in items:
        if it in seen: continue
        count += 1; stack = [it]
        while stack:
            x = stack.pop()
            if x in seen: continue
            seen.add(x)
            for _, p in ops:
                y = p[x] if isinstance(x, int) else frozenset(p[i] for i in x)
                if y not in seen: stack.append(y)
    return count


def count(sym, X, label):
    Y = plane_frame(X); ops = operations(sym, Y); B = bonds(sym, X)
    cc = [frozenset(b) for b in B if sym[b[0]] == sym[b[1]] == "C"]; ch = [frozenset(b) for b in B if {sym[b[0]], sym[b[1]]} == {"C", "H"}]
    C = [i for i, s in enumerate(sym) if s == "C"]; H = [i for i, s in enumerate(sym) if s == "H"]
    res = {"label": label, "nC": len(C), "nH": len(H), "operations_found": [o[0] for o in ops], "group_order_in_plane": len(ops),
           "planarity_max_abs_z_A": float(np.abs(Y[:, 2]).max()), "bonds_CC": len(cc), "bonds_CH": len(ch),
           "unique_C_atoms": orbits(C, ops), "unique_H_atoms": orbits(H, ops), "unique_CC_bonds": orbits(cc, ops), "unique_CH_bonds": orbits(ch, ops)}
    res["unique_bond_fragments"] = res["unique_CC_bonds"] + res["unique_CH_bonds"]; res["total_bond_fragments"] = len(cc) + len(ch)
    res["reduction_factor_bonds"] = res["total_bond_fragments"] / res["unique_bond_fragments"]
    return res


def main():
    # 2026-09-13: parse the small extracted <specie> block when present (data/_uid617_specie.xml, cut with sed from the 503 MB file); streaming the whole
    # file through ElementTree on the Windows side took 3.8 GB and, beside the running anchor job, exhausted host memory (event 2004, 09:46) — never again
    src = HERE / "data/_uid617_specie.xml"
    if not src.exists():
        raise SystemExit("extract the specie block first: sed -n '<start>,<end>p' <xml> > data/_uid617_specie.xml (see README); the full-file parse is forbidden beside a running job")
    sym, X, meta = geometry_from_xml(src, CONSTANTS["uid"])
    pah = count(sym, X, f"PAHdb v4.00 uid {CONSTANTS['uid']} ({meta.get('formula')}, symmetry {meta.get('symmetry')}, {meta.get('method')})")
    s8, X8 = honeycomb(hex_flake(8)); ideal = count(s8, X8 * CONSTANTS["BOHR_TO_A"], "ideal D6h honeycomb flake n = 8 (plan 06 X8 generator)")
    out = {"date": f"{datetime.now():%Y-%m-%d %H:%M}", "constants": CONSTANTS, "pahdb": pah, "ideal": ideal}
    d = HERE / "out/theoretical_4.00"; d.mkdir(parents=True, exist_ok=True)
    json.dump(out, open(d / "c384_environments.json", "w"), indent=1)
    L = [f"# C384H48 — symmetry-unique local environments (R6 input; {out['date']})", "",
         "Fragments related by a symmetry operation give identical local-CC energies (naphthalene xtight timing: equivalent fragments agree to 1e-8 E_h), so a fragment-probed rung "
         "pays per unique fragment. In-plane operations detected numerically (rotations by 60° multiples, reflections through 30° axes; tolerance 0.05 Å); "
         "orbits of atoms and bonds counted under them. One fragment per bond is the proxy for plan 05's one-fragment-per-LMO scheme (π-type LMOs not counted).", "",
         "| geometry | C / H | in-plane operations | planarity (max |z|, Å) | C–C / C–H bonds | unique C / H atoms | unique C–C / C–H bonds | unique bond fragments of total | reduction |", "|---|---|---|---|---|---|---|---|---|"]
    for r in (pah, ideal):
        L.append(f"| {r['label']} | {r['nC']} / {r['nH']} | {r['group_order_in_plane']} ({', '.join(r['operations_found'])}) | {r['planarity_max_abs_z_A']:.3f} | {r['bonds_CC']} / {r['bonds_CH']} | "
                 f"{r['unique_C_atoms']} / {r['unique_H_atoms']} | {r['unique_CC_bonds']} / {r['unique_CH_bonds']} | **{r['unique_bond_fragments']} of {r['total_bond_fragments']}** | ×{r['reduction_factor_bonds']:.1f} |")
    L += ["", "Reading: the reduction factor is what the symmetry prior buys at R6 on the fragment count (the deck's element count is a separate question, X14's largest-irrep-block argument "
          "in plan 06). If PAHdb's stored geometry is slightly less symmetric than the ideal flake, the operation count says so and the PAHdb row is the binding one.", "",
          "Constants: " + json.dumps(CONSTANTS)]
    (d / "c384_environments.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L).encode("ascii", "replace").decode())


if __name__ == "__main__":
    main()
