# Produkcia bannerov — most B1 → Image Ad Generator → B2

Tento súbor prepája stratégiu Meta Ads Managera s produkčnou pipeline projektu. Poradie je záväzné:

```text
S research → E/A stratégia a koncepty → B1 test-plan.json
→ kroky 5–7 Image Ad Generatora → B2 tracker a launch checklist
```

Avatar, angle, awareness stage, hook a testovacia hypotéza vznikajú **pred bannerom**. B2 po produkcii iba doplní reálne súbory a naming; spätne neprepisuje hypotézu podľa hotových kreatív.

## Rozsah

Pipeline pokrýva statické PNG vo viacerých pomeroch a voliteľné rozhýbanie statiku cez `BONUS/02-animate/`. Nepokrýva plnohodnotnú produkciu UGC/talking-head videa. Video koncept z Režimu A preto ide do samostatnej produkcie; statický variant pokračuje týmto mostom.

## Mapovanie konceptu do kontraktu

| Režim A / B1 | Produkčný artefakt |
|---|---|
| Persona/avatar | `test-plan.json variants[].persona` + `prompts[].brief.persona` |
| Angle | `variants[].angle` + `brief.angle` |
| Awareness stage | `variants[].awareness_stage` + `brief.awareness_stage` |
| Presný statický hook/headline | `variants[].hook` + `brief.hook`; renderovaný text je v poli `brief.hook_field` (default `headline`, pri viacriadkovom hooku zoznam polí) a musí sa s hookom zhodovať |
| Brief | `variants[].brief_id` + `brief.id` |
| Koncept | unikátne `concept_id` v pláne aj prompte |
| Formát | `variants[].format`; voliteľne zamknutý `template_number` |
| Hypotéza, testovaná premenná a typ testu | top-level `hypothesis`, `test_variable`, `test_design` |
| Konštanty a dátová brána | top-level `constants` a `data_gate` (aj číselné prahy) |
| Použité learnings | top-level `learnings` (ID, predchodca, dôvod) |

## Praktický postup

1. Dokonči Režim S a zapíš zdrojovo doložené persony, pains a angles do `marketing-research/`.
2. V Režime E podľa potreby potvrď kampaňový kontajner; v Režime A vytvor konkrétne statické koncepty.
3. V Režime B1 vytvor v cieľovom ad sete `test-plan.json` cez `04-test-planning/test_plan.py init`.
4. Načítaj `testing/learnings.md` a aktívne testy. Doplň hypotézu, testovanú premennú, `test_design`, konštanty, primárnu metriku, číselnú dátovú bránu, `learnings` a všetky vyrábané koncepty. Nastav `status: planned` a validuj plán.
5. V kroku 5 vyber šablóny z `05-creative-production/` a vytvor workflow v2 `prompts-{lang}.json`.
6. Do každého briefu prenes presný `concept_id`, `awareness_stage` a `hook`; hook vlož do renderovaného poľa cez `{{placeholder}}`. Potom spusti `test_plan.py bind` — hneď overí kontrakt a pri nezhode skončí chybou.
7. V kroku 6 vykonaj scoring 8 agentmi a ľudské schválenie.
8. V kroku 7 spusti `--validate-only`; až po výslovnom „generuj“ zavolaj platený provider a vizuálne skontroluj každý PNG.
9. V Režime B2 priraď hotové PASS súbory (aj ich SHA-256 z `outputs*/manifest.json`) ku konceptom a doplň `testing/tracker.md` (Stav Pripravená) a launch checklist.
10. Kampaň spustí alebo zmení iba človek, prípadne agent po jeho výslovnom potvrdení.

## Workflow v2 obálka promptov

```json
{
  "workflow_version": 2,
  "brand": "Acme",
  "product": "Hero product",
  "test_plan": {
    "id": "TP-2026-08-06-HOOKS",
    "sha256": "doplní test_plan.py bind"
  },
  "prompts": [
    {
      "template_number": 1,
      "template_name": "headline-template",
      "aspect_ratio": "4:5",
      "needs_product_images": true,
      "brief": {
        "id": "B01",
        "persona": "Konkrétna persona",
        "angle": "Konkrétny angle",
        "emotion": "úľava",
        "customer_voice_anchor": "Zdrojovo doložená formulácia",
        "concept_id": "C01",
        "awareness_stage": "problem-aware",
        "hook": "Presný plánovaný headline",
        "hook_field": "headline"
      },
      "headline": "Presný plánovaný headline",
      "prompt": "Reproduce the exact product from the reference image. HEADLINE: {{headline}}"
    }
  ]
}
```

Generátor kontroluje SHA-256 `test-plan.json` aj zhodu konceptu, briefu, persony, angle, awareness stage, hooku a voliteľného template čísla. Hook musí byť presne text v `hook_field` (tolerujú sa iba veľké písmená a medzery) a prompt ho musí vkladať cez `{{placeholder}}` — natvrdo napísaný text by kontrolu obišiel, preto sa blokuje. Pri preklade (`source_prompts`) sa hook overuje v zdroji a brief prekladu musí byť 1:1 zhodný so zdrojom. Staré ad sety bez `workflow_version` sú podporované v legacy režime; nový ad set sa takto nevytvára.

Toto je iba ilustrácia obálky. Reálny `prompt` string sa kopíruje z recipe cardu v `05-creative-production/`; pravidlá pre jeho stavbu (placeholdery, `[BRACKETED]` tokeny a povinný odkaz na referenčnú fotku pri `needs_product_images: true`) sú v `05-creative-production/01-templates-by-motion/copy-prompt.md`.

## Zásobník kreatív verzus konkrétny test

Research a Režim A môžu vytvoriť širší zásobník konceptov. Do jedného `test-plan.json` však patria iba varianty, ktoré majú spoločnú testovaciu otázku a interpretovateľnú os. Ak chceš testovať inú premennú alebo inú hypotézu, vytvor nový ad set a nový plán.

## B2 handoff

Každý nasadzovaný PASS variant dostane samostatný riadok v `testing/tracker.md`. B2 doplní cestu k súboru, naming, verziu a plánovaný dátum; metriky ostávajú prázdne. Ak hotový banner nezodpovedá plánu, vráť ho do kroku 5 alebo 7 — neupravuj plán tak, aby spätne sedel.
