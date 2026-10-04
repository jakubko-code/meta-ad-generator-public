# Creative QA dashboard

Dashboard je offline pracovný priestor s dvoma časťami: **Creative QA** pre hotové bannery a **Template knižnica** pre globálne aj klientské formáty. Nie je workflow krokom, nenahrádza `--validate-only`, scoring ani ľudské schválenie copy.

## Zostavenie

```bash
python3 tools/dashboard/build_dashboard.py
```

Skript nájde bannery v `brands/*/products/*/product-image-ads/*/outputs*/manifest.json` a template náhľady podľa ich `preview.json`. Vytvorí samostatný `dashboard.html`. CSS a JavaScript vloží priamo do HTML, takže dashboard funguje lokálne bez webového servera. Pri pripojení načíta Jost cez Google Fonts; offline použije systémový fallback.

## Čo podporuje

- vyhľadávanie a kaskádové filtre podľa brandu, produktu, ad setu, jazyka a výstupu,
- náhľady bez orezania pre `4:5`, `9:16`, `1:1` aj ďalšie pomery,
- detail banneru s workflow v2 údajmi,
- vizuálny QA stav `PASS`, `Drobná oprava`, `FAIL` alebo `Nehodnotené`, viazaný na SHA-256 konkrétneho PNG — ak sa súbor pod rovnakou cestou zmení (regenerácia) alebo chýba, banner dostane stav `Prehodnotiť` a treba ho posúdiť znova; pôvodný verdikt ostane v detaile ako história,
- lokálnu poznámku ku každému banneru,
- výber, side-by-side porovnanie, stiahnutie a PDF,
- export všetkých hodnotení do `creative-qa.json` vrátane posúdeného (`sha256`) aj aktuálneho hashu súboru (`current_sha256`, `stale`).

Template knižnica navyše podporuje:

- vyhľadávanie a filtre podľa zdroja, brandu a stavu náhľadu,
- bezplatné SVG wireframy s kompozíciou a copy slotmi,
- voliteľné watermarked Gemini specimen rendery,
- detekciu neaktuálneho náhľadu po zmene `.md` template-u,
- detail s príkazom na obnovu wireframu alebo explicitný platený render.

Wireframy obnovíš bez API nákladov:

```bash
python3 05-creative-production/template_preview.py --all --missing-only
python3 tools/dashboard/build_dashboard.py
```

Platený render sa nikdy nespustí pri builde dashboardu ani pri `--all`. Vyžaduje samostatný príkaz pre jeden template s `--generate-preview`.

QA stav a výber sa ukladajú iba do `localStorage` daného prehliadača. Staré označenia z `ad-gen-flagged` alebo zo vstupného `flagged.json` sa pri prvom otvorení migrujú na stav `Drobná oprava`. Hodnotenia uložené pred zavedením hashu nemajú `sha256`, preto sa zobrazia ako `Prehodnotiť` — ich platnosť pre aktuálny súbor sa nedá preukázať. Exportovaný `creative-qa.json` je handoff artefakt; sám nemení prompty, plán ani produkčné brány.

## Zdrojové súbory

- `build_dashboard.py` — discovery a HTML kontrakt,
- `dashboard.css` — responzívny dizajn a tlač,
- `dashboard.js` — filtre, QA, výber, lightbox, compare režim a template detail.
- `05-creative-production/template_preview.py` — parser template-ov, SVG wireframe, hash freshness a explicitný Gemini preview.

Neupravuj ručne generovaný koreňový `dashboard.html`; pri ďalšom builde by sa zmeny prepísali.
