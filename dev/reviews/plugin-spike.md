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

Not run yet.

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
