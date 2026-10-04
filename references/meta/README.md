# Meta Ads – index tém

Prehľad destilátov (`*-tactics.md`). Toto je rozcestník: aký súbor = aká téma.
Zdroje sú v `sources/` a nie sú tu uvedené (rastú voľne, čítajú sa len pri návrate k originálu).

## Tactics (destiláty – agent číta aktívne)

| Súbor | Téma | Pokrýva |
|-------|------|---------|
| [meta-kreativa-tactics.md](meta-kreativa-tactics.md) | Kreatíva: formáty, archetypy, hooky | Archetypy statiku (problém-riešenie, before/after, recenzia, porovnanie, founder POV, offer stack, advertoriál…) s testovanou premennou, pomery strán, archetypy carouselu (benefity, námietky, recenzie), Stories a videa; formát podľa fázy funnelu a teploty publika; odporúčania podľa odvetvia (lokálne služby, B2B, fintech, wellness); Ad Library; portfólio 70/20/10; rozdiely oproti skillu (broad vs. lookalike, 4:5, rotácia podľa fatigue) |
| [meta-testovanie-tactics.md](meta-testovanie-tactics.md) | Creative testing: odlišnosť, fázy, audit | Kozmetické variácie nie sú test; makro-test konceptov → mikro-test komponentov víťaza; koncepty z hlasu zákazníka; pomenovaný insight víťaza; týždenný kreatívny audit; výkon začína pri reklamách (viacnásobná reklama); rozdiely oproti skillu (jedna premenná vs. viac naraz, týždeň vs. 14-dňový šprint, Sandbox + Post ID vs. in-place – prenesené do skillu; bez testovacieho rozpočtu a bez vypínania reklám podľa CTC) |
| [meta-struktura-tactics.md](meta-struktura-tactics.md) | Štruktúra účtu, remarketing, prístupy | Klient vlastní assety, agentúra partner; štart 1 kampaň / 1 ad set; detailné cielenie a LAL ako návrhy; remarketing iba výnimočne; bez obmedzení veku/pohlavia/umiestnení, radšej value rules; počet reklám v ad sete; kedy má samostatný remarketing zmysel (drahý produkt, frequency > 2, rozpočet 5–10 %); DPA ako „pokladník“ (prah 30 % na existujúcich, click atribúcia, vylúčenia 90 d+); test vypnutia; Evergreen + Marketing Moment, min. ROAS na ad sete, poradie expanzie pri nedočerpaní (bid cap, druhá šanca pre málo minuté reklamy); rozpory prenesené do skillu 2026-09-30 |
| [meta-meranie-tactics.md](meta-meranie-tactics.md) | Meranie: atribúcia, segmenty, deduplikácia | Audience Segments (iba reporting, definovať široko); rozpad podľa atribúcie (1-day click vs. view/engage-through); conversion count a deduplikácia pixel + CAPI; audit synchronizovaných zoznamov a vylúčení; inkrementalita (Meta incremental attribution, holdout, orientačné iROAS faktory akvizícia vs. retencia); optimalizácia na 7-day click; kvalita signálu (CAPI, EMQ) |

## Plánované / možné témy
_(zatiaľ neexistujú – súbor pridaj, až keď naň bude obsah)_

| Súbor | Téma | Súvisiaca metodika skillu |
|-------|------|---------------------------|
| `meta-andromeda-tactics.md` | Andromeda, doručovanie, diverzita kreatív | `creative-sequencing.md` |
| `meta-katalog-tactics.md` | DPA, katalóg, feed, product sety | `katalogova-textacia.md` |
| `meta-fatigue-tactics.md` | Únava kreatív, frequency, rotácia | `fatigue-detector.md` |
| `meta-policy-tactics.md` | Zamietnutia, obmedzené kategórie, health & wellness | `health-wellness-restrikcie.md` |
| `meta-benchmarky-tactics.md` | CPM, CTR, CPA podľa trhu a segmentu | `metriky-diagnostika.md`, `segmenty.md` |

Metodika skillu je v `.claude/skills/meta-ads-manager/references/`. Destilát ju dopĺňa, nemení
(poradie platnosti je v [../README.md](../README.md)).

## Kategórie zdrojov

Delivery / Structure / Creative / Testing / Measurement / Catalog / Fatigue / Policy / Benchmarks

## Ako pridať

1. Nový zdroj → `sources/YYYY-MM-DD-zdroj-tema.md` podľa `sources/_TEMPLATE.md`.
2. Poznatky **zluč** do existujúceho `*-tactics.md` (neduplikuj, radšej prepíš alebo spoj body).
3. Ak téma do žiadneho súboru nesadne → vytvor nový `meta-<tema>-tactics.md` podľa
   `_TACTICS_TEMPLATE.md` a **dopíš riadok do tabuľky vyššie** (z plánovaných ho presuň).
4. Destilát drž štíhly (~do 150 riadkov); keď narastie, rozdeľ tému.
