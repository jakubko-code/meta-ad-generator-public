# Meta – Kreatíva (formáty, archetypy, hooky) – tactics

Destilát: vybrané, použiteľné poznatky z viacerých zdrojov. Tento súbor agent číta aktívne.
Sú to odporúčania, nie pravidlá; brány a metodika skillov majú prednosť.

**Posledná aktualizácia:** 2026-09-30
**Zdroje:** [Stackmatix 2026-09-09](sources/2026-09-09-stackmatix-meta-ads-examples.md),
[Adrio 2026-05-12](sources/2026-05-12-adrio-best-meta-ad-formats.md),
[Search Engine Land 2026-05-29](sources/2026-05-29-searchengineland-creative-testing-structure.md)
**Súvisiaca metodika skillu:** `.claude/skills/meta-ads-manager/references/tvorba-kreativ.md`,
`segmenty.md`, `testovanie-metodika.md`

---

## Odporúčania / postupy

**Základ každej reklamy:** jeden sľub, jeden produkt alebo dôkaz, jedna akcia. Produkt v kontexte
použitia, benefit pred featurou, jasná hierarchia hook → dôkaz → CTA. Najčastejšia chyba statiku je
chcieť povedať priveľa. Mobil ako prvý: veľký text, produkt viditeľný bez zoomu. (Stackmatix, Adrio)

**Archetypy statiku** (zásobník pri Režime A, nie povinná sada):

| Archetyp | Štruktúra | Kedy | Čo v ňom testovať |
|---|---|---|---|
| Problém-riešenie | problém → produkt → 1 konkrétny dôkaz → CTA | studené, Problem Aware | hook |
| Before/after | starý vs. nový stav; „pred“ môže byť proces alebo pocit, nielen fotka | vizuálny výsledok | vizuálny kontrast |
| Recenzia | konkrétny citát ako hook → produkt → dôkaz → CTA | teplé, potreba dôvery | citát |
| Porovnanie | starý vs. nový spôsob, 3–5 riadkov | zákazník má zaužívanú alternatívu | s čím porovnávame |
| Founder POV | „Postavili sme to, pretože…“ → bolesť → dôkaz | výrazný dôvod existencie, plný trh | úvodný pohľad |
| Offer stack | ponuka → 3–5 položiek → cena/úspora/termín → garancia → CTA | akcie, bundly, retargeting | podanie ponuky |
| Advertoriál | titulok ako článok → vizuál → 2–3 odrážky → zdroj → CTA | produkt s mechanizmom na vysvetlenie | titulok |
| Produkt + cena | čisté pozadie, cena, CTA | BOF, Most Aware | — |
| Iba text | text na plnej farbe | akcia, oznámenie, citát | — |
| UGC / lifestyle | selfie alebo situácia použitia, minimum textu | natívny pocit, studené aj teplé | — |

(Adrio: prvých 7; Stackmatix: before/after, UGC, text, lifestyle, produkt + cena.)

**Archetypy carouselu** (Stackmatix):
- rozpad benefitov: 1 karta = 1 benefit, posledná karta cena a CTA,
- **námietky: 1 karta = 1 námietka**, vhodné pri drahom alebo dôveru vyžadujúcom produkte,
- recenzie: 1 karta = 1 zákazník (hviezdičky, citát),
- návod krok za krokom, posledná karta = produkt,
- before/after cez swipe, katalógový výber (bestseller, novinka, bundle).

**Stories / Reels:** 9:16, minimum textu, text mimo horných a dolných UI zón. Sekvenčný príbeh cez
rámčeky (problém → čo som skúšal → riešenie → produkt + CTA). Titulky, lebo väčšina videa sa pozerá
bez zvuku. (Stackmatix, Adrio)

**Video:** hook 0–3 s → produkt a emócia 3–10 s → výsledok a CTA. Pre Stories/Reels 6–15 s.
Archetypy: demo, testimonial s konkrétnym výsledkom, founder/zákulisie, rýchla montáž. (Stackmatix)
Lo-fi obsah z mobilu a founder-led video môžu prekonať vyleštenú produkciu, lebo pôsobia natívne;
hodnota je v správe, nie v produkčnej kvalite. (SEL 2026-05)

**Pomery strán:** 4:5 feed, 9:16 Stories/Reels, 1:1 pre carousel, Marketplace a pravý stĺpec. Pri jedinom
pomere Meta orezáva alebo dopĺňa a správa slabne. (Adrio; zhoduje sa s workflow projektu)

**Formát podľa fázy a teploty publika:**

| Fáza | Formát | Archetypy |
|---|---|---|
| Awareness | video, Stories | emócia, príbeh, founder |
| Studené / consideration | statik, carousel, video | problém-riešenie, before/after, porovnanie, advertoriál, carousel benefitov |
| Teplé | statik, carousel | recenzia, founder POV, offer stack |
| Retargeting / konverzia | statik, DPA | offer stack, recenzia, porovnanie proti námietkam, carousel námietok |
| Lead gen | lead ads, carousel | bezplatná ponuka, predvyplnený formulár |

Retargeting potrebuje inú kreatívu ako prospecting. (Stackmatix, Adrio)

**Archetyp podľa typu testu** (Adrio): problém-riešenie na hooky, porovnanie na pozicionovanie,
before/after na vizuál, offer stack na ponuku. Hodí sa pri voľbe `test_variable` v B1.

**Social proof:** citát má byť konkrétny (čísla, situácia), nie „super“. Bez reálnych recenzií
**nevymýšľať**, použiť dôkaz o produkte. Garancia v offer stacku iba ak je pravdivá. (Adrio; zhoduje sa
s traceovaním claimov Agentom 7)

**Podľa odvetvia** (Stackmatix):
- B2B/SaaS: PAS; konverzia = demo alebo trial, nie nákup.
- Lokálne služby: jasná ponuka, lead ad, **reálne fotky tímu a screenshoty recenzií namiesto stock
  fotiek**. Hodí sa aj pre klientov, kde sú AI bannery zakázané.
- Fintech a drahé produkty: jeden konkrétny benefit, carousel s námietkami.
- Health/wellness: UGC, odborník, výsledok v živote. Before/after s naznačeným garantovaným výsledkom
  vedie k zamietnutiu (pozri `health-wellness-restrikcie.md`).

**Ad Library:** pravidelne sledovať 5–10 konkurenčných a vzorových stránok. Najdlhšie bežiaca verzia
z viacerých variácií je pravdepodobne víťaz. Inšpirácia aj mimo odvetvia. (Stackmatix)

**Portfólio:** rozdelenie 70/20/10 (overené víťazky / iterácie / nové uhly) ako orientačný rámec pre
rozpočet alebo produkčnú kapacitu. (Stackmatix)

## Na čo si dať pozor

- Štatistiky zo Stackmatixu (statiky 60–70 % konverzií, 85 % bez zvuku, DPA 3–5× ROAS, CPM 8–14 $) sú
  bez metodiky a z amerického trhu. Nepoužívať ako benchmark ani argument pre klienta.
- Oba zdroje predávajú vlastnú službu (agentúra, AI nástroj na statiky). Príklady značiek sú ilustratívne.
- Urgentnosť a zľava iba ak sú reálne (brand pravidlá klienta, `chyby-neopakovat.md`).
- Archetypy sú zásobník. Koncepty sa vyberajú z researchu konkrétneho produktu (pravidlo projektu).

## Kedy použiť

- Režim A: voľba archetypu a exekúcie konceptu, najmä porovnanie, advertoriál, offer stack a carousel,
  ktoré skill rozpracúva menej.
- Režim B1: voľba archetypu podľa testovanej premennej.
- Režim E: priradenie formátov k fázam funnelu a k retargetingu.
- Pri klientoch bez AI bannerov: archetypy s reálnymi fotkami, UGC a recenziami.

## Rozdiel oproti metodike skillu

- **Lookalike vs. broad:** Stackmatix odporúča lookalike zo zákazníkov s najvyššou LTV. Skill
  (`kampanova-struktura.md`) po Andromede uprednostňuje broad. Platí skill; lookalike iba ako vedomý test.
- **Obnova kreatív:** Stackmatix dáva kalendár (2–3 týždne, 3–6 týždňov, mesačne/týždenne,
  nekonzistentne). Skill riadi rotáciu fatigue skóre (`fatigue-detector.md`). Platí skill.
- **Test 7 statikov (Adrio):** mení naraz archetyp aj hook, preto je to `test_design: concept-comparison`,
  nie izolovaný test. Čítanie „po 5–10 dňoch podľa CTR a CPA“ nenahrádza číselnú dátovú bránu v
  `test-plan.json`. Nápad 4–7 odlišných archetypov okolo jednej ponuky je v súlade s princípom
  „diverzita > objem“.
- **70/20/10 a 5–10 aktívnych variácií:** skill takéto delenie nemá. Doplnok k rotačnému plánu,
  nie náhrada B1 plánu a dátových brán.
- **Hooky:** vzorce zo Stackmatixu sú pokryté knižnicou v `tvorba-kreativ.md`; nový je „my vs. starý
  spôsob“ (rozpracovaný ako archetyp porovnanie).

## Sporné / názory sa líšia

- **Pomer pre feed (faktický rozpor):** Stackmatix (2026-09) uvádza pre feed 1:1 (1080×1080), Adrio
  (2026-05) 4:5, lebo zaberá viac výšky mobilnej obrazovky. Workflow projektu používa 4:5 ako default
  a formáty sa pýtajú človeka. Pred citovaním klientovi overiť v aktuálnom Meta Ads Guide.
- **Objem vs. debata:** Adrio (2026-05, výrobca AI nástroja) tvrdí, že víťazný formát sa nájde objemom.
  Skill hovorí „diverzita > objem“ a proti takmer identickým variáciám. Zhoda je v tom, že treba testovať
  **odlišné** archetypy; nezhoda pri množstve variácií jedného konceptu. Platí skill.
- **Instagram vs. Facebook tón:** Stackmatix (2026-09) tvrdí, že Instagram uprednostňuje vyleštenú
  estetiku a Facebook UGC. Názor bez dát; overiť na umiestneniach konkrétneho účtu.
