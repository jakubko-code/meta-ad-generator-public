# Meta – Štruktúra účtu (kampane, ad sety, remarketing, prístupy) – tactics

Destilát: vybrané, použiteľné poznatky z viacerých zdrojov. Tento súbor agent číta aktívne.
Sú to odporúčania, nie pravidlá; brány a metodika skillov majú prednosť.

**Posledná aktualizácia:** 2026-10-01
**Zdroje:** [Jon Loomer 2026-05-26](sources/2026-05-26-jonloomer-agency-mistakes.md),
[Marin Istvanic 2026-09-30](sources/2026-09-30-istvanic-retargeting-campaigns.md),
[Common Thread Collective, bez dátumu](sources/2026-10-01-commonthread-methodology-meta.md)
**Súvisiaca metodika skillu:** `.claude/skills/meta-ads-manager/references/kampanova-struktura.md`,
`testovanie-metodika.md`

---

## Odporúčania / postupy

**Vlastníctvo a prístupy (onboarding klienta):** klient má vlastné business portfolio a vlastní ad účet,
dataset/pixel, FB stránku aj IG účet. Agentúra je v jeho portfóliu **partner** s prístupom k assetom,
nikdy nie vlastník. Pri odchode sa partner len odoberie. (Loomer 2026-05) Hodí sa ako bod checklistu
pri zakladaní novej značky alebo prevzatí účtu.

**Jednoduchosť ako štart:** pri malom rozpočte sústrediť rozpočet na jeden cieľ (nákupy, inak leady),
začať 1 kampaňou a 1 ad setom a každý ďalší ad set či kampaň obhájiť obchodným dôvodom. Pri
problémovom účte je prvý krok zvyčajne zjednodušiť. (Loomer 2026-05; v súlade so Štruktúrou A a
princípom konsolidácie v skille)

**Detailné cielenie a lookalike sú dnes návrhy:** samostatné ad sety podľa záujmov či LAL dosiahnu
tých istých ľudí a riedia rozpočet. (Loomer 2026-05; v súlade s korekciou „broad namiesto lookalike“)

**Remarketing sa deje sám:** Sales kampaň s broad/Advantage+ cielením remarketuje automaticky, lebo
teplé publikum konvertuje lacnejšie. Samostatná retargeting kampaň nad tým je „double dipping“:
súťaží s vlastným prospectingom o tých istých ľudí. Signál: frequency retargeting kampane nad 3
(Istvanic 2026-09). Statik v broad kampani s frequency ~3 pri videu ~1,2 v tej istej kampani značí, že
statik v skutočnosti remarketuje (Istvanic 2026-09). Koľko remarketingu Meta robí, ukáže rozpad podľa
Audience Segments (`meta-meranie-tactics.md`).

**Kedy samostatný remarketing má zmysel** (Loomer 2026-05, Istvanic 2026-09):
- **drahý produkt s dlhým rozhodovaním** a malým rozpočtom; malé publikum hlboko vo funneli ako podpora
  e-mailu. Signál: **frequency nad 2 už pri nízkom spende** znamená, že produkt je štrukturálne
  retargetingový; akvizíciu riešiť inými kanálmi, Metu použiť na retargeting (Istvanic),
- **kampane optimalizované na TOF akcie** (klik, LPV, ThruPlay), obmedzené na e-mail list alebo zapojených
  návštevníkov (Loomer),
- **vedome oddelený rozpočet** kvôli viditeľnosti a kontrole: **5–10 % celkového rozpočtu**; 20–30 % už
  kanibalizuje prospecting (Istvanic).

**Katalóg / DPA ako „pokladník“** (Istvanic 2026-09): v Ads Manageri často najlepší ROAS, no môže
najmä obsluhovať existujúcich zákazníkov, ktorí by kúpili tak či tak. Ak beží:
- rozpočet obmedziť, nesmie byť najväčšou kampaňou,
- hodnotiť na 7-day click bez view, nie podľa in-platform ROAS,
- vylúčiť kupujúcich aspoň 90 dní, ideálne celý zoznam zákazníkov (e-mail sync),
- týždenne rozpad podľa Audience Segments; **nad 30 % spendu na existujúcich → sprísniť vylúčenia,**
- pri obchode s veľa produktmi má DPA zmysel ako cross-sell (doplnok ku kúpenému); overiť, že
  neukazuje práve kúpený produkt.

**Test vypnutia:** samostatnú retargeting kampaň vypnúť na 2 týždne a sledovať celkové tržby. Bez
zmeny = nebola inkrementálna; pokles = vrátiť s obmedzeným rozpočtom. (Istvanic 2026-09) Iba so
súhlasom človeka a mimo sezónnych výkyvov.

**Neobmedzovať vek, pohlavie, umiestnenia** pri optimalizácii na nákup (výnimka: tovar s vekovým
obmedzením, napr. alkohol). Keď segment prináša lacné, no nekvalitné výsledky (nízke LTV, zlé leady,
Rewarded Video), namiesto vylúčenia použiť **value rules** na zníženie ponuky a nechať Advantage+ zapnuté.
(Loomer 2026-05; v súlade s Advantage+ placements v `testovanie-metodika.md`)

**Počet reklám v ad sete:** začať s 1–2 reklamami, ktoré sú samy rozmanité (viac textov, nadpisov,
médií v jednej reklame), nechať bežať pár týždňov a pridávať úplne odlišné reklamy podľa výsledkov,
nie kvôli počtu. (Loomer 2026-05, odpoveď v komentároch) CTC na veľkých účtoch plní ad set až po limit
50 reklám a potom otvára ďalší (viď Sporné).

**Evergreen + Marketing Moment** (CTC): trvalá akvizičná kampaň vedľa kampane na kalendárové akcie
(výpredaj, sviatky) s pevným začiatkom a koncom ad setu. Pri e-come s retenčnou stratégiou ešte
zrkadlová retenčná (RTN) kampaň na existujúcich zákazníkov s **nižším** cieľovým ROAS; ACQ ich vylučuje.
DPA / DABA má vlastný ad set, lebo pracuje s inými signálmi ako statiky.

**Cost control namiesto stropu rozpočtu** (CTC): optimalizácia na hodnotu s **min. ROAS na úrovni ad
setu** a rozpočet zámerne vyšší, než sa minie. Spend kolíše podľa ceny trhu, čo je žiaduce. Predpoklad:
spoľahlivá hodnota nákupu v pixeli/CAPI a dosť konverzií; inak ROAS cieľ dusí doručovanie.

**Keď sa rozpočet nedočerpá, expandovať v poradí** (CTC): 1) viac odlišných konceptov, 2) duplikát
Evergreen s Bid Cap, kde **cieľová CPA = AOV / cieľový ROAS**, 3) samostatná ASC pre reklamy, ktoré
minuli **< 3× cieľovej CPA** (druhá šanca), 4) až potom uvoľniť ROAS cieľ, ak to marža dovolí.

## Na čo si dať pozor

- Loomer a Istvanic píšu z auditov a vlastných účtov (USA / e-com), bez štúdie. Čísla (5–10 %, 30 %,
  frequency 2 a 3) sú orientačné prahy, kalibrovať podľa účtu.
- Value rules: overiť dostupnosť pre daný cieľ a účet v aktuálnom UI.
- CTC píše pre veľké US Shopify značky s geo testami; 4 kampane, 50 reklám v ad sete a bid cap duplikáty
  pri malom SK rozpočte rozdrobia dáta. Prenositeľný je princíp (min. ROAS, poradie expanzie), nie rozsah.
- Zmena štruktúry živého účtu sa nerobí bez výslovného súhlasu človeka (pravidlo projektu).

## Kedy použiť

- Režim E: návrh alebo reštruktúra účtu, najmä pri malom rozpočte a pri audite prevzatého účtu.
- Onboarding nového klienta: kontrola vlastníctva assetov a partnerského prístupu.
- Režim C/D: keď výkon slabne pri zložitej štruktúre, najprv zvážiť zjednodušenie.
- Väčší e-com klient (vyšší rozpočet, dosť konverzií, spoľahlivá hodnota nákupu, retenčná báza):
  prístup CTC (min. ROAS, Marketing Moment, poradie expanzie, RTN s nižším cieľom) ponúknuť na
  posúdenie ako alternatívu. Skill sa tým nemení, rozhoduje človek pri konkrétnom klientovi.

## Rozdiel oproti metodike skillu

**Prenesené do skillu 2026-09-30** (so súhlasom človeka, `kampanova-struktura.md`):
- samostatný retargeting už nie je trvalá súčasť Štruktúr A–D; iba s pomenovaným dôvodom a stropom
  5–10 % (sekcia „Retargeting: predvolene ho robí Prospecting“), FAQ o spoločnej kampani prepísané,
- DPA ostáva povinná; pribudla kontrola „pokladníka“ (7-day click, prah 30 % na Existing Customers,
  nie najväčšia kampaň) a cross-sell vylúčenia,
- Štruktúra D: jeden broad ad set, záujmy / job title / LAL iba ako návrh publika alebo dočasný test,
- implementačný checklist: Fáza 0 (Audience Segments, sync zoznamov, vylúčenia, vlastníctvo assetov).

Ostáva mimo skillu: value rules namiesto obmedzení veku a pohlavia (iba zmienka v Štruktúre D),
počet reklám v ad sete (skill má minimum 3, Loomer začína s 1–2 viacnásobnými reklamami).

## Sporné / názory sa líšia

- **Oddelený retargeting:** skill pôvodne oddeľoval, aby prospecting „nehladoval“; od 2026-09-30
  prevzal pohľad Loomer (2026-05) a Istvanic (2026-09). Kedy predsa oddeliť: drahý produkt s dlhým
  rozhodovaním, TOF optimalizácia, vedome riadený rozpočet. Pri pochybnosti rozhoduje test vypnutia.
  CTC (bez dátumu) má retenčnú kampaň ako štandard, no s nižším ROAS cieľom, lebo jej inkrementalita
  je podľa ich testov iba ~0,6× reportovanej. Kedy čo: značka s veľkou zákazníckou bázou a retenčnou
  stratégiou (opakované nákupy) → RTN kampaň s nízkym cieľom môže dávať zmysel; malý účet → skill.
- **Počet reklám v ad sete:** Loomer (2026-05) začína s 1–2 viacnásobnými reklamami, skill má minimum 3,
  CTC plní až 50. Kedy čo: rozpočet a objem konverzií rozhodujú; 50 reklám uživí iba účet, kde každá
  reklama dostane zmysluplný spend.
