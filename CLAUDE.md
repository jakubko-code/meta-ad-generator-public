# CLAUDE.md — spoločné pravidlá projektu

Repozitár musí zostať plne použiteľný v **Claude Code aj v Codexe**. `NAVOD.md` je kanonický workflow, `README.md` rýchly štart a `NAVOD.html` vizuálny návod pre kolegov. Jazyk práce a dokumentácie je slovenčina.

Obsahové zmeny návodu rob v `NAVOD.md`. `NAVOD.html` zosúlaď až na požiadanie, `README.md` iba na výslovný pokyn. Trvalé pravidlá workflowu zapisuj do repozitára (tento súbor, `NAVOD.md`, skilly) — nie iba do lokálnej pamäti agenta, lebo repozitár je záloha nástroja a pravidlá musia platiť aj pre kolegov a Codex.

## Povinný routing

Pri novom klientovi alebo chýbajúcej persone, painoch, awareness stage, angle či hooku začni skillom [Meta Ads Manager](.claude/skills/meta-ads-manager/SKILL.md). Až po režimoch S → E/A → B1 a platnom `test-plan.json` pokračuj skillom [Image Ad Generator](.claude/skills/image-ad-generator/SKILL.md).

```text
1 brand foundation
→ 2 strategický research (S)
→ 3 architektúra + koncepty (E + A)
→ 4 testovací plán (B1)
→ 5 copy a templates
→ 6 quality gates + človek
→ 7 generovanie + vizuálny QA
→ 8 test handoff (B2)
→ 9 performance learning (C + D)
```

Meta Ads Manager je strategický vlastník; Image Ad Generator je produkčný motor. Nevytváraj pre Codex odlišné kópie skillov.

## Brány, ktoré platia vždy

- Nové ad sety používajú `workflow_version: 2`, validný `test-plan.json` a hashovú väzbu vytvorenú cez `04-test-planning/test_plan.py bind`.
- Starý ad set bez tejto väzby alebo so starým plánom `schema_version: 1` je možné spustiť iba explicitne cez `--allow-legacy`; pri novom ad sete je tento prepínač zakázaný.
- Persona, angle, awareness stage, hook a template sa počas produkcie nesmú potichu meniť. Strategická zmena sa vracia do B1, aktualizuje plán a znovu ho naviaže. Hook z plánu musí byť presne renderovaný text (`brief.hook_field`, default `headline`) vložený cez `{{placeholder}}`.
- Nový plán má `schema_version: 2` (`test_design`, číselná dátová brána, `learnings`). Pred A/B1 načítaj `testing/learnings.md` a aktívne testy.
- Pred generovaním musia existovať hashovo previazané `scoring-{lang}.json` a ľudské `approval-{lang}.json`. Preklad (`source_prompts`) so scoringom 04–08 platí iba nad schváleným zdrojom s kompletným scoringom 01–08; image translator prenáša iba takto schválený text.
- Skóre agentov sa nikdy neprepisuje ani nevymýšľa. Pri tvorivom hodnotení pod 90 (agenti 01, 02, 03, 05) môže človek vedome prijať výnimku cez `workflow_gate.py override` s menom a dôvodom. Skutočné skóre ostane zapísané. Značka, formát, fakty a gramatika (04, 06, 07, 08) výnimku nemajú. Výnimku navrhni až po ponúknutí opravy, nie ako skratku.
- Najprv vždy spusti `generate_ads.py --validate-only`.
- Schválenie copy nie je pokyn generovať. Platené obrázky vytvor až po explicitnom „generuj“.
- PMax je iba voliteľný rozmerový export zo schválených Meta konceptov, nie nový strategický workflow. `--pmax` použi len keď človek výslovne požiada o PMax/Google Ads bannery; bežný pokyn na Meta generovanie ho nezahŕňa.
- Bezplatný template wireframe môže vzniknúť cez `05-creative-production/template_preview.py`. Platený Gemini specimen vyžaduje explicitný `--generate-preview`, generuje sa po jednom template, musí byť watermarked a nesmie sa zamieňať za produkčný výstup ani obísť brány.
- Cenu pre iný trh neprepočítavaj. Použi iba potvrdenú cenu a pri `workflow_gate.py approve` pridaj `--market-prices-confirmed`, ktorý zapíše `market_prices_confirmed=true`.
- Pri regenerácii oprav iba chybné varianty a nemaž hotové `outputs/`.
- Pri e-commerce musí architektúra (Režim E) obsahovať trvalú DPA / katalógovú kampaň z produktového feedu, ktorá beží stále vedľa Prospectingu aj Sandboxu. DPA nie je súčasťou B1 plánu ani bannerovej produkcie. Detail je v `meta-ads-manager/references/kampanova-struktura.md`. Textácia DPA a prompt pre externú AI sú v `katalogova-textacia.md`. Prompt pre externú AI sa nepoužíva na copy bannerov a jeho výstup je iba návrh na kontrolu.
- Kampane nespúšťaj, nepauzuj ani nemeň bez výslovného potvrdenia človeka. Verdikt v trackeri je odporúčanie; Stav sa mení až po potvrdenej zmene v účte.

## Spolupráca pri produkcii

Tieto pravidlá vznikli z reálnych incidentov; detail je v [Image Ad Generator](.claude/skills/image-ad-generator/SKILL.md), krok 5.

- **Formáty a rozloženie sa pýtaj, neurčuj ich sám.** Spolu s copy na schválenie (pred `bind`) sa opýtaj, ktoré pomery vyrobiť (4:5 feed, 9:16 Reels/Stories, 1:1, prípadne PMax) a kde bude logo a CTA. Dodatočný formát znamená nový plán, scoring, approval aj ďalšie kolo obrázkov; logo a CTA určené agentom skončili natesno v jednej linke.
- **„Generuj X“ znamená presne schválené varianty.** Nemeň štýl, execution ani copy; ak nie je jasné, ktorý variant alebo štýl sa myslí, spýtaj sa pred generovaním. Copy nových bannerov najprv vždy predlož v tabuľke na schválenie, aj pri brand-template formátoch.
- **Koncepty podľa researchu, nie podľa šablóny.** Uhly a formáty vyberaj z deep-researchu konkrétneho produktu; nelep stále tú istú sadu briefov.
- **Kreatívy dodané klientom** bežia popri našich bez B1 a scoringu. Agent ich skontroluje (fakty, súlad s textom a URL, formát voči umiestneniam), uloží do `client-creatives/` a zapíše do trackera ako `KLIENT-{dátum}` / `K01…`. Postup je v `NAVOD.md`, krok 8.
- **Štruktúra `brands/`:** kategória alebo kolekcia viacerých produktov je pseudo-produkt v `products/<kategoria>/` (inak ju dashboard nevidí); animácie patria do `products/<produkt>/animations/`, nie do `brand-dna/`.

## Research nástroje

Ak sú dostupné, používaj ich podľa účelu:

| Nástroj | Použitie |
|---|---|
| Exa | review mining, fóra a jazyk zákazníkov |
| DataForSEO | lokalizovaný SERP a keyword dáta; pre Slovensko nastav `sk` a lokalitu Slovensko |
| WebSearch / WebFetch | overenie faktu a načítanie známej URL |
| Meta Ads MCP | read-only analýza účtu, kreatív, fatigue a Ad Library |

Verbatim citácie a zdroje patria do `deep-research.md`; Agent 7 do nich traceuje claimy.

## Znalostná databáza (`references/`)

Pri režimoch Meta Ads Managera S, E, A, B1, C a D proaktívne otvor `references/meta/README.md` a príslušný `meta-<tema>-tactics.md`. Sú to odporúčania z článkov, nie pravidlá: brány a metodika skillov majú prednosť, vlastné dáta klienta tiež. Rozpor s metodikou skillu povedz nahlas; skill meň iba vedome so súhlasom človeka. Keď človek pošle článok alebo URL „do references“, postupuj podľa `references/README.md` (zdroj do `sources/`, poznatky do destilátu, aktualizovať index). Priečinok je v Gite, preto sem nepatria klientské dáta ani celé články.

## Dáta a bezpečnosť

- Brand pravidlá sú v `brands/{brand}/brand-dna/chyby-neopakovat.md`; prečítaj ich pred copy.
- Celý obsah `brands/*` je lokálny a ignorovaný Gitom. Nikdy nepouži `git add -f` na klientské dáta.
- Klientské dáta nemaž bez výslovného pokynu.
- API kľúče patria iba do `.env`; nevypisuj ani necommituj ich.
- Dashboard v `tools/dashboard/` je pomocný nástroj, nie krok workflowu. Creative QA slúži hotovým bannerom; Template knižnica globálnym aj klientskym wireframom a voliteľným specimen renderom.

## Klienti a úlohy (`~/agency-hub`)

- **`~/agency-hub`** je rozcestník klientov. `clients.yaml` páruje Productive projekt s ID pre Ads, GTM, GA4 a MC a s priečinkami (`priecinky.meta` = značka v `brands/`). Úlohy z Productive sa nekopírujú do súborov, ťahajú sa živo.
- Úlohy klienta: `python3 ~/agency-hub/scripts/productive_tasks.py --client <kľúč>` (kľúč z `clients.yaml`, pred behom `source ~/.zshrc`). Skript ukazuje len úlohy priradené Paľovi. Všetky otvorené úlohy projektu vráti Productive MCP `get_project_tasks` s `productive_project` z `clients.yaml`.
- **Z Productive len čítaj.** Nezapisuj komentáre, stavy, termíny, výkazy ani nové úlohy, kým to Paľo výslovne nezadá.
- **Rozpočet a poznámky naprieč kanálmi** sú v `~/agency-hub/clients/<kľúč>/` (`rozpocet.md`, `README.md`), ak priečinok existuje. Pred prácou s rozpočtom, ad setmi alebo čerpaním ho prečítaj; je jediný zdroj rozpočtu pre Metu aj Google, v `brands/` sa neopakuje. Odsúhlasenú zmenu rozpočtu zapíš tam (tabuľka + riadok do histórie).
- **Zakladanie novej značky** (`brands/<značka>/`): najprv nájdi klienta v `~/agency-hub/clients.yaml` (kľúč, Meta účet, Productive projekt) a prečítaj `~/agency-hub/clients/<kľúč>/`, ak existuje. Čo je v hube (klient, cieľ, cieľovka, kontakty, dátumy, rozpočet), do `brands/` neprepisuj, len naň odkáž; pýtaj sa len na to, čo chýba. Po založení doplň cestu do `priecinky.meta` v `clients.yaml` (jediný povolený zápis do yaml). Ak klient v `clients.yaml` nie je, povedz to Paľovi.
