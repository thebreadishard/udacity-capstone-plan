# Doelarchitectuur plan 05 (voor de auteurs, Nederlands; eerste versie 19 september 2026, herzien 20 september)

**Wat dit is.** Het systeem zoals het er staat als de lopende toetsen ja zeggen. Het is uitdrukkelijk *niet* het onderzoeksproces: er staan geen beslissingen in die de auteurs de komende dagen of weken nemen, geen ankerrun, geen experimentnummers, geen data. Dat proces krijgt zijn eigen blad. Rekenplaats staat er voorlopig ook niet in; die wordt later per blokje toegevoegd. Het onderzoeksproces — de toetsen die beslissen of de doelarchitectuur er komt, mét data en besluiten — staat apart op de bladen 5 en 6 (groen geslaagd, blauw loopt, gestippeld nog te doen, rood verloren en gesloten).

**Legenda (afgesproken 20 september).**

| figuur | betekenis |
|---|---|
| rechthoek | processtap: een bewerking die data omzet in andere data |
| rechthoek met ronde uiteinden (grijs) | data-object: een invoer, tussenproduct of uitkomst die door de pijplijn stroomt |
| cilinder | opslag: een verzameling die blijft bestaan en door meerdere stappen wordt gelezen of gevuld; getekend onder het data-object dat eruit komt of erin gaat; donkerder blauw = extern, niet van ons |
| ruit (groen) | poort: een toets met een vooraf vastgelegde uitkomst — door, of niet door |
| doorgetrokken rand | bestaat en is gemeten |
| gestippelde rand, gele vulling | nog niet gebouwd |
| pijl | datastroom |

Elke pijplijn begint bij een opslag → data-object en eindigt bij data-object → opslag. Bron van waarheid: de `.mmd`-bestanden in deze map (Mermaid; renderen op GitHub).

## 0. Overzicht (niveau 2)

```mermaid
%% Doelarchitectuur plan 05 — overzicht (niveau 2). Het systeem zoals het staat als de toetsen ja zeggen.
%% Rechthoek = processtap; ronde uiteinden = data-object; cilinder = opslag; ruit = poort. Gestippeld = nog niet gebouwd. Pijlen zijn datastromen.
flowchart LR
  linkStyle default stroke:#8a9bb0,stroke-width:2.2px
  classDef planned stroke-dasharray: 6 4,stroke:#b8860b,fill:#fff3c4,color:#111
  classDef ext fill:#cfd8e3,stroke:#3d5a80,color:#111
  classDef data fill:#e9ecef,stroke:#555,color:#111
  classDef gate fill:#d9f0dc,stroke:#2e7d32,color:#111
  classDef store fill:#dfe7f2,stroke:#5b7a99,color:#111

  subgraph IN [" "]
    direction TB
    MOL(["Molecuul"]):::data
    CAT[("Molecuulcatalogus: geometrieën, lading, multipliciteit")]:::store
    CAT --> MOL
  end

  subgraph B["Pipeline B: hoe één label ontstaat"]
    direction TB
    DFT["DFT-schets: Hessiaan H0, modi, frequenties, families"]
    DECK["Deck: symmetrie-geblokte verplaatsingspatronen"]
    LNO["Coupled-cluster-energieën en -gradiënten in bevroren lokale ruimtes"]
    REC["Herstel van de correctie ΔH per bandfamilie: diagonaal en koppelingen"]
    LIC1{"Licentie van het herstel tegen direct berekende referenties"}:::gate
    DFT --> DECK --> LNO --> REC --> LIC1
  end
  subgraph LB [" "]
    direction TB
    LAB1(["Label: ΔH-blokken met foutmarge per familie"]):::data
    LABELS[("Labelopslag")]:::store
    LAB1 --> LABELS
  end

  subgraph A["Pipeline A: het netwerk dat de correctie overdraagt"]
    direction TB
    PROXY(["Vervangercorrectie: volledige ΔH per molecuul"]):::data
    CORPUS[("Corpus: DFT-paren per molecuul")]:::store
    PRE["Voortraining op de vervangercorrectie"]:::planned
    NET["Netwerk: modus-tokens → ΔH-blok per familie"]:::planned
    ENS["Ensemble → onzekerheid per familie"]:::planned
    LIC2{"Licentie per bandfamilie tegen de labels; anders weigering"}:::gate
    CORPUS --> PROXY --> PRE --> NET --> ENS --> LIC2
  end
  subgraph PB [" "]
    direction TB
    PRED(["Voorspelde ΔH-blokken met onzekerheid; geweigerde families gemarkeerd"]):::data
    PREDS[("Voorspellingsopslag")]:::store
    PRED --> PREDS
  end

  subgraph S["Spectrum en score"]
    direction TB
    CORR["Gecorrigeerde krachtconstanten: H0 + ΔH op gelicentieerde blokken"]
    DIAG["Diagonalisatie → bandposities; intensiteiten en anharmoniek uit DFT"]
    SB{"Score per referentiekolom, binnen de marge van die kolom of niet"}:::gate
    CORR --> DIAG
  end
  subgraph SP [" "]
    direction TB
    SPEC(["Spectrum met foutmarge per band"]):::data
    SPECS[("Spectrumarchief")]:::store
    SPEC --> SPECS
  end
  subgraph RS [" "]
    direction TB
    RES(["Scores per band en familie"]):::data
    RESS[("Scorearchief")]:::store
    RES --> RESS
  end
  LABDB[("Laboratoriumspectra")]:::ext
  PAHDB[("PAHdb en andere voorspellers")]:::ext
  style IN fill:none,stroke:none
  style LB fill:none,stroke:none
  style PB fill:none,stroke:none
  style SP fill:none,stroke:none
  style RS fill:none,stroke:none

  MOL --> DFT
  MOL --> CORPUS
  LIC1 --> LAB1
  LABELS --> NET
  LABELS -- "foutmarge per familie" --> LIC2
  LIC2 --> PRED
  LABELS --> CORR
  PREDS --> CORR
  DFT --> CORR
  DIAG --> SPEC
  SPEC --> SB
  LABDB --> SB
  PAHDB --> SB
  SB --> RES
```

## 1. Pipeline B: hoe één label ontstaat

```mermaid
%% Doelarchitectuur — Pipeline B: hoe één label ontstaat (niveau 3).
%% Rechthoek = processtap; ronde uiteinden = data-object; cilinder = opslag (onder het data-object); ruit = poort. Gestippeld = nog niet gebouwd.
flowchart LR
  linkStyle default stroke:#8a9bb0,stroke-width:2.2px
  classDef planned stroke-dasharray: 6 4,stroke:#b8860b,fill:#fff3c4,color:#111
  classDef data fill:#e9ecef,stroke:#555,color:#111
  classDef gate fill:#d9f0dc,stroke:#2e7d32,color:#111
  classDef store fill:#dfe7f2,stroke:#5b7a99,color:#111

  subgraph IN [" "]
    direction TB
    GEO(["Molecuul: geoptimaliseerde geometrie, lading, multipliciteit"]):::data
    CAT[("Molecuulcatalogus")]:::store
    CAT --> GEO
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
  end
  style IN fill:none,stroke:none
  style OUT fill:none,stroke:none

  GEO --> H0 --> SKETCH --> SYM --> PAT --> DECK
  SKETCH --> REF --> TRANS
  DECK --> TRANS
  TRANS --> EN --> RESP
  TRANS --> GR --> RESP
  TRANS --> OPEN --> RESP
  RESP --> SOLVE --> LIC
  RESP --> BUDGET --> LIC
  LIC --> LABEL
```

## 2. Pipeline A: het netwerk dat de correctie overdraagt

```mermaid
%% Doelarchitectuur — Pipeline A: het netwerk dat de correctie overdraagt (niveau 3).
%% Rechthoek = processtap; ronde uiteinden = data-object; cilinder = opslag (onder het data-object); ruit = poort. Gestippeld = nog niet gebouwd.
flowchart LR
  linkStyle default stroke:#8a9bb0,stroke-width:2.2px
  classDef planned stroke-dasharray: 6 4,stroke:#b8860b,fill:#fff3c4,color:#111
  classDef data fill:#e9ecef,stroke:#555,color:#111
  classDef gate fill:#d9f0dc,stroke:#2e7d32,color:#111
  classDef store fill:#dfe7f2,stroke:#5b7a99,color:#111

  subgraph IN [" "]
    direction TB
    MOL(["Molecuul"]):::data
    CAT[("Molecuulcatalogus")]:::store
    CAT --> MOL
  end
  RUN["Corpusstap: twee DFT-Hessianen per molecuul, laag en hoog niveau"]
  subgraph CP [" "]
    direction TB
    PROXY(["Vervangercorrectie: volledige ΔH per molecuul"]):::data
    CORPUS[("Corpus: DFT-paren")]:::store
    CORPUS --> PROXY
  end
  TOK["Modus-tokens uit de laag-niveau-Hessiaan"]
  PRE["Voortraining op de vervangercorrectie"]:::planned
  subgraph LB [" "]
    direction TB
    LABIN(["Labels: ΔH-blokken met foutmarge"]):::data
    LABELS[("Labelopslag")]:::store
    LABELS --> LABIN
  end
  FT["Bijtrainen op de labels: kleine leersnelheid, vroeg stoppen op apart gehouden moleculen"]:::planned
  NET["Netwerk: modus-tokens → ΔH-blok per familie, diagonaal en koppelingen"]:::planned
  ENS["Ensemble → onzekerheid per familie"]:::planned
  LIC{"Licentie per familie en ladingstoestand: fout onder de marge van de scorekolom en beter dan de eenvoudige regels"}:::gate
  ACT["Keuze van het volgende te labelen molecuul: grootste onenigheid in het ensemble"]:::planned
  NEXT(["Verzoek om een label"]):::data
  subgraph OUT [" "]
    direction TB
    PRED(["Voorspelde ΔH-blokken met onzekerheid; geweigerde families gemarkeerd"]):::data
    STORE[("Voorspellingsopslag")]:::store
    PRED --> STORE
  end
  style IN fill:none,stroke:none
  style CP fill:none,stroke:none
  style LB fill:none,stroke:none
  style OUT fill:none,stroke:none

  MOL --> RUN --> CORPUS
  PROXY --> TOK --> PRE --> NET
  LABIN --> FT --> NET
  NET --> ENS --> LIC --> PRED
  ENS --> ACT --> NEXT --> CAT
```

## 3. Spectrum en score

```mermaid
%% Doelarchitectuur — Spectrum en score (niveau 3).
%% Rechthoek = processtap; ronde uiteinden = data-object; cilinder = opslag (onder het data-object); ruit = poort.
flowchart LR
  linkStyle default stroke:#8a9bb0,stroke-width:2.2px
  classDef data fill:#e9ecef,stroke:#555,color:#111
  classDef ext fill:#cfd8e3,stroke:#3d5a80,color:#111
  classDef gate fill:#d9f0dc,stroke:#2e7d32,color:#111
  classDef store fill:#dfe7f2,stroke:#5b7a99,color:#111

  subgraph IN1 [" "]
    direction TB
    DH(["ΔH-blokken: gemeten of voorspeld, per gelicentieerde familie"]):::data
    LABELS[("Labelopslag")]:::store
    PREDS[("Voorspellingsopslag")]:::store
    LABELS --> DH
    PREDS --> DH
  end
  subgraph IN2 [" "]
    direction TB
    H0(["DFT-schets van het molecuul"]):::data
    SKETCHDB[("DFT-schetsen: H0, dipoolafgeleiden, anharmonische constanten")]:::store
    SKETCHDB --> H0
  end
  SUM["Gecorrigeerde krachtconstanten: H0 + ΔH op de gelicentieerde blokken, elders H0"]
  EIG["Diagonalisatie → harmonische posities met marge per familie"]
  INT["Intensiteiten uit de DFT-dipoolafgeleiden"]
  ANH["Anharmonische verschuiving uit DFT"]
  subgraph SP [" "]
    direction TB
    SPEC(["Spectrum: banden met positie, intensiteit, marge; profiel op de resolutie van de bron"]):::data
    SPECS[("Spectrumarchief")]:::store
    SPEC --> SPECS
  end
  LABDB[("Laboratoriumspectra")]:::ext
  PAHDB[("PAHdb en andere voorspellers")]:::ext
  SB{"Score per referentiekolom: binnen de marge van die kolom of niet"}:::gate
  subgraph RS [" "]
    direction TB
    RES(["Scores per band en familie, met de vergelijking naast de opponenten"]):::data
    RESS[("Scorearchief")]:::store
    RES --> RESS
  end
  style IN1 fill:none,stroke:none
  style IN2 fill:none,stroke:none
  style SP fill:none,stroke:none
  style RS fill:none,stroke:none

  DH --> SUM
  H0 --> SUM --> EIG --> SPEC
  H0 --> INT --> SPEC
  H0 --> ANH --> SPEC
  SPEC --> SB
  LABDB --> SB
  PAHDB --> SB
  SB --> RES
```

## 4. Componenten van het netwerk

```mermaid
%% Doelarchitectuur — Componenten van het netwerk (niveau 4). Grotendeels nog niet gebouwd.
%% Rechthoek = processtap; ronde uiteinden = data-object; cilinder = opslag (onder het data-object). Gestippeld = nog niet gebouwd.
flowchart LR
  linkStyle default stroke:#8a9bb0,stroke-width:2.2px
  classDef planned stroke-dasharray: 6 4,stroke:#b8860b,fill:#fff3c4,color:#111
  classDef data fill:#e9ecef,stroke:#555,color:#111
  classDef store fill:#dfe7f2,stroke:#5b7a99,color:#111

  subgraph IN [" "]
    direction TB
    INP(["Per molecuul: modus-tokens, lading, multipliciteit"]):::data
    CORPUS[("Corpus en labelopslag")]:::store
    CORPUS --> INP
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
  end
  style IN fill:none,stroke:none
  style OUT fill:none,stroke:none

  INP --> EMB --> ENC --> BLK --> UNC --> OUTB
  ENC --> PAIR --> OUTB
```

# Onderzoeksproces (mag data en besluiten bevatten)

## 5. Onderzoeksproces — pipeline B

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

## 6. Onderzoeksproces — pipeline A

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
