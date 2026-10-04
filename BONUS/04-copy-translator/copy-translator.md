# BONUS 04 — Copy Translator (Claude Code / Codex workflow)

Workflow na preklad copy fields zo **schváleného** zdrojového `prompts-{lang}.json` (zvyčajne `prompts-sk.json`) do iných jazykov **priamo cez Claude Code alebo Codex** (nie cez samostatný prekladový skript). Output: `prompts-{target_lang}.json` na rovnakej úrovni v priečinku ad setu.

## Kedy ide o preklad a kedy nie

| Situácia | Postup |
|---|---|
| Rovnaká ponuka a koncept, iný jazyk | **Preklad** podľa tohto návodu (`source_prompts`, scoring 04–08) |
| Iný trh s vlastnou ponukou, cenami, oslovením alebo sortimentom (napr. samostatná CZ vetva klienta) | **Nie je preklad.** Vlastný research/offer-brief, vlastný `test-plan.json` s `market` trhu a zdrojový `prompts-{lang}.json` s plným scoringom 01–08 |
| Rovnaký koncept, iný trh, ponuka sa mení len v cene | Rozhodni v B1, či stačí existujúci plán; cenu potvrdí lokálny človek (`--market-prices-confirmed`) |

## Filozofia

Text-first preklad — prekladajú sa **len copy fields** (headline, subhead, cta, bullets, reviews…), nie hotový obrázok. Po preklade vznikne `prompts-{lang}.json`, z ktorého:

- `generate_ads.py --lang {lang}` vyrobí nový obrázok v cieľovom jazyku, alebo
- `BONUS/03-image-translator/translate_ads.py` prenesie schválené texty do už hotového, vizuálne schváleného banneru (keď má vizuál ostať identický naprieč jazykmi).

V oboch prípadoch sa do obrázka dostane iba text, ktorý prešiel jazykovým scoringom a ľudským schválením. Lokálny review prebieha na texte — rýchlo a bez platených renderov.

**Prečo coding agent direct (nie kampaňovo špecifický API skript):**
- Agent má naraz preklad, brand pravidlá, brief aj zdrojový research
- Konzistentnosť naprieč 8+ promptmi (jedna pracovná pamäť)
- Brand glossary + brief sú v kontexte vždy
- Iterácie sú instant (žiadny API roundtrip)
- Žiadne dodatočné API náklady

## Podmienka pred prekladom

Zdrojový `prompts-{src}.json` musí mať kompletný scoring 01–08 (`scoring-{src}.json`, `status: passed`) aj ľudský `approval-{src}.json` pre presné bajty súboru. Neschválený zdroj neprekladaj — generátor aj image translator by preklad aj tak zablokovali.

## Vstupy

```
brands/{brand}/products/{product}/product-image-ads/{ad-set}/prompts-sk.json   # schválený zdroj
  ├── brief                                         ← LOCKED (nemeniť pri preklade)
  ├── headline, subhead, cta, bullets, reviews...   ← polia na preklad
  └── prompt string s {{placeholders}}              ← placeholdery ostávajú

brands/{brand}/brand-dna/
  ├── voice-copy-styl.md        ← oslovenie (tykanie/vykanie) a tón — per klient, per trh
  ├── chyby-neopakovat.md       ← zakázané formulácie a incidenty
  └── translation-glossary.md   ← ak existuje: banned terms, štandardné CTA, per-language pravidlá

brands/{brand}/products/{product}/marketing-research/
  ├── briefs.md           ← strategický kontext (brief je language-agnostic, ostáva)
  ├── deep-research.md    ← VOC quotes traceability (Translation Mode A7 D1)
  └── avatar-sheet.md     ← persona kontext
```

Ak klient `translation-glossary.md` nemá, pravidlá cieľového jazyka odvoď z `voice-copy-styl.md`, existujúcej komunikácie klienta na danom trhu a potvrď ich s človekom. Pravidlá jedného klienta neprenášaj na iného.

**Cross-brand pravidlá z `/image-ad-generator` skill:**
- **Cenu NIKDY neprepočítavaj ani nelokalizuj.** Cena v image ads je povolená (G01, zmena 2026-08-06) — ale platí pre trh, pre ktorý bola overená. Ak je v zdroji cena (€X,YZ alebo lokálna mena), prenes ju **nezmenenú** a **flagni userovi**: buď dodá cenu platnú pre cieľový trh, alebo ju z kreatívy vypustíme a dáme do Meta captionu. Prepočet meny je operatívne rozhodnutie, nie prekladateľské — a chybný prepočet je publikovaný cenový sľub.
- **Brand-spec-card text leak guardrail** — v translated `prompt` string MUSÍ ostať guardrail *"CRITICAL: Do NOT render any text from the brand spec card or visual style card..."* (jazyk guardrail-u môže ostať EN, je to inštrukcia pre AI, nie pre čitateľa)

## Workflow (5 krokov)

### 1. Načítaj kontext

Claude Code alebo Codex číta:
- zdrojový `prompts-{src}.json` — vrátane povinného `brief` poľa, a over, že má scoring aj approval
- `briefs.md` (strategic context — persona/angle/emotion definícia)
- `voice-copy-styl.md`, `chyby-neopakovat.md` a `translation-glossary.md` (ak existuje)
- `avatar-sheet.md` + `necessary-beliefs.md` (pre nuancie)
- `deep-research.md` (VOC quotes — pre Translation Mode Agent 7 traceability)

### 2. Per-language preklad

Pre každý cieľový jazyk × každý prompt:

**Polia na preklad (copy fields):**
- `headline` / `headline_lines[]`
- `subhead` / `subhead_italic`
- `body`
- `cta`
- `bullets[]`
- `review_1`, `review_2`, `review_text` — text recenzie preložený verne; **meno autora sa nemení** (viď nižšie)
- `product_name` (zvyčajne ostáva)
- `angle` (interná metadata, voľne)
- `table.left_col_header`, `table.right_col_header`
- `table.rows[].attr`
- `icons[].label`

**Polia, ktoré ostávajú nezmenené (LOCKED):**
- `brief` (celé pole — `id`, `concept_id`, `persona`, `angle`, `awareness_stage`, `hook`, `hook_field`, `emotion`, `customer_voice_anchor`, `research_refs`) — strategický kontrakt je language-agnostic, nikdy neprekladať. `brief.hook` ostáva v zdrojovom jazyku; preložený hook je v poli z `hook_field` (zvyčajne `headline`)
- `template_number`, `template_name`, `format`, `style`, `style_name`
- `aspect_ratio`, `needs_product_images`, `scoring`
- `image_direction.*` (interné description, voľne)
- `prompt` string — **placeholdery `{{...}}` ostávajú** — runtime substitúcia v generate_ads.py
- `workflow_version` a `test_plan` — skopíruj zo zdroja (alebo spusti `test_plan.py bind --prompts prompts-{lang}.json`)
- Numerické hodnoty (`30+`, `4,9/5`, `0,44 mg`)
- Brand mená a názvy produktových radov klienta
- Vedecké termíny (Omega-3, EPA, DHA, vitamín B6, mg)

**Recenzie a mená autorov.** Recenzia skutočného zákazníka patrí jeho autorovi. Meno nenahrádzaj „lokálnym“ menom — vznikla by recenzia, ktorú nikto nenapísal (klamlivá reklama, v EÚ zakázané falošné recenzie). Možnosti:
1. použi skutočnú recenziu z cieľového trhu (preferované),
2. prelož text a ponechaj pôvodné meno/iniciály autora,
3. recenziu v cieľovom jazyku vynechaj a nahraď iným overeným dôkazom.

**KRITICKÉ — prompt body sync (lessons learned z B12 multiply 2026-05-06):**

Substitution engine v `generate_ads.py` zvláda top-level polia (`{{headline}}`, `{{subhead}}`, `{{cta}}`, `{{body}}`) **aj bodkovú notáciu vrátane indexov poľa** — `{{table.left_col_header}}`, `{{table.rows.0.right}}`, `{{icons.0.value}}` fungujú (`resolve_path()`).

Jediná notácia, ktorá **nefunguje**, je hranatá: `{{bullets[0]}}` → píš `{{bullets.0}}`.

Pri preklade ad-u, kde `prompt` body obsahuje **literal hardcoded text** zo zdrojového jazyka (napr. inštrukcia *"first line 'Medovka. Harmanček.' runs medium weight"*), MUSÍŠ tento literal text v prompt body **tiež preložiť** (resp. nahradiť target-language ekvivalentom). Inak AI dostane conflicting signal: `{{headline}}` placeholder (target-lang) vs hardcoded source-lang text v inštrukcii — niekedy renderuje source text namiesto translated headline. Hook samotný musí ísť cez placeholder — text hooku natvrdo v prompte generátor zablokuje.

**Heuristika:** po preklade `headline`/`subhead`/`bullets` greppni `prompt` string na source-language slová z týchto polí — ak nájdeš zhodu, prelož ich aj v prompt body. Lepšie: pri buildovaní zdrojového `prompts.json` písať prompt instructions agnosticky (*"render only the {{headline}} value, do not invent alternate text"*).

### 3. Aplikuj brand pravidlá cieľového jazyka

**Univerzálne (cross-language):**
- Brand mená a produktové rady klienta — nikdy nepreložiť
- Vedecké termíny — ostávajú
- Numerické hodnoty — ostávajú (čísla, ratios, percentá)
- **Oslovenie** (tykanie/vykanie, du/Sie, tu/vous, te/Ön…) — podľa `voice-copy-styl.md` klienta **pre daný trh**. Nie je univerzálne: jeden klient môže na SK tykať a na CZ vykať. Ak pravidlo pre cieľový trh chýba, spýtaj sa človeka.

**Per-language (z glossary alebo potvrdené s človekom):**
- **Banned terms** — slová, ktoré daný trh nepoužíva alebo majú negatívnu/regulátorom flagnutú konotáciu; každý klient a jazyk má vlastný set
- **Štandardná CTA** — z glossary klienta (orientačná tabuľka nižšie)
- **Decimal separator** — SK/CZ/HU/RO/DE: `0,44` | EN: `0.44`
- **Quotation marks** — SK/CZ/DE: `„..."` | EN: `"..."` | FR/IT: `«...»`
- **Anglicizmy + Latinizmy** — nahraď natívnym ekvivalentom, ak ho trh reálne používa

**Agent 4 (Brand Consistency) invocation pri Krok 4:**
Pri scoringu sa Agent 4 volá **s explicitným target-language kontextom**: *"Score Agent 4 against target language X, applying the client's rules for market X."* Dimenzia Vocabulary Alignment + Native Language sa overuje proti pravidlám cieľového trhu, nie proti SK zdroju.

### 4. Validácia (scoring v target-language mode)

Brief je locked (persona/angle/emotion language-agnostic, definované v `briefs.md` a zapísané v poli `brief`), takže Agenti 1–3 sa pri čistom preklade nereinterpretujú. Vocabulary a mechanika sa menia per-language → 5 agentov MUSÍ bežať.

```bash
python3 07-image-generation/workflow_gate.py init-scoring \
  --prompts brands/{brand}/products/{product}/product-image-ads/{ad-set}/prompts-hu.json \
  --mode translation
```

`--mode translation` vyžaduje v `prompts-{lang}.json` pole `"source_prompts": "prompts-sk.json"` a do scoringu zapíše SHA-256 zdroja (hash zdroja sa zapíše pri každom súbore so `source_prompts`, aj pri plnom scoringu). Ak sa zdroj po preklade zmení, prekladový scoring prestane platiť.

**Run agents (5 z 8):**
- **Agent 4 (Brand Consistency)** — vocabulary alignment + native syntax v target jazyku, banned terms per-market, oslovenie podľa pravidiel klienta pre trh
- **Agent 5 (Copy Excellence)** — rhythm / punch / surprise sa môžu stratiť v preklade; re-check
- **Agent 6 (Format Compliance)** — word counts varírujú per jazyk (DE typicky ~30 % dlhší než SK), kontrola fitu do template specs
- **Agent 7 (Fact-Check) v Translation Mode** — translator-side fidelity check: embellishment / numerical drift / pridané claimy / vymyslené metafory. Volá sa explicitne s flagom *"Run in Translation Mode"* — viď `06-quality-gates/07-agent-fact-check.md` sekcia "Translation Mode"
- **Agent 8 (Copy Editor)** — target-language mechanics: diakritika, decimal separator, currency format, banned chars (em-dash v headline), quotation marks per market

**Skip agents (3 z 8) — locked by brief:**
- **Agent 1 (Persona Fit)** — persona je v `brief.persona`, language-agnostic
- **Agent 2 (Angle Execution)** — angle je `brief.angle`, strategický kontrakt drží naprieč jazykmi
- **Agent 3 (Emotional Resonance)** — emotion je v `brief.emotion`; ak preklad zachová customer voice anchor, emotion drží

Threshold = 90 per agent. Ak ktorýkoľvek < 90 → iteruj preklad, nepokračuj do generovania. Potom človek schváli text:

```bash
python3 07-image-generation/workflow_gate.py approve \
  --prompts .../prompts-hu.json --by "Meno lokálneho schvaľovateľa" \
  --at "2026-09-11T14:30:00+02:00" --language hu [--market-prices-confirmed]
```

### 5. Output

Pre každý jazyk vznikne `prompts-{lang}.json`:

```json
{
  "brand": "Acme",
  "product": "Hero produkt",
  "language": "HU",
  "source_language": "SK",
  "source_prompts": "prompts-sk.json",
  "workflow_version": 2,
  "test_plan": {"id": "TP-2026-09-11-HOOKS", "sha256": "<rovnaké ako v prompts-sk.json>"},
  "translated_at": "2026-09-11",
  "translated_by": "coding agent + human review",
  "prompts": [
    {
      "template_number": 1,
      "template_name": "headline-template",
      "brief": {
        "id": "B01",
        "concept_id": "C01",
        "persona": "P1 — praktický zákazník",
        "angle": "Overená hodnota",
        "awareness_stage": "problem-aware",
        "hook": "Presný slovenský headline z plánu",
        "hook_field": "headline",
        "emotion": "istota",
        "customer_voice_anchor": "Chcem vedieť, čo kupujem."
      },
      "headline": "Pontos magyar címsor",
      "subhead": "…",
      "cta": "RENDELD MEG MOST",
      "prompt": "...HEADLINE: \"{{headline}}\"...",
      "aspect_ratio": "4:5"
    }
  ]
}
```

`brief` je 1:1 kópia zo zdroja (generátor to overí). JSON nesmie obsahovať komentáre.

## Štandardná CTA tabuľka (orientačná)

| SK CTA | CZ | HU | RO | DE | EN |
|--------|-----|-----|-----|-----|-----|
| OBJEDNAŤ TERAZ | OBJEDNEJ TEĎ | RENDELD MEG MOST | COMANDĂ ACUM | JETZT BESTELLEN | ORDER NOW |
| VYSKÚŠAŤ | VYZKOUŠEJ | PRÓBÁLD KI | ÎNCEARCĂ | JETZT TESTEN | TRY IT |
| ZISTIŤ VIAC | ZJISTI VÍC | TUDJ MEG TÖBBET | AFLĂ MAI MULT | MEHR ERFAHREN | LEARN MORE |
| VYBRAŤ BALENIE | VYBER BALENÍ | VÁLASSZ CSOMAGOT | ALEGE PACHETUL | PACKUNG WÄHLEN | CHOOSE PACKAGE |
| POROVNAŤ | POROVNEJ | HASONLÍTSD ÖSSZE | COMPARĂ | VERGLEICHEN | COMPARE |

Tabuľka je v tykacej forme. Pri klientovi, ktorý na danom trhu vyká, použi vykaciu formu (napr. CZ „OBJEDNEJTE", DE „JETZT BESTELLEN" ostáva neutrálne). Rozšír per klient a kampaň.

## Output location

Všetky jazykové súbory žijú **na jednej úrovni** v priečinku ad setu:

```
brands/{brand}/products/{product}/product-image-ads/{ad-set}/
├── prompts-sk.json    # schválený zdroj
├── scoring-sk.json / approval-sk.json
├── prompts-hu.json    # preklad (source_prompts: prompts-sk.json)
├── scoring-hu.json / approval-hu.json
└── ... (per cieľový jazyk)
```

Po generovaní pribudnú `outputs-{lang}/` priečinky s obrázkami.

## Po preklade — obrázky per jazyk

Najprv bezplatná validácia, potom generovanie až po výslovnom „generuj“:

```bash
python3 07-image-generation/generate_ads.py \
  --brand-dir brands/{brand}/products/{product}/product-image-ads/{ad-set} \
  --lang hu --validate-only

python3 07-image-generation/generate_ads.py \
  --brand-dir brands/{brand}/products/{product}/product-image-ads/{ad-set} \
  --lang hu --provider google
```

`--lang hu` nájde `prompts-hu.json`, `scoring-hu.json`, `approval-hu.json` a výstup zapíše do `outputs-hu/`. Pri `--prompts-file prompts-hu.json` sa jazyk odvodí z názvu súboru. Default provider je `google`; `google-batch` použi iba na výslovný pokyn (väčší neurgentný beh).

Alternatíva pri vizuálne schválenom zdrojovom banneri — prenos schváleného textu do hotového obrázka:

```bash
python3 BONUS/03-image-translator/translate_ads.py \
  --image brands/{brand}/products/{product}/product-image-ads/{ad-set}/outputs/01-headline-template-C01/headline-template_v1_img1.png \
  --languages hu --qa-export path/to/creative-qa.json --dry-run
```

## Local team review workflow (recommended)

1. **Agent preloží** → vznikne `prompts-{lang}.json`
2. **Pošli copy fields** lokálnemu tímu (alebo extrakt do Google Sheet)
3. **Lokálny tím reviewuje TEXT** (rýchle, lacné — žiadne obrázky zatiaľ)
4. **Scoring 04–08 + `approve`** s menom lokálneho schvaľovateľa
5. **Až potom** `--validate-only` a generovanie / image translator — opravy sa robia na texte pred renderom

## Pravidlá

- **Vždy** prekladaj iba zo zdroja so scoringom 01–08 a ľudským approvalom
- **Vždy** pred prekladom prečítaj `voice-copy-styl.md`, `chyby-neopakovat.md`, glossary (ak existuje) a `briefs.md`
- **Vždy** použi oslovenie podľa pravidiel klienta pre cieľový trh — nikdy univerzálne tykanie
- **Nikdy** nemeň meno autora skutočnej recenzie; použi recenziu z cieľového trhu, ponechaj pôvodné meno alebo recenziu vynechaj
- **Vždy** preserve `brief` field 1:1 (LOCKED — language-agnostic strategic contract)
- **Vždy** doplň `"source_prompts"` a skopíruj `workflow_version` + `test_plan` zo zdroja
- **Vždy** synchronizuj literal hardcoded text v `prompt` body s preloženými copy fields (lessons learned: B12 multiply prompt sync incident)
- **Vždy** zachovaj brand-spec-card text leak guardrail v translated `prompt` (jazyk guardrail-u môže ostať EN — je to inštrukcia pre AI)
- **Nikdy** neprekladaj brand mená, vedecké termíny, numerické hodnoty
- **Nikdy** nemeň `prompt` string `{{placeholders}}` — substitúcia runtime
- **Nikdy** neprepočítavaj ceny / nemeň menu — cenu prenes nezmenenú a flagni userovi. Lokálny človek musí potvrdiť cenu pre cieľový trh cez `approval-{lang}.json` (`market_prices_confirmed: true`).
- **Dot-notation funguje** (`{{table.left_col_header}}`, `{{icons.0.value}}`) — nefunguje len hranatá notácia `{{bullets[0]}}`, píš `{{bullets.0}}`
- **Vždy** spusti scoring agentov 4–8 (5 z 8) cez `init-scoring --mode translation` pred generovaním — Agent 7 explicitne s flagom "Translation Mode" (viď `06-quality-gates/07-agent-fact-check.md`)
- Pri konflikte glossary vs. kontext → glossary klienta vyhráva (brand consistency > elegancia prekladu)
