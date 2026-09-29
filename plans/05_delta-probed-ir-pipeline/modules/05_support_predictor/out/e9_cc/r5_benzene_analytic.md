# R5 — diagonal against couplings (R5 benzene (analytic low level), 2026-09-29 09:53); low level pyscf analytic B3LYP

Share of the zero rule's RMS frequency error (B3LYP against CC, same-family blocks) that the diagonal of the CC correction alone removes; prediction on record: ≥ 70 % in plane (ring-ip), less out of plane.

| molecule | family | modes | RMS zero rule | RMS diagonal only | removed by the diagonal |
|---|---|---|---|---|---|
| A_8448043181 | CH-stretch | 6 | 102.12 | 0.01 | **100 %** |
| A_8448043181 | CH-oop | 6 | 48.12 | 0.00 | **100 %** |
| A_8448043181 | ring-ip | 13 | 22.99 | 1.86 | **92 %** |
| A_8448043181 | other | 5 | 42.93 | 0.00 | **100 %** |
| A_8448043181 | all | 30 | 55.54 | 1.23 | **98 %** |
