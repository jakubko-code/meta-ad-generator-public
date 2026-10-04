# Step 2 — Veo b-roll JSON prompty (per segment)

## Čo tento krok robí

Zvolený koncept zo Step 1 rozloží na **samostatné b-roll JSON prompty** — jeden na každý segment: `hook-a`, `hook-b`, `telo`, `cta`. Tieto sa generujú zvlášť vo Veo/Flow a spájajú v Step 3.

## Vstupy

- [x] Zvolený koncept (Hook A/B + Telo + CTA) zo `video-concepts.md`
- [x] Detailný popis produktu (tvar, materiál, farba) — keďže nejdú keyframy, vernosť drží len text
- [x] Schéma: [templates/veo-broll-schema.json](templates/veo-broll-schema.json)

## Ako písať

Pre každý segment vytvor JSON podľa schémy. Kľúčové polia:

- `task`: `"text_to_video"` (b-roll, bez referenčného frame)
- `duration_seconds`: hook 4–8 (zostrihneš na ~3), telo/cta 6–8; dlhšie telo → viď extension nižšie
- `aspect_ratio`, `fps`
- `shot`: `scene`, `subject`, `action`, `camera` (pohyb/uhol/ohnisko), `lighting`, `mood`
- `product_fidelity`: detailný popis produktu (Veo si inak vymyslí tvar/farbu)
- `continuity`: `setting`, `grade`, `in_point`, `out_point` — aby strihy sadli (telo+cta zdieľajú rovnaké prostredie/grading; hook nadväzuje logicky)
- `negative`: VŽDY `"no on-screen text, no captions, no subtitles, no logos, no watermark, no UI"` (b-roll!)
- `audio`: voliteľné (ambient), inak ticho

## Pravidlá

- **Žiadny text v zábere.** B-roll je čistý; headline/CTA/logo sa dopĺňajú v editore (Step 3). Negatívny constraint je povinný.
- **Telo a CTA = rovnaké prostredie/svetlo/grading** (continuity blok identický), aby A aj B verzia sedeli na ten istý stred.
- **Hook môže byť iná scéna**, ale `out_point` hooku má logicky viesť do `in_point` tela (napr. hook končí pohľadom na kreslo → telo začína detailom kresla).
- **Vernosť produktu opíš v každom segmente** rovnako (copy-paste `product_fidelity`).
- **Píš po anglicky.** Štruktúrované JSON, krátke vecné frázy.

## Extension (telo dlhšie než 8 s)

Ak telo potrebuje > 8 s:
1. `telo-1.json` = base (8 s), na konci ustálený, „extension-ready" stav.
2. `telo-2.json` = `task: "extend"`, `continue_from: "telo-1 last second"`, opíš len **ďalší pohyb** (+7 s).
3. Opakuj (telo-3…) max 20× (~148 s).

Každý extension prompt opisuje pokračovanie z poslednej sekundy, nie celú scénu odznova.

## Výstup

```
brands/{brand}/products/{product}/animations/{date}-{slug}/{concept-slug}/
├── hook-a.json
├── hook-b.json
├── telo.json          # alebo telo-1.json (+ telo-2.json … pri extension)
└── cta.json
```

Pokračuj na Step 3 — generovanie a zostavenie.
