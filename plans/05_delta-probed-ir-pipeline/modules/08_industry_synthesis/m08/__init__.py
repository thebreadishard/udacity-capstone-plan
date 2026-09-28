"""Module 08 — the industry synthesis: request officer, certificate generator, replay worker (28 September 2026).

The pipeline repository stays the source of truth: everything here reads the website export (`website/export/out`), the corpus manifest and
ledger, module 03's tolerance table, module 05's learning-curve records, module 07's rule table and gate, and the measured price table.
Nothing here writes into a run directory."""
