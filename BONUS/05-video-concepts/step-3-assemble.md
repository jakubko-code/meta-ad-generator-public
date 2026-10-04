# Step 3 — Generovanie a zostavenie (Flow)

## Čo tento krok robí

Vygeneruje jednotlivé b-roll segmenty vo Veo/Flow, zostaví **dve A/B verzie**, prípadne predĺži telo cez extension, a pripraví na dopísanie textu.

## Vstupy

- [x] JSON prompty zo Step 2 (`hook-a`, `hook-b`, `telo`, `cta`)
- [x] Buď **API cesta** (`07-image-generation/generate_videos.py`, automaticky), alebo **Flow** ([labs.google/flow](https://labs.google/flow)) manuálne

## Cesta A — API (automatizované, odporúčané na rýchlosť)

`generate_videos.py` pošle prompty do Veo (Gemini API) a stiahne mp4; vie aj pospájať A/B cez ffmpeg.

```bash
# dry-run (zadarmo)
python 07-image-generation/generate_videos.py --concept-dir <concept-dir> --assemble --dry-run
# ostrý beh (PLATENÉ) — celý koncept + assemble
python 07-image-generation/generate_videos.py --concept-dir <concept-dir> --assemble
# image-to-video (vernejší produkt — fotka ako prvý frame)
python 07-image-generation/generate_videos.py --prompts-file <telo.json> --image <product-or-startframe.png>
```

**Overené poznatky (2026-06-22 test):**
- **Dĺžka 4 / 6 / 8 s funguje** — treba ju reálne poslať do configu (`duration_seconds` / `--duration`). veo-3.1-fast vie aj 4 s (overené: výstup presne 4,0 s). Ak ju nepošleš, default je 8 s. Kratšie dĺžky pri čistom text-to-video v základnom rozlíšení môžu vyžadovať vyššie `--resolution` (1080p) alebo referenčný obrázok (i2v).
- Text-to-video = produkt „blízko, nie 1:1". Pre hero/produktové zábery použi **image-to-video** (`--image` reálna fotka) na vernosť 1:1.
- Výstup default 9:16, 720×1280, h264+aac. Každý klip = reálny náklad (video je drahé) — najprv `--dry-run`.

## Cesta B — Flow (manuálne)

## Postup

1. **Generuj segmenty** vo Flow (text-to-video, Fast mode):
   - `hook-a`, `hook-b`, `telo`, `cta` — každý 4–8 s, 2–4 variácie, vyber najlepšiu.
   - Telo > 8 s: vygeneruj `telo-1`, potom **Extend** (+7 s) podľa `telo-2…`.
2. **Skontroluj b-roll** každého segmentu:
   - Žiadny text/logo/watermark v zábere (b-roll!)
   - Produkt verný popisu (tvar, materiál, farba)
   - Telo a CTA vizuálne konzistentné (rovnaké prostredie/svetlo)
   - Hook → telo prechod dáva zmysel
3. **Zostav dve verzie** na timeline vo Flow:
   ```
   Verzia A:  hook-a  →  telo  →  cta
   Verzia B:  hook-b  →  telo  →  cta
   ```
   Telo + CTA sú v oboch tie isté klipy — meníš len prvý segment.
4. **Dopíš text** (headline na hook, benefity na telo, CTA text na záver) — v editore/Flow text vrstve. Drž brand pravidlá (oslovenie podľa klienta, žiadne ceny ak to tak chceš, [[chyby-neopakovat]]).
5. **Export** oboch verzií do `exports/` (napr. `verzia-a.mp4`, `verzia-b.mp4`).

## Iterácia

Ak segment nesedí (produkt sa morfuje, prechod tvrdý, pohyb zlý):
- Oprav **JSON prompt** daného segmentu (nie všetko) a pregeneruj len ten segment.
- Telo/CTA nepregenerúvaj zbytočne — sú konštanty pre obe verzie.
- Loguj do `iterations.md` (čo bolo zle → čo sa zmenilo → výsledok).

## A/B test (po nasadení)

Obe verzie majú **identické telo + CTA**, líši sa len hook. V Meta/kampani porovnaj **hook rate / 3s view rate / hold**, aby si zistil, ktorý hook lepšie zastaví scroll pre daný avatar. Víťazný hook použi ako default, prehraný nahraď novým variantom.

## Výstup

```
brands/{brand}/products/{product}/animations/{date}-{slug}/{concept-slug}/
├── assembly.md      # poradie strihu, extension plán, text-overlay návrh
├── iterations.md    # log opráv
└── exports/
    ├── verzia-a.mp4
    └── verzia-b.mp4
```
