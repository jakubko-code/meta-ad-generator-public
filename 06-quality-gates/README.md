# 06 — Quality Gates

8 agentov na hodnotenie copy briefu pred generáciou. Agenti 01–06 bežia paralelne, potom 07 (Fact-Check), potom 08 (Copy Editor).

## Pravidlo

**Agenti 01–07 musia skórovať ≥90 a mať PASS. Agent 08 je binárny PASS/FAIL.** Ak ktorýkoľvek zlyhá, iteruj copy brief a nepokračuj do generácie. Agent 08 má **veto právo** — akýkoľvek mechanický error blokuje generáciu bez ohľadu na skóre ostatných.

Pri workflow v2 musí ešte pred scoringom existovať platný `test-plan.json` z kroku 4. Každý brief je cez `concept_id` naviazaný na schválený koncept a polia `persona`, `angle`, `awareness_stage`, `hook` a template sa nesmú potichu zmeniť. Ak scoring navrhne strategickú zmenu, vráť sa do kroku 4, aktualizuj plán a znovu ho naviaž na prompty.

## Agenti

| # | Súbor | Hodnotí | Typ |
|---|-------|---------|-----|
| 01 | `01-agent-persona.md` | Persona Fit — rezonuje copy s `brief.persona`? | 1–100 |
| 02 | `02-agent-angle.md` | Angle Execution — aktivuje `brief.angle` (Belief #)? | 1–100 |
| 03 | `03-agent-emotion.md` | Emotional Resonance — vyvoláva `brief.emotion`? | 1–100 |
| 04 | `04-agent-brand.md` | Brand Consistency — voice + native vocab + oslovenie podľa klienta a trhu + glossary? | 1–100 |
| 05 | `05-agent-copy-excellence.md` | Copy Excellence — rytmus, kompresia, prekvapenie, hook strength | 1–100 |
| 06 | `06-agent-format.md` | Format Compliance — word counts, štruktúra, template fit + integrita vizuálneho vzoru (8 vzorov) | 1–100 |
| 07 | `07-agent-fact-check.md` | Fact-Check — každý claim/citát/číslo/cena/Belief # traceuje do research? (anti-hallucination) | 1–100 + PASS/FAIL |
| 08 | `08-agent-grammar.md` | Copy Editor — gramatika, diakritika, decimal sep, banned chars | PASS/FAIL + veto |

## Postup

1. Over väzbu promptov na `test-plan.json` príkazom `test_plan.py bind` alebo `generate_ads.py --validate-only`
2. Prečítaj copy brief aj priradený koncept (headline, subhead, CTA, image direction, persona, angle, awareness, hook)
3. Spusti agentov 01–06 paralelne — každý dá skóre + zdôvodnenie + návrhy na opravu
4. Spusti agenta 07 (Fact-Check) — anti-hallucination guard; fact-mismatch reštartuje pipeline, preto pred mechanickou kontrolou
5. Spusti agenta 08 (Copy Editor) — veto právo, blokuje generáciu pri akomkoľvek mechanickom probléme
6. Ak Agenti 01–07 majú ≥90 + PASS a Agent 08 má PASS → vytvor `scoring-{lang}.json`
7. Ak ktorýkoľvek zlyhá → oprav brief a spusti znova zlyhaných agentov; pri zmene stratégie aktualizuj aj krok 4

## Strojová brána pred generovaním

Textový report môže zostať v `scoring.md`, ale generátor vyžaduje aj strojový artefakt viazaný na presné bajty promptov:

```bash
python3 07-image-generation/workflow_gate.py init-scoring \
  --prompts path/to/prompts-sk.json --mode source
```

Po reálnom vyhodnotení doplň v `scoring-sk.json` výsledky, nastav `status` na `passed` a zachovaj vygenerovaný `prompts_sha256`. Pri preklade použi `--mode translation`; vyžadujú sa agenti 04–08. Prekladový `prompts-{lang}.json` musí mať `"source_prompts": "prompts-sk.json"`, scoring si zapíše SHA-256 zdroja a platí iba nad zdrojom s kompletným scoringom 01–08 a ľudským approvalom — aj keď preklad dostane plný scoring 01–08. Nový zdrojový text (aj samostatná vetva pre iný trh) má vždy `--mode source`.

Po zobrazení tabuľky copy človeku zaznamená schválenie človek (nie Claude/Codex):

```bash
python3 07-image-generation/workflow_gate.py approve \
  --prompts path/to/prompts-sk.json --by "Meno schvaľovateľa" \
  --at "2026-08-06T14:30:00+02:00" --language sk
```

Ak verzia pre trh mimo SK obsahuje cenu, lokálny človek musí potvrdiť sumu aj menu a k approval príkazu pridať `--market-prices-confirmed` (spolu so správnym `--language`).

**Výnimka človeka (iba agenti 01, 02, 03, 05):** skutočné skóre sa zapíše do `scoring-{lang}.json` aj pod prahom a človek, ktorý po ponúknutej oprave vedome trvá na pôvodnom texte, spustí `workflow_gate.py override --prompts … --agent 05 --by "Meno" --at "…" --reason "…"`. Záznam `human_overrides` je viazaný na hash promptov aj na zapísané skóre. Agenti 04, 06, 07 a 08 výnimku nemajú.

Každá neskoršia zmena `prompts-sk.json` zneplatní scoring aj approval cez SHA-256. Overenie bez API volania a bez zápisu:

```bash
python3 07-image-generation/generate_ads.py \
  --brand-dir path/to/ad-set --lang sk --validate-only
```

Pri inom jazyku nahraď `sk` jeho kódom, aby sa validovali správne `prompts-{lang}.json`, scoring a approval.

## Multi-language poznámka

Pri preklade existujúcej ad sady sa **A1 / A2 / A3 preskočia** (sú lockované briefom, language-agnostic). Re-runujú sa iba agenti **04, 05, 06, 07 (Translation Mode), 08** — 37% úspora scoring času. Detail v hlavnom `README.md`.
