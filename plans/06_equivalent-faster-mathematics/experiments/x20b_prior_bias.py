"""The one thing X20 assumed away: what does TRUNCATING Delta_2 to the symmetry pattern cost?

X20 measures the recovery against the pattern-restricted truth, so the prior's own bias is excluded by
construction. Here the pattern-restricted Delta_2 is compared with the full one, in cm-1 per family.
"""
import json
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
DRY = HERE.parent.parent / "05_delta-probed-ir-pipeline" / "probes" / "results_dryrun" / "naphthalene_sym"
HARTREE_TO_CM = 219474.63

a = json.load(open(DRY / "stageA.json"))
z = np.load(DRY / "stageA_hessians.npz")
omega, D2 = z["omega_au"], z["D2_direct"]
M, irreps, families = a["M"], a["irreps"], a["families"]
P = np.array([[i == j or irreps[i] == irreps[j] for j in range(M)] for i in range(M)])
D2_trunc = np.where(P, D2, 0.0)

s = np.sqrt(omega)
W2 = np.diag(omega ** 2)


def freqs(D):
    f = np.sqrt(np.abs(np.linalg.eigvalsh(W2 + D * np.outer(s, s)))) * HARTREE_TO_CM
    f.sort()
    return f


d = freqs(D2_trunc) - freqs(D2)
print("Truncating Delta_2 to the symmetry pattern (141 of 1,128 pairs kept):")
print("  elements dropped: %d of %d, largest %.3f uE_h, RMS %.4f uE_h"
      % (int((~P).sum() / 2), M * (M - 1) // 2, np.abs(D2[~P]).max() * 1e6,
         np.sqrt(np.mean(D2[~P] ** 2)) * 1e6))
print("  frequency cost of dropping them, per family (cm-1):")
worst = 0.0
for fam in sorted(set(families)):
    idx = [k for k, f in enumerate(families) if f == fam]
    r = float(np.sqrt(np.mean(d[idx] ** 2)))
    worst = max(worst, r)
    print("    %-14s %8.4f  (%d modes)" % (fam, r, len(idx)))
print("  worst family: %.4f cm-1 against the project's 0.5 cm-1 target" % worst)
json.dump({"dropped_max_uEh": float(np.abs(D2[~P]).max() * 1e6),
           "dropped_rms_uEh": float(np.sqrt(np.mean(D2[~P] ** 2)) * 1e6),
           "worst_family_cm": worst}, open(HERE / "x20b_prior_bias.json", "w"), indent=1)
