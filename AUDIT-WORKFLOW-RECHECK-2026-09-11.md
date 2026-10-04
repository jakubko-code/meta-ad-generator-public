# Kontrola implementácie odporúčaní

Kontrolovaná verzia: `61c521e`, vrátane implementačného commitu `78944ef`. Dátum: 11. 9. 2026.

## Výsledok

Veľká časť odporúčaní je implementovaná. Kontrola však ešte nemá výsledok PASS: zostávajú obchádzky schvaľovacích brán, neúplná izolácia testov a medzery v image translatori. Implementáciu som nemenil; vytvoril som tento kontrolný report. Skúšky používali dočasné dáta, bez platených API a bez zásahov do účtov.

`python3 -m unittest discover -s tests -v`: **64 testov, 0 chýb, 0 zlyhaní**. `git diff --check` bez chýb. Zelené testy nepotvrdzujú nižšie uvedené dodatočné scenáre; tie dnešná sada nepokrýva.

## Potvrdené opravy

- Zdrojový renderovaný headline musí zodpovedať hooku plánu; podporované sú aj viacriadkové polia a povinné placeholdery.
- Nový plán cez init používa schema 2, číselné dátové brány, learnings a rozlíšenie isolated / concept-comparison / pilot.
- Schema 2 odmieta hook test meniaci personu, angle alebo číslo template v pláne.
- Bežný translation scoring vyžaduje zdrojový hash, kompletný source scoring a approval; pôvodné jednoduché prepnutie mode bez source sa blokuje.
- Image translator používa konkrétne schválené dvojice textov, kontroluje cieľové artefakty a potvrdenie ceny.
- Outbound CTR a link CTR sú v metodike oddelené.
- Tracker obsahuje Meta Ad ID, Adset ID a SHA kreatívy, rozlišuje nasadenia 1:N a odporúčanie od skutočného stavu.
- Fatigue pásma a interpolácia sú zjednotené v dokumentácii; výpočet naďalej vykonáva agent podľa metodiky.
- Pred ďalšou stratégiou sa explicitne načítavajú learnings a aktívne testy.
- Research handoff je vysvetlený v skille; preklady už univerzálne nepredpisujú tykanie a premenovanie skutočných recenzentov.
- Manifest zaznamenáva hashe PNG a renderových vstupov. Nové QA hodnotenia nesú hash obrázka.

## Otvorené nálezy

### R1 — P1: JSON null preskočí scoring aj approval

Miesto: `07-image-generation/generate_ads.py:789–795`, `:883–893`.

`load_gate_artifact` prijme platný JSON `null` a vráti `(None, [])`. Volajúca funkcia vykoná kontroly iba pri hodnote odlišnej od None. Prítomný súbor s obsahom `null` teda nie je označený za chybný, ale preskočí celú kontrolu.

Reprodukcia nad platným ad setom bez ceny: do `scoring-sk.json` aj `approval-sk.json` zapísať `null`; `generate_ads(..., validate_only=True)` vracia **0**. To isté načítavanie sa používa aj pre artefakty zdroja prekladu. Ide o novo identifikovanú dieru, nie tvrdenie, že ju zaviedol posledný commit.

Oprava: loader musí vyžadovať JSON objekt a odmietnuť null, pole, číslo, reťazec aj boolean. Pridať testy samostatne pre source/target scoring a approval. Kontrolovať aj vnorené typy tak, aby chybný artefakt skončil zrozumiteľným FAIL.

### R2 — P1: Preklad v režime source obíde kontrolu zdrojového schválenia

Miesto: `07-image-generation/generate_ads.py:883–888`.

Zdrojové brány sa overujú iba podľa `scoring.mode == translation`. Strategická kontrola však rozpoznáva preklad podľa `source_prompts`. Dve funkcie tak používajú rozdielny rozhodovací údaj.

Reprodukcia: vytvoriť platný preklad s `source_prompts`, cieľovým scoringom 01–08 v mode source a cieľovým approvalom. Odstrániť `scoring-sk.json` a `approval-sk.json`. Validácia DE stále vracia **0**. Cieľ má síce vlastných osem kontrol, ale väzba na schválený zdroj a jeho zmeny už nie je vynútená.

Oprava: pri prítomnom `source_prompts` vždy vyžadovať zdrojový hash a overenie zdrojových brán; buď vyžadovať mode translation, alebo dovoliť kompletný scoring ako dodatočnú kontrolu bez vypnutia overenia zdroja.

### R3 — P1: Hook test stále môže meniť ponuku a ostatné copy

Miesto: `04-test-planning/test_plan.py:37–43`, `:208–226`; produkčná kontrola v `generate_ads.py`.

Izolácia porovnáva vybrané strategické polia plánu. Neviaže konštanty na renderované CTA, body, subhead, cenu a ponuku. Rovnaké metadáta preto nezaručujú izoláciu toho, čo zákazník reálne uvidí.

Reprodukcia so **schema_version 2**, isolated hook testom a dvoma variantmi: prvý má cenu 10 € a CTA „Zisti viac“, druhý 100 € a „Kúp teraz“. Cenu aj CTA vložiť do promptu cez placeholdery a obnoviť scoring/approval. Validácia vracia **0**.

Oprava: definovať povolené menené renderované polia pre konkrétny test a kontrolovať nemennosť ostatnej copy/ponuky aj medzi promptmi. Zmena celého vizuálu pri novom AI rendere zostáva metodickou limitáciou aj po tomto doplnení.

### R4 — P1: Vynechaný text v preklade môže zostať v obrázku

Miesto: `BONUS/03-image-translator/translate_ads.py:122–149`, `:204–212`.

`copy_pairs` vytvorí len prienik neprázdnych zdrojových a cieľových polí. Kontrola unplaced zachytí cieľový text bez zdroja, nie zdrojový text bez cieľa. Prompt pritom prikazuje nenahrádzané texty zachovať. Vynechaný subhead, stará cena alebo skrátený zoznam benefitov preto nemajú inštrukciu na odstránenie a môžu zostať v pôvodnom jazyku.

Reprodukcia: source obsahuje a renderuje `subhead: Stará ponuka`; schválený target subhead vynechá. `prepare_language` vracia **prázdny zoznam chýb** a dvojice obsahujú iba headline.

Oprava: kontrolovať pokrytie oboma smermi a dĺžky zoznamov. Odstránenie textu musí byť explicitná schválená operácia; inak image translator odmietnuť a použiť nový render.

### R5 — P2: Image translator nepáruje vstupný PNG s presným schváleným zdrojom

Miesto: `BONUS/03-image-translator/translate_ads.py:185–188`, `:508`; `source_aspect` využíva manifest iba pre pomer strán.

Výber zdrojového promptu sa riadi názvom nadradeného priečinka. Chýba overenie záznamu renderu, PNG hashu, source prompt hashu a vizuálneho PASS. Aj starý obrázok, obrázok z iného jazyka alebo nesúvisiaci súbor v rovnakom priečinku je akceptovaný ako vstup pre výmenu zdrojových textov.

Reprodukcia: do priečinka zodpovedajúceho konceptu vložiť `unrelated.png`, bez manifestu a QA. `prepare_language` ho prijme; nečíta obsah obrázka. Skúška nevolala provider a netvrdí, že provider prijme poškodený PNG — ukazuje chýbajúcu identitnú kontrolu pred jeho volaním.

Oprava: vyžadovať zhodu vstupu s manifestom, jeho aktuálny hash a `render.prompts_sha256` voči deklarovanému source. Vizuálny PASS viazať na ten istý PNG. Pre existujúce výstupy bez manifestu zaviesť explicitné doplnenie evidencie.

### R6 — P2: Historické QA bez hashov zostáva platné

Miesto: `tools/dashboard/dashboard.js:82–90`.

`isStale` je true iba pri existencii oboch hashov a ich nezhode. Staré localStorage hodnotenie PASS bez sha256 sa preto ďalej zobrazuje ako PASS aj po regenerácii. Nové hashované hodnotenia fungujú po obnove dashboardu; nedokončená je migrácia predchádzajúcich hodnotení a prípad chýbajúceho súboru.

Oprava: hodnotenie bez preukázateľného hashu zobraziť ako neoverené/zastaralé. Pôvodný verdikt a poznámku zachovať len ako históriu. Do testov pridať starý PASS bez hashu a zmiznutý PNG. Nález je založený na priamom čítaní vetvy JS, nie na spustenom prehliadači.

## Zvyšné obmedzenia rozsahu

- Produkcia povoľuje schema 1 s upozornením bez explicitného legacy opt-in pre plán. Nový init už správne používa schema 2, ale ručne skopírovaný starý plán obíde nové kontroly. Ak je to zámerná kompatibilita, treba jasne odlíšiť starý a nový ad set.
- Chýbajúce `product-facts.md` zostáva warning, hoci dokumentácia ho označuje za povinný SKU vstup. Testovacia fixture prechádza bez neho. Kontrola researchu overuje existenciu a neprázdnosť šiestich dokumentov, nie obsahovú úplnosť.
- Handoff, história výsledkov a fatigue sú stále manuálny workflow agenta podľa dokumentácie. To môže byť vhodné, ale nebol doplnený jeden integračný test celého cyklu cez simulovaný render, QA, nasadenie, metriky a learning. Jednotkové testy túto slučku nenahrádzajú.
- Market, language a currency stále nie sú samostatne zviazané v produkčnom kontrakte; potvrdenie ceny používa porovnanie jazyka s market plánu. Oddelenie metrík podľa obdobia a atribúcie je dokumentované, no kompletný reprodukovateľný snapshot účtu/meny/atribúcie nie je strojovo vynútený.

## Odporúčaná priorita

Najprv R1, potom R2–R4. Následne R5–R6 a offline integračný test celého cyklu. Základnú architektúru netreba meniť; ide o dotiahnutie kontrol na hraniciach jednotlivých krokov.
