# Plugin spike — Phase 1 measurements

Branch `phase-1-spike`, from `main` at `5eaee23`. One section per check (C1–C7), filled as each is
run. Each says what was run, the result with numbers, and a verdict: pass / fail / pass with a cost.

## Environment

Recorded at the start of the build, 2026-10-17 (the command-line tool updates itself, so record it
again at the start of each later session).

| | |
|---|---|
| Machine | Shira's Windows 10 Pro 10.0.19045, Git Bash (`bash 5.2.37`, `MINGW64_NT-10.0-19045`) |
| `claude --version` | `2.1.301 (Claude Code)` — native install, `C:\Users\shira\.local\bin\claude.exe` |
| Python | `python` → 3.11.0; `py -3` → 3.11.0; `python3` → the Microsoft Store placeholder (does not run Python) |

## Build — what exists, and what was checked before the checks

Built per the plan's Build items 1–10. Hand smoke tests of the scripts, with the plugin variables
set by hand — **not** checks C1 or C3, which need a real plugin session:

- **`bootstrap.sh`** (fake `CLAUDE_PLUGIN_DATA`, `CLAUDE_ENV_FILE`): first run **40 s** (venv +
  `pip install` of 6 packages, 15 with their dependencies), second run **1 s**; stdout empty both
  times; `export CLASSKIT_VENV="C:/Users/shira/.ck-smoke/venv-8ff0bb76164b"` appended to the env
  file. Python found: `python`, after `python3` was correctly rejected as the Store placeholder.
- **Windows path-length limit — a real risk, seen here.** With the data folder under the session's
  long scratchpad path, `pip` failed on a deep `lxml` file (`python-docx` depends on `lxml`):
  `OSError … Windows Long Path support`. The hook did as designed: exit 0, nothing on stdout, a
  message on stderr, the partial venv removed, a retry at the next session (27–39 s each time). The
  real data folder, `C:\Users\<user>\.claude\plugins\data\<plugin id>\venv-<hash>\…`, puts that
  file at **about 199 characters for user `shira`** (computed, not observed) — under 260, but a
  username longer than about 60 characters, or a longer plugin id, would fail. C1 will show the
  real path.
- **`bin/classkit`:** with no `CLASSKIT_VENV`, it prints what is wrong and how to fix it, exit 1.
  With it, from a folder outside this repository: `scaffold course`, `validate` (0 errors),
  `status`, and a piped `write` of `→` and Hebrew saved byte for byte. `find_framework_root()`
  returned `plugin/`, as intended.
- **`rules.sh`:** in a course, valid SessionStart JSON whose `additionalContext` equals
  `core.md`; without `course/course.yaml`, silent (no stdout, exit 0); with a 10,002-character
  `core.md`, a loud stderr message and exit 2; with no Python on `PATH`, `core.md` as plain stdout.
- **`rules/core.md`: 6,877 characters** (limit 8,000; Claude Code's cap 10,000). The source
  sections of the root `CLAUDE.md` it condenses are 14,756.
- **`claude plugin validate --strict ./plugin`: passed.** **`claude plugin validate --strict .`:
  passed** after adding a marketplace `description` (the one warning without it). One piece of
  advice, which does not change the verdict: the root README has no install line.

## C1 — `classkit` as a bare command

**In progress.** Windows (Git Bash), Shira's machine; Claude Code 2.1.301. Session 1 was run by
Shira, step by step, guided from the cloud session; the outputs below are what she pasted back.
The Mac half is deferred (see the plan).

### Session 1 — 2026-10-18, in the empty repository `C:\Projects\c1-empty`

Started from a clean slate: no plugin data folder on the machine (checked by the Windows session).

| Time | Step | Result |
|---|---|---|
| 14:44:31 | `claude --plugin-dir C:/Projects/agent-based-class-plugin/plugin`, in a new Git Bash | Claude Code's own one-time setup questions came first: "flicker-free rendering" and "Claude in Chrome extension detected" (answered: browser tools off). Neither comes from the plugin |
| ≈ 14:47 | Ready to type | About 2–3 minutes from launch, **including** answering those questions and the plugin's first install; the install alone is not separable from this. The Windows session reads the install time from `bootstrap.log` |
| — | Permission mode | The session ran in **Auto mode** (Shira's Claude Code default): an automatic checker approves routine actions. **No permission prompt appeared**; the tool results read "Allowed by auto mode classifier" |
| 14:48 | The rules question, before any course existed | **"No"** — as expected, since there was no `course/` when the session started. Claude did see the plugin's `class-agent-kit:course-reference` skill, so the plugin was loaded |
| 14:53 | `command -v classkit` | **`/c/Projects/agent-based-class-plugin/plugin/bin/classkit`** — the plugin's own copy |
| 14:53 | `echo "$CLASSKIT_VENV"` | **`C:/Users/shira/.claude/plugins/data/class-agent-kit-inline/venv-8ff0bb76164b`** — the bootstrap hook built the venv and published it. No long-path failure |
| 14:53 | Asked to "create a new course here: title "C1 empty", 2 units" | Claude found `classkit scaffold course` on its own (rules not loaded), but ran it with **`--path .`**, putting the course at the repository's top level instead of the usual `course/` subfolder: 15 files created, exit 0 |
| 14:56 | Asked to undo that and create the course again in the default place | Claude deleted the 15 files and 12 folders by name (checked first that nothing else was there), then `classkit scaffold course --title "C1 empty" --units 2`: **15 created in `course/`**, exit 0. It then said later `classkit` commands must run from inside `course/`, which is not right: `find_course_root()` also finds `course/course.yaml` from the repository's top folder |
| ≈ 15:30 | — | Claude Code showed "Update installed · Restart to update": the command-line tool updated itself during the session (still 2.1.301 until restarted), so session 2 runs on a newer version |
| 15:32 | `/clear`, then the rules question again | **"Yes"**: it quoted the heading "# Class Agent Kit — rules for this course" and named the banned words, "topic" and bare "question" |

**Session 1 verdict:** the core of C1 holds on Windows. `classkit` runs from the plugin; the
plugin installed its own environment at session start, without error; and the rules hook behaves as
designed — silent while there is no course, loaded by `/clear` once `course/course.yaml` exists.
Still to come: session 2.

### The data folder, the install time and the long-path limit

Read on the machine by the Windows session after session 1, from the folder itself and its
`bootstrap.log`.

- **Real path:** `C:\Users\shira\.claude\plugins\data\class-agent-kit-inline` — 58 characters.
  The venv is `venv-8ff0bb76164b` inside it, 3,926 files and folders. It is the only plugin data
  folder on the machine.
- **Install time: 48 s** (`bootstrap.log`: venv created 14:46:18, "installed in 48s" 14:47:06),
  Python 3.11.0 found as `python`. No error. 14 packages installed (the 6 required and their
  dependencies).
- **The hook started at 14:46:17, not at launch (14:44:31).** The 1 min 46 s before it was Claude
  Code's own first-run questions. So of the "2–3 minutes" to the prompt, about 48 s was the plugin.
- **The hook ran three times in session 1:** 14:46:17 (install), **14:47:14** ("venv ready", 8 s
  after the install finished), and 15:32:01 (the `/clear`). The second run matches no step Shira
  took — observed, not explained. A guess, unverified: Claude Code started the session again after
  its first-run setup. It did no harm (the venv was ready, 1 s).
- **Longest path: 190 characters**, a compiled `jsonschema` test file:
  `…\class-agent-kit-inline\venv-8ff0bb76164b\Lib\site-packages\jsonschema\tests\typing\__pycache__\test_all_concrete_validators_match_protocol.cpython-311.pyc`.
  The `lxml` file that failed under the long scratchpad path in session 7 is 186 here. No path is
  over 200.
- **Under the marketplace name** (`class-agent-kit-agent-based-class`, 11 characters longer), the
  longest would be **201 characters** (the `lxml` file 197) — **58 under** Windows' limit of 259
  usable characters. So the install fails only for a Windows user folder name longer than about
  **63 characters** (here `shira`, 5) — or if a later dependency installs deeper files.
- **Long-path limit: not hit.** The install completed and nothing in the folder approaches it.

### Findings from session 1

1. **The rules hook misses a course at the top level.** `rules.sh` looks only for
   `course/course.yaml`; `classkit` also accepts `course.yaml` at the top
   (`find_course_root()`). A course created with `--path .` would never get the rules. Fix: the
   hook checks both places.
2. **Without the rules, the conventions slip.** In the first session of a new course the rules are
   absent by design (no course when it started), and Claude read "here" literally. The prompt's
   wording invited it, but a teacher could say the same.
3. **No command to create a course.** Teachers are expected to ask in words. A dedicated command
   (for example `/class-agent-kit:new-course`) would apply the conventions, and could end by telling
   the teacher to run `/clear` so the rules load — `/clear` was shown to work (15:32).
4. **Auto mode hides permission prompts.** C6 (permissions) must be run with Claude Code in its
   default permission mode, or its result means nothing.
5. **The data folder name depends on how the plugin is loaded.** With `--plugin-dir` it is
   `class-agent-kit-inline`; installed from the marketplace it will be
   `class-agent-kit-agent-based-class`, 11 characters longer. The long-path measurement must allow
   for that.

## C2 — inside evals

Not run yet.

## C3 — the core rules reach the session

Not run yet.

## C4 — make a course with the plugin

Not run yet.

## C5 — a second person installs it

Not run yet.

## C6 — permissions

Not run yet.

## C7 — per-course pin, no install step

Not run yet.
