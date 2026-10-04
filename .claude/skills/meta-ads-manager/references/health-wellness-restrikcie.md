# Health & Wellness obmedzenia — kreatíva aj tracking

Ak klient pôsobí v zdravotníctve, wellness, doplnkoch výživy, kozmetike s liečebným prísľubom alebo čo i len vzdialene súvisí so zdravotným stavom (kliniky, fyzioterapia, stomatológia, výživoví poradcovia, psychológovia, telesná hmotnosť), **Meta ho pravdepodobne zaradí do kategórie Health & Wellness** — automaticky, na základe obsahu webu a reklám, nie na základe toho, ako sa firma sama definuje.

> **Prečo je toto vlastný súbor a nie len poznámka:** obmedzenia tu fungujú na **dvoch nezávislých vrstvách**. Schválená reklama neznamená, že doména nie je obmedzená na dátovej úrovni — a naopak. Ak toto neviete rozlíšiť, ťažko diagnostikujete, prečo sa najlepšia kreatíva zrazu prestane dobre optimalizovať.

## Vrstva 1: Kreatíva a copy (schválenie reklamy)

Toto je vrstva, ktorú vidno okamžite — reklama buď prejde recenziou, alebo je zamietnutá.

**Čo spúšťa zamietnutie:**
- **Osobné atribúty (Personal Attributes policy)** — reklama nesmie tvrdiť alebo naznačovať, že pozná osobný stav diváka. Zakázané: „Bojujete s cukrovkou? Vyriešte to." alebo „Konečne sa zbavte príznakov [diagnóza]." Toto je priamy zákaz **druhej osoby spojenej s diagnózou/stavom** — presne ten štýl hookov, ktorý inak v `tvorba-kreativ.md` odporúčame na zastavenie scrollu.
- **Before/after a „implikovaná transformácia"** — zakázané pre chudnutie a estetické zákroky (botox, výplne): žiadne porovnania pred/po, žiadne zábery na štípanie tuku, žiadne zoomy na vrásky. Od 2026 sa zákaz rozšíril aj na **nepriamu** transformáciu — napr. produkt vedľa fotky štíhlej/zdravej osoby sa posudzuje rovnako prísne ako klasické before/after.
- **Negatívne sebavnímanie** — žiadny „ideálny typ postavy", žiadne váhy, pásky na meranie pása, zahanbujúce zábery.
- **Vekové cielenie** — zdravotné/wellness produkty musia cieliť len na 18+.
- **Povinný disclaimer pri doplnkoch výživy** — „Tento produkt nie je určený na diagnostiku, liečbu ani prevenciu žiadneho ochorenia" priamo **v texte reklamy**, nie len na landing page.

**Kde je výnimka (a teda priestor pre kreatívu):**
- Všeobecná pohoda, fitness služby a vybavenie, fitness kluby — nie sú v scope prísneho before/after zákazu.
- **Dentálne produkty (napr. bielenie zubov)** — výslovne vyňaté zo zákazu before/after. Pre Medante stomatológiu je teda before/after prípustný nástroj — na fyzioterapiu už nie.
- Kozmetika a digitálne úpravy bez negatívneho sebavnímania môžu ukázať transformáciu.

### Rizikové slová pri chudnutí a estetike

Pri produktoch/službách súvisiacich s chudnutím alebo telesnou hmotnosťou zvyšujú riziko zamietnutia konkrétne slová v texte reklamy — nielen samotný koncept:

- „diéta" / „diet"
- „spaľovanie tuku" / „fat-burning"
- „štíhlenie" / „slimming"
- podobne rizikové: „schudnúť X kg", „za X dní/týždňov" (časovo viazaný sľub výsledku)

**Reframing namiesto zákazu:** cieľ nie je vyhnúť sa téme, ale komunikovať ju inak. Namiesto „schudni 5 kg za mesiac" → „viac energie a sily počas dňa". Namiesto „spaľovanie tuku" → „podpora celkovej vitality". Namiesto „diéta" → „výživa tela", „stravovací návyk". Táto zmena rámca často prejde recenziou tam, kde priama formulácia neprejde — a mimochodom, aj lepšie rezonuje s Problem Aware/Solution Aware fázami (pozri `creative-sequencing.md`), lebo hovorí o pocite, nie o čísle.

## Vrstva 2: Landing page a doména

Meta skenuje cieľovú URL **v momente, keď ju vložíte do reklamy** — nečaká na konverzie. Analyzuje viditeľný text, text v obrázkoch, metadáta. Ak stránka signalizuje medicínsky stav alebo liečbu, doména sa zaradí do reštrikčnej kategórie **nezávisle od toho, či je samotná reklama v poriadku.**

**Dôsledok:** aj keď je vaša kreatíva 100% compliant, klientov web (napr. popis konkrétnej diagnózy, ktorú fyzioterapia lieči) môže spustiť dátovú reštrikciu na doméne. Toto sa nedá vyriešiť len úpravou reklamy — treba sa pozrieť aj na landing page copy.

## Vrstva 3: Event dáta (Pixel/CAPI) — najzákernejšia, lebo je neviditeľná

Toto je vrstva, ktorá najčastejšie prekvapí — reklamy bežia, schvália sa, konverzie sa zaznamenávajú, ale **kvalita signálu sa potichu degraduje** bez viditeľného varovania.

**Ako to funguje:** každý event (Purchase, Lead, InitiateCheckout) sa sémanticky analyzuje — nielen kľúčové slová, ale aj kontext (názov produktu/služby + parametre + identifikátor typu e-mail). Ak z toho vyplýva zdravotný stav spojený s konkrétnou osobou, Meta to považuje za citlivé zdravotné dáta a obmedzí ich použitie.

**Príklad presne pre Medante typ klienta:** event „Purchase" s hodnotou produktu „Objednávka — Fyzioterapia chrbtice" + e-mail zákazníka = pre Meta signál „táto konkrétna osoba má problém s chrbticou". To je presne typ dát, ktoré systém odmieta prijať na optimalizáciu.

**Úrovne reštrikcie (eskalujú postupne):**

| Úroveň | Čo sa deje | Dopad na vyhodnocovanie |
|--------|-----------|--------------------------|
| Core Setup (Level 1) | URL parametre a custom parametre sa orezávajú | Audience podľa parametrov produktu prestane fungovať, segmentácia sa zhoršuje |
| Level 2 | Purchase/InitiateCheckout sa blokujú alebo prestanú matchovať | Nemôžete optimalizovať na konverziu — len na hornolievikové signály |
| Level 3 | Blokované aj základné eventy (PageView) | Reklamy bežia „naslepo" bez spätnej väzby |

**EU traffic je zasiahnutý prísnejšie** — GDPR považuje zdravotné dáta za osobitnú kategóriu, takže reštrikcie sa na EU návštevnosť aplikujú agresívnejšie a skôr. Pre SK/CEE klientov to znamená, že túto tému netreba podceňovať „lebo sme malý trh" — je to presný opak.

## Praktické dôsledky pre náš skill

**Pri tvorbe konceptov (Režim A):**
- Pri zdravotníckom/wellness klientovi **nepoužívaj druhú osobu spojenú s diagnózou** v hookoch ani copy („Bolí vás chrbát?" je hranica — vyhni sa priamemu tvrdeniu o stave diváka, napr. „Vieme, že bolesť chrbta po sedení pozná veľa ľudí" je bezpečnejšie ako „Máte bolesť chrbta?").
- **Before/after je zakázaný pre fyzioterapiu**, ale **povolený pre stomatológiu** (dentálne produkty sú vyňaté) — pri Medante typu klienta rozlišuj podľa ambulancie/produktu, nie plošne.
- Over vekové cielenie 18+ pre všetky zdravotné koncepty.
- Ak ide o doplnok výživy alebo produkt s liečebným tvrdením, over či treba povinný disclaimer v texte reklamy.

**Pri tvorbe Setup Sheetu (Režim B1) a trackingu:**
- Do launch checklistu (`testovanie-metodika.md`) pridaj: over, že event názvy a parametre **neprezrádzajú diagnózu ani typ zdravotného problému**. Namiesto `Purchase_Fyzioterapia_Chrbtica` použi kódovaný názov, napr. `CONV_01`.
- Neposielaj v event payloade kombináciu „popis služby/produktu spojený s konkrétnou diagnózou" + identifikátor osoby (e-mail, telefón).

**Pri vyhodnotení (Režim C):**
- Ak klient je v Health & Wellness kategórii a vidíš neobvykle nízku kvalitu signálu (Purchase eventy nesedia s reálnymi tržbami, kampane sa nedokážu naučiť optimalizovať na konverziu), **over v Events Manageri → Nastavenia → Kategórie zdrojov dát**, či doména nie je klasifikovaná ako reštringovaná — predtým, než diagnostikuješ problém ako zlú kreatívu alebo zlé publikum.
- Ak je doména reštringovaná na Level 2/3, presuň optimalizačný cieľ vyššie do lievika (napr. na Lead namiesto Purchase, alebo na landing page view) — pokus o optimalizáciu na zablokovaný event nebude fungovať bez ohľadu na kvalitu kreatívy.

## Rýchly test pri každej kreatíve

Jedna otázka dobre zachytí najčastejšiu chybu, ale zdravotnícka/wellness kategória má viac vrstiev rizika než len priamu diagnózu. Použi túto ako **prvý, hlavný gut-check**, a tri doplnkové na zvyšné vrstvy — spolu pokryjú takmer všetko, s čím sa v praxi stretneš.

**1. Personal Attributes (hlavná, najčastejšia chyba):**
> „Znie táto reklama, akoby hovorila priamo človeku: vieme, čo vám je?"

Ak áno — koncept sa pravdepodobne nezhoduje s Personal Attributes policy a treba ho prepísať. Test funguje, lebo zachytáva jadro pravidla (nesmieš tvrdiť/naznačovať, že poznáš osobný stav diváka) bez toho, aby si musel memorovať konkrétne zakázané frázy — stačí sa vžiť do pozície čitateľa a spýtať sa, či mu text priamo pomenúva jeho diagnózu/stav.

**2. Rizikové slová a chudnutie:**
> „Je v texte slovo naznačujúce diétu, chudnutie alebo spaľovanie tuku — alebo časovo viazaný sľub výsledku?"

Ak áno — over proti zoznamu nižšie a zváž reframing (energia, vitalita, sila namiesto čísla na váhe).

**3. Before/after a transformácia:**
> „Ukazuje vizuál telo pred/po, alebo produkt vedľa 'ideálneho'/výrazne fit tela?"

Ak áno — over, či ide o dentálny produkt (výnimka) alebo o chudnutie/estetiku (zakázané, vrátane nepriamej transformácie).

**4. Liečebné tvrdenie:**
> „Tvrdí text, že produkt lieči, rieši alebo garantovane odstráni zdravotný problém?"

Ak áno — preformuluj na opatrnejšie tvrdenie („podporuje", „prispieva k") a over, či treba disclaimer.

**Pomocné doplňujúce otázky, ak si pri prvej otázke stále nie istý:**
- Je veta v 2. osobe naviazaná na konkrétny zdravotný stav? („Máte X?", „Trpíte Y?") → pravdepodobne áno.
- Dala by sa tá istá veta povedať aj o niekom, kto daný problém nemá, bez toho aby znela zvláštne? Ak nie, reklama pravdepodobne diváka „diagnostikuje".
- Je to opísané ako všeobecná situácia, ktorú viac ľudí pozná („veľa ľudí pozná pocit..."), alebo ako priame oslovenie diváka s predpokladom o jeho tele? Prvé je bezpečnejšie.

## Zoznam nežiaducich výrazov a formulácií

Nie je to úplný zoznam všetkého zakázaného Metou — je to praktická pomôcka na rýchlu kontrolu konceptu pred odovzdaním. Rozdelené podľa typu rizika:

**Priama diagnóza v 2. osobe (Personal Attributes):**
- „Máte [diagnóza/stav]?"
- „Trpíte na [ochorenie]?"
- „Bojujete s [zdravotný problém]?"
- „Konečne sa zbavte [príznak/stav]"
- „Vieme, čo cítite, keď máte [stav]"

**Chudnutie a estetika (rizikové slová/formulácie):**
- „diéta", „diétny plán"
- „spaľovanie tuku", „spáľ tuk"
- „štíhlenie", „schudni"
- „schudni X kg", „za X dní/týždňov" (časovo viazaný sľub)
- „ideálna postava", „dokonalé telo"

**Negatívne sebavnímanie / zahanbenie:**
- čokoľvek naznačujúce, že súčasný stav tela diváka je nedostatočný alebo hanebný
- porovnávacie zábery zdôrazňujúce „problémové" časti tela

**Liečebné/zázračné tvrdenia:**
- „lieči", „vylieči", „zaručene vyrieši"
- „vedecky dokázané" bez konkrétneho, overiteľného zdroja
- sľub konkrétneho zdravotného výsledku bez podmieňovacieho spôsobu

**Bezpečnejšie alternatívy (na použitie namiesto vyššie uvedeného):**
- namiesto „Máte bolesť chrbta?" → „Bolesť chrbta po sedení pozná veľa ľudí"
- namiesto „Zbavte sa cukrovky" → „Podpora zdravej hladiny cukru v krvi" (s diskliamerom, ak ide o doplnok)
- namiesto „Schudni 5 kg za mesiac" → „Viac energie a sily počas dňa"
- namiesto „Konečne vyriešte [problém]" → „Ak vás [situácia] trápi, toto je jedna z ciest"

## Rýchly kontrolný zoznam pre zdravotníckeho/wellness klienta

- [ ] **4 rýchle testy aplikované** na každý koncept — Personal Attributes, rizikové slová, before/after, liečebné tvrdenie. Ak ktorýkoľvek vyjde „áno", prepísať.
- [ ] Hooky a copy nepoužívajú druhú osobu spojenú s diagnózou/stavom.
- [ ] Rizikové slová (diéta, spaľovanie tuku, štíhlenie, časovo viazané sľuby) nahradené reframingom (energia, vitalita, sila).
- [ ] Before/after použitý len tam, kde je to povolené (dentálne áno, chudnutie/estetika nie).
- [ ] Žiadne negatívne sebavnímanie, žiadne „ideálne telo".
- [ ] Vekové cielenie 18+ nastavené.
- [ ] Disclaimer v texte reklamy, ak ide o doplnok výživy s tvrdením o zdraví.
- [ ] Event názvy a parametre nekódujú diagnózu/typ zdravotného problému.
- [ ] Skontrolovaná klasifikácia domény v Events Manageri, ak výkon nezodpovedá kvalite kreatívy.
