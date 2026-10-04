# Meta Ad Generator — úplný návod

Tento návod je kanonický pracovný postup pre Claude Code, Codex aj kolegov. Cieľom nie je iba vyrobiť pekný banner, ale vytvoriť kreatívu s jasnou hypotézou, kontrolovanou výrobou a merateľným výsledkom.

## Základný princíp

```text
STRATÉGIA                           PRODUKCIA                    UČENIE
1 Brand → 2 Research → 3 Koncept → 4 Test plán
                                      ↓
                    5 Copy → 6 Kontroly → 7 Banner
                                                  ↓
                                  8 Handoff → 9 Výsledky
                                                   └──→ ďalšia iterácia
```

Meta Ads Manager začína pred produkciou. Image Ad Generator nevymýšľa personu, angle ani hook počas tvorby bannera; vyrába schválený koncept. `test-plan.json` je kontrakt medzi stratégiou a produkciou.

## Ktorý skill použiť

| Situácia | Začni tu |
|---|---|
| Nový klient | Meta Ads Manager S → E/A → B1, potom Image Ad Generator |
| Nová kategória existujúceho klienta | Krok 2, potom A → B1 |
| Nový koncept pri hotovom researchi | Meta Ads Manager A → B1 |
| Hotový koncept a platný testovací plán | Image Ad Generator, krok 5 |
| Oprava chybného schváleného bannera | Image Ad Generator, krok 7 |
| Výsledky kampane alebo fatigue | Meta Ads Manager C alebo D |

Pri novom klientovi (a pred Režimom E) najprv nájdi klienta v `~/agency-hub/clients.yaml` a prečítaj `~/agency-hub/clients/<kľúč>/` (`README.md`, `rozpocet.md`), ak existuje. Čo tam je (klient, cieľ, cieľovka, kontakty, dátumy, rozpočet), sa nepýtaj a do `brands/` neprepisuj, len naň odkáž. Rozpočet Mety je vždy len v hube. Podklady od klienta a dokumenty pre viac kanálov (mediaplány, kreatívne koncepty, timeline, reporty Meta + Google) sú v hube v `inputs/` a `reporty/`, nie v `brands/`. Po založení `brands/{brand}/` doplň cestu do `priecinky.meta` v `clients.yaml`.

Agent musí načítať `.claude/skills/meta-ads-manager/SKILL.md` pre strategické režimy a `.claude/skills/image-ad-generator/SKILL.md` pre produkciu.

## Krok 1 — Brand foundation

Robí sa spravidla raz na značku. Výstupy sú v `brands/{brand}/brand-dna/`:

- `brand-research-brief.json` — positioning, audience, voice, vizuál a obmedzenia,
- `brand-spec-card.png` — rýchla vizuálna referencia,
- `visual-style-card.png` — štýl fotografií a kompozície,
- `voice-copy-styl.md` — pravidlá hlasu,
- `chyby-neopakovat.md` — G-pravidlá a zaznamenané incidenty.

Podklady a prompty sú v `01-brand-foundation/`. Pri novom klientovi si potvrď prioritnú kategóriu, sezónnosť a trh. Obchodnú prioritu neodvodzuj iba z poradia produktov na webe.

## Krok 2 — Strategický research (Meta Ads Manager S)

Research sa robí na zákaznícky problém alebo kategóriu; produktové fakty osobitne na SKU. Použi metodiku v `02-strategic-research/`.

Povinné výstupy v `products/{product}/marketing-research/`:

- `deep-research.md` — zdroje, review mining a doslovný jazyk zákazníkov,
- `avatar-sheet.md` — konkrétne persony, pains, túžby a objections,
- `offer-brief.md` — ponuka, cena, garancia a dôkazy,
- `necessary-beliefs.md` — presvedčenia potrebné ku konverzii,
- `cep-sheet.md` — category entry points,
- `briefs.md` — angle mapa a kreatívne smery,
- `product-facts.md` — overené fakty konkrétneho produktu.

Claim, citát, číslo a cena musia byť traceovateľné do týchto zdrojov. Ak chýba dôkaz, nepouži ich.

**Ručné odovzdanie Deep Research.** Plný research novej kategórie obsahuje ChatGPT Deep Research: agent pripraví prompt (`02-strategic-research/product-research-process.md`, Step 2), človek ho spustí v ChatGPT a výstup vloží späť. Agent medzitým robí vlastný review mining. Na **začatie** stačí URL webu a jeden zdroj reálneho zákazníckeho jazyka; na **dokončenie** kroku treba Deep Research výstup, interný research a doplnené alebo priznané medzery. Ak človek výslovne rozhodne, že Deep Research vynecháme, zapíš to do hlavičky `deep-research.md` (kto, kedy, prečo) a výstupy označ ako hypotézu na overenie testom.

SKU v už pokrytej kategórii dostane iba `product-facts.md` s hlavičkou `> research-source: ../../<kategoria>/marketing-research/`. Generátor pri workflow v2 overí, že vlastný alebo zdedený research obsahuje všetkých šesť dokumentov kategórie a pri pláne schema 2 aj `product-facts.md`; technický PASS však nepotvrdzuje kvalitu researchu.

## Krok 3 — Kampaň a kreatívne koncepty (E + A)

Režim E určí kampaňový kontajner, objective, funnel stage, CBO/ABO a naming, ak sú súčasťou zadania. Pri e-shope architektúra vždy obsahuje trvalú DPA / katalógovú kampaň z feedu. Beží stále a nie je súčasťou testovacieho plánu. Textáciu DPA a prompt pre ChatGPT / Gemini pripraví agent do `testing/dpa-textacia.md`. Výstup externej AI je iba návrh, ktorý agent skontroluje podľa brand pravidiel a schváli človek. Režim A pripraví varianty v poradí:

```text
avatar/persona → angle → awareness stage → hook → body/CTA → formát
```

Každý koncept dostane stabilné `concept_id`. Varianty majú byť strategicky zrozumiteľné ešte pred dizajnom. Ak nevieme pomenovať, komu reklama hovorí a čo testuje, do produkcie nejde.

## Krok 4 — Testovací plán pred produkciou (B1)

V ad sete vytvor `test-plan.json`:

```bash
python3 04-test-planning/test_plan.py init \
  --ad-set brands/{brand}/products/{product}/product-image-ads/{ad-set} \
  --plan-id TP-YYYY-MM-DD-NAZOV \
  --market sk --objective sales --funnel-stage TOF --test-variable hook
```

**Pred plánom načítaj `brands/{brand}/testing/learnings.md` a aktívne testy v `tracker.md`.** Do plánu zapíš, ktoré learning ID si použil, predchodcu testu a dôvod iterácie (`learnings`). Nový klient bez learnings to uvedie v `learnings.note`.

Doplň hypotézu, testovanú premennú, konštanty, primárnu metriku, dátovú bránu a koncepty. Povolené awareness stages sú `unaware`, `problem-aware`, `solution-aware`, `product-aware`, `most-aware`. Povolené testované premenné sú `concept`, `hook`, `angle`, `format`, `copy`, `offer`, `visual`.

Plán `schema_version: 2` rozlišuje tri typy testu (`test_design`):

| `test_design` | Kedy | Čo validátor vynúti |
|---|---|---|
| `isolated` | chceme prenositeľný poznatok o jednej osi | ≥ 2 varianty; testované pole sa líši, ostatné strategické polia sú rovnaké (napr. pri `hook` persona, awareness, angle, formát aj template) |
| `concept-comparison` | porovnávame celé koncepty (iná persona, angle aj hook) | ≥ 2 varianty, `test_variable: concept`; výsledok hovorí o koncepte, nie o jednej premennej |
| `pilot` | overujeme jeden koncept | presne 1 variant, `test_variable: concept`; verdikt je vždy predbežný |

Dátová brána má okrem popisu aj čísla: `minimum_days`, `minimum_impressions_per_variant` a `minimum_events_per_variant` (`event` + `count`, napr. 30 `outbound_clicks`). Pod prahom je verdikt iba predbežný. Starší plán so `schema_version: 1` izoláciu ani číselné prahy strojovo nekontroluje, preto ho generátor pustí iba s výslovným `--allow-legacy` (existujúce ad sety); nový plán vždy vytvor cez `init`.

Pri izolovanom teste generátor porovná aj renderované prompty: pri `hook` teste sa smú líšiť iba polia hooku a brief; v ostatných testoch ostáva cena rovnaká (okrem `offer`), pri `angle` aj CTA a pri `visual` celé copy.

Človek potvrdí smer testu a stav sa zmení na `planned`. Potom:

```bash
python3 04-test-planning/test_plan.py validate --plan path/to/test-plan.json
```

B1 neznamená spustenie kampane. Je to produkčné zadanie a experimentálny kontrakt.

## Krok 5 — Template a copy

Vyber template z `05-creative-production/01-templates-by-motion/`, prípadne z brand-specific templates alebo ad-swipe. Vytvor `prompts-{lang}.json` s `workflow_version: 2`.

Ak ide o nový alebo neznámy template, najprv si zobraz jeho štruktúru. Bezplatný wireframe vytvoríš cez:

```bash
python3 05-creative-production/template_preview.py --template path/to/template.md
python3 tools/dashboard/build_dashboard.py
```

Nájdeš ho v záložke **Template knižnica**. Voliteľný realistickejší Gemini specimen sa smie vytvoriť iba explicitným `--generate-preview`; je označený watermarkom, uložený mimo `outputs/` a nenahrádza produkčný render ani žiadnu bránu.

Každý brief obsahuje minimálne:

- `id`, `concept_id`, `persona`, `angle`, `awareness_stage`, `hook`,
- `emotion`, `customer_voice_anchor`,
- voliteľne `hook_field` — pole alebo zoznam polí, v ktorých sa hook renderuje (default `headline`; napr. `["headline_lines.0", "headline_lines.1"]` alebo `review_text`),
- template a všetky textové/obrazové polia vyžadované daným formátom.

**Spolu s tabuľkou copy sa opýtaj na formáty a rozloženie** — ešte pred `bind`, aby sa odpovede zapísali do plánu a promptu jedným kolom scoringu a schválenia. Formáty: 4:5 feed, 9:16 Reels/Stories, 1:1, prípadne PMax (iba na výslovnú žiadosť). Rozloženie: kde bude logo a kde CTA; ponúkni konkrétne dvojice a nedávaj ich do jednej spodnej linky. Formát ani rozloženie agent neurčuje sám.

Uhly a formáty sa odvodzujú z researchu konkrétneho produktu, nie z rovnakej sady briefov pre každý produkt. Kategória alebo kolekcia viacerých produktov je pseudo-produkt v `products/{kategoria}/` — ad set mimo `products/*/product-image-ads/` dashboard nevidí.

Strategické polia musia presne zodpovedať konceptu v pláne. Hook sa kontroluje aj v tom, čo sa naozaj vykreslí: hodnota `hook_field` sa musí zhodovať s hookom v pláne (tolerujú sa iba veľké písmená a medzery) a prompt ju musí vkladať cez `{{placeholder}}`, nie natvrdo. Po dokončení:

```bash
python3 04-test-planning/test_plan.py bind --prompts path/to/prompts-sk.json
```

Príkaz zapíše ID a SHA-256 plánu a hneď overí kontrakt plán ↔ prompty (koncepty, brief polia, hook ↔ renderované pole). Ak niečo nesedí, vypíše chyby a skončí kódom 1. Ak sa plán neskôr zmení, validácia produkciu zastaví. Existujúci starý ad set bez `workflow_version` spustíš iba vedome s `--allow-legacy`; pri novom ad sete tento prepínač nepoužívaj.

## Krok 6 — Quality gates a ľudské schválenie

Spusti agentov v `06-quality-gates/`:

1. Persona Fit
2. Angle Execution
3. Emotional Resonance
4. Brand Consistency
5. Copy Excellence
6. Format Compliance
7. Fact-Check
8. Copy Editor

Agenti 01–06 môžu bežať paralelne, potom 07 a 08. Agenti 01–07 potrebujú skóre aspoň 90 a PASS. Agent 08 má PASS/FAIL a veto. Scoring zároveň kontroluje, že produkcia nemení schválenú personu, angle, awareness, hook ani template.

Inicializuj hashovo previazaný artefakt:

```bash
python3 07-image-generation/workflow_gate.py init-scoring \
  --prompts path/to/prompts-sk.json --mode source
```

Po skutočnom vyhodnotení doplň výsledky a `status: passed`. Následne ukáž človeku tabuľku finálnych textov. Jeho schválenie zaznamenaj:

```bash
python3 07-image-generation/workflow_gate.py approve \
  --prompts path/to/prompts-sk.json --by "Meno schvaľovateľa" \
  --at "2026-08-06T14:30:00+02:00" --language sk
```

Ak verzia pre trh mimo SK obsahuje cenu, lokálny človek musí potvrdiť sumu aj menu a approval vytvoríš s cieľovým jazykom a flagom:

```bash
python3 07-image-generation/workflow_gate.py approve \
  --prompts path/to/prompts-de.json --by "Meno schvaľovateľa" \
  --at "2026-08-06T14:30:00+02:00" --language de \
  --market-prices-confirmed
```

Zmena promptov zneplatní scoring aj approval. Ak scoring navrhne nový strategický smer, vráť sa do B1, aktualizuj plán a znovu ho naviaž.

**Výnimka pri tvorivom hodnotení.** Ak agent 01, 02, 03 alebo 05 dá menej ako 90 a človek po ponúknutej oprave vedome chce pôvodný text, skutočné skóre ostane zapísané a človek zaznamená výnimku:

```bash
python3 07-image-generation/workflow_gate.py override --prompts path/to/prompts-sk.json \
  --agent 05 --by "Meno" --at "2026-09-14T14:00:00+02:00" --reason "Prečo ostáva pôvodný text"
```

Výnimka platí iba pre presné bajty promptov a zapísané skóre. Značka (04), formát (06), fakty (07) a gramatika (08) výnimku nemajú.

## Krok 7 — Validácia, generovanie a vizuálny QA

Najprv vždy bezplatná kontrola:

```bash
python3 07-image-generation/generate_ads.py \
  --brand-dir path/to/ad-set --lang sk --validate-only
```

Kontroluje testovací plán, jeho hash, strategické polia, renderovaný hook, research dokumenty, prompty, scoring, approval, placeholdery, market price a potrebné assety. Pri `--prompts-file prompts-hu.json` sa jazyk odvodí z názvu súboru.

Platené generovanie spusti iba po výslovnom pokyne „generuj“. Pokyn „generuj 1 a 3“ znamená presne tie schválené varianty v schválenom štýle a so schválenou copy; ak nie je jasné, ktoré, spýtaj sa:

```bash
python3 07-image-generation/generate_ads.py \
  --brand-dir path/to/ad-set --lang sk --provider google --resolution 1K
```

### Voliteľný PMax export z Meta bannerov

PMax nemá vlastný strategický workflow. Používa rovnaký schválený Meta koncept, template, copy, `test-plan.json`, scoring a approval; mení iba kompozíciu a rozmery. Nevytváraj kvôli nemu nový avatar, angle ani hook.

PMax generuj **iba na výslovnú žiadosť používateľa o PMax alebo Google Ads bannery**. Samotné „generuj bannery“ alebo schválenie Meta sady nie je súhlas s PMax generovaním.

Po úspešnom štandardnom `--validate-only`:

```bash
python3 07-image-generation/generate_ads.py \
  --brand-dir path/to/ad-set --lang sk --provider google --resolution 1K --pmax
```

Skript vytvorí každý schválený banner v troch Google Ads pomeroch a odporúčaných rozmeroch:

- landscape `1.91:1` — `1200×628`,
- square `1:1` — `1200×1200`,
- portrait `4:5` — `960×1200`.

Kritický obsah drží v centrálnej 80 % safe zóne. Výstupy zapisuje oddelene do `outputs-pmax/`, pri inom jazyku do `outputs-{lang}-pmax/`. Režim nepoužíva `google-batch`. Každý nový PNG otvor a vizuálne skontroluj; ak by sa mala meniť copy, treba zopakovať scoring a approval.

Rozmery a safe zóna vychádzajú z [oficiálnych požiadaviek Google Ads pre PMax image assets](https://support.google.com/google-ads/answer/14530211). Pred väčšou produkciou over, či Google špecifikácie nezmenil.

### Logo: generovať alebo vložiť

Model logo často osekne, zväčší cez produkt alebo nakreslí dvakrát. Spoľahlivejšie je nechať ho úplne mimo promptu a vložiť reálny súbor až po generovaní:

```bash
python3 07-image-generation/generate_ads.py \
  --brand-dir path/to/ad-set --lang sk --provider google \
  --logo-overlay --logo-width 0.20 --logo-position bottom-left
```

Skript vezme `logo.png` alebo `logo-white.png` z `brand-dna/` a sám vyberie verziu podľa jasu plochy, na ktorú logo dosadá. Podmienka: prompt musí logo **výslovne zakázať** a nechať zvolený roh vizuálne pokojný, inak vznikne logo dvakrát.

Po generovaní otvor každý PNG a over:

- presné copy bez preklepov a vymyslených textov,
- logo, farby, produkt a vizuálnu identitu,
- cenu a ponuku pre správny trh,
- safe zones, aspect ratio a integritu template,
- že vizuál stále realizuje plánovaný hook a angle.

Verdikt je PASS, PASS s drobnosťou alebo FAIL. Pri FAIL regeneruj iba chybný variant; nemaž hotové `outputs/`.

Každý render zapíše do `outputs*/manifest.json` SHA-256 finálneho PNG a presné vstupy (`render`): prompts hash, test plan, approval súbor, provider/model, rozlíšenie a hashe brand kariet aj produktových fotiek. Vizuálny QA v dashboarde sa viaže na hash PNG — nový render pod rovnakou cestou, staré hodnotenie bez hashu aj chýbajúci súbor dostanú stav **Prehodnotiť** a treba ich posúdiť znova. Oprava renderu nevyžaduje nové schválenie copy, ak sa prompty nezmenili.

**Headline test pri AI renderi:** aj pri rovnakom template model zakaždým prekreslí celý obrázok, takže sa mení aj vizuál. Čistý headline test potrebuje spoločný podklad (jeden schválený render a iba výmena textu) — inak výsledok v trackeri označ ako porovnanie kreatív s obmedzenou izoláciou.

### Regenerácia chybných variantov

Cieľ je prepísať iba zlé súbory a nechať hotové bannery na mieste. Priečinok `outputs/` nemaž a nepremenúvaj a nikdy nespájaj `rm -rf outputs` s generovaním v jednom príkaze — prerušený beh raz zmazal všetky hotové bannery. Generátor posiela všetky fotky z `--images-dir` ku každej reklame, preto bannery rôznych produktov rob samostatnými behmi s vlastným priečinkom fotiek v strome `brands/{brand}/`.

Iba chybný koncept pregeneruješ cez `--concepts C08`; ostatné výstupy a ich záznamy v manifeste ostanú. Pri `--logo-keep-clean` sa stará čistá kópia pri novom rendri nahradí.

**Najprv rozhodni, či sa mení copy.** Ak áno, oprav `prompts-{lang}.json`, čím sa rozbije hashová väzba a musíš zopakovať scoring aj approval (krok 6) — inak pre-flight neprejde. Ak je copy v poriadku a zlyhal len render, prompty nechaj tak a nič sa neopakuje.

**Vyber, čo sa má pregenerovať, cez `--templates`.** Ak je na danom template jediný koncept, píš rovno do `outputs/`:

```bash
python3 07-image-generation/generate_ads.py \
  --brand-dir path/to/ad-set --lang sk --provider google \
  --templates 21 --aspects 4:5 --exact-size
```

Ak template zdieľa viac konceptov, použi postup s dočasným priečinkom nižšie.

**`--aspects` a `--exact-size` idú spolu.** Tieto dva flagy určujú názov súboru, a preto aj to, či sa pôvodný banner prepíše:

| Príkaz | Vznikne súbor |
|---|---|
| bez `--aspects` | `…_v1_img1.png` |
| `--aspects 4:5` | `…_v1_4x5_img1.png` |
| `--aspects 4:5 --exact-size` | `…_v1_1080x1350_img1.png` |

Ak pôvodný beh použil `--exact-size` a regenerácia nie, vzniknú **nové súbory s iným názvom** a chybné bannery zostanú ležať vedľa nich. Preto: pozri sa na názov existujúceho PNG a použi rovnakú kombináciu flagov. Pri px názve (`1080x1350`) vždy pridaj `--exact-size`.

Predvolené rozmery: `1:1` = 1080×1080, `4:5` = 1080×1350, `9:16` = 1080×1920, `16:9` = 1920×1080, `2:3` = 1080×1620.

**Duplicitný `template_number`.** Pri hook teste zdieľa viac konceptov jeden template, takže `--templates 21` zasiahne **všetky koncepty na tom template naraz** — filter podľa `concept_id` v skripte nie je. Hotové bannery by sa prepísali.

Riešenie je pustiť beh do dočasného priečinka a prekopírovať späť iba opravený súbor:

```bash
python3 07-image-generation/generate_ads.py \
  --brand-dir path/to/ad-set --lang sk --provider google \
  --templates 21 --aspects 4:5 --exact-size \
  --output-dir outputs-regen
```

Potom z `outputs-regen/` prenes do `outputs/` len PNG chybného konceptu a zvyšok priečinka zmaž. Výstupné priečinky sú odlíšené cez `concept_id` (`21-…-C01`, `21-…-C02`), takže vieš presne, ktorý súbor je ktorý.

Nerieš to okresaným `prompts-{lang}.json` iba s jedným konceptom — pre-flight vyžaduje pokrytie plán ↔ prompty presne 1:1 a takýto súbor neprejde.

## Krok 8 — Test handoff po produkcii (B2)

Až po vizuálnom PASS doplň reálne kreatívy do `brands/{brand}/testing/tracker.md`. B2 priradí creative ID, súbor a jeho SHA-256 z manifestu k `plan_id` a `concept_id`, pripraví launch checklist a overí, že porovnávané varianty menia iba plánovanú premennú. Odovzdáva sa iba verzia PNG, ktorá dostala vizuálny PASS.

Pred spustením má riadok stav **Pripravená** a prázdne Meta ID. Po reálnom nasadení doplň Meta Ad ID a Adset ID — podľa nich sa výsledky párujú, názov je iba záloha. Jedna kreatíva nasadená do viacerých reklám (duplikácia, škálovanie) má riadok na každé nasadenie.

B2 môže pripraviť návrh spustenia. Kampaň nesmie spustiť, pauzovať ani meniť bez výslovného potvrdenia človeka.

### Kreatívy dodané klientom

Klient môže poslať vlastné bannery alebo videá, ktoré chce mať v účte popri našich. Nevznikli v tomto workflowe, preto nemajú B1 plán, scoring ani approval a brány z krokov 4–7 sa na ne neuplatňujú. Neprepisujeme ich ani nevraciame do generátora. Robíme s nimi toto:

1. **Kontrola pred nasadením alebo hneď po ňom.** Najčastejšie ich človek nahodí sám a agent ich dohľadá cez Meta MCP (`ads_get_ad_entities` → `ads_get_creatives` → stiahnuť `image_url`). Agent skontroluje a človeku vypíše:
   - fakty a ceny voči `product-facts.md` a `chyby-neopakovat.md` (cena pre daný trh, záruka, doprava, zakázané tvrdenia),
   - súlad obrázka, nadpisu, primárneho textu, CTA a **cieľovej URL** (rovnaký produkt, rovnaká cena),
   - formát voči umiestneniam: jeden obrázok 9:16 Meta vo Feede oreže na 4:5 a jeden 4:5 v Stories/Reels doplní pruhmi. Text pri okrajoch tak môže vypadnúť. **`ads_get_creatives` pri reklame s obrázkom podľa umiestnenia vracia iba jeden `image_hash`.** Pred záverom „chýba formát“ nájdi v `ads_get_ad_images` súbory s rovnakým názvom (napr. `3.png_105` 1080×1350 aj 1080×1920) a skontroluj každý formát zvlášť, lebo sa môžu líšiť (klient 2026-10-02: CTA zlé iba v 9:16),
   - logo a čitateľnosť textu.

   Chyby v obrázku opravuje klient novým exportom. Chyby v texte či URL navrhne agent ako zmenu, ktorú vykoná človek alebo agent až po výslovnom súhlase. Klientovu kreatívu nehodnotíme skóre agentov 01–08 a výnimky cez `workflow_gate.py` sa jej netýkajú.
2. **Uloženie.** Súbor patrí do `brands/{brand}/products/{produkt}/client-creatives/{YYYY-MM-DD}/` s prefixom `K01`, `K02`… (kategória je pseudo-produkt). Do `product-image-ads/` ani `outputs/` ho nedávaj.
3. **Tracker.** Každá klientova reklama má riadok s `Plan ID = KLIENT-{YYYY-MM-DD}`, `Concept ID = K01…`, Avatar `— (klient)`, Meta Ad ID a Adset ID a SHA súboru. Angle a typ hooku zaraď spätne podľa toho, čo kreatíva skutočne komunikuje, aby sa dala porovnávať s našimi.
4. **Izolácia testov.** Ak klientova reklama pribudne do ad setu s bežiacim B1 testom, test od toho dňa nie je izolovaný. Zapíš to do trackera a v Režime C čítaj obdobia pred a po pridaní zvlášť. Ak je to možné, navrhni človeku pre klientove kreatívy samostatný ad set.
5. **Vyhodnotenie.** Režim C a D ich hodnotí rovnako ako naše. Poznatok z nich ide do `learnings.md` s poznámkou, že nevznikol z plánovanej hypotézy (dôveryhodnosť najviac „Predbežná“). Víťazný klientov koncept môže byť vstupom pre ďalší B1 plán; jeho iterácia už ide celým workflowom.

## Krok 9 — Vyhodnotenie a učenie (C + D)

Režim C čaká na dátovú bránu z plánu a až potom rozhodne: škálovať, iterovať, vypnúť alebo počkať. Režim D sleduje fatigue a navrhuje rotáciu. Primárna klikacia metrika je **outbound CTR** (`outbound_clicks_ctr`); link CTR sa uvádza osobitne a video metriky sú pri statikoch N/A.

Verdikt je odporúčanie, nie vykonaná akcia. Stĺpec **Stav** v trackeri mení až potvrdená zmena v účte (človek ju vykonal alebo ju overil `effective_status` cez MCP).

Learning zapisuj do `brands/{brand}/testing/learnings.md` s ID (L001…); fatigue do `fatigue.md`. Ďalší B1 plán tieto ID načíta a zapíše do `learnings.applied`. Diagnóza určuje miesto návratu:

- chybná persona/pain → krok 2,
- slabý angle alebo hook → krok 3 a nový B1,
- nečistý experiment → krok 4,
- slabé prevedenie copy/template → krok 5,
- render chyba → krok 7.

## Lokalizácia

Rozlišuj tri veci: **jazyk** (prompts-{lang}.json), **trh** (`market` v pláne) a **menu**. Samostatná vetva klienta pre iný trh (napr. CZ e-shop s vlastnou ponukou, cenami a oslovením) má vlastný research/offer-brief, vlastný plán s `market` daného trhu a zdrojový `prompts-{lang}.json` s plným scoringom 01–08.

Preklad schváleného zdroja má vlastný `prompts-{lang}.json` s poľom `"source_prompts": "prompts-sk.json"`, vlastný scoring a approval. Brief a template sú zamknuté na zdroj; `test-plan.json` ostáva rovnaký, iba ak sa nemení ponuka. Pri inom trhu v B1 výslovne rozhodni, či stačí existujúci plán (rovnaká ponuka, potvrdená cena), alebo treba nový. A1–A3 sa pri čistom preklade nereinterpretujú; opakujú sa kontroly 04–08:

```bash
python3 07-image-generation/workflow_gate.py init-scoring \
  --prompts path/to/prompts-hu.json --mode translation
```

Prekladový scoring si zapíše SHA-256 zdroja. Preklad (`source_prompts`) platí iba vtedy, keď má zdroj kompletný scoring 01–08 aj ľudský approval a od prekladu sa nezmenil — a to aj keď preklad dostane plný scoring 01–08. Oslovenie (tykanie/vykanie) sa preberá z brand-dna daného klienta a trhu, nie z univerzálneho pravidla.

Cenu pre iný trh nikdy automaticky neprepočítavaj. Pri preklade alebo keď jazyk nesedí s `market` plánu musí cenu potvrdiť človek a `approval-{lang}.json` musí mať `market_prices_confirmed=true`, čo zapíše prepínač `--market-prices-confirmed`.

Hotový banner môžeš namiesto nového renderu preložiť cez `BONUS/03-image-translator/translate_ads.py`. Skript nič neprekladá sám: prenesie do obrázka iba schválené texty z `prompts-{lang}.json` a prejde rovnakými bránami (scoring, approval, zdroj, ceny). Vstupný PNG musí byť v manifeste s aktuálnym hashom, musí vzniknúť z aktuálneho schváleného zdroja a mať vizuálny PASS v exporte z dashboardu (`--qa-export creative-qa.json`). Každé copy pole musí mať pár v oboch smeroch, inak by v obrázku ostal pôvodný text. Výstup ide do `outputs-{lang}/` a zobrazí sa v dashboarde.

## Dashboard a bonusy

Dashboard je pomocný pracovný priestor, nie workflow krok:

```bash
python3 tools/dashboard/build_dashboard.py
```

Vo vytvorenom `dashboard.html` máš dve záložky. **Creative QA** filtruje hotové bannery, otvára detail, porovnáva 2–4 varianty a ukladá verdikt PASS / Drobná oprava / FAIL s poznámkou. **Template knižnica** zobrazuje globálne aj klientské wireframy, voliteľné Gemini specimen rendery a upozorňuje, keď náhľad po zmene template-u nesedí na jeho SHA-256. QA verdikt sa viaže na SHA-256 konkrétneho PNG; zmenený alebo chýbajúci súbor aj staré hodnotenie bez hashu majú stav **Prehodnotiť** (pôvodný verdikt ostane v detaile ako história). QA stav zostáva v prehliadači, kým ho neexportuješ do `creative-qa.json` (export obsahuje posúdený aj aktuálny hash); dashboard ani export nemenia `test-plan.json`, prompty, scoring ani approval.

Rozšírenia sú v `BONUS/`: multiply, animácia statiku, image translator, copy translator a video concepts. Animácie a videá patria do `products/{produkt}/animations/`; verné produktové video vzniká image-to-video z čistej fotky na bielom pozadí (detail v `BONUS/05-video-concepts/README.md`). Nesmú obísť strategický plán, scoring ani approval; image translator tieto brány vynucuje sám.

## Znalostná databáza (references)

`references/` zbiera poznatky z článkov, Meta dokumentácie a case studies, ktoré nie sú viazané na klienta. Pošli agentovi URL s pokynom „ulož do references“. Agent uloží zdroj do `references/meta/sources/YYYY-MM-DD-zdroj-tema.md`, zlúči poznatky do destilátu `meta-<tema>-tactics.md` a aktualizuje index `references/meta/README.md`.

Meta Ads Manager destiláty číta sám pri režimoch S, E, A, B1, C a D. Sú to odporúčania, nie pravidlá. Brány, metodika skillov a vlastné dáta klienta (`learnings.md`) majú prednosť. Ak článok protirečí metodike skillu, agent to povie a skill zmení iba so súhlasom človeka. Priečinok je v Gite, preto doň nepatria klientské dáta ani celé články. Detail je v `references/README.md`.

## Bezpečnosť a Git

- `brands/*` je lokálne a ignorované Gitom; klientské dáta necommituj ani cez `git add -f`.
- Ak chceš začať s klientom nanovo, po zálohe odstráň iba `brands/{brand}/`, nie celý repozitár.
- API kľúče patria iba do `.env`.
- Nemaž `outputs/` pri regenerácii.
- Bez explicitného súhlasu človeka nevykonávaj platené generovanie ani zmeny v reklamnom účte.

## Diagnostika

```bash
python3 -m unittest discover -s tests -v
python3 04-test-planning/test_plan.py validate --plan path/to/test-plan.json
python3 07-image-generation/generate_ads.py --brand-dir path/to/ad-set --lang sk --validate-only
```

Šablóna `04-test-planning/test-plan-template.json` má zámerne `status: draft`, takže sama validáciou neprejde.

Ak validácia zlyhá, oprav prvú príčinu a spusti ju znova. Brány neobchádzaj ručným prepisovaním hashov.
