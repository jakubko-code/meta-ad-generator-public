# 02 — Product Research Check

Kontrola, či existuje marketing research pre zvolený produkt alebo kategóriu. Spúšťa sa po Brand Foundation (krok 1), pred architektúrou a tvorbou konceptov (krok 3).

---

## ⚠️ NAJPRV: research sa robí na KATEGÓRIU, nie na každé SKU

**Toto je prvá otázka, nie kontrola súborov.** Jednotkou researchu je **zákaznícky problém**, nie položka v katalógu.

Päť závesných kresiel má jedného zákazníka, jednu sadu obáv a jednu sezónnosť — `deep-research`, `avatar-sheet`, `necessary-beliefs` a `cep-sheet` sa pre ne robia **raz**. Líšia sa len faktami (rozmer, cena, materiál), a tie patria do `product-facts.md`.

### Rozhodovací postup

```
Existuje už research pre kategóriu, do ktorej produkt patrí?
│
├─ ÁNO → Vyrob LEN product-facts.md (+ prípadne vlastné briefy).
│        Do hlavičky napíš: > research-source: ../<kategoria>/marketing-research/
│        NEROB deep-research znova. Pokračuj do kroku 3 (E + A).
│
└─ NIE → Je to naozaj nová kategória? Zmenilo sa aspoň jedno:
         · iný zákazník        · iná cenová trieda
         · iný konkurenčný set · iné objekcie
         │
         ├─ ÁNO → plný cyklus (product-research-process.md).
         │        Zdeď, čo sa dá: segmenty a sezónnosť z príbuznej kategórie.
         │
         └─ NIE → patrí do existujúcej kategórie. Späť na vetvu ÁNO.
```

**Tvar, farba, rozmer ani model novú kategóriu nezakladajú.** Okrúhla a štvorcová kaďa = jedna kategória. Kaďa na drevo (2 650 €) a elektrická vírivka (6 399 €) = dve, lebo sa líši cena, konkurencia aj objekcie.

### Ako kategória vyzerá v štruktúre

Kategória **nemá vlastnú úroveň priečinkov** — je to bežná zložka v `products/`, ktorá nesie research za celú skupinu:

```
products/
├── kupacie-kade/          ← KATEGÓRIA: plný research (okrúhle aj štvorcové)
│   └── marketing-research/  deep-research, avatar-sheet, necessary-beliefs,
│                            cep-sheet, offer-brief, briefs, product-facts
├── virivky/               ← iná kategória: vlastný research (iná cena, konkurencia)
└── sauna-premium-220/     ← SKU v kategórii sauny: len product-facts + briefs
    └── marketing-research/
        └── product-facts.md   > research-source: ../../sauny/marketing-research/
```

### Dlhý chvost e-shopu

Pri e-shope s tisíckou SKU je zákazníckych problémov typicky **5–10** — a toľko je aj researchov. Väčšina položiek nikdy nedostane ručne robený banner; obsluhuje ich **katalógová reklama z feedu** (product set, DPA), kde sa kreatíva nerieši. Ručná kreatíva ide na hero produkty a kategórie.

**Research teda nesleduje počet SKU, ale počet zákazníckych problémov.**

---

## Čo skontrolovať

Skontroluj existenciu týchto súborov:

**Pre KATEGÓRIU** (raz na zákaznícky problém):
```
brands/{brand}/products/{kategoria}/marketing-research/
├── deep-research.md       — POVINNÝ
├── avatar-sheet.md        — POVINNÝ
├── necessary-beliefs.md   — POVINNÝ
├── offer-brief.md         — POVINNÝ
├── cep-sheet.md           — POVINNÝ (situačná os briefov)
└── briefs.md              — POVINNÝ, 10–15 strategických kontraktov pre kroky 3–4
```

**Pre každé SKU v kategórii** (aj to, ktoré research zdedí):
```
└── product-facts.md       — POVINNÝ (ceny, rozmery, špecifiká, čo neclaimovať)
```

`briefs.md` musí obsahovať stabilné ID a polia persona, angle, emotion,
`customer_voice_anchor` a best formats. Bez neho sa kroky 3–5 nemajú o čo oprieť.

## Výsledok kontroly

### Všetky povinné súbory existujú → pokračuj do kroku 3

Načítaj:
- `deep-research.md`
- `avatar-sheet.md`
- `necessary-beliefs.md`
- `offer-brief.md`
- `cep-sheet.md`
- `briefs.md`
- `product-facts.md`
- `reviews-verbatim.md` (ak existuje)

### Niektorý povinný súbor chýba → najprv over kategóriu, až potom spúšťaj research

**Nespúšťaj research len preto, že v zložke produktu chýbajú súbory.** Prejdi rozhodovací postup zhora:

1. Pozri ostatné zložky v `brands/{brand}/products/` — existuje kategória s rovnakým zákazníkom?
2. Ak áno → informuj usera a vyrob **len `product-facts.md`** s odkazom `research-source:`:

> Produkt **{product}** patrí do kategórie **{kategoria}**, ktorá už má hotový research.
> Nerobím ho znova — vyrobím len `product-facts.md` a použijem existujúce briefy.

3. Ak nie → over štyri podmienky novej kategórie (zákazník / cena / konkurencia / objekcie). Ak je splnená aspoň jedna:

> Research pre kategóriu **{kategoria}** neexistuje. Spúšťam research proces.
> *(Zdedím segmenty a sezónnosť z {príbuzná kategória}, ak existuje.)*

Pokračuj podľa `product-research-process.md` — kompletný postup od analýzy produktu po všetkých 7 dokumentov.

**Nepokračuj do kroku 3, kým research nie je kompletný** — bez neho nie je možné postaviť dôveryhodné koncepty, testovací plán ani copy. Zdedený research sa počíta ako kompletný.
