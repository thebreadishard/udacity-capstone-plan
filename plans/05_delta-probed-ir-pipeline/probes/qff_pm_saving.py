"""The ± saving and the lanes for a quartic force field's displaced Hessians (2 Nov 2026; registration
GoalGathering/notes/PreRegistration_2026-11-02_S3_Route_A_Transfer.md, route A).

For a displaced geometry x₀ + d whose negative is the image of a point-group operation (D d = −d), H(x₀ − d) = D H(x₀ + d) Dᵀ, so the −d
Hessian is written from the +d one instead of computed (on benzene 0.03 cm⁻¹ rms in Δ_anh, S1's development of 13 Oct; the pair saving
failed there and is not used). Operations that map the laboratory-frame Lebedev grid onto itself are preferred: their images carry only
the noise of a DFT Hessian difference.

    python qff_pm_saving.py symmetrize <stub.json>                         the optimised reference averaged over its group, in place, once
    python qff_pm_saving.py plan <ref.json> <stubs_dir> <compute_dir>      the stubs to compute copied; <compute_dir>/../images.json
    python qff_pm_saving.py split <compute_dir> <lanes_dir> <k>            the stubs to compute over k lane folders, round robin
    python qff_pm_saving.py fill <hess_dir> <stubs_dir> <images.json>      each skipped −d Hessian written as the image of its +d one
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import shutil
import sys
from typing import Any

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "src"))
from e8_symmetry import point_group_ops  # noqa: E402
from qff_symmetry_count import symmetrize as group_average  # noqa: E402
from qff_symmetry_rebuild import REL_TOL, grid_compatible, rep  # noqa: E402

OPS_TOL = 1e-5          # bohr: the operations of a geometry already averaged over its group
MAX_SYMMETRIZE_MOVE = 1e-2   # bohr: an optimised minimum further than this from its group average is not the molecule we think it is
IMAGES_NAME = "images.json"


def read_json(path: str) -> dict[str, Any]:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def write_json(path: str, obj: dict[str, Any]) -> None:
    with open(path + ".tmp", "w", encoding="utf-8") as fh:
        json.dump(obj, fh)
    os.replace(path + ".tmp", path)


def geometry(rec: dict[str, Any]) -> tuple[list[str], np.ndarray]:
    sym = rec["molecule"]["symbols"]
    return sym, np.asarray(rec["molecule"]["geometry"], float).reshape(len(sym), 3)


def symmetrize_stub(path: str) -> dict[str, Any]:
    """Average the stub's geometry over its point group, keeping its centroid; a stub already averaged is left as it is."""
    rec = read_json(path)
    if "symmetrized" in rec:
        return rec["symmetrized"]
    sym, x = geometry(rec)
    xs = group_average(sym, x) + x.mean(0)
    move = float(np.abs(xs - x).max())
    if move > MAX_SYMMETRIZE_MOVE:
        raise ValueError(f"{path}: the group average moves an atom by {move:.2e} bohr (> {MAX_SYMMETRIZE_MOVE:g})")
    info = {"group_order": len(point_group_ops(sym, xs, tol=OPS_TOL)), "max_move_bohr": move, "routine": "probes/qff_pm_saving.py"}
    rec["molecule"]["geometry"] = xs.reshape(-1).tolist()
    rec["symmetrized"] = info
    write_json(path, rec)
    return info


def image_geometry(x: np.ndarray, centre: np.ndarray, R: np.ndarray, perm: list[int]) -> np.ndarray:
    """The geometry an operation (R about `centre`, atom i → perm[i]) makes of x."""
    y = np.empty_like(x)
    for i, j in enumerate(perm):
        y[j] = centre + R @ (x[i] - centre)
    return y


def best_negating_op(d: np.ndarray, ops: list, n: int) -> dict[str, Any] | None:
    """The operation that maps the Cartesian displacement d onto −d with the smallest residual, grid-compatible ones first; None when no
    operation does within REL_TOL."""
    found = []
    for R, perm in ops:
        r = float(np.linalg.norm(rep(R, perm, n) @ d + d) / np.linalg.norm(d))
        if r < REL_TOL:
            found.append((not grid_compatible(R), r, R, list(map(int, perm))))
    if not found:
        return None
    incompatible, r, R, perm = min(found, key=lambda f: (f[0], f[1]))
    return {"R": R.tolist(), "perm": perm, "grid_compatible": not incompatible, "residual": r}


def plan_images(ref_json: str, stubs_dir: str) -> dict[str, dict[str, Any]]:
    """Per −d stub that an operation maps from its +d partner: the operation and its residuals. The reference must be group-averaged."""
    sym, x0 = geometry(read_json(ref_json))
    n = len(sym)
    centre = x0.mean(0)
    ops = point_group_ops(sym, x0, tol=OPS_TOL)
    images = {}
    for p_path in sorted(glob.glob(os.path.join(stubs_dir, "mode*_p.json"))):
        m_name = os.path.basename(p_path)[:-len("_p.json")] + "_m.json"
        m_path = os.path.join(stubs_dir, m_name)
        if not os.path.exists(m_path):
            raise ValueError(f"{p_path}: no partner {m_name}")
        xp, xm = geometry(read_json(p_path))[1], geometry(read_json(m_path))[1]
        op = best_negating_op((xp - x0).reshape(-1), ops, n)
        if op is None:
            continue
        gap = float(np.abs(image_geometry(xp, centre, np.array(op["R"]), op["perm"]) - xm).max())
        images[m_name] = {"from": os.path.basename(p_path), **op, "geometry_residual_bohr": gap}
    return images


def write_plan(ref_json: str, stubs_dir: str, compute_dir: str) -> dict[str, Any]:
    """images.json beside compute_dir, and compute_dir holding every stub that is not an image (the reference stub included)."""
    images_path = os.path.join(os.path.dirname(os.path.abspath(compute_dir)), IMAGES_NAME)
    images = plan_images(ref_json, stubs_dir)
    stubs = sorted(os.path.basename(p) for p in glob.glob(os.path.join(stubs_dir, "*.json")))
    compute = [s for s in stubs if s not in images]
    if os.path.isdir(compute_dir):
        present = sorted(os.listdir(compute_dir))
        if present != compute:
            raise ValueError(f"{compute_dir} exists with other stubs ({len(present)} against {len(compute)} planned)")
    else:
        os.makedirs(compute_dir + ".tmp")
        for s in compute:
            shutil.copy2(os.path.join(stubs_dir, s), os.path.join(compute_dir + ".tmp", s))
        os.replace(compute_dir + ".tmp", compute_dir)
    summary = {"stubs": len(stubs), "computed": len(compute), "images": len(images),
               "grid_compatible": sum(v["grid_compatible"] for v in images.values()),
               "max_geometry_residual_bohr": max((v["geometry_residual_bohr"] for v in images.values()), default=0.0)}
    write_json(images_path, {"summary": summary, "images": images})
    return summary


def split_lanes(compute_dir: str, lanes_dir: str, k: int) -> list[list[str]]:
    """The stubs of compute_dir over k lane folders, round robin in name order; an existing split must hold the same stubs."""
    if k < 1:
        raise ValueError(f"lanes {k}: at least one")
    stubs = sorted(os.listdir(compute_dir))
    lanes = [stubs[j::k] for j in range(k)]
    if os.path.isdir(lanes_dir):
        have = [sorted(os.listdir(os.path.join(lanes_dir, f"lane{j}"))) for j in range(k)]
        if have != lanes:
            raise ValueError(f"{lanes_dir} exists with another split")
        return lanes
    os.makedirs(lanes_dir + ".tmp")
    for j, names in enumerate(lanes):
        os.makedirs(os.path.join(lanes_dir + ".tmp", f"lane{j}"))
        for s in names:
            shutil.copy2(os.path.join(compute_dir, s), os.path.join(lanes_dir + ".tmp", f"lane{j}", s))
    os.replace(lanes_dir + ".tmp", lanes_dir)
    return lanes


def fill_images(hess_dir: str, stubs_dir: str, images_json: str) -> int:
    """Write every planned −d Hessian that is not there yet as D H(+d) Dᵀ at the −d stub's own geometry. Returns the number written."""
    images = read_json(images_json)["images"]
    written = 0
    for m_name, op in images.items():
        out = os.path.join(hess_dir, m_name)
        if os.path.exists(out):
            continue
        src = os.path.join(hess_dir, op["from"])
        if not os.path.exists(src):
            raise FileNotFoundError(f"{m_name}: its source Hessian {src} has not been computed")
        rec = read_json(src)
        sym, _ = geometry(rec)
        n = len(sym)
        D = rep(np.array(op["R"]), op["perm"], n)
        H = D @ np.asarray(rec["return_result"], float).reshape(3 * n, 3 * n) @ D.T
        rec["molecule"]["geometry"] = read_json(os.path.join(stubs_dir, m_name))["molecule"]["geometry"]
        rec["return_result"] = (0.5 * (H + H.T)).reshape(-1).tolist()
        rec["symmetry_image"] = {"from": op["from"], "grid_compatible": op["grid_compatible"], "residual": op["residual"],
                                 "routine": "probes/qff_pm_saving.py"}
        write_json(out, rec)
        written += 1
    return written


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("symmetrize")
    s.add_argument("stub")
    p = sub.add_parser("plan")
    p.add_argument("ref_json")
    p.add_argument("stubs_dir")
    p.add_argument("compute_dir")
    sp = sub.add_parser("split")
    sp.add_argument("compute_dir")
    sp.add_argument("lanes_dir")
    sp.add_argument("k", type=int)
    f = sub.add_parser("fill")
    f.add_argument("hess_dir")
    f.add_argument("stubs_dir")
    f.add_argument("images_json")
    a = ap.parse_args(argv)
    if a.cmd == "symmetrize":
        print(json.dumps(symmetrize_stub(a.stub)))
    elif a.cmd == "plan":
        print(json.dumps(write_plan(a.ref_json, a.stubs_dir, a.compute_dir)))
    elif a.cmd == "split":
        print(" ".join(str(len(lane)) for lane in split_lanes(a.compute_dir, a.lanes_dir, a.k)))
    else:
        print(f"{fill_images(a.hess_dir, a.stubs_dir, a.images_json)} image Hessians written")
    return 0


if __name__ == "__main__":
    sys.exit(main())
