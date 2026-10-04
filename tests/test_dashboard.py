#!/usr/bin/env python3
"""Regression tests for the offline Creative QA dashboard builder."""

import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO / "tools" / "dashboard" / "build_dashboard.py"
SPEC = importlib.util.spec_from_file_location("build_dashboard", MODULE_PATH)
dashboard = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(dashboard)


def sample_item(root: Path) -> dict:
    return {
        "brand": "acme",
        "brand_dir": root / "brands" / "acme",
        "product": "hero-product",
        "adset": "2026-08-12-hook-test",
        "outputs": "outputs",
        "lang": "sk",
        "ad_set_dir": root / "brands" / "acme" / "products" / "hero-product" / "product-image-ads" / "2026-08-12-hook-test",
        "manifest": {
            "total_generated": 1,
            "total_failed": 0,
            "results": [{
                "template": 1,
                "name": "headline-template",
                "concept_id": "C01",
                "variation": "v1_img1",
                "aspect": "9:16",
                "file": "brands/acme/missing-banner.png",
            }],
        },
        "prompts": {
            "workflow_version": 2,
            "test_plan": {"id": "TP-TEST", "sha256": "abc"},
            "prompts": [{
                "template_number": 1,
                "template_name": "headline-template",
                "headline": "Presný headline",
                "brief": {"concept_id": "C01"},
            }],
        },
        "colors": {"primary": "#123456"},
    }


def sample_template() -> dict:
    return {
        "template_path": "brands/acme/acme-templates/01-product-hero.md",
        "title": "Acme — Template 01: Product Hero", "scope": "brand", "brand": "acme",
        "preview_status": "wireframe", "aspect_ratio": "4:5", "layout": "hero",
        "description": "Produktový hero layout.", "styles": [{"code": "A", "name": "Clean"}],
        "slots": ["HEADLINE", "CTA"], "needs_product_images": True,
        "wireframe_file": "brands/acme/acme-templates/previews/01-product-hero/wireframe.svg",
        "wireframe_current": True, "rendered_file": "", "rendered_current": False,
    }


class DashboardBuilderTests(unittest.TestCase):
    def test_banner_id_stays_compatible_with_legacy_flag_storage(self):
        self.assertEqual(
            dashboard.banner_id("acme", "hero", "test", "sk", 1, "v1_img1", "C01"),
            "acme__hero__test__sk__t1__v1-img1__c01",
        )

    def test_dashboard_contains_responsive_qa_workspace(self):
        item = sample_item(REPO)
        html = dashboard.build_html([item], {}, [sample_template()])

        expected = (
            'id="filter-adset"', 'id="filter-qa"', 'id="compare-overlay"', 'class="qa-controls"',
            'role="dialog"', 'object-fit: contain', '@media (max-width: 640px)',
            'data-concept-id="C01"', 'data-plan-id="TP-TEST"', 'Súbor chýba',
            'data-view="templates"', 'id="templates-view"', 'class="template-card"',
            'id="template-overlay"', '--generate-preview',
        )
        for marker in expected:
            self.assertIn(marker, html)
        self.assertNotIn("klient — ukážka reklám", html)
        self.assertIn("fonts.googleapis.com/css2?family=Google+Sans", html)
        self.assertIn('font-family: "Jost"', html)
        self.assertNotIn("object-fit: cover", html)

    def test_card_carries_png_hash_for_qa_binding(self):
        original_root = dashboard.ROOT
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            banner = root / "brands" / "acme" / "banner.png"
            banner.parent.mkdir(parents=True)
            banner.write_bytes(b"render-v1")
            item = sample_item(root)
            item["manifest"]["results"][0]["file"] = str(banner)
            dashboard.ROOT = root
            try:
                first = dashboard.build_card(item["manifest"]["results"][0], item)
                banner.write_bytes(b"render-v2")
                second = dashboard.build_card(item["manifest"]["results"][0], item)
            finally:
                dashboard.ROOT = original_root

        self.assertIn(f'data-sha256="{hashlib.sha256(b"render-v1").hexdigest()}"', first)
        self.assertIn(f'data-sha256="{hashlib.sha256(b"render-v2").hexdigest()}"', second)
        js = (REPO / "tools" / "dashboard" / "dashboard.js").read_text(encoding="utf-8")
        self.assertIn("review.sha256 !== card.dataset.sha256", js)
        # Staré hodnotenie bez hashu a chýbajúci súbor sa nesmú tváriť ako platný PASS.
        self.assertIn("if (!review.sha256) return", js)
        self.assertIn("if (!card.dataset.sha256) return", js)

    def test_embedded_seed_cannot_close_json_script(self):
        html = dashboard.build_html([sample_item(REPO)], {"x": {"note": "</script><script>bad()</script>"}})
        config = html.split('<script type="application/json" id="dashboard-config">', 1)[1].split("</script>", 1)[0]

        self.assertNotIn("</script>", config)
        self.assertIn("<\\/script>", config)

    def test_discovery_reads_language_specific_prompts(self):
        original_root = dashboard.ROOT
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            adset = root / "brands" / "acme" / "products" / "hero" / "product-image-ads" / "test"
            outputs = adset / "outputs-de"
            outputs.mkdir(parents=True)
            (outputs / "manifest.json").write_text(json.dumps({"results": []}), encoding="utf-8")
            (adset / "prompts-de.json").write_text(json.dumps({"brand": "Acme DE"}), encoding="utf-8")
            dashboard.ROOT = root
            try:
                items = dashboard.discover_all_brands()
            finally:
                dashboard.ROOT = original_root

        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["lang"], "de")
        self.assertEqual(items[0]["prompts"]["brand"], "Acme DE")


if __name__ == "__main__":
    unittest.main(verbosity=2)
