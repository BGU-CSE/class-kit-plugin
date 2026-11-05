"""Everything a teacher or Claude reads names the plugin's commands in full (Phase 5).

Claude Code names a plugin's commands `/<plugin>:<command>`. A bare `/plan-units` in a prompt, a
template or a `classkit` message is what Claude then suggests, and Claude Code's own suggestions offer
it ready to send (finding C1, session 2): it runs nothing, or a teacher's own command of that name.
So every command is named as `plugin.json` names the plugin, and a command dispatches the plugin's
agents by their full name too.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

PLUGIN = Path(__file__).resolve().parents[1] / "plugin"
NAME = json.loads((PLUGIN / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))["name"]
COMMANDS = sorted(p.stem for p in (PLUGIN / "commands").glob("*.md"))
AGENTS = sorted(p.stem for p in (PLUGIN / "agents").glob("*.md"))
BARE = re.compile(r"(?<![A-Za-z0-9_:/.$}-])/(" + "|".join(map(re.escape, COMMANDS)) + r")\b")
TEXT = sorted(p for p in PLUGIN.rglob("*")
              if p.is_file() and p.suffix in {".md", ".py", ".sh", ".json", ".yaml"} and "__pycache__" not in p.parts)


@pytest.mark.parametrize("path", TEXT, ids=lambda p: p.relative_to(PLUGIN).as_posix())
def test_no_command_is_named_bare(path):
    found = [m.group(0) for m in BARE.finditer(path.read_text(encoding="utf-8"))]
    assert not found, f"name these in full, /{NAME}:<command>: {sorted(set(found))}"


@pytest.mark.parametrize("command", sorted((PLUGIN / "commands").glob("*.md")), ids=lambda p: p.stem)
def test_commands_send_the_plugins_agents_by_full_name(command):
    text = command.read_text(encoding="utf-8")
    bare = re.findall(r"\*\*(" + "|".join(map(re.escape, AGENTS)) + r")\*\*", text)
    assert not bare, f"name these in full, {NAME}:<agent>: {sorted(set(bare))}"


def test_the_marketplace_lists_the_plugin_by_its_name():
    catalog = json.loads((PLUGIN.parent / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
    assert [p["name"] for p in catalog["plugins"]] == [NAME]
