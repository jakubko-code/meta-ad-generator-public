# Meta – Meranie (atribúcia, segmenty publika, deduplikácia) – tactics

Destilát: vybrané, použiteľné poznatky z viacerých zdrojov. Tento súbor agent číta aktívne.
Sú to odporúčania, nie pravidlá; brány a metodika skillov majú prednosť.

**Posledná aktualizácia:** 2026-10-01
**Zdroje:** [Jon Loomer 2026-05-26](sources/2026-05-26-jonloomer-agency-mistakes.md),
[Marin Istvanic 2026-09-30](sources/2026-09-30-istvanic-retargeting-campaigns.md),
[Common Thread Collective, bez dátumu](sources/2026-10-01-commonthread-methodology-meta.md)
**Súvisiaca metodika skillu:** `.claude/skills/meta-ads-manager/references/metriky-diagnostika.md`,
`tracker-navod.md`, `meta-mcp-playbook.md`

---

## Odporúčania / postupy

**Audience Segments (Advertising Settings):** definovať ich pri každom účte, lebo umožňujú rozpad
výsledkov na nové publikum / zapojené publikum / existujúcich zákazníkov a ukážu, koľko remarketingu
Meta robí sama. Definície **neovplyvňujú doručovanie**, sú iba na reporting, preto čo najširšie
(Loomer 2026-05):
- Engaged Audience: všetci návštevníci webu 180 d, celý e-mail list, lead form publiká 90 d, ďalšie relevantné.
- Existing Customers: všetky nákupy 730 d, zákazníci z e-mail listu, ďalšie relevantné.
Úzke definície iba skresľujú, že remarketingu je málo.
Istvanic (2026-09) pridáva: Existing Customers = Purchase z pixelu + synchronizovaný zoznam kupujúcich;
newsletter odberatelia patria do Engaged, nie do Existing Customers (inak podiel zákazníkov vyzerá
vyšší, než je).

**Audit synchronizovaných zoznamov a vylúčení:** pri zoznamoch z e-mail nástroja (Klaviyo a pod.)
pravidelne skontrolovať dátum poslednej aktualizácie a veľkosť (sedí s počtom kupujúcich?).
Integrácie tretích strán vraj prestanú synchronizovať zhruba po šiestich mesiacoch bez upozornenia;
nefunkčné vylúčenie môže poslať väčšinu „akvizičného“ spendu vracajúcim sa zákazníkom. Bez funkčných
segmentov a vylúčení sa retargeting od prospectingu vyhodnotiť nedá. (Istvanic 2026-09)

**Breakdown by Attribution Settings:** pri čítaní konverzií rozdeliť na 1-day click, 7-day click,
1-day view a 1-day engage-through. Najspoľahlivejší dôkaz vplyvu reklamy je 1-day click; view a
engage-through majú najnižší (stačila impresia). Vysoký podiel view-through pri remarketingu na ľudí,
ktorí dostávajú e-maily, znamená nafúknuté výsledky. (Loomer 2026-05) Istvanic (2026-09) na
škálovacích kampaniach používa iba click atribúciu. Výnimka: keď je Meta takmer jediný zdroj dopytu
(bez organiky, e-mailu, retailu), view-through môže byť reálny.

**Inkrementalita:** (Istvanic 2026-09)
- Meta incremental attribution ukazuje, ktoré konverzie Meta považuje za skutočne spôsobené (príklad:
  630 reportovaných, 380 inkrementálnych),
- holdout test (kontrolná skupina bez reklám) je zlatý štandard; pri meraní prospectingu nemiešať
  retargeting publikum do testu,
- lacná alternatíva pre samostatnú retargeting kampaň: 2-týždňový test vypnutia a sledovanie
  celkových tržieb (`meta-struktura-tactics.md`).
- **Orientačné faktory** (CTC, medián z 45 vlastných geo holdout testov, podobne databáza Haus 640+):
  akvizícia **iROAS ≈ 1,14×** reportovaného 7-day click (7-day click mierne podhodnocuje), retencia /
  existujúci zákazníci **≈ 0,60×** (výrazne nadhodnotená). iROAS = reportované tržby 7-day click × faktor.
  Faktor sa mení so sezónou a konkurenciou; bez vlastného testu iba hrubý odhad.

**Optimalizovať na inkrementálnu maržu, nie na reportovaný ROAS** (CTC): ROAS cieľ odvodiť od marže
a očakávanej inkrementality, pre retenciu iný (nižší) ako pre akvizíciu.

**Kvalita signálu** (CTC): CAPI povinné, Event Match Quality **7+/10**, mesačne porovnať počet
Purchase server eventov s objednávkami v e-shope.

**Breakdown by Conversion Count:** porovnať unikátne konverzie (zákazníkov) so všetkými. Ak sú výsledky
približne dvojnásobné, hľadať chybu deduplikácie pixel + CAPI. (Loomer 2026-05)

**Princíp:** reportovať výsledky, ktoré sú naozaj dobré, nie tie, ktoré dobre vyzerajú. (Loomer 2026-05)

## Na čo si dať pozor

- Názvy rozpadov a nastavení podľa Meta UI k 2026-05; pred použitím overiť v účte.
- Či sa rozpady dajú čítať cez Meta Ads MCP, treba overiť (`meta-mcp-playbook.md`); inak ich človek
  pozrie v Ads Manageri.

## Kedy použiť

- Režim C: pred verdiktom Škálovať/Vypnúť skontrolovať podiel 1-day click a unikátnych konverzií;
  pri DPA a retargetingu aj podiel segmentu Existing Customers.
- Režim E / audit prevzatého účtu: Audience Segments definované? Aký podiel rozpočtu ide na existujúcich
  a zapojených?
- Pri podozrení na nafúknuté výsledky alebo nezhodu s GA4/e-shopom.

## Rozdiel oproti metodike skillu

- Skill (`metriky-diagnostika.md`) rozpad podľa atribučných okien, Audience Segments ani conversion count
  nemal; `tracker-navod.md` iba zapisuje atribučné okno. Od 2026-09-30 skill preberá: Audience Segments
  a sync zoznamov vo Fáze 0 checklistu (`kampanova-struktura.md`), 7-day click a podiel Existing
  Customers pri verdikte retargetingu a DPA (`metriky-diagnostika.md`). Conversion count, holdout a
  incremental attribution ostávajú iba tu.

## Sporné / názory sa líšia

- **View-through:** Loomer (2026-05) ho radí čítať oddelene ako najslabší signál; Istvanic (2026-09)
  ho na škálovacích kampaniach vypína (iba click). Kedy čo: značka s e-mailom, organikou a povedomím →
  click; Meta ako takmer jediný akvizičný kanál → view-through môže byť reálny, čítať oddelene.
  CTC (bez dátumu) to potvrdzuje z optimalizačnej strany: predvolene **optimalizovať na 7-day click**,
  7-day click + 1-day view iba pri malom rozpočte, vysokom AOV alebo minimálnej inej návštevnosti.
