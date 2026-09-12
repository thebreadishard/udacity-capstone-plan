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

**S1 — Bewezen lokaliteit: hoe snel valt de correlatie af bij aromaten?** (E1/E2.) *Aanvulling 12 september:* de wiskundige kant bestaat al voor dichtheidsmatrices (Benzi, Boito & Razouk 2013): bij een begrensde interactieafstand en een gap valt elke nette functie van de Hamiltoniaan exponentieel af in *graafafstand* (aantal bindingen), met een snelheid die ongeveer gelijk is aan de gap. Twee gevolgen: de "vlakke ring" van X5 is lokaliteit in de verkeerde maat gemeten (meta en para zijn maar 2 en 3 bindingen ver), en lokaliteit wordt zwakker naarmate de gap kleiner wordt — dus juist bij de grote PAK's. Voor de correctie zelf is de stelling nog niet geschreven; dat is het "nieuwe wiskunde"-doelwit T3. Als de bijdrage
tussen twee fragmenten exponentieel afvalt met hun afstand, groeit het aantal paren dat ertoe doet
lineair, en de constante is nu al meetbaar. *Test:* X3b, paarenergieën tegen afstand.

**S2 — Lage rang van het verschil, niet van de energie.** (E2.) Plan 05 wil niet de CC-energie maar
het verschil CC − DFT. Misschien heeft dat *verschil* een simpelere structuur (lagere "rang") dan de
energie zelf, zodat de factorisatietrucs uit de literatuur (tensorhypercontractie) er beter op werken.
*Test:* eerst geverifieerd lezen; daarna een prototype op benzeen tegen de opgeslagen waarheidslijn,
niet naast een ankerjob.

**S3 — Bijna-eendimensionale π-systemen.** (E1 bij vaste bonddimensie.) *Aanvulling 12 september:* na lezing (Hachmann e.a. 2007, DMRG in de volledige π-ruimte tot dodecaceen) en X5 is de eerlijke vorm van S3 niet E1 maar E2: een π-ruimte-berekening kan hoogstens het ring-gebonden deel van de correctie leveren, niet het anker. Experiment X6 meet bij benzeen hoeveel dat deel is. Als de verstrengeling over
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
| X2 | gevoeligheid van bandposities voor elk element van Δ₂ | **gedaan 12 sep**: van de 435 koppelingselementen bewegen er maar 6 een bandpositie meer dan 0,5 cm⁻¹ (één paar draagt bijna alles); ruis op de elementen beweegt geen enkele band meer dan 0,05 cm⁻¹ — S4 leeft (E3) |
| X3a | wat LNO bij naftaleen bewaarde, uit de bestaande log | **gedaan**: 92–100 % bezet, ~56 % virtueel |
| X3b | MP2-paarenergieën tegen LMO-afstand, afvalconstante | **gedaan 12 sep**: afvalconstante λ = 0,75 Å bij naftaleen, maar 2,3 % van de correlatie-energie zit voorbij 3 Å — niets weg te laten op deze grootte |
| X4 | wat Mathlib al heeft voor symmetrische matrices, rang, kleuring, variatieprincipe | **gedaan 12 sep** (zie hoofdstuk 5): alles wat algebra is staat erin, alles wat natuurkunde is ontbreekt |
| X8 (12 sep avond) | hoe groeit het aantal substitutieproducten met het molecuul, tegen het aantal matrixelementen, voor patronen die je uit de bindingen alleen kunt opschrijven (benzeen tot C₃₈₄H₄₈) | **gedaan**, met een les: op de echte benzeen-correctie bleek dat "99 % van de norm bewaren" nog bandposities 14 cm⁻¹ verschuift; voor 0,5 cm⁻¹ zijn 74 van de 78 blokken nodig. **Norm-dunheid is geen band-dunheid.** Bij benzeen is dus geen enkel bindingspatroon toegestaan, en de groottereeks (9 producten bij elke grootte onder het bindingspatroon; 18–30 onder "één ring diep"; evenredig met het aantal koolstoffen onder "alle C–C-paren") staat als *haakjes* te wachten op de naftaleen-tensor. Met alleen energieën loont substitutie nergens (6–11× de elementen); met gradiënten groeit het voordeel met de grootte |
| X9 (gedefinieerd 12 sep) | blokprofielen van de DFT-Hessiaan en van de correctie naast elkaar, per grafafstand, op norm- én bandniveau | te doen (minuten); toetst T3′ (§3.4a); verliesvoorwaarde: de verhouding correctie/DFT daalt niet met de afstand |
| X9 (12 sep avond) | valt de correctie sneller af dan de DFT-Hessiaan zelf (T3′)? | **gedaan, negatief**: de verhouding correctie/DFT-Hessiaan *stijgt* met de grafafstand (2,7 % op het atoom → 6,5 % op drie bindingen; C–C meta/para 19–26 %). De correctie is het langeafstandsobject, met het bereik van het π-systeem, niet van de bindingen. T3′ vervalt bij benzeen |
| X10 (12 sep avond) | welke koppelingen moeten gemeten worden voor 0,5 cm⁻¹, en kan DFT alleen ze aanwijzen? | **gedaan, positief**: van 47 toegestane paren zijn er 19 genoeg als je ze rangschikt op de gratis DFT-regel 1/‖ω_i² − ω_j²‖ (een perfect orakel: 17; de beste volgorde: 6); rangcorrelatie 0,75 met het gemeten effect. Naïef 98 energieën tegen K = 448. Kandidaat-voorstel P25 voor plan 05, pas na de herhaling op naftaleen |
| X11 (12 sep avond) | stapelen de twee besparingen (minder elementen én substitutieproducten)? | **gedaan, ja**: op het X10-patroon zijn 4 producten = 8 gradiënten genoeg (symmetrie-prior alleen: 7 = 14; dicht: 30) |
| X12 (12 sep avond) | hoe snel valt de DFT-Hessiaan zélf af per binding, van benzeen tot coroneen (uit de bewaarde Hessianen van plan 02) | **gedaan**: bij elke stap van één binding wordt een blok 3,4–4 keer kleiner, voor alle negen moleculen hetzelfde; maar ook de DFT-Hessiaan mag je niet afkappen: blokken voorbij drie bindingen weglaten verschuift banden 26–246 cm⁻¹. De les van X8 geldt dus voor negen moleculen en voor het gemiddelde veld zelf |
| X13 (12 sep avond) | de modetabel van naftaleen (48 trillingen, symmetrielabels, families) uit de bewaarde DFT-Hessiaan van plan 02 | **gedaan**: 141 van de 1128 koppelingen zijn door symmetrie toegestaan, precies de 282 energieën (2 per koppeling) die plan 05 voor het R1-deck rekende — een onafhankelijke controle; de DFT-rangorde van X10 staat er alvast bij, zodat de toets van P25 straks een tabel leest die hij niet zelf gekozen heeft |
| X6 (gedefinieerd 12 sep) | welk deel van de ringmode-correctie bij benzeen de π-ruimte alleen draagt (CAS(6,6) tegen HF, langs de drie gemeten modes) | te doen (minuten rekenwerk, na de ankerjob); verliesvoorwaarde: minder dan de helft op de C–C-strekmode sluit S3 als ankerroute |
| X7 (gedefinieerd 12 sep) | afvalconstante λ tegen de HOMO–LUMO-gap voor benzeen, naftaleen, pyreen | te doen (rekenwerk); toetst de voorspelling "afvalsnelheid ∝ gap" van de lokaliteitsstellingen |

## §4.3a Toevoeging 12 september 2026 (avond): de vraag van de gebruiker — wordt plan 05 goedkoper door plan 06?

De gebruiker stelde de vraag scherp: bewijs eerst dat de wiskunde van 06 de berekeningen van 05
goedkoper kan maken, en deel het voorstel daarna pas. Daarvoor staat nu een ladder van vier treden in de
README van plan 05.

- **Trede 1 (gedaan): staat de prijs van een gradiënt in de literatuur?** Alles hangt aan één getal,
  g: hoeveel energieën kost één analytische gradiënt? De wiskunde van automatisch differentiëren noemt
  dat de *kostenverhouding* (cost ratio) en bewijst dat hij door een kleine constante begrensd is
  (het overzichtsartikel van Baydin en anderen, 2018, zegt: kleiner dan 6, meestal 2 à 3). Maar dat is
  een bovengrens voor het rekenwerk van één achterwaartse veeg; onze motor herberekent tussenresultaten
  om geheugen te sparen, dus de echte g ligt erboven, en in geen enkel kwantumchemisch artikel dat we
  konden lezen staat hij voor een lokale CCSD(T)-gradiënt afgedrukt. Uitkomst: **niet in de literatuur;
  alleen te meten.**
- **Trede 2 (modelvorm gedaan = X8, echte vorm wacht):** groeit het voordeel van substitutie met de
  grootte? Het model zegt ja, mits blokken voorbij één ring onder de ruis vallen — en dat kan benzeen
  niet laten zien, want in benzeen ligt niets verder dan één ring. De naftaleen-tensor (na de
  DFT-proefrun) is het eerste molecuul dat het kan.
- **Trede 3 (in de wachtrij):** één product echt meten in de motor van plan 05, bij benzeen (beslissing
  34 van plan 05: het voorstel P24 is aanvaard als twee vooraf vastgelegde proefpunten).
- **Trede 4 (weken werk, de gebruiker beslist):** g zelf meten in PySCFAD met bevroren ruimtes — de
  enige trede die een besparing kan *laten zien*.

Eerlijk samengevat: de algebra is bewezen (Lean), de ruis is mild (X1d), de telling is gunstig
(X1c, X8-haakjes), maar de besparing bestaat pas als g klein is, en g kent nog niemand. *Later die avond kwam
er één besparing bij die géén gradiënten nodig heeft: X10's gratis DFT-regel, die bij benzeen 19 van de 47
koppelingen aanwijst (naïef 98 energieën tegen 448), en die met de substitutie stapelt (X11: 8 gradiënten).
De kostenladder in het oriëntatiedocument zet alle hefbomen met hun factor op een rij.*

## §4.4 Het grootboek

Alle richtingen staan in één tabel achterin het oriëntatiedocument: id, niveau, status, eerste
test, resultaat. Een richting is *voorgesteld*, *levend* (test gepland of deels gedaan), *gesneuveld*
(test negatief; blijft staan met het resultaat) of *overgedragen* (positief; gaat via een gedateerde
notitie naar plan 05). Niets wordt gewist. Zo kan iemand over een jaar zien welke ideeën zijn
geprobeerd en waarom ze niet doorgingen — dat is voor een ideeënplan net zo waardevol als een treffer.

## §4.5 Eén zin om te onthouden

Zes richtingen, elk met een goedkope toets op data die er al ligt; één (S1) leeft al met een eerste
getal, de rest wacht op zijn test — en een idee zonder toets wordt geparkeerd. *(Stand 12 september
avond: S5 is overgedragen aan plan 05 als beslissing 34, voorwaardelijk op gradiënten; S2 onwaarschijnlijk;
S1, S3, S4 levend; en de les van X8 geldt voor alles: toets dunheid altijd op bandposities, nooit op normen.)*
