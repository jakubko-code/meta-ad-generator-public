# BONUS — Video Concepts (Hook A/B + Telo + CTA)

Druhý režim videa popri [02-animate](../02-animate/). Kým 02-animate rozhýbe **jednu statickú reklamu** (frame interpolácia), tento flow vyrába **scénové / UGC-style video reklamy** zložené z viacerých b-roll záberov, postavené na **Hook A/B testovaní**.

## Princíp (Hook A/B)

Každý koncept má **jedno telo a CTA** (konštanta — generuje sa raz) a **dva varianty hooku** (0–3 s). Hook A a Hook B sú **fyzicky odlišné scény** (iný záber, iná situácia, prípadne iný typ — situačný vizuál vs talking-head). Výsledkom sú dve hotové verzie:

```
Verzia A:  [Hook A]  +  [Telo]  +  [CTA]
Verzia B:  [Hook B]  +  [Telo]  +  [CTA]
                         ▲ identické v oboch
```

Cieľ: otestovať, ktorý hook lepšie **zastaví scroll** pre daný avatar. Mení sa len úvod.

## Čím sa líši od 02-animate

| | 02-animate | 05-video-concepts |
|---|---|---|
| Vstup | 1 víťazná statika | hrubá scéna + research |
| Technika | start+end frame → interpolácia | b-roll text-to-video po segmentoch |
| Text v zábere | zamrznutý (z reklamy) | **žiadny** (b-roll, text dopĺňaš neskôr) |
| Keyframy | áno | **nie** (len JSON prompty) |
| Dĺžka | 3–4 s | 8 s/segment, dlhšie cez extension |
| Výstup | 1 animovaná reklama | 2 A/B verzie (hook A/B + telo + CTA) |

## Veo limity (kontext)

- Jeden prompt = video **4 / 6 / max 8 s**.
- **Extension (+7 s):** Veo zoberie posledný ~1 s a nadviaže ďalších 7 s. Opakovateľné až 20× → súvislé video do **~148 s**.
- Segmenty sa generujú samostatne a **spájajú v Google Flow** (strih). Telo dlhšie než 8 s = base 8 s + extension(y).

## 3-krokový workflow

1. **Koncepty** ([step-1-concepts.md](step-1-concepts.md)) — z brand+produkt+research vygeneruj N konceptov (Hook A/B + Telo + CTA) so strategickým odôvodnením, mapované na avatar/persona/angle.
2. **JSON prompty** ([step-2-json-prompts.md](step-2-json-prompts.md)) — zvolený koncept → Veo b-roll JSON na každý segment (hook-a, hook-b, telo, cta). Bez textu, bez keyframov, s kontinuitou pre čistý strih.
3. **Generuj + zostav** ([step-3-assemble.md](step-3-assemble.md)) — vygeneruj segmenty v Gemini/Flow, zostav dve A/B verzie, prípadne predĺž telo cez extension, dopíš text v editore, iteruj.

## Výstup (umiestnenie)

```
brands/{brand}/products/{product}/animations/{date}-{slug}/
├── video-concepts.md           # všetky koncepty (step 1)
└── {concept-slug}/             # zvolený koncept (step 2)
    ├── hook-a.json
    ├── hook-b.json
    ├── telo.json               # (alebo telo-1.json, telo-2.json pri extension)
    ├── cta.json
    ├── assembly.md             # poradie strihu + extension plán (step 3)
    └── exports/                # finálne A/B verzie z Flow
```

> Pozn.: animácie patria pod **products/{product}/animations/**, nie do brand-dna (rovnako ako 02-animate).

## Pravidlá

- **B-roll = žiadny text v zábere.** Headline/CTA/logo sa dopĺňajú až v editore. Do JSON daj negatívny constraint „no text, no captions, no logos, no watermark".
- **Telo + CTA identické naprieč A/B.** Generuj raz, použi v oboch verziách.
- **Hook = 0–3 s, scroll-stopper.** Prvý záber musí zaujať do 1 s. Generuj na 4–8 s a zostrihni.
- **Kontinuita pre strih.** Telo a CTA majú rovnaké prostredie/svetlo/grading; hook môže byť iná scéna, ale prechod hook→telo musí dávať zmysel (logický strih).
- **Vernosť produktu = image-to-video z REÁLNEJ webovej fotky.** Ak musí byť produkt 1:1 ako sa predáva (produktové videá), NEPOUŽÍVAJ text-to-video ani AI-generovaný keyframe (oboje produkt prekreslia). Namiesto toho vezmi reálnu webovú fotku, orež na 9:16 (kokon/vysoké produkty sadnú vertikálne) a pošli ju ako prvý frame: `generate_videos.py --image <foto-9x16.png>`. Veo pridá len pohyb, produkt ostane nedotknutý. Overené 2026-06-22 (SOPHIE PLUS). Text-to-video použi len na scény bez produktu (napr. atmosférický hook).
- **Overený recept na verné produktové video (2026-06-23):** image-to-video z **čistej** produktovej fotky na bielom pozadí (nie z lifestyle cropu) + **jeden súvislý ~8 s záber** + jednoduchý ľudský opis scény (prostredie, ľudia, jemný pohyb; pri dvojkresle pár alebo rodič s dieťaťom kvôli emócii) + voliteľný voiceover, 9:16. Príklad: „kreslo na terase domu, žena sedí s malým dieťaťom v náručí, jemne sa hojdajú“. Veo si pri čistej fotke nemá čo domýšľať, takže produkt ostane 1:1.
- **Segmentový Hook A/B cez text-to-video pri produkte zlyhal:** t2v si produkt vymyslelo a medzi zábermi „preskakoval“. Hook A/B flow používaj s produktom iba vtedy, keď sú všetky segmenty image-to-video z tej istej čistej fotky; na dlhšie video radšej viac samostatných i2v scén.
- **Dĺžka:** `07-image-generation/generate_videos.py` ide cez Veo API, ktoré podporuje iba 4 / 6 / 8 s. Dlhšie klipy (napr. 10 s) zatiaľ vychádzajú z aplikácie Gemini, kde beží novšia verzia Veo — tie robí človek ručne.
- **Veo prompty píš po anglicky** (model reaguje spoľahlivejšie), dokumentáciu po slovensky.
