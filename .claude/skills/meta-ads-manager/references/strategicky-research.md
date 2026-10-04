# Strategický research — z čoho staviame kreatívy (Režim S)

Toto je **upstream fáza pred Režimom A aj E.** Z výskumu odvodí **komu** hovoríme, **akú bolesť** trafiť a **akým angle/formátom** — všetko doložené citáciami. Výstup je strategická mapa + prioritné bunky, ktoré Režim A premení na koncepty a Režim B1 na testovací plán.

Nerobí sa týždenne. Je to **onboarding/reštruktúra vec**, presne ako Režim E — jednorazový návrh, ktorý ostatné režimy rámcuje. E rámcuje *kontajner* (štruktúra účtu); tento režim rámcuje *obsah* (kto, bolesť, angle). Poradie pri onboardingu nového klienta: **S → E → A → B1 → produkcia → B2 → C → D**.

> **Vzťah k ostatným referenciám:** tento súbor produkuje surovinu (persony, pains, angle mapa), ktorú `tvorba-kreativ.md` (Režim A) premení na hotové koncepty a `creative-sequencing.md` rozloží v účte. Neduplikuje ich — končí v momente, keď je jasné *čo a komu*, a odovzdáva to ďalej.

---

## 0a. Krok 2 pipeline — kam sa výstupy zapisujú

Režim S **nie je paralelný dokument** — je to metodická vrstva nad **krokom 2 (Strategický research)** z `NAVOD.md`. Jedna metodika, dva vstupné body (skill aj NAVOD). Výstupy sa zapisujú do existujúcich súborov produktu v `brands/<brand>/products/<produkt>/marketing-research/`:

| Výstup Režimu S | Súbor v `marketing-research/` |
|---|---|
| Verbatim quote bank, pains s citáciami, HIGH-FREQUENCY ANCHOR | `deep-research.md` (review-mining, verbatim citácie so zdrojmi) |
| Persony + sub-persony (situácia + vzťah k problému) | `avatar-sheet.md` |
| Ponuka, cena, marža, cieľová CPA/ROAS | `offer-brief.md` |
| Beliefs, ktoré musí zákazník prijať pred kúpou | `necessary-beliefs.md` |
| **Situačné momenty** (sekcia 4) — scény, kedy si zákazník na produkt spomenie | `cep-sheet.md` (Category Entry Points; šablóna a test kvality: `02-strategic-research/cep-sheet-template.md`). Situačné momenty z Režimu A/S a CEP sú **tá istá vec** — zapisuj ich sem, nech neostanú len v konceptoch. |
| **Strategická mapa + hviezdičkované koncepty s hypotézami** (sekcia 7) | `briefs.md` — hviezdičkovaná bunka = strategický brief (persona × angle × emócia × citácia × formáty); angle mapu naprieč fázami povedomia a hypotézy pridaj ako obohatenie formátu briefov |

**Jednotka je kategória, nie SKU** — rovnako ako v kroku 2 pipeline. Research píš do zložky kategórie; jednotlivé položky dostanú len `product-facts.md` s odkazom `research-source:` (rozhodovací postup: `02-strategic-research/product-research-check.md`).

**Postup:** ak `marketing-research/` produktu už existuje (krok 2 prebehol), Režim S ho **číta a dopĺňa** — neprepisuj hotový research, obohať ho (angle mapa, hviezdičkovanie, hypotézy). Ak neexistuje, Režim S ho **zakladá** — vtedy súbežne dodržuj metodiku a kontrolný zoznam z `02-strategic-research/` (`product-research-process.md`, `product-research-check.md`).

---

## 0. Kedy tento režim (a kedy nie)

**Spúšťače:** nový klient, „z čoho staviame kreatívy", „priprav stratégiu / mapu person", „nemáme angles, len produkt a recenzie", „nevieme koho oslovujeme".

**Kedy preskočiť:** klient beží dlho a persony/pains/angles sú známe a funkčné → choď rovno do Režimu A. Tento režim nemá zmysel spúšťať pri každom novom teste — jeho výstup je trvácny a prepoužíva sa.

**Kedy sa vrátiť:** keď Režim C opakovane ukáže, že problém nie je hook ani formát, ale **zlá bolesť/angle** (kreatíva je remeselne dobrá, ale nechytá) → to je signál, že mapa person/pains je slabá a treba ju prekopať tu, nie vyrábať ďalšie varianty.

---

## 1. Vstupy — čo potrebuješ (a čo keď to nemáš)

Systém stojí na reálnom zákazníckom jazyku. Nikdy nevymýšľaj persony ani pains „od stola" — každý musí byť oprený o zdroj.

**Ideálne vstupy:**
- recenzie / hodnotenia (Google, Heureka, web, e-shop)
- prepisy sales callov, dopyty, support tickety
- komentáre pod admi (vlastnými aj konkurencie)
- konkurenčné ady (Meta Ad Library — čo bežia dlho)
- dáta z účtu: čo historicky fungovalo (hooky, angles), ak účet nie je nový

**Minimum na spustenie:** URL webu + aspoň jeden zdroj reálneho zákazníckeho jazyka (čo i len recenzie).

**Podmienky dokončenia** (až potom Režim A a B1) sú prísnejšie — platí gate v `02-strategic-research/product-research-process.md`:
1. ChatGPT Deep Research výstup dodaný človekom (agent pripraví prompt, človek ho spustí a vloží výsledok),
2. interný research agenta (review mining, konkurencia, regulácie),
3. chýbajúce tvrdé dáta doplnené alebo priznané ako medzera.

Deep Research sa vynecháva iba na výslovné rozhodnutie človeka; zapíš ho do hlavičky `deep-research.md` (kto, kedy, prečo) a výstup ber ako hypotézu na overenie testom.

**Keď je dôkazová báza slabá:** povedz to nahlas. Výstup je vtedy **hypotéza na overenie testom, nie hotová stratégia.** Čo chýba z klientových zdrojov, vieme čiastočne dotiahnuť webom (verejné recenzie, konkurenčné ady), ale medzeru vždy priznaj — nezakrývaj ju domýšľaním.

---

## 2. Segmentová optika — čítaj `segmenty.md` ako prvé

Celá logika persona → pain → angle sa **mení podľa segmentu.** Default (nižšie sekcie) je ladený na e-com/DR; pre ostatné archetypy ho prepíš cez optiku `segmenty.md`.

| Segment | „Persona" ťažisko | Unaware populácia | Pains ťažisko | Angle ťažisko |
|---------|-------------------|-------------------|---------------|---------------|
| E-com / DR | životná situácia spotrebiteľa | často existuje | emocionálno-praktické | PAS, offer, social proof, demo |
| Lead-gen služby | lokálny kontext + naliehavosť problému | čiastočne | dôvera, riziko, „ako to funguje" | autorita, edukácia, recenzie |
| Health-wellness / kliniky | vzťah k vlastnému zdraviu/telu | tenká | strach, hanba, dôvera, predošlé zlyhanie | autorita, reframe príčiny, citlivosť *(pozri restrikcie)* |
| Cultural / event | vzťah k zážitku/téme, per trh | podľa témy | FOMO, atmosféra, lokálna relevancia | zážitok, urgencia termínu, lokalizácia |
| Infoprodukt | vzťah k transformácii (FROM/TO) | často existuje | frustrácia zo status quo, túžba po zmene | transformácia, mechanism, dôkaz |
| B2B high-ticket | rozhodovacia rola + biznis kontext | **takmer žiadna** | riziko, čas, ROI, dôveryhodnosť dodávateľa | autorita, case study, ROI |

**Kľúčový reframe:** pri B2B, klinikách a niektorých službách je **prázdna Unaware bunka správna odpoveď, nie chyba.** Nenúť DTC logiku „každý má Unaware fázu" tam, kam nepatrí (viď sekcia 5).

---

## 3. Persony — životná/biznis situácia + vzťah k problému

**Persona = TYP zákazníka.** Definuje ju:
- **situácia** (denný/biznis kontext, ktorý robí problém naliehavým)
- **vzťah k problému** (aktuálne v ňom zlyháva / vyhýba sa mu / má náhradné riešenie / nevie o ňom)

**Persona NIE JE:**
- demografia sama o sebe („32-ročná žena", „firma 50+ zamestnancov") — to je len dekorácia, nemení script
- fáza povedomia („Problem Aware zákazník" nie je persona)
- funnel fáza („teplý lead" nie je persona)
- mindset trait („šetrný", „náročný")

**Test konzistencie:** napíš jednovetový smer scriptu pre tú istú personu na fáze **Unaware** aj **Most Aware**. Ak sa definícia persony medzi nimi zmení → máš v skutočnosti **dve persony**, rozdeľ ich. Ak zostane rovnaká → persona je platná.

**Sub-persony:** rovnaká situácia, ale iná história zlyhania alebo iné náhradné riešenie (napr. „nikdy neskúsil" vs. „skúsil 2 riešenia, zlyhali, teraz to vzdal"). Každá sub-persona = verbatim citácia + zdroj.

**Rozsah:** max 3–4 persony. Ak nevieš piatu obhájiť citáciou z výskumu, nepridávaj ju.

> **Most na Režim A:** persona z tohto režimu = vstup pre **avatar** v `tvorba-kreativ.md`. Persona hovorí KTO a PREČO (situácia + vzťah k problému); avatar v Režime A na ňu nadviaže psychografiou, jazykom a hlasom. Nemýľ tie dva pojmy — persona je strategická vrstva nad avatarom.

---

## 4. Pain points — surový emocionálny spúšťač, nie messaging

**Pain ≠ angle.** Reťaz vyzerá takto:

```
ZÁKAZNÍCKY JAZYK (verbatim citát)
   ↓ underlying spúšťač
PAIN POINT (čo zákazník naozaj cíti)
   ↓ naratívny rámec nad bolesťou
ANGLE (smer scriptu)
   ↓ prvé 3 sekundy
HOOK
   ↓ celý príbeh
SCRIPT
```

**Pravidlá extrakcie:**
- pain = **spodný emocionálny/racionálny spúšťač**, nie hook, nie messaging, nie angle
- **verbatim citácia + zdroj pri každom paine** — ak to nevieš odcitovať, nevytiahol si to z výskumu, vymyslel si to
- žiaden marketingový jazyk („obsessed", „game-changing", „transformačný")
- ak sa tá istá bolesť objaví 5+ krát naprieč zdrojmi → označ **HIGH-FREQUENCY ANCHOR** (stane sa opakujúcou hookovou štruktúrou)

**Pressure test:** pre každý pain sa spýtaj — je toto koreňová bolesť, alebo povrchový symptóm? Nájdi hlbší koreň. Zoskup povrchové pains do klastrov a vyber **top pain na ukotvenie** (najvyššia páka) per persona.

**Segmentový reframe:** pri B2B / službách / klinikách je „pain" často **racionálno-prevádzkový** (riziko zlého rozhodnutia, strata času, dôveryhodnosť), nie čisto emocionálny. Nenúť DTC emóciu tam, kde zákazník rozhoduje hlavou — ale ani neprehliadni emóciu tam, kde reálne je (zdravie, hanba, strach z kliník).

**Výstup:** refinovaný zoznam 3–5 pains per persona, top pain na ukotvenie, klastrová mapa (povrch → koreň), verbatim quote bank (8–12 najsilnejších fráz per persona) pre hook engineering.

---

## 5. Angles per fáza povedomia — prepojenie na `creative-sequencing.md`

**Zjednotenie slovníka (dôležité, aby nevznikli dve mapy):**
- **Fáza povedomia = stav zákazníka** (čo o probléme vie) — presne ako tabuľka v `creative-sequencing.md`.
- **Angle = čo tomu stavu script povie.**
- Tento režim **generuje** 1 angle na fázu per persona × top pain (čo povedať). `creative-sequencing.md` rieši, **koľko konceptov na fázu** a ako ich Andromeda poskladá v účte.

Rovnaký pain zostáva konzistentný naprieč fázami — mení sa len to, čo má script na danej fáze dosiahnuť:

| Fáza | Čo má angle urobiť |
|------|--------------------|
| Unaware | pomenovať situáciu, ktorú zažíva („to som ja") — ešte nie problém |
| Problem Aware | validovať bolesť, pomenovať príčinu |
| Solution Aware | rerámcovať kategóriu / porovnať prístupy |
| Product Aware | pozíciovať voči konkrétnej alternatíve, sociálny dôkaz |
| Most Aware | dať dôvod konať teraz — **konkrétny** urgency mechanic |

**Tolerancia prázdnych buniek:** ak persona nemá Unaware populáciu v danej kategórii (typicky B2B, kliniky, akútne problémy), **nechaj bunku prázdnu** namiesto násilného vyplnenia.

**Kontrola nesprávne zaradených buniek:** ak „Unaware" angle číta ako Problem/Solution Aware, diagnóza je buď (a) **category gap** — populácia tam naozaj nie je → prázdna bunka je OK, alebo (b) **zle definovaná persona** — persona je príliš úzka a kolabuje do dvoch → späť do sekcie 3 a re-cut.

**Most Aware nesmie byť generická urgencia.** „Kúp teraz" nie je angle. Musí menovať mechanic: obmedzený stav, launch verzie/termínu, discount cliff, social-proof trigger, deadline.

---

## 6. Formát × angle × diverzita

Namiesto výberu formátu podľa trendu: každý angle dostane formát, ktorý ho **najlepšie dodá**, s ohľadom na fázu, attention pattern persony a **štrukturálnu diverzitu** (Andromeda odmeňuje odlišné *entity*, nie copy varianty — viď princíp v SKILL.md a `creative-sequencing.md`).

- **Format inventory drž generický:** founder POV, UGC monológ, UGC recenzia, podcast/rozhovor, street interview, authority/expert talking head, demo, porovnanie, day-in-the-life, edukačný explainer, natívny social. *(Bez castingovej/creator-databázovej vrstvy — casting rieši produkcia, nie tento režim.)*
- **Matchovanie na fázu** už máš v tabuľke `creative-sequencing.md` („Typ konceptu → najlepšie fázy"). Použi ju, neduplikuj.
- **Diverzita:** ak >40 % buniek mapuje na jeden formát → buď to diverzifikuj, alebo to vedome potvrď ako strategickú koncentráciu (koncentrácia nie je automaticky slabina).

---

## 7. Syntéza → prioritizácia → odovzdanie do Režimu A/B1

Po sekciách 3–6 máš 20–30 potenciálnych buniek. Bez prioritizácie je to stena možností, ktorú nikto nevyužije.

**Strategická mapa** (jedna tabuľka): persona / sub-persona · pain anchor · fáza povedomia · angle · formát · stav pokrytia (Scaling / Testing / Not Running).

**Hviezdičkuj top 5–8 buniek** podľa:
- najsilnejší verbatim match zo zdrojov
- štrukturálne odlišný formát (nová entita)
- persona/fáza aktuálne nepokrytá (Testing / Not Running)
- rýchlo vyrobiteľné s dostupným talentom/rozpočtom

Pre každú hviezdičkovanú bunku **jednovetová hypotéza:** *„Ak nasadíme [angle] vo [formát] pre [persona] na [fáza], čakáme [konkrétny výsledok], pretože [mechanizmus]."*

**Odovzdanie (toto je pointa celého režimu):**
- strategická mapa + hviezdičkované bunky s hypotézami → **`marketing-research/briefs.md`** produktu (pozri sekciu 0a)
- hviezdičkované bunky + hypotézy → **Režim B1** (`test-plan.json`); reálne PASS súbory sa zapíšu do Trackera až v B2
- persony + angle mapa → **Režim E** (ak treba architektúru účtu) a **Režim A** (konkrétne koncepty avatar → angle → hook → telo → CTA); potom B1 v kroku 4 a copy až v kroku 5 (`prompts-sk.json`)
- prázdne bunky / medzery v pokrytí → vstup pre **Režim E** (rozhodnutie, čo účet vôbec pokrýva)

Research sa nesmie skončiť „mapou v šuflíku" — vždy naň nadviaž konkrétnym ďalším krokom v A alebo B.

---

## 8. Worked example (privátna klinika / health-wellness, SK trh)

*(Ilustruje reframe oproti DTC — tenká Unaware populácia, pains miešajú emóciu a dôveru, angle ťažisko na autorite. Pri reálnom health-wellness klientovi vždy súbežne čítaj `health-wellness-restrikcie.md`.)*

**Persona: „Odkladač, čo sa bojí zákroku"**
- Situácia: dlhodobo rieši estetický/zdravotný problém, roky ho odkladá
- Vzťah k problému: vie o ňom, ale bráni sa — strach z bolesti, z výsledku, nedôvera ku klinikám
- Verbatim: „Chcem s tým konečne niečo urobiť, ale bojím sa, že to dopadne zle." *(recenzia / dopyt)*
- Prečo kúpi: úľava od strachu a získanie dôvery, nie samotný zákrok

**Top pain (ukotvenie):** strach z nezvratného zlého výsledku + nedôvera, komu sa zveriť. HIGH-FREQUENCY ANCHOR: opakované „bojím sa, že…" naprieč recenziami a dopytmi.

**Angle mapa:**

| Fáza | Angle | Poznámka |
|------|-------|----------|
| Unaware | *(prázdne)* | ľudia s týmto problémom oň vedia → category gap, nie chyba |
| Problem Aware | „Odkladáš to roky? Nie si sám — a nie je to o odvahe." | validuje, odbúrava hanbu |
| Solution Aware | „Prečo konzultácia rozhoduje viac než technológia." | rerámcuje, čo si vyberať |
| Product Aware | „Ako u nás prebieha prvý termín — krok po kroku." | znižuje strach cez transparentnosť |
| Most Aware | „Konzultačné termíny tento mesiac obmedzené." | konkrétny urgency mechanic |

**Formáty:** Problem Aware → authority/expert talking head (lekár) alebo confession-style pacientka; Product Aware → demo „ako prebieha termín"; Most Aware → statik s termínom. Andromeda: aktuálna knižnica má len before/after statiky → talking head aj walkthrough sú **nové entity**.

**Prázdna Unaware bunka je tu strategicky správna** — nesnaž sa ju vyplniť.

---

## 9. Časté chyby a oprava

- **Persona je v skutočnosti fáza povedomia** → „Problem Aware klienti" nie je persona. Definuj cez situáciu + vzťah k problému, čo prežije všetkých 5 fáz.
- **Persona je demografia** → „firmy 50+ zamestnancov" je dekorácia. Nahraď biznis situáciou + rozhodovacou rolou.
- **Pain znie ako reklamný text** → ak znie ako headline, je o vrstvu privysoko. Vytiahni spodný spúšťač.
- **Pain bez citácie** → nevytiahnutý z výskumu, vymyslený. Zahoď alebo dohľadaj zdroj.
- **Nútené Unaware bunky v B2B/klinikách/službách** → category gap je platná odpoveď. Prázdna bunka > vymyslený angle.
- **Všetkých 5 angles znie rovnako** → ak Unaware a Problem Aware môžu zameniť miesta, Unaware je zle napísaný.
- **Formát podľa trendu, nie podľa fázy/angle** → funguje na TikToku, ale ak je script job Problem Aware, dostaneš views bez posunu CPA.
- **Research skončí mapou** → ak sa neodovzdá do A a B1 plánu, bola to strata času.

---

## 10. Feed forward

1. **Persony + angle mapa** → Režim A (avatar → angle → hook → telo → CTA); trvalé uloženie v `avatar-sheet.md` + `briefs.md`
2. **Hviezdičkované bunky + hypotézy** → Režim B1 (`test-plan.json`); B2 po produkcii doplní Test Tracker
3. **Verbatim quote bank** → hook engineering v Režime A
4. **Segmentové zistenia** → kalibrácia benchmarkov a „hard" metriky v Režime C (cez `segmenty.md`)
5. **Prázdne bunky / medzery v pokrytí** → strategické rozhodnutie o pokrytí účtu v Režime E
6. **Health-wellness persony** → vždy spárované s `health-wellness-restrikcie.md` pred tvorbou copy
