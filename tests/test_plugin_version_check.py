"""The rules hook's version note (plugin/hooks/inject_rules.py): when the plugin runs from Claude
Code's cache and its marketplace now offers another version, the course rules carry a note telling
Claude to offer the update (Phase 1, C7, finding 13). Built here in Claude Code's folder layout:
<plugins>/cache/<marketplace>/<plugin>/<version>/ and <plugins>/marketplaces/<marketplace>/."""

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
BASH = shutil.which("bash")
MARKETPLACE = "agent-based-class"
PLUGIN = "class-agent-kit"
NOTE = "## Class Agent Kit is not at the version its marketplace offers"

pytestmark = pytest.mark.skipif(
    BASH is None or (os.name == "nt" and "MSYSTEM" not in os.environ),
    reason="needs bash; on Windows only Git Bash's (another bash, such as WSL's, sees other paths)",
)


def set_version(plugin_dir: Path, version: str) -> None:
    path = plugin_dir / ".claude-plugin" / "plugin.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    manifest["version"] = version
    path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def copy_plugin(to: Path) -> Path:
    shutil.copytree(REPO / "plugin", to, ignore=shutil.ignore_patterns("__pycache__"))
    return to


def layout(tmp_path: Path, running: str, offered: str, known: bool = True) -> Path:
    """Claude Code's plugin folders with the plugin cached at `running` and its marketplace copy
    offering `offered`. Returns the cached plugin's root."""
    plugins = tmp_path / "home" / ".claude" / "plugins"
    cached = copy_plugin(plugins / "cache" / MARKETPLACE / PLUGIN / running)
    set_version(cached, running)
    clone = plugins / "marketplaces" / MARKETPLACE
    (clone / ".claude-plugin").mkdir(parents=True)
    shutil.copy(REPO / ".claude-plugin" / "marketplace.json", clone / ".claude-plugin" / "marketplace.json")
    set_version(copy_plugin(clone / "plugin"), offered)
    if known:
        (plugins / "known_marketplaces.json").write_text(json.dumps({
            MARKETPLACE: {"source": {"source": "github", "repo": "owner/repo", "ref": "b"},
                          "installLocation": str(clone)}}), encoding="utf-8")
    return cached


def course(tmp_path: Path) -> Path:
    (tmp_path / "repo" / "course").mkdir(parents=True)
    (tmp_path / "repo" / "course" / "course.yaml").write_text("title: Test\n", encoding="utf-8")
    return tmp_path / "repo"


def context(plugin_root: Path, project: Path, **extra: str) -> str:
    # No data folder unless a test gives one: without it there is no check of GitHub.
    env = {k: v for k, v in os.environ.items() if k not in ("CLAUDE_PLUGIN_DATA", "EVAL_CLASSKIT_DATA")}
    env.update({"CLAUDE_PROJECT_DIR": str(project), **extra})
    result = subprocess.run([BASH, (plugin_root / "hooks" / "rules.sh").as_posix()], env=env,
                            capture_output=True, text=True, encoding="utf-8", timeout=60)
    assert result.returncode == 0, result.stderr
    text = json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]
    assert text.startswith("# Class Agent Kit — rules for this course")
    return text


def test_same_version_no_note(tmp_path):
    assert NOTE not in context(layout(tmp_path, "0.2.0", "0.2.0"), course(tmp_path))


def test_other_version_note(tmp_path):
    text = context(layout(tmp_path, "0.2.0", "0.2.0-b"), course(tmp_path))
    assert NOTE in text
    assert "**0.2.0**" in text and "**0.2.0-b**" in text
    assert "claude plugin update class-agent-kit@agent-based-class --scope" in text


def test_older_version_offered_is_noted_too(tmp_path):
    # A course pinned back to an earlier version: the pin is what counts, not which is newer.
    assert NOTE in context(layout(tmp_path, "0.2.0-b", "0.2.0"), course(tmp_path))


def test_default_marketplace_folder_without_known_marketplaces(tmp_path):
    assert NOTE in context(layout(tmp_path, "0.2.0", "0.3.0", known=False), course(tmp_path))


def test_not_from_a_marketplace_no_note(tmp_path):
    # Loaded with --plugin-dir: the plugin runs from this checkout, not from a cache.
    assert NOTE not in context(REPO / "plugin", course(tmp_path))


def test_unreadable_marketplace_leaves_the_rules(tmp_path):
    cached = layout(tmp_path, "0.2.0", "0.3.0")
    (tmp_path / "home" / ".claude" / "plugins" / "known_marketplaces.json").write_text("{not json", encoding="utf-8")
    assert NOTE not in context(cached, course(tmp_path))


# -- the course log names a newer plugin than the one running (Phase 4) --------------------

COURSE_NOTE = "## This course was worked on with a newer Class Agent Kit"


def logged_with(project: Path, *versions: str) -> Path:
    """The course's LOG.md with one entry per version, as `classkit log` writes them."""
    entries = "".join(f"\n## 2026-11-0{i} — step {i}\n- **Changed:** x\n- **Plugin:** Class Agent Kit {v}\n"
                      for i, v in enumerate(versions, 1))
    (project / "course" / "LOG.md").write_text("# Course log\n" + entries, encoding="utf-8")
    return project


def test_a_course_worked_on_with_a_newer_plugin_is_noted(tmp_path):
    project = logged_with(course(tmp_path), "0.2.0", "0.3.0", "0.2.0")
    text = context(layout(tmp_path, "0.2.0", "0.2.0"), project)
    assert COURSE_NOTE in text
    assert "**0.3.0**" in text and "**0.2.0**" in text
    # finding 18: the marketplace's local copy may be stale, so it is refreshed first
    assert "claude plugin marketplace update agent-based-class" in text
    assert "claude plugin update class-agent-kit@agent-based-class --scope" in text


def test_the_course_note_replaces_the_marketplace_note(tmp_path):
    project = logged_with(course(tmp_path), "0.3.0")
    text = context(layout(tmp_path, "0.2.0", "0.3.0"), project)
    assert COURSE_NOTE in text and NOTE not in text


def test_a_course_worked_on_with_this_version_or_older_is_not_noted(tmp_path):
    project = logged_with(course(tmp_path), "0.1.4-spike", "0.2.0")
    assert COURSE_NOTE not in context(layout(tmp_path, "0.2.0", "0.2.0"), project)


def test_a_pre_release_is_older_than_its_release(tmp_path):
    project = logged_with(course(tmp_path), "0.2.0-b")
    assert COURSE_NOTE not in context(layout(tmp_path, "0.2.0", "0.2.0"), project)
    assert COURSE_NOTE in context(layout(tmp_path / "pre", "0.2.0-a", "0.2.0-a"), project)


def test_a_log_that_names_no_plugin_is_not_noted(tmp_path):
    project = course(tmp_path)
    (project / "course" / "LOG.md").write_text("# Course log\n\n## 2026-11-01 — by hand\n", encoding="utf-8")
    assert COURSE_NOTE not in context(layout(tmp_path, "0.2.0", "0.2.0"), project)


def test_from_a_folder_the_note_says_to_update_the_folder(tmp_path):
    project = logged_with(course(tmp_path), "99.0.0")
    text = context(REPO / "plugin", project)
    assert COURSE_NOTE in text
    assert "git pull" in text and "claude plugin update" not in text


# -- the version GitHub publishes, checked once a day (Phase 4, finding 18) --------------------

UPDATE_NOTE = "## A newer Class Agent Kit is available"


def published(tmp_path: Path, version: str) -> dict:
    """A stand-in for raw.githubusercontent.com serving owner/repo at ref `b` (the ref layout() records),
    with the plugin at `version`; the environment that points the check at it."""
    remote = tmp_path / "remote"
    branch = remote / "owner" / "repo" / "b"
    (branch / ".claude-plugin").mkdir(parents=True, exist_ok=True)
    shutil.copy(REPO / ".claude-plugin" / "marketplace.json", branch / ".claude-plugin" / "marketplace.json")
    (branch / "plugin" / ".claude-plugin").mkdir(parents=True, exist_ok=True)
    (branch / "plugin" / ".claude-plugin" / "plugin.json").write_text(
        json.dumps({"name": PLUGIN, "version": version}), encoding="utf-8")
    return {"CLASSKIT_UPDATE_BASE": remote.as_uri(), "CLAUDE_PLUGIN_DATA": str(tmp_path / "data")}


def cached(tmp_path: Path) -> dict:
    return json.loads((tmp_path / "data" / "update-check.json").read_text(encoding="utf-8"))


def test_a_newer_published_version_is_offered(tmp_path):
    text = context(layout(tmp_path, "0.2.0", "0.2.0"), course(tmp_path), **published(tmp_path, "0.3.0"))
    assert UPDATE_NOTE in text and NOTE not in text
    assert "**0.2.0**" in text and "**0.3.0**" in text
    assert "claude plugin update class-agent-kit@agent-based-class --scope" in text
    assert "https://github.com/owner/repo/blob/b/CHANGELOG.md" in text
    assert "Never update" in text
    assert cached(tmp_path)["version"] == "0.3.0"


def test_the_same_or_an_older_published_version_is_not(tmp_path):
    env = published(tmp_path, "0.2.0")
    assert UPDATE_NOTE not in context(layout(tmp_path, "0.2.0", "0.2.0"), course(tmp_path), **env)
    env = published(tmp_path / "old", "0.1.4")
    assert UPDATE_NOTE not in context(layout(tmp_path / "old", "0.2.0", "0.2.0"), course(tmp_path / "old"), **env)


def test_github_is_asked_once_a_day(tmp_path):
    cached_plugin, project = layout(tmp_path, "0.2.0", "0.2.0"), course(tmp_path)
    env = published(tmp_path, "0.3.0")
    context(cached_plugin, project, **env)
    shutil.rmtree(tmp_path / "remote")  # a second request would now find nothing
    assert UPDATE_NOTE in context(cached_plugin, project, **env)
    # a day later it asks again
    entry = cached(tmp_path)
    entry["checked"] -= 25 * 3600
    (tmp_path / "data" / "update-check.json").write_text(json.dumps(entry), encoding="utf-8")
    assert UPDATE_NOTE not in context(cached_plugin, project, **env)
    assert cached(tmp_path)["version"] == ""


def test_no_network_no_note_and_the_rules_still_load(tmp_path):
    env = {"CLASSKIT_UPDATE_BASE": (tmp_path / "nowhere").as_uri(), "CLAUDE_PLUGIN_DATA": str(tmp_path / "data")}
    assert UPDATE_NOTE not in context(layout(tmp_path, "0.2.0", "0.2.0"), course(tmp_path), **env)


def test_without_a_data_folder_there_is_no_check(tmp_path):
    env = published(tmp_path, "0.3.0")
    del env["CLAUDE_PLUGIN_DATA"]
    assert UPDATE_NOTE not in context(layout(tmp_path, "0.2.0", "0.2.0"), course(tmp_path), **env)


def test_the_course_note_comes_first(tmp_path):
    project = logged_with(course(tmp_path), "0.4.0")
    text = context(layout(tmp_path, "0.2.0", "0.2.0"), project, **published(tmp_path, "0.3.0"))
    assert COURSE_NOTE in text and UPDATE_NOTE not in text
