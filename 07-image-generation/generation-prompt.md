# Step 7 — Image Generation Prompt Template

Vezme finálny prompt string z kroku 5, ktorý prešiel kontrolami v kroku 6, a odošle ho do generátora spolu s reference images.

## When to use

After:
- [x] Krok 1 — Brand foundation je hotový vrátane oboch brand cards
- [x] Krok 2 — Strategický research obsahuje persony, pains, angles, `briefs.md` a `product-facts.md`
- [x] Krok 3 — Meta Ads Manager pripravil konkrétne koncepty (avatar, angle, awareness, hook, formát)
- [x] Krok 4 — `test-plan.json` je validný a stav je `planned`
- [x] Krok 5 — Copy je v `prompts-{lang}.json` workflow v2 a je hashovo previazané s plánom
- [x] Krok 6 — Agenti 01–07 ≥90 + PASS, Agent 08 PASS; scoring sedí hashom
- [x] Krok 6 — Človek schválil copy a existuje hash-bound `approval-{lang}.json`
- [x] Produktové fotografie a obe brand cards sú pripravené

## 10 universal rules (enforced in every generation prompt)

Every generated prompt must include these rules verbatim so the generator respects them:

1. **Exact dimensions:** 1080x1920 pixels, 9:16 vertical aspect ratio (unless format template specifies otherwise — 4:5 = 1080x1350, 1:1 = 1080x1080).
2. **One continuous image.** No panels, borders, split frames, grid lines, collages, or multi-cell compositions. The image fills the entire frame edge to edge.
3. **All copy rendered verbatim in the image.** Every word from the approved brief appears exactly as written — no paraphrasing, no extra words, no missing words.
4. **No text smaller than 24px** at 1080px width. Fine print must still be legible.
5. **Sufficient contrast** between text and background. If the background behind text is busy or low-contrast, use a subtle text treatment (slight shadow or semi-transparent backing) rather than heavy graphic overlays.
6. **Photorealistic product representation.** Reproduce the product EXACTLY as it appears in the uploaded product reference image — do not invent, alter, or idealize shape, color, labels, typography, or design details.
7. **Safe zones respected:** pri 9:16 nechaj horných ~12 % a dolných ~28 % bez textu a kritických prvkov; pri feed formátoch zachovaj bezpečné okraje templatu.
8. **No em dashes (—), en dashes (–), or semicolons** in any rendered copy.
9. **Every data point appears once.** No duplicate prices, stats, claims, or badges across elements.
10. **Brand fingerprint dominates.** Final output must look like this brand's ad — typography, colors, photography direction all sourced from the brand spec card and visual style card, not from generic stock conventions.

## Reference upload checklist

Before sending the prompt to Nano Banana 2 / fal.ai, upload:

- [ ] **Brand Spec Card** (PNG) — `brands/{brand}/brand-dna/brand-spec-card.png`
- [ ] **Visual Style Card** (PNG) — `brands/{brand}/brand-dna/visual-style-card.png`
- [ ] **Logo reference** (transparentné PNG, ak existuje) — `logo.png`, prípadne `logo-white.png`; SVG zostáva master a image API ho nedostáva
- [ ] **Product photo** — authoritative reference for product visual

## Generation prompt template

```
Create a static ad for [BRAND NAME]'s [PRODUCT NAME].

DIMENSIONS: [1080x1920, 9:16 vertical] — [or 1080x1350 4:5 / 1080x1080 1:1 per format template].

REFERENCE IMAGES (uploaded):
1. Brand Spec Card — authoritative source for fonts, colors, logo, CTA styling, typography rules
2. Visual Style Card — authoritative source for photography direction, mood, product styling, always/never rules
3. Optional standalone logo reference(s) — reproduce the official mark exactly when the composition calls for a logo
4. Product photo — reproduce the product EXACTLY as shown; do not invent or alter shape, color, labels, or design

COPY (render verbatim in the image):
[Vložiť finálny prompt string z kroku 5, schválený v kroku 6 — všetky {{placeholdery}} sú už nahradené]

UNIVERSAL RULES (enforce all):
1. Exact dimensions [1080x1920 / 1080x1350 / 1080x1080].
2. One continuous image — no panels, borders, split frames, grid lines, or collages.
3. All copy rendered verbatim — no paraphrasing, no extras.
4. No text smaller than 24px at 1080px width.
5. Sufficient contrast between text and background.
6. Photorealistic product per uploaded reference — do not alter shape, color, labels, or design.
7. Apply format-appropriate safe zones; for 9:16 keep top ~12% and bottom ~28% clear of text and critical content.
8. No em dashes (—), en dashes (–), or semicolons in rendered copy.
9. Every data point appears exactly once.
10. Output must look like [BRAND]'s ad — brand fingerprint dominates generic ad conventions.
```

## Execution

Generovanie prebieha cez centrálny skript `07-image-generation/generate_ads.py` z koreňa repozitára.

```bash
python3 07-image-generation/generate_ads.py \
  --brand-dir brands/{brand}/products/{product}/product-image-ads/{ad-set} \
  --lang sk --provider google --resolution 1K
```

Pred plateným behom:

```bash
python3 07-image-generation/generate_ads.py \
  --brand-dir brands/{brand}/products/{product}/product-image-ads/{ad-set} \
  --lang sk --validate-only
```

Pri starom ad sete bez `workflow_version: 2` alebo so starým plánom `schema_version: 1` je dostupný explicitný prepínač `--allow-legacy`. Nepoužívaj ho pri novom ad sete ani na obídenie chýbajúceho `test-plan.json`.

### Performance Max rozmery zo schválených Meta bannerov

PMax je iba voliteľný rozmerový export toho istého schváleného konceptu a copy. Nepotrebuje nový research ani test plán. Prepínač nepouži automaticky: vyžaduje výslovnú požiadavku človeka na PMax alebo Google Ads bannery.

```bash
python3 07-image-generation/generate_ads.py \
  --brand-dir brands/{brand}/products/{product}/product-image-ads/{ad-set} \
  --lang sk --provider google --resolution 1K --pmax
```

Výsledkom sú rekomponované varianty `1200×628`, `1200×1200` a `960×1200` v samostatnom `outputs-pmax/`. Generátor zachová presné schválené texty, pridá centrálnu 80 % safe zónu a urobí presný finálny crop. `google-batch` nie je pre PMax sadu podporovaný. PMax výstupy musia prejsť vizuálnym QA rovnako ako Meta bannery.

**4 provideri:**

| Provider | Použitie |
|----------|-----------|
| `google` | Default, synchrónny Nano Banana 2 |
| `google-batch` | Asynchrónny hromadný beh; natívny pomer z každého promptu |
| `fal` | Nano Banana 2 cez fal.ai |
| `gpt-image` | Alternatíva cez fal.ai pre textovo náročné formáty |

- **Google model:** `gemini-3.1-flash-image`
- **Keys:** environment alebo najbližší nadradený `.env` → `FAL_KEY`, `GEMINI_API_KEY`
- **Reference images:** skript posiela brand-spec-card + visual-style-card + product photo automaticky ako `inlineData`
- **Nano Banana MCP** (ak je pripojený): `mcp__claude_ai_Nano_Bananna__generate_media` s promptom + asset IDs

## Output location

```
brands/{brand}/products/{product}/product-image-ads/{ad-set}/
├── test-plan.json
├── prompts-sk.json
├── scoring-sk.json
├── approval-sk.json
└── outputs/
    ├── {NN}-{template-name}/
    │   ├── prompt.txt
    │   └── {template-name}_v1_img1.png
    ├── manifest.json
    └── gallery.html
```
