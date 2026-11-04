"""TASKS 173's decoupling test read by its registered line (ledger 4 Nov 07:3x): shifts of modes 20 and 21 (the CH3 bends) when the
torsion leaves the VPT2, in Cartesian and Z-matrix coordinates; plus every mode's shift for the record."""
import json
import sys
from pathlib import Path

import numpy as np

S = Path(sys.argv[1])
BENDS = (20, 21)
nu = {k: np.array(json.loads((S / f"bridge_4mi_{k}.json").read_text(encoding="utf-8"))["nu_psience_cm"], float)
      for k in ("cart", "zmat", "cart_dec", "zmat_dec")}
d_cart = nu["cart_dec"] - nu["cart"]
d_int = nu["zmat_dec"] - nu["zmat"]
s_cart = max(abs(d_cart[b]) for b in BENDS)
s_int = max(abs(d_int[b]) for b in BENDS)
print("mode   coupled(cart)  Δcart   Δint")
for k in range(1, len(d_cart)):
    print(f"{k:4d}  {nu['cart'][k]:10.2f}  {d_cart[k]:+6.2f}  {d_int[k]:+6.2f}")
print(f"rms over modes 1–29: cart {np.sqrt(np.nanmean(d_cart[1:]**2)):.2f}, int {np.sqrt(np.nanmean(d_int[1:]**2)):.2f}")
print(f"s_cart {s_cart:.2f}  s_int {s_int:.2f}")
if s_cart >= 4 and s_int <= 1.5:
    print("VERDICT: rectilinear decoupling is a coordinate artefact; a hindered methyl keeps its coupled value")
elif abs(s_cart - s_int) <= 1.5:
    print("VERDICT: the same shift in both coordinate sets; this test does not decide")
else:
    print("VERDICT: neither branch; reported as it is")
