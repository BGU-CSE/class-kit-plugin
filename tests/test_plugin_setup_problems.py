"""The plugin's setup scripts when classkit cannot run (Phase 4, job 1).

Finding 8: without Python 3.10 or later, the teacher is told so, and how to fix it: by Claude at the
start of a session in a course (hooks/rules.sh), and by bin/classkit whenever it is run, instead of
the wrong advice to start a new session. Finding 16: an eval run names, in EVAL_CLASSKIT_DATA, a
folder its sandbox can read, and hooks/bootstrap.sh builds there.
"""

import os
import shutil
import subprocess
from pathlib import Path

import pytest

PLUGIN = Path(__file__).resolve().parents[1] / "plugin"
BOOTSTRAP = PLUGIN / "hooks" / "bootstrap.sh"
RULES = PLUGIN / "hooks" / "rules.sh"
WRAPPER = PLUGIN / "bin" / "classkit"
BASH = shutil.which("bash")

pytestmark = pytest.mark.skipif(
    BASH is None or os.name == "nt",
    reason="needs bash, and stand-in commands that shadow the real Python (not on Windows)",
)


def without_python(tmp_path: Path) -> str:
    """A PATH on which python3, python and py exist but fail, as the Microsoft Store placeholder
    does, so find-python.sh accepts none of them."""
    stubs = tmp_path / "no-python"
    stubs.mkdir()
    for name in ("python3", "python", "py"):
        stub = stubs / name
        stub.write_text("#!/bin/sh\nexit 1\n", encoding="utf-8")
        stub.chmod(0o755)
    return f"{stubs}{os.pathsep}{os.environ['PATH']}"


def run(script: Path, env: dict) -> subprocess.CompletedProcess:
    return subprocess.run([BASH, script.as_posix()], env={**os.environ, **env},
                          capture_output=True, text=True, encoding="utf-8", timeout=60)


def test_bootstrap_without_python_tells_the_wrapper(tmp_path):
    env_file = tmp_path / "env"
    result = run(BOOTSTRAP, {"PATH": without_python(tmp_path),
                             "CLAUDE_PLUGIN_DATA": str(tmp_path / "data"),
                             "CLAUDE_ENV_FILE": str(env_file)})
    assert result.returncode == 0, result.stderr
    assert result.stdout == ""
    assert 'export CLASSKIT_SETUP_PROBLEM="no-python"' in env_file.read_text(encoding="utf-8")
    assert "no Python 3.10 or later found" in (tmp_path / "data" / "bootstrap.log").read_text(
        encoding="utf-8")


def test_wrapper_names_the_missing_python(tmp_path):
    env = {"CLASSKIT_SETUP_PROBLEM": "no-python"}
    result = subprocess.run([BASH, WRAPPER.as_posix(), "status"],
                            env={k: v for k, v in {**os.environ, **env}.items()
                                 if k != "CLASSKIT_VENV"},
                            capture_output=True, text=True, encoding="utf-8", timeout=60)
    assert result.returncode == 1
    assert "Python 3.10 or later" in result.stderr
    assert "python.org" in result.stderr
    assert "Start a new Claude Code session: the plugin installs it" not in result.stderr


def test_wrapper_after_a_failed_install(tmp_path):
    env = {"CLASSKIT_SETUP_PROBLEM": "install-failed"}
    result = subprocess.run([BASH, WRAPPER.as_posix(), "status"],
                            env={k: v for k, v in {**os.environ, **env}.items()
                                 if k != "CLASSKIT_VENV"},
                            capture_output=True, text=True, encoding="utf-8", timeout=60)
    assert result.returncode == 1
    assert "could not be installed" in result.stderr


def test_rules_without_python_tell_the_teacher(tmp_path):
    course = tmp_path / "repo" / "course"
    course.mkdir(parents=True)
    (course / "course.yaml").write_text("title: Test\n", encoding="utf-8")
    result = run(RULES, {"PATH": without_python(tmp_path),
                         "CLAUDE_PROJECT_DIR": str(tmp_path / "repo")})
    assert result.returncode == 0, result.stderr
    assert result.stdout.startswith("# Class Kit — rules for this course")
    assert "## Python is missing on this computer" in result.stdout
    assert len(result.stdout) <= 10000


def test_eval_runs_build_where_their_sandbox_can_read(tmp_path):
    result = run(BOOTSTRAP, {"PATH": without_python(tmp_path),
                             "CLAUDE_PLUGIN_DATA": str(tmp_path / "data"),
                             "EVAL_CLASSKIT_DATA": str(tmp_path / "eval-data")})
    assert result.returncode == 0, result.stderr
    assert (tmp_path / "eval-data" / "bootstrap.log").is_file()
    assert not (tmp_path / "data").exists()
