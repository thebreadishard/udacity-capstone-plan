# Begeleidend bericht bij het voorstel (27 september 2026, voor het gesprek van maandag 28 september) — voor de student om aan te passen en te versturen

*Concept, Nederlands. Niets hierin is nieuw ten opzichte van het voorstel en zijn gedateerde notities; het wijst alleen de weg erin.
Elk getal staat in de leeskopie of in een resultaatbestand van de repository. Eerdere versies van dit bericht bestaan alleen in de
git-geschiedenis.*

---

Beste [naam],

Dank voor de elf artikelen van 20 september; ze zijn allemaal gelezen en verwerkt, en twee ervan hebben één zin in het voorstel
veranderd (zie hieronder). Hierbij, voor ons gesprek van maandag 28 september, het projectvoorstel voor de Udacity capstone: één
document van ongeveer dertig pagina's. Naast het document staan sinds deze week twee openbare vensters op het werk: de Spectrum
Atlas (https://thebreadishard.github.io/spectrum-atlas/), een catalogus van elk molecuul dat de pijplijn heeft aangeraakt met zijn
status en de herkomst van elk getal, en het labjournaal in blogvorm (https://thebreadishard.github.io/).

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
recept — Mata & Werner beschrijven het in 2006 als de standaardremedie voor numerieke Hessianen; die zin staat sinds 20 september
zo in §3.1. Wat van mij is: LNO-ruimtes hebben geen atoomlijst die je kunt bevriezen, dus ik transporteer ze en meet wat dat kost.
Het aantal energieën per molecuul staat naast elk spectrum, en de nauwkeurigheid wordt gescoord tegen laboratoriumdata en
tegen de bestaande voorspellingen, waaronder die van jouw eigen groep; de getallen van Mackie 2015 en 2016 staan als "lijn B"
in de meetlat.

Wat er gemeten is. Het anker — naftaleen op cc-pVTZ, vijftien energieën van negen tot twaalf uur elk op mijn laptop, sinds
gisternacht negentien — liep van 16 tot 27 september en is voor alle drie de bandfamilies uitgelezen. De vooraf vastgelegde
vraag was of een goedkopere basis (cc-pVDZ, factor tien per energie) de correctie per familie draagt met een constante uit
benzeen. Voor de C–H-uit-het-vlak-familie is het antwoord nee: het increment wisselt van teken (−8,1 tegen +7,9 cm⁻¹), omdat MP2
in een dubbel-zeta-basis juist die bewegingen te slap maakt; de C–H-buiging in het vlak won (+1,2 tegen +1,0 cm⁻¹), de C–C-strek
viel ertussenin (−1,9 tegen −6,0). De goedkope basis is dus per familie vrijgegeven voor één van de drie; de andere twee blijven op
cc-pVTZ met hun gemeten increment in de foutbegroting. Diezelfde negentien punten zeggen hoe schoon de labels zijn: langs de
verdichte trilling liggen ze glad op een curve tot ongeveer 0,04 miljoenste hartree per energie, twee op de honderdduizend van
het signaal; wat een eenvoudige fit eerst als ruis aanzag, was een hogere-orde term van de MP2-bijdrage. En de twee kationen die
in geen enkele kostentabel stonden, hebben nu een gemeten prijs: benzeen⁺ 3.608 s en naftaleen⁺ 34.411 s per energie op een
gehuurde machine met zestien kernen, met de spinverwachting erbij.

Naast het anker draait sinds 19 september een corpus van DFT-paren op gehuurde machines: ruim 450 moleculen hebben beide
Hessianen, waarvan 251 uit de laag met kleine gesubstitueerde aromaten die sinds 25 september wordt aangemaakt voor de
leercurve. Daarop zijn drie dingen gemeten die ik in het gesprek wil laten zien.

Ten eerste hoe het plan werkt als iets misgaat. Een eerste anharmonische berekening van benzeen (B3LYP, VPT2) gaf onbruikbare
getallen. In plaats van de software te vertrouwen heb ik elke anharmonische constante langs twee onafhankelijke routes berekend;
het verschil bleek tot 1.265 cm⁻¹ terwijl het pakket "geen inconsistenties" meldde. De oorzaak — een eindige differentie bovenop
een eindige differentie — heb ik vooraf als voorspelling opgeschreven en daarna met twee tests bevestigd: met analytische
Hessianen zakt het verschil naar 0,1 cm⁻¹ en landen de drie testbanden van benzeen op 851, 1004 en 1324 cm⁻¹ tegen 847, 993 en
1309 gemeten in de gasfase (Goodman, Ozkabak & Thakur 1991). Dezelfde controle vond later een corpus-Hessiaan van benzeen die
133 cm⁻¹ fout was door een kwadratuurrooster. De tweede route is sindsdien een vaste stap, en de verbeteringen aan de gebruikte
pakketten zijn als pull requests ingediend.

Ten tweede waar de correctie leeft. De geleerde laag leerde de verschuiving van elke trilling vanaf de eerste dag, maar de
koppelingen tussen trillingen bij geen enkele datahoeveelheid — tot bleek dat we het verkeerde object vroegen. In de basis van
normaaltrillingen wisselt een koppeling van teken met een willekeurige tekenkeuze die geen kenmerk kan zien; in bindingen en
hoeken is dezelfde correctie dun en lokaal. Gevraagd naar dát object leert hetzelfde netwerk de koppelingen uit 175 moleculen,
ook op ringskeletten die het nooit zag (fout 0,43 en 0,47 van de nulregel, gecorrigeerde frequenties binnen 5 cm⁻¹ tegen 23
zonder correctie). Of de coupled-cluster-correctie in hetzelfde patroon leeft, is op benzeen gemeten (CCSD(T)/cc-pVDZ,
72 gradiënten): 92 % zit in het patroon van diagonaal plus atoomdelende paren, 98 % zodra paren twee bindingen uit elkaar
meetellen. De dure correctie is dus lokaal zoals de goedkope plaatsvervanger, één binding verder. Dezelfde meting voor naftaleen
(dertig gradiënten, symmetriegereduceerd) is dit weekend afgerond en wordt zondagavond uitgelezen. Wat de geometrie betreft:
het dek meet elke methode op de B3LYP-geometrie, de literatuur op het eigen minimum; die geometrieterm is voorspelbaar uit één
gradiënt op het dure niveau en de eigen kubische constanten en zit nu als vaste stap in labelfabriek en pijplijn (de C–H-strekkingen
van benzeen landen ermee op 7 tot 23 cm⁻¹ van CCSD(T)).

Ten derde hoe ver het leren draagt, en wat het meetplan waard is. Drie proxy-toetsen, elk met een vooraf vastgelegde leesregel:
de correctie van een gesubstitueerd molecuul is het blok van zijn moederkern plus de kolommen binnen twee bindingen van de
substituent (een kwart van de kolommen geeft de gecorrigeerde frequenties tot 1,7 cm⁻¹ terug, tegen 23 zonder correctie); dat
buurtblok kan voor elf van de vijftien substituenttypen één keer gemeten en overgezet worden; en een model dat alleen moleculen
tot 26 atomen zag, voorspelt de grotere op 0,59 van de nulregel tegen 0,36 binnen dezelfde grootte. De beslissende leercurve is
vooraf vastgelegd en draait: de kleine-moleculenlaag van 100 tot 1.200 moleculen, drie hold-outs (kale kernen, ongeziene
skeletten, grotere moleculen), leesregel op papier vóór de eerste tabel; het derde punt van die curve (na 45 en 175 moleculen) is
zondagavond gelezen en staat in §3.5. Daarnaast heeft een simulatie op het corpus — zonder nieuwe kwantumchemie, want voor
289 moleculen is de volledige koppelingstabel bekend — het meetplan zelf getoetst: het banddek dat het voorstel beschrijft komt,
volledig gemeten, niet onder een reconstructiefout van 0,5; een kandidatenlijst die elk paar trillingen bereikt haalt 0,08, en een
netwerk dat de volgorde kiest bereikt 0,3 tegen ongeveer 1,35 keer de kosten van het banddek. Die verbreding, de geleerde
volgorde en een stopregel op de meetbare restfout zijn voorgeregistreerd voor na ons gesprek; het dek in het voorstel staat nog
zoals het was, met zijn eerlijke eindpunt.

Wat dit alles niet is: een oordeel over het netwerk. Het leert (diagonaal, koppelingen op ongeziene skeletten, overdracht naar
grotere moleculen), de labels zijn schoon en geprijsd, en de eerste toetsen slagen; of het genoeg leert, beslist de leercurve bij
1.200 moleculen en daarna de echte coupled-cluster-labels. Een geleerde molecuulrepresentatie (een equivariant model, gebouwd
en getest) staat naast het paarmodel klaar met een vooraf vastgelegde vergelijking, en een eerlijke-kans-regel verbiedt een
negatieve zin over welk model dan ook voordat de geregistreerde zoektocht over recept, verliesfunctie, capaciteit, data en
voortraining is doorlopen.

Op mijn eigen laptop is het plan haalbaar tot en met benzeen: het proefdek van 448 energieën kost ruim drie weken. Naftaleen is
de eerste trede die de laptop niet meer kan: één energie op de instellingen van het anker kost daar 38 uur (gemeten 14 september),
het dek van 291 energieën dus ruim een jaar laptoptijd; op vier Snellius-knooppunten is dat naar schatting een maand. Op een
gehuurde machine met zestien kernen kost een LNO-CCSD(T)/cc-pVDZ-energie van een molecuul van 25 atomen meer dan negen uur, en die
van het naftaleenkation 9,6 uur; voor gesubstitueerde moleculen is dus een goedkopere correlatietrap nodig, waarvan de nauwkeurigheid
op benzeen tegen canoniek CCSD(T) gemeten wordt vóór hij labels levert. Daarom staat de clusteraanvraag in §12 en §13.

Wat ik van je vraag staat in §13. De drie belangrijkste: (1) een kritische lezing van §2–§3 en §7, de plekken waar de discipline
van het plan houdt of niet; (3) of jij gasfase- of jet-gekoelde spectra kent van pyreen, chryseen en trifenyleen in het
6–15 µm-gebied die mijn zoektocht van 5 september heeft gemist, want die maken de C–C-families op de pyreentrede beslisbaar; en
(5) of je een Snellius-aanvraag wilt steunen, gedimensioneerd op de gemeten tijden, en of er binnen jouw netwerk een geschikte
machine is. Twee kleine vragen kwamen uit de artikelen: (14) of de naftaleen-QFF op CCSD(T)/cc-pVTZ die het artikel van 2015 als
"net haalbaar, in bewerking" noemt ooit is gepubliceerd — dat zou mijn enige coupled-cluster-referentie boven benzeen zijn; en
(18) welke referentie jij vertrouwt voor de kationen: het artikel van Esposito e.a. uit 2024 rekent fenantreen⁺, pyreen⁺ en
pentaceen⁺ met dezelfde machinerie, maar zegt niets over spincontaminatie van de open-schil-referentie, en mijn kationlabels
hangen daaraan (de gemeten ⟨S²⟩ van benzeen⁺ en naftaleen⁺ breng ik mee). De overige genummerde vragen zijn voor het gesprek;
ze veranderen geen regel, ze leveren een getal of een bron.

Alles wat in het voorstel over mijn eigen resultaten staat, is door een script afgedrukt en staat in de repository:
https://github.com/thebreadishard/udacity-capstone-plan; de atlas en het labjournaal hierboven lezen uit dezelfde bestanden.

Groetjes,
Frederic

---

*Checklist voor het versturen:* de laag-B-lezing van zondagavond staat in §3.5 van de leeskopie en de zin erover hierboven noemt het
getal; het E8-naftaleenresultaat staat in §3.5 zodra het gelezen is; instelling en rol in de kop ingevuld; de pdf of het md-bestand
als bijlage; de repository-link alleen als de student dat wil.
