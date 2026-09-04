# Uitleg van plan 05 — Leeswijzer

*Een verklaring van het Δ-probing-plan op het niveau van klas 6 vwo.*

---

## Voor wie is dit geschreven?

Voor iemand die wiskunde B, natuurkunde, scheikunde en informatica op vwo-6-niveau volgt
en wil begrijpen wat er in plan 05 wordt voorgesteld, waarom, en welke data er door de
pijplijn stroomt. Je hoeft geen kennis van kunstmatige intelligentie of kwantumchemie te
hebben. Alles wat je nodig hebt wordt in deel A opgebouwd.

Je hoeft geen programmacode te kunnen lezen. Wel wordt in hoofdstuk 6 uitgelegd hoe de
data er "van binnen" uitziet: welke lijsten, tabellen en objecten er zijn, en wat erin en
eruit gaat bij elke stap. Dat is informatica op vwo-niveau, geen programmeercursus.

## Waar dit boek over gaat, in drie zinnen

Het plan bouwt één programma: een molecuul erin, een infraroodspectrum eruit. Dat spectrum
moet aantoonbaar beter zijn dan de beste voorspelling die er nu bestaat, gemeten tegen
laboratoriumdata. De vernieuwing zit in hoe de dure, nauwkeurige berekening wordt
uitgevoerd: niet het hele molecuul opnieuw doorrekenen, maar alleen de *correctie* op een
goedkope berekening opmeten, met zo weinig mogelijk dure metingen ("probes").

## Hoe is dit boek opgebouwd?

**Deel A — Het gereedschap (hoofdstuk 1 t/m 6).**
Het probleem; de natuurkunde van trillingen; de scheikunde van goedkope en dure
berekeningen; het wiskundig gereedschap; de kern van het plan (Δ-probing); en de
datastructuren en de pijplijn.

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
één totaaloverzicht van de hele keten plus een woordenlijst.

## Wat dit boek niet is

Het is geen bindend document. De bindende tekst van plan 05 is bevroren op 4 september
2026 en staat in `GoalGathering/`; de [Ladder](../GoalGathering/Frozen_Ladder_and_Tolerances.md)
is de enige plek waar elke regel officieel staat. Als deze uitleg ergens van de Ladder
afwijkt, heeft de Ladder gelijk en moet deze uitleg worden verbeterd. Elk hoofdstuk noemt
onderaan het document waaruit het is samengevat.

## Een waarschuwing vooraf

In dit plan is **nog niets uitgevoerd**. Er bestaat geen code en er is geen enkel getal
gemeten. Overal waar hieronder een getal staat, is dat óf een afspraak (een drempel die
vooraf is vastgelegd), óf een verwachting uit de literatuur die als zodanig is gelabeld, óf
een voorbeeld om iets uit te leggen. Het plan zelf is streng op dit punt: een getal dat niet
door een script is uitgeprint, telt niet als resultaat. Houd die regel in je achterhoofd bij
het lezen.

## Inhoud

| Hoofdstuk | Bestand | Deel |
|---|---|---|
| 1 | [Het probleem](01_Het_Probleem.md) | A |
| 2 | [Natuurkunde: trillingen en licht](02_Natuurkunde_Trillingen_en_Licht.md) | A |
| 3 | [Scheikunde: goedkope en dure berekeningen](03_Scheikunde_DFT_en_Coupled_Cluster.md) | A |
| 4 | [Wiskundig gereedschap](04_Wiskunde_Gereedschap.md) | A |
| 5 | [De kern: Δ-probing](05_De_Kern_Delta_Probing.md) | A |
| 6 | [Datastructuren en de pijplijn](06_Datastructuren_en_Pijplijn.md) | A |
| 7 | [Module 02 — de opponent-atlas](07_Module_02_Opponent_Atlas.md) | B |
| 8 | [Module 03 — het lab-scorebord](08_Module_03_Scorebord.md) | B |
| 9 | [Module 04 — de goedkope tegenstander](09_Module_04_Baseline.md) | B |
| 10 | [Module 05 — de steunvoorspeller](10_Module_05_Steunvoorspeller.md) | B |
| 11 | [Module 06 — de patroonvoorsteller](11_Module_06_Patroonvoorsteller.md) | B |
| 12 | [Module 07 — de campagne-officier](12_Module_07_Campagne_Officier.md) | B |
| 13 | [Module 08 — de pijplijn als geheel](13_Module_08_Synthese.md) | B |
| 14 | [Module 09 — de verdediging](14_Module_09_Verdediging.md) | B |
| 15 | [Het bijproject en de reviews](15_Bijproject_en_Reviews.md) | C |
| 16 | [Checklist voor mapping Pass 6](16_Checklist_Mapping_Pass_6.md) | C |
| 17 | [Totaaloverzicht en woordenlijst](17_Totaaloverzicht_en_Woordenlijst.md) | C |

*Geschreven op 4 september 2026 bij de bevroren tekst van plan 05. Bron van elk hoofdstuk:
de documenten in `../GoalGathering/` en `../probes/README.md`.*
