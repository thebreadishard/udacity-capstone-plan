# Hoofdstuk 7 — Module 02: de opponent-atlas

*Udacity-module "AI Programming Foundations". In de rubriek Project 1.*

---

## 1. Wat is de vraag?

Wat staat er in de openbare NASA-databank met *berekende* infraroodspectra van PAK's
(polycyclische aromatische koolwaterstoffen: platte moleculen van aaneengesloten
koolstofringen)? Deze module leest die databank in tot nette tabellen, schoont ze op en
brengt in kaart welke moleculen erin staan, met welke rekeninstellingen en met welke
schaalfactoren. Die berekende spectra zijn de bestaande voorspellingen waarmee de
pijplijn van dit project wordt vergeleken. Daarom heet de tabel de *opponent-atlas*: de
atlas van de tegenstander.

## 2. Wat eist de school?

Een reproduceerbare verkennende data-analyse **zonder machine learning**: een openbare
tabel van minstens 200 rijen en 5 kolommen inlezen met pandas en NumPy, opschonen met
minstens twee eigen functies, verkennen met minstens één eigen analysefunctie, minstens
drie figuren met titel en benoemde assen, en elke stap toelichten. Het notebook heeft vaste
secties (Setup, Ingestion, Cleaning, EDA, Visualizations, Summary). De README beantwoordt
vier reflectievragen. Er hoort een samenvattend rapport in het APA-7-sjabloon bij. De
rubriek noemt ook de naam van de inlever-repository: `ai-programming-foundations-project`,
met minstens twee branches. Er mag niets getraind worden.

## 3. Invoer

- **PAHdb theoretische bibliotheek v4.00** (NASA Ames). Een XML-download van 503 MB met
  10.749 soorten (een *soort* is een molecuul in één ladingstoestand) en 2.517.399 berekende
  banden. Per soort staan er formule, lading, aantal atomen en de gebruikte rekenmethode in.
  Die methode is B3LYP met de basisset 6-31G* voor de meeste soorten en de grovere 4-31G
  voor de grootste. (Een *basisset* is de verzameling wiskundige functies waarmee de
  elektronen worden beschreven; hoe groter, hoe nauwkeuriger en duurder.) Per band staat
  er ook de *schaalfactor*: een getal net onder 1 waarmee de berekende harmonische
  frequentie is vermenigvuldigd om dichter bij metingen te komen. Het is berekende
  wetenschappelijke data, geen AI-uitvoer.
- **Drie andere vergelijkingslijnen**: de anharmonische PAHdb-bibliotheek 1.00 (lijn B),
  de piekenlijsten van Mai et al. 2025 (lijn C) en de tabel uit de bijlage van Bos et al.
  2025 (de goedkope lijn). De theoretische bibliotheek zelf heet lijn A.
- **De ladder van het oorspronkelijke plan**: een reeks testmoleculen van benzeen via
  naftaleen, pyreen en coroneen tot de reus C₃₈₄H₄₈. De atlas telt per laddermolecuul
  hoeveel vermeldingen elke lijn heeft.

## 4. Bewerking

1. **Inlezen.** Het XML-bestand is te groot om in één keer in het geheugen te laden. Een
   *streaming parser* (`build_opponent_atlas.py`) leest het stuk voor stuk en schrijft een
   soortentabel (één rij per soort, 27 kolommen) en een bandtabel (één rij per band).
2. **Opschonen**, met twee functies. `split_charge_suffix` haalt de lading uit de
   formuletekst (`C54H18-`, `C384H48+2`); zonder die stap telt hetzelfde molecuul meerdere
   keren mee. `flag_unresolved_basis` markeert de 32 soorten waarvan de basisset niet uit
   de beschrijving valt af te leiden, in plaats van ze bij de meerderheid in te delen.
   Isomeren (zelfde formule en lading, ander molecuul) blijven allemaal staan.
3. **Familie-etiket per band**: C–H-strek, C–C-strek, C–H-buiging in en uit het vlak, op
   grond van het frequentiebereik. De XML bevat geen modevectoren (de bewegingspatronen
   van de atomen), dus een preciezere toewijzing kan hier niet.
4. **Verkennen.** De analysefunctie `coverage_summary` telt per laddermolecuul en per
   vergelijkingslijn het aantal soorten. Vijf figuren: soorten naar grootte en lading; de
   schaalfactoren zoals ze in het bestand staan; bandposities per familie; de dekking van
   de ladder; de banden van C₃₈₄H₄₈.

De volledige bandtabel (51 MB) gaat niet mee in de inlevering. Het notebook leest
samenvattingen en steekproeven ervan uit `notebook/bands_derived/`.

## 5. Uitvoer

- **De soortentabel** `species_pahdb_theoretical_4.00.csv` (10.749 rijen × 27 kolommen;
  object O8 van hoofdstuk 6),
  de bandtabel in de repository van het plan, en de soortentabellen van de drie andere
  lijnen.
- **Het notebook** `data_workflow.ipynb` met de vijf figuren, het rapport
  `module_summary.pdf`, en een uitgebreider verslag in `REPORT.md`.

Wat de atlas heeft laten zien:

- **Samenstelling.** Van de 10.749 soorten zijn er 4.479 neutraal, 2.162 kationen, 2.868
  dikationen, 1.231 anionen en 9 trikationen. De grovere basisset 4-31G begint bij 212
  koolstofatomen.
- **De schaalfactoren in het bestand zijn niet die uit het artikel.** Het bestand draagt de
  factoren van versie 3.00 (0,979 / 0,969 / 0,960 voor drie frequentiegebieden). Het artikel
  bij versie 4.00 beschrijft nieuwe factoren (0,964 / 0,979 / 0,975) die in het geleverde
  bestand niet voorkomen. Het verschil is 4 tot 15 cm⁻¹ per band. Beslissing 30 legt vast
  dat lijn A de bibliotheek is zoals geleverd, met een kolom tegen de artikelfactoren
  ernaast.
- **Benzeen ontbreekt** in elke bibliotheek behalve de anharmonische.
- **C₃₈₄H₄₈ staat erin**, neutraal en als dikation, berekend met B3LYP/4-31G (1.290
  trillingen). Het neutrale molecuul is zo symmetrisch dat van zijn 600 bindingen er maar
  56 wezenlijk verschillend zijn (`c384_environments.py`).
- **De bijlage van Bos 2025 bevat 81 soorten**, niet "bijna alle" ruim 4000 waar het
  artikel over spreekt.

Wie gebruikt het daarna? Module 03 gebruikt de familieregel en de experimentele
PAHdb-bibliotheek, die met dezelfde parser is ingelezen. Module 04 koppelt de theoretische
en de experimentele bibliotheek. Module 08 noemt de atlas als de bibliotheek van bestaande
voorspellingen.

## 6. Waarom deze module?

Een voorspelling is alleen "beter" ten opzichte van iets dat al bestaat. Deze tabel maakt
die bestaande voorspellingen per band opvraagbaar, met versienummer en herkomst. De module
liet ook zien hoe kwetsbaar een schaalfactor is: het is een nabewerking achteraf, en de
databank zelf past andere factoren toe dan haar artikel noemt. De pijplijn van dit project
gebruikt geen schaalfactor; de PAHdb-factoren blijven een vergelijkingslijn.

## 7. Waar het kan misgaan — en wat je bij de aftekening controleert

- **Niets trainen.** Het notebook bevat geen model. Een regressie op de banden hoort in
  module 04.
- **De vereiste zin.** README en rapport zeggen dat de data berekende wetenschappelijke
  data zijn, niet AI-gegenereerd, en dat dit de tegenstander van de pijplijn is.
- **Het eerdere concept.** Er bestaat een nooit ingeleverde eerdere versie van deze module
  op de QM9-dataset. Die repository heet nu `draft-qm9-foundations-unsubmitted` en haar
  beschrijving zegt dat ze geen inzending is (beslissing 7). Het rapport noemt dat.
- **Gescheiden datasets.** Module 03 gebruikt de experimentele bibliotheek. Het notebook
  van module 02 laadt die daarom niet; figuur 4 toont alleen de vier berekende lijnen.
- **Bij het inleveren.** De repository `ai-programming-foundations-project` wordt gebouwd
  door `tools/make_module_repo.sh`, dat de eigen geschiedenis van de module meeneemt
  (`main` plus de ontwikkelbranch `module-02-opponent-atlas`). De gebruiker maakt de
  repository aan. `requirements.txt` wordt dan opnieuw gemaakt met `pip freeze` in de
  omgeving waarin het notebook draait.

## 8. In het kort

Module 02 bouwt uit de NASA-databank de tabel van berekende bandposities waartegen de
pijplijn wordt vergeleken: inlezen, opschonen, familie-etiketten en vijf figuren, zonder
machine learning. Ze vond dat het bestand andere schaalfactoren draagt dan het artikel,
dat benzeen ontbreekt en dat C₃₈₄H₄₈ erin staat. De module is af; bij het inleveren
volgen nog de repository en een vers `requirements.txt`.

*Bron: [README.md](../modules/02_opponent_atlas/README.md),
[REPORT.md](../modules/02_opponent_atlas/REPORT.md) §4–§6 en
[RUBRIC_CHECKLIST_2026-10-03.md](../modules/02_opponent_atlas/RUBRIC_CHECKLIST_2026-10-03.md)
van module 02, [REVIEW_2026-10-17.md](../modules/REVIEW_2026-10-17.md),
[Rubrics/02](../../../Rubrics/02_AI_Programming_Foundations_Project.md).*
