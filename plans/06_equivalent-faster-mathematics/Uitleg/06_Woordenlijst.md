# Hoofdstuk 6 — Woordenlijst

*Begrippen van plan 06. Begrippen van plan 05 (Δ₂, deck, probe, mode E, K, K_off, LNO, frozen
spaces, rung, u_band) staan in de woordenlijst van de Uitleg van plan 05 en worden hier alleen
genoemd als plan 06 ze anders gebruikt.*

| term | betekenis |
|---|---|
| **afvalconstante** (decay length λ) | de afstand waarover een bijdrage met een factor e afneemt als het afval exponentieel is: bijdrage ∝ e^(−r/λ). Klein λ = sterk lokaal. Experiment X3b meet λ voor MP2-paarenergieën. |
| **bandkloof** (gap) | het energieverschil tussen de hoogste bezette en de laagste onbezette elektronentoestand. Bepaalt volgens Prodan en Kohn de afvalsnelheid van de bijziendheid. |
| **bijziendheid** (nearsightedness of electronic matter) | het principe dat een lokale elektronische eigenschap nauwelijks afhangt van storingen ver weg; exponentieel afvallend voor gapped systemen. |
| **bonddimensie** | in DMRG/matrixproducttoestanden: de grootte van de matrices; groeit met de verstrengeling over een snede door het molecuul. Begrensd = exact en goedkoop. |
| **CCSD(T)** | coupled cluster met enkele en dubbele excitaties en een storingscorrectie voor drievoudige; de "gouden standaard" van de kwantumchemie voor moleculen als de onze. De (T)-stap groeit als N⁷. |
| **E1, E2, E3** | de drie niveaus van "equivalent" in plan 06: identiek object (stelling), binnen plan 05's foutbudget (numerieke vergelijking), identieke gescoorde uitkomst (vergelijking op het spectrum). |
| **falsificatietest** | de goedkope proef, vooraf benoemd, die een richting kan laten sneuvelen. Een richting zonder zo'n test wordt geparkeerd. |
| **grafafstand** | het kleinste aantal bindingen dat je moet volgen om van het ene atoom bij het andere te komen. De maat waarin de lokaliteitsstellingen hun afval uitdrukken; in benzeen hooguit 3, in naftaleen 5. |
| **Frobenius-norm** | de wortel uit de som van de kwadraten van alle elementen van een matrix; een maat voor "hoeveel er in zit". Les van X8: een blok dat weinig Frobenius-norm draagt, kan toch een bandpositie centimeters verschuiven — dunheid moet op bandposities getoetst worden. |
| **grootboek** (ledger) | de tabel achterin het oriëntatiedocument met per richting id, niveau, status, eerste test en resultaat; er wordt nooit iets uit gewist. |
| **Hartree–Fock** | de eenvoudigste kwantumchemische methode (elk elektron in het gemiddelde veld van de andere). Routine in de praktijk; in het slechtste geval NP-compleet (Schuch en Verstraete, appendix). |
| **klasse** | de verzameling moleculen waarover een uitspraak gaat. Voor plan 06: gapped, gesloten-schil, aromatisch, vlak, bij evenwicht; geparametriseerd door kloof, afvalconstante, nauwkeurigheid, geometrie. |
| **kostenverhouding** (cost ratio, g) | hoeveel energieberekeningen één analytische gradiënt kost. De wiskunde van automatisch differentiëren begrenst hem door een kleine constante (Baydin e.a. 2018: kleiner dan 6, meestal 2 à 3); voor lokale CCSD(T) is hij nergens afgedrukt en moet hij gemeten worden (trede 4 van plan 05's ladder). Beslist of substitutie (S5) ooit goedkoper is dan het deck. |
| **kleuringsgetal** | het kleinste aantal groepen waarin je de kolommen van een matrix met bekend nulpatroon kunt verdelen zodat je elke groep met één meting terugwint (Curtis–Powell–Reid; Coleman–Moré; Powell–Toint). Richting S5. |
| **Lean, Mathlib** | een bewijsassistent en zijn wiskundebibliotheek; in plan 06 de scheidsrechter voor E1-claims, geen ontdekker. |
| **LMO** | gelokaliseerde moleculaire orbitaal: een bezette orbitaal die door een rotatie zo compact mogelijk is gemaakt (hier Pipek–Mezey), zodat "afstand tussen orbitalen" betekenis heeft. |
| **MP2-paarenergie** | de correlatie-energie die aan één paar bezette orbitalen wordt toegeschreven in tweede-orde storingsrekening; de grootheid waarop lokale-CC-drempels zijn gebouwd. |
| **N-representeerbaarheid** | de voorwaarde dat een twee-elektronen-dichtheidsmatrix bij een echte N-elektronentoestand hoort; het volledige stel voorwaarden is QMA-hard. |
| **P, NP, QMA** | complexiteitsklassen: snel oplosbaar; snel controleerbaar door een klassieke computer; snel controleerbaar door een kwantumcomputer. QMA-compleet = tot de moeilijkste in QMA. |
| **QMA-hard** | minstens zo moeilijk als het moeilijkste probleem in QMA. De universele DFT-functionaal is QMA-hard (Schuch en Verstraete 2009). |
| **rang** (van een matrix) | het aantal onafhankelijke rijen of kolommen; lage rang betekent dat de matrix uit weinig informatie is opgebouwd en dus uit weinig metingen terug te winnen is. |
| **richting S1–S6** | de zes onderzoeksrichtingen van plan 06 (lokaliteit; lage rang van het verschil; quasi-1D π-systemen; het doelwit verkleinen; bevragingsalgebra; modellen als voorstellers). |
| **tensorhypercontractie (THC)** | een factorisatie van de vierindex-integralen en amplitudes in producten van kleine matrices, met een gecontroleerde fout; verlaagt de schaling van CC-methoden. Richting S2. |
| **universele functionaal** | het deel van de DFT-energie dat niet van de uitwendige potentiaal afhangt (Hohenberg–Kohn; Levy). Exact maar in het algemeen niet efficiënt berekenbaar. |
| **T3, T3′** | T3: het vermoeden dat de correctie Δ₂ exponentieel afvalt met de grafafstand voor onze klasse (bewijsplan geschreven; nieuw voor coupled cluster). T3′: de sterkere uitspraak dat de correctie *sneller* afvalt dan de DFT- en CC-Hessianen elk; de uitspraak waar plan 05 iets aan zou hebben; getoetst door X9. |
| **substitutie** (Powell–Toint) | de truc waarmee minder matrix-vectorproducten nodig zijn dan een gewone kleuring: je lost de elementen van achteren naar voren op en trekt wat je al weet af. Exact zonder ruis; met ruis een milde versterking (X1d). Aantal producten bij benzeen 6–7 in modes (X1c), begrensd met de grootte onder bindingspatronen (X8). |
| **X0–X4** | de eerste experimenten: lezen van de grensartikelen (gedaan); rang/kleuring van de benzeen-Δ₂; gevoeligheid van bandposities; X3a wat LNO bewaarde (gedaan) en X3b de afvalconstante; Mathlib-inventaris. |
