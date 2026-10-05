# Brief for the supervisor — CFOUR for the coupled-cluster anchors (5 October 2026; ≤ 150 words, question first, as the 27 Sep rule says)

*For the user to send or say; English first, Dutch below. Facts behind it: pyscf has analytic CCSD(T) gradients but no analytic second derivatives; our
anchors are finite differences of those gradients (step 0.005 bohr, pair checks ≤ 1e-4 a.u., an energy-route second check); CFOUR has analytic CCSD(T)
second derivatives and is free for academic use on request.*

---

**Question:** does the group have, or can it obtain, an academic CFOUR licence, and would you support a short test with it?

**Why:** my anchors are CCSD(T) force-constant matrices (benzene, naphthalene, pyridine, fluorobenzene, benzonitrile; anthracene finishing). I build
them by finite differences of analytic gradients in pyscf, with pair checks and a second energy route — it works, but it costs 6 gradients per
symmetry-unique atom and days per molecule above 20 atoms. CFOUR computes the same matrix analytically. One benzene run in CFOUR would (1) check my
finite-difference anchors against an analytic reference and (2) show whether larger anchors become affordable that way. I would run it myself; I only
need the licence and, if available, an installation.

---

**Vraag:** heeft de groep een academische CFOUR-licentie, of kan die worden aangevraagd, en steun je een korte test ermee?

**Waarom:** mijn ankers zijn CCSD(T)-krachtconstantenmatrices (benzeen, naftaleen, pyridine, fluorbenzeen, benzonitril; antraceen is bijna klaar). Ik
bouw ze met eindige verschillen van analytische gradiënten in pyscf, met paarcontroles en een tweede energieroute — dat werkt, maar kost zes gradiënten
per symmetrie-uniek atoom en dagen per molecuul boven de 20 atomen. CFOUR rekent dezelfde matrix analytisch uit. Eén benzeenrun in CFOUR zou (1) mijn
eindige-verschillen-ankers tegen een analytische referentie controleren en (2) laten zien of grotere ankers zo betaalbaar worden. Ik voer het zelf uit;
ik heb alleen de licentie nodig en, als die er is, een installatie.
