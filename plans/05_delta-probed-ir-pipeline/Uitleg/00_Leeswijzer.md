# Uitleg van plan 05 — Leeswijzer

*Een verklaring van plan 05 op het niveau van klas 6 vwo.*

---

## Voor wie is dit geschreven?

Voor iemand die wiskunde B, natuurkunde, scheikunde en informatica op vwo-6-niveau volgt
en wil begrijpen wat er in plan 05 is gebouwd en gemeten, waarom, en welke data er door de
pijplijn stroomt. Je hoeft geen kennis van kunstmatige intelligentie of kwantumchemie te
hebben. Alles wat je nodig hebt wordt in deel A opgebouwd.

Je hoeft geen programmacode te kunnen lezen. Wel wordt in hoofdstuk 6 uitgelegd hoe de
data er "van binnen" uitziet: welke lijsten, tabellen en objecten er zijn, en wat erin en
eruit gaat bij elke stap. Dat is informatica op vwo-niveau, geen programmeercursus.

## Waar dit boek over gaat, in drie zinnen

Het project bouwt één programma: een molecuul erin, zijn infraroodspectrum eruit, met een
certificaat dat per band zegt hoe goed die bekend is. Het programma rekent het molecuul eerst
goedkoop door met DFT en verbetert daarna de veerconstanten met een neuraal netwerk, dat de
correctie naar een beter rekenniveau heeft geleerd op 750 moleculen uit een eigen verzameling
van ruim 1.200. Dat dit werkt is aangetoond tussen twee DFT-methoden, op moleculen die het
netwerk nooit zag (drie van de vier bandfamilies blijven binnen 3 cm⁻¹), en elf
coupled-clusterberekeningen, de "ankers", vormen de brug naar de gouden standaard.

## Hoe is dit boek opgebouwd?

**Deel A — Het gereedschap (hoofdstuk 1 t/m 6).**
Het probleem; de natuurkunde van trillingen; de scheikunde van goedkope en dure
berekeningen; het wiskundig gereedschap; de kern van het plan (het idee van Δ-probing en de
geleerde correctie die eruit is gegroeid); en de datastructuren en de pijplijn.

**Deel B — De modules van de opleiding (hoofdstuk 7 t/m 14).**
Het plan wordt uitgevoerd als acht opeenvolgende Udacity-modules (02 t/m 09). Elke module
krijgt een eigen hoofdstuk met steeds dezelfde vaste indeling:

1. **Wat is de vraag?** — het doel van deze module in één zin.
2. **Wat eist de school?** — de rubriek in gewone taal: wat moet er worden ingeleverd en
   waarop wordt beoordeeld.
3. **Invoer.** — welke objecten, lijsten of tabellen gaan erin, met hun velden, en waar
   komen ze vandaan?
4. **Bewerking.** — wat gebeurt er met die data, stap voor stap?
5. **Uitvoer.** — welke objecten komen eruit, met hun velden, en wie gebruikt ze daarna?
6. **Waarom deze module?** — welk deel van de pijplijn zou stilvallen zonder haar.
7. **Waar het kan misgaan.** — de punten waar de rubriek en het plan elkaar kunnen bijten,
   en wat je bij de aftekening ("mapping Pass 6") moet controleren.
8. **In het kort.**

Modules 04 t/m 08 krijgen extra aandacht bij punt 3 en 5, omdat daar de datastructuren
het meest bepalend zijn.

**Deel C — Overzicht (hoofdstuk 15 t/m 17).**
Het bijproject en de reviewgeschiedenis; een checklist voor de aftekening van de mapping;
één totaaloverzicht van de hele keten, de lessen uit de praktijk en een woordenlijst.

## Wat dit boek niet is

Het is geen bindend document. De bindende tekst van plan 05 is bevroren op 4 september
2026 en staat in `GoalGathering/`; de [Ladder](../GoalGathering/Frozen_Ladder_and_Tolerances.md)
is de plek waar elke regel officieel staat. Wat daarna is besloten, staat als genummerde
besluiten in de [README van plan 05](../README.md). Als deze uitleg ergens afwijkt van de
Ladder of van een besluit, hebben die gelijk en moet deze uitleg worden verbeterd. Elk
hoofdstuk noemt onderaan de documenten waaruit het is samengevat.

## Een waarschuwing vooraf

Plan 05 is uitgevoerd. Er is code, er zijn duizenden berekeningen gedaan en er is veel
gemeten. Elk getal in dit boek komt uit een runlog, een resultaatbestand of een bron, en elk
hoofdstuk noemt onderaan waar het vandaan komt. Een getal dat niet door een script is
uitgeprint, telt niet als resultaat. Daarnaast staan er afspraken in (drempels die vooraf
zijn vastgelegd, zoals de 3 cm⁻¹ per familie) en voorbeelden om iets uit te leggen; die
worden als zodanig genoemd.

Let bij elk getal op twee dingen. Het eerste is het niveau. De meeste metingen vergelijken
twee DFT-methoden met elkaar; dat heet het proxyniveau. Een getal dat tegen coupled cluster
is gemeten, staat er als zodanig bij. Het tweede zijn de moleculen. Een fout van het netwerk
telt alleen op moleculen die het netwerk nooit heeft gezien.

Wordt een meting door een betere vervangen, dan wordt de tekst herschreven. De oude versie
staat in de git-geschiedenis van het bestand.

## Inhoud

| Hoofdstuk | Bestand | Deel |
|---|---|---|
| 1 | [Het probleem](01_Het_Probleem.md) | A |
| 2 | [Natuurkunde: trillingen en licht](02_Natuurkunde_Trillingen_en_Licht.md) | A |
| 3 | [Scheikunde: goedkope en dure berekeningen](03_Scheikunde_DFT_en_Coupled_Cluster.md) | A |
| 4 | [Wiskundig gereedschap](04_Wiskunde_Gereedschap.md) | A |
| 5 | [De kern: de geleerde correctie](05_De_Kern_Delta_Probing.md) | A |
| 6 | [Datastructuren en de pijplijn](06_Datastructuren_en_Pijplijn.md) | A |
| 7 | [Module 02 — de opponent-atlas](07_Module_02_Opponent_Atlas.md) | B |
| 8 | [Module 03 — het lab-scorebord](08_Module_03_Scorebord.md) | B |
| 9 | [Module 04 — de goedkope tegenstander](09_Module_04_Baseline.md) | B |
| 10 | [Module 05 — de ΔH-voorspeller](10_Module_05_Steunvoorspeller.md) | B |
| 11 | [Module 06 — de kandidatenvoorsteller](11_Module_06_Patroonvoorsteller.md) | B |
| 12 | [Module 07 — de run steward](12_Module_07_Campagne_Officier.md) | B |
| 13 | [Module 08 — de pijplijn als geheel](13_Module_08_Synthese.md) | B |
| 14 | [Module 09 — de verdediging](14_Module_09_Verdediging.md) | B |
| 15 | [Het bijproject en de reviews](15_Bijproject_en_Reviews.md) | C |
| 16 | [Checklist voor mapping Pass 6](16_Checklist_Mapping_Pass_6.md) | C |
| 17 | [Totaaloverzicht en woordenlijst](17_Totaaloverzicht_en_Woordenlijst.md) | C |

*Eerste versie 4 september 2026, bij de bevroren tekst van plan 05; deze versie beschrijft de stand van 3 november 2026 (zie het
wijzigingslog hieronder).*

## Wijzigingslog

De Uitleg wordt bijgewerkt door herschrijven, niet door stapelen: de leerling leest de stand van nu. De geschiedenis staat hier en in de
git-geschiedenis van elk bestand.

| Datum | Wat | Waar |
|---|---|---|
| 4 september 2026 | eerste versie, bij de bevroren tekst van plan 05 | alle |
| 12 september 2026 | aanvullingen: basisset (besluit 33), drempellijn (besluit 20), stand module 05, twee lessen | 3, 5, 10, 17 |
| 25 september 2026 | hoofdstukken 10, 11 en 12 herschreven (eigen corpus in lagen, kandidatenvoorsteller, run steward); de lezing "het paarmodel respecteert de symmetrie niet" teruggenomen; aanvullingen in 3, 5, 6 en 17 | 3, 5, 6, 10, 11, 12, 17 |
| 3 november 2026 | nieuwe versie naar de stand van nu, zonder gedateerde kaders: hoofdstukken 0, 1, 5, 6, 10, 11, 13 en 17 herschreven; 2–4, 7–9, 12 en 14–16 nagelopen en waar nodig verbeterd | alle |

*Bron: de documenten in `../GoalGathering/`, de besluiten in de [README](../README.md), en de overzichten
[PIPELINE.md](../modules/PIPELINE.md), [MODELS.md](../modules/MODELS.md) en [ANCHORS.md](../modules/ANCHORS.md).*
