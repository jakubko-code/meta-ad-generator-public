#!/usr/bin/env python3
"""Create deterministic wireframes and optional paid Gemini template previews.

Template previews are visual documentation, not production ads. The default run is
free and writes an SVG wireframe plus preview.json. A paid render requires the
explicit ``--generate-preview`` flag and never bypasses production workflow gates,
because its output is watermarked and stored outside ad-set outputs.
"""

import argparse
import hashlib
import html
import importlib.util
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent
GLOBAL_TEMPLATES = SCRIPT_DIR / "01-templates-by-motion"
PREVIEW_SCHEMA_VERSION = 1
DEFAULT_ACCENT = "#5046e5"


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def relpath(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT.resolve())).replace("\\", "/")
    except ValueError:
        return str(path.resolve()).replace("\\", "/")


def template_scope(path: Path) -> tuple[str, str]:
    """Return (scope, brand): global or brand-specific."""
    resolved = path.resolve()
    try:
        parts = resolved.relative_to(ROOT.resolve() / "brands").parts
        if len(parts) >= 2 and parts[1].endswith("-templates"):
            return "brand", parts[0]
    except ValueError:
        pass
    return "global", ""


def preview_dir_for(template_path: Path) -> Path:
    scope, brand = template_scope(template_path)
    if scope == "brand":
        return ROOT / "brands" / brand / f"{brand}-templates" / "previews" / template_path.stem
    return ROOT / "05-creative-production" / "template-previews" / template_path.stem


def discover_template_paths(root: Path = ROOT, brand: str | None = None) -> list[Path]:
    paths = []
    if brand is None:
        paths.extend(sorted((root / "05-creative-production" / "01-templates-by-motion").glob("[0-9][0-9]-*.md")))
        paths.extend(sorted((root / "brands").glob("*/*-templates/[0-9][0-9]-*.md")))
    else:
        paths.extend(sorted((root / "brands" / brand / f"{brand}-templates").glob("[0-9][0-9]-*.md")))
    return [path for path in paths if path.is_file()]


def first_match(pattern: str, text: str, default: str = "") -> str:
    match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
    return match.group(1).strip() if match else default


def parse_aspect(text: str) -> str:
    metadata = first_match(r"^## Metadata\s*([\s\S]*?)(?=^## |\Z)", text, text)
    value = first_match(r"^\s*-\s*\*\*aspect_ratio:\*\*\s*(.+)$", metadata)
    if not value:
        value = first_match(r"^\s*-\s*aspect_ratio:\s*(.+)$", metadata)
    ratio = re.search(r"(?<!\d)(1\.91:1|\d{1,2}:\d{1,2})(?!\d)", value)
    return ratio.group(1) if ratio else "4:5"


def parse_bool_metadata(text: str, field: str, default: bool = True) -> bool:
    value = first_match(rf"^\s*-\s*\*\*{re.escape(field)}:\*\*\s*(.+)$", text)
    if not value:
        value = first_match(rf"^\s*-\s*{re.escape(field)}:\s*(.+)$", text)
    if not value:
        return default
    return not value.lower().startswith("false")


def parse_title(text: str, fallback: str) -> str:
    return first_match(r"^#\s+(.+)$", text, fallback)


def parse_styles(text: str) -> list[dict]:
    styles = []
    for code, name in re.findall(r"^### Style\s+([A-Z0-9]+)\s*:\s*(.+)$", text, re.MULTILINE):
        styles.append({"code": code, "name": name.strip()})
    return styles or [{"code": "A", "name": "Default"}]


def style_section(text: str, style_code: str) -> str:
    pattern = rf"^### Style\s+{re.escape(style_code)}(?:\s*:\s*.*)?$\s*([\s\S]*?)(?=^### Style\s+|^## |\Z)"
    return first_match(pattern, text, "")


def extract_fenced_block(section: str, heading: str) -> str:
    pattern = rf"^#{{2,4}}\s+{re.escape(heading)}\s*\n```[^\n]*\n([\s\S]*?)^```"
    return first_match(pattern, section, "")


def extract_copy_template(text: str, style_code: str) -> str:
    section = style_section(text, style_code)
    return extract_fenced_block(section, "Copy template") or first_match(
        r"^#{2,4}\s+Copy template\s*\n```[^\n]*\n([\s\S]*?)^```", text, ""
    )


def extract_generation_prompt(text: str, style_code: str) -> str:
    section = style_section(text, style_code)
    return extract_fenced_block(section, "Image generation prompt") or first_match(
        r"^#{2,4}\s+Image generation prompt\s*\n```[^\n]*\n([\s\S]*?)^```", text, ""
    )


def extract_description(text: str) -> str:
    pattern = r"^##\s+(?:What this format is|Čo tento formát je)\s*\n([\s\S]*?)(?=^## |\Z)"
    raw = first_match(pattern, text, "")
    clean = re.sub(r"[`*_>#]", "", raw)
    clean = re.sub(r"\s+", " ", clean).strip()
    return clean[:420]


def extract_slots(copy_template: str, prompt: str) -> list[str]:
    values = []
    sources = [
        re.findall(r"^\s*\[([A-Z][A-Z0-9_. -]{1,40})\]", copy_template, re.MULTILINE),
        re.findall(r"\{\{([\w.]+)\}\}", copy_template + "\n" + prompt),
    ]
    for source in sources:
        for value in source:
            normalized = value.strip().upper().replace("_", " ")
            if normalized not in values:
                values.append(normalized)
    return values[:8] or ["HEADLINE", "SUBHEAD", "CTA"]


def classify_layout(template_path: Path, title: str) -> str:
    haystack = f"{template_path.stem} {title}".lower()
    groups = [
        ("comparison", ("before-after", "before/after", "us-vs", "comparison", "grid")),
        ("testimonial", ("testimonial", "review", "quote", "comment", "social-proof")),
        ("editorial", ("press", "editorial", "advertorial", "news", "notes", "manifesto")),
        ("data", ("stat", "feature", "benefit", "bullet", "checklist", "pointout", "arrow")),
        ("ugc", ("ugc", "lifestyle", "story", "viral")),
    ]
    for layout, needles in groups:
        if any(needle in haystack for needle in needles):
            return layout
    return "hero"


def aspect_dimensions(aspect: str) -> tuple[int, int]:
    mapping = {
        "9:16": (1080, 1920), "4:5": (1080, 1350), "1:1": (1080, 1080),
        "16:9": (1920, 1080), "1.91:1": (1200, 628), "2:3": (1080, 1620),
    }
    return mapping.get(aspect, (1080, 1350))


def brand_accent(brand: str) -> str:
    if not brand:
        return DEFAULT_ACCENT
    brief = ROOT / "brands" / brand / "brand-dna" / "brand-research-brief.json"
    try:
        value = json.loads(brief.read_text(encoding="utf-8")).get("visual_system", {}).get("primary_color_hex", "")
        if re.fullmatch(r"#[0-9A-Fa-f]{6}", value):
            return value
    except (OSError, json.JSONDecodeError, AttributeError):
        pass
    return DEFAULT_ACCENT


def svg_text(value: str) -> str:
    return html.escape(value, quote=True)


def render_wireframe_svg(metadata: dict) -> str:
    width, height = aspect_dimensions(metadata["aspect_ratio"])
    accent = metadata["accent"]
    title = metadata["title"]
    slots = metadata["slots"]
    layout = metadata["layout"]
    pad = int(width * 0.065)
    top = int(height * 0.09)
    bottom = int(height * 0.08)
    content_h = height - top - bottom
    line = max(3, width // 300)

    def rect(x, y, w, h, fill="#ffffff", stroke="#c8cfdb", radius=28, opacity=1.0):
        return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}" stroke="{stroke}" stroke-width="{line}" opacity="{opacity}"/>'

    def label(x, y, text, size=28, fill="#172033", weight=700, anchor="start"):
        return f'<text x="{x}" y="{y}" font-family="Jost,Arial,sans-serif" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}">{svg_text(text)}</text>'

    pieces = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        f'<title id="title">Wireframe: {svg_text(title)}</title>',
        '<desc id="desc">Deterministický štrukturálny náhľad template, nie hotová reklama.</desc>',
        '<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#f7f8fb"/><stop offset="1" stop-color="#e7eaf1"/></linearGradient><pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse"><path d="M32 0H0V32" fill="none" stroke="#dfe4ec" stroke-width="1"/></pattern></defs>',
        f'<rect width="{width}" height="{height}" fill="url(#bg)"/><rect width="{width}" height="{height}" fill="url(#grid)" opacity=".55"/>',
        f'<rect x="{pad}" y="{int(top*.22)}" width="{width-pad*2}" height="{int(top*.44)}" rx="18" fill="{accent}" opacity=".12"/>',
        label(pad + 22, int(top * .52), "TEMPLATE WIREFRAME", max(18, width // 45), accent, 800),
    ]

    if layout == "comparison":
        gap = int(width * .025)
        col_w = (width - pad * 2 - gap) // 2
        pieces += [
            rect(pad, top, col_w, int(content_h * .58), "#ffffff"),
            rect(pad + col_w + gap, top, col_w, int(content_h * .58), "#ffffff"),
            label(pad + col_w // 2, top + int(content_h * .28), "VIZUÁL A", width // 24, "#7c8798", 750, "middle"),
            label(pad + col_w + gap + col_w // 2, top + int(content_h * .28), "VIZUÁL B", width // 24, "#7c8798", 750, "middle"),
        ]
        row_y = top + int(content_h * .62)
    elif layout == "testimonial":
        pieces += [rect(pad, top + int(content_h * .08), width - pad * 2, int(content_h * .62), "#ffffff")]
        pieces += [label(width // 2, top + int(content_h * .24), "★★★★★", width // 16, accent, 800, "middle")]
        pieces += [label(width // 2, top + int(content_h * .39), "„ZÁKAZNÍCKA SKÚSENOSŤ“", width // 27, "#172033", 750, "middle")]
        pieces += [rect(width // 2 - 52, top + int(content_h * .5), 104, 104, accent, accent, 52, .18)]
        row_y = top + int(content_h * .76)
    elif layout == "editorial":
        pieces += [rect(pad, top, width - pad * 2, int(content_h * .78), "#ffffff", "#172033", 8)]
        pieces += [label(width // 2, top + int(content_h * .09), "EDITORIAL / PRESS", width // 29, accent, 800, "middle")]
        pieces += [rect(pad * 2, top + int(content_h * .16), width - pad * 4, int(content_h * .28), "#e3e7ee", "#c8cfdb", 8)]
        pieces += [label(pad * 2, top + int(content_h * .52), "DOMINANTNÝ NADPIS", width // 19, "#172033", 850)]
        row_y = top + int(content_h * .62)
    elif layout == "data":
        pieces += [rect(pad, top + int(content_h * .18), int(width * .46), int(content_h * .48), "#dde2ea")]
        pieces += [label(pad + int(width * .23), top + int(content_h * .43), "PRODUKT", width // 22, "#7c8798", 800, "middle")]
        x = pad + int(width * .51)
        for index in range(3):
            y = top + int(content_h * (.2 + index * .16))
            pieces += [rect(x, y, width - x - pad, int(content_h * .11), "#ffffff", "#c8cfdb", 16)]
            pieces += [label(x + 24, y + int(content_h * .07), f"0{index+1}  BENEFIT / ŠTATISTIKA", width // 39, "#172033", 750)]
        row_y = top + int(content_h * .73)
    elif layout == "ugc":
        pieces += [rect(pad, top, width - pad * 2, int(content_h * .7), "#dce2e8")]
        pieces += [label(width // 2, top + int(content_h * .34), "LIFESTYLE / UGC VIZUÁL", width // 23, "#7c8798", 800, "middle")]
        pieces += [rect(int(width * .13), top + int(content_h * .47), int(width * .74), int(content_h * .16), "#ffffff", "#ffffff", 28, .94)]
        row_y = top + int(content_h * .75)
    else:
        pieces += [rect(pad, top + int(content_h * .22), width - pad * 2, int(content_h * .48), "#dde2ea")]
        pieces += [label(width // 2, top + int(content_h * .47), "PRODUKT / HERO VIZUÁL", width // 22, "#7c8798", 800, "middle")]
        row_y = top + int(content_h * .06)

    visible_slots = slots[:4]
    for index, slot in enumerate(visible_slots):
        y = row_y + index * int(content_h * .075)
        slot_width = int((width - pad * 2) * (1 - index * .08))
        pieces += [rect(pad, y, slot_width, int(content_h * .055), "#ffffff", "#c8cfdb", 14, .96)]
        pieces += [label(pad + 18, y + int(content_h * .036), slot, max(18, width // 42), accent if index == 0 else "#5f6b7d", 800 if index == 0 else 650)]

    pieces += [
        f'<line x1="{pad}" y1="{height-bottom}" x2="{width-pad}" y2="{height-bottom}" stroke="{accent}" stroke-width="{line}" opacity=".35"/>',
        label(pad, height - bottom // 2, f'{metadata["aspect_ratio"]} · {metadata["layout"].upper()} · NIE JE URČENÉ NA PUBLIKOVANIE', max(16, width // 52), "#7c8798", 700),
        "</svg>",
    ]
    return "".join(pieces)


def parse_template(template_path: Path, style_code: str = "A") -> dict:
    text = template_path.read_text(encoding="utf-8")
    scope, brand = template_scope(template_path)
    styles = parse_styles(text)
    valid_codes = {item["code"] for item in styles}
    selected_style = style_code if style_code in valid_codes else styles[0]["code"]
    prompt = extract_generation_prompt(text, selected_style)
    copy_template = extract_copy_template(text, selected_style)
    title = parse_title(text, template_path.stem)
    return {
        "schema_version": PREVIEW_SCHEMA_VERSION,
        "template_path": relpath(template_path),
        "template_sha256": file_sha256(template_path),
        "template_number": int(template_path.name[:2]) if template_path.name[:2].isdigit() else None,
        "slug": template_path.stem,
        "title": title,
        "scope": scope,
        "brand": brand,
        "aspect_ratio": parse_aspect(text),
        "needs_product_images": parse_bool_metadata(text, "needs_product_images", True),
        "styles": styles,
        "selected_style": selected_style,
        "copy_template": copy_template,
        "generation_prompt": prompt,
        "slots": extract_slots(copy_template, prompt),
        "description": extract_description(text),
        "layout": classify_layout(template_path, title),
        "accent": brand_accent(brand),
    }


def load_preview_record(preview_dir: Path) -> dict:
    path = preview_dir / "preview.json"
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def save_preview_record(preview_dir: Path, metadata: dict, existing: dict | None = None) -> Path:
    record = dict(existing or {})
    record.update({key: value for key, value in metadata.items() if key not in ("generation_prompt", "copy_template", "accent")})
    record["schema_version"] = PREVIEW_SCHEMA_VERSION
    path = preview_dir / "preview.json"
    path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def build_wireframe(template_path: Path, style_code: str = "A") -> dict:
    metadata = parse_template(template_path, style_code)
    preview_dir = preview_dir_for(template_path)
    preview_dir.mkdir(parents=True, exist_ok=True)
    wireframe_path = preview_dir / "wireframe.svg"
    wireframe_path.write_text(render_wireframe_svg(metadata), encoding="utf-8")
    existing = load_preview_record(preview_dir)
    existing["wireframe"] = {
        "file": relpath(wireframe_path),
        "template_sha256": metadata["template_sha256"],
        "generated_at": utc_now(),
        "generator": "deterministic-svg-v1",
    }
    record_path = save_preview_record(preview_dir, metadata, existing)
    print(f"✓ Wireframe: {wireframe_path}")
    return {"metadata": metadata, "preview_dir": preview_dir, "record_path": record_path}


def specimen_value(slot: str) -> str:
    key = slot.lower().split(".")[-1]
    mapping = {
        "headline": "HLAVNÝ BENEFIT", "subhead": "Krátke vysvetlenie produktu",
        "body": "Ukážkový podporný text", "cta": "ZISTIŤ VIAC", "badge": "NOVINKA",
        "badge_label": "NOVINKA", "badge_sub": "Ukážkový benefit", "usage_line": "Vytvorené pre váš každodenný komfort",
        "review_text": "Ukážková zákaznícka skúsenosť", "reviewer": "ZÁKAZNÍK",
        "rating": "5.0", "stat": "95 %", "price": "CENA", "offer": "UKÁŽKOVÁ PONUKA",
    }
    return mapping.get(key, key.replace("_", " ").upper()[:32])


def fill_preview_prompt(metadata: dict, brand: str, product_name: str) -> str:
    prompt = metadata["generation_prompt"]
    if not prompt:
        raise ValueError("Template neobsahuje blok 'Image generation prompt'.")
    prompt = re.sub(r"\{\{([\w.]+)\}\}", lambda match: specimen_value(match.group(1)), prompt)
    replacements = {
        "BRAND NAME": brand, "PRODUCT NAME": product_name,
        "ASPECT RATIO": metadata["aspect_ratio"], "TOP SAFE ZONE": "safe top area",
        "BOTTOM SAFE ZONE": "safe bottom area",
    }
    for key, value in replacements.items():
        prompt = re.sub(rf"\[{key}[^\]]*\]", value, prompt, flags=re.IGNORECASE)
    prompt = re.sub(r"\[[^\]]+\]", "the default option described by this template", prompt)
    return (
        "TEMPLATE SPECIMEN RENDER. This is visual documentation, not a live advertisement. "
        "Follow the template structure as faithfully as possible. Use only the neutral specimen "
        "copy supplied below; never invent prices, claims, discounts, testimonials or product facts. "
        "Do not render the words TEMPLATE PREVIEW; a watermark is added after generation.\n\n" + prompt
    )


def import_generator_module():
    path = ROOT / "07-image-generation" / "generate_ads.py"
    spec = importlib.util.spec_from_file_location("shared_generate_ads", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def add_preview_watermark(path: Path) -> None:
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError as exc:
        raise RuntimeError("Pillow je potrebný na bezpečnostný watermark.") from exc
    image = Image.open(path).convert("RGBA")
    draw = ImageDraw.Draw(image, "RGBA")
    height = max(54, image.height // 20)
    draw.rectangle((0, image.height - height, image.width, image.height), fill=(13, 18, 30, 220))
    try:
        font = ImageFont.load_default(size=max(18, image.width // 42))
    except TypeError:  # Pillow < 10.1
        font = ImageFont.load_default()
    text = "TEMPLATE PREVIEW  •  NOT FOR PUBLISHING"
    box = draw.textbbox((0, 0), text, font=font)
    x = (image.width - (box[2] - box[0])) // 2
    y = image.height - height + (height - (box[3] - box[1])) // 2
    draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)
    image.convert("RGB").save(path, "PNG")


def generate_paid_preview(result: dict, brand: str, product_image: Path | None, resolution: str) -> Path:
    metadata = result["metadata"]
    if not brand:
        raise ValueError("Platený preview vyžaduje --brand kvôli brand cards.")
    brand_dir = ROOT / "brands" / brand
    cards = [brand_dir / "brand-dna" / "brand-spec-card.png", brand_dir / "brand-dna" / "visual-style-card.png"]
    missing_cards = [str(path) for path in cards if not path.is_file()]
    if missing_cards:
        raise ValueError("Chýbajú brand cards: " + ", ".join(missing_cards))
    if metadata["needs_product_images"] and (not product_image or not product_image.is_file()):
        raise ValueError("Template vyžaduje produktový obrázok; zadaj --product-image.")

    generator = import_generator_module()
    if not generator.GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY nie je nastavený.")
    references = cards + ([product_image] if product_image else [])
    image_parts = [generator.load_image_part_google(str(path)) for path in references]
    product_name = product_image.stem.replace("-", " ") if product_image else "referenčný produkt"
    prompt = fill_preview_prompt(metadata, brand, product_name)
    image_bytes = generator.run_generation_google(prompt, image_parts, metadata["aspect_ratio"], resolution)
    output_path = result["preview_dir"] / "rendered-preview.png"
    output_path.write_bytes(image_bytes)
    add_preview_watermark(output_path)

    record = load_preview_record(result["preview_dir"])
    record["rendered_preview"] = {
        "file": relpath(output_path), "template_sha256": metadata["template_sha256"],
        "generated_at": utc_now(), "provider": "google", "model": generator.GEMINI_MODEL_ID,
        "resolution": resolution, "style": metadata["selected_style"],
        "product_image": relpath(product_image) if product_image else None,
    }
    save_preview_record(result["preview_dir"], metadata, record)
    print(f"✓ Platený Gemini preview: {output_path}")
    return output_path


def discover_templates(root: Path = ROOT) -> list[dict]:
    """Return dashboard-ready records and preview freshness for every template."""
    records = []
    original_root = globals()["ROOT"]
    if root != original_root:
        globals()["ROOT"] = root
    try:
        for path in discover_template_paths(root):
            metadata = parse_template(path)
            preview_dir = preview_dir_for(path)
            record = load_preview_record(preview_dir)
            wireframe = record.get("wireframe") or {}
            rendered = record.get("rendered_preview") or {}
            wireframe_path = root / str(wireframe.get("file", "")) if wireframe.get("file") else None
            rendered_path = root / str(rendered.get("file", "")) if rendered.get("file") else None
            wireframe_exists = bool(wireframe_path and wireframe_path.is_file())
            wireframe_current = bool(wireframe_exists and wireframe.get("template_sha256") == metadata["template_sha256"])
            rendered_exists = bool(rendered_path and rendered_path.is_file())
            rendered_current = bool(rendered_exists and rendered.get("template_sha256") == metadata["template_sha256"])
            metadata.update({
                "wireframe_file": wireframe.get("file", ""), "wireframe_exists": wireframe_exists,
                "wireframe_current": wireframe_current,
                "rendered_file": rendered.get("file", ""), "rendered_exists": rendered_exists,
                "rendered_current": rendered_current, "rendered_generated_at": rendered.get("generated_at", ""),
                "preview_status": "rendered" if rendered_current else "stale" if rendered_exists or (wireframe_exists and not wireframe_current) else "wireframe" if wireframe_current else "missing",
            })
            metadata.pop("generation_prompt", None)
            metadata.pop("copy_template", None)
            records.append(metadata)
    finally:
        globals()["ROOT"] = original_root
    return records


def main() -> int:
    parser = argparse.ArgumentParser(description="Build template wireframes and optional Gemini previews")
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--template", type=Path, help="One template .md file")
    target.add_argument("--all", action="store_true", help="All global and brand-specific templates")
    parser.add_argument("--brand", help="Limit --all to one brand, or brand context for a paid preview")
    parser.add_argument("--style", default="A", help="Template style code (default: A)")
    parser.add_argument("--generate-preview", action="store_true", help="EXPLICIT paid Gemini render; default only builds free wireframes")
    parser.add_argument("--product-image", type=Path, help="Authoritative product reference for a paid preview")
    parser.add_argument("--resolution", choices=["0.5K", "1K", "2K", "4K"], default="1K")
    parser.add_argument("--missing-only", action="store_true", help="Skip current wireframes; useful for catalogs")
    args = parser.parse_args()

    paths = discover_template_paths(ROOT, args.brand) if args.all else [args.template.resolve()]
    if not paths:
        print("Nenašli sa žiadne template súbory.")
        return 1
    if args.generate_preview and len(paths) != 1:
        print("✗ Platený preview spúšťaj po jednom template, nie cez --all.")
        return 1

    for path in paths:
        if not path.is_file():
            print(f"✗ Template neexistuje: {path}")
            return 1
        preview_dir = preview_dir_for(path)
        current_hash = file_sha256(path)
        existing = load_preview_record(preview_dir)
        wireframe = existing.get("wireframe") or {}
        if args.missing_only and wireframe.get("template_sha256") == current_hash and (preview_dir / "wireframe.svg").is_file():
            continue
        try:
            result = build_wireframe(path, args.style)
            if args.generate_preview:
                product_image = args.product_image.resolve() if args.product_image else None
                generate_paid_preview(result, args.brand or result["metadata"]["brand"], product_image, args.resolution)
        except (OSError, ValueError, RuntimeError) as exc:
            print(f"✗ {path}: {exc}")
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
