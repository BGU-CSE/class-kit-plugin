"""`classkit` reads and writes UTF-8 whatever the console's code page.

On Windows, a piped stream is in the code page — and Claude Code always pipes. Running the CLI in a
subprocess with `PYTHONIOENCODING=cp1256` reproduces that on any system.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from classkit.scaffold import scaffold_course

FRAMEWORK_ROOT = Path(__file__).resolve().parents[1] / "plugin"


def classkit(*args: str, stdin: bytes = b"") -> subprocess.CompletedProcess:
    env = {**os.environ, "PYTHONIOENCODING": "cp1256",
           "PYTHONPATH": str(FRAMEWORK_ROOT / "src")}
    return subprocess.run(
        [sys.executable, "-c", "import sys; from classkit.cli import main; sys.exit(main(sys.argv[1:]))",
         *args],
        input=stdin, capture_output=True, env=env, timeout=120,
    )


def test_ingest_report_survives_a_code_page_console(tmp_path: Path):
    course = tmp_path / "course"
    scaffold_course(course, FRAMEWORK_ROOT, code="T-1", title="Test", institution="U",
                    instructor="", units=2, methodology="question-driven-25")
    (course / "materials" / "source" / "heaps.md").write_bytes(b"# Heaps\n\n## Insert\n\nSift up.\n")

    done = classkit("ingest", "--no-fetch", "--course", str(course))

    assert done.returncode == 0, done.stderr.decode("utf-8", "replace")
    assert "→" in done.stdout.decode("utf-8")


def test_text_piped_into_write_is_saved_byte_for_byte(tmp_path: Path):
    target = tmp_path / "unit.md"
    text = "Heaps → heapsort — ערימות\n".encode("utf-8")

    done = classkit("write", str(target), stdin=text)

    assert done.returncode == 0, done.stderr.decode("utf-8", "replace")
    assert target.read_bytes() == text
