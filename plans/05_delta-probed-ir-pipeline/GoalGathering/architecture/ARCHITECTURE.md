# Architectuur plan 05 (voor de auteurs, Nederlands; eerste versie 19 september 2026, herzien 20 september)

**Vier soorten diagram, uit elkaar gehouden (afspraak van 20 september).**

| soort | wat het toont | bladen |
|---|---|---|
| **Datacreatie** | processen die opslagen vullen: de labelfabriek (coupled-cluster-correcties per molecuul) en de corpusstap (DFT-paren) | 1, 2 |
| **Training, validatie en test** | het proces waar een getraind netwerk met licentietabel uit komt; hier hoort de score tegen de laboratoriumkolommen (de test) | 3 |
| **Pipeline** | wat er staat als onderzoek en training klaar zijn: molecuul in, forward pass als één figuurtje, spectrale vorm uit, naar de astronoom | 4 (en 4a: de componenten van het netwerk) |
| **Onderzoeksproces** | de toetsen die beslissen of dit alles er zo komt; het enige soort blad waar data, besluiten en experimentnummers in mogen | 5, 6 |

Het overzicht (blad 0) toont de vier soorten en de opslagen die ze verbinden. Rekenplaats staat er voorlopig niet in; die komt later per blokje.

**Legenda.**

| figuur | betekenis |
|---|---|
| rechthoek | processtap: een bewerking die data omzet in andere data (op blad 0: een heel proces) |
| rechthoek met ronde uiteinden (grijs) | data-object: een invoer, tussenproduct of uitkomst die door het proces stroomt |
| cilinder | (vervallen op 20 september; alleen nog op de bladen die nog niet zijn bijgewerkt) |
| ruit (groen) | poort: een toets met een vooraf vastgelegde uitkomst — door, of niet door |
| doorgetrokken rand | bestaat en is gemeten |
| gestippelde rand, gele vulling | nog niet gebouwd |
| pijl | datastroom |

**Regel (20 september, de auteur): geen opslagfiguren (cilinders) meer in de diagrammen.** Een proces begint bij zijn eerste data-object en eindigt bij zijn laatste; waar de data vandaan komt of heen gaat staat zo nodig in de naam van het data-object. Daarmee vervallen de onzichtbare groepjes en vulknopen en staat alles weer in standaard Mermaid. Toegepast op blad 4; **de bladen 0, 1, 2, 3, 4a volgen** (samen met de stap→data-object-regel en de naamgeving hieronder). (3) **regel, 20 september:** elke processtap mondt uit in precies één data-object, dat de volgende stap(pen) voedt; splitsingen komen alleen uit een data-object of een ruit, nooit uit een processtap. **Naamgeving (20 sep):** een processtap heet naar de bewerking of de rekenmethode ("DFT", "VPT2", "Diagonalisatie"), een data-object naar het ding ("Hessiaan H0 en dipoolafgeleiden", "Normaalmodi"); geen dubbele woorden tussen stap en object; **elke processtap noemt tussen haken het softwarepakket** ("DFT (psi4)", "VPT2 (pyVPT2 op psi4)") of "eigen software" als wij het maken. Toegepast op blad 4 (de DFT-stap is gesplitst in "DFT: Hessiaan en dipoolafgeleiden" → schets, "Modusanalyse" → modi, "VPT2 op DFT" → anharmonische constanten); **de bladen 1, 2, 3, 4a volgen nog** en worden daarbij op dezelfde manier herschreven.

Op de onderzoeksprocesbladen: groen = geslaagd, blauw = loopt, gestippeld = nog te doen, rood = verloren en gesloten. Elk proces begint en eindigt bij een data-object. Bron van waarheid: de `.mmd`-bestanden in deze map (Mermaid; renderen op GitHub).

## 0. Overzicht: vier soorten proces en hun opslagen

```mermaid
%% Overzicht plan 05 (niveau 1): vier soorten proces en de opslagen die ze verbinden. Stand 20 september 2026.
%% Rechthoek = proces (hier: een heel blad); cilinder = opslag; ronde uiteinden = data-object; pijl = datastroom. Gestippeld = nog niet gebouwd.
flowchart LR
  linkStyle default stroke:#8a9bb0,stroke-width:2.2px
  classDef planned stroke-dasharray: 6 4,stroke:#b8860b,fill:#fff3c4,color:#111
  classDef ext fill:#cfd8e3,stroke:#3d5a80,color:#111
  classDef data fill:#e9ecef,stroke:#555,color:#111
  classDef store fill:#dfe7f2,stroke:#5b7a99,color:#111
  classDef proc fill:#f7f7fb,stroke:#333,stroke-width:1.5px,color:#111
  classDef research fill:#fdf2e3,stroke:#8a5a00,color:#111

  CAT[("Molecuulcatalogus: geometrieën, lading, multipliciteit")]:::store

  subgraph DC["Datacreatie (bladen 1 en 2)"]
    direction TB
    LABF["Labelfabriek: coupled-cluster-correctie per molecuul, gelicentieerd tegen directe referenties"]:::proc
    CORPF["Corpusstap: twee DFT-Hessianen per molecuul"]:::proc
  end
  LABELS[("Labelopslag: ΔH-blokken met foutmarge")]:::store
  CORPUS[("Corpus: DFT-paren, vervangercorrectie")]:::store
  SKETCHES[("DFT-schetsen: H0, dipoolafgeleiden, anharmonische constanten")]:::store

  TRAIN["Training, validatie en test (blad 3): voortrainen op het corpus, bijtrainen op de labels, valideren per molecuul, testen per familie tegen labels en laboratoriumkolommen"]:::planned
  MODEL[("Getraind netwerk + licentietabel per familie en ladingstoestand")]:::store
  LABDB[("Laboratoriumspectra")]:::ext
  PAHDB[("PAHdb en andere voorspellers")]:::ext

  PIPE["Pipeline (blad 4): DFT-schets → forward pass → gelicentieerde ΔH-blokken → gecorrigeerde krachtconstanten → spectrale vorm"]:::planned
  SPEC(["Spectrum met foutmarge per band, voor een molecuul zonder laboratoriumspectrum"]):::data
  SPECS[("Spectrumarchief")]:::store

  RES["Onderzoeksproces (bladen 5 en 6): de toetsen die beslissen of dit alles er zo komt"]:::research

  CAT --> LABF --> LABELS
  CAT --> CORPF --> CORPUS
  CORPF --> SKETCHES
  LABF --> SKETCHES
  CORPUS --> TRAIN
  LABELS --> TRAIN
  LABDB --> TRAIN
  PAHDB --> TRAIN
  TRAIN --> MODEL
  CAT --> PIPE
  SKETCHES --> PIPE
  MODEL --> PIPE
  PIPE --> SPEC --> SPECS
  RES -. beslist over .-> DC
  RES -. beslist over .-> TRAIN
  RES -. beslist over .-> PIPE
```

## 1. Datacreatie — de labelfabriek: hoe één label ontstaat

```mermaid
%% Datacreatie — de labelfabriek: hoe één label ontstaat (niveau 3).
%% Rechthoek = processtap; ronde uiteinden = data-object; cilinder = opslag (onder het data-object); ruit = poort. Gestippeld = nog niet gebouwd.
flowchart LR
  linkStyle default stroke:#8a9bb0,stroke-width:2.2px
  classDef planned stroke-dasharray: 6 4,stroke:#b8860b,fill:#fff3c4,color:#111
  classDef data fill:#e9ecef,stroke:#555,color:#111
  classDef gate fill:#d9f0dc,stroke:#2e7d32,color:#111
  classDef store fill:#dfe7f2,stroke:#5b7a99,color:#111

  subgraph IN [" "]
    direction BT
    GEO(["Molecuul: geoptimaliseerde geometrie, lading, multipliciteit"]):::data
    CAT[("Molecuulcatalogus")]:::store
    CAT --> GEO
    SP0["&nbsp;<br/>&nbsp;<br/>&nbsp;"]
  end
  H0["Stage A: DFT-Hessiaan H0 → modi L, frequenties, families, irreps"]
  SKETCH(["DFT-schets"]):::data
  SYM["Symmetrieprior: koppeling alleen binnen een irrep-blok"]
  PAT["Patronen: gradiëntrichtingen voor de koppelingen, ±q langs enkele modi voor de diagonaal"]
  DECK(["Deck"]):::data
  REF["Referentieruimtes op x0: lokale orbitalen en fragmentruimtes, één keer gebouwd en verzegeld"]
  TRANS["Transport van de ruimtes naar elke deckgeometrie"]
  EN["Coupled-cluster-energieën in de bevroren ruimtes"]
  GR["Coupled-cluster-gradiënten in de bevroren ruimtes"]:::planned
  OPEN["Open-schil-variant voor kationen"]:::planned
  RESP(["Responsen: energieën en gradiënten per patroon, met ruis"]):::data
  SOLVE["Oplossing per familieblok: diagonaal en koppelingen"]
  BUDGET["Foutbudget per familie: ruis, quartische term, herstelfout"]
  LIC{"Licentie tegen direct berekende referenties"}:::gate
  subgraph OUT [" "]
    direction TB
    LABEL(["Label: ΔH-blokken met foutmarge per familie"]):::data
    STORE[("Labelopslag")]:::store
    LABEL --> STORE
    SP1["&nbsp;<br/>&nbsp;<br/>&nbsp;"]
  end
  style IN fill:none,stroke:none
  style OUT fill:none,stroke:none

  IN --> H0 --> SKETCH --> SYM --> PAT --> DECK
  SKETCH --> REF --> TRANS
  DECK --> TRANS
  TRANS --> EN --> RESP
  TRANS --> GR --> RESP
  TRANS --> OPEN --> RESP
  RESP --> SOLVE --> LIC
  RESP --> BUDGET --> LIC
  LIC --> OUT

  %% onzichtbare vulknopen boven de data-objecten (uitlijning met de naaste stap); hun verbindingen zijn weggestyled
  GEO --- SP0
  SP1 --- LABEL
  linkStyle 21 stroke:none,stroke-width:0px
  linkStyle 22 stroke:none,stroke-width:0px
  style SP0 fill:none,stroke:none,color:transparent
  style SP1 fill:none,stroke:none,color:transparent
```

## 2. Datacreatie — het corpus van DFT-paren

```mermaid
%% Datacreatie — het corpus: twee DFT-Hessianen per molecuul en wat eruit volgt (niveau 3).
%% Rechthoek = processtap; ronde uiteinden = data-object; cilinder = opslag (onder het data-object). Alles bestaat.
flowchart LR
  linkStyle default stroke:#8a9bb0,stroke-width:2.2px
  classDef data fill:#e9ecef,stroke:#555,color:#111
  classDef store fill:#dfe7f2,stroke:#5b7a99,color:#111

  subgraph IN [" "]
    direction BT
    MOL(["Molecuul: SMILES of geometrie, lading, multipliciteit"]):::data
    CAT[("Molecuulcatalogus: manifest met lagen")]:::store
    CAT --> MOL
    SP0["&nbsp;<br/>&nbsp;<br/>&nbsp;"]
  end
  GEO["Startgeometrie en optimalisatie op laag niveau"]
  HLO["Hessiaan op laag niveau (de schets die de pipeline ook gebruikt)"]
  HHI["Hessiaan op hoog niveau, zelfde geometrie"]
  DIP["Dipoolafgeleiden en anharmonische constanten op laag niveau"]
  MODES["Modi, frequenties, families, symmetrieblokken uit de laag-niveau-Hessiaan"]
  PROXY["Vervangercorrectie: ΔH = H_hoog − H_laag, volledig, in de modusbasis per familieblok"]
  subgraph OUT1 [" "]
    direction TB
    PAIR(["DFT-paar met vervangercorrectie en modus-tokens"]):::data
    CORPUS[("Corpus")]:::store
    PAIR --> CORPUS
    SP1["&nbsp;<br/>&nbsp;<br/>&nbsp;"]
  end
  subgraph OUT2 [" "]
    direction TB
    SK(["DFT-schets: H0, modi, dipoolafgeleiden, anharmonische constanten"]):::data
    SKETCHES[("DFT-schetsen")]:::store
    SK --> SKETCHES
    SP2["&nbsp;<br/>&nbsp;<br/>&nbsp;"]
  end
  style IN fill:none,stroke:none
  style OUT1 fill:none,stroke:none
  style OUT2 fill:none,stroke:none

  IN --> GEO --> HLO --> MODES
  GEO --> HHI
  GEO --> DIP
  HLO --> PROXY
  HHI --> PROXY
  MODES --> PROXY --> OUT1
  MODES --> OUT2
  HLO --> OUT2
  DIP --> OUT2

  %% onzichtbare vulknopen boven de data-objecten (uitlijning met de naaste stap); hun verbindingen zijn weggestyled
  MOL --- SP0
  SP1 --- PAIR
  SP2 --- SK
  linkStyle 15 stroke:none,stroke-width:0px
  linkStyle 16 stroke:none,stroke-width:0px
  linkStyle 17 stroke:none,stroke-width:0px
  style SP0 fill:none,stroke:none,color:transparent
  style SP1 fill:none,stroke:none,color:transparent
  style SP2 fill:none,stroke:none,color:transparent
```

## 3. Training, validatie en test

```mermaid
%% Training, validatie en test (niveau 3): uit corpus en labels komt een getraind netwerk met een licentietabel. Nog niet begonnen.
%% Rechthoek = processtap; ronde uiteinden = data-object; cilinder = opslag (onder het data-object); ruit = poort. Gestippeld = nog niet gebouwd.
flowchart LR
  linkStyle default stroke:#8a9bb0,stroke-width:2.2px
  classDef planned stroke-dasharray: 6 4,stroke:#b8860b,fill:#fff3c4,color:#111
  classDef data fill:#e9ecef,stroke:#555,color:#111
  classDef gate fill:#d9f0dc,stroke:#2e7d32,color:#111
  classDef store fill:#dfe7f2,stroke:#5b7a99,color:#111
  classDef ext fill:#cfd8e3,stroke:#3d5a80,color:#111

  subgraph IN1 [" "]
    direction BT
    PROXY(["DFT-paren met vervangercorrectie en modus-tokens"]):::data
    CORPUS[("Corpus")]:::store
    CORPUS --> PROXY
    SP0["&nbsp;<br/>&nbsp;<br/>&nbsp;"]
  end
  subgraph IN2 [" "]
    direction BT
    LAB(["Labels: ΔH-blokken met foutmarge per familie"]):::data
    LABELS[("Labelopslag")]:::store
    LABELS --> LAB
    SP1["&nbsp;<br/>&nbsp;<br/>&nbsp;"]
  end
  SPLIT["Splitsing per molecuul en per kern: train, validatie, test — vastgelegd vóór het trainen"]:::planned
  PRE["Voortrainen op de vervangercorrectie: bloktarget per familie, gebalanceerd verlies"]:::planned
  FT["Bijtrainen op de labels: kleine leersnelheid, vroeg stoppen op de validatiemoleculen"]:::planned
  ENS["Ensemble over seeds"]:::planned
  VAL["Validatie: fout per familie op de validatiemoleculen, tegen de nulregel, de mediaanregel en de type-overdracht"]:::planned
  TEST["Test op de testmoleculen: ΔH-blokken en het spectrum dat eruit volgt"]:::planned
  LABDB[("Laboratoriumspectra")]:::ext
  PAHDB[("PAHdb en andere voorspellers")]:::ext
  SCORE{"Licentie per familie en ladingstoestand: fout onder de marge van de scorekolom van die familie"}:::gate
  CAL["Kalibratie van de onzekerheid: spreiding van het ensemble tegen de gemeten fout"]:::planned
  subgraph OUT [" "]
    direction TB
    MODEL(["Getraind netwerk + licentietabel + kalibratie"]):::data
    MODELS[("Modelopslag")]:::store
    MODEL --> MODELS
    SP2["&nbsp;<br/>&nbsp;<br/>&nbsp;"]
  end
  subgraph OUT2 [" "]
    direction TB
    RES(["Testscores per band en familie, naast de opponenten"]):::data
    RESS[("Scorearchief")]:::store
    RES --> RESS
    SP3["&nbsp;<br/>&nbsp;<br/>&nbsp;"]
  end
  style IN1 fill:none,stroke:none
  style IN2 fill:none,stroke:none
  style OUT fill:none,stroke:none
  style OUT2 fill:none,stroke:none

  IN1 --> SPLIT
  IN2 --> SPLIT
  SPLIT --> PRE --> FT --> ENS --> VAL --> TEST --> SCORE
  LABDB --> SCORE
  PAHDB --> TEST
  SCORE --> OUT2
  SCORE --> CAL --> OUT

  %% onzichtbare vulknopen boven de data-objecten (uitlijning met de naaste stap); hun verbindingen zijn weggestyled
  PROXY --- SP0
  LAB --- SP1
  SP2 --- MODEL
  SP3 --- RES
  linkStyle 17 stroke:none,stroke-width:0px
  linkStyle 18 stroke:none,stroke-width:0px
  linkStyle 19 stroke:none,stroke-width:0px
  linkStyle 20 stroke:none,stroke-width:0px
  style SP0 fill:none,stroke:none,color:transparent
  style SP1 fill:none,stroke:none,color:transparent
  style SP2 fill:none,stroke:none,color:transparent
  style SP3 fill:none,stroke:none,color:transparent
```

## 4. Pipeline

```mermaid
%% Pipeline (niveau 3): wat er staat als onderzoek en training klaar zijn. Molecuul in, spectrum met foutmarge uit.
%% Regel (20 sep): elke processtap (rechthoek) mondt uit in precies één data-object (ronde uiteinden); waaiers komen alleen uit data-objecten of ruiten.
%% Ruit = poort. Geen opslagfiguren (regel 20 sep). Gestippeld = nog niet gebouwd. De forward pass is één figuurtje.
flowchart LR
  linkStyle default stroke:#8a9bb0,stroke-width:2.2px
  classDef planned stroke-dasharray: 6 4,stroke:#b8860b,fill:#fff3c4,color:#111
  classDef data fill:#e9ecef,stroke:#555,color:#111

  MOL(["Molecuul: geometrie, lading, multipliciteit"]):::data
  COND(["Waarnemingscondities: temperatuur van de bron, resolutie van het instrument"]):::data

  DFT["DFT (psi4)"]
  SK(["Hessiaan H0 en dipoolafgeleiden"]):::data
  VPT["VPT2 (pyVPT2 op psi4)"]
  ANHC(["Anharmonische constanten"]):::data
  MODE["Modusanalyse (eigen software)"]
  MODES(["Normaalmodi: L, frequenties, families, symmetrieblokken"]):::data
  TOKS["Tokenisatie (eigen software)"]
  TOK(["Modus-tokens"]):::data
  FWD["Forward pass (eigen netwerk, PyTorch)"]:::planned
  DH(["ΔH-blokken per familie, met onzekerheid van het ensemble"]):::data
  LICF["Licentiefilter (eigen software)"]:::planned
  DHL(["Toegepaste en geweigerde ΔH-blokken, met reden"]):::data
  APPLY["Samenstellen van H (eigen software)"]
  H(["Krachtconstanten H = H0 + ΔH op gelicentieerde blokken, elders H0; licentiestatus per familie"]):::data
  EIG["Diagonalisatie (eigen software)"]
  POS(["Bandposities met marge en licentiestatus per familie"]):::data
  INT["Intensiteitsberekening (eigen software)"]
  INTS(["Bandintensiteiten"]):::data
  ANH["Anharmonische correctie (eigen software)"]
  ANHS(["Anharmonische verschuivingen per band"]):::data
  SHAPE["Profielvorming (eigen software)"]

  SPEC(["Spectrum: banden met positie, intensiteit, profiel en foutmarge; licentiestatus per familie"]):::data

  MOL --> DFT --> SK
  SK --> MODE --> MODES
  SK --> VPT --> ANHC
  MODES --> TOKS --> TOK --> FWD --> DH --> LICF --> DHL --> APPLY --> H --> EIG --> POS --> SHAPE
  SK --> APPLY
  SK --> INT
  MODES --> INT --> INTS --> SHAPE
  ANHC --> ANH
  MODES --> ANH --> ANHS --> SHAPE
  COND --> SHAPE
  SHAPE --> SPEC
```

## 4a. Componenten van het netwerk

```mermaid
%% Doelarchitectuur — Componenten van het netwerk (niveau 4). Grotendeels nog niet gebouwd.
%% Rechthoek = processtap; ronde uiteinden = data-object; cilinder = opslag (onder het data-object). Gestippeld = nog niet gebouwd.
flowchart LR
  linkStyle default stroke:#8a9bb0,stroke-width:2.2px
  classDef planned stroke-dasharray: 6 4,stroke:#b8860b,fill:#fff3c4,color:#111
  classDef data fill:#e9ecef,stroke:#555,color:#111
  classDef store fill:#dfe7f2,stroke:#5b7a99,color:#111

  subgraph IN [" "]
    direction BT
    INP(["Per molecuul: modus-tokens, lading, multipliciteit"]):::data
    CORPUS[("Corpus en labelopslag")]:::store
    CORPUS --> INP
    SP0["&nbsp;<br/>&nbsp;<br/>&nbsp;"]
  end
  EMB["Embedding van elk modus-token"]
  ENC["Self-attention over de modi van het molecuul"]
  BLK["Blokkop per familie: diagonaal en koppelingen uit de modusvectoren"]:::planned
  PAIR["Paarkop: welke paren dragen een koppeling"]
  UNC["Ensemble over seeds → spreiding per familie"]:::planned
  subgraph OUT [" "]
    direction TB
    OUTB(["ΔH-blok per familie met onzekerheid"]):::data
    STORE[("Voorspellingsopslag")]:::store
    OUTB --> STORE
    SP1["&nbsp;<br/>&nbsp;<br/>&nbsp;"]
  end
  style IN fill:none,stroke:none
  style OUT fill:none,stroke:none

  IN --> EMB --> ENC --> BLK --> UNC --> OUT
  ENC --> PAIR --> OUT

  %% onzichtbare vulknopen boven de data-objecten (uitlijning met de naaste stap); hun verbindingen zijn weggestyled
  INP --- SP0
  SP1 --- OUTB
  linkStyle 9 stroke:none,stroke-width:0px
  linkStyle 10 stroke:none,stroke-width:0px
  style SP0 fill:none,stroke:none,color:transparent
  style SP1 fill:none,stroke:none,color:transparent
```

## 5. Onderzoeksproces — de labelfabriek en de decks

```mermaid
%% Onderzoeksproces — pipeline B: de toetsen die beslissen of de doelarchitectuur van blad 1 er komt. Stand 20 september 2026.
%% Dit blad mag data en besluiten bevatten. Groen = geslaagd; blauw = loopt; gestippeld = nog te doen; rood = mislukt en gesloten.
flowchart LR
  linkStyle default stroke:#8a9bb0,stroke-width:2.2px
  classDef done fill:#d9f0dc,stroke:#2e7d32,color:#111
  classDef running fill:#dbe9ff,stroke:#2a5db0,color:#111
  classDef todo stroke-dasharray: 6 4,stroke:#b8860b,fill:#fff3c4,color:#111
  classDef closed fill:#f6d5d5,stroke:#a33,color:#111
  classDef dec fill:#eee,stroke:#444,color:#111

  M1["M1: bevroren ruimtes zijn glad (benzeen, DZ en TZ; 5–12 sep)"]:::done
  I14["I14: één energie per niet-totaalsymmetrisch patroon (14 sep)"]:::done
  X14["X14/X21/X22: koppelingen exact uit 2k+1 gradiënten, lineair bij elke symmetrie (16–19 sep)"]:::done
  AMP["Amplitudetest: energieroute voor koppelingen gesloten bij naftaleen (17 sep)"]:::closed
  M2B["M2b: geleende gradiëntmotor rekent onze grootheid niet (17 sep)"]:::closed
  ST0["Anker stage 0: herladen ruimtes reproduceren de referentie, 0,0002 µEh (18 sep)"]:::done
  ANCH["Anker M3: naftaleen cc-pVTZ, 13 energieën van 12 h; modus 12 klaar 20 sep 17:30, 22 op 22 sep, rapport 24 sep"]:::running
  D1{"Draagt DZ de TZ-correctie per familie?"}:::dec
  CHEAP["Decks in cc-pVDZ (factor 14 goedkoper per energie)"]:::todo
  TZ["Decks in cc-pVTZ; cluster nodig (Snellius-aanvraag op de agenda van 28 sep)"]:::todo
  M2["M2-bouw: gradiënt van de bevroren-ruimte-energie in JAX; pre-registratie 18 sep (T-M2-1..3, float64, checkpointing); start na 24 sep op het woord van de auteur"]:::todo
  D2{"T-M2-1 en T-M2-2 geslaagd; g_M2 gedrukt (voorspeld 2–4)"}:::dec
  DECK1["Eerste gradiëntdeck benzeen → licentie tegen canoniek"]:::todo
  DECK2["Naftaleendeck: 19 gradiënten; eerste label buiten benzeen"]:::todo
  TPORT["(T)-port voor open schil (besluit 41), acceptatietests eerst; daarna naftaleen+"]:::todo
  MEM["Geheugen: geleende gradiënt past niet op 32 GB bij plandrempels (19 sep, 3× OOM); 128 GB-machine aangevraagd"]:::closed

  M1 --> ST0 --> ANCH --> D1
  D1 -- ja --> CHEAP
  D1 -- nee --> TZ
  I14 --> X14 --> M2
  AMP --> M2
  M2B --> M2
  MEM --> M2
  M2 --> D2
  D2 -- ja --> DECK1 --> DECK2
  D2 -- nee --> M2
  CHEAP --> DECK2
  TZ --> DECK2
  DECK2 --> TPORT
```

## 6. Onderzoeksproces — het netwerk

```mermaid
%% Onderzoeksproces — pipeline A: de toetsen die beslissen of en hoe het netwerk van blad 2 er komt. Stand 20 september 2026.
%% Dit blad mag data en besluiten bevatten. Groen = geslaagd of gemeten; blauw = loopt; gestippeld = nog te doen; rood = verloren en gesloten.
flowchart LR
  linkStyle default stroke:#8a9bb0,stroke-width:2.2px
  classDef done fill:#d9f0dc,stroke:#2e7d32,color:#111
  classDef running fill:#dbe9ff,stroke:#2a5db0,color:#111
  classDef todo stroke-dasharray: 6 4,stroke:#b8860b,fill:#fff3c4,color:#111
  classDef closed fill:#f6d5d5,stroke:#a33,color:#111
  classDef dec fill:#eee,stroke:#444,color:#111

  LA["Laag A van het corpus: 45 moleculen, DFT-paren (18–19 sep, Helsinki)"]:::done
  LC1["Leercurve 1 en 2: C–H-families onder 5 cm-1 bij 5–20 moleculen; ringfamilie op 12,4, vlak; kenmerken helpen niet (19 sep)"]:::done
  E4["E4: het label per modus is voor de ringfamilie slecht gesteld (9,2 van de 12,4 is definitie); het familieblok draagt over (19 sep)"]:::done
  RULE["Regel: het doelobject is het familieblok, diagonaal + koppelingen (recipe-amendement 19 sep)"]:::done
  E1["E1/E1b/E2/E5/E5b: contrastieve embedding, atoom-encoder, molecuultokens, skip-gram op de koppelingsmatrix — alle verloren op 45 moleculen (19 sep)"]:::closed
  E6["E6 fase 1: laag A2, 200 moleculen op vier machines (sinds 19 sep 23:30; ~woensdag klaar)"]:::running
  D1{"Helling van de ringfamilie over 45 → 200 steiler dan −0,25?"}:::dec
  P2["E6 fase 2: de resterende 668 moleculen (~€160)"]:::todo
  BHH["Vervangercontrole: BHHLYP − B3LYP op benzeen en naftaleen — is de ringcorrectie van de vervanger niet-lokaal?"]:::todo
  ST1["Stap 1 van het ontwerp: equivariant paar-blokmodel leert de volledige correctiematrix uit het corpus; Test 1: ringfamilie onder 5 cm-1 op dezelfde 12 moleculen"]:::todo
  E3["E3: voorwendsel met DFT-grootheden (frequentie, familie, teken) uit ruwe atoomvelden, op het hele corpus"]:::todo
  CC["Eerste CC-labels uit pipeline B (benzeen, naftaleen; daarna de decks van M2)"]:::todo
  FT["Bijtrainen op de CC-projecties; licentie per familie tegen X18 en de mediaanregel"]:::todo
  D2{"Per familie: fout onder de marge van de scorekolom?"}:::dec
  LICF["Familie gelicentieerd in het netwerk"]:::todo
  REF["Familie geweigerd: DFT met melding; volgende label gekozen op onenigheid"]:::todo

  LA --> LC1 --> E4 --> RULE
  LC1 --> E1 --> E6
  E4 --> E6
  E6 --> D1
  D1 -- ja --> P2 --> ST1
  D1 -- nee --> BHH --> ST1
  RULE --> ST1
  E1 --> E3 --> ST1
  ST1 --> FT
  CC --> FT --> D2
  D2 -- ja --> LICF
  D2 -- nee --> REF --> CC
```
