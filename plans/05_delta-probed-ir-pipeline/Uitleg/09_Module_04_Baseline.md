# Hoofdstuk 9 — Module 04: de gekalibreerde goedkope tegenstander

*Udacity-module "Applied Machine Learning". In de rubriek Project 3.*

---

## 1. Wat is de vraag?

Kan een klassiek machine-learningmodel de fout voorspellen die de geschaalde berekende
spectra van NASA (de atlas van module 02) maken ten opzichte van laboratoriummetingen,
alleen uit kenmerken van de band en het molecuul? Als dat lukt, is de gecorrigeerde
bibliotheek de sterkste eerlijke goedkope tegenstander voor de pijplijn. Het antwoord van
de module is **nee**: wat er na de schaalfactor overblijft, is spreiding van band tot band
die deze kenmerken niet vangen.

## 2. Wat eist de school?

Een volledige klassieke ML-workflow: het probleem formuleren (begeleid of onbegeleid),
inlezen en inspecteren, voorbewerken, minstens één model trainen met scikit-learn of
PyTorch, evalueren met passende metrieken, een notebook met samenvatting en een rapport met
citaties. De dataset is openbaar, niet synthetisch of AI-gegenereerd, en **niet dezelfde
als die van module 02 of 03**. Beoordeeld wordt onder meer: het notebook draait van boven
naar beneden; de metriek past en wordt gemotiveerd; de resultaten worden gelezen; minstens
één beperking en één bron van bias met een genomen maatregel; een rapport voor technisch én
niet-technisch publiek.

## 3. Invoer — de datastructuur in detail

**De trainingstabel** `training_table.csv` (object O10 van hoofdstuk 6): 2.477 rijen × 28
kolommen. Elke rij is een
paar van een gemeten band (PAHdb experimenteel v3.10, argonmatrix) en een berekende band
(PAHdb theoretisch v4.00) van hetzelfde molecuul. Van de 84 experimentele soorten komen er
83 in de theoretische bibliotheek voor. De koppeling gebruikt het PAHdb-nummer (`uid`) van
de soort.

| Kolom | Type | Rol in het model |
|---|---|---|
| uid, molecuul | tekst | groepering voor de splitsing |
| ongeschaalde harmonische frequentie | getal (cm⁻¹) | kenmerk |
| log₁₀ van de berekende intensiteit, relatieve intensiteit | getallen | kenmerk |
| schaalfactorgebied (drie gebieden), familie | categorieën | kenmerk |
| aantal C, aantal H, lading, stikstof ja/nee | getallen | kenmerk |
| aantallen H-buren (solo, duo, trio, kwartet) | getallen | kenmerk |
| labpositie | getal (cm⁻¹) | — |
| **y = labpositie − geschaalde berekende positie** | getal (cm⁻¹) | **doelvariabele** |

Het is dus **begeleid leren, regressie**. Geen enkele labgrootheid is een kenmerk.

**Het recept** (`RECIPE.md`) is vastgelegd en gecommit vóór de eerste trainingsrun: de
doelvariabele, de koppelregel, de kenmerken, vier modellen, de evaluatie, de metrieken,
geen afstemming van hyperparameters, en zaadje 0 (de startwaarde van de
toevalsgenerator, zodat elke run hetzelfde uitkomt).

**Openbaarheid.** De tabel koppelt twee openbare PAHdb-bibliotheken. Ze staat sinds
12 september 2026 openbaar in de repository van het plan en gaat mee in de
inlever-repository; dat voldoet aan de eis "openbaar beschikbaar" van de rubriek. Een
aparte Zenodo-uitgave met DOI is daarom niet nodig (besluit van de gebruiker).

## 4. Bewerking

1. Inlezen en inspecteren; de tabel heeft geen ontbrekende waarden.
2. Voorbewerking: standaardisering van de getallen en één-hot-codering van de categorieën
   voor het lineaire model; ruwe kenmerken voor het boommodel.
3. **Splitsing per molecuul** ("leave-one-molecule-out", 83 rondes): alle banden van één
   molecuul zitten óf in de training óf in de test. Anders leert het model een molecuul
   herkennen in plaats van een fout voorspellen.
4. Vier modellen naast elkaar: het **nulmodel** (de bibliotheek zoals geleverd, y = 0; dat
   is lijn A), een **constante per familie** (het gemiddelde y van de familie in de
   trainingsset), **ridge-regressie** (lineair met een straf op grote coëfficiënten) en
   **gradient-boosted trees** (`HistGradientBoostingRegressor`).
5. Evaluatie met de **MAE** (gemiddelde absolute fout, in cm⁻¹) als hoofdmaat, met RMSE, R²
   en het aandeel binnen 5 cm⁻¹ ernaast; per familie en per laddermolecuul.

## 5. Uitvoer — de datastructuur in detail

**De uitslag** (`model_results.json`), MAE op de weggelaten moleculen:

| Model | MAE (cm⁻¹) |
|---|---|
| nulmodel (lijn A) | 6,49 |
| constante per familie | 6,43 |
| ridge-regressie | 6,40 |
| gradient-boosted trees | 6,48 |
| gradient-boosted trees met early stopping | 6,34 |

De R² blijft overal onder 0,02: geen model verklaart een noemenswaardig deel van de fout.
De rij met early stopping is een vervolgrun onder beslissing 51 (*early stopping*: het
trainen stopt als de fout op een aparte validatieset niet meer daalt). De getallen van de
eerste run blijven ernaast staan.

**De basislijn.** Volgens de regel van het recept wint het model met de laagste MAE, en bij
een gelijkspel het eenvoudigste. De gebruiker koos ridge: het verschil met de bomen
(0,06 cm⁻¹) valt binnen de ruis, net als het verschil met niets doen.

**Twee tabellen**: `opponent_column_ladder.csv` (de gekalibreerde posities van de
testmoleculen, telkens voorspeld door een model dat dat molecuul niet zag) en
`uncertainty_layer.csv` (een verwachte fout met spreiding per band). Verder het notebook
`modeling.ipynb` en het rapport `Machine_Learning_Analysis_Report.pdf`.

## 6. Waarom deze module?

Een vergelijking met een zwakke tegenstander bewijst niets. Daarom is eerst geprobeerd de
goedkope voorspelling zo sterk mogelijk te maken, met een recept dat vóór de eerste run
vastlag. De uitkomst is zelf een resultaat: de fout van geschaalde B3LYP tegen het lab is
met een schaalfactor plus klassieke ML op bandkenmerken niet weg te werken.

Dat sluit aan bij een latere meting van module 05, op de *proxytaak*: het verschil tussen
twee DFT-methoden, B3LYP en ωB97X, waarop het netwerk van module 05 is getraind (hoofdstuk
10). Op hold-out (b), 39 moleculen die het netwerk nooit zag, laat de beste schaalfactor met drie frequentiegebieden per familie een
fout van 3,9 (C–H-strek), 10,0 (C–H uit het vlak), 14,2 (ringtrillingen in het vlak) en
14,6 cm⁻¹ (overige) over. Het ΔH-netwerk (versie 1.1) komt op 2,6 / 3,8 / 2,6 / 6,0 cm⁻¹.

## 7. Waar het kan misgaan — en wat je bij de aftekening controleert

- **De Q4-uitzondering.** De pijplijn traint nooit op labdata. Module 04 doet dat wél, met
  opzet, want het is de tegenstander. Het recept verklaart die uitzondering. Controleer dat
  het model nergens anders wordt gebruikt; de code van de pijplijn leest de uitvoer van
  module 04 niet in.
- **De koppeling is zelf een model.** Ongeveer 11 % van de paren verschilt meer dan
  15 cm⁻¹; daar is de toewijzing van labband aan berekende band twijfelachtig. Het rapport
  noemt dat als beperking.
- **Matrix, geen gas.** De labkant is gemeten in argon, niet in de gasfase (zie hoofdstuk 8).
- **Klein en klein.** 83 moleculen, allemaal met hooguit 50 koolstofatomen.
- **Bias.** De gemeten moleculen zijn geen willekeurige steekproef. Daarnaast heeft de
  auteur belang bij een zwakke tegenstander; het vooraf gecommitte recept is de maatregel
  daartegen.
- **Bij het inleveren.** De repository `udacity-applied-machine-learning` (`main` plus
  `module-04-calibrated-harmonic`) en een vers `requirements.txt` met `pip freeze`.

## 8. In het kort

Module 04 koppelt berekende en gemeten banden van 83 moleculen tot een tabel van 2.477
paren en traint vier modellen, getest op moleculen die ze niet zagen. Geen model voorspelt de
resterende fout: de beste MAE is 6,34 cm⁻¹ tegen 6,49 voor niets doen. Ridge-regressie is
de basislijn. De les: een schaalfactor laat spreiding over die je met bandkenmerken niet
terugwint.

*Bron: [README.md](../modules/04_calibrated_harmonic/README.md),
[RECIPE.md](../modules/04_calibrated_harmonic/RECIPE.md) en
[RUBRIC_CHECKLIST_2026-10-03.md](../modules/04_calibrated_harmonic/RUBRIC_CHECKLIST_2026-10-03.md)
van module 04, `notebook/model_results.json` van module 04,
[scale_factor_baseline_2026-10-25.md](../modules/05_support_predictor/out/scale_factor_baseline_2026-10-25.md),
[Rubrics/04](../../../Rubrics/04_Applied_Machine_Learning.md).*
