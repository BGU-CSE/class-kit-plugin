"""A teacher's own methodology, kept in the course (plugin migration, Phase 4; assessment §6.5).

In the framework, a teacher added a file to `methodologies/` in their own clone. Under the plugin
that folder is the plugin's, replaced on every update, so classkit looks in the course first:
`course/methodologies/<name>.yaml`, then the framework's. `classkit status` names the file in use,
so a command can hand its path on.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from classkit.model import LayoutError, load_course, load_methodology, methodology_path
from classkit.scaffold import scaffold_course
from classkit.status import report, status
from classkit.validate import Validator

FRAMEWORK_ROOT = Path(__file__).resolve().parents[1] / "plugin"
STANDARD = FRAMEWORK_ROOT / "methodologies" / "question-driven-25.yaml"


def new_course(tmp_path: Path, methodology: str = "question-driven-25") -> Path:
    root = tmp_path / "course"
    scaffold_course(root, FRAMEWORK_ROOT, title="Test", institution="BGU", instructor="",
                    units=2, methodology=methodology)
    return root


def own_methodology(course_root: Path, name: str, sessions: int = 3, minutes: int = 30) -> Path:
    """The standard methodology with other numbers, saved in the course under `name`."""
    data = yaml.safe_load(STANDARD.read_text(encoding="utf-8"))
    data["id"] = name
    data["home_study"]["sessions_per_unit"] = sessions
    data["home_study"]["session_minutes"] = minutes
    path = course_root / "methodologies" / f"{name}.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    return path


def use(course_root: Path, name: str) -> None:
    config = course_root / "course.yaml"
    text = config.read_text(encoding="utf-8")
    config.write_text(text.replace('methodology: "question-driven-25"', f'methodology: "{name}"'),
                      encoding="utf-8")


def test_without_its_own_the_course_uses_the_frameworks(tmp_path):
    root = new_course(tmp_path)
    assert methodology_path(FRAMEWORK_ROOT, "question-driven-25", root) == STANDARD
    assert load_course(root, FRAMEWORK_ROOT).methodology_file == STANDARD


def test_the_courses_own_methodology_is_used(tmp_path):
    root = new_course(tmp_path)
    mine = own_methodology(root, "my-30")
    use(root, "my-30")
    course = load_course(root, FRAMEWORK_ROOT)
    assert course.methodology_file == mine
    assert course.methodology["home_study"]["sessions_per_unit"] == 3
    assert course.methodology["home_study"]["session_minutes"] == 30


def test_a_course_with_its_own_methodology_validates_clean(tmp_path):
    root = new_course(tmp_path)
    own_methodology(root, "my-30")
    use(root, "my-30")
    validator = Validator(load_course(root, FRAMEWORK_ROOT), FRAMEWORK_ROOT)
    validator.run()
    assert not [f for f in validator.findings if f.level == "error"]


def test_findings_about_it_name_the_courses_file(tmp_path):
    root = new_course(tmp_path)
    mine = own_methodology(root, "my-30")
    data = yaml.safe_load(mine.read_text(encoding="utf-8"))
    data["rules"] = {**(data.get("rules") or {}), "no_such_rule": "warn"}
    mine.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    use(root, "my-30")
    validator = Validator(load_course(root, FRAMEWORK_ROOT), FRAMEWORK_ROOT)
    validator.run()
    unknown = [f for f in validator.findings if f.code == "unknown_rule"]
    assert unknown and all(f.where == "course/methodologies/my-30.yaml" for f in unknown)


def test_an_unknown_name_lists_both_places(tmp_path):
    root = new_course(tmp_path)
    own_methodology(root, "my-30")
    with pytest.raises(LayoutError) as error:
        load_methodology(FRAMEWORK_ROOT, "nope", root)
    assert "my-30" in str(error.value) and "question-driven-25" in str(error.value)


def test_status_names_the_file_in_use(tmp_path):
    root = new_course(tmp_path)
    assert "Methodology   question-driven-25 (the framework's): " in report(status(root, FRAMEWORK_ROOT))
    mine = own_methodology(root, "my-30")
    use(root, "my-30")
    assert (f"Methodology   my-30 (the course's own): {mine.as_posix()}"
            in report(status(root, FRAMEWORK_ROOT)))
