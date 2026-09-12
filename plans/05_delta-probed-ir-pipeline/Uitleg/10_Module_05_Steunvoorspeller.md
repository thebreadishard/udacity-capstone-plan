# Hoofdstuk 10 — Module 05: de Δ₂-steunvoorspeller

*Udacity-module "Deep Learning Systems". In de rubriek Project 4.*

---

## 1. Wat is de vraag?

Kan een neuraal netwerk, alleen uit goedkope DFT-kenmerken, voorspellen *welke* elementen
van de correctiematrix Δ₂ groot zullen zijn — zodat de dure metingen daar geplaatst
worden en er minder van nodig zijn?

## 2. Wat eist de school?

Een deep-learning-experiment in PyTorch: een probleemdomein kiezen (**beeld, tekst of
reeks**), een model uit de familie **CNN, RNN of Transformer**, een baseline trainen, en
**precies één** ding veranderen voor een gecontroleerde vergelijking ("zeg wat er
veranderde en wat gelijk bleef"). Beide modellen evalueren, met leercurves. "Hoge
nauwkeurigheid is niet vereist." De dataset moet openbaar zijn vóór de module, niet
synthetisch of AI-gegenereerd, en **niet hergebruikt uit een eerdere capstone-module**;
standaardbenchmarks en samengestelde echte datasets zijn toegestaan. Het rapport moet een
ethiek-paragraaf hebben en het notebook een samenvatting van 4–6 zinnen.

## 3. Invoer — de datastructuur in detail

**Het corpus, object O11.** Zeven gemeten PAK-tensoren tegen R3 zijn geen
deep-learning-dataset. Daarom is het corpus **DFT-tegen-DFT op schaal**:

- **Hessian QM9** (openbaar; 41.645 kleine organische moleculen met ωB97x/6-31G*-Hessianen).
- **Zelf herberekende B3LYP/6-31G*-Hessianen** op een aromaat-zware deelverzameling ervan
  (benzeenderivaten en geconjugeerde ringen oververtegenwoordigd). Hoe groot die
  deelverzameling is, wordt pas bepaald nadat de dry run de Hessiaan-rekentijd per molecuul
  op de laptop heeft geprint; er staat met opzet geen getal in het plan.
- Per molecuul: Δ₂ = Hessiaan(ωB97x) − Hessiaan(B3LYP) in de B3LYP-modebasis. Twee
  functionalen met sterk verschillend aandeel exacte uitwisseling, zodat het verschil de
  "moderotaties" bevat die het echte CC−DFT-verschil ook heeft.

De vorm per molecuul:

| Onderdeel | Type | Betekenis |
|---|---|---|
| tokens | reeks van M records | één per DFT-mode: frequentie, samenstelling (welke atomen bewegen), atoomomgevingskenmerken |
| label | matrix M × M van 0/1 | de **steun**: welke elementen van Δ₂ boven een drempel liggen |
| Δ₂ | tensor M × M | de volledige correctie, voor het gebruik als prior en voor P3 |
| splits-hash | tekst | per molecuul: train / validatie / test |

**Probleemdomein en modelfamilie, expliciet verklaard:** domein **reeks** (een molecuul als
reeks van M mode-tokens; het doel een label per token-paar), model **Transformer**
(aandacht tussen tokens, equivariant onder de symmetrie van het molecuul). De aandacht
tussen token i en token j is precies de plek waar "zijn modes i en j gekoppeld?" leeft;
dat is waarom een Transformer hier natuurlijk past en een CNN niet.

**Wat er niet in zit.** Geen labdata (Q4 triviaal schoon). De PAK-dry-run-tensoren en de
op de rungs gemeten tensoren zijn **alleen testset**: QM9-moleculen hebben hoogstens negen
zware atomen (herinnerd; wordt gecontroleerd bij het bouwen), dus elk PAK groter dan
benzeen ligt buiten de trainingsverdeling.

**Publicatie vooraf.** Eigen uitgave met Zenodo-DOI en deck-hashes vóór de module begint.

## 4. Bewerking

1. Corpus bouwen: QM9-deelverzameling kiezen, B3LYP-Hessianen rekenen (DFT-only, de
   laptop), Δ₂ en steunlabels afleiden, splitsen per molecuul met hash, publiceren.
2. Baseline-Transformer trainen op de steunvoorspelling; leercurves loggen.
3. **De gecontroleerde vergelijking, bevroren in het plan:** *geleerde prior tegen
   structurele prior bij gelijk K*, op het dry-run-corpus. Zelfde patronen, zelfde
   achtergehouden set, zelfde solver, minstens drie zaadjes. Wat veranderde: de prior. Wat
   gelijk bleef: al het andere. Metriek: ρ bij vast K, en K om ρ* te bereiken (sinds 6 september
   2026: ρ_off en de drempel met modelvloer, besluiten 8, 9, 12; en de baseline waartegen de
   geleerde prior moet winnen is het aantal vrije elementen dat de symmetrieprior overlaat,
   besluiten 11 en 13). Dit
   vergelijkt geen twee netwerken maar een netwerk-als-prior tegen een prior zonder netwerk;
   dat is de vergelijking die de pijplijn nodig heeft, en hij voldoet aan de rubriekvorm.
4. De effectgrootte (P3) rapporteren op het corpus én, informatief, op de weggehouden
   PAK-tensoren.

## 5. Uitvoer — de datastructuur in detail

- **Het getrainde model** met versiehash.
- **De geleerde prior**: voor een nieuw molecuul (gegeven O2) een matrix M × M met per
  element de voorspelde kans dat het groot is. Die matrix gaat als `prior = geleerd` met
  modelhash in het deck (O3) van een rung waar het mag.
- **De P3-effectgrootte**: pilotnotitie-item 5 in vorm; het getal na de meting.
- Notebook, `requirements.txt`, rapport met de vereiste zinnen: het corpus is openbare
  Hessian QM9 plus zelf berekende B3LYP-Hessianen (DOI, hashes), berekende data, niet
  AI-gegenereerd, in geen eerdere module gebruikt (beslissing 7: niets ingeleverd); het lab
  is nooit trainings-, validatie- of stopinvoer; op R0–R3 is elk gescoord spectrum de
  structurele recovery.

## 6. Waarom deze module, en voor welke rungs

Dit is de module waar de "regel 0" van de mapping (elk module-artefact draagt de
pijplijn) het meest is bevochten, en waar de gebruiker op 4 september 2026 heeft beslist.
De uitkomst:

- **Op R0–R3 is de geleerde prior nooit dragend.** Het gescoorde spectrum is daar altijd de
  structurele recovery. De prior wordt er wél gemeten: P3 op het corpus, en op R2 en R3 een
  vergelijking op *dezelfde echte antwoorden* — de structurele recovery tot haar K, de
  prior-geholpen recovery tot een **kleiner** K (een prior die niets bespaart, verdient
  niets), en de twee Δ₂'s moeten per familie binnen τ₇ overeenkomen, met de direct gemeten
  koppelingen binnen η₈. Slaagt dat op R2 én R3, dan is de **licentie verdiend**.
- **Op R4–R6 wordt de licentie gespendeerd.** Daar mag de prior-geholpen recovery de enige
  volledige recovery zijn, en dan is module 05 dragend voor het spectrum én het
  kostenrecord. Het certificaat zegt dat expliciet en noemt de twee rungs waarop de
  licentie is verdiend.

Het motief is de directive "erfenis is geen gezag": plan 04 verbood elke overdracht van
kennis tussen moleculen; plan 05 staat het toe waar het gemeten is en waar het het doel
dient. De grootte-zin en de Q8(c)-verhouding mengen nooit twee priors.

## 7. Waar het kan misgaan — en wat je bij de aftekening controleert

- **De herbruikclausule.** "Niet hergebruikt uit een eerdere capstone-module." Er is een
  niet-ingeleverd concept van module 02 op QM9. Beslissing 7 sluit dit: niets is
  ingeleverd, het concept wordt hernoemd of gearchiveerd. De terugvaloptie (een andere
  openbare Hessiaan-bron) blijft een benoemde schuld, nog niet ingevuld. Controleer dat de
  provenance-paragraaf beide punten noemt.
- **Domein en familie letterlijk.** Het rapport moet "reeks" en "Transformer" met zoveel
  woorden noemen; alles buiten CNN/RNN/Transformer gaat terug naar de gebruiker vóór het
  trainen.
- **Precies één verandering.** De rubriek wil een tweede configuratie die op één punt
  verschilt. De bevroren vergelijking (prior wisselen, al het andere gelijk) voldoet;
  controleer dat er niet stiekem ook een hyperparameter meeverandert.
- **Succescriterium.** Niet nauwkeurigheid maar de licentie: bespaart de prior patronen, en
  klopt de prior-geholpen recovery op een echte rung met de prior-vrije controle? Beide
  uitkomsten zijn publiceerbaar. Controleer dat het rapport dit zo formuleert en niet
  terugvalt op "accuracy".
- **Volgorde.** Module 05 wacht op de publicatie van het corpus, die weer wacht op de
  dry-run-timing. Als de laptop-Hessiaan traag blijkt, wordt de deelverzameling klein; dat
  is per gedateerde notitie, niet stilzwijgend.
- **Off-distribution eerlijk gemeld.** QM9 bevat geen PAK groter dan benzeen; het rapport
  zegt dat en rapporteert de PAK-testset apart.

## 8. In het kort

Module 05 traint een Transformer die uit DFT-modekenmerken voorspelt welke elementen van
Δ₂ groot zijn, op een zelf gepubliceerd corpus van ωB97x−B3LYP-verschillen over een
aromaat-zware QM9-deelverzameling. De gecontroleerde vergelijking is geleerde tegen
structurele prior bij gelijk K. Op de nauwkeurigheidsrungs is de prior alleen een gemeten
experiment; verdient hij zijn licentie op R2 én R3, dan wordt hij op de bereikrungs
dragend, en het certificaat zegt dat.

*Bron: [Capstone_Mapping.md](../GoalGathering/Capstone_Mapping.md) §0 en §3 (Module 05),
[Frozen_Ladder_and_Tolerances.md](../GoalGathering/Frozen_Ladder_and_Tolerances.md) §3
(de geleerde prior: verdiend en gespendeerd), [Distilled_Project_Plan_and_Quality_Checks.md](../GoalGathering/Distilled_Project_Plan_and_Quality_Checks.md)
§5–§6, [Overarching_Goal.md](../GoalGathering/Overarching_Goal.md) (beslissingen 4 en 7),
[Rubrics/05](../../../Rubrics/05_Deep_Learning_Systems.md).*

## 9. Stand van zaken op 12 september 2026 (gedateerde aanvulling)

Dit hoofdstuk beschrijft het plan zoals het is bevroren. Sindsdien is er gemeten, en dat verandert
één aanname in §3.

**Hessian QM9 is binnen.** Het bestand van 6,3 GB is gedownload en gecontroleerd (md5 klopt); alleen het
vacuümdeel is uitgepakt: 41.645 moleculen met per molecuul de geometrie, de energie, de krachten, de
Hessiaan, de frequenties en de normaalmodes. Het artikel is gelezen voor de eenheden (Å, eV, eV/Å²,
cm⁻¹) en de conventies. Twee dingen die je bij gebruik moet weten: de Hessianen zijn *numeriek*
(eindige verschillen met een verplaatsing van 0,01 a.u.; de makers melden dat de frequenties daar tot
15 cm⁻¹ gevoelig voor zijn, dus dat is de ruisvloer van elk label dat we eruit maken), en translaties en
rotaties zijn er niet uitgeprojecteerd (dat doen wij zelf voordat Δ₂ wordt gevormd).

**De aanname "benzeenderivaten oververtegenwoordigd" klopt niet.** Een ringtelling uit de geometrie
(bindingen uit covalente stralen, ringen uit de bindingsgraaf, platheid gecontroleerd) geeft: 66 van de
41.645 moleculen hebben een geheel-koolstof aromatische zesring, benzeen zelf zit er één keer in.
Wat er wél ruim in zit, 6.055 moleculen, zijn platte geconjugeerde vijf- en zesringen met stikstof of
zuurstof erin: pyridine-, pyrrool- en furaanachtigen. De "aromaat-zware QM9-deelverzameling" van §3 is
in werkelijkheid een geconjugeerde, heteroaromatische deelverzameling. De PAK-testset ligt dus nog
verder buiten de trainingsverdeling dan §3 aannam.

**Het antwoord dat klaarstaat: een eigen corpusfabriek.** Omdat QM9 gewoon DFT is en DFT-Hessianen
van kleine aromaten goedkoop zijn (gemeten op de laptop: benzeen 3 tot 7 minuten per Hessiaan,
naftaleen 13 minuten, pyreen 54 minuten), is in `modules/05_support_predictor/corpus/` een
wachtrij klaargezet die molecuul voor molecuul beide Hessianen rekent (B3LYP en ωB97X, 6-31G*), in
drie lagen en in een vaste volgorde:

| laag | inhoud | aantal in het manifest |
|---|---|---|
| A, grootte-brug | aromaten van 12 tot 30 atomen, van benzeen tot pyreen, met aza- en oxa-varianten | 45 |
| B, de klasse | mono- en digesubstitueerde aromatische en heteroaromatische kernen tot 26 atomen | 4.353 |
| C, QM9 geconjugeerd | de 6.055 uit de ringtelling; alleen de B3LYP-Hessiaan hoeft nog | 6.055 |

De fabriek kan op elk moment gestopt en weer gestart worden (laptop, straks de desktop, ooit een
cluster); omdat de volgorde binnen een laag vastligt, is elke tussenstand een reproduceerbare
deelverzameling en zijn "de eerste 300, 600, 1.200" van laag B geneste sets voor een leercurve.
Hoeveel er uiteindelijk gerekend wordt, staat met opzet nergens: dat wordt een gedateerde notitie na
een timingtest van vijf moleculen, precies zoals §3 al voorschreef voor de QM9-deelverzameling.
Er is nog niets gerekend. Of de eigen lagen worden overgenomen, of alleen de geconjugeerde
QM9-klasse, is een keuze van de opdrachtgever; tot die tijd is de fabriek een kandidaat.

*Bron: `modules/05_support_predictor/PROVENANCE.md`, `out/HESSIAN_QM9_SUMMARY.md`,
`out/HESSIAN_QM9_RINGS.md`, `corpus/DESIGN_2026-09-12.md`; gedateerde notitie van 12 september in
[Capstone_Mapping.md](../GoalGathering/Capstone_Mapping.md) §Module 05.*
