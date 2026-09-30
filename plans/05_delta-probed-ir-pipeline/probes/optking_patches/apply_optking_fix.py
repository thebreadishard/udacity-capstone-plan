"""Patch the installed optking (0.5.0) of a conda environment against the linear-bend stall of 30 September 2026 (issue draft
GoalGathering/notes/Issue_Draft_2026-09-30_optking_linear_bend_stall.md; the user: 'los het issue op in onze versie van de code').

Two changes, exact-string, idempotent, with a marker so a second run is a no-op:
  1. v3d.linear_torsion_check: an interior angle near 0 deg (the torsion's middle atom is a terminal atom) is no longer reported as a "linear bend" —
     it raises AlgError with back_transformation=True (optking's existing reset path) instead of adding permuted bends with a terminal vertex.
  2. addIntcos.add_intcos_from_connectivity, collinear-segment torsion search: the two walks along LINEAR bends get a visited set and raise AlgError
     on a cycle instead of spinning silently.

Usage: python apply_optking_fix.py [--check]   (run with the environment's python; --check only reports whether the patch is applied)
"""
import os
import sys

MARK = "# patched 2026-09-30 linear-bend stall (udacity-capstone-plan)"

V3D_OLD = """    # Print specific message of which bend has become problematic in torsion
    if phi_123_bad:
        val = phi_123 * 180.0 / np.pi
        logger.warning(
            f"Interior angle of {val:5.1f} for bend B({indices[:-1]}) can't work in good torsion"
        )
        bad_bends.append(phi_123)
"""
V3D_NEW = """    # Print specific message of which bend has become problematic in torsion
    """ + MARK + """: an interior angle near 0 deg means the torsion's
    # middle atom is a terminal atom (a connectivity artefact), not a linear bend; adding permuted "linear bends" with that
    # atom as vertex feeds a LINEAR-bend cycle into add_intcos_from_connectivity. Reset instead.
    if (phi_123_bad and phi_123 < phi_lim) or (phi_234_bad and phi_234 < phi_lim):
        raise AlgError(
            f"Could not compute T({indices}): interior angle near 0 deg ({phi_123 * 180.0 / np.pi:5.1f}, "
            f"{phi_234 * 180.0 / np.pi:5.1f}); torsion through a terminal atom, resetting coordinates",
            back_transformation=True,
        )
    if phi_123_bad:
        val = phi_123 * 180.0 / np.pi
        logger.warning(
            f"Interior angle of {val:5.1f} for bend B({indices[:-1]}) can't work in good torsion"
        )
        bad_bends.append(phi_123)
"""

ADD_OLD_1 = """                        J = j
                        i = 0
                        while i < Natom:
                            if C[i, J] and i != m:  # i!=J i!=m
                                b = bend.Bend(i, J, k, bend_type="LINEAR")
                                if b in intcos:  # i,J,k is collinear
                                    J = i
                                    i = 0
                                    continue
"""
ADD_NEW_1 = """                        J = j
                        i = 0
                        visited_J = {J}  """ + MARK + """
                        while i < Natom:
                            if C[i, J] and i != m:  # i!=J i!=m
                                b = bend.Bend(i, J, k, bend_type="LINEAR")
                                if b in intcos:  # i,J,k is collinear
                                    if i in visited_J:
                                        raise AlgError(
                                            f"Cycle of LINEAR bends around atoms {sorted(visited_J)} while searching torsions "
                                            "past a collinear segment; the coordinate set is inconsistent",
                                            back_transformation=True,
                                        )
                                    visited_J.add(i)
                                    J = i
                                    i = 0
                                    continue
"""
ADD_OLD_2 = """                                    l = 0
                                    while l < Natom:
                                        if C[l, K] and l != m and l != j and l != i:
                                            b = bend.Bend(l, K, J, bend_type="LINEAR")
                                            if b in intcos:  # J-K-l is collinear
                                                K = l
                                                l = 0
                                                continue
"""
ADD_NEW_2 = """                                    l = 0
                                    visited_K = {K}  """ + MARK + """
                                    while l < Natom:
                                        if C[l, K] and l != m and l != j and l != i:
                                            b = bend.Bend(l, K, J, bend_type="LINEAR")
                                            if b in intcos:  # J-K-l is collinear
                                                if l in visited_K:
                                                    raise AlgError(
                                                        f"Cycle of LINEAR bends around atoms {sorted(visited_K)} while searching "
                                                        "torsions past a collinear segment; the coordinate set is inconsistent",
                                                        back_transformation=True,
                                                    )
                                                visited_K.add(l)
                                                K = l
                                                l = 0
                                                continue
"""


def main():
    import optking
    root = os.path.dirname(optking.__file__)
    check = "--check" in sys.argv
    plan = [("v3d.py", [(V3D_OLD, V3D_NEW)]), ("addIntcos.py", [(ADD_OLD_1, ADD_NEW_1), (ADD_OLD_2, ADD_NEW_2)])]
    for name, edits in plan:
        path = os.path.join(root, name)
        text = open(path, encoding="utf-8").read()
        if MARK in text:
            print(f"{name}: already patched")
            continue
        if check:
            print(f"{name}: NOT patched"); continue
        for old, new in edits:
            n = text.count(old)
            assert n == 1, f"{name}: anchor found {n} times (optking {optking.__version__}); refusing"
        for old, new in edits:
            text = text.replace(old, new)
        if "AlgError" not in text.split("def ")[0] and name == "addIntcos.py":
            assert "from .exceptions import AlgError" in text or "import AlgError" in text, "addIntcos.py does not import AlgError"
        tmp = path + ".tmp"
        open(tmp, "w", encoding="utf-8", newline="\n").write(text)
        os.replace(tmp, path)
        print(f"{name}: patched ({len(edits)} edits) — {path}")
    print("optking", optking.__version__, "at", root)


if __name__ == "__main__":
    main()
