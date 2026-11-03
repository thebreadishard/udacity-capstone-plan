# Hoofdstuk 17 — Totaaloverzicht en woordenlijst

---

## §17.1 De keten in het kort

Het product is één programma, de pijplijn van module 08 (versie 0.9). Het rekent een molecuul
goedkoop door met DFT (B3LYP/6-31G*), telt daar de correctie bij op die het ΔH-netwerk
voorspelt, en rekent uit de gecorrigeerde Hessiaan het spectrum. Bij het spectrum hoort een
certificaat dat per band zegt of de familie van die band is vrijgegeven.

Het ΔH-netwerk (module 05, versie 1.3) leerde de correctie van B3LYP naar ωB97X op 750 moleculen
van het eigen corpus. Het is gemeten op twee groepen moleculen die het nooit zag, hold-out (a) en
hold-out (b). Drie van de vier families blijven daar binnen 3 cm⁻¹ en zijn vrijgegeven; de familie
'other' niet. Die licentie geldt op het proxyniveau. De elf CCSD(T)-ankers zijn de brug naar de
gouden standaard; een licentie op coupled-clusterniveau bestaat nog niet.

Wat "goed" is, komt uit vier lagen (besluit 60). B3LYP/6-31G* is de invoer en blijft dat. ωB97X/6-31G*
is de tussenstap, waarop het netwerk de vorm van de correctie leert. De CCSD(T)-ankers zijn de
ijklaag die zegt wat goed is voor de harmonische correctie. Laboratorium- en sterrenkundige spectra
zijn de controle van buitenaf op de hele keten.

Om die kern staan de andere modules. Modules 02 tot en met 04 bouwen de tegenstanders en de
labwaarheid, module 06 stelt nieuwe moleculen voor, module 07 bewaakt de lange berekeningen, en
module 09 verdedigt het geheel.

## §17.2 De hele keten in één tabel

"Poort" is de controle die moet slagen voordat de uitvoer verder mag.

| Stap | Wie | Erin | Eruit | Poort |
|---|---|---|---|---|
| Tegenstander lezen | M02 | PAHdb v4.00, de berekende bibliotheek van NASA | de opponent-atlas: nette tabellen van berekende banden | — |
| Waarheid bouwen | M03 | PAHdb-experimenteel v3.10 (argonmatrix), NIST-gasfasespectra | het lab-scorebord; de matrix–gasverschuiving per familie; u_band | toets vooraf vastgelegd |
| Goedkope tegenstander | M04 | paren van een labband en een geschaalde PAHdb-band, 83 moleculen | de gekalibreerde kolom en de uitslag dat de restfout spreiding is die de kenmerken niet vangen | recept vooraf vastgelegd; leave-one-molecule-out |
| Corpus | M05 | 1.236 moleculen in vijf lagen (A, A2, B, P3, P3c) | per molecuul de B3LYP-geometrie, de analytische B3LYP- en ωB97X-Hessiaan en de APT | een tweede route voor elke gemarkeerde Hessiaan (besluit 50) |
| Ankers | probes, ankerregister | elf moleculen, van benzeen tot antraceen | CCSD(T)-Hessianen: CCSD(T)/cc-pVDZ plus een MP2-basisstap naar cc-pVTZ; benzeen volledig CCSD(T)/cc-pVTZ | twee tweede routes (besluit 61); één gedragen versie per molecuul (besluit 62) |
| ΔH-netwerk | M05 | 750 corpusmoleculen; hold-outs (a) en (b) apart | versie 1.3 in drie seeds; per molecuul een voorspelde ΔH | early stopping (besluit 51); promotie alleen als beste op beide hold-outs (besluit 57) |
| Licentie | M08 | de evaluatierecords van het gedragen netwerk | per familie vrijgegeven of niet | fout ≤ 3 cm⁻¹ op beide hold-outs (besluit 65) |
| Pijplijn, stap 1–3 | M08 | SMILES of xyz | startgeometrie (RDKit), B3LYP/6-31G*-minimum (psi4), analytische B3LYP-Hessiaan en APT (pyscf); uit het corpus waar het corpus ze precies zo heeft | toelating: neutraal, gesloten schil, aromatisch, alleen C, H, N, O, F, S, Cl |
| Pijplijn, stap 4 | M08 met M05 | de B3LYP-Hessiaan | de gecorrigeerde Hessiaan: B3LYP plus de gemiddelde ΔH van de drie seeds | alleen een gedragen netwerkversie (besluit 55) |
| Pijplijn, stap 5 | M08 | gecorrigeerde Hessiaan, B3LYP-APT | dubbel-harmonisch spectrum en certificaat | licentie per band; gezien of ongezien |
| Anharmonische stap | probes, in aanbouw | DFT-krachtconstanten van derde en vierde orde op niveau G | Δ_anh per band en de geometrieterm | nog niet in de pijplijn |
| Kandidatengenerator | M06 | een bevroren set moleculen uit PubChem | nieuwe moleculen als SMILES | buiten de pijplijn |
| Run steward | M07 | logs van lopende berekeningen | een voorstel uit een gesloten actielijst | deterministische poort en regeltabel |
| Volgordescorer | standout-module (P1) | kenmerken van paren van een molecuul | de volgorde van gedeeltelijke CC-metingen | vastgelegd vóór de hash van het dek (besluit 58) |
| Openbaar | M08, `website/` | de resultaten hierboven | de Spectrum Atlas en de pijplijnshow (42 opgenomen runs) | — |
| Verdediging | M09 | alles | de presentatie | — |

## §17.3 Lessen uit de praktijk

**Les 1: de laptop rekent niet twee dingen tegelijk.** Een naftaleenberekening van 3,5 uur ging
verloren doordat er naast de berekening een tweede klus van 8 GB werd gestart. De berekening liep
in WSL (een Linux-omgeving binnen Windows) en gebruikte 25 van de 31 GB. Windows meldde
geheugentekort en beëindigde de hele virtuele machine. Regel: elke laptoprun noemt vooraf zijn
piekgeheugen, en het startprogramma weigert een run die alle laptopruns samen boven 13 GB brengt.

**Les 2: lange berekeningen moeten kunnen hervatten.** Een berekening die dagen loopt, schrijft elk
tussenresultaat weg zodra het bestaat en slaat bij hervatten over wat al klaar is. De CC-ankers
schrijven zo elke gradiënt apart weg. De regel begon bij de lokale-CC-code van pyscf-forge, die de
resultaten van haar fragmenten alleen in het geheugen hield. De laag eromheen is getest op benzeen:
afgebroken na 2 van 15 fragmenten, hervat, en de energieën waren identiek tot op de laatste cijfers.

**Les 3: een achterhaald resultaatbestand is gevaarlijker dan geen bestand.** In zes documenten
werden getallen aangehaald uit een run die al was vervangen; het doel van benzeen bevatte daarin nog
een rekenfout van 133 cm⁻¹. Een leercurve leek daardoor vlak terwijl ze daalt. Regel: een
resultaatbestand waarvan de invoer later is gecorrigeerd, krijgt bovenaan het woord VERVANGEN, en elk
document dat een curve aanhaalt, noemt het bestand. Voor netwerken geldt hetzelfde: verder werk
draait alleen op een gedragen versie (besluit 55).

**Les 4: een hulpje dat een kopie van een cel uitvoert, kan de echte cel overschrijven.** De
uitvoerder van module 05 mocht alleen cellen toevoegen aan het notebook. Toch verving hij twee
trainingscellen door hun definitie-kopieën. De cellen zijn hersteld uit een eerdere commit.

**Les 5: een controle met geschudde labels vertelt je wat je meetlat meet.** Een model kreeg de
correcties van *andere* moleculen te leren. Het leerde de koppelingen niet; dat is goed, want die
meetlat meet dus leren. Toch halveerde het de frequentiefout, omdat elke klasse van termen een
gemiddelde heeft dat je zonder chemie kunt raden. Die tweede meetlat wordt daarom gelezen tegen
13 cm⁻¹, wat geschudde labels al halen, en niet tegen 23 cm⁻¹, de fout zonder correctie.

**Les 6: een meting van "het model respecteert X" zegt niets zonder dezelfde meting aan het doel.**
Een symmetrietest leek beslissend: spiegelbeeldparen kregen van het paarmodel antwoorden die de helft
van hun grootte uiteenliepen, ver boven de vooraf gestelde grens. Het besluit "het model respecteert de
symmetrie niet" stond binnen een uur in zes documenten. Dezelfde meetlat langs het doel gaf hetzelfde
getal: de klassen waren te grof en het verschil was echte natuurkunde. Met echte symmetriebanen bleek
het model even symmetrisch als zijn doel. Regel: zo'n meting wordt eerst aan het doel gedaan; zonder
die controle is het geen resultaat. De intrekking hoort in dezelfde documenten als de bewering.

**Les 7: een berekening die er goed uitziet, kan de verkeerde berekening zijn.** Zes dagen lang zijn
CCSD(T)-Hessianen berekend met de verkeerde hulpgrootheid. De gradiënt van CCSD(T) heeft een
"lambda" nodig, een tussenuitkomst van de berekening, en de code gebruikte die van CCSD. De aanroep zag er goed uit en de paarcontroles slaagden. De eigen
test van pyscf liet het juiste gebruik al die tijd zien. Twee regels kwamen eruit. Een nieuwe
bibliotheekaanroep in een productieroute noemt de test of het voorbeeld van de makers dat dezelfde
aanroep doet. En elk anker krijgt een tweede route die iets anders meet: de gradiënt wordt vergeleken
met verschillen van de opgeslagen energieën (besluit 61), een controle die een fout van deze grootte
vangt.

**Les 8: een hold-out is pas schoon als je het hebt nagekeken.** Twee moleculen van hold-out (a),
2-naftoëzuur en benzonitril, zaten ook in de training, als tweeling in laag B: hetzelfde molecuul
onder een andere naam. Dat kwam aan het licht toen het certificaat moest zeggen of het netwerk een
molecuul heeft gezien. Op de schone acht moleculen ligt de fout van elke familie 0,04 tot 0,27 cm⁻¹
hoger, en de licentie verandert voor geen enkele familie. Regel: de trainer laat hold-out-tweelingen
standaard weg, en de evaluatie weigert een testset met een tweeling.

**Les 9: hetzelfde molecuul, anders opgeschreven, moet hetzelfde antwoord geven.** Twee schrijfwijzen
van fenantreen verschoven de gecorrigeerde banden van het netwerk tot 2,9 cm⁻¹ (rms 0,65 cm⁻¹), omdat
het antwoord van versie 1.3 afhangt van de volgorde van de atomen. De pijplijn zet daarom elke invoer
eerst in één vaste volgorde, die van de canonieke SMILES. De afhankelijkheid in het netwerk zelf blijft
tot een volgende versie.

## §17.4 Woordenlijst

De Engelse woordenlijst voor de beoordelaars van de school is
[GLOSSARY.md](../modules/GLOSSARY.md); dezelfde termen betekenen hier hetzelfde.

**Anharmonisch** — afwijking van het ideale-veergedrag; verschuift banden meestal een paar procent
omlaag. Het project neemt de anharmonische verschuiving uit DFT (niveau G), niet uit coupled cluster;
de pijplijn rekent nog harmonisch.

**Anker** — een molecuul waarvan het project de CCSD(T)-Hessiaan heeft berekend. Er zijn elf
gedragen ankers; het ankerregister ([ANCHORS.md](../modules/ANCHORS.md)) houdt elke versie bij.

**APT (atomaire polaire tensor)** — hoe het dipoolmoment van een molecuul verandert als een atoom
beweegt. De APT bepaalt de hoogte (intensiteit) van een band.

**Arm A / B / C** — drie manieren om een lokale-CC-energie bij een verplaatste stand te berekenen:
alles bevroren (A), bezette orbitalen overgebracht en virtuele ruimtes vers (B), alles vers (C).

**Atlas (opponent-atlas)** — de tabel van berekende PAHdb-banden van module 02; de tegenstander
waartegen het project zich meet.

**Band, positie, intensiteit** — een piek in het infraroodspectrum; zijn positie is de kleur (in
cm⁻¹), zijn intensiteit de sterkte.

**Basisset** — de verzameling wiskundige functies waaruit orbitalen worden opgebouwd, zoals de
resolutie van een foto. Het project gebruikt 6-31G* voor de DFT-niveaus en cc-pVDZ en cc-pVTZ voor
de ankers. Uitkomsten in verschillende basissets zijn niet direct vergelijkbaar.

**Beat** — een familie waarvan de eigen bandposities aantoonbaar dichter bij het lab liggen dan die
van elke tegenstander, en alleen waar u_band dat kan beslissen.

**Bereikrung** — een trede van de ladder zonder labdata: een spectrum met foutbudget, geen winstclaim.

**Bevroren ruimte** — de orbitaalruimtes van de lokale CC-methode, één keer gekozen en door projectie
overgebracht naar elke verplaatste stand (hoofdstuk 3).

**Certificaat** — wat de pijplijn per molecuul naast het spectrum aflevert: per band de familie en of
die is vrijgegeven, of het netwerk het molecuul heeft gezien, en de ωB97X-waarheid waar het corpus die
heeft. Een molecuul dat de pijplijn niet aanneemt, krijgt een weigering met de reden.

**cm⁻¹ en µm** — twee eenheden voor de positie van een band. 3,3 µm is ongeveer 3.000 cm⁻¹, de
C–H-strek.

**Corpus** — de eigen verzameling moleculen van het project (1.236), in vijf lagen: A (46
handgekozen ouders), A2 (327 afgeleide kinderen), B (743), P3 (60) en P3c (60 kationen).

**Coupled cluster (CC), CCSD(T)** — de nauwkeurige, dure rekenmethode; CCSD(T) heet de "gouden
standaard".

**Dek (deck)** — de vooraf vastgelegde, gehashte lijst patronen van een gedeeltelijke CC-meting, met
alle instellingen.

**Δ, Δ₁, Δ₂, ΔH** — het verschil tussen een betere en een goedkopere methode. Δ₁ is het verschil in
kracht in de goedkope stand, Δ₂ het verschil in Hessiaan. ΔH is Δ₂ zoals het netwerk het voorspelt:
H(ωB97X) − H(B3LYP) op het proxyniveau.

**DFT, B3LYP, ωB97X** — dichtheidsfunctionaaltheorie, de goedkope methode; B3LYP en ωB97X zijn twee
functionalen (recepten) daarbinnen. B3LYP is de invoer van de pijplijn, ωB97X de tussenstap.

**Dry run** — generale repetitie van de meetmachinerie met DFT tegen DFT, die de instellingen van
het meetplan levert.

**Dubbel-harmonisch** — het eenvoudigste model van een spectrum: posities uit de harmonische
Hessiaan, hoogtes uit de eerste afgeleide van het dipoolmoment (de APT).

**Early stopping** — de training houdt een validatieset apart, stopt als die niet meer verbetert, en
bewaart de beste stand (besluit 51).

**Equivariant netwerk** — een netwerk waarvan de uitvoer netjes meedraait als je het molecuul draait
of spiegelt. Het lichaam van het ΔH-netwerk is equivariant.

**Familie** — groep trillingen naar bewegingstype, de eenheid van scoren en vrijgeven. Het netwerk
en de licentie kennen er vier: CH-stretch (C–H-strek, boven 2.800 cm⁻¹), ring-ip (ringtrillingen
in het vlak, 950–1.750 cm⁻¹), CH-oop (C–H-buiging uit het vlak, 600–1.050 cm⁻¹) en 'other' (de rest:
zachte skelettrillingen en trillingen van zijgroepen).

**Gedragen (carried)** — de status van een netwerkversie of anker waar het project tevreden mee is.
Verder werk draait alleen op gedragen versies (besluiten 55 en 62).

**Geometrieterm (eerste-orde)** — ½ Σ φ_iik ΔQ_k: de verschuiving van een frequentie doordat het
betere niveau zijn minimum op een iets andere plek heeft. Nagemeten op 18 moleculen; hoort bij de
anharmonische stap, nog niet in de pijplijn.

**Hash** — vingerafdruk van data; maakt vooraf vastleggen controleerbaar.

**Hessiaan** — de matrix van tweede afgeleiden van de energie naar de atoomposities; bepaalt de
harmonische frequenties.

**Hold-out (a) en (b)** — moleculen die de training nooit ziet. (a): moleculen van laag A die vanaf
het begin apart zijn gezet, zoals benzeen en fenantreen. (b): alle gesubstitueerde moleculen van twee
skeletten, zodat het netwerk op ringskeletten wordt getoetst die het nooit zag.

**Hot band** — verschuiving van een band door thermisch aangeslagen lage trillingen; de reden dat de
temperatuur van een labspectrum in u_band zit.

**Imaginaire frequentie** — een trilling met een negatieve veerconstante; wordt met een minteken
geschreven. In een minimum hoort ze niet voor te komen.

**K, K_off** — K is het aantal dure energieën tot de stopregel van een gedeeltelijke meting; K_off
= K − 2M, het deel buiten de diagonaal.

**Kandidatengenerator** — het netwerk van module 06: een SMILES-Transformer die nieuwe moleculen
voorstelt die het waard zijn om te berekenen; een experiment (0.x) buiten de pijplijn.

**Kostenrecord** — de vaste regel per meting met aantallen, rekentijd, machine en script.

**Lagen van waarheid** — de vier lagen van besluit 60: B3LYP (invoer), ωB97X (tussenstap),
CCSD(T)-ankers (ijklaag), lab en ruimte (controle van buitenaf).

**Licentie** — een vrijgave die op metingen rust, nooit op een aanname. In de pijplijn: een familie
is vrijgegeven waar de seed-gemiddelde fout van het gedragen netwerk op beide hold-outs binnen
3 cm⁻¹ blijft (besluit 65). Onder versie 1.3 zijn ring-ip, CH-stretch en CH-oop vrijgegeven, 'other'
niet.

**Lokale coördinaten** — bindingslengtes, bindingshoeken en torsies in plaats van normale modes.
Het ΔH-netwerk leert de correctie in lokale coördinaten en zet haar daarna om naar de modes
(besluit 49).

**Lokale CC (DLPNO, LNO)** — CC-varianten die verre elektronencorrelatie weglaten en daardoor bijna
lineair schalen; de route voor ankers boven ongeveer 26 atomen.

**M** — het aantal normale modes, 3N − 6.

**Matrixisolatie** — een labspectrum van een molecuul dat bij ongeveer 10 K in argon is ingevroren;
verschoven ten opzichte van gas.

**Mode E / mode G** — een gedeeltelijke CC-meting uit energieën (E) of uit gradiënten (G).

**MP2** — een correlatiemethode die veel goedkoper is dan CCSD(T). De ankers gebruiken het verschil
MP2/cc-pVTZ − MP2/cc-pVDZ als basisstap.

**Netwerk, versie, seed** — een netwerk is een programma met veel instelbare getallen dat een
afbeelding leert uit voorbeelden. Een seed is één trainingsrun; het project traint er drie per
recept. Een versie noemt een recept: 1.x is in productie, 0.x is een experiment
([MODELS.md](../modules/MODELS.md)).

**Normale mode** — een bewegingspatroon waarbij alle atomen met één frequentie trillen.

**Onbeslisbaar door constructie** — een familie waarvan u_band groter is dan de winstmarge; vooraf
verklaard, geen winst en geen verlies.

**Patroon (p), ±paar** — een uitwijkingsvector van alle atomen; gaat altijd als paar +p en −p de
berekening in.

**Pijplijn** — het programma van module 08: een molecuul erin, spectrum en certificaat eruit. Het
heeft een eigen versienummer ([PIPELINE.md](../modules/PIPELINE.md)).

**Pijplijnshow** — een webpagina die de pijplijn als metrokaart met zes stations toont, met
opgenomen runs in hun echte rekentijd en een live-stand op de laptop.

**Pilotnotitie** — het document met alle vooraf vastgelegde getallen van een meting, gecommit vóór
de eerste dure meting.

**Pre-registratie** — vooraf vastleggen wat je meet, hoe je het leest en wat als succes telt, zodat
de uitkomst achteraf niet kan worden gebogen.

**Prior** — de voorkennis die nodig is om uit weinig metingen een grote matrix terug te vinden: de
symmetrie van het molecuul (besluit 11), of de correctie die het netwerk voorspelt.

**Probe** — één dure meting (een ±paar met CC en DFT); ook: elk vooraf omschreven script in
`probes/` dat een getal print.

**Proxyniveau, CC-niveau** — op het proxyniveau worden twee DFT-methoden met elkaar vergeleken om een
methode te oefenen; op CC-niveau wordt vergeleken met coupled cluster.

**R_s, R_a** — de symmetrische combinatie ½[ΔE(+p) + ΔE(−p)] − ΔE(0), die Δ₂ bevat, en de
antisymmetrische ½[ΔE(+p) − ΔE(−p)], die Δ₁ bevat.

**Recovery** — het terugrekenen van Δ₂ uit de antwoorden van de metingen met een prior.

**ρ, ρ_noise, ρ\*** — de fout op achtergehouden metingen; de ruisvloer; de stopdrempel c·ρ_noise.

**Rung, ladder** — de ladder is de eigen lijst testmoleculen van klein naar groot; elke trede is een
rung.

**Run steward** — het programma van module 07 dat lange berekeningen bewaakt, een regeltabel uit
eigen lessen toepast en alleen acties uit een korte lijst mag nemen.

**Scaffold (skelet)** — het ringskelet van een molecuul zonder zijgroepen.

**Schaalfactor** — een getal iets onder één waarmee harmonische DFT-posities worden vermenigvuldigd
om dichter bij metingen te komen; een pleister, geen correctie van de natuurkunde.

**Scorebord** — de tabel van gemeten labbanden met u_band (module 03).

**σ** — de ruis per punt, geschat als √(SSR/(n − p)) uit de residuen van een fit.

**SMILES, canonieke SMILES** — een manier om een molecuul als tekstregel te schrijven; de canonieke
SMILES is de ene vaste schrijfwijze die het programma RDKit kiest.

**Spectrum Atlas** — de openbare website van het project
(https://thebreadishard.github.io/spectrum-atlas/): de corpusmoleculen met hun spectrum, het anker
waar dat bestaat, de gemeten nauwkeurigheid van het netwerk en de licentie.

**Steun (support)** — welke elementen van Δ₂ groot zijn; het eerste doel van module 05, sinds
besluit 49 vervangen door de correctie zelf in lokale coördinaten.

**Tussenstap (stepping stone)** — ωB97X/6-31G*, het niveau waarop het netwerk de vorm van de
correctie leert op de moleculen van het corpus; beoordeeld op hoe weinig de ankers daarna nog moeten
corrigeren.

**u_band** — de gemeten onzekerheid van een labband, met een term voor de temperatuur van het
monster.

**Verzegeld bestand** — een bestand met tussenuitkomsten dat pas opengaat als de drempels zijn
vastgelegd.

**Volgordescorer** — het netwerk van de standout-module (P1, versie 1.0): kiest in welke volgorde
de stukken van een gedeeltelijke CC-meting worden berekend. De geleerde volgordescorer (P2) doet
hetzelfde vanuit het ΔH-netwerk en is een experiment (0.x).

## §17.5 Waar je verder leest

- Het bindende geheel: de [README](../README.md) van plan 05, met de genummerde besluiten, en de
  documenten in `GoalGathering/`, te beginnen met de [Ladder](../GoalGathering/Frozen_Ladder_and_Tolerances.md).
- De pijplijn en haar versies: [PIPELINE.md](../modules/PIPELINE.md); de netwerken:
  [MODELS.md](../modules/MODELS.md); de ankers: [ANCHORS.md](../modules/ANCHORS.md).
- De modules: de mappen in `modules/`, elk met een README en een rubriekchecklist, en de
  [Capstone_Mapping](../GoalGathering/Capstone_Mapping.md).
- Het waarom voor de begeleider: het [Projectvoorstel](../GoalGathering/Projectvoorstel_2026-09-30.md).
- De openbare kant: de Spectrum Atlas en de pijplijnshow op
  https://thebreadishard.github.io/spectrum-atlas/pipeline/.

*Bron: [README.md](../README.md) (besluiten 11, 49–65), [PIPELINE.md](../modules/PIPELINE.md),
[MODELS.md](../modules/MODELS.md), [ANCHORS.md](../modules/ANCHORS.md), [GLOSSARY.md](../modules/GLOSSARY.md),
de README's van de modules 02 tot en met 08, `../TASKS.md` (taken 53, 146, 149, 156) en `../TASKS_closed.md` (taak 157),
de werkregels van de repository over laptopgeheugen en bibliotheekaanroepen, het obstakelregister (lessen 1–6),
en de corpusmap `modules/05_support_predictor/corpus/molecules/`.*
