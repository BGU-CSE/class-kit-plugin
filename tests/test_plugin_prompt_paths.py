"""The plugin's prompts name the framework's own files through ${CLAUDE_PLUGIN_ROOT}, which Claude
Code fills in inside skill and agent text — never by a path relative to the course repository, which
under the plugin has no `schemas/`, `defaults/`, `methodologies/` or `templates/` (findings 17 and the
methodology fix, Phase 4). A course's own methodology is named as `course/methodologies/…`."""

import re
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1] / "plugin"
FRAMEWORK_FILE = re.compile(r"`(schemas|defaults|methodologies|templates)/")


def test_no_prompt_names_a_framework_file_relative_to_the_course_repository():
    offenders = []
    for folder in ("agents", "commands", "skills", "rules"):
        for path in sorted((PLUGIN / folder).rglob("*.md")):
            for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if FRAMEWORK_FILE.search(line):
                    offenders.append(f"{path.relative_to(PLUGIN)}:{number}: {line.strip()}")
    assert offenders == []
