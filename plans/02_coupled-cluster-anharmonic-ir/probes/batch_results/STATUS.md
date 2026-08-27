# Batch status

Regenerated 2026-08-27 13:44:01 by `batch_runner.py` (pid 18416).
**2 done, 4 failed, 6 queued.**

Machine: Asus18, 16 logical cores.

| # | job | kind | state | wall time | result |
|---|---|---|---|---|---|
| 1 | `01_cc_benzene_ccpvdz` | cc_timing | FAILED |  | RuntimeError: 
Fatal Error: not enough memory (ccsd).
Error occurred i |
| 2 | `01a_cc_benzene_ccpvdz_28gb` | cc_timing | FAILED |  | RuntimeError: 
Fatal Error: not enough memory (ccsd).
Error occurred i |
| 3 | `01b_ccsd_benzene_ccpvdz` | cc_timing | done | 0.2 min | 114 basis fn |
| 4 | `01c_cc_benzene_631gs` | cc_timing | done | 0.3 min | 102 basis fn |
| 5 | `02_freq_phenanthrene` | freq | queued |  |  |
| 6 | `03_freq_triphenylene` | freq | queued |  |  |
| 7 | `04_cc_benzene_ccpvtz` | cc_timing | FAILED |  | Error occurred in file: C:/bld/psi4_1786163301228/work/psi4/src/psi4/f |
| 8 | `05_freq_chrysene` | freq | queued |  |  |
| 9 | `06_freq_pyrene` | freq | queued |  |  |
| 10 | `07_freq_tetracene` | freq | queued |  |  |
| 11 | `08_cc_naphthalene_ccpvdz` | cc_timing | FAILED |  | Error occurred in file: C:/bld/psi4_1786163301228/work/psi4/src/psi4/f |
| 12 | `09_freq_coronene` | freq | queued |  |  |

`heartbeat.json` carries the pid and the job in flight. If its timestamp is
stale and the pid is gone, the runner died and can simply be started again:
finished jobs are skipped, so nothing is repeated.
