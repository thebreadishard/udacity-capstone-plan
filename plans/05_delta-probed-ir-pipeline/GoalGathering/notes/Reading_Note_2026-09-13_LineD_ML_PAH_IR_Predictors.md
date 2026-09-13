# Reading note 2026-09-13 (late evening) — opponent line D: the Guangxi group's machine-learning PAH-IR predictors

*Read at the user's request ("download en lees de drie open-access-PDF's volledig"). What was actually read: He, Mai & Wang 2026 **in full** from the publisher's open-access HTML (text saved as `Papers/_txt/He2026_AA708_A335_fullhtml.txt`; the PDF download is blocked for scripts and the in-app browser cannot save files); Tang, He, Wang & Qiu 2026 **in full** from the arXiv version 2602.12560 v1 (PDF in `Papers/lineD/`, text in `Papers/_txt/Tang2026_MNRAS546_arXiv2602.12560.txt`; the journal version may differ in detail); Liu, Wang & Qiu 2026 **abstract only** — Oxford's site held the in-app browser at a bot check for the whole evening and no preprint exists (the user's own arXiv search under "Mai, Xinghong" returned only the 2025 paper). All records Crossref-verified; all three CC BY.*

## 1. Records

| item | record | read |
|---|---|---|
| 77 | He, J.; Mai, X.; Wang, Z., *A&A* 708, A335 (2026), DOI 10.1051/0004-6361/202659248 | full (HTML) |
| 78 | Tang, G.; He, J.; Wang, Z.; Qiu, D., *MNRAS* 546, stag283 (2026), DOI 10.1093/mnras/stag283; arXiv:2602.12560 | full (arXiv v1) |
| 79 | Liu, Y.; Wang, Z.; Qiu, D., *MNRAS* 549, stag893 (2026), DOI 10.1093/mnras/stag893 | abstract |
| 81 | Kovács, P.; Zhu, X.; Carrete, J.; Madsen, G. K. H.; Wang, Z., *ApJ* 902, 100 (2020), DOI 10.3847/1538-4357/abb5b6 — the origin of the line ("Machine-learning prediction of infrared spectra of interstellar PAHs") | record (Crossref) |
| 82 | Wang, Z., "Full-spectrum infrared fingerprinting: A transformative AI paradigm for interstellar polycyclic aromatic hydrocarbons", *A&A* 710, L17 (2026), DOI 10.1051/0004-6361/202659999 | record (Crossref), listed by the publisher beside item 77 |
| — | data and code of item 77: `zwAstroChem/ChargeEncoding-IRPrediction` (GitHub, MIT, created 2026-01-28): `Data_to_be_unzipped.zip` 7.0 MB, two training scripts, README | listing and README read via the GitHub API |

Affiliations as printed on the arXiv version of item 78: Laboratory for Relativistic Astrophysics and Center for Applied Mathematics, Guangxi University, Nanning; Chongqing University of Posts and Telecommunications.

## 2. What the two full texts say (numbers as printed)

**He, Mai & Wang 2026 (item 77).**
- *Data.* 1,155 hydrocarbon PAHs chosen from a self-generated library of over a million structures (Perron-root diversity), each at charges −1, 0, +1: **3,465 B3LYP/6-311+G(d,p) harmonic spectra (Gaussian 16), scaled by 0.9757**; plus **9,731 scaled harmonic spectra from PAHdb v4.0** (O and N heteroatoms included; charges −1 to +2; tri-cations, (de)hydrogenated, Si- and metal-containing species excluded); **12,599 species** after de-duplication.
- *Target.* Each spectrum binned into **300 bins of 11.88 cm⁻¹** (6.95–5,376 cm⁻¹), split at 1,753 cm⁻¹, each half **normalised to unit sum** → the model predicts *relative* intensity distributions, not absolute intensities and not positions.
- *Model.* MLP (1500/1000/800/600) on ECFP fingerprints of radius 11 (42,535 fragments) plus a learnable 16-dimensional charge embedding; earth-mover's-distance loss; 6:2:2 split, five-fold cross-validation.
- *Accuracy.* Mean EMD (dimensionless, in bin units of the cumulative distribution): neutral 2.47, di-cation 2.52, cation 2.81; charge-encoded models "marginally less accurate than the neutral-only baseline"; high-frequency modes easier than low-frequency ones. Error vs size: high below 20 C, a rebound at 90–100 C, best (EMD ≈ 1.0) at 130–150 C, fluctuating above 160 C. Speed: inference ∝ N_C^0.037 versus DFT ∝ N_C^4.
- *Validation against the laboratory.* DFT spectra compared to **84 PAHdb experimental (matrix) spectra**, ten shown, judged qualitatively ("strong consistency"); no band-position statistic is printed.
- *Physics claims from the DFT set.* Anions strong at 3.3 and 6.2 µm; anion ≥ cation across 6–9 µm; 11.2 µm charge-dependent; a cation feature at 9.8 µm.
- *Availability.* Code and the training/testing data (SMILES, spectra, charge; JSON) at the MIT-licensed repository.

**Tang, He, Wang & Qiu 2026 (item 78, arXiv v1).**
- *Data.* **PAHdb only**: 1,570 neutral PAHs from version 3.2 (≤ 47 C) for training and validation, 997 neutral PAHs from version 4.0α (50–100 C) for the size test; "most of the spectra were computed via DFT at the B3LYP level".
- *Target.* Bins of **18.23 cm⁻¹** (309 bins to 5,604 cm⁻¹), normalised to the maximum; split at 2,340 cm⁻¹. Their own sensitivity test: **5 cm⁻¹ bins degrade the model** (JSD 0.121/0.308 against 0.029/0.097 at 18 cm⁻¹) — "the model performs best with a slightly coarser binning".
- *Model.* Four GNNs on SMILES-derived graphs (no 3D geometry, no vibrational features — stated as a fundamental limitation); AFP best among GNNs; **a plain MLP on ECFP fingerprints beats all four GNNs**; JSD the best loss at low frequency.
- *Accuracy.* JSD examples 0.048 (best) to 0.195 (worst) on low-frequency spectra; figures broadened with a 10 cm⁻¹ Gaussian; "even the poorest predictions retain the overall spectral shape and capture major bands". Speed: ∝ N_C^0.21 versus DFT ∝ N_C^4.18 (B3LYP/4-31G on 40 cores); > 10,000× above ≈ 40 C.
- *Data availability.* Stated as public in the text; the statement itself is not in the arXiv v1 extract (journal version to check).

**Liu, Wang & Qiu 2026 (item 79, abstract).** Transformer encoder with rotary position embeddings on molecular strings, fine-tuned on 24,146 PAH spectra, charge-sensitive, "bypassing the bottleneck of DFT".

## 3. What this settles for the mandate (obstacle 14)

1. **These are shape predictors at 12–18 cm⁻¹ bin resolution, trained on scaled B3LYP spectra, judged against DFT.** They reproduce DFT's relative intensity pattern per bin; none predicts band positions finer than its bin, none carries a laboratory-referenced error, and their own test says finer bins make them worse. The goal sentence's "better than what exists" therefore has a concrete, measurable meaning against line D: **positions inside their bin width, intensities with a laboratory or coupled-cluster reference, and an error budget per band** — on molecules where line D can be run (SMILES in, spectrum out; the MIT code allows it).
2. **The user's question ("do we still need the data factory?") — answered by their data availability.** Item 77's public data are **SMILES + binned normalised spectra + charge** (7 MB zip); item 78's are PAHdb spectra. **Neither contains Hessians, geometries or two-functional differences.** Our factory produces Hessians and the DFT–DFT correction proxy the network pre-trains on; their data cannot replace that. What their data *can* do: serve as an extra *shape* pre-training or validation set (relative intensity histograms of 12,599 species incl. cations and anions, to 150 C) and as line D's own predictions for the scoreboard. Layers A/A′/B stay; the size axis above four rings is still ours to compute or to take from PAHdb geometries.
3. **Their stated weakness is our stated strength, if T-2 passes.** All three name training-data scarcity above ≈ 100–160 C as the limit and see the remedy in "physics-informed" approaches (item 77's conclusion cites Mai 2025). A correction expressed in transferable local types (X17/X18) is physics-informed by construction; the claim must still be measured.
4. **The lineage is six years old and fast.** Kovács et al. 2020 → Meng et al. 2021/2023 → Mai et al. 2025 (MLMD) → 2026: charge-aware MLP, GNN, LLM, a single-author "AI paradigm" letter (item 82), the ML double-harmonic code (item 74, paper still not found). Module 02's line D should be the *family*, version-frozen at the He 2026 model (public weights), with the others cited.
5. **What the plan should say in §3.1 and §6 (dated revision, after the user reads this):** line D exists and is public; the pipeline's reach product is compared against it on the shape hold-outs of I3 (Lemmens 2021 cold spectra) and on positions at the pipeline's own resolution; the plan's labels are the difference.

## 4. Not established / to do

- Item 79 unread beyond the abstract (OUP bot check); item 78's journal version not compared with arXiv v1; item 82 (the A&A letter) record only; item 74's paper still unfound.
- Whether the He 2026 weights run on our ladder molecules (benzene to coronene) and what EMD they give against *our* B3LYP spectra: a desk test once the code is installed (permission needed; PyTorch + RDKit, light).
- The 84-molecule matrix validation of item 77 is qualitative; Module 03's u_band machinery could quantify it if their DFT spectra are in the zip.
