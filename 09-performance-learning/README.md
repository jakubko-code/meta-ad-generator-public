# 09 — Vyhodnotenie, learning a rotácia

Meta Ads Manager po nazbieraní dostatočných dát vykoná:

- **C — vyhodnotenie:** kontrola objemu dát, diagnostika a verdikt škálovať / iterovať / vypnúť / počkať;
- **D — fatigue:** týždenné skóre únavy a prioritizovaný rotačný plán.

Výsledky aktualizujú `testing/tracker.md`, prenositeľné poznatky idú do `testing/learnings.md` (s ID L001…) a únava do `testing/fatigue.md`.

- Výsledky sa párujú podľa **Meta Ad ID** z trackera, nie podľa názvu reklamy. Každé čítanie má obdobie; predošlé čítanie sa neprepíše bez stopy.
- Primárna klikacia metrika je **outbound CTR** (`outbound_clicks_ctr`); link CTR sa uvádza osobitne.
- Verdikt je odporúčanie. Stav v trackeri sa mení až po potvrdenej zmene v účte; kampane mení iba človek alebo agent po jeho výslovnom potvrdení.
- **Slučka sa uzatvára čítaním:** každý ďalší B1 plán načíta `learnings.md` a zapíše použité ID, predchodcu a dôvod iterácie do `test-plan.json` → `learnings`.

Spätná slučka je cielená:

- problém hooku alebo execution → krok 3 alebo 5,
- problém testovacej logiky → krok 4,
- problém persony, painu alebo angle mapy → krok 2,
- fatigue → nový koncept z existujúceho researchu, potom kroky 3–8.

Detailné pravidlá sú v referenciách `metriky-diagnostika.md`, `fatigue-detector.md` a `meta-mcp-playbook.md` projektového Meta Ads Manager skillu.
