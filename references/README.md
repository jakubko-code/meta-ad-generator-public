# References

Znalostná databáza: zaujímavé postupy, návody a best practices z internetu (blogy, Meta dokumentácia,
case studies, podcasty). Nie je viazaná na klienta. Na klienta je `brands/<klient>/`, kde sú aj
poznatky z vlastných testov (`testing/learnings.md`).

> **Poznámka:** Obsah tu sú **odporúčania a možnosti, nie záväzné pravidlá ani istá pravda.**
> Ide o názory autorov, Meta sa rýchlo mení a každý účet má iný setup. Pred použitím vždy preveriť
> proti realite konkrétneho účtu.

## Poradie platnosti

1. **Brány a pravidlá** v `CLAUDE.md`, `NAVOD.md` a skilloch platia vždy. Destilát ich nikdy neobchádza.
2. **Metodika skillov** (`.claude/skills/*/references/`) je kanonický postup, podľa ktorého skill pracuje.
3. **Vlastné dáta klienta** (`learnings.md`, výsledky z účtu) majú pri konkrétnom klientovi prednosť pred článkom.
4. **Destiláty tu** dopĺňajú a spochybňujú bod 2 a 3, ale samy ich nemenia.

Keď destilát protirečí metodike skillu, agent to **povie nahlas** a uvedie obe možnosti. Ak sa poznatok
osvedčí, prenesie sa do skillu **vedome, ako samostatná zmena** so súhlasom človeka.

## Dva typy súborov

- **`*-tactics.md`**: destilát. Vybrané poznatky z viacerých zdrojov, pripravené na použitie.
  **Tieto súbory agent číta aktívne.**
- **`sources/*.md`**: zdroj. Kľúčové poznatky a krátke citácie z jedného článku. Archív pre návrat
  k originálu alebo doplnenie destilátov.

## Štruktúra

```
references/
├── README.md                      # tento súbor
└── meta/
    ├── README.md                  # index tém Meta Ads
    ├── _TACTICS_TEMPLATE.md       # vzor pre destilát
    ├── meta-<tema>-tactics.md     # destiláty (agent číta aktívne)
    └── sources/
        ├── _TEMPLATE.md           # vzor pre zdroj
        └── YYYY-MM-DD-zdroj-tema.md
```

Ďalšia vetva (napr. `google-ads/` pre PMax) vznikne, až keď na ňu bude obsah.

## Workflow

1. **Človek** vloží agentovi URL článku (alebo text, prepis videa, PDF).
2. **Agent** určí vetvu a tému, vyextrahuje obsah a uloží ho ako
   `<vetva>/sources/YYYY-MM-DD-zdroj-tema.md` (vyplnená hlavička, kľúčové poznatky, krátke citácie).
3. **Agent** zlúči kľúčové poznatky do príslušného `*-tactics.md` (vytvorí nový, ak ešte neexistuje)
   a aktualizuje index vetvy.
4. Ak poznatok protirečí metodike skillu, agent to uvedie v destiláte aj v odpovedi. Skill sám nemení.

## Kedy agent references číta

Proaktívne, bez pripomínania, pri režimoch Meta Ads Managera **S, E, A, B1, C a D**. Najprv index
vetvy, potom príslušný destilát. Keď návrh stojí na poznatku z references, uvedie súbor, z ktorého
vychádza.

## Konvencie

- **Názov súboru:** malé písmená, bez diakritiky, pomlčky.
- **Destiláty:** `meta/meta-<tema>-tactics.md`, drž ich štíhle (~do 150 riadkov). Keď narastú, rozdeľ tému.
- **Zdroje:** vždy začínaj dátumom publikácie: `2026-09-25-jonloomer-andromeda.md`.
- Vždy uveď **zdroj (URL)** a **dátum**. Meta sa rýchlo mení.
- **Žiadne klientské dáta.** Priečinok je v Gite (súkromné repo na GitHube), na rozdiel od `brands/`.
  Nepíš sem názvy klientov, čísla z ich účtov ani ID.
- **Neukladaj celé články.** V `sources/` sú kľúčové poznatky vlastnými slovami a krátke citácie.

## Rozporné zdroje

Keď si dva zdroje protirečia, **nezamlčuj to a ani jeden „neprehlasuj"**:

- **Faktický rozpor** (ako sa Meta dnes správa) → uprednostni **novší alebo overiteľný** zdroj (Meta
  dokumentácia, Help Center). Starší označ ako neaktuálny; ostáva v `sources/` so zmienkou „platilo do…".
- **Názorový alebo strategický rozpor** (čo odporúčať) → ulož **obe možnosti vedľa seba** v sekcii
  *„Sporné / názory sa líšia"*, vždy s **kto + kedy** a hlavne **kedy ktorý prístup platí** (segment,
  rozpočet, veľkosť účtu, história pixelu…).
- Zachovaj **stopovateľnosť**: každé tvrdenie musí byť dohľadateľné do `sources/`.
