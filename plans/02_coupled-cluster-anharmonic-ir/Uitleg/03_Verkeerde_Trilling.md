# 03 — Ik keek naar de verkeerde trilling

**Datum:** 2026-08-27 · **Beschrijft:** de controle tegen echte metingen, en wat daarbij omviel

Dit hoofdstuk corrigeert hoofdstuk 01. Volgens regel 3 uit de leeswijzer blijft dat
hoofdstuk gewoon staan: wat je dacht en waarom je het bijstelde is onderdeel van het
verhaal.

Er gingen drie dingen om. Het derde was mijn eigen fout.

---

## 1. De aanleiding

In hoofdstuk 01 stonden vier getallen: 890, 833, 787 en 745 cm⁻¹ voor solo, duo,
trio en kwartet. Die had ik uit mijn hoofd opgeschreven.

De regel in dit project is dat je nooit uit je hoofd citeert. Dus zijn ze
gecontroleerd tegen echte gemeten spectra — niet tegen een samenvattingstabel of
een handboek, maar tegen de ruwe meetdata van de NIST-database.

Dat was een goed idee, want er klopte niets van.

## 2. Eerste vondst — het zijn geen moleculaire getallen

Reken de vier terug naar golflengte:

$$\lambda = \frac{10^4}{\tilde\nu}$$

| klasse | cm⁻¹ | μm |
|---|---:|---:|
| solo | 890 | 11,24 |
| duo | 833 | 12,00 |
| trio | 787 | 12,71 |
| kwartet | 745 | 13,42 |

Dat zijn de namen van de **interstellaire banden**: 11,2 / 12,0 / 12,7 / 13,5 μm.

Die banden zijn wat een telescoop ziet als het licht van *ontelbaar veel
verschillende moleculen door elkaar* bij hem aankomt. Het is een gemiddelde over een
hele wolk.

Onze berekening aan één molecuul daartegen afzetten is zoiets als de lengte van één
leerling vergelijken met het gemiddelde van de hele school. Beide getallen bestaan,
maar het verschil betekent niets.

## 3. Tweede vondst — dezelfde rand geeft niet dezelfde piek

Dit is de belangrijke.

Naftaleen en antraceen hebben allebei randen met **vier waterstoffen naast elkaar**.
Volgens de gedachte uit hoofdstuk 01 zouden die dezelfde piek moeten geven.

Gemeten:

| molecuul | ringen | kwartetpiek |
|---|---:|---:|
| naftaleen | 2 | **781,5 cm⁻¹** |
| antraceen | 3 | **725,6 cm⁻¹** |

Verschil: **56 cm⁻¹**. Je tolerantie is 10.

Twee van de eenvoudigste PAK's die bestaan, dezelfde randvorm, en de piek ligt bijna
zes keer je toegestane marge uit elkaar.

**Randvorm alleen bepaalt de piek dus niet.** Dat is een echt feit over deze
moleculen, geen rekenfout.

## 4. Derde vondst — mijn berekening zag dat niet

Onze eigen getallen voor precies diezelfde twee moleculen:

| | naftaleen | antraceen | verschil |
|---|---:|---:|---:|
| gemeten | 781,5 | 725,6 | **56** |
| mijn berekening | 744,4 | 738,5 | **6** |

Negen keer te klein.

En de losse fouten sloegen beide kanten op: benzeen +22, naftaleen −37, antraceen
+13. Dus het argument uit hoofdstuk 02 — dat een systematische fout wegvalt als je
aftrekt — ging hier niet op. Een fout die de ene keer omhoog en de andere keer
omlaag wijst, valt nergens tegen weg.

## 5. Mijn eerste verklaring was ook fout

Ik dacht: ik houd de ring stil terwijl ik het waterstofatoom laat wiebelen, dus ik
mis de beweging van de ring.

Dat leek logisch. Maar toen ik het op benzeen testte, veranderde het antwoord met
0,3 cm⁻¹. Vrijwel niets.

Er kwam één getal uit dat de zaak besliste: **0,99**. Dat is hoeveel van de echte
trilling mijn "bevroren" versie al ving. Negenennegentig procent. Er viel daar dus
niets te repareren.

> Een verklaring die je alleen test op moeilijke gevallen, is geen verklaring. Het
> makkelijke geval had hem meteen omvergeworpen.

## 6. Wat er wél aan de hand was

Een molecuul heeft heel veel trillingen. Benzeen heeft er 30, antraceen 66. Maar
**de meeste daarvan zie je niet in een spectrum**, want ze absorberen geen licht.

Een trilling absorbeert alleen als de ladingsverdeling erdoor verschuift. Beweegt de
lading niet, dan blijft de piek weg — hoe hard het molecuul ook trilt.

En ik had een eigen regel bedacht om te bepalen welke trilling "de piek" was. Die
regel keek naar de vorm van de beweging, en niet naar de vraag of hij licht opneemt.

Voor naftaleen koos mijn regel een trilling bij 744 cm⁻¹. Die bestaat echt. Maar hij
absorbeert bijna niet. De trilling die je in een spectrometer ziet, zit bij 804.

**Ik vergeleek een onzichtbare trilling met een gemeten piek.**

## 7. De reparatie is geen betere regel

Het is helemaal géén regel.

Het rekenprogramma kan zelf uitrekenen hoeveel licht elke trilling opneemt. Dus:
neem gewoon de sterkste. Dat is precies wat een spectrometer doet.

Geen aanname, geen toewijzing, niets van mij.

## 8. Nog één ding: harmonisch tegen echt

Er blijft dan een tweede, veel nettere fout over.

Onze berekening doet alsof de binding een perfecte veer is. Dat is de formule uit
hoofdstuk 01:

$$f = \frac{1}{2\pi}\sqrt{\frac{k}{m}}$$

Een echte binding is slapper als je hard trekt, en daardoor ligt de echte piek altijd
iets **lager** dan de veerberekening zegt. Steeds dezelfde kant op, steeds ongeveer
even veel.

Zo'n fout kun je wegdelen met één getal. Voor benzeen:

$$\frac{673{,}0}{694{,}9} = 0{,}968$$

Alles maal 0,968, en klaar.

**En nu de eerlijke truc.** Dat getal is *alleen* op benzeen bepaald. Naftaleen en
antraceen hebben er niets aan bijgedragen — die zijn dus een echte test, geen
zelfbevestiging.

## 9. Het resultaat

| molecuul | mijn oude regel | nieuw, geschaald | gemeten | fout |
|---|---:|---:|---:|---:|
| benzeen | 694,3 | 673,0 | 673,0 | 0,0 |
| naftaleen | 744,4 | **778,5** | 781,5 | **−3,0** |
| antraceen | 738,5 | **721,8** | 725,6 | **−3,8** |

Gemiddelde fout op de twee moleculen die niet meededen aan het fitten: **3,4 cm⁻¹**,
tegen een tolerantie van 10.

En het verschil van 56 waar het allemaal om begon:

| | verschil |
|---|---:|
| gemeten | +55,9 |
| nieuw | **+56,7** |
| oud | +5,9 |

**Op 0,8 cm⁻¹ na goed.**

De berekening was dus nooit blind voor die 56. Mijn analyse was dat.

## 10. Wat dit betekent

**Goed nieuws:** de methode klopt. Een veerberekening met elektronen plus één
schaalgetal voorspelt deze pieken tot op een paar cm⁻¹, en het draait op je laptop.

**Slecht nieuws, en dat blijft staan:** randvorm alleen legt een piek níét vast.
Naftaleen en antraceen zijn allebei "kwartet" en liggen 56 cm⁻¹ uit elkaar.

**Maar het verschil met vanochtend:** we kunnen die 56 nu *voorspellen* in plaats van
alleen constateren.

Een atlas die alleen op randvorm sorteert, faalt. Een overdrachtswet die óók
meeneemt hoe groot en hoe gevormd het molecuul is, heeft iets echts te leren — en
weet nu voor het eerst hoe groot dat "iets" is.

## 11. Wat er van hoofdstuk 01 overeind blijft

| uit hoofdstuk 01 | status |
|---|---|
| Koppeling zwakt af met factor 3 à 4 per binding | blijft |
| Voorbij vier bindingen verwaarloosbaar | blijft |
| De baai is een uitzondering die ertoe doet | blijft |
| De vier "literatuurwaarden" | **vervallen** — het zijn telescoopbanden |
| "Motieven dragen over op 0,2–0,8 cm⁻¹" | **vervallen** — verkeerde grootheid gemeten |

Die laatste doet het meest pijn. Wat daar gemeten werd was hoe hard een C–H-binding
trilt als je de rest van het molecuul stil houdt. Dat verandert nauwelijks tussen
moleculen — bijna per definitie. We hebben grotendeels gemeten dat een C–H-binding
een C–H-binding is.

## 12. Samenvatting

1. De vier getallen uit hoofdstuk 01 waren namen van telescoopbanden, geen
   eigenschappen van een molecuul.
2. Dezelfde randvorm geeft in het lab pieken die 56 cm⁻¹ uit elkaar liggen.
3. Mijn berekening zag daar maar 6 van, omdat ik naar een trilling keek die geen
   licht opneemt.
4. Mijn eerste verklaring daarvoor was ook fout, en benzeen wees dat aan met één
   getal.
5. De oplossing was geen betere regel maar géén regel: vraag welke trilling
   absorbeert.
6. Nu klopt het tot op 3,4 cm⁻¹, en het verschil van 56 komt er tot op 0,8 na uit.

**Onthoudzin.** Een trilling die je berekent is niet vanzelf een piek die je ziet.

---

## Waar de getallen vandaan komen

| bron | wat erin staat |
|---|---|
| [verify_oop_bands_2026-08-27.py](../probes/verify_oop_bands_2026-08-27.py) | haalt de ruwe spectra bij NIST en zoekt de pieken |
| [nist_cache/](../probes/nist_cache/) | de gedownloade meetdata zelf |
| [dft_locality_2026-08-26.py](../probes/dft_locality_2026-08-26.py) | de berekening, nu met intensiteiten |
| [results_dft_locality/](../probes/results_dft_locality/) | per molecuul alle trillingen én hoeveel licht ze opnemen |

## Wat er nog open staat

- **Antraceens tweede piek klopt minder goed.** De solo-band komt op 863,7 uit tegen
  875,2 gemeten: −11,5, net over de tolerantie. De buurpiek zit er 13 aan de andere
  kant. Daar is de toewijzing dus niet zo schoon als bij het kwartet, en het gasspectrum
  zelf geeft 875 waar de vaste stof 886 geeft.
- **Drie moleculen is weinig** om een schaalfactor op te vertrouwen. Fenantreen,
  pyreen, tetraceen en chryseen moeten opnieuw, nu mét intensiteiten.
- **De baai-straf moet opnieuw gemeten worden.** Het oude getal van 11,2 cm⁻¹ komt uit
  dezelfde verkeerde grootheid als de overdrachtsclaim en is dus verdacht.
- **De grootte-vraag uit hoofdstuk 01 staat nog steeds open.** Die is door dit alles
  niet beantwoord, alleen uitgesteld.
