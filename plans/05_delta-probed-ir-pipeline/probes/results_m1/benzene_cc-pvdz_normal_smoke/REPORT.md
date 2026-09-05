# Probe M1 — frozen spaces — benzene cc-pvdz, LNO thresholds [1e-05, 1e-06], 2026-09-05 15:39, Asus18 (WSL), 8 threads

- reference: 15 fragments (one per PM LMO); frozen-space hash `10b828887fbb36b5…`; arm C at the reference 170 s
- **stage 0 round trip** E_A(0) − E_C(0) = 0.0000 µE_h (the object reloads; target ≤ 1e-3 µE_h)
- raw energies sealed: `m1_sealed_energies.json`, sha256 `ea053eee71b5dd37…` — not printed

| mode | family | ω (cm⁻¹) | q | s_min occ | off-diag occ | s_min vir | off-diag vir | PM fresh | PM transported | match | A−B (µE_h) | A−C (µE_h) | B−C (µE_h) | s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 12 | CH-ip-bend | 1020 | -1.00 | 0.9907 | 6.6e-03 | 0.8721 | 1.1e-01 | 7.010 | 7.003 | 0.836 | +169.09 | +101.58 | -67.52 | 463 |
| 12 | CH-ip-bend | 1020 | +0.00 | 1.0000 | 3.0e-14 | 1.0000 | 1.1e-12 | 7.000 | 7.000 | 1.000 | +0.00 | +0.00 | +0.00 | 395 |
| 12 | CH-ip-bend | 1020 | +1.00 | 0.9943 | 7.0e-03 | 0.8087 | 9.8e-02 | 6.998 | 6.996 | 0.964 | -52.18 | -92.22 | -40.05 | 399 |


No verdict is printed (the τ it would be judged against does not exist yet). Printed by probes/m1_frozen_spaces.py.