# Metriky a diagnostika (Režim C)

Vyhodnotenie je objektívne a založené na číslach. Postup: (1) over kontrolu objemu dát, (2) prečítaj metriky proti **kontextovým** benchmarkom, (3) lokalizuj úzke hrdlo diagnostickým stromom, (4) vyver verdikt kill/iterovať/škálovať.

## Kľúčové metriky — čo merajú a ako sa počítajú

| Metrika | Vzorec | Čo hovorí |
|---------|--------|-----------|
| **Thumb-Stop Ratio / Hook Rate** | 3-sec video plays ÷ impresie | Sila **hooku** — zastavil scroll? |
| **Hold Rate (Retention)** | ThruPlays ÷ 3-sec video plays | Pútavosť **tela** — udržali si ich? |
| **Outbound CTR** | outbound clicks ÷ impresie (`outbound_clicks_ctr`) | Ťah ponuky / **CTA** — klikajú von na web? |
| **Link CTR** | link clicks ÷ impresie | Doplnkovo — zahŕňa aj ciele v Mete (Instant Experience, formulár) |
| **CPC (link)** | spend ÷ link clicks | Cena za preklik na web |
| **CPA / CPL** | spend ÷ konverzie (purchase/lead) | Cena finálnej akcie — **hard** metrika |
| **ROAS** | hodnota konverzií ÷ spend | Návratnosť — **hard** metrika |
| **Frequency** | impresie ÷ reach | Únava publika **a škálovací signál** — vedúci indikátor, mení sa skôr ako ROAS |

> **Pozn. k „CTR" v Mete:** štandardné `ctr` je *all-clicks* (vrátane reakcií, rozkliknutí). Pre rozhodovanie používaj **outbound CTR** (`outbound_clicks_ctr`). `link_click` zahŕňa aj ciele v Mete, preto link CTR uvádzaj osobitne a nevydávaj ho za outbound. Pri 0 impresiách je CTR N/A; hook a hold rate sú pri statikoch N/A. Mapovanie na MCP fieldy je v `meta-mcp-playbook.md`.

> **Frequency ako vedúci indikátor:** weekly frequency < 2 = priestor na škálovanie; > 4 = nepridávaj budget, pridaj TOF koncepty. Korelácia vysoká frequency + vysoký ROAS = BOF saturácia, nie skutočný škálovateľný výkon. Detaily v `creative-sequencing.md`.

## Kontextové benchmarky — NIE jedno globálne číslo

Benchmark závisí od **funnel fázy, cieľa a trhu**. Nasledujúce sú **orientačné** baseline hodnoty (TOF, broad, e-commerce, „lacnejšie" CEE trhy); kalibruj podľa histórie účtu.

**Baseline (TOF / e-commerce):**

| Metrika | Slabé | OK | Dobré |
|---------|-------|----|----|
| Hook rate | < 20 % | 20–30 % | > 30 % |
| Hold rate | < 15 % | 15–25 % | > 25 % |
| Outbound CTR | < 0,7 % | 0,7–1,2 % | > 1,2 % |
| CPA / ROAS | — | — | podľa marže / break-even |

**Modifikátory kontextu:**
- **BOF (retargeting):** CTR aj konverzný pomer bývajú **vyššie** (teplé publikum), hook rate menej kritický. Nečakaj TOF čísla a naopak.
- **Cieľ Awareness/Engagement:** sústreď sa na hook/hold a CPM, nie na CPA.
- **Lead gen / B2B:** nižšie CTR je normál; rozhodujúci je CPL a *kvalita* leadu (optimalizuj na hlbší event, ak objem dovolí).
- **Trh:** PL/HU/CZ/SK majú odlišné CPM aj CTR. Porovnávaj kreatívu voči *iným kreatívam v tom istom účte/trhu*, nie voči cudziemu benchmarku. Na externé porovnanie použi `ads_insights_industry_benchmark` (peer group podľa spend tier a cieľa).

Vždy uprednostni **interný benchmark účtu** (ako sa darí ostatným kreatívam tu) pred univerzálnym číslom.

> **Pozor:** baseline tabuľka vyššie je ladená na **e-com / DR**. Pre lead-gen služby, brand awareness, cultural/event, infoprodukt či B2B high-ticket si najprv načítaj `segmenty.md` — preformuje, čo je vôbec „hard" metrika a ktorým smerom sa benchmarky posúvajú.

## Diagnostický rozhodovací strom — kde je úzke hrdlo

Čítaj metriky v poradí funnelu (hook → telo → CTA → web). Prvé miesto, kde to „spadne", je úzke hrdlo:

| Symptóm | Diagnóza | Riešenie |
|---------|----------|----------|
| **Nízky hook rate** | Hook nezastavuje scroll | Nový hook (iný typ z knižnice), silnejší vizuálny zlom v 1. s, callout cieľovky |
| **Dobrý hook rate, nízky hold rate** | Skvelý háčik, ale telo nudí / nedodalo sľub | Skráť video, pridaj dynamiku strihu po 3. s, splň sľub hooku skôr |
| **Dobrý hold rate, nízke CTR** | Pozerajú, ale neklikajú | Slabé/nejasné CTA, nejasný prínos — priostri výzvu a benefit |
| **Vysoké CTR, nulové/drahé konverzie (vysoká CPA)** | Reklama ťahá, problém je za klikom | Landing page (rýchlosť, súlad s reklamou, dôvera), cena/ponuka, alebo clickbait — reklama sľubuje iné, než web dodá |
| **Dobré všetko, ale rastie frequency a klesá výkon** | Únava kreatívy (fatigue) | Iterácia / nový koncept; pozri `ads_insights_anomaly_signal` |

Diagnostika vždy **menuje konkrétne číslo**, z ktorého verdikt vyplýva — nie „pôsobí to slabo".

## Verdikt — kill / iterovať / škálovať

Až po kontrole objemu dát a diagnostike. **Dôležité: verdikt rob vždy na úrovni adsetu/kampane, nie single reklamy** — Andromeda optimalizuje sekvenciu, ROAS jednotlivej reklamy je zavádzajúci (konverzia ide na last-click, ale predchádzajúce reklamy vo funneli ju umožnili).

**VYPNÚŤ (kill)**
- Frequency vysoká (> 2 týždenná) **A** ROAS pod cieľom → vyčerpané publikum, reklama neprispieva.
- Prešla kontrolou objemu dát a metriky jasne pod baseline, minula 2–3× tolerovanú CPA bez výsledku.
- **Nikdy nevypínaj** reklamu len preto, že má najnižší ROAS v adsete — ak má nízku frequency, pravdepodobne je to TOF/unaware reklama ktorá kŕmi funnel. Bez nej frequency BOF reklám vyletí a celkový ROAS adsetu klesne.

**ITEROVAŤ (stredná cesta)**
- Kreatíva má dobré **soft** metriky (hook/hold/CTR), ale nepredáva → problém je lokalizovaný (telo, CTA, ponuka, web). Vyrob cielenú variáciu, ktorá rieši *konkrétne* to úzke hrdlo z diagnostiky.
- 2026: iteruj smerom k **odlišnosti**, nie k 20 kozmetickým klonom víťaza.

**ŠKÁLOVAŤ (winner)**
- Variant stabilne plní KPI (CPA/ROAS) nad kontrolou objemu dát **a** týždenná frequency je pod 2.
- Frequency > 4 + dobrý ROAS = **nepridávaj budget** — je to BOF saturácia, nie skutočný škálovateľný výkon. Pridaj unaware/TOF koncepty, kým frequency neklesne.
- Test v Sandboxe: prenes víťaza cez **Post ID** (zachováš sociálny dôkaz) do hlavnej kampane. Test in-place v Prospectingu: víťaz ostáva, kde je; nevynucuj mu rozpočet vypínaním ostatných reklám (`kampanova-struktura.md`, „Kde testovať nové kreatívy“). Pozri `creative-sequencing.md` pre pravidlá škálovania.
- Pri retargetingu a DPA pred verdiktom Škálovať over **7-day click bez view** a podiel segmentu Existing Customers; vysoký ROAS tam často nie je inkrementálny (`kampanova-struktura.md`, sekcia Retargeting).

## Štruktúra vyhodnocovacieho výstupu

Drž sa šablóny zo SKILL.md (Zhrnutie pre klienta → Kontrola objemu dát → Tabuľka výkonu → Diagnostika → Verdikt). Pre klienta vždy preložiť číslo do dôsledku pre biznis: nie „hold rate 12 %", ale „ľudia odpadávajú v polovici videa — telo nedrží pozornosť, preto pripravíme kratšiu verziu".
