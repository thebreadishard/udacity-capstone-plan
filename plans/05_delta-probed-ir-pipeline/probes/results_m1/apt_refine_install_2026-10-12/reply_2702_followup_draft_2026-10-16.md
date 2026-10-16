# Follow-up on pyscf/pyscf#2702 — DRAFT, not posted (16 Oct 2026, 04:5x; to be posted only on the user's word)

*Numbers: `repro_2702_large.log` (C12H9Cl; 3384 13 Oct 16:19–22:36, 3384tol 13 Oct 22:36 – 16 Oct 04:50), `repro_2702_small.log` (water,
benzene), `floor_B_127dd8c4ed/diagnose_floor.json` (scipy GMRES, 2,251 s for the twelve worst columns from a batched start). Script
`repro_2702.py` (the residual measure and the counted Krylov operator). "3384tol" = #3384 (e799bb1 on master 52f5737) with one change in
`lib/linalg_helper.py` line 1412: `_per_rhs_refine(..., tol, ...)` instead of `fallback_tol` — the suggestion of the previous comment.
All timings on a laptop that ran other jobs at the same time (WSL, 4 threads requested); the operator counts do not depend on load.*

---

Following up on my question whether the per-root solve could run to `tol`: I tried it (one-line change, `_per_rhs_refine(..., tol, ...)`
on top of #3384) on the same three cases. The residual is the e_ai-scaled max |residual| of the equations `solve_withs1` solves, as before.

| case | #3384 as is | #3384, per-root solve to `tol` |
|---|---|---|
| water B3LYP/6-31G | 1.5e-6, 1.2 s, 38 operator vectors | 9.3e-11, 3.0 s, 50 vectors |
| benzene PBE/6-31G* (99, 590) | 5.4e-8, 1,058 s, 179 vectors | 5.4e-8, 1,036 s, 179 vectors (no fallback needed) |
| C12H9Cl B3LYP/6-31G* (99, 590) | 8.1e-5, 16,305 s, 355 vectors | **3.2e-8**, **191,767 s**, 489 vectors |

So running the per-root solve to `tol` does converge the C12H9Cl case, by more than three orders of magnitude, and the water case too. But
the time goes up far more than the operator applications do: 1.4× the vectors for 11.8× the time on C12H9Cl, 1.3× for 2.5× on water. I
counted the vectors by wrapping the operator passed to `lib.krylov`, so applications made through another path inside the fallback would not
be counted; if the count is complete, most of the time is spent outside the operator. I have not profiled it — the machine was also loaded,
so please take the absolute times with care, but the ratio on water (seconds, small) points the same way.

For comparison, scipy's GMRES on each of the twelve worst C12H9Cl columns alone, starting from a batched solution, reached ≤ 1.2e-11 in
2,251 s in total.

Happy to run a profile of the per-root solve on the water case if that helps.
