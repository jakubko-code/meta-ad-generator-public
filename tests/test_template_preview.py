#!/usr/bin/env python3
"""Regression tests for deterministic template previews."""

import importlib.util
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO / "05-creative-production" / "template_preview.py"
SPEC = importlib.util.spec_from_file_location("template_preview", MODULE_PATH)
preview = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(preview)


TEMPLATE = """# Acme — Template 01: Split proof

## Metadata
- **aspect_ratio:** 4:5
- **needs_product_images:** false

## Čo tento formát je
Porovnáva dva jasne oddelené stavy bez kopírovania cudzej reklamy.

## Styles

### Style A: Clean split

#### Copy template
```
[HEADLINE] — max 5 slov
[PROOF] — max 4 slová
{{cta}}
```

#### Image generation prompt
```
Create a 4:5 split comparison for [BRAND NAME].
HEADLINE: "{{headline}}"
CTA: "{{cta}}"
```
"""


class TemplatePreviewTests(unittest.TestCase):
    def setUp(self):
        self.original_root = preview.ROOT

    def tearDown(self):
        preview.ROOT = self.original_root

    def test_parser_supports_brand_style_templates(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            template = root / "brands" / "acme" / "acme-templates" / "01-split-proof.md"
            template.parent.mkdir(parents=True)
            template.write_text(TEMPLATE, encoding="utf-8")
            preview.ROOT = root

            metadata = preview.parse_template(template)

        self.assertEqual(metadata["scope"], "brand")
        self.assertEqual(metadata["brand"], "acme")
        self.assertEqual(metadata["aspect_ratio"], "4:5")
        self.assertFalse(metadata["needs_product_images"])
        self.assertEqual(metadata["styles"][0]["name"], "Clean split")
        self.assertEqual(metadata["slots"][:2], ["HEADLINE", "PROOF"])

    def test_hash_marks_changed_template_stale_until_rebuild(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            template = root / "brands" / "acme" / "acme-templates" / "01-split-proof.md"
            template.parent.mkdir(parents=True)
            template.write_text(TEMPLATE, encoding="utf-8")
            preview.ROOT = root

            preview.build_wireframe(template)
            current = preview.discover_templates(root)[0]
            template.write_text(TEMPLATE + "\nNová poznámka.\n", encoding="utf-8")
            stale = preview.discover_templates(root)[0]

        self.assertTrue(current["wireframe_current"])
        self.assertEqual(current["preview_status"], "wireframe")
        self.assertFalse(stale["wireframe_current"])
        self.assertEqual(stale["preview_status"], "stale")

    def test_paid_preview_requires_brand_context_before_api_call(self):
        result = {"metadata": {"needs_product_images": False}, "preview_dir": Path("unused")}
        with self.assertRaisesRegex(ValueError, "--brand"):
            preview.generate_paid_preview(result, "", None, "1K")


if __name__ == "__main__":
    unittest.main(verbosity=2)
