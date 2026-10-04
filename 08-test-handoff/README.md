# 08 — Test handoff a launch plán (Meta Ads Manager B2)

Po vizuálnom PASS sa plán z kroku 4 doplní o reálne názvy a cesty výstupov. Každý nasadzovaný variant dostane riadok v `brands/{brand}/testing/tracker.md` so súborom a jeho SHA-256 z `outputs*/manifest.json` — odovzdáva sa presne verzia s vizuálnym PASS. Stav je **Pripravená**; metriky zostávajú prázdne až do vyhodnotenia.

Po reálnom nasadení sa doplní Meta Ad ID a Adset ID a Stav sa zmení na Aktívna. Podľa Meta Ad ID sa neskôr párujú výsledky; jedna kreatíva nasadená do viacerých reklám má riadok na každé nasadenie.

B2 nemení hypotézu ani testovanú premennú. Ak vyrobené kreatívy nezodpovedajú `test-plan.json`, vracajú sa do produkcie — plán sa spätne neupravuje tak, aby ospravedlnil hotové bannery.

Skill pripraví launch checklist a odporúčanie. Kampaň nesmie spustiť, pauzovať ani meniť bez výslovného potvrdenia človeka.

Detail: `.claude/skills/meta-ads-manager/references/tracker-navod.md`.
