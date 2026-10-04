# Meta – Creative testing (štruktúra testov, odlišnosť, iterácia) – tactics

Destilát: vybrané, použiteľné poznatky z viacerých zdrojov. Tento súbor agent číta aktívne.
Sú to odporúčania, nie pravidlá; brány a metodika skillov majú prednosť.

**Posledná aktualizácia:** 2026-10-01
**Zdroje:** [Search Engine Land 2026-05-29](sources/2026-05-29-searchengineland-creative-testing-structure.md),
[Jon Loomer 2026-05-26](sources/2026-05-26-jonloomer-agency-mistakes.md),
[Common Thread Collective, bez dátumu](sources/2026-10-01-commonthread-methodology-meta.md)
**Súvisiaca metodika skillu:** `.claude/skills/meta-ads-manager/references/testovanie-metodika.md`,
`tvorba-kreativ.md`, `strategicky-research.md`

---

## Odporúčania / postupy

**Kozmetická variácia nie je test.** Kreatívy líšiace sa iba farbou, overlayom či drobnou zmenou textu
Meta vyhodnotí ako takmer identické: nenájde nové publikum, reklamy si konkurujú a rozpočet zoberie
jedna-dve. Rozdiel má byť v hooku, emočnom drivri, pozicionovaní, motivácii alebo formáte.
(SEL 2026-05; zhoduje sa so skillom „diverzita > objem“)

**Dve fázy: najprv hodnota, potom objem** (SEL 2026-05):
1. *Makro-test:* 2–3 odlišné koncepty (uhol, formát, štýl) proti sebe, cieľom je víťazný koncept.
2. *Mikro-test:* až nad víťazom iterovať komponenty (hook v prvých 3 s, tempo/hudba, CTA), aby sa
   predĺžila životnosť a zlepšila efektivita.

V projekte to zodpovedá poradiu z `testovanie-metodika.md`: Úroveň 1 koncept/angle → Úroveň 2 hook →
neskôr CTA. Makro-test je v B1 `test_design: concept-comparison`, mikro-test `isolated` s jednou premennou.

**Koncepty z hlasu zákazníka:** recenzie, tikety podpory, komentáre, prieskumy, Reddit/Quora.
Hľadať opakované frustrácie, námietky a emočný jazyk; z nich slovník copy. Netlačiť trendy a virálne
formáty. (SEL 2026-05; pokrýva Režim S a `deep-research.md`)

**Každý víťaz musí mať pomenovaný insight.** Ak nevieme povedať, ktorá námietka, fráza z recenzie
alebo use case stojí za víťaznou reklamou, škálujeme na šťastí. V projekte: pri Režime C zapísať do
`learnings.md` aj zdrojový insight víťaza (trasovateľný do `deep-research.md`). (SEL 2026-05)

**Pravidelný kreatívny audit** (SEL 2026-05 navrhuje týždenne), tri otázky:
- Sú posledné nové reklamy tri odlišné uhly, alebo jedna reklama trikrát?
- Aký insight stál za poslednými víťazmi?
- Aký trend ukazujú dáta naprieč kreatívami (formát, typ talentu), nie jednotlivé metriky?

**Keď výkon slabne, začni pri reklamách.** Pri zjednodušenej štruktúre nesie výkon hlavne kreatíva.
Jedna reklama môže mať až 5 primárnych textov, 5 nadpisov a 10 médií a správa sa ako kedysi ad set;
z toho, čo funguje, tvoriť nové odlišné reklamy namiesto vynucovania rozpočtu víťazovi (vypínaním
ostatných). (Loomer 2026-05)

**Bez testovacieho rozpočtu a bez vypínania** (CTC, bez dátumu): nové koncepty idú priamo do trvalých
kampaní a súťažia o celý rozpočet; reklamy sa nevypínajú podľa historického ROAS, lebo Meta rozhoduje
podľa signálov, ktoré minulý výkon nezachytáva. Reklama, ktorá málo minula (< 3× cieľovej CPA), dostane
druhú šancu v samostatnej ASC (`meta-struktura-tactics.md`). Pre skill je to protipól (viď Rozdiel).

**Lo-fi a founder-led:** produkčná kvalita nie je podmienka. Autorke fungujú najlepšie reklamy so
zakladateľom, pôsobia natívne. (SEL 2026-05; archetyp Founder POV je v `meta-kreativa-tactics.md`)

## Na čo si dať pozor

- Zdroj nemá čísla (prahy, dni, rozpočty). Dátová brána a verdikt ostávajú podľa `test-plan.json`
  a `testovanie-metodika.md`.
- „Víťaz makro-testu“ platí až po splnení dátovej brány; pri malých SK účtoch to môže trvať týždne.
- Metrika „počet vyrobených kreatív“ nie je cieľ. Odlišnosť konceptov je dôležitejšia než tempo šprintu.

## Kedy použiť

- Režim A: kontrola, či sú navrhnuté koncepty naozaj odlišné (nie kozmetické varianty).
- Režim B1: voľba medzi `concept-comparison` (nový koncept) a `isolated` (iterácia víťaza).
- Režim C/D: týždenný alebo šprintový audit, zápis insightu víťaza do `learnings.md`.

## Rozdiel oproti metodike skillu

- **Mikro-test naraz na viac komponentov:** SEL navrhuje v jednej vlne 3 hooky + 2 tempá + viac CTA.
  Skill pri iterácii mení **jednu premennú** (modulárna izolácia) alebo vedome postaví DCT maticu.
  Platí skill; kombinácia bez DCT dá víťaznú kombináciu, nie poznatok o premennej.
- **Rytmus auditu:** SEL týždenne, skill pracuje v 14-dňových šprintoch s fatigue skóre. Týždenný
  audit je doplnok (kvalitatívna kontrola odlišnosti), nie náhrada verdiktu ani šprintu.
- **Testovací rozpočet a verdikt Vypnúť:** CTC nemá testovací rozpočet ani nevypína reklamy. Skill má
  pravidlo 60-30-10 (Sandbox alebo in-place podiel), verdikt VYPNÚŤ v `metriky-diagnostika.md` a
  vypnutie mŕtveho variantu po 2–3× tolerovanej CPA (`testovanie-metodika.md`). Platí skill; zmena iba
  vedome so súhlasom človeka. Zhoda: in-place testovanie a nevynucovať rozpočet víťazovi vypínaním ostatných.

## Sporné / názory sa líšia

- **Objem vs. hodnota:** Adrio (2026-05, výrobca AI nástroja) tvrdí, že víťaz sa nájde objemom.
  SEL (2026-05) a skill: objem až po nájdení hodnotného konceptu, inak rozdrobený rozpočet a learning.
  Zhoda: testovať odlišné koncepty. Pre malé SK účty platí skill (sprint ad set, málo odlišných konceptov).
- **Testovací ad set a presun víťaza:** Loomer (2026-05) považuje Sandbox + presun víťaza za zastaraný
  (víťaz v prenesenom prostredí často nefunguje, reklama má byť viacnásobná). Od 2026-09-30 skill
  (`kampanova-struktura.md`, „Kde testovať nové kreatívy“) ponúka obe cesty: Sandbox pre `isolated`
  test a prenositeľný poznatok, in-place v Prospectingu ako predvolenú voľbu pri malom účte.
- **Vypínať slabé reklamy?** CTC (bez dátumu): nikdy podľa historického výkonu, Meta si spend rozdelí
  sama a nevýrazná reklama nič nestojí. Skill: vypnúť po dátovej bráne alebo pri jasne mŕtvom variante.
  Kedy čo: veľký účet s 20+ reklamami v ad sete a ROAS cieľom → nevypínanie je lacné; malý účet bez
  cost controlu → mŕtva reklama môže brať spend a skill platí. Fatigue (frequency, CTR pokles) CTC nerieši.
