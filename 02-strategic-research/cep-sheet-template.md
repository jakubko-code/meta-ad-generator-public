# CEP Sheet — šablóna a metodika

**CEP = Category Entry Point** — konkrétna situácia alebo moment, kedy si zákazník spomenie na kategóriu produktu. Nie vlastnosť osoby, ale **scéna**: čo robí, kedy, v akom prostredí, čo v tej chvíli cíti.

Výstup: `brands/{brand}/products/{product}/marketing-research/cep-sheet.md`

---

## Prečo to existuje (a čím sa líši od zvyšku researchu)

Zvyšok researchu stojí na osi **kto × prečo nekúpi**:

| Dokument | Os |
|---|---|
| `avatar-sheet.md` | kto je zákazník |
| `necessary-beliefs.md` | čo musí uveriť pred nákupom (objekcie) |
| `deep-research.md` | akým jazykom o tom hovorí |

CEP pridáva tretiu, nezávislú os: **kedy mu produkt napadne**. Ten istý produkt má typicky 10–15 vstupných situácií a **z každej padne vlastný headline + body** bez nového researchu. Preto je CEP sheet najlacnejší násobič briefov, aký v pipeline máme.

Belief-brief odpovedá na „prečo si to nekúpi". CEP-brief odpovedá na „v akej chvíli si na to spomenie". Oba sú platné angles — ale chytajú iného človeka v inom momente, takže **v ad sete majú byť oba**.

> **Kedy CEP nesie väčšinu váhy:** produkty s nízkou bariérou a viacerými scenármi použitia (nábytok, káva, doplnky, darčeky, sezónny tovar). Situácií je veľa a objekcií málo.
> **Kedy dominujú beliefs:** drahé/rizikové nákupy a služby (elektronika z druhej ruky, klinika, B2B). Situácia je jedna, ale objekcií je šesť.
> Nikdy to nie je 100 : 0 — vyváž podľa produktu, nie podľa šablóny.

---

## Ako CEP zbierať

1. **Recenzie a fóra ako prvé** — v `deep-research.md` už väčšinou sú, len nie sú pomenované ako situácie. Hľadaj vety typu „kúpila som to keď…", „používam to hlavne ráno keď…", „konečne mám kde…". Toto sú CEP v surovom stave a rovno aj voice anchor.
2. **Doplň Exou**, čo v recenziách nie je — query píš ako opis stránky, nie ako kľúčové slová: *„diskusia kde ľudia opisujú, v akých situáciách používajú závesné kreslo"*.
3. **Sezónnosť a kalendár** — Vianoce, jar/otvorenie terasy, návrat do školy, Black Friday. Sezónny CEP je legitímny, ale má životnosť; označ ho.
4. **Až nakoniec dedukuj z produktu.** Vydedukované situácie sú slabé — nemajú verbatim oporu a Agent 7 (fact-check) ich neuchytí na nič. Označ ich `⚠️ nedoložené`.

**Cieľ: 10–15 CEP.** Menej ako 8 znamená, že si zostal pri kategórii („relax") namiesto scény („večerné víno na balkóne, keď deti zaspia").

---

## Test kvality CEP — 4 otázky

CEP je použiteľný len ak prejde všetkými štyrmi:

1. **Je to scéna, nie vlastnosť?** „Má rada pohodlie" ❌ · „Kojí o druhej v noci a potrebuje sa hojdať" ✅
2. **Vedel by som ju odfotiť?** Ak z toho nevznikne image direction, je to príliš abstraktné.
3. **Je to moment, kedy mu produkt reálne napadne?** Nie moment, kedy ho už používa.
4. **Odlišuje sa od susedného CEP?** „Ranná káva" a „raňajky na terase" sú jeden CEP. Zlúč.

---

## Šablóna tabuľky

```markdown
# CEP Sheet — {Produkt} ({Brand})

> Category Entry Points = situácie, kedy si zákazník na produkt spomenie.
> Zdroj citácií v klientskom researchi: `deep-research.md` · Segmenty: `avatar-sheet.md`
> Každý CEP je kandidát na brief (stĺpec CEP v klientskom `briefs.md`).

| # | CEP — situácia | Segment | Headline (návrh) | Body copy (návrh) | Voice anchor | Sezóna | Doložené |
|---|---|---|---|---|---|---|---|
| C01 | | | | | | celoročne | ✅ recenzia |
| C02 | | | | | | jar–leto | ⚠️ nedoložené |
```

**Stĺpce:**

| Stĺpec | Čo doň patrí |
|---|---|
| **CEP — situácia** | Scéna v 3–8 slovách. „Večer, keď deti zaspia." |
| **Segment** | Ktorý segment z `avatar-sheet.md` je v tej situácii. Môže byť cross. |
| **Headline** | 4–10 slov, hovorí do situácie — nie o produkte. Je to **návrh**, nie finálne copy. |
| **Body copy** | 1–2 vety, ktoré situáciu dokončia a napoja produkt. |
| **Voice anchor** | Citát/formulácia zákazníka z `deep-research.md`. Slúži na tón, **nie ako testimonial do obrázku**. |
| **Sezóna** | `celoročne` / `jar–leto` / `Vianoce` / … — riadi, kedy sa CEP dá nasadiť. |
| **Doložené** | `✅ recenzia` / `✅ fórum` / `⚠️ nedoložené` (vydedukované). |

---

## Ako sa CEP dostane do briefov

CEP sheet **nenahrádza `briefs.md`** — dopĺňa ho o jednu os. V `briefs.md` pribudne stĺpec **CEP**:

| ID | Segment | Angle (Belief) | **CEP** | Emócia | Voice anchor | Best formats |
|---|---|---|---|---|---|---|
| B02 | S1+S2 | B6 relax kút | **C04 večer po uspávaní** | pokoj | „môj vlastný malý ostrov" | lifestyle-action, headline |
| B11 | S1 | — | **C07 dojčenie o druhej v noci** | nežnosť | „hojdanie ju ukľudní" | ugc-lifestyle, curiosity-gap |

Dve možné väzby:

- **Belief + CEP** — silnejší brief. Objekcia je vyriešená *v konkrétnej scéne*.
- **Len CEP** (angle prázdny) — plne platný brief. Situačný uhol nepredáva produkt, predáva moment. Používaj na cold publikum a hore vo funneli.

Brief z CEP sa v kroku 3 zmení na koncept, v kroku 4 vstúpi do testovacieho plánu a následne prejde rovnakými 8 agentmi. Headline a body z CEP sheetu sú **surovina, nie hotové copy** — do `prompts-sk.json` idú až po prepísaní do hlasu značky a po scoringu.

---

## Pravidlá

- **Cena v headline je povolená** (G01, zmena 2026-08-06), ale v CEP sheete ju uvádzaj len ak je CEP cenový/promo. Sheet je živý dokument a ceny v ňom starnú — vždy ich pri použití over voči `offer-brief.md`.
- **Voice anchor ≠ testimonial.** Citát z cudzieho fóra sa nesmie objaviť v obrázku ako recenzia značky (V01, G09).
- **Sezónny CEP označ.** Nasadiť ho mimo sezóny je tichá chyba, ktorú scoring nechytí — sheet je jediné miesto, kde je to zapísané.
- **`⚠️ nedoložené` CEP sa smie použiť**, ale nesmie z neho vzniknúť claim ani citát — len situačný rámec. Agent 7 (fact-check) traceuje do `deep-research.md`, a vydedukovaná situácia tam oporu nemá.
- CEP sheet je **živý dokument.** Keď test odhalí, že situácia funguje/nefunguje, poznač to sem, nie len do `testing/learnings.md`.
