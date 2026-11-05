"""The plugin's agents declare the skills they work to in `skills:` frontmatter (Phase 4, finding 19).

An agent whose `tools:` list has no Skill tool cannot load a skill it is told to load: in 0.2.0 the
course-critic, asked to, found no way and worked without its standard, or asked for permission to
read the plugin's files. A skill named in `skills:` is preloaded into the agent's context instead
(verified in a session, PLUGIN-LOG session 20). So every skill an agent's text names must be in its
frontmatter, named in full (`class-kit:<skill>`: a teacher's own skill of the same name does
not replace the plugin's standard), and every skill it lists must exist.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
import yaml

PLUGIN = Path(__file__).resolve().parents[1] / "plugin"
NAME = json.loads((PLUGIN / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))["name"]
SKILLS = sorted(p.parent.name for p in (PLUGIN / "skills").glob("*/SKILL.md"))
AGENTS = sorted((PLUGIN / "agents").glob("*.md"))


def frontmatter(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    _, head, body = text.split("---\n", 2)
    return yaml.safe_load(head), body


def named_in(body: str) -> set[str]:
    return {skill for skill in SKILLS if re.search(rf"(?<![\w-]){re.escape(skill)}(?![\w-])", body)}


@pytest.mark.parametrize("agent", AGENTS, ids=lambda p: p.stem)
def test_every_skill_an_agent_names_is_preloaded(agent):
    meta, body = frontmatter(agent)
    declared = meta.get("skills") or []
    assert sorted(f"{NAME}:{s}" for s in named_in(body)) == sorted(declared)


@pytest.mark.parametrize("agent", AGENTS, ids=lambda p: p.stem)
def test_preloaded_skills_exist_and_are_named_in_full(agent):
    meta, _ = frontmatter(agent)
    for entry in meta.get("skills") or []:
        plugin, _, skill = entry.partition(":")
        assert plugin == NAME and skill in SKILLS, entry


@pytest.mark.parametrize("agent", AGENTS, ids=lambda p: p.stem)
def test_no_agent_is_told_to_load_a_skill(agent):
    # It has no Skill tool to do it with; the frontmatter does it.
    _, body = frontmatter(agent)
    assert not re.search(r"\bLoad (the )?\W*(" + "|".join(map(re.escape, SKILLS)) + ")", body)
