# Hoofdstuk 16 — Checklist voor mapping Pass 6

> **Wat dit hoofdstuk is**
> Mapping Pass 6 is de aftekening van het document
> [Capstone_Mapping.md](../GoalGathering/Capstone_Mapping.md): per module de rubriek er
> nog eens naast leggen en punt voor punt vaststellen dat de beschreven bijdrage, dataset,
> code, artefact en rapport elk criterium halen — met de zwakke plekken benoemd. Passen 1–5
> van de mapping zijn geschreven; Pass 6 is in geen enkel plan ooit gedaan. Dit hoofdstuk
> zet op een rij wat je daarvoor nodig hebt en welke vragen je per module moet stellen.

---

## §16.1 Hoe je Pass 6 doet

1. Lees per module eerst het rubriekbestand in `Rubrics/` (het deel "Instructions" en de
   tabel "Rubric"), dan de module-paragraaf in de mapping (§3), dan het bijbehorende
   hoofdstuk hier (7–14).
2. Vul per module de tabel van §16.3 in: **haalt** / **haalt onder voorwaarde** (welke) /
   **haalt niet**. "Onder voorwaarde" is normaal: bijna alles wacht op een publicatie of een
   probe die nog moet komen.
3. Waar je "haalt niet" schrijft, stopt de mapping volgens haar regel 0 en gaat de vraag
   naar jou terug; er wordt geen bezigheidstherapie verzonnen om de rubriek te halen.
4. Schrijf het resultaat als §7 van de mapping ("Pass 6 — sign-off"), gedateerd. De rest
   van de mapping is bevroren; §7 toevoegen is de gedateerde notitie die de bevriezing
   toestaat.

## §16.2 Vier dingen die voor alle modules gelden

- **Datasetregel** (Rubrics/README, niet opnieuw bediscussiëren): openbaar *vóór* de module
  begint; geschikt voor academisch gebruik; niet synthetisch of AI-gegenereerd; niet
  hergebruikt uit een eerdere module. De voorbeeldlijst (Kaggle, UCI, Data.gov) is geen
  gesloten poort. Een zelf berekend corpus telt als het vóór de module met DOI is
  gepubliceerd. "Niet AI-gegenereerd" slaat op modelgegenereerde *trainingsdata*, niet op
  ab-initio-berekeningen; elk rapport zegt dat in één zin.
- **De vereiste zinnen** staan per module letterlijk in de mapping §3. Controleer dat ze
  in het rapportsjabloon van die module terechtkomen.
- **Volgorde** (mapping §6): 02 → 03 → 04; de pilotnotitie vóór het gebruik van de
  opponentkolom; 05 wacht op de corpusuitgave; 06 op de dry-run-uitgave; 07 mag vroeg
  beginnen; 08 traint niets.
- **Beslissing 7**: niets is ingeleverd; het QM9-concept wordt hernoemd of gearchiveerd. Dat
  zinnetje hoort in de provenance van module 02 en 05.

## §16.3 De checklist per module

Legenda voor de kolom "status": ✔ haalt zoals gepland; ◐ haalt onder een genoemde
voorwaarde; ✘ open vraag voor de gebruiker.

### Module 02 — opponent-atlas

| Criterium (rubriek) | Antwoord van het plan | Status | Waar te controleren |
|---|---|---|---|
| openbare tabel, ≥ 200 rijen, ≥ 5 kolommen | PAHdb v4.00, > 10⁵ bandrijen, 9 kolommen | ✔ | mapping §3 M02 |
| geen ML | alleen parseren, opschonen, figuren | ✔ | notebook-eis |
| ≥ 3 figuren | dekking per grootte/lading; 4-31G-grens; rungs; R6-kandidaten | ✔ | H7 §4 |
| provenance-zin | "berekende NASA-data, tegenstander, niet training" | ✔ | mapping §3 |
| het hernoemde concept | beslissing 7 genoemd in de provenance | ◐ hernoeming moet nog gebeuren | Goal, beslissing 7 |

### Module 03 — scorebord en u_band

| Criterium | Antwoord | Status | Waar |
|---|---|---|---|
| openbaar vóór start, ≥ 500 rijen, ≥ 6 kolommen, numeriek + groepering | PAHdb-experimenteel + NIST + PNNL; > 13 kolommen | ◐ rijenaantal natellen na samenvoegen | H8 §3–§5 |
| niet de 02-dataset | metingen versus berekeningen | ✔ | mapping §4 |
| ≥ 1 hypothesetoets, vooraf vastgelegd | matrix–gas-verschuiving = 0 per familie, tweezijdig, α vooraf | ◐ de toetsvorm moet in een gedateerd document staan vóór het samenvoegen | mapping §3 M03 |
| bronnen buiten de voorbeeldlijst | DOI's + de zin over de lijst | ✔ | Rubrics/README |
| u_band vóór de pilotnotitie | probe 2a | ◐ items 52–53, 56–57, 59 eerst lezen | probes/README 2a |
| de begeleidersvraag (R2, 6–15 µm) | Proposal §13.3 | ✘ hangt van de begeleider af | Proposal |

### Module 04 — de goedkope tegenstander

| Criterium | Antwoord | Status | Waar |
|---|---|---|---|
| dataset openbaar vóór start, niet 02/03 | koppeltabel O10 met eigen DOI (lezing 1); terugval CCCBDB / VIBFREQ1295 | ◐ DOI-uitgave moet vóór de startdatum liggen | mapping §3 M04, §4 |
| begeleid/onbegeleid verklaard | begeleid, regressie op de fout van geschaalde DFT | ✔ | H9 §3 |
| passende voorbewerking en splitsing | één-hot, schaling, **per molecuul** gesplitst | ✔ | H9 §4 |
| passende metriek + motivatie | RMSE/MAE in cm⁻¹ per familie, omdat de marge per familie is | ✔ | H9 §4 |
| ≥ 1 beperking, ≥ 1 bias + maatregel | extrapolatie naar R4–R6; spreiding gerapporteerd | ✔ | H9 §7 |
| de Q4-uitzondering verklaard | traint op labresiduen als tegenstander; recept in item 6; alleen P2/P5 | ✔ maar controleer het gebruik | Distilled §7 |
| `requirements.txt`, notebook top-down | standaard | ✔ | rubriek |

### Module 05 — de steunvoorspeller

| Criterium | Antwoord | Status | Waar |
|---|---|---|---|
| domein (beeld/tekst/reeks) en familie (CNN/RNN/Transformer) expliciet | reeks; Transformer | ✔ | H10 §3 |
| dataset openbaar vóór start, niet synthetisch, **niet hergebruikt** | Hessian QM9 + eigen B3LYP-Hessianen, eigen DOI; beslissing 7 sluit de QM9-blootstelling | ◐ corpusuitgave vóór start; de deelverzamelingsgrootte wacht op de dry-run-timing | mapping §3 M05, §4 |
| baseline + precies één verandering | geleerde tegen structurele prior bij gelijk K; al het andere gelijk | ✔ controleer dat er niets meeverandert | Distilled §5 |
| beide geëvalueerd, leercurves, vergelijking | ρ bij vast K; K tot ρ*; ≥ 3 zaadjes | ✔ | H10 §4 |
| "hoge nauwkeurigheid niet vereist" | succescriterium = de licentie | ✔ | mapping §3 M05 |
| ethiek + bias specifiek | off-distribution (QM9 ≤ 9 zware atomen); PAK-testset apart | ✔ | H10 §7 |
| lezing-2-terugval benoemd | "een andere openbare Hessiaanbron", nog niet ingevuld | ◐ benoemde schuld | Method debts |
| geen lab in het corpus | Q4 triviaal schoon | ✔ | mapping §3 |

### Module 06 — de patroonvoorsteller

| Criterium | Antwoord | Status | Waar |
|---|---|---|---|
| GAN / VAE / Transformer-generator | VAE over tweemodes-patronen, geconditioneerd op de modestructuur | ✔ | H11 §3 |
| dataset openbaar of gedocumenteerd, niet hergebruikt, niet de 05-split | dry-run-antwoordrecords, eigen DOI, **nieuwe** splits-hash, PAK-tensoren uitgesloten | ◐ uitgave vóór start | mapping §3 M06, §4 |
| voorbeelden tonen + kwalitatieve beoordeling + mislukkingen | pijldiagrammen; drie criteria (symmetrie, lokaliteit, non-redundantie); mislukte gevallen | ✔ | H11 §4 stap 5 |
| ethiek gebonden aan dit systeem | het hash-lek; voorstel ≠ meting; energiekosten | ✔ | H11 §7 |
| gegenereerde uitvoer geen dataset | alleen berekende antwoorden zijn data | ✔ | mapping §3 |
| succesmaat vooraf | K_off met/zonder voorstellen op het corpus; "wint niet" is publiceerbaar | ✔ | H11 §4 stap 6 |

### Module 07 — de campagne-officier

| Criterium | Antwoord | Status | Waar |
|---|---|---|---|
| doel, grenzen, enkel/meer-agent gemotiveerd | één conservatieve officier; alle beslissingen zijn regelcontroles | ✔ | H12 §7 |
| beslislogica, beperkt geheugen, ≥ 1 tool | zes tools; geheugen = Ladder, budget, pilotnotitie, poortuitslagen | ✔ | H12 §3 |
| logging, veiligheidsmaatregelen, diagram | elke weigering gelogd met verwijzing; diagram persona→lus→geheugen→tools→log | ✔ | H12 §4–§5 |
| ≥ 1 geobserveerde mislukking uit eigen runs | vergiftigde hash; verboden woord | ◐ moeten echte runs worden | mapping §3 M07 |
| ethiek specifiek | ten onrechte weigeren; autonomie bij B3-indiening | ✔ | H12 §7 |
| cursus-tools | "tools you already know" | ◐ controleer welk agent-raamwerk de cursus toestaat | rubriek |
| niet hergebruikt | plan-04-officier is nooit gebouwd; dit is nieuw | ✔ | mapping |

### Module 08 — synthese

| Criterium | Antwoord | Status | Waar |
|---|---|---|---|
| ≥ 3 modules geïntegreerd, traceerbaar | 02, 03, 04, 07 dragend; 05, 06 als gelabelde experimenten | ✔ | H13 §3 |
| architectuur, datastroom, aannames, grenzen | H6 §6.4; Distilled §5; de weigeringen als grenzen | ✔ | mapping §3 M08 |
| nieuw werk | CLI, certificaat, weigering, de R0–R3-metingen | ✔ | H13 §7 |
| evaluatie in realistische scenario's met mislukkingen | de rungs zelf; de fail-closed-zinnen | ✔ | Distilled §8 |
| paper 1500–2000 woorden; ≥ 2 bronnen, ≥ 1 wetenschappelijk | industrieframe; bibliografie van 60 items | ✔ | Goal |
| ethiek en governance specifiek | de officier; pre-registratie; eerlijk verliezen | ✔ | H13 |
| de R6-uitkomst als geldig resultaat | "niet bereikt, om deze gemeten reden" | ✔ | Distilled §8 |
| deadline vs. fail-closed | een module mag eerlijk fail-closed inleveren | ✔ maar gevoelig: benoemen als het gebeurt | mapping §6 |

### Module 09 — verdediging

| Criterium | Antwoord | Status |
|---|---|---|
| 15 minuten; verdedigt ontwerp, integratie, ethiek, evaluatie, relevantie | de zes te verdedigen punten en de drie voorbereide vragen | ✔ |

## §16.4 De vragen die alleen jij kunt beantwoorden

Pass 6 kan drie dingen niet zelf beslissen; ze staan hier zodat je ze niet in het
document tegenkomt zonder antwoord.

1. **Module 03, de begeleidersvraag.** Zonder een gasfase- of jet-gekoelde bron voor
   pyreen, chryseen en trifenyleen in het 6–15 µm-gebied blijven de C–C-families van R2
   onbeslisbaar door constructie. Dat is geen fout van het plan, maar het beperkt wat R2 kan
   bewijzen. Wil je de aftekening van module 03 laten afhangen van het antwoord van de
   begeleider, of tekent je af mét de onbeslisbaarheid als verwacht resultaat?
2. **Module 05, de deelverzamelingsgrootte.** Die wordt pas bepaald na de dry-run-timing.
   Als de laptop traag blijkt, kan het corpus klein worden. Is er een ondergrens waaronder
   je liever de lezing-2-terugval (een andere openbare Hessiaanbron) inzet dan een
   minicorpus?
3. **Module 07, het agent-raamwerk.** De rubriek eist "tools uit de cursus". Welk raamwerk
   dat is, staat niet in de repo. Dat moet je uit het cursusmateriaal halen voordat de
   officier wordt gebouwd.

## §16.5 Wat Pass 6 niet is

Pass 6 beoordeelt de *mapping*, niet de wetenschap. Of Δ₂ lokaal is, of de bevroren ruimte
glad is, of R1 echt onvoorwaardelijk wordt: dat zijn metingen, en die staan in de
probelijst. Als je bij het aftekenen een wetenschappelijke twijfel tegenkomt, hoort die
niet in §7 van de mapping maar in een gedateerde notitie bij de Ladder.

*Bron: [Capstone_Mapping.md](../GoalGathering/Capstone_Mapping.md) §0–§6,
[Rubrics/README.md](../../../Rubrics/README.md), de rubriekbestanden 02–09, en de
hoofdstukken 7–14 van deze uitleg.*
