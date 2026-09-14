# Concept begeleidend bericht bij het voorstel (12 september 2026) — voor de student om te versturen

*Concept, Nederlands; de student past aan en verstuurt zelf. Niets hierin is nieuw ten opzichte van het
voorstel; het wijst alleen de weg erin.*

---

Beste [naam],

Hierbij het projectvoorstel voor de Udacity capstone. Het is één document van
ongeveer dertig pagina's; §1 vat het plan in een paar zinnen samen.

Wat je aan het eind krijgt, als het plan doet wat het belooft: een pijplijn die van elk afzonderlijk
aromatisch molecuul een infraroodspectrum maakt met een coupled-cluster-anker — een klein aantal dure,
nauwkeurige energieën dat de goedkope DFT-berekening corrigeert — met bij elk spectrum een foutenbudget
per bandfamilie dat zegt of het te vertrouwen is en wat het heeft gekost. Het doel daarvan is niet het
spectrum van naftaleen. De ambitie daarachter — bewust niet beloofd, zie §6 — is een bron van
trainingsdata voor een neuraal netwerk, beter dan geschaald DFT, voor de PAK's waarvoor geen
laboratoriumspectrum bestaat. Sinds Mai et al. (2025) met op DFT getrainde ML-dynamica PAK-spectra
voorspellen, ontbreekt vooral betere trainingsdata dan geschaald DFT. Dat netwerk zelf beloof ik in dit
plan niet: §6 zegt waarom niet, en wat er wel geleverd wordt om het mogelijk te maken: de correctie
zelf, honderden atoompaarblokken (stukjes van de correctie per paar atomen) per molecuul, en de meting
op pyreen en coroneen die vooraf beslist of zo'n overdraagbaar model überhaupt kan bestaan.

Kort hoe het werkt. De coupled-cluster-correctie op de harmonische krachtconstanten reken ik niet
uit maar *meet* ik, met zo weinig mogelijk dure energieën: lokale coupled-cluster-berekeningen
(LNO-CCSD(T)) waarvan ik de orbitaalruimtes één keer kies en daarna bij elke vervorming bevroren houd,
zodat de energieverschillen glad zijn. Het aantal energieën per molecuul staat naast elk spectrum, en
de nauwkeurigheid wordt gescoord tegen laboratoriumdata en tegen de bestaande voorspellingen, waaronder
die van jouw eigen groep.

Op mijn eigen laptop is het plan haalbaar tot en met benzeen: het proefdek van 448 energieën kost ruim drie weken. Naftaleen is de eerste trede die de laptop niet meer kan: één energie op de instellingen van het anker kost daar 38 uur (gemeten op 14 september), en het volledige dek van 474 energieën dus ruim twee jaar laptoptijd; op vier Snellius-knooppunten is dat naar schatting een maand, op de werkstation-configuratie uit de hardwarenotitie het grootste deel van een jaar. **Boven naftaleen kan geen enkele machine het volledige dek op de basis van het anker betalen**, ook een cluster niet: pyreen zou op vier knooppunten een tot twee jaar kosten, coroneen een veelvoud. Dat is een eigenschap van de dekken, niet van de machines. Of een goedkopere basis met een overgedragen correctie dat verandert, is een vooraf geregistreerde proef en geen aanname; tot die gemeten is, gaat het plan anders om met de grotere moleculen: naftaleen krijgt de volledige, gemeten correctie; pyreen en coroneen krijgen dunne dekken — enkele tientallen energieën per molecuul, genoeg om per bandfamilie te toetsen of de correctie van kleine naar grote moleculen overdraagt, niet genoeg voor het hele spectrum; en het netwerk waar dit alles naartoe werkt wordt getraind op wat betaalbaar gemeten is, met die dunne dekken als toets. De clusteraanvraag waar ik je steun voor vraag is precies op die twee posten gedimensioneerd: één volledig naftaleen-dek en een handvol dunne dekken, samen binnen één kleine Snellius-aanvraag. Wat ik nu al kan laten zien staat in §3.3 en §8: de kern van de methode werkt (bevroren orbitaalruimtes, glad tot 0,002–0,06 µE_h; bias +0,11 / −0,01 / +0,23 cm⁻¹ tegenover canoniek CCSD(T)), de proefopstelling wint de correctie terug uit een geteld aantal vervormingen, en de lat is bekend. Wat nog niet gemeten is en alleen zo gemeten kan worden: of de correctie per bandfamilie overdraagt van naftaleen naar pyreen (de dunne dekken), en wat één gradiënt kost tegenover één energie (deze week, op de laptop) — het getal dat bepaalt of de dunne dekken nog goedkoper kunnen. Voor allebei staat de verliesvoorwaarde vooraf op papier. Zonder clustertijd valt het project niet om — de opleidingsmodules hangen niet aan de treden — maar de claim over de grote moleculen blijft dan ongetest.

*(Alinea vervangen op 14 september 2026, beslissing 36: de oude alinea staat in `Draft_2026-09-14_P26_Revision_and_Cover_Paragraph.md` §1 als "replacement for"; twee correcties bij het overnemen: "ruim drie weken" voor 448 × 76 min = 24 laptopdagen, en de zin over de grotere moleculen voorwaardelijk gemaakt op proef M3.)*

Wat ik van je vraag staat in §13. De drie belangrijkste: (1) een kritische lezing van §2–§3 en §7,
de plekken waar de discipline van het plan houdt of niet; (3) of jij gasfase- of jet-gekoelde
spectra kent van pyreen, chryseen en trifenyleen in het 6–15 µm-gebied die mijn zoektocht van
5 september heeft gemist, want die maken de C–C-families op de pyreentrede van de grootteladder beslisbaar; en (5) of je
een clusteraanvraag wilt steunen, gedimensioneerd op de gemeten tijden, en of er binnen jouw
netwerk een geschikte machine is. De genummerde vragen 7–17 zijn voor ons eerste gesprek; ze
veranderen geen regel, ze leveren een getal of een bron.

Alles wat in het voorstel over mijn eigen resultaten staat, is door een script afgedrukt en staat
in de repository: https://github.com/thebreadishard/udacity-capstone-plan. Naast het voorstel staat daar een
zijstudie (plan 06) naar goedkopere wiskunde voor de dure stap; die belooft niets en heeft een eigen
sluitdatum.

Groetjes,
Frederic

---

*Checklist voor het versturen:* het xtight-getal is ingevuld (12 september 11:48; `results_m1/XTIGHT_READIN.md`)
en staat gelijkluidend in §1, §3.3, §10 punt 20 en §11 van het voorstel; de pdf of het md-bestand als
bijlage; de repository-link alleen als de student dat wil.
