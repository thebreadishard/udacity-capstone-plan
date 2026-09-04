# Batch status

Regenerated 2026-08-28 02:17:28 by `batch_runner.py` (pid 12144).
**9 done, 5 failed, 0 queued.**

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
| 5 | `02_freq_phenanthrene` | freq | done | 39.2 min | band 752.7 cm-1 |
| 6 | `01d_cc_naphthalene_631gs` | cc_timing | FAILED |  | Error occurred in file: C:/bld/psi4_1786163301228/work/psi4/src/psi4/f |
| 7 | `03_freq_tetracene` | freq | done | 71.7 min | band 908.9 cm-1 |
| 8 | `04_freq_chrysene` | freq | done | 75.3 min | band 778.0 cm-1 |
| 9 | `05_freq_triphenylene` | freq | done | 72.1 min | band 757.9 cm-1 |
| 10 | `06_freq_pyrene` | freq | done | 54.0 min | band 866.0 cm-1 |
| 11 | `09_freq_benzene_tight` | freq | done | 4.2 min | band 694.3 cm-1 |
| 12 | `07_freq_coronene` | freq | done | 173.5 min | band 879.5 cm-1 |
| 13 | `04_cc_benzene_ccpvtz` | cc_timing | FAILED |  | Error occurred in file: C:/bld/psi4_1786163301228/work/psi4/src/psi4/f |
| 14 | `08_cc_naphthalene_ccpvdz` | cc_timing | FAILED |  | Error occurred in file: C:/bld/psi4_1786163301228/work/psi4/src/psi4/f |

`heartbeat.json` carries the pid and the job in flight. If its timestamp is
stale and the pid is gone, the runner died and can simply be started again:
finished jobs are skipped, so nothing is repeated.
