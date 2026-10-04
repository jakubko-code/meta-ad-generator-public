# Meta Ad Generator — pravidlá pre agentov

1. Najprv prečítaj celý `CLAUDE.md`; platí pre Claude Code aj Codex.
2. Kanonický workflow je `NAVOD.md`; obsahové zmeny rob v ňom. `NAVOD.html` zosúlaď na požiadanie, `README.md` iba na výslovný pokyn. Trvalé pravidlá workflowu zapisuj do repozitára, nie iba do lokálnej pamäti agenta.
3. Pri novej stratégii prečítaj celý `.claude/skills/meta-ads-manager/SKILL.md`; pri produkcii celý `.claude/skills/image-ad-generator/SKILL.md`.
4. Pri novom klientovi alebo chýbajúcom avatarovi, angle, awareness či hooku začni Meta Ads Managerom: S → E/A → B1. Produkcia začína až s platným `test-plan.json`.
5. Zachovaj `.claude/skills/` a Claude-compatible relatívne odkazy. Codex používa tie isté skilly; nevytváraj paralelnú verziu.
6. Spoločné skripty patria do očíslovaných priečinkov repozitára, nie do agent-špecifického runtime adresára.
7. Nové ad sety používajú workflow v2. Strategická zmena vyžaduje aktualizáciu a nové naviazanie `test-plan.json`.
8. Negeneruj platené obrázky bez explicitného pokynu. Pred generovaním musí prejsť `--validate-only`, hash-bound scoring a ľudský approval.
9. Nemaž klientské dáta ani hotové `outputs/`; regeneruj iba chybné varianty.
10. Pri strategických režimoch a vyhodnotení čítaj `references/meta/` (index + destilát). Sú to odporúčania; brány a metodika skillov majú prednosť. Postup ukladania článkov je v `references/README.md`.
11. Klientsky obsah v `brands/*` nikdy necommituj. Jazyk práce a dokumentácie je slovenčina.
