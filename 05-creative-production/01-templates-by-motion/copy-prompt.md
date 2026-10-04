# Copy Generation — Motion Templates

Návod na písanie copy pre Motion Foundations recipe cards (krok 5 workflow).

## Vstup

**Brief** (krok 5a — vyberá sa PRVÝ, pred templatom aj copy):
- `brands/{brand}/products/{product}/marketing-research/briefs.md` — zamkne persona × angle (belief a/alebo CEP) × emócia × voice anchor × best formats
- `brands/{brand}/products/{product}/marketing-research/cep-sheet.md` — situačná os briefov (ak existuje)

**Copy polia** (headline, subhead, cta):
- `brands/{brand}/products/{product}/marketing-research/avatar-sheet.md` — jazyk zákazníka, pain points, citáty
- `brands/{brand}/products/{product}/marketing-research/necessary-beliefs.md` — North Star pre každý kus copy
- `brands/{brand}/products/{product}/marketing-research/deep-research.md` — overené claims, specs, diferenciátory

**Image direction** (background, lighting, farby, typografia, product position):
- `brands/{brand}/brand-dna/brand-research-brief.json` — visual_system, primary_color_hex, brand colors
- `brands/{brand}/brand-dna/brand-spec-card.html` — typografia, logo, CTA štýl
- `brands/{brand}/brand-dna/visual-style-card.html` — photography direction, mood, always/never rules

**Template:**
- Vybraný recipe card (napr. `01-headline-template.md`) — variation vectors pre image direction

## Proces

### 1. Načítaj template

Otvor vybraný recipe card. Identifikuj:
- Ktorý štýl (A / B / C) sa použije
- Copy template pre daný štýl (headline / subhead / CTA)
- Word counts pre každý element
- Image direction a variation vectors

### 2. Napíš copy

Pre každý copy element dodržuj word count z template:
- **Headline** — presný počet slov, jedna myšlienka, musí fungovať aj bez vizuálu
- **Subhead** — pridáva novú dimenziu (dôkaz, špecifikum, urgencia) — neopakuje headline
- **CTA** — 2–5 slov

**Pravidlá:**
- Použi jazyk zákazníka z `avatar-sheet.md` (Direct Client Quotes sekcia) — nie marketingový žargón
- Claims musia byť overené z `deep-research.md` alebo `brand-research-brief.json` — nikdy vymyslené
- Beliefs z `necessary-beliefs.md` sú North Star — copy musí viesť k nim
- Žiadne em dash (—), en dash (–), bodkočiarky v renderovanom texte

### 3. Vyber variation

Z variation vectors v template vyber konkrétne hodnoty. Dáta ber z:

| Hodnota | Zdroj |
|---------|-------|
| Background | `brand-research-brief.json` → visual_system + variation vectors z template |
| Lighting | `visual-style-card.html` → photography direction |
| Product position | variation vectors z template |
| Farby | `brand-research-brief.json` → primary_color_hex, secondary_color_hex |
| Typografia | `brand-spec-card.html` → headline font, weights, colors |
| Focal length | variation vectors z template |
| Energy / mood | `visual-style-card.html` → mood + variation vectors z template |

### 4. Zostav JSON output

Výstup musí byť vždy platný JSON — súbor `prompts-{lang}.json` (default `prompts-sk.json`) v priečinku ad setu. Copy polia sú **single source of truth**; prompt string odkazuje na ne cez `{{placeholder}}`, nikdy neobsahuje text natvrdo.

Štruktúra súboru je **obálka + pole `prompts`** — `generate_ads.py` číta presne toto:

```json
{
  "workflow_version": 2,
  "brand": "[názov brandu]",
  "product": "[názov produktu]",
  "test_plan": {
    "id": "[plan_id z test-plan.json]",
    "sha256": "[doplní 04-test-planning/test_plan.py bind]"
  },
  "prompts": [
    {
      "template_number": 13,
      "template_name": "[slug formátu, napr. stat-surround-product-hero]",
      "aspect_ratio": "[napr. 4:5]",
      "needs_product_images": true,
      "brief": {
        "id": "[napr. B03]",
        "persona": "[segment z briefu]",
        "angle": "[Belief # a/alebo CEP #]",
        "emotion": "[cieľová emócia]",
        "customer_voice_anchor": "[citát/formulácia zákazníka]",
        "concept_id": "[presné concept_id z test-plan.json]",
        "awareness_stage": "[unaware/problem-aware/solution-aware/product-aware/most-aware]",
        "hook": "[presný plánovaný hook alebo headline]"
      },
      "headline": "[text]",
      "subhead": "[text alebo null]",
      "cta": "[text alebo null]",
      "image_direction": {
        "background": "[voľba z variation vectors]",
        "product_position": "[voľba]",
        "lighting": "[voľba]",
        "focal_length": "[voľba]",
        "energy": "[voľba]"
      },
      "prompt": "[kompletný image generation prompt z recipe card s {{headline}}, {{subhead}}, {{cta}} namiesto hardcoded textu]"
    }
  ]
}
```

**Povinné polia — bez nich beh spadne alebo scoring nemá o čo oprieť:**

| Pole | Prečo je povinné |
|---|---|
| `template_number` | `generate_ads.py` ho číta priamo (`prompt_entry["template_number"]`) — bez neho `KeyError`. Zároveň ho používa `--templates` filter. |
| `template_name` | Označuje použitý formát. Viac hookov môže mať rovnaký `template_number` aj `template_name`; generátor pridá do výstupného priečinka `brief.concept_id` (napr. `01-headline-template-C02`). **Nikdy `/` v hodnote** — skript ho síce normalizuje na `-`, ale názov si radšej sluguj sám. |
| `brief` | Agenti 1 (persona), 2 (angle) a 3 (emócia) skórujú copy **proti tomuto objektu**. Bez neho nemajú kontrakt a ich skóre je bezcenné. Je to zároveň jediné miesto, kde je vidieť, z ktorého briefu kreatíva vznikla. |
| `prompt` | Vlastný image prompt. Alternatíva `ai_prompt` (hybrid mód s `product_placement`) sa používa len pri kompozitnom generovaní. |

**Workflow v2:** `test-plan.json` musí vzniknúť v kroku 4 ešte pred copy. Po dokončení JSON spusti `python3 04-test-planning/test_plan.py bind --prompts <cesta>`. Generátor potom overí hash plánu, úplné pokrytie variantov 1:1 a zhodu `brief.id`, `persona`, `angle`, `concept_id`, `awareness_stage`, `hook` a voliteľného `template_number` s plánovaným variantom. `concept_id` je stabilná identita kreatívy aj vtedy, keď viac hookov používa rovnakú šablónu. Nové ad sety sa bez tejto väzby nevytvárajú.

**Ďalšie copy polia** (`body`, `bullets`, `headline_lines`, `icons`, `table.rows`, `review_text`, `reviewer`, `rating`, `product_name`, `callouts`) pridaj podľa toho, čo template vyžaduje. Substitúcia je generická — akékoľvek pole v entry sa dá zavolať ako `{{pole}}`, vnorené cez bodkovú notáciu (`{{table.rows.0.left}}`, `{{icons.0.value}}`).

⚠️ **Podmienené polia neexistujú.** Ak je `{{pole}}` v prompt stringu, musí byť v JSON prítomné — nevyriešený placeholder je fatálna chyba pre-flightu. Formát s voliteľným blokom (napr. cenový blok) rieš tak, že pri builde **vynecháš celý riadok promptu**, nie tak, že vynecháš pole.

**Pravidlo pre prompt string:** Vezmi image generation prompt z recipe card pre daný štýl. Všetkých 40 templatov používa pre runtime copy polia `{{}}` syntax — copy-paste do prompt stringu **bez transformácie**. Okrem bežných (`{{headline}}`, `{{subhead}}`, `{{cta}}`, `{{body}}`, `{{review_text}}`, `{{reviewer}}`, `{{rating}}`) majú niektoré formáty vlastné polia — napr. `{{bubble_1..5}}` (32), `{{postit_1..4}}` + `{{caption}}` (40), `{{before_label}}` / `{{after_label}}` (08, 36), `{{platform_details}}` (29), `{{table.rows.N.left/right}}` (31). Pozri copy template daného recipe cardu.

Ostatné `[BRACKETED]` hodnoty (BRAND NAME, PRODUCT NAME, ASPECT RATIO, SAFE ZONES, BRAND COLOR, variation values atď.) vyplň priamo z brand-research-brief.json + format spec. **Žiadny `[BRACKETED]` token nesmie zostať v `prompt` stringu** — pre-flight na to padá.

⚠️ **Odkaz na referenčnú fotku je povinný, keď `needs_product_images` je `true`.** Prompt string musí obsahovať aspoň jednu z fráz `reference image`, `shown in the reference`, `reproduce it exactly`, `reproduce the product exactly` — inak pre-flight spadne na `✗ Chýba 'reference image' v N template(och)`. Pozor: `needs_product_images` **defaultuje na `true`**, takže pole chýbajúce v JSON sa počíta ako `true`.

Pri kopírovaní promptu z recipe cardu sa to rieši samo — 36 zo 40 templatov frázu už obsahuje. Zvyšné štyri (20, 29, 33, 39) ju nemajú, lebo majú `needs_product_images: false`. Ak píšeš prompt ručne alebo skracuješ ten z cardu, frázu nevynechaj.

**Konvencia:**
- `{{x}}` = runtime substitúcia z copy fields (generate_ads.py to nahradí)
- `[X]` = build-time fill (Claude vyplňuje pri builde)

**KRITICKÉ — žiadne sample copy texty v prompt body (language-agnostic):**

Prompt string MUSÍ ostať jazykovo-neutrálny. NIKDY nevkladaj konkrétne hodnoty z `headline` / `subhead` / `cta` / `bullets` polí do prompt instructions ako "ukážku" alebo "popis layoutu". AI dostane konfliktný signál (placeholder + hardcoded sample) a niekedy renderuje hardcoded sample namiesto preloženého placeholderu.

❌ Anti-pattern: `HEADLINE: "{{headline}}" — first line "Bez ospalosti." runs medium, second "Bez závislosti." heavier.`

✅ Správny pattern: `HEADLINE: "{{headline}}" — first line medium weight, second line heavier (split on newline character in {{headline}} value). Render ONLY the {{headline}} value — do not invent or substitute alternate text.`

Layout descriptions (font weight, position, color, line count) sú OK. Konkrétne sample texty z copy fields sú NIKDY OK. Pravidlo: pred uložením `prompts-{lang}.json` (default `prompts-sk.json` pre SK source) greppni prompt body na slová z copy fields → ak nájdeš match → refactor.

JSON ide priamo do kroku 5 (Scoring) — Agent 07 číta len copy polia, prompt string neotvára.
