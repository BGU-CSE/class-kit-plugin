# Plugin migration — implementation plan

**Date:** 2026-10-16 · **Lead:** Shira · **Decides go/no-go:** Avin · **Base:** `BGU-CSE/class-framework`
`main` at `24092db` — this repository's history up to that commit is identical to it ·
**Source:** [`dev/reviews/plugin-migration-assessment.md`](reviews/plugin-migration-assessment.md)
(the assessment; read it before this file)

This file is the working plan for every session in this repository. It does not repeat the
assessment: it says what to do, in what order, what to measure, and where this plan departs from the
assessment because the documentation was checked again on 2026-10-16.

---

## Why this repository exists

- The assessment recommends moving the framework to a Claude Code plugin, gated on a short spike.
- Avin proposed (2026-10-16) doing that work in a **separate repository led by Shira** rather than
  on a branch of `class-framework`, so his repository stays untouched while it is tried. He is
  **not yet convinced the plugin is the right approach**. The first job here is therefore to
  answer that question: Phase 1 is a go/no-go trial, and nothing after it starts without his OK.
- The repository starts from `class-framework`'s full history (not an empty copy), so fixes made
  there can still be merged here with git, and every later change shows as a diff against the
  original.

## Rules for every session in this repository

1. **You are in FRAMEWORK-DEVELOPER mode.** This repository is never a teacher's course repo. Run
   the Phase 0 setup once per checkout. `dev/CLAUDE.md`'s invariants still hold, except where this
   plan changes one explicitly.
2. **Port, don't rewrite.** Code, tests, agents, skills, commands, schemas and templates move
   across as they are. Changing behaviour needs a reason, recorded in this file or the devlog.
3. **One phase at a time.** Each phase ends at a **gate**: stop and report to Shira — what was done,
   what was measured, what is still open — and wait for her OK before starting the next.
4. **Tests stay green at every commit** (`pytest`). Once a plugin directory exists,
   `claude plugin validate --strict` must pass too.
5. **The course layout does not change.** A course built with `class-framework` must work here
   unchanged: `course/` is read and written exactly as today.
6. **Out of scope until Phase 5 is done:** the homework module (paused on purpose), the Gem builder
   and Q-030, and the `[design]` increments in `ROADMAP.md`.
7. **Upstream.** `BGU-CSE/class-framework` `main` is paused for new features during the trial;
   fixes may still land there. Before starting each phase, merge them:
   `git fetch framework && git merge framework/main`. Never push to `BGU-CSE/class-framework` from
   here.
8. **Where things are recorded.** Trial measurements → `dev/reviews/plugin-spike.md`. Decisions →
   `dev/_devlog/01-decisions.md` (next free number is **D-049**; check before using it). Progress →
   the [Status](#status) table at the end of this file, updated in the same commit as the work.
9. **Git.** One branch per phase (`phase-1-spike`, `phase-3-restructure`, …), a pull request, and
   Shira merges. If a tag push is refused from a cloud session, ask Shira to create the tag in
   GitHub instead.

---

## What changed since the assessment

Checked against the Claude Code documentation on 2026-10-16 (hooks, plugin loading, plugin
components, organization settings, plugin evals, marketplace hosting). These override the
assessment where they disagree.

| # | The assessment says | The documentation says | So, in this plan |
|---|---|---|---|
| 1 | Size limit on hook-injected context is **[unverified]** (§6.2, §10); check 3 tests the rules "at the full current size" | A hook's `additionalContext` is **capped at 10,000 characters**. Past that, Claude gets a file path and a 2,000-character preview and is not asked to read the file. No setting raises the cap | Root `CLAUDE.md` is 16,371 bytes; its teacher section alone is 14,054 characters. The core rules must be condensed to **≤ 8,000 characters** (a margin under the cap) in `plugin/rules/core.md`; everything else goes in a reference skill. Check C3 below replaces check 3 |
| 2 | `CLAUDE_ENV_FILE` is an **[inference]** (§6.1) | It exists for SessionStart hooks. Lines written to it run before **every** later Bash command in the session | The bootstrap hook writes `export CLASSKIT_VENV=…` there; the `classkit` wrapper reads it |
| 3 | Bootstrap must work in evals (§6.9) | In an eval run, Bash commands run in an OS sandbox: network only to granted domains, the home directory and Claude Code's configuration unreadable. **Hooks run outside the sandbox** | Install dependencies **in the hook, never in the wrapper**. The wrapper only runs, or fails with a clear message. Check C2 must grant Bash |
| 4 | "Enabled in project settings but isn't installed here" (§3) | True only for plugins with an **external** source. A plugin the marketplace lists by **relative path** loads from the marketplace copy once the repository's `extraKnownMarketplaces` applies, which happens after the folder is trusted | A TA who clones a course repo and trusts the folder gets the plugin with **no install command**. Verified by check C7 |
| 5 | No per-project version pin; mitigation is a warning only (§5.3, §6.7) | A GitHub or git marketplace source can name a `ref` (a branch or tag), and when a source declared in settings changes, Claude Code re-fetches the marketplace. That this works from a course repo's `extraKnownMarketplaces` is read from the docs, not yet tried | A course repo can pin the framework version by `ref` in its own settings, so upgrading becomes a commit in the course repo. Caveats: registration is per user (one person in two courses pinned differently flips between them); only after folder trust; not in cloud sessions; the re-fetch is in the background. **New check C7.** The §6.7 version warning stays as a backstop |
| 6 | — | SessionStart fires on `startup`, `resume`, `clear` and `compact` | The rules hook has **no matcher**, so the rules come back after `/clear` and after compaction |
| 7 | Venv in `${CLAUDE_PLUGIN_DATA}` (§6.1) | That directory survives plugin updates | Name the venv after a hash of the dependency list (`venv-<hash>`), so a release that adds a dependency gets a fresh venv |
| 8 | Bare `/plan-units` probably doesn't resolve (§5.4) | Plugin skill commands are `/<plugin>:<name>`; the prefix stays | The assessment's assumption stands |

Two repository facts the plan relies on (measured at `24092db`):

- There is **no `src/classkit/__main__.py`**, so `python -m classkit` does not work yet. Phase 1 adds
  it (`from .cli import main` / `raise SystemExit(main())`; `main()` already returns an `int`).
- **7 of the 9 test files** compute the framework root as `Path(__file__).resolve().parents[1]`.
  Phase 3 must point each at `plugin/`.

---

## Target layout

Names are **provisional** until Phase 2: plugin `classkit`, marketplace `agent-based-class`.
Neither may start with `claude-`.

```
agent-based-class-plugin/            ← developer repository = the marketplace
  .claude-plugin/marketplace.json    marketplace "agent-based-class"; one plugin, source "./plugin"
  plugin/                            ← the only thing teachers receive
    .claude-plugin/plugin.json       name "classkit", version pinned
    agents/  skills/  commands/
    hooks/hooks.json                 SessionStart: bootstrap.sh, rules.sh (no matcher)
    hooks/bootstrap.sh               ensures the Python venv, publishes it via CLAUDE_ENV_FILE
    hooks/rules.sh                   injects rules/core.md when the project has course/course.yaml
    bin/classkit                     wrapper: the venv's python -m classkit, plugin src/ on PYTHONPATH
    rules/core.md                    the always-on teacher rules, ≤ 8,000 characters
    requirements.txt                 = pyproject dependencies (a test keeps the two equal)
    schemas/  templates/  methodologies/  defaults/  src/classkit/
  dev/  tests/  pyproject.toml  CLAUDE.md  README.md   ← never shipped
```

---

## Phase 0 — Setup and baseline

**Who:** Shira, with a session. **Branch:** none (nothing is committed).

1. Clone this repository, then add the upstream:
   `git remote add framework https://github.com/BGU-CSE/class-framework`.
2. `python3 -m venv .venv && .venv/bin/pip install -e ".[dev]"`, then
   `.venv/bin/classkit mode developer`, then **restart the session** — the mode hook reads the
   marker only at session start.
3. `.venv/bin/pytest -q`. Record the count (the assessment measured 405 at `24092db`).
4. Update Claude Code to the latest version (`claude --version`). The documentation this plan
   relies on was read on 2026-10-16, and some of the features it uses are recent.
5. **Baseline from a real course.** Avin runs, in his course repo on his own machine (where the
   private files are), `classkit validate`, `classkit status` and `classkit doctor`, saves each
   output to a file outside any repository, and sends them to Shira. Check C4 compares against
   these.
6. **Agree the test course** with Avin: which course repository you both use for the trial, and
   that Shira has access to it.

**Gate 0:** tests green; the three baseline files exist; the test course is agreed.

---

## Phase 1 — The trial (go/no-go)

**Branch:** `phase-1-spike`. **Copy, do not move:** the original files stay where they are, so
nothing at the repository root changes in this phase.

**Before starting,** Shira and Avin agree the stop rules under Gate 1 below.

### Build

1. **Copy** `.claude/agents/`, `.claude/skills/`, `.claude/commands/`, `schemas/`, `templates/`,
   `methodologies/`, `defaults/` and `src/classkit/` into `plugin/`. **Do not copy**
   `.claude/hooks/report-mode.sh` or `.claude/settings.json`: the mode hook means nothing inside a
   plugin, and a plugin cannot ship permissions.
2. **Manifests.** `plugin/.claude-plugin/plugin.json`: `name`, `version: "0.1.0-spike"`,
   `description`, `author`. Root `.claude-plugin/marketplace.json`: `name`, `owner`, and one plugin
   entry with `source: "./plugin"`. The entry name and the manifest name must be the same.
3. **`__main__.py`.** Add `src/classkit/__main__.py` at the root and copy it into `plugin/`.
4. **`plugin/requirements.txt`**, the same packages as `pyproject.toml`'s `dependencies`.
5. **`plugin/hooks/bootstrap.sh`** (SessionStart):
   - Check for `python3` ≥ 3.10. If it is missing, write a clear message to stderr and exit 0 —
     never block the session.
   - `venv="$CLAUDE_PLUGIN_DATA/venv-<first 12 hex characters of sha256(requirements.txt)>"`. If
     it doesn't exist: `python3 -m venv`, then `pip install -r requirements.txt`. On failure,
     delete the partial directory.
   - If `CLAUDE_ENV_FILE` is set, append `export CLASSKIT_VENV="$venv"` to it.
   - Print **nothing** to stdout (stdout becomes context). Log to
     `$CLAUDE_PLUGIN_DATA/bootstrap.log`, including how long the install took.
6. **`plugin/bin/classkit`** (POSIX `sh`): find the plugin root from the script's own path; take the
   venv from `CLASSKIT_VENV`. If it is unset or has no python, print what is wrong and how to fix it
   (start a new session; see `bootstrap.log`) and exit non-zero. Otherwise
   `PYTHONPATH="$root/src" exec "$CLASSKIT_VENV/bin/python" -m classkit "$@"`. Running from the
   plugin's `src/` keeps `find_framework_root()`'s `__file__` fallback pointing at `plugin/`, so
   the venv holds dependencies only (assessment §6.1).
7. **`plugin/rules/core.md`** — a first condensation of the root `CLAUDE.md`'s "How to work" section
   and teacher sections, **≤ 8,000 characters**. Keep: vocabulary, ID conventions, "the teacher
   works in the chat — you run `classkit`" (bare `classkit` only), report findings faithfully, the
   teacher is the authority, the agent rules (no invented resources, never copy private text, fix
   what you caused, never approve). Put the long materials rules and command table in a reference
   skill, `plugin/skills/course-reference/SKILL.md`. The wording is reviewed with Avin in Phase 2;
   the trial only needs the real size and the mechanism.
8. **`plugin/hooks/rules.sh`**: if `$CLAUDE_PROJECT_DIR/course/course.yaml` exists, print the
   SessionStart JSON with `additionalContext` set to `core.md` (JSON-escape it with
   `python3 -c 'import json,sys; …'`). Otherwise exit 0 silently. If `core.md` is over 10,000
   characters, fail loudly on stderr rather than let it be truncated.
9. **`plugin/hooks/hooks.json`**: one `SessionStart` entry, **no matcher**, with both hooks;
   bootstrap gets `"timeout": 300`.
10. `claude plugin validate --strict ./plugin` and `claude plugin validate .` both pass.

### Measure — one section per check in `dev/reviews/plugin-spike.md`

For each check, record what was run, the result with numbers, and a verdict (pass / fail / pass
with a cost).

| Check | What to do | Passes if |
|---|---|---|
| **C1** — `classkit` as a bare command | On a machine or user account with no venv: scaffold a throwaway course, run `claude --plugin-dir <repo>/plugin` in it, and ask for `classkit status`. Then start a second session | It runs. Record the first session's install time and that the second session needs no install |
| **C2** — inside evals | A minimal eval case in `plugin/evals/`: a `scaffold_script` copies a small fixture course (generated once with `classkit scaffold`, committed in the case directory); the prompt asks Claude to run `classkit validate` and report. **Grant Bash.** Run with `--max-cost-usd 2` | `classkit` runs inside the sandbox. Record the per-run install cost and time. If the sandbox cannot read the venv, record exactly what failed |
| **C3** — the core rules reach the session | In a course repo, ask something only `core.md` answers (which words are banned; the ID format of a Guiding Question). Repeat after `/clear` and after `/compact`. Then, in a directory with no `course/`, confirm nothing was injected | Answered correctly every time; silent without `course/`. Record `core.md`'s size |
| **C4** — same results on a real course | In the agreed test course: `claude --plugin-dir <repo>/plugin`, run `classkit validate`, `status` and `doctor` through the plugin's wrapper, and diff the output against the Phase 0 baseline | Identical, or every difference explained |
| **C5** — a second person installs it | Push the branch. Avin runs `/plugin marketplace add shiraradshilo/agent-based-class-plugin#phase-1-spike`, then `/plugin install classkit@agent-based-class` | It installs with his ordinary git credentials. Record what he needed (for example `gh auth login` and `gh auth setup-git`) |
| **C6** — permissions | In the test course's `.claude/settings.json`, allow `Bash(classkit validate:*)`, `Bash(classkit status:*)` and `Bash(classkit doctor:*)` | Those commands run without a permission prompt |
| **C7** — per-course pin, no install step | In the test course's `.claude/settings.json`: `extraKnownMarketplaces` → `agent-based-class` with `source: {source: "github", repo: "shiraradshilo/agent-based-class-plugin", ref: "<branch A>"}`, and `enabledPlugins` → `"classkit@agent-based-class": true`. On a machine that has never installed the plugin, trust the folder. Then point `ref` at a branch B whose `plugin.json` version differs, and reopen | The plugin loads with **no install command**. After the `ref` changes, the B version loads. Record when: immediately, after `/reload-plugins`, or at the next session |

### Gate 1 — go/no-go with Avin

Agree these **before** Phase 1 starts. Do not build around a failure.

- **C1 or C3 fails** → stop. Either fall back to a prerequisite install (assessment §6.1, option A)
  or abandon the migration.
- **C4 shows an unexplained difference** → stop until it is explained.
- **C2 fails** → not a stop for the migration itself, but agent evals are off the table, and that
  removes the benefit in assessment §4.4. Avin decides whether the rest is still worth it.
- **C7 fails** → not a stop. The §6.7 version warning becomes the only protection, as in the
  assessment.
- **C5 or C6 problems** → fix them; they are not stops.

---

## Phases 2–10 — after a GO

These follow the assessment's §9, steps 2–10, with these changes:

- **Step 2 (specify).** Also record the separate-repository decision and what becomes of
  `BGU-CSE/class-framework` afterwards — archived, transferred, or replaced by this repository.
  Avin decides. Fix the plugin and marketplace names. The decision is **D-049**, or the next free
  number.
- **Step 3 (restructure).** Delete the spike copies, then `git mv` the originals into `plugin/` — do
  not merge copies with originals. Point the 7 tests that use `parents[1]` at `plugin/`, and point
  `pyproject.toml`'s `packages` at `plugin/src/classkit`. **Bring forward the `CLAUDE.md` swap from
  Step 6:** the root `CLAUDE.md` becomes the developer's in this same commit, because the teacher
  rules no longer live at the root, and no session here should read them as its own instructions.
- **Step 4 (runtime).** Harden the trial's hooks and wrapper, with tests. `classkit scaffold
  course` writes the course repo's `.claude/settings.json`, create-only: the allow rules,
  `enabledPlugins`, and `extraKnownMarketplaces` — with a `ref` if C7 passed. Then the methodology
  search path, the framework version recorded in `course.yaml`, and `skills:` frontmatter on the
  agents.
- **Step 5 (namespacing).** About 330 live command references in 38 files (counted at `24092db`,
  excluding `dev/_devlog/` and `dev/reviews/`).
- **Step 6 (retire the two hats).** As in the assessment, minus the `CLAUDE.md` swap done in Step 3.
- **Step 7 (tests and CI).** There is no CI today. Add a GitHub Actions workflow: `pytest` plus
  `claude plugin validate --strict`. Run the eval suite by hand with `--max-cost-usd`, not on every
  push.
- **Step 9 (migrate the real course).** Avin's call, and only after Step 8.
- **After Step 5:** the homework module comes back, written in plugin form.

---

## Status

| Phase | State | Notes |
|---|---|---|
| 0 — Setup and baseline | not started | |
| 1 — Trial (go/no-go) | not started | stop rules to agree with Avin first |
| 2 — Specify | waiting for GO | |
| 3 — Restructure | waiting for GO | |
| 4 — Runtime | waiting for GO | |
| 5 — Namespacing | waiting for GO | |
| 6 — Retire the two hats | waiting for GO | |
| 7 — Tests and CI | waiting for GO | |
| 8 — Teacher documentation | waiting for GO | |
| 9 — Migrate the real course | waiting for GO | Avin |
| 10 — Review and re-test | waiting for GO | |
