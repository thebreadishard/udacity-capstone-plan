# 01 — Trillingen, buren en afstand

**Datum:** 2026-08-27 · **Beschrijft:** de lokaliteitsmeting, eerst met een krachtveld, daarna met elektronen

In dit hoofdstuk leer je wat we meten als we vragen of een molecuul "uit losse
stukjes optelt", en waarom dat de vraag is waar dit hele project op dit moment om
draait.

---

## 1. Een trilling is een massa aan een veer

Een C–H-binding gedraagt zich als een veertje met een gewichtje eraan. Het
waterstofatoom is het gewichtje, de binding is de veer.

Voor zo'n systeem geldt de formule die je bij trillingen hebt gehad:

$$f = \frac{1}{2\pi}\sqrt{\frac{k}{m}}$$

- $k$ = veerconstante, hoe stug de binding is, in N/m
- $m$ = massa van het gewichtje, in kg
- $f$ = frequentie, in trillingen per seconde (Hz)

**Rekenvoorbeeld.** Voor een C–H-binding is $k \approx 500$ N/m en
$m \approx 1{,}6 \cdot 10^{-27}$ kg.

$$f = \frac{1}{6{,}28}\sqrt{\frac{500}{1{,}6 \cdot 10^{-27}}}
     = \frac{1}{6{,}28} \cdot 5{,}6 \cdot 10^{14}
     \approx 8{,}9 \cdot 10^{13}\ \text{Hz}$$

Bijna honderd biljoen keer per seconde.

## 2. Waarom scheikundigen cm⁻¹ gebruiken

Dat getal is onhandig groot. Daarom deel je door de lichtsnelheid:

$$\tilde\nu = \frac{f}{c} = \frac{8{,}9 \cdot 10^{13}}{3{,}0 \cdot 10^{10}}
            \approx 2965\ \text{cm}^{-1}$$

Dat is de eenheid waarin alle getallen hieronder staan. **Hoger getal = snellere
trilling.** Meer niet.

De gemeten waarde voor benzeen ligt tussen 3047 en 3080 cm⁻¹. Onze schatting zat er
dus ongeveer 3% naast, met een formule van twee regels. Dat is geen toeval: het
model klopt, alleen de details niet.

## 3. Twee veren naast elkaar duwen elkaar

Hang twee schommels naast elkaar en verbind ze met een touwtje. Duw er één aan, en
na een tijdje beweegt de andere mee. Ze zijn **gekoppeld**.

Zo werkt het ook met twee C–H-bindingen in hetzelfde molecuul. Ze zitten aan
hetzelfde koolstofskelet, dus ze voelen elkaar.

> **Definitie — koppeling**
> De koppeling is hoeveel cm⁻¹ de trilling van groep A verschuift doordat groep B
> er is.

Sterke koppeling = grote verschuiving. Geen koppeling = de twee groepen weten niets
van elkaar.

## 4. Wat we gemeten hebben

We hebben de koppeling uitgerekend tussen elk paar C–H-groepen, en gesorteerd op
**afstand**: het aantal koolstofbindingen dat je moet lopen van de één naar de
ander.

| afstand | 1 binding | 2 | 3 | 4 of meer |
|---|---:|---:|---:|---:|
| koppeling (cm⁻¹) | ≈ 9,0 | ≈ 2,2 | ≈ 0,7 | ≈ 0,3 |

Kijk naar de verhoudingen tussen de stappen:

$$\frac{9{,}0}{2{,}2} \approx 4 \qquad
  \frac{2{,}2}{0{,}7} \approx 3 \qquad
  \frac{0{,}7}{0{,}3} \approx 2$$

**Elke binding verder is de koppeling ongeveer drie tot vier keer zwakker.** Dat
werkt als een halveringsformule, alleen met factor 3 à 4 in plaats van 2.

## 5. De liniaal: 10 cm⁻¹

Dit project heeft van tevoren afgesproken hoe nauwkeurig een voorspelling moet
zijn: **binnen 10 cm⁻¹** van de meting.

Dat getal is de liniaal waarmee je alles afmeet. Alles wat kleiner is dan 10 kan een
piek niet over de grens duwen. Daarmee wordt de tabel hierboven leesbaar:

- **1 binding: 9,0** — net onder de grens. Directe buren doen mee.
- **2 bindingen: 2,2** — vijf keer onder de grens.
- **4 of meer: 0,3** — dertig keer onder de grens. Verwaarloosbaar.

Dat de grens vooraf vastligt is belangrijk. Anders kies je hem achteraf zo dat je
resultaat er goed uitziet, en dan meet je niets meer.

## 6. Vraag 1 — groeit de buurt mee met het molecuul?

Dit is de vraag waar alles om draait.

We tellen per C–H-groep hoeveel andere groepen hij *effectief* voelt. Dus niet
simpelweg hoeveel er zijn, maar meegewogen hoe sterk elk contact is. Een groep die
je nauwelijks voelt telt bijna niet mee.

| molecuul | koolstofatomen | effectief aantal buren |
|---|---:|---:|
| benzeen | 6 | 3,5 |
| naftaleen | 10 | 3,7 |
| fenantreen | 14 | 3,6 |
| pyreen | 16 | 4,1 |

Het molecuul wordt bijna drie keer zo groot, maar het aantal buren blijft rond de
3,5 à 4 hangen.

**Blijft dat zo**, dan is een groot molecuul niet moeilijker dan een klein: elk
stukje kijkt alleen naar zijn eigen omgeving, en je kunt het geheel uit stukken
opbouwen.

**Loopt het op**, dan moet je een groot molecuul altijd in zijn geheel doorrekenen —
en dat is precies wat niet kan.

⚠️ **Nog niet beslist.** Die 4,1 bij pyreen ligt hoger dan de rest. Vier punten zijn
te weinig om te zeggen of dat toeval is of het begin van een stijgende lijn. Daarom
draait er nu een langere reeks met acht moleculen.

## 7. Vraag 2 — is een stukje overdraagbaar?

Aan de rand van zo'n molecuul zitten waterstofatomen. Soms eentje alleen, soms twee
naast elkaar, soms drie of vier. Die groepjes hebben namen: **solo, duo, trio,
kwartet**.

De test is simpel: pak hetzelfde groepje in twee verschillende moleculen en kijk of
het dezelfde frequentie geeft.

Een duo in fenantreen tegenover een duo in pyreen:

- gemiddelde: **781,7 cm⁻¹**
- verschil tussen de twee moleculen: **0,7 cm⁻¹**

Verschil 0,7 tegen een liniaal van 10. **Veertien keer meer marge dan nodig.**

Dat betekent dat je een duo één keer goed kunt uitrekenen op een klein molecuul, en
dat antwoord kunt hergebruiken in een groot molecuul. Daar zit de hele winst.

⚠️ **Met één kanttekening.** Dit is voorlopig de énige eerlijke vergelijking die we
hebben. Bij de andere groepjes kwamen beide exemplaren uit hetzelfde molecuul, en
dan meet je alleen dat het molecuul symmetrisch is — wat je al wist. Dat was een
ontwerpfout in onze eigen test, en de langere reeks repareert hem.

## 8. Vraag 3 — de baai

Nu het interessantste.

Bij fenantreen zitten twee waterstofatomen die je via de ringen **drie bindingen**
uit elkaar telt. Volgens de tabel in §4 zou hun koppeling dus rond de 0,7 moeten
liggen.

Gemeten: **8,54 cm⁻¹**.

Twaalf keer te veel. Hoe kan dat?

Omdat het molecuul gekromd is. Die twee waterstoffen zitten ver uit elkaar *langs de
bindingen*, maar staan **vlak naast elkaar in de ruimte**. Ze duwen tegen elkaar
aan. Zo'n plek heet een **baai**.

Vergelijk het met een hoefijzer: de twee uiteinden liggen ver uit elkaar als je
langs het ijzer loopt, maar door de lucht zitten ze bijna tegen elkaar.

**Conclusie: afstand tellen langs de bindingen is niet genoeg.** Je moet ook naar de
vorm kijken. Een baai is een eigen soort plek en moet apart behandeld worden.

## 9. Waarom we alles nu opnieuw doen

De eerste meting gebruikte een rekenmethode die alleen met veren en massa's werkt —
precies de formule uit §1, en verder niets. Snel, maar er zitten **geen elektronen**
in.

En elektronen kunnen ook koppeling doorgeven. In deze platte moleculen zitten ze
uitgesmeerd over het hele oppervlak, als een wolk. Misschien geven ze contact door
over veel grotere afstand dan de veren doen.

Dus draaien we alles nog een keer met een methode die elektronen wél meeneemt.
**Zelfde moleculen, zelfde analyse, alleen een betere rekenmotor.** Zo komt elk
verschil door de elektronen, en niet door iets anders dat we stiekem veranderd
hebben.

Eerste uitkomst: de koppeling op grote afstand werd inderdaad 3 tot 10 keer groter.
Maar van 0,05 naar 0,4 — nog altijd ver onder de 10.

**De elektronen doen dus iets, en het is meetbaar. Maar niet genoeg om iets te
bederven.**

## 10. Samenvatting

1. Een C–H-trilling is een massa aan een veer, met een frequentie die je zelf kunt
   uitrekenen.
2. Twee van die trillingen naast elkaar beïnvloeden elkaar: koppeling.
3. Die koppeling wordt per binding ongeveer 3 à 4 keer zwakker.
4. Vanaf vier bindingen is hij dertig keer kleiner dan de nauwkeurigheid die we
   beloven, dus verwaarloosbaar.
5. Een C–H-groep voelt effectief zo'n 3,5 buren. Of dat getal meegroeit met het
   molecuul, weten we nog niet.
6. Hetzelfde randgroepje in twee verschillende moleculen geeft hetzelfde antwoord op
   0,7 cm⁻¹ na.
7. Behalve bij een baai, waar atomen door de ruimte dicht bij elkaar staan terwijl ze
   langs de bindingen ver weg zijn.

**Onthoudzin.** We meten of een molecuul optelt uit losse stukjes, of dat je hem
altijd in zijn geheel moet nemen.

---

## Waar de getallen vandaan komen

| bron | wat erin staat |
|---|---|
| [probe_band_locality_2026-08-26.ipynb](../probes/probe_band_locality_2026-08-26.ipynb) | de meting met het krachtveld, tien moleculen, met uitvoer en grafieken |
| [dft_locality_2026-08-26.py](../probes/dft_locality_2026-08-26.py) | dezelfde meting, maar met elektronen |
| [results_dft_locality/](../probes/results_dft_locality/) | één bestand per molecuul, met alle frequenties en koppelingen |
| [hardware_capability_2026-08-26.py](../probes/hardware_capability_2026-08-26.py) | hoe lang zo'n berekening duurt op deze laptop |

## Wat er nog open staat

- **Vraag 1 is niet beantwoord.** Vier punten zijn te weinig. De reeks van acht
  moleculen loopt.
- **Vraag 2 rust op één vergelijking.** Er moeten meer groepjes in twee
  verschillende moleculen voorkomen.
- **De baai is één keer gemeten, in één molecuul.** Trifenyleen heeft er drie in
  plaats van één. Als de straf drie keer zo groot wordt, is het effect echt en telt
  het gewoon op. Zo niet, dan begrijpen we het nog niet.
