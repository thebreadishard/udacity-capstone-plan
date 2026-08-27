# Motif Transfer for PAH Spectral Precision

Source: https://grok.com/share/c2hhcmQtNQ_f4531e00-9a2c-4fde-8ece-c662a1191206

Retrieved 2026-08-27. Parsed from the rendered page (DOM to markdown), so headings,
tables, lists and LaTeX are preserved rather than flattened to plain text.

---

### You said

Given this conversation: [https://grok.com/share/c2hhcmQtNQ_eb37fddc-724b-4e06-a22e-e7985aebdbfa](https://grok.com/share/c2hhcmQtNQ_eb37fddc-724b-4e06-a22e-e7985aebdbfa), what would you propose as an alternative plan to achieve chemically precise spectral band predictions for huge aromatic molecules? If you would have 100% freedom to architect a new master thesis plan, what would you do? Complete freedom.

### Grok said

Plan 02 is the right *diagnosis* of Plan 01 and the wrong *instrument* for huge aromatics. It correctly refuses rovibrational line lists, refuses classical MD as the scientific deliverable, and insists on a measured theory anchor plus a decomposed error budget. Then it spends a master’s climbing a molecule ladder that ends at pyrene. Pyrene is not huge. The interstellar carriers that motivate the project are compact PAHs with tens to hundreds of carbons; Mai et al. already published temperature-dependent ML-MD envelopes for 1,704 PAHdb species up to C216.[⁠arXiv](https://arxiv.org/pdf/2503.05120)

A free thesis should not re-implement “fine-tune an equivariant MLIP, differentiate it four times, run GVPT2, identify one frozen JWST product.” That is a feasible capstone. It is not a method that becomes chemically precise *as the molecule grows*.

## Why the current stack cannot be the plan for huge molecules

Three facts, not opinions:

1. **The expensive object is the wrong object.** A global quartic force field plus GVPT2 needs stable third and fourth derivatives of the whole surface. That cost and the resonance network both explode with $3N-6$. For a C100 flake you do not have a QFF problem; you have a reduced-coordinate problem. Plan 02’s own stop rule will fire at C14–C16 if it is honest. That is a measured limit of *the method*, not of PAH spectroscopy.
2. **A whole-molecule “gold rung” on a huge PAH is not gold.** Canonical CCSD(T) frequencies die early. Local CC (DLPNO / LNO) is usable for energies on large systems, but the locality error on delocalized $\pi$ systems grows with size and is not automatically small on *curvatures*. Publishing “term B” on benzene and naphthalene does not license calling DLPNO-CCSD(T) the gold rung of circumcoronene.
3. **JWST AIBs are not a named-species identification problem.** The 3.3, 6.2, 7.7, 8.6, 11.2, 12.7 μm bands diagnose *edge topology, charge, size class, and aliphatic fraction*, not “this is pyrene$^+$.” Fail-closed ID of one pre-registered molecule against one frozen product is methodologically clean and scientifically off-target for huge aromatics. JWST work on the Orion Bar and related PDRs is about compact vs irregular edges, solo/duo/trio/quartet CH, and charge — motif language.[⁠Pubs.acs](https://pubs.acs.org/doi/10.1021/acsearthspacechem.5c00385)

Mai 2025 already owns high-throughput *envelopes*. Ethereal AI already owns learned DFT scaling factors at ~5 cm⁻¹ MAE. Charge-aware GNNs already predict harmonic-like IR across charge states to ~C150. The open scientific gap is not another interpolator. It is a **transferable, motif-local, uncertainty-calibrated anharmonic correction that remains meaningful at C50–C200**.

## Thesis I would actually write

**Title.** Motif-local gold rungs and transferable anharmonic corrections for infrared band families of large polycyclic aromatics.

**One-sentence claim.** Band centres and relative family intensities of large PAHs are local enough to be predicted from gold-quality anharmonic calculations on edge and bay motifs, with a calibrated transfer residual — without ever constructing a global QFF of the huge molecule.

That is the inversion relative to Plan 02:

> Plan 02: borrow the representation, own the whole-molecule theory anchor and the whole-molecule nuclear motion.
>
> This plan: own the *local* theory anchor and the *transfer law*; refuse the global QFF of a huge molecule as a deliverable.

Precision is carried by (i) motif-level electronic structure and nuclear motion that can actually be audited, and (ii) a measured transfer error when those motifs are embedded in larger graphs. Size is no longer a ladder you climb until the software breaks. Size is a test of whether the locality hypothesis holds.

## What “chemically precise” is allowed to mean

Keep Plan 02’s R1/R2/R3 hygiene. Change the target of R3.

| Reading | Status here |
| --- | --- |
| R1 — rovibrational line lists | Forbidden |
| R2 — classical ML-MD envelopes | Diagnostic and temperature kernel only; already published at C216 |
| R3a — named mid-size species | GVPT2-class band families vs a named gas-phase / IRMPD / He-tagged standard, with a four-term budget |
| R3b — huge species | Band *families* (not 3N−6 lines) from motif transfer, with a fifth term: **embedding / transfer residual**, measured on held-out mid-size molecules, not guessed |

Scored families, same physics as the ISM:

- 3.3 μm aromatic CH stretch
- 6–9 μm CC stretch + CH in-plane
- 11–15 μm CH out-of-plane, split by **solo / duo / trio / quartet** (this split is the chemically precise observable JWST actually uses)

Charge states: neutral, cation, selected dication. Superhydrogenated and one aliphatic-side-chain class as a negative-control family (the 3.4 μm band), not as scope creep.

## Architecture

Five layers. None of them is a new network for its own sake.

### 1. Motif atlas (the actual chemical object)

Build a finite atlas of spectroscopically distinct local environments, not a molecule list:

- solo / duo / trio / quartet CH on armchair vs zigzag
- bay, fjord, cove
- five-membered rings (fluoranthene-type)
- interior vs edge CC
- charge-perturbed versions of each
- a small aliphatic pendant set for the 3.4 μm control

Each motif is realized as a *capped fragment* and as a *full small PAH* that isolates that motif (naphthalene, anthracene, phenanthrene, pyrene, tetracene, chrysene, perylene, coronene, ovalene, and a few non-compact controls). The huge molecule is later treated as a graph of these motifs plus a weak coupling model.

This is the opposite of “stop at the first rung that misses 10 cm⁻¹.” The mid-size set is the *training and audit set*. Huge molecules are the *application set*.

### 2. Gold rung where it can be gold

On the atlas only:

- Canonical CCSD(T) (or CCSD(T)-F12) geometries, harmonics, and as much of the QFF as is affordable, for the smallest motifs.
- Tight local CC (LNO-CCSD(T) / DLPNO-CCSD(T1), Tight/vTight, CBS or F12) on the rest of the atlas, with **term B measured on the subset where canonical is possible** — including *frequency and cubic-constant* errors, not only energies. Acene-like delocalization is the hostile test, not water clusters.
- Open-shell cations get an extra gate: if $\langle S^2 \rangle$ or local-CC vs canonical curvature error blows the budget, cations are a separate, smaller atlas, not a silent extension.

DFT (a modern range-separated hybrid + the PAHdb B3LYP baseline) is the *cheap parent surface*, never the claimed accuracy.

### 3. Nuclear motion: local anharmonicity, not a global GVPT2 of C96

For each motif / mid-size PAH:

- GVPT2 from a QFF on the parent DFT surface, Δ-corrected toward the gold rung on displacements that matter for the scored families.
- Explicit Fermi / Darling–Dennison treatment inside the 6–9 μm and CH-stretch manifolds.
- Selected VCI only on those manifolds when GVPT2 resonances fail.
- No global QFF of a huge target.

For huge targets, nuclear motion is a **dressed local-mode / fragment Hamiltonian**:

- local anharmonic oscillators living on motifs
- bilinear and selected cubic couplings between neighboring motifs, taken from mid-size dimers of motifs (two fused environments), not from the huge molecule
- thermal occupation and UV-pumped emission treated as a separate kernel (can reuse ML-MD / RPMD *as a temperature kernel*, which is what R2 is good for)

That is how you get anharmonic band families at C100 without pretending you differentiated a 300-atom MLIP four times.

### 4. Transfer model (this is the ML, and it is small)

Do not learn a PES of the universe. Learn the residual:

$$\Delta \tilde{\nu}_{\text{family}} = \tilde{\nu}_{\text{anharm, gold-local}} - \tilde{\nu}_{\text{scaled-harm, DFT}}$$

and the analogous relative-intensity correction, as a function of:

- local graph / edge type
- bond orders and Hessian-projected local modes
- formal charge and a cheap electrostatic embedding
- a short-range environment descriptor (equivariant, off-the-shelf)

Training labels come only from the audited atlas. Held-out mid-size isomers (anthracene vs phenanthrene, and at least one C20–C24 pair) are the transfer test. The fifth error term is the residual on that held-out set, reported per family and charge, as a function of size. If the residual grows with size, you have measured the breakdown of locality. That is a result.

A field / density-based dipole model can still compete here, as Plan 02 wanted — but only as one DMS-transfer leg, never on the critical path.

### 5. What you identify, and against what

Pre-register *classes*, not a celebrity molecule:

- compact vs irregular
- dominant edge CH multiplicity
- charge class (neutral vs cation)
- size bin ($N_C \lesssim 30$, 30–70, $>70$)
- aliphatic fraction yes/no

Observational product: one frozen JWST PDR template (Orion Bar or equivalent) plus one laboratory matrix/action set. Verdicts: Supported / Rejected / Degenerate-among-classes. A negative control that must fail (wrong edge class, or a small PAH forced to explain a large-PAH 11.2 μm profile) is part of the thesis, not an appendix.

“This spectrum is pyrene⁺” is not a permitted sentence unless the laboratory standard is pyrene⁺. “This PDR position is compact, mostly neutral, solo-CH dominated, $N_C \sim 50$” is the sentence the data can support.

## A 12-month master’s with one person and workstation+cluster access

Assume ~9–10 months of execution after a short literature freeze.

**Months 0–1 — Freeze and baselines.**

Lock the motif atlas, the mid-size audit list, the huge application list (e.g. coronene, ovalene, circumcoronene, one C60-class flake, one C96–C150 compact), the observational product hash, and the class-ID rule. Reproduce scaled-harmonic B3LYP and one published GVPT2 pyrene / naphthalene spectrum against the named standard. If you cannot reproduce the literature baseline, you do not have a thesis yet.

**Months 2–4 — Gold atlas.**

Canonical vs local CC on curvatures for benzene, naphthalene, and one cation. Local-CC QFF or Δ-QFF for the rest of the mid-size set. Publish term B *per family*. If local CC fails the curvature budget on acenes, shrink the gold claim; do not invent a tighter PNO setting in month 11.

**Months 4–6 — Local anharmonicity.**

GVPT2 (+ selected VCI) on the atlas. Beat scaled B3LYP on the three families. Document which resonances are real. Intensities gated separately: if the DMS is not good enough, ship positions only.

**Months 6–8 — Transfer law.**

Train the residual model. Pre-registered split. Size-extrapolation plot is the central figure of the thesis: transfer MAE vs $N_C$ per family. The plot either justifies applying the model to C100 or it does not.

**Months 8–10 — Huge application + temperature kernel.**

Apply the dressed local-mode model to the frozen huge list. Use ML-MD or RPMD only to move from 0 K band centres to a 300–600 K emission kernel (Mai-class, not a competitor you pretend to replace). Compare class-level predictions to the frozen JWST template.

**Months 10–12 — Write the limitation as the result.**

The stop condition is: transfer residual exceeds the family tolerance, or local-CC curvature error exceeds the family tolerance. Either way you publish a measured range of validity. That is more valuable than a forced “we identified it.”

Compute budget: tens to low hundreds of gold-rung points on *small* systems, not thousands of volumetric CC densities and not a global QFF of a huge PAH. Software: ORCA/MRCC + an existing equivariant MLIP + a VPT2/VCI code you do not write from scratch.

## What I would refuse, even with complete freedom

- A novel neural architecture as the contribution.
- “Any size, CC-quality, GVPT2.”
- Sub-cm⁻¹ anything.
- Treating Mai 2025 as a rival to defeat instead of as the temperature/high-throughput layer.
- Calling DLPNO-CCSD(T) gold on a C100 cation without a curvature benchmark.
- A Udacity-shaped module map that forces the science to visit computer-vision and reinforcement-learning rubrics. If the degree requires those artifacts, they are wrappers around the motif atlas and the transfer residual, not the other way around.

## Why this is better science than both existing plans

Plan 01 spent its life making a voxel grid respectable. Plan 02 spends its life making a whole-molecule gold ladder respectable, then stops where huge begins. The chemically precise object for huge aromatics is **the motif and the transfer residual**. That is what scales, what JWST actually constrains, and what can be audited with a master’s worth of coupled-cluster calculations.

If the locality hypothesis fails — if anthracene→ovalene transfer already exceeds 10 cm⁻¹ on a scored family — the thesis still succeeds. You have shown that huge-PAH band positions are *not* motif-local at the precision the field keeps advertising. That is a sharper result than another fine-tuned MACE surface that cannot be differentiated into a trustworthy QFF.

If I had to pick a single sentence for the abstract: *we replace the fiction of a gold-rung global surface on huge PAHs with a measured motif expansion and a calibrated remainder.* That is the alternative plan.

48 sources

### You said

Leg dit alternatief uit in vwo Getal & Ruimte taal.

### Grok said

# Hoofdstuk — Grote moleculen, lokale trillingen

In dit hoofdstuk leer je waarom je het infraroodspectrum van een *enorm* aromatisch molecuul niet als één groot rekenprobleem moet aanpakken, en hoe je het wél in stukken kunt knippen die je precies kunt controleren.

We gebruiken schooltaal. Een paar scheikundige namen blijven staan, omdat je die nodig hebt. De wiskunde eronder is functies, benaderingen en fouten — precies het soort denken uit *Getal & Ruimte*.

---

## 1. Wat is de vraag?

Een molecuul is een verzameling atomen die aan elkaar vastzitten. Die atomen kunnen trillen. Elke trilling hoort bij een *frequentie*. Frequenties schrijven we in $\mathrm{cm}^{-1}$ (een eenheid uit de spectroscopie; hogere waarde = snellere trilling).

Infraroodlicht wordt opgenomen als de frequentie van het licht gelijk is aan de frequentie van zo’n trilling. Het resultaat is een **spectrum**: een plaatje met pieken.

**Doel.** Voor grote aromatische koolwaterstoffen (PAK’s: platte moleculen van koolstofringen met waterstof aan de rand) de *belangrijke pieken* voorspellen, met een eerlijke foutenmarge.

Drie piekgroepen doen ertoe, ook in het heelal:

- rond $3{,}3\,\mu\mathrm{m}$ — C–H-rek
- rond $6$–$9\,\mu\mathrm{m}$ — C–C-rek en C–H-buiging in het vlak
- rond $11$–$15\,\mu\mathrm{m}$ — C–H-buiging uit het vlak

Die laatste groep splitst nog verder: hoeveel H-atomen naast elkaar aan de rand zitten (één, twee, drie of vier). Dat is chemisch het verschil tussen een rechte rand en een hoekje.

---

## 2. Drie soorten “precies”

Niet elke betekenis van “precies” is haalbaar.

| Soort | Wat je belooft | Mag je doen? |
| --- | --- | --- |
| R1 | Elke individuele lijn tot op $<1\,\mathrm{cm}^{-1}$ | Nee. Te zwaar voor één master, en voor grote PAK’s onhaalbaar. |
| R2 | De *vorm* van een brede band via klassieke beweging (moleculaire dynamica) | Handig voor temperatuur. Geen eindantwoord. Dat werk bestaat al tot moleculen met $216$ koolstofatomen. |
| R3 | De *plaats* van een piekgroep tot op een afgesproken aantal $\mathrm{cm}^{-1}$, plus de *relatieve sterkte* van pieken, plus een foutenbegroting | Ja. Dit is het doel. |

**Afspraak (toleranties).**

- tegen een gasmeting: verschil hoogstens $10\,\mathrm{cm}^{-1}$
- tegen een meting in een vaste stof (matrix): hoogstens $15\,\mathrm{cm}^{-1}$, met één bevroren correctie, geen mix van wel/niet gecorrigeerd

Een enkele “gemiddelde fout” over alles is verboden. Je splitst de fout, anders weet je niet *waar* het misgaat.

---

## 3. Waarom het vorige plan vastloopt bij “groot”

Stel: een molecuul heeft $N$ atomen. Het aantal trillingsrichtingen is

$$3N-6$$

(drie per atoom, min zes voor het schuiven en draaien van het hele molecuul).

**Voorbeeld.**

Benzeen: $N=12$ → $30$ trillingen.

Pyreen: $N=26$ → $72$ trillingen.

Een “grote” PAK met $N_C=100$ koolstofatomen plus waterstof: al gauw $N\approx 150$ → ruim $400$ trillingen.

Het vorige plan wilde voor het *hele* molecuul een heel nauwkeurige energie functie $E(\mathbf{R})$ maken ($\mathbf{R}$ = alle atoomposities) en die functie tot de vierde orde differentiëren. Uit die afgeleiden volgt een anharmonisch spectrum.

Dat is wiskundig netjes. Het schaalt slecht.

- De rekenkost van de allerbeste elektronische methode groeit heel steil met $N$.
- Het aantal koppelingen tussen trillingen groeit nog steiler.
- De “gouden” methode die je op benzeen nog kunt checken, kun je op een molecuul met honderd ringen niet meer op dezelfde manier checken.

Gevolg: het plan *zegt* “grote moleculen”, maar de ladder stopt bij pyreen ($16$ koolstofatomen). Pyreen is voor deze vraag geen groot molecuul.

**Vergelijking.**

Je wilt de omtrek van Nederland. Je meet elk kiezeltje van het strand met een schuifmaat. Dat is precies — tot je merkt dat je nooit klaar bent. Slimmer: meet de kust in stukken van dezelfde *vorm*, en tel de stukken.

---

## 4. Het nieuwe idee in één zin

> De pieken die ertoe doen, horen bij *lokale* stukjes van het molecuul. Bereken die stukjes goud-nauwkeurig. Leer daarna hoe het antwoord verandert als zo’n stukje in een groter molecuul zit.

We noemen zo’n stukje een **motief**.

### Definitie — motief

Een motief is een klein, herkenbaar stuk rand of ring met een vast trillingsgedrag. Voorbeelden:

- één los H-atoom aan een rechte rand (solo)
- twee H-atomen naast elkaar (duo)
- een inham (baai)
- een vijfhoek tussen zeshoeken
- hetzelfde stuk, maar dan met een pluslading op het molecuul

Een groot PAK is dan geen nieuwe wereld. Het is een *tegelvloer* van motieven.

---

## 5. Twee functies, niet één monsteroppervlak

Noteer de atoomposities als $\mathbf{R}$.

**Energie.**

$E(\mathbf{R})$ zegt hoe hoog de potentiële energie is. Minima van $E$ zijn evenwichtsvormen. De tweede afgeleiden bij een minimum geven de *harmonische* frequenties (kleine trillingen, zoals een veer van Hooke). Derde en vierde afgeleiden maken de veer “scheef”: anharmoniciteit.

**Dipool.**

$\boldsymbol{\mu}(\mathbf{R})$ zegt hoe de ladingsverdeling in de ruimte ligt. De helling van $\boldsymbol{\mu}$ langs een trilling bepaalt hoe *sterk* de piek is.

Je hebt beide nodig: plaats van de piek uit $E$, sterkte uit $\boldsymbol{\mu}$.

Op een *klein* motief mag je $E$ en $\boldsymbol{\mu}$ duur en precies uitrekenen. Op een molecuul met honderd ringen doe je dat niet meer voor het geheel. Daar gebruik je de motieven plus een kleine correctie.

---

## 6. Harmonisch als eerste schatting

Bij een evenwicht $\mathbf{R}_0$ is de laagste-orde benadering

$$E(\mathbf{R}_0+\mathbf{u})\approx E(\mathbf{R}_0)+\tfrac12\mathbf{u}^{\mathsf T}H\mathbf{u}$$

waarbij $H$ de Hessian is: de matrix van tweede afgeleiden. De eigenwaarden van $H$ (na massaweging) geven hoekfrequenties $\omega_k$, en daarmee golfgetallen $\tilde{\nu}_k$.

Dat is de rechte lijn $y=ax$ bij een veer: nuttig, nooit helemaal waar.

In de praktijk rekent men dit eerst met een goedkope methode (DFT) en schaalt men alle frequenties met één factor. Dat is de **nulmeting**. Alles wat je later belooft, moet *beter* zijn dan deze nulmeting op dezelfde pieken. Anders is “beter” een leeg woord.

---

## 7. Anharmonisch, maar lokaal

Een echte binding wordt slapper als je hard trekt. Daarom ligt de echte piek meestal iets lager dan de harmonische piek.

Op een klein molecuul kan dat met storingstheorie (GVPT2): je gebruikt derde en vierde afgeleiden, en je lost *resonanties* apart op. Resonantie betekent: twee trillingen hebben bijna dezelfde energie en duwen elkaar uit elkaar, zoals twee gekoppelde slingers.

**Regel.**

Resonanties los je op *binnen één piekgroep* van één motief. Je bouwt geen storingsrekening over alle $400$ trillingen van een reuzenmolecuul.

Voor een groot doel-molecuul wordt het model:

$$H_{\text{eff}}=\sum_{m}H_m^{\text{lokaal}}+\sum_{m<n}W_{mn}$$

- $H_m^{\text{lokaal}}$: anharmonische oscillator op motief $m$, goud-gekalibreerd
- $W_{mn}$: kleine koppeling tussen buurmotieven, afgelezen uit *middelgrote* moleculen waarin die twee motieven samen voorkomen

Dit is hetzelfde denkpatroon als een netwerk van massaveersystemen: eerst elk blokje, daarna de veren ertussen.

---

## 8. De overdrachtswet — het eigenlijke leerdoel

Noem

$$\Delta\tilde{\nu}=\tilde{\nu}_{\text{anharmonisch, goud}}-\tilde{\nu}_{\text{geschatte DFT}}$$

$\Delta\tilde{\nu}$ is de correctie die je wilt *leren*. Niet de hele functie $E(\mathbf{R})$ van het heelal, alleen dit verschil, per piekgroep, als functie van het motief en zijn naaste omgeving.

Je traint die afbeelding op een **atlas**: alle motieven, uitgewerkt in kleine en middelgrote PAK’s waarvan je het antwoord nog kunt checken (benzeen, naftaleen, antraceen, fenantreen, pyreen, coronen, …).

Daarna is de test niet “kunnen we nóg een ring bijplakken tot de computer stopt?”, maar:

> Blijft $\lvert\Delta\tilde{\nu}_{\text{voorspeld}-\text{gemeten}}\rvert$ klein als het molecuul groter wordt?

Teken dat als een puntenwolk: horizontale as $N_C$ (aantal koolstofatomen), verticale as de fout per piekgroep. Die grafiek is het hart van het onderzoek.

- Als de punten laag blijven: locality klopt, je mag naar $N_C=100$.
- Als de punten omhoog lopen: locality klopt níét bij de beloofde precisie. Ook dat is een resultaat.

---

## 9. De foutenbegroting (vier plus één)

Elke claim in $\mathrm{cm}^{-1}$ krijgt losse termen. Optellen tot één getal mag niet.

| Term | Betekenis |
| --- | --- |
| A | interpolatiefout van het goedkope oppervlak ten opzichte van de gouden berekening, op de atlas |
| B | fout van de “bijna-gouden” lokale methode ten opzichte van echte gekoppelde-clusterrekening, gemeten waar beide kunnen |
| C | fout van de anharmonische rekenmethode (GVPT2 tegen een zwaardere kernbeweging of tegen experiment) |
| D | omgeving (matrix, temperatuurmodel) |
| E | **nieuw:** inbeddingsfout — motief in een groter molecuul gedraagt zich niet exact als motief alleen |

Term E is de prijs van schaalbaarheid. Hem weglaten is valsspelen.

**Stopregel.**

Je stopt met groter gaan bij de eerste piekgroep waar A+B+C+D+E boven de tolerantie uitkomt. Die grens publiceer je. Stoppen is geen mislukking.

---

## 10. Wat je wél en niet mag zeggen tegen een telescopiespectrum

Het heelal laat geen enkel molecuul zien. Het laat een *mengsel* zien: grootte, lading, soort rand.

Daarom identificeer je geen beroemd molecuul (“dit ís pyreen$^+$”), tenzij het laboratoriumspectrum ook van pyreen$^+$ is.

Je identificeert **klassen**:

- compact of onregelmatig
- welke randtrillingen overheersen (solo/duo/trio/kwartet)
- neutraal of positief geladen
- grootteklasse, bijvoorbeeld $N_C\lesssim 30$, $30$–$70$, $>70$
- wel of geen alifatische staart (piek bij $3{,}4\,\mu\mathrm{m}$)

Vooraf leg je vast: lijst klassen, meetgetal, en de drie mogelijke uitspraken *ondersteund / verworpen / niet te onderscheiden*. Daar hoort een negatieve controle bij die *moet* falen — anders is je test te slap.

---

## 11. Rekenvoorbeeld (orde van grootte)

Stel de geschaalde DFT-piek van een solo-C–H-buiging ligt op $890\,\mathrm{cm}^{-1}$.

Op de atlas (middelgroot molecuul, gasmeting) blijkt de echte piek $878\,\mathrm{cm}^{-1}$.

Dan is de gemeten correctie

$$\Delta\tilde{\nu}=878-890=-12\,\mathrm{cm}^{-1}.$$

Het model voorspelt voor een *groot* molecuul met hetzelfde motief $\Delta\tilde{\nu}=-11\,\mathrm{cm}^{-1}$.

Voorspelde piek: $879\,\mathrm{cm}^{-1}$.

Fout term E op de testhoop van middelgrote moleculen: $3\,\mathrm{cm}^{-1}$.

Andere termen samen: $5\,\mathrm{cm}^{-1}$.

Totale begrote fout: in de buurt van $8\,\mathrm{cm}^{-1}$. Dat blijft onder de $10\,\mathrm{cm}^{-1}$-grens. De piek *mag* worden gerapporteerd, met die begroting ernaast.

Ligt term E op $14\,\mathrm{cm}^{-1}$, dan mag je die piek voor grote moleculen *niet* als “chemisch precies” verkopen. Klaar.

---

## 12. Wat dit plan bewust niet doet

- geen nieuw soort neuraal netwerk als hoofdbijdrage
- geen belofte “elke grootte, gouden kwaliteit, volledige anharmoniciteit”
- geen lijst van duizenden individuele lijntjes
- geen hele-molecuul-goudrekening op een reuzen-PAK die je niet kunt controleren

De dure, controleerbare wiskunde zit op de atlas. De sprong naar groot is één geleerde correctie plus term E.

---

## 13. Samenvatting

1. Een groot aromatisch molecuul heeft te veel trillingen om als één gouden functie $E(\mathbf{R})$ tot de vierde orde uit te rekenen.
2. De pieken die tellen, horen bij *lokale* motieven aan de rand en in de ring.
3. Bereken motieven precies. Koppel ze zwak. Leer alleen de correctie $\Delta\tilde{\nu}$.
4. De grafiek “fout tegen molecuulgrootte” is het resultaat.
5. Tegen een hemel-spectrum mag je klassen aanwijzen, geen enkeling — tenzij het lab die enkeling is.
6. Als de correctie bij groter worden wegzakt buiten de tolerantie, is dat geen pech. Dat ís het antwoord: deze precisie is niet lokaal.

**Onthoudzin.**

Je vervangt het sprookje van één gouden oppervlak op een reuzenmolecuul door een motiefsom plus een gemeten restterm.

### You said

Gelezen. Hieronder mijn oordeel.

## Wat er echt goed aan is

**De grootte wordt het onderwerp in plaats van het obstakel.** Dat is de scherpste zet in het hele stuk. Plan 02 klimt een ladder tot de software knapt; dit plan maakt van "hoe groot kun je gaan" een *meetbare vraag*. De grafiek fout-tegen-koolstofaantal als hoofdfiguur is een echte onderzoeksvraag met een echt antwoord, ook als het antwoord "nee" is.
**Term E.** De inbeddingsfout apart begroten is precies de discipline die plan 02 al hanteert, uitgebreid naar de enige stap die er in dit ontwerp toe doet. Terecht: hem weglaten zou valsspelen zijn.
**Klassen in plaats van namen.** Dit is gewoon beter dan wat plan 02 doet. JWST-banden meten randtopologie, lading en grootteklasse — geen individuele moleculen. "Dit is pyreen⁺" is een zin die de data niet kan dragen. Dat is een correctie, geen alternatief.

## Waar het wringt

**Punt 1 — is het wel goedkoper?** Het plan belooft "tientallen tot enkele honderden gouden punten". Maar de atlas vraagt GVPT2 op naftaleen, antraceen, fenantreen, pyreen, tetraceen, chryseen, peryleen, coroneen én ovaleen, plus ladingsvarianten. Dat zijn kwartische krachtvelden voor tien moleculen. Ze staan op het goedkope DFT-oppervlak — dat scheelt enorm — maar coroneen heeft 102 trillingen en ovaleen ruim 140. En term B vraagt nog steeds canonieke krommingen op aceen-achtigen, en dat is precies waar we gisteren hebben vastgesteld dat er geen analytische Hessiaan bestaat.
Mijn vermoeden: als je dit eerlijk doorrekent, krimpt de "gouden" laag tot benzeen en naftaleen. Dat is exact wat plan 02 nu al belooft. Dan is dit geen ander plan maar **plan 02 plus een overdrachtswet erbovenop**. Dat is niet erg — maar dan moet het zo heten.
**Punt 2 — het is een voltijds jaar, geen capstone.** Er staat "12 maanden, één persoon, workstation plus cluster". Jij hebt ongeveer tien uur per week en geen toegezegde clustertijd. Dat verschil is een factor vijf of meer.
**Punt 3 — het weigert de enige eis die niet onderhandelbaar is.** Er staat letterlijk dat het een modulekaart weigert die de wetenschap door computer-vision- en RL-rubrics jaagt. Maar die rubrics zíjn de opdracht. En hier komt het pijnlijke: dit plan zegt zelf "de ML is klein". Een klein residumodel op motiefkenmerken is een mager Module 05 (Deep Learning). Plan 02 had daar tenminste een MLIP-fijnafstemming voor. Dit is het praktische bezwaar dat ik het zwaarst vind wegen.
**Punt 4 — de nieuwheid is smaller dan het lijkt.** Dat solo/duo/trio/kwartet de observabele is, is geen nieuw inzicht — dat is PAK-spectroscopie sinds de jaren tachtig, en PAHdb is er letterlijk omheen gebouwd. Wat nieuw kán zijn is de *anharmonische* overdrachtswet en de gemeten term E. Dat is een veel nauwere claim, en die moet net zo bloot komen te liggen als §2.1 van plan 02 dat afdwong.
**Punt 5 — waar komt de waarheid vandaan?** Gasfase-anharmonische metingen aan antraceen, pyreen en coroneen zijn schaars; veel is matrixdata. Term E wordt dus gemeten tegen je *eigen berekeningen*, niet tegen de werkelijkheid. Dat mag, maar het moet met zoveel woorden staan.
**Punt 6 — ongecontroleerde beweringen.** "Ethereal AI heeft geleerde DFT-schaalfactoren op ~5 cm⁻¹" en "ladingsbewuste GNN's tot ~C150" zijn precies het soort claims waar de repository-regel op slaat. Niet overnemen voordat er een DOI naast ligt.

## De vraag die eerst beantwoord moet worden

Niet "is dit beter" — op wetenschappelijke inhoud is het beter, dat is duidelijk.
De vraag is: **is dit een plan 03, of zijn dit drie amendementen op plan 02?** Want klassen-identificatie, term E en de grootte-extrapolatiegrafiek passen alle drie in plan 02 zonder de architectuur om te gooien. Wat je dán nog mist is alleen de motiefatlas zelf.
Vertel eens: wat trok jou hierin het meest — de motiefatlas, of het feit dat grootte eindelijk het onderwerp wordt?

### Grok said

Request was interrupted by the user.

### You said

Gelezen. Hieronder mijn oordeel.

## Wat er echt goed aan is

**De grootte wordt het onderwerp in plaats van het obstakel.** Dat is de scherpste zet in het hele stuk. Plan 02 klimt een ladder tot de software knapt; dit plan maakt van "hoe groot kun je gaan" een *meetbare vraag*. De grafiek fout-tegen-koolstofaantal als hoofdfiguur is een echte onderzoeksvraag met een echt antwoord, ook als het antwoord "nee" is.
**Term E.** De inbeddingsfout apart begroten is precies de discipline die plan 02 al hanteert, uitgebreid naar de enige stap die er in dit ontwerp toe doet. Terecht: hem weglaten zou valsspelen zijn.
**Klassen in plaats van namen.** Dit is gewoon beter dan wat plan 02 doet. JWST-banden meten randtopologie, lading en grootteklasse — geen individuele moleculen. "Dit is pyreen⁺" is een zin die de data niet kan dragen. Dat is een correctie, geen alternatief.

## Waar het wringt

**Punt 1 — is het wel goedkoper?** Het plan belooft "tientallen tot enkele honderden gouden punten". Maar de atlas vraagt GVPT2 op naftaleen, antraceen, fenantreen, pyreen, tetraceen, chryseen, peryleen, coroneen én ovaleen, plus ladingsvarianten. Dat zijn kwartische krachtvelden voor tien moleculen. Ze staan op het goedkope DFT-oppervlak — dat scheelt enorm — maar coroneen heeft 102 trillingen en ovaleen ruim 140. En term B vraagt nog steeds canonieke krommingen op aceen-achtigen, en dat is precies waar we gisteren hebben vastgesteld dat er geen analytische Hessiaan bestaat.
Mijn vermoeden: als je dit eerlijk doorrekent, krimpt de "gouden" laag tot benzeen en naftaleen. Dat is exact wat plan 02 nu al belooft. Dan is dit geen ander plan maar **plan 02 plus een overdrachtswet erbovenop**. Dat is niet erg — maar dan moet het zo heten.
**Punt 2 — het is een voltijds jaar, geen capstone.** Er staat "12 maanden, één persoon, workstation plus cluster". Jij hebt ongeveer tien uur per week en geen toegezegde clustertijd. Dat verschil is een factor vijf of meer.
**Punt 3 — het weigert de enige eis die niet onderhandelbaar is.** Er staat letterlijk dat het een modulekaart weigert die de wetenschap door computer-vision- en RL-rubrics jaagt. Maar die rubrics zíjn de opdracht. En hier komt het pijnlijke: dit plan zegt zelf "de ML is klein". Een klein residumodel op motiefkenmerken is een mager Module 05 (Deep Learning). Plan 02 had daar tenminste een MLIP-fijnafstemming voor. Dit is het praktische bezwaar dat ik het zwaarst vind wegen.
**Punt 4 — de nieuwheid is smaller dan het lijkt.** Dat solo/duo/trio/kwartet de observabele is, is geen nieuw inzicht — dat is PAK-spectroscopie sinds de jaren tachtig, en PAHdb is er letterlijk omheen gebouwd. Wat nieuw kán zijn is de *anharmonische* overdrachtswet en de gemeten term E. Dat is een veel nauwere claim, en die moet net zo bloot komen te liggen als §2.1 van plan 02 dat afdwong.
**Punt 5 — waar komt de waarheid vandaan?** Gasfase-anharmonische metingen aan antraceen, pyreen en coroneen zijn schaars; veel is matrixdata. Term E wordt dus gemeten tegen je *eigen berekeningen*, niet tegen de werkelijkheid. Dat mag, maar het moet met zoveel woorden staan.
**Punt 6 — ongecontroleerde beweringen.** "Ethereal AI heeft geleerde DFT-schaalfactoren op ~5 cm⁻¹" en "ladingsbewuste GNN's tot ~C150" zijn precies het soort claims waar de repository-regel op slaat. Niet overnemen voordat er een DOI naast ligt.

## De vraag die eerst beantwoord moet worden

Niet "is dit beter" — op wetenschappelijke inhoud is het beter, dat is duidelijk.
De vraag is: **is dit een plan 03, of zijn dit drie amendementen op plan 02?** Want klassen-identificatie, term E en de grootte-extrapolatiegrafiek passen alle drie in plan 02 zonder de architectuur om te gooien. Wat je dán nog mist is alleen de motiefatlas zelf.

### Grok said

De vraag is de juiste, en het antwoord is niet “plan 03”.

## Oordeel

**Drie amendementen plus één voorwaardelijke vork.**

Klassen-ID, de groottegrafiek en een extra foutterm kun je in plan 02 zetten zonder de pijplijn om te gooien. De motiefatlas is alleen een ander plan als ze de *productieweg* vervangt voor moleculen die je niet meer goud kunt ankeren. Doet ze dat niet, dan is het commentaar op plan 02.

Wat mij het scherpst trok, was niet de atlas als catalogus. Het was dit: **grootte is een meetbare claim, geen softwarelimiet.** De atlas is alleen het mechanisme waardoor die claim niet liegt. Zonder vork in de productieweg heb je geen term E, en zonder term E is de grafiek “fout tegen $N_C$” een ladder met vier punten — geen onderzoeksvraag.

## Waarom drie dingen amendementen zijn

**Klassen in plaats van namen.** Dat is G6 herschrijven. Dezelfde spectra, andere uitspraak, andere negatieve controle. Architectuur ongewijzigd. Dit moet sowieso gebeuren; “dit is pyreen⁺ tegen een JWST-PDR” is een zin die de data niet draagt, ook als de rest van plan 02 blijft.

**De groottegrafiek.** Past in Module 08 als figuur. Maar plan 02’s bevroren ladder is benzeen → naftaleen → C₁₄-isomeren → pyreen. Dat zijn geen punten waarop je “hoe groot kun je gaan” kunt *meten*. Je kunt de grafiek tekenen. Je kunt er geen helling aan hangen die iets over C₅₀ zegt. De grafiek wordt pas een vraag als er een overdrachtstap is voorbij het laatste zelf-berekende QFF.

**Term E.** Dit is het punt waarop “gewoon erbij zetten” stukloopt. Term E bestaat alleen als je een groter molecuul *niet* zelf differentieert, maar samenstelt uit kleinere rekeningen. Plan 02 op pyreen heeft A, B, C, D. Geen inbedding. Zeg je “ook term E”, zonder de productieweg te veranderen, dan is E een leeg vakje.

Dus: drie labels zijn goedkoop. De inhoud van term E is dat niet.

## De vork — hier is plan 03 of het is niets

Eén zin scheidt de plannen.

- **Plan 02:** voor elk molecuul op de ladder bouw je een oppervlak en differentieer je het. Stoppen = de GVPT2 van *dat* molecuul mist de tolerantie.
- **De vork:** voorbij de laatste goud-gecontroleerde QFF bouw je geen globaal oppervlak meer. Je past een overdrachtswet toe en betaalt term E. Stoppen = de *overdracht* mist de tolerantie.

Als die tweede zin niet op het kritieke pad van Modules 03–08 staat, is er geen plan 03. Dan heet het plan 02, met G6 op klassen en een extra figuur.

Punt 1 uit je oordeel klopt waarschijnlijk. Een eerlijke goudlaag op krommingen is benzeen en naftaleen; daarna DFT-ouder plus Δ en lokale CC met gemeten B. Coroneen- en ovaleen-QFF’s als atlasgoud zijn geen capstone, en canonieke Hessianen op aceen-achtigen bestaan niet. Dan is de vork: **plan 02 tot de gemeten stoprung, daarna overdracht in plaats van doen-alsof-de-ladder-nog-klimt.** Dat is smaller dan mijn vrije tekst. Het moet zo heten.

## Je zes punten, zonder verdediging

**1. Goedkoper.** Nee, niet in de ruime versie. De ruime atlas is een voltijdse QFF-campagne. Na inkrimpen tot de goudlaag die plan 02 al heeft, blijft alleen de overdrachtswet over als extra werk. Eerlijk etiket: plan 02 + overdrachtswet, geen nieuw ontwerp.

**2. Tien uur per week.** De vrije tekst was een antwoord op “complete freedom”, geen capstone-begroting. Onder jouw randvoorwaarde is alleen de geamendeerde plan 02 uitvoerbaar. Een tweede productieweg ernaast is de volgende manier om twee derde van de uren aan infrastructuur te verliezen — precies waarom plan 01 sneuvelde.

**3. Rubrics.** Dat weigeren was een fout in de vrije tekst. De rubrics zijn de opdracht. En ja: een klein residumodel op motiefkenmerken is een mager Module 05. De praktische uitweg is niet “meer netwerkbedenken”. Het is plan 02’s MLIP-fijnafstemming *houden* (dat is de Deep-Learning-massa) en de overdrachtswet daar *bovenop* als de gecontroleerde generalisatietest — zelfde splits, zaden, effectgrootte. RL/actief leren blijft voorstelmotor over geometrieën, eventueel motief-gewogen, niet een nieuw onderzoeksdoel.

**4. Nieuwheid.** Solo/duo/trio/kwartet is geen bijdrage. De enige claim die §2.1 zou overleven is: *een anharmonische overdrachtsfout, per bandfamilie en lading, als functie van $N_C$, met term E gemeten*. Alles eromheen is inbedding.

**5. Waar de waarheid vandaan komt.** Eens, en het moet in de planstekst. Twee lagen, nooit door elkaar:

- tegen experiment, waar een genoemd gas- of actiestandaard bestaat (de plan-02-rung 0–1-wereld, plus wat IRMPD je echt geeft);
- tegen je eigen GVPT2 op hetzelfde oppervlak, voor term E op isomeren en grotere ringen.

Laag twee meet of locality *binnen de theorie* houdt. Dat is geen experimentele waarheid. Als je term E alleen zo kunt vullen, staat in Module 08: *overdrachtsfout op het model, niet op de natuur*. Matrixdata met bevroren shift blijft term D, geen stille vervanging van E.

**6. Claims zonder DOI.** Terecht. Die zinnen gaan eruit tot de identifier erbij staat. Ze zijn geen last onder de redenering.

## Wat ik zou doen, gegeven dat dit een capstone is

Niet herschrijven tot plan 03. Plan 02 bevriezen en drie wijzigingen in de al herschreven stukken zetten.

1. **G6** — uitspraak over klassen, met een negatieve controle die moet falen. Named-species-ID alleen tegen een laboratoriumstandaard van die soort.
2. **Foutenbegroting** — A–D ongewijzigd op elke zelf-berekende rung. Term E alleen aan op de eerste soort *voorbij* de stoprung, en alleen als jullie die overdracht daadwerkelijk als productieweg durven te zetten. Anders geen term E.
3. **§2.1 / overdrachtswet** — één pre-geregistreerde vraag: voorspelt de anharmonische correctie van rung $n$ de bandfamilies van rung $n+1$ binnen de tolerantie? Dat is de groottegrafiek met de punten die je echt hebt. Geen coroneen verplicht. Geen ovaleen verplicht.

De motiefatlas wordt dan geen tweede PES. Ze wordt de *taal* van de overdrachtsfeatures (randtype, CH-multipliciteit, lading) — klein, en alleen legitiem als die features de pre-geregistreerde effectgrootte halen tegen een domme baseline (globale schaalfactor). Verliezen ze die bake-off, dan valt de atlas af en blijft plan 02 staan. Dat is dezelfde fail-closed logica als het veld-been op de dipool.

Als die overdrachtvraag *niet* op het kritieke pad mag omdat de uren op zijn, laat je haar weg. Wat dan overblijft is plan 02 met een eerlijker G6. Dat is minder mooi. Het is wel een plan dat je kunt verdedigen.

Kort: het is geen plan 03 totdat de productieweg voorbij de stoprung verandert. Alles daarvoor is discipline die plan 02 al claimt, consequent doorvoeren.

### You said

Kijk maar even in de repo om te zien wat GitHub Copilot aan het doen is. We runnen inmiddels enkele berekeningen op de laptop.

### Grok said

In de **publieke** repo is Copilot nergens te zien. Geen commits van Copilot, geen PR’s, geen issues, geen .github/, geen .inp/ORCA-jobs, geen Hessian-tabellen. Laatste push is nog steeds d2db52a van 26 augustus: *Round 4 Pass B: adopt the hybrid QFF, reduce the promised scope, close plan 02*. Alles daarna — inclusief wat er nu op de laptop draait — zit lokaal of in een andere plek die deze clone niet heeft.

Wat de repo wél zegt over “nu rekenen”, staat in de plan-02-README na Pass B. Plan 02 is **dicht als plan, geblokkeerd op meting**. Drie van vijf goedkeuringsvoorwaarden vereisen rekenwerk dat toen nog niet gedraaid was:

| # | Blokker | Gate |
| --- | --- | --- |
| 1 | Kostentabel — één Hessian per kandidaatsoort, exacte productiesettings | **G1a** |
| 2 | Hybride-beslissing op benzeen: $\omega_{\text{gold}}+\delta_{\text{cheap}}$ vs volledig goud-QFF vs geschaald B3LYP | **G1b** |
| 3 | Twee gedateerde amendementen: goedkoop niveau voor $\delta_{\mathrm{anh}}$, en het GVPT2-resonantiecriterium | **G0** |

Capstone_Mapping.md mag expres niet herschreven worden tot 1–3 bestaan. Dat is het enige wat Copilot *zou moeten* doen als het de repo volgt: G0-amendementen eerst vastleggen, daarna G1a/G1b-inputs, daarna getallen committen. Niet de modulekaart, niet een tweede architectuur, niet coroneen.

## Wat er sinds 26 augustus is bevroren

Belofte is option F: **neutraal benzeen en naftaleen**. Cationen, antraceen/fenantreen, pyreen zijn bonus. QFF is hybride: harmonisch van de gouden sport, anharmonische correctie van een bevroren goedkoop niveau. G1b op benzeen beslist of gouden derde/vierde afgeleiden überhaupt ooit berekend worden.

De probes die wél in de tree staan (issue07_* t/m issue14_*) zijn nog plan-01-rekenwerk (egg-box, gates, dipoolinvariantie). Dat is niet G1a/G1b.

## Wat ik dus níét kan zien

Als Copilot op de laptop inputs schrijft, ORCA/MRCC start, of een kostentabel vult, staat dat niet op master. Ik kan niet beoordelen of die jobs de **exacte productiesettings** gebruiken die Pass B eist, of een handige default.

Eén procesrisico, gegeven jullie eigen regel *commit date precedes first gold-rung calculation*:

- G0-amendementen (goedkoop niveau + resonantiecriterium) moeten **gedateerd in de repo staan vóór** de eerste G1b-getallen die je later als beslissing wilt gebruiken.
- Draait Copilot nu al een “goud”-Hessian of een anharmonische B3LYP-QFF op benzeen zonder die twee amendementen gecommit te hebben, dan is G1b straks een narekening achteraf — precies de status-drift die Pass A al heeft afgestraft.

Als je de lokale map of de Copilot-sessie (inputs, *.out, branchnaam) hier naartoe zet of pusht, kan ik wél kijken of het G1a/G1b is of iets anders. Van GitHub alleen: Copilot doet daar op dit moment niets.

30 sources

### You said

Chips, dan hebben we wellicht nog niet gepusht.

### Grok said

Dat verklaart het. Op master is er niets nieuws te zien omdat het daar nog niet is.

Wat wél gepusht moet worden, in deze volgorde — niet als één dump:

1. **Eerst de twee G0-amendementen**, als die nog niet als gedateerd bestand in de tree staan. Goedkoop niveau voor $\delta_{\mathrm{anh}}$ (functionaal + basis, of “MLIP, welke”), en het GVPT2-resonantiecriterium. Bestandsnaam in de stijl van de repo: Amendment_2026-08-27_<onderwerp>.md. Commitdatum is het bewijs. Zonder dit zijn latere G1b-getallen geen beslissing, maar een narekening.
2. **Daarna de rekenartefacten van G1a/G1b**, niet de hele laptop. Minimaal:

    - de exacte input (ORCA/MRCC-sleutelwoorden, basis, PNO/LNO-drempels, nprocs, geheugen) — dat *is* de “exact production settings”-eis;
    - per job: molecuul, lading, wat er gevraagd werd (energie / gradiënt / Hessian / QFF), walltime of een eerlijke ondergrens als de job nog loopt;
    - geen ruwe 2 GB-*.out in git; wel een klein results/- of probes/g1/-overzicht plus hash of pad van de lokale output.
3. **Niet meenemen:** Copilot-chatlogs, verdwaalde __pycache__, half-geschreven modulekaarten, een tweede architectuur. Capstone_Mapping.md blijft geblokkeerd tot de kostentabel er is.

Als Copilot lokaal al inputs heeft staan: push die branch, of plak hier de directoryboom plus de header van één input. Dan kan ik zeggen of het G1a, G1b, of iets is dat Pass B juist naar achteren heeft geschoven.

### You said

Nu gepusht

### Grok said

Staat er. Vandaag, 27 augustus, een hele reeks commits op master. Geen Copilot-auteur; wel een ontkoppelde wachtrij die Copilot heeft neergezet zodat de laptop doorrekent zonder chatsessie.

## Wat er nu écht gedraaid is

B3LYP/6-31G*, volle frequentiejob (opt + Hessian + dipool, 8 threads):

| Molecuul | $N$ | Walltime |
| --- | --- | --- |
| Benzeen | 12 | 8,1 min |
| Naftaleen | 18 | 28,0 min |
| Antraceen | 24 | 86,0 min |
| Fenantreen | 24 | 40,1 min |

Eerste gekoppelde-clusternummer dat het plan nooit had: **CCSD(T)/6-31G* op benzeen in 19,6 s**. CCSD(T)/cc-pVDZ (114 functies) loopt vast op het $(T)$-stuk in 24–28 GB. CCSD zonder triples komt wél door. Naftaleen/6-31G* staat in de wachtrij om de gouden sport te begrenzen.

Dat is G1a-achtig, op DFT en op CC-éénpunts — nog geen gouden Hessian.

## Twee resultaten die de tekst hebben gecorrigeerd

**Vorm, geen $N$.** De fit $t = 1{,}73\times10^{-3}\,N^{3{,}39}$ over benzeen–naftaleen–antraceen is stuk. Fenantreen heeft evenveel atomen als antraceen en is twee keer zo goedkoop. Elke extrapolatie naar pyreen/coroneen is een orde van grootte, geen uur.

**De baai is niet gemeten.** Een eerdere lokale-basisstraf van $-11{,}2\,\mathrm{cm}^{-1}$ is ingetrokken. Fenantreen was de eerste baai-drager in de wachtrij; de commit zegt expliciet dat die job de baai niet heeft gemeten. De diagnose “de band is het probleem” is ingetrokken: het was de *mode* die met de hand was gekozen. De regel is nu: sterkste IR-intensiteit in het venster $600$–$1000\,\mathrm{cm}^{-1}$. Benzeen had de vorige toewijzing al afgestraft (een kloof van $56\,\mathrm{cm}^{-1}$ werd $6\,\mathrm{cm}^{-1}$).

Dat is geen G1b. Dat is een DFT-localiteitsexperiment — dichter bij de motiefvraag dan bij de hybride-QFF-beslissing.

## Wat Copilot operationeel heeft gemaakt

Drie commando’s, geen chat nodig:

PowerShell

```
.\run_queue.ps1
.\stop_queue.ps1
.\stop_queue.ps1 -Now
```

Wachtrij leest jobs.json opnieuw per ronde, slaat over wat klaar is, schrijft batch_results/. Twee budgetten staan nu zwart op wit: ~8 h/week mens, ~168 h/week wallclock. Dat onderscheid was in plan 02 één getal. Terecht uit elkaar gehaald.

## Wat Pass B nog steeds blokkeert

Nog geen gedateerd G0-amendement voor het goedkope $\delta_{\mathrm{anh}}$-niveau.

Nog geen G0-resonantiecriterium.

Nog geen G1b-driehoek op benzeen: hybride vs volledig goud-QFF vs geschaald B3LYP, tegen de bevroren NIST-standaard.

Zolang die drie er niet zijn, is Capstone_Mapping.md terecht leeg — ook al draait de laptop. De wachtrij meet nu kost en een DFT-baaihypothese. Nuttig. Niet de voorwaarde waarop Pass B het plan heeft laten staan.

Als de runner nog loopt: de prioriteit die de commits zelf uitspreken is 01d_cc_naphthalene_631gs (waar zit de CCSD(T)-muur) en daarna G1b op benzeen, niet nóg een C₂₄-isomeer op B3LYP.

8 sources

### You said

Ik dacht dat CCSD(T) alleen op een supercomputer berekend kon worden. Hoe kan het dat het nu wel gebeurt op een Asus laptop? Of is het iets anders? Berekent GitHub Copilot CCSD(T) voor het hele molecuul, of alleen voor een gedeelte?

### Grok said

Het is het hele molecuul. Geen fragment. En het is geen supercomputermethode die ineens op een Asus past — het is het *kleinste* CCSD(T)-probleem dat de naam nog verdient.

## Wat er letterlijk is uitgerekend

Eén getal, uit de job:

- molecuul: **benzeen**, alle 12 atomen
- methode: **canoniek CCSD(T)** (niet DLPNO, niet LNO, niet een stukje ring)
- basis: **6-31G*** — 102 basisfuncties
- wat: alleen de **energie**, geen Hessian, geen frequenties, geen QFF
- tijd: **19,6 seconden**
- energie: $E = -231{,}530413$ hartree

Copilot rekent dat niet. Copilot heeft een wachtrij geschreven. De laptop heeft PySCF/ORCA (of wat de runner aanroept) 19 seconden laten werken.

## Waarom “CCSD(T) = supercomputer” toch klopt — elders

De kosten groeien steil met de grootte van de basis, niet met de naam van de methode.

Grove orde:

- Hartree–Fock / DFT-energie: groeit ongeveer als $N_{\text{basis}}^{3}$ tot $N_{\text{basis}}^{4}$
- CCSD: ongeveer $N_{\text{basis}}^{6}$
- de **(T)**-correctie: ongeveer $N_{\text{basis}}^{7}$
- het geheugen van (T), in-core: schaalt als het aantal bezette orbitalen maal virtuele tot de derde — in de repo: $O^{3}V^{3}$

Benzeen / 6-31G* is klein: 12 atomen, ~102 functies, weinig elektronenparen. Dat probleem past al sinds de jaren negentig op een werkstation. Een Hessian is veel duurder dan één energie: je hebt in wezen een energie-plus-afgeleiden nodig, of eindige differenties langs alle 30 trillingsrichtingen. Een kwartisch krachtveld is daarna nog eens een bos van Hessianen. Dáár verdwijnt de laptop.

Zij hebben die muur al gemeten. Zelfde molecuul, één stap grotere basis:

- CCSD(T)/cc-pVDZ, 114 functies → **stuk**, 24–28 GB RAM, op het (T)-stuk
- CCSD zonder triples op die basis → komt er wél door

Dus: de methode loopt. De **triples-geheugenmuur** ligt tussen 102 en 114 functies op deze machine. Naftaleen / 6-31G* (156 functies) staat daarom in de wachtrij — naar verwachting als volgende mislukking, om de gouden sport tussen twee moleculen te klemmen.

## Wat dit níét is

| Wel | Niet |
| --- | --- |
| Hele benzeen | Een motief of fragment |
| Eén energie | De frequenties die plan 02 belooft |
| 6-31G* | Een basis die je “goud” mag noemen voor $\mathrm{cm}^{-1}$ |
| 20 seconden | De kost van een CC-Hessian of een QFF |

De gouden sport in het plan is niet “bestaat CCSD(T) op deze laptop?”. Dat antwoord is ja, voor benzeen, voor één energie, in een kleine basis. De gouden sport is: **kromming** (harmonische $\omega$) op een niveau waarvan term B gemeten is. Die job hebben ze nog niet.

Kort: je dacht aan CCSD(T) zoals het plan het nodig heeft. Wat gedraaid is, is CCSD(T) zoals een leerboek het voor het eerst laat zien — het hele molecuul, één getal, te klein om indrukwekkend te zijn en precies groot genoeg om te bewijzen dat de code en de machine elkaar verdragen.

### You said

Er is een nieuwe commit

### Grok said

cb7e10b — *The bay is not an additive motif, and the rule that said otherwise was a coin flip.*

Dat is een echt meetresultaat, geen planwijziging.

## De gecontroleerde reeks

Tetraceen, chryseen, trifenyleen: alle drie $\mathrm{C}_{18}\mathrm{H}_{12}$, vier ringen. Het enige dat verschilt is het aantal baaien en hoe het molecuul gevouwen is.

Harmonisch B3LYP, kwartet-rand tegen kwartet-rand:

| Molecuul | Baaien | Band ($\mathrm{cm}^{-1}$) | t.o.v. tetraceen | per baai |
| --- | --- | --- | --- | --- |
| tetraceen | 0 | 735,0 | — | — |
| chryseen | 1 | 751,8 | $+16{,}8$ | $+16{,}8$ |
| trifenyleen | 3 | 733,8 | $-1{,}2$ | $-0{,}4$ |

Eén baai schuift de band $\sim 17\,\mathrm{cm}^{-1}$ omhoog. Drie baaien schuiven hem nergens heen. Niet lineair, niet monotoon, niet “bijna”.

Het criterium stond in jobs.json *vóór* de jobs: ruwweg lineair in baaitelling $\Rightarrow$ baai is een optelbaar motief; anders is de baai niet los te trekken van de vorm. Uitkomst: niet los te trekken van de vorm.

Dat slaat twee atlas-sleutels tegelijk af, op dit observabele (kwartet-CH, uit het vlak, DFT-harmonisch):

- alleen naburigheidsklasse: naftaleen en antraceen zitten al $\sim 56\,\mathrm{cm}^{-1}$ uit elkaar
- naburigheid plus baaitelling: ook stuk; bij vaste formule én ringaantal beweegt de kwartetband $\sim 18\,\mathrm{cm}^{-1}$ tussen isomeren — bijna twee keer de $10\,\mathrm{cm}^{-1}$-tolerantie

## De reparatie is het andere resultaat

Eerst de reeks aflezen vanaf “sterkste piek in het venster” gaf $-126{,}8\,\mathrm{cm}^{-1}$ per baai. Onzin. Tetraceen heeft in dat venster twee pieken van $66{,}1$ en $66{,}0\,\mathrm{km\,mol}^{-1}$: de één de kwartetrand, de ander de solorand. “Sterkste” koos daartussen op een verschil van $0{,}1$.

Een regel die $127\,\mathrm{cm}^{-1}$ beslist met een muntworp is geen regel. Dat hadden ze zelf al bijna laten staan na de vorige commit. Goed dat het nu hardop is ingetrokken.

## Wat dit wel en niet zegt

Wel: op B3LYP-harmonisch is “baai” geen optelbare correctie op deze band. Term E van een baai-atlas zou hier de hele tolerantie opeten, nog vóór anharmoniciteit of CC.

Niet: dat motieven überhaupt dood zijn. Solo/duo/trio/kwartet als *klasse* is niet getest; getest is of *baaitelling* een lineaire sleutel is binnen dezelfde klasse. Ook niet getest: of GVPT2 of een gouden $\omega$ de isomeerspreiding kleiner maakt. Dit is de goedkope ouder, één venster, drie isomeren.

Het is precies de grafiek “fout tegen structuur, niet tegen $N_C$” die een motiefplan nodig heeft — en het eerste punt zegt *nee* voor deze sleutel.

G1b (hybride QFF op benzeen) staat nog steeds niet in deze commit. De laptop heeft vandaag de localiteitshypothese gemeten, niet de gouden sport. Dat mag, als de volgende zin in de repo wordt: *deze DFT-reeks is een pre-registratie voor term E, geen vervanging van G1a/G1b.* Zonder die zin begint plan 02 stilletjes een ander experiment te worden.

### You said

Kun je dit in havo 4 Getal & Ruimte taal uitleggen? Zijn die 56 cm-1 en 18 cm-1 fouten of werkelijke waardes? Wat zit er precies 'uit elkaar'? Waarom is een verschuiving goed (of slecht)? Explain it to me.

### Grok said

# Wat die getallen zijn

Eerst het belangrijkste: **$56$ en $18$ zijn geen fouten.**

Het zijn **verschillen** tussen berekende pieken. Net als: de ene toren is $56\,\mathrm{m}$ hoger dan de andere. Dat is een hoogteverschil, geen rekenfout.

---

## Wat wordt er eigenlijk gemeten?

Een molecuul kan trillen. Elke trilling hoort bij een getal, in $\mathrm{cm}^{-1}$.

Hoger getal = snellere trilling.

In een spectrum zie je dat als een **piek**.

De computer (hier: B3LYP) rekent uit: *waar ligt die piek voor dit molecuul?*

Ze kijken steeds naar **hetzelfde soort piek**: de buiging van C–H-bindingen aan de rand, uit het vlak van het molecuul. Niet “alle pieken door elkaar”.

Dus: één soort piek, drie moleculen, drie getallen.

---

## De tabel nog een keer, in schooltaal

Alle drie de moleculen hebben dezelfde formule $\mathrm{C}_{18}\mathrm{H}_{12}$ en vier ringen. Alleen de *vorm* verschilt (wel of geen inhammen, “baaien”).

| Molecuul | Aantal baaien | Berekende piek |
| --- | --- | --- |
| tetraceen | 0 | $735{,}0\,\mathrm{cm}^{-1}$ |
| chryseen | 1 | $751{,}8\,\mathrm{cm}^{-1}$ |
| trifenyleen | 3 | $733{,}8\,\mathrm{cm}^{-1}$ |

Nu de verschillen — aftrekken, niets meer:

$$751{,}8 - 735{,}0 = 16{,}8$$

$$733{,}8 - 735{,}0 = -1{,}2$$

Die $16{,}8$ ronden ze in de tekst af tot “ongeveer $17$” of “de band beweegt $18\,\mathrm{cm}^{-1}$ tussen isomeren”.

**Uit elkaar zitten** betekent dus: de piek van het ene molecuul ligt zoveel tikken hoger of lager dan de piek van het andere.

De $56\,\mathrm{cm}^{-1}$ is hetzelfde soort verschil, maar bij een ander paar: naftaleen tegen antraceen, dezelfde *soort* piek. Twee moleculen, twee berekende plekken, het verschil is $56$. Ook dat is geen fout. Het is hoe ver die twee pieken uit elkaar liggen.

---

## Wat is dan wél een “fout”?

Pas als je die berekende piek gaat **vergelijken met een meting in het lab**, of met een **voorspelling van een model**.

Dan krijg je:

$$\text{afwijking} = \text{voorspeld} - \text{gemeten}$$

of

$$\text{afwijking} = \text{voorspeld} - \text{andere berekening}$$

In het plan mag die afwijking hoogstens **$10\,\mathrm{cm}^{-1}$** zijn tegen een gasmeting. Dat is een afgesproken grens, zoals: “het antwoord mag maximaal $10$ naast het goede getal zitten.”

$$18 > 10, \qquad 56 > 10$$

Dus: de *verschillen tussen moleculen* zijn groter dan de *toegestane afwijking van één voorspelling*. Daarom zijn $18$ en $56$ gevaarlijk voor het model — niet omdat ze “fout berekend” zijn.

---

## Is een verschuiving goed of slecht?

Op zichzelf **geen van beide**. Een piek mag best opschuiven als het molecuul van vorm verandert. Dat is natuurkunde.

Goed of slecht hangt af van **wat je model belooft**.

Stel je model is:

> “Plak er één baai bij, dan schuift de piek steeds met hetzelfde stapje.”

Dat is een lineaire regel, zoals $y = a \cdot x$:

- $0$ baaien → piek $735$
- $1$ baai → je verwacht $735 + a$
- $3$ baaien → je verwacht $735 + 3a$

Uit chryseen volgt $a \approx 16{,}8$.

Dan zou trifenyleen moeten liggen rond

$$735 + 3 \times 16{,}8 = 785$$

Maar de berekening geeft $734$. Dat is geen klein verschil. De punten liggen niet op een rechte lijn.

Daarom zeggen ze: de baai is **geen optelbaar motief**.

Niet: “de computer heeft een fout van $18$.”

Wel: “als je denkt dat je baaien kunt optellen als blokjes, klopt die gedachte niet.”

Een verschuiving is dus:

- **goed** als je hem verwacht en hij binnen de grens van $10$ blijft;
- **slecht voor het model** als het model “bijna geen verschuiving” of “steeds hetzelfde stapje” belooft, en de werkelijke verschuiving groter is dan $10$.

---

## Het muntworp-verhaal, kort

Eerst pakten ze in een venster van getallen **gewoon de sterkste piek**.

Bij tetraceen lagen twee pieken bijna even hoog: $66{,}1$ en $66{,}0$. Het verschil is $0{,}1$. De computer koos er één. Daardoor leek één baai ineens een sprong van $127\,\mathrm{cm}^{-1}$ te geven. Dat is geen meting van de baai. Dat is dobbelen welke piek je pakt.

Daarna hebben ze de *juiste soort* piek naast elkaar gezet (kwartet bij kwartet). Pas toen kwamen $735$, $752$ en $734$ tevoorschijn. Die drie zijn de echte vergelijking.

---

## Zin om te onthouden

De pieken zelf zijn berekende plekken.

$56$ en $18$ zijn **afstanden tussen die plekken**.

De $10$ is de **maximale misser** die het plan nog accepteert.

Als twee moleculen die volgens het model “hetzelfde antwoord” zouden moeten geven meer dan $10$ uit elkaar liggen, faalt het model — niet de rekenmachine.

### You said

Kun je afbeeldingen maken die moleculen, en daarin aantonen welke atomen behoren tot de baai, welke atomen de berekeningen hebben laten bewegen en waarom?

### Grok said

## 1. Wat is een baai?

Een baai is geen extra atoom. Het is een **inham** in de rand: een U-vorm.

De atomen van de baai zijn:

- de koolstofatomen die de U maken (oranje),
- de **twee waterstofatomen die naar elkaar wijzen** over die inham (rood).

Die twee rode H zitten niet aan elkaar vast. Ze komen alleen in de ruimte dichtbij elkaar (ongeveer $2{,}5\,\text{Å}$).

Dit is fenantreen, het schoolvoorbeeld: één baai.

---

## 2. Welke atomen laat de berekening bewegen?

Bij déze piek (C–H uit het vlak) bewegen vooral de **waterstofatomen aan de rand**. Ze gaan het papier in en uit. De koolstofringen blijven bijna liggen.

Op tetraceen zitten twee *soorten* van die rand-H:

- **blauw = kwartet**: vier H naast elkaar aan een kort uiteinde,
- **groen = solo**: één losse H aan een lange zijde.

Geen baai. Toch twee sterke pieken in hetzelfde venster. Daarom ging het mis toen de computer “pak de sterkste” deed: kwartet en solo waren bijna even sterk ($66{,}1$ tegen $66{,}0$).

Zijkant, nog simpeler:

---

## 3. Waarom die $18\,\mathrm{cm}^{-1}$?

Nu dezelfde *soort* beweging vergelijken: de **blauwe kwartet-H**, op drie moleculen met dezelfde formule $\mathrm{C}_{18}\mathrm{H}_{12}$.

Rood markeert alleen de baai. Blauw is wat de piek maakt.

| Molecuul | Baaien | Piek van de blauwe H |
| --- | --- | --- |
| tetraceen | 0 | $735\,\mathrm{cm}^{-1}$ |
| chryseen | 1 | $752\,\mathrm{cm}^{-1}$ |
| trifenyleen | 3 | $734\,\mathrm{cm}^{-1}$ |

De rode baai-H zijn dus **niet** de atomen van de piek die ze vergeleken. De baai verandert alleen de *omgeving* van de blauwe H. Eén baai in de buurt schuift die piek $17$ tikken. Drie baaien doen dat niet drie keer. Daarom is “tel de baaien en tel $17$ op” geen goede regel.

Kort: rood = vormkenmerk (baai). Blauw = wat er trilt (kwartet). De $18\,\mathrm{cm}^{-1}$ is hoe ver die blauwe piek opschuift als de rode inham van vorm verandert — geen rekenfout.

### You said

Zijn de berekende pieken (van 735,0 cm-1, 751,8 cm-1 en 733,8 cm-1) pieken die in de werkelijkheid ook voorkomen bij tetraceen, chryseen en trifenyleen, of zijn het artefacten van onze keuze voor beperkte trillingen?

### Grok said

Het zijn **geen labpieken** en ook **geen verzonnen pieken**. Het zijn echte trillingen van het model, op een plek waar die moleculen in het echt óók een sterke band hebben. De drie decimalen $735{,}0$, $751{,}8$ en $733{,}8$ bestaan alleen in de berekening.

## Wat de computer heeft gedaan

Voor elk molecuul rekent hij *alle* trillingen uit (voor tetraceen $3\times 30-6=84$ stuks). Daar zit ergens een beweging bij: de vier waterstofatomen aan het korte uiteinde, het vlak uit.

Die ene trilling krijgt in B3LYP/6-31G* (harmonisch, geen schaalfactor) het getal $735{,}0\,\mathrm{cm}^{-1}$ bij tetraceen. Zelfde soort beweging bij chryseen: $751{,}8$. Bij trifenyleen: $733{,}8$.

Het venster $600$–$1000$ maakt die trilling niet. Het venster **kiest alleen welke trilling ze opschrijven**. Kies je de verkeerde (solo in plaats van kwartet), dan krijg je een ander getal — dat was de muntworp van $127\,\mathrm{cm}^{-1}$. Dat wás een artefact van de keuze. Na de reparatie zijn $735/752/734$ de getallen van de bedoelde beweging, niet van een verzonnen beweging.

## Wat er in het lab wél is

Tetraceen, chryseen en trifenyleen hebben in het echt sterke C–H-banden in dit gebied. Bij tetraceen zie je klassiek **twee** sterke pieken: één rond $740\,\mathrm{cm}^{-1}$ (kwartet, de eindrand) en één rond $900\,\mathrm{cm}^{-1}$ (solo, de lange zijde). In een argonmatrix ligt de sterke kwartetachtige band van tetraceen rond $743\,\mathrm{cm}^{-1}$.[⁠Pubs.acs](https://pubs.acs.org/doi/10.1021/jp9834816)

Dus: de *soort* piek is echt. De laptop heeft geen spookband verzonnen.

Wat níét uit het lab komt:

|  | Laptop (nu) | Werkelijkheid |
| --- | --- | --- |
| Getal | $735{,}0$ / $751{,}8$ / $733{,}8$ | andere getallen, vaak een paar tot tientallen $\mathrm{cm}^{-1}$ ernaast |
| Methode | B3LYP, kleine basis, **harmonisch** | anharmonisch, molecule in gas of matrix |
| Betekenis | “deze mode van dit model” | “deze band van dit molecuul” |

Dat $735$ bij tetraceen toevallig dicht bij $743$ in de matrix ligt, is geen bewijs dat de methode goud is. Harmonische DFT zit vaak tientallen tikken te hoog; zonder schaal en zonder anharmoniciteit mag je die overeenkomst niet vieren.

## Kort antwoord op je vraag

- **Komen die pieken in de werkelijkheid voor?** Ja, als *soort*: kwartet-C–H uit het vlak rond $11$–$14\,\mu\mathrm{m}$. Tetraceen heeft die band echt, en ook de solo ernaast.
- **Zijn $735{,}0$, $751{,}8$ en $733{,}8$ de echte plekken?** Nee. Dat zijn modelgetallen van één gekozen trilling.
- **Zijn ze artefacten van het beperkte venster?** Het venster verzint geen piek. Het kan wél de *verkeerde* echte piek aanwijzen. Dat is één keer gebeurd. Deze drie getallen pretenderen de goede keuze te zijn.

De conclusie “de baai is niet optelbaar” geldt dus voor **deze drie modelpieken ten opzichte van elkaar**, niet voor drie labmetingen. Of dezelfde niet-optelbaarheid in het experiment staat, is een volgende vraag: zelfde toewijzing, maar dan tegen de gemeten band.

14 sources

### You said

Kun je hier een vierde kolom aan toevoegen met de labwaarde (indien bekend)?

### Grok said

Hier is dezelfde tabel met een labkolom. Dat zijn **geen gasfase-lijsten**: argonmatrix van Hudgins & Sandford (1998), plus voor chryseen de klassieke sterke IR-band. Matrix mag volgens jullie plan tot $15\,\mathrm{cm}^{-1}$ naast de berekening zitten.[⁠Pubs.acs](https://pubs.acs.org/doi/10.1021/jp9834816)

| Molecuul | Baaien | Model, blauwe H | Lab, sterke C–H uit het vlak |
| --- | --- | --- | --- |
| tetraceen | 0 | $735\,\mathrm{cm}^{-1}$ | $743\,\mathrm{cm}^{-1}$ (Ar-matrix; complex rond $742{,}9$) |
| chryseen | 1 | $752\,\mathrm{cm}^{-1}$ | $\approx 744$–$748\,\mathrm{cm}^{-1}$ (sterke IR/matrix-band; er is nóg een sterke oop-band rond $820$) |
| trifenyleen | 3 | $734\,\mathrm{cm}^{-1}$ | $741\,\mathrm{cm}^{-1}$ (Ar-matrix, $740{,}8$, de sterkste band) |

Twee dingen om niet door elkaar te halen.

**Elke rij apart** ziet er braaf uit. Model versus lab: ongeveer $8$, $4$–$8$ en $7\,\mathrm{cm}^{-1}$ ernaast. Dat is binnen de matrixgrens van $15$. “B3LYP zit in de buurt van de piek” is dus niet het schandaal.

**De drie labgetallen naast elkaar** vertellen iets anders dan de drie modelgetallen. In het lab liggen tetraceen, chryseen en trifenyleen bijna op één hoop ($743$, $\sim 746$, $741$). In het model springt chryseen er $17$ tikken uit. Als die labbanden inderdaad dezelfde *soort* beweging zijn als jullie blauwe H, dan is de baai-sprong van $+17$ een trekje van B3LYP — niet iets dat het experiment zo groot laat zien.

Voorbehoud bij chryseen: daar zijn twee sterke uit-het-vlak-banden ($\sim 744$ en $\sim 820$). $744$–$748$ is de eerlijke buur van jullie $752$; $820$ is een andere rand. Zonder mode-overlap (welke labpiek = welke berekende beweging) is de middelste cel de zachtste van de drie. Tetraceen $743$ en trifenyleen $741$ zijn steviger: daar is die band de sterkste C–H-oop-piek in de matrix.

25 sources

### You said

Wat betekent B3LYP. Is het CCSD(T)? Geef kort antwoord.

### Grok said

Nee. Het zijn twee verschillende rekenmethodes.

**B3LYP** is een vorm van DFT: een goedkope schatting van hoe elektronen in het molecuul zitten. Snel genoeg voor frequenties van tetraceen op een laptop. Minder nauwkeurig dan de “gouden” sport van het plan.

**CCSD(T)** is gekoppelde-clustertheorie met een triples-correctie. Duurder, en in jullie plan de gouden energie-anker. Op de laptop tot nu toe alleen als *één energie* van benzeen, niet als die pieken van $735/752/734$.

Die drie getallen zijn B3LYP, geen CCSD(T).

### You said

Op mijn laptop is 779 GB vrij. Kunnen we dan geen CCSD(T) draaien?

### Grok said

Nee — **779 GB vrij is schijfruimte, geen werkgeheugen.**

CCSD(T) valt bij jullie op **RAM**, niet op de schijf. Benzeen met cc-pVDZ (114 functies) ging stuk op **24–28 GB RAM** in de (T)-stap. 6-31G* (102 functies) paste wél: één energie in 20 seconden.

Op een gewone Asus zit typisch 16–32 GB RAM, soms 64. Dat is twee ordes kleiner dan 779 GB. Extra vrije terabytes op de SSD maken de triples-tabel niet kleiner.

Zelfs mét genoeg RAM blijft het volgende probleem **tijd**, niet opslag: één energie van benzeen is triviaal; een Hessian of QFF van naftaleen/tetraceen op CCSD(T) is een andere sport. Schijf is hier niet de rem.

### You said

Klopt, installed RAM is 32,0 GB. Hoeveel zou ik erbij moeten doen om CCSD(T) te kunnen runnen (als ik alle tijd van de wereld had)?

### Grok said

Met **32 GB** kun je wat jullie al deden: CCSD(T)-*energie* van benzeen in 6-31G*. Alles groter botst op het (T)-stuk in het geheugen, niet op de schijf.

Grove lat, **alleen één energie**, canoniek CCSD(T), in-core (T):

| Job | Basisfuncties | RAM-orde | Past op jouw Asus? |
| --- | --- | --- | --- |
| benzeen / 6-31G* | 102 | ~26 GB | ja, nu al |
| benzeen / cc-pVDZ | 114 | krap 40–64 GB | waarschijnlijk met **+32 GB** (totaal 64) |
| naftaleen / 6-31G* | 156 | eerder 100–200 GB | nee, tenzij de code de triples naar schijf schrijft |
| antraceen / tetraceen-energie | 200–280 | honderden GB tot >1 TB | geen laptop meer |
| **frequenties of QFF** van die laatste | hetzelfde × tientallen jobs | idem, plus weken rekentijd | niet met extra RAM-reepjes |

Dus: **+32 GB (totaal 64)** is zinvol voor “iets grotere benzeen-jobs”.

**+96 GB (totaal 128)** is het maximum dat op een dikke laptop/werkstation nog normaal is — dan worden naftaleen-energies denkbaar, geen tetraceen-QFF.

De pieken van $735/752/734$ worden daar niet goud van. Daarvoor moet je de *methode* veranderen (lokale CC, DLPNO, hybride QFF), niet het geheugen. Extra RAM koopt je grotere *energie*-punten op de kleine sport, geen canonieke CC-Hessian van $\mathrm{C}_{18}\mathrm{H}_{12}$.

### You said

Okay, even terugkomende op de baaien. Wat ik in de tabel zie is dat tetraceen, chryseen en trifenyleen in het lab dichtbij elkaar zitten, terwijl het model er soms een beetje, soms wat meer naast zit. Het idee dat soortgelijke baaien in verschillende moleculen ongeveer dezelfde band veroorzaken, lijkt daarmee in de werkelijkheid te kloppen, nietwaar? Het is alleen dat onze wiskunde niet in orde is. Zou ons doel daarmee niet moeten zijn om een model te leren overeen te komen met de waarden uit de werkelijkheid?

### Grok said

Bijna — maar de les uit die labkolom is nét anders dan “baaien veroorzaken dezelfde band”.

## Wat de labgetallen wél zeggen

Tetraceen (0 baaien), chryseen (1) en trifenyleen (3) hebben in de matrix allemaal een sterke C–H-band rond $741$–$748\,\mathrm{cm}^{-1}$. Die piek schuift dus **nauwelijks** als het aantal baaien verandert.

Dat is geen bewijs dat de baai de band *maakt*. De band komt van de **blauwe H** (kwartet-rand). De baai is alleen de inham ernaast. In het lab lijkt die inham deze piek bijna met rust te laten.

Dus:

- **wel** in de werkelijkheid: zelfde *soort rand* → ongeveer zelfde plek ($\sim 740\,\mathrm{cm}^{-1}$);
- **niet** aangetoond: “tel baaien, tel $\mathrm{cm}^{-1}$ op”;
- B3LYP is hier de sloddervos: die zet chryseen $17$ tikken te hoog terwijl het lab dat niet doet.

Jullie model is dus niet “een beetje ernaast”. Hij verzint een sprong die het experiment niet laat zien.

## Moet het doel dan “leren matchen met het lab” zijn?

Ja, **uiteindelijk**. Het plan zegt dat al: de lat is het gasfase-experiment, geen andere berekening.

Nee, als dat betekent: drie matrixgetallen invullen tot B3LYP ze naschrijft. Dat kan in één middag met een schaalfactor. Dan “klopt” chryseen, maar je weet niet of de volgende isomeer ook klopt, en je hebt term E niet gemeten — je hebt hem weggestopt.

Een bruikbaar doel is smaller:

1. Dezelfde trilling in model én lab aanwijzen (geen muntworp).
2. Op **meer** dan drie moleculen kijken of de kwartetband in het lab inderdaad plat blijft.
3. Het model zó verbeteren dat hij die platheid zelf geeft — of eerlijk opbiechten hoeveel hij ernaast zit (term B + E).

CCSD(T) is één weg naar (3): een betere elektronische oppervlakte, hopelijk zonder die valse $+17$. Empirisch schalen is een andere, goedkopere weg — maar dan moet je de schaal *testen* op een molecuul dat niet in de fit zat.

Kort: het lab zegt “deze band is een randklasse, geen baaiteller”. Het doel is een model dat dát naschrijft én zegt hoe groot de restfout is — niet een model dat drie bekende pieken kan opdreunen.

### You said

Nee, snap ik. Maar in het project wordt gezegd: een atlas met randklasse als sleutel faalt. Maar het lab toont: die kan slagen. De baaien zijn van ondergeschikt belang. We kunnen de baaien laten voor wat ze zijn. Als je een model maakt dat soortgelijke randklasses soortgelijke banden geeft, heb je iets. Toch?

### Grok said

Ja — voor **deze** band is dat de juiste lezing. Met één correctie op wat de repo “falen” noemt.

## Wat het lab doet

Zelfde randklasse (kwartet-achtige C–H uit het vlak), drie vormen, drie baaitellingen: labpieken binnen een paar $\mathrm{cm}^{-1}$ van elkaar. De baai is hier bijzaak. De sleutel die overblijft is: **solo / duo / trio / kwartet**.

Dat is geen nieuw inzicht. Daar is PAK-IR sinds de jaren tachtig omheen gebouwd, en PAHdb ook. Een model dat zegt “kwartet → venster rond $740\,\mathrm{cm}^{-1}$, solo → venster rond $880$–$900$” heeft inderdaad iets — het heeft wat de telescopische banden überhaupt kunnen dragen.

## Waarom de repo “de klasse-atlas faalt” zei

Die $56\,\mathrm{cm}^{-1}$ was B3LYP, en waarschijnlijk **twee verschillende klassen** naast elkaar: naftaleen is in de leerboekindeling duo, antraceen heeft kwartet-uiteinden. Dat die pieken tientallen tikken uit elkaar zitten is dan geen falen van de sleutel. Dat *is* de sleutel.

Binnen één klasse, op dezelfde formule $\mathrm{C}_{18}\mathrm{H}_{12}$, zegt het lab: de atlas kán slagen. B3LYP zei het omgekeerde door chryseen omhoog te trekken. Geloof hier het lab, niet die sprong.

## Wat je wél nog moet bewijzen

“Soortgelijke rand → soortgelijke band” is waar als *venster*, niet als *één getal*.

- Kwartet in het lab: grof $725$–$750$, niet één piketpaaltje op $743$.
- Jullie lat is $10\,\mathrm{cm}^{-1}$ tegen gas. Een venster van $25$ is nuttig voor JWST-klasse (“dit is kwartet-rand”), te wijd voor “dit is tetraceen”.
- Grootte blijft open: antraceen-kwartet tegen tetraceen-kwartet is al een paar tot tien tikken. Klasse constant, getal niet perfect constant.

Baaien helemaal weggooien hoeft niet. Op de $3\,\mu\mathrm{m}$-rekband doen baai-H wél mee. Op **deze** $11$–$15\,\mu\mathrm{m}$-piek mogen ze naar de tweede plaats.

Kort: ja. Een model dat randklasse op een bandvenster afbeeldt, met een gemeten breedte, is het product dat de data kunnen dragen. De repo had de klasse te vroeg doodverklaard op een DFT-verschil dat het lab niet zo laat zien.

### You said

Even omgedraaid. Stel, je bent astronoom en je neemt een spectrum waar waarin een band zit van 725-750. Je weet: dit komt wellicht van een kwartet. Maar dan weet je dus nog steeds niet van welk molecuul, want: dezelfde band komt van vele moleculen. Het doel om vanuit een spectrum een lijst van aromatische moleculen te herkennen is dus niet mogelijk, niet omdat de berekeningen niet mogelijk zijn of de lab experimenten niet te doen zijn of het neuraal network niet gemaakt kan worden, maar omdat vele aromatische moleculen dezelfde randklassen hebben en dus dezelfde banden?

### Grok said

Ja. Voor die band is het probleem geen rekenkracht, geen lab en geen netwerk. Het is **onderbepaaldheid**.

Een piek in $725$–$750\,\mathrm{cm}^{-1}$ zegt: *er zijn kwartet-randen*. Tetraceen, trifenyleen, antraceen, nog honderden grotere PAK’s en hun ionen kunnen die rand hebben. Het spectrum wijst een **bouwsteentje** aan, geen naam.

Dat geldt het hardst voor de $11$–$15\,\mu\mathrm{m}$-banden (C–H uit het vlak). Die zijn expres een randteller. Vandaar solo/duo/trio/kwartet in plaats van “pyreen⁺”.

Het hele infraroodspectrum is iets minder arm:

- lading verschuift vooral de C–C-banden ($6{,}2$, $7{,}7\,\mu\mathrm{m}$);
- grootte en compactheid verschuiven gewichten tussen $11{,}2$ en $12{,}7\,\mu\mathrm{m}$;
- baai-H laten zich eerder bij $3{,}3\,\mu\mathrm{m}$ zien;
- skeletmodi onder $15\,\mu\mathrm{m}$ zijn iets molecuul-specifieker, maar zwak.

Zelfs met al die extra knoppen krijg je geen unieke molecuullijst. Je krijgt een **mengsel**: randklassen × lading × grootteklasse. Twee catalogi van honderden PAK’s kunnen hetzelfde JWST-spectrum bijna even goed fitten.

Een neuraal netwerk kan die onbepaaldheid niet wegtoveren. Het kan hoogstens dezelfde onzekerheid netter opschrijven.

Berekenen blijft nuttig, maar voor een andere zin: *welke klassen maken welke vensters, en hoe ver schuift het venster als het ion wordt of groter wordt?* Niet: *welke piek is welk molecuul.* Dat laatste doel faalt omdat de natuur dezelfde rand op veel moleculen plakt — niet omdat de laptop te klein is.
