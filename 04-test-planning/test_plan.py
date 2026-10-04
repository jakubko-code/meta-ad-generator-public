#!/usr/bin/env python3
"""Create and validate the upstream B1 test plan for a creative ad set."""

import argparse
import hashlib
import json
from pathlib import Path


ALLOWED_AWARENESS_STAGES = {
    "unaware",
    "problem-aware",
    "solution-aware",
    "product-aware",
    "most-aware",
}

ALLOWED_TEST_VARIABLES = {
    "concept",
    "hook",
    "angle",
    "format",
    "copy",
    "offer",
    "visual",
}

CURRENT_SCHEMA_VERSION = 2
SUPPORTED_SCHEMA_VERSIONS = {1, 2}

# isolated = mení sa jedna os; concept-comparison = porovnanie celých konceptov;
# pilot = jeden koncept bez porovnania (verdikt je vždy iba predbežný).
ALLOWED_TEST_DESIGNS = {"isolated", "concept-comparison", "pilot"}

# Pri izolovanom teste musia tieto polia variantov zostať rovnaké. Testovaná
# premenná sama je vo variante pole s rovnakým názvom a musí sa medzi variantmi líšiť.
ISOLATION_CONSTANTS = {
    "hook": ("persona", "awareness_stage", "angle", "format", "template_number"),
    "angle": ("persona", "awareness_stage", "format", "template_number"),
    "format": ("persona", "awareness_stage", "angle", "hook"),
    "visual": ("persona", "awareness_stage", "angle", "hook", "format"),
    "copy": ("persona", "awareness_stage", "angle", "hook", "format", "template_number"),
    "offer": ("persona", "awareness_stage", "angle", "format", "template_number"),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_plan_data(data: dict) -> list[str]:
    issues = []
    if not isinstance(data, dict):
        return ["test-plan.json musí obsahovať JSON objekt"]

    schema_version = data.get("schema_version")
    if schema_version not in SUPPORTED_SCHEMA_VERSIONS:
        issues.append(f"schema_version musí byť {CURRENT_SCHEMA_VERSION} (starší plán 1)")
    if str(data.get("status", "")).lower() != "planned":
        issues.append("status musí byť 'planned'")

    required_strings = (
        "plan_id",
        "market",
        "campaign_objective",
        "funnel_stage",
        "test_question",
        "hypothesis",
        "test_variable",
        "test_method",
        "primary_metric",
    )
    for field in required_strings:
        value = data.get(field)
        if not isinstance(value, str) or not value.strip():
            issues.append(f"{field} je povinný neprázdny text")

    test_variable = str(data.get("test_variable", "")).lower()
    if test_variable and test_variable not in ALLOWED_TEST_VARIABLES:
        allowed = ", ".join(sorted(ALLOWED_TEST_VARIABLES))
        issues.append(f"test_variable musí byť jedna z hodnôt: {allowed}")

    constants = data.get("constants")
    if not isinstance(constants, list) or not constants or not all(
        isinstance(item, str) and item.strip() for item in constants
    ):
        issues.append("constants musí byť neprázdny zoznam textových konštánt")

    data_gate = data.get("data_gate")
    if not isinstance(data_gate, dict):
        issues.append("data_gate musí byť objekt")
    else:
        for field in ("minimum_runtime", "minimum_evidence"):
            value = data_gate.get(field)
            if not isinstance(value, str) or not value.strip():
                issues.append(f"data_gate.{field} je povinný neprázdny text")

    variants = data.get("variants")
    if not isinstance(variants, list) or not variants:
        issues.append("variants musí obsahovať aspoň jeden koncept")
        return issues

    seen = set()
    required_variant_strings = (
        "concept_id",
        "brief_id",
        "persona",
        "awareness_stage",
        "angle",
        "hook",
        "format",
    )
    for index, variant in enumerate(variants):
        prefix = f"variants[{index}]"
        if not isinstance(variant, dict):
            issues.append(f"{prefix} musí byť objekt")
            continue
        for field in required_variant_strings:
            value = variant.get(field)
            if not isinstance(value, str) or not value.strip():
                issues.append(f"{prefix}.{field} je povinný neprázdny text")
        concept_id = str(variant.get("concept_id", "")).strip()
        if concept_id:
            if concept_id in seen:
                issues.append(f"{prefix}.concept_id '{concept_id}' je duplicitný")
            seen.add(concept_id)
        awareness = str(variant.get("awareness_stage", "")).lower()
        if awareness and awareness not in ALLOWED_AWARENESS_STAGES:
            allowed = ", ".join(sorted(ALLOWED_AWARENESS_STAGES))
            issues.append(f"{prefix}.awareness_stage musí byť jedna z hodnôt: {allowed}")
        template_number = variant.get("template_number")
        if template_number is not None and (
            isinstance(template_number, bool) or not isinstance(template_number, int)
        ):
            issues.append(f"{prefix}.template_number musí byť číslo alebo sa vynechá")

    if schema_version == 2:
        issues.extend(validate_schema_v2(data, test_variable, variants))
    return issues


def is_positive_int(value) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 1


def validate_schema_v2(data: dict, test_variable: str, variants: list) -> list[str]:
    """Machine-checkable experiment contract: design, isolation, numeric data gate, learnings."""
    issues = []
    design = str(data.get("test_design", "")).lower()
    if design not in ALLOWED_TEST_DESIGNS:
        allowed = ", ".join(sorted(ALLOWED_TEST_DESIGNS))
        issues.append(f"test_design musí byť jedna z hodnôt: {allowed}")

    data_gate = data.get("data_gate")
    if isinstance(data_gate, dict):
        for field in ("minimum_days", "minimum_impressions_per_variant"):
            if not is_positive_int(data_gate.get(field)):
                issues.append(f"data_gate.{field} musí byť celé číslo >= 1")
        events = data_gate.get("minimum_events_per_variant")
        if not isinstance(events, dict):
            issues.append("data_gate.minimum_events_per_variant musí byť objekt {event, count}")
        else:
            if not isinstance(events.get("event"), str) or not events["event"].strip():
                issues.append("data_gate.minimum_events_per_variant.event je povinný text (napr. outbound_clicks)")
            if not is_positive_int(events.get("count")):
                issues.append("data_gate.minimum_events_per_variant.count musí byť celé číslo >= 1")

    learnings = data.get("learnings")
    if not isinstance(learnings, dict):
        issues.append("learnings musí byť objekt {reviewed, applied, predecessor_plan_id, note}")
    else:
        if learnings.get("reviewed") is not True:
            issues.append("learnings.reviewed musí byť true — pred plánom načítaj testing/learnings.md")
        applied = learnings.get("applied")
        if not isinstance(applied, list) or not all(isinstance(item, str) and item.strip() for item in applied):
            issues.append("learnings.applied musí byť zoznam learning ID (môže byť prázdny)")
        predecessor = learnings.get("predecessor_plan_id")
        if predecessor is not None and (not isinstance(predecessor, str) or not predecessor.strip()):
            issues.append("learnings.predecessor_plan_id musí byť plan_id alebo null")
        if not isinstance(learnings.get("note"), str) or not learnings["note"].strip():
            issues.append("learnings.note je povinný text: prečo tento test a čo z learnings vyplýva")

    valid_variants = [variant for variant in variants if isinstance(variant, dict)]
    if design == "pilot":
        if len(valid_variants) != 1:
            issues.append("test_design 'pilot' má presne jeden variant; viac variantov je porovnanie")
        if test_variable != "concept":
            issues.append("test_design 'pilot' používa test_variable 'concept'")
    elif design == "concept-comparison":
        if len(valid_variants) < 2:
            issues.append("test_design 'concept-comparison' potrebuje aspoň dva varianty")
        if test_variable != "concept":
            issues.append("test_design 'concept-comparison' používa test_variable 'concept'")
    elif design == "isolated":
        if test_variable == "concept":
            issues.append("izolovaný test nemôže mať test_variable 'concept'; použi concept-comparison")
        elif len(valid_variants) < 2:
            issues.append("izolovaný test potrebuje aspoň dva varianty; jeden koncept je 'pilot'")
        elif test_variable in ISOLATION_CONSTANTS:
            issues.extend(validate_isolation(test_variable, valid_variants))
    return issues


def validate_isolation(test_variable: str, variants: list) -> list[str]:
    issues = []
    baseline = variants[0]
    for field in ISOLATION_CONSTANTS[test_variable]:
        differing = [
            str(variant.get("concept_id", index))
            for index, variant in enumerate(variants)
            if variant.get(field) != baseline.get(field)
        ]
        if differing:
            issues.append(
                f"izolovaný test '{test_variable}': variants[].{field} musí byť rovnaké; "
                f"líši sa pri {', '.join(differing)}. Ak sa má meniť viac osí, je to concept-comparison."
            )
    values = [variant.get(test_variable) for variant in variants]
    if any(not isinstance(value, str) or not value.strip() for value in values):
        issues.append(f"izolovaný test '{test_variable}': každý variant musí mať neprázdne pole {test_variable}")
    elif len({value.strip() for value in values}) != len(values):
        issues.append(f"izolovaný test '{test_variable}': hodnoty variants[].{test_variable} sa musia líšiť")
    return issues


def plan_warnings(data: dict) -> list[str]:
    if isinstance(data, dict) and data.get("schema_version") == 1:
        return [
            "test-plan.json má schema_version 1: izolácia premennej, číselná dátová brána "
            "a learnings sa strojovo nekontrolujú. Nový plán vytvor cez init (schema 2)."
        ]
    return []


def load_and_validate(path: Path) -> tuple[dict, list[str]]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}, [f"chýba {path.name}"]
    except (OSError, json.JSONDecodeError) as exc:
        return {}, [f"neplatný {path.name}: {exc}"]
    return data, validate_plan_data(data)


def initial_plan(args) -> dict:
    return {
        "schema_version": CURRENT_SCHEMA_VERSION,
        "status": "draft",
        "plan_id": args.plan_id,
        "market": args.market.lower(),
        "campaign_objective": args.objective,
        "funnel_stage": args.funnel_stage,
        "test_question": "",
        "hypothesis": "",
        "test_variable": args.test_variable,
        "test_design": "concept-comparison" if args.test_variable == "concept" else "isolated",
        "test_method": "",
        "primary_metric": "",
        "constants": [],
        "data_gate": {
            "minimum_runtime": "",
            "minimum_evidence": "",
            "minimum_days": None,
            "minimum_impressions_per_variant": None,
            "minimum_events_per_variant": {"event": "", "count": None},
        },
        "learnings": {
            "reviewed": False,
            "applied": [],
            "predecessor_plan_id": None,
            "note": "",
        },
        "variants": [
            {
                "concept_id": "C01",
                "brief_id": "B01",
                "persona": "",
                "awareness_stage": "",
                "angle": "",
                "hook": "",
                "format": "",
            }
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Manage the B1 test-plan.json contract")
    sub = parser.add_subparsers(dest="command", required=True)

    init_cmd = sub.add_parser("init", help="Create a draft test-plan.json in an ad set")
    init_cmd.add_argument("--ad-set", required=True)
    init_cmd.add_argument("--plan-id", required=True)
    init_cmd.add_argument("--market", required=True)
    init_cmd.add_argument("--objective", required=True)
    init_cmd.add_argument("--funnel-stage", required=True)
    init_cmd.add_argument("--test-variable", choices=sorted(ALLOWED_TEST_VARIABLES), required=True)
    init_cmd.add_argument("--force", action="store_true")

    validate_cmd = sub.add_parser("validate", help="Validate a completed test-plan.json")
    validate_cmd.add_argument("--plan", required=True)

    hash_cmd = sub.add_parser("hash", help="Print SHA-256 of an exact test-plan.json")
    hash_cmd.add_argument("--plan", required=True)

    bind_cmd = sub.add_parser("bind", help="Bind prompts JSON to a valid test-plan.json")
    bind_cmd.add_argument("--prompts", required=True)
    bind_cmd.add_argument("--plan", help="Defaults to test-plan.json beside prompts")

    args = parser.parse_args()
    if args.command == "init":
        ad_set = Path(args.ad_set).resolve()
        ad_set.mkdir(parents=True, exist_ok=True)
        path = ad_set / "test-plan.json"
        if path.exists() and not args.force:
            raise SystemExit(f"Refusing to overwrite {path}. Use --force only after reviewing it.")
        path.write_text(
            json.dumps(initial_plan(args), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(path)
        print("Draft created. Complete every field, set status to 'planned', then run validate.")
        return 0
    if args.command == "hash":
        print(sha256(Path(args.plan).resolve()))
        return 0
    if args.command == "bind":
        prompts_path = Path(args.prompts).resolve()
        plan_path = Path(args.plan).resolve() if args.plan else prompts_path.with_name("test-plan.json")
        plan, issues = load_and_validate(plan_path)
        if issues:
            for issue in issues:
                print(f"✗ {issue}")
            return 1
        try:
            prompts = json.loads(prompts_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            print(f"✗ neplatný {prompts_path.name}: {exc}")
            return 1
        if not isinstance(prompts, dict):
            print(f"✗ {prompts_path.name} musí obsahovať JSON objekt")
            return 1
        prompts["workflow_version"] = 2
        prompts["test_plan"] = {
            "id": plan["plan_id"],
            "sha256": sha256(plan_path),
        }
        prompts_path.write_text(
            json.dumps(prompts, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(prompts_path)
        contract_issues = prompts_contract_issues(prompts, prompts_path)
        if contract_issues:
            print("Väzba je zapísaná, ale prompty ešte nesedia s plánom:")
            for issue in contract_issues:
                print(f"  {issue}")
            return 1
        print("Kontrakt plán ↔ prompty sedí (koncepty, brief polia, hook ↔ renderované pole).")
        return 0

    path = Path(args.plan).resolve()
    data, issues = load_and_validate(path)
    if issues:
        for issue in issues:
            print(f"✗ {issue}")
        return 1
    for warning in plan_warnings(data):
        print(f"⚠ {warning}")
    print(f"VALID — {path}")
    return 0


def prompts_contract_issues(prompts: dict, prompts_path: Path) -> list[str]:
    """Run the generator's plan ↔ prompts contract right after binding (lazy import, no API)."""
    import importlib.util

    module_path = Path(__file__).resolve().parent.parent / "07-image-generation" / "generate_ads.py"
    spec = importlib.util.spec_from_file_location("generate_ads_contract", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.validate_strategy_contract(prompts, prompts_path)


if __name__ == "__main__":
    raise SystemExit(main())
