"""`classkit scaffold course` writes the course repository's Claude Code settings,
`.claude/settings.json` beside `course/` (Phase 4, done early in session 18): the PowerShell tool off,
so that on Windows classkit always runs through Bash (finding 9), the read-only classkit commands
allowed without a prompt (D-045), and the plugin and its marketplace (session 23). Create-only, like
everything scaffold writes."""

import json
import subprocess
import sys
from pathlib import Path

from classkit.model import find_framework_root
from classkit.scaffold import scaffold_course

PLUGIN = Path(__file__).resolve().parents[1] / "plugin"
LAUNCHER = PLUGIN / "scripts" / "run_classkit.py"
READ_ONLY = ["Bash(classkit validate:*)", "Bash(classkit status:*)", "Bash(classkit doctor:*)",
             "Bash(classkit ingest --preflight:*)"]


def scaffold(course_root: Path):
    return scaffold_course(course_root, find_framework_root(), title="Test", institution="BGU",
                           instructor="", units=2, methodology="question-driven-25")


def assert_settings(path: Path) -> None:
    settings = json.loads(path.read_text(encoding="utf-8"))
    assert settings["env"]["CLAUDE_CODE_USE_POWERSHELL_TOOL"] == "0"
    assert settings["permissions"]["allow"] == READ_ONLY
    # The plugin, so that a TA who opens the course is offered it — named as the plugin and its
    # marketplace name themselves, with no `ref`: a course is not pinned to a version (D-049).
    plugin = json.loads((PLUGIN / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))["name"]
    catalog = json.loads((PLUGIN.parent / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
    marketplace = catalog["name"]
    assert settings["enabledPlugins"] == {f"{plugin}@{marketplace}": True}
    assert settings["extraKnownMarketplaces"] == {
        marketplace: {"source": {"source": "github", "repo": "BGU-CSE/class-kit-plugin"}}}


def test_settings_beside_the_course(tmp_path):
    result = scaffold(tmp_path / "course")
    settings = tmp_path / ".claude" / "settings.json"
    assert settings in result.created
    assert_settings(settings)
    # Not part of the course, so not in the course log.
    assert ".claude" not in (tmp_path / "course" / "LOG.md").read_text(encoding="utf-8")


def test_settings_in_a_course_folder_with_another_name(tmp_path):
    scaffold(tmp_path / "my-course")
    assert_settings(tmp_path / "my-course" / ".claude" / "settings.json")


def test_existing_settings_are_left_alone(tmp_path):
    settings = tmp_path / ".claude" / "settings.json"
    settings.parent.mkdir()
    settings.write_text('{"model": "opus"}\n', encoding="utf-8")
    result = scaffold(tmp_path / "course")
    assert settings in result.skipped
    assert settings.read_text(encoding="utf-8") == '{"model": "opus"}\n'


def test_a_rerun_adds_them_to_an_older_course(tmp_path):
    scaffold(tmp_path / "course")
    settings = tmp_path / ".claude" / "settings.json"
    settings.unlink()
    result = scaffold(tmp_path / "course")
    assert result.created == [settings]
    assert_settings(settings)


def test_the_plugins_copy_writes_them_too(tmp_path):
    result = subprocess.run([sys.executable, str(LAUNCHER), "scaffold", "course", "--title", "Test"],
                            cwd=tmp_path, capture_output=True, text=True, encoding="utf-8",
                            timeout=120)
    assert result.returncode == 0, result.stderr
    assert "created  .claude/settings.json" in result.stdout
    assert_settings(tmp_path / ".claude" / "settings.json")
