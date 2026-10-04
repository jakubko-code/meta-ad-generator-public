# Bonus — Multiply prompt

Použi tento prompt v Claude Code alebo Codexe až vtedy, keď má pôvodná reklama reálny performance signál a nový multiply ad set už obsahuje validný `test-plan.json` s `test_variable: format`.

## Vstupy

- `original-winner.md` s víťazným briefom a performance signálom,
- hotový `test-plan.json`,
- zvolené template `.md` súbory,
- brand DNA a produktové fakty.

## Prompt

```text
Prenes jednu overenú víťaznú reklamu do všetkých kompatibilných formátov uvedených
v test-plan.json. Ide o workflow v2 experiment, v ktorom je jediná testovaná premenná
format. Nevytváraj koncept, ktorý nie je v pláne, a nevynechaj žiadny koncept z plánu.

Pre každý variant:
- zachovaj concept_id presne podľa test-plan.json,
- zachovaj rovnakú personu, awareness stage, angle, hook, emóciu, ponuku,
  produktovú pravdu a hlas značky,
- použi template_number a format pridelené danému konceptu,
- prepíš copy len natoľko, aby spĺňalo štruktúru a limity daného formátu,
- prispôsob kompozíciu, typografiu a podporné prvky danému template,
- vytvor kompletný prompt pre Nano Banana 2.

Strategický základ sa nesmie zmeniť. Ak je formát s víťaznou DNA nekompatibilný,
zastav sa a navrhni jeho odstránenie z test-plan.json ešte pred bindom. Nevynechávaj ho
potichu iba z prompts-sk.json.

Výstup zapíš do prompts-sk.json. Nastav workflow_version: 2 a zabezpeč presné
pokrytie konceptov medzi plánom a promptami v pomere 1 : 1. test_plan.id a
test_plan.sha256 doplní až príkaz test_plan.py bind.
```

## Čo zostáva konštantné

- persona a awareness stage,
- angle, hook a cieľová emócia,
- ponuka, produktová pravda a dôkaz,
- hlas a vizuálny fingerprint značky.

## Čo sa môže meniť

- `format` a `template_number`,
- copy štruktúra v medziach rovnakého hooku a claimu,
- kompozícia, typografická hierarchia a podporné prvky vyžadované template.

## Kontrola

Všetky varianty prejdú agentmi 01–08 v `06-quality-gates/`. Agenti 01–07 potrebujú score aspoň 90 a PASS; Agent 08 má binárne veto. Potom nasleduje ľudské schválenie a `generate_ads.py --validate-only`.

Nemultiplikuj reklamu bez reálneho signálu. Výsledky testu zapisuj do `tracker.md` a `learnings.md`, nie do naviazaného `test-plan.json`.
