# Bonus — Multiply

Multiply prenesie **víťaznú strategickú DNA reklamy** do ďalších formátov. Nie je to skratka mimo hlavného workflow: každý nový multiply ad set je workflow v2 test zmennej `format` a musí prejsť krokmi 4–9.

## Predpoklady

- Pôvodná reklama prešla krokmi 1–9 a má reálny performance signál, nie iba dobre ohodnotený brief.
- Persona, awareness stage, angle, hook, emócia, ponuka a produktové fakty víťaza sú dohľadateľné.
- Dostupné sú vhodné templates v [`05-creative-production/01-templates-by-motion/`](../../05-creative-production/01-templates-by-motion/).
- Brand cards a produktové fotografie sú pripravené.

## Povinný kontrakt nového ad setu

```text
brands/{brand}/products/{product}/product-image-ads/{date}-{winner-slug}-multiply/
├── original-winner.md          # zdrojový brief + performance signál
├── test-plan.json            # B1 plán, test_variable: format
├── prompts-sk.json           # workflow_version: 2 + presná väzba na plán
├── scoring-sk.json           # hash-bound výsledky 8 agentov
├── approval-sk.json          # explicitné schválenie človekom
└── outputs/                    # obrázky, manifest.json a gallery.html
```

Každý generovaný variant má unikátny `concept_id` a v pláne aj promptoch sa nachádza presne raz. Pri tomto teste sa mení iba `format` a `template_number`. Persona, awareness stage, angle, hook, ponuka a ostatné strategické konštanty ostávajú rovnaké.

## Postup

1. Ulož víťaza a jeho performance signál do `original-winner.md`.
2. Vytvor nový ad set a inicializuj `test-plan.json`:

   ```bash
   python3 04-test-planning/test_plan.py init \
     --ad-set brands/{brand}/products/{product}/product-image-ads/{date}-{winner-slug}-multiply \
     --plan-id TP-YYYY-MM-DD-MULTIPLY --market sk --objective sales \
     --funnel-stage TOF --test-variable format
   ```

3. Pred produkciou uprav plán: každému kompatibilnému formátu priraď jedinečné `concept_id`, správny `template_number` a rovnaké strategické konštanty. Nekompatibilný formát vynechaj z plánu, nie až z promptov.
4. Validuj plán:

   ```bash
   python3 04-test-planning/test_plan.py validate \
     --plan brands/{brand}/products/{product}/product-image-ads/{date}-{winner-slug}-multiply/test-plan.json
   ```

5. Podľa [`multiply-prompt.md`](multiply-prompt.md) vytvor `prompts-sk.json`. Musí pokrývať všetky koncepty z plánu v pomere 1 : 1.
6. Naviaž presné bajty plánu:

   ```bash
   python3 04-test-planning/test_plan.py bind \
     --prompts brands/{brand}/products/{product}/product-image-ads/{date}-{winner-slug}-multiply/prompts-sk.json
   ```

7. Pokračuj krokom 6: scoring, ľudské schválenie, bezplatné `--validate-only`, a až po explicitnom pokyne generovanie.
8. Výsledky po vyhodnotení zapisuj do `tracker.md` a `learnings.md`. Naviazaný `test-plan.json` nemeníš.

## V jednej vete

Víťaz s reálnym signálom → nový B1 plán s `test_variable: format` → 1 : 1 prompty → bind → quality gates → generovanie → test handoff → learning.
