---
name: meta-ads-manager
description: >
  Riadi celý Meta Ads cyklus: strategický research, persony, pains, awareness a angle mapu; kampaňovú architektúru CBO/ABO; kreatívne koncepty avatar → angle → hook → CTA; B1 testovací plán pred výrobou; B2 handoff hotových kreatív; vyhodnotenie CTR, CPA, ROAS a ďalších metrík; fatigue a tracker. Použi pri novom klientovi, stratégii, štruktúre účtu, návrhu hookov, DCT alebo inom kreatívnom teste, diagnostike výkonu, rozhodnutí škálovať/iterovať/vypnúť, únave kreatív či aktualizácii trackeru. Podporuje e-com/DR, lead-gen, brand awareness, cultural/event, infoprodukt a B2B.
---

# Meta Ads — Tvorba, testovanie a vyhodnocovanie kreatív

> **Prostredie:** skill je spoločný pre Claude Code aj Codex. Meta Ads MCP nástroje (`ads_get_*`, `ads_insights_*`) sa používajú v Režimoch C a D, ak sú dostupné. Produkcia statických kreatív ide cez kroky 5–7 projektu, ale až po B1 testovacom pláne. Evidencia testov žije lokálne v `brands/<brand>/testing/`.

**Kreatíva je dnes cielenie.** Po algoritmickom posune (Andromeda, Advantage+) Meta nájde publikum sama — na základe toho, kto na kreatívu reaguje. Targeting sa zúžil na pár pák, kreatíva sa stala hlavnou pákou výkonu. Z toho vyplýva celá logika tohto skillu: vyrábaj kreatívy systematicky, testuj ich tak, aby si vedel **čo** zafungovalo, a vyhodnocuj ich **podľa dát, nie pocitov**.

## Tri princípy, na ktorých všetko stojí

1. **Izoluj premennú.** Ak v jednej reklame naraz zmeníš video, text aj nadpis, výsledok ti nepovie nič o príčine. Test má vždy jednu kontrolovanú os (hook / formát / angle / copy), zvyšok drž konštantný. Toto je dôvod, prečo dekonštruujeme kreatívu na stavebné bloky.
2. **Čítaj dáta až keď sú dáta.** Najčastejšia chyba nie je zlé rozhodnutie, ale predčasné rozhodnutie z objemu, ktorý je ešte šum. Pred akýmkoľvek verdiktom over **kontrola objemu dát** (dosť impresií / spendu / času na variant). Detaily v `references/testovanie-metodika.md`.
3. **2026: diverzita > objem.** Keď nájdeš víťaza, úlohou nie je vychrliť 20 takmer identických variácií — algoritmus ich kanibalizuje. Lepšie je testovať **odlišné koncepty** (iné angles, formáty, hooky). To mení aj logiku iterácie a škálovania.

---

## Ako skill funguje — režimy celého cyklu

Skill obsluhuje sedem prepojených režimov. **Najprv rozpoznaj, v ktorom režime používateľ je** (často povie priamo; ak nie, odvoď z toho, čo prinesie — brief = tvorba/plán, čísla alebo žiadosť o vyhodnotenie = vyhodnotenie, otázka „čo s tým" nad bežiacim testom = rozhodnutie).

| Režim | Spúšťač | Výstup |
|-------|---------|--------|
| **S — Strategický research** | „nový klient — z čoho staviame", „priprav stratégiu / mapu person", „nemáme angles, len produkt a recenzie", „koho vlastne oslovujeme" | **Strategická mapa** (persona → pain → fáza → angle → formát) + hviezdičkované koncepty s hypotézami, doložené citáciami z výskumu |
| **A — Tvorba** | „navrhni kreatívy/hooky", „daj mi angles pre…", máme produkt + cieľovku | Sada konceptov: avatar → angle → hook → telo → CTA, pripravená na test |
| **B1 — Plán pred produkciou** | „postav mi creative test", „čo máme vyrobiť", „setup pre DCT" | `test-plan.json`: hypotéza, jedna premenná, konštanty, koncepty, metrika a dátová brána |
| **B2 — Handoff po produkcii** | „priprav bannery na test", „doplň tracker", „launch checklist" | Konkrétne súbory/naming v `tracker.md` + launch checklist bez automatického spustenia |
| **C — Vyhodnotenie + rozhodnutie** | „vyhodnoť tieto kreatívy", „prečo to nefunguje", „čo vypnúť / škálovať" | **Vyhodnocovací report** s diagnostikou a verdiktom kill/iterovať/škálovať |
| **D — Únava kreatív** | „ktoré kreatívy dožívajú", „skontroluj fatigue", „čo rotovať", „frequency rastie" | **Fatigue report** so skóre (0–100) na kreatívu, prioritizovaný rotačný plán |
| **E — Kampaňová architektúra** | „ako nastaviť účet", „koľko kampaní/adsetov", „CBO alebo ABO", „reštruktúra účtu", „nový klient — založ účet" | **Kampaňový architektonický plán** (Štruktúra A/B/C/D, CBO/ABO, naming, rozdelenie rozpočtu, implementačný checklist) |

Režimy sa reťazia: **S → E → A → B1 → Image Ad Generator kroky 5–7 → B2 → človek spustí test → C → D**. Výsledok C/D sa vracia do S, A, B1 alebo produkcie podľa diagnózy. Režim E možno pri existujúcej aktuálnej architektúre preskočiť; avatara, angle, hook ani B1 plán pred novou produkciou nepreskakuj.

### Klient v hube (`~/agency-hub`)

Pri Režime S pre nového klienta a pri Režime E najprv prečítaj `~/agency-hub/clients/<kľúč>/` (`README.md`, `rozpocet.md`; kľúč z `~/agency-hub/clients.yaml`), ak existuje. Cieľ, cieľovku, dátumy a rozpočet ber odtiaľ a nepýtaj sa na ne. Rozdelenie rozpočtu v pláne E musí sedieť s `rozpocet.md`; odsúhlasenú zmenu zapíš tam (tabuľka + riadok do histórie).

### Vždy navrhni ďalší krok

Skill má sprevádzať, nielen reagovať. **Na konci výstupu každého režimu vždy navrhni konkrétny ďalší krok** — nečakaj, že sa používateľ spýta „čo teraz". Ďalší krok vyplýva z výsledku, nie je univerzálny:

| Po... | Výsledok / verdikt | Ďalší krok, ktorý navrhni |
|-------|---------------------|----------------------------|
| **Režim S** (strategický research) | Mapa + hviezdičkované bunky hotové | „Poďme postaviť kostru účtu (E) alebo premeňme prioritné bunky na koncepty (A)." |
| **Režim E** (kampaňová architektúra) | Plán hotový | „Teraz naplňme Prospecting/Sandbox kampane konceptmi — poďme na Režim A." Pri e-commerce navrhni aj textáciu DPA + prompt pre externú AI (`references/katalogova-textacia.md`). |
| **Režim A** (koncepty) | Sada konceptov hotová | „Pred produkciou z nich vytvorme B1 `test-plan.json`." |
| **Režim B1** | Validný plán so stavom `planned` | „Teraz vyrobme iba naplánované varianty cez Image Ad Generator kroky 5–7." |
| **Režim B2** | Súbory a tracker sú previazané | „Po výslovnom potvrdení človeka spusti test a po dátovej bráne sa vráť na C." |
| **Režim C** | Verdikt **Škálovať** | Sandbox: „Po tvojom potvrdení presuň cez Post ID do hlavnej kampane (nové nasadenie = nový riadok s Meta Ad ID) a zaraď do Fatigue Monitora (Režim D).“ In-place: „Víťaz ostáva v Prospectingu; zaraď ho do Fatigue Monitora (Režim D).“ |
| **Režim C** | Verdikt **Iterovať** | „Spravme cielenú variáciu — späť do Režimu A, ale meň len to, čo diagnostika označila." |
| **Režim C** | Verdikt **Vypnúť** | „Tento angle/hook nefunguje — chceš nový koncept (Režim A) pre iný avatar/angle?" |
| **Režim C** | Problém nie je hook/formát, ale **angle/persona** (kreatíva je dobrá, ale nechytá) | „Toto nie je remeselný problém — mapa person/pains je slabá. Vráťme sa do Režimu S a prekopme ju." |
| **Režim C** | Verdikt **Predbežná** | „Nechaj bežať ďalší týždeň, kontrola objemu dát ešte nebola splnená." |
| **Režim D** (fatigue) | Skóre 46+ (Raná únava a vyššie) | „Čas pripraviť náhradu — nový hook alebo koncept cez A, potom nový B1 plán." |
| **Režim D** | Všetko do 45 | „Portfólio je zdravé, ďalšia kontrola o týždeň." |
| **Tracker** | Po vyplnení/aktualizácii | Ak vznikol prenositeľný poznatok → „Zapíš to do learnings.md s ID; ďalší B1 ho načíta." |

Návrh ďalšieho kroku má byť **stručný, jedna až dve vety na konci odpovede** — nie samostatná veľká sekcia. Cieľom je, aby kolega vedel v čom pokračovať, nie aby skill diktoval celý proces.

---

## Čo potrebuješ vedieť (kontext pred prácou)

Nepýtaj sa na všetko naraz — vytiahni z konverzácie, čo už je, a dopýtaj sa len to, čo chýba a naozaj mení návrh.

**Vždy (jadro):**
- **Segment biznisu** — e-com/DR, lead-gen služby, brand awareness, cultural/event, infoprodukt, B2B high-ticket. **Najsilnejší vstup vôbec** — preformuje frameworky, „hard" metriku aj benchmarky. Po určení segmentu si **hneď načítaj `references/segmenty.md`** a ďalšie referencie čítaj cez jeho optiku.
- **Cieľ kampane a optimalizácia** — Sales (Purchase) / Leads / Awareness / Engagement. Určuje, na čo sa pozeráme ako na „hard" metriku.
- **Trh / jazyk** — SK / CZ / HU / PL / RO. Ovplyvňuje CPM, benchmarky aj jazyk výstupu.
- **Produkt a ponuka** — čo predávame, za koľko, aká je marža / cieľová CPA alebo ROAS (break-even).

**Silne odporúčané:**
- **Funnel fáza** testu — TOF (prospecting, broad) vs BOF (retargeting). Iné benchmarky, iné kreatívy.
- **História účtu** — má pixel dáta? Nový/fresh účet bez histórie sa správa inak: dlhší learning, opatrnejšie čítanie výsledkov.
- **Rozpočet** na test (denný/celkový) a ako dlho môže bežať.

**Pri režime A navyše:** uhly, hooky a formáty odvodzuj z researchu konkrétneho produktu (beliefs, CEP, objekcie). Nepoužívaj pre každý produkt rovnakú formulaickú sadu briefov.

**Pri režime S, A a B1 navyše — povinná vstupná kontrola:**
- Načítaj `brands/<brand>/testing/learnings.md` a aktívne riadky `tracker.md` (ak existujú). Koncepty a plán nesmú opakovať vyvrátenú hypotézu bez nového dôvodu.
- Použité learning ID, predchodcu testu a dôvod iterácie zapíš do `test-plan.json` → `learnings` (`reviewed`, `applied`, `predecessor_plan_id`, `note`). Nový klient bez learnings to uvedie v `note`.

**Pri režime C navyše:**
- **Ad account ID** (pre Meta Ads MCP), prípadne konkrétne entity IDs (campaign/adset/ad).
- Časové okno, za ktoré vyhodnocujeme.

---

## Rozcestník — kedy čítať ktorý reference

SKILL.md je rozcestník. Detaily sú v `references/`. Načítaj len ten súbor, ktorý je pre aktuálny režim relevantný:

- **`references/strategicky-research.md`** — **Čítaj pri Režime S** (nový klient / reštruktúra obsahu, alebo keď Režim C ukáže, že problém je angle/persona, nie remeslo). Je to krok 2 pipeline — výstupy sa zapisujú do `brands/<brand>/products/<produkt>/marketing-research/` (`deep-research.md`, `avatar-sheet.md`, `briefs.md`…), nie do samostatného dokumentu. Z výskumu odvodí persony, pains, angle mapu a prioritné koncepty. Odovzdáva surovinu do Režimu A, B1 a E.
- **`references/segmenty.md`** — **Čítaj ako prvé, hneď po určení segmentu** (platí pre všetky režimy). Šesť archetypov (e-com/DR, lead-gen služby, brand awareness, cultural/event, infoprodukt, B2B high-ticket), z ktorých každý preformuje, čo je „hard" metrika, kedy smieš verdiktovať, posun benchmarkov, sediace angles a definíciu víťaza. Reframuje default e-com logiku ostatných referencií.
- **`references/creative-sequencing.md`** — **Čítaj pri tvorbe konceptov (Režim A) a pri vyhodnocovaní (Režim C).** Ako Andromeda optimalizuje sekvenciu (nie jednotlivé reklamy), 5 fáz povedomia (Unaware → Most Aware) a ako pokryť každú fázu konceptmi, prečo reportovaný ROAS single reklamy zavádza, frequency ako škálovací signál, pravidlá vypínania v kontexte sekvencie.
- **`references/health-wellness-restrikcie.md`** — **Čítaj vždy, keď klient je zdravotnícky/wellness** (kliniky, fyzioterapia, stomatológia, doplnky výživy, kozmetika s liečebným tvrdením, chudnutie). Dve nezávislé vrstvy obmedzení: kreatíva/copy a event dáta/tracking. Relevantné pri A, B1 (plán/naming), B2 (handoff) aj C.
- **`references/kampanova-struktura.md`** — **Čítaj pri Režime E** (návrh/reštruktúra celej architektúry účtu). Štruktúry A/B/C/D podľa veľkosti účtu, CBO/ABO rozhodovanie, mapovanie na Tier systém, retargeting iba s dôvodom (predvolene ho robí Prospecting) a kontrola DPA, testovanie v Sandboxe alebo in-place v Prospectingu, audit Audience Segments a vylúčení, jednotná naming konvencia (trvalá kampaň aj testovacia), konsolidačná stratégia, korekcia broad namiesto lookalike.
- **`references/katalogova-textacia.md`** — **Čítaj pri texte pre DPA / katalógové reklamy** (po Režime E pri e-commerce). Pravidlá textu platného pre celý product set, dynamické polia Meta, formát `testing/dpa-textacia.md` s návrhom agenta a šablóna promptu pre ChatGPT / Gemini. Výstup externej AI je iba návrh na kontrolu. Na bannery sa nepoužíva, tie idú cez B1 a Image Ad Generator.
- **`references/tvorba-kreativ.md`** — Režim A. Avatary (psychografia, nie demografia), marketing angles, copy frameworky (PAS, AIDA, 4U, PASTOR), dekonštrukcia videa (hook/body/CTA), knižnica typov hookov. Čítaj pri tvorbe konceptov.
- **`references/testovanie-metodika.md`** — Režimy B1 a B2. Pred produkciou určí hypotézu, izolovanú premennú, konštanty, metódu a dátovú bránu; po produkcii doplní reálne súbory a launch checklist.
- **`references/metriky-diagnostika.md`** — Režim C. Definície metrík a ako sa počítajú, **kontextové benchmarky** (podľa funnelu, cieľa a trhu), diagnostický rozhodovací strom (hook vs telo vs CTA vs landing page), rozhodovací rámec kill/iterovať/škálovať. Čítaj pri vyhodnocovaní.
- **`references/fatigue-detector.md`** — Režim D. Scoring model (0–100) z pokles CTR, frequency, veku a CPA; životný cyklus kreatívy; diagnostika typov únavy; MCP volania pre časový rad (time_increment = 7); rotačný plán s prioritizáciou; prevencia. Čítaj pri detekcii únavy a plánovaní rotácie portfólia.
- **`references/tracker-navod.md`** — Návod pre B2, C a D: `tracker.md`, `learnings.md`, `fatigue.md`. B1 plán patrí do ad setu ako `test-plan.json`; tracker dostane reálny súbor až po produkcii.
- **`references/banner-produkcia.md`** — Most **B1 → kroky 5–7 → B2**. Mapuje naplánované koncepty na workflow v2 prompty, quality gates a hotové PNG.
- **`references/meta-mcp-playbook.md`** — Režim C a D s živými dátami. Presná sekvencia volaní Meta Ads MCP a mapovanie metrika → field (vrátane toho, že thumb-stop/hold rate sa na ad-leveli skladá z `video_continuous_2_sec_watched_actions` / `video_pXX_watched_actions` / `video_thruplay_watched_actions`). Čítaj, keď ťaháš dáta cez MCP.

**Znalostná databáza projektu:** pri režimoch S, E, A, B1, C a D otvor aj `references/meta/README.md` v koreni repozitára a príslušný `meta-<tema>-tactics.md`. Sú to poznatky z článkov: dopĺňajú referencie vyššie, ale nemenia ich ani brány. Ak im protirečia, uveď obe možnosti a skill neupravuj bez súhlasu človeka. Pri konkrétnom klientovi majú prednosť jeho vlastné `learnings.md`.

---

## Výstupné artefakty

Výstupy sú vždy v **slovenčine** (pre klienta/kolegov), expertné a bez vaty. Pri client-facing reportoch píš tak, aby tomu rozumel marketér klienta, nie len PPC špecialista — vysvetli „čo to znamená pre biznis", nielen číslo.

### Režim B1 → Creative Test Setup Sheet a `test-plan.json`

```
═══════════════════════════════════════════════════════════════════
CREATIVE TEST — SETUP SHEET
Klient/účet: [názov]   |   Trh: [SK/CZ/…]   |   Dátum: [DD.MM.RRRR]
═══════════════════════════════════════════════════════════════════

CIEĽ TESTU
- Otázka, na ktorú odpovedáme: [napr. „Ktorý hook zastaví scroll?"]
- Testovaná premenná (1 os): [hook / formát / angle / copy]
- Konštanty (čo držíme rovnaké): [...]

HYPOTÉZA
- Očakávam, že [variant A] prekoná [variant B] v [metrika] o [číslo/%], pretože [dôvod].
- (Po vyhodnotení doplniť: potvrdená / vyvrátená → poznatok do Learnings)

ARCHITEKTÚRA
- Metóda: [DCT 3:2:2 / modulárna izolácia]
- Štruktúra: [kampaň → ad set(y) → varianty], CBO/ABO: [...]
- Publikum: Broad (bez detailného cielenia), trh [...]
- Umiestnenia: Advantage+ placements
- Formáty nemiešané (video vs. video, statik vs. statik)

VARIANTY
| ID | Premenná (čo sa líši) | Konštanty | Naming |
|----|----------------------|-----------|--------|
| V1 | [...]                | [...]     | [...]  |

ROZPOČET A ČAS
- Denný rozpočet ad setu: [~0,5–1× cieľová CPA / variant]
- Min. doba behu: [pozri learning fázu]

KONTROLA OBJEMU DÁT (kedy smieme čítať výsledky)
- Min. impresie / variant: [...]
- Min. spend / variant: [...]
- Min. konverzie pre „hard" verdikt: [...]

PRED SPUSTENÍM OVERIŤ
- Tracking (pixel/event) funguje; URL bez UTM, agentúrne UTM v poli „Parametre URL“
- Stabilné obdobie (nie sviatky/výpadok)
- Všetky varianty štartujú naraz

CO ROBÍME PO TESTE
- [stručný next step podľa výsledku]
═══════════════════════════════════════════════════════════════════
```

Setup Sheet vždy materializuj aj ako validný `test-plan.json` (`schema_version: 2`) cez `test_plan.py init` podľa `04-test-planning/test-plan-template.json`. Všetky plánované statické varianty musia mať `concept_id`, `brief_id`, personu, awareness stage, angle, presný hook a formát. Zvoľ `test_design`:

- `isolated` — mení sa iba testovaná os; validátor vynúti, že ostatné strategické polia sú rovnaké,
- `concept-comparison` — varianty sa líšia vo viacerých osiach (`test_variable: concept`); poznatok platí pre koncept, nie pre jednu premennú,
- `pilot` — jeden koncept, verdikt vždy predbežný.

Dátovú bránu zapíš aj číselne (`minimum_days`, `minimum_impressions_per_variant`, `minimum_events_per_variant`). Nastav `status: planned` až po potvrdení smeru testu človekom.

### Režim B2 → handoff po produkcii

Po vizuálnom PASS priraď ku každému nasadzovanému `concept_id` konkrétny súbor, jeho SHA-256 z `outputs*/manifest.json`, naming a verziu v `testing/tracker.md`; Stav = Pripravená. Meta Ad ID a Adset ID doplň až po reálnom nasadení. Metriky nevymýšľaj a nechaj ich prázdne. Vytvor launch checklist, ale kampaň nespúšťaj ani nemeň bez výslovného potvrdenia človeka.

**Kreatívy dodané klientom** idú popri našich bez B1, scoringu a approval. Postup je v `NAVOD.md`, sekcia „Kreatívy dodané klientom“: kontrola faktov, súladu obrázka s textom a cieľovou URL a formátu voči umiestneniam, uloženie do `client-creatives/`, riadok v trackeri s `Plan ID = KLIENT-{dátum}` a `K01…`, upozornenie na narušenú izoláciu testu v spoločnom ad sete.

### Režim C → Vyhodnocovací report

```
═══════════════════════════════════════════════════════════════════
VYHODNOTENIE KREATÍV — [klient/účet]
Obdobie: [od–do]   |   Zdroj dát: [Meta Ads MCP / manuál]
═══════════════════════════════════════════════════════════════════

ZHRNUTIE (3–5 viet, pre klienta)
[Čo sa udialo a čo s tým ideme robiť — jazykom biznisu.]

GATE CHECK
[Splnil test kontrola objemu dát? Ak nie → verdikt je predbežný, povedz to nahlas.]

TABUĽKA VÝKONU
| Kreatíva | Spend | Impr. | Hook rate | Hold rate | Outbound CTR | CPA/CPL | ROAS | Verdikt |
|----------|-------|-------|-----------|-----------|--------------|---------|------|---------|

DIAGNOSTIKA (pre problémové kreatívy)
[Kde je úzke hrdlo: hook / telo / CTA / landing page — s odôvodnením z čísel.]

VERDIKT A ĎALŠÍ KROK
- Škálovať: [...]   (Sandbox: cez Post ID do hlavnej kampane — pozor na 2026 friction; in-place: nechať bežať, nevynucovať rozpočet)
- Iterovať: [...]   (čo konkrétne zmeniť)
- Vypnúť: [...]
═══════════════════════════════════════════════════════════════════
```

---

## 2026 — na čo myslieť (terminológia a posuny)

Meta sa hýbe; nepoužívaj zastarané názvy a zohľadni tieto posuny:

- **Advantage+ Sales Campaign (ASC)** — bývalé *Advantage+ Shopping*. Dnes pokrýva sales / leads / app. Pri škálovaní víťazov je toto častý cieľový formát.
- **Advantage+ Creative** (na úrovni reklamy) — Meta sama generuje AI variácie (nadpisy, popisy, crop). Pri **čistom teste premennej to vypni**, nech ti to nezašumí izoláciu; pri škálovaní zváž zapnutie.
- **Opportunity Score (0–100)** — účtová metrika v Ads Manageri s odporúčaniami; ťahá sa cez `ads_get_opportunity_score`. **Je vždy účtová**, nikdy ju nepripisuj konkrétnej kampani/kreatíve.
- **Test → Scale friction** — kreatívy, čo vyhrajú v dedikovanom test ad sete, sa v 2026 ťažšie prenášajú do škálovacej kampane (iné prostredie aukcie). Spomeň to a zváž testovanie bližšie k cieľovému prostrediu. Pozri `references/testovanie-metodika.md`.
- **~50 výsledkov / 7 dní / ad set** ostáva orientačný prah pre stabilný learning.

Pri akomkoľvek detaile, kde si nie istý aktuálnosťou (nové názvy, limity, policy), over si to webovým vyhľadávaním — radšej over, než napíš zastarané.

---

## Quality checklist (pred odovzdaním)

- [ ] **Segment určený** a `segmenty.md` zohľadnený — „hard" metrika a benchmarky sedia na archetyp, nie na e-com default.
- [ ] **Jedna izolovaná premenná** na test (alebo čistá DCT matica) — nie zmena viacerých vecí naraz.
- [ ] **Broad publikum** na testovanie kreatív (nie detailné cielenie).
- [ ] **Kontrola objemu dát** explicitne definovaný (a pri vyhodnotení skontrolovaný).
- [ ] **Benchmarky kontextové** — zvolené podľa funnelu, cieľa a trhu, nie jedno globálne číslo.
- [ ] **Diagnostika z čísel** — verdikt má oporu v metrikách, nie v pocite.
- [ ] **E-commerce architektúra obsahuje trvalú DPA / katalógovú kampaň** z feedu (aj pri malom budgete a novom účte); chýbajúci katalóg, feed alebo `content_ids` sú blokujúce položky checklistu, nie dôvod DPA vynechať. Pozri `references/kampanova-struktura.md`.
- [ ] **Retargeting iba s pomenovaným dôvodom** (predvolene ho robí Prospecting), max 5–10 % rozpočtu; DPA hodnotená na click atribúcii s kontrolou podielu Existing Customers; Audience Segments a vylúčenia overené. Pozri `references/kampanova-struktura.md`, sekcia Retargeting.
- [ ] **Naming** nadväzuje na konvenciu účtu (pozri `references/kampanova-struktura.md`).
- [ ] **Popis kreatív** je vecný a neutrálny — žiadne skratkové alebo neformálne označenia (napr. „banner s melónom"), použiť popis vizuálu alebo názov súboru.
- [ ] Pri MCP: over `is_queryable` a **verifikuj fieldy** cez `ads_get_field_context` pred ťahaním.

## Limity

- Skill dáva blueprint a analýzu — **nespúšťa ani nepauzuje kampane sám** bez explicitného potvrdenia používateľa (a aktivácia entít je akcia, ktorá míňa rozpočet).
- Benchmarky sú **orientačné**, nie absolútne pravdy; kalibruj podľa histórie účtu.
- Štatistická istota pri malých objemoch je obmedzená — pri nízkom spende je verdikt vždy predbežný.
- Meta mení best practices priebežne; terminológiu a limity over, ak je to citlivé na aktuálnosť.
