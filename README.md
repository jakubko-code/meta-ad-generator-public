# Meta Ad Generator

Nástroj na strategickú prípravu, výrobu a vyhodnocovanie statických bannerov pre Meta Ads. Funguje v **Claude Code aj v Codexe** a pre oba používa rovnaké projektové skilly.

> Avatar, angle a hook vznikajú pred bannerom. Platené generovanie sa spúšťa až po validácii, scoringu, ľudskom schválení a výslovnom pokyne „generuj“.

## Rýchly štart

Požiadavky: Python 3.10+, Claude Code alebo Codex a API kľúč podporovaného image providera.

```bash
git clone https://github.com/jakubko-code/meta-ad-generator.git
cd meta-ad-generator
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Potom zadaj agentovi napríklad:

```text
Priprav nového klienta pre Meta Ads. Začni stratégiou a testovacím plánom.
Zatiaľ nič negeneruj.
```

Agent si načíta [CLAUDE.md](CLAUDE.md), [NAVOD.md](NAVOD.md) a príslušné skilly.

## Kanonická postupnosť

| Krok | Výsledok | Hlavný vlastník |
|---:|---|---|
| 1 | Brand foundation a brand karty | Image Ad Generator |
| 2 | Persona, pains, awareness a angle mapa | Meta Ads Manager S |
| 3 | Architektúra kampane a kreatívne koncepty | Meta Ads Manager E + A |
| 4 | Learnings, hypotéza, typ testu, číselná dátová brána a `test-plan.json` | Meta Ads Manager B1 |
| 5 | Template, copy a `prompts-{lang}.json` | Image Ad Generator |
| 6 | Scoring 1–8 a ľudské schválenie | Image Ad Generator + človek |
| 7 | Validácia, generovanie a vizuálny QA | Image Ad Generator |
| 8 | Tracker a launch handoff po hotovej kreatíve | Meta Ads Manager B2 |
| 9 | Vyhodnotenie, fatigue a learning | Meta Ads Manager C + D |

Meta Ads Manager teda nezačína až po výrobe. Pri novom klientovi vstupuje už v kroku 2 a pred produkciou uzamkne strategický zámer v kroku 4. Image Ad Generator následne vyrába presne to, čo bolo naplánované.

## Štruktúra repozitára

```text
01-brand-foundation/             # brand research a brand karty
02-strategic-research/           # metodika a šablóny researchu
03-campaign-creative-strategy/   # prepojenie režimov E + A
04-test-planning/                # B1, test-plan.json a validátor
05-creative-production/          # templates, copy, ad swipe a template previews
06-quality-gates/                # scoring agenti 01–08
07-image-generation/             # validácia, generovanie, preklady
08-test-handoff/                 # B2, tracker a launch checklist
09-performance-learning/         # C + D, learning a fatigue
tools/dashboard/                 # Creative QA + Template knižnica
brands/                          # lokálne klientské dáta, Git ich ignoruje
```

Číslovanie vyjadruje poradie rozhodnutí. Dashboard je offline pomocný nástroj: Creative QA filtruje, porovnáva a hodnotí hotové bannery; Template knižnica zobrazuje bezplatné wireframy a voliteľné Gemini specimen náhľady globálnych aj klientskych template-ov. Nie je krokom workflowu ani náhradou produkčných brán. Detail je v [`tools/dashboard/README.md`](tools/dashboard/README.md).

Po vytvorení alebo zmene template-u obnov jeho bezplatný náhľad a dashboard:

```bash
python3 05-creative-production/template_preview.py --all --missing-only
python3 tools/dashboard/build_dashboard.py
```

Platený preview sa nespúšťa automaticky. Vyžaduje explicitný `--generate-preview` pre jeden template, používa neutrálne specimen copy, dostane watermark a ukladá sa mimo produkčných `outputs/`.

## Klientske dáta

Celý obsah `brands/*` je lokálny a ignorovaný Gitom. Na GitHub nepatria research, fotografie, prompty, scoring, schválenia ani výstupy klientov. Nepoužívaj `git add -f brands/...`.

Ak chceš jedného klienta odstrániť a začať nanovo, odstráň iba jeho `brands/{brand}/` — po zálohe toho, čo chceš zachovať. Samotný priečinok `brands/` nemaž; obsahuje `.gitkeep`. Nástroj klientov automaticky nemaže.

Očakávaná štruktúra ad setu:

```text
brands/{brand}/products/{product}/product-image-ads/{ad-set}/
├── test-plan.json
├── prompts-sk.json
├── scoring-sk.json
├── approval-sk.json
├── prompts-hu.json         # voliteľný preklad (source_prompts: prompts-sk.json)
└── outputs/
    └── manifest.json       # SHA-256 každého PNG + vstupy renderu
```

Prevádzkové poznatky sú v `brands/{brand}/testing/{tracker,learnings,fatigue}.md`.

## Strategický kontrakt workflow v2

Nový ad set musí mať `test-plan.json` (`schema_version: 2`) so stavom `planned`. V ňom sú koncepty, persona, angle, awareness stage, hook, template, testovaná premenná, typ testu, konštanty, metrika, číselná dátová brána a použité learnings. Pred plánom sa načíta `brands/{brand}/testing/learnings.md`.

| `test_design` | Použitie | Validátor vynúti |
|---|---|---|
| `isolated` | prenositeľný poznatok o jednej osi | ≥ 2 varianty, líši sa iba testované pole |
| `concept-comparison` | porovnanie celých konceptov | ≥ 2 varianty, `test_variable: concept` |
| `pilot` | overenie jedného konceptu | 1 variant, verdikt vždy predbežný |

```bash
python3 04-test-planning/test_plan.py init \
  --ad-set brands/{brand}/products/{product}/product-image-ads/{ad-set} \
  --plan-id TP-YYYY-MM-DD-NAZOV --market sk --objective sales \
  --funnel-stage TOF --test-variable hook

python3 04-test-planning/test_plan.py validate \
  --plan brands/{brand}/products/{product}/product-image-ads/{ad-set}/test-plan.json

python3 04-test-planning/test_plan.py bind \
  --prompts brands/{brand}/products/{product}/product-image-ads/{ad-set}/prompts-sk.json
```

`bind` zapíše do promptov `workflow_version: 2`, ID plánu a jeho SHA-256 a hneď overí kontrakt plán ↔ prompty. Každý brief musí obsahovať `concept_id`, `persona`, `angle`, `awareness_stage` a `hook` z plánu. Hook musí byť presne text renderovaného poľa (`brief.hook_field`, default `headline`) vložený cez `{{placeholder}}`. Zmena plánu väzbu zneplatní. Starší ad set bez `workflow_version` alebo so starým plánom `schema_version: 1` sa dá spustiť iba vedome s `--allow-legacy`; nový ad set tento prepínač nikdy nepoužíva.

## Brány a generovanie

Agenti 01–07 musia dosiahnuť aspoň 90 a PASS; Agent 08 má binárne veto. Potom človek schváli finálnu tabuľku copy. Hash promptov viaže scoring aj approval na presný obsah. `--validate-only` pri workflow v2 overí aj vlastný alebo zdedený strategický research.

```bash
python3 07-image-generation/workflow_gate.py init-scoring \
  --prompts path/to/prompts-sk.json --mode source

python3 07-image-generation/workflow_gate.py approve \
  --prompts path/to/prompts-sk.json --by "Meno" \
  --at "2026-08-06T14:30:00+02:00" --language sk

python3 07-image-generation/generate_ads.py \
  --brand-dir path/to/ad-set --lang sk --validate-only
```

Ak preklad alebo copy pre jazyk mimo trhu plánu obsahuje cenu, lokálny človek musí potvrdiť sumu aj menu. Pri approval použi cieľový jazyk a explicitný flag:

```bash
python3 07-image-generation/workflow_gate.py approve \
  --prompts path/to/prompts-de.json --by "Meno" \
  --at "2026-08-06T14:30:00+02:00" --language de \
  --market-prices-confirmed
```

Až po explicitnom „generuj“:

```bash
python3 07-image-generation/generate_ads.py \
  --brand-dir path/to/ad-set --lang sk --provider google --resolution 1K
```

### Voliteľné rozmery pre Google Ads Performance Max

PMax bannery nie sú nový workflow ani nová stratégia. Sú to rekomponované rozmerové varianty už schválených Meta konceptov a používajú rovnaký plán, copy, scoring aj approval. Vytvoria sa iba vtedy, keď používateľ výslovne požiada o **PMax alebo Google Ads bannery**; bežné „generuj bannery“ spúšťa iba štandardné Meta výstupy.

```bash
python3 07-image-generation/generate_ads.py \
  --brand-dir path/to/ad-set --lang sk --provider google --resolution 1K --pmax
```

`--pmax` vytvorí `1200×628` (`1.91:1`), `1200×1200` (`1:1`) a `960×1200` (`4:5`), zachová schválený koncept a copy, udrží kritický obsah v centrálnej 80 % safe zóne a uloží výsledky do samostatného `outputs-pmax/`. Pred ním musí prejsť štandardný `--validate-only`; potom otvor a skontroluj každý nový PNG.

Technické rozmery vychádzajú z [oficiálnych požiadaviek Google Ads pre PMax image assets](https://support.google.com/google-ads/answer/14530211).

Predvolený provider je `google`; dostupné sú aj `google-batch`, `fal` a `gpt-image`. Batch alebo iného providera použi iba na výslovný pokyn. Pri chybe regeneruj iba chybný variant a nemaž `outputs/`.

Každý render zapíše do `outputs*/manifest.json` SHA-256 finálneho PNG a presné vstupy. Vizuálny QA v dashboarde sa viaže na tento hash; zmenený alebo chýbajúci súbor aj staré hodnotenie bez hashu majú stav „Prehodnotiť“.

### Preklady

Preklad schváleného zdroja je `prompts-{lang}.json` s `"source_prompts": "prompts-sk.json"` a zamknutým briefom. Scoring 04–08 (`init-scoring --mode translation`) si zapíše hash zdroja a platí iba nad zdrojom s kompletným scoringom 01–08 a approvalom. Oslovenie sa riadi pravidlami klienta pre daný trh. Samostatná vetva pre iný trh s vlastnou ponukou nie je preklad — má vlastný plán a plný scoring.

```bash
python3 07-image-generation/workflow_gate.py init-scoring \
  --prompts path/to/prompts-hu.json --mode translation
```

Hotový banner možno preložiť cez `BONUS/03-image-translator/translate_ads.py` — skript prenesie iba schválené texty z `prompts-{lang}.json`, prejde rovnakými bránami a prijme iba evidovaný render aktuálneho zdroja s vizuálnym PASS z exportu dashboardu (`--qa-export`). Detail: [copy translator](BONUS/04-copy-translator/copy-translator.md) a [image translator](BONUS/03-image-translator/image-translator.md).

## Skilly a dokumentácia

- [Meta Ads Manager](.claude/skills/meta-ads-manager/SKILL.md) — S, E, A, B1, B2, C a D.
- [Image Ad Generator](.claude/skills/image-ad-generator/SKILL.md) — kroky 1, 5, 6 a 7 a produkčné väzby.
- [NAVOD.md](NAVOD.md) — úplný pracovný postup.
- [NAVOD.html](NAVOD.html) — vizuálny návod pre kolegov.
- [CLAUDE.md](CLAUDE.md) a [AGENTS.md](AGENTS.md) — spoločné pravidlá pre Claude Code aj Codex.

Kampane sa bez výslovného potvrdenia človeka nespúšťajú, nepauzujú ani nemenia. Verdikt v trackeri je odporúčanie; Stav sa mení až po potvrdenej zmene v účte. API kľúče patria iba do lokálneho `.env`.

## Kontrola repozitára

```bash
python3 -m unittest discover -s tests -v
python3 04-test-planning/test_plan.py validate --plan path/to/test-plan.json
```

Testy nesmú volať platené generovanie. Šablóna `04-test-planning/test-plan-template.json` má zámerne `status: draft`, takže sama validáciou neprejde.
