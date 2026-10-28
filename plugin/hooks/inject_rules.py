"""SessionStart, run by rules.sh: print the course rules as hook JSON for Claude's context.

Usage: inject_rules.py RULES LIMIT PLUGIN_ROOT

When the plugin was installed from a marketplace and that marketplace now offers another version of
it — usually because the course's settings point at another branch or tag — a short note is added
after the rules, so that Claude tells the teacher and offers to run the update (C7, finding 13).

Exit 3: the text is over LIMIT characters; nothing is printed.
"""

import json
import sys
from pathlib import Path


def plugin_manifest(plugin_dir: Path) -> dict:
    return json.loads((plugin_dir / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))


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
    # Installed from a marketplace, a plugin runs from <plugins>/cache/<marketplace>/<plugin>/<version>.
    # Loaded with --plugin-dir it runs from anywhere else, and there is nothing to compare.
    if len(root.parts) < 5 or root.parts[-4] != "cache":
        return ""
    plugins, marketplace = root.parents[3], root.parts[-3]
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
    text = Path(rules).read_text(encoding="utf-8") + version_note(root)
    if len(text) > limit:
        print(f"class-agent-kit: the course rules are {len(text)} characters, over the {limit} "
              "Claude Code accepts; they were NOT loaded", file=sys.stderr)
        return 3
    sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": text}}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
