# Hoofdstuk 10 — Project 04: het eenvoudige ijkmodel

> **In dit hoofdstuk leer je**
> – wat een descriptor is en waarom je een molecuul niet zomaar als coördinaten aanbiedt;
> – hoe een eenvoudig machine-learningmodel een energielandschap leert;
> – waarom het nuttig is om expres een simpel model te bouwen;
> – waar de grens ligt van deze aanpak.

**Categorie in het plan:** (A) natuurlijke aansluiting.
**Positie in de keten:** na de watercampagne; levert één van de drie ijkpunten voor fase 4.

---

## §10.1 Wat is de vraag?

De schoolopdracht: train een model met scikit-learn of PyTorch, met de nadruk op
een zorgvuldige beoordeling van de kwaliteit.

De onderzoeksvraag eronder:

> Hoe goed kom je met een **doodgewoon** model? Als een eenvoudig model met drie
> ingangsgetallen het energielandschap van water al bijna perfect leert, dan moet
> een ingewikkeld model wel heel goed zijn om zijn bestaan te rechtvaardigen.

Dit is het principe van de **nulmeting**. In [Distilled Plan §4](../GoalGathering/Distilled_Project_Plan_and_Quality_Checks.md)
staat dat er drie vergelijkingsmodellen moeten zijn, en dit is er één van:

1. een gangbaar equivariant atomistisch model (werkstroom G1, hoofdstuk 11);
2. **een eenvoudig niet-veldmodel — dit project;**
3. de klassieke harmonische Hessiaan-berekening (§4.2).

## §10.2 Invoer

**Het bestand: de descriptor-CSV van water.**

| Kenmerk | Waarde |
|---|---|
| Vorm | Eén CSV-bestand |
| Rijen | Minstens 2000, één per configuratie |
| Herkomst | De PySCF-rekencampagne van [Distilled Plan §5.1](../GoalGathering/Distilled_Project_Plan_and_Quality_Checks.md) |
| Publicatie | Zenodo-DOI, vóór het notitieboek een bron claimt |

De kolommen:

| Kolom | Rol | Betekenis |
|---|---|---|
| `config_id` | identificatie | Het nummer uit §6.2 |
| `r_OH1`, `r_OH2` | **invoer** | De twee O–H-afstanden, in Å |
| `theta_HOH` | **invoer** | De H–O–H-hoek, in graden |
| `energy_hartree` | **doel** | De CCSD(T)/cc-pVTZ-energie |
| `fx_O` … `fz_H2` | **doel** | Negen krachtcomponenten (3 atomen × 3 richtingen) |
| `derivative_kind`, `fd_step_bohr`, `derivative_uncertainty`, … | herkomst | De manifestkolommen uit §6.4 |

> **Eén campagne, twee producten**
> Dezelfde 2000 waterstanden leveren twee verschillende bestanden op: deze tabel
> (voor project 04) én driedimensionale tensoren (voor werkstroom P1, hoofdstuk 11).
> Er wordt dus niet twee keer gerekend. Maar alleen de **tabel** telt als de
> dataset van project 04; de tensoren worden nooit als schoolopdracht ingeleverd.
> Zo blijven de datasets van de projecten formeel gescheiden, zoals de schoolregels
> eisen.

## §10.3 Wat is een descriptor?

Kijk naar de invoerkolommen. Er staan drie getallen, terwijl water negen
coördinaten heeft. Dat is geen slordigheid maar een keuze.

> **Definitie 10.1 — Descriptor**
> Een descriptor is een omzetting van de ruwe atoomposities naar getallen die de
> **vorm** van het molecuul beschrijven, en die niet veranderen als je het hele
> molecuul verschuift of draait.

> **Voorbeeld 10.1**
> Leg uit waarom je een model beter drie interne coördinaten kunt geven dan negen
> cartesische.
>
> *Uitwerking.*
> Verschuif je water één ångström naar rechts, dan veranderen alle negen
> cartesische coördinaten, terwijl de energie exact gelijk blijft. Een model dat
> op cartesische coördinaten traint, moet die onveranderlijkheid dus zelf uit de
> data afleiden — en heeft daarvoor veel meer voorbeelden nodig.
>
> De twee bindingslengtes en de hoek veranderen bij verschuiven of draaien
> helemaal niet. Ze bevatten precies de informatie die de energie bepaalt, en niets
> meer: exact de drie vrijheidsgraden uit Voorbeeld 3.1.

Bekende descriptors uit de vakliteratuur zijn de **Coulomb-matrix** (voor elk
atoompaar $Z_AZ_B/R_{AB}$) en **SOAP**, dat de omgeving van elk atoom beschrijft
als een gladde wolk. Voor water volstaan de drie interne coördinaten.

**Waar de grens ligt.** Wat bij water zo mooi werkt, werkt bij benzeen niet meer.
Daar heb je 30 interne coördinaten, en welke combinaties ervan er echt toe doen,
is niet vooraf duidelijk. Handmatig descriptors ontwerpen wordt dan een
onbegonnen zaak. Dat is precies de motivering voor de projecten daarna: laat het
model de voorstelling **zelf** vinden, via een graaf (G1) of via een veld (P1 en
project 05).

## §10.4 Bewerking

> **Stappenplan 10.1**
>
> **Stap 1 — Splitsen.** Verdeel de configuraties in train, validatie en test,
> volgens het vastgelegde splitsingsbestand uit §6.4. Niet zelf opnieuw splitsen.
>
> **Stap 2 — Model kiezen.** Het plan noemt drie toegestane opties:
> - **Kernel Ridge Regressie (KRR)** — leert een gladde functie als gewogen som van
>   "gelijkenissen" met de trainingsvoorbeelden;
> - **Gaussische Procesregressie (GPR)** — vergelijkbaar, maar geeft er een
>   onzekerheidsschatting bij;
> - **een klein neuraal netwerk** — enkele lagen, met de drie descriptors als
>   ingang en de energie als uitgang.
>
> **Stap 3 — Trainen** op de trainingsdata.
>
> **Stap 4 — Beoordelen** op de testdata: RMSE van de energie in kcal/mol, RMSE van
> de kracht in meV/Å, en een grafiek van voorspeld tegen werkelijk.
>
> **Stap 5 — Fouten analyseren.** Waar zit het model er het meest naast? Bij grote
> uitwijkingen? Bij één bepaalde trilling?

Stap 5 is waar de opdracht op let: de schooleis benadrukt "zorgvuldigheid in de
beoordelingsmaten boven een hoog percentage".

> **Voorbeeld 10.2 — Hoe lees je een RMSE?**
> Stel het model haalt een energie-RMSE van $0{,}3$ kcal/mol. Wat betekent dat?
>
> *Uitwerking.*
> $0{,}3$ kcal/mol is ruim onder de grens voor chemische nauwkeurigheid (1 kcal/mol,
> §3.6). Omgerekend is dat $0{,}3 \times 350 \approx 105$ cm⁻¹.
>
> En daar zie je meteen het probleem van dit project in het klein: een model dat
> "chemisch nauwkeurig" is op energie, kan spectraal nog steeds ruim 100 cm⁻¹
> mistasten. De eis voor bandposities is 10 tot 15 cm⁻¹. Energie-nauwkeurigheid
> alleen is dus **niet genoeg** — daarom worden ook krachten en (bij P1) de
> Hessiaan meegetraind.

## §10.5 Uitvoer

| Bestand | Inhoud |
|---|---|
| `modeling.ipynb` | Het notitieboek met de hele werkwijze |
| `Machine_Learning_Analysis_Report.pdf` | Verslag met de beoordelingsmaten en de foutanalyse |
| `requirements.txt` | Softwareversies |
| De dataset-CSV | Een kopie in de inlevermap |

Voor het onderzoek is de uitvoer: **één rij in de vergelijkingstabel van fase 4**,
namelijk de kolom "eenvoudig niet-veldmodel".

## §10.6 Twee waarschuwingen uit het plan

**Waarschuwing 1 — dit is niet het veldmodel.**
[Capstone_Mapping §4.1](../GoalGathering/Capstone_Mapping.md) is er stellig over:
project 04 traint níét het model uit hoofdstuk 5. Dat is werkstroom P1. De
verleiding zou zijn om de $32^3$-tensoren plat te slaan tot een lange rij getallen
en die "ook een tabel" te noemen — en dat wordt uitdrukkelijk afgewezen. De
schoolopdracht vraagt om een tabel en een eenvoudig model, en dat is wat er komt.

**Waarschuwing 2 — de bronnenkwestie.**
De schoolopdracht noemt als toegestane bronnen Kaggle, UCI, Data.gov en
overheidsportalen. Zelf berekende data staat er niet bij. Het plan lost dat niet
op met een juridische redenering maar met een handeling: **publiceer de dataset
op Zenodo, met DOI, vóórdat het notitieboek een bron noemt.** Dan is de data
aantoonbaar openbaar beschikbaar. Het advies in het plan is kort: *"Put the link
that works."*

## §10.7 Waarom deze stap?

Omdat een vergelijking zonder ondergrens niets zegt. Stel het geavanceerde
veldmodel haalt op water een krachtfout van 0,8 meV/Å. Is dat goed? Dat hangt er
maar van af:

- haalt dit eenvoudige model 0,9 meV/Å, dan is al die complexiteit weggegooid werk;
- haalt het 15 meV/Å, dan doet het veldmodel werkelijk iets.

Zonder project 04 kun je die vraag niet beantwoorden. Dat is de reden dat het
plan dit een **verplicht** ijkpunt noemt en niet een vrijblijvende oefening.

## In het kort

- **Invoer:** een CSV met minstens 2000 waterconfiguraties: twee bindingslengtes, een hoek, de CCSD(T)-energie en negen krachtcomponenten, plus herkomstkolommen.
- **Bewerking:** een eenvoudig model (KRR, GPR of een klein netwerk) trainen op drie descriptors.
- **Uitvoer:** een getraind model, foutmaten, en het eerste ijkpunt van de driewegvergelijking.
- Een descriptor is invariant onder verschuiven en draaien; daarom drie getallen in plaats van negen.
- Deze aanpak werkt bij water maar loopt vast bij benzeen; dat motiveert de latere projecten.
- Project 04 traint nadrukkelijk **niet** het veldmodel, en de dataset moet vóór inlevering een DOI hebben.
