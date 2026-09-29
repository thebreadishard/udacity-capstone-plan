# R5 — diagonal against couplings (R5 benzene ((T)-lambda route, analytic low level), 2026-09-29 23:12); low level pyscf analytic B3LYP

Share of the zero rule's RMS frequency error (B3LYP against CC, same-family blocks) that the diagonal of the CC correction alone removes; prediction on record: ≥ 70 % in plane (ring-ip), less out of plane.

| molecule | family | modes | RMS zero rule | RMS diagonal only | removed by the diagonal |
|---|---|---|---|---|---|
| A_8448043181 | CH-stretch | 6 | 99.29 | 0.00 | **100 %** |
| A_8448043181 | CH-oop | 6 | 72.03 | 0.00 | **100 %** |
| A_8448043181 | ring-ip | 13 | 24.96 | 2.62 | **89 %** |
| A_8448043181 | other | 5 | 55.94 | 0.00 | **100 %** |
| A_8448043181 | all | 30 | 61.65 | 1.73 | **97 %** |
