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
