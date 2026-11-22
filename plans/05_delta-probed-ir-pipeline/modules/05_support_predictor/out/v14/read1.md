# v1.4 stage 1 — selection-set scores (seeds 0, 1)

| rank | configuration | schedule | score (seed mean) | per seed | registered score (all 169) | worse than control on | best epoch / cap |
|---|---|---|---|---|---|---|---|
| 1 | c07 | cosine | 1.024 | 1.011, 1.038 | 1.117 | — | 195, 163 / 300 |
| 2 | c15 | constant | 1.072 | 1.091, 1.053 | 1.119 | (sel) coupling_ratio | 183, 158 / 300 |
| 3 | c10 | cosine | 1.083 | 1.088, 1.078 | 1.156 | (sel) CH-stretch, (sel) CH-oop, (sel) coupling_ratio | 205, 214 / 300 |
| 4 | c13 | constant | 1.085 | 1.089, 1.080 | 1.142 | (sel) ring-ip, (sel) CH-stretch, (sel) CH-oop, (sel) coupling_ratio | 190, 193 / 300 |
| 5 | c00_control | constant | 1.088 | 1.064, 1.112 | 1.178 | — | 205, 153 / 300 |
| 6 | c09 | cosine | 1.099 | 1.054, 1.145 | 1.153 | (sel) CH-stretch, (sel) CH-oop, (sel) coupling_ratio | 198, 179 / 300 |
| 7 | c02_control_target | constant | 1.119 | 1.119, 1.118 | 1.221 | (sel) CH-stretch, (sel) CH-oop, (sel) other, (sel) coupling_ratio | 214, 231 / 300 |
| 8 | c14 | constant | 1.119 | 1.100, 1.138 | 1.258 | (sel) CH-stretch, (sel) CH-oop, (sel) coupling_ratio | 153, 103 / 300 |
| 9 | c03_control_schedule | cosine | 1.127 | 1.105, 1.149 | 1.230 | (sel) ring-ip, (sel) CH-stretch, (sel) CH-oop, (sel) other, (sel) coupling_ratio | 188, 192 / 300 |
| 10 | c08 | constant | 1.157 | 1.184, 1.130 | 1.240 | (sel) ring-ip, (sel) CH-stretch, (sel) CH-oop, (sel) other, (sel) coupling_ratio | 130, 185 / 300 |
| 11 | c01_control_parity | constant | 1.182 | 1.216, 1.147 | 1.274 | (sel) ring-ip, (sel) CH-stretch, (sel) CH-oop, (sel) other, (sel) coupling_ratio | 149, 139 / 300 |
| 12 | c04 | cosine | 1.191 | 1.212, 1.169 | 1.259 | (sel) ring-ip, (sel) CH-stretch, (sel) CH-oop, (sel) other, (sel) coupling_ratio | 192, 185 / 300 |
| 13 | c12 | cosine | 1.216 | 1.222, 1.210 | 1.334 | (sel) ring-ip, (sel) CH-stretch, (sel) CH-oop, (sel) other, (sel) coupling_ratio | 205, 171 / 300 |
| 14 | c11 | cosine | 1.257 | 1.257, 1.257 | 1.354 | (sel) ring-ip, (sel) CH-stretch, (sel) CH-oop, (sel) other, (sel) coupling_ratio | 185, 170 / 300 |
| 15 | c05 | constant | 1.259 | 1.274, 1.244 | 1.320 | (sel) ring-ip, (sel) CH-stretch, (sel) CH-oop, (sel) other, (sel) coupling_ratio | 185, 220 / 300 |
| 16 | c06 | constant | 1.262 | 1.190, 1.334 | 1.341 | (sel) ring-ip, (sel) CH-stretch, (sel) CH-oop, (sel) other, (sel) coupling_ratio | 97, 98 / 300 |

Stage 2: c07, c15, c10, c13 and the control, seed 2. Two seeds: the no-worsening column informs, stage 2 decides on three.

The score is read on the selection set without biphenylene (161 of 169 molecules, §13); the registered score is the same formula on all 169. **It would send other configurations to stage 2: c07, c15, c13, c09.**
