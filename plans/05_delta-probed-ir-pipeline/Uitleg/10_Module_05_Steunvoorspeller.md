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
   gelijk bleef: al het andere. Metriek: ρ bij vast K, en K om ρ* te bereiken. Dit
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
