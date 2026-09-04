# Hoofdstuk 9 — Module 04: de goedkope tegenstander en de onzekerheidslaag

*Udacity-module "Applied Machine Learning". In de rubriek Project 3.*

---

## 1. Wat is de vraag?

Bouw met klassiek machine learning de sterkste *eerlijke goedkope* voorspeller van
bandposities die er te maken is, zodat de pijplijn een tegenstander heeft die niet
zwak is; en gebruik hetzelfde model om op de bereikrungs een foutenmarge per band te
schatten.

## 2. Wat eist de school?

Een volledige klassieke ML-workflow: dataset kiezen en het probleem formuleren (begeleid
of onbegeleid), inlezen en inspecteren, voorbewerken, een model trainen met scikit-learn
of PyTorch, evalueren met passende metrieken, een notebook-samenvatting en een rapport met
citaties. De dataset moet openbaar zijn vóór de module, niet synthetisch of AI-gegenereerd,
en **niet dezelfde als die van module 02 of 03**. Beoordeeld wordt op: het notebook draait
van boven naar beneden; voorbewerking is passend; het model past bij het probleem; er is
minstens één passende metriek; `requirements.txt`; uitleg waarom de metriek past;
interpretatie met eigen resultaten; minstens één beperking of afweging; minstens één bron
van bias met een genomen of voorgestelde maatregel; leesbare code; een rapport voor
technisch én niet-technisch publiek.

## 3. Invoer — de datastructuur in detail

**De trainingstabel, object O10.** Eén rij per (molecuul, band) waarvoor zowel een
berekende als een gemeten positie bestaat: de atlas van module 02 gekoppeld aan het
scorebord van module 03.

| Kolom | Type | Herkomst | Rol in het model |
|---|---|---|---|
| molecuul, uid | tekst | O8 | groepering voor de splitsing |
| N, aantal ringen, lading | gehele getallen | O8 | kenmerk (feature) |
| familie | categorie | O8/O9 | kenmerk, en de eenheid waarin gerapporteerd wordt |
| geschaalde harmonische DFT-positie | getal (cm⁻¹) | O8 | kenmerk |
| basisset, schaalfactor | categorie, getal | O8 | kenmerk |
| modekenmerken (samenstelling, lokale omgeving) | getallen | O2 waar beschikbaar | kenmerk |
| labpositie | getal (cm⁻¹) | O9 | — |
| fase, u_band | categorie, getal | O9 | weging; filter op beslisbare banden |
| **fout = labpositie − DFT-positie** | getal (cm⁻¹) | afgeleid | **doelvariabele** |

Het is dus **begeleid leren, regressie**: voorspel per band hoeveel de geschaalde
harmonische DFT-waarde ernaast zit.

**Publicatie vooraf.** Deze tabel wordt als eigen, versiebeheerde uitgave met een
Zenodo-DOI gepubliceerd **voordat module 04 begint**, met een provenance-paragraaf die
uitlegt dat het een afgeleide tabel is (koppeling van twee openbare bronnen), verschillend
van de datasets van module 02 (berekeningen) en 03 (metingen). Dat is "lezing 1" van de
herbruikregel, door de gebruiker op 2 september 2026 beslist en overgenomen. Terugval als
een beoordelaar "lezing 2" hanteert (elke koppeling van eerdere data is hergebruik): de
NIST CCCBDB-tabel, of anders VIBFREQ1295.

**Het recept** (welke kenmerken, welke afstemming, welke zaadjes) staat vast in
pilotnotitie-item 6.

## 4. Bewerking

1. Inlezen en inspecteren van O10; ontbrekende modekenmerken markeren.
2. Voorbewerking: één-hot-codering van categorieën, schaling van getallen, filtering op
   banden met een beslisbaar oordeel.
3. **Splitsing per molecuul**, nooit per band: alle banden van één molecuul zitten óf in de
   training óf in de test ("leave-molecule-out"). Anders leert het model een molecuul
   herkennen in plaats van een fout voorspellen.
4. Trainen van een scikit-learn-model (bijvoorbeeld een gradiënt-boosting-regressor of
   een gereguleerde lineaire regressie; het recept van item 6 beslist).
5. Evalueren met **RMSE en MAE in cm⁻¹ per familie** op de weggelaten moleculen; een
   figuur van voorspelde tegen werkelijke fout; een figuur van de restfout per familie.
6. Interpretatie: welke families laten zich goed kalibreren, welke niet. De verwachting
   uit de literatuur: de kalibratie vangt het *gemiddelde* van een ongeveer 5 cm⁻¹ groot
   CC−DFT-verschil per familie op; de pijplijn met Δ₂ moet dan de *spreiding* binnen de
   familie winnen.

## 5. Uitvoer — de datastructuur in detail

Twee objecten, allebei dragend.

**(1) De gekalibreerde opponentkolom.** Voor elke band van elk laddermolecuul: de
DFT-positie plus de door het model voorspelde correctie. Vorm: een tabel `molecuul, band,
familie, gekalibreerde positie (cm⁻¹)`. Dit wordt in module 08 de tweede tegenstander in de
beat-vergelijking (naast de ruwe atlas). Het plan zegt hardop wat deze kolom doet: ze
absorbeert het gemiddelde; Δ₂ moet de rest kopen.

**(2) De empirische onzekerheidslaag.** Voor de bereikrungs R4–R6 (geen labdata) geeft het
model per band een **geschatte fout met spreiding**: `molecuul, band, familie, verwachte
fout, spreiding (cm⁻¹)`. Die spreiding gaat in het foutbudget van het certificaat (object
O13) als "P5 empirische onzekerheid".

Verder: het notebook, `requirements.txt`, het rapport, en de vereiste zin: "De
trainingstabel is een gepubliceerde afgeleide dataset (DOI …) die openbare berekende
banden aan openbare laboratoriumbanden koppelt; haar herkomst en het verschil met de
datasets van module 02 en 03 staan in §…; ze is niet AI-gegenereerd."

## 6. Waarom deze module?

Een "beat" tegen een zwakke tegenstander is niets waard. De atlas van module 02 is ruwe
geschaalde DFT; iedereen in het vakgebied weet dat je die met een slimme kalibratie een
paar cm⁻¹ beter kunt maken (de "Ethereal-AI-klasse"-aanpak uit de literatuur, hier in eigen
uitvoering). Door die kalibratie zelf te bouwen, speelt de pijplijn tegen de sterkste
goedkope tegenstander en niet tegen een stroman. Zonder module 04 is P2 (de beat-toets)
niet eerlijk en heeft R4–R6 geen foutenmarge.

## 7. Waar het kan misgaan — en wat je bij de aftekening controleert

- **De Q4-uitzondering.** De pijplijn heeft als regel dat het lab nooit trainingsinvoer is.
  Module 04 traint *wél* op labresiduen, met opzet, want het is de tegenstander en niet de
  pijplijn. Dat is een verklaarde uitzondering: leave-molecule-out, recept bevroren in de
  pilotnotitie, en de uitvoer verschijnt alleen als opponentkolom (P2) en als
  onzekerheidslaag (P5). Controleer dat het model nergens anders wordt gebruikt.
- **Distinctheid.** De koppeltabel moet vóór de start gepubliceerd zijn met DOI en
  provenance-paragraaf. Zonder dat is de dataset "gemaakt tijdens de module" en voldoet
  hij niet. Controleer de datum van de uitgave tegen de startdatum.
- **Volgorde.** Module 02 → 03 → 04 is verplicht (atlas → scorebord → koppeltabel), en de
  pilotnotitie moet gecommit zijn voordat de opponentkolom in enige vergelijking wordt
  gebruikt.
- **Bias-sectie van de rubriek.** De voor de hand liggende bron: het model is getraind op
  kleine PAK's en wordt op grote toegepast (R4–R6); de onzekerheidslaag is daar een
  extrapolatie. Dat moet in het rapport staan als bias én als maatregel (de spreiding wordt
  gerapporteerd, niet verzwegen).
- **Metriekkeuze.** RMSE/MAE in cm⁻¹ per familie, met de reden: de beat-marge is per
  familie gedefinieerd, dus de metriek ook.

## 8. In het kort

Module 04 traint een klassiek regressiemodel dat per band de fout van geschaalde
harmonische DFT tegen het lab voorspelt, op een vooraf gepubliceerde koppeltabel van
atlas en scorebord, gesplitst per molecuul. Eruit komen de gekalibreerde opponentkolom
voor de beat-toets en de foutenmarge voor de bereikrungs. Het is de sterkste eerlijke
tegenstander, en het enige onderdeel dat met opzet op labdata traint.

*Bron: [Capstone_Mapping.md](../GoalGathering/Capstone_Mapping.md) §3 (Module 04) en §4,
[Distilled_Project_Plan_and_Quality_Checks.md](../GoalGathering/Distilled_Project_Plan_and_Quality_Checks.md)
§7 (P2, P5, Q4), [Frozen_Ladder_and_Tolerances.md](../GoalGathering/Frozen_Ladder_and_Tolerances.md)
§4 item 6, [Rubrics/04](../../../Rubrics/04_Applied_Machine_Learning.md).*
