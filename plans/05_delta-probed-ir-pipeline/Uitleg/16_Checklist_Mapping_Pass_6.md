# Hoofdstuk 16 — Checklist voor mapping Pass 6

> **Wat dit hoofdstuk is**
> Mapping Pass 6 is de aftekening van het document
> [Capstone_Mapping.md](../GoalGathering/Capstone_Mapping.md): per module de rubriek er
> nog eens naast leggen en punt voor punt vaststellen dat de bijdrage, dataset, code,
> artefact en rapport elk criterium halen, met de zwakke plekken benoemd. Passen 1–5 van de
> mapping zijn geschreven; Pass 6 wacht op het woord van de gebruiker. Dit hoofdstuk zet op
> een rij wat je daarvoor nodig hebt en wat de modules nu leveren.

---

## §16.1 Hoe je Pass 6 doet

1. Lees per module eerst het rubriekbestand in `Rubrics/` (het deel "Instructions" en de
   tabel "Rubric"), dan de module-paragraaf in de mapping (§3), dan de rubriekchecklist van
   de module (`RUBRIC_CHECKLIST_*.md` in de modulemap) en het bijbehorende hoofdstuk hier
   (7–14).
2. Vul per module de tabel van §16.3 in: **haalt** / **haalt onder voorwaarde** (welke) /
   **haalt niet**. De modules 02–07 zijn gebouwd; "onder voorwaarde" betekent nu bijna altijd
   een handeling bij het inleveren.
3. Noteer waar een module anders is gebouwd dan de mapping beschrijft. De mapping is
   bevroren op het plan van september 2026; drie modules wijken af: module 05 traint op het
   eigen corpus in plaats van Hessian QM9, module 06 is de kandidatenvoorsteller (een
   SMILES-Transformer) in plaats van de patroonvoorsteller (die is nu het standout-project
   buiten de reeks), en module 07 is de run steward in plaats van de
   campagne-officier.
4. Waar je "haalt niet" schrijft, stopt de mapping volgens haar regel 0 en gaat de vraag
   naar de gebruiker; er wordt geen bezigheidstherapie verzonnen om de rubriek te halen.
5. Schrijf het resultaat als §7 van de mapping ("Pass 6 — sign-off"), gedateerd. De rest
   van de mapping is bevroren; §7 toevoegen is de gedateerde notitie die de bevriezing
   toestaat.

## §16.2 Wat voor alle modules geldt

- **Datasetregel** (Rubrics/README): openbaar *vóór* de module begint; geschikt voor
  academisch gebruik; niet synthetisch of AI-gegenereerd; niet hergebruikt uit een eerdere
  module. De voorbeeldlijst (Kaggle, UCI, Data.gov) is geen gesloten poort. "Niet
  AI-gegenereerd" slaat op modelgegenereerde *trainingsdata*, niet op ab-initio-berekeningen;
  elk rapport zegt dat in één zin. Een Zenodo-DOI is geen eis: voor module 04 besliste de
  gebruiker dat de openbare tabel in de repository volstaat; voor module 05 is de DOI een
  keuze bij het inleveren.
- **Gescheiden datasets.** 02 berekeningen (PAHdb theoretisch), 03 metingen (PAHdb
  experimenteel + NIST), 04 de koppeling van beide. Module 02 laadt de experimentele
  bibliotheek niet meer.
- **Beslissing 7.** Het nooit ingeleverde QM9-concept heet nu
  `draft-qm9-foundations-unsubmitted`; de provenance van module 02 noemt het.
- **De vorm van het inleveren.** Elke module heeft een `SUBMISSION.txt` met de bestanden die
  de inlever-repository houdt (module 08 krijgt het zijn met zijn losstaande momentopname).
  `tools/make_module_repo.sh` bouwt de repository met de eigen geschiedenis van de module en
  voert het notebook uit in een verse kopie. Alleen de rubriek van module 02 noemt een
  repositorynaam; de andere namen volgen de stijl `udacity-…`. Bij elke inlevering wordt
  `requirements.txt` opnieuw gemaakt met `pip freeze` in de omgeving waarin het notebook
  draait.

## §16.3 De checklist per module

Legenda voor de kolom "status": ✔ gedaan; ◐ gedaan, met een handeling bij het inleveren of
een open punt; ✘ open vraag voor de gebruiker.

### Module 02 — opponent-atlas

| Criterium (rubriek) | Wat de module levert | Status | Waar te controleren |
|---|---|---|---|
| openbare tabel, ≥ 200 rijen, ≥ 5 kolommen | PAHdb v4.00, soortentabel 10.749 × 27 | ✔ | README module 02 |
| geen ML | parseren, opschonen, figuren | ✔ | notebook |
| ≥ 2 opschoonfuncties, ≥ 1 EDA-functie | `split_charge_suffix`, `flag_unresolved_basis`; `coverage_summary` | ✔ | notebook, H7 §4 |
| ≥ 3 figuren met titel en assen | vijf figuren, elk met interpretatie | ✔ | notebook |
| README met reflectievragen | vier antwoorden | ✔ | README module 02 |
| rapport (Task 10) | `module_summary.pdf`, APA 7 | ◐ eigen lezing van de student | checklist module 02 |
| repository met ≥ 2 branches | `ai-programming-foundations-project`: `main` + `module-02-opponent-atlas` | ◐ de gebruiker maakt hem aan | `tools/make_module_repo.sh` |

### Module 03 — scorebord en u_band

| Criterium | Wat de module levert | Status | Waar |
|---|---|---|---|
| openbaar, ≥ 500 rijen, ≥ 6 kolommen, numeriek + groepering | `bands_lab.csv`, 4.218 × 31 | ✔ | README module 03 |
| niet de 02-dataset | metingen tegenover berekeningen | ✔ | H8 §7 |
| ≥ 3 visuele modellen | drie figuren, met een vergelijking welke de vraag beantwoordt | ✔ | notebook |
| één hypothesetoets, vooraf vastgelegd | Wilcoxon per familie, Holm; zes van acht families verwerpen H₀ | ✔ | `PRE_REGISTRATION.md`, H8 §5 |
| beperkingen en bias | vier moleculen; matrix- en hot-band-verschuiving niet te scheiden | ✔ | rapport |
| uitleg voor een leek | "Interpretation for a Non-Technical Audience" | ✔ | rapport |
| de C–C-families op de hete bron | onbeslist door constructie als verwacht resultaat (keuze van de gebruiker) | ✔ | H8 §5 |

### Module 04 — de gekalibreerde goedkope tegenstander

| Criterium | Wat de module levert | Status | Waar |
|---|---|---|---|
| dataset openbaar, niet 02/03 | koppeltabel 2.477 × 28, openbaar in de repository | ✔ | README module 04 |
| begeleid/onbegeleid verklaard | begeleid, regressie op de fout van geschaalde DFT | ✔ | H9 §3 |
| voorbewerking en splitsing | standaardisering, één-hot; splitsing per molecuul (83 rondes) | ✔ | H9 §4 |
| model, metriek + motivatie | vier modellen; MAE per familie | ✔ | H9 §5 |
| resultaten gelezen | geen model leert de fout (MAE 6,34–6,49 cm⁻¹) | ✔ | `model_results.json` |
| beperking, bias + maatregel | de koppeling als model; recept vóór de training gecommit | ✔ | H9 §7 |
| de Q4-uitzondering | traint op labresiduen als tegenstander; nergens anders gebruikt | ✔ | `RECIPE.md` |

### Module 05 — de ΔH-voorspeller

| Criterium | Wat de module levert | Status | Waar |
|---|---|---|---|
| taaktype (CNN/RNN/Transformer) | Transformer over de trillingen van een molecuul | ✔ | H10, checklist module 05 |
| dataset openbaar, niet synthetisch, niet hergebruikt | eigen corpus, uitgave `layerA2_2026-09-23` (224 moleculen) met checksums | ◐ DOI-keuze bij het inleveren | README module 05 |
| basislijn + precies één verandering | 2 → 4 Transformerlagen, al het andere gelijk | ✔ | `RECIPE.md` module 05 |
| evaluatie en vergelijking | fout per familie tegen twee eenvoudige regels, drie zaadjes | ✔ | notebook |
| notebook draait van boven naar beneden | hoofdrun ongewijzigd; vervolgsecties apart uitgevoerd | ◐ §12.6 wacht op een nieuwe uitvoering | TASKS 20 |
| rapport | `module_summary.pdf` met aanvullingen | ◐ aanvulling over het ΔH-netwerk in de schrijffase | REVIEW_2026-10-17 |

### Module 06 — de kandidatenvoorsteller

| Criterium | Wat de module levert | Status | Waar |
|---|---|---|---|
| GAN / VAE / Transformer | decoder-only Transformer op SMILES (≈ 3 M parameters) | ✔ | H11, checklist module 06 |
| dataset gedocumenteerd | bevroren PubChem-set met zoekopdracht en checksum | ✔ | `data/README.md` module 06 |
| uitvoer beoordeeld, met mislukkingen | zeven vooraf vastgelegde maten (zes gehaald), een galerij van mislukkingen | ✔ | notebook §4 |
| ethiek specifiek | kandidaten zijn "wat je hierna berekent", nooit geclaimde moleculen | ✔ | rapport |
| reproduceerbaarheid | drie zaadjes; het checkpoint van zaadje 2 is niet bewaard | ✘ reproductie op het woord van de gebruiker | TASKS 20 |

### Module 07 — de run steward

| Criterium | Wat de module levert | Status | Waar |
|---|---|---|---|
| doel, grenzen, enkel/meer-agent gemotiveerd | één begrensde agent, elf toegestane acties | ✔ | H12 §4 |
| beslislogica, geheugen, tools | poort in gewone Python; regeltabel van 41 regels | ✔ | H12 §3–§4 |
| logging, veiligheid, diagram | één logregel per stap; architectuurfiguur | ✔ | notebook |
| ≥ 1 echte mislukking | de herhaalfout in scenario S3 | ✔ | H12 §5 |
| voorbeeldruns | 17 scenario's, 17 van de 17 met het deterministische beleid; 29 tests | ✔ | `notebook/results.json` |
| run met het taalmodel | nog niet gedraaid; later met de cursussleutel | ◐ de rubriek eist hem niet strikt, het rapport belooft hem | REVIEW_2026-10-17 |
| cursus-tools | LangGraph; model-id gelogd | ✔ | README module 07 |

### Module 08 — synthese

| Criterium | Wat de module levert | Status | Waar |
|---|---|---|---|
| ≥ 3 modules geïntegreerd | 03, 05, 06 en 07 in de code | ✔ | H13, H14 §4 |
| systeem draait, waarneembare uitvoer | de pijplijn 0.9, certificaten, scenario's 8/8 | ✔ | `modules/PIPELINE.md` |
| paper 1.500–2.000 woorden, bronnen | 1.852 woorden, vier bronnen | ◐ herschrijven onder beslissing 63 in de schrijffase | checklist module 08 |
| ethiek en verantwoord gebruik | certificaat per band, weigering als volwaardige uitvoer | ✔ | paper §5 |
| portfoliowaarde | de Spectrum Atlas en de pipeline show, openbaar | ✔ | H13 |
| losstaande inlevering | momentopname en `SUBMISSION.txt` | ◐ in de schrijffase | TASKS 20 |

### Module 09 — verdediging

| Criterium | Wat de module levert | Status |
|---|---|---|
| 30 minuten: 15 presentatie in zeven onderdelen, 15 verdediging, Engels | de te verdedigen punten en voorbereide vragen van H14 | ◐ dia's in de schrijffase |

## §16.4 De vragen die alleen de gebruiker kan beantwoorden

De drie vragen die Pass 6 oorspronkelijk niet zelf kon beslissen, zijn beantwoord:

1. **Module 03, de C–C-families van R2.** Een uitputtende zoektocht vond geen gasfasebron bij
   kamertemperatuur in het 6–15 µm-gebied. De gebruiker koos: aftekenen mét de onbeslisbaarheid
   als verwacht resultaat.
2. **Module 05, de omvang van de dataset.** De gebruiker koos het eigen corpus; Hessian QM9
   valt af (te weinig aromatische ringen, hooguit negen zware atomen).
3. **Module 07, het agent-raamwerk.** LangGraph, verdedigbaar via het Udacity-keuzevak over
   LangChain en LangGraph.

Open voor de gebruiker: de reproductie van zaadje 2 van module 06, de DOI van de dataset van
module 05, en het moment van de run met het taalmodel van module 07.

## §16.5 Wat Pass 6 niet is

Pass 6 beoordeelt de *mapping*, niet de wetenschap. Of het netwerk een familie haalt, of de
hold-outs schoon zijn, of de ankers kloppen: dat zijn metingen, en die staan in de
resultaatbestanden en het ankerregister. Als je bij het aftekenen een wetenschappelijke
twijfel tegenkomt, hoort die niet in §7 van de mapping maar in een taak op het takenbord
(`TASKS.md`) of een genummerde beslissing.

*Bron: [Capstone_Mapping.md](../GoalGathering/Capstone_Mapping.md) §0–§6,
[Rubrics/README.md](../../../Rubrics/README.md), de rubriekbestanden 02–09, de
rubriekchecklists van modules 02–08 (`RUBRIC_CHECKLIST_*.md`),
[REVIEW_2026-10-17.md](../modules/REVIEW_2026-10-17.md), [TASKS.md](../TASKS.md) taak 20,
en de hoofdstukken 7–14 van deze uitleg.*
