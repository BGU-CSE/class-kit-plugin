"""The plugin's copy of classkit ends a course scaffold with the reminder to start a new session, so
the course rules load (Phase 1, C1, finding 12) — and says nothing when nothing was created."""

import subprocess
import sys
from pathlib import Path

LAUNCHER = Path(__file__).resolve().parents[1] / "plugin" / "scripts" / "run_classkit.py"
REMINDER = "start a new Claude Code session (or type /clear) so the course rules load"


def scaffold(folder: Path) -> str:
    result = subprocess.run([sys.executable, str(LAUNCHER), "scaffold", "course", "--title", "Test"],
                            cwd=folder, capture_output=True, text=True, encoding="utf-8", timeout=120)
    assert result.returncode == 0, result.stderr
    return result.stdout


def test_new_course_reminds_to_start_a_new_session(tmp_path):
    assert REMINDER in scaffold(tmp_path)


def test_nothing_created_no_reminder(tmp_path):
    scaffold(tmp_path)
    assert REMINDER not in scaffold(tmp_path)
