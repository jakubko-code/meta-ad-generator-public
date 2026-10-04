# CTC Core Methodology Series – Meta Advertising v1.0

**URL:** https://commonthreadco.com/pages/methodology-meta
**Autor:** Common Thread Collective (CTC), americká e-com agentúra; bez mena autora
**Dátum publikácie:** neuvedený (stránka bez dátumu, verzia v1.0; spomína dáta Meta za Q1 2025). V názve súboru je dátum uloženia.
**Uložené:** 2026-10-01
**Kategória:** Structure / Testing / Measurement
**Relevantné tactics:** meta-struktura-tactics.md, meta-testovanie-tactics.md, meta-meranie-tactics.md

---

## Kľúčové poznatky (pre destiláciu)

**Cieľ optimalizácie**
- Optimalizujú na **inkrementálnu marginu (contribution margin)**, nie na reportované tržby ani ROAS v platforme.
- Andromeda (retrieval) a GEM (ranking) vyberajú reklamy; štruktúra účtu je podľa nich „strategické rozhodnutie“:
  algoritmus pracuje v mantineloch, ktoré mu nastavíš.

**Predvolená architektúra (e-com, Shopify)**
- Štyri jadrové kampane: **Evergreen ACQ**, **Evergreen RTN** (retencia, existujúci zákazníci), **Marketing Moment ACQ**
  a **Marketing Moment RTN** (kalendárové akcie s pevným začiatkom a koncom ad setu).
- Cieľ Sales (~95 % prípadov), optimalizácia na **hodnotu s minimálnym ROAS**, ASC alebo CBO.
- **Min. ROAS na úrovni ad setu**, nie kampane. RTN má nižší cieľový ROAS ako ACQ.
- Broad cielenie; ACQ vylučuje kupujúcich (Shopify, pixel, Klaviyo lifetime), RTN cieli na nich.
- Max **50 reklám v ad sete** (limit Mety); plní sa postupne, po 50 reklamách nový ad set.
- **DABA (Dynamic Ads for Broad Audiences) má v každej Evergreen kampani vlastný ad set**, lebo pracuje
  s inými signálmi ako statiky.
- **„Nafúknutý“ rozpočet + cost control:** rozpočet vyšší, než sa reálne minie, a spend riadi ROAS cieľ.
  Kolísanie spendu zo dňa na deň je žiaduce (lacné dni využiť, drahé vynechať).

**Atribúcia a signál**
- Optimalizačné okno **7-day click**; podľa ich geo testov s inkrementalitou súvisí najviac.
- **7-day click + 1-day view** iba pri malom rozpočte, vysokom AOV alebo minimálnej inej (organickej) návštevnosti.
- CAPI povinné, **EMQ 7+/10**, preferujú natívnu Shopify integráciu; mesačne kontrolovať, či počet server
  eventov sedí s počtom objednávok.

**Kreatíva a testovanie**
- **Žiadny testovací rozpočet:** každá reklama súťaží o každé euro v celom portfóliu.
- **Reklamu nikdy nevypínať** podľa historického výkonu: minulý ROAS nepredpovedá budúci, Meta rozhoduje podľa
  signálov nad rámec ROAS. Vypnutie berie „opciu“ bez zlepšenia výsledku.
- Nové kreatívy idú do existujúcich Evergreen a Marketing Moment ad setov; prioritou je **diverzita konceptov,
  nie drobné variácie**.
- Využívať Advantage+ creative (dynamický text, creative enhancements, viac URL).

**Expanzia pri nedočerpaní rozpočtu (4 fázy, v poradí)**
1. Viac kreatívy: ďalšie odlišné koncepty do Evergreen a Marketing Moment.
2. Bid surface: duplikát Evergreen ako Lowest Cost s **Bid Cap, cieľová CPA = AOV / cieľový ROAS**.
3. Under-spend ASC: samostatná ASC iba s reklamami, ktoré v Evergreen minuli **menej než 3× cieľovej CPA**
   (dostanú druhú šancu).
4. Uvoľnenie cieľa ROAS: iba ak marža ide podľa plánu a tržby/spend sú pod plánom; tROAS prehodnotiť
   podľa inkrementality.

**Denná práca media buyera:** správna alokácia rozpočtu (bez stropov na kampani), disciplína ROAS cieľov
podľa inkrementality a marže, nepretržitý prísun novej kreatívy.

**Inkrementalita (ich databáza)**
- ACQ: medián **iROAS 1,14×** platformou reportovaného 7-day click (45 geo holdout testov) → 7-day click mierne
  podhodnocuje skutočný efekt.
- RTN: medián **iROAS 0,60×** → retencia je výrazne menej inkrementálna, než ukazuje Ads Manager.
- Podobné výsledky má podľa nich verejná databáza Haus (640+ experimentov).
- iROAS = reportované tržby 7-day click × faktor inkrementality. Faktor sa mení so sezónou, konkurenciou,
  únavou kreatív; treba ho pre každý biznis pretestovať.

## Dôležité citácie

> "The structure is the strategy."

> "There is no 'testing budget.' There is only the budget, and every ad competes for it."

> "When you turn off an ad based on its past performance, you are asserting a relationship between the past and the future that does not exist."

> "I will spend as much as you can find at this return threshold."

> "Meta Retention has a median iROAS of 0.60 (6% incrementality), while Meta Acquisition has a median iROAS of 1.14 (63% incrementality)."

## Kontext a obmedzenia

- Metodika veľkej US agentúry pre Shopify značky s veľkými rozpočtami, Klaviyo a pravidelnými geo holdout
  testami. Pri malých SK účtoch neprenášať doslovne (50 reklám v ad sete, 4 kampane, bid cap kampane).
- Je to aj marketingový materiál agentúry; čísla inkrementality sú ich interná databáza, nie nezávislá štúdia
  (Haus je jediné externé potvrdenie).
- Percentá v citácii o inkrementalite („6 %“, „63 %“) nie sú v texte vysvetlené a nesedia priamo s iROAS;
  použiteľné sú iba faktory 1,14× a 0,60×.
- Bez dátumu: Meta UI a názvy (ASC, DABA) overiť v aktuálnom účte.
