#!/usr/bin/env python3
"""Regression tests for the B1 test-plan.json contract."""

import copy
import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("test_plan", REPO / "04-test-planning" / "test_plan.py")
test_plan = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(test_plan)
TEMPLATE = REPO / "04-test-planning" / "test-plan-template.json"


def planned_template() -> dict:
    data = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    data["status"] = "planned"
    return data


class TestPlanContractTests(unittest.TestCase):
    def test_shipped_template_is_draft_but_valid_once_planned(self):
        self.assertTrue(test_plan.validate_plan_data(json.loads(TEMPLATE.read_text(encoding="utf-8"))))
        self.assertEqual(test_plan.validate_plan_data(planned_template()), [])

    def test_isolated_hook_test_rejects_changed_constants(self):
        data = planned_template()
        data["variants"][1].update({"persona": "iná persona", "angle": "iný angle", "template_number": 2})
        issues = test_plan.validate_plan_data(data)
        self.assertTrue(any("persona" in issue for issue in issues))
        self.assertTrue(any("angle" in issue for issue in issues))
        self.assertTrue(any("template_number" in issue for issue in issues))

    def test_isolated_test_requires_distinct_tested_values(self):
        data = planned_template()
        data["variants"][1]["hook"] = data["variants"][0]["hook"]
        self.assertTrue(any("sa musia líšiť" in issue for issue in test_plan.validate_plan_data(data)))

    def test_isolated_test_needs_two_variants(self):
        data = planned_template()
        data["variants"] = data["variants"][:1]
        self.assertTrue(any("pilot" in issue for issue in test_plan.validate_plan_data(data)))

    def test_concept_comparison_allows_multiple_axes(self):
        data = planned_template()
        data.update({"test_variable": "concept", "test_design": "concept-comparison"})
        data["variants"][1].update({"persona": "iná persona", "angle": "iný angle", "awareness_stage": "solution-aware"})
        self.assertEqual(test_plan.validate_plan_data(data), [])

    def test_pilot_is_a_single_concept(self):
        data = planned_template()
        data.update({"test_variable": "concept", "test_design": "pilot"})
        data["variants"] = data["variants"][:1]
        self.assertEqual(test_plan.validate_plan_data(data), [])

    def test_data_gate_requires_numeric_thresholds(self):
        data = planned_template()
        data["data_gate"]["minimum_impressions_per_variant"] = "8000"
        data["data_gate"]["minimum_events_per_variant"] = {"event": "", "count": 0}
        issues = test_plan.validate_plan_data(data)
        self.assertEqual(len([issue for issue in issues if issue.startswith("data_gate")]), 3)

    def test_learnings_must_be_reviewed_with_reason(self):
        data = planned_template()
        data["learnings"] = {"reviewed": False, "applied": [], "predecessor_plan_id": None, "note": ""}
        issues = test_plan.validate_plan_data(data)
        self.assertTrue(any("learnings.reviewed" in issue for issue in issues))
        self.assertTrue(any("learnings.note" in issue for issue in issues))

    def test_schema_1_plan_stays_valid_with_warning(self):
        data = copy.deepcopy(planned_template())
        data["schema_version"] = 1
        for field in ("test_design", "learnings"):
            data.pop(field)
        data["variants"][1]["persona"] = "iná persona"
        self.assertEqual(test_plan.validate_plan_data(data), [])
        self.assertTrue(test_plan.plan_warnings(data))

    def test_init_creates_schema_2_draft(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                ["python3", str(REPO / "04-test-planning" / "test_plan.py"), "init", "--ad-set", tmp,
                 "--plan-id", "TP-X", "--market", "sk", "--objective", "sales",
                 "--funnel-stage", "TOF", "--test-variable", "hook"],
                check=False, capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            data = json.loads((Path(tmp) / "test-plan.json").read_text(encoding="utf-8"))
        self.assertEqual(data["schema_version"], 2)
        self.assertEqual(data["test_design"], "isolated")
        self.assertIn("learnings", data)


if __name__ == "__main__":
    unittest.main()
