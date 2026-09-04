# Hoofdstuk 8 — Module 03: het lab-scorebord, de matrixtolerantie en u_band

*Udacity-module "Conduct a Statistical Analysis Using Python". In de rubriek Project 2.*

---

## 1. Wat is de vraag?

Verzamel alle bruikbare *gemeten* bandposities van de laddermoleculen in één tabel, meet
per band hoe onzeker die positie is, en toets per bandfamilie of matrixspectra
systematisch verschoven zijn ten opzichte van gasspectra.

## 2. Wat eist de school?

Beschrijvende statistiek plus minstens één **hypothesetoets**, op een openbare dataset
die vóór de module beschikbaar was, met minstens 500 rijen en 6 kolommen, numerieke én
groeperende variabelen, en **niet** dezelfde dataset als module 02. De rubriek noemt
voorbeeldbronnen (Kaggle, UCI, Data.gov); die lijst is volgens de repo-leesnotitie een
lijst voorbeelden, geen gesloten poort. De toets moet vooraf worden vastgelegd.

## 3. Invoer

- **PAHdb experimentele bibliotheken**: v3.10 (84 soorten, matrixisolatie in argon bij
  ongeveer 10 K) en de gasfasebibliotheek v1.00.
- **NIST WebBook**: JCAMP-bestanden per CAS-nummer (benzeen, naftaleen, pyreen, chryseen,
  trifenyleen). Voor de R2-moleculen zijn dat GC-IR-spectra van hete damp, gehomogeniseerd
  tot 8 cm⁻¹; voor naftaleen een dampspectrum bij 245 °C en een GC-IR-vermelding; voor
  benzeen twintig kwantitatieve celspectra bij 0,125–1,93 cm⁻¹.
- **PNNL/NWIR**: het kwantitatieve dampfasespectrum van naftaleen bij 25 °C en 0,1 cm⁻¹
  (gevonden in de laatste review; genoemd vóór deze module iets print, zoals de
  niet-verwisselregel eist).
- **De documentatie van die bronnen** (bibliografie-items 50, 56, 57, 59): daarin staan
  de meetcondities (temperatuur, resolutie) die het JCAMP-bestand zelf vaak niet noemt.
- **De hot-band-literatuur** (items 52–53, 60): hoeveel cm⁻¹ per kelvin een band
  verschuift, per familie. Nog niet gelezen; de eerste literatuurschuld die betaald wordt.
- **De parser en cache uit plan 02 en 04** (in de git-geschiedenis).

## 4. Bewerking

1. Alle bronnen inlezen tot één tabel met dezelfde kolommen (object O9).
2. Per gasfaseband **u_band** bepalen: de kwadratensom van (i) de opgegeven resolutie uit de
   documentatie (nooit de puntafstand van het bestand), (ii) de centroïde-precisie uit de
   signaal-ruisverhouding, en (iii) de temperatuurterm u_T: een vastgepinde
   hot-band-correctie met ±30 %, of, zolang die er niet is, de vloer
   χ_max·(T_bron − 296 K) + u_296 met χ_max = 0,03 cm⁻¹/K (herinnerd, wordt vervangen) en u_296
   het 0 → 296 K-aandeel per molecuul (1 / 3 / 5 cm⁻¹ voor benzeen / naftaleen / R2-soorten,
   schattingen). Een bron zonder opgegeven temperatuur krijgt die uit de documentatie van
   haar reeks; is die er ook niet, dan geldt "heet".
3. Per familie het **beslisbaarheidsoordeel**: gas-beslisbaar als u_band kleiner is dan de
   beat-marge van die familie; anders onbeslisbaar door constructie. Matrixdata gaat door de
   matrix–gas-poort van stap 4.
4. De **vooraf vastgelegde toets**: per familie "de matrix-naar-gas-verschuiving is nul",
   tweezijdig, met vooraf gekozen α; "onbeslist" is een toegestane uitkomst. Het resultaat is
   de gemeten **matrixtolerantie** per familie.
5. Beschrijvende statistiek per familie en fase, met figuren.

## 5. Uitvoer

- **O9, het scorebord**: CSV met `bron, identifier, molecuul, fase, bronklasse,
  temperatuur, resolutie, bandpositie, centroïde-precisie, u_T, u_band, familie, oordeel`.
- **De matrixtolerantie per familie** met toetsuitslag: pilotnotitie-item 4.
- **De bandlijst per molecuul met oordelen**: pilotnotitie-item 1; de marges: item 2.
- **Een provenance-kolom**: per spectrum de bronklasse (cel / dampcel / GC-IR), de
  opgegeven temperatuur en resolutie — zodat de herkomst een kolom is en geen voetnoot.

Verwachting, vooraf opgeschreven: R0 en R1 beslisbaar in alle families op hun
kamertemperatuurbronnen (de hete naftaleenvermeldingen als aparte, gelabelde kolommen);
de C–C-families van R2 onbeslisbaar door constructie op de hete GC-IR-bron, tenzij een
hot-band-correctie wordt vastgepind.

Wie gebruikt het? De pilotnotitie (items 1, 2, 4), module 04 (de labkant van de
koppeltabel), module 08 (de score), en de campagne-officier, die een "beslisbaar"-oordeel
zonder u_band weigert.

## 6. Waarom deze module?

Zonder scorebord is er geen waarheid om tegen te scoren, en zonder u_band kan het plan
niet zeggen welke vergelijkingen eerlijk zijn. De temperatuurterm is bovendien de plek
waar het plan in de laatste twee reviews het meest is bijgesteld: eerst leek naftaleen
alleen als hete damp beschikbaar, waardoor R1 per familie zou moeten worden gescoord; toen
bleek er een kamertemperatuurspectrum te bestaan. Dat dit vóór de meting is uitgezocht en
opgeschreven, is precies wat pre-registratie betekent.

## 7. Waar het kan misgaan — en wat je bij de aftekening controleert

- **Bronnen buiten de voorbeeldlijst.** NASA en NIST staan niet op de rubrieklijst. Het
  rapport moet de DOI's noemen en in één zin zeggen dat de lijst voorbeelden bevat, geen
  gesloten poort (zoals de repo-leesnotitie vastlegt).
- **Rijen en kolommen.** ≥ 500 rijen en ≥ 6 kolommen moeten aantoonbaar gehaald worden
  vóórdat de module begint; tel het na in de gecombineerde tabel.
- **De toets vooraf.** De vorm van de toets (welke grootheid, tweezijdig, α) moet in een
  gedateerd document staan voordat de data worden samengevoegd.
- **Niet dezelfde data als module 02.** Metingen versus berekeningen: het rapport zegt het
  expliciet.
- **De schuld eerst.** u_band mag pas worden geprint als items 52–53 (hot-band-hellingen)
  en 56–57, 59 (meetcondities van de R0- en R1-bronnen) zijn gelezen. Zonder dat is de
  temperatuurterm een schatting en het oordeel voorlopig.
- **De vraag aan de begeleider.** Voor de C–C-families van de R2-moleculen bestaat geen
  kamertemperatuurbron in het 6–15 µm-gebied; het voorstel vraagt de begeleider daarom om
  hulp bij het vinden van gasfase- of jet-gekoelde spectra. Dat is dragend, geen
  beleefdheid.

## 8. In het kort

Module 03 bouwt de tabel van gemeten bandposities, meet per band de onzekerheid u_band
(resolutie, centroïde, temperatuur) en toetst vooraf vastgelegd of matrixspectra verschoven
zijn. Het levert drie van de dertien onderdelen van de pilotnotitie en beslist welke
vergelijkingen het plan eerlijk kan aangaan.

*Bron: [Capstone_Mapping.md](../GoalGathering/Capstone_Mapping.md) §3 (Module 03),
[Frozen_Ladder_and_Tolerances.md](../GoalGathering/Frozen_Ladder_and_Tolerances.md) §2
(beslisbaarheid, temperatuurterm, R0/R1-rijen), [probes/README.md](../probes/README.md)
probe 2a, [Relevant_Scientific_Papers.md](../GoalGathering/Relevant_Scientific_Papers.md)
items 50–60, [Rubrics/03](../../../Rubrics/03_Conduct_a_Statistical_Analysis_Using_Python.md).*
