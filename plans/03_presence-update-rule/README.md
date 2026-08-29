# Plan 03 — Presence-Update-Rule

**Status: current as of 2026-08-29.**  
Supersedes plan 02 (Coupled-Cluster Anharmonic IR).  
Plan 01 and plan 02 remain in the repository, complete and readable.

**Promised deliverable.** A *single* translation-equivariant local update rule

\[
(\rho_+,\rho_-,\mathbf{j},\mathbf{E},\mathbf{B})_{\mathcal{N}(x)}
\;\longmapsto\;
(\rho_+,\rho_-,\mathbf{j},\mathbf{E},\mathbf{B})_{x}^{t+\Delta t}
\]

trained as one 3-D stencil / small conv-net, evaluated on a **frozen** real-space grid, with a pre-registered one-step and rollout test on **H₂** and a transfer test on **H₂O**.

Infrared spectra, JWST identification, and C₃₈₄H₄₈ are **not** Module 08 promises. They sit in Horizon 10–12.

Nothing in this folder has been executed. Nothing here is a result.
