"""Which Class Agent Kit is running, and which the course was last worked on with (Phase 4).

A teacher's computers can run different versions of the plugin — one updated, another not — and a
course is shared between them through git. Changes keep a newer plugin able to read an older course
(D-049), but not the reverse: an older plugin may not understand what a newer one wrote, and may
report errors that are not there. So every entry `classkit log` writes names the plugin that wrote
it (`- **Plugin:** Class Agent Kit 0.3.0`), and the session-start hook and `classkit doctor`
compare the newest version in the course log with the one running.

Standard library only: `hooks/inject_rules.py` imports this module with the system Python, before
the plugin's own dependencies are installed.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

#: The plugin's own folder — `plugin/` in the development repository, the installed copy otherwise.
PLUGIN_ROOT = Path(__file__).resolve().parents[2]

#: The log field that names the plugin, and a version in it (MAJOR.MINOR.PATCH, maybe -pre-release).
LOG_FIELD = "Plugin"
_VERSION = re.compile(r"(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z.-]+))?")
_LOG_LINE = re.compile(r"^- \*\*Plugin:\*\* .*?(\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?)\s*$", re.MULTILINE)


def manifest(plugin_root: Path | None = None) -> dict:
    """The plugin's `.claude-plugin/plugin.json`, or {} when it cannot be read."""
    path = (plugin_root or PLUGIN_ROOT) / ".claude-plugin" / "plugin.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def running(plugin_root: Path | None = None) -> str:
    """The running plugin's version, or "" when it cannot be read."""
    return str(manifest(plugin_root).get("version") or "")


def label(plugin_root: Path | None = None) -> str:
    """What a log entry names: the plugin's display name and version ("" when unknown)."""
    data = manifest(plugin_root)
    version = str(data.get("version") or "")
    if not version:
        return ""
    return f"{data.get('displayName') or data.get('name') or 'the plugin'} {version}"


def key(version: str) -> tuple | None:
    """A sort key for a version, or None if it is not one. A pre-release sorts before its release
    (0.1.4-spike < 0.1.4), as in semantic versioning."""
    found = _VERSION.fullmatch(version.strip())
    if found is None:
        return None
    major, minor, patch, pre = found.groups()
    return (int(major), int(minor), int(patch), 0 if pre else 1, pre or "")


def newest_in_log(text: str) -> str:
    """The newest plugin version any entry of a course log names, or "" when none does."""
    versions = [v for v in _LOG_LINE.findall(text) if key(v) is not None]
    return max(versions, key=key, default="")


def course_newer(course_root: Path, plugin_root: Path | None = None) -> tuple[str, str]:
    """(newest in the course log, running) when the course log names a newer version than the one
    running; ("", "") otherwise — including when either cannot be read."""
    try:
        text = (course_root / "LOG.md").read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return "", ""
    newest, current = newest_in_log(text), running(plugin_root)
    if newest and key(current) is not None and key(newest) > key(current):
        return newest, current
    return "", ""
