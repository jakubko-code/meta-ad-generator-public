#!/usr/bin/env python3
"""Offline akceptačný test celého cyklu na fiktívnom klientovi.

Pokrýva prechody medzi krokmi, ktoré jednotkové testy nevidia: B1 plán → prompty a bind →
scoring a ľudské schválenie → validácia → simulovaný render (bez plateného API) →
dashboard hash → QA export → preklad → image translator → ďalší plán s learnings.
"""

import hashlib
import importlib.util
import io
import json
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock


REPO = Path(__file__).resolve().parents[1]
TEST_PLAN = REPO / "04-test-planning" / "test_plan.py"
GATE = REPO / "07-image-generation" / "workflow_gate.py"
TRANSLATOR = REPO / "BONUS" / "03-image-translator" / "translate_ads.py"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


generate_ads = load("generate_ads_cycle", REPO / "07-image-generation" / "generate_ads.py")
dashboard = load("dashboard_cycle", REPO / "tools" / "dashboard" / "build_dashboard.py")
test_plan = load("test_plan_cycle", TEST_PLAN)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(*args):
    result = subprocess.run([sys.executable, *map(str, args)], capture_output=True, text=True, check=False)
    return result.returncode, result.stdout + result.stderr


def fake_png(color) -> bytes:
    from PIL import Image
    buffer = io.BytesIO()
    Image.new("RGB", (64, 80), color).save(buffer, format="PNG")
    return buffer.getvalue()


class WorkflowCycleTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        brand = self.root / "brands" / "acme"
        (brand / "brand-dna").mkdir(parents=True)
        for card in ("brand-spec-card.png", "visual-style-card.png"):
            (brand / "brand-dna" / card).write_bytes(fake_png("white"))
        product = brand / "products" / "hero"
        (product / "source-product-images").mkdir(parents=True)
        (product / "source-product-images" / "hero.png").write_bytes(fake_png("gray"))
        research = product / "marketing-research"
        research.mkdir()
        for name in generate_ads.RESEARCH_DOCS + ("product-facts.md",):
            (research / name).write_text(f"# {name}\n", encoding="utf-8")
        self.adset = product / "product-image-ads" / "2026-09-11-hooks"

    def tearDown(self):
        self.tmp.cleanup()

    def entry(self, concept_id, headline):
        return {
            "template_number": 1,
            "template_name": "headline-template",
            "brief": {
                "id": "B01", "concept_id": concept_id, "persona": "P1", "angle": "Overená hodnota",
                "awareness_stage": "problem-aware", "hook": headline, "emotion": "istota",
                "customer_voice_anchor": "Chcem vedieť, čo kupujem.",
            },
            "headline": headline,
            "cta": "Zisti viac",
            "prompt": "Reproduce the exact product from the reference image. HEADLINE: {{headline}} CTA: {{cta}}",
            "aspect_ratio": "4:5",
        }

    def score_and_approve(self, prompts: Path, lang: str, mode: str):
        code, out = run(GATE, "init-scoring", "--prompts", prompts, "--mode", mode)
        self.assertEqual(code, 0, out)
        scoring_path = prompts.with_name(f"scoring-{lang}.json")
        scoring = json.loads(scoring_path.read_text(encoding="utf-8"))
        for agent_id, result in scoring["agents"].items():
            result["verdict"] = "PASS"
            if agent_id != "08":
                result["score"] = 95
        scoring["status"] = "passed"
        scoring_path.write_text(json.dumps(scoring), encoding="utf-8")
        code, out = run(GATE, "approve", "--prompts", prompts, "--by", "Pavol",
                        "--at", "2026-09-11T12:00:00+02:00", "--language", lang)
        self.assertEqual(code, 0, out)

    def validate(self, lang="sk"):
        with redirect_stdout(io.StringIO()) as out:
            code = generate_ads.generate_ads(provider="google", brand_dir=str(self.adset), lang=lang,
                                             validate_only=True)
        return code, out.getvalue()

    def test_full_cycle_offline(self):
        # B1 — plán cez init, doplnený a validný
        code, out = run(TEST_PLAN, "init", "--ad-set", self.adset, "--plan-id", "TP-CYCLE-1", "--market", "sk",
                        "--objective", "sales", "--funnel-stage", "TOF", "--test-variable", "hook")
        self.assertEqual(code, 0, out)
        plan_path = self.adset / "test-plan.json"
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        plan.update({
            "status": "planned", "test_question": "Ktorý hook?", "hypothesis": "Situačný hook vyhrá.",
            "test_method": "modular-isolation", "primary_metric": "outbound CTR", "constants": ["persona"],
        })
        plan["data_gate"].update({"minimum_runtime": "3 dni", "minimum_evidence": "30 klikov",
                                  "minimum_days": 3, "minimum_impressions_per_variant": 8000,
                                  "minimum_events_per_variant": {"event": "outbound_clicks", "count": 30}})
        plan["learnings"] = {"reviewed": True, "applied": [], "predecessor_plan_id": None, "note": "Nový klient."}
        base = {"brief_id": "B01", "persona": "P1", "awareness_stage": "problem-aware",
                "angle": "Overená hodnota", "format": "statik 4:5", "template_number": 1}
        plan["variants"] = [dict(base, concept_id="C01", hook="Hook A"), dict(base, concept_id="C02", hook="Hook B")]
        plan_path.write_text(json.dumps(plan, ensure_ascii=False), encoding="utf-8")
        code, out = run(TEST_PLAN, "validate", "--plan", plan_path)
        self.assertEqual(code, 0, out)

        # Krok 5 — prompty a bind (overí kontrakt)
        prompts = self.adset / "prompts-sk.json"
        prompts.write_text(json.dumps({"brand": "Acme", "prompts": [
            self.entry("C01", "Hook A"), self.entry("C02", "Hook B"),
        ]}, ensure_ascii=False), encoding="utf-8")
        code, out = run(TEST_PLAN, "bind", "--prompts", prompts)
        self.assertEqual(code, 0, out)

        # Krok 6 — scoring a ľudské schválenie, potom bezplatná validácia
        self.score_and_approve(prompts, "sk", "source")
        code, out = self.validate()
        self.assertEqual(code, 0, out)

        # Krok 7 — simulovaný render bez plateného API
        renders = iter([fake_png("red"), fake_png("blue")])
        with mock.patch.object(generate_ads, "GEMINI_API_KEY", "offline"), \
                mock.patch.object(generate_ads, "load_image_part_google", return_value=object()), \
                mock.patch.object(generate_ads, "run_generation_google", side_effect=lambda *a: next(renders)), \
                redirect_stdout(io.StringIO()):
            code = generate_ads.generate_ads(provider="google", brand_dir=str(self.adset))
        self.assertEqual(code, 0)
        manifest = json.loads((self.adset / "outputs" / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(len(manifest["results"]), 2)
        for result in manifest["results"]:
            self.assertEqual(result["sha256"], sha(Path(result["file"])))
            self.assertEqual(result["render"]["prompts_sha256"], sha(prompts))
        c01 = next(r for r in manifest["results"] if r["concept_id"] == "C01")
        c01_png = Path(c01["file"])

        # Dashboard viaže QA na rovnaký hash ako manifest; export s PASS pre C01
        original_root = dashboard.ROOT
        dashboard.ROOT = self.root
        try:
            item = {"brand": "acme", "product": "hero", "adset": self.adset.name, "outputs": "outputs",
                    "lang": "sk", "prompts": json.loads(prompts.read_text(encoding="utf-8")),
                    "colors": {"primary": "#123456"}, "manifest": manifest}
            card = dashboard.build_card(c01, item)
        finally:
            dashboard.ROOT = original_root
        self.assertIn(f'data-sha256="{c01["sha256"]}"', card)
        qa_export = self.adset / "creative-qa.json"
        qa_export.write_text(json.dumps({"items": [{"id": "c01", "status": "pass", "sha256": c01["sha256"]}]}),
                             encoding="utf-8")

        # Lokalizácia — preklad schváleného zdroja, prekladový scoring a approval
        german = json.loads(prompts.read_text(encoding="utf-8"))
        german["source_prompts"] = "prompts-sk.json"
        for entry, headline in zip(german["prompts"], ("Aufhänger A", "Aufhänger B")):
            entry.update({"headline": headline, "cta": "Mehr erfahren"})
        prompts_de = self.adset / "prompts-de.json"
        prompts_de.write_text(json.dumps(german, ensure_ascii=False), encoding="utf-8")
        self.score_and_approve(prompts_de, "de", "translation")
        code, out = self.validate("de")
        self.assertEqual(code, 0, out)

        # Image translator prenesie iba schválené texty do vizuálne schváleného renderu
        code, out = run(TRANSLATOR, "--image", c01_png, "--languages", "de", "--dry-run", "--qa-export", qa_export)
        self.assertEqual(code, 0, out)
        self.assertIn('"Hook A" → "Aufhänger A"', out)

        # Zmena zdroja po preklade zneplatní preklad aj prenos do obrázka
        source = json.loads(prompts.read_text(encoding="utf-8"))
        source["prompts"][0]["cta"] = "Kúp teraz"
        source["prompts"][1]["cta"] = "Kúp teraz"
        prompts.write_text(json.dumps(source, ensure_ascii=False), encoding="utf-8")
        self.assertEqual(self.validate("de")[0], 1)
        code, _ = run(TRANSLATOR, "--image", c01_png, "--languages", "de", "--dry-run", "--qa-export", qa_export)
        self.assertEqual(code, 1)

        # C + D → ďalší B1: nový plán odkazuje na learning a predchodcu; pôvodný plán ostáva viazaný
        follow_up = json.loads(plan_path.read_text(encoding="utf-8"))
        follow_up["plan_id"] = "TP-CYCLE-2"
        follow_up["learnings"] = {"reviewed": True, "applied": ["L001"], "predecessor_plan_id": "TP-CYCLE-1",
                                  "note": "L001: situačný hook vyhral; overujeme ho na novom angle."}
        self.assertEqual(test_plan.validate_plan_data(follow_up), [])
        bound = json.loads(prompts.read_text(encoding="utf-8"))["test_plan"]
        self.assertEqual(bound["sha256"], sha(plan_path))


if __name__ == "__main__":
    unittest.main()
