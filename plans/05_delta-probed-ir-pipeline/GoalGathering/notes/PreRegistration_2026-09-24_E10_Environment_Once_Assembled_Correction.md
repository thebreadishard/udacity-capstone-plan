# Pre-registration 2026-09-24, 22:4x — E10: measure each environment once, assemble the correction (the user: "wat is het beste idee dat we nog niet eerder hadden")

**Claim.** If the correction ΔH lives within two bonds (E7, E8, E9), then the neighbourhood block of a substituent is a property of the
substituent's environment, not of the host molecule. It can be measured once, on the smallest host that carries it, and transplanted to every
other host — as E9 transplants the parent core's block. The label price of a molecule then becomes the price of the environment types it
contains; for the A2 layer 14 cores + 15 substituent neighbourhoods instead of 199 molecules.

**Data (fixed).** As E9: the corpus on 24 September, 182 admitted substituted molecules, 14 cores, 15 substituents; DFT–DFT ΔH (ωB97X − B3LYP,
projected Hessians). For each substituent X the **donor** is the admitted host of X with the fewest atoms (ties: the first id in sorted order); all
other hosts of X are **receivers** (the donor is not scored).

**Construction (fixed).** For a receiver S with parent core C and donor D (same substituent X):
1. Neighbourhood N₂ of S as in E9 (substituent atoms + atoms within two bonds); the same for D.
2. Map N₂(D) → N₂(S): the substituent atoms by RDKit substructure match of the substituent-plus-ipso fragment, extended to the ortho atoms by the
   bond graph and to their hydrogens by nearest position after a Kabsch alignment on the matched heavy atoms (the script asserts the two
   neighbourhoods have the same element multiset; a receiver whose neighbourhood differs from the donor's — e.g. a ring nitrogen at the ortho
   position — is skipped and counted).
3. ΔH_assembled = the core's ΔH_C wherever both atoms are mapped to the core (E9 variant (d): far × far and near × far), overwritten on the
   near × near block by the donor's block rotated into S's frame with the Kabsch rotation of the neighbourhood. Nothing is fitted; nothing of S's
   own ΔH is used.
4. Comparisons: (a) assembled (the claim); (b) E9 variant (d) with S's own near × near block (the ceiling of this construction: what a measured
   block gives); (c) core only (near × near zero); the zero rule.

**Read-outs (fixed; E6/E7, pooled over receivers):** corrected-frequency RMS, ring coupling ratio, ring diagonal RMS, Duschinsky overlap median,
ΔH residual ratio; per substituent and per core printed (not registered). Cost read-out: the number of distinct measurements the A2 layer would
need under the claim (cores + donors) against the number of molecules.

**Reading (fixed before any number), variant (a):**
- **Pass:** corrected-frequency RMS ≤ 3.3 cm⁻¹ and ring coupling ratio ≤ 0.5 (the E9 bars) → the environment-once label strategy holds on the
  proxy; the coupled-cluster plan for substituted molecules becomes "one donor per substituent" and L2's molecule is re-chosen as the smallest
  host of its substituent.
- **Fail:** corrected-frequency RMS > 6 cm⁻¹ or ratio > 0.8 → the neighbourhood block depends on the host beyond two bonds; labels stay per
  molecule (E9's saving stands, this one does not).
- **Between:** otherwise; the per-substituent table says which environments transplant and which do not, and the strategy applies to those.

**Not registered:** the per-substituent/per-core tables; a donor-averaged block (mean over several hosts) as a follow-up if between.

**Cost.** Seconds on the laptop, files on disk. Script `modules/05_support_predictor/m05/e10_environment_once.py`; output
`modules/05_support_predictor/data/e9/e10_environment_once_2026-09-24.{json,md}`.

## Outcome — 24 September 2026, 22:5x: BETWEEN as registered; the post-hoc split says which environments transplant

**Registered rule (smallest host of X as donor):** 123 receivers scored, 44 skipped — the smallest hosts of CHO, Cl and OH are quinoxaline
hosts whose substituent sits next to a ring nitrogen, so their neighbourhood signature differs from every carbon-ortho receiver (the registered
skip rule). Pooled: corrected-frequency RMS **3.75 cm⁻¹**, ring coupling ratio 0.24, ΔH residual 0.181 → **between** (pass ≤ 3.3). The
ceiling with the receiver's own block is 1.90, the core alone 8.94, the zero rule 23.10. Output `data/e9/e10_environment_once_2026-09-24.{json,md}`.

**Post-hoc (not registered), two donor rules, 172 receivers each, 25 environment classes (substituent + ortho elements):**

| donor rule | corrected ω RMS | ratio | residual | substituents within the bars (of 15) |
|---|---|---|---|---|
| smallest host in the environment class | 3.61 | 0.23 | 0.172 | 11: F 1.8, OH 2.1, NH2 2.3, CN 2.3, NO2 2.4, CHO 2.6, Cl 2.6, ethynyl 2.2, COOH 2.8, CF3 3.1 — and vinyl 3.6 just outside |
| nearest substituent torsion in the class | **3.36** | 0.23 | 0.160 | 11: CF3 2.5, CHO 2.6, CN 2.3, COOH 2.3, Cl 2.6, F 1.8, NH2 2.2, NO2 2.4, OH 2.2, ethynyl 2.7, vinyl 3.0 |
| (own block, the ceiling) | 1.92 | 0.15 | 0.085 | — |

What fails under every rule: **CH3 (4.2–4.5), OCH3 (4.1–4.2), SH (4.1–7.5), CONH2 (5.9–7.4)** — the rotor and soft-torsion substituents,
whose neighbourhood block depends on the conformation more finely than a rigid rotation of a donor block captures (the torsion match helps SH
from 7.5 to 4.1 and hurts CONH2). The planar or rigid substituents (halogens, CN, NO2, CHO, COOH, ethynyl, vinyl, NH2, OH, CF3) transplant to
1.8–3.1 cm⁻¹, within a cm⁻¹ of the ceiling.

**Reading, within scope (proxy).** The environment-once strategy holds for 11 of 15 substituent types; for the four rotor types the label stays
per molecule (or per conformer, a follow-up). Cost for the A2 layer under that split: 14 cores + 11 donors + the 43 rotor-type molecules ≈ 68
measurements for 182 molecules (2.7× fewer), each measurement itself a neighbourhood under E9 (4× fewer gradients). The coupled-cluster
confirmation is the same L2 chain: the donor of a transplantable substituent is the first molecule to price. Note: the cost line in the JSON counts
all 42 layer-A molecules as "cores"; the 14 actually used are the number that matters.
