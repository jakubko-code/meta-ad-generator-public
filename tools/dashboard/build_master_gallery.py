#!/usr/bin/env python3
"""
Master Gallery Builder — všeobecný skript pre každý brand v ad-generatore.

Auto-discoveruje všetky ad-sets a jazyky cez glob:
    brands/{brand}/products/*/product-image-ads/*/outputs*/manifest.json

Pre každú nájdenú ad-set vyrenderuje karty s odkazmi na obrázky a metadáta z
prompts-sk.json (headline preview, ad_id, aspect ratio, template number).

Výstup: brands/{brand}/master-gallery.html

Použitie:
    python3 tools/dashboard/build_master_gallery.py brands/brand-a
    python3 tools/dashboard/build_master_gallery.py  # všetky brands/*

Štýl sa adaptuje na brand farby z brand-dna/brand-research-brief.json.
"""

import json
import argparse
import html as html_lib
from datetime import datetime
from pathlib import Path


def load_brand_colors(brand_dir: Path) -> dict:
    """Načíta farby z brand-research-brief.json, fallback na neutrálne."""
    defaults = {
        "primary": "#4F6B52",
        "primary_alt": "#2BAF6A",
        "accent": "#F5F5F5",
        "bg": "#0d0d0f",
        "bg_card": "#1a1a1f",
        "bg_card_alt": "#15151a",
        "border": "#222",
        "text": "#f0f0f0",
        "text_muted": "#888",
        "heading_font": "-apple-system, 'Inter', 'Segoe UI', sans-serif",
        "heading_color": "#FCE4EE",
    }
    brief_path = brand_dir / "brand-dna" / "brand-research-brief.json"
    if not brief_path.exists():
        return defaults

    try:
        brief = json.loads(brief_path.read_text(encoding="utf-8"))
    except Exception:
        return defaults

    vs = brief.get("visual_system", {})
    defaults["primary"] = vs.get("primary_color_hex", defaults["primary"])
    defaults["primary_alt"] = vs.get("tertiary_signal_color_hex", defaults["primary_alt"])
    defaults["accent"] = vs.get("accent_color_hex", defaults["accent"])
    defaults["heading_color"] = vs.get("primary_color_hex", defaults["heading_color"])
    return defaults


def discover_ad_sets(brand_dir: Path) -> list:
    """Nájde všetky ad-sets v brand/products/*/product-image-ads/*/."""
    ad_sets = []
    for manifest_path in sorted(brand_dir.glob("products/*/product-image-ads/*/outputs*/manifest.json")):
        ad_set_dir = manifest_path.parent.parent
        product = ad_set_dir.parent.parent.name
        adset = ad_set_dir.name
        output_name = manifest_path.parent.name
        language = output_name[len("outputs-"):] if output_name.startswith("outputs-") else "sk"

        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except Exception:
            continue

        prompts_path = ad_set_dir / f"prompts-{language}.json"
        if not prompts_path.exists() and language == "sk":
            prompts_path = ad_set_dir / "prompts.json"
        prompts_data = {}
        if prompts_path.exists():
            try:
                prompts_data = json.loads(prompts_path.read_text(encoding="utf-8"))
            except Exception:
                pass

        ad_sets.append({
            "product": product,
            "adset": adset,
            "language": language,
            "ad_set_dir": ad_set_dir,
            "manifest": manifest,
            "prompts": prompts_data,
        })
    return ad_sets


def relpath(file_str: str, brand_dir: Path) -> Path:
    """Konvertuje manifest 'file' (absolute alebo brand-root-relative) na cestu relatívnu k brand_dir."""
    p = Path(file_str)
    if p.is_absolute():
        try:
            return p.relative_to(brand_dir)
        except ValueError:
            # Manifest zo starej polohy repozitára (napr. ~/Desktop/...): prepoj od "brands/{brand}/".
            if "brands" not in p.parts:
                return p
    # Manifest cesty sú typicky "brands/{brand}/products/..."
    parts = p.parts
    if "brands" in parts:
        idx = parts.index("brands")
        if idx + 2 < len(parts):
            return Path(*parts[idx + 2:])
    return p


def find_prompt_def(prompts: list, result: dict) -> dict:
    """Nájdi prompt patriaci k výsledku z manifestu.

    Vo workflow v2 môže mať viac konceptov rovnaký template_number aj template_name
    (napr. hook test na jednej šablóne), takže samotný názov šablóny nie je unikátny
    kľúč — rozlišuje až concept_id. Staršie manifesty ho nemajú, tam sa páruje po starom.
    """
    tpl_name = result.get("name", "")
    concept_id = result.get("concept_id")
    if concept_id:
        for p in prompts:
            brief = p.get("brief") or {}
            if p.get("template_name", "") == tpl_name and brief.get("concept_id") == concept_id:
                return p
    return next((p for p in prompts if p.get("template_name", "") == tpl_name), {})


def build_card(result: dict, ad_set: dict, brand_dir: Path) -> str:
    """Vyrenderuje 1 kartu pre 1 vygenerovaný obrázok."""
    aspect = result.get("aspect") or ad_set["prompts"].get("_meta", {}).get("aspect_ratio_default", "")

    tpl_name = result.get("name", "")
    tpl_num = result.get("template", 0)
    variation = result.get("variation", "")
    prompt_def = find_prompt_def(ad_set["prompts"].get("prompts", []), result)

    headline_raw = prompt_def.get("headline") or ""
    headline = headline_raw.replace("\n", " / ").strip()
    ad_id = prompt_def.get("ad_id") or result.get("concept_id") or tpl_name

    rel = relpath(result.get("file", ""), brand_dir)
    abs_path = brand_dir / rel
    size_kb = abs_path.stat().st_size / 1024 if abs_path.exists() else 0

    var_label = variation.split("_")[0] if variation else "v?"

    rel_str = str(rel).replace("\\", "/")

    return f"""
                <div class="card" data-product="{html_lib.escape(ad_set['product'])}" data-adset="{html_lib.escape(ad_set['adset'])}" data-variant="{html_lib.escape(ad_id)}">
                  <a href="{html_lib.escape(rel_str)}" target="_blank">
                    <img src="{html_lib.escape(rel_str)}" alt="T{tpl_num} {var_label}" loading="lazy">
                  </a>
                  <div class="card-info">
                    <h4>T{tpl_num:02d} · {html_lib.escape(ad_id)} · <span class="var-badge">{html_lib.escape(var_label)}</span></h4>
                    <p class="hl">{html_lib.escape(headline) if headline else '<em>(no headline)</em>'}</p>
                    <p class="meta">{html_lib.escape(ad_set['adset'])} · {html_lib.escape(ad_set['language'].upper())} · {html_lib.escape(aspect)} · {size_kb:.1f} KB</p>
                  </div>
                </div>"""


def build_html(brand_dir: Path) -> str:
    brand_name = brand_dir.name
    colors = load_brand_colors(brand_dir)
    ad_sets = discover_ad_sets(brand_dir)

    # Per-adset progress bars
    total_done = sum(a["manifest"].get("total_generated", 0) for a in ad_sets)
    total_failed = sum(a["manifest"].get("total_failed", 0) for a in ad_sets)
    total_attempted = total_done + total_failed
    global_pct = (total_done / total_attempted * 100) if total_attempted else 0

    adset_bars_html = []
    cards_html = []
    products_set = set()
    adsets_set = set()

    for ad_set in ad_sets:
        done = ad_set["manifest"].get("total_generated", 0)
        failed = ad_set["manifest"].get("total_failed", 0)
        total = done + failed
        pct = (done / total * 100) if total else 0
        products_set.add(ad_set["product"])
        adsets_set.add(ad_set["adset"])
        adset_bars_html.append(f"""
                <div class="adset-bar">
                  <div class="adset-label">{html_lib.escape(ad_set['product'])} / {html_lib.escape(ad_set['adset'])}</div>
                  <div class="bar-wrap"><div class="bar" style="width:{pct:.1f}%"></div><span class="bar-text">{done} / {total} ({pct:.0f}%)</span></div>
                </div>""")

        for result in ad_set["manifest"].get("results", []):
            cards_html.append(build_card(result, ad_set, brand_dir))

    product_options = "".join(f'<option value="{html_lib.escape(p)}">{html_lib.escape(p)}</option>' for p in sorted(products_set))
    adset_options = "".join(f'<option value="{html_lib.escape(a)}">{html_lib.escape(a)}</option>' for a in sorted(adsets_set))

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    css = f"""
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      body {{ font-family: {colors['heading_font']}; background: {colors['bg']}; color: {colors['text']}; padding: 24px; }}
      header {{ background: {colors['bg']}; padding: 16px 0 24px; border-bottom: 1px solid {colors['border']}; margin-bottom: 24px; }}
      h1 {{ font-size: 1.8rem; margin-bottom: 4px; color: {colors['heading_color']}; text-transform: uppercase; letter-spacing: 0.05em; }}
      h1 + .subtitle {{ color: {colors['text_muted']}; font-size: 0.85rem; margin-bottom: 20px; }}

      .progress-global {{ background: {colors['bg_card']}; border-radius: 12px; padding: 16px; margin-bottom: 16px; }}
      .progress-global-label {{ font-size: 0.85rem; color: {colors['text_muted']}; margin-bottom: 8px; display: flex; justify-content: space-between; }}
      .bar-wrap {{ position: relative; height: 28px; background: #2a2a2f; border-radius: 14px; overflow: hidden; }}
      .bar {{ height: 100%; background: linear-gradient(90deg, {colors['primary']} 0%, {colors['primary_alt']} 100%); transition: width 0.5s; }}
      .bar-text {{ position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-weight: 700; font-size: 0.9rem; color: #fff; text-shadow: 0 1px 2px rgba(0,0,0,0.5); }}

      .adset-bar {{ background: {colors['bg_card_alt']}; padding: 10px 16px; border-radius: 8px; margin-bottom: 8px; }}
      .adset-label {{ font-size: 0.8rem; color: #aaa; margin-bottom: 6px; font-family: monospace; }}
      .adset-bar .bar-wrap {{ height: 18px; }}
      .adset-bar .bar-text {{ font-size: 0.75rem; }}

      .filters {{ display: flex; gap: 12px; flex-wrap: wrap; margin-top: 16px; }}
      .filters select, .filters input {{ background: {colors['bg_card']}; border: 1px solid #333; color: #fff; padding: 8px 14px; border-radius: 8px; font-size: 0.85rem; }}
      .filters label {{ font-size: 0.85rem; color: {colors['text_muted']}; display: flex; align-items: center; gap: 6px; }}

      .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px; }}
      .card {{ background: {colors['bg_card']}; border-radius: 12px; overflow: hidden; transition: transform 0.15s, box-shadow 0.15s; }}
      .card:hover {{ transform: translateY(-2px); box-shadow: 0 8px 20px {colors['primary']}33; }}
      .card.pending {{ opacity: 0.5; border: 2px dashed #444; }}
      .card img {{ width: 100%; display: block; aspect-ratio: 1 / 1; object-fit: cover; background: #fff; }}
      .card-info {{ padding: 12px 14px; }}
      .card-info h4 {{ font-size: 0.85rem; margin-bottom: 4px; color: #fff; }}
      .var-badge {{ background: {colors['primary']}; color: #fff; padding: 1px 6px; border-radius: 4px; font-size: 0.7rem; font-weight: 700; }}
      .card-info .hl {{ font-size: 0.75rem; color: #bbb; margin-bottom: 4px; line-height: 1.4; }}
      .card-info .meta {{ font-size: 0.7rem; color: #666; font-family: monospace; }}

      .empty-state {{ text-align: center; padding: 60px 20px; color: {colors['text_muted']}; }}
    """

    js = """
      const filterProduct = document.getElementById('filter-product');
      const filterAdset = document.getElementById('filter-adset');
      const filterSearch = document.getElementById('filter-search');
      const hidePending = document.getElementById('hide-pending');

      function applyFilters() {
        const p = filterProduct.value.toLowerCase();
        const a = filterAdset.value.toLowerCase();
        const s = filterSearch.value.toLowerCase();
        const hidePend = hidePending.checked;

        document.querySelectorAll('.card').forEach(card => {
          const cp = (card.dataset.product || '').toLowerCase();
          const ca = (card.dataset.adset || '').toLowerCase();
          const cv = (card.dataset.variant || '').toLowerCase();
          const ch = card.textContent.toLowerCase();
          const isPending = card.classList.contains('pending');

          let show = true;
          if (p && !cp.includes(p)) show = false;
          if (a && !ca.includes(a)) show = false;
          if (s && !cv.includes(s) && !ch.includes(s)) show = false;
          if (hidePend && isPending) show = false;

          card.style.display = show ? '' : 'none';
        });
      }

      filterProduct.addEventListener('change', applyFilters);
      filterAdset.addEventListener('change', applyFilters);
      filterSearch.addEventListener('input', applyFilters);
      hidePending.addEventListener('change', applyFilters);
    """

    grid_content = "\n".join(cards_html) if cards_html else '<div class="empty-state">Žiadne ad-sets nenájdené. Spusti generate_ads.py najprv.</div>'

    return f"""<!DOCTYPE html>
<html lang="sk">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="refresh" content="30">
<title>{html_lib.escape(brand_name).title()} — Master Gallery</title>
<style>{css}</style>
</head>
<body>

<header>
  <h1>{html_lib.escape(brand_name).title()} — Master Gallery</h1>
  <div class="subtitle">Aktualizované {timestamp} · auto-refresh každých 30s</div>

  <div class="progress-global">
    <div class="progress-global-label">
      <span>Celkový progress</span>
      <span><strong>{total_done}</strong> / {total_attempted} vygenerovaných · {total_failed} fail</span>
    </div>
    <div class="bar-wrap"><div class="bar" style="width:{global_pct:.1f}%"></div><span class="bar-text">{global_pct:.1f}%</span></div>
  </div>

  <div class="adset-bars">{''.join(adset_bars_html)}
  </div>

  <div class="filters">
    <label>Produkt: <select id="filter-product"><option value="">všetky</option>{product_options}</select></label>
    <label>Ad-set: <select id="filter-adset"><option value="">všetky</option>{adset_options}</select></label>
    <label>Hľadať: <input type="search" id="filter-search" placeholder="V1, BD01, hero, leto..." /></label>
    <label><input type="checkbox" id="hide-pending"> skryť čakajúce</label>
  </div>
</header>

<div class="grid" id="grid">
{grid_content}
</div>

<script>{js}</script>

</body>
</html>
"""


def build_one(brand_dir: Path) -> None:
    html_content = build_html(brand_dir)
    output_path = brand_dir / "master-gallery.html"
    output_path.write_text(html_content, encoding="utf-8")

    ad_sets = discover_ad_sets(brand_dir)
    total = sum(a["manifest"].get("total_generated", 0) for a in ad_sets)
    print(f"✓ Master gallery saved: {output_path}")
    print(f"  Brand: {brand_dir.name}")
    print(f"  Ad-sets: {len(ad_sets)}")
    print(f"  Total bannerov: {total}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build one or all brand master galleries")
    parser.add_argument("brand_dirs", nargs="*", help="Brand directories; omit to process brands/*")
    args = parser.parse_args()

    if args.brand_dirs:
        brand_dirs = [Path(value).resolve() for value in args.brand_dirs]
    else:
        # parents[2] = koreň repozitára (súbor je v tools/dashboard/)
        brands_root = Path(__file__).resolve().parents[2] / "brands"
        brand_dirs = sorted(path for path in brands_root.iterdir() if path.is_dir()) if brands_root.is_dir() else []

    missing = [path for path in brand_dirs if not path.is_dir()]
    if missing:
        for path in missing:
            print(f"Brand directory neexistuje: {path}")
        return 1
    if not brand_dirs:
        print("Nenašli sa žiadne brand priečinky.")
        return 1

    for brand_dir in brand_dirs:
        build_one(brand_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
