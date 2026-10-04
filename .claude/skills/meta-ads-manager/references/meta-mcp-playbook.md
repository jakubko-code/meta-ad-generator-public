# Meta Ads MCP — playbook pre živé vyhodnotenie (Režim C)

Tento súbor hovorí, **ako presne ťahať dáta kreatív cez Meta Ads MCP** a ako z dostupných fieldov poskladať metriky z `metriky-diagnostika.md`. Drž sa sekvencie — preskočenie krokov (najmä verifikácie fieldov) spôsobí zlyhané volania.

## Sekvencia volaní

### Krok 0 — Účet a queryability
1. `ads_get_ad_accounts` → nájdi cieľový `ad_account_id` a skontroluj `is_queryable`.
   - Ak `is_queryable = false` → **netiahaj dáta**, oznám používateľovi `not_queryable_reason`.

### Krok 1 — Verifikácia fieldov (povinné)
2. `ads_get_field_context` na každý field, ktorý plánuješ použiť vo `fields`, `filtering`, `sort`.
   - Je zdroj pravdy pre `levels` (na ktorej úrovni field existuje), `filterable`, `sortable`, `supported_filter_operators`, `enum_values`.
   - **Fieldy sú level-scoped** — field platný na `campaign` nemusí existovať na `ad`. Toto je dôvod, prečo 3-sec plays riešime nižšie inak.

### Krok 2 — Dáta kreatív na úrovni ad
3. `ads_get_ad_entities` s `level = ad`, časovým oknom (`date_preset` alebo `time_range`), `fields` (viď mapovanie nižšie) a `filtering` na zúženie na testované kreatívy.
   - **Časové okno je povinné** pre metriky/filtrovanie/sortovanie. Bez neho dostaneš len atribúty.
   - Filtrovanie na test primárne podľa **Meta Ad ID z trackera**: `{"field":"ad.id","operator":"IN","value":["120214…"]}`. Naming stopa (`{"field":"ad.name","operator":"CONTAIN","value":["HOOK-A"]}`) je iba záloha, keď ID ešte nie je v trackeri — po duplikovaní či premenovaní názov nie je jednoznačný.
   - Filter na bežiace: `{"field":"effective_status","operator":"IN","value":["ACTIVE"]}`.
   - **Limit na počet vrátených entít:** ak chceš najlepšie aj najhoršie, zavolaj 2× s opačným `sort` (napr. `cost_per_result_ascending` a `_descending`).
   - **Len jeden `breakdown` na volanie** (ostatné sa ignorujú). Ak breakdown vráti prázdno, zopakuj bez neho.

### Krok 3 — Doplnkové signály
4. `ads_insights_performance_trend` (`analysis_level = AD`) — časový vývoj CPC/CPM/CPR/ROAS/CTR/CVR, na zachytenie trendu a únavy.
5. `ads_insights_anomaly_signal` (s `entity_ids` testovaných adov) — spiky/prepady, fatigue. **Anomália = podnet na skúmanie, nie záver.**
6. `ads_insights_auction_ranking_benchmarks` — kvalita/engagement/konverzný ranking v aukcii a auction overlap (vysoký overlap → fragmentácia, konsoliduj).
7. `ads_insights_industry_benchmark` — externé porovnanie voči peer group (`cas_segment`, `optimization_goal_override`); používaj na business-outcome metriky (CPR), nie na CPM.
8. `ads_get_opportunity_score` (account-level, 0–100) — odporúčania Meta. **Vždy účtové**, nikdy ho nepripíš konkrétnej kreatíve.
9. `ads_get_errors` (`entity_ids`) — ak variant nemíňa / nedoručuje, over delivery-blocking chyby pred tým, než to označíš za „slabú kreatívu".
10. `ads_get_ad_preview` / `ads_get_creatives` — pozri reálnu kreatívu očami, keď čísla nedávajú zmysel.

## Mapovanie metrika → field (`ads_get_ad_entities`, level = ad)

Fieldy spoločné pre všetky úrovne sú dostupné aj na `ad`. Kľúčové pre kreatívy:

**Základ:** `impressions`, `reach`, `frequency`, `clicks`, `ctr` (all-clicks!), `cpc`, `cpm`, `cpp`, `amount_spent`.

**Kliky von z Mety:** `outbound_clicks`, `outbound_clicks_ctr` (percento, dostupné aj na ad úrovni), `cost_per_outbound_click`.

**Video (na skladanie hook/hold):**
- `video_continuous_2_sec_watched_actions` — 2-sek. kontinuálne prehratia
- `video_p25_watched_actions`, `video_p50_…`, `video_p75_…`, `video_p95_…`, `video_p100_watched_actions`
- `video_thruplay_watched_actions`, `cost_per_thruplay`, `cost_per_2_sec_continuous_video_view`

**Akcie (cez `actions:` a cost_per):**
- `actions:link_click` (link click — ciele **v Mete aj mimo nej**, napr. aj Instant Experience či formulár; nie je to outbound), `cost_per_link_click`, `cost_per_link_click_result`
- `actions:omni_purchase`, `purchase_roas`, `results`, `result_values`, `cost_per_result`, `cost_per_conversion`, `cost_per_action_type`
- `actions:post_save`, `actions:post_reaction`, `actions:comment`, `actions:like`, `actions:page_engagement` (kvalita engagementu)
- `lead` (pre lead gen)

> **Nežiadaj `actions` ani `action_values` ako samostatný field** — vyber konkrétny podtyp (napr. `actions:omni_purchase`).

### Ako poskladať cieľové metriky

| Metrika | Výpočet na ad-leveli | Poznámka |
|---------|----------------------|----------|
| **Hook / hold rate** | — | Iba pri videu. Pri statických banneroch sú N/A. |
| **Hook rate** (proxy) | `video_continuous_2_sec_watched_actions` ÷ `impressions` | Klasický thumb-stop = 3-sec plays ÷ impresie, ale **`3_second_video_plays` na ad-leveli nie je fetchable** (len adset/campaign/account). Na ad použi 2-sec kontinuálne ako proxy, alebo `video_p25` ÷ impressions. |
| **Hook rate** (presný) | `3_second_video_plays` ÷ `impressions` | Pull na úrovni **adset/campaign** (tam field existuje), ak potrebuješ klasickú definíciu. |
| **Hold rate** (proxy) | `video_thruplay_watched_actions` ÷ `video_continuous_2_sec_watched_actions` | Alebo `video_p100_watched_actions` ÷ `video_p25_watched_actions` ako alternatíva retencie. |
| **Outbound CTR** (primárna) | `outbound_clicks_ctr`, alebo `100 × outbound_clicks ÷ impressions` | Kliky, ktoré vedú mimo Metu (web). **Nepoužívaj `ctr`** (je all-clicks). Pri 0 impresiách N/A. |
| **Link CTR** (doplnková) | `100 × actions:link_click ÷ impressions` | Zahŕňa aj ciele v Mete; uvádzaj osobitne, nezamieňaj s outbound. |
| **CPA / CPL** | `cost_per_result` / `cost_per_action_type` (omni_purchase/lead) | Alebo `amount_spent` ÷ `actions:omni_purchase`. |
| **ROAS** | `purchase_roas` | Priamo field. |
| **Fatigue indikátor** | `frequency` (trend cez `time_increment`) | Rastúca frequency + klesajúci výkon = únava. |

## Gotchas (časté chyby)

- Bez časového okna → žiadne metriky (len atribúty).
- Neoverené fieldy → zlyhanie. Vždy najprv `ads_get_field_context`.
- Neopakuj identické volanie s rovnakými parametrami.
- `3_second_video_plays` na ad-leveli neexistuje — viď tabuľka vyššie.
- Opportunity Score je účtový, nie per-kreatíva.
- Ak je breakdown prázdny, skús bez neho.
- **`ads_update_entity` môže aktívnu entitu vypnúť.** Pri zmene `daily_budget` ad setu vrátil nástroj `status_forced_to_paused: true` a ad set ostal PAUSED (klient, 2026-09-15). Zmena názvu kampane stav nemenila. Pred úpravou rozpočtu alebo publika aktívnej entity preto človeku povedz, že entita sa môže vypnúť, a vopred si vyžiadaj súhlas s jej opätovným zapnutím cez `ads_activate_entity`. Po každej zmene over `status_forced_to_paused` v odpovedi a stav spätne načítaj.
- **Zmena cez `ads_update_entity` môže skončiť iba ako koncept (draft).** Od 2026-09-30 (klient) nástroj pri pauze reklamy vrátil `is_draft: true` a živý `effective_status` ostal ACTIVE; zmena čakala v konceptoch Ads Managera. Postup:
  1. Po každej úprave skontroluj `is_draft` v odpovedi a živý stav spätne načítaj (`ads_get_ad_entities`, predvolene `object_state: live`).
  2. Koncepty zobraz cez `ads_get_ad_entities` s `object_state: draft` a `object_ids` upravených entít; over, že obsahujú iba odsúhlasenú zmenu (`values`).
  3. Zverejni presne tie koncepty: `ads_activate_entity` s `object_ids` (nič iné sa nezverejní). Odpoveď `PUBLISHING` znamená iba odovzdanie, nie hotovú zmenu; výsledok over spätným načítaním živého stavu.
  - Zverejnenie konceptu s pauzou iba uplatní odsúhlasenú pauzu. Ak koncept obsahuje zmenu rozpočtu či publika aktívnej entity (vynútené PAUSED) alebo zapnutie, zverejnenie entitu zapína a míňa rozpočet — vopred si vyžiadaj výslovný súhlas.
  - Nezverejnený koncept ostáva v Ads Manageri a človek ho uvidí pri ďalšej úprave; nenechávaj po sebe rozpracované koncepty bez upozornenia.
- **Obrázok podľa umiestnenia nie je v `ads_get_creatives` vidieť.** Kreatíva vracia iba jeden `image_hash` (a `ads_get_ad_preview` ukáže ten istý obrázok aj pre Feed), hoci reklama má aj ďalší formát. Druhý formát nájdeš v `ads_get_ad_images` pod rovnakým názvom súboru; rozmery over cez `hashes` (klient 2026-10-02: `3.png_105` 1080×1350 a 1080×1920). Nehlás „chýba 4:5/9:16“, kým to neoveríš.
- **Stratégia životného cyklu zákazníka (Ads Manager, 2026) sa cez MCP nedá prečítať.** Nastavenie „Získanie nových zákazníkov“ automaticky vylučuje existujúcich zákazníkov (skupina štítkov Zákazníci + napr. `WCA - Purchase (180d)`), aj keď `targeting` ukazuje to isté publikum ako zahrnutý návrh Advantage+. Pred záverom „kupujúci sú zacielení/vylúčení“ si nechaj od človeka overiť túto sekciu v Ads Manageri. Úprava `targeting` cez API ju nemusí zachovať — po zmene publika ju over v UI.
- Pred každou zmenou ulož pôvodné nastavenie entity a zmenu zapíš do `brands/<brand>/testing/meta-changelog.md`.

## Bezpečnostná hranica

Tento skill **vyhodnocuje a odporúča** — **nepauzuje ani neaktivuje** kreatívy sám. `ads_activate_entity` (a akákoľvek zmena statusu) **míňa rozpočet** a robí entitu live; vykonaj ju len po **explicitnom potvrdení používateľa**, nikdy nie automaticky ako súčasť vyhodnotenia. Verdikt „vypnúť/škálovať" daj ako odporúčanie; realizáciu nechaj na používateľa, prípadne si vyžiadaj jasné potvrdenie.
