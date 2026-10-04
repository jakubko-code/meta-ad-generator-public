# Testovacia metodika (Režimy B1 a B2)

Cieľ: postaviť test, ktorého výsledok je **interpretovateľný** — teda po skončení vieš povedať, *čo* spôsobilo úspech alebo zlyhanie. Všetko nižšie slúži jedinému: izolovať premennú a získať dosť dát, aby výsledok nebol šum.

## Povinné poradie

- **B1 pred produkciou:** zapíš hypotézu, testovanú premennú, konštanty, koncepty, primárnu metriku a dátovú bránu do `test-plan.json` v ad sete. Plán musí mať stav `planned` ešte pred písaním copy.
- **B2 po produkcii:** ku konceptom priraď iba vizuálne schválené súbory, doplň naming, tracker a launch checklist. B2 nemení hypotézu ani premennú podľa toho, čo sa podarilo vygenerovať.

Použi `04-test-planning/test_plan.py` a štruktúru z `test-plan-template.json`. Jeden plán patrí jednej interpretovateľnej testovacej otázke.

## Tier systém — voľba metódy podľa rozpočtu

Nie každý účet má rovnaký objem — a metóda testovania by mala zodpovedať rozpočtu. Tri tiery:

| Tier | Mesačný budget na testovanie | Metóda | Štruktúra | Cieľ konverzií |
|------|------------------------------|--------|-----------|----------------|
| **1 — Concept Isolation** | Vysoký (5–10k €+/deň) | Separátny adset per koncept | Viac adsetov paralelne | 50+ konverzií / adset / týždeň |
| **2 — Persona Isolation** | Stredný | Separátny adset per persona | 2–3 adsety, 8–20 kreatív | 25–50 konverzií / adset / týždeň |
| **3 — Sprint Isolation** | Nízky (pod ~30k €/mesiac) | Všetky nové kreatívy do jedného "sprint" adsetu | 1 adset, algorithm sortuje | Čo objem dovolí |

**Tier 1 — Concept Isolation**
Každý testovaný koncept dostane vlastný adset s vlastným budgetom. Výsledky adsetu ti povedia, ktorý *koncept* (nie ktorá kreatíva) víťazí. Vyžaduje vysoký budget aby každý adset dosiahol štatisticky spoľahlivý objem. Pre väčšinu SK/CEE účtov nereálne.

**Tier 2 — Persona Isolation**
Adsety sú rozdelené podľa persony/avatara — každý adset obsahuje kreatívy zamerané na jednu skupinu. Konsoliduje spend do menej adsetov, čo dáva algoritmu viac dát na optimalizáciu. Vhodné keď máš jasne odlišné segmenty publika a stredný budget.

**Tier 3 — Sprint Isolation**
Všetky nové kreatívy idú do jedného dedikovaného "sprint" adsetu. Budget je skonsolidovaný → každá kreatíva dostane aspoň nejaký objem. Algoritmus sortuje víťazov sám. Kreatívy s nulovým výkonom po 3–7 dňoch sa vypínajú, víťazi sa presúvajú do hlavnej kampane.

> **Pre väčšinu SK/CEE klientov (menšie účty, obmedzený budget) platí Tier 3.** Sprint isolation nie je kompromis — je to správna stratégia pre daný objem. Chyba nastáva keď sa Tier 3 budget rozdelí do viacerých adsetov à la Tier 1 — každý adset dostane príliš málo a algoritmus sa nenaučí nič.



### A) DCT — Dynamic Creative Testing (framework 3:2:2)
Dnes najefektívnejší spôsob vďaka strojovému učeniu. Vytvoríš **jednu dynamickú reklamu**, do ktorej vložíš komponenty a Meta testuje ich kombinácie:

- **3 kreatívy** — napr. to isté video s 3 rôznymi hookmi.
- **2 primárne texty** — jeden dlhší emotívny, jeden kratší úderný.
- **2 nadpisy** — jeden na benefit, jeden na ponuku/zľavu.

**Kedy:** keď chceš rýchlo nájsť funkčnú kombináciu a máš dosť rozpočtu, aby algoritmus prešiel kombináciami. **Pozor:** DCT ti dá *víťaznú kombináciu*, ale slabšie izoluje *jednotlivú* premennú (efekty sa prelínajú). Na čistú odpoveď „ktorý hook" je presnejšia modulárna metóda.

> **2026:** Pri DCT zváž **Advantage+ Creative vypnúť**, ak chceš čisté čítanie komponentov — inak Meta pridá vlastné AI variácie a zašumí ti maticu.

### B) Modulárna izolácia (postupné testovanie)
Keď chceš tvrdú odpoveď na jednu otázku. Testuj v tomto poradí, vždy meň len jednu os:

1. **Test hookov** — rovnaké telo, rovnaké copy, 3–5 rôznych začiatkov.
2. **Test formátov** — víťazný hook + telo vo verzii Video vs Statik vs Carousel.
3. **Test angles/copy** — víťazná vizuálna kreatíva + 3 rôzne angles v texte.

Pomalšie, ale každý výsledok je čistý a prenositeľný do ďalších kreatív ako poznatok.

**Rozhodovacie pravidlo:** Potrebuješ rýchlo funkčnú reklamu → DCT. Budeš z výsledku robiť *systémový poznatok* pre ďalšie kreatívy (čo robíš v agentúre naprieč klientmi) → modulárna izolácia.

## Hypotéza — povinný krok pred spustením testu

Pred spustením každého testu sformuluj **hypotézu**: čo presne očakávaš, o koľko, a prečo. Bez nej je test len „pustíme to a uvidíme" — a keď skončí, nevieš, čo si sa naučil.

Rozdiel oproti strategickému odôvodneniu konceptu (Režim A): odôvodnenie hovorí *prečo koncept existuje*. Hypotéza hovorí *čo presne od testu očakávam a kedy ho výsledok potvrdí alebo vyvráti*.

**Štruktúra hypotézy:**
> Očakávam, že [variant A] prekoná [variant B] v [metrika] aspoň o [číslo/%], pretože [dôvod opretý o dáta alebo insight].

**Príklady:**
- „Situačný hook (osoba pri počítači) prekoná talking head v hook rate aspoň o 20 %, pretože cieľovka sa v konkrétnej scéne spozná rýchlejšie."
- „Testimonial video zníži CPA oproti produktovému videu aspoň o 15 %, pretože sociálny dôkaz znižuje nedôveru pri prvom kontakte."
- „Angle ‚nie je to normálne' prekoná ‚rýchly návrat do formy' v CTR, pretože adresuje problém, nie aspiráciu."

**Prečo to má zmysel:**
- Núti premyslieť *prečo* by mal variant vyhrať — nie len „skúsme obe".
- Robí z každého testu učenie: keď výsledok hypotézu potvrdí alebo vyvráti, vieš to zapísať do **Learnings** záložky trackera (pozri `tracker-navod.md`). Aj prehratý test je poznatok, ak si mal hypotézu.
- Chráni pred racionalizáciou po fakte („veď to bolo jasné") — hypotéza je zapísaná *pred* spustením.

Hypotézu zapíš do `test-plan.json` v Režime B1. Po naviazaní promptov je plán **nemenný produkčný kontrakt** — výsledok doň nedopisuj, pretože by sa zmenil jeho SHA-256. Po vyhodnotení (Režim C) zapíš potvrdenie alebo vyvrátenie hypotézy do `tracker.md` a prenositeľný poznatok do `learnings.md`.

## Čo testovať ako prvé — prioritný žebríček

Nie všetky premenné majú rovnaký dopad. Testuj od najväčšieho k najmenšiemu — vyšší level ti dá väčší lift za rovnaký rozpočet.

| Úroveň | Čo testuješ | Dopad | Náročnosť výroby | Testuj ako... |
|--------|-------------|-------|------------------|---------------|
| **1 — Concept / Angle** | Základná myšlienka, uhol pohľadu | Veľmi vysoký | Vysoká | Prvé vždy |
| **2 — Hook (0–3 s)** | Začiatok videa / headline statiku | Veľmi vysoký | Nízka–stredná | Hneď po koncepte |
| **3 — Formát** | Video vs. statik vs. carousel vs. UGC | Vysoký | Vysoká | Ak máš kapacitu |
| **4 — Telo / stred** | Proof points, demonštrácia, body copy | Stredný | Stredná | Po víťaznom hooku |
| **5 — CTA** | „Kúp teraz" vs. „Zisti viac" vs. urgencia | Stredný | Nízka | Neskôr |
| **6 — Vizuálne prvky** | Farby, font, kompozícia | Nízky–stredný | Stredná | Neskôr |
| **7 — Copy variácie** | Drobné textové zmeny | Nízky | Nízka | Posledné |

**Praktické pravidlo:** Ak nevieš, kde začať — začni na Úrovni 1 (rôzne angles, rovnaký formát a hook štýl). Keď máš víťazný koncept, prejdi na Úroveň 2 (varianty hooku). Toto poradie maximalizuje, čo sa naučíš za každé euro míňané na testovanie.

**Pre video ads — priority premenných:**

| Premenná | Príklady | Priorita |
|----------|----------|----------|
| Hook (prvé 3 s) | Otázka vs. tvrdenie vs. pattern interrupt | 🔴 Kritická |
| Talent v hooku | Zakladateľ vs. zákazník vs. UGC tvorca | 🔴 Kritická |
| Vizuál hooku | Produkt vs. osoba vs. text on screen | 🟡 Vysoká |
| Štruktúra tela | Problém→Riešenie vs. Features→Benefits | 🟡 Vysoká |
| Štýl CTA | Mäkké vs. tvrdé vs. urgentné | 🟢 Stredná |
| Dĺžka videa | 15 s vs. 30 s vs. 60 s | 🟢 Stredná |
| Hudba / zvuk | Energická vs. pokojná vs. bez hudby | 🟢 Stredná |

**Pre statické reklamy — priority premenných:**

| Premenná | Príklady | Priorita |
|----------|----------|----------|
| Hlavný vizuál | Produkt vs. lifestyle vs. UGC štýl | 🔴 Kritická |
| Angle headlinu | Benefit vs. pain point vs. social proof | 🔴 Kritická |
| Vizuálny štýl | Čistý vs. plný vs. natívny/organický | 🟡 Vysoká |
| Text overlay | Áno vs. nie vs. množstvo | 🟡 Vysoká |
| Farebná schéma | Brand farby vs. kontrast vs. tlmené | 🟢 Stredná |
| CTA tlačidlo | „Zistiť viac" vs. „Kúpiť teraz" vs. „Získať ponuku" | 🟢 Stredná |

## Štatistické požiadavky — kedy je výsledok spoľahlivý

Orientačná kontrola objemu dát z predchádzajúcej sekcie hovorí *kedy začať čítať*. Toto hovorí *ako veľký objem treba na konkrétnu úroveň istoty*. Použi pri plánovaní rozpočtu a dĺžky testu.

**Konverzné testy (Purchase / Lead) — potrebné kliknutia / variant:**

| Baseline konv. pomer | Detekovateľný lift | Potrebné kliknutia / variant |
|----------------------|-------------------|------------------------------|
| 1 % | 20 % relatívny | ~3 800 |
| 2 % | 20 % relatívny | ~1 900 |
| 5 % | 20 % relatívny | ~760 |
| 1 % | 50 % relatívny | ~610 |
| 2 % | 50 % relatívny | ~305 |

**CTR testy — potrebné impresie / variant:**

| Baseline CTR | Detekovateľný lift | Potrebné impresie / variant |
|--------------|--------------------|-----------------------------|
| 0,5 % | 20 % relatívny | ~150 000 |
| 1,0 % | 20 % relatívny | ~75 000 |
| 2,0 % | 20 % relatívny | ~37 500 |
| 1,0 % | 50 % relatívny | ~12 000 |

**Zjednodušené pravidlo (pre bežné rozhodnutia):**
- Konverzný test: min. 50 konverzií / variant, min. 7 dní
- CTR test: min. 100 klikov / variant, min. 7 dní

**Odhadovaná dĺžka testu podľa denného rozpočtu a CPA:**

| Denný rozpočet / variant | Cieľová CPA | Denné konverzie | Dní do 50 konverzií |
|--------------------------|-------------|-----------------|---------------------|
| 50 € | 25 € | 2 | 25 dní |
| 50 € | 10 € | 5 | 10 dní |
| 100 € | 25 € | 4 | 13 dní |
| 100 € | 10 € | 10 | 5 dní → min. 7 dní |
| 200 € | 25 € | 8 | 7 dní (minimum) |

> Pri nízkych objemoch (lead-gen služby, B2B) tieto prahi konverzný objem skoro nikdy nedosiahneš — pozri `segmenty.md` pre stratégiu verdiktovania na vyššom evente.

## Architektúra testu — kde test postaviť

Klasický model je **dedikovaná testovacia kampaň** (ABO), oddelená od hlavnej „Scale" kampane. Má svoje výhody (čistota, kontrola rozpočtu na variant) aj svoju 2026 nevýhodu:

> **Test → Scale friction (2026):** kreatíva, ktorá vyhrá v izolovanom test ad sete, sa pri prenose do škálovacej kampane (iné prostredie aukcie, iný objem, iné publikum) často nespráva rovnako. Andromeda zvýraznila, že prostredie rozhoduje.

Preto zváž dva prístupy a vyber podľa situácie:

| Prístup | Ako | Kedy zvoliť |
|---------|-----|-------------|
| **Dedikovaná test kampaň (ABO)** | Samostatná kampaň len na test, broad, fixný rozpočet/variant | Agentúrna prehľadnosť, multi-klient, keď chceš tvrdú izoláciu a reportovateľnosť |
| **Testovanie in-place / v ASC** | Nové kreatívy nasadíš priamo do cieľového (škálovacieho/ASC) prostredia a sleduješ ich relatívny výkon | Keď ti záleží hlavne na tom, či kreatíva obstojí *v reálnom* prostredí, a chceš sa vyhnúť scale frictionu. **Predvolená voľba pri malom účte (Štruktúra A / Tier 3)**, keď test nemá byť `isolated` |

Pri dedikovanej test kampani počítaj s tým, že výsledok je *indikácia*, nie záruka výkonu po škálovaní. Pri in-place teste víťaza nepresúvaj a nevynucuj mu rozpočet vypínaním ostatných reklám; nový variant, ktorý nedostal doručenie, nie je porazený. Detail a rozhodovacia tabuľka: `kampanova-struktura.md`, sekcia „Kde testovať nové kreatívy“.

## Publikum a umiestnenia

- **Broad (bez detailného cielenia).** Nechaj algoritmus nájsť cieľovku na základe samotnej kreatívy — to je dnes zmysel testu. Detailné cielenie by zamaskovalo, či ťahá kreatíva alebo publikum.
- **Advantage+ placements** — nech sa kreatíva otestuje tam, kde reálne pobeží.
- Pri teste *neoddeľuj* publiká do viacerých ad setov kvôli premennej kreatívy — fragmentuješ dáta. Premennú drž na úrovni reklamy/komponentu, nie publika.

## Nemiešaj formáty v jednom teste

Video proti statiku v jednom ad sete **nie je férový test**. Meta systematicky preferuje niektoré formáty (video/Reels dostávajú v aukcii iné zaobchádzanie ako statiky) — takže rozdiel vo výkone môže spôsobiť formát, nie kreatíva. Rovnaká pasca platí pre výrazne odlišné dĺžky videa.

**Pravidlá férového porovnania:**
- Testuj **video proti videu, statik proti statiku, carousel proti carouselu** — nie krížom.
- Drž **porovnateľné dĺžky** — netestuj 15 s spot proti 2 min demu; formát dĺžky sám o sebe skreslí výsledok.
- Ak *chceš* zistiť, ktorý formát funguje lepšie (video vs. statik), je to legitímny test — ale je to **test formátu (Úroveň 3)**, nie test hooku/angle. Postav ho vedome ako porovnanie formátov, nie ako vedľajší efekt zamiešaný do iného testu.

> **Poznámka k Tier 3 / sprint adsetu:** aj keď pri malom budgete konsoliduješ všetko do jedného sprint adsetu, drž v ňom formáty oddelene v čítaní výsledkov — pri verdikte porovnávaj video s videom a statik so statikom, nie naprieč. Ak máš kapacitu, sprint pre video a sprint pre statik zvlášť je čistejší.

## Rozpočet a čas

- **Denný rozpočet ad setu:** orientačne **0,5–1× cieľová CPA** na jeden variant. Príliš málo = nikdy nenazbieraš signál; príliš veľa = drahé učenie.
- **Learning fáza:** Meta potrebuje čas a objem (~50 výsledkov / 7 dní / ad set je orientačný prah stabilného learningu). **Prvé ~72 hodín do testu nezasahuj** — žiadne pauzy, edity, zmeny rozpočtu. Každý zásah reštartuje učenie.
- Veľké edity dávkuj (bundluj), nech nereštartuješ learning opakovane.

## Kontrola objemu dát — KEDY smieš čítať výsledky

Toto je najdôležitejšia poistka proti zlým rozhodnutiam. **Pred verdiktom musí variant prejsť kontrolou objemu dát.** Hodnoty kalibruj podľa účtu, ako orientačný štart:

| Brána | Orientačný prah | Prečo |
|-------|-----------------|-------|
| **Čas** | min. 3 dni (72 h) po learningu | menej = čítaš learning šum |
| **Impresie / variant** | aspoň ~8 000–10 000 | „soft" metriky (hook/hold/CTR) potrebujú objem, aby boli stabilné |
| **Spend / variant** | aspoň ~1–2× cieľová CPA | menej = na „hard" verdikt (CPA/ROAS) nie sú dáta |
| **Konverzie / variant pre hard verdikt** | ideálne 10+ (min. niekoľko) | pri 1–3 konverziách je CPA/ROAS prakticky náhoda |

**Dôležité rozlíšenie:**
- **Soft metriky** (hook rate, hold rate, CTR) sú spoľahlivé skôr — pri pár tisíc impresiách už čítaš signál o kreatíve.
- **Hard metriky** (CPA, ROAS) potrebujú konverzný objem. Ak ho nemáš, **neverdiktuj na hard** — povedz nahlas, že je to predbežné, a oprie sa o soft signál + (ak treba) o vyšší event vo funneli (napr. button click pri službách s nízkym objemom konverzií).

Ak test kontrola objemu dát nesplnená: verdikt je **predbežný**. Buď nechaj bežať, alebo (pri jasne mŕtvom variante — minul 2–3× tolerovanú CPA bez výsledku) vypni.

## Naming konvencia testovacích kreatív

Naviaž na konvenciu účtu (pozri `kampanova-struktura.md`: `[TYP] - [ANGLE/HOOK] - [verzia]`, napr. `VID - Pain Hook - v1`). Pre testovanie pridaj **stopu testovanej premennej**, nech je v reportingu jasné, čo sa líši:

```
Reklama:  [FORMÁT] - [TESTOVANÁ PREMENNÁ] - [konštanta] - [verzia]
Príklady: VID - HOOK-A_Problem - TeloX - v1
          VID - HOOK-B_Callout - TeloX - v1
          IMG - ANGLE_Zdravie - StatikY - v1
```

Konzistentné pomenovanie je predpoklad toho, aby sa dal výsledok v Režime C automaticky priradiť k premennej (aj cez `name CONTAIN` filter v Meta Ads MCP).

## Psychológia víťazov — správne očakávania

Väčšina kreatív nevyhrá. A to je normálne — nie chyba stratégie, nie zlá kreatíva.

Na základe dát z veľkých Meta účtov platí: len ~4–8 % kreatív sa stane víťazmi (kreatívy ktoré výrazne prekonajú mediánový výkon účtu). Zvyšok sú mid-range (bežia dlho, ale bez výnimočného výkonu) alebo loseri (vypnuté pred 28 dňami bez signálu).

**Čo z toho plynie pre testovanie:**

- Systém funguje na **objeme a variácii** — viac testov = viac šancí natrafiť na víťaza. Nie preto, že by priemerná kreatíva bola lepšia, ale preto, že sa zvyšuje pravdepodobnosť výnimočnej.
- Keď test neskončí víťazom, nie je to zlyhanie — je to dáta. Každá „prehratá" kreatíva zúži priestor hľadania.
- **Neinterroguj losera** — viac sa naučíš z analýzy toho, prečo víťaz vyhral, než prečo loser prehral.
- Výsledky sú štatisticky riedke — pri malých SK účtoch (nízky budget, malé publikum) bude hit rate nižší a víťazi vzácnejší než v benchmarkoch z veľkých trhov. To neznamená, že systém nefunguje — znamená to, že treba dlhší horizont a trpezlivosť.

> **Pre SK/CEE trh:** benchmarkové čísla z veľkých štúdií (hit rate 4–8 %, spend thresholdy v stovkách USD) platia pre iné veľkosti účtov. Nepoužívaj ich doslovne. Dôležitý je princíp: víťazi sú vzácni, objem testov pomáha, a väčšina kreatív skončí ako mid-range alebo loser — aj na najlepšie spravovaných účtoch.



Testovacia kampaň je len jedna časť ekosystému. Celkový rozpočet účtu rozdeľ systematicky:

| Alokácia | Kde | Čo |
|----------|-----|-----|
| **60 %** | Hlavná / škálovacia kampaň | Overené víťazné kreatívy — dlhodobo stabilný výkon |
| **30 %** | Iteračná kampaň | Variácie víťazov — nové hooky, iné formáty, upresnené copy |
| **10 %** | Testovacia kampaň | Úplne nové koncepty a angles |

Toto rozdelenie chráni celkový výkon účtu — väčšina peňazí pracuje v overenom prostredí, menšia časť systematicky hľadá nových víťazov.

## 14-dňové kreatívne šprint cykly

Únava kreatív je nevyhnutná. Kľúčom nie je reaktívne reagovať keď niečo prestane fungovať — ale **proaktívne nasadzovať nové kreatívy skôr, ako staré vyhorá**.

**Cieľ:** 2–4 nové testované kreatívy každé 2 týždne v obehu.

Prakticky to znamená:
- Každý 14-dňový cyklus spustiť nový batch kreatív do testovacej kampane
- Víťazov z predchádzajúceho cyklu presunúť do hlavnej kampane (cez Post ID); pri in-place teste ostávajú v Prospectingu
- Unavené kreatívy (fatigue skóre 65+, pozri `fatigue-detector.md`) vypnúť alebo presunúť do rotácie

Tým vybuduješ **systém, nie ad-hoc reakciu** — účet má neustále čerstvý prísun dátami overených kreatív a nikdy nie si závislý na jednej unavujúcej reklame.

> **Poznámka k Medante a podobným lead-gen klientom:** 2–4 kreatívy týždenne je tempo pre e-com s väčším budgetom. Pri menšom účte s obmedzenou produkčnou kapacitou stačí 1–2 nové kreatívy za 2 týždne. Dôležitejší je rytmus ako objem.



- [ ] **Hypotéza sformulovaná** — čo, o koľko, prečo (zapísaná pred spustením).
- [ ] **Learnings načítané** — `testing/learnings.md` a aktívne testy; použité ID v `test-plan.json` → `learnings`.
- [ ] Jedna premenná izolovaná (`test_design: isolated`, validátor overí konštanty), alebo vedome `concept-comparison` / `pilot`, alebo čistá DCT matica.
- [ ] Pri statickom headline teste je vizuál spoločný; inak výsledok označ ako porovnanie kreatív s obmedzenou izoláciou (AI render mení celý obrázok).
- [ ] **Formáty nemiešané** — video proti videu, statik proti statiku; porovnateľné dĺžky.
- [ ] Broad publikum, Advantage+ placements.
- [ ] Rozpočet 0,5–1× cieľová CPA / variant.
- [ ] Kontrola objemu dát definovaná aj číselne (`minimum_days`, `minimum_impressions_per_variant`, `minimum_events_per_variant`); pod prahom je verdikt predbežný.
- [ ] Naming nesie testovanú premennú.
- [ ] Advantage+ Creative podľa zámeru (vyp. pre čistú izoláciu).
- [ ] **Tracking overený pred launchom** — pixel/konverzný event funguje, čistá URL bez UTM a agentúrne UTM v poli „Parametre URL“ (`kampanova-struktura.md`), správny konverzný event nastavený. Test s rozbitým trackingom = stratené dáta.
- [ ] **Stabilné obdobie** — nespúšťaj tesne pred sviatkami, Black Friday alebo počas výpadku webu/e-shopu. Časové skreslenie sa tvári ako rozdiel v kreatíve.
- [ ] **Zdravotnícky/wellness klient?** — over compliance kreatívy aj naming eventov podľa `health-wellness-restrikcie.md` (osobné atribúty v copy, before/after, kódované názvy eventov bez diagnózy).
- [ ] Všetky varianty spustené naraz (rovnaký štart) — nie postupne, inak má prvý náskok.
- [ ] Plán „čo po teste" pre každý možný výsledok.
