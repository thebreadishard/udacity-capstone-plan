# Architectuur plan 05 — stand 19 september 2026 (eerste versie; voor de auteurs, Nederlands)

Bron van waarheid: de `.mmd`-bestanden in deze map (Mermaid; renderen op GitHub en in de blog). Doorgetrokken = gemeten of bestaand; gestippeld = te bouwen; rekenplaats tussen haken; stromen zijn data. Gesloten routes staan er niet in (besluit van de auteurs, 19 september). Kationen toegevoegd 19 september, gestippeld (besluit 41: de (T)-port; R1+ naftaleen+; kationkolommen nog te benoemen). Wijzigingen gedateerd, zoals alles hier.

## 0. Overzicht (niveau 2)

```mermaid
%% Architectuur plan 05 — overzicht (niveau 2), stand 19 september 2026.
%% Doorgetrokken = gemeten/bestaat; gestippeld = te bouwen. Stromen zijn data. Rekenplaats tussen haken.
flowchart LR
  classDef planned stroke-dasharray: 6 4,stroke:#7a5c00,fill:#fff8e1
  classDef ext fill:#eef3f8,stroke:#5b7a99
  classDef data fill:#f3f3f3,stroke:#666
  classDef gate fill:#e8f5e9,stroke:#2e7d32

  MOL(["Molecuul: geometrie + lading"]):::data

  subgraph B["Pipeline B: hoe één label ontstaat  [laptop / gehuurde machine]"]
    direction TB
    DFT["DFT-schets: B3LYP/6-31G* Hessiaan H0, modi L, frequenties"]
    DECK["Deck: symmetrie-geblokte verplaatsingspatronen (2k+1 gradiënten; energieën voor de diagonaal)"]
    LNO["Bevroren lokale CC-ruimtes: LNO-CCSD(T)-energieën langs de patronen"]
    GRAD["M2: gradiënten van de bevroren-ruimte-energieën (JAX)"]:::planned
    CAT["Kationen: onbeperkte (T)-port voor open schil (besluit 41); zelfde deck; R1+ = naftaleen+"]:::planned
    REC["Herstel van de correctie ΔH per bandfamilie (diagonaal + koppelingen)"]
    LIC1{"Licentie: exact tegen direct berekende referentie (benzeen, naftaleen)"}:::gate
    DFT --> DECK --> LNO --> REC
    DECK -.-> GRAD -.-> REC
    LNO -.-> CAT -.-> REC
    REC --> LIC1
  end

  LABELS[("Labels: ΔH-blokken per molecuul, met ruis en foutmarge")]:::data

  subgraph A["Pipeline A: het netwerk dat de correctie overdraagt  [laptop / gehuurde machine]"]
    direction TB
    CORP["Corpus: DFT-paren (B3LYP, wB97X) — 45 gedaan, 868 lopend, 11.321 mogelijk"]
    PRE["Voortraining op de vervanger-ΔH (volledige matrices)"]:::planned
    NET["Netwerk: modus-tokens + lading/multipliciteit → bloktarget per familie; neutraal gelicentieerd tot er kationlabels zijn"]:::planned
    ENS["Ensemble over seeds → onzekerheid per familie"]:::planned
    LIC2{"Licentie per bandfamilie tegen de labels; anders weigering met melding"}:::gate
    CORP --> PRE -.-> NET --> ENS --> LIC2
  end

  subgraph S["Spectrum en score  [laptop]"]
    direction TB
    CORR["Gecorrigeerde krachtconstanten H0 + ΔH op gelicentieerde families; DFT elders"]
    DIAG["Diagonalisatie → bandposities; intensiteiten uit DFT-dipoolafgeleiden; anharmoniek uit DFT"]
    SPEC(["Spectrum met foutmarge per band"]):::data
    SCORE["Scorebord per referentiekolom: Pirali 0,5 · Maltseva ~1 · FEL 5–17 cm-1; kationkolommen (gas/matrix naftaleen+) nog te benoemen"]
    CORR --> DIAG --> SPEC --> SCORE
  end

  LAB[("Laboratoriumspectra: NIST/PNNL, Pirali 2009, Maltseva 2016, Lemmens 2019/2021")]:::ext
  PAHDB[("PAHdb v4.00: geschaalde DFT-spectra (vergelijking, geen oordeel)")]:::ext
  JWST(["Astronomische banden (JWST): de vraag"]):::ext

  MOL --> DFT
  MOL --> CORP
  LIC1 --> LABELS --> NET
  LABELS -. "foutmarge per familie" .-> LIC2
  LIC2 --> CORR
  DFT --> CORR
  LAB --> SCORE
  PAHDB --> SCORE
  SCORE --> JWST
```

## 1. Pipeline B: hoe één label ontstaat

```mermaid
%% Pipeline B: hoe één label ontstaat (niveau 3), stand 19 september 2026.
flowchart TB
  classDef planned stroke-dasharray: 6 4,stroke:#7a5c00,fill:#fff8e1
  classDef data fill:#f3f3f3,stroke:#666
  classDef gate fill:#e8f5e9,stroke:#2e7d32

  GEO(["Geometrie, geoptimaliseerd B3LYP/6-31G*"]):::data
  H0["Stage A: DFT-Hessiaan H0 → modi L, frequenties, families, irreps  [psi4, laptop]"]
  SYM["Symmetrieprior: koppeling alleen binnen een irrep-blok (X14, X22)"]
  PAT["Patronen: k producten → 2k+1 gradiëntrichtingen; ±q langs enkele modi voor de diagonaal"]
  REF["Referentie op x0: Pipek-Mezey LMOs + PNO-ruimtes per fragment, één keer gebouwd en verzegeld  [pyscf-forge, WSL]"]
  TRANS["Transport naar x: projectie + Löwdin (glad: 0,002–0,06 µEh)"]
  EA["E_A(x): LNO-CCSD(T) in de bevroren ruimtes  [12 h per TZ-energie, 70 min per DZ-energie]"]
  G["M2: gradiënt van E_A via JAX/PySCFAD, stop_gradient op C0, transport op de band  [te bouwen; pre-registratie 18 sep]"]:::planned
  CAT["Kationen: onbeperkte (T)-port in C voor de LNO-energieën van open-schil-systemen (besluit 41, acceptatietests eerst); benzeen+ alleen timingpunt (Jahn-Teller), naftaleen+ = R1+ met de deck van het neutrale  [te bouwen, 1–2 weken]"]:::planned
  ANCH{"Anker M3: draagt DZ de TZ-correctie? (oordeel 24 sep)"}:::gate
  SOLVE["Oplossing per familieblok: diagonaal uit energieën, koppelingen uit gradiënten (exact; ruis gedempt 0,27)"]
  NOISE["Ruisbudget: sigma per energie; quartische term uit twee amplitudes"]
  LIC{"Licentie tegen canonieke CCSD(T): benzeen 27 punten, naftaleen"}:::gate
  OUT[("Label: ΔH-blokken + foutmarge per familie, verzegeld (sha256)")]:::data

  GEO --> H0 --> SYM --> PAT
  H0 --> REF --> TRANS --> EA
  PAT --> EA
  PAT -.-> G
  TRANS -.-> G
  TRANS -.-> CAT -.-> SOLVE
  EA --> ANCH
  EA --> SOLVE
  G -.-> SOLVE
  EA --> NOISE --> SOLVE
  SOLVE --> LIC --> OUT
```

## 2. Pipeline A: het netwerk dat de correctie overdraagt

```mermaid
%% Pipeline A: het netwerk dat de correctie overdraagt (niveau 3), stand 19 september 2026.
flowchart TB
  classDef planned stroke-dasharray: 6 4,stroke:#7a5c00,fill:#fff8e1
  classDef data fill:#f3f3f3,stroke:#666
  classDef gate fill:#e8f5e9,stroke:#2e7d32

  MAN(["Manifest: 11.321 kandidaten (lagen A 45 · A2 868 · B 4.353 · C 6.055)"]):::data
  RUN["Corpusrunner: B3LYP- en wB97X-Hessiaan per molecuul (deck v1)  [gehuurde machines, shards]"]
  PROXY[("Vervanger-ΔH per molecuul: volledige matrix, gratis label")]:::data
  TOK["Modus-tokens: frequentie, familie, C/H/N/O-aandelen, lokalisatie, uit-vlak-aandeel; omgevingsklassen als diagnostiek"]
  PRE["Voortraining op vervanger-ΔH  [laptop, minuten]"]:::planned
  NET["Transformer over modi (2 lagen, breedte 64) → bloktarget per familie: diagonaal + koppelingen"]:::planned
  CC[("CC-labels uit pipeline B: benzeen, naftaleen, … (ΔH-blokken); kationlabels na de (T)-port")]:::data
  FT["Bijtrainen op CC-projecties: kleine leersnelheid, vroeg stoppen op apart gehouden moleculen"]:::planned
  ENS["Ensemble over seeds → spreiding per familie"]:::planned
  LIC{"Licentie per familie en per ladingstoestand: fout onder de marge van de scorekolom, en beter dan mediaanregel en type-overdracht (X18); neutralen eerst"}:::gate
  ACT["Actieve keuze: volgende deck waar het ensemble het oneens is"]:::planned
  PRED[("Voorspelde ΔH-blokken + onzekerheid; geweigerde families → DFT met melding")]:::data

  MAN --> RUN --> PROXY --> TOK --> PRE -.-> NET
  CC --> FT -.-> NET
  NET --> ENS --> LIC --> PRED
  ENS -.-> ACT -.-> CC
```

## 3. Spectrum en score

```mermaid
%% Spectrum en score (niveau 3), stand 19 september 2026.
flowchart LR
  classDef data fill:#f3f3f3,stroke:#666
  classDef ext fill:#eef3f8,stroke:#5b7a99

  H0(["H0 (DFT)"]):::data
  DH(["ΔH-blokken: gemeten (B) of voorspeld (A), per gelicentieerde familie"]):::data
  SUM["H = H0 + ΔH op de gelicentieerde blokken; elders H0"]
  EIG["Diagonalisatie → harmonische posities met marge per familie"]
  INT["Intensiteiten: DFT-dipoolafgeleiden (stage A)"]
  ANH["Anharmoniek: DFT-VPT2 (geen CC-anharmoniek)"]
  SPEC(["Spectrum: sticks + profiel op de resolutie van de bron"]):::data
  SB["Scorebord (module 03): per kolom een eigen marge; geen kolomwissel achteraf"]
  LAB[("NIST/PNNL 296 K · Pirali 2009 · Maltseva 2016 · Lemmens 2019/2021 · Joblin 1994/95")]:::ext
  CATLAB[("Kationen: gas- en matrixspectra van naftaleen+, kolommen door de supervisor te benoemen vóór het scoren")]:::ext
  PAHDB[("PAHdb v4.00 en ML-lijnen: naast elkaar, geen oordeel")]:::ext

  H0 --> SUM
  DH --> SUM --> EIG --> SPEC
  INT --> SPEC
  ANH --> SPEC
  SPEC --> SB
  LAB --> SB
  CATLAB -.-> SB
  PAHDB --> SB
```

## 4. Componenten van het netwerk

```mermaid
%% Componenten van het netwerk (niveau 4), stand 19 september 2026 — ontwerp, grotendeels te bouwen.
flowchart LR
  classDef planned stroke-dasharray: 6 4,stroke:#7a5c00,fill:#fff8e1
  classDef data fill:#f3f3f3,stroke:#666

  IN(["Per molecuul: M modus-tokens, plus lading en multipliciteit"]):::data
  EMB["Embedding: lineair → GELU → LayerNorm (64)"]
  ENC["Self-attention over modi: 2 lagen, 4 koppen, dropout 0,1"]
  BLK["Blokkop per familie: e_i' W e_j → diagonaal en koppelingen (gebalanceerd verlies)"]:::planned
  PAIR["Paarkop (steun-label s_ij), baseline P25-rangschikking"]
  UNC["Ensemble (5 seeds) → spreiding per familie = onzekerheid"]:::planned
  OUTB(["ΔH-blok per familie + onzekerheid"]):::data
  ALT["Alternatieve encoders op dezelfde toets: atoom-set-encoder (E1, E5); equivariant paar-blokmodel op atomen (ontwerpnotitie 19 sep)"]:::planned

  IN --> EMB --> ENC --> BLK --> UNC --> OUTB
  ENC --> PAIR
  ALT -.-> BLK
```
