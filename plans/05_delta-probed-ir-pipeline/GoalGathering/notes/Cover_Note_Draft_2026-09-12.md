# Concept begeleidend bericht bij het voorstel (12 september 2026) — voor de student om te versturen

*Concept, Nederlands; de student past aan en verstuurt zelf. Het getal tussen [ ] komt uit de xtight-run
van vanmiddag (`probes/m1_xtight_readin.py`). Niets hierin is nieuw ten opzichte van het voorstel; het
wijst alleen de weg erin.*

---

Beste [naam],

Hierbij het projectvoorstel voor mijn capstone, in de versie van vandaag. Het is één document van
ongeveer dertig pagina's; §1 vat het plan in drie zinnen samen, en die drie zinnen zijn voor jou
geschreven. De rest is de onderbouwing en het contract waaraan ik mezelf houd.

Kort wat het is. Ik bouw een pijplijn die van een aromatisch molecuul een infraroodspectrum maakt,
met een coupled-cluster-correctie op de harmonische krachtconstanten die ik niet uitreken maar
*opmeet* met zo weinig mogelijk dure energieën, en waarvan ik het aantal per molecuul afdruk naast
elk spectrum. Die dure energieën komen uit lokale coupled-cluster-berekeningen (LNO-CCSD(T)) waarvan
ik de orbitaalruimtes bij de evenwichtsgeometrie één keer kies en daarna bij elke vervorming
bevroren houd, zodat de energieverschillen tussen vervormingen glad zijn en niet door de
orbitaalselectie worden verstoord. De accuracy wordt gescoord tegen laboratoriumdata en tegen de
bestaande voorspellingen, waaronder die van jouw eigen groep; de regels daarvoor staan vast voordat
er één vergelijking is gemaakt (§7).

Wat er sinds 6 september is gemeten, en wat het voorstel daardoor anders zegt dan een plan op
papier: het bevriezen van de orbitaalruimtes werkt bij benzeen — de energie langs een vervorming is
glad tot 0,002–0,06 µE_h, en de systematische afwijking van de kromming tegenover canoniek
CCSD(T) is [x] cm⁻¹ na de strengste drempels (§3.3); één lokale-CC-energie van naftaleen kost op mijn
laptop 11,5 uur, dus het eerste echte molecuul kost 5.450 laptopuren en vraagt om een cluster (§8,
§13 punt 5); en het laboratoriumscorebord voor benzeen en naftaleen staat, met gemeten
bandonzekerheden (§7).

Vanaf naftaleen kan dit plan niet meer op mijn eigen machine; het vraagt clustertijd, en ik wil je
kunnen laten zien dat die aanvraag op bewijs rust en niet op hoop. Wat er nu al gemeten is: de kern
van de methode werkt — met bevroren orbitaalruimtes is de lokale-CC-energie langs een vervorming
glad tot 0,002–0,06 µE_h waar de gangbare aanpak, die de ruimtes bij elk punt opnieuw kiest, bij
dezelfde instellingen tot 3 µE_h aan sprongen geeft (en 7–11 µE_h in de kleinere basis), en de systematische
afwijking van de kromming tegenover canoniek CCSD(T) is [x] cm⁻¹, ruim binnen wat de pijplijn
nodig heeft (§3.3); de proefopstelling op DFT-niveau wint de correctie inderdaad terug uit een
eindig aantal vervormingen, en dat aantal is geteld (§3.2); een telling van vanochtend laat zien dat
van de 435 koppelingselementen bij benzeen er maar zes een bandpositie meer dan 0,5 cm⁻¹ bewegen,
dus dat het deck weinig hoeft te vangen om de posities goed te krijgen; en de lat is bekend en
beweegt niet meer — de best mogelijke goedkope tegenstander, een per band gekalibreerde harmonische
bibliotheek, blijkt op 2.477 gepaarde banden niet beter dan de bibliotheek zelf, 6,5 cm⁻¹
gemiddelde fout, en het scorebord met laboratoriumonzekerheden en de matrix–gas-verschuiving is
uitgeprint voordat er één vergelijking is gemaakt (§7). Wat nog niet gemeten is en alleen met
clustertijd gemeten kán worden: of de correctie bij pyreen en coroneen per bandfamilie onder die lat
komt, en of het aantal energieën ophoudt te groeien met de molecuulgrootte (§4, Q8). Voor allebei
staat de verliesvoorwaarde vooraf op papier, zodat de uitkomst ook bij nee een resultaat is. Zonder
clustertijd valt het project niet om — de opleidingsmodules hangen niet aan de rungs, en benzeen en
naftaleen blijven haalbaar — maar de claim over de grote moleculen blijft dan ongetest.

Wat ik van je vraag staat in §13. De drie belangrijkste: (1) een kritische lezing van §2–§3 en §7,
de plekken waar de discipline van het plan houdt of niet; (3) of jij gasfase- of jet-gekoelde
spectra kent van pyreen, chryseen en trifenyleen in het 6–15 µm-gebied die mijn zoektocht van
5 september heeft gemist, want die maken de C–C-families op de pyreenrung beslisbaar; en (5) of je
een clusteraanvraag wilt steunen, gedimensioneerd op de gemeten tijden, en of er binnen jouw
netwerk een geschikte machine is. De genummerde vragen 7–13 zijn voor ons eerste gesprek; ze
veranderen geen regel, ze leveren een getal of een bron.

Twee dingen die ik liever nu zeg dan later. In §7 staat een alinea over belangenverstrengeling:
twee van de tegenstanderslijnen zijn werk waar jij coauteur van bent, en het plan zegt hoe het
daarmee omgaat. En §10 bevat 31 genummerde beslissingen die ik zelf heb genomen als methodische
keuzes onder meting; elk daarvan kan door een bezwaar van jou heropend worden, dat is precies
waarvoor ze genummerd zijn.

Alles wat in het voorstel over mijn eigen resultaten staat, is door een script afgedrukt en staat
in de repository; ik stuur je de link graag als je erin wilt kijken.

Hartelijke groet,
Frederic

---

*Checklist voor het versturen:* [x] invullen uit `results_m1/XTIGHT_READIN.md`; §3.3 en §1 van het
voorstel dragen hetzelfde getal; de pdf of het md-bestand als bijlage; de repository-link alleen als
de student dat wil.
