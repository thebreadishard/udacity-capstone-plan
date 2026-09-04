# Hoofdstuk 5 — De kern: Δ-probing

> **In dit hoofdstuk leer je**
> – hoe één "probe" eruitziet en wat een deck is;
> – hoe K = 2M + K_off is opgebouwd en wat er precies geteld wordt;
> – wat de drie licenties Q6, Q7 en Q8 controleren, in gewone taal;
> – het verschil tussen mode E (energieën) en mode G (gradiënten);
> – wat de pilotnotitie is en waarom ze vóór de eerste echte meting wordt geschreven;
> – hoe het plan de grootste moleculen aanpakt (fragmenten) en onder welke voorwaarden.

---

## §5.1 Eén probe

Een **probe** is één dure meting: het molecuul wordt langs een patroon p uitgewijkt, en
in die stand worden de lokale-CC-energie (met bevroren ruimtes) en de DFT-energie
berekend. Omdat elk patroon als paar ±p gaat, kost één patroon twee CC-energieën; met de
ene gedeelde referentie-energie in het evenwicht levert dat het antwoord R_s(p) van
hoofdstuk 4.

Er zijn twee soorten patronen:

- **Enkelvoudige modes.** Het molecuul wordt langs één DFT-mode uitgewijkt, ±q_s. Dit zijn
  er 2M energieën voor M modes; ze leveren de diagonaal van Δ₂ en vormen altijd het
  eerste blok. In de literatuur heet dit blok "CMA-0" (Concordant Mode Approach, niveau 0):
  een bestaande methode die precies dit doet en niet verder gaat.
- **Meervoudige patronen.** Meerdere atomen tegelijk, zó gekozen dat elke lokale
  omgeving van het molecuul in alle richtingen "aangeraakt" wordt (een constructie
  ontleend aan de O1NumHess-methode), plus expliciete tweemodes-patronen voor de
  koppelingen waarvan de dry run zegt dat ze groot zijn. Deze leveren de informatie over de
  niet-diagonale elementen.

Op elke gescoorde mode komt er nog een tweede amplitude q₂ bij (twee energieën per
gescoorde mode). Die zijn nodig om de fout in de gedeelde referentie-energie te bepalen
(één gedeelde afwijking zou anders elke frequentie dezelfde kant op schuiven), en ze leveren
gratis de kubische bonuswaarde en verwijderen de kwartische vervuiling op die modes. Ze
worden apart geteld, buiten K.

## §5.2 Het deck en de telling

Alle patronen van een rung staan vooraf in een vaste, gehashte lijst: het **deck**. De
volgorde is gehusseld met een vast zaadje, de paren blijven bij elkaar, en een vaste
fractie f_h van de paren is als achtergehouden set gemarkeerd. Niets hiervan mag veranderen
nadat er ook maar één antwoord bekend is.

> **Definitie 5.1 — K en K_off**
> K is het aantal CC-energieën (mode E; een ±paar telt voor twee) dat is verwerkt op het
> moment dat de achtergehouden fout ρ voor het eerst onder ρ* = c·ρ_noise komt. Het eerste
> blok van 2M enkelvoudige energieën zit er altijd in; K_off = K − 2M is het aantal daarna.
> Beide worden geprint, nooit vooraf opgeschreven. Er is een plafond K_cap (uit de dry run,
> vastgelegd in de pilotnotitie); wordt ρ* niet gehaald vóór K_cap, dan luidt het resultaat
> "niet teruggevonden binnen het plafond" en wordt het plafond niet verhoogd.

De **grootte-zin**, het enige dat het plan over kostengroei mag zeggen, is dan letterlijk:
"K_off ging n₁ → n₂ → n₃ van R1 naar R3 terwijl het aantal modes M₁ → M₂ → M₃ ging." Geen
bijvoeglijke naamwoorden. Om de drie rungs eerlijk te vergelijken wordt K_off op de
bewaarde ρ-curven afgelezen bij één gemeenschappelijke drempel (de strengste van de twee
rungs), want ρ* is per rung anders.

## §5.3 Het kostenrecord

Elke rung die heeft gedraaid, levert per mode één regel in een vast formaat, het
**kostenrecord**: K (waarvan 2M diagonaal en K_off daarna), de rung, de mode (E of G), de
prior (structureel of geleerd), σ, de referentiecorrectie c₀, het q₂-blok, RMS_resp,
ρ_noise, c, ρ*, ρ(K), of er extrapolatie is toegepast, de rekentijd per probe op welke
machine, en welk script het printte. Dat record is een wetenschappelijk resultaat op
zichzelf: een beheerder van een spectrendatabank kan ermee uitrekenen wat een molecuul
zou kosten.

## §5.4 Drie licenties

Voordat een teruggevonden Δ₂ een spectrum mag maken, moet het drie controles doorstaan.
Het plan noemt ze **licenties**, met de nummers uit zijn lijst van poortwachters
(Q6, Q7, Q8).

**Q6 — de ankerlicentie: is de dure methode zelf betrouwbaar genoeg?** Drie lijnen.
- *Ruislijn.* Langs vier modes van naftaleen (C–C-strek, C–H-strek, C–H-buiging uit het
  vlak, en één totaalsymmetrische mode) worden negen energieën gemeten, in de armen A en B.
  De gepoolde σ (hoofdstuk 4) moet onder een drempel liggen die uit de kleinste "beat"-marge
  τ volgt: σ_E ≤ 0,82·τ·q_s². De afleiding: de tweede-afgeleide-schatting uit drie punten
  heeft ruis σ_E·√6/q_s², en die mag hoogstens 2τ zijn. Faalt dit, dan is mode E op die
  grootte "boven de ruislijn" en wordt er geen "beat" geclaimd.
- *Biaslijn.* Op benzeen: de bevroren Δ₂ tegen de Δ₂ uit een volledige CCSD(T)-berekening,
  per mode binnen τ. Dit is de enige test die het bevriezen zelf controleert. Of die
  volledige berekening op de laptop past, meet een aparte haalbaarheidsprobe vooraf.
- *Drempellijn.* Twee presets van de lokale methode (Tight en Normal) mogen hoogstens τ
  verschillen; anders is extrapolatie verplicht en tellen alle probes dubbel in de
  kostenclassificatie.

**Q7 — de probinglicentie: vindt de methode terug wat er echt is?** Op benzeen en
naftaleen wordt Δ₂ ook op de klassieke manier berekend (een volledige numerieke Hessiaan,
duizenden energieën, één keer). De teruggevonden Δ₂ moet daar per familie binnen τ₇ mee
overeenkomen; moet aantoonbaar beter zijn dan "niets doen" (Δ₂ = 0) met een vaste factor
d₇; en een controle met door elkaar gehusselde antwoorden moet *mislukken*. Beide
versies (alleen diagonaal, en volledig) worden naast elkaar geprint.

**Q8 — lokaliteit en verzadiging: is Δ₂ echt lokaal en dun?** Op pyreen en coroneen worden
een aantal koppelingen tussen atoomparen *direct* gemeten (vier energieën per paar en
familie, in drie afstandsklassen: gebonden, twee of drie bindingen ver, vier of meer). Die
directe waarden worden vergeleken met wat de teruggevonden Δ₂ zegt (absolute
overeenkomst binnen η₈ maal de schaal van die afstandsklasse), en er wordt gefit hoe snel
de koppeling met de afstand afvalt (de lokaliteitslengte r_c). Verder moet het aandeel van
de correctie dat van verre paren komt, klein zijn (≤ ε₈). En tot slot de verzadiging:
K_off mag van rung naar rung hoogstens met een factor γ groeien. Alle drempels (τ₇, d₇,
η₈, ε₈, γ, de paarlijst) staan vast in de pilotnotitie.

## §5.5 Mode E en mode G

Alles hierboven werkt met **energieën** (mode E): één getal per berekening. Als het
programma ook de **gradiënt** kan geven (de kracht op alle atomen, 3N getallen per
berekening), levert één probe 3N antwoorden in plaats van één; dat heet **mode G** en zou
K drastisch kunnen verlagen. Voor lokale CC met bevroren ruimtes bestond zo'n gradiënt op
3 september 2026 nog niet in een productieversie. Het plan belooft daarom mode E op elke
rung en bouwt mode G in een apart, vooraf geregistreerd **bijproject** met eigen
mijlpalen (hoofdstuk 15). Waar het bijproject een mijlpaal haalt, draait mode G *erbij*, en
de rung krijgt twee kostenrecords.

## §5.6 De pilotnotitie: vastleggen vóór je meet

Alle drempels en instellingen die het resultaat kunnen sturen (c, K_cap, τ₇, d₇, de
Q8-getallen, de Q6-formules met hun getallen, de bandlijsten per molecuul, de marges per
familie) worden in één gedateerde **pilotnotitie** vastgelegd en gecommit **voordat ook maar
één lokale-CC-Δ₂-waarde leesbaar is**. De notitie mag alleen gebaseerd zijn op: de labkant,
de tegenstanders, een DFT-tegen-DFT-generale repetitie van de hele machinerie (de **dry
run**, met een kolom waarin kunstmatige ruis per energie is toegevoegd om c en K_cap af te
lezen), probe M1, de haalbaarheidsprobe, een run/no-run-test van gradiënten in het
evenwicht, en de σ van de gladheidsprobe (met de fits verzegeld). Daarna wordt de notitie
niet meer aangepast. Elke afwijking hiervan heet een deviatie en wordt als zodanig gemeld.

## §5.7 De grootste moleculen: fragmenten en hun licentie

Voor de 432-atomige schijf van R6 is zelfs het eerste blok van 2M = 2580 energieën
onbetaalbaar. Het plan mag Δ₂ daar in **fragmenten** opmeten: ringgesloten,
waterstof-afgesloten stukken die uit de DFT-geometrie van het hele molecuul worden
gesneden, met een straal in ringschillen. Dat is een methode, geen recht, en ze moet haar
**licentie** verdienen met vier metingen:

- (a) Q8 op de directe koppelingen slaagt op R2 en R3 (de correctie is lokaal).
- (b) Op coroneen: Δ₂ uit fragmenten van één schil tegen Δ₂ van het hele molecuul, per
  familie binnen τ₇ — één vergelijking, per familie gescoord op de paren die de
  verschuiving van die familie dragen. Slaagt één schil niet, dan is de licentie
  "in afwachting van (b′)": twee schillen zijn op coroneen niet te testen.
- (b′) Dezelfde vergelijking op circumcoroneen (R4), beloofd op voorwaarde dat het
  rekencluster beschikbaar is.
- (c) Op het interieur van het doelmolecuul zelf: directe koppelingen uit fragmenten met
  straal r_f en r_f + één schil moeten overeenkomen. Dit is de enige test die kan mislukken
  omdat het interieur van de schijf anders is dan alles wat eerder gemeten is.

Faalt een familie op één van de vier, dan wordt die familie uit het R6-certificaat
geschrapt, met het gemeten aandeel erbij. Falen ze allemaal, dan is "R6 niet bereikt" met
de meting erbij het eindresultaat, en dat is een volwaardig resultaat voor module 08.

## §5.8 Wat er gebeurt als het mislukt

Het plan heeft voor elke poort een vooraf geschreven zin. Enkele voorbeelden, in woorden:
"mode E is op deze grootte boven de ruislijn; er wordt geen beat geclaimd; het
kostenrecord is bijgevoegd"; "Δ₂ is niet teruggevonden binnen K_cap; het terugvalspectrum
is gescoord"; "familie F is op deze rung niet lokaal; geen nauwkeurigheidsclaim fijner dan
het gemeten verre aandeel"; "de fragmentlicentie is in afwachting van (b′); R6 is niet
in fragmenten opgemeten". Het plan kan dus op elke rung eerlijk verliezen, en verliezen is
een resultaat, geen schande.

## In het kort

Een probe is een ±paar uitwijkingen met CC en DFT; het deck legt vooraf alle patronen,
hun volgorde en de achtergehouden set vast onder een hash. K telt de CC-energieën tot de
achtergehouden fout onder c maal de ruisvloer komt; K_off = K − 2M is het kostengetal.
Drie licenties bewaken het resultaat: Q6 (is de dure methode glad en onbevooroordeeld
genoeg), Q7 (vindt de methode op kleine moleculen terug wat een volledige berekening
geeft) en Q8 (is Δ₂ lokaal en dun, en verzadigt K_off). Mode E is gegarandeerd; mode G komt
erbij als het bijproject slaagt. Alle drempels staan in een pilotnotitie die vóór de eerste
echte meting wordt gecommit. De grootste moleculen worden in fragmenten opgemeten, maar
alleen onder een licentie van vier metingen, en elke mislukking heeft een vooraf geschreven
uitkomst.

*Bron: [Frozen_Ladder_and_Tolerances.md](../GoalGathering/Frozen_Ladder_and_Tolerances.md)
§1 (kostenrecord, grootte-zin), §3 (alle regels), §4 (pilotnotitie), §5 (stops);
[Distilled_Project_Plan_and_Quality_Checks.md](../GoalGathering/Distilled_Project_Plan_and_Quality_Checks.md)
§7 (Q6–Q8) en §8 (fail-closed zinnen).*
