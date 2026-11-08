"""The homework module in the plugin: loading, the rules, scaffolding, approval and status.

Like test_course_lifecycle.py, a throwaway course built by the scaffold (invariant 1). Every rule is
broken on purpose and asserted to fire at its severity, and each has its silent case: homework is
optional (HW-D13), so a course without it — and a scaffolded placeholder — says nothing.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from classkit import approve, status
from classkit.cli import main
from classkit.frontmatter import load
from classkit.model import load_course
from classkit.scaffold import ITEM_FORMATS, scaffold_course, scaffold_homework, scaffold_item, scaffold_unit
from classkit.validate import DEFAULT_SEVERITY, validate

FRAMEWORK_ROOT = Path(__file__).resolve().parents[1] / "plugin"

HOMEWORK_RULES = {
    "homework_item_reference", "homework_unit_reference", "homework_plan_reference",
    "homework_version_reference", "homework_source_quiz_exists", "homework_tools_declared",
    "class_tools_declared", "item_class_declared", "item_class_guide_reference",
    "item_source_resolvable", "homework_defaults_class_reference", "code_execution_reference_present",
    "homework_coverage", "homework_item_usage", "homework_units_declared", "homework_budget_fits",
    "homework_versions_targeted", "graded_requires_rubric", "item_class_bundle_drift",
    "item_class_evaluation_declared", "homework_defaults_consistent",
}


@pytest.fixture
def course_root(tmp_path: Path) -> Path:
    root = tmp_path / "course"
    scaffold_course(root, FRAMEWORK_ROOT, code="TEST-101", title="Test Course",
                    institution="Test University", instructor="", units=13,
                    methodology="question-driven-25")
    scaffold_unit(root, FRAMEWORK_ROOT, 1, "First Unit")
    scaffold_unit(root, FRAMEWORK_ROOT, 2, "Second Unit")
    return root


@pytest.fixture
def hw(course_root: Path) -> Path:
    """A scaffolded homework placeholder for U01, with its configuration files."""
    scaffold_homework(course_root, FRAMEWORK_ROOT, ["U01"])
    return course_root / "assessments" / "homework" / "HW01.md"


def findings(course_root: Path):
    return validate(load_course(course_root, FRAMEWORK_ROOT), FRAMEWORK_ROOT)


def fired(course_root: Path, code: str) -> set[str]:
    """The severities at which `code` fired."""
    return {f.level for f in findings(course_root) if f.code == code}


def homework_findings(course_root: Path) -> list:
    return [f for f in findings(course_root) if f.code in HOMEWORK_RULES]


def errors(course_root: Path) -> list:
    return [f for f in findings(course_root) if f.level == "error"]


def front(path: Path) -> dict:
    return load(path)[0]


def set_front(path: Path, **changes) -> None:
    """Rewrite a file's front matter with `changes` applied (None removes a key)."""
    data, body = load(path)
    for key, value in changes.items():
        if value is None:
            data.pop(key, None)
        else:
            data[key] = value
    path.write_text("---\n" + yaml.safe_dump(data, sort_keys=False, allow_unicode=True) + "---\n" + body,
                    encoding="utf-8")


def new_item(course_root: Path, unit: str = "U01", fmt: str = "multiple-choice",
             item_class: str | None = "DIY", **changes) -> str:
    result = scaffold_item(course_root, FRAMEWORK_ROOT, unit, fmt, item_class)
    path = next(p for p in result.created if p.parent.name == "items")
    if changes:
        set_front(path, **changes)
    return path.stem


def item_path(course_root: Path, item_id: str) -> Path:
    return course_root / "assessments" / "items" / f"{item_id}.md"


def answers_path(course_root: Path, item_id: str) -> Path:
    return course_root / "assessments" / "answers" / f"{item_id}.md"


def config(course_root: Path, name: str) -> Path:
    return course_root / "assessments" / name


def edit_yaml(path: Path, change) -> None:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    change(data)
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def slot(number: int, gq: str = "U01-S01-G1", **extra) -> dict:
    return {"slot": number, "guiding_questions": [gq], "intent": "practise the basics",
            "item_class": "DIY", "format": "multiple-choice", "est_minutes": 3, **extra}


# -- optional, and the templates validate --------------------------------------------

def test_a_course_without_homework_has_no_homework_findings(course_root: Path):
    assert homework_findings(course_root) == []


def test_a_scaffolded_homework_has_no_errors_and_no_homework_findings(course_root: Path, hw: Path):
    assert errors(course_root) == []
    assert homework_findings(course_root) == []


@pytest.mark.parametrize("fmt", ITEM_FORMATS)
def test_every_item_template_validates_with_a_class(course_root: Path, fmt: str):
    new_item(course_root, fmt=fmt, item_class="Practicing" if fmt != "code" else "Coding")
    assert errors(course_root) == []


def test_scaffold_course_does_not_create_the_homework_files(course_root: Path):
    assert not config(course_root, "item-classes.yaml").exists()
    assert list((course_root / "assessments" / "homework").glob("HW*.md")) == []


# -- scaffold homework -------------------------------------------------------------

def test_scaffold_homework_creates_the_placeholder_and_the_configuration(course_root: Path, hw: Path):
    data = front(hw)
    assert data["id"] == "HW01" and data["units"] == ["U01"]
    assert data["items"] == [] and data["plan"] == {"slots": []}
    assert data["total_minutes"] == yaml.safe_load(
        config(course_root, "homework-defaults.yaml").read_text(encoding="utf-8"))["total_minutes"]
    for name in ("item-classes.yaml", "homework-defaults.yaml", "homework-document.yaml"):
        assert config(course_root, name).is_file()
    assert "classkit scaffold homework 1" in (course_root / "LOG.md").read_text(encoding="utf-8")


def test_scaffold_homework_takes_the_next_number_and_never_overwrites(course_root: Path, hw: Path):
    config(course_root, "item-classes.yaml").write_text("MINE: {}\n", encoding="utf-8")
    result = scaffold_homework(course_root, FRAMEWORK_ROOT, ["1", "U02"])
    assert (course_root / "assessments" / "homework" / "HW02.md") in result.created
    assert front(course_root / "assessments" / "homework" / "HW02.md")["units"] == ["U01", "U02"]
    assert config(course_root, "item-classes.yaml").read_text(encoding="utf-8") == "MINE: {}\n"


def test_scaffold_homework_uses_the_teachers_budget(course_root: Path, hw: Path):
    edit_yaml(config(course_root, "homework-defaults.yaml"), lambda d: d.update(total_minutes=120))
    scaffold_homework(course_root, FRAMEWORK_ROOT, ["U01"])
    assert front(course_root / "assessments" / "homework" / "HW02.md")["total_minutes"] == 120


def test_scaffold_item_with_a_class_is_a_homework_item(course_root: Path):
    item_id = new_item(course_root, fmt="numeric", item_class="Practicing")
    data = front(item_path(course_root, item_id))
    assert data["item_class"] == "Practicing" and data["usage"] == ["homework"]
    assert config(course_root, "item-classes.yaml").is_file()


def test_the_cli_scaffolds_a_homework(course_root: Path, monkeypatch, capsys):
    monkeypatch.chdir(course_root)
    assert main(["scaffold", "homework", "--units", "U01", "U02"]) == 0
    assert front(course_root / "assessments" / "homework" / "HW01.md")["units"] == ["U01", "U02"]
    assert main(["scaffold", "item", "U01", "--format", "code", "--class", "Coding"]) == 0
    assert front(item_path(course_root, "U01-I01"))["item_class"] == "Coding"


def test_a_model_answer_replaces_answer(course_root: Path):
    item_id = new_item(course_root, fmt="open", item_class=None)
    data = front(item_path(course_root, item_id))
    assert "model_answer" in data and "answer" not in data
    set_front(item_path(course_root, item_id), answer="old field")
    assert "schema" in {f.code for f in errors(course_root)}


# -- schema and id ------------------------------------------------------------------

def test_a_malformed_homework_fails_the_schema(course_root: Path, hw: Path):
    set_front(hw, purpose="optional")
    assert "error" in fired(course_root, "schema")


def test_an_unreadable_configuration_file_is_a_schema_error_not_a_crash(course_root: Path, hw: Path):
    config(course_root, "item-classes.yaml").write_text("DIY: [unclosed\n", encoding="utf-8")
    found = [f for f in findings(course_root) if f.code == "schema"]
    assert any("cannot be read" in f.message for f in found)


def test_a_configuration_file_that_breaks_its_schema_is_reported(course_root: Path, hw: Path):
    edit_yaml(config(course_root, "homework-document.yaml"), lambda d: d.update(direction="up"))
    assert any(f.code == "schema" and "homework-document.yaml" in f.where for f in errors(course_root))


def test_a_homework_whose_id_differs_from_its_file_is_an_error(course_root: Path, hw: Path):
    set_front(hw, id="HW07")
    assert "error" in fired(course_root, "id_consistency")


# -- references (errors) --------------------------------------------------------------

def test_a_homework_covering_a_unit_that_does_not_exist(course_root: Path, hw: Path):
    set_front(hw, units=["U01", "U09"])
    assert fired(course_root, "homework_unit_reference") == {"error"}


def test_a_homework_listing_an_item_that_does_not_exist(course_root: Path, hw: Path):
    set_front(hw, items=["U01-I09"])
    assert fired(course_root, "homework_item_reference") == {"error"}


def test_item_tools_naming_an_item_outside_the_homework(course_root: Path, hw: Path):
    item_id = new_item(course_root)
    other = new_item(course_root)
    set_front(hw, items=[item_id], item_tools={other: ["pen_and_paper"]})
    assert fired(course_root, "homework_item_reference") == {"error"}


def test_a_slot_built_from_an_item_that_does_not_exist(course_root: Path, hw: Path):
    set_front(hw, plan={"slots": [slot(1, decision="reuse", **{"from": "U01-I42"})]})
    assert fired(course_root, "homework_item_reference") == {"error"}


def test_a_slot_testing_a_guiding_question_that_does_not_exist(course_root: Path, hw: Path):
    set_front(hw, plan={"slots": [slot(1, gq="U01-S09-G1")]})
    assert fired(course_root, "homework_plan_reference") == {"error"}


def test_a_slot_of_a_version_that_does_not_exist(course_root: Path, hw: Path):
    set_front(hw, plan={"slots": [slot(1, version="B")]})
    assert fired(course_root, "homework_plan_reference") == {"error"}


def quiz_homework(course_root: Path, hw: Path, versions: list[dict]) -> None:
    new_item(course_root, item_class=None, usage=["in-class-quiz"])
    set_front(hw, source={"kind": "quiz_report", "ref": "U01"}, versions=versions)


def test_two_versions_with_one_label(course_root: Path, hw: Path):
    quiz_homework(course_root, hw, [{"label": "A", "targets": ["U01-S01-G1"]},
                                    {"label": "A", "targets": ["U01-S01-G2"]}])
    assert fired(course_root, "homework_version_reference") == {"error"}


def test_a_version_targeting_a_guiding_question_that_does_not_exist(course_root: Path, hw: Path):
    quiz_homework(course_root, hw, [{"label": "A", "targets": ["U01-S07-G1"]}])
    assert fired(course_root, "homework_version_reference") == {"error"}


def test_a_quiz_report_from_a_unit_with_no_entry_quiz(course_root: Path, hw: Path):
    set_front(hw, source={"kind": "quiz_report", "ref": "U01"})
    assert fired(course_root, "homework_source_quiz_exists") == {"error"}
    new_item(course_root, item_class=None, usage=["in-class-quiz"])
    assert fired(course_root, "homework_source_quiz_exists") == set()


def test_a_tool_course_yaml_does_not_declare(course_root: Path, hw: Path):
    set_front(hw, allowed_tools=["wireshark"])
    assert fired(course_root, "homework_tools_declared") == {"error"}
    edit_yaml(course_root / "course.yaml",
              lambda d: d["tools"].update(wireshark={"description": "Wireshark"}))
    assert fired(course_root, "homework_tools_declared") == set()


def test_a_slots_tool_is_checked_too(course_root: Path, hw: Path):
    set_front(hw, plan={"slots": [slot(1, tools=["gns3"])]})
    assert fired(course_root, "homework_tools_declared") == {"error"}


def test_a_class_naming_an_undeclared_tool(course_root: Path, hw: Path):
    edit_yaml(config(course_root, "item-classes.yaml"), lambda d: d["DIY"]["default_tools"].append("r"))
    assert fired(course_root, "class_tools_declared") == {"error"}


def test_the_starter_classes_tools_are_declared_in_a_new_course(course_root: Path, hw: Path):
    assert fired(course_root, "class_tools_declared") == set()


def test_an_item_of_a_class_that_does_not_exist(course_root: Path, hw: Path):
    new_item(course_root, item_class="Reading")
    assert fired(course_root, "item_class_declared") == {"error"}


def test_a_slot_of_a_class_that_does_not_exist(course_root: Path, hw: Path):
    set_front(hw, plan={"slots": [slot(1, item_class="Diy")]})  # case-sensitive
    assert fired(course_root, "item_class_declared") == {"error"}


def test_a_class_writing_guide_that_does_not_exist(course_root: Path, hw: Path):
    edit_yaml(config(course_root, "item-classes.yaml"),
              lambda d: d["DIY"].update(writing_guide="assessments/writing-guides/diy.md"))
    assert fired(course_root, "item_class_guide_reference") == {"error"}
    guide = course_root / "assessments" / "writing-guides" / "diy.md"
    guide.parent.mkdir(parents=True)
    guide.write_text("# Writing DIY items\n", encoding="utf-8")
    assert fired(course_root, "item_class_guide_reference") == set()


def test_a_custom_strategy_guide_that_does_not_exist(course_root: Path, hw: Path):
    edit_yaml(config(course_root, "item-classes.yaml"), lambda d: d["Research"].update(
        evaluation={"strategy": "custom", "custom_guide": "assessments/writing-guides/check.md"}))
    assert fired(course_root, "item_class_guide_reference") == {"error"}


def test_an_adapted_item_whose_original_does_not_exist(course_root: Path):
    new_item(course_root, source_ref="U01-I30")
    assert fired(course_root, "item_source_resolvable") == {"error"}


def test_an_autograded_code_item_with_nothing_to_run(course_root: Path):
    item_id = new_item(course_root, fmt="code", item_class="Coding")
    assert fired(course_root, "code_execution_reference_present") == set()
    set_front(answers_path(course_root, item_id), tests=None)
    assert fired(course_root, "code_execution_reference_present") == {"error"}
    set_front(item_path(course_root, item_id), evaluation_strategy="persona_attempt")
    assert fired(course_root, "code_execution_reference_present") == set()


def test_defaults_counting_a_class_that_does_not_exist(course_root: Path, hw: Path):
    edit_yaml(config(course_root, "homework-defaults.yaml"),
              lambda d: d["default_class_counts"].update(Reading=1))
    assert fired(course_root, "homework_defaults_class_reference") == {"error"}


# -- advisory ------------------------------------------------------------------------

def test_a_unit_no_item_tests_is_an_alert(course_root: Path, hw: Path):
    item_id = new_item(course_root)
    set_front(hw, units=["U01", "U02"], items=[item_id])
    assert fired(course_root, "homework_coverage") == {"alert"}


def test_a_unit_no_planned_slot_tests_is_an_alert_before_the_build(course_root: Path, hw: Path):
    set_front(hw, units=["U01", "U02"], plan={"slots": [slot(1)]})
    assert fired(course_root, "homework_coverage") == {"alert"}
    set_front(hw, plan={"slots": [slot(1), slot(2, gq="U02-S01-G1")]})
    assert fired(course_root, "homework_coverage") == set()


def test_an_item_without_homework_in_its_usage_warns(course_root: Path, hw: Path):
    item_id = new_item(course_root, item_class=None)  # usage: [in-class-quiz]
    set_front(hw, items=[item_id])
    assert fired(course_root, "homework_item_usage") == {"warn"}


def test_an_item_from_another_unit_warns(course_root: Path, hw: Path):
    item_id = new_item(course_root, unit="U02", guiding_questions=["U02-S01-G1"])
    set_front(hw, items=[item_id])
    assert fired(course_root, "homework_units_declared") == {"warn"}


def test_a_slot_from_another_unit_warns(course_root: Path, hw: Path):
    set_front(hw, plan={"slots": [slot(1), slot(2, gq="U02-S01-G1")]})
    assert fired(course_root, "homework_units_declared") == {"warn"}


def test_items_far_from_the_budget_warn(course_root: Path, hw: Path):
    items = [new_item(course_root), new_item(course_root)]  # DIY, 2 minutes each
    set_front(hw, items=items, total_minutes=90)
    assert fired(course_root, "homework_budget_fits") == {"warn"}
    set_front(hw, total_minutes=10)
    assert fired(course_root, "homework_budget_fits") == set()


def test_an_item_without_minutes_counts_its_class_midpoint(course_root: Path, hw: Path):
    item_id = new_item(course_root, fmt="code", item_class="Coding")  # no est_minutes; 30–90
    set_front(hw, items=[item_id], total_minutes=60)
    assert fired(course_root, "homework_budget_fits") == set()


def test_the_budget_of_a_plan_is_judged_before_the_build(course_root: Path, hw: Path):
    set_front(hw, plan={"slots": [slot(1)]}, total_minutes=90)
    assert fired(course_root, "homework_budget_fits") == {"warn"}


def test_the_teachers_tolerance_is_used(course_root: Path, hw: Path):
    items = [new_item(course_root), new_item(course_root)]
    set_front(hw, items=items, total_minutes=30)
    assert fired(course_root, "homework_budget_fits") == {"warn"}
    edit_yaml(config(course_root, "homework-defaults.yaml"), lambda d: d.update(budget_tolerance_minutes=30))
    assert fired(course_root, "homework_budget_fits") == set()


def versioned(course_root: Path, hw: Path, version_items: list[str], targets: list[str],
              shared: list[str] | None = None) -> None:
    new_item(course_root, item_class=None, usage=["in-class-quiz"])
    set_front(hw, source={"kind": "quiz_report", "ref": "U01"}, items=shared or [],
              versions=[{"label": "A", "targets": targets, "items": version_items}], total_minutes=5)


def test_a_valid_targeted_version_is_silent(course_root: Path, hw: Path):
    item_id = new_item(course_root, guiding_questions=["U01-S01-G2"])
    versioned(course_root, hw, [item_id], ["U01-S01-G2"])
    assert fired(course_root, "homework_versions_targeted") == set()


def test_a_version_item_testing_none_of_its_targets_warns(course_root: Path, hw: Path):
    item_id = new_item(course_root, guiding_questions=["U01-S01-G3"])
    versioned(course_root, hw, [item_id], ["U01-S01-G2"])
    assert fired(course_root, "homework_versions_targeted") == {"warn"}


def test_a_target_none_of_the_versions_items_tests_warns(course_root: Path, hw: Path):
    item_id = new_item(course_root, guiding_questions=["U01-S01-G2"])
    versioned(course_root, hw, [item_id], ["U01-S01-G2", "U01-S02-G1"])
    messages = [f.message for f in findings(course_root) if f.code == "homework_versions_targeted"]
    assert len(messages) == 1 and messages[0].startswith("U01-S02-G1")


def test_an_item_both_shared_and_in_a_version_warns(course_root: Path, hw: Path):
    item_id = new_item(course_root, guiding_questions=["U01-S01-G2"])
    versioned(course_root, hw, [item_id], ["U01-S01-G2"], shared=[item_id])
    assert fired(course_root, "homework_versions_targeted") == {"warn"}


def test_a_target_outside_the_homeworks_units_warns(course_root: Path, hw: Path):
    versioned(course_root, hw, [], ["U02-S01-G1"])
    assert fired(course_root, "homework_versions_targeted") == {"warn"}


def test_a_graded_homeworks_code_item_without_a_rubric_warns(course_root: Path, hw: Path):
    item_id = new_item(course_root, fmt="code", item_class="Coding")
    set_front(answers_path(course_root, item_id), rubric=None)
    set_front(hw, items=[item_id], total_minutes=60)
    assert fired(course_root, "graded_requires_rubric") == set()  # practice
    set_front(hw, purpose="graded")
    assert fired(course_root, "graded_requires_rubric") == {"warn"}


def test_an_item_outside_its_class_drifts(course_root: Path, hw: Path):
    item_id = new_item(course_root, bloom="create")
    assert fired(course_root, "item_class_bundle_drift") == {"warn"}
    set_front(item_path(course_root, item_id), bloom="understand", est_minutes=30)
    assert fired(course_root, "item_class_bundle_drift") == {"warn"}
    set_front(item_path(course_root, item_id), est_minutes=3)
    assert fired(course_root, "item_class_bundle_drift") == set()


def test_a_class_that_does_not_say_how_it_is_checked_warns(course_root: Path, hw: Path):
    edit_yaml(config(course_root, "item-classes.yaml"), lambda d: d["DIY"].pop("evaluation"))
    assert fired(course_root, "item_class_evaluation_declared") == {"warn"}


def test_defaults_with_no_positive_count_warn(course_root: Path, hw: Path):
    edit_yaml(config(course_root, "homework-defaults.yaml"),
              lambda d: d.update(default_class_counts={k: 0 for k in d["default_class_counts"]}))
    assert fired(course_root, "homework_defaults_consistent") == {"warn"}


def test_defaults_that_do_not_fit_their_budget_warn(course_root: Path, hw: Path):
    assert fired(course_root, "homework_defaults_consistent") == set()
    edit_yaml(config(course_root, "homework-defaults.yaml"), lambda d: d.update(total_minutes=300))
    assert fired(course_root, "homework_defaults_consistent") == {"warn"}


# -- the teacher's authority -----------------------------------------------------------

def test_a_homework_may_accept_an_exception(course_root: Path, hw: Path):
    item_id = new_item(course_root)
    set_front(hw, units=["U01", "U02"], items=[item_id],
              accepted=[{"rule": "homework_coverage", "reason": "U02 is next week's homework"}])
    assert fired(course_root, "homework_coverage") == set()


def test_the_course_can_switch_a_homework_rule_off(course_root: Path, hw: Path):
    edit_yaml(course_root / "course.yaml", lambda d: d.update(rules={"homework_unit_reference": "off"}))
    set_front(hw, units=["U09"])
    assert fired(course_root, "homework_unit_reference") == set()


def test_every_homework_rule_is_registered():
    assert HOMEWORK_RULES <= set(DEFAULT_SEVERITY)


def test_a_homework_finding_names_the_item_it_is_about(course_root: Path, hw: Path):
    set_front(hw, items=["U01-I09"])
    found = next(f for f in findings(course_root) if f.code == "homework_item_reference")
    assert found.item == "U01-I09"


# -- approval and status ---------------------------------------------------------------

def planned_homework(course_root: Path, hw: Path) -> None:
    set_front(hw, plan={"slots": [slot(1), slot(2, gq="U01-S01-G2")]}, total_minutes=6)
    approve.approve_homework(course_root, 1, stage="planned", on="2026-11-07")


def build(course_root: Path, hw: Path) -> list[str]:
    items = [new_item(course_root), new_item(course_root, guiding_questions=["U01-S01-G2"])]
    data = front(hw)
    for entry, item_id in zip(data["plan"]["slots"], items):
        entry["item"] = item_id
    set_front(hw, plan=data["plan"], items=items)
    return items


def line(course_root: Path) -> status.HomeworkLine:
    return status.homework_lines(course_root)[0]


def test_a_homework_needs_a_stage_to_be_approved(course_root: Path, hw: Path):
    with pytest.raises(approve.ApproveError, match="which stage"):
        approve.approve_homework(course_root, 1)


def test_approving_a_homework_that_does_not_exist(course_root: Path):
    with pytest.raises(approve.ApproveError, match="plan-homework"):
        approve.approve_homework(course_root, 4, stage="planned")


def test_approving_the_plan_records_and_logs_it(course_root: Path, hw: Path):
    planned_homework(course_root, hw)
    record = front(hw)["approved"]
    assert record["stage"] == "planned" and str(record["date"]) == "2026-11-07"
    assert "classkit approve homework 1" in (course_root / "LOG.md").read_text(encoding="utf-8")
    assert line(course_root).detail == "planned 2026-11-07"


def test_building_does_not_make_the_plan_edited_since(course_root: Path, hw: Path):
    planned_homework(course_root, hw)
    build(course_root, hw)
    found = line(course_root)
    assert found.state == "planned" and not found.edited
    assert "items written, not yet approved as built" in found.detail


def test_changing_the_plan_makes_it_edited_since(course_root: Path, hw: Path):
    planned_homework(course_root, hw)
    set_front(hw, total_minutes=8)
    assert line(course_root).edited


def test_the_built_hash_covers_the_items(course_root: Path, hw: Path):
    planned_homework(course_root, hw)
    items = build(course_root, hw)
    approve.approve_homework(course_root, 1, stage="built", on="2026-11-08")
    assert line(course_root).detail == "built 2026-11-08"
    set_front(item_path(course_root, items[0]), stem="A reworded stem")
    assert line(course_root).detail == "built 2026-11-08 — edited since"
    assert errors(course_root) == []


def test_approving_again_unchanged_records_nothing(course_root: Path, hw: Path):
    planned_homework(course_root, hw)
    again = approve.approve_homework(course_root, 1, stage="planned", on="2026-11-09")
    assert again.already


def test_status_reports_homework_only_when_there_is_some(course_root: Path):
    assert "Homework" not in status.report(status.status(course_root, FRAMEWORK_ROOT))
    scaffold_homework(course_root, FRAMEWORK_ROOT, ["U01"])
    report = status.report(status.status(course_root, FRAMEWORK_ROOT))
    assert "HW01  U01  drafted, not approved" in report
    assert "HW01: still placeholder" in report


def test_the_cli_approves_a_homework(course_root: Path, hw: Path, capsys):
    set_front(hw, plan={"slots": [slot(1)]})
    assert main(["approve", "homework", "1", "--course", str(course_root)]) == 2
    assert main(["approve", "homework", "1", "--stage", "planned", "--course", str(course_root)]) == 0
    assert "as planned" in capsys.readouterr().out


# -- the independent review's findings ---------------------------------------------------

def test_a_versioned_homeworks_shared_part_is_not_judged_alone(course_root: Path, hw: Path):
    new_item(course_root, item_class=None, usage=["in-class-quiz"])
    coding = {"item_class": "Coding", "format": "code"}
    set_front(hw, source={"kind": "quiz_report", "ref": "U01"}, total_minutes=90,
              versions=[{"label": "A", "targets": ["U01-S01-G1"]}, {"label": "B", "targets": ["U01-S01-G2"]}],
              plan={"slots": [slot(1, item_class="Practicing", format="open", est_minutes=15),
                              slot(2, item_class="Practicing", format="open", est_minutes=15),
                              {**slot(3, version="A"), **coding, "est_minutes": 60},
                              {**slot(4, gq="U01-S01-G2", version="B"), **coding, "est_minutes": 60}]})
    assert fired(course_root, "homework_budget_fits") == set()


def test_an_item_class_that_is_not_a_string_is_a_schema_error_not_a_crash(course_root: Path, hw: Path):
    set_front(hw, plan={"slots": [slot(1, item_class=["DIY"])]})
    item_id = new_item(course_root, fmt="code", item_class="Coding")
    set_front(item_path(course_root, item_id), item_class=["Coding"])
    assert "schema" in {f.code for f in errors(course_root)}


def test_an_item_written_with_the_old_answer_field_still_validates(course_root: Path):
    item_id = new_item(course_root, fmt="open", item_class=None)
    data = front(item_path(course_root, item_id))
    set_front(item_path(course_root, item_id), model_answer=None, answer=data["model_answer"])
    assert errors(course_root) == []


def test_an_unquoted_due_date_is_read_as_a_date(course_root: Path, hw: Path):
    hw.write_text(hw.read_text(encoding="utf-8").replace("# due_date: 2026-11-15", "due_date: 2026-11-15"),
                  encoding="utf-8")
    assert errors(course_root) == []


def test_an_older_course_without_tools_is_told_which_to_declare(course_root: Path, monkeypatch, capsys):
    edit_yaml(course_root / "course.yaml", lambda d: d.pop("tools"))
    monkeypatch.chdir(course_root)
    assert main(["scaffold", "homework", "--units", "U01"]) == 0
    assert "pen_and_paper" in capsys.readouterr().out
    assert {f.code for f in errors(course_root)} == {"class_tools_declared"}  # the placeholder adds none


def test_an_unreadable_item_classes_file_is_one_finding_not_a_cascade(course_root: Path, hw: Path):
    new_item(course_root)
    config(course_root, "item-classes.yaml").write_text("DIY: [unclosed\n", encoding="utf-8")
    codes = [f.code for f in errors(course_root)]
    assert "item_class_declared" not in codes and "homework_defaults_class_reference" not in codes
    assert codes.count("schema") == 1


def test_two_slots_with_one_number(course_root: Path, hw: Path):
    set_front(hw, plan={"slots": [slot(1), slot(1, gq="U01-S01-G2")]})
    assert fired(course_root, "homework_plan_reference") == {"error"}


def test_a_file_that_only_starts_with_hw_is_not_a_homework(course_root: Path, hw: Path):
    (hw.parent / "HW-notes.md").write_text("just notes\n", encoding="utf-8")
    (hw.parent / "HW01 copy.md").write_text(hw.read_text(encoding="utf-8"), encoding="utf-8")
    assert [d.path.name for d in load_course(course_root, FRAMEWORK_ROOT).homework] == ["HW01.md"]


def test_scaffold_item_with_a_class_logs_the_configuration_and_fits_its_class(course_root: Path):
    new_item(course_root, fmt="numeric", item_class="DIY")  # the template says 5 min; DIY is 2–4
    new_item(course_root, fmt="open", item_class="DIY")     # the template says analyze, 10 min
    assert fired(course_root, "item_class_bundle_drift") == set()
    assert "the homework's configuration created" in (course_root / "LOG.md").read_text(encoding="utf-8")


def test_a_guide_outside_the_course_is_an_error(course_root: Path, hw: Path):
    outside = course_root.parent / "guide.md"
    outside.write_text("# not in the course\n", encoding="utf-8")
    edit_yaml(config(course_root, "item-classes.yaml"), lambda d: d["DIY"].update(writing_guide="../guide.md"))
    assert fired(course_root, "item_class_guide_reference") == {"error"}


# -- answers kept out of git (HW-D35) ----------------------------------------------------

def test_a_homework_items_answers_are_scaffolded_apart_from_its_question(course_root: Path):
    item_id = new_item(course_root, fmt="multiple-choice")
    question = front(item_path(course_root, item_id))
    answers = front(answers_path(course_root, item_id))
    assert all(set(c) == {"label", "text"} for c in question["choices"])
    assert answers["correct"] == ["A"] and set(answers["rationales"]) == {"A", "B", "C", "D"}
    code = new_item(course_root, fmt="code", item_class="Coding")
    assert not {"rubric", "expected_solution", "tests"} & set(front(item_path(course_root, code)))
    assert {"rubric", "expected_solution", "tests"} <= set(front(answers_path(course_root, code)))
    assert fired(course_root, "homework_answers_committed") == set()
    assert errors(course_root) == []


def test_a_new_courses_gitignore_keeps_answers_out_of_git(course_root: Path):
    assert "assessments/answers/" in (course_root / ".gitignore").read_text(encoding="utf-8").splitlines()


def test_answers_in_a_homework_items_committed_file_warn(course_root: Path):
    item_id = new_item(course_root, fmt="open")
    set_front(item_path(course_root, item_id), model_answer="The answer, in git")
    assert fired(course_root, "homework_answers_committed") == {"warn"}


def test_a_marked_choice_in_a_homework_item_warns(course_root: Path):
    item_id = new_item(course_root)
    data = front(item_path(course_root, item_id))
    data["choices"][0]["correct"] = True
    set_front(item_path(course_root, item_id), choices=data["choices"])
    assert fired(course_root, "homework_answers_committed") == {"warn"}


def test_an_entry_quiz_item_keeps_its_answers_in_its_file(course_root: Path):
    new_item(course_root, item_class=None, usage=["in-class-quiz", "homework"])
    assert fired(course_root, "homework_answers_committed") == set()
    assert errors(course_root) == []


def test_answers_to_an_item_that_does_not_exist(course_root: Path):
    item_id = new_item(course_root)
    answers_path(course_root, item_id).rename(answers_path(course_root, "U01-I09"))
    set_front(answers_path(course_root, "U01-I09"), id="U01-I09")
    assert fired(course_root, "homework_answers_reference") == {"error"}


def test_answers_naming_a_choice_the_item_does_not_have(course_root: Path):
    item_id = new_item(course_root)
    set_front(answers_path(course_root, item_id), correct=["E"])
    assert fired(course_root, "homework_answers_reference") == {"error"}


def test_a_malformed_answers_file_fails_the_schema(course_root: Path):
    item_id = new_item(course_root)
    set_front(answers_path(course_root, item_id), correct="A")
    assert any(f.code == "schema" and "answers" in f.where for f in errors(course_root))


def test_answers_not_on_this_computer_are_not_a_course_finding(course_root: Path, hw: Path):
    item_id = new_item(course_root, fmt="code", item_class="Coding")
    set_front(hw, items=[item_id], purpose="graded", total_minutes=60)
    answers_path(course_root, item_id).unlink()
    codes = {f.code for f in findings(course_root)}
    assert not {"code_execution_reference_present", "graded_requires_rubric"} & codes
    from classkit import doctor
    notes = [line.what for line in doctor.check_homework_answers(course_root)]
    assert len(notes) == 1 and item_id in notes[0]


def test_a_gitignore_without_the_answers_rule_warns_once_there_is_homework(course_root: Path):
    path = course_root / ".gitignore"
    path.write_text(path.read_text(encoding="utf-8").replace("assessments/answers/\n", ""), encoding="utf-8")
    assert fired(course_root, "course_gitignore_missing") == set()  # no homework yet
    new_item(course_root)
    assert fired(course_root, "course_gitignore_missing") == {"warn"}


def test_git_tracking_an_answers_file_warns(course_root: Path):
    import subprocess
    item_id = new_item(course_root)
    run = lambda *a: subprocess.run(["git", *a], cwd=course_root, check=True, capture_output=True)  # noqa: E731
    run("init", "-q")
    run("add", "-f", f"assessments/answers/{item_id}.md")
    assert fired(course_root, "homework_answers_committed") == {"warn"}



# -- what the first real run found (2026-11-08) ------------------------------------------

def test_the_document_settings_start_from_the_course(course_root: Path, hw: Path):
    settings = yaml.safe_load(config(course_root, "homework-document.yaml").read_text(encoding="utf-8"))
    assert settings["course_title"] == "Test Course"
    assert (settings["language"], settings["direction"], settings["font"]) == ("en", "ltr", "Calibri")
    assert errors(course_root) == []


def test_a_hebrew_course_gets_right_to_left_documents(course_root: Path):
    edit_yaml(course_root / "course.yaml", lambda d: d.update(language="he"))
    scaffold_homework(course_root, FRAMEWORK_ROOT, ["U01"])
    settings = yaml.safe_load(config(course_root, "homework-document.yaml").read_text(encoding="utf-8"))
    assert (settings["language"], settings["direction"], settings["font"]) == ("he", "rtl", "David")


def test_a_slot_outside_its_class_is_seen_at_the_plan(course_root: Path, hw: Path):
    set_front(hw, plan={"slots": [slot(1, est_minutes=5)]})  # DIY is 2–4 minutes
    found = [f for f in findings(course_root) if f.code == "item_class_bundle_drift"]
    assert {f.level for f in found} == {"warn"} and "slot 1" in found[0].message
    set_front(hw, plan={"slots": [slot(1, bloom="create")]})
    assert fired(course_root, "item_class_bundle_drift") == {"warn"}
    set_front(hw, plan={"slots": [slot(1)]})
    assert fired(course_root, "item_class_bundle_drift") == set()
