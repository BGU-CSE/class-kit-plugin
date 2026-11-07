# Changelog — Class Agent Kit

One entry per release: what changed for a teacher, and what they must do, if anything. The version is
`plugin/.claude-plugin/plugin.json`'s; a teacher sees an update offered at the start of a session.

## Unreleased

- **`README.md` and `GETTING-STARTED.md` describe the plugin**: installing it from the Claude desktop
  app, starting a course with `/class-kit:new-course`, updating, and a colleague or TA on the same
  course.

## 0.3.0 — 2026-11-05

- **The plugin is now called Class Kit.** Its commands are `/class-kit:<name>` — for example
  `/class-kit:plan-units` — and it comes from the marketplace `class-kit`.
- **`/design-unit` is now `/build-unit`**, so the commands read plan, build, review. A unit approved
  at the end of it is recorded as *built* (it was *designed*); units already approved as *designed*
  keep working, and `classkit status` shows them as built.
- **Claude names the commands in full**, so the commands it suggests are the plugin's.
- **A new course's settings bring the plugin in:** `/class-kit:new-course` writes the marketplace and
  the plugin into the course's `.claude/settings.json`, so a TA who opens the course is offered the
  plugin. A course created before keeps its settings file as it is.
- **The plugin lives in `BGU-CSE/class-kit-plugin`** on GitHub.

**To do — install it again, once per computer**, because the plugin and its marketplace have new
names. In a terminal:

```
claude plugin marketplace remove agent-based-class
claude plugin marketplace add BGU-CSE/class-kit-plugin
claude plugin install class-kit@class-kit
```

Removing the old marketplace uninstalls the old plugin; your courses are not touched. Then start a
new session.

## 0.2.1 — 2026-11-02

- **The agents now work to their standards.** Each agent — the syllabus and unit planners, the
  study-session designer, the critic and the others — was told to load its skill (how to write a
  syllabus, plan a unit, write guiding questions, estimate study time) but could not: it had no way
  to. Now each one starts with its skills loaded. Drafts and reviews made before this update were
  not held to them.
- **You are asked when a new version is out.** Once a day, at the start of a session, the plugin
  checks the version published on GitHub; when it is newer, Claude asks whether to update, and
  updates only if you say yes.
- **A course remembers which version worked on it.** Every entry in `course/LOG.md` now ends with
  the plugin version that wrote it. If a computer with an older version opens a course that a newer
  one has worked on, Claude says so first and offers to update; `classkit doctor` reports it too.

**To do:** start a new session after updating. Then run `/review-syllabus` and `/review-unit` on
what you have planned so far: the critic now reviews with its standards, which it did not have
before.

## 0.2.0 — 2026-11-02

The framework now lives in the plugin itself (Phase 3), with these changes for a teacher:

- **A new course gets its Claude Code settings** — `.claude/settings.json` beside `course/`: the
  read-only `classkit` commands run without asking, and on Windows `classkit` always runs through
  Bash. An existing course gets the file by running `classkit scaffold course` again (ask Claude);
  it only adds what is missing.
- **Your own methodology.** Put it in `course/methodologies/<name>.yaml` and name it in
  `course.yaml`; it is read before the plugin's, and updates never touch it. `classkit status` shows
  which methodology file is in use; `classkit validate` warns if yours reuses the plugin's name.
- **A missing Python is named**, with how to install it, instead of "start a new session".
- **The agents find the plugin's own files** — the methodology, the schemas, the default study
  times. Before, they pointed to folders a course repository does not have.

**To do:** start a new session after updating.

## 0.1.0-spike – 0.1.4-spike — 2026-10

The plugin trial (Phase 1): `classkit` from the plugin, the course rules at session start, the
version notice, `/class-agent-kit:new-course`.
