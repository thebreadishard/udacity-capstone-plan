# Hoofdstuk 14 — Module 09: de verdediging

*Udacity-module "Professional Industry Defense". In de rubriek Project 8.*

---

## 1. Wat is de vraag?

Leg in vijftien minuten uit wat er is gebouwd en wat het heeft gemeten, en verdedig daarna
de keuzes, inclusief wat niet lukte, in een gesprek met een deskundige mentor.

## 2. Wat eist de school?

Een live sessie van 30 minuten met een mentor: 15 minuten presentatie en 15 minuten
discussie en verdediging, in het Engels. De presentatie gaat volledig over het
syntheseproject (module 08) en introduceert geen nieuw werk. Dia's worden sterk aangeraden;
een strakke vormgeving niet. De presentatie heeft zeven verplichte onderdelen:

1. de sector en het echte probleem, en waarom AI past;
2. het geïntegreerde systeem: wat het doet, de onderdelen, hoe data, modellen en agents
   samenwerken;
3. de integratie van minstens drie eerdere projecten: welke, wat elk bijdroeg, en waarom;
4. de belangrijkste technische beslissingen, de alternatieven en de afwegingen;
5. ethische risico's die bij *dit* systeem horen, en de genomen maatregelen;
6. evaluatie, beperkingen en risico's: haalde het systeem zijn doel, waar faalt het;
7. professionele relevantie en volgende stappen.

Beoordeeld worden structuur en helderheid, tijdbeheer, uitleg van het systeem, integratie,
onderbouwing van beslissingen, ethisch redeneren, evaluatie, reflectie, en de antwoorden
tijdens de verdediging, die moeten steunen op de eigen code, analyse en paper.

## 3. Invoer

Alles uit module 08 en de modules die het integreert:

- **De pijplijn** (versie 0.9): een molecuul erin als SMILES-tekst of als xyz-bestand met
  atoomcoördinaten, het infraroodspectrum eruit, met een certificaat (object O13 van
  hoofdstuk 6) dat per band zegt hoe goed die bekend is.
- **De pipeline show**: een metrokaart van de stations van de pijplijn met opgenomen runs en
  hun echte rekentijden, openbaar op de Spectrum Atlas.
- **De Spectrum Atlas**: de openbare catalogus van de corpusmoleculen met hun spectrum, het
  coupled-cluster-anker waar dat bestaat, en de gemeten nauwkeurigheid van het netwerk.
- **Het syntheseverslag** van module 08 en de vastgelegde beslissingen in de README van het
  plan, waaruit elke keuze is terug te halen.

## 4. Bewerking — wat er verdedigd wordt

**De integratie (onderdeel 3).** De code van module 08 leest werk uit vier eerdere modules
in: module 03 levert de laboratoriumtolerantie u_band per bandfamilie (hoofdstuk 8); module
05 levert het ΔH-netwerk dat de krachtconstanten van B3LYP corrigeert; module 06 levert
kandidaatmoleculen die buiten het corpus liggen; module 07 levert de poort waar een opdracht
tot rekenen doorheen moet. Modules 02 en 04 leveren de vergelijkingslijnen: de bestaande
voorspellingen en de gekalibreerde goedkope tegenstander. Hun uitvoer wordt niet door de
code ingelezen.

**De beslissingen en afwegingen (onderdeel 4):**

- *De correctie zit in het krachtveld, niet in een schaalfactor per band.* Module 04 liet
  zien dat een schaalfactor plus klassieke ML op bandkenmerken de resterende fout niet
  verkleint (hoofdstuk 9). Op de proxytaak laat het netwerk in elke familie minder fout over
  dan de beste schaalfactor.
- *Koppelingen in lokale coördinaten* (beslissing 49): het netwerk leert de koppelingen
  tussen trillingen per atoom en binding, niet per trilling van het hele molecuul.
- *Het eindpunt is het proxybewijs* (beslissing 63). Het netwerk leert de vorm van de
  correctie op ruim duizend moleculen tussen twee DFT-methoden (B3LYP → ωB97X). De elf
  bestaande CCSD(T)-ankers vormen de brug naar coupled cluster. Nieuwe ankers vallen tot
  juli 2027 buiten de capstone; vanaf 15 november 2026 rekent alleen de laptop nog.
- *Gemiddelde van drie zaadjes*: drie netwerken met een andere startwaarde, waarvan de
  gemiddelde correctie wordt gebruikt.

**De ethiek (onderdeel 5).** Het grootste risico is een spectrum dat er gecertificeerd
uitziet waar het netwerk geen licentie heeft. Daarom markeert het certificaat elke band:
vrijgegeven familie of niet, en of het netwerk het molecuul al eens heeft gezien. Moleculen
buiten het domein (geladen, open schil, andere elementen) worden vóór elke berekening
geweigerd, met de reden. De steward van module 07 kan geen geld uitgeven, niets verwijderen
en geen wetenschappelijk oordeel vellen.

**De evaluatie (onderdeel 6).** Een familie is vrijgegeven als de fout van het netwerk op
beide hold-outs (sets moleculen waarop nooit is getraind) binnen 3 cm⁻¹ blijft (beslissing
65). Onder versie 1.3 halen de ringtrillingen in het vlak, de C–H-strek en de C–H-buiging uit
het vlak die lijn; de familie 'other' niet (3,62 cm⁻¹ op de schone hold-out (a), 3,89 op
(b)). De licentie geldt op het niveau van de proxy (ωB97X); er bestaat geen
coupled-cluster-licentie. De posities zijn harmonisch: de anharmonische stap zit nog niet
in de pijplijn.

**Te verwachten vragen, met het voorbereide antwoord:**

- *"Is dit niet gewoon een schaalfactor?"* — Nee. Op hold-out (b) laat de beste schaalfactor
  met drie frequentiegebieden 14,2 cm⁻¹ over bij de ringtrillingen in het vlak; het netwerk
  (versie 1.1) 2,6 cm⁻¹ (hoofdstuk 9).
- *"Waarom niet meteen coupled cluster leren?"* — Er zijn elf ankers. Het netwerk leert de
  vorm van de correctie op de tussenstap, waar duizenden moleculen betaalbaar zijn; de
  ankers zijn de kalibratielaag die bepaalt wat 'goed' is (de lagen van waarheid,
  beslissing 60).
- *"Hoe weet je dat de hold-outs schoon zijn?"* — Een controle vond dat twee moleculen van
  hold-out (a) als tweeling in de trainingsset zaten. De fout op de schone set lag 0,04 tot
  0,27 cm⁻¹ hoger, en de licentie veranderde voor geen enkele familie. Sindsdien laat de
  trainer zulke tweelingen standaard weg en weigert de evaluatie een besmette testset.
- *"Is dit niet Mai 2025 met extra stappen?"* — Op het eindpunt van de capstone is ook dit
  netwerk begrensd door zijn DFT-leraar; dat zegt het certificaat. Het verschil zit in het
  certificaat per band en in de brug naar coupled cluster via de ankers, de volgende stap.

**Volgende stappen (onderdeel 7):** de ankers en de coupled-cluster-laag na juni 2027 (de
begeleider beslist hoe die worden gemaakt), de anharmonische stap in de pijplijn, en de
familie 'other' (de laagste trillingen).

## 5. Uitvoer

De dia's, de presentatie van 15 minuten en de verdediging zelf. Geen nieuw object in de
pijplijn. De dia's worden gemaakt in de schrijffase (december 2026 – februari 2027); het
inleveren van de modules valt tussen januari en juni 2027.

## 6. Waarom deze module?

Zonder verdediging is de synthese volgens de opleiding niet afgerond. Inhoudelijk is het de
plek waar de werkwijze van het project haar waarde moet bewijzen: elke lastige vraag heeft
een antwoord dat al in een vastgelegde beslissing, een pre-registratie of een resultaatbestand
staat, met het getal erbij.

## 7. Waar het kan misgaan — en wat je bij de aftekening controleert

- **De tijd.** Zeven onderdelen in vijftien minuten; het project heeft meer resultaten dan
  er passen. Kies per onderdeel één getal.
- **Wat niet lukte, hoort erin.** De familie 'other' haalt de lijn niet, er is geen
  coupled-cluster-licentie, en de anharmonische stap ontbreekt. Dat staat in de presentatie
  zoals in het paper, met de getallen.
- **De integratie eerlijk tellen.** De rubriek vraagt minstens drie eerdere projecten. Noem
  alleen wat de code van module 08 echt inleest; module 04 staat in het notebook van module
  08 als achtergrond, niet in de code.
- **Engels en leesbaar voor een leek.** De rubriek beoordeelt of ook een niet-technische
  luisteraar het probleem en het systeem begrijpt.
- **De voorbereide vragen zijn geen garantie** dat er geen vijfde komt. De veiligste
  voorbereiding is de checklist van hoofdstuk 16.

## 8. In het kort

Module 09 is een live sessie van 30 minuten met een mentor: 15 minuten presentatie in zeven
verplichte onderdelen over het syntheseproject, en 15 minuten verdediging. Verdedigd worden
de pijplijn met zijn certificaat, de integratie van modules 03, 05, 06 en 07, het
proxybewijs als eindpunt, en de licentie per familie, inclusief wat nog niet gehaald is. De
dia's komen in de schrijffase.

*Bron: [Rubrics/09](../../../Rubrics/09_Professional_Industry_Defense.md) (Presentation
Instructions en Rubric), [README.md](../README.md) beslissingen 49, 60, 63, 64 en 65,
[PIPELINE.md](../modules/PIPELINE.md),
[README.md van module 08](../modules/08_industry_synthesis/README.md),
[REVIEW_2026-10-17.md](../modules/REVIEW_2026-10-17.md),
[scale_factor_baseline_2026-10-25.md](../modules/05_support_predictor/out/scale_factor_baseline_2026-10-25.md),
[TASKS_closed.md](../TASKS_closed.md) taak 157.*
