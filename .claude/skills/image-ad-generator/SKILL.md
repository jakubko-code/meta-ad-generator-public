---
name: image-ad-generator
description: "Vyrob statické Meta Ads bannery z už pripravenej stratégie: over brand foundation, strategický research, Meta Ads koncept a test-plan.json; potom vytvor prompts-{lang}.json, vykonaj scoring, ľudské schválenie, bezpečnú AI generáciu a vizuálnu kontrolu. Použi pri novej ad sade, banneroch pre produkt, prepise copy, regenerácii, multiply, preklade alebo ad-swipe. Pri novom klientovi alebo chýbajúcom avatarovi/angle/hooku najprv použi projektový meta-ads-manager."
---

# Image Ad Generator — produkcia kreatív

Tento skill je **produkčný motor**, nie začiatok stratégie. Pre nový klientsky workflow platí:

```text
1 Brand foundation
→ 2 Meta Ads strategický research (S)
→ 3 architektúra + kreatívne koncepty (E + A)
→ 4 testovací plán pred produkciou (B1)
→ 5 copy a templaty
→ 6 quality gates + ľudské schválenie
→ 7 generovanie + vizuálny QA
→ 8 test handoff (B2)
→ 9 vyhodnotenie a learning (C + D)
```

Jazyk práce a výstupov je slovenčina. Úplný používateľský workflow je v [NAVOD.md](../../../NAVOD.md).

## Routing pred produkciou

| Situácia | Kde začať |
|---|---|
| Nový klient alebo chýba persona/pain/angle mapa | `meta-ads-manager` Režim S, potom E/A/B1 |
| Existujúci klient, nová kategória | Krok 2: strategický research, potom A/B1 |
| Existujúci research, ale nový koncept | `meta-ads-manager` Režim A, potom B1 |
| Hotový koncept a validný `test-plan.json` | Krok 5 v tomto skille |
| Regenerácia schválenej chybnej kreatívy | Krok 7, iba konkrétny variant |

Avatar, angle, awareness stage a hook sa **nedopĺňajú po banneroch**. Ak chýbajú, zastav produkciu a vráť sa do Meta Ads Managera.

## Krok 1 — Brand foundation *(raz na brand)*

Načítaj `brands/{brand}/brand-dna/chyby-neopakovat.md`, `voice-copy-styl.md` a `MEMORY.md`, ak existuje.

- Chýbajúci research brief: [brand research](../../../01-brand-foundation/brand-research/).
- Chýbajúce `brand-spec-card.png` a `visual-style-card.png`: [brand cards](../../../01-brand-foundation/brand-cards/).
- SVG logo zachovaj ako master. Pre image provider priprav aj transparentné `logo.png` a podľa potreby `logo-white.png`; generátor ich načíta ako voliteľné samostatné referencie po dvoch povinných brand kartách.

Pri novom klientovi sa človeka spýtaj na prioritný sortiment, sezónnosť a kategórie, ktoré sa líšia zákazníkom, cenou alebo konkurenciou. Neodvodzuj obchodnú prioritu z poradia na webe.

## Krok 2 — Strategický research *(Meta Ads Manager S)*

Research sa robí raz na zákaznícky problém/kategóriu, nie automaticky na každé SKU. Metodika je v [02-strategic-research](../../../02-strategic-research/) a v `meta-ads-manager/references/strategicky-research.md`.

Povinné dokumenty kategórie: `deep-research.md`, `avatar-sheet.md`, `offer-brief.md`, `necessary-beliefs.md`, `cep-sheet.md`, `briefs.md`. Každé SKU má `product-facts.md`.

Režim S zapisuje do týchto istých súborov; nevytvára paralelnú stratégiu. Bez zdrojovo doloženej persony, painu a angle mapy nepokračuj.

Plný research kategórie čaká na ChatGPT Deep Research výstup od človeka (prompt pripraví agent podľa `02-strategic-research/product-research-process.md`). Vynechať ho možno iba na výslovné rozhodnutie človeka, zapísané v hlavičke `deep-research.md`. SKU so zdedeným researchom má v `product-facts.md` hlavičku `> research-source:`; generátor pri workflow v2 overí, že vlastný alebo zdedený research má všetkých šesť dokumentov; pri pláne schema 2 je povinný aj `product-facts.md`.

## Kroky 3–4 — Koncept a testovací plán *(Meta Ads Manager E/A/B1)*

Režim E určí kampaňový kontajner, ak je to v rozsahu úlohy. Režim A pripraví pre každý statický variant: personu/avatar, angle, awareness stage, presný hook alebo headline, CTA a formát.

Pred copy vytvor v ad sete `test-plan.json` podľa [04-test-planning](../../../04-test-planning/):

```bash
python3 04-test-planning/test_plan.py init \
  --ad-set brands/{brand}/products/{product}/product-image-ads/{ad-set} \
  --plan-id TP-YYYY-MM-DD-NAZOV --market sk --objective sales \
  --funnel-stage TOF --test-variable hook
```

Pred plánom načítaj `brands/{brand}/testing/learnings.md` a aktívne testy v `tracker.md`; použité learning ID a dôvod iterácie patria do `learnings`. Doplň hypotézu, testovanú premennú, `test_design` (`isolated` / `concept-comparison` / `pilot`), konštanty, primárnu metriku, číselnú dátovú bránu a koncepty. Človek potvrdí smer testu; nastav `status: planned` a spusti `test_plan.py validate`.

## Krok 5 — Brief → template → copy

Poradie je záväzné: **koncept/brief → test plan → template → copy**.

### Pred schválením copy sa opýtaj na formáty a rozloženie

Tieto otázky polož **spolu s tabuľkou copy**, ešte pred `bind` — vtedy sa odpovede zapíšu do plánu (`format`) a promptu jedným kolom scoringu a schválenia. Ponúkni konkrétne možnosti, nie otvorenú otázku.

- **Formáty:** 4:5 feed, 9:16 Reels/Stories, 1:1, prípadne PMax sada (iba na výslovnú žiadosť). Nerozhoduj jeden pomer sám. Formát doplnený až po generovaní znamená úpravu plánu, nový bind, scoring, approval aj ďalšie kolo obrázkov (klient, 2026-08-07). Pri 9:16 spomeň, že generátor pridá Reels safe zóny a logo cez `--logo-overlay` potrebuje `--logo-margin-y` okolo `0.30`.
- **Rozloženie loga a CTA:** ponúkni dvojice, napr. „logo vľavo hore + CTA dole na stred“ alebo „logo vľavo dole + CTA vpravo dole“. Logo a CTA v tej istej spodnej linke si konkurujú a pôsobia natesno (klient, 2026-08-07). Logo vložené cez `--logo-overlay` sa dá posunúť bez zmeny promptu (`--logo-position`, `--logo-width`, `--logo-margin-y`, `place_logo.py`); CTA kreslí model, takže jeho umiestnenie je v prompte a mení hash.

### Pokyn „generuj“ nemení zadanie

Pokyn „generuj 1 a 3“ znamená presne tie schválené varianty v schválenom štýle a so schválenou copy. Nevyber iný štýl ani execution a neprepisuj text (incident Selena: „1 a 3“ sa mylne vyrobili ako iný štýl s prepísanou copy). Ak nie je jasné, ktorý variant alebo štýl sa myslí, spýtaj sa pred generovaním. Schválenie copy stále nie je pokyn na generovanie.

### Koncepty podľa researchu

Uhly a formáty odvodzuj z deep-researchu konkrétneho produktu (beliefs, CEP, objekcie). Nepoužívaj stále rovnakú formulaickú sadu briefov B01–B04 pre každý produkt.

### Kam ukladať

- Kategória alebo kolekcia viacerých produktov je pseudo-produkt: `brands/{brand}/products/{kategoria}/product-image-ads/{ad-set}/`. Dashboard aj galérie skenujú iba `brands/*/products/*/product-image-ads/*/outputs*/manifest.json`, takže ad set mimo tejto cesty nevidia. Manifest drží cesty k PNG od koreňa repozitára — pri presune ad setu treba prepísať aj `results[].file`.
- Animácie (`BONUS/02-animate`) patria do `brands/{brand}/products/{produkt}/animations/{date}-{slug}/`, nie do `brand-dna/`.

Vyber template z [05-creative-production](../../../05-creative-production/), brand templates alebo ad-swipe. Vytvor `prompts-{lang}.json` s `workflow_version: 2`.

Pri neznámom alebo novom brand template najprv vytvor bezplatný štrukturálny náhľad cez `python3 05-creative-production/template_preview.py --template PATH`. Voliteľný realistickejší specimen vyžaduje explicitný `--generate-preview`, generuje sa po jednom template, je watermarked a ukladá sa mimo `outputs/`. Template preview je vizuálna dokumentácia; nespúšťa produkčný workflow a nenahrádza test plán, scoring, approval ani `--validate-only`.

Každý `brief` musí obsahovať:

- `id`, `persona`, `angle`, `emotion`, `customer_voice_anchor`,
- `concept_id`, `awareness_stage`, `hook` presne podľa `test-plan.json`,
- voliteľne `hook_field` — kde sa hook renderuje (default `headline`; zoznam pri viacriadkovom hooku, napr. `["headline_lines.0", "headline_lines.1"]`).

Prompt string obsahuje iba `{{placeholdery}}`, nikdy hardcoded sample copy. Generátor vynúti, že hook z plánu je presne text v `hook_field` (tolerujú sa iba veľké písmená a medzery) a že sa vkladá cez `{{placeholder}}`. Po dokončení previaž prompty s presnými bajtmi plánu:

```bash
python3 04-test-planning/test_plan.py bind --prompts path/to/prompts-sk.json
```

`bind` hneď overí kontrakt plán ↔ prompty a pri nezhode skončí kódom 1.

## Krok 6 — Quality gates a ľudské schválenie

Spusti agentov z [06-quality-gates](../../../06-quality-gates/): 1–6 paralelne, potom 7 a 8. Agenti 01–07 potrebujú score ≥90 a PASS; Agent 08 má binárny PASS/FAIL.

Skutočné skóre vždy zapíš, aj keď je pod prahom. Najprv ponúkni opravu copy. Ak človek vedome trvá na pôvodnom texte pri tvorivom hodnotení (01 Persona, 02 Angle, 03 Emócia, 05 Copy Excellence), zaznamená výnimku človek: `python3 07-image-generation/workflow_gate.py override --prompts … --agent 05 --by "Meno" --at "ISO čas" --reason "…"`. Výnimka platí iba pre presné bajty promptov a zapísané skóre. Agenti 04, 06, 07 a 08 výnimku nemajú, ich nález sa vždy opraví. Incident klient 2026-09-14.

Inicializuj a doplň `scoring-{lang}.json` podľa README quality gates. Po PASS zobraz človeku tabuľku všetkých renderovaných textov. Jeho schválenie zaznamenaj cez `07-image-generation/workflow_gate.py approve`.

Ak preklad alebo verzia pre jazyk mimo `market` plánu obsahuje cenu, lokálny človek musí potvrdiť sumu aj menu a príkaz `approve` musí dostať `--market-prices-confirmed`. Bez neho generátor cenu zablokuje.

Zmena `test-plan.json` zneplatní strategickú väzbu. Zmena promptov zneplatní scoring aj approval.

Starý ad set bez `workflow_version: 2` alebo so starým plánom `schema_version: 1` prejde iba s explicitným `--allow-legacy`. Tento prepínač nikdy nepoužívaj pri novom ad sete ani na obídenie chýbajúceho plánu.

Pri izolovanom teste generátor porovná aj renderované prompty: pri `hook` teste sa smú líšiť iba polia hooku a brief; inak ostáva cena rovnaká (okrem testu `offer`), pri `angle` aj CTA a pri `visual` celé copy.

## Krok 7 — Validácia, generovanie a vizuálny QA

Najprv vždy bezplatná validácia:

```bash
python3 07-image-generation/generate_ads.py \
  --brand-dir brands/{brand}/products/{product}/product-image-ads/{ad-set} \
  --lang sk --validate-only
```

Platené generovanie spusti až po výslovnom „generuj“. Default provider je `google`; iného providera ani batch režim nevyberaj bez explicitného pokynu.

### Voliteľný PMax export — iba na výslovnú žiadosť

PMax nie je samostatný strategický workflow. Vychádza z rovnakých schválených Meta konceptov, `test-plan.json`, promptov, copy, scoringu a approvalu. Nevytváraj novú personu, angle ani hook a nemeň copy len preto, že sa mení pomer strán.

Prepínač `--pmax` použi **iba vtedy, keď človek výslovne požiada o PMax alebo Google Ads bannery**. Všeobecný pokyn „generuj bannery“ znamená štandardné Meta výstupy a PMax nezahŕňa.

Najprv musí prejsť rovnaký bezplatný `--validate-only`. Po explicitnom pokyne na PMax spusti:

```bash
python3 07-image-generation/generate_ads.py \
  --brand-dir brands/{brand}/products/{product}/product-image-ads/{ad-set} \
  --lang sk --provider google --resolution 1K --pmax
```

Vzniknú tri rekomponované varianty každého bannera: `1.91:1` (1200×628), `1:1` (1200×1200) a `4:5` (960×1200). Dôležitý obsah zostáva v centrálnej 80 % safe zóne a súbory sa ukladajú oddelene do `outputs-pmax/` (pri inom jazyku `outputs-{lang}-pmax/`). `google-batch` sa pre tento režim nepoužíva. Každý PMax PNG prejde rovnakým vizuálnym QA; zmena copy by vyžadovala nový scoring a approval.

Ak má byť v kreatíve logo, nenechaj ho kresliť model — zakáž ho v prompte, rezervuj mu roh a pridaj `--logo-overlay` (voliteľne `--logo-width`, `--logo-position`). Generátor vloží reálny súbor z `brand-dna/` a vyberie bielu alebo farebnú verziu podľa jasu podkladu.

Po generovaní prečítaj každý PNG a over presné copy, logo, brand identitu, cenu pre trh, chýbajúci alebo vymyslený text a integritu formátu. Verdikt: PASS / PASS s drobnosťou / FAIL. Pri FAIL regeneruj iba chybný variant cez `--concepts C08` (viac konceptov môže zdieľať template, `--templates` by prepísal aj hotové); nemaž `outputs/`. Hľadaj aj text, ktorý v copy nie je — model vie prekresliť ukážkový text z brand karty (klient W17). Logo s nízkym kontrastom oprav bez generovania cez `place_logo.py`, ktorý aktualizuje aj SHA-256 v manifeste.

Pri regenerácii nikdy nespájaj `rm -rf outputs` s generovaním v jednom príkaze — prerušený beh raz zmazal všetky hotové bannery a stihol vyrobiť iba torzo. Generátor posiela **všetky** fotky z `--images-dir` ku každej reklame; bannery rôznych produktov preto rob samostatnými behmi s vlastným priečinkom fotiek, a ten musí ležať v strome `brands/{brand}/`, inak sa nenájdu brand karty.

`outputs*/manifest.json` nesie pri každom PNG jeho SHA-256 a vstupy renderu (prompts hash, test plan, approval, provider/model, hashe brand kariet a produktových fotiek). Do B2 odovzdaj práve tú verziu, ktorá dostala vizuálny PASS.

## Kroky 8–9 — Handoff a spätná slučka

Po vizuálnom PASS odovzdaj výstupy späť do `meta-ads-manager`:

- B2 doplní konkrétne kreatívy do `brands/{brand}/testing/tracker.md` (súbor + SHA, Stav Pripravená, Meta ID až po nasadení) a pripraví launch checklist;
- C vyhodnotí dostatočné dáta;
- D sleduje fatigue;
- learning sa vracia do kroku 2, 3, 4 alebo 5 podľa diagnózy.

Dashboard je pomocný nástroj, nie krok workflowu: `python3 tools/dashboard/build_dashboard.py`. Záložka Creative QA slúži na hotové bannery a verdikt viaže na SHA-256 PNG (zmenený súbor treba posúdiť znova); Template knižnica zobrazuje globálne aj klientské wireframy, platené specimen rendery a upozornenie na náhľad neaktuálny voči SHA-256 template-u.

## Bonus flowy

[BONUS](../../../BONUS/): multiply, animácia statiku, image translator, copy translator a video concepts.

Preklad schváleného zdroja je `prompts-{lang}.json` s `"source_prompts": "prompts-sk.json"`; brief, `concept_id` a template sú zamknuté na zdroj. Pre každý jazyk sa opakuje jazykový scoring (`init-scoring` zapíše hash zdroja pri každom súbore so `source_prompts`) a ľudské schválenie; zdroj musí mať kompletný scoring 01–08 a approval, aj keď preklad dostane plný scoring. `test-plan.json` ostáva rovnaký iba pri nezmenenej ponuke — pri inom trhu o pláne rozhodni v B1. Samostatná vetva pre iný trh (vlastná ponuka, ceny, oslovenie) nie je preklad: má vlastný plán a zdrojový scoring. Image translator prenáša iba takto schválený text, a to len do evidovaného renderu aktuálneho zdroja s vizuálnym PASS (`--qa-export`).

## Zákazy

- Negeneruj platené obrázky bez výslovného pokynu.
- Nevymýšľaj avatar, angle ani hook počas písania promptov.
- Nemeň schválenú copy bez nového scoringu a approval.
- Nemaž klientské dáta ani hotové výstupy.
- Nespúšťaj, nepauzuj ani neupravuj kampane bez výslovného potvrdenia človeka.
