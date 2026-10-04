# Kampaňová architektúra účtu

Toto je Režim E — návrh alebo reštruktúra **celej architektúry Meta Ads účtu** (koľko kampaní, CBO/ABO, ako rozdeliť Prospecting/Retargeting/Retention, naming na úrovni účtu). Nadväzuje na Režimy A–D: tie riešia *čo sa testuje a ako sa to vyhodnocuje*, tento režim rieši *kde to v účte trvalo býva*.

> **Filozofia:** zlá štruktúra = neustále hasenie požiarov. Dobrá štruktúra = algoritmus robí väčšinu práce sám. Každé rozdrobenie účtu na viac kampaní/adsetov/publík rozdeľuje konverzné dáta na menšie kúsky — algoritmus dostane menej signálu z každého kúska a učenie trvá dlhšie. **Moderná prax je konsolidácia**: menej kampaní s viac dátami, menej adsetov s viac konverziami, nech algoritmus optimalizuje naprieč väčším poolom.

## Kedy použiť tento režim

- Zakladáš nový účet od nuly.
- Klient má neprehľadný, rozdrobený účet („20 kampaní a je to chaos") a treba konsolidovať.
- Otázka „CBO alebo ABO?" na úrovni celého účtu (nie testu — to rieši `testovanie-metodika.md`).
- Treba rozhodnúť, ako rozdeliť Prospecting/Retargeting/Retention.

## Potrebný kontext pred návrhom

**Musíš mať:**
1. Business ciele — hlavný cieľ (predaj/leady/povedomie), cieľová CPA/ROAS, úroveň budgetu (denný/mesačný).
2. Súčasný stav (ak ide o reštruktúru) — počet kampaní/adsetov/reklám, objem konverzií, čo funguje a čo nie.
3. Publiková stratégia — akvizícia (prospecting), odlišné segmenty zákazníkov, prípadný dôvod na samostatný retargeting (sekcia „Retargeting“ nižšie).

**Silne odporúčané:**
4. Produktová štruktúra — jeden produkt alebo viac, rôzne cenové hladiny, rôzne nákupné cesty.
5. Geografický rozsah — jedna krajina alebo viac, rôzne jazyky.

**Pekné mať:**
6. Historický kontext — ako dlho účet beží, minulé experimenty so štruktúrou, sezónne vzory.

## CBO vs. ABO na úrovni účtu

| Faktor | CBO | ABO |
|---|---|---|
| Alokácia budgetu | Necháš rozhodnúť algoritmus | Potrebuješ manuálnu kontrolu |
| Počet adsetov | 3–5 adsetov | 1–2 adsety ALEBO testovanie |
| Objem konverzií | Vysoký (50+/týždeň/adset) | Nižší, potrebuješ garantovaný spend |
| Testovanie | Netestuješ publiká | Testuješ konkrétne publiká |

**CBO best practices:** minimálne 3 adsety (dáva algoritmu možnosti), podobná veľkosť publík naprieč adsetmi, nepoužívaj na striktné A/B testy publík.

**ABO best practices:** na testovanie konkrétnych publík, keď musí byť budget garantovaný per segment, pri retargetingu s malými publikami.

> **Testovacia (Sandbox) kampaň je vždy ABO** — bez ohľadu na to, či zvyšok účtu beží na CBO. Či sa testuje v Sandboxe alebo priamo v Prospectingu, rieši sekcia nižšie „Kde testovať nové kreatívy".

## Retargeting: predvolene ho robí Prospecting

Broad / Advantage+ kampaň optimalizovaná na nákup alebo lead **remarketuje sama**: kým je teplé publikum dostupné, Meta mu reklamu ukazuje, lebo konvertuje lacnejšie. Samostatná retargeting kampaň nad tým súťaží s vlastným Prospectingom o tých istých ľudí, zvyšuje frequency a nafukuje reportované výsledky konverziami, ktoré by prišli aj bez nej (e-mail, organika, priama návšteva). Zdroj a detail: `references/meta/meta-struktura-tactics.md` (Loomer 2026-05, Istvanic 2026-09).

**Predvolene:** trvalé kampane sú Prospecting (+ DPA pri e-commerce). Samostatný retargeting sa pridáva **iba s pomenovaným dôvodom**, ktorý sa zapíše do architektonického plánu:

| Dôvod | Signál | Ako |
|---|---|---|
| **Drahý produkt s dlhým rozhodovaním** | frequency Prospectingu nad ~2 už pri nízkom spende; zákazníci sa rozhodujú týždne až mesiace | malé teplé publikum (web, engageri, e-mail list) ako podpora e-mailovej komunikácie; akvizíciu riešiť aj inými kanálmi |
| **Kampaň optimalizovaná na TOF akciu** (klik, LPV, ThruPlay, video views) | Meta pri takomto cieli nerieši kvalitu | obmedziť na e-mail list alebo zapojených návštevníkov |
| **Vedome riadený rozpočet na teplé publikum** | klient chce vidieť a kontrolovať, koľko ide na teplých / existujúcich | jeden ad set s vlastným rozpočtom |

- **Strop:** samostatný retargeting spolu **5–10 % rozpočtu účtu** (DPA sa sem nepočíta, má vlastné pravidlo nižšie). Pri 20–30 % už kanibalizuje Prospecting.
- **Varovné signály:** frequency retargeting kampane nad 3 / mesiac; najlepší ROAS v účte pri vysokom podiele view-through; statik v Prospectingu s frequency ~3, keď video v tej istej kampani má ~1,2 (statik v skutočnosti remarketuje).
- **Overenie inkrementality:** Meta incremental attribution alebo holdout. Pri existujúcej samostatnej retargeting kampani navrhni **test vypnutia na 2 týždne** a sleduj celkové tržby (nie ROAS kampane). Bez zmeny → nebola inkrementálna, rozpočet do Prospectingu. Pokles → vrátiť so stropom vyššie. Vypnutie iba s výslovným súhlasom človeka a mimo sezónnych výkyvov.
- **Predpoklad:** správne Audience Segments a funkčné vylúčenia (implementačný checklist). Bez nich sa retargeting od prospectingu vyhodnotiť nedá.

## E-commerce: katalógová kampaň (DPA) beží vždy

**Povinné pravidlo:** každá architektúra e-shopu (segment e-com / DR, predaj cez web s košíkom alebo dopytovým košíkom) obsahuje **trvalú katalógovú kampaň z produktového feedu** — Advantage+ catalog ads / DPA. Platí pre Štruktúry A, B aj C, bez ohľadu na budget. Nie je to fáza „neskôr“, ani doplnok pre veľké účty. Beží stále vedľa Prospecting a Sandboxu, **nepauzuje sa počas testov** a z rozpočtu sa vypína iba na výslovný pokyn človeka.

**Prečo:** ručná kreatíva pokryje pár hero produktov. Zvyšok sortimentu a návštevníkov, ktorí si prezreli konkrétny produkt, obslúži iba feed. Bez DPA účet stráca najlacnejšie konverzie a teplé publikum sa nevyužije.

**Tvar kampane:**

```
📁 [CONV] Katalóg - DPA - [Trh]          ← trvalá, samostatný rozpočet
  └── 📂 DPA - Retargeting - ViewContent/AddToCart 14–30d - bez kupujúcich 180d
        └── 📄 CAT - Carousel/Collection - Product set Všetky produkty
  └── 📂 DPA - Broad - Advantage+ catalog   ← doplniť, keď je retargeting pool malý
        └── 📄 CAT - Single/Carousel - Product set Hero kategória
```

- **Cieľ:** Sales, katalóg zapnutý na úrovni kampane, optimalizácia na Purchase (pri nízkom objeme dočasne AddToCart).
- **Nový účet bez publika:** začni broad katalógovou vetvou (Meta sama cieli na ľudí so záujmom o produkty z feedu). Retargetingovú vetvu zapni, keď publikum ViewContent 30d dosiahne použiteľnú veľkosť (orientačne 1 000+ ľudí). Aj pri malom účte teda DPA beží od začiatku, len v inej vetve.
- **Rozpočet:** orientačne 10–20 % účtu, pri malom účte nie menej ako je nutné na ~1 konverziu/deň v cieľovom evente. Pri pravidle 60-30-10 sa DPA počíta do trvalých 60 %.
- **Vylúčenia:** kupujúci 180d (pri nízkej frekvencii nákupu, napr. drahý tovar), aby DPA neukazovala práve kúpený produkt. Ak existuje synchronizovaný zoznam zákazníkov (e-mail nástroj), vylúč aj ten. Pri obchode s veľkým sortimentom, kde DPA slúži ako cross-sell (doplnok ku kúpenému), vylučuj kupujúcich konkrétneho produktu / product setu, nie všetkých.
- **Kontrola, že DPA nie je iba „pokladník“:** DPA v Ads Manageri často vyzerá ako najlepšia kampaň, lebo jej ROAS tvoria existujúci a takmer rozhodnutí zákazníci. Preto:
  - hodnoť ju na **7-day click** (bez view), nie podľa in-platform ROAS s view-through,
  - týždenne pozri rozpad podľa **Audience Segments**; ak **nad 30 % spendu DPA ide na Existing Customers**, sprísni vylúčenia,
  - DPA nesmie byť najväčšou kampaňou v účte; ak ňou je, navrhni presun rozpočtu do Prospectingu.
  Toto pravidlo trvalej DPA nemení, iba ju drží inkrementálnu.
- **Kreatíva:** skladá ju Meta z feedu, nie z bannerov tejto pipeline. Kvalitu určujú fotky, názvy a ceny vo feede, product sety a voliteľný rámik/overlay katalógu. Hook ani koncept sa pre DPA nenavrhuje a DPA **nie je súčasťou B1 testovacieho plánu**. Texty okolo katalógu (primárny text, nadpis, popis) a prompt pre externú AI rieši `katalogova-textacia.md`. Pri únave pozri `fatigue-detector.md`.
- **Trhy:** jeden katalóg na trh/menu alebo jeden katalóg s krajinovými/jazykovými feedmi; cieľová URL a cena musia sedieť s trhom.

**Predpoklady (patria do implementačného checklistu, nie do „neskôr“):**
1. Produktový katalóg v Commerce Manageri a feed (WooCommerce/Shoptet/Shopify plugin alebo XML feed) s `id`, `title`, `price`, `availability`, `link`, `image_link`.
2. Pixel/dataset prepojený s katalógom.
3. Eventy `ViewContent`, `AddToCart`, `Purchase` s `content_ids`, ktoré sa **zhodujú s `id` vo feede** (inak DPA nevie priradiť produkt). Overiť cez `ads_catalog_get_dynamic_ads_health` / diagnostiku katalógu.
4. Product set aspoň „Všetky produkty skladom“.

Ak niektorý predpoklad chýba, architektúra DPA **aj tak obsahuje** a chýbajúci krok označí ako blokujúci. Nevynechá ju.

Výnimka: segment nie je e-commerce (lead-gen, služby, B2B, event, infoprodukt bez feedu). Vtedy DPA nepoužívaj.

## Odporúčané štruktúry účtu

### Štruktúra A — Zjednodušená (väčšina SK/CEE účtov)

**Pre koho:** účty do ~10 000 €/mesiac, jeden produkt/ponuka. **Toto je predvolená štruktúra pre väčšinu klientov agentúry.**

```
📁 [CONV] Prospecting
  └── 📂 Broad / Advantage+ (1 adset)
        ├── 📄 Reklama 1: hlavná kreatíva
        ├── 📄 Reklama 2: variácia A
        ├── 📄 Reklama 3: variácia B
        └── 📄 Reklama 4: testovacia kreatíva

📁 [CONV] Katalóg - DPA               ← e-commerce: povinné, beží stále
  └── 📂 DPA - Broad alebo Retargeting ViewContent/ATC 30d
        └── 📄 CAT - Product set Všetky produkty

📁 [CONV] Retargeting                 ← VOLITEĽNÉ, iba s dôvodom zo sekcie „Retargeting“, max 5–10 % rozpočtu
  └── 📂 Teplé publikum / e-mail list (1 adset)
```

**Spolu: 1 kampaň, 1 adset** + pri e-commerce trvalá DPA kampaň (1 adset); retargeting iba s pomenovaným dôvodom. Zodpovedá **Tier 3 — Sprint Isolation** z `testovanie-metodika.md`. Nové kreatívy sa testujú v Sandboxe alebo priamo v Prospectingu (sekcia „Kde testovať nové kreatívy“).

### Štruktúra B — Štandardná (rastúce účty)

**Pre koho:** účty ~10 000–50 000 €/mesiac, overená kreatíva.

```
📁 [CONV] Prospecting — Studené publikum
  └── 📂 CBO
        ├── 📂 Broad / Advantage+
        │     └── [4–6 reklám]
        └── 📂 Lookalike alebo broad segment (test podľa potreby)
              └── [4–6 reklám]

📁 [CONV] Katalóg - DPA               ← e-commerce: povinné, beží stále
  └── 📂 ABO/CBO
        ├── 📂 DPA - Prezerali/ATC 14–30d - bez kupujúcich
        └── 📂 DPA - Broad - Advantage+ catalog

📁 [CONV] Retargeting                 ← VOLITEĽNÉ, iba s dôvodom, max 5–10 % rozpočtu
  └── 📂 ABO
        └── 📂 Návštevníci webu 30d + engageri (bez kupujúcich)
              └── [3–4 reklamy]
```

**Spolu: 1 kampaň, 2 adsety** + pri e-commerce trvalá DPA kampaň; retargeting (1 adset) iba s pomenovaným dôvodom. Opustený košík pokrýva DPA retargetingová vetva, samostatný adset netreba. Zodpovedá **Tier 2 — Persona Isolation**.

### Štruktúra C — Škálovaná (veľké účty)

**Pre koho:** účty 50 000+ €/mesiac, viacero produktov/ponúk.

```
📁 [CONV] Prospecting — Primárny produkt
  └── 📂 CBO
        ├── 📂 Broad / Advantage+ Shopping
        └── 📂 Interest stack (testovanie)

📁 [CONV] Prospecting — Sekundárny produkt
  └── 📂 CBO
        └── 📂 Advantage+ Shopping

📁 [CONV] Katalóg - DPA               ← e-commerce: povinné, beží stále
  └── 📂 ABO/CBO
        ├── 📂 DPA - Prezerali produkt 30d / Opustený košík 14d - bez kupujúcich
        └── 📂 DPA - Broad - Advantage+ catalog (cross-sell pri veľkom sortimente)

📁 [CONV] Retencia — Existujúci zákazníci   ← VOLITEĽNÉ, iba s dôvodom
  └── 📂 ABO
        ├── 📂 Kupujúci 30–180d (nová ponuka, doplnky)
        └── 📂 Neaktívni 180d+ (reaktivácia)
```

**Spolu: 3 kampane, 6 adsetov** (bez retencie). Retargeting a retencia spolu max 5–10 % rozpočtu, s dôvodom zo sekcie „Retargeting“ a s vlastnou ponukou (inak ich Prospecting pokryje sám). Zodpovedá **Tier 1 — Concept Isolation**.

### Štruktúra D — Lead generácia

**Pre koho:** B2B, služby, vysoká cenová hladina.

```
📁 [LEADS] Prospecting
  └── 📂 Broad / Advantage+ publikum (1 adset)
        └── voliteľne: záujmy, job title alebo LAL iba ako návrh publika (Advantage+ audience)
            v tom istom adsete, nie ako samostatné adsety

📁 [LEADS] Retargeting                ← VOLITEĽNÉ, iba s dôvodom, max 5–10 % rozpočtu
  └── 📂 ABO
        └── 📂 Návštevníci webu 60d + diváci videa 50%+ + otvorili lead formulár (1 adset)

📁 [LEADS] Nurture                    ← VOLITEĽNÉ: dlhý predajný cyklus, leady bez uzavretia
  └── 📂 ABO
        └── 📂 Leady (nekonvertovali na zákazníka)
```

**Spolu: 1 kampaň, 1 adset** + retargeting / nurture iba s pomenovaným dôvodom. Detailné cielenie, job title a lookalike sú dnes pri Advantage+ publiku **návrhy**; samostatné adsety podľa nich dosiahnu tých istých ľudí a rozdrobia malý lead-gen objem. Samostatný adset podľa cielenia iba ako **vedomý test publika** (ABO, dočasne). Kvalitu leadov rieš konverzným eventom (kvalifikovaný lead) a pri zlých segmentoch radšej value rules než obmedzením veku či pohlavia. Pri B2B s drahou službou je retargeting častejšie oprávnený (dlhé rozhodovanie).

## Mapovanie na Tier systém (Režim B1)

| Veľkosť účtu | Štruktúra (tento režim) | Zodpovedajúci Tier (Režim B1) |
|---|---|---|
| Malý (do ~10 000 €/mesiac) | Štruktúra A | **Tier 3 — Sprint Isolation** |
| Rastúci (~10–50 000 €/mesiac) | Štruktúra B | **Tier 2 — Persona Isolation** |
| Veľký (50 000+ €/mesiac) | Štruktúra C alebo D | **Tier 1 — Concept Isolation** |

> **Pri Štruktúre D** Tier určuje objem leadov, nie štruktúra; pri malom lead-gen účte je to prakticky vždy Tier 3.
>
> **Pre väčšinu SK/CEE klientov platí kombinácia Štruktúra A + Tier 3.** Nie je to kompromis z núdze — je to správna dvojica pre daný objem dát. Chyba nastáva, keď niekto použije Štruktúru A (2 kampane), ale skúša testovať podľa Tier 1 logiky (veľa paralelných adsetov) — vtedy sa dáta fragmentujú na oboch úrovniach naraz.

## Kde testovať nové kreatívy: Sandbox alebo priamo v Prospectingu

Štruktúry vyššie sú **trvalé** (Prospecting, DPA a prípadný retargeting s dôvodom). Nové kreatívy z Režimu B1 sa testujú jedným z dvoch spôsobov. Voľbu zapíš do architektonického plánu (Režim E) a pri každom teste do hypotézy / poznámky v B1:

```
Účet:
├── [CONV] Prospecting          ← trvalá, škálovacia kampaň (podľa štruktúry vyššie)
│                                  In-place: nové reklamy pribúdajú priamo sem.
├── [CONV] Katalóg - DPA        ← trvalá pri e-commerce, beží aj počas testov
├── [CONV] Retargeting          ← iba s dôvodom (sekcia „Retargeting“)
└── [CONV] Sandbox / Test       ← iba pri voľbe Sandbox (vždy ABO, Tier podľa budgetu)
                                    Víťaz sa presúva cez Post ID do Prospectingu.
```

| Spôsob | Kedy | Víťaz |
|---|---|---|
| **Sandbox (ABO)** | test má dať **prenositeľný poznatok** (`test_design: isolated`, agentúrne learnings), treba garantovaný spend na variant, alebo sa nový koncept nesmie dotknúť výkonu hlavnej kampane | presun cez Post ID do Prospectingu; počítaj s Test → Scale friction, výsledok je indikácia |
| **In-place v Prospectingu** | malý účet (Štruktúra A / Tier 3), kde rozhoduje výkon v reálnom prostredí viac než čistá izolácia; `concept-comparison` alebo `pilot` | ostáva, kde je; netreba ho presúvať ani mu **vynucovať rozpočet vypínaním ostatných** reklám. Slabé reklamy vypni až po dátovej bráne |

- Pri in-place teste Meta rozdeľuje spend nerovnomerne; nová reklama môže dostať málo impresií. Dátová brána (`minimum_impressions_per_variant`) je preto rovnako povinná; ak ju variant po rozumnom čase nesplní, verdikt je „nedostal doručenie“, nie „prehral“.
- Reklama v Prospectingu môže mať viac primárnych textov, nadpisov a médií naraz (Meta skladá kombinácie). To zvyšuje výkon, ale znemožňuje čítať jednotlivú premennú. Pre `isolated` test preto použi Sandbox alebo reklamy s jedným textom a nadpisom.
- Zdroj rozdielu: `references/meta/meta-testovanie-tactics.md` (Loomer 2026-05).

Rozpočtovo to zodpovedá pravidlu **60-30-10** (`testovanie-metodika.md`): 60 % do overených trvalých kampaní, 30–40 % kombinovane do variácií víťazov a testov (Sandbox alebo in-place podiel v Prospectingu).

## Ad set guidelines

**Konverzie potrebné na adset (týždenne):**

| Týždenné konverzie | Stav učenia | Odporúčanie |
|---|---|---|
| 50+ | Optimálne učenie | Udrž štruktúru |
| 25–50 | Obmedzené učenie | Zváž konsolidáciu |
| 10–25 | Problémy | Konsoliduj alebo zvýš budget |
| <10 | Neučí sa | Zlúč s inými adsetmi |

**Veľkosť publika podľa budgetu:**

| Denný budget | Minimálne publikum | Ideálne publikum |
|---|---|---|
| 50 € | 500 000 | 2 000 000+ |
| 100 € | 1 000 000 | 5 000 000+ |
| 500 € | 5 000 000 | 10 000 000+ |
| 1 000+ € | 10 000 000+ | Broad/Advantage+ |

**Reklám na adset:** minimum 3 (algoritmus potrebuje možnosti), ideálne 4–6, maximum okolo 10 (nad tým sa ťažko získava signál).

## Dôležitá korekcia: broad namiesto lookalike

Staršia prax (do cca 2024) uprednostňovala pri prospectingu lookalike publiká (LAL) ako predvolenú voľbu. **Post-Andromeda dáta z `creative-sequencing.md` ukazujú opak** — broad publikum dnes prináša vyššiu návratnosť než lookalike (rádovo o desiatky percent), pretože Andromeda dnes robí segmentáciu sama na základe kreatívy, nie na základe vopred definovaného publika.

**Praktický dôsledok:** pri návrhu Prospecting adsetov (Štruktúra A, B, C, D) **defaultuj na broad/Advantage+**, nie na LAL. LAL ponechaj ako legitímnu testovaciu vetvu (napr. v Štruktúre B), nie ako automaticky správnu voľbu.

## UTM parametre — agentúrny štandard

Cieľová URL reklamy je **čistá, bez UTM** (napr. `https://www.example.sk/masazne-kresla-2/`). UTM sa zapisujú **iba do poľa „Parametre URL“** (URL parameters) na úrovni reklamy, vždy v tomto tvare:

```
utm_source=facebook&utm_medium=cpc&utm_campaign={{campaign.name}}&utm_id={{campaign.id}}&utm_term={{adset.name}}&utm_content={{ad.id}}&utm_source_platform={{site_source_name}}
```

- Dynamické makrá doplní Meta, ručne písané hodnoty (`utm_content=C01`, vlastné názvy kampaní) sa nepoužívajú. Koncept sa páruje cez Meta Ad ID v `tracker.md`.
- Naming kampaní a ad setov sa vďaka makrám prenáša do analytiky — preto dodržuj naming konvenciu nižšie.
- Pri kontrole reklám (aj katalógových) over, že URL neobsahuje `?utm_` a pole „Parametre URL“ má presne tento reťazec.

## Naming konvencia — jednotná naprieč celým skillom

```
Kampaň:   [CIEĽ] [FUNNEL FÁZA] - [POPIS] - [DÁTUM/VERZIA]
Adset:    [TYP PUBLIKA] - [NÁZOV PUBLIKA] - [DETAIL CIELENIA]
Reklama (trvalá kampaň):    [FORMÁT] - [ANGLE/HOOK] - [VERZIA]
Reklama (testovacia Sandbox): [FORMÁT] - [AWARENESS STAGE]_[ANGLE/HOOK] - [KONŠTANTA] - v[X]
```

**Príklady kampaní:**
- `[CONV] Prospecting - Broad Focus - Q1 2026`
- `[CONV] Retargeting - Teple publikum` (iba s dôvodom)
- `[CONV] Sandbox - Test - Máj 2026`
- `[LEADS] Prospecting - Odvetvové cielenie`

**Príklady adsetov:**
- `BROAD - Advantage+ publikum`
- `RTG - Web 30d - Bez kupujúcich`
- `LAL - Kupujúci 2% - test`

**Príklady reklám (trvalá kampaň):**
- `VID - Pain Hook - v1`
- `IMG - UGC štýl - Sociálny dôkaz`

**Príklady reklám (testovacia Sandbox — so stopou premennej a awareness stage):**
- `VID - PROBLEM_HookA-Sedenie - TeloX - v1`
- `IMG - UNAWARE_Situacia-PocitacovaPraca - StatikY - v1`

Keď sa víťaz presunie zo Sandboxu do trvalej Prospecting kampane, naming sa zjednoduší späť na trvalý formát (`VID - Pain Hook - v1`) — v trvalej kampani už netreba stopu experimentu.

### Naming publík (knižnica publík)

```
Publikum: [TYP] - [ZDROJ/UDALOSŤ] - [OKNO] - [TRH] - [DETAIL]
```

| Časť | Hodnoty |
|---|---|
| TYP | `CA` vlastné publikum z webu/pixelu/katalógu · `CA-LIST` zoznam zákazníkov · `CA-ENG` interakcie FB/IG, video, lead form · `LAL` lookalike |
| ZDROJ/UDALOSŤ | `Purchase`, `ATC`, `IC`, `VC`, `Web-All`, `Video50`, `IG-Eng`, `Lead`; pri LAL zdrojové publikum, napr. `Purchase-180d` |
| OKNO | `7d`, `14d`, `30d`, `60d`, `180d` (pri `CA-LIST` vynechať) |
| TRH | `SK`, `CZ`, … alebo `ALL`, keď publikum nie je obmedzené na doménu/krajinu |
| DETAIL | voliteľné: `bez-Purchase`, `1%`, kategória (`Kade`) |

**Príklady:**
- `CA - Purchase - 180d - ALL` — vylúčenie kupujúcich v DPA, prospectingu aj testoch
- `CA - VC - 60d - SK` — retargetingová vetva DPA
- `CA - ATC - 30d - SK - bez-Purchase`
- `CA-ENG - IG-Eng - 90d - ALL`
- `CA-LIST - Zakaznici - ALL`
- `LAL - Purchase-180d - SK - 1%`

Pravidlá:
- Typ je vždy na začiatku, aby sa publiká v zozname zoskupili.
- Okno a trh sú povinné. Bránia zámene napr. SK retargetingu v CZ adsete.
- Skratky udalostí sú rovnaké ako v názvoch adsetov.
- Pri zdieľanom pixeli pre viac domén je `ALL` v poriadku. Trhové publikum sa robí filtrom URL (doména).
- Vylúčenia sa neoznačujú v názve publika. Ide o použitie v adsete, nie o vlastnosť publika.

**Skratky:**

| Skratka | Význam |
|---|---|
| CONV | Konverzná kampaň |
| LEADS | Lead generácia |
| PROS | Prospecting |
| RTG | Retargeting |
| LAL | Lookalike |
| BROAD | Broad/Advantage+ |
| VID | Video |
| IMG | Statik |
| CAR | Carousel |
| DPA | Dynamický produktový ad (Advantage+ catalog ads) |
| CAT | Katalógová reklama z feedu (formát reklamy) |
| CA / CA-LIST / CA-ENG | Vlastné publikum: web a pixel / zoznam zákazníkov / interakcie |
| VC / ATC / IC | ViewContent / AddToCart / InitiateCheckout |
| UNAWARE / PROBLEM / SOLUTION / PRODUCT / MOSTAWARE | Awareness stage (pozri `creative-sequencing.md`) |

## Konsolidačná stratégia (pre existujúce účty)

**Kedy konsolidovať:** priveľa kampaní s podobným cieľom, adsety s <25 týždennými konverziami, prekrývajúce sa publiká, tá istá kreatíva bežiaca na viacerých miestach.

**Postup:**
1. **Audit súčasnej štruktúry** — zoznam všetkých kampaní/adsetov/konverzií, identifikuj slabých výkonných (< 25 konv/týždeň) a prekrývajúce sa publiká.
2. **Navrhni cieľovú štruktúru** — podľa rámcov vyššie, cieľ 50+ konverzií na adset.
3. **Zvoľ prístup migrácie:**

| Prístup | Kedy použiť | Riziko |
|---|---|---|
| Postupný | Účet funguje OK | Nízke |
| Fresh start | Účet rozbitý/neprehľadný | Stredné |
| Paralelný | Potreba porovnať | Vyššie náklady |

**Postupná migrácia:** týždeň 1 vytvor novú štruktúru, týždeň 2 presuň 20–30 % budgetu, týždeň 3 presuň 50 %, týždeň 4 dokonči migráciu, pauzni starú.

**Fresh start:** pauzni všetky existujúce kampane, spusti novú štruktúru. Riziko: strata historického učenia. Benefit: čistý štart.

## Bežné scenáre

**„Mám 20 kampaní a je to chaos"** → Diagnóza: prefragmentované, algoritmus sa nevie učiť. Riešenie: konsoliduj na 3–4 kampane podľa rámcov vyššie, postupná migrácia 4 týždne.

**„CBO alebo ABO?"** → 3+ adsety s podobnými publikami → CBO. Testuješ konkrétne publiká → ABO. Potrebuješ garantovaný spend → ABO. Chceš hands-off optimalizáciu → CBO. Predvoľ CBO, pokiaľ nemáš konkrétny dôvod na ABO.

**„Chcem testovať 10 rôznych publík"** → Problém: 10 adsetov fragmentuje dáta. Riešenie: zoskup podobné publiká, testuj 3–4 „typy" publík, nie 10 jednotlivcov. Alternatíva: testuj postupne, nie súčasne.

**„Retargeting a prospecting mám v jednej kampani"** → Pri broad / Advantage+ kampani je to normálny stav: Meta remarketuje sama. Neoddeľuj automaticky. Najprv pozri rozpad podľa **Audience Segments**: aký podiel spendu ide na Engaged a Existing Customers. Ak je podiel existujúcich zákazníkov vysoký, sprísni vylúčenia alebo použi stratégiu životného cyklu „Získanie nových zákazníkov“ (pozri `meta-mcp-playbook.md`). Samostatný retargeting iba s dôvodom zo sekcie „Retargeting“.

**„Retargeting (alebo DPA) má najlepší ROAS v účte"** → Často nie je inkrementálny: kupujú ľudia, ktorí by kúpili aj tak. Porovnaj 7-day click bez view, podiel Existing Customers a pri samostatnom retargetingu navrhni 2-týždňový test vypnutia (so súhlasom človeka).

**„Chcem samostatné adsety podľa záujmov / job title / LAL"** → Pri Advantage+ publiku sú to iba návrhy, adsety sa prekrývajú a delia malý objem. Daj ich ako návrh publika do jedného broad adsetu. Samostatne iba ako dočasný test publika v ABO.

**„Advantage+ Shopping vs. bežná štruktúra"** → ASC funguje pri e-commerce s katalógom a silnými pixel dátami (1000+ nákupov). Bežná štruktúra funguje, keď potrebuješ viac kontroly alebo testuješ konkrétne publiká/kreatívy. Testuj oboje paralelne, nech rozhodne výkon.

## Výstupný formát — Kampaňový architektonický plán

```
═══════════════════════════════════════════════════════
KAMPAŇOVÁ ARCHITEKTÚRA ÚČTU
Klient: [názov]
Vytvorené: [dátum]
Budget: [X] €/mesiac
═══════════════════════════════════════════════════════

PREHĽAD ŠTRUKTÚRY
- Odporúčaná štruktúra: [A Zjednodušená / B Štandardná / C Škálovaná / D Lead Gen]
- Zodpovedajúci Tier (Režim B1): [1/2/3]
- Celkovo kampaní: [X], celkovo adsetov: [X]
- Typ budgetu: [CBO/ABO/Mix]

ARCHITEKTÚRA
Kampaň 1: [názov]
- Cieľ: [...], Typ budgetu: [CBO/ABO], Denný budget: [X] €
- Adsety: [tabuľka: názov, publikum, odhad veľkosti, budget, počet reklám]
- Vylúčenia: [zoznam]

[Kampaň 2, 3... rovnaký formát]

NAMING KONVENCIA
[podľa vzoru vyššie, s konkrétnymi príkladmi pre tento účet]

ROZDELENIE ROZPOČTU
- Prospecting: [X] %
- Katalóg / DPA (e-commerce, povinné): [X] % (nie najväčšia kampaň)
- Retargeting: [0 % | X % s dôvodom: ...] (max 5–10 %)
- Testy: [Sandbox X % | in-place v Prospectingu] (pravidlo 60-30-10)

IMPLEMENTAČNÝ CHECKLIST
Fáza 0 — Audit dát: Audience Segments v Advertising Settings definované široko
  (Engaged = web 180d, celý e-mail list, lead form 90d; Existing Customers = Purchase 730d + zoznam kupujúcich;
  newsletter patrí do Engaged, nie do Existing); synchronizované zoznamy zákazníkov majú čerstvý dátum
  aktualizácie a veľkosť sedí s počtom kupujúcich (integrácie tretích strán vedia prestať synchronizovať
  bez upozornenia); vylúčenia kupujúcich nie sú prázdne; klient vlastní ad účet, dataset, stránku aj IG
  a agentúra je v jeho business portfóliu partner
Fáza 1 — Setup: vytvor kampane so správnymi cieľmi, nastav CBO/ABO, vytvor adsety, aplikuj naming
  E-commerce: katalóg + feed, pixel prepojený s katalógom, content_ids = id vo feede, product set
Fáza 2 — Kreatíva: nahraj kreatívy (4–6/adset), čistá URL + agentúrne UTM v poli „Parametre URL“ (sekcia UTM parametre)
Fáza 3 — Launch: skontroluj nastavenia, nastav budgety, spusti, sleduj prvých 48 hodín

═══════════════════════════════════════════════════════
```

## Limity tohto režimu

- Poskytuje návrh (blueprint), implementácia je na tebe/klientovi.
- Optimálna štruktúra sa líši podľa účtu — toto sú vodítka, nie absolútne pravidlá.
- Správanie algoritmu sa mení — best practices sa vyvíjajú.
- Nezaručuje výkon — štruktúra umožňuje, negarantuje.
