#!/usr/bin/env python3
"""Image translator may only transfer approved, gated translations into finished ads."""

import hashlib
import importlib.util
import json
import subprocess
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "BONUS" / "03-image-translator" / "translate_ads.py"
SPEC = importlib.util.spec_from_file_location("generator_fixture", Path(__file__).with_name("test_generate_ads.py"))
fixture = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(fixture)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class ImageTranslatorGateTests(fixture.GeneratorContractTests):
    def setUp(self):
        super().setUp()
        self.outputs = self.adset / "outputs"
        folder = self.outputs / "01-headline-template-C01"
        folder.mkdir(parents=True)
        self.image = folder / "headline-template_v1_img1.png"
        self.image.write_bytes(b"png")
        self.qa_export = self.adset / "creative-qa.json"

    def register_render(self, qa_status="pass"):
        """Simuluje generate_ads manifest a dashboard export pre aktuálny zdroj."""
        source = self.adset / "prompts-sk.json"
        (self.outputs / "manifest.json").write_text(json.dumps({"results": [{
            "template": 1,
            "concept_id": "C01",
            "variation": "v1_img1",
            "aspect": "4:5",
            "file": f"brands/acme/products/hero-product/product-image-ads/{self.adset.name}/outputs/"
                    f"01-headline-template-C01/{self.image.name}",
            "sha256": sha(self.image),
            "render": {"prompts_file": source.name, "prompts_sha256": sha(source)},
        }]}), encoding="utf-8")
        self.qa_export.write_text(json.dumps({"items": [
            {"id": "x", "status": qa_status, "sha256": sha(self.image)},
        ]}), encoding="utf-8")

    def translate(self, *extra, qa=True):
        args = ["python3", str(SCRIPT), "--image", str(self.image), "--languages", "de", "--dry-run"]
        if qa:
            args += ["--qa-export", str(self.qa_export)]
        return subprocess.run(args + list(extra), check=False, capture_output=True, text=True)

    def test_approved_translation_is_transferred_verbatim(self):
        self.write_translation()
        self.register_render()
        result = self.translate()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('"Presný headline" → "Genaue Überschrift"', result.stdout)
        self.assertIn("outputs-de/01-headline-template-C01", result.stdout)

    def test_missing_translation_blocks(self):
        self.register_render()
        result = self.translate()
        self.assertEqual(result.returncode, 1)
        self.assertIn("prompts-de.json", result.stdout)

    def test_unapproved_translation_blocks(self):
        self.write_translation()
        self.register_render()
        (self.adset / "approval-de.json").unlink()
        self.assertEqual(self.translate().returncode, 1)

    def test_unconfirmed_foreign_price_blocks(self):
        self.prompts = self.adset / "prompts-sk.json"
        self.write_prompts(price="Len 49,90 €")
        self.write_gates()
        self.write_translation(price="Nur 49,90 €")
        self.write_gates(language="de", market_prices_confirmed=False)
        self.register_render()
        result = self.translate()
        self.assertEqual(result.returncode, 1)
        self.assertIn("market_prices_confirmed", result.stdout)

    def test_translated_copy_without_source_text_is_rejected(self):
        self.write_translation(price="Nur 49,90 €")
        self.register_render()
        result = self.translate()
        self.assertEqual(result.returncode, 1)
        self.assertIn("nemajú zdrojový text", result.stdout)

    def test_source_copy_without_approved_translation_is_rejected(self):
        self.prompts = self.adset / "prompts-sk.json"
        self.write_prompts(price="Stará ponuka")
        self.write_gates()
        self.write_translation()
        self.register_render()
        result = self.translate()
        self.assertEqual(result.returncode, 1)
        self.assertIn("nemajú schválený preklad", result.stdout)

    def test_unregistered_image_is_rejected(self):
        self.write_translation()
        self.register_render()
        unrelated = self.image.with_name("unrelated.png")
        unrelated.write_bytes(b"other")
        result = subprocess.run(
            ["python3", str(SCRIPT), "--image", str(unrelated), "--languages", "de", "--dry-run",
             "--qa-export", str(self.qa_export)],
            check=False, capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("manifest.json", result.stdout)

    def test_modified_image_is_rejected(self):
        self.write_translation()
        self.register_render()
        self.image.write_bytes(b"edited after render")
        result = self.translate()
        self.assertEqual(result.returncode, 1)
        self.assertIn("zmenil", result.stdout)

    def test_render_of_outdated_source_is_rejected(self):
        self.write_translation()
        self.register_render()
        manifest = json.loads((self.outputs / "manifest.json").read_text(encoding="utf-8"))
        manifest["results"][0]["render"]["prompts_sha256"] = "0" * 64
        (self.outputs / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        result = self.translate()
        self.assertEqual(result.returncode, 1)
        self.assertIn("nevznikol z aktuálneho", result.stdout)

    def test_visual_pass_is_required(self):
        self.write_translation()
        self.register_render(qa_status="minor")
        self.assertEqual(self.translate().returncode, 1)
        self.register_render()
        result = self.translate(qa=False)
        self.assertEqual(result.returncode, 1)
        self.assertIn("--qa-export", result.stdout)

    def test_image_outside_ad_set_is_rejected(self):
        loose = Path(self.tmp.name) / "loose.png"
        loose.write_bytes(b"png")
        result = subprocess.run(
            ["python3", str(SCRIPT), "--image", str(loose), "--languages", "de", "--dry-run"],
            check=False, capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 1)


# Rodičovské testy generátora sa tu nemajú spúšťať druhýkrát.
for name in list(vars(fixture.GeneratorContractTests)):
    if name.startswith("test_"):
        setattr(ImageTranslatorGateTests, name, None)


if __name__ == "__main__":
    unittest.main()
