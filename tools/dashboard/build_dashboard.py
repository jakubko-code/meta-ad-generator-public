#!/usr/bin/env python3
"""Build an offline multi-brand Creative QA dashboard.

The dashboard discovers generated image manifests under ``brands/*`` and embeds
its CSS and JavaScript so the resulting ``dashboard.html`` works as one local file.
It is a review helper, never a workflow gate or campaign-management interface.
"""

import argparse
import hashlib
import html as html_lib
import importlib.util
import json
import re
from datetime import datetime
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parents[1]
DEFAULT_PRIMARY = "#4f46e5"


def discover_template_library() -> list[dict]:
    """Load the shared preview catalog without duplicating its parsing rules."""
    module_path = ROOT / "05-creative-production" / "template_preview.py"
    if not module_path.is_file():
        return []
    spec = importlib.util.spec_from_file_location("template_preview", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.discover_templates(ROOT)


def safe_color(value: str) -> str:
    return value if isinstance(value, str) and re.fullmatch(r"#[0-9a-fA-F]{6}", value) else DEFAULT_PRIMARY


def load_brand_colors(brand_dir: Path) -> dict:
    brief_path = brand_dir / "brand-dna" / "brand-research-brief.json"
    primary = DEFAULT_PRIMARY
    if brief_path.exists():
        try:
            brief = json.loads(brief_path.read_text(encoding="utf-8"))
            primary = brief.get("visual_system", {}).get("primary_color_hex", primary)
        except (OSError, json.JSONDecodeError, AttributeError):
            pass
    return {"primary": safe_color(primary)}


def discover_all_brands() -> list[dict]:
    """Return all valid output manifests with their prompt and brand context."""
    items = []
    brands_dir = ROOT / "brands"
    if not brands_dir.exists():
        return items

    pattern = "*/products/*/product-image-ads/*/outputs*/manifest.json"
    for manifest_path in sorted(brands_dir.glob(pattern)):
        outputs_dir = manifest_path.parent
        ad_set_dir = outputs_dir.parent
        product_dir = ad_set_dir.parent.parent
        brand_dir = product_dir.parent.parent
        core = outputs_dir.name[len("outputs"):].lstrip("-").lower()
        lang = core.replace("9x16", "").strip("-") or "sk"

        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue

        prompts_path = ad_set_dir / f"prompts-{lang}.json"
        if not prompts_path.exists():
            prompts_path = ad_set_dir / "prompts-sk.json"
        prompts_data = {}
        if prompts_path.exists():
            try:
                prompts_data = json.loads(prompts_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                pass

        items.append({
            "brand": brand_dir.name,
            "brand_dir": brand_dir,
            "product": product_dir.name,
            "adset": ad_set_dir.name,
            "outputs": outputs_dir.name,
            "lang": lang,
            "ad_set_dir": ad_set_dir,
            "manifest": manifest,
            "prompts": prompts_data,
            "colors": load_brand_colors(brand_dir),
        })
    return items


def relpath_from_root(file_str: str) -> str:
    """Return a browser-friendly file path relative to repository root."""
    path = Path(file_str)
    if path.is_absolute():
        try:
            return str(path.relative_to(ROOT)).replace("\\", "/")
        except ValueError:
            # Manifest zo starej polohy repozitára (napr. ~/Desktop/...): prepoj od "brands/".
            if "brands" in path.parts:
                return "/".join(path.parts[path.parts.index("brands"):])
            return str(path).replace("\\", "/")
    return str(path).replace("\\", "/")


def banner_id(brand: str, product: str, adset: str, lang: str, tpl_num, variation: str, ad_id: str = "") -> str:
    var_clean = str(variation).replace("_", "-")
    ad_clean = re.sub(r"[^A-Za-z0-9]+", "-", str(ad_id)).strip("-").lower()
    return f"{brand}__{product}__{adset}__{lang}__t{tpl_num}__{var_clean}__{ad_clean}"


def find_prompt_def(prompts: list, result: dict) -> dict:
    """Match a rendered result to its workflow-v2 prompt using concept identity."""
    template_name = result.get("name", "")
    concept_id = result.get("concept_id")
    if concept_id:
        for prompt in prompts:
            brief = prompt.get("brief") or {}
            if prompt.get("template_name", "") == template_name and brief.get("concept_id") == concept_id:
                return prompt
    return next((prompt for prompt in prompts if prompt.get("template_name", "") == template_name), {})


def humanize_slug(value: str) -> str:
    clean = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", value or "")
    return clean.replace("-", " ").strip().capitalize() or "Bez názvu"


def banner_count_label(count: int) -> str:
    if count == 1:
        return "1 banner"
    if 2 <= count <= 4:
        return f"{count} bannery"
    return f"{count} bannerov"


def build_template_card(template: dict) -> str:
    status_labels = {
        "rendered": "Gemini preview", "wireframe": "Wireframe",
        "stale": "Neaktuálny render", "missing": "Chýba náhľad",
    }
    status = template.get("preview_status", "missing")
    image_file = template.get("rendered_file") if template.get("rendered_current") else template.get("wireframe_file")
    image_path = ROOT / str(image_file or "")
    image_exists = bool(image_file and image_path.is_file())
    image_url = f"{image_file}?v={int(image_path.stat().st_mtime)}" if image_exists else ""
    scope = template.get("scope", "global")
    brand = template.get("brand") or "Globálna"
    template_path = template.get("template_path", "")
    command = f"python3 05-creative-production/template_preview.py --template {template_path}"
    if scope == "brand":
        command += f" --brand {template.get('brand', '')}"
    paid_command = command + " --generate-preview" + (" --product-image PATH_K_PRODUKTU" if template.get("needs_product_images") else "")
    styles = ", ".join(f"{item['code']}: {item['name']}" for item in template.get("styles", []))
    slots = " · ".join(template.get("slots", []))
    preview = (
        f'<img src="{html_lib.escape(image_url, quote=True)}" alt="Náhľad šablóny {html_lib.escape(template.get("title", ""), quote=True)}" loading="lazy">'
        if image_exists else '<div class="template-placeholder" aria-hidden="true">NÁHĽAD<br>CHÝBA</div>'
    )
    attrs = {
        "template-path": template_path, "title": template.get("title", ""),
        "scope": scope, "brand": template.get("brand", ""), "status": status,
        "aspect": template.get("aspect_ratio", ""), "layout": template.get("layout", ""),
        "description": template.get("description", ""), "styles": styles, "slots": slots,
        "image": image_url, "wireframe": template.get("wireframe_file", ""),
        "rendered": template.get("rendered_file", ""),
        "wireframe-current": str(bool(template.get("wireframe_current"))).lower(),
        "rendered-current": str(bool(template.get("rendered_current"))).lower(),
        "command": command, "paid-command": paid_command,
    }
    data_attrs = " ".join(f'data-{key}="{html_lib.escape(str(value), quote=True)}"' for key, value in attrs.items())
    product_badge = '<span class="chip">produktový ref.</span>' if template.get("needs_product_images") else '<span class="chip">bez produktu</span>'
    return f"""
      <article class="template-card" {data_attrs}>
        <button class="template-preview" type="button" aria-label="Otvoriť detail šablóny">
          {preview}<span class="template-scope">{html_lib.escape(brand)}</span>
          <span class="preview-status status-{html_lib.escape(status)}">{status_labels.get(status, status)}</span>
        </button>
        <div class="template-info">
          <p class="template-kicker">{html_lib.escape(template.get('layout', '').upper())} · {html_lib.escape(template.get('aspect_ratio', ''))}</p>
          <h3>{html_lib.escape(template.get('title', 'Bez názvu'))}</h3>
          <p>{html_lib.escape(template.get('description') or 'Štrukturálny náhľad rozloženia a copy slotov.')}</p>
          <div class="chips"><span class="chip">{len(template.get('styles', []))} štýl/y</span>{product_badge}</div>
        </div>
      </article>"""


def build_card(result: dict, ad_set: dict) -> str:
    prompts = ad_set["prompts"].get("prompts", [])
    prompt_def = find_prompt_def(prompts, result)
    brief = prompt_def.get("brief") or {}
    aspect = str(result.get("aspect") or ad_set["prompts"].get("_meta", {}).get("aspect_ratio_default", "") or "—")
    template_name = str(result.get("name", ""))
    template_number = result.get("template", 0)
    variation = str(result.get("variation", ""))
    concept_id = str(result.get("concept_id") or brief.get("concept_id") or "")
    ad_id = str(prompt_def.get("ad_id") or concept_id or template_name or "Banner")
    headline = str(prompt_def.get("headline") or "").replace("\n", " / ").strip()
    plan_id = str(ad_set["prompts"].get("test_plan", {}).get("id") or "")

    relative_file = relpath_from_root(result.get("file", ""))
    absolute_file = ROOT / relative_file
    exists = absolute_file.is_file()
    size_kb = absolute_file.stat().st_size / 1024 if exists else 0
    # QA verdikt sa viaže na presné bajty PNG; nový render pod rovnakou cestou ho nezdedí.
    file_hash = hashlib.sha256(absolute_file.read_bytes()).hexdigest() if exists else ""
    mtime = int(absolute_file.stat().st_mtime) if exists else 0
    image_url = f"{relative_file}?v={mtime}"
    variant_label = variation.split("_")[0] if variation else "v?"
    language = ad_set.get("lang", "sk").upper()
    primary = safe_color(ad_set["colors"].get("primary"))
    bid = banner_id(
        ad_set["brand"], ad_set["product"], ad_set["adset"],
        ad_set.get("lang", "sk"), template_number, variation, ad_id,
    )
    missing_class = " missing" if not exists else ""
    missing_overlay = '<span class="missing-file">Súbor chýba</span>' if not exists else ""
    headline_html = html_lib.escape(headline) if headline else '<span class="muted-copy">Headline nie je v prompte</span>'
    concept_badge = f'<span class="chip concept">{html_lib.escape(concept_id)}</span>' if concept_id else ""

    attrs = {
        "banner-id": bid,
        "brand": ad_set["brand"],
        "country": language,
        "product": ad_set["product"],
        "adset": ad_set["adset"],
        "outputs": ad_set["outputs"],
        "variant": ad_id,
        "file": relative_file,
        "image-url": image_url,
        "headline": headline,
        "ad-id": ad_id,
        "template-name": template_name,
        "template-num": template_number,
        "variation": variation,
        "aspect": aspect,
        "concept-id": concept_id,
        "plan-id": plan_id,
        "exists": "true" if exists else "false",
        "sha256": file_hash,
    }
    data_attrs = " ".join(
        f'data-{key}="{html_lib.escape(str(value), quote=True)}"' for key, value in attrs.items()
    )
    image_alt = f"{ad_set['brand']} – {ad_id}, template {template_number}, variant {variant_label}"

    return f"""
      <article class="card{missing_class}" {data_attrs} style="--brand-color:{primary}">
        <div class="card-preview">
          <button class="select-btn" type="button" aria-label="Vybrať banner" aria-pressed="false"><span aria-hidden="true">✓</span></button>
          <span class="brand-tag">{html_lib.escape(ad_set['brand'])}</span>
          <span class="country-tag">{html_lib.escape(language)}</span>
          <a href="{html_lib.escape(image_url, quote=True)}" class="card-img-link" aria-label="Otvoriť detail banneru">
            <img src="{html_lib.escape(image_url, quote=True)}" alt="{html_lib.escape(image_alt, quote=True)}" loading="lazy">
          </a>
          {missing_overlay}
        </div>
        <div class="card-info">
          <div class="card-title-row">
            <h3>{html_lib.escape(ad_id)}</h3>
            <button class="qa-badge qa-unreviewed" type="button" aria-label="Otvoriť QA hodnotenie">Nehodnotené</button>
          </div>
          <p class="headline">{headline_html}</p>
          <div class="chips">
            {concept_badge}
            <span class="chip">T{int(template_number):02d}</span>
            <span class="chip">{html_lib.escape(aspect)}</span>
            <span class="chip">{html_lib.escape(variant_label)}</span>
            <span class="chip">{size_kb:.0f} KB</span>
          </div>
        </div>
      </article>"""


def build_html(items: list[dict], existing_flagged: dict, templates: list[dict] | None = None) -> str:
    templates = templates if templates is not None else discover_template_library()
    brands = sorted({item["brand"] for item in items})
    products = sorted({item["product"] for item in items})
    adsets = sorted({item["adset"] for item in items})
    outputs = sorted({item["outputs"] for item in items})
    languages = sorted({item.get("lang", "sk").upper() for item in items})
    total_banners = sum(len(item["manifest"].get("results", [])) for item in items)
    total_failed = sum(int(item["manifest"].get("total_failed", 0) or 0) for item in items)
    template_brands = sorted({item.get("brand", "") for item in templates if item.get("brand")})

    per_brand_counts = {
        brand: sum(len(item["manifest"].get("results", [])) for item in items if item["brand"] == brand)
        for brand in brands
    }
    option = lambda value, label=None: f'<option value="{html_lib.escape(value, quote=True)}">{html_lib.escape(label or value)}</option>'
    brand_options = "".join(option(brand, f"{brand} ({per_brand_counts[brand]})") for brand in brands)
    product_options = "".join(option(product) for product in products)
    adset_options = "".join(option(adset, humanize_slug(adset)) for adset in adsets)
    output_options = "".join(option(output) for output in outputs)
    language_options = "".join(option(language) for language in languages)
    template_brand_options = "".join(option(brand) for brand in template_brands)

    sections = []
    for item in items:
        cards = []
        section_mtime = 0
        for result in item["manifest"].get("results", []):
            cards.append(build_card(result, item))
            absolute_file = ROOT / relpath_from_root(result.get("file", ""))
            if absolute_file.is_file():
                section_mtime = max(section_mtime, int(absolute_file.stat().st_mtime))
        if not cards:
            continue

        count = len(cards)
        updated = datetime.fromtimestamp(section_mtime).strftime("%d. %m. %Y · %H:%M") if section_mtime else "bez dostupného súboru"
        raw_attrs = {
            "brand": item["brand"], "product": item["product"], "adset": item["adset"],
            "outputs": item["outputs"], "country": item.get("lang", "sk").upper(), "mtime": section_mtime,
        }
        attrs = " ".join(f'data-{key}="{html_lib.escape(str(value), quote=True)}"' for key, value in raw_attrs.items())
        sections.append((section_mtime, f"""
        <section class="adset-section" {attrs}>
          <header class="section-header">
            <div class="section-identity">
              <span class="section-brand">{html_lib.escape(item['brand'])}</span>
              <div>
                <h2>{html_lib.escape(humanize_slug(item['adset']))}</h2>
                <p>{html_lib.escape(item['product'])} · {html_lib.escape(item.get('lang', 'sk').upper())} · <span class="outputs-label">{html_lib.escape(item['outputs'])}</span></p>
              </div>
            </div>
            <div class="section-summary">
              <span>{updated}</span>
              <span class="section-count">{banner_count_label(count)}</span>
              <button class="collapse-btn" type="button" aria-expanded="true" aria-label="Zbaliť ad set"><span aria-hidden="true">⌃</span></button>
            </div>
          </header>
          <div class="cards-grid">{"".join(cards)}</div>
        </section>"""))
    sections.sort(key=lambda pair: pair[0], reverse=True)

    if sections:
        content = "".join(section for _, section in sections)
    else:
        content = """
        <div class="empty-state permanent-empty">
          <div class="empty-icon" aria-hidden="true">▧</div>
          <h2>Zatiaľ tu nie sú žiadne bannery</h2>
          <p>Po kroku 7 spusti <code>python3 tools/dashboard/build_dashboard.py</code>.</p>
        </div>"""

    template_cards = "".join(build_template_card(template) for template in templates)
    if not template_cards:
        template_cards = '<div class="empty-state permanent-empty"><div class="empty-icon">▧</div><h2>Zatiaľ tu nie sú žiadne šablóny</h2><p>Vytvor prvý wireframe cez <code>template_preview.py</code>.</p></div>'

    config = json.dumps({"seed": existing_flagged}, ensure_ascii=False).replace("</", "<\\/")
    css = (SCRIPT_DIR / "dashboard.css").read_text(encoding="utf-8")
    javascript = (SCRIPT_DIR / "dashboard.js").read_text(encoding="utf-8")
    timestamp = datetime.now().strftime("%d. %m. %Y · %H:%M")

    return f"""<!DOCTYPE html>
<html lang="sk">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="color-scheme" content="light">
  <title>Creative QA · Meta Ad Generator</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Google+Sans:ital,opsz,wght@0,17..18,400..700;1,17..18,400..700&family=Jost:ital,wght@0,100..900;1,100..900&display=swap" rel="stylesheet">
  <style>{css}</style>
</head>
<body>
  <div class="app-shell">
    <header class="app-header">
      <div class="topline">
        <div>
          <p class="eyebrow">Meta Ad Generator</p>
          <h1>Creative Workspace</h1>
          <p class="subtitle">Aktualizované {timestamp}</p>
        </div>
        <div class="stats" aria-label="Súhrn dashboardu">
          <div><strong>{total_banners}</strong><span>bannerov</span></div>
          <div><strong>{len(items)}</strong><span>ad setov</span></div>
          <div><strong>{len(brands)}</strong><span>brandov</span></div>
          <div class="stat-failed"><strong>{total_failed}</strong><span>zlyhaní</span></div>
        </div>
      </div>

      <nav class="view-tabs" aria-label="Časti dashboardu">
        <button class="view-tab active" type="button" data-view="creative" aria-selected="true">Creative QA <span>{total_banners}</span></button>
        <button class="view-tab" type="button" data-view="templates" aria-selected="false">Template knižnica <span>{len(templates)}</span></button>
      </nav>

      <div class="creative-controls">
      <div class="search-row">
        <label class="search-box" for="filter-search"><span aria-hidden="true">⌕</span><input type="search" id="filter-search" placeholder="Hľadať headline, koncept, template alebo produkt…"></label>
        <button id="btn-toggle-filters" class="secondary mobile-filter-toggle" type="button" aria-expanded="false" aria-controls="filters-panel">Filtre</button>
        <button id="btn-export-qa" class="secondary" type="button">Export QA</button>
      </div>

      <div class="filters-panel" id="filters-panel">
        <label>Brand<select id="filter-brand"><option value="">Všetky brandy</option>{brand_options}</select></label>
        <label>Produkt<select id="filter-product"><option value="">Všetky produkty</option>{product_options}</select></label>
        <label>Ad set<select id="filter-adset"><option value="">Všetky ad sety</option>{adset_options}</select></label>
        <label>Jazyk<select id="filter-country"><option value="">Všetky jazyky</option>{language_options}</select></label>
        <label>Výstup<select id="filter-outputs"><option value="">Všetky výstupy</option>{output_options}</select></label>
        <label>QA stav<select id="filter-qa"><option value="">Všetky stavy</option><option value="unreviewed">Nehodnotené</option><option value="pass">PASS</option><option value="minor">Drobná oprava</option><option value="fail">FAIL</option><option value="stale">Prehodnotiť</option></select></label>
        <label>Zoradenie<select id="filter-sort"><option value="newest">Najnovšie</option><option value="oldest">Najstaršie</option><option value="name">Názov A–Z</option></select></label>
        <button id="btn-reset-filters" class="text-button" type="button">Vymazať filtre</button>
      </div>

      <div class="results-row" aria-live="polite"><strong id="visible-count">{total_banners}</strong><span> z {banner_count_label(total_banners)}</span><span id="active-filter-summary"></span></div>
      </div>

      <div class="template-controls" hidden>
        <div class="search-row">
          <label class="search-box" for="template-search"><span aria-hidden="true">⌕</span><input type="search" id="template-search" placeholder="Hľadať template, layout, copy slot alebo brand…"></label>
        </div>
        <div class="filters-panel template-filter-panel">
          <label>Zdroj<select id="template-scope"><option value="">Všetky</option><option value="global">Globálne</option><option value="brand">Klientske</option></select></label>
          <label>Brand<select id="template-brand"><option value="">Všetky brandy</option>{template_brand_options}</select></label>
          <label>Náhľad<select id="template-status"><option value="">Všetky stavy</option><option value="rendered">Gemini preview</option><option value="wireframe">Wireframe</option><option value="stale">Neaktuálny</option><option value="missing">Chýba</option></select></label>
          <button id="btn-reset-template-filters" class="text-button" type="button">Vymazať filtre</button>
        </div>
        <div class="results-row" aria-live="polite"><strong id="visible-template-count">{len(templates)}</strong><span> z {len(templates)} šablón</span></div>
      </div>
    </header>

    <main id="dashboard-content"><div id="creative-view">{content}
      <div class="empty-state filter-empty" id="filter-empty" hidden>
        <div class="empty-icon" aria-hidden="true">⌕</div><h2>Nič sme nenašli</h2><p>Skús upraviť alebo vymazať aktívne filtre.</p>
      </div>
      </div>
      <section id="templates-view" hidden>
        <div class="template-intro"><div><p class="eyebrow">Visual reference</p><h2>Template knižnica</h2><p>Wireframe ukazuje kompozíciu a copy sloty. Gemini preview je približný specimen, nie hotová reklama.</p></div><code>python3 05-creative-production/template_preview.py --all --missing-only</code></div>
        <div class="template-grid">{template_cards}</div>
        <div class="empty-state filter-empty" id="template-filter-empty" hidden><div class="empty-icon">⌕</div><h2>Nič sme nenašli</h2><p>Skús upraviť filtre template knižnice.</p></div>
      </section>
    </main>
  </div>

  <div class="selection-bar" id="selection-bar" hidden aria-live="polite">
    <strong><span id="selected-count">0</span> vybrané</strong>
    <button id="btn-compare" class="primary" type="button">Porovnať</button>
    <button id="btn-download" type="button">Stiahnuť</button>
    <button id="btn-pdf" type="button">PDF</button>
    <button id="btn-clear-selection" class="text-button" type="button">Zrušiť výber</button>
  </div>

  <div class="overlay lightbox" id="lightbox" role="dialog" aria-modal="true" aria-labelledby="lb-title" hidden>
    <button class="overlay-close" id="lb-close" type="button" aria-label="Zavrieť detail">×</button>
    <button class="nav-btn prev" id="lb-prev" type="button" aria-label="Predošlý banner">‹</button>
    <div class="lightbox-stage"><img id="lb-img" src="" alt=""></div>
    <aside class="review-panel">
      <p class="eyebrow" id="lb-context"></p><h2 id="lb-title">Banner</h2><p class="lb-headline" id="lb-headline"></p>
      <dl class="detail-list" id="lb-details"></dl>
      <fieldset class="qa-controls"><legend>Vizuálny QA verdikt</legend>
        <button type="button" data-qa="pass">PASS</button><button type="button" data-qa="minor">Drobná oprava</button><button type="button" data-qa="fail">FAIL</button><button type="button" data-qa="unreviewed">Nehodnotené</button>
      </fieldset>
      <label class="note-label" for="lb-note">Poznámka k úprave<textarea id="lb-note" rows="5" placeholder="Čo presne treba opraviť?"></textarea></label>
      <button id="lb-select" class="secondary full-width" type="button" aria-pressed="false">Pridať do výberu</button>
    </aside>
    <button class="nav-btn next" id="lb-next" type="button" aria-label="Nasledujúci banner">›</button>
  </div>

  <div class="overlay compare-overlay" id="compare-overlay" role="dialog" aria-modal="true" aria-labelledby="compare-title" hidden>
    <div class="compare-header"><div><p class="eyebrow">Side-by-side</p><h2 id="compare-title">Porovnanie kreatív</h2></div><button class="overlay-close" id="compare-close" type="button" aria-label="Zavrieť porovnanie">×</button></div>
    <div class="compare-grid" id="compare-grid"></div>
  </div>

  <div class="overlay template-overlay" id="template-overlay" role="dialog" aria-modal="true" aria-labelledby="template-detail-title" hidden>
    <button class="overlay-close" id="template-close" type="button" aria-label="Zavrieť detail">×</button>
    <div class="template-detail-visual"><img id="template-detail-image" src="" alt=""></div>
    <aside class="review-panel template-detail-panel">
      <p class="eyebrow" id="template-detail-context"></p><h2 id="template-detail-title">Template</h2><p id="template-detail-description"></p>
      <dl class="detail-list" id="template-detail-list"></dl>
      <label class="command-label">Bezplatný wireframe<textarea id="template-command" rows="3" readonly></textarea></label>
      <button class="secondary full-width copy-template-command" type="button" data-copy-target="template-command">Kopírovať príkaz</button>
      <label class="command-label paid-label">Platený Gemini specimen<textarea id="template-paid-command" rows="4" readonly></textarea></label>
      <p class="command-note">Príkaz s <code>--generate-preview</code> je jediný režim, ktorý volá platené API.</p>
      <button class="secondary full-width copy-template-command" type="button" data-copy-target="template-paid-command">Kopírovať platený príkaz</button>
    </aside>
  </div>

  <div id="print-area"></div><div class="toast" id="toast" role="status" aria-live="polite"></div>
  <script type="application/json" id="dashboard-config">{config}</script>
  <script>{javascript}</script>
</body>
</html>"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the offline Creative QA dashboard")
    parser.add_argument("--output", "-o", default=str(ROOT / "dashboard.html"))
    parser.add_argument("--flagged-seed", default=str(ROOT / "flagged.json"))
    args = parser.parse_args()

    seed = {}
    seed_path = Path(args.flagged_seed)
    if seed_path.exists():
        try:
            raw = json.loads(seed_path.read_text(encoding="utf-8"))
            if isinstance(raw, dict) and isinstance(raw.get("items"), list):
                seed = {item["id"]: {key: value for key, value in item.items() if key != "id"} for item in raw["items"] if item.get("id")}
            elif isinstance(raw, dict):
                seed = raw
        except (OSError, json.JSONDecodeError) as exc:
            print(f"⚠ Nemôžem čítať {seed_path}: {exc}")

    items = discover_all_brands()
    templates = discover_template_library()
    output_path = Path(args.output)
    output_path.write_text(build_html(items, seed, templates), encoding="utf-8")
    total = sum(len(item["manifest"].get("results", [])) for item in items)
    brands = sorted({item["brand"] for item in items})
    print(f"✓ Dashboard saved: {output_path}")
    print(f"  Brandy: {len(brands)} ({', '.join(brands)})")
    print(f"  Ad sety: {len(items)}")
    print(f"  Bannery: {total}")
    print(f"  Templates: {len(templates)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
