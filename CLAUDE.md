# Developing Class Kit

This repository develops the **Class Kit** plugin — the framework for building a flipped
course with Claude, shipped as a Claude Code plugin (D-049). It is never a teacher's course
repository: every session here is framework development.

**Start every session** by reading **`dev/PLUGIN-MIGRATION.md`** — the plan, its rules and its
current status — and the latest entry of **`dev/PLUGIN-LOG.md`**; add an entry to the log before the
session ends.

What a teacher sees — the rules, the commands, the agents — is in `plugin/`. The always-on teacher
rules are `plugin/rules/core.md`; their long reference is the `course-reference` skill.

## How to work

Be **honest, rigorous and unbiased**, whoever you are working with — a teacher or a developer. They
want a colleague who thinks, not one who agrees.

- **No reflexive agreement or praise.** Don't open with "good call", "great idea", "you're right".
  Assess the proposal on its merits and say what you actually think.
- **Disagree when you have a reason**, and give the reason. If you concede, say *what* changed your
  mind — an argument, not the fact that the person pushed back.
- **Name the cost of every decision**, including ones you agree with, and anything it contradicts
  elsewhere in the course or the spec. Say it *before* the decision is made, not after.
- **Separate fact from judgement.** Say what you verified, what you inferred, and how confident you
  are. Don't present a guess as a finding.
- **Critique your own earlier work** with the same rigour — including what you got wrong.
- Being direct is not being contrary: when something is right, say so plainly and move on.

**The vocabulary and the ID conventions** are in `plugin/rules/core.md` and apply here fully. They
are deliberately not copied here — two copies would drift.

## Setting up a developer checkout

```bash
pip install -e ".[dev]"
```

To try the plugin as a teacher would, open a throwaway course folder with
`claude --plugin-dir <this repository>/plugin`: it loads this working copy for that session only,
over any installed release. After editing plugin files, `/reload-plugins` picks up most changes; a
hook or rules change needs a new session.

## Where to start reading

Start at `dev/VISION.md` (why the project exists) and `dev/FRAMEWORK-SPEC.md` (what the framework
must contain; §2.3 and §8.10 for the plugin). `dev/ROADMAP.md` carries the implementation plan and
the ledger — **the ledger is authoritative for what actually exists**, because the spec deliberately
runs ahead of the code.

## Invariants — do not break these

1. **No course content in this repository.** No `course/` directory, no real units, no example
   course. Course content lives only in course repositories, created by `classkit scaffold`. Tests
   build a throwaway course in `tmp_path` instead.
2. **Nothing hardcodes methodology numbers.** "4 sessions", "25 minutes", "3–5 questions",
   "50 minutes" are read from the methodology file — the course's own in `course/methodologies/`,
   else `plugin/methodologies/`. A second methodology with different numbers must work without code
   changes.
3. **Downstream consumes `goals[]`, never the methodology.** The study-session schema is the
   contract between a methodology and everything else. Code that branches on
   `methodology.id == "question-driven-25"` is a bug.
4. **The class hour is built on the home study.** Activities reference that unit's Guiding
   Questions. An activity referencing none is permitted but flagged, and the **total unmapped
   time in an hour is capped** (`in_class.max_unmapped_minutes`). Legitimate exceptions exist —
   exam logistics, a current-events hook — but an hour made of them is a lecture. An agent never
   raises the cap, or accepts an exception, on its own; the teacher may (D-028, D-037).
5. **Nothing overwrites a teacher's work without permission — enforced in code, not by prompt.**
   Scaffolding is create-only (`write_new()` is the only way scaffold touches disk), and **every
   agent and command writes through `classkit.write.write()` / `classkit write`, which structurally
   refuses to overwrite existing content** without explicit confirmation (`--overwrite`) — see
   `FRAMEWORK-SPEC.md` §8.6 (D-030, D-031b). Silent loss of a teacher's authored work is
   unrecoverable — this is the one place the framework does not trust a prompt. **Scope (D-040):**
   the framework's commands and agents; an edit the teacher asks for directly in conversation is
   the teacher's own. To change part of a file, show `classkit write --diff`, then `--overwrite`.
6. **Templates must validate.** A fresh scaffold has to produce a course with zero errors,
   or `tests/test_course_lifecycle.py` fails. Change a schema → change the template.
7. **The plugin names its own files through `${CLAUDE_PLUGIN_ROOT}`**, never by a path relative to
   the course repository, which has none of them (`tests/test_plugin_prompt_paths.py`).

## Where things live

```
.claude-plugin/marketplace.json   the marketplace; lists the plugin at ./plugin
plugin/                    everything a teacher receives (FRAMEWORK-SPEC §8.10)
  .claude-plugin/plugin.json   name and version — the version changes only at a release
  commands/                /class-kit:<name> — new-course, ingest, plan-syllabus, review-syllabus,
                           plan-units, build-unit, review-unit, write-items, build-gem;
                           homework: plan-homework, build-homework, new-item-class
  agents/                  syllabus-designer, curriculum-architect, study-session-designer,
                           lesson-planner, assessment-writer, topic-researcher, gem-builder,
                           course-critic, material-classifier; homework: homework-planner,
                           homework-item-writer, item-critic, item-solver
  skills/                  course-reference, writing-a-syllabus, planning-units,
                           writing-guiding-questions, estimating-study-time; homework:
                           interviewing-teachers, planning-homework, writing-code-items,
                           writing-research-items, making-homework-documents
  rules/core.md            the always-on teacher rules, injected at session start
  hooks/                   hooks.json; bootstrap.sh (the Python venv); rules.sh + inject_rules.py
  bin/classkit             the classkit command; scripts/run_classkit.py
  schemas/*.schema.json    the content contract (JSON Schema draft 2020-12)
  methodologies/*.yaml     pluggable study-session designs
  defaults/time-constants.yaml   how long a study path is assumed to take
  templates/               what scaffold copies into a course
  src/classkit/
    frontmatter.py         Markdown + YAML front-matter parsing
    model.py               locating and loading a course tree; the methodology file in use
    scaffold.py            create-only content generation, the course's .claude/settings.json included
    write.py               the overwrite-safe write path — every agent and command writes here; remove() and --diff (D-040, D-041)
    log.py                 the course log, LOG.md — `classkit log`, append-only through write.append (D-036, D-038)
    ingest/                materials (D-035, spec §8.7): `classkit ingest`, `add-url`, `material`
    approve.py             `classkit approve syllabus | unit N | homework N` (D-043, D-046, HW-D35)
    status.py              `classkit status`: read-only overview (D-043, D-046)
    doctor.py              `classkit doctor`: this machine's copy — private files, .gitignore, deps (D-040)
    validate.py            schema layer + semantic rules; validate_homework.py, the homework rules
    cli.py                 argparse entry point
tests/                     scaffold → validate round-trip and the rest (fixtures in tmp_path); the plugin's hooks
.claude/                   this repository's own settings — never shipped
dev/                       never shipped
  VISION.md, FRAMEWORK-SPEC.md, ROADMAP.md, MANUAL-TESTING.md
  PLUGIN-MIGRATION.md, PLUGIN-LOG.md   the migration: plan and log
  homework/                homework's specification, plan, ledger and design history (HW-D…)
  reviews/                 assessments, reviews, the plugin trial's measurements
  _devlog/                 decisions, progress, open questions — kept, like the logs
```

## Before changing anything structural

Read `dev/FRAMEWORK-SPEC.md` first — it explains the layering, the contracts between layers, and
which constraints are load-bearing. **If your change alters structure or flow, update
`FRAMEWORK-SPEC.md` in the same commit**; it is the normative document, which the logs are not.

Then read `dev/_devlog/01-decisions.md`. Locked decisions are not to be relitigated; several
constraints that look arbitrary have a recorded reason. `dev/_devlog/03-open-questions.md` lists what
is genuinely undecided.

A decision marked `locked (design)` must get a row in `ROADMAP.md`'s ledger in the same commit.

## Adding a validation rule

Add the check to `Validator`, give it a code, and register its default severity in
`DEFAULT_SEVERITY` — every rule, errors included (the table is complete; an unregistered code
raises). Methodologies override severities in their `rules:` block, and a course overrides the
methodology in `course.yaml` `rules:`. Every rule needs a test in `tests/test_course_lifecycle.py`
that breaks a scaffolded course and asserts the code fires **at its severity** — a rule that never
fires is worse than no rule.

**Say which kind it is** (D-037). *Integrity* — it names something that does not exist, or a file
cannot be read — defaults to `error`. *Advisory* — something is missing or departs from the
methodology — defaults to `warn` (`alert` if it matters most). **The teacher is the authority:** do
not make a pedagogical check an error, and do not put pedagogical presence into a schema's
`required`, which would turn advice back into an error by the back door.

**Say which course state the rule judges** (D-033). A course is half-built for almost all of its
life, and invariant 6 requires a fresh scaffold to validate clean. A **consistency** rule (does
what is present hold together?) is always active. A **completeness** rule (was everything promised
delivered?) runs only once the course is complete — units on disk == `course.yaml` `units` — and is
reported as *skipped* until then. Getting this wrong produces a rule that fails every scaffolded
course and that teachers switch off.

## Branches

The repository is `BGU-CSE/class-kit-plugin`. Work lands in **`dev`**: the owner pushes to it,
everyone else opens a pull request into it, from a branch or a fork — and since **`main` stays the
default branch** (an install follows it), point a new pull request's base at `dev`. `main` is
protected and takes only releases: a pull request from `dev` with the version in `plugin.json` and a
`CHANGELOG.md` entry. An urgent fix branches from `main`, is released, and is merged back into `dev`.
On GitHub, rulesets enforce it: **`main`** — pull requests only, no force-push, no deletion;
**`dev`** — no force-push, no deletion (merged branches are deleted automatically, so `dev` must be
protected from it).

## Running things

```bash
pip install -e ".[dev]"
pytest
claude plugin validate --strict plugin
```

`classkit validate` needs a course, so it does nothing useful in this repository. Test against a
throwaway scaffold in a temp directory. For **hand-testing as a teacher would**, follow
`dev/MANUAL-TESTING.md` with the plugin loaded (`--plugin-dir`, above).

## The agent layer

The commands, agents and skills in `plugin/` are **teacher-facing**: they run in the *teacher's*
Claude Code, in their course repository. They reach teachers as a plugin release (D-049): an
improvement made here reaches a course when its teacher updates.

When editing agents:

- **Read the methodology, never hardcode it.** An agent that assumes 4 sessions of 25 minutes
  breaks every other teacher's course (D-011, invariant 2).
- **What goes where (D-044, spec §2.1):** the command is the procedure in the teacher's
  conversation (gates, writing, logging, and the revisions made with the teacher); an agent is sent
  off for a fresh context or for independence, and returns; a skill is the craft, loaded by the chat
  and the agents. Every `description` names the command it belongs to.
- **Craft shared by more than one agent — or by an agent and the chat — belongs in a skill**, so the
  designer and the critic judge by the same standard rather than drifting apart.
- **Agents must not fabricate resources.** No invented URLs, page numbers, or video titles. A
  fabricated study path validates cleanly and fails a student mid-session.
- **Agents write through `classkit write`**, never a raw file write (invariant 5).
- **Agents finish by running `classkit validate`** and fixing what it reports.

## Not built yet

PPTX export (D-006) and Moodle sync (D-004). Do not assume either exists. `dev/ROADMAP.md` has the
phases: what is done, what is next, and why each remaining phase exists.
