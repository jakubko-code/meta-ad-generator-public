# BONUS 03 — Image Translator

Prenesie **schválený preklad copy** do hotového banneru. Vizuál, kompozícia, farby, produkt a typografia ostanú; zmenia sa iba texty, a to presne na tie, ktoré prešli jazykovým scoringom a ľudským schválením. Model nič neprekladá sám.

Hodí sa, keď má banner ostať vizuálne identický naprieč jazykmi (napr. vizuálne schválený víťaz). Keď na vizuálnej zhode nezáleží, stačí `generate_ads.py --lang {lang}`.

## Podmienky (skript ich vynúti)

1. Zdrojový banner leží v ad sete (`products/<produkt>/product-image-ads/<ad-set>/outputs*/<NN-template-concept>/…png`), je zapísaný v `manifest.json` toho priečinka so SHA-256, ktorý sedí s aktuálnym súborom, a vznikol z aktuálneho schváleného zdroja (`render.prompts_sha256`). Rendery spred evidencie hashu treba vyrobiť znova.
2. Banner má vizuálny PASS pre presne tento súbor: exportuj QA z dashboardu (`creative-qa.json`) a odovzdaj ho cez `--qa-export`.
3. Pre každý cieľový jazyk existuje `prompts-{lang}.json` z [copy translatora](../04-copy-translator/copy-translator.md) s `"source_prompts": "prompts-sk.json"`.
4. `scoring-{lang}.json` (s hashom zdroja) a `approval-{lang}.json` sedia na presné bajty prekladu; zdroj má kompletný scoring 01–08 aj approval a od prekladu sa nezmenil.
5. Brief a template prekladu sú zamknuté na zdroj; hook sa renderuje cez `{{placeholder}}`.
6. Cena v preklade vyžaduje `market_prices_confirmed=true` v `approval-{lang}.json`.
7. Copy polia majú pár v oboch smeroch. Preložené pole, ktoré zdroj nemá (napr. nová cenová línia), sa nemá kam umiestniť; zdrojové pole bez schváleného prekladu (napr. vynechaný subhead) by v obrázku ostalo v pôvodnom jazyku. V oboch prípadoch použi `generate_ads.py --lang {lang}`.

Ak niečo nesedí, skript skončí pred API volaním s konkrétnou chybou.

## Spustenie

Najprv bezplatne skontroluj brány a presné prompty:

```bash
python3 BONUS/03-image-translator/translate_ads.py \
  --image brands/{brand}/products/{product}/product-image-ads/{ad-set}/outputs/01-headline-template-C01/headline-template_v1_img1.png \
  --languages hu,cz --qa-export path/to/creative-qa.json --dry-run
```

Platené spustenie až po výslovnom „generuj“ (bez `--dry-run`).

| Parameter | Popis | Default |
|-----------|-------|---------|
| `--image` | Hotový banner v `outputs*/` ad setu | povinné |
| `--languages` | Kódy jazykov so schváleným `prompts-{lang}.json` | povinné |
| `--brand` | Presný názov značky pre ochranu wordmarku | `brand` z prompts JSON |
| `--provider` | `google` / `google-batch` / `fal` | `google` |
| `--qa-export` | `creative-qa.json` z dashboardu s PASS pre zdrojový PNG | povinné |
| `--aspect-ratio` | Pomer strán | z `manifest.json` zdroja, inak z promptu |
| `--dry-run` | Over brány a ukáž prompty bez volania API | — |

`google-batch` a `fal` používaj iba na výslovný pokyn. Keys sa načítajú z environmentu alebo z najbližšieho nadradeného `.env`.

## Čo model dostane

Pre každý jazyk obrázok + zoznam dvojíc `"zdrojový text" → "schválený text"` zo zdrojového a preloženého promptu (headline, subhead, body, CTA, recenzie, bullets, ikony, tabuľky). Pravidlá: použiť náhrady doslova, nemeniť neuvedený text, nemeniť obal produktu ani wordmark, zachovať pozíciu, font a farbu.

## Output

```
<ad-set>/outputs-{lang}/<NN-template-concept>/<pôvodný-názov>_translated.png
<ad-set>/outputs-{lang}/manifest.json   ← SHA-256 PNG + zdrojový obrázok, prompts hash, provider/model
```

Výstup sa zobrazí v dashboarde pod jazykom `{lang}` a prechádza rovnakým vizuálnym QA ako bežný render: presné schválené texty, žiadny zvyšok zdrojového jazyka, nezmenený produkt a logo, správna cena pre trh. Ak model zmení produkt alebo text, oprav iba daný jazyk; hotové výstupy nemaž.
