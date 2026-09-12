# Concept begeleidend bericht bij het voorstel (12 september 2026) — voor de student om te versturen

*Concept, Nederlands; de student past aan en verstuurt zelf. Niets hierin is nieuw ten opzichte van het
voorstel; het wijst alleen de weg erin.*

---

Beste [naam],

Hierbij het projectvoorstel voor mijn capstone, in de versie van 12 september. Het is één document van
ongeveer dertig pagina's; §1 vat het plan in een paar zinnen samen, en die zinnen zijn voor jou
geschreven. De rest is de onderbouwing en het contract waaraan ik mezelf houd.

Wat je aan het eind krijgt, als het plan doet wat het belooft: een pijplijn die van elk afzonderlijk
aromatisch molecuul een infraroodspectrum maakt met een coupled-cluster-anker — een klein aantal dure,
nauwkeurige energieën dat de goedkope DFT-berekening corrigeert — met bij elk spectrum een foutenbudget
per bandfamilie dat zegt of het te vertrouwen is en wat het heeft gekost. Het doel daarvan is niet het
spectrum van naftaleen. De ambitie daarachter — bewust niet beloofd, zie §6 — is een bron van
trainingsdata voor een neuraal netwerk, beter dan geschaald DFT, voor de PAK's waarvoor geen
laboratoriumspectrum bestaat. Sinds Mai et al. (2025) met op DFT getrainde ML-dynamica PAK-spectra
voorspellen, ontbreekt vooral betere trainingsdata dan geschaald DFT. Dat netwerk zelf beloof ik in dit
plan niet: §6 zegt waarom niet, en wat er wel geleverd wordt om het mogelijk te maken — de correctie
zelf, honderden atoompaarblokken (stukjes van de correctie per paar atomen) per molecuul, en de meting
op pyreen en coroneen die vooraf beslist of zo'n overdraagbaar model überhaupt kan bestaan. De
dekkingstabel van §6 is de toets die zegt wanneer de banden van de pijplijn goed genoeg zijn om als
trainingslabels te dienen; is die tabel op orde en is de gemeten reikwijdte kort, dan volgt het netwerk
als gedateerd vervolgvoorstel onder dezelfde licentie als de rest.

Onderweg levert het plan dingen op die je eerder hebt, en vier daarvan liggen er al: de bevinding dat
de PAHdb-bibliotheek zoals ze wordt uitgeleverd de schaalfactoren van versie 3.00 bevat en niet de
drie die het artikel van versie 4.00 beschrijft, een verschil van 4 tot 15 cm⁻¹ op de bandposities;
dat een per band gekalibreerde harmonische bibliotheek, getraind op 2.477 gepaarde matrix- en
rekenbanden van 83 moleculen, niet beter blijkt dan de bibliotheek zelf (6,5 cm⁻¹ gemiddelde
fout); een laboratoriumscorebord voor benzeen en naftaleen met per band gemeten onzekerheden; en de
eerste gemeten matrix–gas-verschuiving per bandfamilie voor naftaleen, antraceen, pyreen en chryseen
(+3 tot +6 cm⁻¹, matrix boven hete damp).

Dat netwerk heb ik op 12 september met naam in het voorstel gezet als het stand-out-werk van dit
project, buiten de reeks van negen modules, met die twee voorwaarden en de verliesvoorwaarde erbij
(§6, beslissing 32) — zodat duidelijk is waar het plan naartoe werkt zonder dat het iets belooft wat
nog niet gemeten is.

Kort hoe het werkt. De coupled-cluster-correctie op de harmonische krachtconstanten reken ik niet
uit maar *meet* ik, met zo weinig mogelijk dure energieën: lokale coupled-cluster-berekeningen
(LNO-CCSD(T)) waarvan ik de orbitaalruimtes één keer kies en daarna bij elke vervorming bevroren houd,
zodat de energieverschillen glad zijn. Het aantal energieën per molecuul staat naast elk spectrum, en
de nauwkeurigheid wordt gescoord tegen laboratoriumdata en tegen de bestaande voorspellingen, waaronder
die van jouw eigen groep, volgens regels die vaststaan voordat er één vergelijking is gemaakt (§7).

Vanaf naftaleen kan dit plan niet meer op mijn eigen machine; het vraagt clustertijd, en ik wil je
kunnen laten zien dat die aanvraag op bewijs rust en niet op hoop. Wat er nu al gemeten is: de kern
van de methode werkt — met bevroren orbitaalruimtes is de lokale-CC-energie langs een vervorming
glad tot 0,002–0,06 µE_h, ruim binnen wat de pijplijn nodig heeft (§3.3), waar de gangbare aanpak,
die de ruimtes bij elk punt opnieuw kiest, bij dezelfde instellingen tot 3 µE_h aan sprongen geeft (en
7–11 µE_h bij de standaarddrempels van het programma), en de systematische afwijking van de
frequenties tegenover canoniek CCSD(T) is +0,11 / −0,01 / +0,23 cm⁻¹ op de drie
geteste modes na de strengste drempels (geprint op 12 september; +0,47 / +0,03 / +0,79 bij de 'tight'-drempels, één decade minder
streng) — klein tegenover de basissetterm van 3–11 cm⁻¹ die het anker sinds beslissing 33 zelf
meedraagt (§3.3); de proefopstelling op DFT-niveau wint de correctie inderdaad terug uit een
eindig aantal vervormingen, en dat aantal is geteld (§3.2); en de lat is bekend en
beweegt niet meer — de best mogelijke goedkope tegenstander, een per band gekalibreerde harmonische
bibliotheek, blijkt op 2.477 gepaarde banden niet beter dan de bibliotheek zelf, 6,5 cm⁻¹
gemiddelde fout, en het scorebord met laboratoriumonzekerheden en de matrix–gas-verschuiving is
uitgeprint voordat er één vergelijking is gemaakt (§7). Wat nog niet gemeten is en alleen met
clustertijd gemeten kán worden: of de correctie bij pyreen en coroneen per bandfamilie onder die lat
komt, en of het aantal energieën ophoudt te groeien met de molecuulgrootte (§4, de kostenvraag; §5.3). Voor allebei
staat de verliesvoorwaarde vooraf op papier, zodat de uitkomst ook bij nee een resultaat is. Zonder
clustertijd valt het project niet om — de opleidingsmodules hangen niet aan de treden van de
grootteladder; benzeen blijft haalbaar op de laptop en naftaleen op de desktop uit de hardwarenotitie
(§12, P13) — maar de claim over de grote moleculen blijft dan ongetest.

Wat ik van je vraag staat in §13. De drie belangrijkste: (1) een kritische lezing van §2–§3 en §7,
de plekken waar de discipline van het plan houdt of niet; (3) of jij gasfase- of jet-gekoelde
spectra kent van pyreen, chryseen en trifenyleen in het 6–15 µm-gebied die mijn zoektocht van
5 september heeft gemist, want die maken de C–C-families op de pyreentrede van de grootteladder beslisbaar; en (5) of je
een clusteraanvraag wilt steunen, gedimensioneerd op de gemeten tijden, en of er binnen jouw
netwerk een geschikte machine is. De genummerde vragen 7–17 zijn voor ons eerste gesprek; ze
veranderen geen regel, ze leveren een getal of een bron.

Twee dingen die ik liever nu zeg dan later. In §7 staat een alinea over jouw dubbele rol:
één tegenstanderslijn (de anharmonische PAHdb-lijn) en één laboratoriumkolom (de jet-gekoelde
3 µm-spectra) zijn werk waar jij coauteur van bent, en het plan zegt hoe het
daarmee omgaat. En §10 bevat 34 genummerde beslissingen die ik zelf heb genomen als methodische
keuzes onder meting; elk daarvan kan door een bezwaar van jou heropend worden, dat is precies
waarvoor ze genummerd zijn.

Alles wat in het voorstel over mijn eigen resultaten staat, is door een script afgedrukt en staat
in de repository; ik stuur je de link graag als je erin wilt kijken.

Hartelijke groet,
Frederic

---

*Checklist voor het versturen:* het xtight-getal is ingevuld (12 september 11:48; `results_m1/XTIGHT_READIN.md`)
en staat gelijkluidend in §1, §3.3, §10 punt 20 en §11 van het voorstel; de pdf of het md-bestand als
bijlage; de repository-link alleen als de student dat wil.
