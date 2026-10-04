# 04 — Testovací plán pred produkciou (Meta Ads Manager B1)

Pred písaním `prompts-{lang}.json` musí byť jasné, **čo testujeme a prečo**. Výstupom je `test-plan.json` priamo v ad sete.

```bash
python3 04-test-planning/test_plan.py init \
  --ad-set brands/{brand}/products/{product}/product-image-ads/{ad-set} \
  --plan-id TP-YYYY-MM-DD-NAZOV \
  --market sk \
  --objective sales \
  --funnel-stage TOF \
  --test-variable hook
```

`init` vytvorí plán `schema_version: 2`. Pred vyplnením agent načíta `brands/{brand}/testing/learnings.md` a aktívne testy v `tracker.md`. Potom doplní hypotézu, konštanty, dátovú bránu, `learnings` a varianty z Meta Ads Manager režimov S/A. Človek potvrdí smer testu; potom sa stav zmení z `draft` na `planned`. Každý variant musí mať unikátny `concept_id`. Pri hook teste môžu varianty zdieľať rovnaký `template_number` aj neskorší `template_name`; generátor ich vo výstupe odlišuje cez `concept_id`.

### Čo validátor pri schema 2 vynúti

| Pole | Pravidlo |
|---|---|
| `test_design` | `isolated` (≥ 2 varianty, mení sa iba testovaná os), `concept-comparison` (≥ 2 varianty, `test_variable: concept`) alebo `pilot` (1 variant, `test_variable: concept`, verdikt vždy predbežný) |
| izolácia | pri `isolated` musí mať každý variant rovnaké strategické polia okrem testovaného: `hook` → persona, awareness, angle, formát, template; `angle` → persona, awareness, formát, template; `format` → persona, awareness, angle, hook; `visual` → persona, awareness, angle, hook, formát; `copy` → persona, awareness, angle, hook, formát, template; `offer` → persona, awareness, angle, formát, template. Testované pole (napr. `hook`, pri `visual`/`copy`/`offer` rovnomenné pole variantu) je neprázdne a medzi variantmi sa líši |
| `data_gate` | okrem textov `minimum_runtime` a `minimum_evidence` aj celé čísla `minimum_days`, `minimum_impressions_per_variant` a `minimum_events_per_variant: {event, count}` |
| `learnings` | `reviewed: true`, `applied` (zoznam learning ID, môže byť prázdny), `predecessor_plan_id` (alebo `null`) a neprázdne `note` s dôvodom testu |

Plány `schema_version: 1` (vytvorené pred 11. 9. 2026) `test_plan.py validate` stále prijme kvôli hashovej väzbe existujúcich ad setov, ale generátor ich pustí iba s výslovným `--allow-legacy`, lebo izoláciu ani prahy strojovo nekontrolujú. Nový plán nikdy nekopíruj zo starého — vytvor ho cez `init`.

Generátor pri izolovanom teste porovná aj renderované prompty: pri `hook` teste sa smú líšiť iba polia hooku a brief; v ostatných testoch ostáva cena rovnaká (okrem `offer`), pri `angle` aj CTA a pri `visual` celé copy. Šablóna `test-plan-template.json` je vzor so `status: draft`.

```bash
python3 04-test-planning/test_plan.py validate \
  --plan brands/{brand}/products/{product}/product-image-ads/{ad-set}/test-plan.json
```

Po vytvorení `prompts-{lang}.json` ho previaž s presnými bajtmi plánu:

```bash
python3 04-test-planning/test_plan.py bind \
  --prompts brands/{brand}/products/{product}/product-image-ads/{ad-set}/prompts-sk.json
```

Nový `prompts-{lang}.json` používa `workflow_version: 2`, obsahuje ID a SHA-256 plánu a každý brief odkazuje na presný `concept_id`, awareness stage a hook. Plán a prompty sa musia pokrývať presne 1 : 1 a hook musí byť presne text renderovaného poľa (`brief.hook_field`, default `headline`) vloženého cez `{{placeholder}}`. `bind` tento kontrakt overí hneď po zápise väzby a pri nezhode skončí kódom 1; generátor ho kontroluje znova pred každým behom.

Po `bind` je `test-plan.json` nemenný záznam pôvodnej hypotézy. Výsledok testu zapisuj do `tracker.md` a `learnings.md` (s ID, ktoré ďalší plán uvedie v `learnings.applied`), nie späť do plánu. Strategická zmena vyžaduje nový alebo vedome revidovaný B1 plán a nový bind, scoring aj approval. Starý ad set bez `workflow_version` prejde iba pri explicitnom `--allow-legacy`; pri novom ad sete tento prepínač nepoužívaj.
