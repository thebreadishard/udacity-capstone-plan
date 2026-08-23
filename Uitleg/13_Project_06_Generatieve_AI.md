# Hoofdstuk 13 — Project 06: een generator van molecuulvormen

> **In dit hoofdstuk leer je**
> – hoe een variational autoencoder (VAE) werkt;
> – wat een latente ruimte is en waarom die klein moet zijn;
> – waarom hier bewust goedkope, onnauwkeurige data wordt gebruikt;
> – waarom dat tóch geen inbreuk op de nauwkeurigheidsbelofte is;
> – welk ethisch risico er concreet aan verbonden is.

**Categorie in het plan:** (B) brugproject, met een (D)-tintje.
**Positie in de keten:** hangt van niets af; kan op elk moment worden gedaan.

---

## §13.1 Wat is de vraag?

De schoolopdracht: bouw een generatief model — een GAN, een VAE, een
diffusiemodel of een op transformers gebaseerde generator — laat meerdere
gegenereerde voorbeelden zien, beoordeel ze inhoudelijk, en bespreek minstens één
mislukking.

De onderzoeksvraag eronder:

> De configuraties in dit project worden bedacht met de hand: verplaats langs een
> normaaltrilling, of geef alle atomen een willekeurige thermische zet (§6.3). Dat
> zijn menselijke recepten. **Kan een model leren om zelf zinnige molecuulvormen
> voor te stellen?**

## §13.2 Invoer

**Een geheel nieuw, goedkoop verzameld bestand.**

| Kenmerk | Waarde |
|---|---|
| Moleculen | 5 tot 8 kleine aromaten die **geen benzeen** zijn: tolueen, pyridine, aniline, fenol, styreen, furaan, pyrrool |
| Aantal geometrieën | 1000 tot 2000 |
| Rekenniveau | **HF/6-31G of B3LYP/6-31G\*** — bewust goedkoop |
| Vorm | XYZ-bestanden of `.npz`, plus een manifest-CSV |
| Publicatie | Zenodo-DOI vóór het verslag een bron noemt |

Twee keuzes verdienen toelichting.

**Waarom geen benzeen?** Vanwege een schoolregel: een dataset mag niet worden
hergebruikt uit een eerder project. Benzeen is van project 05. Door hier andere
aromaten te nemen, blijven de datasets aantoonbaar gescheiden. Bijkomend
voordeel: het model leert over een bredere familie dan alleen de ene ring.

**Waarom zo'n laag rekenniveau?** Dat is de interessantste kwestie van dit
hoofdstuk, en die krijgt een eigen paragraaf.

## §13.3 Waarom goedkope data hier is toegestaan

Op het eerste gezicht lijkt dit een breuk met alles wat in hoofdstuk 3 is
afgesproken. Het hele project draait om het weren van DFT-data, en hier wordt
gewoon B3LYP gebruikt.

De oplossing zit in het onderscheid tussen **voorstellen** en **leren**.

> **De redenering ([Capstone_Mapping §5.3](../GoalGathering/Capstone_Mapping.md))**
> Het plan gebruikt zelf al drie manieren om configuraties te verzinnen:
> verplaatsing langs normaaltrillingen, willekeurige thermische verstoring, en
> starre draaiing. Geen van die drie is "chemisch nauwkeurig" — het zijn gewoon
> manieren om een **kandidaat** te bedenken. Nauwkeurig wordt het pas op het moment
> dat er een CCSD(T)-berekening op wordt losgelaten.
>
> Een geleerde generator is precies hetzelfde soort ding: een manier om een
> kandidaat te bedenken. Hij vervangt de hand-ontworpen recepten, niet de
> berekening.

Daaruit volgt één keiharde regel:

> **Verbod**
> Geen enkele door dit model gegenereerde geometrie mag in de train-, validatie-
> of testverzameling van project 04, werkstroom P1 of project 05 terechtkomen
> **zonder eerst opnieuw op CCSD(T)-niveau te zijn doorgerekend**.

Met die regel is dit project niet "een toegestane uitzondering" maar
**compliant by construction** — het valt buiten de belofte, in plaats van eronder.
Het plan draagt op dat expliciet in het verslag te zetten, zodat een lezer het
niet als een verzwakking leest.

## §13.4 Wat is een VAE?

> **Definitie 13.1 — Autoencoder**
> Een netwerk van twee delen. De **encoder** perst de invoer samen tot een korte
> code; de **decoder** probeert uit die code de oorspronkelijke invoer weer op te
> bouwen. Het netwerk wordt getraind door de invoer met de gereconstrueerde uitvoer
> te vergelijken.

> **Definitie 13.2 — Latente ruimte**
> De ruimte van die korte codes. Als de code uit 8 getallen bestaat, spreek je van
> een 8-dimensionale latente ruimte.

Omdat de code veel korter is dan de invoer, kan het netwerk niet alles onthouden.
Het wordt gedwongen te bewaren wat er werkelijk toe doet.

> **Voorbeeld 13.1**
> Tolueen $\mathrm{C_7H_8}$ heeft 15 atomen, dus 45 cartesische coördinaten.
> Hoeveel van die 45 getallen zijn werkelijk "vorm"?
>
> *Uitwerking.*
> Er gaan 6 vrijheidsgraden af voor verschuiven en draaien: $45 - 6 = 39$ interne
> vrijheidsgraden.
>
> Maar die 39 zijn niet allemaal even belangrijk. De C–C-afstanden in een
> aromatische ring variëren nauwelijks; de draaihoek van de $\mathrm{CH_3}$-groep
> juist wel. Een latente ruimte van bijvoorbeeld 8 dimensies dwingt het netwerk te
> ontdekken wélke bewegingen er echt toe doen. Dat is de eigenlijke waarde van dit
> project: het is **representatieleren**, niet zomaar plaatjes maken.

> **Definitie 13.3 — Variational autoencoder (VAE)**
> Een autoencoder waarbij de encoder geen punt in de latente ruimte teruggeeft
> maar een **kansverdeling** (een gemiddelde en een spreiding). Bij het trainen
> wordt daaruit geloot. Daardoor wordt de latente ruimte glad en aaneengesloten:
> elk punt dat je erin kiest, levert bij het decoderen een zinnig resultaat op.

Dat laatste is precies wat je nodig hebt om iets nieuws te maken. Bij een gewone
autoencoder kun je tussen twee codes in belanden en onzin krijgen; bij een VAE
levert de tussenliggende code een molecuulvorm op die ergens tussen de twee
originelen in ligt.

## §13.5 Bewerking

> **Stappenplan 13.1**
>
> **Stap 1 — Data verzamelen.** Reken voor 5 tot 8 aromaten de evenwichtsstand uit
> op HF- of B3LYP-niveau, plus verplaatsingen langs de normaaltrillingen. Dit is
> goedkoop, en het kan naast alle andere werk door.
>
> **Stap 2 — Coördinaten kiezen.** Cartesisch of intern. Bij cartesische
> coördinaten moet het model zelf ontdekken dat verschuiven en draaien er niet toe
> doen (vergelijk §10.3).
>
> **Stap 3 — VAE trainen.** Reconstructiefout plus een regularisatieterm die de
> latente ruimte glad houdt.
>
> **Stap 4 — Genereren.** Loot punten in de latente ruimte en decodeer ze. Laat
> meerdere voorbeelden zien — dit is een harde eis van de opdracht.
>
> **Stap 5 — Beoordelen.** Zijn de bindingslengtes realistisch? Is de ring nog
> vlak? Zitten de waterstofatomen aan de buitenkant?
>
> **Stap 6 — Een mislukking documenteren.** Bijvoorbeeld: twee atomen die door
> elkaar heen staan, een ring die is opengebroken, of een waterstofatoom dat aan
> niets meer vastzit.

Stap 6 is geen tegenvaller maar een eis. Een verslag dat alleen de geslaagde
voorbeelden laat zien, voldoet niet.

## §13.6 Uitvoer

| Bestand | Inhoud |
|---|---|
| `generative_ai.ipynb` | Het notitieboek met training en generatie |
| `Generative_AI_Analysis_Report.pdf` | Verslag met ethiekparagraaf |
| `requirements.txt` | Softwareversies |
| De geometriedataset | Met DOI |

Voor het onderzoek: een werkend, beoordeeld **voorstelmechanisme** dat later — in
project 10 en verder — de hand-ontworpen bemonstering kan uitbreiden.

## §13.7 De ethiekparagraaf

De opdracht vraagt om ethische overwegingen die op je eigen uitvoer slaan, niet om
algemeenheden over AI. Het plan levert een concreet en overtuigend risico:

> **Het risico**
> Een gegenereerde molecuulvorm ziet er plausibel uit maar is fysisch onmogelijk.
> Belandt zo'n vorm ongemerkt in de trainingsdata van het veldmodel, dan leert dat
> model een energielandschap met een gebied dat niet bestaat. Dat model produceert
> vervolgens spectra. Die spectra worden vergeleken met sterrenkundige metingen.
> En zo kan een verzonnen molecuulvorm uiteindelijk leiden tot een onjuiste
> bewering over wat er in het heelal zweeft.

Het plan voegt er een scherpe voorwaarde aan toe: die zin is alleen eerlijk als in
hetzelfde verslag staat dat de gegenereerde voorbeelden **niet** als leerstof zijn
gebruikt. Anders beschrijf je een risico dat je zelf loopt en doet alsof je erover
nadenkt.

## §13.8 Wat er níét gebeurt

- **Geen diffusiemodel.** Diffusiemodellen zijn momenteel het krachtigst voor het
  genereren van moleculen, maar de opdracht laat de keuze vrij en het plan kiest de
  VAE, omdat het doel representatieleren is en niet zo mooi mogelijke plaatjes.
  Diffusie mag in het verslag besproken worden, maar wordt niet gebouwd.
- **Geen benzeen.** Zie §13.2.
- **Geen levering van leerstof.** Zie §13.3.

## §13.9 Waarom deze stap?

Eerlijk gezegd is dit het project dat het verst van de kern af staat. Het plan
noemt het zelf een "brugproject": iets wat is bedacht om aan een schooleis te
voldoen, met de uitdrukkelijke voorwaarde dat het toch echt nuttig moet zijn en
geen bezigheidstherapie.

De nuttigheid zit in de toekomst. Bij water en benzeen kun je nog met de hand
bedenken welke standen je wilt doorrekenen. Bij een PAK met vier ringen en meer
dan honderd trillingen kan dat niet meer. Dan heb je een geleerd
voorstelmechanisme nodig — en dan is het handig als je er al een hebt gebouwd en
beoordeeld.

Bijkomend voordeel voor de planning: dit project hangt van niets af. Het is
daarmee het aangewezen werk voor perioden waarin er op een rekencluster gewacht
wordt.

## In het kort

- **Invoer:** 1000–2000 geometrieën van 5–8 kleine aromaten die geen benzeen zijn, op goedkoop HF- of B3LYP-niveau.
- **Bewerking:** een VAE trainen die geometrieën samenperst tot een kleine latente ruimte en er weer uit opbouwt.
- **Uitvoer:** gegenereerde molecuulvormen, een beoordeling daarvan, en minstens één gedocumenteerde mislukking.
- Goedkope data mag hier, omdat dit een **voorstelmechanisme** is en geen bron van leerstof; elke kandidaat wordt opnieuw op CCSD(T)-niveau gelabeld voordat hij ergens wordt gebruikt.
- Het ethische risico is concreet: een onwerkelijke vorm die ongemerkt een energielandschap vergiftigt.
- Dit project hangt van niets af en vult dus wachttijd zonder het kritieke pad te hinderen.
