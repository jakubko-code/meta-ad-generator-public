# 05 — Creative Production

Tri zdroje šablón pre statické reklamy a workflow na vytvorenie vlastnej štruktúry z konkurenčnej reklamy. Produkcia začína až po platnom `test-plan.json`; každý výstup používa workflow v2 a odkazuje na schválený `concept_id`.

---

## 01-templates-by-motion/

**40 Motion Foundations recipe cards** — jeden súbor = jeden formát.

Každá šablóna obsahuje:
- Metadata (aspect ratio, safe zones, reference uploads)
- 2–3 štýly s vlastnou copy template + image generation promptom
- Presné word counts pre headline / subhead / CTA
- Variation vectors (BG, lighting, product position, color)
- Scoring kritériá pre 8 agentov

Vhodné pre: **plný Motion workflow** (copy → scoring → generácia). Vyššia kvalita, viac iterácií.

Postup písania copy: `01-templates-by-motion/copy-prompt.md`

---

## 02-40-templates/

**40 generických ad formátov** — všetky v jednom súbore `template-prompts.md`.

Každý formát obsahuje:
- Hotový prompt s [BRACKETED PLACEHOLDERS] na vyplnenie
- Aspect ratio + needs_product_images flag

Vhodné pre: **rýchle prototypy**.

Postup písania copy: `02-40-templates/copy-prompt.md`

---

## 03-ad-swipe.md

**Výroba šablóny z konkurenčnej reklamy** — 3-fázový proces:

1. **Deconstruct** — JSON extrakcia zo screenshotu konkurenčného adu
2. **Rebuild** — mapovanie na štruktúru format template
3. **Preview** — bezplatný SVG wireframe a voliteľný platený Gemini specimen

Výstup: nový template pripravený na copy v kroku 5, scoring v kroku 6 a generovanie v kroku 7.

---

## Vizuálne náhľady template-ov

Po vytvorení alebo zmene template-u vygeneruj bezplatný deterministický wireframe:

```bash
python3 05-creative-production/template_preview.py \
  --template brands/{brand}/{brand}-templates/{NN}-{slug}.md
```

Všetky chýbajúce wireframy obnovíš cez:

```bash
python3 05-creative-production/template_preview.py --all --missing-only
```

Skript uloží `wireframe.svg` a `preview.json` s SHA-256 template-u. Po zmene `.md` dashboard označí starý náhľad ako neaktuálny. Voliteľný približný Gemini render vznikne iba s explicitným `--generate-preview`; je označený watermarkom a nie je produkčnou reklamou:

```bash
python3 05-creative-production/template_preview.py \
  --template brands/{brand}/{brand}-templates/{NN}-{slug}.md \
  --brand {brand} --product-image brands/{brand}/products/{product}/source-product-images/{image}.png \
  --generate-preview
```

Template knižnicu otvoríš po `python3 tools/dashboard/build_dashboard.py` v koreňovom `dashboard.html`. Náhľady sú dokumentácia formátu; nenahrádzajú koncept, `test-plan.json`, scoring, approval ani produkčný `--validate-only`.

---

## Kedy čo použiť

| Situácia | Zdroj |
|----------|-------|
| Chcem kvalitný ad s plným workflow | `01-templates-by-motion/` |
| Chcem rýchly prototyp | `02-40-templates/` |
| Videl som dobrý ad konkurencie | `03-ad-swipe.md` |
| Mám brand-špecifický formát | `brands/{brand}/{brand}-templates/` |
