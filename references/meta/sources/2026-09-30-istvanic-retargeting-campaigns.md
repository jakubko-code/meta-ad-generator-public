# Stop Running Retargeting Campaigns on Facebook (Here's Why)

**URL:** https://www.youtube.com/watch?v=pfKJkwbx1P8
**Autor:** Marin Istvanic (YouTube, e-commerce agentúra a vlastná značka)
**Dátum publikácie:** 2026-09-30
**Uložené:** 2026-09-30
**Kategória:** Structure / Measurement / Catalog
**Relevantné tactics:** meta-struktura-tactics.md, meta-meranie-tactics.md

---

## Hodnotenie zdroja

- Video s príkladmi z vlastných a klientskych e-com účtov. Čísla sú jednotlivé prípady, nie štúdia.
- Uprostred reklama na platenú komunitu autora; na konci ponuka auditu.
- Poznatky vychádzajú z automatického prepisu s chybami (napr. „trust/Ross“ = ROAS, „triple value“ =
  Triple Whale, „Clavio“ = Klaviyo, „NCOs“ = pravdepodobne NC-ROAS). Nejasné čísla sú označené.

## Kľúčové poznatky (pre destiláciu)

**Mechanizmus:** broad prospecting už obsahuje remarketing. Meta ukazuje reklamu teplému publiku,
kým je dostupné, lebo konvertuje lacnejšie. Príklad: statik v broad kampani mal frequency 3
(správanie remarketingu), video v tej istej kampani 1,24 (skutočne nové publikum). Samostatná
retargeting kampaň je potom „double dipping“: súťaží s vlastnými reklamami o tých istých ľudí.
Test, či niečo nie je v poriadku: frequency retargeting kampane nad 3 (u klienta až 22 / mesiac).

**Katalóg / DPA ako „pokladník“:** v Ads Manageri vyzerá ako najlepšia kampaň (najvyšší ROAS),
ale v rozpade podľa Audience Segments autor našiel 3 000 zo 4 000 (mena neuvedená) spendu na
existujúcich zákazníkov, frequency 15 / mesiac; ROAS 4 v Ads Manageri vs. ~0,7 NC-ROAS v Triple Whale.
Ak ju chceš držať vedome na teplé publikum:
- obmedziť rozpočet, nesmie byť najväčšou kampaňou,
- nehodnotiť podľa in-platform ROAS; minimum 7-day click bez view,
- vylúčenie nákupov predĺžiť z 30 na aspoň 90 dní, ideálne vylúčiť celý zoznam zákazníkov (Klaviyo),
- týždenne pozrieť rozpad podľa Audience Segments; **ak nad 30 % spendu katalógu ide existujúcim
  zákazníkom, sprísniť vylúčenia.**

**Inkrementalita:**
- holdout test (náhodná kontrolná skupina bez reklám). Pri meraní TOF kampaní nemiešať do holdoutu
  retargeting publikum; retargeting testovať zvlášť,
- Meta incremental attribution: 630 reportovaných nákupov, iba 380 inkrementálnych,
- ak je Meta jediný akvizičný kanál (bez organiky, retailu, e-mailu), view-through môže byť reálny;
  pri značke s e-mailom, organikou a povedomím je view-through takmer iste nafúknutý. Autor preto na
  škálovacích kampaniach používa **iba click atribúciu**.

**Kedy samostatný retargeting má zmysel (framework):**
1. **Drahý produkt s dlhým rozhodovaním:** produkt za 450 $, väčšina kupujúcich sa rozhodovala 3–4
   mesiace (percento v prepise nejasné). Diagnostický signál: **frequency nad 2 už pri nízkom spende**
   = produkt je štrukturálne retargetingový; akvizíciu robiť inými kanálmi (influenceri, Google,
   e-mail) a Metu použiť na retargeting.
2. **Obchod s veľa produktmi, katalóg ako cross-sell:** po nákupe bundy ukázať nohavice je užitočné
   a môže byť inkrementálne. Obmedziť rozpočet, vylúčiť nedávnych kupujúcich daného produktu a overiť,
   že DPA naozaj ukazuje doplnky, nie práve kúpený produkt.
3. **Vedome oddelený rozpočet:** samostatný ad set na existujúcich zákazníkov s vlastným rozpočtom kvôli
   viditeľnosti a kontrole. Retargeting má mať **5–10 % celkového rozpočtu**; 20–30 % už kanibalizuje
   prospecting.

**Audit segmentov a vylúčení (predpoklad všetkého):**
- Existing Customers = Purchase event z pixelu + synchronizovaný zoznam kupujúcich (Klaviyo).
  Newsletter odberatelia patria do Engaged, nie do Existing Customers.
- Skontrolovať dátum poslednej aktualizácie a veľkosť synchronizovaného zoznamu (sedí s počtom
  kupujúcich?). Integrácie tretích strán **prestanú synchronizovať zhruba po šiestich mesiacoch bez
  upozornenia**. Prípad: vylúčenie kupujúcich nebolo synchronizované od 2022, 80 % spendu na nové
  produkty išlo vracajúcim sa zákazníkom.

**Test vypnutia:** vypnúť samostatnú retargeting kampaň na 2 týždne a sledovať celkové tržby. Ak sa
nezmenia, reklamy nič nerobili. Ak klesnú, retargeting je inkrementálny; vrátiť s obmedzeným rozpočtom.
Princíp: radšej prísť o retargetingovú príležitosť ako platiť za ľudí, ktorí by kúpili tak či tak.

## Dôležité citácie

> „Broad campaigns already contain a mix of prospecting and retargeting.“

> „I call catalog campaign the cashier of your Ecom.“

> „If more than 30% of catalog spend is going to existing customers, tighten the exclusions.“

> „If your exclusions are broken, everything in this video is moot.“

> „It's better to miss a retargeting opportunity than to waste budget on people who already bought anyway.“

## Kontext a obmedzenia

- E-commerce so silným e-mailom (Klaviyo) a treťostrannou atribúciou (Triple Whale); pri malých SK
  e-shopoch bez týchto nástrojov ostáva rozpad podľa Audience Segments a click atribúcia.
- Test vypnutia na 2 týždne je citlivý na sezónu a iné zmeny; výsledok je indikácia, nie holdout.
- Zmena alebo vypnutie kampane v účte klienta iba s výslovným súhlasom človeka (pravidlo projektu).
