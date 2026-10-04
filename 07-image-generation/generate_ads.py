#!/usr/bin/env python3
"""
Static Ad Generator — Step 7: validated image generation

Supports FAL AI and Google Gemini API as providers.
Default provider is google (Gemini / Nano Banana 2); fal a gpt-image len na požiadanie.

Usage:
    python generate_ads.py                          # Default: google (Nano Banana 2)
    python generate_ads.py --provider fal           # Use FAL AI directly (Nano Banana 2)
    python generate_ads.py --provider google        # Use Google Gemini API (Nano Banana 2)
    python generate_ads.py --provider gpt-image      # Use ChatGPT Images 2.0 (gpt-image-2) via FAL
    python generate_ads.py --provider gpt-image --quality medium  # Cheaper tier for iteration
    python generate_ads.py --templates 1,7,13,15    # Generate specific templates
    python generate_ads.py --resolution 2K          # Use 2K resolution
    python generate_ads.py --variations 3           # Generate 3 variations per template
    python generate_ads.py --dry-run                # Show what would be generated without calling API
    python generate_ads.py --prompts-file prompts/essentials-vitapack-prompts.json
    python generate_ads.py --images-dir source-product-images/essentials-vitapack
    python generate_ads.py --output-dir outputs/essentials-vitapack/sk

Required env vars:
    FAL_KEY         — FAL AI API key
    GEMINI_API_KEY  — Google Gemini API key (only if using google/google-batch provider)
"""

import argparse
import json
import os
import re
import sys
import time
import base64
import hashlib
import mimetypes
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TEST_PLANNING_DIR = REPO_ROOT / "04-test-planning"
if str(TEST_PLANNING_DIR) not in sys.path:
    sys.path.insert(0, str(TEST_PLANNING_DIR))

from test_plan import load_and_validate as load_and_validate_test_plan
from test_plan import plan_warnings as test_plan_warnings
from test_plan import sha256 as test_plan_sha256

try:
    import requests
except ImportError:
    print("Error: 'requests' package required. Install with: pip install requests")
    sys.exit(1)

try:
    from PIL import Image
    import io as _io
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False

try:
    from dotenv import load_dotenv
    _here = Path(__file__).resolve().parent
    for _candidate in (_here / ".env", _here.parent / ".env"):
        if _candidate.exists():
            load_dotenv(_candidate)
            break
except ImportError:
    pass


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

FAL_KEY = os.environ.get("FAL_KEY", "")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

FAL_DIRECT_URL = "https://fal.run"
T2I_ENDPOINT = "fal-ai/nano-banana-2"
EDIT_ENDPOINT = "fal-ai/nano-banana-2/edit"
# ChatGPT Images 2.0 (gpt-image-2) — beží tiež cez FAL, silnejší text-rendering engine.
GPT_IMAGE_T2I_ENDPOINT = "fal-ai/gpt-image-2"
GPT_IMAGE_EDIT_ENDPOINT = "openai/gpt-image-2/edit"
GEMINI_MODEL_ID = "gemini-3.1-flash-image"
FAL_MAX_IMAGES = 14  # common safe limit: Nano Banana 2 supports up to 14 references

DEFAULT_GPT_IMAGE_QUALITY = "high"  # low | medium | high

# gpt-image-2 používa image_size (nie aspect_ratio) — explicitné px, násobky 16, max hrana 3840.
# fit_exact (--exact-size) doreže na presné cieľové px, tieto slúžia len na správny pomer pri generovaní.
GPT_IMAGE_SIZES = {
    "1:1":    (1024, 1024),
    "4:5":    (1024, 1280),
    "2:3":    (1024, 1536),
    "3:4":    (1024, 1360),
    "9:16":   (1024, 1792),
    "16:9":   (1792, 1024),
    "1.91:1": (1536, 800),
}


def gpt_image_size(aspect: str) -> dict:
    """Vráti {'width','height'} (násobky 16) pre daný pomer pre gpt-image-2 image_size."""
    w, h = GPT_IMAGE_SIZES.get(aspect, (1024, 1024))
    return {"width": w, "height": h}


def google_image_size(resolution: str) -> str:
    """Gemini API spells the 0.5K tier as the literal value '512'."""
    return "512" if resolution == "0.5K" else resolution

MAX_POLL_TIME = 180
DEFAULT_RESOLUTION = "1K"
DEFAULT_OUTPUT_FORMAT = "png"
BRAND_REFERENCE_NAMES = (
    "brand-spec-card.png",
    "visual-style-card.png",
    "logo.png",
    "logo-white.png",
)

RESOLUTION_MAP_GOOGLE = {
    "0.5K": "512x512",
    "1K":   "1024x1024",
    "2K":   "2048x2048",
    "4K":   "4096x4096",
}


def collect_brand_reference_files(brand_cards_dir):
    """Return ordered raster brand references; SVG masters are never sent to image APIs."""
    if not brand_cards_dir:
        return []
    root = Path(brand_cards_dir)
    return [root / name for name in BRAND_REFERENCE_NAMES if (root / name).exists()]


# ---------------------------------------------------------------------------
# Provider selection
# ---------------------------------------------------------------------------

def select_provider():
    print("\n╔════════════════════════════════════════════════════════╗")
    print("║         Static Ad Generator — Provider               ║")
    print("╠════════════════════════════════════════════════════════╣")
    print("║  1. FAL — Nano Banana 2       (synchrónne)            ║")
    print("║  2. Google — Nano Banana 2    (synchrónne)            ║")
    print("║  3. Google Batch — NB2        (asynchrónne)           ║")
    print("║  4. FAL — ChatGPT Images 2.0  (silný text rendering)  ║")
    print("╚════════════════════════════════════════════════════════╝")
    while True:
        choice = input("\nVyber provider [1/2/3/4]: ").strip()
        if choice == "1":
            return "fal"
        elif choice == "2":
            return "google"
        elif choice == "3":
            return "google-batch"
        elif choice == "4":
            return "gpt-image"
        else:
            print("Zadaj 1, 2, 3 alebo 4.")


# ---------------------------------------------------------------------------
# FAL API helpers
# ---------------------------------------------------------------------------

def fal_headers():
    return {
        "Authorization": f"Key {FAL_KEY}",
        "Content-Type": "application/json",
    }


def upload_image_to_fal(image_path: str) -> str:
    mime_type = mimetypes.guess_type(image_path)[0] or "image/png"
    with open(image_path, "rb") as f:
        image_data = f.read()
    resp = requests.post(
        "https://fal.run/fal-ai/file-storage/upload",
        headers={"Authorization": f"Key {FAL_KEY}"},
        files={"file": (os.path.basename(image_path), image_data, mime_type)},
    )
    if resp.status_code != 200:
        b64 = base64.b64encode(image_data).decode("utf-8")
        return f"data:{mime_type};base64,{b64}"
    data = resp.json()
    return data.get("url", data.get("file_url", ""))


def run_generation_fal(endpoint: str, payload: dict) -> dict:
    url = f"{FAL_DIRECT_URL}/{endpoint}"
    resp = requests.post(url, headers=fal_headers(), json=payload, timeout=MAX_POLL_TIME)
    resp.raise_for_status()
    return resp.json()


def download_image(image_url: str, save_path: str):
    resp = requests.get(image_url, stream=True)
    resp.raise_for_status()
    with open(save_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)


def composite_product(image_source, product_png_path: str, placement: dict, save_path: str):
    if not PILLOW_AVAILABLE:
        print("     ⚠ Pillow not available — skipping product composite")
        return

    if isinstance(image_source, (str, Path)):
        base = Image.open(image_source).convert("RGBA")
    else:
        base = Image.open(_io.BytesIO(image_source)).convert("RGBA")

    product = Image.open(product_png_path).convert("RGBA")

    img_w, img_h = base.size
    area_x = int(placement["x"] * img_w)
    area_y = int(placement["y"] * img_h)
    area_w = int(placement["w"] * img_w)
    area_h = int(placement["h"] * img_h)

    product.thumbnail((area_w, area_h), Image.LANCZOS)

    offset_x = area_x + (area_w - product.width) // 2
    offset_y = area_y + (area_h - product.height) // 2

    base.paste(product, (offset_x, offset_y), product)
    base.convert("RGB").save(save_path, "PNG")
    print(f"     ✓ Product composited onto image")


# ---------------------------------------------------------------------------
# Google Gemini API helpers
# ---------------------------------------------------------------------------

def load_image_part_google(image_path: str):
    try:
        from google.genai import types
    except ImportError:
        print("Error: 'google-genai' package required. Install with: pip install google-genai")
        sys.exit(1)
    mime_type = mimetypes.guess_type(image_path)[0] or "image/png"
    with open(image_path, "rb") as f:
        data = f.read()
    return types.Part.from_bytes(data=data, mime_type=mime_type)


def run_generation_google(prompt_text: str, image_parts: list, aspect_ratio: str, resolution: str) -> bytes:
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        print("Error: 'google-genai' package required. Install with: pip install google-genai")
        sys.exit(1)
    client = genai.Client(api_key=GEMINI_API_KEY)
    contents = image_parts + [types.Part.from_text(text=prompt_text)]
    response = client.models.generate_content(
        model=GEMINI_MODEL_ID,
        contents=contents,
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE"],
            image_config=types.ImageConfig(
                aspect_ratio=aspect_ratio,
                image_size=google_image_size(resolution),
            ),
        ),
    )
    for part in response.candidates[0].content.parts:
        if part.inline_data:
            return part.inline_data.data
    raise ValueError("No image returned in response")


# ---------------------------------------------------------------------------
# Template name mapping
# ---------------------------------------------------------------------------

TEMPLATE_NAMES = {
    1: "headline",
    2: "offer-promotion",
    3: "testimonials",
    4: "features-benefits",
    5: "bullet-points",
    6: "social-proof",
    7: "us-vs-them",
    8: "before-after-ugc",
    9: "negative-marketing",
    10: "press-editorial",
    11: "pull-quote-review",
    12: "lifestyle-colorway",
    13: "stat-surround-hero",
    14: "bundle-showcase",
    15: "social-comment-screenshot",
    16: "curiosity-gap-testimonial",
    17: "verified-review-card",
    18: "stat-surround-flatlay",
    19: "highlighted-testimonial",
    20: "advertorial-editorial",
    21: "bold-statement",
    22: "flavor-story",
    23: "long-form-manifesto",
    24: "product-comment-callout",
    25: "us-vs-them-color-split",
    26: "stat-callout-lifestyle",
    27: "benefit-checklist",
    28: "feature-arrow-callout",
    29: "ugc-viral-post",
    30: "hero-statement-icon-bar",
    31: "comparison-grid",
    32: "ugc-story-callout",
    33: "faux-press-screenshot",
    34: "faux-iphone-notes",
    35: "hero-product-stat-bar",
    36: "whiteboard-before-after",
    37: "hero-statement-promo",
    38: "ugc-lifestyle-review-split",
    39: "curiosity-gap-scroll-stopper",
    40: "post-it-note-style",
}


# ---------------------------------------------------------------------------
# Placeholder substitution
# ---------------------------------------------------------------------------

PLACEHOLDER_PATTERN = re.compile(r"\{\{([\w.]+)\}\}")
BRACKETED_PLACEHOLDER_PATTERN = re.compile(r"\[[A-Z][A-Z][^\]]*\]")

GUARDRAIL_MARKER = "[GUARDRAIL_BAKED]"
GUARDRAIL = (
    "CRITICAL: Do NOT render any text from the brand spec card or visual style card into the output image — "
    "those are style references, not text content. The brand cards may contain font names, weight specifications, "
    "or instructional text — NONE of that text should appear in the final ad. The ONLY text in the output image "
    "is what is explicitly specified in the composition below."
)


def resolve_path(entry, path):
    """Resolve dot-notation path on entry: 'a.b.c' → entry['a']['b']['c'].
    Supports numeric indices for arrays: 'icons.0.value' → entry['icons'][0]['value'].
    Returns the resolved value or None if path doesn't exist or isn't a string-leaf.
    """
    parts = path.split(".")
    current = entry
    for part in parts:
        if isinstance(current, list):
            try:
                current = current[int(part)]
            except (ValueError, IndexError):
                return None
        elif isinstance(current, dict):
            if part not in current:
                return None
            current = current[part]
        else:
            return None
    return current


def safe_template_name(name):
    """template_name ide priamo do názvu priečinka — '/' by vyrobil vnorený adresár
    a uloženie PNG by zlyhalo až po API behu (drahé). Normalizuj separátory."""
    return str(name).replace("/", "-").replace("\\", "-").strip()


def prompt_concept_id(entry):
    """Return the workflow concept ID used as the stable creative/output identity."""
    brief = entry.get("brief") if isinstance(entry, dict) else None
    if not isinstance(brief, dict):
        return ""
    return str(brief.get("concept_id", "")).strip()


def output_folder_name(entry):
    """Build a collision-safe folder name; v2 concepts may share one template."""
    number = entry["template_number"]
    name = safe_template_name(
        entry.get("template_name", TEMPLATE_NAMES.get(number, f"template-{number}"))
    )
    concept_id = safe_template_name(prompt_concept_id(entry))
    suffix = f"-{concept_id}" if concept_id else ""
    return f"{number:02d}-{name}{suffix}"


def prepend_guardrail(prompt_text):
    """Auto-prepend brand-card guardrail (idempotent — won't double-prepend if marker present)."""
    if GUARDRAIL_MARKER in prompt_text:
        return prompt_text
    return f"{GUARDRAIL_MARKER}\n{GUARDRAIL}\n\n{prompt_text}"


def substitute_placeholders(prompt_text, entry):
    """Substituuje {{field}} aj {{nested.path}} placeholdery hodnotami z entry. Pre-flight validácia:
    1. Žiadny {{placeholder}} nesmie zostať nevyriešený
    2. Žiadny [BRACKETED PLACEHOLDER] nesmie zostať v prompt stringu (template doc syntax — mal byť transformovaný pred prompts.json)
    Auto-prepends brand-card guardrail if not already present.
    """
    # Auto-prepend guardrail (idempotent)
    result = prepend_guardrail(prompt_text)

    for match in PLACEHOLDER_PATTERN.finditer(result):
        path = match.group(1)
        if "." in path:
            value = resolve_path(entry, path)
        else:
            value = entry.get(path)
        if isinstance(value, str):
            result = result.replace(match.group(0), value)

    # Strip the guardrail marker before sending to AI (it's just a hint to avoid double-prepending)
    result = result.replace(f"{GUARDRAIL_MARKER}\n", "", 1)

    # Check 1: nevyriešené {{}} placeholdery
    unresolved = set(PLACEHOLDER_PATTERN.findall(result))
    if unresolved:
        tpl = entry.get("template_number", "?")
        raise ValueError(
            f"Unresolved {{placeholder}} in prompt for template {tpl}: {sorted(unresolved)}. "
            f"Note: dot-notation supported (e.g. {{table.left_col_header}}, {{icons.0.value}}). "
            f"Available top-level fields: {sorted(entry.keys())}"
        )

    # Check 2: zabudnuté [BRACKETED] placeholdery (templaty používajú [HEADLINE] etc.
    # ako documentation syntax; mali byť transformované na {{}} alebo nahradené hodnotami pri builde)
    leftover_brackets = set(BRACKETED_PLACEHOLDER_PATTERN.findall(result))
    if leftover_brackets:
        tpl = entry.get("template_number", "?")
        raise ValueError(
            f"Leftover [BRACKETED] placeholders in prompt for template {tpl}: {sorted(leftover_brackets)}. "
            f"Templaty používajú [BRACKETED] ako documentation syntax — Claude pri builde má transformovať "
            f"runtime fields na {{{{placeholder}}}} a build-time fields nahradiť priamo hodnotami. "
            f"Pozri copy-prompt.md guidance."
        )

    return result


# ---------------------------------------------------------------------------
# Pre-generation prompt validation
# ---------------------------------------------------------------------------

REFERENCE_PHRASES = ["reference image", "shown in the reference", "reproduce it exactly", "reproduce the product exactly"]
INVENTION_PATTERNS = ["white/cream bottle", "white/cream shampoo", "matte black box", "amber/white cosmetic",
                      "blue bottle", "green bottle", "red bottle", "plastic bottle", "glass jar", "metal tube"]

# Ceny v image ads sú POVOLENÉ (rozhodnutie 2026-08-06, nahradilo staré plošné G01).
# Detekcia zostáva, ale slúži na kontrolu, nie na blokovanie:
#   - default: vypíše nájdené ceny ako info (over ich voči offer-brief/product-facts)
#   - --lang != sk: ceny sú confirm-issue (najčastejšia chyba je cena skopírovaná
#     z SK JSON do iného trhu bez prepočtu meny)
#   - --no-prices: tvrdý zákaz pre daný beh / brand
# Matchuje aj integer aj decimal sumy + symbol/word v oboch poradiach
PRICE_PATTERN = re.compile(
    r"[€$£¥]\s*\d+(?:[,.]\d+)?|"                                            # €5, $10, £4.99, €0,12
    r"\b\d+(?:[,.]\d+)?\s*(?:eur|euro|usd|gbp|kč|ft|lei|zł|chf)\b|"          # 5,95 eur / 149 Kč / 2400 Ft
    r"\b(?:eur|euro|usd|gbp|kč|ft|lei|zł|chf)\s*\d+(?:[,.]\d+)?\b|"          # eur 5,95 / Kč 149
    r"\b\d+(?:[,.]\d+)?\s*[€$£¥]",                                           # 5,95€ / 0.12$ / 149€
    re.IGNORECASE
)
# Copy fields ktoré sa renderujú v image (text inventory)
RENDERABLE_COPY_FIELDS = [
    "headline", "subhead", "body", "cta", "rating", "subhead_italic",
    "review_1", "review_2", "review_text", "reviewer", "product_name",
]


def find_prices_in_entry(entry):
    """Vráť zoznam (field, snippet) tuplov pre každý field s detegovanou cenou.
    Skenuje renderable copy fields (headline/subhead/cta/...) + array fields (bullets/headline_lines/icons/table.rows)."""
    hits = []
    for field in RENDERABLE_COPY_FIELDS:
        val = entry.get(field)
        if isinstance(val, str):
            m = PRICE_PATTERN.search(val)
            if m:
                hits.append((field, m.group(0)))
    # Array fields: bullets, headline_lines, callouts
    for field in ("bullets", "headline_lines", "callouts"):
        items = entry.get(field, [])
        if isinstance(items, list):
            for i, item in enumerate(items):
                if isinstance(item, str):
                    m = PRICE_PATTERN.search(item)
                    if m:
                        hits.append((f"{field}[{i}]", m.group(0)))
    # Icons: list of dicts with value + label
    for i, icon in enumerate(entry.get("icons", []) or []):
        for k in ("value", "label"):
            v = icon.get(k) if isinstance(icon, dict) else None
            if isinstance(v, str):
                m = PRICE_PATTERN.search(v)
                if m:
                    hits.append((f"icons[{i}].{k}", m.group(0)))
    # Table rows: attr/left/right
    for i, row in enumerate(entry.get("table", {}).get("rows", []) or []):
        for k in ("attr", "left", "right"):
            v = row.get(k) if isinstance(row, dict) else None
            if isinstance(v, str):
                m = PRICE_PATTERN.search(v)
                if m:
                    hits.append((f"table.rows[{i}].{k}", m.group(0)))
    return hits


def prompt_artifact_path(prompts_path: Path, artifact: str) -> Path:
    """prompts-sk.json -> scoring-sk.json / approval-sk.json."""
    name = prompts_path.name
    suffix = name[len("prompts"):] if name.startswith("prompts") else f"-{prompts_path.stem}"
    return prompts_path.with_name(f"{artifact}{suffix}")


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def lang_from_prompts_name(name: str):
    """prompts-hu.json -> 'hu'; iné názvy nevedia jazyk určiť."""
    match = re.fullmatch(r"prompts-([a-z]{2,3})\.json", Path(name).name.lower())
    return match.group(1) if match else None


DEFAULT_HOOK_FIELD = "headline"
RESEARCH_DOCS = (
    "deep-research.md",
    "avatar-sheet.md",
    "offer-brief.md",
    "necessary-beliefs.md",
    "cep-sheet.md",
    "briefs.md",
)


def normalize_copy(value) -> str:
    """Porovnanie hooku ignoruje iba biele znaky a veľkosť písmen (štýl, nie obsah)."""
    return " ".join(str(value).split()).casefold()


def hook_fields(entry) -> list:
    brief = entry.get("brief") if isinstance(entry.get("brief"), dict) else {}
    raw = brief.get("hook_field", DEFAULT_HOOK_FIELD)
    if isinstance(raw, str):
        return [raw.strip()] if raw.strip() else []
    if isinstance(raw, list) and raw and all(isinstance(item, str) and item.strip() for item in raw):
        return [item.strip() for item in raw]
    return []


def rendered_hook_issues(entry, label, planned_hook=None) -> list:
    """Plánovaný hook musí byť presne text, ktorý sa renderuje cez {{placeholder}} polia."""
    fields = hook_fields(entry)
    if not fields:
        return [f"✗ {label}: brief.hook_field musí byť názov poľa alebo zoznam polí s renderovaným hookom"]
    raw_prompt = str(entry.get("ai_prompt") or entry.get("prompt") or "")
    rendered_paths = set(PLACEHOLDER_PATTERN.findall(raw_prompt))
    issues = []
    values = []
    for field in fields:
        value = resolve_path(entry, field) if "." in field else entry.get(field)
        if not isinstance(value, str) or not value.strip():
            issues.append(f"✗ {label}: hook pole '{field}' chýba alebo je prázdne")
            continue
        values.append(value)
        if field not in rendered_paths:
            issues.append(
                f"✗ {label}: prompt nerenderuje hook cez {{{{{field}}}}} — text hooku nesmie byť v prompte natvrdo"
            )
    if planned_hook is not None and not issues and normalize_copy(" ".join(values)) != normalize_copy(planned_hook):
        issues.append(
            f"✗ {label}: renderovaný hook ({' + '.join(fields)}) nesedí s hookom konceptu v test-plan.json — "
            f"zmena hooku sa vracia do B1"
        )
    return issues


def load_translation_source(prompts_data: dict, prompts_path: Path):
    """Preklad musí odkazovať na schválený zdrojový prompts JSON v tom istom ad sete."""
    name = prompts_data.get("source_prompts")
    if not isinstance(name, str) or not name.strip() or Path(name).name != name:
        return None, None, ["✗ source_prompts musí byť názov súboru v tom istom ad sete (napr. prompts-sk.json)"]
    source_path = prompts_path.parent / name
    if source_path.resolve() == prompts_path.resolve():
        return None, None, ["✗ source_prompts nesmie odkazovať sám na seba"]
    try:
        source_data = json.loads(source_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None, None, [f"✗ source_prompts {name} neexistuje"]
    except (OSError, json.JSONDecodeError) as exc:
        return None, None, [f"✗ neplatný source_prompts {name}: {exc}"]
    if not isinstance(source_data, dict):
        return None, None, [f"✗ source_prompts {name} musí obsahovať JSON objekt"]
    issues = []
    if source_data.get("source_prompts"):
        issues.append(f"✗ {name} je sám prekladom; prekladaj iba zo schváleného zdroja")
    if source_data.get("test_plan") != prompts_data.get("test_plan"):
        issues.append(f"✗ preklad a {name} nie sú naviazané na ten istý test-plan.json")
    return source_path, source_data, issues


def research_source_dir(facts_path: Path):
    """Resolve `research-source:` header from product-facts.md; None = vlastný research."""
    try:
        text = facts_path.read_text(encoding="utf-8")
    except OSError:
        return None
    match = re.search(r"research-source:\s*`?([^`\n]+?)`?\s*$", text, re.MULTILINE)
    if not match or match.group(1).strip().lower() in ("self", ""):
        return None
    value = match.group(1).strip()
    for base in (facts_path.parent, facts_path.parent.parent):
        candidate = (base / value).resolve()
        if candidate.is_dir():
            return candidate
    return (facts_path.parent / value).resolve()


def validate_research_docs(ad_set_dir: Path, require_facts=False):
    """Workflow v2: strategický research (vlastný alebo zdedený) musí existovať pred generovaním.

    `require_facts` (plány schema 2) robí z chýbajúceho product-facts.md chybu, nie varovanie.
    """
    ad_set_dir = ad_set_dir.resolve()
    if ad_set_dir.parent.name != "product-image-ads":
        return ["✗ workflow v2 očakáva ad set v products/<produkt>/product-image-ads/<ad-set>/ — research sa nedá overiť"], []
    research_dir = ad_set_dir.parent.parent / "marketing-research"
    facts = research_dir / "product-facts.md"
    warnings = []
    if facts.is_file():
        inherited = research_source_dir(facts)
        if inherited:
            research_dir = inherited
    elif require_facts:
        return [f"✗ Chýba {facts} — každé SKU má overené fakty; pri zdedenom researchi s hlavičkou research-source"], []
    else:
        warnings.append("⚠ chýba marketing-research/product-facts.md — fakty SKU (cena, rozmery, claims) over ručne")
    missing = [
        name for name in RESEARCH_DOCS
        if not (research_dir / name).is_file() or not (research_dir / name).read_text(encoding="utf-8").strip()
    ]
    if missing:
        return [f"✗ Strategický research v {research_dir} nie je kompletný, chýba: {', '.join(missing)}"], warnings
    return [], warnings


COPY_COLLECTION_FIELDS = ("bullets", "headline_lines", "callouts", "icons", "table")


def rendered_copy(entry) -> dict:
    """Všetko copy, ktoré sa môže vykresliť do banneru."""
    fields = list(RENDERABLE_COPY_FIELDS) + list(COPY_COLLECTION_FIELDS)
    return {field: entry[field] for field in fields if field in entry}


def price_snippets(entry) -> list:
    return sorted(snippet for _, snippet in find_prices_in_entry(entry))


def rendered_isolation_issues(test_variable: str, entries: list) -> list:
    """Izolovaný test musí byť izolovaný aj v tom, čo zákazník vidí, nielen v metadátach plánu."""
    if len(entries) < 2:
        return []
    base = entries[0]
    base_id = prompt_concept_id(base)
    issues = []
    for entry in entries[1:]:
        concept_id = prompt_concept_id(entry)
        if test_variable == "hook":
            # Hook test: prompty sa smú líšiť iba v brief a v poliach hooku.
            skip = {"brief"} | {field.split(".")[0] for field in hook_fields(base) + hook_fields(entry)}
            keys = (set(base) | set(entry)) - skip
            differing = sorted(key for key in keys if base.get(key) != entry.get(key))
            if differing:
                issues.append(
                    f"✗ izolovaný hook test: {concept_id} sa od {base_id} líši aj mimo hooku "
                    f"({', '.join(differing)}); ak sa má meniť viac, je to concept-comparison"
                )
            continue
        if test_variable == "visual" and rendered_copy(base) != rendered_copy(entry):
            issues.append(f"✗ izolovaný test vizuálu: {concept_id} má iné copy než {base_id}; copy musí ostať rovnaké")
        if test_variable != "offer" and price_snippets(base) != price_snippets(entry):
            issues.append(
                f"✗ izolovaný test '{test_variable}': {concept_id} má inú cenu než {base_id}; "
                f"ponuka sa mení iba v teste 'offer'"
            )
        if test_variable == "angle" and base.get("cta") != entry.get("cta"):
            issues.append(f"✗ izolovaný test angle: {concept_id} má iné CTA než {base_id}; CTA je konštanta")
    return issues


def plan_schema_version(ad_set_dir: Path):
    try:
        plan = json.loads((ad_set_dir / "test-plan.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return plan.get("schema_version") if isinstance(plan, dict) else None


def validate_strategy_contract(
    prompts_data: dict,
    prompts_path: Path,
    templates_filter=None,
    allow_legacy=False,
):
    """Validate the workflow v2 binding from prompts to the upstream B1 test plan.

    Files without workflow_version are legacy and require an explicit opt-in. Every
    new ad set must declare workflow_version 2 and bind exact prompt concepts to
    test-plan.json.
    """
    version = prompts_data.get("workflow_version")
    if version is None:
        if allow_legacy:
            print("  ⚠ Legacy workflow povolený cez --allow-legacy: bez test-plan.json väzby")
            return []
        return [
            "✗ chýba workflow_version 2 + test-plan.json väzba; "
            "starý ad set spusti iba vedome s --allow-legacy"
        ]
    if version != 2:
        return ["✗ workflow_version musí byť 2 (alebo sa pri starom ad sete úplne vynechá)"]

    issues = []
    plan_ref = prompts_data.get("test_plan")
    if not isinstance(plan_ref, dict):
        return ["✗ workflow v2 vyžaduje test_plan objekt s id a sha256"]
    for field in ("id", "sha256"):
        if not isinstance(plan_ref.get(field), str) or not plan_ref[field].strip():
            issues.append(f"✗ test_plan.{field} je povinné")

    plan_path = prompts_path.parent / "test-plan.json"
    plan, plan_issues = load_and_validate_test_plan(plan_path)
    issues.extend(f"✗ test-plan.json: {issue}" for issue in plan_issues)
    if plan_issues:
        return issues

    if plan.get("schema_version") == 1:
        if not allow_legacy:
            issues.append(
                "✗ test-plan.json má schema_version 1 — starý plán bez strojovej kontroly izolácie, prahov "
                "a learnings. Existujúci ad set spusti vedome s --allow-legacy; nový plán vytvor cez "
                "test_plan.py init (schema 2)"
            )
        else:
            for warning in test_plan_warnings(plan):
                print(f"  ⚠ Povolené cez --allow-legacy: {warning}")
    if plan_ref.get("id") != plan.get("plan_id"):
        issues.append("✗ test_plan.id nesedí s test-plan.json plan_id")
    if plan_ref.get("sha256") != test_plan_sha256(plan_path):
        issues.append("✗ test_plan.sha256 nesedí — testovací plán sa po vytvorení promptov zmenil")

    # Preklad (source_prompts) nesie zamknutý brief zo schváleného zdroja; hook sa porovnáva
    # so zdrojom, lebo preložený headline sa legitímne líši od slovenského hooku v pláne.
    source_entries = None
    if "source_prompts" in prompts_data:
        _, source_data, source_issues = load_translation_source(prompts_data, prompts_path)
        issues.extend(source_issues)
        if source_data is not None:
            source_entries = {
                prompt_concept_id(item): item
                for item in source_data.get("prompts", [])
                if isinstance(item, dict) and prompt_concept_id(item)
            }

    variants = {
        item["concept_id"]: item
        for item in plan.get("variants", [])
        if isinstance(item, dict) and item.get("concept_id")
    }
    prompts = prompts_data.get("prompts", [])
    if not isinstance(prompts, list):
        return issues

    planned_ids = set(variants)
    prompt_ids = []
    prompt_id_locations = {}
    for index, entry in enumerate(prompts):
        concept_id = prompt_concept_id(entry)
        if not concept_id:
            continue
        prompt_ids.append(concept_id)
        prompt_id_locations.setdefault(concept_id, []).append(index)

    prompt_id_set = set(prompt_ids)
    for concept_id in sorted(planned_ids - prompt_id_set):
        issues.append(f"✗ test-plan.json koncept {concept_id} nemá zodpovedajúci prompt")
    for concept_id in sorted(prompt_id_set - planned_ids):
        locations = ", ".join(str(i) for i in prompt_id_locations[concept_id])
        issues.append(f"✗ prompts[{locations}]: concept_id '{concept_id}' nie je v test-plan.json")
    for concept_id, locations in sorted(prompt_id_locations.items()):
        if len(locations) > 1:
            joined = ", ".join(str(i) for i in locations)
            issues.append(f"✗ concept_id '{concept_id}' je v promptoch duplicitne na indexoch {joined}")

    for index, entry in enumerate(prompts):
        if not isinstance(entry, dict):
            continue
        number = entry.get("template_number")
        if templates_filter is not None and number not in templates_filter:
            continue
        brief = entry.get("brief")
        if not isinstance(brief, dict):
            continue
        for field in ("concept_id", "awareness_stage", "hook"):
            if not isinstance(brief.get(field), str) or not brief[field].strip():
                issues.append(f"✗ T{number or index}: brief.{field} je povinné vo workflow v2")
        concept_id = str(brief.get("concept_id", "")).strip()
        if not concept_id:
            continue
        planned = variants.get(concept_id)
        if not planned:
            continue
        comparisons = {
            "id": "brief_id",
            "persona": "persona",
            "angle": "angle",
            "awareness_stage": "awareness_stage",
            "hook": "hook",
        }
        for brief_field, plan_field in comparisons.items():
            if brief.get(brief_field) != planned.get(plan_field):
                issues.append(
                    f"✗ T{number or index}: brief.{brief_field} nesedí s konceptom {concept_id} "
                    f"v test-plan.json"
                )
        planned_template = planned.get("template_number")
        if planned_template is not None and number != planned_template:
            issues.append(
                f"✗ T{number or index}: template_number nesedí s konceptom {concept_id} v test-plan.json"
            )

        label = f"T{number or index} ({concept_id})"
        if source_entries is None:
            issues.extend(rendered_hook_issues(entry, label, planned.get("hook")))
            continue
        source_entry = source_entries.get(concept_id)
        if source_entry is None:
            issues.append(f"✗ {label}: koncept chýba v zdrojovom {prompts_data.get('source_prompts')}")
            continue
        if brief != source_entry.get("brief"):
            issues.append(f"✗ {label}: brief prekladu sa líši od zdroja — brief je pri preklade zamknutý")
        if number != source_entry.get("template_number"):
            issues.append(f"✗ {label}: template_number prekladu sa líši od zdroja")
        issues.extend(rendered_hook_issues(entry, label))
        issues.extend(rendered_hook_issues(source_entry, f"{label} zdroj", planned.get("hook")))

    if plan.get("schema_version") == 2 and str(plan.get("test_design", "")).lower() == "isolated":
        planned_entries = [
            entry for entry in prompts
            if isinstance(entry, dict) and prompt_concept_id(entry) in variants
        ]
        issues.extend(rendered_isolation_issues(str(plan.get("test_variable", "")).lower(), planned_entries))

    return issues


def load_gate_artifact(path: Path, missing_label: str):
    """Brána existuje iba ako JSON objekt; null, pole či reťazec je chyba, nie prázdna brána."""
    if not path.exists():
        return None, [f"✗ Chýba {missing_label}: {path.name}"]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return None, [f"✗ Neplatný {path.name}: {exc}"]
    if not isinstance(data, dict):
        return None, [f"✗ Neplatný {path.name}: musí obsahovať JSON objekt, nie {type(data).__name__}"]
    return data, []


OVERRIDABLE_AGENTS = ("01", "02", "03", "05")
AI_APPROVERS = ("", "ai", "agent", "assistant", "chatgpt", "claude", "codex")


def human_override_valid(scoring: dict, agent_id: str, result: dict, prompt_hash: str) -> bool:
    """Vedomá výnimka človeka pre tvorivé hodnotenie (01, 02, 03, 05) viazaná na presné bajty promptov.
    Skutočné skóre agenta musí ostať zapísané; výnimka ho nemaže, iba ho vedome prijíma."""
    if agent_id not in OVERRIDABLE_AGENTS:
        return False
    overrides = scoring.get("human_overrides")
    override = overrides.get(agent_id) if isinstance(overrides, dict) else None
    if not isinstance(override, dict):
        return False
    score = result.get("score")
    return (
        str(override.get("by", "")).strip().lower() not in AI_APPROVERS
        and bool(override.get("at"))
        and bool(str(override.get("reason", "")).strip())
        and override.get("prompts_sha256") == prompt_hash
        and not isinstance(score, bool)
        and isinstance(score, (int, float))
        and override.get("score_at_override") == score
    )


def scoring_issues(scoring: dict, prompt_hash: str, name: str, required_mode=None) -> list:
    issues = []
    if scoring.get("schema_version") != 1:
        issues.append(f"✗ {name}: schema_version musí byť 1")
    if str(scoring.get("status", "")).lower() != "passed":
        issues.append(f"✗ {name}: status musí byť 'passed'")
    if scoring.get("prompts_sha256") != prompt_hash:
        issues.append(f"✗ {name}: prompts_sha256 nesedí — copy sa po scoringu zmenilo")
    mode = scoring.get("mode", "source")
    if mode not in ("source", "translation"):
        issues.append(f"✗ {name}: mode musí byť 'source' alebo 'translation'")
    if required_mode and mode != required_mode:
        issues.append(f"✗ {name}: mode musí byť '{required_mode}'")
    required_agents = ["04", "05", "06", "07", "08"] if mode == "translation" else [f"{i:02d}" for i in range(1, 9)]
    agents = scoring.get("agents")
    if not isinstance(agents, dict):
        return issues + [f"✗ {name}: agents musí byť objekt s výsledkami agentov"]
    for agent_id in required_agents:
        result = agents.get(agent_id)
        if not isinstance(result, dict):
            issues.append(f"✗ {name}: chýba výsledok agenta {agent_id}")
            continue
        if human_override_valid(scoring, agent_id, result, prompt_hash):
            continue
        if str(result.get("verdict", "")).upper() != "PASS":
            issues.append(f"✗ {name}: agent {agent_id} nemá PASS")
        if agent_id != "08":
            score = result.get("score")
            if isinstance(score, bool) or not isinstance(score, (int, float)) or score < 90:
                issues.append(f"✗ {name}: agent {agent_id} musí mať score >= 90")
    return issues


def approval_issues(approval: dict, prompt_hash: str, name: str, lang=None) -> list:
    issues = []
    if approval.get("schema_version") != 1:
        issues.append(f"✗ {name}: schema_version musí byť 1")
    if str(approval.get("status", "")).lower() != "approved":
        issues.append(f"✗ {name}: status musí byť 'approved'")
    if str(approval.get("approved_by", "")).strip().lower() in AI_APPROVERS:
        issues.append(f"✗ {name}: approved_by musí označovať človeka")
    if not approval.get("approved_at"):
        issues.append(f"✗ {name}: chýba approved_at")
    if approval.get("prompts_sha256") != prompt_hash:
        issues.append(f"✗ {name}: prompts_sha256 nesedí — copy sa po schválení zmenilo")
    if lang and approval.get("language") and str(approval.get("language", "")).lower() != lang.lower():
        issues.append(f"✗ {name}: language nesedí s --lang {lang}")
    return issues


def translation_source_gate_issues(prompts_path: Path, prompts_data: dict, scoring: dict, scoring_name: str) -> list:
    """Preklad (source_prompts) platí iba nad schváleným a plne skórovaným zdrojom — v každom mode."""
    source_path, _, source_issues = load_translation_source(prompts_data, prompts_path)
    if source_path is None or source_issues:
        return []  # konkrétnu chybu hlási strategický kontrakt
    source_hash = file_sha256(source_path)
    issues = []
    if scoring.get("source_prompts_sha256") != source_hash:
        issues.append(
            f"✗ {scoring_name}: source_prompts_sha256 nesedí so {source_path.name} — "
            f"zdroj sa po preklade zmenil alebo väzba chýba (workflow_gate.py init-scoring --mode translation)"
        )
    source_scoring_path = prompt_artifact_path(source_path, "scoring")
    source_scoring, load_issues = load_gate_artifact(source_scoring_path, "scoring zdroja")
    issues.extend(load_issues)
    if source_scoring is not None:
        issues.extend(scoring_issues(source_scoring, source_hash, source_scoring_path.name, required_mode="source"))
    source_approval_path = prompt_artifact_path(source_path, "approval")
    source_approval, load_issues = load_gate_artifact(source_approval_path, "schválenie zdroja")
    issues.extend(load_issues)
    if source_approval is not None:
        issues.extend(approval_issues(source_approval, source_hash, source_approval_path.name))
    return issues


def validate_workflow_gates(prompts_path: Path, lang: str, prompts_data=None):
    """Validate machine-readable scoring and explicit human approval for exact prompt bytes."""
    if prompts_data is None:
        prompts_data = json.loads(prompts_path.read_text(encoding="utf-8"))
    issues = []
    prompt_hash = file_sha256(prompts_path)
    scoring_path = prompt_artifact_path(prompts_path, "scoring")
    approval_path = prompt_artifact_path(prompts_path, "approval")

    scoring, load_issues = load_gate_artifact(scoring_path, "scoring gate")
    issues.extend(load_issues)
    if scoring is not None:
        issues.extend(scoring_issues(scoring, prompt_hash, scoring_path.name))
        # O preklade rozhoduje source_prompts (rovnako ako strategický kontrakt), nie mode:
        # aj plný scoring 01–08 prekladu nesmie vypnúť väzbu na schválený zdroj.
        if "source_prompts" in prompts_data:
            issues.extend(translation_source_gate_issues(prompts_path, prompts_data, scoring, scoring_path.name))
        elif scoring.get("mode", "source") == "translation":
            issues.append(
                f"✗ {scoring_path.name}: mode 'translation' vyžaduje v prompts JSON pole source_prompts; "
                f"nový zdrojový text má mode 'source' a všetkých 8 agentov"
            )

    approval, load_issues = load_gate_artifact(approval_path, "human approval gate")
    issues.extend(load_issues)
    if approval is not None:
        issues.extend(approval_issues(approval, prompt_hash, approval_path.name, lang))

    return issues, approval or {}, scoring_path, approval_path


def validate_prompts_quick(prompts, templates_filter, images_dir, brand_cards_dir=None,
                           block_prices=False, lang="sk", market_prices_confirmed=False,
                           price_confirmation_required=None):
    issues = []
    if not isinstance(prompts, list) or not prompts:
        return ["✗ prompts[] chýba alebo je prázdne"]

    filtered = []
    for index, entry in enumerate(prompts):
        if not isinstance(entry, dict):
            issues.append(f"✗ prompts[{index}] musí byť objekt")
            continue
        number = entry.get("template_number")
        if not isinstance(number, int):
            issues.append(f"✗ prompts[{index}].template_number musí byť číslo")
            continue
        if templates_filter is None or number in templates_filter:
            filtered.append(entry)

    if templates_filter is not None and not filtered:
        issues.append(f"✗ --templates nevybral žiadny prompt: {templates_filter}")

    seen_outputs = set()
    for index, entry in enumerate(filtered):
        number = entry["template_number"]
        name = entry.get("template_name")
        if not isinstance(name, str) or not name.strip():
            issues.append(f"✗ T{number}: chýba template_name")
        concept_id = prompt_concept_id(entry)
        key = (number, safe_template_name(name or ""), safe_template_name(concept_id))
        if key in seen_outputs:
            issues.append(
                f"✗ T{number}: duplicitná výstupná identita "
                f"(template_number + template_name + concept_id) by prepísala výstup"
            )
        seen_outputs.add(key)
        brief = entry.get("brief")
        if not isinstance(brief, dict):
            issues.append(f"✗ T{number}: chýba brief objekt")
        else:
            for field in ("id", "persona", "angle", "emotion", "customer_voice_anchor"):
                if not brief.get(field):
                    issues.append(f"✗ T{number}: brief.{field} je povinné")
        raw_prompt = entry.get("ai_prompt") or entry.get("prompt")
        if not isinstance(raw_prompt, str) or not raw_prompt.strip():
            issues.append(f"✗ T{number}: chýba prompt/ai_prompt")
        else:
            try:
                substitute_placeholders(raw_prompt, entry)
            except ValueError as exc:
                issues.append(f"✗ T{number}: {exc}")

    missing_ref = []
    invented = []
    price_hits = []
    for p in filtered:
        prompt = str(p.get("ai_prompt") or p.get("prompt") or "").lower()
        needs_images = p.get("needs_product_images", True)
        num = p["template_number"]
        if needs_images:
            if not any(ph in prompt for ph in REFERENCE_PHRASES):
                missing_ref.append(num)
            for pat in INVENTION_PATTERNS:
                if pat.lower() in prompt:
                    invented.append((num, pat))
        # Price detection in copy fields — informatívne, nie blokujúce (viď PRICE_PATTERN)
        hits = find_prices_in_entry(p)
        if hits:
            for field, snippet in hits:
                price_hits.append((num, field, snippet))

    if missing_ref:
        issues.append(f"✗ Chýba 'reference image' v {len(missing_ref)} template(och): {missing_ref}")
    if invented:
        for num, pat in invented:
            issues.append(f"✗ T{num:02d}: podozrivý popis produktu '{pat}'")
    if price_hits:
        if block_prices:
            for num, field, snippet in price_hits:
                issues.append(
                    f"✗ T{num}: cena '{snippet}' v poli '{field}' — beh spustený s --no-prices. "
                    f"Odstráň cenu alebo spusti bez --no-prices."
                )
        elif (lang != "sk" if price_confirmation_required is None else price_confirmation_required) \
                and not market_prices_confirmed:
            for num, field, snippet in price_hits:
                issues.append(
                    f"✗ T{num}: cena '{snippet}' v poli '{field}' pri --lang {lang} — over menu a sumu "
                    f"pre daný trh. Ceny sa pri preklade často prenesú zo zdroja bez prepočtu."
                )
        else:
            print(f"  ⓘ Ceny v copy ({len(price_hits)}×) — over voči offer-brief / product-facts:")
            for num, field, snippet in price_hits:
                print(f"     T{num}: '{snippet}' v poli '{field}'")
            print("     Cena v obrázku je povolená; zodpovedáš za to, že je aktuálna a platná pre trh.")

    if not brand_cards_dir or not (brand_cards_dir / "brand-spec-card.png").exists() or not (brand_cards_dir / "visual-style-card.png").exists():
        issues.append("✗ Chýbajú obe povinné brand cards: brand-spec-card.png + visual-style-card.png")

    needs_images_templates = [p["template_number"] for p in filtered if p.get("needs_product_images", True)]
    if needs_images_templates and (not images_dir or not images_dir.is_dir()):
        issues.append(f"✗ Priečinok s produktovými obrázkami neexistuje: {images_dir}")
    elif images_dir and images_dir.exists():
        img_files = [f for f in images_dir.iterdir()
                     if f.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp") and not f.name.startswith(".")]
        if needs_images_templates and not img_files:
            issues.append(f"✗ Žiadne produktové obrázky v {images_dir}")
        else:
            if needs_images_templates and not issues:
                issues_info = f"✓ {len(img_files)} obrázok(ov) nájdených pre {len(needs_images_templates)} template(ov) s needs_product_images=true"
                print(f"  {issues_info}")

    return issues


# ---------------------------------------------------------------------------
# Main generation logic
# ---------------------------------------------------------------------------

ASPECT_DIMS = {
    "1:1": "1080x1080",
    "4:5": "1080x1350",
    "9:16": "1080x1920",
    "16:9": "1920x1080",
    "2:3": "1080x1620",
    "1.91:1": "1200x628",  # Google Ads / PMax landscape
}

# PMax (Google Ads Performance Max) sada pomerov — landscape, square, portrait.
PMAX_ASPECTS = ["1.91:1", "1:1", "4:5"]
PMAX_DIMS = {
    "1.91:1": "1200x628",
    "1:1": "1200x1200",
    "4:5": "960x1200",
}

# Pomery, ktoré image API (Gemini/fal) priamo akceptuje.
SUPPORTED_API_ASPECTS = {
    "1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4",
    "9:16", "16:9", "21:9", "1:4", "4:1", "1:8", "8:1",
}
# Nepodporovaný cieľový pomer → najbližší podporovaný pre API call (presné px dorieši fit_exact).
API_ASPECT_FALLBACK = {"1.91:1": "16:9"}


def api_aspect(ratio: str) -> str:
    """Vráti pomer, ktorý image API akceptuje. Pre nepodporované (napr. 1.91:1) najbližší
    podporovaný (16:9); presné cieľové px potom doreže fit_exact."""
    if ratio in SUPPORTED_API_ASPECTS:
        return ratio
    return API_ASPECT_FALLBACK.get(ratio, ratio)


def default_output_dir(lang: str = "sk", pmax: bool = False) -> str:
    """Keep optional PMax exports separate from the canonical Meta outputs."""
    base = "outputs" if not lang or lang == "sk" else f"outputs-{lang}"
    return f"{base}-pmax" if pmax else base


def reframe_prompt(prompt_text: str, target_ratio: str) -> str:
    """Prepíše natvrdo zapísaný pomer (napr. '4:5 (1080x1350)') na cieľový pomer.
    Pri vertikálnom 9:16 pridá reframe inštrukciu pre Reels/Stories (rovnaký koncept,
    využité vertikálne miesto, safe-zóny pre UI). Tým istý banner vznikne aj v 9:16."""
    dims = ASPECT_DIMS.get(target_ratio, "")
    target_str = f"{target_ratio} ({dims})" if dims else target_ratio
    new = re.sub(r"\b\d{1,2}:\d{1,2}\s*\(\d{3,4}x\d{3,4}\)", target_str, prompt_text)
    new = re.sub(r"(aspect ratio\s+)\d{1,2}:\d{1,2}", r"\g<1>" + target_ratio, new, flags=re.IGNORECASE)
    # Záchranná sieť: prompt, ktorý pomer píše bez rozmerov („Create a 4:5 vertical static ad").
    # Viazané na „Create a/an", aby sa neprepisovali pomery clony či iné čísla v texte.
    new = re.sub(r"(Create an?\s+)\d{1,2}:\d{1,2}", r"\g<1>" + target_str, new)
    if target_ratio == "9:16":
        new += (
            "\n\nREFRAME FOR 9:16 VERTICAL (Reels/Stories): recompose the SAME concept for a tall "
            "9:16 frame — keep the product as the centered hero and use the extra vertical space "
            "naturally (more background above and below), do not stretch, crop awkwardly or distort "
            "anything. Identical colors, typography, copy and product fidelity as specified above.\n"
            "REELS SAFE ZONES (strict): keep the TOP ~12% and the BOTTOM ~28% of the frame completely "
            "clear of any text, headline, CTA, badge, logo or important product detail — these bands are "
            "covered by the Reels/Stories UI (profile, caption, action buttons). Place ALL text, CTA, "
            "badges and key elements within the central ~60% vertical band. The product hero may extend "
            "into the bands visually, but nothing critical (text/CTA/logo) may sit there.\n"
            "PLACEMENT OVERRIDE (this rule wins): ignore ANY earlier instruction in this prompt that puts "
            "the call to action, headline, subhead, badge or logo near the bottom edge, in a bottom corner "
            "or in the lower part of the frame — those describe the feed layout of a shorter format and do "
            "NOT apply here. In this 9:16 frame the call to action button sits inside the central band, "
            "roughly two thirds of the way down, and never in the bottom quarter."
        )
    elif target_ratio in ("1.91:1", "16:9"):
        new += (
            "\n\nREFRAME FOR WIDE LANDSCAPE (Google Ads / Performance Max): recompose the SAME concept "
            "for a wide horizontal frame — do NOT just letterbox or stretch the portrait layout. Use a "
            "side-by-side composition: the product as the hero on ONE side (roughly 45–55% of the width) "
            "and the text elements grouped on the OTHER side, vertically centered and comfortably "
            "readable. Fill the whole frame edge to edge with the scene/background; no empty bars. Keep a "
            "clear margin on all four edges and keep all critical content inside the center 80% safe area "
            "so nothing important is cropped across Google placements. Identical colors, typography, "
            "copy and product fidelity as specified above.\n"
            "STRICT TEXT RULE: render ONLY the exact text elements already specified above (the same "
            "headline/subhead/stats/CTA/badge values and NOTHING else). Do NOT invent a CTA, button, "
            "tagline or label that was not specified. Do NOT render any text, labels or tags from the "
            "brand spec card or visual style card (e.g. 'BRAND SPEC CARD') into the image."
        )
    elif target_ratio == "1:1":
        new += (
            "\n\nREFRAME FOR 1:1 SQUARE (Google Ads / feed): recompose the SAME concept for a balanced "
            "square frame — product as the centered hero, text/CTA/badge arranged in a balanced layout "
            "(headline top or product-side), filling the frame edge to edge with no empty bars. Keep a "
            "clear margin on all four edges and keep all critical content inside the center 80% safe area. "
            "Identical colors, typography, copy and product fidelity as "
            "specified above."
        )
    elif target_ratio == "4:5":
        new += (
            "\n\nREFRAME FOR 4:5 PORTRAIT ASSET: preserve the SAME approved Meta concept and copy, "
            "but keep the product, headline, CTA, logo and every other critical element inside the center "
            "80% safe area so Google placements can crop the asset safely. Do not invent, remove or "
            "rewrite any text or visual claim."
        )
    return new


def _parse_dims(dim_str: str):
    """'1200x628' -> (1200, 628)."""
    try:
        w, h = dim_str.lower().split("x")
        return int(w), int(h)
    except Exception:
        return None


def fit_exact(path, dim_str: str):
    """Doreže/zmenší obrázok na presné px rozmery (cover + center-crop), bez deformácie.
    Pre PMax assety priamo nahrateľné do Google Ads (napr. 1200x628)."""
    if not PILLOW_AVAILABLE:
        print(f"     ⚠ Pillow chýba — presný rozmer {dim_str} sa nepoužil")
        return
    dims = _parse_dims(dim_str)
    if not dims:
        return
    tw, th = dims
    im = Image.open(path).convert("RGB")
    sw, sh = im.size
    if (sw, sh) == (tw, th):
        return
    scale = max(tw / sw, th / sh)
    nw, nh = round(sw * scale), round(sh * scale)
    im = im.resize((nw, nh), Image.LANCZOS)
    left, top = (nw - tw) // 2, (nh - th) // 2
    im = im.crop((left, top, left + tw, top + th))
    im.save(path)


LOGO_POSITIONS = ("bottom-left", "bottom-right", "top-left", "top-right")


def pick_logo_variant(brand_cards_dir, base_im, box):
    """Vyber farebné alebo biele logo podľa jasu plochy, na ktorú sa vkladá."""
    root = Path(brand_cards_dir)
    colored, white = root / "logo.png", root / "logo-white.png"
    if not colored.exists() and not white.exists():
        return None
    if not white.exists():
        return colored
    if not colored.exists():
        return white
    patch = base_im.convert("RGB").crop(box)
    background = relative_luminance(*patch.resize((1, 1), Image.BILINEAR).getpixel((0, 0)))
    # Stredne sivý podklad (dlažba, betón) prekĺzol cez prah jasu 128 so zeleným logom, ktoré
    # tam malo kontrast ~1,9 : 1 (klient 2026-09-14). Vyber verziu s vyšším kontrastom.
    contrast = {
        path: contrast_ratio(logo_luminance(path), background) for path in (colored, white)
    }
    return max(contrast, key=contrast.get)


def relative_luminance(r, g, b):
    def channel(value):
        c = value / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b)


def contrast_ratio(a, b):
    light, dark = max(a, b), min(a, b)
    return (light + 0.05) / (dark + 0.05)


def logo_luminance(path):
    """Priemerná relatívna svietivosť nepriehľadných pixelov loga."""
    logo = Image.open(path).convert("RGBA")
    logo.thumbnail((64, 64))
    pixels = [(r, g, b) for r, g, b, a in logo.getdata() if a > 128]
    if not pixels:
        return 1.0
    return sum(relative_luminance(*p) for p in pixels) / len(pixels)


def discard_stale_clean_copy(path):
    """Pred vložením loga do NOVO vygenerovaného obrázka zmaže čistú kópiu z predošlého behu.
    Inak by --logo-keep-clean nechal starý render a place_logo.py by vrátil starý banner."""
    stale = Path(path).parent / "_clean" / Path(path).name
    if stale.exists():
        stale.unlink()


def composite_logo(path, brand_cards_dir, width_ratio=0.18, margin_ratio=0.05,
                   position="bottom-left", margin_y_ratio=None, keep_clean=False):
    """Vloží reálne logo značky do hotového obrázka.

    Logo je asset, nie predmet dohadovania s generatívnym modelom — vkladá sa
    deterministicky až po generovaní, takže je vždy úplné, správne veľké a práve raz.

    `margin_y_ratio` oddeľuje zvislý okraj od vodorovného. Pri 9:16 pre Reels/Stories
    zaberá UI spodných ~28 % výšky, takže logo musí ísť vyššie, kým vodorovný okraj
    zostáva úzky. Bez toho by logo skončilo pod tlačidlami prehrávača.

    Vracia (nazov_suboru_loga, (w, h)) alebo None.
    """
    if not PILLOW_AVAILABLE:
        print("     ⚠ Pillow chýba — logo sa nevložilo")
        return None
    if position not in LOGO_POSITIONS:
        raise ValueError(f"position musí byť jedna z {LOGO_POSITIONS}")
    src = Path(path)
    if keep_clean:
        clean_dir = src.parent / "_clean"
        clean_dir.mkdir(parents=True, exist_ok=True)
        clean_path = clean_dir / src.name
        if not clean_path.exists():
            Image.open(src).convert("RGB").save(clean_path)
    base = Image.open(path).convert("RGBA")
    bw, bh = base.size
    target_w = max(1, round(bw * width_ratio))
    margin_x = round(bw * margin_ratio)
    margin_y = round(bh * (margin_ratio if margin_y_ratio is None else margin_y_ratio))

    # Predbežný box na odhad jasu podkladu (výška podľa pomeru strán loga doladí sa nižšie).
    probe_h = max(1, round(target_w * 0.2))
    if position.startswith("bottom"):
        py = bh - margin_y - probe_h
    else:
        py = margin_y
    px_ = margin_x if position.endswith("left") else bw - margin_x - target_w
    probe_box = (max(0, px_), max(0, py), min(bw, px_ + target_w), min(bh, py + probe_h))

    logo_path = pick_logo_variant(brand_cards_dir, base, probe_box)
    if not logo_path:
        print("     ⚠ V brand-dna nie je logo.png ani logo-white.png — logo sa nevložilo")
        return None

    logo = Image.open(logo_path).convert("RGBA")
    ratio = logo.height / logo.width
    target_h = max(1, round(target_w * ratio))
    logo = logo.resize((target_w, target_h), Image.LANCZOS)

    x = margin_x if position.endswith("left") else bw - margin_x - target_w
    y = margin_y if position.startswith("top") else bh - margin_y - target_h
    base.alpha_composite(logo, (x, y))
    base.convert("RGB").save(path)
    return logo_path.name, (target_w, target_h)


def price_confirmation_needed(prompts_data: dict, prompts_path: Path, lang: str) -> bool:
    """Cena potrebuje potvrdenie trhu pri preklade alebo keď jazyk nesedí s trhom plánu."""
    if prompts_data.get("source_prompts"):
        return True
    try:
        plan = json.loads((prompts_path.parent / "test-plan.json").read_text(encoding="utf-8"))
        market = str(plan.get("market", "")).strip().lower()
    except (OSError, json.JSONDecodeError, AttributeError):
        market = ""
    return not market or market != lang.lower()


def render_model_id(provider: str) -> str:
    if provider == "gpt-image":
        return "gpt-image-2"
    if provider == "fal":
        return EDIT_ENDPOINT
    return GEMINI_MODEL_ID


def render_provenance(prompts_path, prompts_data, approval_path, provider, resolution, quality,
                      brand_cards_dir, image_files, exact_size, logo_overlay) -> dict:
    assets = {}
    reference_files = collect_brand_reference_files(brand_cards_dir) if brand_cards_dir else []
    for path in list(reference_files) + list(image_files or []):
        path = Path(path)
        try:
            key = str(path.resolve().relative_to(REPO_ROOT))
        except ValueError:
            key = path.name
        try:
            assets[key] = file_sha256(path)
        except OSError:
            assets[key] = None
    return {
        "prompts_file": prompts_path.name,
        "prompts_sha256": file_sha256(prompts_path),
        "test_plan": prompts_data.get("test_plan"),
        "approval_file": approval_path.name,
        "provider": provider,
        "model": render_model_id(provider),
        "resolution": quality if provider == "gpt-image" else resolution,
        "exact_size": bool(exact_size),
        "logo_overlay": bool(logo_overlay),
        "assets": assets,
    }


def generate_ads(
    provider,
    brand_dir,
    prompts_file=None,
    images_dir=None,
    output_dir=None,
    templates_filter=None,
    concepts_filter=None,
    resolution=DEFAULT_RESOLUTION,
    num_variations=1,
    dry_run=False,
    block_prices=False,
    lang="sk",
    aspects=None,
    exact_size=False,
    exact_dimensions=None,
    quality=DEFAULT_GPT_IMAGE_QUALITY,
    validate_only=False,
    allow_legacy=False,
    logo_overlay=False,
    logo_width=0.18,
    logo_position="bottom-left",
    logo_margin_y=None,
    logo_keep_clean=False,
):
    brand_path = Path(brand_dir)

    if prompts_file:
        prompts_path = Path(prompts_file) if Path(prompts_file).is_absolute() else brand_path / prompts_file
    else:
        # Auto-detect prompts-{lang}.json (default sk) — fall back to legacy prompts.json
        candidates = [brand_path / f"prompts-{lang}.json", brand_path / "prompts-sk.json", brand_path / "prompts.json"]
        prompts_path = next((p for p in candidates if p.exists()), brand_path / f"prompts-{lang}.json")

    if images_dir:
        product_images_dir = Path(images_dir) if Path(images_dir).is_absolute() else brand_path / images_dir
    else:
        # Canonical layout: <product>/product-image-ads/<ad-set>/, while images
        # live directly in <product>/source-product-images/.
        image_candidates = [
            brand_path / "source-product-images",
            brand_path.parent.parent / "source-product-images",
        ]
        product_images_dir = next((p for p in image_candidates if p.is_dir()), image_candidates[1])

    if output_dir:
        outputs_dir = Path(output_dir) if Path(output_dir).is_absolute() else brand_path / output_dir
    else:
        outputs_dir = brand_path / "outputs"

    # Auto-detect brand-dna folder pre brand-spec-card.png + visual-style-card.png
    # Path traversal: hľadá `brand-dna/` v parents od product_images_dir
    brand_cards_dir = None
    search_path = product_images_dir.resolve() if product_images_dir.exists() else brand_path.resolve()
    for parent in [search_path] + list(search_path.parents):
        candidate = parent / "brand-dna"
        if candidate.is_dir() and (candidate / "brand-spec-card.png").exists():
            brand_cards_dir = candidate
            break

    if not prompts_path.exists():
        print(f"Error: {prompts_path} not found. Complete step 5 first.")
        sys.exit(1)

    if not dry_run and not validate_only:
        if provider in ("fal", "gpt-image") and not FAL_KEY:
            print("Error: FAL_KEY not set. Set with: export FAL_KEY='your-key'")
            sys.exit(1)
        if provider in ("google", "google-batch") and not GEMINI_API_KEY:
            print("Error: GEMINI_API_KEY not set. Set with: export GEMINI_API_KEY='your-key'")
            sys.exit(1)

    with open(prompts_path, encoding="utf-8") as f:
        prompts_data = json.load(f)
    if not isinstance(prompts_data, dict):
        print(f"Error: {prompts_path.name} musí obsahovať JSON objekt.")
        return 1

    brand_name = prompts_data.get("brand", "unknown")
    prompts = prompts_data.get("prompts", [])

    gate_issues, approval, scoring_path, approval_path = validate_workflow_gates(
        prompts_path, lang, prompts_data
    )
    issues = validate_strategy_contract(
        prompts_data,
        prompts_path,
        templates_filter,
        allow_legacy=allow_legacy,
    )
    is_v2 = prompts_data.get("workflow_version") == 2
    if is_v2:
        research_issues, research_warnings = validate_research_docs(
            brand_path, require_facts=plan_schema_version(prompts_path.parent) == 2
        )
        issues.extend(research_issues)
        for warning in research_warnings:
            print(f"  {warning}")
    issues.extend(validate_prompts_quick(
        prompts, templates_filter, product_images_dir, brand_cards_dir=brand_cards_dir,
        block_prices=block_prices, lang=lang,
        market_prices_confirmed=bool(approval.get("market_prices_confirmed")),
        price_confirmation_required=price_confirmation_needed(prompts_data, prompts_path, lang) if is_v2 else None,
    ))
    issues.extend(gate_issues)
    if issues:
        print("\n✗ PRE-FLIGHT ZLYHAL:")
        for issue in issues:
            print(f"   {issue}")
        print("\nGenerovanie je zablokované. Oprav kontrakt, scoring alebo schválenie a spusti znova.")
        return 1
    print(f"  ✓ Workflow gates: {scoring_path.name} + {approval_path.name}")
    print()

    if templates_filter:
        prompts = [p for p in prompts if p["template_number"] in templates_filter]
    if concepts_filter:
        # Regenerácia jedného chybného variantu, keď viac konceptov zdieľa template (pravidlo: nemaž hotové výstupy).
        prompts = [p for p in prompts if (p.get("brief") or {}).get("concept_id") in concepts_filter]
        if not prompts:
            print(f"✗ --concepts nevybral žiadny prompt: {', '.join(concepts_filter)}")
            return 1

    print(f"\n{'='*60}")
    print(f"  Static Ad Generator — {brand_name}")
    print(f"  Provider: {provider.upper()}")
    print(f"  Prompts file: {prompts_path}")
    print(f"  Images dir:   {product_images_dir}")
    print(f"  Brand cards:  {brand_cards_dir if brand_cards_dir else '(not found — only product images will be sent)'}")
    quality_or_res = f"Quality: {quality}" if provider == "gpt-image" else f"Resolution: {resolution}"
    print(f"  Templates: {len(prompts)} | {quality_or_res} | Variations: {num_variations}")
    print(f"{'='*60}\n")

    if validate_only:
        print("VALIDATION PASS — kontrakt, scoring, schválenie aj vstupy sú platné.")
        return 0

    brand_image_urls = []
    product_image_urls = []
    brand_image_parts = []
    product_image_parts = []
    image_files = []

    # Raster brand references — cards are required; standalone PNG logos are optional.
    # SVG remains the editable master but is intentionally not sent to image APIs.
    if brand_cards_dir and not dry_run:
        brand_card_files = collect_brand_reference_files(brand_cards_dir)

        if brand_card_files:
            if provider in ("fal", "gpt-image"):
                print(f"Uploading {len(brand_card_files)} brand reference(s) from {brand_cards_dir.name}/...")
                for card_file in brand_card_files:
                    try:
                        url = upload_image_to_fal(str(card_file))
                        brand_image_urls.append(url)
                        print(f"  ✓ {card_file.name} (brand reference)")
                    except Exception as e:
                        print(f"  ✗ {card_file.name}: {e}")
            else:
                print(f"Loading {len(brand_card_files)} brand reference(s) from {brand_cards_dir.name}/...")
                for card_file in brand_card_files:
                    try:
                        part = load_image_part_google(str(card_file))
                        brand_image_parts.append(part)
                        print(f"  ✓ {card_file.name} (brand reference)")
                    except Exception as e:
                        print(f"  ✗ {card_file.name}: {e}")
            print()

    if product_images_dir.exists() and not dry_run:
        image_files = sorted([
            f for f in product_images_dir.iterdir()
            if f.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp")
        ])
        if image_files:
            if provider in ("fal", "gpt-image"):
                print(f"Uploading {len(image_files)} product image(s) to FAL storage...")
                for img_file in image_files:
                    try:
                        url = upload_image_to_fal(str(img_file))
                        product_image_urls.append(url)
                        print(f"  ✓ {img_file.name}")
                    except Exception as e:
                        print(f"  ✗ {img_file.name}: {e}")
            else:
                print(f"Loading {len(image_files)} product image(s)...")
                for img_file in image_files:
                    try:
                        part = load_image_part_google(str(img_file))
                        product_image_parts.append(part)
                        print(f"  ✓ {img_file.name}")
                    except Exception as e:
                        print(f"  ✗ {img_file.name}: {e}")
            print()
        else:
            print("Warning: No product images found in images dir.\n")

    render_inputs = render_provenance(
        prompts_path, prompts_data, approval_path, provider, resolution, quality,
        brand_cards_dir, image_files, exact_size, logo_overlay,
    )

    results = []
    # Aspect ratios: ak --aspects nie je zadané, použije sa natívny pomer každého promptu (spätná
    # kompatibilita). Ak je zadané (napr. "4:5,9:16"), každý banner sa vygeneruje v každom pomere.
    aspects_list = [a.strip() for a in aspects.split(",") if a.strip()] if aspects else None
    if aspects_list and provider == "google-batch":
        print("  ⚠ --aspects sa pri provideri google-batch ignoruje (batch používa natívny pomer).")
        aspects_list = None
    ratios = aspects_list if aspects_list else [None]
    if aspects_list:
        print(f"  Aspect ratios: {', '.join(aspects_list)}")

    total = len(prompts) * num_variations * len(ratios)
    completed = 0
    failed = 0

    if provider == "google-batch" and not dry_run:
        from google import genai
        client = genai.Client(api_key=GEMINI_API_KEY)
        results, completed, failed = run_generation_google_batch(
            client, prompts, brand_image_parts, product_image_parts, outputs_dir,
            brand_name, num_variations, resolution,
            brand_cards_dir=brand_cards_dir, logo_overlay=logo_overlay,
            logo_width=logo_width, logo_position=logo_position,
            logo_margin_y=logo_margin_y, logo_keep_clean=logo_keep_clean,
        )
    else:
        for prompt_entry in prompts:
            tpl_num = prompt_entry["template_number"]
            tpl_name = safe_template_name(prompt_entry.get("template_name", TEMPLATE_NAMES.get(tpl_num, f"template-{tpl_num}")))
            is_hybrid = isinstance(prompt_entry.get("ai_prompt"), str) and bool(prompt_entry["ai_prompt"].strip())
            raw_prompt = prompt_entry["ai_prompt"] if is_hybrid else prompt_entry["prompt"]
            prompt_text = substitute_placeholders(raw_prompt, prompt_entry)
            product_placement = prompt_entry.get("product_placement") if is_hybrid else None
            aspect_ratio = prompt_entry.get("aspect_ratio", "1:1")
            needs_images = prompt_entry.get("needs_product_images", True)

            concept_id = prompt_concept_id(prompt_entry)
            folder_name = output_folder_name(prompt_entry)
            output_folder = outputs_dir / folder_name

            print(f"[{tpl_num:02d}] {tpl_name}")

            if dry_run:
                for ratio in ratios:
                    eff_aspect = ratio if ratio else aspect_ratio
                    print(f"     → DRY RUN: {num_variations} variation(s) | Aspect: {eff_aspect} | Provider: {provider}")
                print()
                continue

            output_folder.mkdir(parents=True, exist_ok=True)

            for ratio in ratios:
                eff_aspect = ratio if ratio else aspect_ratio
                req_aspect = api_aspect(eff_aspect)  # čo reálne pošleme do API (podporovaný pomer)
                eff_prompt = reframe_prompt(prompt_text, ratio) if ratio else prompt_text
                dimension_map = exact_dimensions or ASPECT_DIMS
                dim_str = dimension_map.get(eff_aspect) if exact_size else None
                if ratio:
                    slug = dim_str if (exact_size and dim_str) else ratio.replace(":", "x")
                else:
                    slug = None

                prompt_file = f"prompt_{slug}.txt" if slug else "prompt.txt"
                with open(output_folder / prompt_file, "w") as f:
                    f.write(eff_prompt)

                for var_idx in range(num_variations):
                    var_label = f"v{var_idx + 1}" if num_variations > 1 else "v1"
                    suffix = f"_{slug}" if slug else ""

                    try:
                        ratio_note = f" [{eff_aspect}]" if slug else ""
                        print(f"     → Generating ({var_label}){ratio_note} via {provider}...")

                        if provider in ("fal", "gpt-image"):
                            num_images = 1
                            reference_urls = brand_image_urls + (
                                product_image_urls if needs_images else []
                            )
                            if provider == "gpt-image":
                                # ChatGPT Images 2.0 — image_size (px) + quality tier namiesto aspect_ratio/resolution.
                                if reference_urls:
                                    endpoint = GPT_IMAGE_EDIT_ENDPOINT
                                    payload = {
                                        "prompt": eff_prompt,
                                        "image_urls": reference_urls[:FAL_MAX_IMAGES],
                                        "image_size": gpt_image_size(req_aspect),
                                        "quality": quality,
                                        "num_images": num_images,
                                        "output_format": DEFAULT_OUTPUT_FORMAT,
                                    }
                                else:
                                    endpoint = GPT_IMAGE_T2I_ENDPOINT
                                    payload = {
                                        "prompt": eff_prompt,
                                        "image_size": gpt_image_size(req_aspect),
                                        "quality": quality,
                                        "num_images": num_images,
                                        "output_format": DEFAULT_OUTPUT_FORMAT,
                                    }
                            elif reference_urls:
                                endpoint = EDIT_ENDPOINT
                                payload = {
                                    "prompt": eff_prompt,
                                    "image_urls": reference_urls[:FAL_MAX_IMAGES],
                                    "aspect_ratio": req_aspect,
                                    "num_images": num_images,
                                    "output_format": DEFAULT_OUTPUT_FORMAT,
                                    "resolution": resolution,
                                    "safety_tolerance": "5",
                                    "limit_generations": False,
                                }
                            else:
                                endpoint = T2I_ENDPOINT
                                payload = {
                                    "prompt": eff_prompt,
                                    "aspect_ratio": req_aspect,
                                    "num_images": num_images,
                                    "output_format": DEFAULT_OUTPUT_FORMAT,
                                    "resolution": resolution,
                                    "safety_tolerance": "5",
                                    "limit_generations": False,
                                }
                            result = run_generation_fal(endpoint, payload)
                            images = result.get("images", [])
                            if not images:
                                print(f"     ✗ No images returned")
                                failed += 1
                                continue
                            img_url = images[0].get("url", "")
                            if not img_url:
                                print(f"     ✗ No image URL in response")
                                failed += 1
                                continue
                            save_name = f"{tpl_name}_{var_label}{suffix}_img1.{DEFAULT_OUTPUT_FORMAT}"
                            save_path = output_folder / save_name
                            download_image(img_url, str(save_path))
                            if product_placement and product_image_urls:
                                product_local = image_files[0] if image_files else None
                                if product_local:
                                    composite_product(save_path, str(product_local), product_placement, str(save_path))

                        else:
                            image_parts = brand_image_parts + (
                                product_image_parts if needs_images else []
                            )
                            img_bytes = run_generation_google(
                                eff_prompt, image_parts, req_aspect, resolution
                            )
                            save_name = f"{tpl_name}_{var_label}{suffix}_img1.{DEFAULT_OUTPUT_FORMAT}"
                            save_path = output_folder / save_name
                            if product_placement and image_files:
                                composite_product(img_bytes, str(image_files[0]), product_placement, str(save_path))
                            else:
                                with open(save_path, "wb") as f:
                                    f.write(img_bytes)

                        if dim_str:
                            fit_exact(str(save_path), dim_str)

                        if logo_overlay and brand_cards_dir:
                            discard_stale_clean_copy(save_path)
                            placed = composite_logo(
                                str(save_path), brand_cards_dir,
                                width_ratio=logo_width, position=logo_position,
                                margin_y_ratio=logo_margin_y, keep_clean=logo_keep_clean,
                            )
                            if placed:
                                print(f"     ✓ Logo vložené: {placed[0]} {placed[1][0]}x{placed[1][1]} px ({logo_position})")

                        print(f"     ✓ Saved: {save_name}")
                        completed += 1
                        results.append({
                            "template": tpl_num,
                            "name": tpl_name,
                            "concept_id": concept_id or None,
                            "variation": f"{var_label}{suffix}_img1",
                            "aspect": eff_aspect,
                            "file": str(save_path),
                        })

                    except Exception as e:
                        print(f"     ✗ Error: {e}")
                        failed += 1

            print()

    if not dry_run:
        print(f"\n{'='*60}")
        print(f"  Generation Complete")
        print(f"  ✓ Completed: {completed}/{total}")
        if failed:
            print(f"  ✗ Failed: {failed}/{total}")
        print(f"  Output: {outputs_dir}/")
        print(f"{'='*60}\n")

        # Presná verzia renderu: hash finálneho PNG + vstupy, z ktorých vznikol.
        # Vizuálny QA aj B2 handoff sa viažu na tento hash, nie iba na cestu.
        for result in results:
            try:
                result["sha256"] = file_sha256(Path(result["file"]))
            except OSError:
                result["sha256"] = None
            result["render"] = render_inputs

        manifest_path = outputs_dir / "manifest.json"
        # Zlúč s existujúcim manifestom, nech ostanú aj reklamy z predošlých behov.
        prev_results = []
        if manifest_path.exists():
            try:
                prev_results = json.load(open(manifest_path)).get("results", [])
            except Exception:
                prev_results = []
        seen = {r.get("file") for r in results}
        merged_results = results + [r for r in prev_results if r.get("file") not in seen]
        manifest = {
            "brand": brand_name,
            "provider": provider,
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "resolution": resolution,
            "total_generated": len(merged_results),
            "total_failed": failed,
            "last_run_generated": completed,
            "results": merged_results,
        }
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)
        print(f"Manifest saved: {manifest_path}")

        generate_gallery(outputs_dir, brand_name, results)

    return 1 if failed else 0


def run_generation_google_batch(
    client, prompts, brand_image_parts, product_image_parts, outputs_dir,
    brand_name, num_variations, resolution,
    brand_cards_dir=None, logo_overlay=False, logo_width=0.18,
    logo_position="bottom-left", logo_margin_y=None, logo_keep_clean=False,
):
    try:
        from google.genai import types
        import tempfile
    except ImportError:
        print("Error: 'google-genai' package required. Install with: pip install google-genai")
        sys.exit(1)

    request_map = {}
    jsonl_lines = []

    for entry_idx, prompt_entry in enumerate(prompts, start=1):
        tpl_num = prompt_entry["template_number"]
        tpl_name = safe_template_name(prompt_entry.get("template_name", TEMPLATE_NAMES.get(tpl_num, f"template-{tpl_num}")))
        raw_prompt = prompt_entry.get("ai_prompt") or prompt_entry.get("prompt", "")
        prompt_text = substitute_placeholders(raw_prompt, prompt_entry)
        aspect_ratio = prompt_entry.get("aspect_ratio", "1:1")
        needs_images = prompt_entry.get("needs_product_images", True)

        concept_id = prompt_concept_id(prompt_entry)
        folder_name = output_folder_name(prompt_entry)
        output_folder = outputs_dir / folder_name
        output_folder.mkdir(parents=True, exist_ok=True)

        with open(output_folder / "prompt.txt", "w") as f:
            f.write(prompt_text)

        for var_idx in range(num_variations):
            var_label = f"v{var_idx + 1}" if num_variations > 1 else "v1"
            key = f"ad{entry_idx:03d}_tpl{tpl_num:02d}_{var_label}"
            request_map[key] = (
                tpl_num, tpl_name, concept_id, var_label, output_folder, aspect_ratio
            )

            parts = []
            for img_part in brand_image_parts:
                parts.append({
                    "inlineData": {
                        "mimeType": img_part.inline_data.mime_type,
                        "data": base64.b64encode(img_part.inline_data.data).decode("utf-8")
                    }
                })
            if needs_images and product_image_parts:
                for img_part in product_image_parts:
                    parts.append({
                        "inlineData": {
                            "mimeType": img_part.inline_data.mime_type,
                            "data": base64.b64encode(img_part.inline_data.data).decode("utf-8")
                        }
                    })
            parts.append({"text": prompt_text})

            jsonl_lines.append(json.dumps({
                "key": key,
                "request": {
                    "contents": [{"parts": parts}],
                    "generation_config": {
                        "responseModalities": ["IMAGE"],
                        "imageConfig": {
                            "aspectRatio": api_aspect(aspect_ratio),
                            "imageSize": google_image_size(resolution)
                        }
                    }
                }
            }))

    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
        f.write("\n".join(jsonl_lines))
        jsonl_path = f.name

    print(f"Uploading batch file ({len(jsonl_lines)} requests)...")
    uploaded_file = client.files.upload(
        file=jsonl_path,
        config=types.UploadFileConfig(display_name=f'{brand_name}-batch', mime_type='jsonl')
    )

    print(f"Submitting batch job...")
    batch_job = client.batches.create(
        model=GEMINI_MODEL_ID,
        src=uploaded_file.name,
        config={"display_name": f"{brand_name}-ads-batch"}
    )
    print(f"Batch job created: {batch_job.name}")
    print(f"Waiting for results (up to 24h, checking every 30s)...\n")

    completed_states = {"JOB_STATE_SUCCEEDED", "JOB_STATE_FAILED", "JOB_STATE_CANCELLED", "JOB_STATE_EXPIRED"}
    while True:
        batch_job = client.batches.get(name=batch_job.name)
        state = batch_job.state.name
        print(f"  Status: {state} ({time.strftime('%H:%M:%S')})")
        if state in completed_states:
            break
        time.sleep(30)

    if batch_job.state.name != "JOB_STATE_SUCCEEDED":
        print(f"  ✗ Batch job failed: {batch_job.state.name}")
        return [], 0, len(request_map)

    result_file = batch_job.dest.file_name
    file_content = client.files.download(file=result_file)
    results = []
    completed = 0
    failed = 0

    for line in file_content.decode("utf-8").splitlines():
        if not line:
            continue
        resp = json.loads(line)
        key = resp.get("key", "")
        if key not in request_map:
            continue
        tpl_num, tpl_name, concept_id, var_label, output_folder, aspect_ratio = request_map[key]
        try:
            parts = resp["response"]["candidates"][0]["content"]["parts"]
            img_bytes = None
            for part in parts:
                if "inlineData" in part:
                    img_bytes = base64.b64decode(part["inlineData"]["data"])
                    break
            if not img_bytes:
                print(f"  ✗ [{tpl_num:02d}] {tpl_name}: no image in response")
                failed += 1
                continue
            save_name = f"{tpl_name}_{var_label}_img1.{DEFAULT_OUTPUT_FORMAT}"
            save_path = output_folder / save_name
            with open(save_path, "wb") as f:
                f.write(img_bytes)
            if logo_overlay and brand_cards_dir:
                discard_stale_clean_copy(save_path)
                composite_logo(str(save_path), brand_cards_dir,
                               width_ratio=logo_width, position=logo_position,
                               margin_y_ratio=logo_margin_y, keep_clean=logo_keep_clean)
            print(f"  ✓ [{tpl_num:02d}] {tpl_name}: {save_name}")
            completed += 1
            results.append({
                "template": tpl_num,
                "name": tpl_name,
                "concept_id": concept_id or None,
                "variation": f"{var_label}_img1",
                "aspect": aspect_ratio,
                "file": str(save_path),
            })
        except Exception as e:
            print(f"  ✗ [{tpl_num:02d}] {tpl_name}: {e}")
            failed += 1

    os.unlink(jsonl_path)
    return results, completed, failed


def generate_gallery(outputs_dir: Path, brand_name: str, results: list):
    html_parts = [f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{brand_name} — Static Ad Gallery</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #0a0a0a; color: #fff; padding: 2rem; }}
  h1 {{ font-size: 1.8rem; margin-bottom: 0.5rem; }}
  .meta {{ color: #888; margin-bottom: 2rem; font-size: 0.9rem; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 1.5rem; }}
  .card {{ background: #1a1a1a; border-radius: 12px; overflow: hidden; }}
  .card img {{ width: 100%; display: block; }}
  .card .info {{ padding: 1rem; }}
  .card .info h3 {{ font-size: 0.95rem; margin-bottom: 0.3rem; }}
  .card .info p {{ font-size: 0.8rem; color: #888; }}
</style>
</head>
<body>
<h1>{brand_name} — Static Ad Gallery</h1>
<p class="meta">Updated {time.strftime("%B %d, %Y")} · __COUNT__ ads</p>
<div class="grid">
"""]

    # Skenuj CELÝ výstupný priečinok (každá reklama = vlastný podpriečinok s PNG),
    # nech galéria vždy ukáže VŠETKY reklamy, nie len z posledného behu.
    pngs = sorted(outputs_dir.glob("*/*.png"), key=lambda p: p.parent.name.lower())
    for png in pngs:
        rel_path = png.relative_to(outputs_dir)
        folder = png.parent.name
        m = re.match(r"(\d+)\s*-\s*(.*)", folder)
        if m:
            tpl_label = f"#{int(m.group(1)):02d} — {m.group(2).strip()}"
        else:
            tpl_label = folder
        html_parts.append(f"""  <div class="card">
    <img src="{rel_path}" alt="{tpl_label}" loading="lazy">
    <div class="info">
      <h3>{tpl_label}</h3>
    </div>
  </div>
""")
    html_parts[0] = html_parts[0].replace("__COUNT__", str(len(pngs)))

    html_parts.append("</div>\n</body>\n</html>")

    gallery_path = outputs_dir / "gallery.html"
    with open(gallery_path, "w") as f:
        f.write("".join(html_parts))
    print(f"Gallery saved: {gallery_path}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Generate static ads via Nano Banana 2")
    parser.add_argument("--provider", type=str, default=None, choices=["fal", "google", "google-batch", "gpt-image"],
        help="Image generation provider (default: google — Gemini/Nano Banana 2). "
             "fal a gpt-image len na výslovné požiadanie.")
    parser.add_argument("--templates", type=str, default=None,
        help="Comma-separated template numbers to generate (e.g., 1,7,13,15)")
    parser.add_argument("--concepts", type=str, default=None,
        help="Čiarkou oddelené concept_id na (re)generovanie, napr. C08. Ostatné výstupy ostanú nedotknuté.")
    parser.add_argument("--resolution", type=str, default=DEFAULT_RESOLUTION,
        choices=["0.5K", "1K", "2K", "4K"], help="Image resolution (default: 1K). Iba Nano Banana 2 (fal/google).")
    parser.add_argument("--quality", type=str, default=DEFAULT_GPT_IMAGE_QUALITY,
        choices=["low", "medium", "high"],
        help="Kvalita pre gpt-image provider (default: high). low/medium na rýchle iterácie.")
    parser.add_argument("--variations", type=int, default=1,
        help="Number of variations per template (default: 1)")
    parser.add_argument("--dry-run", action="store_true",
        help="Validate and show what would be generated, without API calls or filesystem writes")
    parser.add_argument("--validate-only", action="store_true",
        help="Validate contracts, hashes, approval and inputs; do not call APIs or write files")
    parser.add_argument("--logo-overlay", action="store_true",
        help="Po vygenerovaní vloží reálne logo z brand-dna do obrázka (deterministicky, "
             "namiesto toho, aby ho kreslil AI model). Prompt by mal logo výslovne zakázať.")
    parser.add_argument("--logo-width", type=float, default=0.18,
        help="Šírka loga ako podiel šírky obrázka pri --logo-overlay (default 0.18).")
    parser.add_argument("--logo-keep-clean", action="store_true",
        help="Pred vložením loga odloží kópiu bez loga do outputs/.../_clean/. "
             "Umožní neskôr presunúť logo cez place_logo.py bez nového generovania.")
    parser.add_argument("--logo-margin-y", type=float, default=None,
        help="Zvislý okraj loga ako podiel výšky (default = rovnaký ako vodorovný). "
             "Pri 9:16 pre Reels použi ~0.30, inak logo padne do UI pásu prehrávača.")
    parser.add_argument("--logo-position", type=str, default="bottom-left",
        choices=list(LOGO_POSITIONS), help="Umiestnenie loga pri --logo-overlay.")
    parser.add_argument("--allow-legacy", action="store_true",
        help="Explicitly allow an old ad set without workflow_version 2 and test-plan.json binding")
    parser.add_argument("--brand-dir", type=str, default=".",
        help="Path to the brand folder (default: current directory)")
    parser.add_argument("--prompts-file", type=str, default=None,
        help="Path to prompts JSON file, relative to brand-dir or absolute")
    parser.add_argument("--images-dir", type=str, default=None,
        help="Path to product images folder, relative to brand-dir or absolute")
    parser.add_argument("--output-dir", type=str, default=None,
        help="Path to output folder, relative to brand-dir or absolute")
    parser.add_argument("--lang", type=str, default=None,
        help="Jazyk prompts-{lang}.json, approval a výstupného priečinka "
             "(default: z názvu --prompts-file, inak sk)")
    parser.add_argument("--no-prices", action="store_true",
        help="Zakáž ceny v obrázku pre tento beh — cena v copy fields spadne v pre-flighte. "
             "Default: ceny sú povolené; pri preklade alebo jazyku mimo trhu plánu ich musí potvrdiť approval-{lang}.json.")
    parser.add_argument("--allow-prices", action="store_true",
        help=argparse.SUPPRESS)  # deprecated no-op: ceny sú povolené defaultne (staré príkazy nech nespadnú)
    parser.add_argument("--aspects", type=str, default=None,
        help="Čiarkou oddelené pomery strán pre KAŽDÝ banner (napr. '4:5,9:16'). "
             "Bez tohto sa použije natívny pomer z promptu. 9:16 = verzia pre Reels/Stories.")
    parser.add_argument("--pmax", action="store_true",
        help="Performance Max export zo schválených Meta bannerov: 1.91:1 (1200x628), 1:1 (1200x1200) "
             "a 4:5 (960x1200). Spúšťa sa iba týmto explicitným flagom; nikdy automaticky.")
    parser.add_argument("--exact-size", action="store_true",
        help="Doreže výstupy na presné px rozmery podľa pomeru (cover + center-crop). --pmax to zapína sám.")

    args = parser.parse_args()

    # --prompts-file prompts-hu.json bez --lang: jazyk (approval, ceny, výstup) odvoď z názvu súboru.
    if args.lang is None:
        inferred = lang_from_prompts_name(args.prompts_file) if args.prompts_file else None
        args.lang = inferred or "sk"
    elif args.prompts_file:
        inferred = lang_from_prompts_name(args.prompts_file)
        if inferred and inferred != args.lang.lower():
            parser.error(f"--lang {args.lang} nesedí s {Path(args.prompts_file).name}")

    # Default provider = google (Gemini / Nano Banana 2). fal a gpt-image len na výslovné požiadanie.
    provider = args.provider if args.provider else "google"

    # PMax skratka: zapne sadu pomerov + presný px rozmer (iba na požiadanie cez --pmax).
    aspects = args.aspects
    exact_size = args.exact_size
    if args.pmax:
        aspects = ",".join(PMAX_ASPECTS)
        exact_size = True
        if provider == "google-batch":
            parser.error("--pmax nepodporuje google-batch, pretože batch ignoruje viac pomerov; použi provider google")

    templates_filter = None
    if args.templates:
        templates_filter = [int(t.strip()) for t in args.templates.split(",")]

    # Default outputs do KANONICKÉHO umiestnenia: <ad-set>/outputs (sk) alebo outputs-<lang>.
    # (generate_ads() pri output_dir=None použije brand_dir/outputs — to nájde aj tools/dashboard.)
    output_dir = args.output_dir or default_output_dir(args.lang, pmax=args.pmax)

    return generate_ads(
        provider=provider,
        brand_dir=args.brand_dir,
        prompts_file=args.prompts_file,
        images_dir=args.images_dir,
        output_dir=output_dir,
        templates_filter=templates_filter,
        concepts_filter=[c.strip() for c in args.concepts.split(",") if c.strip()] if args.concepts else None,
        resolution=args.resolution,
        num_variations=args.variations,
        dry_run=args.dry_run,
        block_prices=args.no_prices,
        lang=args.lang,
        aspects=aspects,
        exact_size=exact_size,
        exact_dimensions=PMAX_DIMS if args.pmax else None,
        quality=args.quality,
        validate_only=args.validate_only,
        allow_legacy=args.allow_legacy,
        logo_overlay=args.logo_overlay,
        logo_width=args.logo_width,
        logo_position=args.logo_position,
        logo_margin_y=args.logo_margin_y,
        logo_keep_clean=args.logo_keep_clean,
    )


if __name__ == "__main__":
    sys.exit(main())
