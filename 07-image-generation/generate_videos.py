#!/usr/bin/env python3
"""
generate_videos.py — Veo (Gemini API) video generátor pre BONUS/05-video-concepts.

Analóg generate_ads.py, ale pre VIDEO. Číta segmentový JSON (hook-a / hook-b / telo / cta
alebo {"segments":[...]}) a pre každý segment zavolá Veo cez google-genai, odpolluje
long-running operáciu a stiahne mp4. Voliteľne segmenty pospája cez ffmpeg.

Príklady:
    # dry-run (NIČ nemíňa — len ukáže, čo by sa generovalo)
    python generate_videos.py --concept-dir brands/<znacka>/products/<produkt>/animations/2026-06-22-relax-concepts/5-min-pre-teba --dry-run

    # ostrý beh jedného segmentu (najlacnejší test)
    python generate_videos.py --prompts-file .../5-min-pre-teba/cta.json

    # celý koncept + auto-assemble A/B verzií
    python generate_videos.py --concept-dir .../5-min-pre-teba --assemble

Pozn.: VIDEO STOJÍ PENIAZE. Default model je veo-3.1-fast (najlacnejší).
"""
import argparse, json, os, re, sys, time, subprocess
from pathlib import Path

DEFAULT_MODEL = "veo-3.1-fast-generate-preview"
POLL_SECONDS = 10
POLL_TIMEOUT = 600  # 10 min na klip


def load_api_key() -> str:
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if env_path.exists():
        env = dict(re.findall(r'^([A-Z_]+)=(.*)$', env_path.read_text(), re.M))
        key = env.get("GEMINI_API_KEY", "").strip()
        if key:
            return key
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not key:
        print("Error: GEMINI_API_KEY chýba (.env alebo env).")
        sys.exit(1)
    return key


def shot_to_prompt(seg: dict) -> str:
    """Sploští štruktúrovaný segment JSON do textového Veo promptu."""
    shot = seg.get("shot", {})
    parts = []
    order = ["scene", "subject", "action", "camera", "lighting", "mood"]
    for k in order:
        v = shot.get(k)
        if v:
            parts.append(f"{k.capitalize()}: {v}.")
    if seg.get("product_fidelity"):
        parts.append(f"Product (reproduce exactly): {seg['product_fidelity']}")
    cont = seg.get("continuity", {})
    if cont.get("grade"):
        parts.append(f"Color grade: {cont['grade']}.")
    return " ".join(parts).strip()


def collect_segments(args) -> list:
    """Vráti zoznam (name, path, seg_dict)."""
    segs = []
    if args.prompts_file:
        p = Path(args.prompts_file)
        data = json.loads(p.read_text())
        if "segments" in data:
            for i, s in enumerate(data["segments"]):
                segs.append((s.get("segment", f"seg{i}"), p, s))
        else:
            segs.append((data.get("segment", p.stem), p, data))
    elif args.concept_dir:
        d = Path(args.concept_dir)
        for name in ["hook-a", "hook-b", "telo", "cta"]:
            f = d / f"{name}.json"
            if f.exists():
                segs.append((name, f, json.loads(f.read_text())))
        # extra telo-N pri extension
        for f in sorted(d.glob("telo-*.json")):
            segs.append((f.stem, f, json.loads(f.read_text())))
    else:
        print("Error: zadaj --prompts-file alebo --concept-dir.")
        sys.exit(1)
    return segs


def out_dir_for(args) -> Path:
    if args.output_dir:
        return Path(args.output_dir)
    base = Path(args.concept_dir) if args.concept_dir else Path(args.prompts_file).parent
    return base / "exports"


def generate_one(client, types, seg, name, image_path, model, out_path):
    prompt = shot_to_prompt(seg)
    cfg_kwargs = {
        "aspect_ratio": seg.get("aspect_ratio", "9:16"),
        "number_of_videos": 1,
    }
    if seg.get("negative"):
        cfg_kwargs["negative_prompt"] = seg["negative"]
    # duration: Veo 3.1 podporuje 4/6/8 s — TREBA reálne poslať do configu (inak default 8 s).
    dur = seg.get("duration_seconds")
    if dur:
        cfg_kwargs["duration_seconds"] = int(dur)
    # resolution: napr. "720p" / "1080p"; vyššie rozlíšenie môže odomknúť kratšie dĺžky pri t2v
    res = seg.get("resolution")
    if res:
        cfg_kwargs["resolution"] = res
    kwargs = dict(model=model, prompt=prompt,
                  config=types.GenerateVideosConfig(**cfg_kwargs))
    # image-to-video (produktová fotka / start frame ako prvý frame)
    if image_path:
        data = Path(image_path).read_bytes()
        mime = "image/png" if str(image_path).lower().endswith("png") else "image/jpeg"
        kwargs["image"] = types.Image(image_bytes=data, mime_type=mime)

    op = client.models.generate_videos(**kwargs)
    waited = 0
    while not op.done:
        if waited > POLL_TIMEOUT:
            raise TimeoutError(f"{name}: operácia prekročila {POLL_TIMEOUT}s")
        time.sleep(POLL_SECONDS)
        waited += POLL_SECONDS
        op = client.operations.get(op)
    vids = op.response.generated_videos
    if not vids:
        raise ValueError(f"{name}: žiadne video v odpovedi")
    vid = vids[0].video
    client.files.download(file=vid)
    vid.save(str(out_path))
    return out_path


def assemble(out_dir: Path, segs=None):
    """ffmpeg concat podľa reálne existujúcich mp4: hook-a/b + telo + cta -> verzia-a/b."""
    def path(n): return out_dir / f"{n}.mp4"
    plan = []
    if all(path(n).exists() for n in ["hook-a", "telo", "cta"]):
        plan.append(("verzia-a", ["hook-a", "telo", "cta"]))
    if all(path(n).exists() for n in ["hook-b", "telo", "cta"]):
        plan.append(("verzia-b", ["hook-b", "telo", "cta"]))
    if not plan:
        print("  (assemble preskočené — chýbajú niektoré mp4: treba hook-a/hook-b + telo + cta)")
    for label, order in plan:
        listfile = out_dir / f"_{label}.txt"
        listfile.write_text("".join(f"file '{path(n).resolve()}'\n" for n in order))
        target = out_dir / f"{label}.mp4"
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat",
                        "-safe", "0", "-i", str(listfile), "-c", "copy", str(target)],
                       check=True)
        listfile.unlink(missing_ok=True)
        print(f"  ✓ assembled {target.name} ({' + '.join(order)})")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompts-file", help="jeden segment JSON alebo {segments:[...]}")
    ap.add_argument("--concept-dir", help="priečinok s hook-a/hook-b/telo/cta .json")
    ap.add_argument("--image", help="image-to-video: cesta k fotke/start frame (prvý frame)")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--duration", type=int, default=None, help="dĺžka s (4/6/8) — override pre všetky segmenty")
    ap.add_argument("--resolution", default=None, help="napr. 720p / 1080p — override pre všetky segmenty")
    ap.add_argument("--output-dir", help="kam uložiť mp4 (default <dir>/exports)")
    ap.add_argument("--assemble", action="store_true", help="po generovaní pospájať A/B cez ffmpeg")
    ap.add_argument("--dry-run", action="store_true", help="nič negeneruj, len vypíš plán")
    args = ap.parse_args()

    segs = collect_segments(args)
    # CLI override dĺžky/rozlíšenia pre všetky segmenty
    for _n, _p, _s in segs:
        if args.duration:
            _s["duration_seconds"] = args.duration
        if args.resolution:
            _s["resolution"] = args.resolution
    out_dir = out_dir_for(args)

    print("=" * 60)
    print(f"  Veo Video Generator  |  model: {args.model}")
    print(f"  Segmentov: {len(segs)}  |  output: {out_dir}")
    print("=" * 60)
    for name, path, seg in segs:
        ar = seg.get("aspect_ratio", "9:16")
        dur = seg.get("duration_seconds", "?")
        print(f"\n[{name}] {ar} ~{dur}s")
        print(f"  prompt: {shot_to_prompt(seg)[:160]}...")
    if args.dry_run:
        print("\nDRY RUN — nič sa nevygenerovalo, nič sa neminulo.")
        if args.assemble:
            print("(--assemble by pospájal verziu A/B z hook-a/b + telo + cta)")
        return

    key = load_api_key()
    from google import genai
    from google.genai import types
    client = genai.Client(api_key=key)
    out_dir.mkdir(parents=True, exist_ok=True)

    ok = 0
    for name, path, seg in segs:
        try:
            # per-segment image (relatívne k JSON súboru) má prednosť pred --image
            seg_img = seg.get("image")
            img_path = str((path.parent / seg_img).resolve()) if seg_img else args.image
            tag = " [i2v]" if img_path else " [t2v]"
            print(f"\n[{name}]{tag} generujem cez Veo (async, môže trvať minúty)...")
            target = out_dir / f"{name}.mp4"
            generate_one(client, types, seg, name, img_path, args.model, target)
            print(f"  ✓ {target}")
            ok += 1
        except Exception as e:
            print(f"  ✗ {name} zlyhalo: {e}")

    print(f"\nHotovo: {ok}/{len(segs)} segmentov.")
    if args.assemble and ok:
        print("Assembling A/B verzií cez ffmpeg...")
        assemble(out_dir, segs)


if __name__ == "__main__":
    main()
