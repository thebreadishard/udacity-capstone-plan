"""Does the two-route disagreement of the benzene semi-diagonal quartic constants behave like finite-difference noise?
Model: an isotropic error sigma on the (mass-weighted Cartesian) Hessians becomes, in reduced normal coordinates,
delta H_ii ~ sigma/omega_i; route a of phi_iijj (displace j, read ii) is a second difference of H_ii and carries
noise ~ sqrt(6) sigma / (omega_i d^2), route b ~ sqrt(6) sigma / (omega_j d^2). Prediction of the noise model:
|route_a - route_b| for the pair (i, j) scales with sqrt(1/omega_i^2 + 1/omega_j^2) and not with |phi_iijj|.
Truncation error (a too-large step) would instead grow with the size of the constants and the higher derivatives.
Input: the npz written by qff_from_hessians.py (routes in cm-1, omega in cm-1)."""
import sys
import numpy as np

z = np.load(sys.argv[1])
w = z["omega_cm"]; a = z["phi_iijj_route_a"]; b = z["phi_iijj_route_b"]; phi = z["phi_iijj"]
n = len(w); iu = np.triu_indices(n, 1)
d = np.abs(a - b)[iu]; mag = np.abs(phi)[iu]
pred = np.sqrt(1 / w[iu[0]] ** 2 + 1 / w[iu[1]] ** 2)
pred_min = 1 / np.minimum(w[iu[0]], w[iu[1]])


def spearman(x, y):
    rx = np.argsort(np.argsort(x)); ry = np.argsort(np.argsort(y))
    return np.corrcoef(rx, ry)[0, 1]


def r2_log(x, y):
    m = (x > 0) & (y > 0)
    lx, ly = np.log(x[m]), np.log(y[m])
    slope, icpt = np.polyfit(lx, ly, 1)
    res = ly - (slope * lx + icpt)
    return slope, 1 - res.var() / ly.var()


print(f"pairs {len(d)}; |route a - route b|: median {np.median(d):.1f}, p90 {np.percentile(d, 90):.1f}, max {d.max():.1f} cm-1")
print(f"Spearman(|diff|, sqrt(1/wi^2 + 1/wj^2)) = {spearman(d, pred):+.3f}")
print(f"Spearman(|diff|, |phi_iijj|)             = {spearman(d, mag):+.3f}")
s, r2 = r2_log(pred, d)
print(f"log-log fit |diff| vs sqrt(1/wi^2+1/wj^2): slope {s:.2f} (noise model predicts 1.0), R^2 {r2:.2f}")
s2, r22 = r2_log(mag, d)
print(f"log-log fit |diff| vs |phi_iijj|:          slope {s2:.2f}, R^2 {r22:.2f}")
# implied noise amplitude per pair: sigma' = |diff| * d^2 / (sqrt(6) * sqrt(1/wi^2 + 1/wj^2)); its spread says how constant it is
disp = 0.05
sig = d * disp ** 2 / (np.sqrt(6) * pred)
print(f"implied sigma' (cm-1 * cm-1 units): median {np.median(sig):.3g}, IQR {np.percentile(sig, 25):.3g}-{np.percentile(sig, 75):.3g}")
# binned view by the lower frequency of the pair
lo = np.minimum(w[iu[0]], w[iu[1]])
for lo_edge, hi_edge in [(0, 700), (700, 1000), (1000, 1300), (1300, 1700), (1700, 4000)]:
    m = (lo >= lo_edge) & (lo < hi_edge)
    if m.any():
        print(f"  pairs whose lower frequency is in [{lo_edge}, {hi_edge}) cm-1: n={m.sum():3d}, median |diff| {np.median(d[m]):6.1f}, max {d[m].max():7.1f}")
print("prediction for the same Hessians at DISP_SIZE 0.20 if the disagreement is noise: median "
      f"{np.median(d) / 16:.1f}, max {d.max() / 16:.0f} cm-1 (a factor (0.20/0.05)^2 = 16 smaller)")

# --- per-displacement model: diff_ij^2 = s_i^2 + s_j^2, s_k = noise carried by the Hessians displaced along mode k
A = np.zeros((len(d), n)); A[np.arange(len(d)), iu[0]] = 1; A[np.arange(len(d)), iu[1]] = 1
x, *_ = np.linalg.lstsq(A, d ** 2, rcond=None)
x = np.clip(x, 0, None); pred2 = np.sqrt(A @ x)
r2_lin = 1 - ((d - pred2) ** 2).sum() / ((d - d.mean()) ** 2).sum()
print(f"per-displacement noise model (30 parameters for 435 pairs): R^2 on |diff| {r2_lin:.2f}; Spearman(|diff|, model) {spearman(d, pred2):+.3f}")
order = np.argsort(-x)
print("  noisiest displaced modes (index, omega cm-1, s_k cm-1):", ", ".join(f"({k}, {w[k]:.0f}, {np.sqrt(x[k]):.0f})" for k in order[:8]))
print("  quietest:", ", ".join(f"({k}, {w[k]:.0f}, {np.sqrt(x[k]):.0f})" for k in order[-6:]))
# degenerate partners (|dw| < 0.5 cm-1) should share s_k if the noise is structural rather than random per geometry
pairs_deg = [(k, l) for k in range(n) for l in range(k + 1, n) if abs(w[k] - w[l]) < 0.5]
print("  degenerate partners (k, l, s_k, s_l):", ", ".join(f"({k},{l},{np.sqrt(x[k]):.0f},{np.sqrt(x[l]):.0f})" for k, l in pairs_deg))
