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

**Windows: pass** (2026-10-18; session 2 below). Mac: deferred (see the plan).

Windows (Git Bash), Shira's machine; Claude Code 2.1.301 in session 1, 2.1.302 in session 2. Session 1 was run by
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

### Session 2 — 2026-10-18, same repository, now holding the course

Run by Shira in a new Git Bash, one step at a time, guided from the Windows session; the outputs are
from her screenshots, the hook timings from `bootstrap.log`.

| Time | Step | Result |
|---|---|---|
| 16:44:15 | `claude --version` | **`2.1.302 (Claude Code)`** — the update installed during session 1 |
| — | `claude --plugin-dir C:/Projects/agent-based-class-plugin/plugin` | **Ready immediately** (Shira). `bootstrap.log`: **one** hook run, 16:45:54 — "venv ready", published, all in the same second. **No install.** No second, unexplained run this time, which fits (does not prove) the guess that session 1's came from Claude Code's first-run setup |
| 16:48 | The rules question | **"Yes"**: the heading "Class Agent Kit — rules for this course", and the banned words "topic" and bare "question" — **at startup, no `/clear` needed**, since `course/course.yaml` existed when the session began |
| 17:15 | `command -v classkit`; `echo "$CLASSKIT_VENV"`; `classkit status` | `/c/Projects/agent-based-class-plugin/plugin/bin/classkit`; `C:/Users/shira/.claude/plugins/data/class-agent-kit-inline/venv-8ff0bb76164b`; `classkit status` printed the "C1 empty" course correctly — syllabus not started, 2 units in `course.yaml` and none on disk, no materials, last log entry the scaffold |
| — | Permission mode | Auto mode again ("auto mode on"); no prompts. C6 needs default mode (finding 4) |
| 17:35 | `classkit doctor` (Claude Code's own prompt suggestion, which Shira sent; so were the next two) | "Nothing to fix on this machine; 3 note(s)". **ok:** `course/.gitignore` keeps `private/` and `private-text/` out of git; no private material; "dependencies import: PyYAML, jsonschema, python-pptx, python-docx, pypdf, fonttools". **notes:** `course/.gitignore` not committed yet (true: nothing in `c1-empty` is committed), pandoc and LibreOffice not installed. Last line: **"ok working mode: teacher (`classkit mode` to switch)"**, finding 7. Claude offered to commit `.gitignore` and waited for a go-ahead |
| 17:42 | `classkit validate` | **0 alerts, 0 errors, 2 warnings**: `syllabus_workload_missing` and `unit_count` ("0 of 2 units exist so far"). The same output, line for line, as the plugin's `classkit` on Linux on a freshly scaffolded two-unit course (cloud session). Unprompted, Claude also noted that `course.yaml`'s 2 units differ from the rules' "12–13 per semester": the injected rules are used, not only present |
| 17:47 | `classkit ingest --preflight` | "Pre-flight — nothing has been converted or written." / "materials/source/ is empty: no files, and no links in links.md." The same as on Linux |

**Verdict — C1 on Windows: pass.** `classkit` runs as a bare command from the plugin; the first
session installed the environment in **48 s** at session start, and the second needed **no install**
and started at once; the rules arrive at startup in a course repository, and after `/clear` once a
course has been created. The read-only commands a teacher runs most — `status`, `doctor`,
`validate`, `ingest --preflight` — all work through the plugin, and the two compared with Linux
match it exactly.

### Findings from session 2

6. **Claude recommends commands by their old names.** After `classkit status`, Claude suggested
   `/ingest` and `/plan-syllabus`. In a plugin session those names don't exist; they are
   `/class-agent-kit:ingest` and `/class-agent-kit:plan-syllabus`. The names come from `classkit
   status`'s own output ("run /plan-syllabus", "/ingest writes materials/coverage.md") and the
   copied prompts. Already planned for Step 5 (renaming, including the Python code's messages);
   this is the first time it was seen to mislead in a live session. Whether a bare `/ingest` still
   resolves in a plugin session was not tried; the assessment assumes it does not (§5.4).
   **Session 13:** Claude Code's own prompt suggestions — the grey text it puts in the input box
   after a reply, sent with Enter — carried the same names (`/plan-syllabus`, `run /plan-syllabus`),
   so a teacher is offered the old name ready to send. Fixing the names Claude uses fixes these too.
7. **"Working mode" leaks into the plugin.** `classkit doctor` ends with "working mode: teacher
   (`classkit mode` to switch)". A plugin has no working mode: Build step 1 left the mode hook out
   on purpose, but `mode.py`, the `classkit mode` command and doctor's line came in with the copied
   `src/classkit/`. With no framework in the course repository, `find_framework_root()` falls back
   to the plugin's own folder, so the marker it reads is the plugin's `dev/.developer`. Tried in the
   cloud session (Linux), from a course folder: with the plugin loaded from this git checkout,
   `classkit mode developer` **refuses**, telling the teacher to add a rule to `.gitignore` — the
   plugin's, which a teacher should never touch; with a copy of the plugin folder outside any git
   repository (as an installed plugin may be — not checked), it **creates `dev/.developer` inside
   the plugin folder**, and doctor reports "framework-developer" from then on for every course using
   that copy. Harmless until someone runs the command. Fix with Step 5's Python changes: under the
   plugin, doctor drops the line and `classkit mode` says it does not apply.

## C2 — inside evals

Not run yet.

## C3 — the core rules reach the session

**Windows: pass** (2026-10-18, session 12).

Windows (Git Bash), Shira's machine, Claude Code 2.1.302, Auto mode. Run by Shira one step at a
time, guided from the cloud session, after pulling the finding-1 fix (`8983818`). Each question
began "Without running any command or reading any file", and asked for IDs **not yet named in the
conversation**, so a right answer could come only from the rules — not from the conversation, a
summary of it, or general knowledge. `core.md` is 6,877 characters (Python `len`), 3,123 under the
10,000 cap.

| Time | Where, and what came before | Asked | Answer |
|---|---|---|---|
| 18:17 | `C:\Projects\c1-empty` (course in `course/`), at startup | The ID of a Guiding Question; the banned words | **`U01-S02-G1`**; "topic" and bare "question". Said the rules came from the plugin's hook |
| 18:19 | Same session, after **`/compact`** | The ID of an In-Class Session and of an Assessment Item | **`U01-IC`**, **`U01-I01`** |
| 18:21 | Same session, after **`/clear`** | The ID of a Unit Objective; how to cite slide 18 of material 7 | **`U01-O1`**, **`M0007#slide-18`**, adding the rule to write a locator in full, never `#slide-18` |
| 18:23 | A new session **started inside `course/`** — the case finding 1's fix added | The ID of an Activity and of a Course Outcome | **`U01-A1`**, **`CO1`** |
| 18:24 | A new session in **`C:\Projects\c3-nocourse`**, an empty folder with no course above it | Are the rules in context? Is the skill `class-agent-kit:course-reference` there? | **No** to the rules, **yes** to the skill: the plugin is loaded and the rules hook stays silent |

**The hook really ran each time.** `bootstrap.log` records every SessionStart (the bootstrap hook
runs beside the rules hook, with no matcher). It shows runs at **18:18:51** — between the 18:17
answer and the 18:19 one, where the only step was `/compact` — **18:21:34** (`/clear`), **18:22:42**
(the session in `course/`) and **18:24:30** (the empty folder), each about a second, the venv ready.
So after `/compact` the rules were **injected again**, not merely left over from before it. (The
startup run itself was above the 14 lines read; the 18:17 answer shows it happened.)

**Verdict — C3 on Windows: pass.** The rules are there at startup, after `/compact`, after `/clear`,
and in a session started inside `course/`; they are absent where there is no course, while the
plugin stays loaded. Not run on Linux or a Mac: `rules.sh` is the same script, and its course
detection is covered by `tests/test_plugin_rules_hook.py` on Linux and Windows.

## C4 — make a course with the plugin

Not run yet.

## C5 — a second person installs it

Not run yet.

## C6 — permissions

**Windows, through Bash: pass. Through PowerShell: fails — finding 9** (2026-10-18, session 12).

Windows (Git Bash), Shira's machine, Claude Code 2.1.302, in `C:\Projects\c1-empty`. Started with
`claude --permission-mode default --plugin-dir …`; the status line read **"manual mode on"**, not
Auto (finding 4), so a missing prompt means the rule matched. Run by Shira one step at a time,
guided from the cloud session.

**The settings file**, created by Shira from Git Bash (there was no `.claude/` before, and no
`settings.local.json` after): `C:\Projects\c1-empty\.claude\settings.json`

```json
{
  "permissions": {
    "allow": [
      "Bash(classkit validate:*)",
      "Bash(classkit status:*)",
      "Bash(classkit doctor:*)",
      "Bash(classkit ingest --preflight:*)"
    ]
  }
}
```

The plan named three commands; `ingest --preflight` was added because the framework's own
`.claude/settings.json` allows it too, and it is read-only. These are the framework's plain-`classkit`
entries, without its `.venv/bin/` and `.venv/Scripts/` forms, which a plugin course has no use for.

| Time | Step | Result |
|---|---|---|
| ≈ 19:14 | Asked Claude to run the four commands, each on its own, exactly as written | Claude chose its **PowerShell** tool, not Bash. The prompt read "PowerShell command … `classkit validate` … This command requires approval", offering "Yes, and don't ask again for: `classkit validate *`". The `Bash(…)` rules do not cover a PowerShell call |
| ≈ 19:16 | Approved once ("Yes"), to see what PowerShell does | PowerShell **found** a `classkit` on its path — the only one is the plugin's `bin/classkit`, so the plugin's `bin/` reaches PowerShell too (inferred) — but it is an extensionless shell script, so Windows treated it as a document: a **"How do you want to open this file?"** window (Photoshop, Firefox, …). Nothing ran; the command printed nothing, and Claude went on to `classkit status`, again through PowerShell, again asking |
| ≈ 19:26 | Closed the Windows window without choosing; answered "No"; told Claude PowerShell cannot run `classkit` and to use the Bash tool | — |
| 19:28 | The four commands through **Bash** | **No prompt for any of them.** Last lines: "0 alerts, 0 errors, 2 warnings"; "Last log 2026-10-18 — classkit scaffold course"; "Nothing to fix on this machine; 3 note(s)."; "materials/source/ is empty: no files, and no links in links.md." Claude also said the earlier PowerShell run "printed nothing at all, so I didn't count it" |

**Verdict.** The course's own `.claude/settings.json` does what C6 asks, through Bash: the four
read-only commands run with no prompt. But on Windows Claude may reach for PowerShell first, and
there `classkit` neither runs nor matches the rules.

### Finding from C6

9. **On Windows, Claude can run `classkit` through PowerShell, which cannot run it.** Claude Code
   2.1.302 on Windows has a PowerShell tool, and Claude chose it unprompted. The plugin's `classkit`
   is a POSIX shell script, and `CLASSKIT_VENV` is published to Bash only (`CLAUDE_ENV_FILE`).
   PowerShell finds the file but asks Windows which program should open it: a baffling window for
   a teacher, no output, and a permission prompt the course's `Bash(…)` rules cannot prevent. In C1
   and C3 (Auto mode) Claude used Bash; what made it choose PowerShell here is not known. Ways to
   fix, not yet chosen: a line in `rules/core.md` that `classkit` runs through the Bash tool only;
   a Windows `bin/classkit.cmd` that finds the venv on its own; and checking whether a setting can
   keep Claude to Bash in a course. **Before C4**, which runs on Windows and calls `classkit` often.

### Finding 9 fixed and tested — 2026-10-21, session 13

The fix (approved by Shira): the course's `.claude/settings.json` sets
`"env": {"CLAUDE_CODE_USE_POWERSHELL_TOOL": "0"}` beside the four permissions, and `rules/core.md`
says to run `classkit` with the Bash tool, never PowerShell (`efc2203`). Windows, Claude Code
2.1.302, then 2.1.306 after it updated itself; both sessions in default mode ("manual mode on"), with
the same request: "do you have a tool named PowerShell?", then the four commands, naming no shell.

| Started in | Settings that applied | PowerShell tool? | Result |
|---|---|---|---|
| `C:\Projects\c1-empty` (2.1.302) | The course's: the switch and the four permissions | **No** | All four through **Bash**, **no prompt**, no Windows window. Same last lines as in C6 |
| `C:\Projects\c1-empty\course` (2.1.306) | **None**: the settings file in the folder above is not read | **Yes** | Claude chose **Bash** anyway, quoting the rules ("PowerShell can't run it on Windows. So I'll use Bash"). Each command **asked permission** (Bash), since the permissions did not apply either; approved once each, all four ran and printed the same last lines |

**Verdict: finding 9 is fixed.** The setting removes PowerShell where it applies; the rules line
keeps Claude on Bash where it does not.

**Finding 11:** a course's `.claude/settings.json` applies only to a session started in the folder
that holds it — here the repository's top folder — not to one started in a subfolder, even inside
the same git repository. So a teacher should start Claude from the course repository's top folder;
started in `course/`, the rules still arrive (finding 1's fix), but the pre-approved permissions and
the PowerShell switch do not.

## C7 — per-course pin, no install step

Not run yet.
