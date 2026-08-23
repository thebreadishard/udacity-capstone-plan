# Uitleg van het Capstone-project — Leeswijzer

> **VEROUDERD SINDS 2026-08-23 — HERSCHRIJVING VOLGT.**
> Het plan is op 2026-08-23 fundamenteel omgegooid, zie
> [Overarching_Goal.md](../GoalGathering/Overarching_Goal.md) en
> [het herstructureringsvoorstel](../GoalGathering/Restructure_Proposal_2026-08-23_Project12_in_Module08.md).
> Kort: het voxel-/veldmodel is niet langer de motor voor de energie (het strijdt nu alleen nog mee
> als **dipooloppervlak**), de eigen CCSD(T)-campagnes vervallen, en het einddoel is niet meer
> H₂O-bandenveloppen maar **anharmonische bandfamilies van benoemde PAK's, met foutbudget en een
> fail-closed identificatie**. Deze hele Uitleg-serie (hoofdstuk 01 t/m 20) beschrijft nog het oude
> plan en wordt pas herschreven nadat het nieuwe plan een professor-review heeft doorstaan.

*Een verklaring van dit onderzoeksplan op het niveau van klas 6 vwo.*

---

## Voor wie is dit geschreven?

Voor iemand die wiskunde B, natuurkunde en scheikunde op vwo-6-niveau volgt, en die
wil begrijpen wat er in deze repository wordt gepland. Je hoeft geen kennis van
kunstmatige intelligentie of kwantumchemie te hebben. Alles wat je nodig hebt,
wordt in de hoofdstukken 2 tot en met 6 opgebouwd.

Je hoeft geen enkele regel programmacode te kunnen lezen.

## Hoe is dit boek opgebouwd?

Dit boek bestaat uit drie delen.

**Deel A — Het gereedschap (hoofdstuk 1 t/m 6).**
Eerst het probleem: waarom zou iemand dit onderzoek willen doen? Daarna de
natuurkunde, de scheikunde en de wiskunde die je nodig hebt. Deel A sluit af met
een beschrijving van de "motor" van het project en van de datastructuren die
overal terugkomen.

**Deel B — De twaalf projecten (hoofdstuk 7 t/m 19).**
Elk project krijgt een eigen hoofdstuk. In elk hoofdstuk staat steeds dezelfde
vaste structuur:

1. **Wat is de vraag?** — het doel van deze stap in één zin.
2. **Invoer.** — welke data gaat erin, hoe ziet die eruit, en waar komt die vandaan?
3. **Bewerking.** — wat gebeurt er met die data, stap voor stap?
4. **Uitvoer.** — welke data komt eruit, hoe ziet die eruit, en wat betekent die?
5. **Waarom deze stap?** — hoe hangt dit samen met de rest van de keten.
6. **In het kort.** — een samenvatting van een paar regels.

**Deel C — Overzicht (hoofdstuk 20).**
Eén tabel met de hele keten, plus een woordenlijst.

## Een waarschuwing vooraf

Deze repository is **geen onderzoek**. Het is een *plan* voor onderzoek. Er is nog
geen enkel molecuul doorgerekend en er is nog geen enkel model getraind. Wat hier
ligt, is de complete beschrijving van wat er gedaan gaat worden, inclusief de
regels waaraan de resultaten straks moeten voldoen.

Dat verschil is belangrijk. Als je in deze hoofdstukken leest "het model bereikt
een fout kleiner dan 1 meV/Å", dan betekent dat: *dat is de eis die vooraf is
opgeschreven*, niet: *dat is gemeten*.

## Hoofdstukoverzicht

### Deel A — Het gereedschap

| # | Bestand | Onderwerp |
|---|---|---|
| 1 | [01_Het_Probleem.md](01_Het_Probleem.md) | Moleculen in de ruimte, JWST, en waarom dit moeilijk is |
| 2 | [02_Natuurkunde_Trillingen_en_Licht.md](02_Natuurkunde_Trillingen_en_Licht.md) | Trillingen, veerkracht, golfgetallen, infrarood licht |
| 3 | [03_Scheikunde_Moleculen_en_Elektronendichtheid.md](03_Scheikunde_Moleculen_en_Elektronendichtheid.md) | Elektronenwolken, energielandschappen, CCSD(T) |
| 4 | [04_Wiskunde_Gereedschap.md](04_Wiskunde_Gereedschap.md) | Afgeleiden in meer variabelen, Fourier, statistiek |
| 5 | [05_De_Motor_Architectuur.md](05_De_Motor_Architectuur.md) | Het rooster, het neurale netwerk, de krachtenberekening |
| 6 | [06_Datastructuren_en_Pijplijn.md](06_Datastructuren_en_Pijplijn.md) | Welke bestandsvormen bestaan er en wat zit erin? |

### Deel B — De twaalf projecten

| # | Bestand | Project |
|---|---|---|
| 7 | [07_Project_01_APA.md](07_Project_01_APA.md) | 01 — Schrijven en bronvermelding |
| 8 | [08_Project_02_Data_Verkenning.md](08_Project_02_Data_Verkenning.md) | 02 — Data-analyse zonder machine learning |
| 9 | [09_Project_03_Statistiek.md](09_Project_03_Statistiek.md) | 03 — Statistische toetsing van de rekenmachine |
| 10 | [10_Project_04_Klassiek_ML.md](10_Project_04_Klassiek_ML.md) | 04 — Het eenvoudige ijkmodel |
| 11 | [11_Werkstromen_P1_en_G1.md](11_Werkstromen_P1_en_G1.md) | P1 en G1 — de twee ongewaardeerde kernstappen |
| 12 | [12_Project_05_Deep_Learning.md](12_Project_05_Deep_Learning.md) | 05 — Het vlaggenschip op benzeen |
| 13 | [13_Project_06_Generatieve_AI.md](13_Project_06_Generatieve_AI.md) | 06 — Een generator van moleculuurvormen |
| 14 | [14_Project_07_Agent.md](14_Project_07_Agent.md) | 07 — De automatische laboratoriumassistent |
| 15 | [15_Project_08_Synthese.md](15_Project_08_Synthese.md) | 08 — Alles aan elkaar knopen |
| 16 | [16_Project_09_Verdediging.md](16_Project_09_Verdediging.md) | 09 — De mondelinge verdediging |
| 17 | [17_Project_10_Grotere_Moleculen.md](17_Project_10_Grotere_Moleculen.md) | 10 — Opschalen naar grotere ringen |
| 18 | [18_Project_11_Anharmonisch_IR.md](18_Project_11_Anharmonisch_IR.md) | 11 — Echte spectra met intensiteiten |
| 19 | [19_Project_12_Identificatie.md](19_Project_12_Identificatie.md) | 12 — Herkenning in een echte sterrenkundige meting |

### Deel C — Overzicht

| # | Bestand | Onderwerp |
|---|---|---|
| 20 | [20_Totaaloverzicht_en_Woordenlijst.md](20_Totaaloverzicht_en_Woordenlijst.md) | De keten in één tabel, plus alle begrippen |

## Bronbestanden

Alles in dit boek is afgeleid uit de volgende bestanden in deze repository:

- [`README.md`](../README.md) — de samenvatting van het geheel
- [`GoalGathering/Overarching_Goal.md`](../GoalGathering/Overarching_Goal.md) — het hoofddoel
- [`GoalGathering/Distilled_Project_Plan_and_Quality_Checks.md`](../GoalGathering/Distilled_Project_Plan_and_Quality_Checks.md) — het technische plan
- [`GoalGathering/Capstone_Mapping.md`](../GoalGathering/Capstone_Mapping.md) — de verdeling over de projecten
- [`CapstoneProjects/`](../CapstoneProjects/) — de eisen per project
- [`probes/`](../probes/) — kleine rekenprogramma's die enkele beweringen narekenen

Waar een hoofdstuk een getal noemt, staat erbij uit welk bestand het komt.
