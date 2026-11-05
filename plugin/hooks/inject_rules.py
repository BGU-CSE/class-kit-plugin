"""SessionStart, run by rules.sh: print the course rules as hook JSON for Claude's context.

Usage: inject_rules.py RULES LIMIT PLUGIN_ROOT [COURSE]

When the course log names a newer Class Kit than the one running — another computer, updated,
has worked on the course — a note is added after the rules, so that Claude tells the teacher and
offers to update before anything is changed (Phase 4; `classkit/version.py`). Otherwise, when the
plugin was installed from a marketplace and that marketplace now offers another version of
it — usually because the course's settings point at another branch or tag — a short note is added
after the rules, so that Claude tells the teacher and offers to run the update (C7, finding 13).

Between the two: once a day, when the plugin came from a GitHub marketplace, the version that
marketplace publishes is read from GitHub — Claude Code's own copy of the marketplace is refreshed only
when asked (finding 18) — and when it is newer than the one running, Claude asks the teacher whether to
update. Never without their OK. The answer is kept in the plugin's data folder for a day; with no data
folder, or no network, there is no check and no note.

Exit 3: the text is over LIMIT characters; nothing is printed.
"""

import json
import os
import posixpath
import re
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

#: How often GitHub is asked for the published version, and how long one request may take.
CHECK_EVERY = 24 * 3600
TIMEOUT = 3
#: Where GitHub serves a repository's files; tests point it at a folder (a file:// URL).
RAW = os.environ.get("CLASSKIT_UPDATE_BASE", "https://raw.githubusercontent.com")
CACHE = "update-check.json"


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


def _versions():
    """The plugin's own classkit/version.py: standard library only, so the system Python imports it.
    Imported when a note needs it, so that a failure only drops that note, never the rules."""
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
    from classkit import version  # noqa: PLC0415

    return version


def _course_note(root: Path, course: Path) -> str:
    version = _versions()
    newest, running = version.course_newer(course, root)
    if not newest:
        return ""
    name = str(version.manifest(root).get("name") or "class-kit")
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

## This course was worked on with a newer Class Kit

The course log (`LOG.md`) shows Class Kit **{newest}** at work on this course, and this
session runs **{running}** — usually because another computer, already updated, has worked on it. An older version may not
understand what a newer one wrote, and its checks may report errors that are not there. In your first
reply, before anything else, tell the teacher in one or two plain sentences, and offer to update.
{how} Until the teacher has updated or said to go on, change nothing in the course, and do not
"fix" what `classkit validate` reports.
"""


def github_source(root: Path) -> tuple[str, str] | None:
    """("owner/repo", ref) of the GitHub marketplace the plugin was installed from, else None.
    The ref is "HEAD" — the default branch — when the marketplace was added without one."""
    source = installed_from(root)
    if source is None:
        return None
    marketplace, plugins = source
    known = json.loads((plugins / "known_marketplaces.json").read_text(encoding="utf-8"))
    entry = (known.get(marketplace) or {}).get("source") or {}
    repo = entry.get("repo") if entry.get("source") == "github" else None
    if repo is None and isinstance(entry.get("url"), str):
        found = re.fullmatch(r"(?:https://|git@)github\.com[/:]([\w.-]+/[\w.-]+?)(?:\.git)?/?", entry["url"])
        repo = found[1] if found else None
    if not repo:
        return None
    return repo, str(entry.get("ref") or "HEAD")


def fetch(url: str) -> str:
    """A file's text, or "" on any failure. curl as a fallback: on a Mac, Python from python.org
    has no certificates until its installer's "Install Certificates" is run."""
    try:
        with urllib.request.urlopen(url, timeout=TIMEOUT) as response:  # noqa: S310
            return response.read().decode("utf-8")
    except Exception:  # noqa: BLE001
        pass
    if url.startswith("https://") and shutil.which("curl"):
        try:
            done = subprocess.run(["curl", "-fsSL", "--max-time", str(TIMEOUT), url],
                                  capture_output=True, text=True, encoding="utf-8", timeout=TIMEOUT + 2)
            return done.stdout if done.returncode == 0 else ""
        except Exception:  # noqa: BLE001
            return ""
    return ""


def published_version(repo: str, ref: str, name: str) -> str:
    """The version of plugin `name` that the marketplace at repo@ref publishes, or ""."""
    base = f"{RAW}/{repo}/{ref}"
    catalog = json.loads(fetch(f"{base}/.claude-plugin/marketplace.json") or "{}")
    entry = next((p for p in catalog.get("plugins", []) if p.get("name") == name), None)
    if entry is None or not isinstance(entry.get("source"), str):
        return ""
    folder = posixpath.normpath(entry["source"])
    if folder.startswith(".."):
        return ""
    manifest = json.loads(fetch(f"{base}/{folder}/.claude-plugin/plugin.json") or "{}")
    return str(manifest.get("version") or "")


def update_note(root: Path) -> str:
    """The note when GitHub publishes a newer version than the one running; "" otherwise, or on any
    surprise (a convenience: it never stops the rules)."""
    try:
        return _update_note(root)
    except Exception:  # noqa: BLE001
        return ""


def _update_note(root: Path) -> str:
    data = os.environ.get("EVAL_CLASSKIT_DATA") or os.environ.get("CLAUDE_PLUGIN_DATA")
    source = github_source(root)
    if not data or source is None:
        return ""
    repo, ref = source
    manifest = plugin_manifest(root)
    name, running = manifest["name"], str(manifest.get("version", ""))
    key = f"{repo}@{ref}"

    cache = Path(data) / CACHE
    try:
        cached = json.loads(cache.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        cached = {}
    if cached.get("source") == key and 0 <= time.time() - float(cached.get("checked", 0)) < CHECK_EVERY:
        latest = str(cached.get("version") or "")
    else:
        latest = published_version(repo, ref, name)
        try:  # a failed check is kept too, so that an offline computer waits a day, not a request a session
            cache.parent.mkdir(parents=True, exist_ok=True)
            cache.write_text(json.dumps({"source": key, "checked": time.time(), "version": latest}),
                             encoding="utf-8")
        except OSError:
            pass

    version = _versions()
    if not latest or version.key(latest) is None or version.key(running) is None:
        return ""
    if version.key(latest) <= version.key(running):
        return ""
    plugin_id = f"{name}@{installed_from(root)[0]}"
    changes = f"https://github.com/{repo}/blob/{ref}/CHANGELOG.md"
    return f"""

## A newer Class Kit is available

This session runs Class Kit **{running}**, and **{latest}** has been released. In your first
reply, before anything else, tell the teacher in one or two plain sentences and ask whether to update
now; what changed is in {changes}. With their OK, in Bash: run `claude plugin list` to see the scope
`{plugin_id}` is installed at for this folder, then `claude plugin update {plugin_id} --scope <that
scope>`. Then tell the teacher to start a new session — close Claude Code and open it again — for the
new version to load. If they say no, carry on and do not ask again in this session. Never update
without their OK.
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

## Class Kit is not at the version its marketplace offers

This session runs Class Kit **{running}**, and its marketplace (`{marketplace}`) now offers
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
    # One note at most: the course note says why the update matters; the update note, that one exists;
    # the marketplace note, that the marketplace's copy (perhaps pinned) differs.
    note = (course_note(root, course) if course else "") or update_note(root) or version_note(root)
    text = Path(rules).read_text(encoding="utf-8") + note
    if len(text) > limit:
        print(f"class-kit: the course rules are {len(text)} characters, over the {limit} "
              "Claude Code accepts; they were NOT loaded", file=sys.stderr)
        return 3
    sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": text}}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
