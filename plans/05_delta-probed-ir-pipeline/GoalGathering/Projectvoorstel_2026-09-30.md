# Gemeten coupled-cluster-correcties op de harmonische krachtconstanten van PAK's, en een netwerk dat ze draagt

*Projectvoorstel, versie 30 september 2026, bijgewerkt 30 september 07:5x (het CC-getal in §4 na de lambda-correctie van 29 september) (twee pagina's). Vervangt de tekst van 26 september; oudere versies staan in de git-geschiedenis.
Wijzigingen komen in deze tekst zelf, met de datum in de kop. Student: Frederic Petrignani.*

## 1. Samenvatting

Eén pijplijn: een aromatisch molecuul erin, een infraroodspectrum eruit, met bandposities die aantoonbaar nauwkeuriger zijn dan de beste
beschikbare voorspelling, overal waar laboratoriumdata dat kunnen beslissen. De kern is een **gemeten coupled-cluster-correctie op de harmonische
krachtconstanten** (ΔH = H_CC − H_DFT), gekocht met zo weinig mogelijk CC-energieën, en een **netwerk** dat die correctie leert en overdraagt naar
moleculen waarvoor geen waarheid bestaat. Mandaat: met een desktop en een klein beetje Snellius een getraind netwerk dat voor een groot PAK de
spectrumvorm geeft, in 2027. Stand: een DFT-corpus van ruim vijfhonderd moleculen, één CCSD(T)-anker (benzeen) met een tweede (naftaleen) onderweg
en vier in aanbouw, en de eerste meting op echte CC-respons dat de geleerde meetvolgorde de kosten halveert.

## 2. De vraag

**Nauwkeurigheid:** verbetert de gemeten correctie de bandposities meetbaar tegenover PAHdb, per band tegen laboratoriumspectra? **Kosten:**
hoeveel CC-energieën per molecuul, en hoe groeit dat met de grootte? **Bereik:** geeft het netwerk voor een PAK van honderden atomen een spectrum
met foutbudget, per bandfamilie toegelaten of geweigerd?

## 3. De architectuur zoals besloten

| # | stap | besloten vorm |
|---|---|---|
| 1 | Corpus | DFT-geometrie en twee Hessianen per molecuul (B3LYP, ωB97X); analytische Hessian als tweede route |
| 2 | Labelfabriek | ΔH uit CC-energieën in bevroren lokale ruimtes: alle modeparen als kandidaat, in geleerde volgorde, met een stopregel; kosten per molecuul afgedrukt |
| 3 | Ankers | canonieke CCSD(T)-Hessianen waar betaalbaar; lokaliteit gemeten, niet aangenomen |
| 4 | ΔH-model | de correctie als blokobject (diagonaal plus koppelingen binnen een familie), equivariant netwerk op de DFT-Hessian |
| 5 | Training | leercurve op ongeziene moleculen; eerst DFT-proxy, dan CC-labels |
| 6 | Toets en licentie | per bandfamilie toegelaten of geweigerd door geregistreerde overdrachtstoetsen; bij weigering DFT met de reden |
| 7 | Spectrum | GVPT2 op analytische Hessianen; intensiteiten en hot bands gerapporteerd |
| 8 | Certificaat en officier | wat elke uitspraak waard is en wat ze kostte |

Boven twee ringen wordt de correctie op afgedekte fragmenten gemeten, met lokaal-CC-energieën of -gradiënten, mits de lokaliteitsmeting dat toestaat.

## 4. Waaraan succes wordt afgemeten (lijnen vooraf geregistreerd; stand 29 september)

| vraag | lijn | stand |
|---|---|---|
| Is een label betaalbaar? | ≥ 90 % van de moleculen binnen budget, ≤ 5 % valse stops | benzeen op CC: geleerde volgorde 0,54 van de blinde, orakel 124 energieën |
| Reist het label mee? | gecorrigeerde frequenties ≤ 3,3 cm⁻¹, koppelingsratio ≤ 0,5 | proxy: alle paren slagen (0,8–2,0 cm⁻¹); CC deze week |
| Leert het netwerk het juiste? | verslaat nulregel en geschaald krachtveld op ongeziene moleculen | proxy-curve op 600 (30 sep); CC-curve met 40 ankers in oktober |
| Kan het groot? | één lokaal-CC-label per dag op de desktop, drie ringen | meting in november op de PC |
| Klopt de vorm? | beter dan de opponenten binnen de gemeten bandonzekerheid, koud en warm | analytische route aangetoond; hot-band-toets deze week |

## 5. Plan, middelen, risico's

| wanneer | wat | beslist |
|---|---|---|
| 30 sep – 2 okt | naftaleen gelezen; vier ankers op CCSD(T); stopregel opnieuw geregistreerd | vragen 1 en 2 op CC-niveau |
| oktober | eigen PC (16 kernen, 128 GB); 40 ankers, ook gesubstitueerde naftalenen; CC-leercurve bij 10, 20, 40 | vraag 3 |
| november | gradiëntprijs op antraceenformaat; gesprek | vraag 4 |
| tot voorjaar 2027 | netwerk op CC-labels, licentie per familie, spectrum tegen het lab | vragen 3 en 5 |

**Middelen:** gehuurd tot nu ≈ €375; vanaf oktober een werkstation van ≈ €4.240 (≈ honderd ankers per maand); een kleine Snellius-aanvraag na de
eerste CC-overdrachtsmeting. **Risico's met toets:** ΔH draagt op CC-niveau niet over (oktobercurve; terugval het per molecuul gemeten label); de
gradiënt is te duur voor drie ringen (novembermeting; terugval energieën op fragmenten); de anharmonische stap is te ruizig (opgelost met
analytische Hessianen).

## 6. Wat ik van u vraag

1. Een kritische lezing van deze twee pagina's, vooral §3 en §4.
2. Eén koude, opgeloste meting van pyreen, of een bron ervan: één sterke band per familie bij 6,2, 7,7, 8,6 en 11–13 µm, bandcentra tot ≤ 1 cm⁻¹.
3. Het gesprek in november, met de CC-leercurve op tafel.

Ik rapporteer in berichten van ten hoogste 150 woorden, met de vraag voorop; logboek, pre-registraties en referenties staan in het repo.
