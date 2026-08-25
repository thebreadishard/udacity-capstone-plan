# Hoofdstuk 18 — Project 11: echte spectra met intensiteiten

> **In dit hoofdstuk leer je**
> – waarom de klassieke simulatie uit de master hier gedegradeerd wordt tot hulpmiddel;
> – wat storingsrekening voor trillingen is (VPT2) en waarom die soms stukloopt;
> – wat een Fermi-resonantie is, met een voorbeeld dat je al kent;
> – hoe een foutbudget met vier termen eruitziet, en waarom één getal niet volstaat.

**Geen Udacity-module.** Post-master's.
**Hangt af van:** project 10 (een meeschalend, verankerd energielandschap).
**Geeft door aan:** project 12.

---

## §18.1 Wat is de vraag?

> Gegeven een overdraagbaar energielandschap **en** een dipooloppervlak: welke
> methode voor de kernbeweging levert infraroodspectra op die het woord
> **nauwkeurig** mogen dragen voor grote PAK's, en tegen welk experiment wordt dat
> afgemeten?

Let op de tweede helft van die vraag. "Nauwkeurig" zonder genoemd vergelijkingspunt
betekent niets.

## §18.2 Waarom de aanpak van de master hier niet volstaat

| Wat de master doet | Wat het hier nog mag zijn |
|---|---|
| Simulatie met bevroren gewichten + Fourier van de dipoolautocorrelatie | **Alleen een controle** op de enveloppe |
| Bandposities binnen 10 tot 15 cm⁻¹ voor water en benzeen | Overgenomen als diagnose, niet als nauwkeurigheidsclaim |
| Intensiteiten als relatieve enveloppen uit de simulatie | Vervangen door een dipooloppervlak plus echte trillingsgolffuncties |
| 300 K bij constante energie | Niet de astrofysische situatie — en dat los je niet op met een langere simulatie |

De reden is fundamenteel. Een klassieke simulatie behandelt de atoomkernen als
biljartballen die de wetten van Newton volgen. In werkelijkheid zijn
trillingsniveaus **gekwantiseerd**: er zijn discrete energieniveaus, er is een
nulpuntsenergie, en de overgangen daartussen zijn wat een spectrometer meet. De
klassieke aanpak vangt de anharmoniciteit van het landschap wel, maar niet de
kwantumaard van de trilling zelf.

## §18.3 Storingsrekening voor trillingen

> **Definitie 18.1 — VPT2**
> *Vibrational Perturbation Theory, second order.* Je begint bij het harmonische
> antwoord (de parabool uit §2.8) en berekent daar correcties op met behulp van de
> **derde en vierde** afgeleiden van het energielandschap. Zo krijg je
> anharmonische bandposities, boventonen en combinatiebanden.

De gedachte is dezelfde als bij een Taylorreeks: neem meer termen mee en je
benadering wordt beter.

$$E(x) = \underbrace{\tfrac12 k x^2}_{\text{harmonisch}} + \underbrace{\tfrac16 g x^3 + \tfrac1{24} h x^4}_{\text{anharmonische correcties}} + \cdots$$

De prijs is fors.

> **Voorbeeld 18.1 — Hoeveel afgeleiden zijn er nodig?**
> Voor een molecuul met $N$ normaaltrillingen heb je ongeveer $N^3/6$ unieke derde
> afgeleiden nodig. Bereken dat voor benzeen en voor pyreen $\mathrm{C_{16}H_{10}}$
> (26 atomen, een vierringstructuur).
>
> *Uitwerking.*
> Benzeen: $N = 30$, dus $30^3/6 = 4500$ derde afgeleiden.
> Pyreen: $26$ atomen geeft $N = 3\cdot26 - 6 = 72$, dus $72^3/6 \approx 62\,000$.
>
> Elk van die afgeleiden vraagt meerdere evaluaties van het energielandschap. Met
> canonieke CCSD(T) is dat volstrekt onmogelijk — en dat is precies waarom dit
> project pas kán bestaan nadat project 10 een **snel** en toch verankerd landschap
> heeft opgeleverd.

## §18.4 Wanneer storingsrekening stukloopt

Storingsrekening werkt zolang de correcties klein zijn ten opzichte van de
afstand tussen de energieniveaus. Liggen twee niveaus toevallig vrijwel gelijk,
dan komt er een bijna-nul in de noemer en explodeert het antwoord.

> **Definitie 18.2 — Fermi-resonantie**
> Twee trillingstoestanden met bijna dezelfde energie en dezelfde symmetrie
> beïnvloeden elkaar sterk. Ze "duwen" uit elkaar en verdelen hun intensiteit.
> Wat één piek had moeten zijn, wordt een dubbelpiek.

> **Voorbeeld 18.2 — De klassieke Fermi-resonantie**
> Koolstofdioxide heeft een symmetrische strek bij ongeveer 1333 cm⁻¹, en de
> buigtrilling zit op ongeveer 667 cm⁻¹. Wat is de eerste boventoon van de
> buigtrilling, en wat gebeurt er?
>
> *Uitwerking.*
> $$2 \times 667 = 1334\ \mathrm{cm^{-1}}.$$
> Dat ligt op één golfgetal van de symmetrische strek. De twee toestanden gaan
> resoneren en er ontstaat een dubbelpiek rond 1285 en 1388 cm⁻¹ — een verschijnsel
> dat al sinds de jaren dertig bekendstaat als de Fermi-dublet van $\mathrm{CO_2}$.
>
> Een storingsrekening die deze twee toestanden als onafhankelijk behandelt, geeft
> hier onzin. En dit is nog een klein, symmetrisch molecuul. In een PAK met
> tientallen ringtrillingen die dicht op elkaar liggen, gebeurt dit voortdurend.

Vandaar de **G** in de methode:

> **Definitie 18.3 — GVPT2**
> *Generalized* VPT2. De resonerende toestandsparen worden uit de storingsrekening
> gehaald en apart, exact, behandeld; de rest gaat gewoon door de storingsrekening.

Werkt zelfs dat niet, dan is de voorgeschreven volgende stap **selectieve VCI**
(*vibrational configuration interaction*): een variationele methode die de
trillingsgolffunctie rechtstreeks opbouwt uit een verzameling basisfuncties.
Duurder, maar betrouwbaarder.

Het plan voegt een instructie toe die je inmiddels herkent: escaleren doe je door
naar een betere methode voor de kernbeweging te gaan, **niet** door langer
klassiek te simuleren.

## §18.5 Intensiteiten

Voor de bandposities heb je alleen het energielandschap nodig. Voor de
**intensiteiten** heb je meer nodig.

> **Definitie 18.4 — Dipooloppervlak (DMS)**
> Net zoals het PES de energie geeft als functie van de kernposities, geeft het
> dipooloppervlak het dipoolmoment als functie van de kernposities:
> $\boldsymbol\mu(\mathbf R)$.

Uit het dipooloppervlak plus de trillingsgolffuncties volgen de relatieve
bandsterktes, volgens Eigenschap 2.3.

Wat er **niet** mag:

- absolute lijnlijsten met $|\langle f|\boldsymbol\mu|i\rangle|^2$ per overgang — dat
  is een eigen onderzoeksveld, en het plan zegt: sluip ze niet de titel in;
- intensiteiten zonder dipooloppervlak.

Wat er wél bij hoort: de restintensiteit van verboden trillingen (§2.5) en het
verschil in intensiteit tussen neutrale en geïoniseerde moleculen.

## §18.6 Eén experimenteel ijkpunt, en dat wordt bevroren

Per bewering wordt precies één genoemde standaard gebruikt:

| Voorkeur | Standaard | Voorwaarde |
|---|---|---|
| 1 | Gasfase-FTIR waar die bestaat | Dezelfde regel als bij benzeen in de master |
| 2 | NASA PAHdb, matrix-geïsoleerde banden | **Plus** een expliciet verschuivingsmodel |

> **Definitie 18.5 — Matrixverschuiving**
> Bij matrix-isolatie wordt een molecuul opgesloten in bevroren edelgas bij
> ongeveer 10 K. De omringende atomen beïnvloeden de trillingen en verschuiven de
> banden 2 tot 15 cm⁻¹ ten opzichte van een vrij zwevend molecuul.

Die verschuiving is van dezelfde orde als de gewenste nauwkeurigheid. Er zijn
daarom twee harde regels:

1. Meng nooit ongecorrigeerde matrixwaarden met gasfasewaarden in één vergelijking.
2. Stel het verschuivingsmodel **niet** bij om een match te forceren. Het model
   wordt bevroren en gaat ongewijzigd door naar project 12.

## §18.7 Het foutbudget met vier termen

Dit is de belangrijkste eis van het hele project.

> **Regel**
> Zonder foutbudget is het woord "nauwkeurig" verboden. En één samenvattend getal
> — "wij zitten binnen 5 cm⁻¹" — geldt als een **onvoldoende**.

| Term | Wat het is | Hoe gemeten |
|---|---|---|
| **A** | Fout van het geleerde landschap tegen de gouden trede van project 10 | Op achtergehouden configuraties |
| **B** | Fout van die gouden trede tegen een nog hogere referentie | Waar berekenbaar |
| **C** | Fout van de kernbewegingsmethode | GVPT2 tegen VCI, of tegen het experiment |
| **D** | Omgevingsfout | Het matrixverschuivingsmodel, indien gebruikt |

De reden dat dit ertoe doet: stel een berekende band ligt 12 cm⁻¹ naast de
meting. Zonder budget weet je niet of dat komt door het model (A), door de
kwantumchemie (B), door de trillingsmethode (C) of doordat het experiment in
bevroren argon is gedaan (D). Zonder dat onderscheid weet je ook niet wat je zou
moeten verbeteren, en dan is het getal wetenschappelijk onbruikbaar.

Merk op dat dit dezelfde discipline is als de drieledige foutsplitsing in §16.3,
maar dan met een vierde term omdat er nu een experimentele omgeving in het spel is.

## §18.8 Invoer, bewerking en uitvoer

**Invoer:**

- Het bevroren, meeschalende energielandschap uit project 10;
- een gedocumenteerd dipooloppervlak;
- één bevroren experimentele standaard per bewering.

**Bewerking:**

> **Stappenplan 18.1**
> 1. Bereken uit het landschap de Hessiaan en de derde en semi-diagonale vierde afgeleiden.
> 2. Voer GVPT2 uit; behandel resonanties apart.
> 3. Escaleer naar selectieve VCI waar GVPT2 het niet aankan.
> 4. Bereken de intensiteiten uit het dipooloppervlak en de trillingsgolffuncties.
> 5. Vergelijk met de bevroren standaard.
> 6. Stel het foutbudget A–D op, naast elke bewering in cm⁻¹.
> 7. Draai de klassieke simulatie erbij, maar uitsluitend als bijlage-diagnose.

**Uitvoer:**

| Product | Inhoud |
|---|---|
| Anharmonische spectra | Per beoordeelde grootte en ladingstoestand |
| Foutbudgettabel | A tot en met D, naast elke claim |
| Diagnosebijlage | De klassieke enveloppen, uitdrukkelijk niet de score |
| Ga/niet-ga voor project 12 | Alleen als de bandfamilies stabiel genoeg zijn |

## §18.9 Wat je dan mag zeggen

Wel:

> Anharmonische bandcentra voor [genoemde PAK-groottes en ladingstoestanden] binnen
> een **genoemd** aantal cm⁻¹ van [genoemde dataset], met een gepubliceerd
> foutbudget van vier termen. De relatieve intensiteiten van de diagnostische
> bandfamilies worden gereproduceerd binnen een genoemde tolerantie.

Niet:

- chemisch nauwkeurige rovibrationele lijnlijsten;
- nauwkeurigheid onder één golfgetal uit een klassieke simulatie;
- "willekeurige grootte";
- identificatie in een astronomische bron — dat is project 12.

Het plan vat dat samen als "chemisch nauwkeurig **genoeg voor PAK-bandidentificatie**",
en merkt op dat dát is wat de horizon werkelijk nodig heeft.

## In het kort

- **De muur:** de kernbeweging kwantummechanisch behandelen in plaats van klassiek.
- De klassieke simulatie uit de master wordt hier gedegradeerd tot een controle op de enveloppe.
- GVPT2 gebruikt derde en vierde afgeleiden van het landschap; het aantal daarvan groeit als $N^3$, wat een snel landschap onmisbaar maakt.
- Resonanties — zoals de bekende Fermi-dublet van $\mathrm{CO_2}$ — breken gewone storingsrekening; die worden apart behandeld, desnoods met VCI.
- Intensiteiten vragen een expliciet dipooloppervlak; lijnlijsten blijven buiten bereik.
- Eén bevroren experimentele standaard per bewering, en een matrixverschuivingsmodel dat nooit wordt bijgesteld om een match te forceren.
- Zonder foutbudget van vier termen is het woord "nauwkeurig" verboden.
