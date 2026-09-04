# Hoofdstuk 7 — Module 02: de opponent-atlas

*Udacity-module "AI Programming Foundations". In de rubriek heet dit Project 1.*

---

## 1. Wat is de vraag?

Maak van de openbare NASA-databank met *berekende* PAK-spectra één nette, doorzoekbare
tabel, en breng in kaart wat erin zit — want dat is de tegenstander die de pijplijn moet
verslaan.

## 2. Wat eist de school?

Een verkennende data-analyse **zonder machine learning**: een openbare tabel van minstens
200 rijen en 5 kolommen inlezen met pandas en NumPy, opschonen, minstens drie figuren
maken, en de stappen documenteren. De rubriek zegt letterlijk dat je ook een eigen dataset
mag gebruiken zolang die aan de eisen voldoet. Er mag niets getraind worden.

## 3. Invoer

- **PAHdb v4.00, de theoretische bibliotheek** (NASA Ames). Een download met per molecuul
  (meer dan tienduizend) de berekende bandposities en intensiteiten, plus metadata:
  formule, lading, aantal atomen, welke basisset is gebruikt (6-31G* voor kleine, 4-31G
  voor grote moleculen), welke schaalfactor op de harmonische frequenties is toegepast.
  Het is berekende wetenschappelijke data, geen AI-uitvoer; het rapport zegt dat in één
  zin.
- **De ladder** (hoofdstuk 1): welke moleculen en welke grootteklassen ertoe doen.
- **Openstaande schuld 6** uit de tegenstanderslijst: welke soorten in de
  C₃₈₄H₄₈-klasse bestaan er in PAHdb?

## 4. Bewerking

1. Parseren van het downloadformaat naar één tabel: één rij per band (object O8).
2. Opschonen: eenheden gelijktrekken, dubbele vermeldingen herkennen, ontbrekende
   metadata markeren, de schaalfactor als aparte kolom.
3. Familie-etiket per band toekennen (C–H-strek, C–C-strek, C–H-buiging in en uit het
   vlak) op grond van frequentiebereik en, waar beschikbaar, de modebeschrijving.
4. Verkenning met figuren: dekking per grootte en lading; waar het 4-31G-regime begint;
   welke rungs van de ladder een vermelding hebben; welke soorten in de grootste klasse
   bestaan en hoeveel symmetrisch verschillende lokale omgevingen die hebben (dat laatste
   getal bepaalt hoeveel fragmenten R6 nodig heeft).

## 5. Uitvoer

- **O8, de opponent-atlas**: een CSV met kolommen `uid, formule, lading, N, bandpositie
  (cm⁻¹), intensiteit, schaalfactor, basisset, familie`. Ruim 10⁵ rijen.
- **Een notebook met de figuren** en een kort rapport.
- **Een antwoord op schuld 6**: de lijst kandidaat-doelmoleculen voor R6 met hun aantal
  unieke lokale omgevingen.

Wie gebruikt het daarna? Module 04 koppelt deze tabel aan het lab-scorebord; module 08
gebruikt hem als de "lijn A"-kolom in elke beat-vergelijking; de campagne-officier weigert
een beat-claim zonder deze kolom.

## 6. Waarom deze module?

Zonder atlas is er geen tegenstander en dus geen "beat". De maatstaf van het hele plan is
relatief (hoofdstuk 1): beter dan de beste bestaande voorspelling. Die voorspelling moet
machinaal opvraagbaar zijn, per band, met versienummer. Dat is precies deze tabel.

## 7. Waar het kan misgaan — en wat je bij de aftekening controleert

- **Niets trainen.** De verleiding is groot om alvast een regressie op de banden te
  doen; dat hoort in module 04. Controleer dat het notebook geen model bevat.
- **De vereiste zin.** Het rapport moet zeggen: geparseerd uit de openbare NASA Ames
  PAHdb v4.00 (met DOI), berekende data, niet AI-gegenereerd, en de *tegenstander* van de
  pijplijn, niet haar trainingsdata.
- **Het hernoemde concept.** Er bestaat een niet-ingeleverde eerdere versie van deze
  module op QM9. Beslissing 7 (4 september 2026): die wordt hernoemd of gearchiveerd, en
  de provenance-paragraaf van dit rapport noemt dat, zodat een beoordelaar het concept
  niet voor een inzending aanziet.
- **Distinctheid.** Deze tabel mag later niet nog eens als dataset van module 03 of 04
  opduiken; module 03 gebruikt *metingen*, module 04 een *afgeleide koppeltabel* met eigen
  DOI.

## 8. In het kort

Module 02 bouwt uit de NASA-databank de tabel van berekende bandposities waartegen de
pijplijn wordt afgerekend: inlezen, opschonen, familie-etiketten, figuren, en het antwoord
op de vraag welke reuzenmoleculen er in de databank staan. Geen machine learning, wel de
eerste van de veertien objecten van hoofdstuk 6.

*Bron: [Capstone_Mapping.md](../GoalGathering/Capstone_Mapping.md) §1 en §3 (Module 02),
[Rubrics/02](../../../Rubrics/02_AI_Programming_Foundations_Project.md),
[Overarching_Goal.md](../GoalGathering/Overarching_Goal.md) (beslissing 7).*
