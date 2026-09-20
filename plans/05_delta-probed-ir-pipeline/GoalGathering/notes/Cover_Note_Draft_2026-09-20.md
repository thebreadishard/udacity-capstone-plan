# Concept begeleidend bericht bij het voorstel (20 september 2026, voor het gesprek van maandag 28 september) — voor de student om aan te passen en te versturen

*Concept, Nederlands. Vervangt het concept van 12 september (dat blijft staan als geschiedenis). Niets hierin is nieuw ten
opzichte van het voorstel en zijn gedateerde notities; het wijst alleen de weg erin. Elk getal staat in de leeskopie of in een
resultaatbestand van de repository.*

---

Beste [naam],

Dank voor de elf artikelen van vandaag; ze zijn allemaal gelezen en verwerkt, en twee ervan hebben één zin in het voorstel
veranderd (zie hieronder). Hierbij, voor ons gesprek van maandag 28 september, het projectvoorstel voor de Udacity capstone.
Het is één document van ongeveer dertig pagina's.

Wat je aan het eind krijgt, als het plan doet wat het belooft: een pijplijn die van elk afzonderlijk aromatisch molecuul een
infraroodspectrum maakt met een coupled-cluster-anker — een klein aantal dure, nauwkeurige energieën dat de goedkope
DFT-berekening corrigeert — met bij elk spectrum een foutenbudget per bandfamilie dat zegt of het te vertrouwen is en wat het
heeft gekost. Het doel daarvan is niet het spectrum van naftaleen. De ambitie daarachter — bewust niet beloofd, zie §6 — is een
bron van trainingsdata voor een neuraal netwerk dat de correctie per bandfamilie voorspelt voor de PAK's waarvoor geen
laboratoriumspectrum bestaat. Jouw groep sloot in 2016 af met de hoop dat de anharmonische effecten zich over de PAK-familie
laten generaliseren zonder voor elk molecuul een volledig krachtveld te rekenen (Mackie et al. 2016, slotparagraaf); dit plan is
één antwoord op die hoop, met de kanttekening dat het netwerk in §6 een voorwaardelijk doel is en de gemeten correctie het
beloofde product.

Kort hoe het werkt. De coupled-cluster-correctie op de harmonische krachtconstanten reken ik niet uit maar *meet* ik, met zo
weinig mogelijk dure energieën: lokale coupled-cluster-berekeningen (LNO-CCSD(T)) waarvan ik de orbitaalruimtes één keer kies
en daarna naar elke vervorming meeneem, zodat de energieverschillen glad zijn. Het bevriezen van zulke ruimtes is een bekend
recept — Mata & Werner beschrijven het in 2006 als de standaardremedie voor numerieke Hessianen; die zin staat sinds vandaag zo
in §3.1. Wat van mij is: LNO-ruimtes hebben geen atoomlijst die je kunt bevriezen, dus ik transporteer ze en meet wat dat kost.
Het aantal energieën per molecuul staat naast elk spectrum, en de nauwkeurigheid wordt gescoord tegen laboratoriumdata en
tegen de bestaande voorspellingen, waaronder die van jouw eigen groep; de getallen van Mackie 2015 en 2016 staan nu als
"lijn B" in de meetlat.

Wat er sinds het concept van 12 september gemeten is. Het anker — naftaleen op cc-pVTZ, dertien energieën van twaalf uur op
mijn laptop — loopt sinds 16 september; vanavond kwam de eerste van drie bandfamilies binnen. De vooraf vastgelegde vraag was
of een goedkopere basis (cc-pVDZ, factor tien per energie) de correctie per familie draagt met een constante uit benzeen. Voor
de C–H-uit-het-vlak-familie is het antwoord nee: het increment wisselt van teken (−8,1 tegen +7,9 cm⁻¹), omdat MP2 in een
dubbel-zeta-basis juist die bewegingen te slap maakt. Voor die familie blijft het anker dus cc-pVTZ; de twee families in het
vlak volgen dinsdag en donderdag, het rapport vrijdag. Daarnaast draait sinds gisteren op vier gehuurde machines een corpus van
DFT-paren (45 moleculen klaar, 200 in aanmaak, 868 gepland) waarop de eerste leercurves zijn gemeten: de C–H-families leren
snel, de ringfamilie niet, en de reden bleek dat een label per modus daar slecht gedefinieerd is — sindsdien is het doelobject
het hele familieblok. Dat is de stand; niets ervan is een oordeel over het netwerk.

Op mijn eigen laptop is het plan haalbaar tot en met benzeen: het proefdek van 448 energieën kost ruim drie weken. Naftaleen is
de eerste trede die de laptop niet meer kan: één energie op de instellingen van het anker kost daar 38 uur (gemeten 14 september),
het dek van 291 energieën dus ruim een jaar laptoptijd; op vier Snellius-knooppunten is dat naar schatting een maand. Daarom
staat de clusteraanvraag in §12 en §13.

Wat ik van je vraag staat in §13. De drie belangrijkste: (1) een kritische lezing van §2–§3 en §7, de plekken waar de discipline
van het plan houdt of niet; (3) of jij gasfase- of jet-gekoelde spectra kent van pyreen, chryseen en trifenyleen in het
6–15 µm-gebied die mijn zoektocht van 5 september heeft gemist, want die maken de C–C-families op de pyreentrede beslisbaar; en
(5) of je een Snellius-aanvraag wilt steunen, gedimensioneerd op de gemeten tijden, en of er binnen jouw netwerk een geschikte
machine is. Twee kleine vragen kwamen uit de artikelen van vandaag: (14) of de naftaleen-QFF op CCSD(T)/cc-pVTZ die het artikel
van 2015 als "net haalbaar, in bewerking" noemt ooit is gepubliceerd — dat zou mijn enige coupled-cluster-referentie boven
benzeen zijn; en (18) welke referentie jij vertrouwt voor de kationen: het artikel van Esposito e.a. uit 2024 rekent fenantreen⁺,
pyreen⁺ en pentaceen⁺ met dezelfde machinerie, maar zegt niets over spincontaminatie van de open-schil-referentie, en mijn
kationlabels hangen daaraan. De overige genummerde vragen zijn voor het gesprek; ze veranderen geen regel, ze leveren een getal
of een bron.

Alles wat in het voorstel over mijn eigen resultaten staat, is door een script afgedrukt en staat in de repository:
https://github.com/thebreadishard/udacity-capstone-plan, met een openbaar labjournaal in blogvorm.

Groetjes,
Frederic

---

*Checklist voor het versturen:* de datum in de kop van de leeskopie is 28 september; het B1-verdict van vrijdag is ingevuld op de
plek van de marker in §3.5 (de eerste familie staat er al als gedateerde notitie); instelling en rol in de kop ingevuld; de pdf of
het md-bestand als bijlage; de repository-link alleen als de student dat wil.

*Wat dit concept toevoegt ten opzichte van 12 september:* de dank voor de artikelen en de zin over Mata & Werner (§3.1 herschreven
20 september); de stand van het anker met de eerste familie (20 september 18:43) en van het corpus; de vragen 14 en 18 in concrete
vorm; het dek van 291 in plaats van 474 energieën (besluit 37). Plan 06 en zijn annex worden in de brief niet genoemd (de gebruiker, 20 september).
