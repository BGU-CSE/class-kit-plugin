# Assessment — moving the framework to a Claude Code plugin

**Date:** 2026-10-11 · **Status:** decision input, not a decision · **Base:** `main` = `24092db`
(405 tests green) · **For:** Avin (the decision) and the developer session that would execute it.

Plugin facts below were checked against the official Claude Code documentation on 2026-10-11
(`plugins-reference`, `plugins/components`, `plugins/loading`, `plugin-evals`). Each claim is
marked **[docs]** (stated in the documentation), **[repo]** (measured in this repository), or
**[inference]** (my reasoning, to be confirmed). Repo counts were measured at `24092db`.

---

## 1. Summary and recommendation

**Recommendation: yes, migrate — but gated on a short spike, and before the `[design]`
increments start, not after.**

The plugin model fixes, structurally, three problems this project has been managing by
convention since August: how framework updates reach a teacher who has edited things (Q-007), how
a teacher's clone is kept from inheriting developer material (D-034's two-hats machinery), and how
to give teachers a clean artifact without splitting the repo (Q-031). It also unlocks the only
available way to regression-test the agents themselves (`claude plugin eval`), which today is
impossible because evals deliberately ignore project `CLAUDE.md` and `.claude/` (§4.4).

The costs are real and concentrated in two places: **the Python tooling** (`classkit`, 6,874
lines with five extraction dependencies) has no native home in a plugin, and **the always-on
teacher rules** (root `CLAUDE.md`, 252 lines) cannot ship as a `CLAUDE.md`. Both have workable
designs (§6.1, §6.2), but neither has been tried — hence the spike. There is also a reproducibility
cost with no full mitigation: a plugin version is per-user, not per-course (§5.3).

**Timing matters more than usual.** The next increments rewrite four agents and `/design-unit` and
retire `/write-items`. Migrating first means those are written once, in their final form. Migrating
after means writing them twice. Steps 0–3 are built and checked on a real course, so the cost of
migrating now is one re-test, not a redesign.

---

## 2. What changes, in one picture

**Today (D-009):** a course repo *is* a clone of the framework, with `course/` added.

```
teacher's course repo  =  clone of BGU-CSE/class-framework
  .claude/ (agents, skills, commands, hooks, settings)     ← framework
  schemas/ templates/ methodologies/ src/classkit/ dev/    ← framework
  CLAUDE.md                                                 ← framework (teacher rules)
  course/                                                   ← the teacher's
updates: git fetch framework && git merge framework/main   (conflicts if edited)
```

**Plugin model:** the framework is installed once per machine; a course repo holds only the course.

```
BGU-CSE/class-framework  (developer repo = marketplace)
  .claude-plugin/marketplace.json
  plugin/                         ← the only thing teachers receive
    .claude-plugin/plugin.json
    agents/ skills/ commands/ hooks/ bin/
    schemas/ templates/ methodologies/ defaults/ src/classkit/
  dev/ tests/ pyproject.toml CLAUDE.md   ← never shipped

teacher's course repo  =  course only
  .claude/settings.json   (enables the plugin; permissions)
  course/
updates: /plugin update  (+ /reload-plugins)   — no merge, no conflicts
```

---

## 3. What the plugin system provides — the facts this assessment rests on

| Capability | Fact | Source |
|---|---|---|
| Components | `agents/`, `skills/`, `commands/` (older format, still supported), `hooks/hooks.json`, `.mcp.json`, `bin/`, `settings.json`, output styles | [docs] |
| Namespacing | Every component is namespaced by plugin name: command `/<plugin>:<name>`, agent `<plugin>:<name>`, skill `<plugin>:<name>` | [docs] |
| Executables | Files in `bin/` are on the Bash tool's `PATH` while the plugin is enabled, *after* the user's own entries | [docs] |
| Paths | `${CLAUDE_PLUGIN_ROOT}` (changes every version) and `${CLAUDE_PLUGIN_DATA}` (`~/.claude/plugins/data/<id>/`, kept across updates) | [docs] |
| Path variables in Bash | **Not** present in the Bash tool's environment; substituted inline in skill/command/agent Markdown, exported to hooks | [docs] |
| `CLAUDE.md` | A `CLAUDE.md` at the plugin root **is not loaded**; "to include instructions … put them in a skill"; "if a rule must hold every time … add it as a hook" | [docs] |
| Settings | Plugin `settings.json` honours only `agent` and `subagentStatusLine`; **no permissions** | [docs] |
| `agent` setting | Runs the session's main thread *as* a plugin agent — its prompt, tool restrictions and model apply to the whole session | [docs] |
| Agent frontmatter | Supported: `tools`, `disallowedTools`, `skills` (preload), `model`, `memory`, `omitClaudeMd`, `isolation`… Ignored: `permissionMode`, `hooks`, `mcpServers`, `initialPrompt` | [docs] |
| Dependencies | Node packages auto-installed from a lockfile. **Python is not**: the docs direct Python dependencies to be installed "from a hook into the persistent data directory" | [docs] |
| Versions | `version` in `plugin.json` pins users until it changes; unset, the version is the commit SHA | [docs] |
| Updates | Auto-update is **off by default** for third-party marketplaces; a running session keeps its version until `/reload-plugins` | [docs] |
| Per-project enabling | `enabledPlugins` can be set in a repo's `.claude/settings.json`; it is a boolean — **no per-project version pin** | [docs] |
| Not installed here | A plugin enabled only in project settings is not fetched automatically; the user sees "enabled in project settings but isn't installed here" | [docs] |
| Local development | `--plugin-dir` loads a plugin in place; edits apply on `/reload-plugins`; a `--plugin-dir` copy **overrides** an installed plugin of the same name | [docs] |
| Validation | `claude plugin validate [--strict]` checks manifest, paths, MCP config | [docs] |
| Evals | `claude plugin eval`: cases (prompt + graders: regex, `tool_used`, `file_exists`, LLM judge), 3 runs each, with/without-plugin baseline, sandboxed, CI-gated, real model cost. **Runs load nothing personal or project-level — no `.claude/`, no `CLAUDE.md`** | [docs] |
| Other surfaces | claude.ai and Cowork don't install a plugin with a top-level `bin/` | [docs] |

---

## 4. Pros

### 4.1 Framework updates stop being merges — Q-007 dissolves into a smaller question

Today a teacher who edits a framework file gets a merge conflict on every update, and the interim
rule ("want updates? don't edit framework files") has stood since August because nobody found a
better mechanism. In the plugin model the teacher's repo contains no framework files, so there is
nothing to conflict. Q-007 becomes "how does a teacher *override* a plugin agent?" — a design
question with clean answers (§6.5), not a git-hygiene problem every teacher inherits.

### 4.2 The two-hats machinery becomes unnecessary — D-034's problem is solved structurally

`classkit mode`, the gitignored `dev/.developer` marker, the `report-mode.sh` SessionStart hook,
the check that `.gitignore` itself is tracked, and the split between root and `dev/CLAUDE.md` all
exist to stop a teacher's clone from behaving like a developer checkout [repo: `mode.py`,
`test_mode.py`, `report-mode.sh`]. With a plugin, a teacher never has the developer repo at all,
and the plugin directory carries no developer material. That is a whole mechanism deleted, not
maintained.

### 4.3 Q-031 is resolved in a better form than it was posed

Q-031 proposed two repositories and was rejected because it "destroys spec↔code atomicity". A
plugin in a subdirectory of the developer repo gives teachers exactly the clean artifact Q-031
wanted, while spec, ledger and code stay in one repo and one commit. The atomicity rules
(`FRAMEWORK-SPEC` and the ledger updated in the same commit) survive intact.

### 4.4 The agents become testable — and only in plugin form

The project's own premise is that "agents are the point", yet the agent layer has no regression
test: every prompt change is checked by Avin running the real course by hand. `claude plugin eval`
runs a prompt against the plugin in a fresh sandbox, grades the result (did the
`planning-units` skill load? does `unit.md` exist? does a judge model accept the objectives
against a rubric?), compares with and without the plugin, and can gate CI with a cost ceiling
[docs].

**The decisive detail:** eval runs deliberately load no project `CLAUDE.md` and no `.claude/`
[docs]. The current framework *is* project `CLAUDE.md` plus `.claude/`, so it cannot be evaluated
this way at all. Moving to a plugin is the precondition for agent regression testing — and it
also forces the teacher rules into the plugin (§6.2), which is where they belong anyway.

### 4.5 Developing against a real course without mixing trees

Today, testing a framework change on Avin's real course means merging framework commits into the
course repo or keeping parallel clones. With `--plugin-dir`, the developer's working copy loads in
place into *any* course repo and overrides the installed release for that session only [docs].
The real course stays on the released version; the dev version is tried against it with no git
operations. This is the most direct way to "ease development and testing".

### 4.6 Teacher onboarding without git surgery

Today: clone, rename a remote, create a private repo, add an origin, push, create a venv,
`pip install -e .`, scaffold. Plugin: add the marketplace, install the plugin, create an empty
private repo, ask the chat to set up the course. Git is still needed for the course repo itself,
but the remote-juggling that D-009 requires disappears.

### 4.7 Smaller wins

- **Skills preloaded deterministically.** Plugin agents support a `skills:` frontmatter field
  [docs]. The eleven "load the X skill first" instructions in prompts [repo] become declarations
  the runtime enforces, rather than instructions an agent may skip.
- **Invariant 1 becomes structural.** The plugin directory cannot contain a course; there is no
  `course/` to keep out.
- **Updates are deliberate.** Auto-update is off by default for this kind of marketplace [docs], so
  a teacher is not changed under mid-semester — a good default for teaching.
- **`claude plugin validate --strict`** gives CI a free structural check of every agent, skill and
  command file.

---

## 5. Cons and costs

### 5.1 The Python tooling has no native home — the largest technical risk

`classkit` is 6,874 lines with PyYAML, jsonschema, python-pptx, python-docx, pypdf and fonttools
[repo]. Plugins install Node dependencies automatically; for Python the documentation says to
install "from a hook into the persistent data directory" [docs]. That is workable (§6.1), but it is
custom bootstrap code the project must own, with failure modes the current `pip install -e .` does
not have: first-run install time, network on first use, Windows paths, and behaviour inside the
eval sandbox. **Nothing in this assessment proves it works; the spike must.**

### 5.2 The teacher rules lose their natural home

The root `CLAUDE.md` (252 lines, 16 KB [repo]) carries the vocabulary, the materials rules, "report
every finding", "agents never approve", the private-material rule. A plugin cannot ship a
`CLAUDE.md` [docs]. The alternatives (§6.2) each have a cost; the one that avoids reintroducing the
update problem — a SessionStart hook — is also the least tried.

### 5.3 Reproducibility across a teaching team gets weaker

Today a course repo pins its framework by git commit: everyone who clones the course gets the same
framework. A plugin version is per *user*, and project settings can enable a plugin but not pin its
version [docs]. A teacher on 0.6 and a TA on 0.5 can edit the same course; if a schema or rule
differs, `classkit validate` gives them different answers — breaking the property that validate
gives "the same answer on every clone". **Mitigation (§6.7) is a warning, not a guarantee.** This
is the cost I would weigh most heavily for a joint project.

### 5.4 Every command and cross-reference gets a namespace

Commands become `/<plugin>:ingest`, agents `<plugin>:curriculum-architect`, skills
`<plugin>:planning-units` [docs]. There are **514 live slash-command references in 35 files**
[repo], plus 11 agent and 11 skill references inside prompts. A short plugin name limits the
friction (`/flip:plan-units` rather than `/class-framework:plan-units`). Whether a bare `/plan-units`
resolves when unambiguous is **not stated in the docs** — assume it does not.

### 5.5 Teachers lose "edit freely"

D-014 lets a teacher edit any framework file in their own repo. Plugin files live in a versioned
cache and are replaced on update; editing them is pointless. Customization must go through a
designed mechanism (course-local agents and skills, or an override table — §6.5). This is arguably
a gain in discipline, but it removes a freedom D-014 deliberately granted.

### 5.6 Migration cost and delay

A restructure of every framework path, a namespacing pass, new bootstrap code, removal of the mode
machinery, rewritten teacher docs and `MANUAL-TESTING.md`, a migration of Avin's existing course
repo, and **a re-test of steps 0–3 on the real course**. My estimate — judgement, not measurement —
is one spike session, one specification session, three to four build sessions, then the usual
review and Avin's check. The `[design]` increments wait for it.

### 5.7 Two smaller costs

- **Reach beyond Claude Code.** claude.ai and Cowork refuse plugins with a top-level `bin/` [docs].
  If teachers ever work in Cowork rather than Claude Code — plausible, given D-045 "the teacher
  works in the chat" — the `bin/` choice would have to be revisited.
- **Outstanding branches.** Any branch built in the current layout (the homework branch among them —
  noted as a cost only, per Avin's instruction not to address it here) will conflict with a
  restructure that moves every framework path.

---

## 6. The design problems the migration must solve

### 6.1 Running `classkit` (and its dependencies)

| Option | How | For | Against |
|---|---|---|---|
| **A. Prerequisite install** | Teacher runs `pipx install` (PyPI or git URL); prompts call `classkit` | Standard; nothing custom | Two installs; **plugin and `classkit` versions can drift apart** — prompts written for one, tooling from another |
| **B. Self-bootstrapping (recommended)** | Plugin vendors `src/classkit/`; `bin/classkit` is a small wrapper; a SessionStart hook ensures a venv of the pinned dependencies in `${CLAUDE_PLUGIN_DATA}`; the wrapper runs `python -m classkit` with the plugin's `src/` on `PYTHONPATH` | One install; **prompts and tooling always the same version** | Custom bootstrap; first-run delay; needs Python ≥3.10 (as today); network on first run |
| C. MCP server | `classkit` exposed as MCP tools | Structured tools; read-only agents could validate without Bash | Rewrite of 105 `classkit` invocations in prompts [repo]; new runtime; biggest change |

**Recommend B.** Lock-step versions are the property that matters: the same reasoning that made
Q-031's atomicity non-negotiable applies to prompts and tooling. Two details the spike must settle:

- The wrapper cannot read `${CLAUDE_PLUGIN_DATA}` — plugin variables are absent from the Bash tool's
  environment [docs]. It can find its own plugin root from its own path; the venv location must be
  either derived deterministically or published by the SessionStart hook (which does receive the
  variable). One candidate is the hook writing to `CLAUDE_ENV_FILE` — **[inference] — verify it
  exists and behaves as expected.**
- `find_framework_root()` already falls back to `Path(__file__).parents[2]` [repo]. If `classkit`
  runs from the plugin's `src/` (not installed into site-packages), that fallback finds the
  plugin's `schemas/` and `methodologies/` **unchanged** — so the venv should hold dependencies only,
  not `classkit` itself. Moving to `importlib.resources` is cleaner but not required.

### 6.2 The always-on teacher rules

| Option | Verdict |
|---|---|
| Scaffold writes `course/CLAUDE.md` | **Reject.** Teacher-owned, never updated by the plugin — reintroduces exactly the update problem the migration removes |
| Plugin `settings.json` `agent` → main thread runs as a `teacher` agent | Possible [docs], but it applies to *every* session wherever the plugin is enabled, imposes that agent's tool restrictions on the whole session, and its interaction with the base system prompt is unstated. Too blunt |
| A skill | Loaded on demand by description — **not guaranteed** to be in context. Right for long reference material, wrong for rules that must always hold |
| **SessionStart hook (recommended)** | The docs' own guidance for must-hold rules [docs]. The hook can check for `course/` in the project and stay silent otherwise — preserving "a `course/` directory is positive confirmation". Size limits on injected context are **[unverified]** |

**Recommend a split:** a SessionStart hook injecting the *core* rules (vocabulary, ID conventions,
"report every finding", the teacher is the authority, never copy private text) when `course/`
exists; a reference skill for the long materials and approval sections; and the teacher's own
`CLAUDE.md` left entirely to them for personal notes. This also makes the rules visible to evals,
which a project `CLAUDE.md` is not.

### 6.3 Permissions

A plugin cannot ship permission rules [docs]. D-045's pre-allowed read-only commands therefore
move to the **course repo's** `.claude/settings.json`, written by `classkit scaffold course` (create-
only, like everything scaffold writes), together with `enabledPlugins` and
`extraKnownMarketplaces`. With `classkit` on `PATH` via `bin/`, the allow rules simplify to bare
`classkit validate:*` and the duplicated `.venv/bin/classkit` forms go away [repo]. Commands can
additionally declare `allowed-tools` in their own frontmatter.

### 6.4 Framework assets inside the plugin

Schemas, templates, methodologies and defaults move into `plugin/`. Covered by §6.1's
`__file__` fallback provided the relative layout (`src/classkit/` beside `schemas/`) is preserved.

### 6.5 Teacher customization (what Q-007 becomes)

- **New** agents and skills: the teacher adds them to the course repo's `.claude/` — they load
  un-namespaced and coexist with the plugin's.
- **Replacing** a plugin agent: needs the `agents:` override in `course.yaml` (already in the
  schema since August [repo]) to be honoured by the commands that dispatch agents.
- **A teacher's own methodology** cannot live in the plugin (it would be erased on update):
  `classkit` needs a search path — `course/methodologies/` first, then the plugin's. Small code and
  spec change; required to keep D-011 true.

### 6.6 Namespacing

Choose the plugin name first; it fixes every reference. Short and distinctive (e.g. `flip`); the
validator rejects names starting `claude-` and warns on `claude` as a word [docs]. Rewrite live
references only — `dev/_devlog/` history stays as written (the D-024 precedent).

### 6.7 Version compatibility

- Pin `version` in `plugin.json` and release deliberately; unpinned, every commit is an update
  [docs].
- Record the framework version in the course (`course.yaml`, written by scaffold and refreshed by
  `approve`); `classkit validate` and `doctor` warn when the running plugin is older than the one
  that last wrote the course, or a major version newer.
- A changelog with migration notes per release. None of this restores the per-commit guarantee of
  §5.3; it makes skew visible.

### 6.8 What ships

The plugin goes in a subdirectory. If the plugin root were the repo root, `dev/` (780 KB, including
14 review documents, one of them the report of Avin's real-course test [repo]) would be copied into
every teacher's plugin cache, and the developer `CLAUDE.md` would sit at the plugin root.

### 6.9 Evals have constraints of their own

Runs start in an empty workspace with a temporary `HOME`; fixtures come from a scaffold script; Bash
runs in an OS sandbox with network limited to granted domains; hooks run outside the sandbox
[docs]. So the §6.1 bootstrap must work with a fresh `HOME`, or every eval run reinstalls the
dependencies — **a spike check, not an assumption.** Evals cost real model calls; cap them with
`--max-cost-usd`.

---

## 7. Effect on recorded decisions and open questions

| Item | Effect |
|---|---|
| D-009 clone-and-repoint | **Retired** — replaced by marketplace install |
| D-014 governance | Framework side unchanged; course side still sovereign, but now holds only the course; "edit freely" becomes an override mechanism (§5.5) |
| D-015 no `course/` in the framework | Unchanged, and structural |
| D-034 two hats, `classkit mode` | **Retired** — the problem no longer exists (§4.2) |
| D-045 read-only commands pre-allowed | Moves to the course repo's settings, written by scaffold (§6.3) |
| Invariant 1 | Structural |
| Invariant 5 (writes through `classkit write`) | Unchanged — depends on §6.1 working |
| Invariant 6 (templates validate) | Unchanged |
| Q-007 | Reframed as an override question (§6.5) |
| Q-021 scaffold as Python | Unaffected |
| Q-022 who owns course repos | Unaffected |
| Q-031 two repositories at release | **Resolved** by a subdirectory plugin (§4.3) |
| "Validate gives the same answer on every clone" | **Weakened** to "on every clone with the same plugin version" (§5.3) |

---

## 8. Go/no-go — what the spike must show

A throwaway branch with a minimal plugin wrapping the current files. Proceed only if all of these
hold; record the measurements in `dev/reviews/plugin-spike.md`.

1. **`classkit` runs as a bare command** from the plugin on a clean macOS user account with no
   prior venv. First-run time recorded; second session instant.
2. **It runs inside `claude plugin eval`** with a temporary `HOME` — or there is a documented,
   acceptable cost (reinstall per run) — so agent evals can call it.
3. **The SessionStart hook's injected rules reach the session** at the full current size, and the
   hook stays silent in a directory without `course/`.
4. **Avin's existing real course works** with `--plugin-dir`, `course/` layout unchanged:
   `classkit validate`, `status` and `doctor` give the same findings as the saved baseline.
5. **Install from the private GitHub marketplace** works on a second machine with ordinary git
   credentials.
6. **Bare `classkit …` allow rules** in the course repo's settings suppress the permission prompt.

If 1 or 3 fails, fall back to option A (prerequisite install) or reconsider the whole move; do not
build around a failure.

---

## 9. The migration process, step by step

Each step follows the project's existing discipline: decision before code, spec and ledger updated
in the same commit, a fresh developer session per build step with a gap report, an independent
review, then Avin's check. Nothing reaches `main` until step 4.

### Step 0 — Freeze and baseline (Avin, one short session)

1. Decide to explore. Pause the `[design]` increments until go/no-go.
2. Tag the current state: `git tag pre-plugin 24092db` (or the then-current head) and push the tag.
3. On the real course, save baseline outputs to compare against later:
   `classkit validate > baseline-validate.txt`, likewise `status` and `doctor`. Keep them outside
   the framework repo.

### Step 1 — Spike (developer session, branch `spike/plugin`, never merged)

1. Create `plugin/.claude-plugin/plugin.json` (`name`, pinned `version: 0.1.0-spike`) and a root
   `.claude-plugin/marketplace.json` with a relative source `./plugin`.
2. Copy — do not move — `.claude/agents|skills|commands`, `schemas/`, `templates/`,
   `methodologies/`, `defaults/`, `src/classkit/` into `plugin/`.
3. Add `plugin/bin/classkit` (wrapper) and a `plugin/hooks/hooks.json` SessionStart hook that
   (a) ensures the dependency venv and (b) injects the core teacher rules when `course/` exists.
4. Run `claude plugin validate --strict ./plugin`.
5. Run the six checks of §8. Write `dev/reviews/plugin-spike.md` with the measured results.
6. **Go/no-go with Avin.** On no-go: delete the branch; record the outcome as a decision anyway.

### Step 2 — Specify (developer session with Avin; design only, on `main`)

1. Write **D-049 — the framework ships as a Claude Code plugin**: what it retires (D-009, D-034),
   amends (D-014, D-045) and resolves (Q-031); the §6 choices as decided; the §5.3 cost accepted
   explicitly.
2. Update `FRAMEWORK-SPEC.md`: the architecture section (distribution, layout, runtime), §8.6
   (where `classkit` runs), a new normative section for the plugin layout, the namespaced names,
   the version-compatibility rule, the methodology search path.
3. Add ledger rows tagged **[plugin]** in `ROADMAP.md` — one per artifact change below.
4. Annotate Q-007, Q-031 and any other affected open question **in the same commit**.
5. Choose and record the plugin name.

### Step 3 — Restructure (one mechanical commit; no behaviour change)

1. `git mv` the framework assets into `plugin/` (agents, skills, commands, hooks, schemas,
   templates, methodologies, defaults, `src/classkit/`).
2. Point `pyproject.toml` at the new package path; keep `tests/` at the repo root.
3. Add `plugin.json` (pinned `version`) and `marketplace.json`.
4. Full suite green; `claude plugin validate --strict ./plugin` clean.

### Step 4 — Runtime (build session, gap report)

1. `bin/classkit` and the bootstrap hook (§6.1).
2. The core-rules SessionStart hook and the reference skill (§6.2); trim the root teacher
   `CLAUDE.md` content out of the repo once both exist.
3. `classkit scaffold course` writes the course repo's `.claude/settings.json`: allow rules,
   `enabledPlugins`, `extraKnownMarketplaces` (§6.3) — create-only.
4. Methodology search path (§6.5) and the framework version recorded in `course.yaml` with the
   validate/doctor warning (§6.7).
5. Replace the "load the X skill first" prose with `skills:` frontmatter on each agent.
6. Tests for each, at its severity, per `dev/CLAUDE.md`.

### Step 5 — Namespacing pass (build session)

1. Rewrite live references to commands, agents and skills in `plugin/`, root docs,
   `GETTING-STARTED.md`, `MANUAL-TESTING.md` and the spec. Leave `dev/_devlog/` and `dev/reviews/`
   as written.
2. Check none remain — a grep for the bare forms (`/ingest`, `/plan-units`, …) outside
   `dev/_devlog/` and `dev/reviews/` should return only deliberate mentions.

### Step 6 — Retire the two-hats machinery (build session)

Remove `classkit mode`, `mode.py`, `test_mode.py`, `report-mode.sh`, the `dev/.developer` marker
and its `.gitignore` checks; make the repo-root `CLAUDE.md` the developer's (it is never shipped);
update the spec and the ledger.

### Step 7 — Tests and CI

1. pytest green; `claude plugin validate --strict` in CI.
2. A first eval suite — a handful of cases, not coverage: `/ingest` pre-flight on a tiny synthetic
   fixture (`file_exists`, `tool_used`), `/plan-units` on a fixture course (`tool_used: Skill`
   for `planning-units`, an LLM-judged rubric for the objectives). Run with `--max-cost-usd`.

### Step 8 — Teacher documentation

Rewrite `GETTING-STARTED.md` for the plugin flow (install, empty private course repo, set up), and
write a one-page migration note for course repos created by cloning.

### Step 9 — Migrate the real course (Avin, with the chat)

1. In the existing course repo, on a branch: remove every framework file, keeping `course/` and its
   history (`git rm -r` everything else).
2. Write `.claude/settings.json` (scaffold's version) and enable the plugin at project scope.
3. Run `classkit validate`, `status`, `doctor`; compare with the step 0 baseline. Differences must be
   explained or fixed before merging.

### Step 10 — Review and re-test

Gap report, one independent review of steps 3–8, then Avin re-runs `MANUAL-TESTING.md` steps 0–3 on
the real course. Then the `[design]` increments resume — written in plugin form from the start.

---

## 10. What I am least sure of

- That the Python bootstrap is robust across machines and inside evals (§6.1, §6.9) — the spike
  exists for this.
- That a 16 KB SessionStart injection is acceptable in size and in effect (§6.2) — unverified.
- The behaviour of a private-repo marketplace for a second user (§8, check 5) — not covered by the
  pages I read.
- My effort estimate in §5.6 — a judgement from the size of the change, not from comparable work.
