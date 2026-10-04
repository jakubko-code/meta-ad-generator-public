# Segmentové profily

Segment **preformuje** to, čo ostatné referencie berú ako default. `metriky-diagnostika.md` má baseline ladený na e-com direct response; tento súbor ho prepíše pre daný archetyp — najmä **čo je „hard" metrika**, **kedy vôbec smieš verdiktovať na hard**, a **ako vyzerá víťaz**.

**Načítaj tento súbor hneď po určení segmentu**, ešte pred vyhodnocovaním — inak budeš ťahať e-com logiku tam, kam nepatrí.

## Rýchly selektor (segment → „hard" metrika)

| Archetyp | „Hard" metrika | Typický problém pri vyhodnocovaní |
|----------|----------------|-----------------------------------|
| 1. E-com / DR | ROAS / CPA (purchase) | väčšinou dosť objemu — kontrola objemu dát splniteľná |
| 2. Lead-gen služby | CPL + **kvalita** leadu | málo konverzií → hard kontrola objemu dát sa nesplní |
| 3. Brand awareness | CPM, reach, **hold rate**, frequency | žiadny purchase event — ROAS irelevantná |
| 4. Cultural / event | intent (LP views, clicks) + reach v okne | multi-market + sezónne okno |
| 5. Infoprodukt | CPA na opt-in/registráciu → backend ROAS | dvojkrokový funnel, optimalizuj na opt-in |
| 6. B2B high-ticket | CPL **kvalifikovaného** leadu (SQL/MQL) | extrémne nízky objem, dlhý cyklus |

Ak biznis nesedí presne, vyber najbližší archetyp a povedz nahlas, čím sa líši.

---

## 1. E-com / Direct Response

- **Hard metrika a kedy verdiktovať:** ROAS / CPA na purchase (`actions:omni_purchase`, `purchase_roas`). Konverzný objem býva dostatočný → na hard verdiktuj po splnení kontroly objemu dát. Pri nízkom AOV alebo malom objeme použi ako proxy add-to-cart / initiate-checkout.
- **Posun benchmarkov:** baseline z `metriky-diagnostika.md` platí priamo (TOF e-com). ROAS porovnávaj voči break-even, nie voči cudziemu číslu.
- **Sediace angles/frameworky/kreatívy:** PAS pri hmatateľnej bolesti; UGC/demo, social proof, offer/zľava hooky; carousel na produktové feature; statik na BOF (cart abandoners).
- **Víťaz a škálovanie:** stabilný ROAS nad break-even nad kontrolou objemu dát → Post ID do ASC / Advantage+ Sales. Pozor na Test→Scale friction.
- **Test nuansy:** najpriamočiarejší segment; kontrola objemu dát na hard je reálne splniteľný. Drž odlišnosť konceptov (2026: diverzita > objem).

## 2. Lead-gen služby (local / services)

- **Hard metrika a kedy verdiktovať:** CPL **a kvalita** leadu (nie len cena). Konverzný objem býva nízky → hard kontrola objemu dát na lead/purchase sa často nesplní. Vtedy **verdiktuj a optimalizuj na vyššom evente vo funneli** (form view, button click, booking start) a hodnoť kvalitu, nie len počet.
- **Posun benchmarkov:** nižšie outbound CTR je normál; CPL posudzuj proti hodnote zákazníka, nie proti e-com benchmarku. Lead **volume vs quality** — lacný lead nízkej kvality nie je víťaz.
- **Sediace angles/frameworky:** dôvera, autorita, „ako to funguje", riešenie konkrétneho problému, recenzie/case studies, lead magnet. Menej „zľava", viac edukácie.
- **Víťaz a škálovanie:** nízky CPL pri dobrej kvalite. Škáluj opatrne — malé/lokálne publikum sa rýchlo vyčerpá (rastúca frequency), takže víťaz má strop objemu.
- **Test nuansy:** dlhší kontrola objemu dát (málo konverzií = pomalší signál). Počas testu zváž optimalizáciu na vyššie-objemový event, potom prepni. Soft metriky + mid-funnel event sú tvoj hlavný signál.

## 3. Brand awareness / upper-funnel

- **Hard metrika a kedy verdiktovať:** **nie ROAS.** Hard = efektívny reach, CPM, **hold rate** a completion (`video_p100`), frequency; brand lift ak je dostupný. Verdikt sa opiera o impresie/reach, nie o konverzie.
- **Posun benchmarkov:** hook/hold dominujú, outbound CTR a CPA sú sekundárne až irelevantné. Sleduj frequency proti únave.
- **Sediace angles/frameworky:** emócia, príbeh (PASTOR/story), distinktívne brand assets, konzistencia. Hook stále zastavuje scroll, ale cieľ je **zapamätateľnosť**, nie klik.
- **Víťaz a škálovanie:** vysoký hold rate + efektívny CPM/reach. Škáluj cez awareness/reach kampaň, manažuj frequency, plánuj creative waves proti únave.
- **Test nuansy:** kontrola objemu dát je o reach/impresiách, NIE o konverziách. Pravidlo „neverdiktuj na hard kvôli málo konverziám" tu neplatí — hard tu nie je konverzia. Vyhodnocuj p100 a hold rate.

## 4. Cultural / event (hybrid, multi-market, sezónne)

- **Hard metrika a kedy verdiktovať:** hybrid — intent signály (link clicks, landing page views, prípadne registrácia/vstupenka ak je tracking) + reach v **cieľovom časovom okne**. Často multi-market (napr. PL/HU/CZ/SK) a viazané na dátum eventu.
- **Posun benchmarkov:** **per-trh** (CPM aj CTR sa medzi trhmi líšia), pod sezónnym tlakom. Nepoužívaj jeden benchmark naprieč trhmi — porovnávaj v rámci trhu.
- **Sediace angles/frameworky:** zážitok, atmosféra/vizuál, FOMO a urgencia termínu, lokalizácia copy per trh; silný vizuálny hook (miesto/event).
- **Víťaz a škálovanie:** kreatíva, čo ťahá lacný kvalitný traffic/intent v danom trhu. Škáluj **per-market** a časuj k dátumu (build-up → peak → last-call).
- **Test nuansy:** krátke okno = rýchly kontrola objemu dát, ale v menších trhoch pozor na nízky objem. Testuj kreatívu **oddelene per trh** — čo ťahá v jednom trhu nemusí v inom; lokalizácia je samostatná premenná.

## 5. Infoprodukt (kurzy, webináre, VSL)

- **Hard metrika a kedy verdiktovať:** CPA na **opt-in/registráciu** (webinar signup, VSL opt-in) ako primárny, backend ROAS ako sekundárny. Dvojkrokový funnel — optimalizuj a verdiktuj na opt-in evente (má objem), nie na finálnom predaji (málo, neskoro).
- **Posun benchmarkov:** pri silnom hooku vyššie CTR/engagement; sleduj CPL na opt-in, potom show-up rate a sales konverziu.
- **Sediace angles/frameworky:** transformácia (FROM/TO), big promise + dôveryhodnosť, story/PASTOR, „mechanism/secret" angles, výsledky/social proof; dlhší VSL-style copy funguje. **Pozor na policy** (sľuby výsledkov, zdravie, zárobky).
- **Víťaz a škálovanie:** nízky CPL na opt-in pri dobrej show-up a sales konverzii. Škáluj cez opt-in optimalizáciu + retargeting na neukončené registrácie.
- **Test nuansy:** hook a promise sú najsilnejšie testovacie osi. Optimalizácia na opt-in dáva dosť objemu na čistejší kontrola objemu dát než finálny predaj.

## 6. B2B high-ticket

- **Hard metrika a kedy verdiktovať:** CPL **kvalifikovaného** leadu (SQL/MQL), nie raw lead. Veľmi nízky objem a dlhý sales cyklus → hard kontrola objemu dát sa takmer nikdy nesplní → **verdiktuj na mid-funnel** (LP view, lead form open, MQL) + kvalita.
- **Posun benchmarkov:** nízke CTR a vysoký CPL sú normál; hodnota dealu CPL ospravedlňuje. Publikum aj frequency malé.
- **Sediace angles/frameworky:** autorita, ROI/business case, case study („ako [firma] dosiahla [výsledok]"), thought leadership; lead magnet (whitepaper, audit, demo). Menej emócie, viac dôkazu a špecifickosti.
- **Víťaz a škálovanie:** kreatíva generujúca kvalifikované leady. Škálovanie limituje veľkosť publika (malý TAM) → skôr **creative rotation proti únave** než zvyšovanie objemu.
- **Test nuansy:** extrémne nízky konverzný objem → spoľahni sa na soft metriky + mid-funnel event; dlhý kontrola objemu dát; pri vyhodnotení kvalita > kvantita.
