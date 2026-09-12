# Hoofdstuk 4 — De richtingen en de experimenten

> **In dit hoofdstuk leer je**
> – welke exacte herformuleringen van het elektronenprobleem al bestaan, en waar hun prijs zit;
> – de zes richtingen S1 t/m S6 van plan 06, elk met de toets die hem kan afschieten;
> – de eerste experimenten X0 t/m X4 en wat ze al hebben opgeleverd;
> – hoe het grootboek werkt en hoe een idee sterft.

---

## §4.1 Dezelfde vergelijking, vijf keer anders opgeschreven

De Schrödingervergelijking voor alle elektronen kun je op verschillende manieren exact
herschrijven. Elke herschrijving verplaatst de moeilijkheid naar een andere plek. Dat is precies
waar plan 06 naar kijkt: is er een herschrijving waarin de moeilijkheid voor *onze klasse* klein wordt?

| herschrijving | exact? | waar de prijs zit | wat hem voor onze klasse snel zou maken |
|---|---|---|---|
| coupled cluster (exponentiële ansatz) | exact bij volledige orde; CCSD(T) is een afkapping | de "(T)"-stap groeit als N⁷; lokale varianten maken het bijna lineair | bewezen afval van de amplitudes met afstand; lage rang van de amplitude-tensoren |
| twee-elektronen-dichtheidsmatrix als variabele | exact, mits "N-representeerbaar" | de voorwaarden voor N-representeerbaarheid (zelf QMA-hard) | een klasse waarvoor een eindig stel voorwaarden bewezen volstaat |
| dichtheidsfunctionaaltheorie | exact met de exacte functionaal | de functionaal is in het algemeen QMA-hard (hoofdstuk 2) | een klasse-beperkte functionaal met een foutgrens |
| matrixproducttoestanden (DMRG) | exact bij grote "bonddimensie" | de bonddimensie groeit met de verstrengeling over een snede | π-systemen als bijna-eendimensionaal: begrensde verstrengeling |
| neurale-netwerkgolffuncties | variationeel, exact alleen in de limiet | Monte-Carlo-bemonstering; per molecuul duur; nog geen hergebruik | één ansatz voor een hele familie, gecertificeerd tegen opgeslagen CC-lijnen |

De laatste rij is de "AI-eigen" herformulering; de eerste vier zijn exact. Een richting van plan 06
is steeds: een rij, gekoppeld aan een structuurstelling of een meting over de klasse.

## §4.2 De zes richtingen

Elke richting heeft een niveau (E1/E2/E3 uit hoofdstuk 1) en een goedkope **falsificatietest**: een
proef op data die al in de repository ligt, die de richting kan laten sneuvelen. Geen coupled-cluster-
rekentijd voor plan 06 totdat een richting zijn eerste test heeft doorstaan.

**S1 — Bewezen lokaliteit: hoe snel valt de correlatie af bij aromaten?** (E1/E2.) Als de bijdrage
tussen twee fragmenten exponentieel afvalt met hun afstand, groeit het aantal paren dat ertoe doet
lineair, en de constante is nu al meetbaar. *Test:* X3b, paarenergieën tegen afstand.

**S2 — Lage rang van het verschil, niet van de energie.** (E2.) Plan 05 wil niet de CC-energie maar
het verschil CC − DFT. Misschien heeft dat *verschil* een simpelere structuur (lagere "rang") dan de
energie zelf, zodat de factorisatietrucs uit de literatuur (tensorhypercontractie) er beter op werken.
*Test:* eerst geverifieerd lezen; daarna een prototype op benzeen tegen de opgeslagen waarheidslijn,
niet naast een ankerjob.

**S3 — Bijna-eendimensionale π-systemen.** (E1 bij vaste bonddimensie.) Als de verstrengeling over
elke snede van een aromatische vlok begrensd is, is DMRG er exact bij vaste bonddimensie en lineair
in kosten. *Test:* de literatuur over DMRG op polyacenen en PAK's; later een kleine controle op de
π-ruimte van benzeen.

**S4 — Het doelwit verkleinen.** (E3.) Een bandverschuiving hangt in eerste orde alleen af van de
diagonaal van de correctie; de koppelingen komen pas in tweede orde. Als maar een klein deel van de
correctie de gescoorde banden verschuift, hoeft de Schrödingervergelijking maar "langs die richtingen"
opgelost te worden. *Test:* X2 op de benzeen-tensor van de dry run: welke elementen verschuiven een
band met meer dan 0,5 cm⁻¹?

**S5 — De bevragingsalgebra rond de energie** (nevenspoor, E1). Een gradiënt is een
Hessiaan-maal-vector-product; matrices met structuur zijn exact te herstellen uit een klein aantal
zulke producten (kleuringsstellingen uit de jaren zeventig en tachtig, en gerandomiseerde
lage-rangmethoden). Dit raakt niet de Schrödingervergelijking maar hoe vaak je hem oplost. *Test:*
X1, rang en kleuringsgetal van de benzeen-tensor tegen de gemeten K = 448. Kanttekening: een gradiënt
kostte ongeveer 50 energieën.

**S6 — Modellen als voorstellers, nooit als autoriteit.** Geen richting maar een vaste regel. Een
taalmodel mag herformuleringen en literatuur voorstellen; elk voorstel komt alleen in het grootboek
met een toets, en verlaat het als de toets is gedaan.

## §4.3 De experimenten en wat ze al gaven

| experiment | wat | stand op 12 september 2026 |
|---|---|---|
| X0 | de drie complexiteits- en lokaliteitsartikelen volledig lezen en vastleggen wat ze uitsluiten | **gedaan** (leesnotitie); E1 "in het algemeen" dicht, klasse-beperkt open |
| X5 (nieuw, 12 sep) | waar de correctie in de ruimte zit: per atoompaar | gedaan: 93,5 % zit op atomen en bindingen, maar geen enkel van de 78 blokken is nul (alle boven 3× de ruis), en de koolstofring is "vlak" (meta en para even groot als gebonden) — de correctie is een ring-eigenschap; lage rang opnieuw afwezig (S2 onwaarschijnlijk) |
| X1 | rang en kleuringsgetal van de benzeen-Δ₂ tegen K = 448 | gedaan 12 sep; **gecorrigeerd dezelfde avond (X1b)**: de eerste telling kleurde de verkeerde graaf; geverifieerd kost exacte terugwinning 8–18 producten (CPR) of 7–14 (symmetrisch) = 420–1080 energieën bij 2M per product, tegen K = 448 — dus niet goedkoper, tenzij een product veel minder dan 2M energieën kost; de rang is vol (30). **X1c (na het lezen van Coleman & Moré 1984):** met hun substitutiemethode (rijen van achteren naar voren oplossen) zijn 6–7 producten genoeg = 360–420 energieën, voor het eerst ónder de 448. **X1d (dezelfde avond):** de ruisversterking is gemeten en mild — bandposities 0,10 cm⁻¹ tegen 0,07 voor het volledige deck, geen enkele trekking boven de 0,5 cm⁻¹ — **Correctie dezelfde avond:** een tweede-orde product uit energieën kost ≈ 4M = 120 energieën, dus 6 producten ≈ 720 — méér dan de 448 van het deck; de route loont alleen met analytische gradiënten (bijproject M2), en dan met een orde van grootte. Als voorstel P24 aan plan 05 aangeboden |
| X2 | gevoeligheid van bandposities voor elk element van Δ₂ | te doen (minuten) |
| X3a | wat LNO bij naftaleen bewaarde, uit de bestaande log | **gedaan**: 92–100 % bezet, ~56 % virtueel |
| X3b | MP2-paarenergieën tegen LMO-afstand, afvalconstante | script klaar; na de ankerjob |
| X4 | wat Mathlib al heeft voor symmetrische matrices, rang, kleuring, variatieprincipe | te doen (lezen) |

## §4.4 Het grootboek

Alle richtingen staan in één tabel achterin het oriëntatiedocument: id, niveau, status, eerste
test, resultaat. Een richting is *voorgesteld*, *levend* (test gepland of deels gedaan), *gesneuveld*
(test negatief; blijft staan met het resultaat) of *overgedragen* (positief; gaat via een gedateerde
notitie naar plan 05). Niets wordt gewist. Zo kan iemand over een jaar zien welke ideeën zijn
geprobeerd en waarom ze niet doorgingen — dat is voor een ideeënplan net zo waardevol als een treffer.

## §4.5 Eén zin om te onthouden

Zes richtingen, elk met een goedkope toets op data die er al ligt; één (S1) leeft al met een eerste
getal, de rest wacht op zijn test — en een idee zonder toets wordt geparkeerd.
