# Hoofdstuk 4 — Wiskundig gereedschap

> **In dit hoofdstuk leer je**
> – wat vectoren en matrices hier betekenen, en wat "diagonaliseren" doet;
> – hoe je een tweede afgeleide meet met eindige verschillen, en waarom je dat symmetrisch doet;
> – wat kleinste kwadraten is en wat een "residu" zegt;
> – hoe je uit weinig metingen toch een grote matrix kunt bepalen als die "dun" is;
> – wat ruis is, hoe je σ schat, en waarom je door n − p deelt;
> – wat een hash is en waarom het plan er overal een op zet.

---

## §4.1 Vectoren en matrices

Een **vector** is een lijstje getallen. De stand van benzeen is een vector van 36 getallen
(12 atomen × 3 coördinaten). Een uitwijking uit het evenwicht is ook een vector: hoeveel
elk atoom in elke richting is verplaatst. In het plan heet zo'n uitwijkingsvector een
**patroon**, met symbool p.

Een **matrix** is een tabel van getallen met rijen en kolommen. De Hessiaan (hoofdstuk 2)
is een vierkante matrix. Een matrix "werkt" op een vector: H·p is weer een vector, hier de
kracht die het molecuul terugduwt als je het langs p uitwijkt. De energie van die
uitwijking is een getal:

E(p) = ½ pᵀ H p,

waarbij pᵀ H p betekent: neem de vector, laat de matrix erop werken, en neem het inproduct
met de oorspronkelijke vector. Voor één veer is dit gewoon ½ k x².

**Diagonaliseren** is de stap die uit de Hessiaan de normale modes haalt: je zoekt de
bijzondere vectoren (eigenvectoren) waarvoor H·v gewoon een veelvoud van v is, H·v = λ v.
Die v's zijn de normale modes en de λ's de bijbehorende veerconstanten, dus de
frequenties. In de coördinaten van die v's is de matrix diagonaal: alle koppelingen zijn
weggedraaid. Dat is waarom het plan de correctie Δ₂ uitdrukt "in de basis van de
DFT-modes": daar is de goedkope Hessiaan diagonaal, en Δ₂ laat zien wat er nog aan
ontbreekt.

## §4.2 Tweede afgeleiden meten met eindige verschillen

Je kunt een programma vragen om E(p) bij elke stand, maar niet direct om de tweede
afgeleide. Die schat je met **eindige verschillen**. Voor één coördinaat q:

d²E/dq² ≈ [E(+h) − 2 E(0) + E(−h)] / h².

Je hebt dus drie energieën nodig: in het evenwicht, een stapje h vooruit, een stapje
achteruit. Voor een kruisterm tussen twee coördinaten heb je vier energieën nodig (beide
vooruit, beide achteruit, en de twee gemengde). Voor een volledige Hessiaan van M modes op
deze manier: 1 + 2M + 4·M(M−1)/2 energieën. Voor benzeen (M = 30) is dat 1801. Voor coroneen
(M = 102) bijna 21.000. Dat is precies het aantal dat plan 05 wil vermijden.

**Waarom symmetrisch (±h)?** Schrijf E als machtreeks: E(q) = E₀ + a q + ½ k q² + b q³ + …
Tel je E(+h) en E(−h) op, dan vallen alle *oneven* termen (a q, b q³) precies weg en blijft
alleen k q² + (kwartisch) over. Neem je alleen E(+h) − E(0), dan zit de lineaire term a h
er nog in, en die is voor de CC−DFT-energie een paar keer zo groot als het Δ₂-signaal
(hoofdstuk 3, Δ₁). Daarom gaat in plan 05 **elk patroon als paar ±p** de berekening in, en
is het "antwoord" van een patroon de symmetrische combinatie

R_s(p) = ½ [ΔE(+p) + ΔE(−p)] − ΔE(0) = ½ pᵀ Δ₂ p + (kwartisch).

De antisymmetrische combinatie ½ [ΔE(+p) − ΔE(−p)] = Δ₁·p komt er gratis bij en levert Δ₁.

**De stapgrootte** is een afweging. Te klein: het verschil verdrinkt in de rekenruis. Te
groot: de kwartische term vervuilt de schatting. Het plan gebruikt q = 1 (de natuurlijke
trillingsamplitude) en controleert vooraf, met de ruislijn van hoofdstuk 5, of de ruis
daar klein genoeg voor is.

## §4.3 Kleinste kwadraten en residuen

Stel je meet negen punten E(q) langs één mode en wilt er een gladde kromme door leggen.
**Kleinste kwadraten** kiest de kromme (bijvoorbeeld een polynoom van graad 4, met vijf
coëfficiënten) waarvoor de som van de gekwadrateerde afstanden tot de meetpunten minimaal
is. Die afstanden heten **residuen**.

De residuen zeggen iets over de ruis. Als de meetpunten precies op een gladde kromme
liggen, zijn de residuen nul; als er ruis in de metingen zit, blijven er residuen over. De
standaardafwijking van de ruis schat je als

σ = √( SSR / (n − p) ),

met SSR de som van de gekwadrateerde residuen, n het aantal punten (9) en p het aantal
gefitte coëfficiënten (5). Dat **n − p** in plaats van n is belangrijk: een polynoom met
vijf coëfficiënten "eet" vijf van de negen vrijheidsgraden op en drukt de residuen
kunstmatig omlaag. Deel je door 9, dan onderschat je σ met een factor √(4/9) ≈ 0,67. Het
plan schrijft daarom uitdrukkelijk n − p voor.

Met maar vier vrijheidsgraden over is één σ een onzeker getal (het 90%-interval loopt van
0,42 σ tot 1,54 σ). Daarom **poolt** het plan de vier gemeten modes: σ² wordt over de vier
modes gemiddeld (16 vrijheidsgraden), de gepoolde waarde beslist, en de afzonderlijke
waarden worden erbij geprint met een vlag als één ervan meer dan twee keer de gepoolde is.

## §4.4 Veel onbekenden, weinig metingen: dunne matrices terugvinden

Dit is het wiskundige hart van het plan. Δ₂ is een M × M-matrix; voor coroneen zijn dat
ruim 5000 verschillende getallen. Elke meting (één patroonpaar) levert één getal:
R_s(p) = ½ pᵀ Δ₂ p. Dat is één **lineaire vergelijking** in de onbekende elementen van Δ₂.
Met K metingen heb je K vergelijkingen. Als je er evenveel hebt als onbekenden, kun je
het stelsel oplossen. Maar het plan wil juist **veel minder** metingen dan onbekenden.

Dat kan als je iets over de oplossing weet. Twee vormen van voorkennis, in het plan
**priors** genoemd:

1. **Structureel (frequentie-gebande) prior.** De verwachting is dat Δ₂ vooral
   niet-diagonale elementen heeft tussen modes met bijna dezelfde frequentie (binnen een
   band van breedte w). Elementen buiten die band krijgen een "straf" op hun grootte
   (technisch: een ℓ₁-straf, die oplossingen met veel exacte nullen bevoordeelt), plus een
   lage-rangterm. Het oplossen wordt dan: zoek de matrix die de metingen verklaart én zo
   weinig mogelijk buiten-de-band-elementen heeft. Dit is een standaardprobleem uit de
   **compressed sensing**: een dun object kun je met weinig, slim gekozen metingen exact
   terugvinden. De bandbreedte w en de strafgewichten worden niet gekozen maar uit een
   DFT-tegen-DFT-oefening (de "dry run") afgelezen volgens een vaste regel.
2. **Geleerde prior.** Een neuraal netwerk (module 05) voorspelt uit DFT-kenmerken *welke*
   niet-diagonale elementen groot zullen zijn. Dat voorspelde patroon ("de steun" van Δ₂,
   Engels: support) vervangt de straf. Hoofdstuk 10 legt uit onder welke voorwaarden dat
   mag.

Hoe weet je of je genoeg metingen hebt? Door een deel van de metingen **achter te houden**
(een fractie f_h, gekozen met een vast zaadje vóórdat er metingen zijn) en te kijken hoe
goed de gevonden Δ₂ die achtergehouden metingen voorspelt. De maat daarvoor is

ρ = (RMS van de fout op de achtergehouden metingen) / (RMS van die metingen zelf),

een dimensieloos getal tussen 0 (perfect) en 1 (niets verklaard; ρ = 1 is precies wat de
lege oplossing Δ₂ = 0 scoort). Naarmate je metingen toevoegt, daalt ρ. Het plan stopt bij
het aantal K waarbij ρ onder een drempel komt die van de gemeten ruis afhangt (§4.5), en
niet bij een van tevoren gekozen aantal. Dat is de zin "K is een meting, geen keuze".

## §4.5 Ruis en de stopregel

Elke gemeten energie heeft een ruis σ_E (§4.3). De symmetrische combinatie van twee
energieën heeft dan ruis σ_E/√2 (de referentie-energie is één gedeelde waarde en telt niet
als extra ruis per patroon; de fout erin wordt apart bepaald en afgetrokken, hoofdstuk 5).
De verhouding van die ruis tot de grootte van de metingen heet de **ruisvloer**:

ρ_noise = σ(R_s) / RMS_resp.

Beter dan de ruisvloer kun je niet fitten. De stopdrempel is daarom een vast veelvoud
ervan: ρ* = c · ρ_noise, met c ≥ 1 een constante die uit de dry run komt en vóór de eerste
echte meting wordt vastgelegd. Twee beveiligingen: als c·ρ_noise ≥ 0,5 is de meting "op
ruisniveau" en wordt er niets teruggevonden (anders zou de lege oplossing slagen); en de
regel wordt pas geëvalueerd nadat het vaste eerste blok van 2M energieën (de ±-stap langs
elke mode afzonderlijk, de diagonaal) is verwerkt. Het aantal daarna, K − 2M, heet
**K_off** en is het getal waar de kostenvraag van hoofdstuk 1 om draait.

## §4.6 Hashes

Een **hash** is een korte vingerafdruk van een bestand of een stuk data: een vaste functie
maakt van willekeurig veel invoer een getal van bijvoorbeeld 64 hexadecimale tekens, zó dat
elke kleine wijziging in de invoer een totaal andere vingerafdruk geeft, en zó dat je uit
de vingerafdruk de invoer niet kunt terugrekenen. Git gebruikt hashes om versies te
identificeren.

Het plan zet een hash op alles wat vooraf vastgelegd moet zijn: de lijst patronen in hun
vaste volgorde (de "deck"), het zaadje van de achtergehouden set, de bevroren orbitalen,
de vaste afspraken in de pilotnotitie. Wie later een patroon toevoegt of de volgorde
verandert, verandert de hash, en de campagne-officier (hoofdstuk 12) weigert dan de
berekening. Zo wordt "we hebben vooraf vastgelegd wat we gaan meten" controleerbaar in
plaats van een belofte.

Het plan gebruikt hashes ook voor **verzegelen**: de negen-puntsfits van de gladheidsprobe
bevatten al de diagonale Δ₂-elementen van naftaleen, en die mogen niet leesbaar zijn
voordat de drempels zijn vastgelegd. De fitcoëfficiënten gaan daarom in een bestand dat
het script weigert te openen zolang de pilotnotitie geen commit-hash heeft. Alleen σ, dat
géén Δ₂-informatie bevat (de residuen staan loodrecht op alles wat de fit vastlegt), wordt
geprint.

## In het kort

Δ₂ is een matrix; elk patroonpaar ±p levert via de symmetrische combinatie R_s één
lineaire vergelijking in haar elementen, waarbij de storende lineaire term Δ₁·p exact
wegvalt. Met een prior (structureel of geleerd) kun je een dunne matrix uit veel minder
vergelijkingen dan onbekenden terugvinden, en met een achtergehouden set meet je wanneer
het genoeg is: K is het aantal energieën waarbij de achtergehouden fout ρ onder c maal de
ruisvloer komt. De ruis σ komt uit residuen van een polynoomfit, gedeeld door n − p en
gepoold over vier modes. Hashes maken vooraf-vastleggen controleerbaar en verzegelen wat
nog niet gelezen mag worden.

*Bron: [Frozen_Ladder_and_Tolerances.md](../GoalGathering/Frozen_Ladder_and_Tolerances.md)
§3 (stopregel, estimator, ±paren, hashes, verzegeling), [Distilled_Project_Plan_and_Quality_Checks.md](../GoalGathering/Distilled_Project_Plan_and_Quality_Checks.md)
§3 (patronen, hold-out, priors), [Research_Note_2026-09-03_Delta_Probing.md](../GoalGathering/Research_Note_2026-09-03_Delta_Probing.md)
(de compressed-sensing-achtergrond).*
