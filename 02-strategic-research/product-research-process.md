# Product Research — Proces

Kompletný postup na vytvorenie marketing research dokumentov. Spúšťa sa keď `product-research-check.md` zistí, že research chýba **pre celú kategóriu**.

> ⚠️ **Nespúšťaj tento proces pre nové SKU v už pokrytej kategórii.** Research je na zákaznícky problém, nie na položku v katalógu — súrodenci dostanú len `product-facts.md` s odkazom `research-source:`. Rozhodovací postup je v `product-research-check.md`.

## Výstup (7 dokumentov)

Ukladaj do `brands/{brand}/products/{product}/marketing-research/`:

1. `deep-research.md` — research trhu (min 6 strán)
2. `avatar-sheet.md` — profil ideálneho zákazníka
3. `offer-brief.md` — ponuka a positioning
4. `necessary-beliefs.md` — beliefs pred nákupom
5. `cep-sheet.md` — situácie, kedy si zákazník na produkt spomenie
6. `briefs.md` — 10–15 strategických kontraktov pre tvorbu reklám
7. `product-facts.md` — overené SKU fakty, ceny a zakázané claims

Šablóny: `avatar-sheet-template.md`, `offer-brief-template.md`, `cep-sheet-template.md`,
`briefs-template.md`, `product-facts-template.md` (v tomto priečinku)

**Filozofický základ:** Agora prístup — marketing nie je o „magnificence of words" ale o „magnificence of the argument". Najprv postav argument, potom ho obleč do slov; `necessary-beliefs.md` sú North Star, ku ktorým každý kus obsahu vedie. Detail: [marketing-research/references/argument-first-philosophy.md](marketing-research/references/argument-first-philosophy.md).

---

## Step 1: Analýza produktu

Požiadaj usera o URL produktovej stránky alebo popis produktu. Analyzuj:
- Čo sa predáva a komu
- Aký problém to rieši
- Unique mechanism / proprietary solution
- Aktuálny messaging a positioning

Výsledné overené SKU dáta zapíš do `product-facts.md`. Minimálne: zdrojová URL a dátum
overenia, názov produktu, aktuálna cena a mena, rozmery/varianty, materiál alebo zloženie,
dostupnosť, povolené claims s ich zdrojom a sekcia „neclaimovať“. Neoverené údaje označ
`NEOVERENÉ`; nikdy ich nedopĺňaj odhadom.

---

## Step 2: Deep Research Prompt (pre ChatGPT Deep Research)

Vygeneruj prompt pre ChatGPT Deep Research prispôsobený konkrétnemu produktu.

### Poradie zdrojov (povinné)

Prompt musí ChatGPT nariadiť, aby postupoval presne v tomto poradí:

**ZDROJ 1 — FÓRA (primárny)**
- Vyhľadaj „[téma] forum", „[problém] reddit", „[kategória] forum"
- Otvor vlákna s **najviac odpoveďami** (sort by replies = najangažovanejšie témy)
- Choď hlboko do **jedného** dobrého vlákna — nechoď plytko po mnohých
- Jedno dobré vlákno = väčšina celého researchu
- Copy-paste presné citáty zákazníkov verbatim v ich pôvodnom jazyku

**ZDROJ 2 — RECENZIE (primárny)**
- Amazon, Heureka a podobné — produkty z kategórie s čo najväčším počtom recenzií
- Čítaj 5★ (čo milujú, aké výsledky dostali) **aj** 1★ (horror stories, čo nenávidia)
- Copy-paste presné vety zákazníkov, nie parafrázu

**ZDROJ 3 — GOOGLE (len pre Curiosity + Corruption)**
- „[problém] horror story", „história [riešenia]", „miesta kde [problém] neexistuje"
- Tento zdroj je **tretí** — nie na zákazníkov, len na historický kontext a corruption angles

### Čo prompt NESMIE nariadiť

- Akademické štúdie a vedecké prehľady ako primárny zdroj
- Demografické správy a market research reports
- Rozkladanie researchu naprieč 10 fórami plytko
- Parafrázu — vždy verbatim citáty

### Čo musí prompt požadovať ako výstup

- Jeden kompilovaný dokument, minimum 6 strán
- Každá sekcia plná verbatim citátov v pôvodnom jazyku zákazníka
- Konkrétne, nie generické — nie „chcú schudnúť", ale „chcem, aby sa na mňa manžel pozrel s hrdosťou"

### 4 sekcie, ktoré prompt musí pokryť

**Sekcia 1: Demografické insights**
- Kto je zákazník (vek, pohlavie, príjem, lokalita)
- Aké postoje má (náboženské, politické, sociálne, ekonomické)
- Nádeje a sny — konkrétne, nie generické
- Víťazstvá a zlyhania s ich problémom
- Vonkajšie sily ktoré im bránia žiť najlepší život (naratívy, ktoré si hovoria)
- Predsudky a stereotypy (signalizujú „som jeden z vás")
- Core beliefs o živote, láske a rodine — 1–3 vety, kto je táto osoba

**Sekcia 2: Existujúce riešenia**
- Čo trh už používa
- Aká bola ich skúsenosť (používajú veľa/málo, prestali, prečo)
- Čo sa im páči / nepáči
- Horror stories o existujúcich riešeniach
- Verí trh, že existujúce riešenia fungujú? Ak áno → treba viac diferenciácie. Ak nie → prečo?

**Sekcia 3: Curiosity**
- Stratené objavy — riešenia, ktoré boli zabudnuté
- Potlačené riešenia — niekto mal odpoveď, ale bola skrytá
- Staré unikátne pokusy (pre-1960), inherentne odlišné od dnešných riešení
- Čo sa s nimi stalo? Boli úspešné ale zabudnuté? Zlyhali a prečo?

**Sekcia 4: Corruption**
- Existoval pain point vždy alebo sa zhoršil?
- „Fall from Eden" — vonkajšia sila ktorá situáciu zhoršila
- Izolované skupiny ľudí, ktoré tento problém **nemajú** — prečo?

Prezentuj prompt userovi — user ho skopíruje do ChatGPT Deep Research.

> **Plná metodika:** [deep-research-methodology.md](deep-research-methodology.md) (Mark Builds Brands, Research Part 1 & 2) — rozpísané všetky 4 sekcie s príkladmi, konkrétne Google queries a princípy hľadania na fórach. Prečítaj ju, keď potrebuješ hlbší kontext než zhrnutie vyššie.

---

## Step 3: Interný research agenta (doplnkový zdroj)

Paralelne s čakaním na ChatGPT výstup urob vlastný research. **Platí rovnaká metodológia ako pre ChatGPT** — primárne fóra a recenzie, nie akademické zdroje:

- **Fóra** — nájdi 1–2 vlákna s najviac odpoveďami, choď do hĺbky, copy-paste verbatim citáty
- **Recenzie (Heureka, Amazon)** — 5★ aj 1★, presné vety zákazníkov
- **Konkurenčný landscape** — hlavní hráči, ich positioning a unique mechanisms (stačí povrchovo)
- **Corruption / curiosity angles** — historický kontext, potlačené riešenia (Google ako zdroj)

Sekundárne — nie customer voice, ale užitočné pre UMS a claims:
- Vedecké štúdie — pri health produktoch mechanizmus účinku a opora pre claims
- Regulačné obmedzenia — len ak je produkt v regulovanej kategórii

Čo **nie** je prioritou: demografické správy, market research reports a akademické prehľady ako náhrada za customer voice.

**Akými nástrojmi** *(použi tie, ktoré má aktuálne prostredie k dispozícii; projekt funguje v Claude Code aj Codexe)*:
1. **Exa** — hlavný nástroj na review mining. Query píš ako opis ideálnej stránky, nie kľúčové slová (napr. „diskusia kde ľudia opisujú obavy pred kúpou X"). Vracia plný text, takže z jedného volania máš viac citácií než z viacerých keyword hľadaní.
2. **WebFetch** — konkrétna produktová stránka, recenzie e-shopu, Heureka profil.
3. **DataForSEO** — lokalizovaný SERP (Slovensko, jazyk `sk`) a objemy vyhľadávania, keď potrebuješ vedieť, ako trh problém reálne pomenúva.
4. **Meta Ads MCP** (`ads_library_search`) — čo v danej kategórii reálne bežia konkurenti.

Vstavaný WebSearch je keyword-based a US-orientovaný — pri SK/CZ obsahu ho ber ako doplnok, nie ako primárny zdroj.

---

## ⛔ GATE pred Step 4+

NEPOKRAČOVAŤ na Step 4 (kompilácia) ani Step 5–7 kým nie sú splnené VŠETKY podmienky:

1. ✅ ChatGPT Deep Research output dodaný userom
2. ✅ Všetky potrebné interné research workstreamy sú dokončené (review mining, konkurenčný landscape, veda a regulácie). Delegovanie na subagentov je voliteľná implementácia, nie podmienka.
3. ✅ Chýbajúce tvrdé dáta (ceny, dávkovanie, claims) doplnené alebo explicitne označené ako gap

Ak niečo chýba → confirm-back userovi čo presne ešte chýba a čakaj. Nepokračovať „aspoň s tým čo máme" — half-finished research = half-finished hooks.

**Výnimka iba na výslovné rozhodnutie človeka:** ak user povie, že ChatGPT Deep Research nespustí (čas, rozpočet, malý klient), podmienku 1 nahradí rozšírený interný research podľa rovnakej metodiky (Step 3, rovnaké poradie zdrojov). Do hlavičky `deep-research.md` zapíš `> deep-research-waiver: <meno>, <dátum>, <dôvod>` a v briefoch označ závery ako hypotézy na overenie testom. Agent túto výnimku sám neudeľuje.

---

## Step 4: Kompilácia do deep-research.md

Keď user dodá ChatGPT výstup A všetky potrebné workstreamy sú hotové:
- Skombinuj oba zdroje (ChatGPT Deep Research + interný research aktuálneho agenta)
- Odstráň duplicity, zachovaj najlepšie citáty a insights z oboch zdrojov
- Štruktúruj podľa 4 sekcií + doplnkové zistenia
- Minimum 6 strán, copy-paste presné slová zákazníkov

> **Princíp:** Copy-paste presné slová zákazníkov. Nehádaj, čo chcú počuť — oni ti to povedia. Jedno dobré vlákno na fóre = väčšina researchu.

Ulož: `brands/{brand}/products/{product}/marketing-research/deep-research.md`

---

## Step 5: Avatar Sheet

Vyplň `avatar-sheet-template.md` na základe deep-research.md.

Ulož: `brands/{brand}/products/{product}/marketing-research/avatar-sheet.md`

---

## Step 6: Offer Brief

Vyplň `offer-brief-template.md` na základe deep-research.md + avatar-sheet.md.

Ulož: `brands/{brand}/products/{product}/marketing-research/offer-brief.md`

---

## Step 7: Necessary Beliefs

Na základe všetkých predošlých dokumentov identifikuj max 6 beliefs ktoré musí prospect mať PRED tým ako uvidí ponuku. Štruktúruj ako "I believe that..." statements.

Tieto beliefs sú North Star pre všetok copy — každá reklama musí viesť prospecta k nim.

Ulož: `brands/{brand}/products/{product}/marketing-research/necessary-beliefs.md`

---

## Step 8: CEP Sheet

Beliefs (Step 7) pokrývajú os **prečo nekúpi**. CEP sheet pridá os **kedy si na produkt spomenie** — 10–15 konkrétnych situácií, z ktorých každá je kandidát na samostatný brief s vlastným headlinom.

Postup, testy kvality a šablóna tabuľky: `cep-sheet-template.md` v tomto priečinku.

Zdroj situácií je v poradí: (1) recenzie a fóra už zozbierané v `deep-research.md` — vety „kúpila som to keď…", (2) doplnenie cez Exu, (3) sezónny kalendár, (4) až nakoniec dedukcia z produktu (označ `⚠️ nedoložené`).

Ulož: `brands/{brand}/products/{product}/marketing-research/cep-sheet.md`

---

## Step 9: Brief library

Z `necessary-beliefs.md`, `cep-sheet.md`, verbatim citátov a ponuky vytvor 10–15 briefov.
Každý brief je samostatný strategický kontrakt a musí obsahovať:

- stabilné ID (`B01`, `B02`, ...), názov a cieľ/fázu povedomia,
- personu alebo segment,
- angle s odkazom na Belief # a/alebo CEP #,
- jednu cieľovú emóciu,
- presný `customer_voice_anchor` dohľadateľný v `deep-research.md`,
- overené podporné fakty/claims a najlepšie formáty.

Ulož: `brands/{brand}/products/{product}/marketing-research/briefs.md`

## Step 10: Návrat do workflow

Po uložení všetkých 7 dokumentov sa vráť do `product-research-check.md` a spusti kontrolu znova. Potom pokračuj krokom 3 (E + A: architektúra a koncepty), krokom 4 (B1 testovací plán) a až následne krokom 5 (Template + Copy).

Pri stavbe `briefs.md` čerpaj z **oboch osí**: `necessary-beliefs.md` (objekcie) aj `cep-sheet.md` (situácie). Brief môže stáť na belief, na CEP, alebo na oboch naraz — mapovanie je v `cep-sheet-template.md`, sekcia „Ako sa CEP dostane do briefov".
