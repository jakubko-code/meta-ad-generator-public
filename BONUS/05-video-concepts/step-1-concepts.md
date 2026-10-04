# Step 1 — Video koncepty (Hook A/B + Telo + CTA)

## Čo tento krok robí

Z brand DNA + strategického researchu vygeneruje N video konceptov. Každý koncept je postavený na jednom avatare/persone/angle a obsahuje **Hook A vs Hook B + Telo + CTA**. Je to video ekvivalent konceptov z kroku 3 a pred produkciou vstupuje do testovacieho plánu v kroku 4.

## Vstupy

- [x] `brand-dna/voice-copy-styl.md`, `chyby-neopakovat.md`
- [x] Product research: `briefs.md`, `avatar-sheet.md`, `necessary-beliefs.md`, `deep-research.md`
- [x] (voliteľné) víťazné statické reklamy ako vizuálna referencia

## Ako generovať

Pre každý koncept naplň túto štruktúru (viď [templates/concept-template.md](templates/concept-template.md)):

- **ID + názov** — napr. „V1 — 5 minút len pre teba"
- **Avatar / Persona / Angle (Belief #)** — z briefs.md / necessary-beliefs.md
- **Strategické odôvodnenie** — prečo tento uhol zastaví scroll pre tento segment (1–3 vety)
- **Hook A** — typ (situačný vizuál / talking-head / POV / pattern-interrupt) + popis scény (0–3 s)
- **Hook B** — iný typ alebo iná situácia (musí byť fyzicky odlišný od A)
- **Telo** — konštantný stred (čo ukazujeme, aký benefit; 6–12 s)
- **CTA** — konštantný záver (akcia; 3–5 s)
- **On-screen text (návrh)** — čo sa dopíše v editore (b-roll je bez textu)

## Pravidlá pre koncepty

- **Hook A ≠ Hook B fyzicky.** Nie dve verzie tej istej vety — dve odlišné scény/uhly (napr. situačný záber vs talking-head). To je podstata A/B testu.
- **Telo + CTA sú konštanty.** Píš ich raz; v oboch verziách identické.
- **Grounded v researchu.** Každý koncept mapuj na konkrétny brief/belief a avatar. Žiadne generické nápady mimo stratégie.
- **Hook rieši scroll-stop, nie predaj.** Prvé 3 s = pattern interrupt / spoznanie sa / otázka. Predaj rieši telo.
- **Rešpektuj brand pravidlá** (oslovenie podľa klienta, žiadne anglicizmy, žiadne fabrikované tvrdenia) — [[voice-copy-styl]], [[chyby-neopakovat]].
- **Default 3 koncepty** na beh (rôzne avatary/angly), ak nie je povedané inak.

## Výstup

Ulož všetky koncepty do:
```
brands/{brand}/products/{product}/animations/{date}-{slug}/video-concepts.md
```

Vyber koncept, ktorý ide do produkcie → pokračuj na Step 2 s jeho Hook A/B + Telo + CTA.
