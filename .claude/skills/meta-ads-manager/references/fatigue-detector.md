# Detektor únavy kreatív (Režim D)

Každá kreatíva má životný cyklus. Otázka nie je *či* unaví — ale *kedy*, a či to zachytíš včas. Únava (fatigue) sa prejavuje skôr v CTR než v CPA: do momentu, kedy ti vyskočí CPA, si zvyčajne zbytočne minul rozpočet.

**Tri základné pravidlá únavy:**
1. **Frequency je leading indicator** — rastúca frequency predchádza únave; sleduj ju skôr než CPA.
2. **CTR klesá skôr, ako CPA rastie** — pokles CTR je tvoje včasné varovanie.
3. **Víťazi unavujú najrýchlejšie** — najlepšia kreatíva dostáva najviac impresií, a teda horí najrýchlejšie.

## Scoring model — Fatigue Score (0–100)

Vypočítaj pre každú kreatívu. Váhy:

```
Fatigue Score = (Skóre poklesu CTR × 0,40)
              + (Frequency Score × 0,30)
              + (Age Score       × 0,20)
              + (CPA Score       × 0,10)
```

Každé čiastkové skóre je 0–100 a počíta sa **deterministicky**. Pokles CTR a zmena CPA sú zadané kotvami: medzi nimi lineárne interpoluj, pod prvou platí 0, od poslednej 100. Frequency a vek sú pásma s polootvorenými intervalmi (dolná hranica patrí do pásma, horná už nie). Zaokrúhľuj až celkové skóre, na celé číslo.

**Skóre poklesu CTR** — outbound CTR (`outbound_clicks_ctr`), baseline = prvých 7 celých dní vs. posledných 7 celých dní:

| Pokles CTR | 0 % alebo rast | 10 % | 20 % | 35 % | ≥ 50 % |
|---|---|---|---|---|---|
| Skóre | 0 | 25 | 50 | 75 | 100 |

Príklad: pokles 27,5 % leží v polovici medzi 20 % a 35 % → skóre 62,5.

**Frequency Score** (orientačné prahy pre Meta prospecting; frequency za posledných 7 dní):

| Frequency | < 2,5 | 2,5 až < 3,0 (pri prahu) | 3,0 až < 4,5 | ≥ 4,5 (2× prah) |
|---|---|---|---|---|
| Skóre | 0 | 50 | 75 | 100 |

> Pre retargeting posuň všetky hranice o +1,5 (~4,0–5,0 je ešte OK). Úzke publikum (remarketing, small LAL) fatiguuje rýchlejšie.

**Age Score** (dni od spustenia):

| Vek | < 14 dní | 14–27 dní | 28–41 dní | 42–55 dní | ≥ 56 dní |
|---|---|---|---|---|---|
| Skóre | 0 | 25 | 50 | 75 | 100 |

**CPA Score** (zmena CPA posledných 7 dní voči baseline prvých 7 dní):

| Zmena CPA | ≤ 0 % | +15 % | +30 % | +50 % | ≥ +75 % |
|---|---|---|---|---|---|
| Skóre | 0 | 25 | 50 | 75 | 100 |

**Keď dáta nestačia:**
- Kreatíva beží < 14 dní → nemáš dve nezávislé 7-dňové okná; pokles CTR a CPA Score nepočítaj a stav označ **Nedostatok dát**.
- Neúplný týždeň (napr. dnešok) do okna nezapočítaj; používaj iba celé dni.
- Baseline CTR alebo baseline CPA je 0 alebo chýba (žiadne kliky / konverzie v prvom týždni) → dané čiastkové skóre je **N/A**, jeho váhu rozpočítaj pomerne medzi zvyšné zložky a v reporte to uveď.
- Menej ako 1 000 impresií v niektorom okne → CTR zložku ber ako N/A (šum).

**Interpretácia celkového skóre** — jediná tabuľka pásiem pre report aj `fatigue.md`:

| Skóre | Stav | Odporúčanie |
|-------|------|-------|
| 0–25 | Čerstvá | Monitoruj týždenne |
| 26–45 | Zdravá | Priprav zálohu / novú kreatívu |
| 46–65 | Raná únava | Rotuj do 2 týždňov |
| 66–80 | Stredná únava | Rotuj do 1 týždňa |
| 81–100 | Kritická únava | Navrhni pauzu / okamžitú rotáciu |

Skóre je orientačný signál, nie automatický pokyn. Pauzu alebo rotáciu v účte vykoná (alebo výslovne potvrdí) človek.

## Životný cyklus kreatívy

```
VÝKON
  │
  │     .-------.
  │    /         \
  │   /           \
  │  /             \
  │ /               \
  │/                 \___
  │
  └──────────────────────────── CAS
     Learning  Peak  Fatigue  Vycerpana
     (1-2 t.)  (2-6 t.) (2-4 t.)
```

**Orientačná životnosť na Meta:**

| Funnel | Životnosť |
|--------|-----------|
| Prospecting (broad) | 3–6 týždňov |
| Retargeting | 2–4 týždne |

Faktory, ktoré životnosť **skracujú:** úzke publikum, vysoký denný spend, jediná kreatíva v ad sete, virálny výkon (algoritmus tlačí = rýchlejšie horí).

Faktory, ktoré ju **predlžujú:** broad publikum, viacero kreatív v rotácii, video (viac engagementu než statik), dynamic creative.

## Diagnostika — typy únavy a príčiny

| Symptóm | Čo to znamená | Ako reagovať |
|---------|---------------|--------------|
| Rastie frequency, klesá CTR | Klasická únava — tí istí ľudia vidia to isté | Nová kreatíva alebo rozšír publikum |
| Klesá hook rate (video) | Ľudia prestávajú zastavovať na reklame | Nový hook — obsah poznajú |
| CTR stabilné, rastie CPA | Únava konverzného publika alebo zmena na webe / ponuke | Over landing page, sezónu, konkurenciu |
| Všetky metriky padajú naraz | Kombinácia únavy a externý faktor (sezóna, konkurent) | Skontroluj anomaly signal a kontext |

> **Katalógové / dynamické reklamy (DPA, Advantage+ catalog):** kreatívu skladá Meta z produktového feedu, nie z bannerov tejto pipeline. Pri ich únave nenavrhuj nový hook ani koncept — páka je feed (produkty, ceny, fotky), product set a publikum, prípadne samostatné statické kreatívy vedľa katalógu.

## MCP volania pre fatigue analýzu

Použi `meta-mcp-playbook.md` pre detaily volaní. Pre únavu sú kľúčové:

1. **`ads_get_ad_entities`** (`level = ad`, `time_increment = 7` alebo `monthly`) — týždenné trendy CTR, CPA, frequency, video metrík. Potrebuješ časový rad, nie len snapshot.
2. **`ads_insights_performance_trend`** (`analysis_level = AD`) — trend CPC/CTR/CPR v čase, priamo stavané na zachytenie poklesu.
3. **`ads_insights_anomaly_signal`** — automaticky detegované spiky a prepady; použi ako prvý filter pred manuálnym výpočtom skóre.
4. **`ads_insights_auction_ranking_benchmarks`** — klesajúci engagement/quality ranking v aukcii je ďalší signál únavy.

**Fieldy pre frequency a poklesu videa (ad úroveň):**
- `frequency`, `impressions`, `reach`
- `video_continuous_2_sec_watched_actions`, `video_p25_watched_actions`, `video_p100_watched_actions`, `video_thruplay_watched_actions`
- `outbound_clicks_ctr`, `outbound_clicks`, `cost_per_result`, `amount_spent`

Pre pokles CTR potrebuješ **časový rad** — použi `time_increment = 7` s dostatočným `time_range`.

## Rotačný plán

**Prioritizácia rotácie:**

| Priorita | Fatigue Score | Akcia |
|----------|---------------|-------|
| Okamžite | 81–100 | Návrh pauzy + náhrada (vykoná človek) |
| Tento týždeň | 66–80 | Priprav + spusti náhradu |
| Do 2 týždňov | 46–65 | Zadaj brief na novú kreatívu |
| Sledovať | 26–45 | Monitoruj týždenne |

**Rotačné pravidlá:**
- Vždy maj v ad sete aspoň 1 čerstvú alebo zdravú kreatívu (skóre ≤ 45) ako zálohu.
- Keď víťaz dosiahne skóre 46+, **spusti prípravu náhrady** — nie až keď sa zrúti.
- Pred pauzou kreatívy s vysokým engagementom over Post ID — pri prenose do novej kampane zachováš sociálny dôkaz (lajky, komentáre).
- 2026: namiesto 20 klonov jedného víťaza priprav **konceptuálne odlišnú** náhradu (iný angle alebo hook typ z knižnice v `tvorba-kreativ.md`).

## Výstupný report Režim D

```
═══════════════════════════════════════════════════════════════════
ANALYZA UNAVY KREATIV — [klient/ucet]
Obdobie: [od–do]   |   Zdroj: Meta Ads MCP / manual
═══════════════════════════════════════════════════════════════════

CELKOVE ZDRAVIE PORTFOLIA: [ZDRAVE / VAROVANIE / KRITICKE]

PREHLAD
| Stav            | Pocet kreativ |
|-----------------|---------------|
| Cerstve (0–25)  | X             |
| Zdrave (26–45)  | X             |
| Rana unava (46–65) | X          |
| Stredna (66–80) | X             |
| Kriticka (81–100)| X            |

TABULKA SKORE
| Kreativa | Format | Vek (dni) | Freq. | pokles CTR | CPA zmena | Skore | Stav | Akcia |
|----------|--------|-----------|-------|-----------|-----------|-------|------|-------|

ROTACNY PLAN
Okamzite:        [ ] vypnut [X], nahradit [tipom]
Tento tyzden:    [ ] pripravit nahradu pre [X]
Do 2 tyzdnov:    [ ] zadat brief na [X]

PIPELINE ODPORUCANIE
- Aktualna rychlost spotreby: ~X kreativ / mesiac
- Odporucany pipeline: X novych kreativ / mesiac v priprave
═══════════════════════════════════════════════════════════════════
```

## Prevencia únavy

- **Nepush jeden winner na maximum** — rotuj medzi 3–5 aktívnymi kreatívami, nech algoritmus nemíňa objem len na jednu.
- **Sleduj frequency weekly** pri retargetingu a úzkych publikách — únava prichádza rýchlo.
- **Iteruj skôr, ako kreatíva unaví** — keď je skóre okolo 40, začni vyrábať náhradu, nie až pri 80.
- **Dynamic creative / Advantage+ Creative** predlžuje životnosť tým, že Meta kombinuje assety — ale pri čistom teste ho vypni (pozri `testovanie-metodika.md`).
