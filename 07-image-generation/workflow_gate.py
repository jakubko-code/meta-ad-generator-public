#!/usr/bin/env python3
"""Create hash-bound scoring and human-approval artifacts for an ad set.

This helper never scores copy and never approves it on behalf of a person. It only
creates the machine-readable records consumed by generate_ads.py.
"""

import argparse
import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def artifact_path(prompts: Path, kind: str) -> Path:
    suffix = prompts.name[len("prompts"):] if prompts.name.startswith("prompts") else f"-{prompts.stem}.json"
    return prompts.with_name(f"{kind}{suffix}")


def write_json(path: Path, data: dict, overwrite: bool = False) -> None:
    if path.exists() and not overwrite:
        raise SystemExit(f"Refusing to overwrite {path}. Use --force only after reviewing it.")
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(path)


def translation_source(prompts: Path, mode: str):
    """A translation (source_prompts) is always bound to its approved source, whatever the scoring mode."""
    data = json.loads(prompts.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit(f"{prompts.name} must contain a JSON object.")
    if "source_prompts" not in data:
        if mode == "translation":
            raise SystemExit(
                "--mode translation requires \"source_prompts\": \"prompts-sk.json\" in the translated prompts JSON. "
                "A new source text uses --mode source with all 8 agents."
            )
        return None
    name = data.get("source_prompts")
    if not isinstance(name, str) or not name.strip() or Path(name).name != name:
        raise SystemExit("source_prompts must be a file name in the same ad set, e.g. prompts-sk.json.")
    source = prompts.with_name(name)
    if not source.is_file() or source.resolve() == prompts.resolve():
        raise SystemExit(f"source_prompts {name} must be another existing prompts file in the same ad set.")
    return source


def init_scoring(args) -> None:
    prompts = Path(args.prompts).resolve()
    prompt_hash = sha256(prompts)
    source = translation_source(prompts, args.mode)
    agent_ids = ["04", "05", "06", "07", "08"] if args.mode == "translation" else [f"{i:02d}" for i in range(1, 9)]
    agents = {}
    for agent_id in agent_ids:
        result = {"verdict": "PENDING", "notes": ""}
        if agent_id != "08":
            result["score"] = None
        agents[agent_id] = result
    record = {
        "schema_version": 1,
        "mode": args.mode,
        "status": "pending",
        "prompts_sha256": prompt_hash,
    }
    if source:
        record["source_prompts"] = source.name
        record["source_prompts_sha256"] = sha256(source)
    record["agents"] = agents
    write_json(artifact_path(prompts, "scoring"), record, args.force)


def approve(args) -> None:
    prompts = Path(args.prompts).resolve()
    blocked = {"ai", "agent", "assistant", "chatgpt", "claude", "codex"}
    if args.by.strip().lower() in blocked:
        raise SystemExit("--by must identify the human approver, not an AI agent.")
    write_json(artifact_path(prompts, "approval"), {
        "schema_version": 1,
        "status": "approved",
        "approved_by": args.by.strip(),
        "approved_at": args.at,
        "language": args.language.lower(),
        "market_prices_confirmed": args.market_prices_confirmed,
        "prompts_sha256": sha256(prompts),
    }, args.force)


OVERRIDABLE_AGENTS = ("01", "02", "03", "05")


def override(args) -> None:
    """Record a human's conscious decision to accept a failed creative score. The real score stays."""
    prompts = Path(args.prompts).resolve()
    if args.by.strip().lower() in {"ai", "agent", "assistant", "chatgpt", "claude", "codex"}:
        raise SystemExit("--by must identify the human who accepts the exception, not an AI agent.")
    if not args.reason.strip():
        raise SystemExit("--reason is required.")
    path = artifact_path(prompts, "scoring")
    if not path.is_file():
        raise SystemExit(f"{path.name} does not exist. Run init-scoring and record the real agent results first.")
    scoring = json.loads(path.read_text(encoding="utf-8"))
    prompt_hash = sha256(prompts)
    if scoring.get("prompts_sha256") != prompt_hash:
        raise SystemExit(f"{path.name} is bound to different prompt bytes. Re-score the current prompts first.")
    result = (scoring.get("agents") or {}).get(args.agent)
    score = result.get("score") if isinstance(result, dict) else None
    if isinstance(score, bool) or not isinstance(score, (int, float)):
        raise SystemExit(f"Agent {args.agent} has no recorded numeric score; an override cannot replace scoring.")
    scoring.setdefault("human_overrides", {})[args.agent] = {
        "by": args.by.strip(),
        "at": args.at,
        "reason": args.reason.strip(),
        "score_at_override": score,
        "prompts_sha256": prompt_hash,
    }
    write_json(path, scoring, overwrite=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Manage hash-bound ad workflow gates")
    sub = parser.add_subparsers(dest="command", required=True)

    hash_cmd = sub.add_parser("hash", help="Print SHA-256 of an exact prompts file")
    hash_cmd.add_argument("prompts")

    init_cmd = sub.add_parser("init-scoring", help="Create a pending scoring artifact")
    init_cmd.add_argument("--prompts", required=True)
    init_cmd.add_argument("--mode", choices=["source", "translation"], default="source")
    init_cmd.add_argument("--force", action="store_true")
    init_cmd.set_defaults(func=init_scoring)

    approve_cmd = sub.add_parser("approve", help="Record an explicit human approval")
    approve_cmd.add_argument("--prompts", required=True)
    approve_cmd.add_argument("--by", required=True, help="Name or identifier of the human approver")
    approve_cmd.add_argument("--at", required=True, help="Approval timestamp, preferably ISO 8601")
    approve_cmd.add_argument("--language", required=True)
    approve_cmd.add_argument("--market-prices-confirmed", action="store_true")
    approve_cmd.add_argument("--force", action="store_true")
    approve_cmd.set_defaults(func=approve)

    override_cmd = sub.add_parser(
        "override", help="Record a human exception for a failed creative score (agents 01, 02, 03, 05 only)"
    )
    override_cmd.add_argument("--prompts", required=True)
    override_cmd.add_argument("--agent", required=True, choices=OVERRIDABLE_AGENTS)
    override_cmd.add_argument("--by", required=True, help="Name of the human accepting the exception")
    override_cmd.add_argument("--at", required=True, help="Timestamp, preferably ISO 8601")
    override_cmd.add_argument("--reason", required=True)
    override_cmd.set_defaults(func=override)

    args = parser.parse_args()
    if args.command == "hash":
        print(sha256(Path(args.prompts).resolve()))
    else:
        args.func(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
