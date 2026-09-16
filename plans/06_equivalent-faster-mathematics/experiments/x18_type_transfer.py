"""X18 (prepared 2026-09-13, evening; mandate ledger obstacle 2 / idea I4) — TYPE TRANSFER of the internal-coordinate correction:
fit the orbit constants of X17's set S2 (diagonal + couplings between internals sharing an atom + one bond apart) on a SOURCE molecule,
map them by LOCAL TYPE onto a TARGET molecule, and read the predicted per-mode first-order shifts against the target's measured ones,
per family, in the T-1 form (RMS and max per family; losing condition RMS > 2.5 cm-1 for CH-stretch and CC-stretch, agreed 13 September).

Local type of a coordinate pair = (type_a, type_b, graph separation, and for pairs sharing atoms the shared-atom count), e.g.
("CC","CC",sep0) = adjacent ring bonds, ("CC","CCH",sep0) = ring bond with a bend at one of its atoms, ("CH","CH",sep1) = C-H bonds on
neighbouring carbons. On the source, symmetry orbits are finer than types (benzene: 51 S2 orbits); a type's constant is the norm-weighted
mean of its orbits' constants on the source (the redundancy caveat of X17 applies: constants are not unique, so the transfer is tested
on RESIDUALS, and the source fit is repeated with a type-constrained model so that source and target use the same parameterisation).
On the target every pair of the same type gets that constant; the predicted Delta_2 in the target's mode basis is L^T M^-1/2 B^T dF B M^-1/2 L.

Block: in-plane coordinates only (see CONSTANTS["why_in_plane_only"]); out-of-plane modes therefore get the zero rule.
Inputs: X17's machinery (imported), plan 05 stageA_hessians.npz + stageA.json of source and target. Self-test today: --source benzene
--target benzene must reproduce the type-constrained source fit exactly (transfer error = the type-model's own residual on benzene).
The real test — benzene -> naphthalene — needs naphthalene's stand-in Hessian (plan 05 machine-queue item 5) and prints NOT_RUN until then.
Output: x18_<source>_to_<target>.md/.json beside this script. Every number from the files; constants in CONSTANTS."""
import argparse
import json
from datetime import datetime
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
import sys
sys.path.insert(0, str(HERE))
from x17_internal_coordinate_orbits import (load, internal_set, b_matrix, operations_of, coordinate_images, orbits, graph_distance, HARTREE_TO_CM, P05)  # noqa: E402

CONSTANTS = {"parameter_set": "S2 = diagonal + shared-atom couplings + one-bond-apart couplings (X17), IN-PLANE BLOCK ONLY", "threshold_cm": 2.5,
             "lstsq_rcond": 1e-3,
             "why_rcond": "2026-09-16: the type design on benzene has 24 real directions and 5 null ones from the redundancy of the internal set "
                          "(singular values 2.4e-3 … 6.3e-5, then 2e-10, 3e-11, 7e-16, 3e-19, 2e-19); numpy's default cutoff kept the 1e-10 "
                          "directions and gave three CC-CCC coupling types constants of 2.7e6 that cancel on benzene and not on naphthalene "
                          "(first run: 1e9 cm-1 'errors'). Truncating at 1e-3 of the largest singular value drops exactly the five null "
                          "directions: source residual unchanged (0.031 cm-1 in-plane), max|constant| 0.0125.", "inplane_types": ["CC", "CH", "CCC", "CCH"],
             "why_in_plane_only": "out-of-plane coordinates (wags, torsions) carry an orientation sign that a type key does not fix across molecules (the first, signed-orbit-free version of X17 failed by 14 cm-1 for the same reason); the type transfer is therefore tested on the in-plane block, which holds both judged families (CH-stretch, CC-stretch); the out-of-plane block waits for a declared, symmetry-covariant sign convention (mandate ledger)",
             "judged_families": ["CH-stretch", "CC-stretch"], "type_key": "(type_a, type_b, graph separation, shared atoms) with the pair sorted by type name",
             "source_model": "type-constrained least squares on the source (one constant per type), so source and target share the parameterisation"}


def types_and_design(mol):
    """Everything X18 needs for one molecule: internal set, B, mode-basis design per pair, pair -> type."""
    d = load(mol); X = d["coords"]; sym = d["symbols"]; L = d["L"]; Minv = d["Minv"]
    ic, bonds = internal_set(X, sym); B = b_matrix(ic, X); sep = graph_distance(ic, bonds, len(sym))
    T = B * Minv[None, :] @ L
    def shared(a, b): return len(set(ic[a][1]) & set(ic[b][1]))
    def key(a, b):
        ta, tb = ic[a][0], ic[b][0]
        if ta > tb: ta, tb = tb, ta
        return (ta, tb, int(sep(a, b)) if a != b else -1, shared(a, b) if a != b else -1)
    inplane = {r for r, (t, _) in enumerate(ic) if t in CONSTANTS["inplane_types"]}
    pairs = [(a, b) for a in range(len(ic)) for b in range(a, len(ic)) if (a == b or sep(a, b) <= 1) and a in inplane and b in inplane]  # S2 reach, in-plane block
    return d, ic, T, pairs, key


def type_design(T, pairs, key, n_ic):
    cols = {}; M = T.shape[1]
    for a, b in pairs:
        F = np.zeros((n_ic, n_ic)); F[a, b] += 1; F[b, a] += (1 if a != b else 0)
        cols.setdefault(key(a, b), np.zeros(M * M))
        cols[key(a, b)] += (T.T @ F @ T).reshape(-1)
    keys = sorted(cols); return keys, np.array([cols[k] for k in keys]).T


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--source", default="benzene"); ap.add_argument("--target", default="naphthalene"); args = ap.parse_args()
    out = {"date": f"{datetime.now():%Y-%m-%d %H:%M}", "constants": CONSTANTS, "source": args.source, "target": args.target}
    S, ic_s, T_s, pairs_s, key_s = types_and_design(args.source)
    keys_s, A_s = type_design(T_s, pairs_s, key_s, len(ic_s)); target_s = S["D2Q"].reshape(-1)
    sv_s = np.linalg.svd(A_s, compute_uv=False)
    x_s, *_ = np.linalg.lstsq(A_s, target_s, rcond=CONSTANTS["lstsq_rcond"]); fit_s = (A_s @ x_s).reshape(len(S["omega"]), -1)
    out["source_design"] = {"singular_values": [float(v) for v in sv_s], "rank_used": int(np.sum(sv_s > CONSTANTS["lstsq_rcond"] * sv_s[0])),
                            "max_abs_constant": float(np.abs(x_s).max())}
    meas_s = np.diag(S["D2Q"]) / (2 * S["omega"]) * HARTREE_TO_CM; res_s = np.diag(fit_s) / (2 * S["omega"]) * HARTREE_TO_CM - meas_s
    consts = dict(zip(keys_s, x_s))
    out["source_fit"] = {"n_types": len(keys_s), "rms_first_order_cm": float(np.sqrt(np.mean(res_s ** 2))), "max_cm": float(np.abs(res_s).max()),
                         "types": [{"type": list(map(str, k)), "constant": float(v)} for k, v in consts.items()]}
    L = [f"# X18 — type transfer of the internal-coordinate correction, {args.source} → {args.target} ({out['date']})", "",
         f"Source model: {CONSTANTS['source_model']}; {len(keys_s)} types on {args.source}; source residual (type model, first order) RMS {out['source_fit']['rms_first_order_cm']:.2f} cm⁻¹, max {out['source_fit']['max_cm']:.2f}.", ""]
    tgt_dir = P05 / args.target
    if not (tgt_dir / "stageA_hessians.npz").exists():
        L += [f"## Transfer to {args.target}: **NOT_RUN** — `{tgt_dir.name}/stageA_hessians.npz` does not exist yet (plan 05 machine-queue item 5)."]; out["transfer"] = "NOT_RUN"
    else:
        Tt, ic_t, T_t, pairs_t, key_t = types_and_design(args.target)
        keys_t, A_t = type_design(T_t, pairs_t, key_t, len(ic_t))
        x_t = np.array([consts.get(k, 0.0) for k in keys_t]); missing = [k for k in keys_t if k not in consts]
        pred = (A_t @ x_t).reshape(len(Tt["omega"]), -1)
        meas_t = np.diag(Tt["D2Q"]) / (2 * Tt["omega"]) * HARTREE_TO_CM; pred_t = np.diag(pred) / (2 * Tt["omega"]) * HARTREE_TO_CM
        rows = []; verdict = True
        for f in sorted(set(Tt["fam"])):
            idx = [k for k, g in enumerate(Tt["fam"]) if g == f]; e = pred_t[idx] - meas_t[idx]; z = -meas_t[idx]
            r = {"family": f, "n": len(idx), "rms_cm": float(np.sqrt(np.mean(e ** 2))), "max_cm": float(np.abs(e).max()), "rms_zero_rule_cm": float(np.sqrt(np.mean(z ** 2))), "judged": f in CONSTANTS["judged_families"]}
            r["passes"] = r["rms_cm"] <= CONSTANTS["threshold_cm"]; verdict &= (r["passes"] or not r["judged"]); rows.append(r)
        out["transfer"] = {"rows": rows, "types_missing_on_source": [list(map(str, k)) for k in missing], "verdict": "PASS" if verdict else "LOSE"}
        L += [f"## Transfer to {args.target}: {len(keys_t)} types on the target, {len(missing)} without a source constant (set to 0)", "",
              "| family | modes | RMS error (cm⁻¹) | max | RMS zero rule | judged | passes 2.5 |", "|---|---|---|---|---|---|---|"]
        for r in rows:
            L.append(f"| {r['family']} | {r['n']} | **{r['rms_cm']:.2f}** | {r['max_cm']:.2f} | {r['rms_zero_rule_cm']:.2f} | {'yes' if r['judged'] else '—'} | {'yes' if r['passes'] else 'NO'} |")
        L += ["", f"**Verdict (judged families): {out['transfer']['verdict']}.**"]
    if args.source == args.target:
        L += ["", "Self-test: source = target — the transfer reproduces the type-constrained source fit; the error printed is the type model's own residual, not a transfer error."]
    p = HERE / f"x18_{args.source}_to_{args.target}"; p.with_suffix(".md").write_text("\n".join(L), encoding="utf-8")
    json.dump(out, open(p.with_suffix(".json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False); print("\n".join(L).encode("ascii", "replace").decode())


if __name__ == "__main__":
    main()
