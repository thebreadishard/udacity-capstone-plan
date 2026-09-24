# Probe M1 — frozen spaces — naphthalene cc-pvtz, LNO thresholds [1e-06, 1e-07], arms A, 2026-09-24 21:02, Asus18 (WSL), 8 threads

- reference: 24 fragments (one per PM LMO); frozen-space hash `a4fdb8fed0989c11…`; arm C at the reference 10 s
- **stage 0 round trip** E_A(0) − E_C(0) = 0.0002 µE_h (the object reloads; target ≤ 1e-3 µE_h)
- raw energies sealed: `m1_sealed_energies.json`, sha256 `4dc086e7942a9682…` — not printed
- resumed 2026-09-20 19:34: reference spaces reloaded from `frozen_spaces_reference.npz`, 5 finished points kept from the interrupted run; reload test +0.0000 µE_h

| mode | family | ω (cm⁻¹) | q | s_min occ | off-diag occ | s_min vir | off-diag vir | PM fresh | PM transported | match | A−B (µE_h) | A−C (µE_h) | B−C (µE_h) | s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 12 | CH-oop | 785 | -1.00 | 0.9901 | 1.1e-02 | 0.3842 | 9.9e-01 | 11.256 | 11.255 | 1.000 | — | — | — | 43888 |
| 12 | CH-oop | 785 | -0.50 | 0.9951 | 5.3e-03 | 0.5688 | 3.3e-01 | 11.256 | 11.256 | 1.000 | — | — | — | 44249 |
| 12 | CH-oop | 785 | +0.00 | 1.0000 | 9.7e-14 | 1.0000 | 6.8e-12 | 11.256 | 11.256 | 1.000 | — | — | — | 44702 |
| 12 | CH-oop | 785 | +0.50 | 0.9952 | 5.3e-03 | 0.5692 | 3.3e-01 | 11.256 | 11.256 | 1.000 | — | — | — | 45236 |
| 12 | CH-oop | 785 | +1.00 | 0.9902 | 1.1e-02 | 0.3848 | 1.0e+00 | 11.256 | 11.255 | 1.000 | — | — | — | 46027 |
| 22 | CH-ip-bend | 1045 | -1.00 | 0.9934 | 7.2e-03 | 0.6278 | 2.4e-01 | 11.255 | 11.255 | 1.000 | — | — | — | 42277 |
| 22 | CH-ip-bend | 1045 | -0.50 | 0.9967 | 3.5e-03 | 0.7881 | 1.2e-01 | 11.256 | 11.256 | 1.000 | — | — | — | 42861 |
| 22 | CH-ip-bend | 1045 | +0.00 | 1.0000 | 9.7e-14 | 1.0000 | 6.8e-12 | 11.256 | 11.256 | 1.000 | — | — | — | 0 |
| 22 | CH-ip-bend | 1045 | +0.50 | 0.9967 | 3.5e-03 | 0.7884 | 1.2e-01 | 11.256 | 11.256 | 1.000 | — | — | — | 43469 |
| 22 | CH-ip-bend | 1045 | +1.00 | 0.9934 | 7.2e-03 | 0.6282 | 2.4e-01 | 11.255 | 11.255 | 1.000 | — | — | — | 43424 |
| 31 | CC-stretch | 1410 | -1.00 | 0.9931 | 4.1e-03 | 0.5510 | 3.9e-01 | 11.251 | 11.250 | 1.000 | — | — | — | 45172 |
| 31 | CC-stretch | 1410 | -0.50 | 0.9966 | 2.1e-03 | 0.7318 | 1.9e-01 | 11.255 | 11.255 | 1.000 | — | — | — | 45652 |
| 31 | CC-stretch | 1410 | +0.00 | 1.0000 | 9.7e-14 | 1.0000 | 6.8e-12 | 11.256 | 11.256 | 1.000 | — | — | — | 0 |
| 31 | CC-stretch | 1410 | +0.50 | 0.9966 | 2.1e-03 | 0.7322 | 1.9e-01 | 11.254 | 11.254 | 1.000 | — | — | — | 43465 |
| 31 | CC-stretch | 1410 | +1.00 | 0.9932 | 4.1e-03 | 0.5515 | 3.9e-01 | 11.249 | 11.248 | 1.000 | — | — | — | 44574 |


No verdict is printed (the τ it would be judged against does not exist yet). Printed by probes/m1_frozen_spaces.py.