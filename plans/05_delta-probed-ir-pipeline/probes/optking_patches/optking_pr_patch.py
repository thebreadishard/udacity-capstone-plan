"""Apply the linear-bend fix to an optking git checkout (master, for the pull request; issue psi-rking/optking#115). Same two changes as
probes/optking_patches/apply_optking_fix.py, written for upstream: comments reference the issue, no repo marker. Exact-string, refuses if an anchor is
not found exactly once. Usage: python optking_pr_patch.py <checkout dir>"""
import os
import sys

ROOT = sys.argv[1]

V3D_OLD = """    # Print specific message of which bend has become problematic in torsion
    if phi_123_bad:
"""
V3D_NEW = """    # An interior angle near 0 (below phi_lim) is not a linear bend: the torsion runs through a
    # terminal atom (a connectivity artefact). Adding "linear bends" with that atom as vertex feeds
    # inconsistent LINEAR coordinates into add_intcos_from_connectivity (see issue #115). Reset instead.
    if (phi_123_bad and phi_123 < phi_lim) or (phi_234_bad and phi_234 < phi_lim):
        raise AlgError(
            f"Could not compute T({indices}): interior angle near 0 "
            f"({phi_123 * 180.0 / np.pi:5.1f}, {phi_234 * 180.0 / np.pi:5.1f} deg); "
            "torsion through a terminal atom, resetting coordinates",
            back_transformation=True,
        )

    # Print specific message of which bend has become problematic in torsion
    if phi_123_bad:
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
                        visited_J = {J}  # guard against a cycle of LINEAR bends (issue #115)
                        while i < Natom:
                            if C[i, J] and i != m:  # i!=J i!=m
                                b = bend.Bend(i, J, k, bend_type="LINEAR")
                                if b in intcos:  # i,J,k is collinear
                                    if i in visited_J:
                                        raise AlgError(
                                            "Cycle of LINEAR bends around atoms "
                                            f"{sorted(visited_J)} while searching for torsions "
                                            "past a collinear segment; the coordinate set is "
                                            "inconsistent",
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
                                    visited_K = {K}  # same guard for the outward walk from k
                                    while l < Natom:
                                        if C[l, K] and l != m and l != j and l != i:
                                            b = bend.Bend(l, K, J, bend_type="LINEAR")
                                            if b in intcos:  # J-K-l is collinear
                                                if l in visited_K:
                                                    raise AlgError(
                                                        "Cycle of LINEAR bends around atoms "
                                                        f"{sorted(visited_K)} while searching for "
                                                        "torsions past a collinear segment; the "
                                                        "coordinate set is inconsistent",
                                                        back_transformation=True,
                                                    )
                                                visited_K.add(l)
                                                K = l
                                                l = 0
                                                continue
"""

for name, edits in (("optking/v3d.py", [(V3D_OLD, V3D_NEW)]), ("optking/addIntcos.py", [(ADD_OLD_1, ADD_NEW_1), (ADD_OLD_2, ADD_NEW_2)])):
    path = os.path.join(ROOT, name)
    text = open(path, encoding="utf-8").read()
    for old, new in edits:
        n = text.count(old)
        assert n == 1, f"{name}: anchor found {n} times; refusing"
    for old, new in edits:
        text = text.replace(old, new)
    tmp = path + ".tmp"
    open(tmp, "w", encoding="utf-8", newline="\n").write(text)
    os.replace(tmp, path)
    print("patched", name)
