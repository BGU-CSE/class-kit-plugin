# Changelog — Class Agent Kit

One entry per release: what changed for a teacher, and what they must do, if anything. The version is
`plugin/.claude-plugin/plugin.json`'s; a teacher sees an update offered at the start of a session.

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
