# Audit nadväznosti Meta Ad Generatora

Dátum: 11. 9. 2026. Rozsah: spoločné pravidlá, NAVOD.md, README.md, NAVOD.html, oba projektové skilly, strategické a produkčné referencie, B1 validátor, generátor, scoring/approval, lokalizácia, dashboard, handoff a performance learning.

## Verdikt

Architektúra má správne poradie: brand → research → koncepty → testovací plán → copy → scoring a človek → generovanie a QA → handoff → výkon a učenie. Hlavné návody sa na tomto poradí zhodujú. Nástroj však ešte nemá spoľahlivo uzavretý celý cyklus. Najpevnejšia je ochrana presnej verzie promptov pred generovaním; slabšie sú experimentálny kontrakt, bonusové cesty a spojenie výstupov so skutočnými reklamami a historickými výsledkami.

Ide o audit implementácie a pracovných pravidiel, nie o audit výkonu konkrétneho klienta. Neboli menené klientské súbory, spúšťané platené rendery ani upravované kampane. Overenie Meta MCP bolo obmedzené na katalóg metrík, bez načítania klientskych účtov. Funkčné súbory zostali nezmenené.

## Čo funguje

- Meta Ads Manager má jasné vlastníctvo stratégie a Image Ad Generator produkcie.
- Nové ad sety štandardne vyžadujú workflow v2 a hash testovacieho plánu.
- Kontrola pokrytia concept_id plán ↔ prompty je 1:1; duplicity a chýbajúce koncepty sa blokujú.
- Scoring aj ľudský approval sú naviazané na presné bajty promptov. Zmena promptov bez obnovy artefaktov sa zablokuje.
- Bežný generátor kontroluje placeholdery, referenčné assety a potvrdenie zahraničných cien podľa jazyka.
- Dokumentácia rozlišuje schválenie copy, pokyn na platené generovanie a povolenie meniť kampane.
- Kategóriový research sa dá zdediť medzi SKU. Je to vhodný základ pre väčšie katalógy.
- Existuje vizuálny QA dashboard a oddelená knižnica template náhľadov.
- Všetkých 30 existujúcich testov prešlo.

## Nálezy a priority

### 1. P1 — Plánovaný hook nie je previazaný s renderovaným textom

Miesto: `07-image-generation/generate_ads.py:612`, funkcia `validate_strategy_contract`; mapovanie v `.claude/skills/meta-ads-manager/references/banner-produkcia.md`.

Validátor porovnáva `brief.hook` s `variants[].hook`. Nekontroluje však, či tomu zodpovedá `headline` alebo iné pole, ktoré sa skutočne vloží do promptu. Pri pôvodnom pláne môže vzniknúť iný headline, prejsť novým scoringom a approvalom a validácia nevyžiada návrat do B1.

Reprodukcia: v existujúcej testovacej fixture zmeniť len `headline`, obnoviť scoring/approval a zavolať `validate_only=True`. Výsledok: exit 0.

Oprava: explicitné mapovanie hooku na renderované pole/polia podľa template. Pri zdrojovom jazyku kontrolovať presnú zhodu; pri lokalizácii používať schválené jazykové mapovanie a zdrojový hash. Samotná rovnosť so slovenským hookom by legitímny preklad zablokovala.

### 2. P1 — Jedna testovaná premenná a dátová brána sú prevažne deklarácie

Miesto: `04-test-planning/test_plan.py:38`, `04-test-planning/test-plan-template.json`.

`constants` je zoznam textov a `data_gate` obsahuje dva neprázdne texty. Validátor neporovnáva konštanty medzi variantmi a nevyžaduje konkrétne číselné prahy. Aj dodávaná šablóna s neurčitým pokynom „prahy stanov…“ má `status: planned`. Test s jedným variantom je tiež platný, bez rozlíšenia pilotu od porovnania.

Reprodukcia: pri `test_variable: hook` zmeniť v druhom variante personu, angle aj template a zosúladiť prompty. Výsledok: exit 0.

Oprava: štruktúrované konštanty, kontrola rozdielov podľa druhu testu, konkrétne prahy a jednotky; explicitne odlíšiť pilot, porovnanie konceptov a izolovaný test. Pri nízkom objeme má zostať verdikt predbežný.

### 3. P1 — Prekladový scoring umožňuje preskočiť agentov 01–03 aj pri novom zdroji

Miesto: `07-image-generation/generate_ads.py:658`, `07-image-generation/workflow_gate.py:38`.

O počte vyžadovaných agentov rozhoduje iba `scoring.mode`. Chýba väzba na existujúci zdrojový prompt s kompletným a aktuálnym scoringom. Označenie nového slovenského zdroja ako `translation` preto zníži požadované kontroly na 04–08.

Reprodukcia: v platnej fixture zmeniť mode na translation a odstrániť agentov 01–03. Výsledok: exit 0.

Oprava: vyžadovať `source_prompts_sha256`, overiť pôvodný source scoring a nemennosť strategických polí. Výber jazyka sám osebe nesmie rozhodovať, či ide o preklad.

### 4. P1 — Image translator obchádza produkčné artefakty

Miesto: `BONUS/03-image-translator/translate_ads.py:378` a `:467`.

Samostatný image translator po kontrole obrázka, jazyka a API kľúča volá platený provider. Nevyžaduje testovací plán, jazykový scoring, schválený cieľový text ani potvrdenie cien. `--dry-run` ukáže všeobecnú prekladovú inštrukciu; konkrétny výsledný text ešte nie je známy. To nezodpovedá pravidlu NAVOD.md, že bonusy nesmú obísť brány.

Oprava: používať schválený textový preklad ako vstup, pripojiť rovnaké brány, prípadne túto cestu dočasne vyradiť z produkčného workflowu. Tento nález bol overený čítaním kódu, bez API generovania.

### 5. P1 — Vyhodnotenie zamieňa link CTR s outbound CTR

Miesto: `.claude/skills/meta-ads-manager/references/meta-mcp-playbook.md:55` a tabuľka výpočtov; `metriky-diagnostika.md:11`.

Playbook označuje `actions:link_click / impressions` za outbound CTR. Dňa 11. 9. 2026 katalóg `ads_get_field_context` potvrdil:

- `actions:link_click` je alias `link_click`; zahŕňa ciele v Meta aj mimo Meta.
- `outbound_clicks` počíta kliknutia mimo Meta.
- `outbound_clicks_ctr` je percentuálny podiel outbound kliknutí a je dostupný aj na ad úrovni.

Oprava: používať priamo `outbound_clicks_ctr` alebo `100 × outbound_clicks / impressions`; link CTR uvádzať osobitne. Pri nulových impresiách uviesť N/A. Pri statických banneroch nemajú video hook/hold metriky zmysel a majú byť N/A. Obmedzenie `3_second_video_plays` na account/campaign/adset v aktuálnom MCP bolo naopak potvrdené ako správne.

### 6. P1 — Handoff nedáva spoľahlivý kľúč banner → nasadenie → výsledky

Miesto: `.claude/skills/meta-ads-manager/references/tracker-navod.md:23`, šablóna trackeru; `meta-mcp-playbook.md:23`.

Tracker eviduje interné ID, plan/concept a cestu, ale nemá povinné account ID, campaign ID, adset ID, ad ID, creative/post ID ani identitu presného PNG. Playbook pripúšťa hľadanie cez názov. Po duplikovaní, premenovaní alebo škálovaní môže jedna kreatíva žiť vo viacerých reklamách a výsledky sa nespoja jednoznačne. Chýbajú aj samostatné historické snapshoty obdobia, meny, atribúcie a optimalizačného eventu.

Oprava: manifest hotových assetov a samostatná evidencia nasadení 1:N. Pred launchom stav prepared; po reálnom nasadení doplniť platformové ID. Performance ukladať po obdobiach a konkrétnom nasadení, nie iba prepisovať posledné čísla v jednom riadku.

### 7. P1 — Tracker zamieňa odporúčanie s vykonanou akciou

Miesto: `.claude/skills/meta-ads-manager/references/tracker-navod.md`, sekcia aktualizácie po C, riadok Stav.

Referencia prikazuje pri verdikte Vypnúť prepísať stav na Vypnutá a pri Škálovať na Škálovaná. Analytický verdikt však nespôsobuje zmenu v Meta účte. Evidencia môže tvrdiť, že reklama je vypnutá, hoci stále míňa.

Oprava: oddeliť `recommendation`, `actual_status`, `action_confirmed_at` a zdroj potvrdenia. Skutočný stav meniť až po overení vykonanej akcie.

### 8. P2 — Onboarding skrýva povinné ručné odovzdanie Deep Research

Miesto: `02-strategic-research/product-research-process.md:138`; `strategicky-research.md:55`.

Hlavný workflow vedie používateľa cez research, ale podrobný postup zakazuje kompiláciu bez ChatGPT Deep Research výstupu dodaného používateľom. Strategická referencia pritom ako minimum uvádza web a jeden zdroj zákazníckeho jazyka. Zdroje nehovoria rovnako jasne, čo stačí na dokončenie kroku.

Oprava: explicitne odlíšiť minimum na začatie od podmienok dokončenia. Buď ručné odovzdanie uviesť už v hlavnom návode, alebo povoliť rovnocenný doložený research agenta s jednotnými kritériami kvality. Nestačí túto požiadavku len ignorovať.

### 9. P2 — Lokalizácia nie je úplne zovšeobecnená pre nových klientov a trhy

Miesto: `BONUS/04-copy-translator/copy-translator.md`, ukážka JSON, sekcie glossary, generovanie a pravidlá; `.claude/skills/image-ad-generator/SKILL.md`, Bonus flowy; `NAVOD.md`, Lokalizácia.

Prekladový návod prikazuje univerzálne tykanie a menenie mien recenzentov podľa jazykových zoznamov. Obsahuje normatívne pravidlá odvodené od GymBeam, ktoré nemusia sedieť novému brandu. Ukážka JSON neobsahuje workflow v2 obálku a aktuálne strategické polia; ukážky preferujú batch a jeden príkaz s `--prompts-file` neuvádza cieľový `--lang`. Pri kompletnom approvale pre HU by tak zostal predvolený jazyk SK a validácia ho odmietla.

Skill navyše hovorí všeobecne o zachovaní toho istého plánu pri prekladoch, kým NAVOD to podmieňuje nezmeneným trhom a ponukou. Generátor trh plánu neporovnáva s explicitným produkčným trhom; cenu posudzuje cez `lang != sk`.

Oprava: oddeliť market, language a currency; pri zmene trhu explicitne rozhodnúť o novom pláne. Tykanie/vykanie odvodzovať od klienta. Autora skutočnej recenzie svojvoľne nemenovať inak. Aktualizovať JSON a príkazy na v2 a google default; pred prekladom vyžadovať schválený zdroj.

### 10. P2 — Vizuálny PASS nie je naviazaný na konkrétne bajty obrázka

Miesto: `tools/dashboard/dashboard.js`, localStorage a export; `NAVOD.md`, regenerácia a dashboard; `generate_ads.py:635`.

Dashboard uchováva verdikty podľa identity súboru v prehliadači. Nahradený PNG pod rovnakou cestou môže zdediť starý verdikt. Generátor tiež neviaže scoring/approval na hashe brand a produktových assetov. Zmena brand karty po schválení v doplnkovej skúške nezablokovala validáciu. To neznamená, že každá oprava obrázka musí vyžadovať nové schválenie copy; chýba však evidencia presnej verzie renderu a zneplatnenie vizuálneho QA.

Oprava: QA viazať na hash finálneho PNG; pri zmene renderu vyžiadať nové vizuálne posúdenie. K renderu uložiť použitý prompt hash, asset hashe, provider/model a parametre. B2 môže odovzdať iba túto konkrétnu schválenú verziu.

### 11. P2 — Fatigue používa rôzne hranice a nejednoznačné pásma

Miesto: `fatigue-detector.md`, interpretácia a CPA Score; `tracker-navod.md`, šablóna fatigue.

Tracker označuje skóre 75+ ako kritické; detektor až 81+. Skóre 78 preto dostane rozdielny slovný stav. Tracker síce odkazuje na nadradenú tabuľku, ale vkladaná šablóna zostáva zavádzajúca. CPA +50 % má v detektore súčasne skóre 75 aj 100; priebežné hodnoty medzi bodmi nemajú definované zaokrúhľovanie/interpoláciu. Nie je jednoznačne ošetrená nulová baseline a neúplné týždne.

Oprava: jedna tabuľka hraníc a spoločná deterministická výpočtová funkcia; definovať okná a správanie pri nedostatku dát. Skóre ponechať ako orientačný signál, nie automatický pokyn na pauzu.

### 12. P2 — Zápis learnings existuje, povinné čítanie v ďalšej iterácii chýba

Miesto: Image Ad Generator krok 1; Meta Ads Manager S/A/B1 vstupy; `09-performance-learning/README.md`.

Výsledky sa majú zapísať do `testing/learnings.md`, ale pred novými konceptmi a plánom nie je explicitný povinný krok načítať relevantné learnings. Uvedenie historických výsledkov medzi ideálnymi vstupmi nie je rovnaké ako konkrétna vstupná kontrola. Agent môže vyrobiť ďalšie varianty bez aplikovania už získaného poznatku.

Oprava: pred A/B1 načítať learnings a aktívne testy klienta; do plánu zapísať použité learning IDs, predchodcu testu a dôvod iterácie. Manuálny režim je v poriadku, ak je odovzdanie explicitné.

## Doplnkové metodické rozpory

- `tvorba-kreativ.md:106` tvrdí, že hook test musí meniť aj vizuálnu scénu. Pre test presného textového headline to koliduje s izoláciou premennej. Rozlíšiť textový hook od celého audiovizuálneho hooku a od testu konceptov; tvrdenie o algoritme nepoužívať ako všeobecný dôvod meniť konštanty.
- Opakované AI generovanie celého obrázka aj pri zmene jedného headline prirodzene mení vizuál. Rovnaký template nezaručuje rovnaký obrázok. Pri čistom headline teste je vhodný spoločný podklad a deterministické vloženie textu, alebo treba výsledok označiť ako porovnanie kreatív s obmedzenou izoláciou.
- Kontrola existencie research súborov je v manuálnom checkliste, nie v pre-flight generátore. Aj platná testovacia fixture prejde bez research dokumentov. Nezamieňať technický PASS s potvrdením kvality výskumu; pri rozšírení brán overovať aj zdedený `research-source`.
- `test_plan.py bind` viaže hash validného plánu, ale sám neoveruje zhodu obsahu promptov. V návode quality gates ho preto nepovažovať za ekvivalent kompletnej kontroly kontraktu.
- Read-only Meta MCP schopnosť overiť definície metrík je funkčná. Audit neoveroval oprávnenia ku konkrétnemu účtu ani kompletný živý performance report.

## Odporúčané poradie opráv

1. Opraviť hook/render väzbu, validáciu experimentu a source/translation scoring.
2. Zjednotiť bonusové produkčné cesty a lokalizačný návod s v2.
3. Zaviesť manifest assetov, QA podľa hashov a evidenciu reálnych Meta nasadení.
4. Opraviť CTR a oddeliť odporúčanie od stavu; ukladať reprodukovateľné performance snapshoty a konkrétne dátové brány.
5. Zjednotiť fatigue a povinné čítanie learnings; spresniť onboarding a synchronizovať hlavné návody s detailnými referenciami.

Akceptačný test celého cyklu má použiť fiktívneho klienta: onboarding → zdedený research SKU → dva varianty jednej premennej → scoring → explicitné schválenie → simulovaný render → QA → fiktívne deployment IDs → offline export metrík → predbežný/finálny verdikt → nový plán s learning ID. Platené API ani reálna aktivácia kampane na tento integračný test nie sú potrebné.

## Vykonané overenie

- `python3 -m unittest discover -s tests -v`: 30 testov, 0 zlyhaní, 0 chýb.
- Štyri dočasné negatívne scenáre: headline mimo plánu, nečistý hook test, translation scoring bez source 01–03, zmenený brand asset. Všetky dnes vracajú validačný exit 0.
- Katalóg Meta Ads MCP: priamym read-only volaním overené definície a podporované úrovne link/outbound metrík a 3-second video plays.
- Audit nemení implementáciu. Uvedené opravy sú návrhy, nie už realizované funkcie.
