# Creative Testing Tracker — návod na vyplnenie

Tracker je centrálna evidencia testov, výsledkov a poznatkov. Vedie sa **v markdown súboroch per brand**:

```
brands/<brand>/testing/
├── tracker.md     # Test Tracker — jeden riadok = jedna kreatíva/variant
├── learnings.md   # Learnings — jeden riadok = jeden overený poznatok
└── fatigue.md     # Fatigue Monitor — sledovanie únavy aktívnych kreatív
```

Súbory vznikajú **lazy** v Režime B2 po tom, čo existujú vizuálne schválené kreatívy. Režim B1 ešte nevytvára aktívne riadky trackera; jeho zdrojom pravdy je `test-plan.json` v ad sete. Nič sa nepočíta vzorcami v Exceli: odvodené hodnoty dopočítaj pri každej aktualizácii.

Tento súbor mapuje výstupy jednotlivých režimov skillu na konkrétne stĺpce, aby nový používateľ vedel kde čo patrí.

---

## tracker.md — vyplnenie v Režime B2

Po produkcii vznikne jeden riadok pre každý variant z `test-plan.json`, ktorý má vizuálny PASS a má sa nasadiť. Mapovanie:

| Stĺpec | Odkiaľ to vziať | Príklad |
|---|---|---|
| **ID** | Sekvenčné číslo, vlastná konvencia | 001, 002... |
| **Plan ID** | `test-plan.json.plan_id` | `TP-YYYY-MM-DD-HOOKS` |
| **Concept ID** | `test-plan.json.variants[].concept_id` | `C01` |
| **Dátum spustenia** | Deň, kedy reklama ide live | 12.06.2026 |
| **Kampaň** | Názov kampane z B1/E plánu | „TEST — Brand — ABO" |
| **Adset** | Názov zložky `product-image-ads/<YYYY-MM-DD-adset>/` | „YYYY-MM-DD-hook-test" |
| **Produkt** | Produkt z konceptu / briefu | „hero-produkt" |
| **Avatar** | Pole **Avatar** z výstupu Režimu A (= persona z `avatar-sheet.md`) | „Sedavé zamestnanie" |
| **Angle** | Pole **Angle** z výstupu Režimu A (= angle briefu z `briefs.md`) | „Bolesť chrbta po sedení nie je normálna" |
| **Typ hooku** | Typ z knižnice hookov (`tvorba-kreativ.md`) | „Situačný" |
| **Popis hooku (0–3 s)** | Konkrétny popis Hook A alebo Hook B scény / headline statiku | „Osoba vstáva od PC, grimasa + text" |
| **Formát** | Video/statik/carousel + dĺžka; pri statiku aj `template_number` a názov | „Statik T01 headline-template" |
| **Kreatíva (súbor)** | Odkaz na PNG v `product-image-ads/.../outputs/`; priečinok je `{NN}-{template_name}-{concept_id}` | „01-headline-template-C01" |
| **Kreatíva SHA** | Prvých 12 znakov `sha256` tohto PNG z `outputs*/manifest.json` — presne verzia s vizuálnym PASS | `3f9a1c07b2e4` |
| **Meta Ad ID / Adset ID** | Pred spustením `—`; po reálnom nasadení ID z Ads Managera alebo `ads_get_ad_entities` | `120214…` |
| **Verzia** | v1 pri prvom nasadení, v2/v3 pri iterácii | v1 |
| **Stav** | **Skutočný** stav v účte: Pripravená / Aktívna / Pauza / Vypnutá. Mení sa iba po potvrdenej zmene v účte | „Pripravená" |

**Dôležité:** ak koncept má Hook A aj Hook B (alebo Variant A/B pri statiku), **každý dostane svoj riadok** — sú to dve odlišné kreatívy s vlastným ID, aj keď zdieľajú telo/koncept. Pole „Popis hooku" je to, čo ich odlišuje.

**Jedna kreatíva, viac nasadení:** keď ten istý PNG (rovnaké Kreatíva SHA) beží vo viacerých reklámach — duplikácia do ďalšieho ad setu, škálovacia kampaň — každé nasadenie má vlastný riadok s vlastným Meta Ad ID. Výsledky sa párujú podľa Meta Ad ID; hľadanie podľa názvu reklamy je iba záloha, keď ID ešte chýba.

Metrické stĺpce (Obdobie metrík, Spend, Impresie, Outbound CTR, Link CTR, CPC, Konverzie, CPA, Verdikt, Ďalší krok, Stav potvrdený, Poznámka) ostávajú **prázdne** (`—`) až do prvého vyhodnotenia — nevypĺňaj odhady. Meta Ad ID a Adset ID doplň hneď po reálnom nasadení a Stav zmeň z Pripravená na Aktívna až vtedy.

### Šablóna tracker.md

```markdown
# Test Tracker — <brand>

Legenda verdiktov: Škálovať / Iterovať / Sledovať / Vypnúť / Predbežná

| ID | Plan ID | Concept ID | Dátum spustenia | Kampaň | Adset | Meta Adset ID | Meta Ad ID | Produkt | Avatar | Angle | Typ hooku | Popis hooku | Formát | Kreatíva (súbor) | Kreatíva SHA | Verzia | Stav | Obdobie metrík | Spend (€) | Impresie | Outbound CTR | Link CTR | CPC | Konverzie | CPA | Verdikt | Ďalší krok | Stav potvrdený | Poznámka / Učenie |
|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|
```

---

## tracker.md — aktualizácia po Režime C

Po kontrole objemu dát a vyhodnotení (Režim C) sa **existujúce riadky aktualizujú** (nevytvárajú sa nové), pokiaľ nejde o nový variant:

| Stĺpec | Odkiaľ to vziať |
|---|---|
| **Obdobie metrík** | Presné `time_range` čítania, napr. `2026-09-01–2026-09-07`, + atribučné okno a optimalizačný event, ak sa líšia od účtu |
| **Spend (€), Impresie, Outbound CTR, Link CTR, CPC, Konverzie, CPA** | Priamo z `ads_get_ad_entities` (MCP) podľa Meta Ad ID alebo z manuálneho exportu. Outbound CTR = `outbound_clicks_ctr`; pri nulových impresiách N/A |
| **Verdikt** | **Odporúčanie** Režimu C: Škálovať / Iterovať / Sledovať / Vypnúť / Predbežná |
| **Ďalší krok** | Konkrétna navrhovaná akcia — napr. „Presunúť cez Post ID do hlavnej kampane", „Nový hook, telo nechať" |
| **Poznámka / Učenie** | Kľúčový diagnostický záver v skratke — napr. „Vysoký hook rate, slabé CTR — CTA problém" |
| **Stav** | **Nemeň podľa verdiktu.** Verdikt je odporúčanie; v účte sa nič nestane samo. Stav zmeň až keď človek akciu vykonal alebo ju overíš cez `effective_status` v MCP |
| **Stav potvrdený** | Kedy a ako bol Stav overený, napr. „2026-09-08, MCP effective_status PAUSED" alebo „2026-09-08, potvrdil Pavol" |

**Historické čísla neprepisuj naslepo.** Pri ďalšom vyhodnotení prepíš metriky v riadku novým obdobím a predošlé čítanie (obdobie + kľúčové čísla + verdikt) presuň do stĺpca Poznámka alebo do `testing/snapshots/<plan_id>.md`. Inak sa stratí, na akých dátach vznikol pôvodný verdikt.

**Pravidlo „Predbežná":** ak kontrola objemu dát nebola splnená, Verdikt = „Predbežná" a riadok sa **neuzatvára** — pri ďalšom vyhodnotení (o týždeň) sa aktualizuje znova, kým nedostane definitívny verdikt.

---

## tracker.md — iterácia (nová verzia)

Keď z verdiktu „Iterovať" vznikne upravená kreatíva (nový hook, nové CTA...), je to **nový riadok** s novým ID, ale:
- **Verzia** = v2 (alebo v3...)
- **Angle** a **Avatar** zostávajú rovnaké (ak sa nemenia)
- **Popis hooku** alebo iný zmenený prvok sa aktualizuje
- V poli **Poznámka** uveď z čoho táto verzia vychádza, napr. „Iterácia v1 (ID 003) — zmenený CTA z 'Zistiť viac' na 'Objednať sa online'"

Takto vidno v tabuľke celú históriu iterácií jedného konceptu pri filtrovaní podľa Avatara/Angle. Pri regenerovaní vizuálu platí pravidlo pipeline: regeneruj len chybné varianty, nemaž hotové výstupy.

---

## learnings.md — kedy a čo zapísať

Nie každý riadok trackera generuje poznatok. Zapíš do `learnings.md` len keď je výsledok **prenositeľný** — platí aj pre iné kampane/produkty, nie len pre tento jeden test.

> **Hypotéza → Learning:** ak si pred testom sformuloval hypotézu (pozri `testovanie-metodika.md`), zápis do Learnings je jej priame pokračovanie. Potvrdená hypotéza = overený poznatok. Vyvrátená hypotéza = tiež poznatok (často cennejší — prekvapil ťa). Bez hypotézy prehratý test nič nezanechá; s ňou sa aj „neúspech" stane pravidlom do budúcna.

| Stĺpec | Ako vyplniť |
|---|---|
| **ID** | L001, L002... (samostatná séria od trackera) |
| **Dátum** | Dátum vyhodnotenia |
| **Typ poznatku** | Hook / Angle / Formát / Avatar / Štruktúra / Vizuál |
| **Čo sme zistili** | Jedna veta, formulovaná ako **prenositeľné pravidlo**, nie popis výsledku. Nie: „Banner 2 mal CTR 2,9 %" — ale: „Situačný hook (problém v deji) má vyšší CTR ako talking head pri sedavom avatarovi". Ak vychádza z hypotézy, uveď či ju potvrdil alebo vyvrátil. |
| **Kontext** | Odkaz na ID v tracker.md, odkiaľ poznatok pochádza |
| **Dôveryhodnosť** | „Predbežná (1 test)" alebo „Overená (viac testov)" — jeden test nestačí na pravidlo |
| **Použiť pri...** | Kde tento poznatok aplikovať nabudúce — segment, avatar, typ produktu |

**Prepojenie s `segmenty.md`:** ak poznatok platí len pre konkrétny segment (napr. lead-gen služby), uveď to v poli „Použiť pri..." — poznatky z e-com sa nemusia preniesť na B2B. Prenositeľné poznatky, ktoré sa týkajú copy/štýlu brandu, zváž premietnuť aj do `brands/<brand>/brand-dna/chyby-neopakovat.md`.

### Šablóna learnings.md

```markdown
# Learnings — <brand>

| ID | Dátum | Typ poznatku | Čo sme zistili | Kontext | Dôveryhodnosť | Použiť pri... |
|----|----|----|----|----|----|----|
```

---

## fatigue.md — vyplnenie (Režim D)

Fatigue Monitor sleduje **aktívne kreatívy v hlavnej kampani** (po škálovaní), nie testovacie varianty v sprint adsete.

| Stĺpec | Odkiaľ to vziať |
|---|---|
| **ID** | F001, F002... |
| **Kreatíva** | Názov + odkaz na ID z tracker.md (odkiaľ bola škálovaná) |
| **Formát, Dátum spustenia** | Vyplň manuálne |
| **Vek (dni)** | **Dopočítaš ty:** dnešný dátum − Dátum spustenia |
| **Frequency, CTR týždeň 1, CTR aktuálny, CPA zmena (%)** | Z `ads_get_ad_entities` s `time_increment=7` — pozri `meta-mcp-playbook.md` |
| **Pokles CTR (%)** | **Dopočítaš ty:** (CTR týždeň 1 − CTR aktuálny) / CTR týždeň 1 × 100 |
| **Fatigue skóre** | **Dopočítaš ty** podľa vzorca z `fatigue-detector.md`: pokles CTR 40 % + frequency 30 % + vek 20 % + CPA 10 %; pásmové hranice podľa tabuliek tamtiež |
| **Stav** | Slovný ekvivalent skóre podľa jedinej tabuľky pásiem vo `fatigue-detector.md` |
| **Odporúčanie** | Text podľa Stavu, zodpovedá rotačnému plánu z `fatigue-detector.md` |

**Vstupné hodnoty sú len:** Dátum spustenia, Frequency, CTR týždeň 1, CTR aktuálny, CPA zmena. Zvyšok dopočítaš pri každej aktualizácii — **prepíš staré odvodené hodnoty novými**, nikdy nenechávaj vek/skóre z minulého týždňa.

**Kedy aktualizovať:** týždenne pre všetky aktívne kreatívy v hlavnej kampani. Keď fatigue skóre dosiahne pásmo Raná únava (≥ 46), príprava náhrady ide cez A → B1 → produkciu → B2; nový riadok vznikne až pre reálny PASS súbor. Skóre je signál, nie automatický pokyn na pauzu.

### Šablóna fatigue.md

```markdown
# Fatigue Monitor — <brand>

Posledná aktualizácia: <YYYY-MM-DD>
Stavy: Čerstvá (0–25) / Zdravá (26–45) / Raná únava (46–65) / Stredná únava (66–80) / Kritická (81–100)

| ID | Kreatíva | Formát | Dátum spustenia | Vek (dni) | Frequency | CTR týždeň 1 | CTR aktuálny | Pokles CTR (%) | CPA zmena (%) | Fatigue skóre | Stav | Odporúčanie |
|----|----|----|----|----|----|----|----|----|----|----|----|----|
```

*(Pásma sú prevzaté z `fatigue-detector.md`; pri zmene uprav obe miesta naraz.)*

---

## Celý cyklus — ako súbory spolupracujú

```
Režim A → B1 test-plan.json → produkcia → B2
                                  └──► tracker.md: nové riadky (v1), Stav = Pripravená
                              │
                              ▼
Režim C (vyhodnotenie) ──► tracker.md: aktualizácia metrík + Verdikt
                              │
              ┌───────────────┼────────────────┐
              ▼               ▼                ▼
         Škálovať        Iterovať          Vypnúť
              │               │                │
              ▼               ▼                ▼
    fatigue.md:         tracker.md:       tracker.md: Verdikt = Vypnúť;
    nový riadok F00x    nový riadok v2     Stav = Vypnutá až po potvrdení
              │
              ▼ (skóre 46+)
    Nový cyklus A → B1 → kroky 5–7 → B2
              │
Prenositeľné zistenia ──► learnings.md (kedykoľvek v procese)
```
