# Price of the corpus fill list (405 molecules, fill_t30.json)

6-31G* functions 113–498, median 207.

| route | timed rows (functions) | seconds | fill hours |
|---|---|---|---|
| deck, CPX62, 16 threads | 839 (100–318) | e^-9.20 n^3.21 | 861 |
| deck, CPX62, 8 threads | 259 (94–401) | e^-8.97 n^3.22 | 1,120 |
| deck, laptop | 77 (102–258) | e^-5.43 n^2.63 | 1,276 |
| analytic labels, CCX53 8-thread lane (n = atoms) | 705 (8–30 atoms) | e^-1.90 n^3.54 | 2,686 lane-hours = 672 server-hours ≈ €574 |

Extrapolated: 33 fill molecules above the largest timed deck row (401 functions), 127 above the lanes' largest molecule.
