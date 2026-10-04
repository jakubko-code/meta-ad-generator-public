# Textácia katalógových reklám (DPA) + prompt pre externú AI

Nadväzuje na povinnú DPA kampaň z `kampanova-struktura.md`. Obrázok, názov a cenu skladá Meta z feedu. Tento postup rieši iba **texty okolo nich**: primárny text, nadpis, popis a tlačidlo.

Výstupom sú dve veci v jednom súbore `brands/{brand}/testing/dpa-textacia.md`:
1. **Návrh textácie od agenta** (hotové varianty na schválenie).
2. **Prompt pre ChatGPT / Gemini**, aby si človek vedel dať vygenerovať ďalšie varianty mimo agenta.

## Rozsah a hranice

- **Platí pre:** katalógové a DPA reklamy (Advantage+ catalog ads), SK aj iné trhy.
- **Neplatí pre bannery.** Copy statických bannerov ide výhradne cez B1 → Image Ad Generator (scoring, approval, hashová väzba). Prompt pre externú AI sa na bannery nepoužíva a nenahrádza žiadnu bránu.
- DPA text **nie je súčasťou B1 plánu** a netestuje sa ako izolovaný angle. Viac variantov primárneho textu v jednej reklame je v poriadku, Meta ich strieda.
- **Výstup externej AI je iba návrh.** Pred schválením ho agent skontroluje podľa rovnakých pravidiel ako vlastný návrh (sekcia „Kontrola“) a porušenia vráti alebo prepíše. Nasadzuje sa až po schválení človekom.
- Kampane, reklamy ani texty v účte agent nemení bez výslovného potvrdenia.

## Vstupy (prečítaj pred písaním)

| Zdroj | Na čo |
|---|---|
| `brands/{brand}/brand-dna/chyby-neopakovat.md` | zakázané tvrdenia, incidenty |
| `brands/{brand}/brand-dna/voice-copy-styl.md` | tón, oslovenie, slovník, CTA |
| `brands/{brand}/brand-dna/translation-glossary.md` | terminológia iných trhov + stav potvrdenia |
| `products/*/marketing-research/product-facts.md` | iba overené claims |
| katalóg cez Meta MCP (`ads_catalog_list_products`, product set) | skutočný sortiment v sete, názvy, ceny, `sale_price` |
| `health-wellness-restrikcie.md` | ak je klient wellness/zdravie |

**Najprv over sortiment v product sete.** Text musí sedieť na **každý** produkt, ktorý môže reklama ukázať. Návrh stavaný na jednu kategóriu (napr. iba kade) pri sete so saunami a vírivkami je chyba. Pozri incident klient 2026-09-14.

## Pravidlá DPA textu

1. **Platí pre celý product set.** Žiadne parametre jednej kategórie (objem, počet trysiek, výbava). Keď sa sortiment výrazne líši, navrhni radšej samostatné sety s vlastným textom.
2. **Iba claims overené pre celý set.** Claim overený pre jednu kategóriu (napr. doprava zdarma len pri kadiach) do spoločného textu nepatrí, kým ho klient nepotvrdí pre všetko.
3. **Cenu a zľavu nepíš do textu.** Na cenu slúži `{{product.price}}`. Percento zľavy je dovolené, iba ak feed posiela `sale_price` a zľava platí pre celý set.
4. **Žiadna retargetingová domnienka** („ešte váhate?“, „zabudli ste v košíku“) v broad adsete. Pripomínací tón iba pre adset čisto na retargetingové publikum.
5. **Dynamické polia Meta** v presnom zápise: `{{product.name}}`, `{{product.price}}`, `{{product.current_price}}`, `{{product.brand}}`, `{{product.description}}`. Default nadpis je `{{product.name}}`. Text s poľom musí dávať zmysel aj pri najdlhšom názve v sete.
6. **Odporúčané dĺžky:** primárny text do 125 znakov (viditeľné bez „viac“), nadpis do 40, popis do 30. Znaky prepočítaj skriptom, nie odhadom.
7. **Tlačidlo** z ponuky Meta, zosúladené s CTA inventárom značky (napr. „Nakupovať“, „Ďalšie informácie“).
8. **Iné trhy:** samostatné varianty prirodzeným jazykom trhu podľa glossary. Kým glossary nie je potvrdený, označ ich ako návrh. Menu ani cenu neprepočítavaj.

## Formát súboru `testing/dpa-textacia.md`

```markdown
# {Brand} — textácia DPA (katalógová reklama)
Dátum, kampane, product set a jeho sortiment.

## 1. Prompt pre ChatGPT / Gemini
(blok podľa šablóny nižšie, vyplnený pre značku)

## 2. Návrh textov (agent)
### {TRH}
| # | Uhol | Primárny text | Znaky | Nadpis | Popis | Tlačidlo |
### Poznámky k nasadeniu
- ktoré varianty dať do prvej reklamy
- claims zámerne vynechané a čo by ich odomklo
- riziká dynamických polí (cena bez sale_price, dlhé názvy)
```

Označenie variantov: `{TRH-PÍSMENO}{číslo}`, napr. `S1` SK, `C1` CZ.

## Šablóna promptu pre externú AI

Vyplň hranaté zátvorky z brand súborov. **Do promptu nedávaj nič neoverené** a nekopíruj text z webu doslovne. Zakázané body prenášaj konkrétne, nie všeobecne („žiadne zdravotné tvrdenia: regenerácia, krvný obeh…“).

```text
Si senior copywriter pre Meta Ads. Píšeš texty pre dynamickú katalógovú reklamu (Advantage+ catalog ads / DPA). Obrázok, názov a cenu produktu dopĺňa Meta automaticky z produktového feedu. Ty píšeš iba texty okolo nich.

## Značka
[Značka: čo predáva, cenové rozpätie, kto kupuje, pozícia značky.]

Jedna reklama zobrazuje ktorýkoľvek z týchto produktov: [sortiment v product sete]. Text preto musí sedieť na všetky naraz. Nepíš nič, čo platí iba pre jednu kategóriu (napr. [príklady parametrov]).

## Hlas
- [oslovenie: vykanie/tykanie]
- [tón, 3–5 prídavných mien + čím značka nie je]
- Bez anglicizmov, ak existuje domáci výraz. Nepoužívaj: [zakázané slová zo slovníka].
- [emoji / výkričníky / verzálky: povolené alebo nie]

## Overené fakty (používaj iba tieto)
- [claim s presnou formuláciou a podmienkou]

## Zakázané
- [každé pravidlo z chyby-neopakovat, ktoré sa týka textu, konkrétne]
- cena alebo percento zľavy v texte (cenu zobrazuje Meta sama)
- vety, ktoré naznačujú, že poznáme správanie používateľa („ešte váhate?“), pretože reklama ide aj novým ľuďom

## Dynamické polia Meta
Môžeš ich vložiť presne v tomto zápise: {{product.name}}, {{product.price}}.
- {{product.name}} je napríklad „[dva reálne názvy z feedu, krátky a dlhý]“.
- {{product.price}} je cena s menou, napríklad „[reálna cena z feedu]“.
- Nadpis s dynamickým poľom musí dávať zmysel aj pri dlhom názve.

## Úloha
Navrhni 5 variantov. Každý variant stavaj na inom uhle:
[4 uhly z researchu značky + 5. vlastný návrh]

Ku každému variantu napíš:
- Primárny text: max. 125 znakov vrátane medzier, 1–2 vety
- Nadpis: max. 40 znakov; môže obsahovať {{product.name}}
- Popis: max. 30 znakov
- Tlačidlo: [povolené tlačidlá Meta]

## Výstup
Tabuľka so stĺpcami: # | Uhol | Primárny text | Znaky | Nadpis | Popis | Tlačidlo.
Pod tabuľkou krátka kontrola: pri každom variante potvrď, že neobsahuje nič zo zoznamu „Zakázané“ a sedí na všetky produkty. Ak niečo porušuje pravidlo, prepíš to skôr, než odpovieš.

JAZYK: [SK]
```

Pod prompt pridaj **odsek pre každý ďalší trh**: jazyk, terminológia z glossary, oslovenie a tlačidlá v danom jazyku.

## Kontrola (vlastný návrh aj výstup externej AI)

- [ ] Sortiment product setu overený z katalógu; každý variant sedí na všetky kategórie v sete.
- [ ] Žiadny claim mimo overených faktov pre celý set.
- [ ] Nič zo zakázaných bodov značky (zdravie, recenzie, termíny akcií, montáž, superlatívy…).
- [ ] Oslovenie a slovník podľa voice guide.
- [ ] Dynamické polia v presnom zápise; pri cene zohľadnený chýbajúci `sale_price`.
- [ ] Dĺžky prepočítané skriptom.
- [ ] Iné trhy: prirodzený jazyk, glossary, stav potvrdenia uvedený.
- [ ] Pri nasadení: náhľad reklamy v Ads Manageri pre krátky aj dlhý názov produktu.

Po schválení človekom zapíš do súboru, ktoré varianty sú nasadené a v ktorej reklame. Výkon textov sa vyhodnocuje v Režime C na úrovni DPA reklamy, nie ako B1 test.
