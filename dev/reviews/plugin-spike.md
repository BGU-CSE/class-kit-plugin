# Plugin spike — Phase 1 measurements

Branch `phase-1-spike`, from `main` at `5eaee23`. One section per check (C1–C7), filled as each is
run. Each says what was run, the result with numbers, and a verdict: pass / fail / pass with a cost.

## Environment

Recorded at the start of the build, 2026-10-17 (the command-line tool updates itself, so record it
again at the start of each later session).

| | |
|---|---|
| Machine | The Windows test machine: Windows 10 Pro 10.0.19045, Git Bash (`bash 5.2.37`, `MINGW64_NT-10.0-19045`) |
| `claude --version` | `2.1.301 (Claude Code)` — native install, `C:\Users\<user>\.local\bin\claude.exe` |
| Python | `python` → 3.11.0; `py -3` → 3.11.0; `python3` → the Microsoft Store placeholder (does not run Python) |

## Build — what exists, and what was checked before the checks

Built per the plan's Build items 1–10. Hand smoke tests of the scripts, with the plugin variables
set by hand — **not** checks C1 or C3, which need a real plugin session:

- **`bootstrap.sh`** (fake `CLAUDE_PLUGIN_DATA`, `CLAUDE_ENV_FILE`): first run **40 s** (venv +
  `pip install` of 6 packages, 15 with their dependencies), second run **1 s**; stdout empty both
  times; `export CLASSKIT_VENV="C:/Users/<user>/.ck-smoke/venv-8ff0bb76164b"` appended to the env
  file. Python found: `python`, after `python3` was correctly rejected as the Store placeholder.
- **Windows path-length limit — a real risk, seen here.** With the data folder under the session's
  long scratchpad path, `pip` failed on a deep `lxml` file (`python-docx` depends on `lxml`):
  `OSError … Windows Long Path support`. The hook did as designed: exit 0, nothing on stdout, a
  message on stderr, the partial venv removed, a retry at the next session (27–39 s each time). The
  real data folder, `C:\Users\<user>\.claude\plugins\data\<plugin id>\venv-<hash>\…`, puts that
  file at **about 199 characters for a 5-character user name** (computed, not observed) — under 260, but a
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

Windows (Git Bash), the Windows test machine; Claude Code 2.1.301 in session 1, 2.1.302 in session 2.
Session 1 was run step by step; the outputs below were pasted back from that machine.
The Mac half is deferred (see the plan).

### Session 1 — 2026-10-18, in the empty repository `C:\Projects\c1-empty`

Started from a clean slate: no plugin data folder on the machine (checked there first).

| Time | Step | Result |
|---|---|---|
| 14:44:31 | `claude --plugin-dir C:/Projects/agent-based-class-plugin/plugin`, in a new Git Bash | Claude Code's own one-time setup questions came first: "flicker-free rendering" and "Claude in Chrome extension detected" (answered: browser tools off). Neither comes from the plugin |
| ≈ 14:47 | Ready to type | About 2–3 minutes from launch, **including** answering those questions and the plugin's first install; the install alone is not separable from this. The install time is read from `bootstrap.log` afterwards |
| — | Permission mode | The session ran in **Auto mode** (the Claude Code default on that machine): an automatic checker approves routine actions. **No permission prompt appeared**; the tool results read "Allowed by auto mode classifier" |
| 14:48 | The rules question, before any course existed | **"No"** — as expected, since there was no `course/` when the session started. Claude did see the plugin's `class-agent-kit:course-reference` skill, so the plugin was loaded |
| 14:53 | `command -v classkit` | **`/c/Projects/agent-based-class-plugin/plugin/bin/classkit`** — the plugin's own copy |
| 14:53 | `echo "$CLASSKIT_VENV"` | **`C:/Users/<user>/.claude/plugins/data/class-agent-kit-inline/venv-8ff0bb76164b`** — the bootstrap hook built the venv and published it. No long-path failure |
| 14:53 | Asked to "create a new course here: title "C1 empty", 2 units" | Claude found `classkit scaffold course` on its own (rules not loaded), but ran it with **`--path .`**, putting the course at the repository's top level instead of the usual `course/` subfolder: 15 files created, exit 0 |
| 14:56 | Asked to undo that and create the course again in the default place | Claude deleted the 15 files and 12 folders by name (checked first that nothing else was there), then `classkit scaffold course --title "C1 empty" --units 2`: **15 created in `course/`**, exit 0. It then said later `classkit` commands must run from inside `course/`, which is not right: `find_course_root()` also finds `course/course.yaml` from the repository's top folder |
| ≈ 15:30 | — | Claude Code showed "Update installed · Restart to update": the command-line tool updated itself during the session (still 2.1.301 until restarted), so session 2 runs on a newer version |
| 15:32 | `/clear`, then the rules question again | **"Yes"**: it quoted the heading "# Class Agent Kit — rules for this course" and named the banned words, "topic" and bare "question" |

**Session 1 verdict:** the core of C1 holds on Windows. `classkit` runs from the plugin; the
plugin installed its own environment at session start, without error; and the rules hook behaves as
designed — silent while there is no course, loaded by `/clear` once `course/course.yaml` exists.
Still to come: session 2.

### The data folder, the install time and the long-path limit

Read on the machine after session 1, from the folder itself and its
`bootstrap.log`.

- **Real path:** `C:\Users\<user>\.claude\plugins\data\class-agent-kit-inline` — 58 characters,
  measured with a 5-character user name, as are all the lengths below.
  The venv is `venv-8ff0bb76164b` inside it, 3,926 files and folders. It is the only plugin data
  folder on the machine.
- **Install time: 48 s** (`bootstrap.log`: venv created 14:46:18, "installed in 48s" 14:47:06),
  Python 3.11.0 found as `python`. No error. 14 packages installed (the 6 required and their
  dependencies).
- **The hook started at 14:46:17, not at launch (14:44:31).** The 1 min 46 s before it was Claude
  Code's own first-run questions. So of the "2–3 minutes" to the prompt, about 48 s was the plugin.
- **The hook ran three times in session 1:** 14:46:17 (install), **14:47:14** ("venv ready", 8 s
  after the install finished), and 15:32:01 (the `/clear`). The second run matches no step
  taken — observed, not explained. A guess, unverified: Claude Code started the session again after
  its first-run setup. It did no harm (the venv was ready, 1 s).
- **Longest path: 190 characters**, a compiled `jsonschema` test file:
  `…\class-agent-kit-inline\venv-8ff0bb76164b\Lib\site-packages\jsonschema\tests\typing\__pycache__\test_all_concrete_validators_match_protocol.cpython-311.pyc`.
  The `lxml` file that failed under the long scratchpad path in session 7 is 186 here. No path is
  over 200.
- **Under the marketplace name** (`class-agent-kit-agent-based-class`, 11 characters longer), the
  longest would be **201 characters** (the `lxml` file 197) — **58 under** Windows' limit of 259
  usable characters. So the install fails only for a Windows user folder name longer than about
  **63 characters** (here 5 characters) — or if a later dependency installs deeper files.
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

Run in a new Git Bash, one step at a time; the outputs are from screenshots, the hook timings
from `bootstrap.log`.

| Time | Step | Result |
|---|---|---|
| 16:44:15 | `claude --version` | **`2.1.302 (Claude Code)`** — the update installed during session 1 |
| — | `claude --plugin-dir C:/Projects/agent-based-class-plugin/plugin` | **Ready immediately** (as reported). `bootstrap.log`: **one** hook run, 16:45:54 — "venv ready", published, all in the same second. **No install.** No second, unexplained run this time, which fits (does not prove) the guess that session 1's came from Claude Code's first-run setup |
| 16:48 | The rules question | **"Yes"**: the heading "Class Agent Kit — rules for this course", and the banned words "topic" and bare "question" — **at startup, no `/clear` needed**, since `course/course.yaml` existed when the session began |
| 17:15 | `command -v classkit`; `echo "$CLASSKIT_VENV"`; `classkit status` | `/c/Projects/agent-based-class-plugin/plugin/bin/classkit`; `C:/Users/<user>/.claude/plugins/data/class-agent-kit-inline/venv-8ff0bb76164b`; `classkit status` printed the "C1 empty" course correctly — syllabus not started, 2 units in `course.yaml` and none on disk, no materials, last log entry the scaffold |
| — | Permission mode | Auto mode again ("auto mode on"); no prompts. C6 needs default mode (finding 4) |
| 17:35 | `classkit doctor` (Claude Code's own prompt suggestion, sent as offered; so were the next two) | "Nothing to fix on this machine; 3 note(s)". **ok:** `course/.gitignore` keeps `private/` and `private-text/` out of git; no private material; "dependencies import: PyYAML, jsonschema, python-pptx, python-docx, pypdf, fonttools". **notes:** `course/.gitignore` not committed yet (true: nothing in `c1-empty` is committed), pandoc and LibreOffice not installed. Last line: **"ok working mode: teacher (`classkit mode` to switch)"**, finding 7. Claude offered to commit `.gitignore` and waited for a go-ahead |
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

**Linux: pass, with two adjustments** (2026-10-31, session 17). Not run on a Mac.

The claude.ai cloud workspace (Linux), Claude Code 2.1.316, Python 3.13. On Linux the eval
sandbox needs `bubblewrap` and `socat`; they were installed first (`apt-get install bubblewrap
socat`). The plugin was a copy of `plugin/` at `0.1.4-spike` in a scratch folder (`<scratch>/plugin`
below); nothing in this repository was changed for the runs. Command, every run:

```
claude plugin eval . --case <case> --runs 1 --ablation none --no-publish --max-cost-usd 2 \
  --scaffold --trust-plugin --keep-temp --allow-tools Bash --json <file>
```

One run per try, no no-plugin baseline (without the plugin there is no `classkit`), no judge model.

**The case** (`evals/c2-classkit-validate/`): `case.yaml` names `scaffold_script: fixture.sh`, which
copies a fixture course into the empty workspace — a fresh `classkit scaffold course --title "Eval
course" --units 2`, kept in the case folder (`fixture/course/`). `prompt.md` (`model: sonnet`,
`max_turns: 15`, `timeout_seconds: 900`, `allowed_tools: [Read, Glob, Grep]`):

```
Run `classkit validate` in this folder and copy its last line exactly as printed.
Then answer, without running anything: do you have instructions headed
"Class Agent Kit — rules for this course"? Answer RULES: yes or RULES: no.
```

Three graders, none paid: `tool_used` Bash matching `classkit\s+validate`; `regex` over the trace
for `0 alerts, 0 errors, 2 warnings` (what `classkit validate` prints for this fixture); `regex`
over the last message for `RULES:\s*yes`.

| Try | What | Result |
|---|---|---|
| 1 | The plugin as it is | **Score 0.67.** The SessionStart hooks ran: the setup built the venv in the run's own data folder (`<run>/config/plugins/data/class-agent-kit-inline/venv-…`) in **14 s**, network included (hooks run outside the sandbox), and published `CLASSKIT_VENV`; the rules reached the session (`RULES: yes`). But `classkit validate` → `classkit: command not found` (exit 127) |
| 2 | Diagnostic: Claude ran one fixed command printing `PATH`, `CLASSKIT_VENV`, and calling the wrapper by its full path | `PATH` held the shell's own entries only, **not the plugin's `bin/`**. `CLASSKIT_VENV` was set, but the sandboxed shell **could not see the venv**: `No such file or directory`. The plugin folder itself was readable |
| 3 | `PATH` with `<scratch>/plugin/bin` exported before the run; the setup script told (an `EVAL_` variable, below) to build the venv in `/tmp/ck-eval-data` | `classkit` found. The venv was built there (28 s), but the sandbox could not see `/tmp/ck-eval-data` either: `classkit: no Python found in …` |
| 4 | As 3, with the venv inside the plugin folder (`<scratch>/plugin/.eval-data`) | **Score 1.0.** `classkit validate` ran in the sandbox and printed the expected result; `RULES: yes`. 18 s |

The change for tries 3 and 4, in the scratch copy of `hooks/bootstrap.sh` only, before the
`CLAUDE_PLUGIN_DATA` check:

```bash
if [ -n "${EVAL_CLASSKIT_DATA:-}" ]; then CLAUDE_PLUGIN_DATA="$EVAL_CLASSKIT_DATA"; fi
```

and in the case's `prompt.md`: `env: {EVAL_CLASSKIT_DATA: <scratch>/plugin/.eval-data}`. A case's
`EVAL_*` variables reach the plugin's hooks.

**Cost:** about $0.07–0.11 a try with Sonnet, $0.36 for all four (the tool's list-price estimate,
taken from the plan's usage). **Install:** every run has a fresh home, so the venv is rebuilt each
time: 14–28 s.

Also seen: after each Bash command the sandboxed shell printed `…/cwd-…: Read-only file system`
(Claude Code's own working-directory file) and `classkit validate` showed exit 1; the output itself
was complete, and Claude read it correctly.

### Findings from C2

15. **In an eval run the plugin's `bin/` is not on the Bash tool's `PATH`**, so the bare
    `classkit` the prompts use is not found. The run inherits `PATH` from the shell that starts
    `claude plugin eval`, so that shell (a CI step, or a developer) can add the plugin's `bin/`.
16. **The eval sandbox cannot see the plugin's data folder** (under the run's Claude Code
    configuration), nor a folder made for it in `/tmp`, so `classkit` finds no Python. It can see
    the plugin folder. The
    venv has to be built where the sandbox can read it — in the trial, a folder inside the plugin,
    named through an `EVAL_` variable that only eval runs set.

## C3 — the core rules reach the session

**Windows: pass** (2026-10-18, session 12).

Windows (Git Bash), the Windows test machine, Claude Code 2.1.302, Auto mode. Run one step at a
time, after pulling the finding-1 fix (`8983818`). Each question
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

**Windows: accepted as passed** (decision, 2026-10-28, session 15), on what was seen; two of its
parts were not run.

On the Windows test machine, in the desktop app's Code tab, in a new folder `C:\Projects\c4-course`,
Claude Code 2.1.306:

- **Install:** the desktop app's Add marketplace, `shiraradshilo/agent-based-class-plugin#phase-1-spike`
  (the repository's main branch had no marketplace yet: "This repository isn't a marketplace — no
  manifest found"), then Class Agent Kit installed for all folders (scope user, `0.1.0-spike`). Its
  page showed 5 skills, 8 commands, the hook and 9 agents.
- **Course and materials:** the course was created in words; the materials were copied from a
  separate folder; `/class-agent-kit:ingest` ran to the end.
- **`/class-agent-kit:plan-syllabus`:** stepwise, as specified — the course's state, the evidence
  and 14 open questions asked one at a time ("Nothing is written yet"), then the full draft, revision
  rounds and approval. Its questions showed the materials were read (the 80% exam weight against the
  flipped method; a contradiction on an exam cover page) and their roles respected (a unit whose only
  material is the publisher's instructor-only slides). The draft: 7 Course Outcomes, a 13-unit map;
  `classkit validate`: 0 errors, 0 alerts, 2 warnings.
- **`/review-syllabus`**, asked for in words: the course-critic agent ran in the background and
  returned findings marked broken or "would have done differently"; the ones chosen were acted on.

**Not run:** the comparison of the plugin's `classkit` output with the original tool's on the same
files, and `/plan-units`.

## C5 — a second person installs it

Not run yet.

## C6 — permissions

**Windows, through Bash: pass. Through PowerShell: fails — finding 9** (2026-10-18, session 12).

Windows (Git Bash), the Windows test machine, Claude Code 2.1.302, in `C:\Projects\c1-empty`. Started with
`claude --permission-mode default --plugin-dir …`; the status line read **"manual mode on"**, not
Auto (finding 4), so a missing prompt means the rule matched. Run one step at a time.

**The settings file**, created from Git Bash (there was no `.claude/` before, and no
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

The fix (approved): the course's `.claude/settings.json` sets
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

**Windows: works, with commands — findings 12 and 13** (2026-10-21, session 13), in the terminal and in
the desktop app's Code tab. A course pins its version, but moving it takes the `ref` edit **plus**
`claude plugin update … --scope project` and a restart.

Windows (Git Bash), the Windows test machine, Claude Code 2.1.306, Auto mode, in `C:\Projects\c1-empty`
(already trusted). Started with plain `claude`, never `--plugin-dir`. Branch B, `c7-version-b`
(`d8db5ea`), is `phase-1-spike` with only `plugin.json`'s version changed to `0.1.0-spike-b`.

The course's `.claude/settings.json` kept the PowerShell switch and the four permissions, and gained:

```json
"extraKnownMarketplaces": {
  "agent-based-class": {
    "source": { "source": "github", "repo": "shiraradshilo/agent-based-class-plugin", "ref": "phase-1-spike" }
  }
},
"enabledPlugins": { "class-agent-kit@agent-based-class": true }
```

| Time | Step | Result |
|---|---|---|
| 12:17 | `claude`, the first start with these settings | **No install command and no question** (none seen). `classkit` on the path from `~/.claude/plugins/cache/agent-based-class/class-agent-kit/0.1.0-spike/bin/classkit` — the GitHub copy, not the local checkout. But **no rules and no `CLASSKIT_VENV`**: the plugin's SessionStart hooks did not run (finding 12) |
| 12:20 | `/clear` | The hooks ran: `bootstrap.log`'s **first** entry is 12:20:38 (nothing from 12:17), plugin root the cache copy; venv `venv-04b824dfb77a` installed in **44 s** (pip's cached wheels), no error. Rules then present |
| ≈ 12:30 | `ref` → `c7-version-b`; new session | **The plugin did not load at all**: no rules, no `classkit` on the path (finding 13) |
| 12:35 | `/reload-plugins` | "Reloaded: 2 plugins · 15 skills · 15 agents · 2 hooks". `classkit` now from `…/class-agent-kit/0.1.0-spike-b/bin/classkit`: **branch B loaded, mid-session**. Rules still absent — a reload runs no SessionStart |
| 12:37 | `/exit`, a fresh `claude` | **Again no plugin**: no rules, no `classkit` |
| 12:39 | What Claude Code recorded | `claude plugin list` lists **no** `class-agent-kit` (only a plugin synced from claude.ai). `claude plugin marketplace list`: `agent-based-class`, "GitHub (shiraradshilo/agent-based-class-plugin@c7-version-b)". `known_marketplaces.json`: `ref` `c7-version-b`, last updated 09:30:55Z (12:30:55 local). The cache holds `0.1.0-spike/` and `0.1.0-spike-b/` |
| 12:41 | `claude --debug-file …`, then `/exit` | At start, repeated: `Plugin "class-agent-kit" not cached at C:\Users\<user>\.claude\plugins\marketplaces\agent-based-class — run /plugin to refresh`, and `Plugin not available for MCP: class-agent-kit@agent-based-class - error type: plugin-cache-miss` |
| 12:49 | `claude plugin install class-agent-kit@agent-based-class --scope project`, from Git Bash in the course folder | "Successfully installed plugin: class-agent-kit@agent-based-class (scope: project)". `claude plugin list` now lists it: version `0.1.0-spike-b`, scope project, enabled |
| 13:03 | A fresh `claude` | **Everything at startup:** the rules present; `classkit` from `…/0.1.0-spike-b/bin/classkit`; `CLASSKIT_VENV` set to the same `venv-04b824dfb77a`, so nothing was reinstalled |
| 13:10 | `ref` back to `phase-1-spike`, installed; a fresh `claude` | Rules present, but `classkit` still from **`0.1.0-spike-b`**: once installed, the plugin does **not** follow a `ref` change by itself |
| 13:12 | `claude plugin update class-agent-kit@agent-based-class --scope project` | "Plugin "class-agent-kit" updated from 0.1.0-spike-b to 0.1.0-spike for scope project (C:\Projects\c1-empty). Restart to apply changes." `claude plugin list`: `0.1.0-spike` |
| 13:14 | A fresh `claude` | Rules present; `classkit` from **`0.1.0-spike`** |
| 13:21 | The **Claude desktop app's Code tab**, a session in `C:\Projects\c1-empty` ("Started on This computer · c1-empty", Auto) | **The same as the terminal:** rules present; `classkit` from `…/0.1.0-spike/bin/classkit`. No question about trust or plugins appeared in what was shown |

The documentation says this error means an install record points at a directory that is missing,
and gives the fix: `claude plugin install <name>@<marketplace>`, then `/reload-plugins`. Here
`claude plugin list` shows no install record at all, so the documented cause does not obviously fit;
why the start-up lookup misses while `/reload-plugins` finds the plugin is not known.

**Also seen:** the cache copy's venv is `venv-04b824dfb77a`, the `--plugin-dir` copy's
`venv-8ff0bb76164b`. The name is a hash of `requirements.txt`, so the two copies of that file differ —
most likely only in line endings (the Windows checkout converts to CRLF; `.gitattributes` does not cover
`.txt`). Not verified. Harmless: it cost one extra install.

### Findings from C7

12. **The first session after a course's settings bring the plugin in runs none of its start-up
    hooks**: no rules, and no `CLASSKIT_VENV`, so `classkit` fails ("start a new session"). `/clear` or
    a new session fixes it. Claude Code's documentation warns of the same for plugins that finish
    installing after the SessionStart hooks have run.
13. **After the course's `ref` changes, sessions start without the plugin at all** (`plugin-cache-miss`
    in the debug log), session after session; `/reload-plugins` loads the new version mid-session,
    without the rules. Cause not known. **One `claude plugin install class-agent-kit@agent-based-class
    --scope project` fixes it:** with an install record, the next session loads the plugin, rules and
    venv at startup. So "no install step" holds only until the course's `ref` first changes.
    Once installed, a later `ref` change is **not** followed by itself: the session keeps the installed
    version until `claude plugin update class-agent-kit@agent-based-class --scope project` and a
    restart (tested, back from `0.1.0-spike-b` to `0.1.0-spike`).

### The version check, tested — 2026-10-28, session 15

The check of `3bd65d2` (`plugin/hooks/inject_rules.py`, version `0.1.1-spike`), on the Windows test
machine, in the desktop app's Code tab and the terminal, Claude Code 2.1.306.

| Step | Result |
|---|---|
| `claude plugin marketplace update agent-based-class`, then `claude plugin update … --scope project` in `c1-empty` | "updated from 0.1.0-spike to 0.1.1-spike for scope project". The all-folders install (scope user, `0.1.0-spike`, made through the desktop app in C4) was left as it was, so as not to disturb C4's running session |
| Baseline: a new session in `c1-empty`, desktop app and terminal | No version notice; `classkit` from `…/0.1.1-spike/bin/classkit` |
| The course's `ref` changed to `version-check-b` (`0.1.1-spike-b`); a new session, "Where does my course stand?" | **No notice.** Claude Code's record of the marketplace still said `phase-1-spike`, so its copy offered `0.1.1-spike`, the running version — finding 14 |
| `~/.claude/settings.json` | `extraKnownMarketplaces` → `agent-based-class`, `source: git`, the repository's URL, `ref: phase-1-spike` — written by the desktop app's Add marketplace in C4 |
| A release instead: `0.1.2-spike` published (`1db0796`, no other change), `claude plugin marketplace update agent-based-class` | The marketplace copy offers `0.1.2-spike`; `c1-empty` still runs `0.1.1-spike` |
| A new session in `c1-empty` (desktop app), only "Where does my course stand?" | **The notice, unprompted, first:** "this session is running Class Agent Kit 0.1.1-spike, and version 0.1.2-spike is available. If you'd like, I can update it. You'd then need to close and reopen Claude Code…", then the course's status |
| "Yes, please update it." | Claude ran two commands and reported "updated Class Agent Kit from 0.1.1-spike to 0.1.2-spike for this course folder"; it left the all-folders `0.1.0-spike` alone, saying this course uses the folder's own install, and offered to update it too |
| A **New** session in the desktop app, `command -v classkit` | `…/0.1.2-spike/bin/classkit`. A new session in the app is enough; the whole app did not need closing |

Also seen: the desktop app's plugin page showed an enabled **Update** button once the marketplace
offered a newer version — another route for a teacher (not tried: which install it updates is not
known). The Code tab's plugin menu listed Class Agent Kit twice, apparently one entry per install.
The app's chat side has its own Plugins page, which lists only the claude.ai account's plugins.

14. **A marketplace added for the whole computer overrides a course's pin.** The desktop app's Add
    marketplace writes the marketplace into the personal `~/.claude/settings.json`; that declaration
    wins over the one in a course's `.claude/settings.json`, so changing the course's `ref` has no
    effect. Installing for all folders and pinning per course do not combine; one of them has to be
    the teachers' route.
