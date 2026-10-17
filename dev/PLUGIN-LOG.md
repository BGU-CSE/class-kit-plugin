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

**Who:** Shira, with Claude in a claude.ai cloud session. **Base:** `BGU-CSE/class-framework`
`main` at `24092db`.

### What happened

- **Avin's assessment reviewed.** The plugin-migration assessment of 2026-10-11 was checked against
  the Claude Code documentation. Several of its open questions now have answers: hook context is
  capped at 10,000 characters, `CLAUDE_ENV_FILE` exists, the eval sandbox blocks the network,
  plugins listed by relative path load without an install, and a course can pin the plugin version
  by marketplace `ref`. Recorded in `dev/PLUGIN-MIGRATION.md`, "What changed since the
  assessment".
- **This repository created.** Avin proposed doing the migration in a separate repository led by
  Shira. Shira created this one (private), and it was seeded with `class-framework`'s full `main`
  history: 104 commits, ending at `24092db`. The tag `pre-plugin` could not be pushed from the
  cloud session (HTTP 403), so the plan names the commit instead.
- **The plan written:** `dev/PLUGIN-MIGRATION.md` — rules for every session, Phase 0 (setup),
  Phase 1 (the go/no-go trial, checks C1–C7), and Phases 2–10.
- **Windows, macOS and Linux.** Shira's first session ran on Windows, so the framework was checked
  for anything that assumes one operating system. The findings, and where each is handled, are in
  the plan's section "Windows, macOS and Linux".

### Decisions (Shira)

Recorded here and in the plan; they become numbered decisions in Phase 2.

- This repository is Shira's: she decides names, stop rules and go/no-go. Whether
  `class-framework`'s own courses and teachers move to the plugin stays Avin's call.
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
| `2210264` | Shira's decisions: ownership, the plugin name, Phase 0 without a real course, C4 builds a course | #2, merged as `918193c` |
| `63cedd7` | Windows, macOS and Linux: `.gitattributes` (shell scripts keep LF line endings); the Windows forms beside the Mac ones in `.claude/settings.json`, `CLAUDE.md`, `GETTING-STARTED.md`, `dev/FRAMEWORK-SPEC.md` and `dev/MANUAL-TESTING.md`; the plan's rule 10 and its "Windows, macOS and Linux" section. `pytest`: 405 passed (Linux) | #3, merged as `af4ccf9` |
| this commit | This log; the plan's rule 8 points to it; Phase 0 marked in progress | #4 |

### Phase 0 — started in Shira's Windows session (reported there, not verified here)

- The clone is up to date; the `framework` remote is added and fetched, with nothing new upstream.
  That session recommended blocking pushes to it; Phase 0 step 1 now includes that.
- It found that Python is `python` or `py` on Windows, not `python3`, and that the `claude`
  command-line tool was not on that shell's path. The first led to the Windows changes above. Git
  Bash is installed.

### Next

- Shira's Windows session: pull `main` (latest `af4ccf9` before this log), run
  `git checkout -- .claude/hooks/report-mode.sh`, finish Phase 0 with the Windows commands, and
  stop at Gate 0 to report, including any test that fails only on Windows.
- Before Phase 1: put the `claude` command-line tool on the path (it is needed to validate, load
  and test the plugin), and Shira confirms the stop rules under Gate 1.

---

## Session 2 — 2026-10-16

**Who:** Shira, with Claude in the Claude desktop app (Code tab) on Windows 10, Git Bash, Python
3.11.0. **Base:** `main` at `50e5a54`; `framework/main` still `24092db`, nothing to merge.

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

None yet. Open for Shira: which Windows failures to fix here, and when.

### Commits

| Commit | What | Pull request |
|---|---|---|
| this commit | This entry; the plan's Phase 0 Status row set to "at Gate 0". No code or test changes | branch `phase-0-log` |

### Next

- Install the `claude` command-line tool on this machine and record `claude --version` (Phase 0
  step 4).
- Shira decides on the Windows failures above, and whether to tell Avin now: the backslash
  log entry, the `ingest` encoding crash and the CRLF false "edits" all exist in
  `class-framework` today.
- Then Phase 1: Shira confirms the Gate 1 stop rules. The `ingest` crash matters for C1 and C4 on
  Windows: `bin/classkit` should set `PYTHONUTF8=1` (or `classkit` should reconfigure stdout to
  UTF-8).

---

## Session 3 — 2026-10-16

**Who:** Shira, with Claude in the claude.ai cloud session of session 1. **Base:** `main` at
`185f237`.

### What happened

- Merged session 2's log entry. The Windows session pushed it on branch `phase-0-log`; it has no
  GitHub command-line tool, so this session opened and merged the pull request.
- Reviewed session 2's Gate 0 report against the code. Its reading holds: `src/` and `tests/` are
  unchanged since `24092db`, and 405 tests passed on Linux in session 1. One more problem found by
  reading `cli.py`, **not yet seen on Windows**: `classkit write` reads its input from `stdin` in the
  console's code page, so text agents pipe into it would be saved garbled on Windows. Added to
  Phase 0b, step 1, to check there.
- Corrected two mistakes in the plan, both from session 1: Phase 0 step 1's line-ending
  instruction (`git checkout` alone skips the file — delete it first), and "nothing is committed" in
  Phase 0, written before the log existed.

### Decisions (Shira)

- **Fix the Windows bugs before Phase 1**, as a new Phase 0b: UTF-8 in and out, forward slashes in
  the three places, a scaffolded `course/.gitattributes` (moved here from Step 4), and the test
  fixes. One small commit per fix, so Avin can cherry-pick them into `class-framework`.

### Commits

| Commit | What | Pull request |
|---|---|---|
| `0a22e70` | Session 2's entry (written in the Windows session) | #5, merged as `185f237` |
| this commit | The plan: Phase 0b; Phase 0 step 1 and its commit rule corrected; the Windows section and Step 4 updated; Status rows for Phase 0 (done) and 0b (next). This entry | #6 |

### Next

- Shira's Windows session: Phase 0b on branch `phase-0b-windows`, stopping at Gate 0b.
- Before Phase 1: install the `claude` command-line tool on the Windows machine (Phase 0 step 4),
  and Shira confirms the Gate 1 stop rules.

---

## Session 4 — 2026-10-16

**Who:** Shira, with Claude in the Claude desktop app (Code tab) on Windows 10, Git Bash, Python
3.11.0. **Base:** `main` at `ae4dc96`; `framework/main` still `24092db`.

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
    `pip` or `venv`; running it needs `sudo apt install python3-venv`, a change to Shira's WSL that
    this session did not make without asking. Run by the cloud session instead — see "Linux check"
    below.
- **Seen, not fixed:** `classkit write` ("created  course\units\probe.md") and ingest's "logged …"
  line still print Windows paths with backslashes. Display only, nothing committed is affected, and
  outside the plan's list — for Shira to decide.

### Commits — each can be cherry-picked into `class-framework` on its own

| Commit | Fixes |
|---|---|
| `33e0041` | UTF-8 in and out: the `ingest` crash on a code-page console, garbled em dashes, and text piped into `classkit write` saved garbled. New `tests/test_encoding.py` |
| `f6f0fe1` | Forward slashes: `LOG.md`'s scaffold entry, validate's finding locations, scaffold's report, add-url's message |
| `290ac7a` | `classkit scaffold course` writes `course/.gitattributes` (`* text=auto eol=lf`): no false "edited by hand" on a Windows clone. Spec and MANUAL-TESTING updated. An existing course repo needs the file added and `git add --renormalize .` once |
| `e9e1e7f` | Tests: six fixtures written with LF; the two permission tests skip on Windows. Test-only |
| `fb87f00` | This entry; the plan's Phase 0b Status row |
| the next commit | The Linux check below; Status row: Gate 0b met (cloud session) |

Not opened as a pull request from this machine; the cloud session opened and merged it.

### Linux check (cloud session, same day)

Run on branch `phase-0b-windows` at `fb87f00`, in a fresh environment (Linux, Python 3.13.16):

- `pytest -q -rs`: **409 passed, none skipped** — the two permission tests run and pass on Linux,
  as they should. **Gate 0b is met.**
- **The encoding test catches the bug on any system.** With the `use_utf8()` call disabled,
  both tests in `tests/test_encoding.py` fail on Linux too: `ingest`'s report fails, and the text
  piped into `classkit write` is saved garbled. Restored, both pass.

### Next

- ~~Gate 0b still needs `pytest` on Linux or macOS~~ — done by the cloud session; Gate 0b met.
- `phase-0b-windows` merged into `main`. Shira tells Avin about the four commits.
- Before Phase 1: the `claude` command-line tool (Phase 0 step 4), and the Gate 1 stop rules.

---

## Session 5 — 2026-10-16

**Who:** Shira, with Claude in the Claude desktop app (Code tab) on Windows 10. **Base:** `main` at
`0c125b8`.

### What happened — Phase 0 step 4, the `claude` command-line tool

- **Installed** with the method Anthropic's setup page recommends for native Windows
  (code.claude.com/docs/en/setup, "Native Install"), from PowerShell, no administrator rights:
  `irm https://claude.ai/install.ps1 | iex`. It installed **Claude Code 2.1.301** at
  `C:\Users\shira\.local\bin\claude.exe`. The binary's Authenticode signature is valid, signed by
  "Anthropic, PBC".
- **PATH.** The installer reported that `C:\Users\shira\.local\bin` was not on the PATH. Fixed with
  the two PowerShell commands from the docs' troubleshooting page ("Verify your PATH"), which append
  it to the **User** PATH only; the previous User PATH was saved first (in the session's scratchpad).
- **Verified in Git Bash:** a fresh login shell (Git for Windows `bash 5.2.37`, `MINGW64`) with the
  PATH as a new terminal gets it finds `/c/Users/shira/.local/bin/claude`, and `claude --version`
  prints **`2.1.301 (Claude Code)`**. Shells already open — including the desktop app's — keep the
  old PATH until they are restarted.
- **`claude doctor`:** native install 2.1.301, `win32-x64`, search OK. Its one warning, "not in
  your PATH", came from its process inheriting the desktop app's old PATH; the fresh-shell check
  above shows the fix. Two things to know:
  - **Not signed in.** The command-line tool needs its own login (run `claude` once and follow the
    browser prompt) before Phase 1's `claude --plugin-dir` sessions. Not done here — it is Shira's
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

- Shira: restart the desktop app (so its shells see the new PATH), and sign the command-line tool in
  (`claude` in Git Bash, once).
- Before Phase 1: Shira confirms the Gate 1 stop rules.

---

## Session 6 — 2026-10-17

**Who:** Shira, with Claude in the claude.ai cloud session. **Base:** `main` at `4fcb7a8`.

### What happened

- Merged session 5's log entry (branch `phase-0-cli`, PR #8). Reviewed first: the installer is
  Anthropic's native one, the signature is valid, and only the User PATH changed, with a backup.
- Shira restarted the desktop app and signed the command-line tool in (reported by Shira; not
  verified here). Phase 0 is complete.
- Explained to Shira the difference between the framework and a plugin, and how each part of the
  framework maps to a plugin part: commands, agents, skills, schemas and templates carry over as
  they are; what changes is how `classkit` is installed, how the always-on rules reach Claude, and
  where permissions live — exactly what checks C1, C3 and C6 test.

### Decisions (Shira)

- **The Gate 1 stop rules are confirmed as written:** C1 or C3 failing means stop; C4 failing means
  pause until fixed or explained; C2 and C7 are not stops; C5 and C6 are problems to fix.
- C5 (a second person installs it) and C7 (per-course pin) are also run in the **desktop app's Code
  tab**, which teachers are likely to use.

### Commits

| Commit | What | Pull request |
|---|---|---|
| this commit | The plan: stop rules confirmed; Phase 1 records `claude --version`, says who runs which check, adds the desktop app to C5 and C7, and notes the WSL setup C2 needs on Shira's machine; Status: Phase 1 next. This entry | #9 |

### Next

- Shira's Windows session: Phase 1 on branch `phase-1-spike` — build first, then the checks, with
  C4 last. Stop at Gate 1.

---

## Session 7 — 2026-10-17

**Who:** Shira, with Claude in the Claude desktop app (Code tab) on Windows 10. **Base:** `main` at
`5eaee23`. **Versions:** `claude --version` → `2.1.301 (Claude Code)`; Python 3.11.0 (`python`,
`py -3`); `python3` is the Microsoft Store placeholder.

### What happened — Phase 1, Build items 1–10 (the checks are not started)

On branch `phase-1-spike`. Details and smoke-test numbers in `dev/reviews/plugin-spike.md`.

- **Item 1.** 60 tracked files copied into `plugin/` (agents, skills, commands, schemas,
  templates, methodologies, defaults, `src/classkit`); each folder identical to its original.
  `report-mode.sh` and `.claude/settings.json` not copied.
- **Items 2–4.** `plugin.json` (`class-agent-kit`, `displayName` "Class Agent Kit", `0.1.0-spike`,
  author Shira); `marketplace.json` (`agent-based-class`, source `./plugin`, plus a `description` —
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
  puts it at about 199 characters for user `shira` — computed, not observed; C1 shows the real
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

- Phase 1 checks, C4 last. The session runs what it can (C2's eval needs WSL2 on this machine, per
  the plan); Shira follows given steps for C1's second session, C3's `/clear` and `/compact`, C5,
  C6 and C7.

---

## Session 8 — 2026-10-17

**Who:** Shira, with Claude in the claude.ai cloud session: a review of session 7's build.
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

- Check C1 on Shira's Windows machine: a real `claude --plugin-dir` session in a throwaway course,
  then a second session. Shira runs the sessions; the working session gives her the steps.
