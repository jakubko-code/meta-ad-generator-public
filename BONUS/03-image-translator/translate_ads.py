#!/usr/bin/env python3
"""
Ad Image Translator — prenesie schválený preklad copy do hotového banneru.

Model nič neprekladá sám: dostane dvojice "zdrojový text → schválený text" zo
schváleného prompts-{lang}.json (source_prompts, jazykový scoring, ľudský approval,
potvrdené ceny). Vizuál, layout a produkt ostávajú; texty na obale sa nemenia.
Uses Nano Banana 2 (gemini-3.1-flash-image) via Google API or FAL.

Usage:
    python translate_ads.py --image <ad-set>/outputs/01-headline-C01/headline_v1_img1.png --languages hu,cz
    python translate_ads.py --image ... --languages hu --dry-run
"""

import argparse
import base64
import importlib.util
import json
import mimetypes
import os
import sys
import time
import tempfile
from pathlib import Path

try:
    import requests
except ImportError:
    print("Error: 'requests' required. pip install requests")
    sys.exit(1)


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

def _load_env():
    starts = [Path.cwd().resolve(), Path(__file__).resolve().parent]
    checked = set()
    for start in starts:
        for d in [start] + list(start.parents):
            for env_file in (d / ".env", d / "jozef" / "keys" / ".env"):
                if env_file in checked or not env_file.is_file():
                    continue
                checked.add(env_file)
                with open(env_file, encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            k, v = line.split("=", 1)
                            os.environ.setdefault(k.strip(), v.strip().strip("\"'"))
                return

_load_env()

FAL_KEY = os.environ.get("FAL_KEY", "")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL_ID = "gemini-3.1-flash-image"
FAL_EDIT_ENDPOINT = "fal-ai/nano-banana-2/edit"

LANGUAGE_NAMES = {
    "sk": "Slovak",
    "hu": "Hungarian",
    "cz": "Czech",
    "cs": "Czech",
    "ro": "Romanian",
    "pl": "Polish",
    "de": "German",
    "en": "English",
    "hr": "Croatian",
    "bg": "Bulgarian",
    "rs": "Serbian",
    "si": "Slovenian",
    "uk": "Ukrainian",
    "it": "Italian",
    "es": "Spanish",
    "fr": "French",
    "nl": "Dutch",
    "pt": "Portuguese",
    "sv": "Swedish",
    "no": "Norwegian",
    "da": "Danish",
    "fi": "Finnish",
    "el": "Greek",
    "tr": "Turkish",
    "at": "German",
}

APPROVED_COPY_PROMPT = (
    "Role: Professional Multilingual Graphic Designer for {brand}.\n\n"
    "Task: Replace the ad copy in this image with the APPROVED {language} copy below, maintaining 100% visual identity.\n\n"
    "Approved copy (source text in the image → exact replacement):\n"
    "{pairs}\n\n"
    "Copy Rules:\n"
    "1. Use the replacement strings EXACTLY as written — do not translate on your own, paraphrase, shorten, add or drop words.\n"
    "2. Replace only the listed source texts. Text that is not listed stays exactly as it is.\n"
    "3. EXCLUSIONS:\n"
    "   - Do NOT translate or modify text on the product packaging, labels, or bottle.\n"
    "   - BRAND WORDMARK: The '{brand}' logo/wordmark is a visual element — preserve it EXACTLY as it appears. Do NOT redraw or replace it.\n"
    "   - Keep numbers, prices and ratings exactly as given in the replacement strings.\n\n"
    "Visual Consistency Rules:\n"
    "- POSITION: Place each replacement at the EXACT coordinates of its source text.\n"
    "- STYLE: Match font family, weight (bold/italic), and color perfectly.\n"
    "- SPACING: If the replacement is longer, use tighter kerning or slightly smaller font size. "
    "Do NOT overlap other visual elements.\n"
    "- QUALITY: No blurring or artifacts around the text. The background must remain untouched.\n\n"
    "Double-check: every listed replacement appears exactly once, and no source-language copy remains."
)

REPO_ROOT = Path(__file__).resolve().parents[2]
_GEN_SPEC = importlib.util.spec_from_file_location(
    "generate_ads_gates", REPO_ROOT / "07-image-generation" / "generate_ads.py"
)
gen = importlib.util.module_from_spec(_GEN_SPEC)
_GEN_SPEC.loader.exec_module(gen)


# ---------------------------------------------------------------------------
# Approved copy + gates
# ---------------------------------------------------------------------------

def copy_pairs(source_entry: dict, target_entry: dict) -> list:
    """(pole, zdrojový text, schválený text) pre každé renderované copy pole."""
    pairs = []

    def add(label, src, tgt):
        if isinstance(src, str) and isinstance(tgt, str) and src.strip() and tgt.strip():
            pairs.append((label, src.strip(), tgt.strip()))

    for field in gen.RENDERABLE_COPY_FIELDS:
        add(field, source_entry.get(field), target_entry.get(field))
    for field in ("bullets", "headline_lines", "callouts"):
        src_items, tgt_items = source_entry.get(field) or [], target_entry.get(field) or []
        if isinstance(src_items, list) and isinstance(tgt_items, list):
            for index, (src, tgt) in enumerate(zip(src_items, tgt_items)):
                add(f"{field}[{index}]", src, tgt)
    for index, (src, tgt) in enumerate(zip(source_entry.get("icons") or [], target_entry.get("icons") or [])):
        if isinstance(src, dict) and isinstance(tgt, dict):
            for key in ("value", "label"):
                add(f"icons[{index}].{key}", src.get(key), tgt.get(key))
    src_table, tgt_table = source_entry.get("table") or {}, target_entry.get("table") or {}
    if isinstance(src_table, dict) and isinstance(tgt_table, dict):
        for key in ("left_col_header", "right_col_header"):
            add(f"table.{key}", src_table.get(key), tgt_table.get(key))
        for index, (src, tgt) in enumerate(zip(src_table.get("rows") or [], tgt_table.get("rows") or [])):
            if isinstance(src, dict) and isinstance(tgt, dict):
                for key in ("attr", "left", "right"):
                    add(f"table.rows[{index}].{key}", src.get(key), tgt.get(key))
    return pairs


def find_ad_set(image_path: Path):
    for parent in image_path.parents:
        if parent.parent.name == "product-image-ads":
            return parent
    return None


def entry_for_folder(entries: list, folder_name: str):
    return next(
        (item for item in entries if isinstance(item, dict) and gen.output_folder_name(item) == folder_name),
        None,
    )


def prepare_language(image_path: Path, ad_set: Path, lang: str):
    """Returns (job, issues). Job obsahuje schválené dvojice textov a presné vstupy."""
    prompts_path = ad_set / f"prompts-{lang}.json"
    if not prompts_path.is_file():
        return None, [f"✗ {lang}: chýba {prompts_path.name} — najprv copy translator, scoring a approval"]
    try:
        prompts_data = json.loads(prompts_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return None, [f"✗ {lang}: neplatný {prompts_path.name}: {exc}"]
    if not isinstance(prompts_data, dict):
        return None, [f"✗ {lang}: {prompts_path.name} musí obsahovať JSON objekt"]
    if not prompts_data.get("source_prompts"):
        return None, [f"✗ {lang}: {prompts_path.name} nie je preklad (chýba source_prompts)"]

    issues, approval, _, _ = gen.validate_workflow_gates(prompts_path, lang, prompts_data)
    issues = list(issues) + gen.validate_strategy_contract(prompts_data, prompts_path)
    source_path, source_data, source_issues = gen.load_translation_source(prompts_data, prompts_path)
    issues.extend(source_issues)
    if source_data is None:
        return None, issues

    folder_name = image_path.parent.name
    source_entry = entry_for_folder(source_data.get("prompts", []), folder_name)
    if source_entry is None:
        return None, issues + [f"✗ {lang}: priečinok {folder_name} nezodpovedá žiadnemu promptu v {source_path.name}"]
    concept_id = gen.prompt_concept_id(source_entry)
    target_entry = next(
        (item for item in prompts_data.get("prompts", [])
         if isinstance(item, dict) and gen.prompt_concept_id(item) == concept_id
         and item.get("template_number") == source_entry.get("template_number")),
        None,
    )
    if target_entry is None:
        return None, issues + [f"✗ {lang}: koncept {concept_id or folder_name} chýba v {prompts_path.name}"]

    price_hits = gen.find_prices_in_entry(target_entry)
    if price_hits and not approval.get("market_prices_confirmed"):
        for field, snippet in price_hits:
            issues.append(f"✗ {lang}: cena '{snippet}' v poli '{field}' — approval-{lang}.json nemá market_prices_confirmed")

    pairs = copy_pairs(source_entry, target_entry)
    if not pairs:
        issues.append(f"✗ {lang}: v prompte nie sú renderované copy polia na prenos")
    # Pokrytie oboma smermi: cieľový text bez zdroja nemá kam ísť, zdrojový text bez
    # schváleného prekladu by v banneri ostal v pôvodnom jazyku (prompt ho má zachovať).
    paired = {label for label, _, _ in pairs}
    unplaced = [label for label, _, _ in copy_pairs(target_entry, target_entry) if label not in paired]
    if unplaced:
        issues.append(
            f"✗ {lang}: polia {', '.join(unplaced)} nemajú zdrojový text v banneri — "
            f"preklad by ich nemal kam umiestniť; použi generate_ads.py --lang {lang}"
        )
    untranslated = [label for label, _, _ in copy_pairs(source_entry, source_entry) if label not in paired]
    if untranslated:
        issues.append(
            f"✗ {lang}: zdrojové polia {', '.join(untranslated)} nemajú schválený preklad — "
            f"v banneri by ostal pôvodný text; doplň preklad alebo použi generate_ads.py --lang {lang}"
        )
    return {
        "lang_code": lang,
        "prompts_path": prompts_path,
        "source_path": source_path,
        "target_entry": target_entry,
        "folder_name": folder_name,
        "pairs": pairs,
    }, issues


def render_record(image_path: Path):
    """Záznam o tomto PNG v manifeste jeho outputs priečinka (manifest je per outputs, takže
    priečinok konceptu + názov súboru sú jednoznačné bez ohľadu na cwd pri generovaní)."""
    manifest_path = image_path.parent.parent / "manifest.json"
    try:
        results = json.loads(manifest_path.read_text(encoding="utf-8")).get("results", [])
    except (OSError, json.JSONDecodeError, AttributeError):
        return None
    key = (image_path.parent.name, image_path.name)
    return next(
        (item for item in results
         if isinstance(item, dict) and Path(str(item.get("file", ""))).parts[-2:] == key),
        None,
    )


def load_qa_items(qa_export):
    if not qa_export:
        return None
    try:
        data = json.loads(Path(qa_export).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    items = data.get("items") if isinstance(data, dict) else None
    return [item for item in items or [] if isinstance(item, dict)]


def source_render_issues(image_path: Path, source_path: Path, qa_items) -> list:
    """Vstup musí byť presne evidovaný render aktuálneho schváleného zdroja s vizuálnym PASS."""
    record = render_record(image_path)
    if record is None:
        return [f"✗ {image_path.name} nie je v {image_path.parent.parent.name}/manifest.json — "
                f"prekladá sa iba evidovaný render z generate_ads.py"]
    image_hash = gen.file_sha256(image_path)
    issues = []
    if not record.get("sha256"):
        issues.append(f"✗ {image_path.name} nemá v manifeste SHA-256 (render spred evidencie) — "
                      f"vyrob ho znova cez generate_ads.py alebo použi generate_ads.py --lang")
    elif record["sha256"] != image_hash:
        issues.append(f"✗ {image_path.name} sa od renderu zmenil (hash nesedí s manifestom)")
    render = record.get("render") if isinstance(record.get("render"), dict) else {}
    if render.get("prompts_file") != source_path.name or render.get("prompts_sha256") != gen.file_sha256(source_path):
        issues.append(f"✗ {image_path.name} nevznikol z aktuálneho schváleného {source_path.name} — "
                      f"zdroj sa zmenil alebo ide o iný jazyk / starší render")
    if qa_items is None:
        issues.append("✗ chýba --qa-export: creative-qa.json z dashboardu s vizuálnym PASS pre tento PNG")
    elif not any(item.get("sha256") == image_hash and item.get("status") == "pass" for item in qa_items):
        issues.append(f"✗ {image_path.name} nemá v QA exporte vizuálny PASS pre presne tento súbor (hash)")
    return issues


def source_aspect(image_path: Path, entry: dict) -> str:
    manifest_path = image_path.parent.parent / "manifest.json"
    try:
        for result in json.loads(manifest_path.read_text(encoding="utf-8")).get("results", []):
            if Path(result.get("file", "")).name == image_path.name and result.get("aspect"):
                return gen.api_aspect(result["aspect"])
    except (OSError, json.JSONDecodeError):
        pass
    return gen.api_aspect(entry.get("aspect_ratio") or "4:5")


def write_manifest(output_dir: Path, brand: str, provider: str, results: list) -> None:
    manifest_path = output_dir / "manifest.json"
    previous = []
    if manifest_path.exists():
        try:
            previous = json.loads(manifest_path.read_text(encoding="utf-8")).get("results", [])
        except (OSError, json.JSONDecodeError):
            previous = []
    seen = {item["file"] for item in results}
    merged = results + [item for item in previous if item.get("file") not in seen]
    manifest_path.write_text(json.dumps({
        "brand": brand,
        "provider": provider,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "total_generated": len(merged),
        "total_failed": 0,
        "last_run_generated": len(results),
        "results": merged,
    }, indent=2), encoding="utf-8")


# ---------------------------------------------------------------------------
# Google helpers
# ---------------------------------------------------------------------------

def load_image_part_google(image_path: str):
    try:
        from google.genai import types
    except ImportError:
        print("Error: 'google-genai' required. pip install google-genai")
        sys.exit(1)
    mime = mimetypes.guess_type(image_path)[0] or "image/png"
    with open(image_path, "rb") as f:
        data = f.read()
    return types.Part.from_bytes(data=data, mime_type=mime)


def translate_google_realtime(image_part, prompt_text: str, aspect_ratio: str) -> bytes:
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        print("Error: 'google-genai' required. pip install google-genai")
        sys.exit(1)
    client = genai.Client(api_key=GEMINI_API_KEY)
    response = client.models.generate_content(
        model=GEMINI_MODEL_ID,
        contents=[image_part, types.Part.from_text(text=prompt_text)],
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE"],
            image_config=types.ImageConfig(aspect_ratio=aspect_ratio),
        ),
    )
    for part in response.candidates[0].content.parts:
        if part.inline_data:
            return part.inline_data.data
    raise ValueError("No image returned in response")


# ---------------------------------------------------------------------------
# Google Batch
# ---------------------------------------------------------------------------

def translate_google_batch(image_path: str, jobs: list, aspect_ratio: str, brand: str) -> list:
    """
    jobs: list of {"lang_code": "hu", "lang_name": "Hungarian", "output_path": Path}
    Returns list of result dicts.
    """
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        print("Error: 'google-genai' required. pip install google-genai")
        sys.exit(1)

    client = genai.Client(api_key=GEMINI_API_KEY)

    mime = mimetypes.guess_type(image_path)[0] or "image/png"
    with open(image_path, "rb") as f:
        image_b64 = base64.b64encode(f.read()).decode("utf-8")

    jsonl_lines = []
    key_map = {}

    for job in jobs:
        key = job["lang_code"]
        key_map[key] = job
        prompt_text = job["prompt"]
        jsonl_lines.append(json.dumps({
            "key": key,
            "request": {
                "contents": [{
                    "parts": [
                        {"inlineData": {"mimeType": mime, "data": image_b64}},
                        {"text": prompt_text},
                    ]
                }],
                "generation_config": {
                    "responseModalities": ["IMAGE"],
                    "imageConfig": {"aspectRatio": aspect_ratio},
                }
            }
        }))

    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
        f.write("\n".join(jsonl_lines))
        jsonl_path = f.name

    slug = Path(image_path).stem
    print(f"Uploading batch ({len(jsonl_lines)} languages)...")
    uploaded = client.files.upload(
        file=jsonl_path,
        config=types.UploadFileConfig(display_name=f"{slug}-translate-batch", mime_type="jsonl"),
    )

    print("Submitting batch job...")
    batch_job = client.batches.create(
        model=GEMINI_MODEL_ID,
        src=uploaded.name,
        config={"display_name": f"{slug}-translate"},
    )
    print(f"Batch job: {batch_job.name}")
    print("Čakám na výsledky (môže trvať až 24h, kontrolujem každých 30s)...\n")

    done_states = {"JOB_STATE_SUCCEEDED", "JOB_STATE_FAILED", "JOB_STATE_CANCELLED", "JOB_STATE_EXPIRED"}
    while True:
        batch_job = client.batches.get(name=batch_job.name)
        state = batch_job.state.name
        print(f"  Status: {state} ({time.strftime('%H:%M:%S')})")
        if state in done_states:
            break
        time.sleep(30)

    if batch_job.state.name != "JOB_STATE_SUCCEEDED":
        print(f"✗ Batch failed: {batch_job.state.name}")
        return []

    result_file = batch_job.dest.file_name
    file_content = client.files.download(file=result_file)

    results = []
    for line in file_content.decode("utf-8").splitlines():
        if not line.strip():
            continue
        resp = json.loads(line)
        key = resp.get("key", "")
        if key not in key_map:
            continue
        job = key_map[key]
        try:
            candidates = resp.get("response", {}).get("candidates", [])
            if not candidates:
                print(f"  ✗ {key}: no candidates — {str(resp.get('response', {}))[:300]}")
                continue
            content = candidates[0].get("content", {})
            parts = content.get("parts", [])
            if not parts:
                finish = candidates[0].get("finishReason", "unknown")
                print(f"  ✗ {key}: no parts (finishReason={finish}) — {str(content)[:200]}")
                continue
            img_bytes = None
            for part in parts:
                if "inlineData" in part:
                    img_bytes = base64.b64decode(part["inlineData"]["data"])
                    break
            if not img_bytes:
                print(f"  ✗ {key}: no image in response")
                continue
            with open(job["output_path"], "wb") as f:
                f.write(img_bytes)
            print(f"  ✓ {key}: {job['output_path'].name}")
            results.append({"lang": key, "file": str(job["output_path"])})
        except Exception as e:
            print(f"  ✗ {key}: {e}")

    os.unlink(jsonl_path)
    return results


# ---------------------------------------------------------------------------
# FAL helpers
# ---------------------------------------------------------------------------

def upload_to_fal(image_path: str) -> str:
    mime = mimetypes.guess_type(image_path)[0] or "image/png"
    with open(image_path, "rb") as f:
        data = f.read()
    resp = requests.post(
        "https://fal.run/fal-ai/file-storage/upload",
        headers={"Authorization": f"Key {FAL_KEY}"},
        files={"file": (os.path.basename(image_path), data, mime)},
    )
    if resp.status_code != 200:
        b64 = base64.b64encode(data).decode("utf-8")
        return f"data:{mime};base64,{b64}"
    result = resp.json()
    return result.get("url", result.get("file_url", ""))


def translate_fal(image_url: str, prompt_text: str, aspect_ratio: str) -> bytes:
    resp = requests.post(
        f"https://fal.run/{FAL_EDIT_ENDPOINT}",
        headers={"Authorization": f"Key {FAL_KEY}", "Content-Type": "application/json"},
        json={
            "prompt": prompt_text,
            "image_urls": [image_url],
            "aspect_ratio": aspect_ratio,
            "num_images": 1,
            "output_format": "png",
            "safety_tolerance": "5",
        },
        timeout=180,
    )
    resp.raise_for_status()
    result = resp.json()
    img_url = result["images"][0]["url"]
    img_resp = requests.get(img_url)
    img_resp.raise_for_status()
    return img_resp.content


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Transfer approved translated copy into a finished ad image via Nano Banana 2"
    )
    parser.add_argument("--image", required=True,
        help="Hotový banner v <ad-set>/outputs*/<NN-template-concept>/")
    parser.add_argument("--languages", required=True,
        help="Kódy jazykov so schváleným prompts-{lang}.json, napr. hu,cz")
    parser.add_argument("--brand", default=None,
        help="Presný názov značky; inak z prompts JSON")
    parser.add_argument("--provider", choices=["fal", "google", "google-batch"], default="google",
        help="Generation provider (default: google)")
    parser.add_argument("--qa-export", default=None,
        help="creative-qa.json z dashboardu; zdrojový PNG v ňom musí mať PASS so zhodným hashom")
    parser.add_argument("--aspect-ratio", default=None,
        help="Pomer strán; default z manifestu zdroja alebo z promptu")
    parser.add_argument("--dry-run", action="store_true",
        help="Over brány a ukáž presné prompty bez volania API")
    args = parser.parse_args()

    image_path = Path(args.image).resolve()
    if not image_path.is_file():
        print(f"Error: image not found: {image_path}")
        return 1
    ad_set = find_ad_set(image_path)
    if ad_set is None:
        print("Error: image translator prenáša iba schválené preklady bannerov z ad setu "
              "(products/<produkt>/product-image-ads/<ad-set>/outputs*/...).")
        return 1

    lang_codes = [code.strip().lower() for code in args.languages.split(",") if code.strip()]
    unknown = [code for code in lang_codes if code not in LANGUAGE_NAMES]
    if unknown:
        print(f"Error: neznáme kódy jazykov: {unknown}. Podporované: {', '.join(sorted(LANGUAGE_NAMES))}")
        return 1

    jobs, issues = [], []
    for code in lang_codes:
        job, job_issues = prepare_language(image_path, ad_set, code)
        issues.extend(job_issues)
        if job:
            jobs.append(job)
    qa_items = load_qa_items(args.qa_export)
    for source_path in sorted({job["source_path"] for job in jobs}):
        issues.extend(source_render_issues(image_path, source_path, qa_items))
    if issues:
        print("\n✗ PRE-FLIGHT ZLYHAL:")
        for issue in issues:
            print(f"   {issue}")
        print("\nPreklad je zablokovaný. Oprav preklad copy, scoring alebo schválenie a spusti znova.")
        return 1

    target_prompts = json.loads(jobs[0]["prompts_path"].read_text(encoding="utf-8"))
    brand = args.brand or target_prompts.get("brand") or ad_set.parents[3].name
    source_hash = gen.file_sha256(image_path)
    for job in jobs:
        job["lang_name"] = LANGUAGE_NAMES[job["lang_code"]]
        pairs = "\n".join(f'- "{src}" → "{tgt}"' for _, src, tgt in job["pairs"])
        job["prompt"] = APPROVED_COPY_PROMPT.format(language=job["lang_name"], brand=brand, pairs=pairs)
        job["output_dir"] = ad_set / gen.default_output_dir(job["lang_code"])
        job["output_path"] = job["output_dir"] / job["folder_name"] / f"{image_path.stem}_translated.png"
    aspect_ratio = args.aspect_ratio or source_aspect(image_path, jobs[0]["target_entry"])

    print(f"\n{'='*60}")
    print(f"  Ad Image Translator — schválený preklad copy")
    print(f"  Source:       {image_path.name}")
    print(f"  Brand:        {brand}")
    print(f"  Languages:    {', '.join(job['lang_name'] for job in jobs)}")
    print(f"  Provider:     {args.provider.upper()}")
    print(f"  Aspect ratio: {aspect_ratio}")
    print(f"{'='*60}\n")

    if args.dry_run:
        print("DRY RUN — brány prešli; prompty, ktoré by sa poslali:\n")
        for job in jobs:
            print(f"[{job['lang_code'].upper()}] → {job['output_path']}\n{job['prompt']}\n")
        return 0

    if args.provider == "fal" and not FAL_KEY:
        print("Error: FAL_KEY not set. Export it or place it in a parent .env file.")
        return 1
    if args.provider in ("google", "google-batch") and not GEMINI_API_KEY:
        print("Error: GEMINI_API_KEY not set. Export it or place it in a parent .env file.")
        return 1

    for job in jobs:
        job["output_path"].parent.mkdir(parents=True, exist_ok=True)

    results = []
    if args.provider == "google-batch":
        results = translate_google_batch(str(image_path), jobs, aspect_ratio, brand)
    elif args.provider == "google":
        image_part = load_image_part_google(str(image_path))
        for job in jobs:
            print(f"Translating → {job['lang_name']}...")
            try:
                img_bytes = translate_google_realtime(image_part, job["prompt"], aspect_ratio)
                job["output_path"].write_bytes(img_bytes)
                print(f"  ✓ {job['output_path'].name}")
                results.append({"lang": job["lang_code"], "file": str(job["output_path"])})
            except Exception as e:
                print(f"  ✗ {job['lang_name']}: {e}")
    else:
        print("Uploading source image to FAL storage...")
        image_url = upload_to_fal(str(image_path))
        print("  ✓ Uploaded\n")
        for job in jobs:
            print(f"Translating → {job['lang_name']}...")
            try:
                img_bytes = translate_fal(image_url, job["prompt"], aspect_ratio)
                job["output_path"].write_bytes(img_bytes)
                print(f"  ✓ {job['output_path'].name}")
                results.append({"lang": job["lang_code"], "file": str(job["output_path"])})
            except Exception as e:
                print(f"  ✗ {job['lang_name']}: {e}")

    # Manifest v outputs-{lang}/ → banner sa zobrazí v dashboarde a nesie presnú verziu vstupov.
    by_lang = {job["lang_code"]: job for job in jobs}
    for result in results:
        job = by_lang[result["lang"]]
        entry = job["target_entry"]
        write_manifest(job["output_dir"], brand, args.provider, [{
            "template": entry.get("template_number"),
            "name": gen.safe_template_name(entry.get("template_name", "")),
            "concept_id": gen.prompt_concept_id(entry) or None,
            "variation": f"{image_path.stem.split('_', 1)[-1]}_translated",
            "aspect": aspect_ratio,
            "file": result["file"],
            "sha256": gen.file_sha256(Path(result["file"])),
            "render": {
                "method": "image-translate",
                "source_image": image_path.name,
                "source_image_sha256": source_hash,
                "prompts_file": job["prompts_path"].name,
                "prompts_sha256": gen.file_sha256(job["prompts_path"]),
                "provider": args.provider,
                "model": FAL_EDIT_ENDPOINT if args.provider == "fal" else GEMINI_MODEL_ID,
            },
        }])

    print(f"\n{'='*60}")
    print(f"  Done: {len(results)}/{len(jobs)} translations")
    if len(results) < len(jobs):
        failed = [job["lang_code"] for job in jobs if not any(r["lang"] == job["lang_code"] for r in results)]
        print(f"  Failed: {', '.join(failed)}")
    print(f"{'='*60}\n")
    return 0 if len(results) == len(jobs) else 1


if __name__ == "__main__":
    raise SystemExit(main())
