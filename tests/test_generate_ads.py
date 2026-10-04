import hashlib
import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "generate_ads", REPO / "07-image-generation" / "generate_ads.py"
)
generate_ads = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(generate_ads)


class GeneratorContractTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.brand = root / "brands" / "acme"
        cards = self.brand / "brand-dna"
        cards.mkdir(parents=True)
        (cards / "brand-spec-card.png").write_bytes(b"brand")
        (cards / "visual-style-card.png").write_bytes(b"style")

        product = self.brand / "products" / "hero-product"
        images = product / "source-product-images"
        images.mkdir(parents=True)
        (images / "product.png").write_bytes(b"product")
        self.research = product / "marketing-research"
        self.research.mkdir()
        for name in generate_ads.RESEARCH_DOCS + ("product-facts.md",):
            (self.research / name).write_text(f"# {name}\n", encoding="utf-8")
        self.adset = product / "product-image-ads" / "2026-08-06-test"
        self.adset.mkdir(parents=True)
        self.prompts = self.adset / "prompts-sk.json"
        self.plan = self.adset / "test-plan.json"
        self.write_plan()
        self.write_prompts()
        self.write_gates()

    def tearDown(self):
        self.tmp.cleanup()

    def test_brand_references_include_optional_png_logos_but_not_svg_masters(self):
        cards = self.brand / "brand-dna"
        (cards / "logo.png").write_bytes(b"logo-color")
        (cards / "logo-white.png").write_bytes(b"logo-white")
        (cards / "logo.svg").write_text("<svg/>", encoding="utf-8")

        refs = generate_ads.collect_brand_reference_files(cards)

        self.assertEqual(
            [path.name for path in refs],
            [
                "brand-spec-card.png",
                "visual-style-card.png",
                "logo.png",
                "logo-white.png",
            ],
        )

    def write_plan(self, hook="Presný headline", schema_version=2):
        plan = {
            "schema_version": schema_version,
            "status": "planned",
            "plan_id": "TP-TEST-001",
            "market": "sk",
            "campaign_objective": "sales",
            "funnel_stage": "TOF",
            "test_question": "Funguje presný headline?",
            "hypothesis": "Presný situačný headline zvýši outbound CTR.",
            "test_variable": "concept",
            "test_design": "pilot",
            "test_method": "modular-isolation",
            "primary_metric": "outbound CTR",
            "constants": ["rovnaká persona", "rovnaký angle", "rovnaký formát"],
            "data_gate": {
                "minimum_runtime": "3 dni",
                "minimum_evidence": "8 000 impresií a 30 outbound klikov na variant",
                "minimum_days": 3,
                "minimum_impressions_per_variant": 8000,
                "minimum_events_per_variant": {"event": "outbound_clicks", "count": 30},
            },
            "learnings": {
                "reviewed": True,
                "applied": [],
                "predecessor_plan_id": None,
                "note": "Testovací klient bez learnings.",
            },
            "variants": [{
                "concept_id": "C01",
                "brief_id": "B01",
                "persona": "Praktický zákazník",
                "awareness_stage": "problem-aware",
                "angle": "Overená hodnota",
                "hook": hook,
                "format": "statik headline-first",
                "template_number": 1,
            }],
        }
        if schema_version == 1:
            plan["test_variable"] = "hook"
            for field in ("test_design", "learnings"):
                plan.pop(field)
        self.plan.write_text(json.dumps(plan), encoding="utf-8")

    def write_prompts(self, headline="Presný headline", price=None, workflow_version=2,
                      source_prompts=None, prompt=None):
        entry = {
            "template_number": 1,
            "template_name": "headline-template",
            "brief": {
                "id": "B01",
                "persona": "Praktický zákazník",
                "angle": "Overená hodnota",
                "emotion": "istota",
                "customer_voice_anchor": "Chcem vedieť, čo kupujem.",
                "concept_id": "C01",
                "awareness_stage": "problem-aware",
                "hook": "Presný headline",
            },
            "headline": headline,
            "prompt": prompt or "Reproduce the exact product from the reference image. HEADLINE: {{headline}}",
            "aspect_ratio": "4:5",
            "needs_product_images": True,
        }
        if price:
            entry["subhead"] = price
        payload = {"brand": "Acme", "prompts": [entry]}
        if source_prompts:
            payload["source_prompts"] = source_prompts
        if workflow_version is not None:
            payload["workflow_version"] = workflow_version
            payload["test_plan"] = {
                "id": "TP-TEST-001",
                "sha256": hashlib.sha256(self.plan.read_bytes()).hexdigest(),
            }
        self.prompts.write_text(json.dumps(payload), encoding="utf-8")

    def write_gates(self, language="sk", market_prices_confirmed=False, mode=None):
        prompt_hash = hashlib.sha256(self.prompts.read_bytes()).hexdigest()
        agents = {
            f"{i:02d}": {"verdict": "PASS", "score": 95, "notes": "ok"}
            for i in range(1, 8)
        }
        agents["08"] = {"verdict": "PASS", "notes": "ok"}
        mode = mode or ("source" if language == "sk" else "translation")
        scoring = {
            "schema_version": 1,
            "mode": mode,
            "status": "passed",
            "prompts_sha256": prompt_hash,
            "agents": agents if mode == "source" else {k: v for k, v in agents.items() if k >= "04"},
        }
        if mode == "translation" or "source_prompts" in json.loads(self.prompts.read_text(encoding="utf-8")):
            source = self.adset / "prompts-sk.json"
            scoring["source_prompts_sha256"] = hashlib.sha256(source.read_bytes()).hexdigest()
        (self.adset / f"scoring-{language}.json").write_text(json.dumps(scoring), encoding="utf-8")
        (self.adset / f"approval-{language}.json").write_text(json.dumps({
            "schema_version": 1,
            "status": "approved",
            "approved_by": "Pavol",
            "approved_at": "2026-08-06T12:00:00+02:00",
            "language": language,
            "market_prices_confirmed": market_prices_confirmed,
            "prompts_sha256": prompt_hash,
        }), encoding="utf-8")

    def run_generator(self, **kwargs):
        return generate_ads.generate_ads(
            provider="google", brand_dir=str(self.adset), validate_only=True, **kwargs
        )

    def test_clean_contract_passes_and_finds_product_images(self):
        self.assertEqual(self.run_generator(), 0)

    def test_prompt_change_invalidates_both_hash_bound_gates(self):
        self.write_prompts(headline="Zmenený headline")
        self.assertEqual(self.run_generator(), 1)

    def test_test_plan_change_invalidates_strategy_binding(self):
        self.write_plan(hook="Iný plánovaný hook")
        self.write_gates()
        self.assertEqual(self.run_generator(), 1)

    def test_workflow_v2_requires_concept_fields(self):
        data = json.loads(self.prompts.read_text(encoding="utf-8"))
        del data["prompts"][0]["brief"]["hook"]
        self.prompts.write_text(json.dumps(data), encoding="utf-8")
        self.write_gates()
        self.assertEqual(self.run_generator(), 1)

    def add_second_planned_hook(self, include_prompt):
        plan = json.loads(self.plan.read_text(encoding="utf-8"))
        second_variant = dict(plan["variants"][0])
        second_variant.update({"concept_id": "C02", "hook": "Druhý headline"})
        plan["variants"].append(second_variant)
        plan.update({"test_variable": "hook", "test_design": "isolated"})
        self.plan.write_text(json.dumps(plan), encoding="utf-8")

        prompts = json.loads(self.prompts.read_text(encoding="utf-8"))
        if include_prompt:
            second_prompt = json.loads(json.dumps(prompts["prompts"][0]))
            second_prompt["brief"]["concept_id"] = "C02"
            second_prompt["brief"]["hook"] = "Druhý headline"
            second_prompt["headline"] = "Druhý headline"
            prompts["prompts"].append(second_prompt)
        prompts["test_plan"]["sha256"] = hashlib.sha256(self.plan.read_bytes()).hexdigest()
        self.prompts.write_text(json.dumps(prompts), encoding="utf-8")
        self.write_gates()

    def test_hook_variants_can_share_template_without_output_collision(self):
        self.add_second_planned_hook(include_prompt=True)
        data = json.loads(self.prompts.read_text(encoding="utf-8"))

        self.assertEqual(self.run_generator(), 0)
        self.assertEqual(
            [generate_ads.output_folder_name(entry) for entry in data["prompts"]],
            ["01-headline-template-C01", "01-headline-template-C02"],
        )

    def test_every_planned_concept_requires_exactly_one_prompt(self):
        self.add_second_planned_hook(include_prompt=False)

        self.assertEqual(self.run_generator(), 1)

    def test_prompt_for_unplanned_concept_is_rejected(self):
        prompts = json.loads(self.prompts.read_text(encoding="utf-8"))
        extra_prompt = json.loads(json.dumps(prompts["prompts"][0]))
        extra_prompt["brief"]["concept_id"] = "C99"
        prompts["prompts"].append(extra_prompt)
        self.prompts.write_text(json.dumps(prompts), encoding="utf-8")
        self.write_gates()

        self.assertEqual(self.run_generator(), 1)

    def test_duplicate_prompt_concept_is_rejected(self):
        prompts = json.loads(self.prompts.read_text(encoding="utf-8"))
        prompts["prompts"].append(json.loads(json.dumps(prompts["prompts"][0])))
        self.prompts.write_text(json.dumps(prompts), encoding="utf-8")
        self.write_gates()

        self.assertEqual(self.run_generator(), 1)

    def test_legacy_adset_requires_explicit_opt_in(self):
        self.write_prompts(workflow_version=None)
        self.write_gates()
        self.assertEqual(self.run_generator(), 1)
        self.assertEqual(self.run_generator(allow_legacy=True), 0)

    def test_bind_command_upgrades_prompts_to_workflow_v2(self):
        self.write_prompts(workflow_version=None)
        result = subprocess.run(
            [
                "python3",
                str(REPO / "04-test-planning" / "test_plan.py"),
                "bind",
                "--prompts",
                str(self.prompts),
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        data = json.loads(self.prompts.read_text(encoding="utf-8"))
        self.assertEqual(data["workflow_version"], 2)
        self.assertEqual(data["test_plan"]["id"], "TP-TEST-001")
        self.assertEqual(
            data["test_plan"]["sha256"],
            hashlib.sha256(self.plan.read_bytes()).hexdigest(),
        )

    def write_translation(self, lang="de", headline="Genaue Überschrift", price=None):
        target = self.adset / f"prompts-{lang}.json"
        self.prompts = target
        self.write_prompts(headline=headline, price=price, source_prompts="prompts-sk.json")
        self.write_gates(language=lang, market_prices_confirmed=True)
        return target

    def test_foreign_price_requires_market_confirmation(self):
        foreign = self.write_translation(price="Nur 49,90 €")
        self.write_gates(language="de", market_prices_confirmed=False)
        self.assertEqual(self.run_generator(prompts_file=str(foreign), lang="de"), 1)
        self.write_gates(language="de", market_prices_confirmed=True)
        self.assertEqual(self.run_generator(prompts_file=str(foreign), lang="de"), 0)

    def test_rendered_headline_must_match_planned_hook(self):
        self.write_prompts(headline="Úplne iný headline mimo plánu")
        self.write_gates()
        self.assertEqual(self.run_generator(), 1)

    def test_hook_hardcoded_in_prompt_is_rejected(self):
        self.write_prompts(prompt="Reproduce the exact product from the reference image. HEADLINE: Iný text")
        self.write_gates()
        self.assertEqual(self.run_generator(), 1)

    def test_hook_match_ignores_only_case_and_whitespace(self):
        self.write_prompts(headline="PRESNÝ   HEADLINE")
        self.write_gates()
        self.assertEqual(self.run_generator(), 0)

    def test_hook_can_span_multiple_rendered_fields(self):
        data = json.loads(self.prompts.read_text(encoding="utf-8"))
        entry = data["prompts"][0]
        entry["brief"]["hook_field"] = ["headline_lines.0", "headline_lines.1"]
        entry["headline_lines"] = ["Presný", "headline"]
        entry["prompt"] = "Reproduce the exact product from the reference image. {{headline_lines.0}} / {{headline_lines.1}}"
        self.prompts.write_text(json.dumps(data), encoding="utf-8")
        self.write_gates()
        self.assertEqual(self.run_generator(), 0)

    def test_translation_scoring_requires_declared_source(self):
        scoring_path = self.adset / "scoring-sk.json"
        scoring = json.loads(scoring_path.read_text(encoding="utf-8"))
        scoring["mode"] = "translation"
        for agent_id in ("01", "02", "03"):
            scoring["agents"].pop(agent_id)
        scoring_path.write_text(json.dumps(scoring), encoding="utf-8")
        self.assertEqual(self.run_generator(), 1)

    def test_translation_with_approved_source_passes(self):
        target = self.write_translation()
        self.assertEqual(self.run_generator(prompts_file=str(target), lang="de"), 0)

    def test_translation_invalidated_when_source_changes(self):
        target = self.write_translation()
        source = json.loads((self.adset / "prompts-sk.json").read_text(encoding="utf-8"))
        source["prompts"][0]["subhead"] = "Nový podnadpis po preklade"
        (self.adset / "prompts-sk.json").write_text(json.dumps(source), encoding="utf-8")
        self.assertEqual(self.run_generator(prompts_file=str(target), lang="de"), 1)

    def test_translation_requires_approved_source(self):
        target = self.write_translation()
        (self.adset / "approval-sk.json").unlink()
        self.assertEqual(self.run_generator(prompts_file=str(target), lang="de"), 1)

    def test_translation_brief_is_locked_to_source(self):
        target = self.write_translation()
        data = json.loads(target.read_text(encoding="utf-8"))
        data["prompts"][0]["brief"]["emotion"] = "iná emócia"
        target.write_text(json.dumps(data), encoding="utf-8")
        self.write_gates(language="de", market_prices_confirmed=True)
        self.assertEqual(self.run_generator(prompts_file=str(target), lang="de"), 1)

    def test_non_object_gate_artifacts_block(self):
        for artifact in ("scoring-sk.json", "approval-sk.json"):
            for payload in ("null", "[]", '"passed"', "true", "7"):
                self.write_gates()
                (self.adset / artifact).write_text(payload, encoding="utf-8")
                self.assertEqual(self.run_generator(), 1, f"{artifact} = {payload}")

    def fail_agent(self, agent_id, score=86):
        scoring_path = self.adset / "scoring-sk.json"
        scoring = json.loads(scoring_path.read_text(encoding="utf-8"))
        scoring["agents"][agent_id] = {"verdict": "FAIL", "score": score, "notes": "pod prahom"}
        scoring_path.write_text(json.dumps(scoring), encoding="utf-8")
        return scoring_path

    def run_override(self, agent_id, by="Pavol Jakubko", reason="Klient preferuje pôvodný nadpis"):
        gate = REPO / "07-image-generation" / "workflow_gate.py"
        return subprocess.run(
            ["python3", str(gate), "override", "--prompts", str(self.prompts), "--agent", agent_id,
             "--by", by, "--at", "2026-09-14T14:00:00+02:00", "--reason", reason],
            check=False, capture_output=True, text=True,
        )

    def test_human_override_accepts_failed_creative_score(self):
        self.fail_agent("05")
        self.assertEqual(self.run_generator(), 1)
        result = self.run_override("05")
        self.assertEqual(result.returncode, 0, result.stderr)
        scoring = json.loads((self.adset / "scoring-sk.json").read_text(encoding="utf-8"))
        self.assertEqual(scoring["agents"]["05"]["score"], 86)
        self.assertEqual(scoring["human_overrides"]["05"]["score_at_override"], 86)
        self.assertEqual(self.run_generator(), 0)

    def test_human_override_refused_for_non_creative_agents_and_ai(self):
        for agent_id in ("04", "06", "07", "08"):
            self.fail_agent(agent_id)
            self.assertNotEqual(self.run_override(agent_id).returncode, 0, agent_id)
        self.write_gates()
        self.fail_agent("05")
        self.assertNotEqual(self.run_override("05", by="Claude").returncode, 0)

    def test_human_override_invalid_after_score_or_copy_change(self):
        scoring_path = self.fail_agent("03")
        self.assertEqual(self.run_override("03").returncode, 0)
        scoring = json.loads(scoring_path.read_text(encoding="utf-8"))
        scoring["agents"]["03"]["score"] = 60
        scoring_path.write_text(json.dumps(scoring), encoding="utf-8")
        self.assertEqual(self.run_generator(), 1)
        scoring["agents"]["03"]["score"] = 86
        scoring["human_overrides"]["03"]["prompts_sha256"] = "0" * 64
        scoring_path.write_text(json.dumps(scoring), encoding="utf-8")
        self.assertEqual(self.run_generator(), 1)

    def test_scoring_agents_must_be_an_object(self):
        scoring_path = self.adset / "scoring-sk.json"
        scoring = json.loads(scoring_path.read_text(encoding="utf-8"))
        scoring["agents"] = None
        scoring_path.write_text(json.dumps(scoring), encoding="utf-8")
        self.assertEqual(self.run_generator(), 1)

    def test_translation_source_artifacts_must_be_objects(self):
        target = self.write_translation()
        for artifact in ("scoring-sk.json", "approval-sk.json"):
            original = (self.adset / artifact).read_text(encoding="utf-8")
            (self.adset / artifact).write_text("null", encoding="utf-8")
            self.assertEqual(self.run_generator(prompts_file=str(target), lang="de"), 1, artifact)
            (self.adset / artifact).write_text(original, encoding="utf-8")

    def test_translation_scored_in_source_mode_still_requires_approved_source(self):
        target = self.write_translation()
        self.write_gates(language="de", market_prices_confirmed=True, mode="source")
        self.assertEqual(self.run_generator(prompts_file=str(target), lang="de"), 0)
        (self.adset / "scoring-sk.json").unlink()
        (self.adset / "approval-sk.json").unlink()
        self.assertEqual(self.run_generator(prompts_file=str(target), lang="de"), 1)

    def test_isolated_hook_test_rejects_changed_price_or_cta(self):
        self.add_second_planned_hook(include_prompt=True)
        data = json.loads(self.prompts.read_text(encoding="utf-8"))
        for entry, (cta, price) in zip(data["prompts"], (("Zisti viac", "Len 10 €"), ("Kúp teraz", "Len 100 €"))):
            entry.update({"cta": cta, "subhead": price})
            entry["prompt"] += " SUB: {{subhead}} CTA: {{cta}}"
        self.prompts.write_text(json.dumps(data), encoding="utf-8")
        self.write_gates()
        self.assertEqual(self.run_generator(), 1)

        for entry in data["prompts"]:
            entry.update({"cta": "Zisti viac", "subhead": "Len 10 €"})
        self.prompts.write_text(json.dumps(data), encoding="utf-8")
        self.write_gates()
        self.assertEqual(self.run_generator(), 0)

    def test_isolation_keeps_price_constant_outside_offer_tests(self):
        base = {"template_number": 1, "brief": {"concept_id": "C01"}, "subhead": "Len 10 €", "cta": "Kúp"}
        other = dict(base, brief={"concept_id": "C02"}, subhead="Len 100 €")
        self.assertTrue(generate_ads.rendered_isolation_issues("angle", [base, other]))
        self.assertEqual(generate_ads.rendered_isolation_issues("offer", [base, other]), [])

    def test_schema_1_plan_requires_explicit_legacy_opt_in(self):
        self.write_plan(schema_version=1)
        self.write_prompts()
        self.write_gates()
        self.assertEqual(self.run_generator(), 1)
        self.assertEqual(self.run_generator(allow_legacy=True), 0)

    def test_product_facts_required_for_schema_2_plans(self):
        (self.research / "product-facts.md").unlink()
        self.assertEqual(self.run_generator(), 1)
        self.write_plan(schema_version=1)
        self.write_prompts()
        self.write_gates()
        self.assertEqual(self.run_generator(allow_legacy=True), 0)

    def test_missing_research_blocks_v2_generation(self):
        (self.research / "deep-research.md").unlink()
        self.assertEqual(self.run_generator(), 1)

    def test_inherited_research_source_is_followed(self):
        category = self.brand / "products" / "category" / "marketing-research"
        category.mkdir(parents=True)
        for path in self.research.iterdir():
            (category / path.name).write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
            path.unlink()
        (self.research / "product-facts.md").write_text(
            "# Fakty\n> research-source: ../../category/marketing-research/\n", encoding="utf-8"
        )
        self.assertEqual(self.run_generator(), 0)
        (category / "briefs.md").unlink()
        self.assertEqual(self.run_generator(), 1)

    def test_source_price_in_plan_market_needs_no_foreign_confirmation(self):
        self.write_prompts(price="Len 49,90 €")
        self.write_gates()
        self.assertEqual(self.run_generator(), 0)
        data = json.loads(self.prompts.read_text(encoding="utf-8"))
        self.assertFalse(generate_ads.price_confirmation_needed(data, self.prompts, "sk"))
        self.assertTrue(generate_ads.price_confirmation_needed(data, self.prompts, "cz"))

    def test_slash_in_template_name_never_creates_nested_output_folder(self):
        entry = {"template_number": 31, "template_name": "Comparison Grid / Table", "brief": {"concept_id": "C01"}}
        self.assertEqual(generate_ads.output_folder_name(entry), "31-Comparison Grid - Table-C01")
        self.assertNotIn("/", generate_ads.safe_template_name("Whiteboard Before/After"))

    def test_lang_is_inferred_from_prompts_file_name(self):
        self.assertEqual(generate_ads.lang_from_prompts_name("prompts-hu.json"), "hu")
        self.assertIsNone(generate_ads.lang_from_prompts_name("essentials-prompts.json"))

    def test_render_provenance_hashes_prompts_and_assets(self):
        cards = self.brand / "brand-dna"
        image = self.brand / "products" / "hero-product" / "source-product-images" / "product.png"
        provenance = generate_ads.render_provenance(
            self.prompts, json.loads(self.prompts.read_text(encoding="utf-8")),
            self.adset / "approval-sk.json", "google", "1K", "high", cards, [image], False, False,
        )
        self.assertEqual(provenance["prompts_sha256"], hashlib.sha256(self.prompts.read_bytes()).hexdigest())
        self.assertEqual(provenance["model"], generate_ads.GEMINI_MODEL_ID)
        self.assertIn(hashlib.sha256(b"brand").hexdigest(), provenance["assets"].values())
        self.assertIn(hashlib.sha256(b"product").hexdigest(), provenance["assets"].values())

    def test_translation_scoring_init_binds_source_hash(self):
        gate = REPO / "07-image-generation" / "workflow_gate.py"
        target = self.adset / "prompts-de.json"
        target.write_text(self.prompts.read_text(encoding="utf-8"), encoding="utf-8")
        refused = subprocess.run(
            ["python3", str(gate), "init-scoring", "--prompts", str(target), "--mode", "translation"],
            check=False, capture_output=True, text=True,
        )
        self.assertNotEqual(refused.returncode, 0)
        self.assertFalse((self.adset / "scoring-de.json").exists())

        data = json.loads(target.read_text(encoding="utf-8"))
        data["source_prompts"] = "prompts-sk.json"
        target.write_text(json.dumps(data), encoding="utf-8")
        created = subprocess.run(
            ["python3", str(gate), "init-scoring", "--prompts", str(target), "--mode", "translation"],
            check=False, capture_output=True, text=True,
        )
        self.assertEqual(created.returncode, 0, created.stderr)
        scoring = json.loads((self.adset / "scoring-de.json").read_text(encoding="utf-8"))
        self.assertEqual(scoring["source_prompts_sha256"], hashlib.sha256(self.prompts.read_bytes()).hexdigest())
        self.assertEqual(sorted(scoring["agents"]), ["04", "05", "06", "07", "08"])

    def test_bind_reports_contract_mismatch(self):
        self.write_prompts(headline="Headline mimo plánu", workflow_version=None)
        result = subprocess.run(
            ["python3", str(REPO / "04-test-planning" / "test_plan.py"), "bind", "--prompts", str(self.prompts)],
            check=False, capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("nesedí s hookom", result.stdout)

    def test_dry_run_creates_no_output_directory(self):
        result = generate_ads.generate_ads(
            provider="google", brand_dir=str(self.adset), dry_run=True
        )
        self.assertEqual(result, 0)
        self.assertFalse((self.adset / "outputs").exists())

    def _logo_fixture(self, tmp, colored=(60, 100, 81), white=(255, 255, 255)):
        from PIL import Image
        for name, rgb in (("logo.png", colored), ("logo-white.png", white)):
            im = Image.new("RGBA", (400, 60), rgb + (0,))
            im.paste(rgb + (255,), (0, 0, 300, 60))
            im.save(tmp / name)

    def test_composite_logo_places_logo_and_picks_variant_by_luminance(self):
        from PIL import Image
        tmp = self.adset
        self._logo_fixture(tmp)
        for bg, expected in ((0, 0, 0), "logo-white.png"), ((255, 255, 255), "logo.png"):
            target = tmp / "shot.png"
            Image.new("RGB", (1000, 1250), bg).save(target)
            placed = generate_ads.composite_logo(str(target), tmp, width_ratio=0.2)
            self.assertIsNotNone(placed)
            name, (w, h) = placed
            self.assertEqual(name, expected)
            self.assertEqual(w, 200)
            self.assertEqual(h, 30)
            out = Image.open(target).convert("RGB")
            self.assertEqual(out.size, (1000, 1250))
            # logo sedí v ľavom dolnom rohu, teda tam pixel nesmie zostať farbou pozadia
            self.assertNotEqual(out.getpixel((60, 1250 - 62 - 15)), bg)

    def test_logo_variant_uses_contrast_on_mid_grey_paving(self):
        from PIL import Image
        tmp = self.adset
        self._logo_fixture(tmp)
        target = tmp / "paving.png"
        Image.new("RGB", (1000, 1250), (126, 133, 131)).save(target)
        name, _ = generate_ads.composite_logo(str(target), tmp, width_ratio=0.2)
        self.assertEqual(name, "logo-white.png")

    def test_place_logo_updates_manifest_hash(self):
        from PIL import Image
        brand_dna = self.adset / "brand-dna"
        brand_dna.mkdir()
        self._logo_fixture(brand_dna)
        folder = self.adset / "outputs" / "01-test-C01"
        (folder / "_clean").mkdir(parents=True)
        Image.new("RGB", (400, 500), (126, 133, 131)).save(folder / "_clean" / "ad.png")
        Image.new("RGB", (400, 500), (126, 133, 131)).save(folder / "ad.png")
        rel = (folder / "ad.png").relative_to(Path(self.tmp.name))
        manifest = {"results": [{"file": str(rel), "sha256": "old"}]}
        (self.adset / "outputs" / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        result = subprocess.run(
            ["python3", str(REPO / "07-image-generation" / "place_logo.py"), "--ad-set", str(self.adset),
             "--brand-dna", str(brand_dna)],
            check=False, capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        saved = json.loads((self.adset / "outputs" / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(saved["results"][0]["sha256"], hashlib.sha256((folder / "ad.png").read_bytes()).hexdigest())
        self.assertEqual(saved["results"][0]["logo"]["file"], "logo-white.png")

    def test_keep_clean_refreshes_copy_after_regeneration(self):
        from PIL import Image
        tmp = self.adset
        self._logo_fixture(tmp)
        target = tmp / "regen.png"
        for color in ((10, 10, 10), (240, 240, 240)):
            Image.new("RGB", (400, 500), color).save(target)
            generate_ads.discard_stale_clean_copy(target)
            generate_ads.composite_logo(str(target), tmp, keep_clean=True)
            self.assertEqual(Image.open(tmp / "_clean" / "regen.png").getpixel((200, 100)), color)

    def test_composite_logo_noop_without_logo_files(self):
        from PIL import Image
        target = self.adset / "shot2.png"
        Image.new("RGB", (600, 600), (10, 10, 10)).save(target)
        empty = self.adset / "no-brand"
        empty.mkdir()
        self.assertIsNone(generate_ads.composite_logo(str(target), empty))

    def test_composite_logo_rejects_unknown_position(self):
        with self.assertRaises(ValueError):
            generate_ads.composite_logo("x.png", self.adset, position="middle")

    def test_reframe_rewrites_bare_ratio_and_keeps_focal_length(self):
        src = "Create a 4:5 vertical static ad for Acme. Shot at 50mm f/2.8 for a clean look."
        out = generate_ads.reframe_prompt(src, "9:16")
        self.assertIn("Create a 9:16 (1080x1920) vertical static ad", out)
        self.assertIn("50mm f/2.8", out)
        self.assertIn("REELS SAFE ZONES", out)

    def test_composite_logo_vertical_margin_can_clear_reels_ui(self):
        from PIL import Image
        tmp = self.adset
        self._logo_fixture(tmp)
        target = tmp / "reels.png"
        Image.new("RGB", (1080, 1920), (0, 0, 0)).save(target)
        generate_ads.composite_logo(str(target), tmp, width_ratio=0.2,
                                    margin_ratio=0.05, margin_y_ratio=0.30)
        out = Image.open(target).convert("RGB")
        # logo musí sedieť nad spodným 28 % UI pásom Reels
        ui_band_top = int(1920 * 0.72)
        band = out.crop((0, ui_band_top, 1080, 1920))
        self.assertEqual(band.getextrema()[0], (0, 0), "logo zasahuje do UI pásu Reels")
        above = out.crop((0, 0, 1080, ui_band_top))
        self.assertGreater(above.getextrema()[0][1], 0, "logo sa vôbec nevložilo")

    def test_composite_logo_keeps_clean_copy_for_later_repositioning(self):
        from PIL import Image
        tmp = self.adset
        self._logo_fixture(tmp)
        shots = tmp / "01-tpl"
        shots.mkdir()
        target = shots / "ad.png"
        Image.new("RGB", (800, 1000), (0, 0, 0)).save(target)

        generate_ads.composite_logo(str(target), tmp, width_ratio=0.2, keep_clean=True)
        clean = shots / "_clean" / "ad.png"
        self.assertTrue(clean.exists(), "čistá verzia sa neodložila")
        # čistá kópia nesmie obsahovať logo
        self.assertEqual(Image.open(clean).convert("RGB").getextrema()[0], (0, 0))
        # výstup logo obsahuje
        self.assertGreater(Image.open(target).convert("RGB").getextrema()[0][1], 0)

        # druhé vloženie nesmie čistú verziu prepísať už olologovaným výstupom
        generate_ads.composite_logo(str(target), tmp, width_ratio=0.2, keep_clean=True)
        self.assertEqual(Image.open(clean).convert("RGB").getextrema()[0], (0, 0))

    def test_reframe_9x16_overrides_feed_bottom_placement(self):
        src = ("Create a 4:5 (1080x1350) static ad. Render the CTA as a pill button placed in the "
               "LOWER RIGHT of the frame, near the bottom of the frame.")
        out = generate_ads.reframe_prompt(src, "9:16")
        self.assertIn("PLACEMENT OVERRIDE", out)
        self.assertIn("never in the bottom quarter", out)
        # override musí prísť AŽ ZA pôvodnou inštrukciou, inak ju neprebije
        self.assertGreater(out.index("PLACEMENT OVERRIDE"), out.index("LOWER RIGHT"))
        # pri 4:5 sa override nepridáva
        self.assertNotIn("PLACEMENT OVERRIDE", generate_ads.reframe_prompt(src, "4:5"))

    def test_pmax_profile_uses_google_recommended_dimensions(self):
        self.assertEqual(generate_ads.PMAX_ASPECTS, ["1.91:1", "1:1", "4:5"])
        self.assertEqual(generate_ads.PMAX_DIMS, {
            "1.91:1": "1200x628",
            "1:1": "1200x1200",
            "4:5": "960x1200",
        })
        self.assertEqual(generate_ads.default_output_dir("sk", pmax=True), "outputs-pmax")
        self.assertEqual(generate_ads.default_output_dir("de", pmax=True), "outputs-de-pmax")
        self.assertEqual(generate_ads.default_output_dir("sk", pmax=False), "outputs")

    def test_pmax_reframes_keep_critical_content_in_center_80_percent(self):
        prompt = "Create a 4:5 static ad. HEADLINE: {{headline}}"
        for ratio in generate_ads.PMAX_ASPECTS:
            with self.subTest(ratio=ratio):
                out = generate_ads.reframe_prompt(prompt, ratio)
                self.assertIn("center 80% safe area", out)
                self.assertIn("{{headline}}", out)

    def test_google_half_k_uses_api_literal(self):
        self.assertEqual(generate_ads.google_image_size("0.5K"), "512")
        self.assertEqual(generate_ads.google_image_size("2K"), "2K")


if __name__ == "__main__":
    unittest.main()
