# Hoofdstuk 1 — De vraag van plan 06

> **In dit hoofdstuk leer je**
> – welk getal plan 05 zo duur betaalt, en waarom;
> – dat "dezelfde uitkomst" drie verschillende dingen kan betekenen (E1, E2, E3);
> – waar de rekentijd werkelijk in gaat zitten, met de gemeten getallen;
> – waarom het doelwit de Schrödingervergelijking zelf is, en niet de boekhouding eromheen.

---

## §1.1 Het dure getal

Plan 05 wil voor elk molecuul een nauwkeurig infraroodspectrum. De nauwkeurigheid komt van één
soort getal: de **elektronische grondtoestandsenergie** van het molecuul, uitgerekend op
"coupled-cluster"-niveau (CCSD(T), een van de nauwkeurigste methoden die de scheikunde kent), voor
een molecuul waarvan de atomen een klein beetje zijn verschoven. Zo'n energie is de oplossing van de
**Schrödingervergelijking** voor alle elektronen tegelijk, met de kernen stilgezet.

Gemeten op de laptop van het project, met de lokale variant (LNO-CCSD(T)) en de basis cc-pVTZ:

| molecuul | één energie | bron |
|---|---|---|
| benzeen (12 atomen) | 2.087 s, ruim een half uur | plan 05, 5 september 2026 |
| naftaleen (18 atomen) | 41.375 s, 11,5 uur; 24 fragmenten; 19,8 GB geheugen | plan 05, 11 september 2026 |

En plan 05 heeft er niet één nodig maar een heel **deck**: bij benzeen 448 energieën (2M voor de
diagonaal plus 388 voor de koppelingen), bij naftaleen 474. Vermenigvuldig: 474 × 11,5 uur ≈ 5.450
laptopuren voor één molecuul. Dat is de reden dat plan 05 om een cluster vraagt.

## §1.2 Wat "dezelfde uitkomst" kan betekenen

"Een andere wiskunde die hetzelfde oplevert" klinkt eenduidig, maar is het niet. Plan 06 onderscheidt
drie niveaus, en zegt bij elk idee welk niveau het claimt.

| niveau | "equivalent" betekent | wat een kandidaat moet laten zien |
|---|---|---|
| **E1 — identiek object** | precies dezelfde energie, langs een andere weg | een stelling (een bewijs); dit is waar Lean kan meekijken |
| **E2 — binnen de foutmarge van plan 05** | dezelfde energie tot op de ruis en de systematische afwijking die plan 05 zelf al accepteert | een getalsmatige vergelijking met de "waarheidslijnen" die plan 05 al heeft opgeslagen |
| **E3 — identieke gescoorde uitkomst** | dezelfde bandposities in het spectrum, ook als de energie ergens afwijkt waar het er niet toe doet | dezelfde vergelijking, maar op het spectrum |

Hoe lager het niveau, hoe meer kandidaten er mogelijk zijn en hoe minder je bewijst. Een kandidaat
op niveau E1 die sneller is, zou een echt wiskundig resultaat zijn. Op E2 of E3 is het een
benadering met een certificaat, en dat is precies wat plan 05 zelf ook is.

## §1.3 Waar de tijd in gaat zitten

Kosten = (prijs per energie) × (aantal energieën) + naverwerking. De naverwerking (de trillingen
uitrekenen uit de gecorrigeerde krachtconstanten) kost seconden tot minuten en is geen doelwit.

Er zijn dus twee knoppen: de prijs per energie en het aantal. Halveer de een of de ander en je wint
een factor twee. Iets *anders* vragen dan energieën (bijvoorbeeld gradiënten, die per stuk meer
informatie dragen) of iets *kleiners* willen weten (alleen de delen van de correctie die bandposities
verschuiven) kan meer opleveren, of niets. Dat is de open vraag.

## §1.4 Het doelwit: de Schrödingervergelijking zelf

De opdrachtgever van dit plan heeft het doelwit scherp gezet: niet de boekhouding rondom de
energieën (hoeveel er nodig zijn, hoe je ze slim kiest), maar **het oplossen van de
Schrödingervergelijking zelf** — de prijs per energie. De boekhouding blijft als nevenspoor bestaan
(richting S5 in hoofdstuk 4), omdat hij goedkoop te toetsen is, maar het hoofdspoor is de vraag of
de elektronen van een aromatisch molecuul een structuur hebben die de huidige wiskunde nog niet
uitbuit.

## §1.5 Eén zin om te onthouden

Plan 06 zoekt geen snellere manier om de Schrödingervergelijking *in het algemeen* op te lossen —
dat kan niet, zie hoofdstuk 2 — maar een bewijs of een meting dat *onze klasse moleculen* een
structuur heeft die een exacte of gecertificeerde kortere weg toelaat.
