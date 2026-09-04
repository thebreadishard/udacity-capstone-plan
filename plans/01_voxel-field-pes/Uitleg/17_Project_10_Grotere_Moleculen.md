# Hoofdstuk 17 — Project 10: opschalen naar grotere ringen

> **In dit hoofdstuk leer je**
> – wat *size-extensiviteit* betekent en waarom dat hier de eerste muur is;
> – waarom "meer van hetzelfde" hier niet werkt;
> – wat een theorieladder is en hoe je een goedkope methode toch verantwoord gebruikt;
> – waarom de uitkomst van de master bepaalt hoe dit project wordt ingericht.

**Geen Udacity-module.** Post-master's. Niet beoordeeld in de projecten 02 t/m 09.
**Hangt af van:** een afgeronde veld-tegen-graafvergelijking (hoofdstuk 15).
**Geeft door aan:** project 11.

---

## §17.1 Wat is de vraag?

> Kan een energielandschap **size-extensief** zijn op aromaten, terwijl het
> verankerd blijft aan CCSD(T) op systemen die daadwerkelijk uit te rekenen zijn?

> **Definitie 17.1 — Size-extensief**
> Een methode heet size-extensief als ze bruikbaar blijft naarmate het systeem
> groeit: de fout per atoom loopt niet op en de kosten groeien niet sneller dan
> ongeveer evenredig met het aantal atomen.

Dit is de eerste van drie muren tussen het masterwerk en het doel uit hoofdstuk 1.
De formulering in het plan is scherp: zonder dit project is project 11 niets meer
dan "DFT-infrarood in een mooier notitieboek".

## §17.2 Waarom meer van hetzelfde niet werkt

| Wat de master heeft | Waarom herhalen niet helpt |
|---|---|
| Eén globale kubus van $N^3$ | Geheugen en rekentijd groeien met het **volume van de doos**, niet met het aantal atomen |
| Canonieke CCSD(T)-data | Onhaalbaar voorbij een paar ringen ($N^7$, Voorbeeld 1.2) |
| Nog 5000 benzeenconfiguraties | Zegt niets over overdracht naar de volgende ring |
| Naftaleen als vooruitblik | Moet hier een **beoordeeld** onderdeel worden |

De eerste rij is het minst voor de hand liggend, dus die verdient een sommetje.

> **Voorbeeld 17.1 — Waarom een globale kubus stukloopt**
> Benzeen past in een doos van 12,8 Å, oftewel $64^3 = 262\,144$ voxels. Neem een
> PAK die in elke richting twee keer zo breed is.
>
> *Uitwerking.*
> De doos wordt $25{,}6$ Å, dus $128^3 = 2\,097\,152$ voxels: **acht keer zoveel**.
>
> Maar hoeveel atomen zijn er bij gekomen? PAK's zijn **plat**. Twee keer zo breed
> in twee richtingen betekent ongeveer vier keer zoveel atomen, niet acht keer.
>
> De kubus groeit dus sneller dan het molecuul. Sterker nog: het grootste deel van
> die acht keer meer voxels is **lege ruimte boven en onder het vlakke molecuul**.
> Je betaalt geheugen voor niets.

Vandaar het verbod dat het plan formuleert: *"Keeping a global cube after the
field lost the master's comparison"* staat op de lijst van verboden handelingen.
Een globale kubus is alleen te rechtvaardigen als de master heeft aangetoond dat
de veldvoorstelling werkelijk iets oplevert — en zelfs dan moet hij vervangen
worden door iets slimmers.

## §17.3 De theorieladder

Het kernprobleem: je hebt data nodig van moleculen die je met de gouden methode
niet kunt doorrekenen. De oplossing is een **ladder van methoden met gemeten
onderlinge fouten**.

| Trede | Methode | Waar toegepast |
|---|---|---|
| **Goud** | Canonieke CCSD(T), of een lokale variant met een **gemeten** fout ertegen | Benzeen, naftaleen, enkele gesubstitueerde ringen |
| **Werkpaard** | Lokale-correlatiemethode of range-separated methode | De grotere moleculen |
| **Optioneel: Δ-ML** | Leer het **verschil** $E_{\text{goud}} - E_{\text{goedkoop}}$ op kleine aromaten en pas het toe op grotere | Overal |

> **Definitie 17.2 — Lokale-correlatiemethode**
> CCSD(T) is zo duur omdat het alle elektronenparen in het hele molecuul aan
> elkaar koppelt. Maar correlatie is in werkelijkheid **plaatselijk**: twee
> elektronen aan weerszijden van een groot molecuul beïnvloeden elkaar nauwelijks.
> Lokale methoden benutten dat en verlagen het schaalgedrag van $N^7$ naar bijna
> lineair, tegen een kleine en te meten fout.

> **Definitie 17.3 — Δ-machine learning**
> In plaats van de energie zelf te leren, leer je het **verschil** tussen een dure
> en een goedkope methode. Dat verschil is doorgaans veel gladder en kleiner dan de
> energie zelf, dus je hebt er minder voorbeelden voor nodig.

De strenge voorwaarde: de fout van het werkpaard tegen goud wordt **per
trillingsfamilie** gepubliceerd, niet als één gemiddelde. De reden is duidelijk als
je terugdenkt aan §2.3: de C–H-strektrillingen rond 3 μm en de buigtrillingen rond
11 μm zijn fysisch heel verschillende bewegingen, en een methode kan de ene
uitstekend en de andere slecht beschrijven.

En de valkuil die het plan expliciet benoemt: een goedkope **energie** met een
onbekende fout is gewoon DFT-infrarood met extra stappen. Het verschil tussen dit
project en zomaar een goedkope berekening zit volledig in de gemeten verankering.

## §17.4 De keuze tussen veld en graaf

Hier komt de master terug als een beslissing.

| Uitkomst van hoofdstuk 15 | Wat project 10 doet |
|---|---|
| **Het veld wint** op achtergehouden trillingen en de $\pi$-elektronen van benzeen | Houd $\mathcal E[\rho]$, maar **stop met de globale kubus**. Bouw een size-extensief veld: superpositie van atoomdichtheden plus een geleerde rest, overlappende plaatselijke roosters, of meerdere resoluties tegelijk |
| **Het veld verliest of komt gelijk uit** | Het PES voor grote PAK's wordt het graafmodel, eventueel als hybride: een graaf voor de energie en een veld alleen waar delokalisatie er echt toe doet |

En dan de zin die de discipline van dit plan het scherpst laat zien:

> *"Forcing voxels to C₄₈ because they were the master's novelty is how the
> program dies of RAM."*

Vasthouden aan je eigen vondst omdat het je vondst is, is hier expliciet
verboden. Sterker: als het veld verliest en dit project weigert over te stappen,
luidt de instructie **stop** — want project 11 gaat een niet-extensief PES niet
redden.

## §17.5 De ladder van moleculen

| Stap | Molecuul | Wat wordt beoordeeld |
|---|---|---|
| 0 | Benzeen (1 ring) | Overgenomen uit de master |
| 1 | Naftaleen (2 ringen) | Overdracht: train op kleiner, evalueer hier. **Niet langer "bespreking"** |
| 2 | Antraceen of fenantreen (3 ringen) | Overdracht naar de volgende ring |
| 3 | Eén compacte vierringstructuur | Doorgaan alleen als de overdrachtsfout nog binnen het bandbudget past |

Bij elke stap hoort een controle op de **ladingstoestand**: neutraal én als kation
(een molecuul dat een elektron kwijt is). De reden is astrofysisch. In
interstellaire wolken worden PAK's door ultraviolet licht geïoniseerd, en een
geïoniseerde PAK heeft een merkbaar ander infraroodspectrum dan een neutrale.
Alleen naar neutrale moleculen bij 300 K kijken zou het verkeerde molecuul
berekenen.

## §17.6 Invoer en uitvoer

**Invoer:**

- De uitkomst van de vergelijking uit hoofdstuk 15 (bepaalt de voorstelling);
- de methodiek van [Distilled Plan §5.1](../GoalGathering/Distilled_Project_Plan_and_Quality_Checks.md) als voorouder van de theorieladder;
- gemeten rekenkosten van elke ladderrung.

**Uitvoer:**

| Product | Inhoud |
|---|---|
| Theorieladder + metingen | De gemeten fout van werkpaard tegen goud, per trillingsfamilie |
| Beslissingsnotitie | Veld, graaf of hybride — met verwijzing naar de mastervergelijking |
| Openbare dataset | Aromaten van **meerdere groottes**, met DOI en volledige herkomstkolommen |
| Overdrachtsrapport | Benzeen → naftaleen → drie ringen → vier ringen, neutraal en kation |
| Ga/niet-ga-besluit voor project 11 | |

Merk op wat het dataproduct **niet** is: nog eens 5000 benzeenkubussen. Het is een
verzameling van **verschillende groottes**, want alleen daarmee kun je aantonen
dat een methode meeschaalt.

## §17.7 Het uitgangscriterium

Na dit project mag je dit zeggen:

> Op molecuulklasse X zijn de bandrelevante fouten van het energielandschap
> gekwantificeerd tegen een gouden referentie, en de overdracht naar de volgende
> ring valt niet uit elkaar.

En dit nog **niet**:

> Chemisch nauwkeurige infraroodspectra.

Dat is project 11.

## §17.8 Verboden

Uit [`10_Size_Extensive_Aromatic_PES.md`](../GoalGathering/Horizon/10_Size_Extensive_Aromatic_PES.md):

- Trainen op PAHdb- of JWST-spectra in plaats van op een energielandschap. Dat is
  patroonherkenning, geen natuurkunde.
- Canonieke CCSD(T) voor $\mathrm{C_{48}}$ beloven.
- De globale kubus vasthouden nadat het veld de vergelijking verloren heeft.
- Dit een Udacity-module of een uitbreiding van project 08 noemen.

## In het kort

- **De muur:** een energielandschap dat meeschaalt met de molecuulgrootte, zonder de verankering aan CCSD(T) los te laten.
- Een globale kubus schaalt met het **volume** en dus slechter dan het aantal atomen: twee keer zo breed is acht keer zoveel voxels maar slechts vier keer zoveel atomen.
- De oplossing is een theorieladder — goud, werkpaard, eventueel Δ-ML — met **gemeten** onderlinge fouten per trillingsfamilie.
- De uitkomst van de master bepaalt of het veld of de graaf wordt doorontwikkeld; vasthouden aan de eigen vondst is verboden.
- De moleculenladder loopt van benzeen naar naftaleen naar drie ringen naar één vierringstructuur, steeds neutraal én als kation.
- **Uitvoer:** een dataset van meerdere groottes met DOI, een overdrachtsrapport en een besluit over project 11.
