# Plugin migration — implementation plan

**Date:** 2026-10-16 · **Decided here:** names, stop rules and go/no-go ·
**Base:** `BGU-CSE/class-framework`
`main` at `24092db` — this repository's history up to that commit is identical to it ·
**Source:** [`dev/reviews/plugin-migration-assessment.md`](reviews/plugin-migration-assessment.md)
(the assessment; read it before this file)

This file is the working plan for every session in this repository. It does not repeat the
assessment: it says what to do, in what order, what to measure, and where this plan departs from the
assessment because the documentation was checked again on 2026-10-16.

---

## Why this repository exists

- The assessment recommends moving the framework to a Claude Code plugin, gated on a short spike.
- Doing that work in a **separate repository** rather than on a branch of `class-framework` was
  proposed (2026-10-16), so that `class-framework` stays untouched while it is tried. It is **not
  yet settled that the plugin is the right approach**. The first job here is therefore to answer
  that question: Phase 1 is a go/no-go trial, and nothing after it starts without a GO. Whether
  `class-framework`'s own courses and teachers move to the plugin is decided outside this
  repository; the trial's results are the evidence for it.
- The repository starts from `class-framework`'s full history (not an empty copy), so fixes made
  there can still be merged here with git, and every later change shows as a diff against the
  original.

## Rules for every session in this repository

1. **You are in FRAMEWORK-DEVELOPER mode.** This repository is never a teacher's course repo. Run
   the Phase 0 setup once per checkout. `dev/CLAUDE.md`'s invariants still hold, except where this
   plan changes one explicitly.
2. **Port, don't rewrite.** Code, tests, agents, skills, commands, schemas and templates move
   across as they are. Changing behaviour needs a reason, recorded in this file or the devlog.
3. **One phase at a time.** Each phase ends at a **gate**: stop and report — what was done,
   what was measured, what is still open — and wait for an OK before starting the next.
4. **Tests stay green at every commit** (`pytest`). Once a plugin directory exists,
   `claude plugin validate --strict` must pass too.
5. **The course layout does not change.** A course built with `class-framework` must work here
   unchanged: `course/` is read and written exactly as today.
6. **Out of scope until Phase 5 is done:** the homework module (paused on purpose), the Gem builder
   and Q-030, and the `[design]` increments in `ROADMAP.md`.
7. **Upstream.** Fixes, and possibly features, may still land on `BGU-CSE/class-framework` `main`
   during the trial. Before starting each phase, merge them:
   `git fetch framework && git merge framework/main`. Never push to `BGU-CSE/class-framework` from
   here.
8. **Where things are recorded.** **What was done, with its commits → [`dev/PLUGIN-LOG.md`](PLUGIN-LOG.md)**:
   append an entry at the end of every working session. Not `dev/_devlog/02-progress.md`, which
   is shared with `class-framework` and would conflict on every merge from it. Trial measurements →
   `dev/reviews/plugin-spike.md`. Decisions → `dev/_devlog/01-decisions.md` (next free number is
   **D-049**; check before using it). Progress → the [Status](#status) table at the end of this
   file, updated in the same commit as the work.
9. **Git.** One branch per phase (`phase-1-spike`, `phase-3-restructure`, …), a pull request, merged
   only once approved. If a tag push is refused from a cloud session, the tag is created in
   GitHub instead.
10. **Every operating system.** The plugin must work on Windows (with Git Bash, which comes with Git
    for Windows), macOS and Linux. Write nothing that assumes one of them. See
    [Windows, macOS and Linux](#windows-macos-and-linux).

---

## What changed since the assessment

Checked against the Claude Code documentation on 2026-10-16 (hooks, plugin loading, plugin
components, organization settings, plugin evals, marketplace hosting). These override the
assessment where they disagree.

| # | The assessment says | The documentation says | So, in this plan |
|---|---|---|---|
| 1 | Size limit on hook-injected context is **[unverified]** (§6.2, §10); check 3 tests the rules "at the full current size" | A hook's `additionalContext` is **capped at 10,000 characters**. Past that, Claude gets a file path and a 2,000-character preview and is not asked to read the file. No setting raises the cap | Root `CLAUDE.md` is 16,371 bytes; its teacher section alone is 14,054 characters. The core rules must be condensed to **≤ 8,000 characters** (a margin under the cap) in `plugin/rules/core.md`; everything else goes in a reference skill. Check C3 below replaces check 3 |
| 2 | `CLAUDE_ENV_FILE` is an **[inference]** (§6.1) | It exists for SessionStart hooks. Lines written to it run before **every** later Bash command in the session | The bootstrap hook writes `export CLASSKIT_VENV=…` there; the `classkit` wrapper reads it |
| 3 | Bootstrap must work in evals (§6.9) | In an eval run, Bash commands run in an OS sandbox: network only to granted domains, the home directory and Claude Code's configuration unreadable. **Hooks run outside the sandbox** | Install dependencies **in the hook, never in the wrapper**. The wrapper only runs, or fails with a clear message. Check C2 must grant Bash |
| 4 | "Enabled in project settings but isn't installed here" (§3) | True only for plugins with an **external** source. A plugin the marketplace lists by **relative path** loads from the marketplace copy once the repository's `extraKnownMarketplaces` applies, which happens after the folder is trusted | A TA who clones a course repo and trusts the folder gets the plugin with **no install command**. Verified by check C7 |
| 5 | No per-project version pin; mitigation is a warning only (§5.3, §6.7) | A GitHub or git marketplace source can name a `ref` (a branch or tag), and when a source declared in settings changes, Claude Code re-fetches the marketplace. That this works from a course repo's `extraKnownMarketplaces` is read from the docs, not yet tried | A course repo can pin the framework version by `ref` in its own settings, so upgrading becomes a commit in the course repo. Caveats: registration is per user (one person in two courses pinned differently flips between them); only after folder trust; not in cloud sessions; the re-fetch is in the background. **New check C7.** The §6.7 version warning stays as a backstop |
| 6 | — | SessionStart fires on `startup`, `resume`, `clear` and `compact` | The rules hook has **no matcher**, so the rules come back after `/clear` and after compaction |
| 7 | Venv in `${CLAUDE_PLUGIN_DATA}` (§6.1) | That directory survives plugin updates | Name the venv after a hash of the dependency list (`venv-<hash>`), so a release that adds a dependency gets a fresh venv |
| 8 | Bare `/plan-units` probably doesn't resolve (§5.4) | Plugin skill commands are `/<plugin>:<name>`; the prefix stays | The assessment's assumption stands |

Two repository facts the plan relies on (measured at `24092db`):

- There is **no `src/classkit/__main__.py`**, so `python -m classkit` does not work. The plugin does
  not need it: its wrapper runs a small launcher script instead (Phase 1, Build 3).
- **7 of the 9 test files** compute the framework root as `Path(__file__).resolve().parents[1]`.
  Phase 3 must point each at `plugin/`.

---

## Windows, macOS and Linux

Checked at `24092db` on 2026-10-16, after the first session on the test machine ran on Windows. The framework was
written on a Mac; this is everything that assumes one system, and where each is handled.

| Where | What is system-specific today | Handled |
|---|---|---|
| Teacher instructions and permissions: root `CLAUDE.md`, `GETTING-STARTED.md`, `dev/FRAMEWORK-SPEC.md`, `.claude/settings.json` | `.venv/bin/classkit`, `.venv/bin/pip`, `python3` — the Mac and Linux forms | **Now:** the Windows forms (`.venv/Scripts/…`, `python`) are added beside them, and the five pre-allowed read-only commands are allowed in both forms. **Steps 4, 5 and 8:** in the plugin, `classkit` is a plain command on every system (the plugin's `bin/`), so all of these become bare `classkit` and the `.venv` forms disappear |
| Developer docs: `dev/MANUAL-TESTING.md` (35 places) and this plan | The same forms | **Now:** this plan's Phase 0 gives both forms, and `MANUAL-TESTING.md` opens with a note to read `.venv/bin/` as `.venv/Scripts/` and `python3` as `python` on Windows. **Step 8:** both forms written out |
| Python code | Mostly system-neutral: commands run without a shell, external tools are found with `shutil.which`, approval hashes ignore line endings, and paths written into committed files use forward slashes (`as_posix()`). **Exceptions:** `scaffold.py`'s course-log entry uses `str()`, so on Windows it writes backslashes into `LOG.md`; two places that only print — `validate`'s finding locations and `scaffold`'s report — show backslashes too. **Encoding** (session 2): when Claude runs `classkit`, its output is piped, so Python uses the Windows code page; `ingest` crashes on `→`, and the others print em dashes Claude can't read. `classkit write` reads its input the same way (found in `cli.py`, not yet seen on Windows) | **Phase 0b.** Worth reporting upstream: all of these exist in `class-framework` today |
| Line endings | There was no `.gitattributes`. Git for Windows converts text files to CRLF on checkout by default, and a shell script with CRLF fails in Git Bash. In a course repo cloned on Windows, both text materials (`.md`, `links.md`) and the committed `ingested/` files get CRLF, so `ingest` and `status` report changes and hand edits that aren't there (confirmed in session 2) | **Now:** this repository's `.gitattributes` keeps `*.sh` and `plugin/bin/*` at LF. **Phase 0b:** `classkit scaffold course` also writes a `course/.gitattributes` into course repos, create-only |
| The plugin's own scripts | Not written yet | **Phase 1:** written for every system from the start (Build 3, 5 and 6) |
| Evals (C2) | The eval sandbox does not exist on native Windows | Run C2 under WSL2 or on a Mac |
| Long paths | Windows limits a path to 260 characters unless long paths are turned on (that needs administrator rights). The deepest file `pip` installs (from `lxml`, needed by `python-docx` and `python-pptx`) sits about 199 characters deep under the plugin's data folder for the test machine's 5-character user name; under a longer path the install failed in session 7 | **C1** measures it with the real data folder. If it fails, shorten the venv folder's name, or tell teachers to turn on long paths |
| LibreOffice | On Windows and macOS, its `soffice` command is usually not on the `PATH`, so `doctor` may report it missing although it is installed. True of `class-framework` today, too | Noted only; revisit if a teacher hits it |

---

## Target layout

**Plugin name: `class-agent-kit`** (decided 2026-10-16), shown in the UI as "Class Agent
Kit" through `displayName`. Commands become `/class-agent-kit:<name>`, for example
`/class-agent-kit:plan-units`. The command-line tool keeps its name, `classkit`. **Marketplace
name: `agent-based-class`** (provisional until Phase 2). Names must be kebab-case and may not start
with `claude-`.

```
agent-based-class-plugin/            ← developer repository = the marketplace
  .claude-plugin/marketplace.json    marketplace "agent-based-class"; one plugin, source "./plugin"
  plugin/                            ← the only thing teachers receive
    .claude-plugin/plugin.json       name "class-agent-kit", displayName "Class Agent Kit", version pinned
    agents/  skills/  commands/
    hooks/hooks.json                 SessionStart: bootstrap.sh, rules.sh (no matcher)
    hooks/bootstrap.sh               ensures the Python venv, publishes it via CLAUDE_ENV_FILE
    hooks/rules.sh                   injects rules/core.md when the project has course/course.yaml
    bin/classkit                     wrapper: the venv's python runs scripts/run_classkit.py
    scripts/run_classkit.py          launcher: puts plugin/src on sys.path, calls classkit's main()
    rules/core.md                    the always-on teacher rules, ≤ 8,000 characters
    requirements.txt                 = pyproject dependencies (a test keeps the two equal)
    schemas/  templates/  methodologies/  defaults/  src/classkit/
  dev/  tests/  pyproject.toml  CLAUDE.md  README.md   ← never shipped
```

---

## Phase 0 — Setup

**Where:** each checkout of this repository, in a working session. **Branch:** none for the setup
itself. The log entry and the Status row are always committed, on a branch with a pull request.

1. Clone this repository, then add the upstream and block pushing to it:
   `git remote add framework https://github.com/BGU-CSE/class-framework`, then
   `git remote set-url --push framework DISABLED`. Fetching and merging still work. On Windows, if
   the clone was made before `.gitattributes` existed, run
   `rm .claude/hooks/report-mode.sh && git checkout -- .claude/hooks/report-mode.sh` once so the
   script gets LF line endings. `git checkout` alone is not enough: it skips a file git considers
   unchanged (found in session 2).
2. Create the environment. In what follows, **`<venv-bin>`** means `.venv/bin` on macOS and Linux,
   and `.venv/Scripts` on Windows.
   - macOS and Linux: `python3 -m venv .venv`
   - Windows, in Git Bash: `python -m venv .venv` (or `py -3 -m venv .venv`)

   Then `<venv-bin>/pip install -e ".[dev]"` and `<venv-bin>/classkit mode developer`, then
   **restart the session** — the mode hook reads the marker only at session start.
3. `<venv-bin>/pytest -q`. Record the count (the assessment measured 405 at `24092db`, on a Mac).
   On Windows, list every test that fails **only** there: that is a Windows bug in today's
   framework, not a migration problem. Which to fix here is to be decided; report them upstream as well.
4. Update Claude Code to the latest version (`claude --version`). The documentation this plan
   relies on was read on 2026-10-16, and some of the features it uses are recent.
5. **The real test course is left alone for now.** A real course repository exists for testing;
   it is not touched until check C4, where the course is built through the plugin. Checks C1, C3,
   C6 and C7 use a throwaway course made with `classkit scaffold` outside this repository.

**Gate 0:** tests green — or, on Windows, every failure listed and shown to be Windows-only.

---

## Phase 0b — Windows fixes (before Phase 1)

**Decided 2026-10-16.** **Where:** the Windows test machine, because the fixes must be checked
on Windows. **Branch:** `phase-0b-windows`.

Phase 0 found 9 tests that fail only on Windows, and two problems the tests miss (`dev/PLUGIN-LOG.md`,
session 2). Fixing them before the trial means the tests pass on the Windows test machine at every later
gate, and check C4 doesn't run into them. These are bug fixes, not changes of behaviour. **Make one
small commit per fix**, so each can be taken into `class-framework` with `git cherry-pick`: the two
repositories share history.

1. **UTF-8 in and out.** At the start of `classkit`'s `main()` in `cli.py`, set `sys.stdout`,
   `sys.stderr` and `sys.stdin` to UTF-8 (`.reconfigure(encoding="utf-8")`), whatever the console's
   code page. This fixes the `ingest` crash and the unreadable em dashes. `stdin` matters as much:
   `classkit write` reads the text that agents pipe into it, so on Windows that text would be
   decoded in the code page and saved garbled. That one was found by reading `cli.py`, not yet seen
   on Windows — check it in step 5. **Test:** run the CLI in a subprocess with
   `PYTHONIOENCODING=cp1256`, which reproduces the Windows code page on any system, and assert that
   `ingest`'s report and a `write` of non-ASCII text both come through intact.
2. **Forward slashes.** `as_posix()` instead of `str()` in `scaffold.py` (the course-log entry),
   `validate.py` (finding locations) and `cli.py` (the scaffold report).
3. **Course repos keep LF line endings.** `classkit scaffold course` writes `course/.gitattributes`
   (`* text=auto eol=lf`), create-only, from a new template beside `templates/course/gitignore` —
   the same way it writes `course/.gitignore`. This stops the false "edited by hand" findings in a
   course cloned on Windows. A course repo that already exists needs the file added by hand,
   followed once by `git add --renormalize .`. **Test:** scaffold creates it; a re-run leaves it
   untouched.
4. **Tests.** The four tests that write their setup file with `write_text()` write it with LF
   (`newline="\n"`); the tests were wrong, not `classkit`. The two file-permission tests are skipped
   on Windows (`skipif(sys.platform == "win32", reason=…)`).
5. **Check on Windows:**
   - `pytest`: everything passes except the two skipped permission tests.
   - With a throwaway course (as in session 2): `classkit ingest` run through a pipe in Git Bash
     works; a `classkit write` of text with `→` and Hebrew, piped in, is saved byte for byte; and a
     CRLF clone of an LF-committed course that has the new `.gitattributes` shows no false edits.
   - Then `pytest` on Linux or macOS as well (a cloud session can run Linux): everything passes.
6. **Log:** a session entry listing each commit and what it fixes, so each can be picked.

**Gate 0b:** tests pass on Windows (only the two permission tests skipped) and on Linux or macOS,
and the three throwaway-course checks in step 5 pass.

---

## Phase 1 — The trial (go/no-go)

**Branch:** `phase-1-spike`. **Copy, do not move:** the original files stay where they are, so
nothing at the repository root changes in this phase.

**Stop rules confirmed** on 2026-10-17 (Gate 1, below). **At the start,** record
`claude --version` and the Python version in `dev/reviews/plugin-spike.md`: the command-line tool
updates itself, so the version can change between sessions.

**What runs where.** The plugin is built, and everything that can run without a person is run, in
the working session, such as `claude plugin validate` and one-shot `claude -p` runs. Some checks need
a person in a live session: a second session, `/clear` and `/compact`, a "trust this folder" prompt,
the desktop app. For those, exact steps are given to follow in Git Bash or the desktop app, and what
was seen is reported back.

### Build

1. **Copy** `.claude/agents/`, `.claude/skills/`, `.claude/commands/`, `schemas/`, `templates/`,
   `methodologies/`, `defaults/` and `src/classkit/` into `plugin/`. **Do not copy**
   `.claude/hooks/report-mode.sh` or `.claude/settings.json`: the mode hook means nothing inside a
   plugin, and a plugin cannot ship permissions.
2. **Manifests.** `plugin/.claude-plugin/plugin.json`: `name`, `version: "0.1.0-spike"`,
   `description`, `author`. Root `.claude-plugin/marketplace.json`: `name`, `owner`, and one plugin
   entry with `source: "./plugin"`. The entry name and the manifest name must be the same.
3. **`plugin/scripts/run_classkit.py`**, a launcher of a few lines: put the folder `src/` beside
   it (found from the launcher's own `__file__`) at the front of `sys.path`, then
   `from classkit.cli import main` and `raise SystemExit(main())`. Python works out its own path
   on every system, so the wrapper never has to build a `PYTHONPATH`, whose separator and path
   style differ between Windows and the rest.
4. **`plugin/requirements.txt`**, the same packages as `pyproject.toml`'s `dependencies`.
5. **`plugin/hooks/bootstrap.sh`** (SessionStart; runs in Git Bash on Windows):
   - **Find Python:** try `python3`, then `python`, then `py -3`, and use the first whose
     `--version` runs and reports 3.10 or later. On Windows, `python3` may be the Microsoft Store
     placeholder, which does not run Python — hence checking the version, not just the name. If
     none is found, write a clear message to stderr and exit 0 — never block the session.
   - `venv="$CLAUDE_PLUGIN_DATA/venv-<first 12 hex characters of sha256(requirements.txt)>"`, with
     forward slashes. If it doesn't exist: `<python> -m venv "$venv"`, then the venv's own python
     `-m pip install -r requirements.txt`. The venv's python is `bin/python` on macOS and Linux and
     `Scripts/python.exe` on Windows — look for both. On failure, delete the partial directory.
   - If `CLAUDE_ENV_FILE` is set, append `export CLASSKIT_VENV="$venv"` to it.
   - Print **nothing** to stdout (stdout becomes context). Log to
     `$CLAUDE_PLUGIN_DATA/bootstrap.log`, including the system, the Python found, and how long the
     install took.
6. **`plugin/bin/classkit`** (POSIX `sh`, LF line endings — `.gitattributes` enforces it): find the
   plugin root from the script's own path; take the venv from `CLASSKIT_VENV` and its python from
   `bin/python` or `Scripts/python.exe`. If none is there, print what is wrong and how to fix it
   (start a new session; see `bootstrap.log`) and exit non-zero. Otherwise
   `exec "<venv python>" "$root/scripts/run_classkit.py" "$@"`. Running from the plugin's `src/`
   keeps `find_framework_root()`'s `__file__` fallback pointing at `plugin/`, so the venv holds
   dependencies only (assessment §6.1).
7. **`plugin/rules/core.md`** — a first condensation of the root `CLAUDE.md`'s "How to work" section
   and teacher sections, **≤ 8,000 characters**. Keep: vocabulary, ID conventions, "the teacher
   works in the chat — you run `classkit`" (bare `classkit` only), report findings faithfully, the
   teacher is the authority, the agent rules (no invented resources, never copy private text, fix
   what you caused, never approve). Put the long materials rules and command table in a reference
   skill, `plugin/skills/course-reference/SKILL.md`. The wording is reviewed in Phase 2;
   the trial only needs the real size and the mechanism.
8. **`plugin/hooks/rules.sh`**: if `$CLAUDE_PROJECT_DIR/course/course.yaml` exists, print the
   SessionStart JSON with `additionalContext` set to `core.md` (JSON-escape it with
   `python3 -c 'import json,sys; …'`). Otherwise exit 0 silently. If `core.md` is over 10,000
   characters, fail loudly on stderr rather than let it be truncated.
9. **`plugin/hooks/hooks.json`**: one `SessionStart` entry, **no matcher**, with both hooks;
   bootstrap gets `"timeout": 300`.
10. `claude plugin validate --strict ./plugin` and `claude plugin validate .` both pass.

### Measure — one section per check in `dev/reviews/plugin-spike.md`

For each check, record what was run, the result with numbers, and a verdict (pass / fail / pass
with a cost).

| Check | What to do | Passes if |
|---|---|---|
| **C1** — `classkit` as a bare command | On a machine or user account with no plugin venv, in a **new, empty git repository** (no course yet — as a teacher starts): run `claude --plugin-dir <repo>/plugin`, show `command -v classkit` (it must be the plugin's `bin/classkit`), and ask Claude to create a new course with `classkit scaffold course`. Note whether the course rules are in context — they should not be, since there was no `course/` when the session started — then `/clear` and check again. Then start a second session there: `classkit status`, and are the rules present? Record the plugin data folder's real path, its longest path's length, and whether the install hit Windows' 260-character limit. **Do it on Windows (Git Bash) and on a Mac** — the Windows test machine and a Mac. **The Mac half is deferred** (see [Decided at the end of Phase 1](#decided-at-the-end-of-phase-1)) | It runs on both: the plugin creates the course; the first session's install time is recorded; the second session needs no install. The rules are expected absent in session 1 until `/clear`, and present after `/clear` and in session 2 (C3 tests them in depth) |
| **C2** — inside evals | A minimal eval case in `plugin/evals/`: a `scaffold_script` copies a small fixture course (generated once with `classkit scaffold`, committed in the case directory); the prompt asks Claude to run `classkit validate` and report. **Grant Bash.** Run with `--max-cost-usd 2`, **under WSL2 or on a Mac** — the eval sandbox does not exist on native Windows. On the Windows test machine, WSL first needs `sudo apt install python3-venv` (session 4); to be confirmed before WSL is changed | `classkit` runs inside the sandbox. Record the per-run install cost and time. If the sandbox cannot read the venv, record exactly what failed |
| **C3** — the core rules reach the session | In a course repo, ask something only `core.md` answers (which words are banned; the ID format of a Guiding Question). Repeat after `/clear` and after `/compact`. Then, in a directory with no `course/`, confirm nothing was injected | Answered correctly every time; silent without `course/`. Record `core.md`'s size |
| **C4** — make a course with the plugin. **Run it last**: it is the slowest and uses the most model time, and it is pointless if a plumbing check failed | To be confirmed before the real test course repository is touched. **It must hold only the course**: a course repo made by cloning `class-framework` also carries the old framework's `.claude/` commands, agents and skills and its `CLAUDE.md`, which Claude Code loads next to the plugin, and its `schemas/` and `methodologies/`, which `classkit` prefers over the plugin's because `find_framework_root()` looks in the current folder first (session 7). Use a course-only copy — the framework files removed on a branch, as Step 9 does, or a fresh repo. Clone it outside this repository and open it with `claude --plugin-dir <repo>/plugin`. Work through `dev/MANUAL-TESTING.md` as a teacher would, from Step 1 (initialize) to Step 3-units (`/plan-units`), using the plugin's commands (`/class-agent-kit:ingest`, `/class-agent-kit:plan-syllabus`, `/class-agent-kit:plan-units`). After each step, also run the **original** tool from this repository's root (`<venv-bin>/classkit validate`, `status`, `doctor`) on the same files, and diff its output with the plugin's. The copied prompts still name commands without the prefix; where that breaks a step, record it (Phase 5 fixes it) and continue by invoking the prefixed command directly | Every step behaves as `MANUAL-TESTING.md` expects, the agents load their skills, the write path still refuses overwrites, and the two tools' outputs are identical or every difference is explained |
| **C5** — a second person installs it | Push the branch. On a different machine, a second person with access to this repository (a collaborator) runs `/plugin marketplace add shiraradshilo/agent-based-class-plugin#phase-1-spike`, then `/plugin install class-agent-kit@agent-based-class`. Then repeat the install in the **desktop app's Code tab** (**+** → Plugins → Add plugin), which teachers are likely to use | It installs both ways with their ordinary git credentials. Record what they needed (for example `gh auth login` and `gh auth setup-git`) |
| **C6** — permissions | In the test course's `.claude/settings.json`, allow `Bash(classkit validate:*)`, `Bash(classkit status:*)` and `Bash(classkit doctor:*)` | Those commands run without a permission prompt |
| **C7** — per-course pin, no install step | In the test course's `.claude/settings.json`: `extraKnownMarketplaces` → `agent-based-class` with `source: {source: "github", repo: "shiraradshilo/agent-based-class-plugin", ref: "<branch A>"}`, and `enabledPlugins` → `"class-agent-kit@agent-based-class": true`. On a machine that has never installed the plugin, trust the folder. Then point `ref` at a branch B whose `plugin.json` version differs, and reopen. Repeat the opening in the **desktop app's Code tab** | The plugin loads with **no install command**. After the `ref` changes, the B version loads. Record when: immediately, after `/reload-plugins`, or at the next session |

### Found during the checks — to fix

Problems the checks turned up, with where each is handled. Details in `dev/reviews/plugin-spike.md`.

| Found in | Problem | Handled |
|---|---|---|
| C1, session 1 | `rules.sh` looks only for `course/course.yaml`, but `classkit` also accepts a course at the repository's top level; such a course never gets the rules | **Done** (session 12): the hook looks wherever `classkit` does — `course.yaml` in the project folder, or `course/course.yaml` there or in any folder above; `tests/test_plugin_rules_hook.py` |
| C1, session 1 | No command creates a course, and in a new course's first session the rules are absent, so conventions can slip (Claude put the course at the top level) | **Done early (session 16):** `/class-agent-kit:new-course` asks for the course's details, scaffolds it in `course/` (never `--path`), validates, and tells the teacher to start a new session; the plugin's `classkit scaffold course` now ends with the same reminder. Phase 2 may still reshape it |
| C1, session 1 | Claude Code on the Windows test machine runs in Auto mode, which approves routine actions without asking | **C6** runs in the default permission mode |
| C1, session 1 | The data folder is `class-agent-kit-inline` with `--plugin-dir`, 11 characters longer when installed from the marketplace | **C1's long-path measurement** allows for the longer name |
| C1, session 2 | Claude suggests commands without the plugin prefix (`/ingest`), taken from `classkit`'s own messages and the copied prompts; Claude Code's own prompt suggestions then offer them, ready to send (session 13) | **Step 5** (renaming, including the Python code's messages) |
| C1, session 2 | `classkit doctor` reports a "working mode", and `classkit mode` acts on the plugin's own folder: it refuses with a `.gitignore` error, or writes `dev/.developer` into the plugin | **Phase 6** (retire the two hats; corrected in session 15 from Step 5): under the plugin, doctor drops the line and `classkit mode` says it does not apply |
| Session 12 (raised as a question) | **Python 3.10+ must already be installed**; the plugin builds its venv but cannot install Python. Without it, the hook writes "no Python 3.10 or later found" to stderr and exits 0, which Claude Code probably does not show (unverified); `bin/classkit` then says "Start a new Claude Code session: the plugin installs it", wrong advice in that case | **Deferred (session 13)**; C4 first. Setup instructions tell teachers to install Python 3.10+ (and Git Bash on Windows) either way. Was: before C5, `bin/classkit` names the missing Python and where to get it, and the hook's message reaches the teacher |
| C6 | On Windows Claude may run `classkit` through its **PowerShell** tool: PowerShell finds the plugin's extensionless shell script and Windows asks which program should open it; nothing runs, and the course's `Bash(…)` permissions do not apply | **Before C4.** **Done** (session 13, tested on Windows): the `rules/core.md` line is added; with the course setting below, Claude has no PowerShell tool: the course's `.claude/settings.json` sets `"env": {"CLAUDE_CODE_USE_POWERSHELL_TOOL": "0"}` (documented; a plugin's own settings cannot), plus a line in `rules/core.md` that `classkit` runs through Bash. Not a `bin/classkit.cmd`: on Windows PowerShell commands do not receive `CLAUDE_ENV_FILE` variables whose value holds `/` or `\`, so it would never see `CLASSKIT_VENV`. Test on Windows whether the setting needs a restart |
| Session 13 (finding 11) | A course's `.claude/settings.json` applies only when Claude starts in the folder that holds it (the repository's top folder); started inside `course/`, the rules still load, but the permissions and the PowerShell switch do not | Teacher instructions: start Claude from the course repository's top folder |
| C7 (finding 12) | The first session after a course's settings bring the plugin in runs none of its start-up hooks: no rules, no Python environment, until `/clear` or a new session | Phase 2, with finding 3: whatever sets up a course tells the teacher to `/clear` or restart |
| C7 (finding 13) | After the course's `ref` changes, every new session starts without the plugin (`plugin-cache-miss`); `/reload-plugins` loads the new version, without the rules | **Fixed in the plugin and tested on Windows (session 15):** at session start the plugin compares its version with its marketplace's; Claude tells the teacher and, on their yes, runs the update; a new session loads it. Not fixable in the plugin: a plugin never installed does not load after a version change — Phase 8 instructions: install once per computer |
| Session 15 (finding 14) | A marketplace added for the whole computer (the desktop app's Add marketplace writes it to `~/.claude/settings.json`) overrides a course's `ref`; computer-wide install and per-course pinning do not combine | **Decided (session 17): install once per computer.** Versions move by release, and the check offers the update; no per-course pin, so the course settings that `classkit scaffold course` writes (Phase 4) carry no `ref`. The cost, a course not held on one version, is made visible by the course's recorded version (Phase 4), not prevented |
| C2 (finding 15) | In an eval run the plugin's `bin/` is not on the Bash tool's `PATH`; the bare `classkit` is not found | **Phase 7:** the step that starts `claude plugin eval` (CI, or a developer's shell) puts the plugin's `bin/` on `PATH`; the run inherits it |
| C2 (finding 16) | The eval sandbox cannot see the plugin's data folder, so `classkit` finds no Python | **Phase 4:** `bootstrap.sh` builds the venv in a folder named by an `EVAL_` variable when one is set — eval runs only; inside the plugin folder worked (session 17). **Phase 7:** the eval cases set it |
| Session 12 (docs) | **Git Bash is required on Windows** (finding 10): Claude Code can run on Windows without it (PowerShell only), but the plugin's hooks are Bash scripts, so there would be no install and no rules | State it as a prerequisite beside Python 3.10+ (finding 8) |
| Session 12 (docs) | Plugins with a `bin/` folder **cannot be installed through claude.ai, Cowork or an organisation's claude.ai plugin settings**; a marketplace install into Claude Code is unaffected | **Gate 1:** the distribution route for teachers |

### Decided at the end of Phase 1

Items left open while the checks run. Each is decided together with Gate 1.

| Item | Why it matters | Options |
|---|---|---|
| **C1 on a Mac** (deferred 2026-10-17) | C1 asks for `classkit` to run from the plugin on Windows **and** on a Mac. The Windows half runs on the test machine. Linux was run by hand in session 8 and shares the shell scripts and path style with macOS, but it is not macOS (different system tools, Python installs and security prompts). Concretely (session 12): the `python3` Apple's developer tools install is, as far as known, **3.9** — below the plugin's 3.10 minimum — so a Mac with only that Python gets "no Python 3.10 or later found", and on a fresh Mac `python3` may only offer to install those tools. Hooks run under Apple's **bash 3.2**; the hook scripts were checked and use no bash 4 features | **Done (session 17):** the plugin was installed and used on a Mac on 2026-10-29, reported to behave as on Windows; first-run time and Python version not recorded |

### Gate 1 — go/no-go

Confirmed on 2026-10-17, before Phase 1 started. Do not build around a failure.

- **C1 or C3 fails** → stop. Either fall back to a prerequisite install (assessment §6.1, option A)
  or abandon the migration.
- **C4: a teacher step doesn't work through the plugin, or a difference can't be explained** →
  stop until it is fixed or explained. A step that breaks only because a prompt names a command
  without the prefix is not a stop; record it for Phase 5.
- **C2 fails** → not a stop for the migration itself, but agent evals are off the table, and that
  removes the benefit in assessment §4.4. Whether the rest is still worth it is then decided.
- **C7 fails** → not a stop. The §6.7 version warning becomes the only protection, as in the
  assessment.
- **C5 or C6 problems** → fix them; they are not stops.

**Outcome (session 17, 2026-10-31): GO.** No stop rule was hit: C1 passed (Windows; Mac reported),
C3 passed, C4 accepted, C2 passed on Linux with two adjustments (findings 15–16), C5 reported, C6
and C7 passed. Decided with it:

- **Teachers install the plugin once per computer** (finding 14; see the findings table).
- **`BGU-CSE/class-framework` stays as it is for now**; what becomes of it is decided later.
- **A changelog per release** is needed (assessment §6.7). Phase 2 records it in the spec.
- **The marketplace name is deferred.** Command names do not depend on it. Changing it before
  teachers have the plugin costs almost nothing; after, every teacher reinstalls and every course's
  settings change. It must be decided before Phase 8.
- Still open, for Phase 2: whether a teacher can replace a plugin agent with their own (the
  `agents:` override in `course.yaml`, assessment §6.5).

---

## Phases 2–10 — after a GO

These follow the assessment's §9, steps 2–10, with these changes:

- **Step 2 (specify).** Also record the separate-repository decision and what becomes of
  `BGU-CSE/class-framework` afterwards — archived, transferred, or replaced by this repository.
  That part is decided outside this repository. Fix the marketplace name (the plugin name
  is already decided). The decision is **D-049**, or the next free number.
- **Step 3 (restructure).** Delete the spike copies, then `git mv` the originals into `plugin/` — do
  not merge copies with originals. Point the 7 tests that use `parents[1]` at `plugin/`, and point
  `pyproject.toml`'s `packages` at `plugin/src/classkit`. **Bring forward the `CLAUDE.md` swap from
  Step 6:** the root `CLAUDE.md` becomes the developer's in this same commit, because the teacher
  rules no longer live at the root, and no session here should read them as its own instructions.
- **Step 4 (runtime).** Harden the trial's hooks and wrapper, with tests. `classkit scaffold
  course` writes the course repo's `.claude/settings.json`, create-only: the allow rules,
  `enabledPlugins`, and `extraKnownMarketplaces` — with a `ref` if C7 passed. Then the methodology
  search path, the framework version recorded in `course.yaml`, and `skills:` frontmatter on the
  agents. Also from [Windows, macOS and Linux](#windows-macos-and-linux): the teacher-facing
  `.venv/bin/…` and `.venv/Scripts/…` forms become bare `classkit` (the other Windows fixes are
  done in Phase 0b).
- **Step 5 (namespacing).** About 330 live command references in 38 files (counted at `24092db`,
  excluding `dev/_devlog/` and `dev/reviews/`). **The Python code too:** `classkit status` and
  other messages name commands without the prefix ("run /plan-syllabus"; session 7).
- **Step 6 (retire the two hats).** As in the assessment, minus the `CLAUDE.md` swap done in Step 3.
- **Step 7 (tests and CI).** There is no CI today. Add a GitHub Actions workflow that runs `pytest`
  on **Windows, macOS and Linux**, plus `claude plugin validate --strict`. Run the eval suite by
  hand with `--max-cost-usd`, not on every push.
- **Step 8 (teacher documentation).** `GETTING-STARTED.md` and `MANUAL-TESTING.md` cover Windows
  (Git Bash) as well as macOS and Linux.
- **Step 9 (migrate the real course).** Decided outside this repository, and only after Step 8.
- **After Step 5:** the homework module comes back, written in plugin form.

---

## Status

| Phase | State | Notes |
|---|---|---|
| 0 — Setup | done | Gate 0 met on Windows terms: 396/405 pass, 9 Windows-only failures (`dev/PLUGIN-LOG.md` session 2). Step 4 done: Claude Code 2.1.301 on the Windows test machine, `claude --version` works in Git Bash (session 5) |
| 0b — Windows fixes | done | Gate 0b met: Windows 407 passed + 2 skipped; Linux 409 passed; the encoding test proven to catch the bug — `dev/PLUGIN-LOG.md` session 4 |
| 1 — Trial (go/no-go) | **done — GO** (session 17) | Build done (session 7) and reviewed, with one fix and a Linux run (session 8); C1 **passed on Windows** (sessions 10–12; Mac deferred); C3 **passed on Windows** (session 12); C4 **accepted as passed** (session 15); C6 **passed through Bash** (session 12); finding 9, PowerShell, **fixed and tested** (session 13); C7 **works, with an install and an update command** (findings 12–13; terminal and desktop app; session 13); C1 and C5 **on a Mac, reported** (session 17); C2 **passed on Linux, with two adjustments** (findings 15–16; session 17); finding 14 **decided** (session 17). All checks done; Gate 1: **GO** — `dev/reviews/plugin-spike.md` |
| 2 — Specify | next | |
| 3 — Restructure | waiting for GO | |
| 4 — Runtime | waiting for GO | |
| 5 — Namespacing | waiting for GO | |
| 6 — Retire the two hats | waiting for GO | |
| 7 — Tests and CI | waiting for GO | |
| 8 — Teacher documentation | waiting for GO | |
| 9 — Migrate the real course | waiting for GO | Decided outside this repository |
| 10 — Review and re-test | waiting for GO | |
