# Plugin migration — log

What was done in this repository, session by session, with its commits. **Newest last.**

**Append an entry at the end of every working session:** what happened, what was decided, the
commits (short hash, what each did, and its pull request), and what's next. Keep it factual, and say
what was verified and what was only reported.

This log is kept apart from `dev/_devlog/02-progress.md` on purpose. That file is shared with
`BGU-CSE/class-framework`, and appending to it here would conflict on every
`git merge framework/main`.

---

## Session 1 — 2026-10-16

**Where:** a claude.ai cloud checkout (Linux). **Base:** `BGU-CSE/class-framework`
`main` at `24092db`.

### What happened

- **The assessment reviewed.** The plugin-migration assessment of 2026-10-11 was checked against
  the Claude Code documentation. Several of its open questions now have answers: hook context is
  capped at 10,000 characters, `CLAUDE_ENV_FILE` exists, the eval sandbox blocks the network,
  plugins listed by relative path load without an install, and a course can pin the plugin version
  by marketplace `ref`. Recorded in `dev/PLUGIN-MIGRATION.md`, "What changed since the
  assessment".
- **This repository created.** Doing the migration in a separate repository was proposed. This
  one was created (private) and seeded with `class-framework`'s full `main`
  history: 104 commits, ending at `24092db`. The tag `pre-plugin` could not be pushed from the
  cloud session (HTTP 403), so the plan names the commit instead.
- **The plan written:** `dev/PLUGIN-MIGRATION.md` — rules for every session, Phase 0 (setup),
  Phase 1 (the go/no-go trial, checks C1–C7), and Phases 2–10.
- **Windows, macOS and Linux.** The first session on the test machine ran on Windows, so the
  framework was checked for anything that assumes one operating system. The findings, and where
  each is handled, are in the plan's section "Windows, macOS and Linux".

### Decisions

Recorded here and in the plan; they become numbered decisions in Phase 2.

- Names, stop rules and go/no-go are decided in this repository. Whether
  `class-framework`'s own courses and teachers move to the plugin is decided outside it.
- Plugin name **`class-agent-kit`** (display name "Class Agent Kit"); commands become
  `/class-agent-kit:<name>`. The command-line tool keeps the name `classkit`. The marketplace name
  `agent-based-class` is provisional.
- The homework module is paused until after Phase 5.
- The real test course repository is left alone until check C4, which builds a course through the
  plugin (`MANUAL-TESTING.md`, Step 1 to Step 3-units).
- The plugin must work on Windows (with Git Bash), macOS and Linux.
- Nothing is ever pushed to `BGU-CSE/class-framework` from here; only this repository changes.

### Commits

| Commit | What | Pull request |
|---|---|---|
| `00e4bda` | The plan; the assessment, unchanged, in `dev/reviews/`; a note at the top of `CLAUDE.md` saying this repository is never a course repo | #1, merged as `5886805` |
| `2210264` | The decisions: ownership, the plugin name, Phase 0 without a real course, C4 builds a course | #2, merged as `918193c` |
| `63cedd7` | Windows, macOS and Linux: `.gitattributes` (shell scripts keep LF line endings); the Windows forms beside the Mac ones in `.claude/settings.json`, `CLAUDE.md`, `GETTING-STARTED.md`, `dev/FRAMEWORK-SPEC.md` and `dev/MANUAL-TESTING.md`; the plan's rule 10 and its "Windows, macOS and Linux" section. `pytest`: 405 passed (Linux) | #3, merged as `af4ccf9` |
| this commit | This log; the plan's rule 8 points to it; Phase 0 marked in progress | #4 |

### Phase 0 — started on the Windows test machine (reported there, not verified here)

- The clone is up to date; the `framework` remote is added and fetched, with nothing new upstream.
  Blocking pushes to it was recommended there; Phase 0 step 1 now includes that.
- It was found there that Python is `python` or `py` on Windows, not `python3`, and that the `claude`
  command-line tool was not on that shell's path. The first led to the Windows changes above. Git
  Bash is installed.

### Next

- On the Windows test machine: pull `main` (latest `af4ccf9` before this log), run
  `git checkout -- .claude/hooks/report-mode.sh`, finish Phase 0 with the Windows commands, and
  stop at Gate 0 to report, including any test that fails only on Windows.
- Before Phase 1: put the `claude` command-line tool on the path (it is needed to validate, load
  and test the plugin), and the stop rules under Gate 1 are confirmed.

---

## Session 2 — 2026-10-16

**Where:** the Windows test machine: the Claude desktop app (Code tab) on Windows 10, Git Bash,
Python 3.11.0. **Base:** `main` at `50e5a54`; `framework/main` still `24092db`, nothing to merge.

### What happened — Phase 0, up to Gate 0

All of this was run and checked in this session unless it says otherwise.

- **Step 1.** The clone already existed. `framework` remote added, fetched, and its push URL set to
  `DISABLED`. `report-mode.sh` was CRLF; `git checkout -- .claude/hooks/report-mode.sh` alone did
  **not** fix it (git saw the file as unchanged and skipped it). Deleting the file and checking it
  out again did. No other tracked `*.sh` is CRLF. The plan's step 1 instruction is therefore
  incomplete for an existing clone.
- **Step 2.** `python -m venv .venv`, `.venv/Scripts/pip install -e ".[dev]"`,
  `.venv/Scripts/classkit mode developer` (marker created, confirmed ignored). Session restarted;
  the hook now announces FRAMEWORK-DEVELOPER.
- **Step 3.** `.venv/Scripts/pytest -q`: **405 tests, 396 passed, 9 failed** (run twice: at
  `af4ccf9` and `50e5a54`; `src/` and `tests/` are unchanged since `24092db`, where the assessment
  measured 405 passed on a Mac and session 1 measured 405 on Linux). All 9 are Windows-only, by
  root cause:

  | Tests | Cause | Kind |
  |---|---|---|
  | `test_course_lifecycle::test_scaffold_course_creates_the_private_folder_and_says_what_it_is_for`, `test_course_log::test_scaffold_creates_the_log_with_one_entry`, `test_course_lifecycle::test_a_broken_locator_in_the_saved_coverage_report_warns` | Backslashes: `str(path.relative_to(…))` in `scaffold.py:180` (written into `LOG.md`) and `validate.py:241` (finding locations) | **Code bug** — already in the plan's Windows section, Step 4 |
  | `test_write_path::test_remove_deletes_only_what_the_caller_wrote`, `test_doctor::test_a_full_text_from_another_library_version_is_not_an_edit`, `test_private_material::test_a_stale_unedited_full_text_is_refreshed_not_refused`, `test_private_material::test_a_full_text_from_another_library_version_is_not_an_edit` | The test writes its fixture with `Path.write_text()`, which writes CRLF on Windows, then compares with a hash of the LF text. `classkit` itself writes with `newline=""`. Read in each test's code; not re-run with a fix | **Test bug** — fixture should write bytes or pass `newline=""` |
  | `test_write_path::test_replacing_a_file_keeps_its_permissions`, `test_write_path::test_a_new_file_gets_the_umask_default_not_0600` | Windows has no POSIX permission bits (mode is always `0o666`) | **Not applicable on Windows** — skip there |

- **Two Windows problems the tests do not catch**, found with a throwaway course in the scratchpad
  (committed with LF, cloned with `core.autocrlf=true`, which is Git for Windows' default and is set
  on this machine):
  1. **`classkit ingest` crashes when its output is piped** — which is how Claude's Bash tool runs
     it. Python encodes stdout in the Windows code page (`cp1256` here); the report contains `→`;
     `UnicodeEncodeError`, exit 1. The crash comes **after** the manifest and the ingested file are
     written and **before** the course-log entry, so the ingest is silently missing from
     `LOG.md`. With `PYTHONUTF8=1` it runs. `validate`, `status` and `doctor` don't crash but print
     em dashes in `cp1256`, which reach Claude as `�`. Pytest misses this because `capsys` captures
     strings. **Not in the plan.**
  2. **Line endings in a course repo** — confirmed: in the CRLF clone, `ingest` (with UTF-8) exits
     3 and `status` reports M0001 as "edited by hand and its source has changed"; neither is true.
     The plan's Windows section names source materials only; the committed `ingested/` files are
     affected the same way (`_hand_edited` compares raw bytes). The planned fix — scaffold writes
     `* text=auto eol=lf` into course repos — covers both; existing course repos need it added by
     hand.
- **Step 4 not done.** The `claude` command-line tool is on neither the Git Bash nor the PowerShell
  path, so `claude --version` cannot run.
- **Step 5.** The real test course was not touched.

### Decisions

None yet. Open: which Windows failures to fix here, and when.

### Commits

| Commit | What | Pull request |
|---|---|---|
| this commit | This entry; the plan's Phase 0 Status row set to "at Gate 0". No code or test changes | branch `phase-0-log` |

### Next

- Install the `claude` command-line tool on this machine and record `claude --version` (Phase 0
  step 4).
- To be decided: the Windows failures above, and whether to report them upstream now: the backslash
  log entry, the `ingest` encoding crash and the CRLF false "edits" all exist in
  `class-framework` today.
- Then Phase 1: the Gate 1 stop rules are confirmed. The `ingest` crash matters for C1 and C4 on
  Windows: `bin/classkit` should set `PYTHONUTF8=1` (or `classkit` should reconfigure stdout to
  UTF-8).

---

## Session 3 — 2026-10-16

**Where:** the claude.ai cloud checkout of session 1 (Linux). **Base:** `main` at
`185f237`.

### What happened

- Merged session 2's log entry. It was pushed from the Windows test machine on branch
  `phase-0-log`; that machine has no GitHub command-line tool, so the pull request was opened and
  merged here.
- Reviewed session 2's Gate 0 report against the code. Its reading holds: `src/` and `tests/` are
  unchanged since `24092db`, and 405 tests passed on Linux in session 1. One more problem found by
  reading `cli.py`, **not yet seen on Windows**: `classkit write` reads its input from `stdin` in the
  console's code page, so text agents pipe into it would be saved garbled on Windows. Added to
  Phase 0b, step 1, to check there.
- Corrected two mistakes in the plan, both from session 1: Phase 0 step 1's line-ending
  instruction (`git checkout` alone skips the file — delete it first), and "nothing is committed" in
  Phase 0, written before the log existed.

### Decisions

- **Fix the Windows bugs before Phase 1**, as a new Phase 0b: UTF-8 in and out, forward slashes in
  the three places, a scaffolded `course/.gitattributes` (moved here from Step 4), and the test
  fixes. One small commit per fix, so each can be cherry-picked into `class-framework`.

### Commits

| Commit | What | Pull request |
|---|---|---|
| `0a22e70` | Session 2's entry (written on the Windows test machine) | #5, merged as `185f237` |
| this commit | The plan: Phase 0b; Phase 0 step 1 and its commit rule corrected; the Windows section and Step 4 updated; Status rows for Phase 0 (done) and 0b (next). This entry | #6 |

### Next

- On the Windows test machine: Phase 0b on branch `phase-0b-windows`, stopping at Gate 0b.
- Before Phase 1: install the `claude` command-line tool on the Windows machine (Phase 0 step 4),
  and the Gate 1 stop rules are confirmed.

---

## Session 4 — 2026-10-16

**Where:** the Windows test machine: the Claude desktop app (Code tab) on Windows 10, Git Bash,
Python 3.11.0. **Base:** `main` at `ae4dc96`; `framework/main` still `24092db`.

### What happened — Phase 0b, up to Gate 0b

Steps 1–4 done on branch `phase-0b-windows`, one commit per fix. Everything below was run on this
Windows machine unless it says otherwise.

- **Fix 1, UTF-8.** `main()` reconfigures stdin, stdout and stderr to UTF-8. The new
  `tests/test_encoding.py` runs the CLI with `PYTHONIOENCODING=cp1256`. **Without the fix both of
  its tests fail on Windows**: `ingest` with session 2's `UnicodeEncodeError`, and `write` saves the
  piped text garbled (`\xc3…` where `\xe2…` was sent). That second one confirms session 3's
  reading of `cli.py`.
- **Fix 2, forward slashes.** The plan's three places, plus a fourth found while editing: `add-url`'s
  message (`cli.py`), printed with `str()` the same way. No test checks that message's slashes; it
  only prints.
- **Fix 3, `course/.gitattributes`.** From the new `templates/course/gitattributes`, written right
  after `.gitignore`, create-only. Two tests: scaffold writes it; a re-run leaves a teacher's edited
  copy byte for byte. `dev/FRAMEWORK-SPEC.md` lists it in its three tables of course files (required
  in the same commit, `dev/CLAUDE.md`). `dev/MANUAL-TESTING.md` now expects 15 files created, not
  14 (counted by running scaffold).
- **Fix 4, tests.** The plan's four tests now write with `newline="\n"`, and so do **two more**,
  `test_write_path::test_remove_refuses_a_changed_file` and
  `test_private_material::test_a_stale_edited_full_text_is_refused`, which write "the teacher's
  edit" — they passed on Windows only because CRLF also looks like an
  edit, so they tested nothing there. The two permission tests skip on Windows.
- **Step 5, Windows checks** (throwaway course in the scratchpad; Bash tool stdout is `cp1256`):
  - **A — ingest through a pipe:** exit 0, no encoding error, report shows `→`, and `LOG.md` now has
    the ingest entry. **Pass.**
  - **B — `write` of `→`, an em dash and Hebrew, piped in:** saved byte for byte (`cmp`). **Pass.**
  - **C — CRLF clone** (`core.autocrlf=true`) of an LF-committed course with the new
    `.gitattributes`: files check out LF (`git check-attr eol` → `lf`); `ingest` "Nothing to do",
    `status` "nothing outstanding", `doctor` no edit findings. **Pass.**
  - **pytest on Windows:** 409 tests (405 + 4 new), **407 passed, 2 skipped** — the two
    permission tests, as the plan expects. **Pass.**
  - **pytest on Linux: not run here.** This machine's WSL (Ubuntu 22.04, Python 3.10.12) has no
    `pip` or `venv`; running it needs `sudo apt install python3-venv`, a change to this machine's WSL that
    was not made without asking. Run in the cloud checkout instead — see "Linux check"
    below.
- **Seen, not fixed:** `classkit write` ("created  course\units\probe.md") and ingest's "logged …"
  line still print Windows paths with backslashes. Display only, nothing committed is affected, and
  outside the plan's list — still to be decided.

### Commits — each can be cherry-picked into `class-framework` on its own

| Commit | Fixes |
|---|---|
| `33e0041` | UTF-8 in and out: the `ingest` crash on a code-page console, garbled em dashes, and text piped into `classkit write` saved garbled. New `tests/test_encoding.py` |
| `f6f0fe1` | Forward slashes: `LOG.md`'s scaffold entry, validate's finding locations, scaffold's report, add-url's message |
| `290ac7a` | `classkit scaffold course` writes `course/.gitattributes` (`* text=auto eol=lf`): no false "edited by hand" on a Windows clone. Spec and MANUAL-TESTING updated. An existing course repo needs the file added and `git add --renormalize .` once |
| `e9e1e7f` | Tests: six fixtures written with LF; the two permission tests skip on Windows. Test-only |
| `fb87f00` | This entry; the plan's Phase 0b Status row |
| the next commit | The Linux check below; Status row: Gate 0b met (cloud checkout) |

Not opened as a pull request from this machine; it was opened and merged from the cloud checkout.

### Linux check (cloud session, same day)

Run on branch `phase-0b-windows` at `fb87f00`, in a fresh environment (Linux, Python 3.13.16):

- `pytest -q -rs`: **409 passed, none skipped** — the two permission tests run and pass on Linux,
  as they should. **Gate 0b is met.**
- **The encoding test catches the bug on any system.** With the `use_utf8()` call disabled,
  both tests in `tests/test_encoding.py` fail on Linux too: `ingest`'s report fails, and the text
  piped into `classkit write` is saved garbled. Restored, both pass.

### Next

- ~~Gate 0b still needs `pytest` on Linux or macOS~~ — done in the cloud checkout; Gate 0b met.
- `phase-0b-windows` merged into `main`. The four commits are reported upstream, to `class-framework`.
- Before Phase 1: the `claude` command-line tool (Phase 0 step 4), and the Gate 1 stop rules.

---

## Session 5 — 2026-10-16

**Where:** the Windows test machine: the Claude desktop app (Code tab) on Windows 10. **Base:**
`main` at `0c125b8`.

### What happened — Phase 0 step 4, the `claude` command-line tool

- **Installed** with the method Anthropic's setup page recommends for native Windows
  (code.claude.com/docs/en/setup, "Native Install"), from PowerShell, no administrator rights:
  `irm https://claude.ai/install.ps1 | iex`. It installed **Claude Code 2.1.301** at
  `C:\Users\<user>\.local\bin\claude.exe`. The binary's Authenticode signature is valid, signed by
  "Anthropic, PBC".
- **PATH.** The installer reported that `C:\Users\<user>\.local\bin` was not on the PATH. Fixed with
  the two PowerShell commands from the docs' troubleshooting page ("Verify your PATH"), which append
  it to the **User** PATH only; the previous User PATH was saved first (in the session's scratchpad).
- **Verified in Git Bash:** a fresh login shell (Git for Windows `bash 5.2.37`, `MINGW64`) with the
  PATH as a new terminal gets it finds `/c/Users/<user>/.local/bin/claude`, and `claude --version`
  prints **`2.1.301 (Claude Code)`**. Shells already open — including the desktop app's — keep the
  old PATH until they are restarted.
- **`claude doctor`:** native install 2.1.301, `win32-x64`, search OK. Its one warning, "not in
  your PATH", came from its process inheriting the desktop app's old PATH; the fresh-shell check
  above shows the fix. Two things to know:
  - **Not signed in.** The command-line tool needs its own login (run `claude` once and follow the
    browser prompt) before Phase 1's `claude --plugin-dir` sessions. Not done here — it is a personal
    account.
  - **Auto-updates show as disabled**, because the desktop app sets `DISABLE_AUTOUPDATER=1` in the
    environment it gives its shells. In an ordinary terminal the native install auto-updates.
    Phase 1 should record `claude --version` when it starts.

### Decisions

None.

### Commits

| Commit | What | Pull request |
|---|---|---|
| this commit | This entry; the plan's Phase 0 Status row (step 4 done) | branch `phase-0-cli` |

### Next

- Restart the desktop app (so its shells see the new PATH), and sign the command-line tool in
  (`claude` in Git Bash, once).
- Before Phase 1: the Gate 1 stop rules are confirmed.

---

## Session 6 — 2026-10-17

**Where:** the claude.ai cloud checkout (Linux). **Base:** `main` at `4fcb7a8`.

### What happened

- Merged session 5's log entry (branch `phase-0-cli`, PR #8). Reviewed first: the installer is
  Anthropic's native one, the signature is valid, and only the User PATH changed, with a backup.
- The desktop app was restarted and the command-line tool signed in (reported; not verified
  here). Phase 0 is complete.
- Explained the difference between the framework and a plugin, and how each part of the
  framework maps to a plugin part: commands, agents, skills, schemas and templates carry over as
  they are; what changes is how `classkit` is installed, how the always-on rules reach Claude, and
  where permissions live — exactly what checks C1, C3 and C6 test.

### Decisions

- **The Gate 1 stop rules are confirmed as written:** C1 or C3 failing means stop; C4 failing means
  pause until fixed or explained; C2 and C7 are not stops; C5 and C6 are problems to fix.
- C5 (a second person installs it) and C7 (per-course pin) are also run in the **desktop app's Code
  tab**, which teachers are likely to use.

### Commits

| Commit | What | Pull request |
|---|---|---|
| this commit | The plan: stop rules confirmed; Phase 1 records `claude --version`, says what runs where, adds the desktop app to C5 and C7, and notes the WSL setup C2 needs on the Windows test machine; Status: Phase 1 next. This entry | #9 |

### Next

- On the Windows test machine: Phase 1 on branch `phase-1-spike` — build first, then the checks, with
  C4 last. Stop at Gate 1.

---

## Session 7 — 2026-10-17

**Where:** the Windows test machine: the Claude desktop app (Code tab) on Windows 10. **Base:**
`main` at `5eaee23`. **Versions:** `claude --version` → `2.1.301 (Claude Code)`; Python 3.11.0 (`python`,
`py -3`); `python3` is the Microsoft Store placeholder.

### What happened — Phase 1, Build items 1–10 (the checks are not started)

On branch `phase-1-spike`. Details and smoke-test numbers in `dev/reviews/plugin-spike.md`.

- **Item 1.** 60 tracked files copied into `plugin/` (agents, skills, commands, schemas,
  templates, methodologies, defaults, `src/classkit`); each folder identical to its original.
  `report-mode.sh` and `.claude/settings.json` not copied.
- **Items 2–4.** `plugin.json` (`class-agent-kit`, `displayName` "Class Agent Kit", `0.1.0-spike`,
  an `author`); `marketplace.json` (`agent-based-class`, source `./plugin`, plus a `description` —
  the validator's one warning without it); `scripts/run_classkit.py`; `requirements.txt`.
- **Items 5, 6, 8, 9.** `hooks/bootstrap.sh`, `bin/classkit`, `hooks/rules.sh`, `hooks/hooks.json`
  (one SessionStart entry, no matcher, bootstrap `timeout: 300`). Hooks run as
  `bash "${CLAUDE_PLUGIN_ROOT}/hooks/…sh"` — Git Bash on Windows (docs: shell-form hooks run in Git
  Bash there), `sh -c` elsewhere — so they don't depend on the executable bit; the scripts are
  committed `100755` anyway.
- **Item 7.** `rules/core.md`, **6,877 characters** (source sections: 14,756);
  `skills/course-reference/SKILL.md`, 8,550 characters, the commands table, materials rules and
  exception syntax ported from `CLAUDE.md` as written, commands prefixed `/class-agent-kit:`.
- **Item 10.** `claude plugin validate --strict ./plugin` and `claude plugin validate --strict .`
  **both pass**. Advice only: the root README has no install line (Step 8's job).
- **Smoke tests of the scripts by hand** (not C1/C3): bootstrap 40 s first run, 1 s second, stdout
  empty; wrapper, scaffold, validate, status and a piped non-ASCII `write` work from outside the
  repo; rules.sh right in all four cases (course, no course, too long, no Python).
- **`pytest` on Windows:** 407 passed, 2 skipped (the permission tests), as after Phase 0b. The
  tests still run against the root copies; nothing at the root changed.

### Departures from the plan, with reasons

- **Item 8 said `python3 -c` for the JSON escaping.** On Windows `python3` is the Store
  placeholder, and rules.sh cannot use the venv, because hooks of one event may run at the same
  time as bootstrap. So both hooks share **`hooks/find-python.sh`** (the plan's own search: `python3`,
  `python`, `py -3`, each actually run). Without any Python, rules.sh prints `core.md` as plain
  stdout, which SessionStart also adds as context.
- **Bootstrap writes a `.complete` marker and takes a lock** (`mkdir venv-….lock`), so an
  interrupted install is rebuilt rather than trusted, and two sessions starting at once don't both
  install. The plan asked only for deleting a partial directory on failure.

### Found, for later phases

- **Windows path-length limit.** `pip` failed with the data folder under a long path: `lxml`
  (a dependency of `python-docx`) has a file ~110 characters deep in the venv. The real data folder
  puts it at about 199 characters for a 5-character user name — computed, not observed; C1 shows the real
  path. A long Windows username would cross 260. The hook fails safely (no block, partial venv
  removed), but retries at every session start (~30–40 s each).
- **`find_framework_root()` looks in the current directory and its parents first**, before its
  own `__file__`. Run from this repository's root, the plugin's `classkit` uses the root copies of
  `schemas/` and `methodologies/` (identical during the spike). **For C4:** a course repository
  made by cloning `class-framework` also has them at its root, so the plugin's `classkit` would use
  the course repository's framework files, not the plugin's — read in `model.py`, not yet run.
- **Command names live in the Python code too:** `classkit status` prints "run /plan-syllabus".
  Phase 5's renaming pass must cover `src/`, not only the prompts.
- **`CLAUDE_ENV_FILE` and the PowerShell tool:** on Windows a variable whose value is a path is not
  passed to PowerShell commands (docs), so `CLASSKIT_VENV` reaches only the Bash tool — which is
  also the only tool with the plugin's `bin/` on its PATH.

### Commits

| Commit | What |
|---|---|
| `4475f2e` | Build item 1: the copy into `plugin/` |
| `3e59746` | Items 2–4: manifests (with the marketplace `description`), launcher, requirements |
| `34133f3` | Items 5, 6, 8, 9: the hooks and `bin/classkit` |
| `64aff42` | Item 7: `rules/core.md` and the `course-reference` skill |
| this commit | `dev/reviews/plugin-spike.md` (environment, build smoke tests, C1–C7 placeholders); this entry; Phase 1 Status row |

Branch pushed; no pull request (Phase 1 ends at Gate 1).

### Next

- Phase 1 checks, C4 last. What can run in the session is run there (C2's eval needs WSL2 on this
  machine, per the plan); C1's second session, C3's `/clear` and `/compact`, C5, C6 and C7 are run
  by hand from given steps.

---

## Session 8 — 2026-10-17

**Where:** the claude.ai cloud checkout (Linux): a review of session 7's build.
**Base:** branch `phase-1-spike` at `8ad562d`.

### What happened

- **Reviewed** the build: the manifests, `hooks.json`, `find-python.sh`, `bootstrap.sh`,
  `rules.sh`, `bin/classkit`, `run_classkit.py`, `requirements.txt` and `rules/core.md`. Sound
  overall. Session 7's two departures from the plan (a shared `find-python.sh`; a completion marker
  and an install lock in `bootstrap.sh`) are improvements.
- **One bug, fixed here:** the install lock. If an install is killed — by the hook's 300 s timeout
  on a slow network, a closed app, a power cut — its lock folder stays behind, and every later
  session would wait 280 s, give up, and never install `classkit`. A lock older than 10 minutes is
  now treated as abandoned and removed. Tested on Linux: a 20-minute-old lock is cleared and the
  install runs (7 s); a fresh lock is still waited for (3 s, until the other install finished).
- **Linux, the second system** (Claude Code 2.1.302, Python 3.13):
  - `claude plugin validate --strict` passes for `./plugin` and for the marketplace.
  - `pytest`: 409 passed.
  - The hooks and the wrapper, run with the plugin's variables set by hand: the first bootstrap
    took 8 s and the second none, with nothing on stdout; `classkit scaffold`, `validate` and
    `status` work from a course repo outside this repository; without `CLASSKIT_VENV` the wrapper
    explains what is wrong; `rules.sh` prints valid SessionStart JSON with 6,877 characters of
    context in a course, and nothing outside one.
  - As in session 7, these are hand runs, not checks C1 or C3: those need real plugin sessions.
- **Recorded in the plan** from session 7's findings: the Windows long-path risk (row in the
  Windows section, measured in C1); C4 must run in a course repo that holds only the course; and
  Step 5's renaming covers the Python code's messages too.

### Commits

| Commit | What | Pull request |
|---|---|---|
| this commit | The stale-lock fix in `plugin/hooks/bootstrap.sh`; the plan updates above; this entry | on `phase-1-spike`, no pull request yet |

### Next

- Check C1 on the Windows test machine: a real `claude --plugin-dir` session in a throwaway course,
  then a second session. The sessions are run by hand, from steps given in the working session.

---

## Session 9 — 2026-10-17

**Where:** the claude.ai cloud checkout (Linux). **Base:** branch `phase-1-spike` at
`3efeccf`.

### Decisions

- **C1 on a Mac is deferred**, to be decided at the end of Phase 1 together with Gate 1. Recorded
  in the plan's new list, "Decided at the end of Phase 1", with the options: ask someone
  with a Mac to run it; accept the Linux run as a stand-in until before teachers use the plugin; or
  drop the Mac requirement. C1 on Windows goes ahead now.

### Commits

| Commit | What | Pull request |
|---|---|---|
| this commit | The plan: the "Decided at the end of Phase 1" list, and C1's row points to it. This entry | on `phase-1-spike` |

### Next

- Check C1 on the Windows test machine.

---

## Session 10 — 2026-10-18

**Where:** the Windows test machine (Git Bash, Claude Code 2.1.301): C1's first plugin session, run
step by step; the results recorded in the claude.ai cloud checkout. The empty repository and the
steps were prepared on the Windows test machine (pushed `f83bf92`). **Base:** branch `phase-1-spike`
at `f83bf92`.

### What happened — C1, session 1

- In `C:\Projects\c1-empty`, an empty git repository: `claude --plugin-dir …/plugin` started at
  14:44:31 and was ready at about 14:47, including Claude Code's own first-run questions and the
  plugin's first install.
- The rules question before any course existed: **no**, as expected; the plugin's skill was visible.
- `command -v classkit` → the plugin's `bin/classkit`. `CLASSKIT_VENV` →
  `C:/Users/<user>/.claude/plugins/data/class-agent-kit-inline/venv-8ff0bb76164b`. **The core of
  C1 holds on Windows:** the plugin installed its environment at session start, and `classkit`
  runs from it.
- Asked in words to create the course, Claude found `classkit scaffold course` itself, but used
  `--path .`, so the course landed at the repository's top level (15 files) instead of `course/`.
- Full details and five findings in `dev/reviews/plugin-spike.md`, C1.

### Decisions

- Everything is logged: the session's results are recorded as they come in, not only at the end of C1.

### Commits

| Commit | What | Pull request |
|---|---|---|
| `9e23663` | C1 session 1, first half, in `dev/reviews/plugin-spike.md`; a new "Found during the checks — to fix" list in the plan; this entry | on `phase-1-spike` |
| this commit | The rest of session 1 | on `phase-1-spike` |

### Later in session 1

- 14:56 — the top-level course removed and created again in `course/` (15 files, exit 0).
- No permission prompt appeared: Auto mode's checker approved each action.
- Claude Code updated itself during the session ("Restart to update"); session 2 runs on the newer
  version.
- 15:32 — after `/clear`, the rules question: **yes**, with the heading and both banned words.
  **Session 1 of C1 passed on Windows.** Recorded in `dev/reviews/plugin-spike.md`, C1.

### Next

- Session 1 is left with `/exit`. On the Windows test machine, the data folder is read (path
  lengths, install time from `bootstrap.log`) and the steps for session 2 are given.

---

## Session 11 — 2026-10-18

**Where:** the Windows test machine: the Claude desktop app (Code tab) on Windows 10. **Base:**
branch `phase-1-spike` at `f5c3db0`.

### What happened — C1, after session 1

- Read the plugin's data folder on the machine. Details in `dev/reviews/plugin-spike.md`, C1, "The
  data folder, the install time and the long-path limit".
- **Install time 48 s** (from `bootstrap.log`); the hook started 1 min 46 s after launch, after
  Claude Code's own first-run questions.
- **Data folder** `C:\Users\<user>\.claude\plugins\data\class-agent-kit-inline` (58 characters;
  every length here was measured with a 5-character user name). **Longest path 190** (a compiled
  `jsonschema` test file, not the `lxml` file); **201 under the marketplace name**
  `class-agent-kit-agent-based-class` — 58 under the limit; it would fail only for a Windows user
  folder name over about 63 characters. **The long-path limit was not hit.**
- `bootstrap.log` shows **a second SessionStart at 14:47:14** that matches no step taken —
  recorded, not explained.
- Fixed a blank line that split C1's session-1 table in two.

### Commits

| Commit | What | Pull request |
|---|---|---|
| `202c10f` | The data-folder measurements in C1; this entry | on `phase-1-spike` |
| this commit | C1 session 2 and the Windows verdict; finding 6; Phase 1 Status row | on `phase-1-spike` |

### C1, session 2 — run one step at a time

- `claude --version` → **2.1.302**. The session started **immediately**; `bootstrap.log` shows one
  hook run (16:45:54), venv ready, **no install**.
- The rules question: **yes**, at startup — the course existed when the session began.
- `command -v classkit` → the plugin's `bin/classkit`; `CLASSKIT_VENV` → the same venv;
  `classkit status` → the "C1 empty" course, correct.
- **C1 passes on Windows.** Mac deferred (plan, "Decided at the end of Phase 1").
- New finding 6: Claude suggested `/ingest` and `/plan-syllabus` without the plugin prefix, taken
  from `classkit status`'s messages and the copied prompts — Step 5's renaming, now seen in a live
  session.

### Next

- The next Phase 1 check (C2, C3, C5, C6 or C7; C4 last), still to be chosen. C6 in Claude Code's
  default permission mode, not Auto (finding 4).

---

## Session 12 — 2026-10-18

**Where:** the Windows test machine (Git Bash, Claude Code 2.1.302), finishing C1's second plugin
session; recorded in the claude.ai cloud checkout. **Base:** branch `phase-1-spike` at `6b4f330`.

### What happened — the end of C1, session 2

- In the same plugin session, after `classkit status`, three more read-only commands were sent —
  Claude Code's own prompt suggestions (an earlier record that described them as typed was corrected
  in session 13): `classkit doctor`, `classkit validate`, `classkit ingest --preflight`. All worked
  through the plugin. `validate` (0 alerts, 0 errors, 2 warnings) and the preflight ("materials/source/
  is empty") match the plugin's `classkit` on Linux line for line, on a two-unit course scaffolded
  the same way in the cloud session. Details in `dev/reviews/plugin-spike.md`, C1, session 2.
- **Finding 7:** doctor reports a "working mode", which means nothing under a plugin. Tried on Linux:
  `classkit mode developer` from a course either refuses with a `.gitignore` error about the
  plugin's folder (plugin in a git checkout) or writes `dev/.developer` into the plugin folder
  (plugin folder outside git). Added, with finding 6, to the plan's "Found during the checks — to
  fix"; both go to Step 5.
- The question why C1 needs a Mac came up again. The concrete Mac risks are now in the plan's "C1 on a Mac"
  row: Apple's own `python3` is, as far as known, 3.9 (below the 3.10 minimum), and hooks run under
  bash 3.2 — the hook scripts were searched and use no bash 4 features. Still to be decided at
  Gate 1.

### Open — to be decided later

- **The order of the remaining checks.** The check that builds a real course from books and slides
  is C4. Proposed: **C3 → C6 → C4**, then C2, C5 and C7 alongside or after, instead of
  C4 last. Reason: "C4 last" guards against spending model time on broken plumbing, and the
  plumbing stop checks are C1 (passed) and C3; C2, C5 and C7 test other things (evals, a second
  person, loading through settings) and do not change what C4 finds; C6 first spares approving
  every `classkit` command during C4. Cost: none found — C4 loads the plugin with `--plugin-dir`,
  as C1 did. Not decided; the plan still says C4 last.
- C4's shape as proposed: a new empty repository where the plugin creates the course; the course
  materials copied in from `C:\Projects\ds-agbf` (published books into `materials/source/private/`),
  the original never touched; then `/class-agent-kit:ingest`, `plan-syllabus`, `plan-units`, comparing
  the plugin's `classkit` output with the original tool's on the same files.

### Commits

| Commit | What | Pull request |
|---|---|---|
| `16f1191` | The end of C1 session 2 and finding 7 in `dev/reviews/plugin-spike.md`; findings 6–7 and the Mac specifics in the plan; this entry | on `phase-1-spike` |
| this commit | Finding 1 fixed in `plugin/hooks/rules.sh`, with `tests/test_plugin_rules_hook.py` | on `phase-1-spike` |

### Later in session 12 — finding 1 fixed, in this session

- C1 session 2 was left with `/exit`, and the fix was made in this session.
- `rules.sh` now loads the rules wherever `classkit`'s `find_course_root()` finds a course:
  `course.yaml` in the project folder itself (a course made with `--path .`, or a session started
  inside `course/`), or `course/course.yaml` there or in any folder above (a session started deeper
  in the repository). This goes one step past the plan's "both places": a session started below
  the top folder now gets the rules too, as the old framework's `CLAUDE.md` reached such sessions.
  Cost: a session started in an unrelated folder that happens to sit below a course also gets them
  — the same place `classkit` itself would find that course. In Git Bash the project path is first
  turned into `/c/…` form with `cygpath -u`, so that `dirname` can walk up it.
- `tests/test_plugin_rules_hook.py`, 5 tests: the usual place, the top level, a subfolder, no
  course, a `course/` folder without `course.yaml`. Against the old hook, the top-level and
  subfolder tests fail — they catch the bug. Skipped on Windows outside Git Bash (another `bash`,
  such as WSL's, sees other paths). Linux: **414 passed** (409 + 5). **Windows (Git Bash): the 5 pass** (9.85 s), run after pulling `8983818` — so the `cygpath -u` conversion of a Windows project path works.

### Finding 8 — a machine without Python (raised as a question)

- Would the plugin have worked had Python not been installed first? **No:**
  the plugin builds its own venv but needs Python 3.10+ to build it, as the framework did. On
  Windows without Python, `python` and `python3` are the Microsoft Store placeholders, which
  `find-python.sh` runs and rejects. The rules would still load (`rules.sh` falls back to plain
  output), but `classkit` would not run.
- What the teacher would see is the problem: the hook's "install Python" message goes to stderr
  with exit 0, which Claude Code probably does not show (not verified), and `bin/classkit` then
  advises starting a new session, which cannot help. Added to the plan's to-fix list, **before C5**.

### C3 — run one step at a time

- **C3 passes on Windows.** In `C:\Projects\c1-empty`: the rules answered at startup, after
  `/compact` and after `/clear`, each time about IDs not yet named in the conversation; in a session
  started inside `course/` (finding 1's new case) too; and in an empty folder, `c3-nocourse`, no
  rules while the plugin's skill was present. `bootstrap.log` shows a SessionStart for `/compact`
  (18:18:51) and for each later step, so the rules were injected again, not left over. Details in
  `dev/reviews/plugin-spike.md`, C3.
- Leftover folder `C:\Projects\c3-nocourse`, with `c1-course`: to clear at the end of Phase 1.

### C6 — run one step at a time (chosen as the next check)

- `C:\Projects\c1-empty\.claude\settings.json` allows four read-only commands (the plan's three, plus
  `ingest --preflight`, as the framework allows). Claude Code started with `--permission-mode
  default` ("manual mode on").
- Claude first ran `classkit` through its **PowerShell** tool: a permission prompt (the `Bash(…)`
  rules do not cover it), and, approved once, a Windows "How do you want to open this file?" window
  — PowerShell cannot run the plugin's shell script. **Finding 9**, to fix before C4.
- Told to use Bash, all four ran **with no prompt**. **C6 passes through Bash.** Details in
  `dev/reviews/plugin-spike.md`, C6.
- Claude Code then suggested `run /plan-syllabus` in the input box (its own prompt suggestion; an
  earlier record that described it as typed was corrected in session 13); advised not to send it
  (C4's work).

### Finding 9 researched; findings 10 and a distribution constraint

From Claude Code's documentation (`code.claude.com/docs/en/tools`, `/hooks`, `/plugins-reference`) and the
local 2.1.302 binary:

- On Windows with Git Bash, the PowerShell tool is **on by default** for claude.ai accounts, and
  "Claude treats PowerShell as the primary shell" — so finding 9 will recur. Off switch:
  `CLAUDE_CODE_USE_POWERSHELL_TOOL=0`, in the environment or a settings file's `env` block (the name
  is in the binary too). A plugin's own `settings` honours only `agent` and `subagentStatusLine`, so
  the switch belongs in the course's `.claude/settings.json`.
- PowerShell commands get `CLAUDE_ENV_FILE` variables only when every line is a plain assignment, and
  on Windows never one whose value holds `/` or `\` — so never `CLASSKIT_VENV`. A `bin/classkit.cmd`
  would have to find the venv itself: fragile.
- **Finding 10:** Git Bash is a hard prerequisite on Windows (the hooks are Bash scripts; Claude Code
  can run without Git Bash).
- **Distribution:** plugins with `bin/` cannot be installed through claude.ai, Cowork or an
  organisation's claude.ai plugin settings. Marketplace installs into Claude Code are unaffected.
- **Proposed** (not yet approved): the course settings switch, plus a line in
  `rules/core.md`; who writes the course's settings file (permissions, C7 pin, this switch) is a
  Phase 2 decision, with finding 3. All added to the plan's to-fix list.

### The trial report

- A short report was written: a Claude Docs document, "Class Agent Kit — plugin trial report"
  (private until shared) — what was done, the C1/C3/C6 results, the findings and their handling,
  and three asks: a Mac run of C1, a second person for C5, and a view on distribution.

### Next

- Done: `8983818` pulled into `C:\Projects\agent-based-class-plugin`, where `--plugin-dir` loads the
  plugin from.
- C3 and C6 done. Next: a decision on finding 9's proposed fix, then its test on Windows; finding 8
  (no Python) before C5; then C2, C4, C5, C7 in an order still to be chosen.

---

## Session 13 — 2026-10-21

**Where:** the Windows test machine (Git Bash, Claude Code 2.1.302, then 2.1.306); recorded in the
claude.ai cloud checkout. **Base:** branch `phase-1-spike` at `8b32c73`.

### Finding 9 — the fix

- The branch was pulled, with an instruction to continue: taken as approval of the fix proposed in
  session 12.
- `plugin/rules/core.md`: one line added — run `classkit` with the Bash tool, never PowerShell, which
  cannot run it on Windows. The file is now 6,989 characters (under the 8,000 target).
- The other half, `"env": {"CLAUDE_CODE_USE_POWERSHELL_TOOL": "0"}` in the course's
  `.claude/settings.json`, is course data, not plugin code: it is added to `C:\Projects\c1-empty`
  for the test. Who writes a course's settings file stays a Phase 2 decision (finding 3).

### Commits

| Commit | What | Pull request |
|---|---|---|
| `efc2203` | The `core.md` line; the plan's finding-9 row; this entry | on `phase-1-spike` |
| this commit | The fix's test in `dev/reviews/plugin-spike.md`; the plan's row and Status | on `phase-1-spike` |

### The test — run one step at a time

- `efc2203` was pulled and the switch added to `C:\Projects\c1-empty\.claude\settings.json`
  (its earlier content unchanged, checked first).
- **In `c1-empty`** (Claude Code 2.1.302, default mode): no PowerShell tool; the four commands ran
  through Bash with no prompt and no Windows window.
- Claude Code updated itself to **2.1.306** ("Restart to update"); Claude Code was restarted.
- **In `c1-empty\course`** (no settings apply there): Claude had PowerShell, but chose Bash, citing
  the rules line; each command asked permission, approved once; all four ran.
- **Finding 9 fixed.** Observed: a course's settings apply only when Claude starts in the folder that
  holds them, not in a subfolder. Details in `dev/reviews/plugin-spike.md`, under C6.
- Twice Claude Code suggested `/plan-syllabus` (and once `commit the .gitignore`) in the input box. These
  were its own prompt suggestions; earlier records that described them as typed were corrected
  (sessions 12–13). Added to finding 6: a teacher is offered the old command name ready to send.

### The trial report, updated

- "Class Agent Kit — plugin trial report" was updated: it now says finding 9 is fixed and
  tested (lead, C6 row, findings table, next steps), notes Claude Code 2.1.306, adds finding 11, and
  adds the prompt suggestions to finding 6.

### C7 — run one step at a time (chosen as the next check)

- Branch B, `c7-version-b` (`d8db5ea`): `phase-1-spike` with `plugin.json`'s version `0.1.0-spike-b`.
- The course's settings gained the marketplace (GitHub, `ref` `phase-1-spike`) and `enabledPlugins`.
  First plain `claude`: the plugin arrived with **no install command**, from the GitHub copy — but its
  start-up hooks did not run (**finding 12**); `/clear` ran them (venv in 44 s).
- `ref` switched to `c7-version-b`: new sessions start **without the plugin** (**finding 13**,
  `plugin-cache-miss` in the debug log); `/reload-plugins` loads `0.1.0-spike-b` mid-session.
- A terminal "Reset" chosen by accident blanked the window mid-test; the session carried on.
- Details in `dev/reviews/plugin-spike.md`, C7. Still open: one try of the documented
  `claude plugin install`, and the desktop app's Code tab.

- How this touches teachers, and why a branch was needed: the branch stood for a new version being
  published; the course's `ref` line is the pin, changed by one edit. Teachers never
  make branches.
- **The try:** `claude plugin install class-agent-kit@agent-based-class --scope project`
  from Git Bash, then a fresh `claude`: rules, `classkit` from `0.1.0-spike-b`, and the same venv, all at
  startup. **Finding 13 is fixed by one install command.**

- **Then (option 1 chosen):** `ref` back to `phase-1-spike` with the plugin installed: the next session
  still ran `0.1.0-spike-b`. `claude plugin update class-agent-kit@agent-based-class --scope project`
  ("updated from 0.1.0-spike-b to 0.1.0-spike … Restart to apply changes"), then a fresh session ran
  `0.1.0-spike`. So moving a course's version = the `ref` edit + the update command + a restart.

- **The desktop app's Code tab**, a session in `c1-empty`: the rules and `classkit` from `0.1.0-spike`,
  the same as the terminal. **C7 is done on Windows.**

### Decisions

- **Finding 8 deferred:** teachers can be asked to install Python first, and C4 is the most
  important check, so it comes first. The setup instructions name Python 3.10+ (and Git Bash on
  Windows) as prerequisites either way; the clearer failure message waits.
- **C4 next.**

### Next

- C4: a real course from real materials, in a new repository; C2 and C5 after.


---

## Session 14 — 2026-10-24

**Where:** the claude.ai cloud checkout (Linux). **Base:** branch `phase-1-spike` at `959da3a`.

### What happened

- Names of people and who-did-what wording were removed from this log, `dev/reviews/plugin-spike.md`
  and `dev/PLUGIN-MIGRATION.md`; the sentences were rewritten as plain statements, mostly passive.
  Decisions keep their content and dates. The Windows user name in recorded paths is now `<user>`,
  and every path length measured with it says it was measured with a 5-character user name.
- Kept, as data rather than attribution: the repository's address
  `shiraradshilo/agent-based-class-plugin`.
- Not changed: earlier commit messages on GitHub (that would rewrite the branch's history), and the
  `author` and `owner` fields in `plugin.json` and `marketplace.json`, which are plugin metadata.

### Commits

| Commit | What | Pull request |
|---|---|---|
| this commit | The three files without names; this entry | on `phase-1-spike` |

---

## Session 15 — 2026-10-28

**Where:** the claude.ai cloud checkout (Linux), with tests on the Windows test machine.
**Base:** branch `phase-1-spike` at `7f1ec98`.

### Decisions

- **C4 is accepted as passed.** Done through the plugin, in the desktop app's Code tab, on
  `C:\Projects\c4-course`: the plugin installed from the app's Add marketplace (`#phase-1-spike`),
  the course created, the materials ingested, and `/class-agent-kit:plan-syllabus` drafting
  stepwise — evidence first, then its open questions one at a time, nothing written before
  approval. Its questions showed the materials were read (the exam weight against the flipped
  method; a contradiction on an exam cover page) and their roles respected (instructor-only
  slides). **Not done:** the comparison of the plugin's `classkit` output with the original tool's
  on the same files, and `/plan-units`.
- **Finding 13 is fixed now**, in the plugin, as far as a plugin can (below).

### Finding 13 — the version check

- `plugin/hooks/inject_rules.py` (new; `rules.sh` now runs it): when the plugin runs from Claude
  Code's cache (`<plugins>/cache/<marketplace>/<plugin>/<version>/`) and its marketplace copy
  (`known_marketplaces.json`'s `installLocation`, else `<plugins>/marketplaces/<marketplace>/`)
  offers another version, a note follows the course rules: Claude tells the teacher in its first
  reply and, with their OK, runs `claude plugin list` for the scope, then `claude plugin update
  class-agent-kit@agent-based-class --scope <scope>`, and asks for a new session. Any surprise in
  Claude Code's folders leaves the check silent; with `--plugin-dir` there is nothing to compare.
- Not fixable in the plugin: a plugin that was never installed (only enabled by the course's
  settings) does not load at all after a version change, so none of its code runs. That case is
  for the teacher instructions (Phase 8): install once per computer.
- `tests/test_plugin_version_check.py`: 6 tests; three fail against the old hook. Linux: **420
  passed**. `claude plugin validate .` passes.
- The plugin's version is now `0.1.1-spike`, so an installed `0.1.0-spike` sees an update.
- The plan's finding-7 row now names Phase 6 (retire the two hats), not Step 5.

### The check on Windows

- The `c1-empty` install was updated to `0.1.1-spike` by hand (scope project only; the all-folders
  install stays at `0.1.0-spike` while C4 runs on it). Baseline: no notice.
- Changing the course's `ref` brought no notice: the marketplace stayed at `phase-1-spike`, because
  the desktop app's Add marketplace had declared it in `~/.claude/settings.json`, which wins
  (**finding 14**).
- `0.1.2-spike` was published (`1db0796`) and the marketplace updated by hand. A new session with
  only "Where does my course stand?" opened with the notice; "Yes, please update it." had Claude run
  the update for the folder's install; a **New** session in the desktop app then ran `0.1.2-spike`.
  **Finding 13 is fixed as far as the plugin can fix it.** Details in `dev/reviews/plugin-spike.md`.
- C4 went on meanwhile in the desktop app: a draft syllabus (7 outcomes, a 13-unit map) and
  `/review-syllabus`'s critic, with its findings acted on as chosen. Recorded under C4 in
  `dev/reviews/plugin-spike.md`.

### Commits

| Commit | What | Pull request |
|---|---|---|
| `3bd65d2` | The version check, its tests, version `0.1.1-spike`; this entry's first part | on `phase-1-spike` |
| `a9999f8` | Branch `version-check-b`: `0.1.1-spike-b`, for the test | — |
| `1db0796` | Version `0.1.2-spike`, no other change | on `phase-1-spike` |
| this commit | C4 and the check's Windows test recorded; finding 14 | on `phase-1-spike` |

### Next

- Remove the extra installs after the tests (the all-folders one or the `c1-empty` one).
- Gate 1 / Phase 2: the teachers' route (finding 14). Remaining: C2, C5, C1 on a Mac.

---

## Session 16 — 2026-10-29

**Where:** the claude.ai cloud checkout (Linux). **Base:** branch `phase-1-spike` at `d96ab98`.

### What happened

- **A create-course command, ahead of Phase 2** (decision: done now rather than in Phase 2).
  `plugin/commands/new-course.md` → `/class-agent-kit:new-course`: checks there is no course yet;
  asks for the title, code, institution, instructors and number of units in one message; on the
  teacher's confirmation runs `classkit scaffold course` in this folder (never `--path`, so the
  course lands in `course/`); validates; then tells the teacher to start a new session so the course
  rules load, to put materials in `course/materials/source/` (books in `private/`), and to run
  `/class-agent-kit:ingest`. It carries the Bash-only line itself, since the rules are not loaded
  before a course exists. Listed in the `course-reference` skill.
- **The reminder in `classkit` too:** the plugin's copy of `classkit scaffold course` ends with
  "Next: start a new Claude Code session (or type /clear) so the course rules load" whenever it
  created something — for a teacher who asks in words instead of using the command. Only in
  `plugin/src/`; the framework's `src/` is unchanged (Phase 3 makes the plugin the one copy).
- `tests/test_plugin_scaffold_message.py`: 2 tests; one fails without the change. Linux: **422
  passed**. `claude plugin validate` passes for the marketplace and the plugin.
- Version `0.1.3-spike`, so installed copies see an update (and the version notice offers it).
- Command names stay as they are until Phase 5 (decision): renaming dozens of files while the
  framework is still changing would make every later merge harder.

### Commits

| Commit | What | Pull request |
|---|---|---|
| `278e403` | The command, the reminder, its tests, version `0.1.3-spike`; this entry | on `phase-1-spike` |
| this commit | The existence check that does not end in an error; version `0.1.4-spike` | on `phase-1-spike` |

### On Windows (desktop app, Claude Code 2.1.306)

- **Updating from the desktop app:** in a session in a new empty folder (`C:\Projects\c6-newcourse`),
  the plugin's page showed the all-folders install, `0.1.0-spike`, with **Update greyed out**, although
  the marketplace copy already offered a newer version. Its `…` menu offers only VS Code, Cursor, Show
  in Explorer and Remove — no way to fetch a release. The page cannot bring an update by itself.
- **Asking Claude instead worked:** "Update the Class Agent Kit plugin to the latest version, for all
  my folders." Claude found both installs, refreshed the marketplace and updated them: all folders
  `0.1.0-spike` → `0.1.3-spike`, `c1-empty` `0.1.2-spike` → `0.1.3-spike` (one of its first commands
  failed; it went on), and said to restart open sessions.
- **`/class-agent-kit:new-course`** in a new session there: its first check ("Check whether a course
  exists here") showed as **Failed** in the app — `classkit status` errors when there is no course,
  and the command rightly took that as "go on", but a teacher may read it as a fault (to change: a
  check that does not fail). It asked for the details in one message; with "Test course", 2 units, it
  showed and ran `classkit scaffold course --title "Test course" --institution "Ben-Gurion
  University of the Negev" --units 2` — **15 files, in `course/`** — validated (0 errors, 2 expected
  warnings), and ended with the next steps in order: start a new session or `/clear`, put the
  materials in `course/materials/source/` (books in `private/`), then `/class-agent-kit:ingest`.
- **The course rules load in the next session.** Asked, without running anything, whether
  instructions headed "Class Agent Kit — rules for this course" were present: in the session that
  created the course, **no** — as the command says; in a **new** session in `c6-newcourse`, **yes**.
  So finding 2–3's fix works end to end on Windows: create the course, start a new session, and the
  rules are there from its start.

### The existence check no longer ends in an error

- `/class-agent-kit:new-course` step 1 now runs `classkit status || true`. Without a course,
  `classkit status` exits 2 ("cannot find a course"), which the app shows as **Failed**; with
  `|| true` it exits 0 and prints the same message. Checked on Linux: exit 2 before, 0 after.
- Why not a check for `course/course.yaml` alone, as first proposed: `classkit` also finds a course
  in a folder above, or a session started inside `course/` itself; a file check in this folder would
  miss both and scaffold a second course inside the first. `classkit status` keeps the one rule for
  where a course is. Any other error now stops the command and is reported as it is.
- Version `0.1.4-spike`. Linux: 422 passed; `claude plugin validate` passes for both.

### Next

- On Windows: update to `0.1.4-spike` and run `/class-agent-kit:new-course` in a new empty folder —
  the first step should no longer show as Failed.


## Session 17 — 2026-10-31

**Where:** the claude.ai cloud checkout (Linux). **Base:** branch `phase-1-spike` at `4594084`.

### What happened

- **The plugin on a Mac (reported, not observed here).** On 2026-10-29 the plugin was installed on
  a Mac, on a second person's machine, and used; it was reported to behave as on Windows. This
  stands for C1 on a Mac and for C5 (a second person installs it). Reported, not certain: ingest
  and building units were among what was run. Not recorded: the install route, the Python version
  and the first-run time.
- **C2 run on Linux** (the cloud workspace): `classkit` runs inside `claude plugin eval` once two
  things are adjusted — the plugin's `bin/` put on `PATH` by the shell that starts the run
  (finding 15), and the venv built in a folder the sandbox can read (finding 16). With both, score
  1.0: `classkit validate` gave the expected result in the sandbox, and the rules reached the
  session. Each run rebuilds the venv (14–28 s); four tries cost about $0.36 (estimate). The
  adjustments were made in a scratch copy only; the plugin in this repository is unchanged. Details
  and the case's text: `dev/reviews/plugin-spike.md`, C2.
- **Phase 1 status:** all checks done — C1 (Windows; Mac reported), C3, C4 (accepted), C5
  (reported), C6, C7, and C2 (Linux, with two adjustments). Next is Gate 1.
- **The scaffold reminder copied into the original `src/classkit/cli.py`** (session 16 had added it
  to the plugin's copy only). Phase 3 deletes the copies and keeps the originals, so it would have
  been lost. The plugin's copies now match the originals exactly; only new files differ. Nobody runs
  this repository's `src/` for a course. Linux: 422 passed.

### Decisions

- **Teachers install the plugin once per computer** (finding 14), not pinned per course. Reasons:
  it is the simpler route, the one tested end to end (install, the version notice, the update), and
  the desktop app's own Add marketplace does not break it; a per-course pin breaks as soon as the
  marketplace is added for the whole computer, and needs an install and an update command after
  each version change (findings 12–13). The cost: nothing holds a course on one version through a
  semester, and a teacher and a TA may run different versions. The plan's partial answer (Phase 4,
  assessment §6.7): the course records the version that last wrote it, and `classkit` warns when
  the running version differs — a mismatch is made visible, not prevented. Follows from it for
  Phase 4: the course settings written by `classkit scaffold course` carry no `ref`.

- **Gate 1: GO** (2026-10-31). Phase 1 is done; Phase 2 is next. Decided with it: the
  `class-framework` repository stays as it is for now; a changelog per release is needed; the
  marketplace name is deferred, to be decided before Phase 8 (cheap to change before teachers have
  the plugin, a reinstall for every teacher after). Left for Phase 2: whether a teacher can replace
  a plugin agent with their own. Recorded in the plan's Gate 1 section and status table.

### Commits

| Commit | What | Pull request |
|---|---|---|
| `67daf13`, `402a9eb` | This entry: the Mac result | on `phase-1-spike` |
| `8d920c2` | The install-route decision; finding 14's row in the plan | on `phase-1-spike` |
| `5602fea` | C2's results, findings 15–16 and where each is handled; the plan's status | on `phase-1-spike` |
| `a5c080a` | The scaffold reminder in the original `cli.py` | on `phase-1-spike` |
| this commit | Gate 1: GO, and what was decided with it | on `phase-1-spike` |

### Next

- Merge `phase-1-spike` into `main` through a pull request, once approved.
- Phase 2 (specify), with the decisions above; the distribution route (Claude Code only) and the
  agent override to be settled there.

## Session 18 — 2026-10-31

**Where:** the claude.ai cloud checkout (Linux). **Base:** branch `phase-1-spike` at `e24deb2`; this
work on a new branch, `phase-4-runtime`.

### What happened

- **Phase 4, job 1, done early: the setup scripts.** It touches only files that exist in the plugin
  alone (`hooks/`, `bin/`), so Phase 3 does not affect it. The rest of Phase 4 waits for Phase 3.
- **Finding 8, no Python.** `bootstrap.sh` now publishes `CLASSKIT_SETUP_PROBLEM` (`no-python`, or
  `install-failed` when the install fails). `bin/classkit` then says what is wrong and what to do:
  install Python 3.10+ from python.org (on Windows, tick "Add python.exe to PATH"), then start a new
  session — instead of only "start a new session". In a course, `rules.sh` adds a note to the rules
  so that Claude tells the teacher in its first reply.
- **Finding 16, evals.** `bootstrap.sh` builds the venv in `EVAL_CLASSKIT_DATA` when it is set; only
  eval runs set it. C2 re-run on Linux against the committed script: score 1.0.
- `tests/test_plugin_setup_problems.py`: 5 tests; all 5 fail without the change. Linux: **427
  passed**. `claude plugin validate --strict` passes. Not yet seen on Windows or a Mac.
- **Phase 4, job 2, done early (decided: every course gets it, Windows above all): the course
  settings file.** `classkit scaffold course` now writes `.claude/settings.json` beside `course/`,
  create-only: the PowerShell tool off (finding 9) and the four read-only `classkit` commands
  allowed (D-045). Until now it was written by hand. A repository that already has settings keeps
  them; re-running `classkit scaffold course` adds the file to an existing course. Left out for
  now: `enabledPlugins` and the marketplace, which name the plugin's repository and marketplace —
  both still to be decided. Made in both copies of `classkit` (`src/` and `plugin/src/`) and both
  copies of the templates, which stay identical. `FRAMEWORK-SPEC.md` lists the file.
  `tests/test_scaffold_course_settings.py`: 5 tests; all 5 fail without the change. Linux: **432
  passed**.
- **Phase 4, job 3, done early: the teacher's own methodology.** In the framework a teacher added a
  file to `methodologies/` in their own clone; under the plugin that folder is replaced on every
  update. `classkit` now reads `course/methodologies/<name>.yaml` first, then the framework's
  (`model.methodology_path`); validation names the file in use; `classkit status` prints a
  "Methodology" line with the file. The prompts that told agents to read `methodologies/<name>.yaml`
  — a path a course repository under the plugin does not have, so they could not find it — now name
  the course's file, else `${CLAUDE_PLUGIN_ROOT}/methodologies/<name>.yaml`; the command and the core
  rules point to `classkit status`. Checked on Linux with `claude -p --plugin-dir`: Claude Code fills
  in `${CLAUDE_PLUGIN_ROOT}` inside a skill's text and an agent's. A file in the course with the same
  name as the framework's replaces it for that course; whether `classkit validate` should warn about
  that was decided below. Both copies of `classkit` and of the prompts stay identical.
  `tests/test_course_methodology.py`: 6 tests; they fail without the change. Linux: **438 passed**.
- **Finding 17**, found on the way: the prompts also name `schemas/…` (7 places) and
  `defaults/time-constants.yaml` (2), which a course repository under the plugin lacks. **Fixed**
  the same way (`${CLAUDE_PLUGIN_ROOT}/…`), in both copies. `tests/test_plugin_prompt_paths.py`
  fails if a prompt names a framework file by a course-relative path again.
- **Decided: warn when the course's methodology has the framework's name.** A new advisory rule,
  `methodology_replaces_framework` (warn, consistency): the course's own file replaces the
  framework's of that name for the course, and stops getting its changes; the message suggests a
  name of its own. Registered in `DEFAULT_SEVERITY`, listed in the spec's rule table, tested in
  `tests/test_course_lifecycle.py` at its severity. Linux: **442 passed**.
- No version change: nothing is released from this branch yet.

### Commits

| Commit | What | Pull request |
|---|---|---|
| `3e3ec4e` | Job 1 of Phase 4, its tests, the plan's rows for findings 8 and 16 and its status table | on `phase-4-runtime` |
| `5ca3c7e` | Job 2 of Phase 4: the course settings file; its tests; the spec; the plan's status | on `phase-4-runtime` |
| `29ad2a9` | Job 3 of Phase 4: the teacher's own methodology; the prompts; its tests; the spec; finding 17 recorded | on `phase-4-runtime` |
| this commit | Finding 17 fixed; `methodology_replaces_framework`; their tests; the spec's rule table | on `phase-4-runtime` |

### Next

- Phase 2, with the answers from the meeting; then Phase 3; then the rest of Phase 4.
- On Windows, once this branch is merged: a session with Python hidden, to see the teacher told.

## Session 19 — 2026-11-02

**Where:** the claude.ai cloud checkout (Linux). **Base:** branch `phase-4-runtime` at `e23845f`; this
work on `phase-2-specify`.

### What happened

- **Pull requests opened** for the work so far, to be merged in order with merge commits: #10,
  `phase-1-spike` into `main` (Phase 1, Gate 1: GO), and #11, `phase-4-runtime` into `main` (Phase 4,
  done early).
- **Phase 2, specify.** **D-049** — the framework ships as a Claude Code plugin — written in
  `_devlog/01-decisions.md`: what a teacher receives; install once per computer and the cost
  accepted with it; `classkit` from the plugin; the rules from a hook; the scaffolded course settings;
  namespaced names; customization through the course; agents testable. It retires D-009 and D-034,
  amends D-014 and D-045, and resolves Q-031. What is still open is listed in it: where the
  repository moves and whether it is public, the workflow there, replacing a plugin agent, a
  teacher's own agents, course-local templates, the marketplace name, the `policies/` folder.
- `FRAMEWORK-SPEC.md`: §2.3, the repository model, rewritten for the plugin; a new normative §8.10,
  the plugin — layout, session start, the course settings, names, versions, what a teacher may
  change, evals — with **(target)** where not built; §5.2 and §8.6 point to it; §9 lists the version
  cost. `ROADMAP.md`: a D-049 ledger block, a row per artifact, tagged with its phase.
  `_devlog/03-open-questions.md`: Q-007 reframed, Q-031 resolved.
- The plugin name stays `class-agent-kit`; any rename is decided before Phase 5.
- **Phase 3, the restructure**, on `phase-3-restructure`, from `phase-2-specify`. The copies and the
  originals were identical (checked before deleting). In two commits, so that history follows the
  files: first the plugin's copies deleted (the plugin is incomplete between the two), then the
  originals moved in with `git mv` — `.claude/agents`, `.claude/commands`, `.claude/skills`,
  `src/classkit`, `schemas`, `templates`, `methodologies`, `defaults`. `pyproject.toml` (package and
  pytest path) and nine tests point at `plugin/`.
- **The root `CLAUDE.md` is the developer's** (brought forward from Phase 6, as the plan says): how
  to work, setting up, the invariants (a seventh: the plugin names its own files through
  `${CLAUDE_PLUGIN_ROOT}`), where things live, the rules for validation rules and agents. The
  vocabulary and IDs are referred to `plugin/rules/core.md`, not copied. `dev/CLAUDE.md` now only
  points to it.
- **`classkit mode` keeps working until Phase 6:** its marker and `.gitignore` are the repository's,
  but the framework root is now `plugin/`, so `mode.repository_root()` looks above it (finding 7's
  failure otherwise: a refusal, or a marker written into the plugin). Two tests in `test_mode.py`
  follow. The mode hook's TEACHER text still names the old paths; it goes in Phase 6.
- Checks: `pytest` **442 passed**; `claude plugin validate --strict plugin` and `claude plugin
  validate .` pass. A real session with `--plugin-dir plugin` in an empty folder: no rules (no
  course), `classkit scaffold course` created the course and its `.claude/settings.json`, `classkit
  status` named the methodology file, `validate` gave 0 errors and 2 expected warnings; a new session
  there had the rules. Also seen: `claude -p` in a folder never trusted ignores the course's allow
  rules ("this workspace has not been trusted") — an interactive session asks for trust first.
- Left for later phases, unchanged here: the teacher docs (`GETTING-STARTED.md`, `README.md`) and
  `dev/MANUAL-TESTING.md` still describe the clone model (Phase 8); `classkit mode` and its hook
  (Phase 6).

### Commits

| Commit | What | Pull request |
|---|---|---|
| `09ff360` | Phase 2: D-049, the spec, the ledger, the open questions; the plan's status | #12 |
| `4b18332` | Phase 3: the plugin's copies deleted | #13 |
| `494a63b` | Phase 3: the originals moved into `plugin/`; paths; the developer's `CLAUDE.md`; `classkit mode`'s root | #13 |
| `c708624` | Release `0.2.0`: the version, `CHANGELOG.md`, this entry | #14 |
| this commit | The Mac result, finding 18, the repository decisions | on `log/session-19-notes` |

### After the merges

- **#10, #11, #12 and #13 merged** into `main`, in that order, each as a merge commit (checked: two
  parents each). On `main`: `pytest` 442 passed; `claude plugin validate --strict plugin` and
  `claude plugin validate .` pass.
- **The merged branches could not be deleted from the cloud session:** `git push --delete` and the
  GitHub API both answer 403 (the session's proxy allows no branch deletion). They are deleted on
  GitHub instead: the 13 branches contained in `main`; `c7-version-b` and `version-check-b` kept.
- **Release `0.2.0`**, on `release/0.2.0`: the version, and `CHANGELOG.md` started at the repository's
  root (D-049: an entry per release), with what changed for a teacher and what to do.

### Also this session

- **The plugin on a Mac, 2026-11-01 (reported, from a photo of the screen).** `/ingest` ran on a
  Mac: 16 materials converted and classified (7 instructor-only rows confirmed), the coverage report
  saved, `classkit validate` 0 errors and the 2 expected warnings. Claude then reported
  `methodologies/question-driven-25.yaml` as **missing** and offered to "fix" it. Nothing was
  missing: `classkit` found the methodology (validation needs it). It was the bug fixed under
  finding 17 — the prompts named the methodology by a path relative to the course repository — and
  that install followed `#phase-1-spike`, still `0.1.4-spike`, without the fix. Advice given: plan
  the syllabus, not the "fix" (a copied methodology would stop receiving updates); update to
  `0.2.0`.
- **Finding 18: the update notice depends on a refreshed marketplace copy.** At session start the
  plugin compares its version with the marketplace's **local copy**; it does not ask GitHub. Claude
  Code refreshes that copy only when asked (`claude plugin marketplace update`, or "update the
  plugin") — auto-update is off by default for a marketplace like this one. So a teacher who never
  asks may never be told of a release. Recorded in the plan for Phase 4.
- **Decided (D-049's open items):** the repository moves to **its own repository** (not into
  `class-framework`), and it is **public**. Cost of public, named: everything in it can be read by
  anyone, `dev/` included — the logs, the reviews, the reports of the real-course tests; worth a read
  for anything that should not be published before the move.

### Next

- Delete the merged branches on GitHub; repoint the test installs to `main` and update to `0.2.0`.
- Before the move: the repository's name, the marketplace's name, whether the plugin keeps
  `class-agent-kit`, and the workflow there (`dev` and a protected `main`).
- The rest of Phase 4 (finding 18 among it), and Phase 5.


## Session 20, in parallel — 2026-11-02

*A session on another branch, `claude/bold-meitner-2swi76`, the same day as session 20 below;
merged 2026-11-05 (session 22), where item 8 moved to a phase of its own, Phase 11.*

**Where:** the claude.ai cloud checkout (Linux). **Base:** `main` at `c76b0fb` (release `0.2.0`
merged, #14); this work on `claude/bold-meitner-2swi76`.

### What happened

- **The Status table brought up to date.** Phase 4 said "the rest after Phase 3" although Phase 3 is
  merged; it now lists what is done (released in `0.2.0`) and what is left, and which part is blocked
  (`enabledPlugins` and the marketplace, on the repository's home and the marketplace name). Phases
  5–10 read "not started" instead of "waiting for GO" — Gate 1 was GO; each phase still ends at its
  own gate. Session 19's "Next" still lists merging `release/0.2.0`: that is done (#14).
- **Decided, by the developer: a teacher may replace a plugin agent and may add their own** — D-049
  item 8. Replacement through `course.yaml` `agents:` (the key was already in the schema and the
  template, read by nothing); the command keeps the procedure, so the write guard and the validator
  hold whatever the replacement does; `validate` checks the map, `status` lists it. The costs are
  recorded with it: a replacement does not follow plugin updates; replacing `course-critic` gives up
  its independence. Built in Phase 5, with the namespacing. Recorded in `FRAMEWORK-SPEC.md` §8.10
  (a target row and a paragraph), Q-007, and a ⬜ ledger row.
- **Proposed, not decided:** course-local templates and the `policies/` folder — the recommendations
  were given to the developer; D-049 still lists both as open.
- Documentation only; no code changed, so no tests were run.

### Next

- Decide course-local templates and `policies/`; then the rest of Phase 4.

## Session 20 — 2026-11-02

**Where:** the claude.ai cloud checkout (Linux). **Base:** `log/session-19-notes` at `68a4c93` (pull
request #15, not yet merged); this work on `phase-4-runtime-2`.

### What happened

- **Phase 4: the plugin version in the course.** Every entry `classkit log` writes now ends with
  `- **Plugin:** Class Agent Kit 0.2.0` (`classkit/version.py`, from `plugin.json`). When the newest
  version in `LOG.md` is newer than the one running, the session-start note asks Claude to tell the
  teacher first, offer the update — `claude plugin marketplace update`, then `claude plugin update`
  — and change nothing until the teacher has updated or said to go on; it replaces the marketplace
  note, which would repeat it. `classkit doctor` reports the same as an action. A pre-release sorts
  before its release. **Changed from the plan:** the version is in the log, not in a `course.yaml`
  field written by scaffold and approve. `course.yaml` and the `approved` blocks are validated with
  `additionalProperties: false`, so a new field there would be a schema error for every older
  plugin — the very case the warning is for — and an agent told to fix what `validate` reports might
  delete it. Cost: a line per log entry, and a course that logs nothing is not covered.
- **Finding 19, found while doing the `skills:` job: the agents could not load their skills.** Their
  `tools:` lists have no Skill tool, so "load the X skill" (eleven places, six agents) had nothing
  to load it with. Seen in a headless session with `0.2.0`'s plugin: the course-critic tried to read
  the skill files, was refused, and reported NONE. A probe plugin showed that `skills:` frontmatter
  preloads a skill by its bare name or by `plugin:skill`, and that an agent without the Skill tool
  cannot load one on instruction.
- **Phase 4: `skills:` frontmatter** on the six agents, named in full
  (`class-agent-kit:writing-guiding-questions`), so a teacher's own skill of the same name does not
  replace the standard the plugin's designers and critic share. The course-critic preloads all four
  of its skills, the two used only for a plan or a syllabus included (about 23 KB): judged
  deterministic over lean. Seen in a session: the critic starts with all four. The prose now says
  they are preloaded; `tests/test_plugin_agent_skills.py` fails if an agent's text names a skill
  its frontmatter does not declare, or tells it to load one.
- **Finding 18, the options looked into** (in the plan): the teacher turns on auto-update once; the
  scaffolded course settings turn it on (after the move, and if a project setting reaches a
  marketplace added for the whole computer); the start-up script refreshes the copy; or nothing more.
  **Chosen: check, then ask.** Once a day `inject_rules.py` reads the version the GitHub marketplace
  publishes (`raw.githubusercontent.com`, the ref the marketplace was added with, 3 seconds, `curl`
  as a fallback for a Mac's python.org Python); when it is newer, the note asks Claude to ask the
  teacher, and to update only on their word. The answer is kept a day in the plugin's data folder,
  a failure included. Checked here: the raw address works through this network (a public
  repository); this repository is private, so the check finds nothing until it is public.
- Checks: `pytest` **483 passed**; `claude plugin validate --strict plugin` and `claude plugin
  validate .` pass.

### Commits

| Commit | What |
|---|---|
| `2bfc387` | The plugin version in the course log; the session-start note and `doctor` line |
| `7aad369` | The agents' `skills:` frontmatter (finding 19); finding 18's options; this entry |
| this commit | Finding 18: the daily check of the published version, and the question to the teacher |

### After the merges

- **#15 and #16 merged** into `main` as merge commits. **Release `0.2.1`**, on `release/0.2.1`: the
  version and its changelog entry — a patch number by choice, though it adds features; the update
  check compares numbers, so `0.2.1` is offered over `0.2.0` either way. It had to be a new number:
  `claude plugin update` compares the version, so a change released under `0.2.0` would reach no
  one. The changelog asks teachers to re-run the reviews of what they planned before it (finding 19).

### Next
- After the move: the course settings' `enabledPlugins` and marketplace; then Phase 5.

## Session 21 — 2026-11-05

**Where:** the claude.ai cloud checkout (Linux). **Base:** `main` at `1155f95` (0.2.1); this work on
`cleanup/class-kit`.

### What happened

The clean-up before the repository moves. Asked first, and decided (D-050):

- **The plugin is `class-kit`** (Class Kit), **its marketplace `class-kit`**: the install id is
  `class-kit@class-kit`. The command `classkit` and the Python package keep their name.
- **Plan, build, review:** `/design-unit` becomes **`/build-unit`**; `/new-course`, `/ingest` and
  `/write-items` keep their names. The unit stage **`designed` becomes `built`**; a record with the
  old name is read as `built` (`model.normalize_approved`, as `on:` was for `date:`), and `--stage
  designed` is still accepted.
- **`dev/` stays as it is**, names and real-course reports included, though the repository will be
  public. The logs are kept, `_devlog/` included (the developer guide had said it would be deleted
  before release).

Done:

- **Phase 6, the two hats retired:** `classkit mode`, `mode.py`, `.claude/hooks/report-mode.sh` and
  its settings entry, the `dev/.developer` marker and its `.gitignore` line, doctor's working-mode
  line, `tests/test_mode.py`; the developer guide's instructions about them.
- **The renames**, by one script over every tracked text file except the history (`_devlog/`,
  `reviews/`, this log, the migration plan, the changelog): `class-agent-kit` → `class-kit`, "Class
  Agent Kit" → "Class Kit", the marketplace `agent-based-class` → `class-kit` (not the repository's
  name, `agent-based-class-plugin`), `design-unit` → `build-unit`; the command file moved with
  `git mv`. The state's wording in the prompts, the spec and the schema by hand.
- **Phase 5, names in full**, in the same pass: every `/command` in `plugin/` (prompts, templates,
  schema descriptions, `classkit` messages) and in the teacher docs (`README.md`, `GETTING-STARTED.md`,
  `MANUAL-TESTING.md`) is `/class-kit:<command>`; the commands send agents as `class-kit:<agent>` and
  load skills as `class-kit:<skill>`. The spec keeps the short names and says so (§8.10).
  `tests/test_plugin_names_in_full.py` fails on a bare command name anywhere in `plugin/`, or a
  command sending an agent by its bare name.
- **D-050** written; the spec (§2.1's verb table, §5.1, §8.2's `approved` row, §8.9, §8.10), the
  ledger (Phases 5 and 6 done, a D-050 block), the plan's status; `CHANGELOG.md` **0.3.0**, with how to
  install again; the version `0.3.0`.
- Checks: `pytest` **555 passed**; `claude plugin validate --strict plugin` and `claude plugin
  validate .` pass. A real session with `--plugin-dir plugin` in a fresh course: the rules open with
  "Class Kit — rules for this course", the commands are `/class-kit:new-course` … `/class-kit:build-unit`
  … `/class-kit:build-gem`, and the course log's first entry ends `Plugin: Class Kit 0.3.0`.

Not done here: the unmerged branch `claude/bold-meitner-2swi76` (replacing a plugin agent) — left
out, to be decided separately; the course settings' `enabledPlugins` and marketplace lines, which
need the new repository's address.

### Next

- Merge this; then move the repository, and install `class-kit@class-kit` from its new address on
  each computer.

## Session 22 — 2026-11-05

**Where:** the claude.ai cloud checkout (Linux). **Base:** `main` at `b426b43` (#18 merged); this work
on `agents/own-phase`.

- **The branch `claude/bold-meitner-2swi76` merged** (a merge commit, so its own commit stays in the
  history). It recorded, on 2026-11-02, D-049 item 8 — a teacher may replace a plugin agent through
  `course.yaml` `agents:` and may add their own — with the Status table brought up to date. Conflicts
  resolved: Phases 4–6 keep what is done since; Phases 7–10 take its "not started"; the ledger keeps
  both; the log keeps both session-20 entries, the branch's titled "in parallel".
- **Then moved to a phase of its own, Phase 11**, at the developer's request: D-049 item 8 stays
  decided *in principle*, and its mechanism becomes the proposal Phase 11 starts from, to be decided
  there and then built. The spec's row and paragraph say "Phase 11"; the ledger row is `[plugin, 11]`;
  Q-007 says how is open; the plan has a Step 11 and a Status row (after Phase 5, before Phase 8).
- Documentation only; no code changed.

### Next

- Merge; then push `main` to `BGU-CSE/class-kit-plugin`.

## Session 23 — 2026-11-05

**Where:** the claude.ai cloud checkout (Linux). **Base:** `main` at `9224090` (#19 merged); this work
on `move/bgu-cse`.

The new home is `BGU-CSE/class-kit-plugin` (public, empty when this was written). This session can
read it but not push to it — the Claude GitHub app is not installed for the organization, and the
developer is an admin of the repository only — so the move is a push of `main` from the developer's
computer, and what needs the new address is done here first, to arrive with it:

- **The course settings bring the plugin in** (Phase 4's last job): `classkit scaffold course`
  writes `extraKnownMarketplaces.class-kit` (GitHub, `BGU-CSE/class-kit-plugin`, no `ref`) and
  `enabledPlugins` `class-kit@class-kit`, the shape C7 verified in Phase 1. A Claude Code session in a
  scaffolded course read the file without complaint; a TA's first opening, with the marketplace
  fetched from the new repository, can only be tried once `main` is there. Finding 12 still applies:
  that first session runs none of the plugin's start-up hooks.
- **The marketplace's owner** is `BGU-CSE`; the plugin's author stays the developer.
- **`CHANGELOG.md` 0.3.0** gives the real address to install from, and lists the settings change
  (0.3.0 has not reached anyone yet).
- **Decided (D-049's open items):** the home, `BGU-CSE/class-kit-plugin`; how development runs
  there — work lands in `dev` (the owner pushes, everyone else opens a pull request into it), `main`
  is protected and takes only releases, and stays the default branch; an urgent fix branches from
  `main` and is merged back into `dev`. In the developer guide too (`CLAUDE.md`, "Branches").
- Checks: `pytest` **555 passed**; `claude plugin validate --strict plugin` and `claude plugin
  validate .` pass.

### Next

- Merge; push `main` to `BGU-CSE/class-kit-plugin` from the developer's computer; there, create
  `dev`, protect `main`, turn on deleting merged branches; archive the old repository.
- Install `class-kit@class-kit` from the new address on each computer, and try a TA's first opening
  of a scaffolded course.

## Session 25 — 2026-11-07

**Where:** the claude.ai cloud checkout (Linux). **Base:** `dev` at `e2b7350`; this work on
`homework/bring-in`. (Session 24, Phase 8, is on its own branch.)

The homework module, designed in the class-framework repository (branch `homework-by-shira`, forked
from its `main` at `24092db`), is brought into this repository so that nothing of it is lost —
staged, not yet part of the plugin:

- `dev/homework/`: its documents, unchanged; its own files at their old paths in
  `framework-files/`, outside `plugin/`, so nothing half-adapted ships and the plugin's tests do not
  run on files written before their rules; its changes to 14 framework files as
  `framework-changes.patch`.
- `dev/homework/PLUGIN-PORT.md`: the workflow, what is done (H0, 72 ledger rows) and left (H1–H7,
  46 rows, the first real homework, 8 open questions), and what the port must change. Found while
  writing it: the `interviewer` agent is told to wait for the teacher's answer, which an agent
  cannot do (D-044), so the interview moves into the commands — a reversal of HW-D04 to decide;
  `/new-hw-type` writes a skill into the course, which waits for Phase 11.
- **Decided** (in `PLUGIN-PORT.md`): `/plan-homework` and `/build-homework`, as for units; a
  homework is kept as a unit is — one file, `HW0N.md`, with the plan, its items' list and the
  approval record (`classkit approve homework N --stage planned | built`), the items in the shared
  bank, no `.plans/` and no `status: draft`; validation after the build; the Word or PDF documents
  on request; no item-bank work for now. **Proposed:** `/new-hw-type` → `/new-item-class`.
- Checks: nothing under `plugin/` changed; `pytest` **555 passed**; `claude plugin validate
  --strict plugin` passes.

### The port (same session, branch `homework/port`, from `homework/bring-in`)

Asked for "everything at once". The rest of HW-D35 decided first: the interview in the commands
(HW-D04 reversed), `/class-kit:new-item-class`, a course's class guidance as a file the agents read.

- **Prompts** (a forked agent, then checked here): `plan-homework`, `build-homework`,
  `new-item-class`; `write-items` hands `homework` off; agents `homework-planner` (returns, writes
  nothing), `homework-item-writer`, `item-critic`, `item-solver`, each with its skills in its
  frontmatter; skills `interviewing-teachers` (with the interviewer's procedure), `writing-code-items`,
  `writing-research-items`, and two new ones — `planning-homework` (the plan's standard, shared by
  the planner and the chat that revises, per CLAUDE.md) and `making-homework-documents` (the
  documents on request). `core.md` gains Homework, Item Class and `HW01`; `course-reference` the
  commands.
- **Schemas and templates:** the homework file gains `plan` and `approved`, loses `status`; `items`
  may be empty until the build; a quiz report's `ref` is a unit. The item schema gains the homework
  fields and renames `answer` → `model_answer` (D-031g's rows ticked). `course.yaml`'s template
  declares the starter classes' three tools — without them the first homework of a new course had
  three errors.
- **Python:** `model.py` loads homework and its configuration (an unreadable file is a `schema`
  error, not a crash); `validate_homework.py`, 21 rules in `DEFAULT_SEVERITY` — two of the module's
  folded into `schema` and `id_consistency`, `homework_unit_reference`, `homework_plan_reference` and
  `item_class_guide_reference` added; `approve.py`'s `approve homework` — the planned hash leaves out
  what the build writes, the built hash covers the items; `status.py` lists homework (only when there
  is some) and placeholders; `scaffold homework`, and `scaffold item` for all six formats with
  `--class`; `homework_budget_tolerance_minutes` in the time constants.
- **Docs:** HOMEWORK-SPEC rewritten for the plugin form; HW-D35; the module's ledger and plan
  ticked; `FRAMEWORK-SPEC.md` (the Assessment row, the commands, the files, `HW<NN>`), `ROADMAP.md`,
  `CLAUDE.md`, the migration plan. **Not** `README.md`, `GETTING-STARTED.md`, `CHANGELOG.md`: the
  Phase 8 branch rewrites them; they gain homework after it is merged. The staged copies removed.
- Checks: `pytest` **666 passed** (`tests/test_homework.py`, 71); `claude plugin validate --strict
  plugin` passes.

### Next

- Merge Phase 8, then this (`dev/PLUGIN-LOG.md` will conflict: both add at its end); then
  `README.md`, `GETTING-STARTED.md` and `CHANGELOG.md` gain homework.
- The first real homework, on a real course.
