# Hoofdstuk 8 — Module 03: het lab-scorebord, de matrixverschuiving en u_band

*Udacity-module "Conduct a Statistical Analysis Using Python". In de rubriek Project 2.*

---

## 1. Wat is de vraag?

Laboratoria meten infraroodspectra op twee manieren. In een *matrix* worden de moleculen
ingevroren in vast argon bij ongeveer 10 K (−263 °C): scherp gemeten, maar het argon kan
de banden een beetje verschuiven. In de *gasfase* meet je de damp: dichter bij de
omstandigheden in de ruimte, maar bij de beschikbare bronnen heet en wazig. De vraag van
deze module, vastgelegd vóórdat er één paar was gevormd: **is de verschuiving tussen de
matrixpositie en de gasfasepositie van een band nul, per bandfamilie?** Daarnaast meet de
module per gasfaseband hoe onzeker die positie is (u_band).

## 2. Wat eist de school?

Beschrijvende statistiek, minstens drie figuren ("visuele modellen") en precies één
**hypothesetoets** met hypothesen, toetsingsgrootheid en p-waarde. De dataset is openbaar,
bestond al vóór het project, heeft minstens 500 rijen en 6 kolommen met numerieke én
groeperende variabelen, en is **niet** dezelfde als die van module 02. Het rapport
verklaart de keuze van de toets, leest de resultaten, noemt minstens één beperking en één
bron van bias, en heeft een uitleg voor een niet-technisch publiek. De rubriek noemt
voorbeeldbronnen (Kaggle, UCI, Data.gov); dat is een lijst voorbeelden, geen gesloten poort.

## 3. Invoer

- **PAHdb experimentele bibliotheek v3.10**: 84 soorten, 3.896 banden, gemeten in argon bij
  10 K met 0,9 cm⁻¹ resolutie (Hudgins & Sandford 1998). Ingelezen door de parser van
  module 02.
- **NIST Chemistry WebBook**: acht gasfaserecords van benzeen en vijf PAK's. De
  hoofdbron voor de toets is de GC-IR-reeks van NIST/EPA: hete damp in een verwarmde buis,
  8 cm⁻¹ resolutie. De documentatie van die reeks noemt geen temperatuur; aangenomen is
  250 °C. Daarnaast een dampspectrum van naftaleen bij 245 °C en een benzeencelspectrum.
- **Het kwantitatieve benzeenscorebord**: vier banden uit het NIST-record met 0,125 cm⁻¹
  resolutie (Chu et al. 1999).
- **De hot-band-literatuur** (Joblin et al. 1995): hoeveel cm⁻¹ een band per kelvin
  verschuift, per familie. Een *hot band* is een overgang vanuit een trilling die bij hoge
  temperatuur al aangeslagen is; die ligt iets lager en trekt de gemeten piek mee.

## 4. Bewerking

1. **Eén tabel.** `build_lab_tables.py` voegt alle bronnen samen tot `bands_lab.csv`: één
   rij per laboratoriumband, 4.218 rijen × 31 kolommen.
2. **De toets eerst vastleggen.** `PRE_REGISTRATION.md` is gecommit vóórdat er een paar
   werd gevormd. Daarin staan: hoe een gaspiek wordt gevonden (minstens 5 σ boven de ruis),
   welke matrixband erbij hoort (dezelfde soort, binnen 20 cm⁻¹, de sterkste; één-op-één),
   de grootheid Δ = ν_matrix − ν_gas, de familieregel van module 02, en een minimum van zes
   paren per familie.
3. **De paren.** Vier soorten hebben zowel matrix- als gasfasedata: naftaleen, antraceen,
   pyreen en chryseen. Dat levert 63 paren op de hoofdbron, plus 11 op het naftaleenspectrum
   bij 245 °C, dat apart wordt getoond en niet meetelt.
4. **De toets.** Per familie de Wilcoxon-rangtekentoets: een toets die vraagt of de
   verschuivingen rond nul liggen, zonder aan te nemen dat ze normaal verdeeld zijn.
   Tweezijdig, α = 0,05, met de Holm-correctie omdat dezelfde vraag voor meerdere families
   tegelijk wordt gesteld. Een familie met minder dan zes paren heet *onbeslist door
   constructie*: bij vijf paren kan de kleinste mogelijke p-waarde (0,0625) α niet halen.
5. **u_band per gasfaseband.** De kwadratensom van drie termen: de opgegeven resolutie, de
   precisie van het piekmidden (uit de signaal-ruisverhouding) en een temperatuurterm u_T.
   Voor de hete bronnen is u_T een ondergrens: de hot-band-helling per familie maal het
   temperatuurverschil met 296 K, plus het aandeel tussen 0 en 296 K. De helling komt uit
   Joblin 1995 waar die gemeten is, anders geldt een vloer van 0,044 cm⁻¹ per kelvin.

## 5. Uitvoer

- **Het scorebord** `bands_lab.csv` (object O9 van hoofdstuk 6) en de paren
  `pairs_matrix_gas.csv` (74 rijen).
- **De toetsuitslag** `test_results.json`. Zes van de acht families verwerpen H₀ na de
  Holm-correctie: de matrixbanden liggen 3,3 tot 5,9 cm⁻¹ (mediaan per familie) hoger dan
  de hete gasbanden. De C–H-strek (4 paren) en de laagste trillingen (5 paren) zijn onbeslist
  door constructie. Alle 63 paren samen: mediaan 3,74 cm⁻¹, p ≈ 1,6 · 10⁻¹⁰.
- **u_band per record en familie** (`out/U_BAND.md`, `out/u_band_by_record_family.csv`). Op
  de hete GC-IR-bronnen is u_band 8,6 cm⁻¹ (C–H-buiging in het vlak), 9,6 (C–H uit het
  vlak), 10,2–12,1 (C–H-strek) en 15,9–16,2 cm⁻¹ (de families zonder gemeten helling). Geen
  van de 63 paren is beslisbaar bij een marge van 2 of 5 cm⁻¹; 17 zijn het bij 10 cm⁻¹. De
  benzeenbanden van het kwantitatieve record houden u_band = 2,55 cm⁻¹.
- **Koude kolommen**: jet-gekoelde bandlijsten van tetraceen (34 banden) en coroneen (20
  banden) als aparte, gelabelde kolommen, zonder temperatuurterm.
- **Het notebook** `analysis.ipynb` en het rapport `Statistical_Analysis_Report.pdf`.

Wie gebruikt het? Het certificaat van de pijplijn (module 08) zet bij elke band de
laboratoriumtolerantie u_band van zijn familie, gelezen uit
`u_band_by_record_family.csv`. Module 04 gebruikt dezelfde experimentele bibliotheek als
labkant van zijn koppeltabel.

## 6. Waarom deze module?

Zonder scorebord is er geen meting om tegen te scoren, en zonder u_band weet je niet welke
vergelijkingen eerlijk zijn. De getallen laten zien waar de grens ligt. Op de hete
gasbronnen is de meetonzekerheid 8,6 cm⁻¹ of meer. De doelwaarde voor de fout van het
netwerk is 3 cm⁻¹ per familie (beslissing 53). Die bronnen kunnen een verschil van een paar cm⁻¹ dus niet beslissen; alleen
koude of kwantitatieve bronnen kunnen dat. Dat dit vooraf is opgeschreven en daarna gemeten,
is wat pre-registratie betekent: de verwachting "onbeslist door constructie op de hete bron"
staat in het plan en is nu een getal.

## 7. Waar het kan misgaan — en wat je bij de aftekening controleert

- **Vier moleculen dragen de toets.** Banden van één molecuul zijn niet onafhankelijk. Het
  rapport noemt dat als beperking.
- **Twee effecten door elkaar.** Δ vergelijkt een 10 K-matrix met een hete damp. De
  matrixverschuiving en de hot-band-verschuiving zijn in deze data niet te scheiden; het
  rapport zegt dat.
- **De temperatuur van de hete bron is aangenomen.** De documentatie van de GC-IR-reeks
  noemt geen temperatuur. Elk getal met u_T draagt de aanname 250 °C.
- **Niet de dataset van module 02.** Metingen tegenover berekeningen; notebook en rapport
  zeggen het. Module 02 laadt de experimentele bibliotheek daarom niet.
- **Bronnen buiten de voorbeeldlijst.** NASA en NIST staan niet op de lijst van de rubriek;
  README en rapport noemen elke bron met versie en webadres.
- **Bij het inleveren.** De repository `udacity-statistical-analysis` (`main` plus
  `module-03-lab-scoreboard`) en een vers `requirements.txt` met `pip freeze`.

## 8. In het kort

Module 03 bouwt een tabel van 4.218 gemeten banden, vormt volgens een vooraf vastgelegde
regel 63 paren van matrix- en gasfasebanden en toetst per familie of de verschuiving nul is.
Zes families hebben een verschuiving van 3 tot 6 cm⁻¹, twee hebben te weinig paren. De
module meet ook per band de onzekerheid u_band; op de hete gasbronnen is die 8,6 cm⁻¹ of
meer. Het certificaat van de pijplijn draagt die tolerantie bij elke band.

*Bron: [README.md](../modules/03_lab_scoreboard/README.md),
[PRE_REGISTRATION.md](../modules/03_lab_scoreboard/PRE_REGISTRATION.md),
[PROVENANCE.md](../modules/03_lab_scoreboard/PROVENANCE.md),
[RUBRIC_CHECKLIST_2026-10-03.md](../modules/03_lab_scoreboard/RUBRIC_CHECKLIST_2026-10-03.md),
`notebook/test_results.json` en `out/U_BAND.md` van module 03,
[Rubrics/03](../../../Rubrics/03_Conduct_a_Statistical_Analysis_Using_Python.md).*
