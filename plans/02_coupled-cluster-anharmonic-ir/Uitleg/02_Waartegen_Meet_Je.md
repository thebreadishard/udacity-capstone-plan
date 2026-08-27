# 02 — Waartegen meet je eigenlijk?

**Datum:** 2026-08-27 · **Beschrijft:** wat "fout" en "marge" betekenen als er geen bekend antwoord is

In hoofdstuk 01 stonden getallen als "0,7 cm⁻¹ verschil" en "binnen 10 cm⁻¹". Maar
een fout is altijd een verschil tussen **twee** dingen. Als het ene je berekening
is, wat is dan het andere?

Voor benzeen kun je dat opzoeken. Maar voor een molecuul met vierentwintig
koolstofatomen is de allerbeste rekenmethode nooit uitgevoerd. Waar meet je het dan
tegen af?

Dit hoofdstuk beantwoordt dat, en het antwoord is niet één ding maar een ladder.

---

## 1. Twee heel verschillende soorten getallen

Dit onderscheid is de kern van het hele hoofdstuk.

> **Een waarde** is één getal op zichzelf. "De piek ligt op 744 cm⁻¹."
>
> **Een verschil** is de afstand tussen twee getallen. "Deze piek ligt 6 cm⁻¹ lager
> dan die."

Voor een **waarde** heb je een echte waarheid nodig om tegen af te zetten.

Voor een **verschil** heb je die niet nodig. En dat is een veel groter voordeel dan
het lijkt.

## 2. Een verkeerde liniaal meet verschillen nog steeds goed

Stel je meet met een meetlint dat 2 cm te kort is.

Je meet Anouk: 170 cm. Fout, ze is 172.
Je meet Bram: 180 cm. Fout, hij is 182.

Allebei mis. Maar:

$$180 - 170 = 10 \qquad\text{en}\qquad 182 - 172 = 10$$

**Het verschil klopt precies.** De fout van het meetlint zit in allebei de metingen
en valt weg bij het aftrekken.

Dat heet een **systematische fout**: een fout die steeds dezelfde kant op gaat.
Systematische fouten vernietigen waardes en laten verschillen met rust.

## 3. Dit is precies wat wij zien

Kijk naar de baai-meting uit hoofdstuk 01, met twee verschillende rekenmethodes.

|  | zonder baai | met baai | **verschil** |
|---|---:|---:|---:|
| krachtveld (MMFF) | 768,5 | 760,4 | **8,1** |
| met elektronen (DFT) | 744,4 | 738,3 | **6,1** |

Kijk nu naar hoe erg de twee methodes het oneens zijn.

Over de **waardes**:

$$768{,}5 - 744{,}4 = 24{,}1\ \text{cm}^{-1}$$

Over het **verschil**:

$$8{,}1 - 6{,}1 = 2{,}0\ \text{cm}^{-1}$$

**De twee methodes zijn het twaalf keer beter eens over het verschil dan over de
waarde.**

Dat is geen toeval. Beide methodes hebben dezelfde soort systematische fout, en die
valt grotendeels weg zodra je aftrekt.

## 4. Daarom heeft onze meting geen waarheid nodig

Loop nu terug door hoofdstuk 01 en kijk wat er eigenlijk gemeten werd.

| meting | waartegen afgezet | waarheid nodig? |
|---|---|---|
| koppeling per afstand | tegen de andere afstanden in hetzelfde molecuul | **nee** |
| overdracht van een duo | tegen hetzelfde duo in een ander molecuul | **nee** |
| baai-straf | tegen dezelfde klasse zonder baai | **nee** |
| krachtveld tegen DFT | de twee methodes tegen elkaar | **nee** |

Alle vier zijn **verschillen**. Geen enkele heeft een bekend antwoord nodig.

Dat is de reden dat deze hele meting op een laptop kan, in een paar uur, zonder dat
er ooit een coupled-cluster-berekening aan te pas komt. **We vragen niet "waar ligt
de piek?" maar "verschuift de piek als ik iets verander?"**

Die tweede vraag is veel goedkoper en is toevallig ook precies de vraag waar de
motiefatlas op rust.

## 5. Maar soms heb je de waarheid wél nodig

Zodra je een **bandpositie** wilt beloven — "deze piek ligt op 745 cm⁻¹" — is een
verschil niet meer genoeg. Dan moet er iets zijn om tegen af te zetten.

En dan komt jouw vraag met volle kracht terug: wat is dat?

## 6. Het antwoord: het experiment, niet de berekening

Voor infraroodspectra van deze moleculen is de waarheid **de meting in het lab**.

Niet CCSD(T). Niet DFT. Gewoon: iemand heeft het molecuul gemaakt, er infrarood
licht doorheen gestuurd en opgeschreven waar de pieken zaten.

De getallen 890, 833, 787 en 745 cm⁻¹ uit hoofdstuk 01 komen daarvandaan.

Dat is een belangrijke omkering. In dit vakgebied is de dure rekenmethode niet de
waarheid — die is een **vervanger** voor de waarheid, voor gevallen waar niemand
gemeten heeft.

## 7. Hoe betrouwbaar is dat experiment dan?

Niet oneindig. Er zijn twee soorten metingen, en ze geven niet hetzelfde antwoord.

**In gasvorm.** Losse moleculen die vrij zweven. Dit is de schone meting, want het
molecuul wordt door niets gestoord. Maar grote PAK's zijn vaste stoffen die je maar
moeilijk in gasvorm krijgt, dus deze metingen zijn schaars.

**In een matrix.** Het molecuul wordt ingevroren in vast argon of neon bij ongeveer
10 kelvin. Veel makkelijker, dus hier is veel meer van. Maar het bevroren gas duwt
tegen het molecuul aan, en daardoor verschuiven de pieken een paar cm⁻¹.

Daarom heeft dit project twee verschillende linialen afgesproken:

| waartegen | tolerantie |
|---|---:|
| gasfase | 10 cm⁻¹ |
| matrix | 15 cm⁻¹, mét een vooraf vastgelegde correctie |

En een harde regel erbij: **nooit gecorrigeerde en ongecorrigeerde getallen door
elkaar gebruiken.** Anders kies je per band welke vergelijking het beste uitkomt,
en dan meet je niets meer.

## 8. En CCSD(T)? Je vermoeden klopt

Ja. Voor grote PAK's is CCSD(T) nooit volledig uitgevoerd, en dat gaat voorlopig ook
niet gebeuren.

De reden staat in hoofdstuk 01 in een ander jasje: de rekentijd. Voor een molecuul
met $N$ atomen groeit het werk voor de trillingen ruwweg met $N^2$, en de kosten van
CCSD(T) zelf nog veel harder dan dat. Op onze laptop kostte een DFT-berekening:

| molecuul | atomen | tijd |
|---|---:|---:|
| benzeen | 12 | 3 min |
| naftaleen | 18 | 14 min |
| fenantreen | 24 | 38 min |
| tetraceen | 30 | 66 min |

En CCSD(T) is duizenden keren duurder dan DFT.

**Dat is precies waarom plan 02 is gekrompen.** De belofte ging van "PAK's tot
pyreen, neutraal en geladen" terug naar "benzeen en naftaleen, neutraal". Niet omdat
het idee slechter werd, maar omdat de rekensom eerlijk gemaakt werd.

## 9. De ladder van waarheden

Zet het naast elkaar en het wordt overzichtelijk. Van links naar rechts: wie is de
baas over wie.

$$\text{experiment} \;\;>\;\; \text{CCSD(T)} \;\;>\;\; \text{DFT} \;\;>\;\; \text{krachtveld}$$

| niveau | bestaat voor | rol |
|---|---|---|
| **experiment** | veel PAK's in matrix, weinig in gasfase | de waarheid |
| **CCSD(T)** | tot ongeveer naftaleen | vervanger waar geen meting is |
| **DFT** | tot honderden atomen | werkpaard, moet geijkt worden |
| **krachtveld** | duizenden atomen | verkenning, geen claim |

Elk niveau wordt gecontroleerd door het niveau erboven, waar dat bestaat. Waar het
niet bestaat, moet je opschrijven dat je het niet weet.

**Boven naftaleen heeft niemand een CCSD(T)-controle.** Dat is geen tekortkoming van
dit project, dat is de stand van het vakgebied.

## 10. Daarom wordt de fout opgesplitst

Als je meerdere lagen op elkaar stapelt, moet je per laag opschrijven hoeveel fout
er bijkomt. Dit project doet dat met vijf losse termen:

| term | wat er misgaat |
|---|---|
| **A** | het goedkope model kopieert het dure niet perfect |
| **B** | de dure methode is zelf niet exact |
| **C** | de manier waarop je de trillingen uitrekent is benaderd |
| **D** | de omgeving: matrix, temperatuur |
| **E** | een motief in een groot molecuul gedraagt zich net iets anders dan alleen |

Term **E** is de nieuwe, en het is precies wat wij op dit moment meten. De 0,7 cm⁻¹
uit hoofdstuk 01 is een eerste schatting van term E.

## 11. De regel die het eerlijk houdt

> **Deze vijf termen mogen nooit tot één getal opgeteld worden.**

Waarom niet? Omdat één samengevat getal verbergt waar het misgaat. Als je zegt
"onze fout is 8 cm⁻¹", weet niemand of dat komt door de rekenmethode, door het
overzetten naar een groter molecuul, of doordat je met een matrixmeting vergeleek.

En jij weet het zelf ook niet meer. Dan kun je het volgend jaar niet verbeteren,
want je weet niet waaraan.

## 12. Een eerlijkheid over hoofdstuk 01

Nu je dit weet, moet er iets bij dat in hoofdstuk 01 te makkelijk overkwam.

Daar stond de gemeten ladder naast de experimentele waarden:

| klasse | onze berekening | experiment | verschil |
|---|---:|---:|---:|
| duo | 781,7 | 833 | **−51** |
| trio | 772,7 | 787 | −14 |
| kwartet | 744,4 | 745 | **−0,6** |

Kwartet lijkt bijna perfect en duo zit er vijftig naast. Dat is een verdacht groot
verschil binnen dezelfde tabel.

De verklaring is dat wij een **vereenvoudigd model** gebruiken: wij laten alleen het
waterstofatoom wiebelen, terwijl in werkelijkheid de hele ring meebeweegt. Onze
getallen zijn dus niet echt bandposities, en tegen het experiment afzetten is niet
eerlijk.

**Dat is geen probleem voor wat we willen weten.** Onze vraag is een *verschil*, en
uit §2 weet je dat verschillen tegen zo'n fout bestand zijn. Beide moleculen krijgen
dezelfde vereenvoudiging.

Maar die 0,6 bij kwartet is geluk, geen prestatie, en zo hoort hij ook gelezen te
worden.

## 13. Samenvatting

1. Een fout is altijd een verschil tussen twee dingen.
2. Voor een **waarde** heb je een echte waarheid nodig. Voor een **verschil** niet.
3. Een systematische fout vernietigt waardes maar laat verschillen met rust — het te
   korte meetlint meet hoogteverschillen nog steeds goed.
4. Onze lokaliteitsmeting bestaat volledig uit verschillen. Daarom kan hij op een
   laptop en heeft hij geen coupled cluster nodig.
5. Wil je een échte bandpositie beloven, dan is de waarheid **het lab**, niet de
   berekening.
6. CCSD(T) bestaat inderdaad niet voor grote PAK's. Dat is de reden dat plan 02 zijn
   belofte heeft teruggebracht naar benzeen en naftaleen.
7. Boven naftaleen bestaat er geen controle. Dat schrijf je op, in plaats van het te
   verbergen achter een gemiddelde.

**Onthoudzin.** Je hebt geen waarheid nodig om een verandering te meten — alleen om
een waarde te beloven.

---

## Waar de getallen vandaan komen

| bron | wat erin staat |
|---|---|
| [results_dft_locality/](../probes/results_dft_locality/) | de DFT-frequenties per molecuul |
| [probe_band_locality_2026-08-26.ipynb](../probes/probe_band_locality_2026-08-26.ipynb) | de krachtveldmeting waar de MMFF-getallen uit komen |
| [hardware_capability_2026-08-26.py](../probes/hardware_capability_2026-08-26.py) | de rekentijden uit §8 |
| [Frozen_Ladder_and_Tolerances_2026-08-26.md](../GoalGathering/Frozen_Ladder_and_Tolerances_2026-08-26.md) | de vastgelegde toleranties van 10 en 15 cm⁻¹ |

## Wat er nog open staat

- **De experimentele waarden 890/833/787/745 zijn nog niet tegen een bron
  gecontroleerd.** In dit project geldt: nooit citeren uit het hoofd. Voordat een van
  die getallen in de scriptie komt, moet er een DOI bij.
- **Hoeveel CCSD(T)-werk er precies voor naftaleen bestaat, moet nog opgezocht
  worden.** Dat het boven naftaleen ophoudt is zeker; waar precies de grens ligt,
  is een literatuurvraag die nog beantwoord moet worden.
- **Term E is nog niet af.** De 0,7 cm⁻¹ komt uit één vergelijking. De langere reeks
  moet er meer opleveren voordat het een getal is waar iets op mag rusten.
