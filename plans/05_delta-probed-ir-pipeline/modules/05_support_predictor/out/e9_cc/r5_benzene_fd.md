# R5 — diagonal against couplings (R5 benzene (psi4 FD low level), 2026-09-29 09:54); low level corpus psi4 FD B3LYP

Share of the zero rule's RMS frequency error (B3LYP against CC, same-family blocks) that the diagonal of the CC correction alone removes; prediction on record: ≥ 70 % in plane (ring-ip), less out of plane.

| molecule | family | modes | RMS zero rule | RMS diagonal only | removed by the diagonal |
|---|---|---|---|---|---|
| A_8448043181 | CH-stretch | 6 | 102.07 | 0.04 | **100 %** |
| A_8448043181 | CH-oop | 6 | 47.86 | 0.01 | **100 %** |
| A_8448043181 | ring-ip | 13 | 23.98 | 2.56 | **89 %** |
| A_8448043181 | other | 5 | 46.13 | 0.13 | **100 %** |
| A_8448043181 | all | 30 | 56.08 | 1.69 | **97 %** |
