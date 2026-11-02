"""The plugin's rules hook, plugin/hooks/rules.sh: it loads the course rules wherever classkit finds a
course (model.find_course_root), and stays silent everywhere else (Phase 1, C1 finding 1)."""

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

HOOK = Path(__file__).resolve().parents[1] / "plugin" / "hooks" / "rules.sh"
BASH = shutil.which("bash")

pytestmark = pytest.mark.skipif(
    BASH is None or (os.name == "nt" and "MSYSTEM" not in os.environ),
    reason="needs bash; on Windows only Git Bash's (another bash, such as WSL's, sees other paths)",
)


def run_hook(project: Path) -> subprocess.CompletedProcess:
    env = {**os.environ, "CLAUDE_PROJECT_DIR": str(project)}
    return subprocess.run([BASH, HOOK.as_posix()], env=env, capture_output=True, text=True,
                          encoding="utf-8", timeout=60)


def assert_rules_loaded(result: subprocess.CompletedProcess) -> None:
    assert result.returncode == 0, result.stderr
    context = json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]
    assert context.startswith("# Class Agent Kit — rules for this course")


def assert_silent(result: subprocess.CompletedProcess) -> None:
    assert result.returncode == 0, result.stderr
    assert result.stdout == ""


def course_at(folder: Path) -> Path:
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "course.yaml").write_text("title: Test\n", encoding="utf-8")
    return folder


def test_course_in_the_usual_place(tmp_path):
    course_at(tmp_path / "repo" / "course")
    assert_rules_loaded(run_hook(tmp_path / "repo"))


def test_course_at_the_top_level(tmp_path):
    # `classkit scaffold course --path .` puts course.yaml in the repository's top folder (C1).
    course_at(tmp_path / "repo")
    assert_rules_loaded(run_hook(tmp_path / "repo"))


def test_session_started_inside_the_repository(tmp_path):
    course_at(tmp_path / "repo" / "course")
    units = tmp_path / "repo" / "course" / "units"
    units.mkdir()
    assert_rules_loaded(run_hook(units))


def test_no_course(tmp_path):
    (tmp_path / "repo").mkdir()
    assert_silent(run_hook(tmp_path / "repo"))


def test_course_folder_without_course_yaml(tmp_path):
    (tmp_path / "repo" / "course").mkdir(parents=True)
    assert_silent(run_hook(tmp_path / "repo"))
