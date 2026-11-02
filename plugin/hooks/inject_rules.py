"""SessionStart, run by rules.sh: print the course rules as hook JSON for Claude's context.

Usage: inject_rules.py RULES LIMIT PLUGIN_ROOT [COURSE]

When the course log names a newer Class Agent Kit than the one running — another computer, updated,
has worked on the course — a note is added after the rules, so that Claude tells the teacher and
offers to update before anything is changed (Phase 4; `classkit/version.py`). Otherwise, when the
plugin was installed from a marketplace and that marketplace now offers another version of
it — usually because the course's settings point at another branch or tag — a short note is added
after the rules, so that Claude tells the teacher and offers to run the update (C7, finding 13).

Exit 3: the text is over LIMIT characters; nothing is printed.
"""

import json
import sys
from pathlib import Path


def plugin_manifest(plugin_dir: Path) -> dict:
    return json.loads((plugin_dir / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))


def installed_from(root: Path) -> tuple[str, Path] | None:
    """(marketplace, the plugins folder) when the plugin runs from a marketplace install, else None.

    Installed from a marketplace, a plugin runs from <plugins>/cache/<marketplace>/<plugin>/<version>.
    Loaded with --plugin-dir it runs from anywhere else."""
    root = root.resolve()
    if len(root.parts) < 5 or root.parts[-4] != "cache":
        return None
    return root.parts[-3], root.parents[3]


def course_note(root: Path, course: Path) -> str:
    """The note when the course log names a newer plugin than this one; "" otherwise, or on any
    surprise (a convenience, like the marketplace note: it never stops the rules)."""
    try:
        return _course_note(root, course)
    except Exception:  # noqa: BLE001
        return ""


def _course_note(root: Path, course: Path) -> str:
    # The plugin's own classkit/version.py: standard library only, so the system Python imports it.
    # Imported here, so that a failure only drops this note, never the rules.
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
    from classkit import version  # noqa: PLC0415

    newest, running = version.course_newer(course, root)
    if not newest:
        return ""
    name = str(version.manifest(root).get("name") or "class-agent-kit")
    source = installed_from(root)
    if source is None:
        how = (f"This session loads the plugin from a folder (`{root.resolve().as_posix()}`), not from "
               "a marketplace: the teacher updates that copy (`git pull` in it), then starts a new "
               "session.")
    else:
        plugin_id = f"{name}@{source[0]}"
        how = (f"With their OK, in Bash: `claude plugin marketplace update {source[0]}`, then "
               f"`claude plugin list` to see the scope `{plugin_id}` is installed at for this folder, "
               f"then `claude plugin update {plugin_id} --scope <that scope>`. Then tell the teacher "
               "to start a new session — close Claude Code and open it again — for the new version "
               "to load. Never update without their OK.")
    return f"""

## This course was worked on with a newer Class Agent Kit

The course log (`LOG.md`) shows Class Agent Kit **{newest}** at work on this course, and this
session runs **{running}** — usually because another computer, already updated, has worked on it. An older version may not
understand what a newer one wrote, and its checks may report errors that are not there. In your first
reply, before anything else, tell the teacher in one or two plain sentences, and offer to update.
{how} Until the teacher has updated or said to go on, change nothing in the course, and do not
"fix" what `classkit validate` reports.
"""


def version_note(root: Path) -> str:
    """The note, or "" when the versions match or the layout is not the one expected.

    The check is a convenience: any surprise in Claude Code's own folders — a layout a later version
    changes, a file that does not parse — leaves it silent rather than stopping the rules.
    """
    try:
        return _version_note(root)
    except Exception:  # noqa: BLE001
        return ""


def _version_note(root: Path) -> str:
    root = root.resolve()
    source = installed_from(root)
    if source is None:
        return ""  # loaded with --plugin-dir: there is no marketplace to compare with
    marketplace, plugins = source
    manifest = plugin_manifest(root)
    name, running = manifest["name"], str(manifest.get("version", ""))

    location = plugins / "marketplaces" / marketplace
    known = plugins / "known_marketplaces.json"
    if known.is_file():
        entry = json.loads(known.read_text(encoding="utf-8")).get(marketplace) or {}
        if entry.get("installLocation"):
            location = Path(entry["installLocation"])

    catalog = json.loads((location / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
    entry = next((p for p in catalog.get("plugins", []) if p.get("name") == name), None)
    if entry is None or not isinstance(entry.get("source"), str):
        return ""  # a remote source: its version is not on this machine to compare
    offered = str(plugin_manifest(location / entry["source"]).get("version") or entry.get("version") or "")
    if not offered or not running or offered == running:
        return ""

    plugin_id = f"{name}@{marketplace}"
    return f"""

## Class Agent Kit is not at the version its marketplace offers

This session runs Class Agent Kit **{running}**, and its marketplace (`{marketplace}`) now offers
**{offered}** — usually because the course's settings point at another version. In your first
reply, before anything else, tell the teacher in one or two plain sentences, and offer to update.
With their OK, in Bash: run `claude plugin list` to see the scope `{plugin_id}` is installed at for
this folder, then `claude plugin update {plugin_id} --scope <that scope>`. Then tell the teacher to
start a new session — close Claude Code and open it again — for the new version to load. Never
update without their OK.
"""


def main() -> int:
    rules, limit, root = sys.argv[1], int(sys.argv[2]), Path(sys.argv[3])
    course = Path(sys.argv[4]) if len(sys.argv) > 4 else None
    # The course note already asks for the update, and says why; the marketplace note would repeat it.
    note = (course_note(root, course) if course else "") or version_note(root)
    text = Path(rules).read_text(encoding="utf-8") + note
    if len(text) > limit:
        print(f"class-agent-kit: the course rules are {len(text)} characters, over the {limit} "
              "Claude Code accepts; they were NOT loaded", file=sys.stderr)
        return 3
    sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": text}}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
