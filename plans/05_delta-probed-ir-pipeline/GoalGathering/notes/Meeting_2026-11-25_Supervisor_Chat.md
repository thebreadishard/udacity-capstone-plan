# The supervisor's chat, 25 November 2026

Written 25 Nov 12:48, right after the conversation. The supervisor sat at the keyboard at the UvA and asked her questions slide by
slide (the PDF of 23 November, 27 pages); the assistant answered under `Supervisor_Chat_Brief_2026-11-25.md` and
`Supervisor_Chat_Facts_2026-11-25.md`. This note holds what she said, what was looked up or counted during the chat, and what
follows. Her statements are given as she made them (Dutch, here in English); nothing here is a decision of the project until the
user makes it one. No run was started during the chat; no live demo was asked for.

## What she wants (her words, in the order she said them)

1. **Accuracy: 2 cm⁻¹, not 3.** 'Preferably within 2 cm⁻¹, neutrals and cations; starting with the neutrals is a good first
   step.' Then: 'if three of the four kinds of vibration come under 2 cm⁻¹ we are already happy.' The skeletal modes 'matter but
   are not the main goal; if those do not come under 2 cm⁻¹ that is not bad.'
2. **Spectral range: the aromatic infrared bands first**, 'outside them is of secondary importance'. She corrected the
   assistant: 600–700 cm⁻¹ lies inside that range (the assistant had taken 3–20 µm, 500–3300 cm⁻¹, and she did not contradict
   those limits).
3. **Charge states**: neutrals first, cations 'very interesting' but she needs to know what they cost in time and anchors;
   'anions are not the goal at the moment'. The 50 cations among 1,132 entries: fine for a proxy test, 'but if the project is
   later used on ions it may be handy to look at this bias'.
4. **Elements**: C, H, N, O, P, S are what occurs ('CHNOPS'), perhaps iron; phosphorus and iron 'are not important' but she does
   not exclude them. **Chlorine and fluorine are not in scope at all.** She proposed a decision matrix that weights the CHNOPS
   elements more heavily in the selection of the ≈ 300 anchors, by presence in interstellar space.
5. **Detected molecules**: look at the Cologne database (CDMS). But 'this list is biased: we can only see very specific PAHs
   because of their dipole moment', and 'most PAHs we cannot detect, we assume'.
6. **Size**: 30–80 carbon atoms and photostable — 'which does not mean only compact structures, there are all kinds of
   protection mechanisms'; recent publications put interstellar PAHs below 80 carbon atoms rather than at 100–150, 'favourable
   towards the smaller sizes'. 'Starting with smaller sizes is fine.' Photostability as a selection criterion: she raised it,
   then said 'leave photostability out for now'.
7. **Astrochemical value**: not cyano-PAHs in particular; rather **explaining the satellite bands around the aromatic bands,
   such as the one at 6.0 µm**, now speculated to come from carbonyl groups — aldehydes at the edge and quinones, 'both'; other
   satellite bands matter too: 'it tells us a lot about PAH derivatives or even carbon allotropes'.
8. **Experiment**: cold gas-phase measurements on the smaller pure PAHs 'come closest to the truth' — for neutrals ion-dip
   spectroscopy, cavity ring-down, matrix isolation, emission spectroscopy; for ions, ion traps and storage rings. She asked
   whether absolute accuracy against experiment is looked at (it is not, for the product), and whether measurements where the
   prediction agrees should be treated differently from those where it does not.
9. **Anharmonicity**: she asked how the coupled-cluster route includes it, whether combination bands and polyads could be had,
   and whether her group's SPECTRO-based method (Mackie et al.) could be used; its availability to us she will look into, 'for
   later'. On the two coronene modes: 'many couplings can occur there'; 'anharmonic calculations may be needed to get these
   errors down with DFT'.
10. **Intensities** 'matter, but the most important is that we reach the 2 cm⁻¹ in frequencies'.
11. **Publications**: 'one publication should be enough for now; the data are published under their own DOI anyway (an RDM
    requirement)' — the method paper, 'unless a really clear added insight for astrochemistry comes out'.
12. **Compute**: she asked whether access to SURF (the national computing centre) would be handy.
13. **Electronic spectra** are a current interest of hers (TD-DFT, a separate project): 'if we learn something here for those
    predictions I would like to hear it'.
14. **Practical**: she asked for the list of papers we still need with their DOIs, and asked the student to set up a Slack
    workspace for their communication.

## Counted or looked up during the chat (scripts in the session's scratchpad; each is a few lines of RDKit on the manifest)

- **The 1,132 training entries** (the handed-out network's `train_ids`): 1,082 neutral, 50 radical cations. Of the neutrals
  only 16 are unsubstituted pure hydrocarbons; 653 substituted carbon ring systems, 393 substituted with a ring heteroatom, 20
  unsubstituted heterocycles; one to five rings (221 / 524 / 233 / 79 / 25). Elements beside C and H: N in 646, O 584, F 175,
  S 144, Cl 87.
- **The plan of 167 reference molecules**: 81 contain F or Cl (F 49, Cl 42); N in 159, O 31, S 21; **no carbonyl group in any
  of the 167, nor in the 23 carried references**. Of the 23 carried, 8 contain F or Cl. Of wave 2's 122 staged molecules, 68
  contain F or Cl. Of wave 1's 20 molecules still running, 5 do (isoquinoline+F, naphthalene+F twice, naphthalene+Cl,
  quinoline+Cl).
- **Carbonyl in the training set**: 298 of 1,082 neutrals (aldehyde 106, carboxylic acid 105, amide 106), 5 ketones, **one**
  molecule with the carbonyl carbon in a ring.
- **Bond type is not an input of the network**: connectivity comes from distances, every bond counts as the same kind
  (`internal_coords.py`); bond character enters through the bond length and the B3LYP force constants.
- **Coronene's two modes** (807.1 and 642.9 cm⁻¹, B3LYP/6-31G*, from the QFF run's reference Hessian): both non-degenerate,
  fully out of plane, even under inversion and odd under the six-fold rotation (b1g or b2g, not told apart), mostly carbon
  motion (hydrogen share 0.07 and 0.09) — skeletal puckering, the same symmetry type as benzene's ring puckering.
- **The rehearsal's curve at 2 cm⁻¹** (`out/anchor_count_2026-10-29/anchor_count_read.md`, arm c, body1_es, against ωB97X):
  ring in-plane 2.05 at k = 170 and 1.71 at 200; CH stretch 2.20 and 1.76; CH out-of-plane 2.98 and 2.73. So two kinds cross 2
  between 170 and 200; CH out-of-plane does not by 200 (the assistant's extrapolation, about 300, is not a measurement).
- **'Other' by frequency** (October, an earlier network): 77 % of its error below 700 cm⁻¹; not split at 500 cm⁻¹, and not
  redone for the current network.
- **CDMS, 'Molecules in Space'** (page of 13 October 2026, about 350 molecules): the aromatic species listed are benzene,
  benzyne, benzonitrile, phenylacetylene, indene, cyanoindene, 1- and 2-cyanonaphthalene, four cyanoacenaphthylenes, phenalene,
  three cyanopyrenes, cyanocoronene, the fullerenes, and a sulfur-containing six-ring (2026). F and Cl occur only in small
  species (HF, CF⁺, AlF, HCl, CH₃Cl, NaCl …), in no aromatic one. Read through a fetch agent; not re-read by hand.
- **Mai et al. 2026 on their basis set**: they chose 4-31G 'for its computational efficiency in high-throughput generation',
  acknowledging it lacks diffuse and polarisation functions (read in the PDF in `Papers/`).
- **DOIs** (Crossref, matched on journal, volume and page): Qu 2026 10.1063/5.0320718; Di Grande 2024
  10.1021/acs.jctc.4c00900; Puzzarini 2019 10.1021/acs.chemrev.9b00007; Bloino 2012 10.1021/ct200814m; Bloino 2015
  10.1021/jp509985u; Martin, Taylor & Lee 1997 10.1016/s0009-2614(97)00735-5; Moran 2006 10.1021/ja0630285; Hanson-Heine 2026
  (the power-law preprint) 10.26434/chemrxiv.15000348/v1; Mackie et al. 2021 10.1007/s00214-021-02807-z. **Not found**: 'Mackie
  2026, JCP 165, 034104' and 'Barone 2026, JCP 164, 114309' — slide 19's citations may be wrong.

## Where the assistant was corrected or wrong

- It said the skeletal modes below 600–700 cm⁻¹ fall mostly outside the AIB range; she: 600–700 cm⁻¹ is inside. Only what lies
  below about 500 cm⁻¹ is outside.
- It listed OH among the working substituents as if slide 13 named them; the slide names only the four that fail (the eleven
  are in the speaker note).
- It called benzonitrile and indene 'detected in TMC-1' from its own knowledge, before the CDMS list was read; the list has
  both.

## What follows (each has its row on the board)

The goal (2 cm⁻¹ on three kinds, the AIB range, neutrals first), the re-selection of the anchors (F and Cl out, carbonyl and
pure PAHs in, weights by interstellar presence), an error per spectral region, the literature to find, and the practical
points (one paper and a dataset DOI, Slack, SURF, SPECTRO): TASKS 305–309. Wave 2 as staged holds 68 halogen molecules of 122
and should not be launched as it stands.

## After the chat, the same afternoon (25 Nov 12:55)

- The user: stop the halogen molecules of wave 1. Four were still waiting and were taken out of their servers' lists
  without stopping anything (naphthalene+F twice, naphthalene+Cl, quinoline+Cl); the fifth, isoquinoline+F, had already
  finished and was collected, which makes 24 reference Hessians.
- The supervisor's addition, through the user: graphene and fullerenes are in scope too.
- The user: every request for papers carries a clickable DOI link per paper.
