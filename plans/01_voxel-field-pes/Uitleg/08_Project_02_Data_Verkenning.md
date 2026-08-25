# Hoofdstuk 8 — Project 02: data verkennen zonder machine learning

> **In dit hoofdstuk leer je**
> – wat de dataset QM9 is en wat erin staat;
> – wat verkennende data-analyse (EDA) inhoudt;
> – hoe je uit een bestaande dataset de conclusie trekt dat je hem *niet* kunt gebruiken;
> – waarom een "negatief" resultaat hier de bedoeling is.

**Categorie in het plan:** (A) natuurlijke aansluiting, met een (D)-tintje.
**Positie in de keten:** helemaal aan het begin; hangt van niets af.

---

## §8.1 Wat is de vraag?

De schoolopdracht luidt: verken een tabel met data, maak hem schoon, en maak
minstens drie grafieken. Er mag uitdrukkelijk **geen** machine learning aan te
pas komen.

De onderzoeksvraag die eronder ligt is scherper:

> Er bestaan al grote, openbare databanken met moleculen en hun eigenschappen.
> Waarom zou je dan zelf duizenden peperdure CCSD(T)-berekeningen gaan doen?

Het antwoord is bekend (zie hoofdstuk 3), maar in een wetenschappelijk verslag
mag je dat niet als bekend veronderstellen. Je moet het **laten zien**. Dat is
wat dit project doet.

## §8.2 Invoer

**De dataset: QM9.**

> **Definitie 8.1 — QM9**
> Een openbare databank met ongeveer 134 000 kleine organische moleculen, elk met
> maximaal negen zware atomen (C, N, O, F). Voor elk molecuul zijn de geometrie en
> een reeks eigenschappen berekend. Gepubliceerd door Ramakrishnan en anderen in
> 2014, en sindsdien de standaard-testbank voor machine learning in de chemie.

**Structuur.** Eén tabel; één rij per molecuul. De kolommen zijn onder meer:

| Kolom | Betekenis | Eenheid |
|---|---|---|
| `smiles` | Tekstcodering van de structuurformule, bijv. `CCO` voor ethanol | — |
| `mu` | Dipoolmoment (§2.5) | debye |
| `alpha` | Polariseerbaarheid: hoe makkelijk vervormt de elektronenwolk | $a_0^3$ |
| `homo`, `lumo`, `gap` | Energie van de hoogste bezette en laagste lege orbitaal, en het verschil | hartree |
| `zpve` | Nulpuntsenergie: de trillingsenergie die zelfs bij 0 K overblijft | hartree |
| `u0`, `u298`, `h298`, `g298` | Inwendige energie, enthalpie en vrije energie | hartree |
| `cv` | Warmtecapaciteit | cal/(mol·K) |

**Herkomst.** De getallen zijn níét gemeten in een laboratorium. Ze zijn berekend,
met **DFT op het niveau B3LYP/6-31G(2df,p)**. Dat is precies het niveau dat in
hoofdstuk 3 als ontoereikend werd aangewezen.

**Omvang in dit project.** Er wordt een willekeurige greep van 5000 tot 10 000
moleculen gebruikt. De schooleis is minstens 200 rijen en 5 kolommen; daar zit je
ruimschoots boven.

## §8.3 Bewerking

> **Stappenplan 8.1 — De verkenning**
>
> **Stap 1 — Inladen.** Lees de tabel in met de bibliotheek Pandas.
>
> **Stap 2 — Schoonmaken.** QM9 bevat ongeveer **3054 gemarkeerde moleculen** die
> door de makers zelf als onbetrouwbaar zijn aangemerkt: de geometrie die de
> berekening opleverde, komt niet overeen met de structuurformule waarmee is
> begonnen. Die rijen worden verwijderd. Dit is de opdracht "schrijf
> schoonmaakfuncties", maar dan met een echte reden.
>
> **Stap 3 — Beschrijven.** Bepaal per kolom het gemiddelde, de spreiding, de
> uitersten en het aantal ontbrekende waarden.
>
> **Stap 4 — Visualiseren.** Maak minstens drie grafieken, bijvoorbeeld:
> - een histogram van het dipoolmoment (met een duidelijke piek bij nul: de
>   symmetrische moleculen uit §2.5);
> - een spreidingsdiagram van de HOMO-LUMO-kloof tegen het aantal atomen;
> - een staafdiagram van het aantal moleculen per samenstelling.
>
> **Stap 5 — Concluderen.** Vergelijk het rekenniveau van QM9 met de eis van dit
> project.

Stap 5 is de eigenlijke inhoud. De redenering:

> **Voorbeeld 8.1 — Waarom QM9 niet volstaat**
> QM9 is berekend met B3LYP. De typische fout van B3LYP op reactie-energieën
> bedraagt enkele kcal/mol, en die fout is **systematisch**: hij hangt af van het
> soort binding en middelt niet uit.
>
> De eis in dit project is een fout onder 1 kcal/mol, aangetoond met een audit
> (Stappenplan 3.1). QM9 haalt die eis niet, en — belangrijker — QM9 komt niet
> eens met een foutschatting waarmee je het zou kunnen nagaan.
>
> Bovendien: QM9 bevat per molecuul precies één geometrie, namelijk de
> evenwichtsstand. Voor het leren van een heel *energielandschap* heb je juist
> duizenden **verwrongen** standen van hetzelfde molecuul nodig (§6.3). QM9 is dus
> ook qua vorm ongeschikt: het is een brede, ondiepe dataset, en dit project heeft
> een smalle, diepe nodig.

## §8.4 Uitvoer

| Bestand | Inhoud |
|---|---|
| `data_workflow.ipynb` | Het notitieboek met de schoonmaakfuncties, de beschrijvende statistiek en de grafieken |
| `module_summary.pdf` | Verslag met bronvermelding en conclusie |
| `requirements.txt` | Welke softwareversies zijn gebruikt |
| `README.md` | Uitleg bij de code |
| Een GitHub-repository | Met minstens één extra vertakking (branch) en meerdere opslagmomenten (commits) |

Maar het eigenlijke resultaat is een **argument**: een schriftelijke, met
grafieken onderbouwde motivering waarom fase 0b een eigen rekencampagne moet
starten in plaats van bestaande data te hergebruiken.

## §8.5 Twee verplichte zinnen

Het plan schrijft twee waarschuwingen voor
([Capstone_Mapping §5.4](../GoalGathering/Capstone_Mapping.md)):

1. Het verslag moet **expliciet** vermelden dat QM9 geen onderdeel is van de
   werkelijke onderzoekspijplijn en alleen voor deze verkenning is gebruikt.
2. Het moet vermelden dat het lage rekenniveau van QM9 juist de reden is dat de
   pijplijn eigen data genereert.

Zonder die zinnen zou een lezer kunnen denken dat QM9 wél als leerstof wordt
gebruikt, en dan zou de hele nauwkeurigheidsbelofte van het project onderuitgaan.

## §8.6 Waarom deze stap?

Drie redenen.

**Rubriek.** De opdracht vraagt een data-analyse zonder machine learning, en dit
is er een.

**Onafhankelijkheid.** Dit project hangt van niets af en kan meteen op dag één
beginnen, terwijl de rekenmachine nog gebouwd wordt. In de planning
([Capstone_Mapping §8.4](../GoalGathering/Capstone_Mapping.md)) is dat een van de
drie sporen die bij de start tegelijk opengaan.

**Wetenschappelijke waarde.** Het levert de gedocumenteerde motivering voor de
duurste keuze in het hele plan. Zonder dit hoofdstuk is "we rekenen alles zelf
uit op CCSD(T)-niveau" een dure aanname; met dit hoofdstuk is het een onderbouwd
besluit.

## In het kort

- **Invoer:** een greep van 5000–10 000 moleculen uit de openbare tabel QM9, met eigenschappen berekend op DFT-niveau (B3LYP).
- **Bewerking:** ongeveer 3054 door de makers gemarkeerde rijen verwijderen, beschrijvende statistiek, drie of meer grafieken.
- **Uitvoer:** een notitieboek, een verslag en vooral een onderbouwde conclusie.
- **De conclusie is negatief, en dat is de bedoeling:** QM9 is te onnauwkeurig én verkeerd van vorm (één stand per molecuul in plaats van veel standen per molecuul).
- Het verslag moet expliciet zeggen dat QM9 buiten de echte pijplijn valt.
