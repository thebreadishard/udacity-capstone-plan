import json, numpy as np
d = json.load(open('results_dryrun/naphthalene_sym/stageB2_floor.json'))
q = np.linspace(-1, 1, 9)
sig = d["pooled_sigma_E_uEh"]
print("Even part of the stand-in response fitted as c2*q^2 + c4*q^4 (uE_h).")
print("The quartic term IS the contamination of a quadratic read; the question is whether")
print("q^2+q^4 is the whole story, i.e. whether the residual sits at the noise floor.\n")
print(f"{'mode':>18} {'c2':>12} {'c4 (=cont. @q=1)':>18} {'@q=0.5':>10} {'resid RMS':>10} {'/sigma':>7}")
for name, v in d["per_mode"].items():
    y = np.array(v["dE_uEh"])
    ev = 0.5 * (y + y[::-1]) - y[4]
    A = np.vstack([q**2, q**4]).T
    c, *_ = np.linalg.lstsq(A, ev, rcond=None)
    res = ev - A @ c
    rms = float(np.sqrt(np.mean(res**2)))
    print(f"{name:>18} {c[0]:12.3f} {c[1]:18.3f} {c[1]/16:10.3f} {rms:10.4f} {rms/sig:7.2f}")
print(f"\npooled DFT-arm noise sigma_E = {sig:.4f} uE_h over nu = {d['nu_pooled']}")
print("stage C for comparison: off-diagonal signal 7.00 uE_h, model floor 6.74 uE_h, both at q = 1.")
