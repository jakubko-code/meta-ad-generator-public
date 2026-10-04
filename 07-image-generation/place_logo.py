#!/usr/bin/env python3
"""Umiestni brand logo na už vygenerované obrázky — bez nového volania API.

Používa čisté verzie odložené cez `generate_ads.py --logo-keep-clean`
(`outputs/.../_clean/`), takže posun loga do iného rohu, zmena veľkosti alebo
odstupu nestojí ani cent a dá sa vyskúšať koľkokrát treba.

Príklady:
    # prepíše hotové výstupy logom v pravom dolnom rohu
    python3 07-image-generation/place_logo.py \\
      --ad-set brands/{brand}/products/{p}/product-image-ads/{ad-set} \\
      --position bottom-right

    # náhľad do samostatného priečinka, bez prepisovania výstupov
    python3 07-image-generation/place_logo.py --ad-set ... \\
      --position top-left --out-suffix nahlad-topleft

Logo sa berie z `brand-dna/` (logo.png / logo-white.png); verziu vyberá skript
sám podľa kontrastu s plochou pod logom. Pri prepísaní výstupov aktualizuje SHA-256
v `outputs/manifest.json`, aby B2 handoff sedel so súborom.
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from generate_ads import LOGO_POSITIONS, composite_logo  # noqa: E402


def find_brand_cards_dir(start: Path):
    """Nájde brand-dna/ smerom nahor od ad setu — rovnaká logika ako v generátore."""
    for parent in [start] + list(start.parents):
        candidate = parent / "brand-dna"
        if candidate.is_dir():
            return candidate
    return None


def collect_clean_images(outputs_dir: Path):
    """Vráti dvojice (čistý zdroj, cieľový výstup) pre každý vygenerovaný obrázok."""
    pairs = []
    for clean_dir in sorted(outputs_dir.glob("*/_clean")):
        for clean in sorted(clean_dir.glob("*.png")):
            pairs.append((clean, clean_dir.parent / clean.name))
    return pairs


def update_manifest_hashes(outputs_dir: Path, replaced: dict) -> int:
    """Prepíše sha256 pri výstupoch, na ktoré sa logo vložilo nanovo. Vracia počet zmien."""
    manifest_path = outputs_dir / "manifest.json"
    if not replaced or not manifest_path.is_file():
        return 0
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    repo = outputs_dir
    while repo.parent != repo and not (repo / "brands").is_dir():
        repo = repo.parent
    changed = 0
    for result in manifest.get("results", []):
        target = (repo / result.get("file", "")).resolve()
        if target in replaced:
            result["sha256"], result["logo"] = replaced[target]
            changed += 1
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return changed


def main() -> int:
    ap = argparse.ArgumentParser(description="Umiestni logo na hotové bannery bez regenerácie")
    ap.add_argument("--ad-set", required=True, help="Priečinok ad setu (obsahuje outputs/)")
    ap.add_argument("--brand-dna", default=None, help="Cesta k brand-dna/ (default: hľadá sa nahor)")
    ap.add_argument("--position", default="bottom-left", choices=list(LOGO_POSITIONS))
    ap.add_argument("--width", type=float, default=0.18, help="Šírka loga ako podiel šírky obrázka")
    ap.add_argument("--margin", type=float, default=0.05, help="Vodorovný okraj ako podiel šírky")
    ap.add_argument("--margin-y", type=float, default=None,
                    help="Zvislý okraj ako podiel výšky (pri 9:16 pre Reels ~0.30)")
    ap.add_argument("--out-suffix", default=None,
                    help="Ak je zadané, zapíše do outputs/<priecinok>-<suffix>/ namiesto prepísania")
    args = ap.parse_args()

    ad_set = Path(args.ad_set).resolve()
    outputs_dir = ad_set / "outputs"
    if not outputs_dir.is_dir():
        print(f"✗ Chýba {outputs_dir}")
        return 1

    brand_cards = Path(args.brand_dna).resolve() if args.brand_dna else find_brand_cards_dir(ad_set)
    if not brand_cards or not brand_cards.is_dir():
        print("✗ Nenašiel sa priečinok brand-dna/ s logom")
        return 1

    pairs = collect_clean_images(outputs_dir)
    if not pairs:
        print("✗ Nenašli sa čisté verzie (_clean/). Vygeneruj s --logo-keep-clean, "
              "inak sa logo nedá presunúť bez nového generovania.")
        return 1

    done = 0
    replaced = {}
    for clean, target in pairs:
        if args.out_suffix:
            target = target.parent.with_name(f"{target.parent.name}-{args.out_suffix}") / target.name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(clean.read_bytes())
        placed = composite_logo(str(target), brand_cards, width_ratio=args.width,
                                margin_ratio=args.margin, position=args.position,
                                margin_y_ratio=args.margin_y)
        if not placed:
            print(f"  ✗ {target.parent.name}: logo sa nevložilo")
            continue
        name, (w, h) = placed
        if not args.out_suffix:
            digest = hashlib.sha256(target.read_bytes()).hexdigest()
            replaced[target.resolve()] = (digest, {"file": name, "position": args.position, "width": args.width})
        print(f"  ✓ {target.parent.name}/{target.name} — {name} {w}x{h} px ({args.position})")
        done += 1

    changed = update_manifest_hashes(outputs_dir, replaced)
    if changed:
        print(f"  ✓ manifest.json: aktualizované SHA-256 pri {changed} výstupoch")
    print(f"\nHotovo: {done}/{len(pairs)} obrázkov, bez volania API.")
    return 0 if done else 1


if __name__ == "__main__":
    raise SystemExit(main())
