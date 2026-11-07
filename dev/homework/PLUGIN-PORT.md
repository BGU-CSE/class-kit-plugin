# Bringing the homework module into the plugin

The homework module was designed in the class-framework repository (branch `homework-by-shira`,
forked from its `main` at `24092db`), before the plugin restructure (D-049). This folder brings it
into this repository **as it was**, so that nothing of it is lost; it is not yet part of the plugin.

- **The documents** — `README.md`, `HOMEWORK-SPEC.md`, `ROADMAP.md`, `_devlog/` — are copied
  unchanged. Their paths (`.claude/agents/…`, `schemas/…`, `src/classkit/…`) are the old
  repository's; in this one they are under `plugin/`.
- **The module's own files** — 5 agents, 3 commands, 3 skills, 4 new schemas, 8 new templates, and
  full copies of the 5 framework files it changed — are in `framework-files/`, at their old paths.
  They are kept **outside `plugin/` on purpose**: nothing half-adapted reaches a teacher, and the
  plugin's tests (full names, preloaded skills, `${CLAUDE_PLUGIN_ROOT}` paths) do not run on files
  that were written before those rules existed.
- **`framework-changes.patch`** — what the module changed in 14 framework files, against `24092db`.
  The schema and template changes apply as they are: the plugin's copies of
  `assessment-item.schema.json`, `course.schema.json`, `item-open.md` and `item-multiple-choice.md`
  have not changed since. `write-items.md` and the root documents have, so those changes are made
  again by hand. The patch's one change to `scaffold.py` (a Windows path) is already in the plugin.

## The workflow (as designed)

**`/create-homework [units] [purpose]`** — plan first, the teacher approves, then write (HW-D15):

1. **Ground** — read the course, the units, the item bank, and `item-classes.yaml`,
   `homework-defaults.yaml` and `homework-document.yaml` (each created from its template the
   first time).
2. **Interview** — one round: the full draft spec, and only the questions the teacher knows better.
3. **Follow-ups** — what the interview turned up that needs another action (a tool to declare in
   `course.yaml`, say), each with the teacher's consent.
4. **Plan** — `homework-planner`: the coverage skeleton, the item slots, reuse or adapt or new.
5. **Gate 1** — the teacher approves the plan. Logged.
6. **Write** — `homework-item-writer`, one item per slot, `status: draft`.
7. **Critique** — `item-critic` on each item; writer and critic loop.
8. **Solve** — `item-solver` attempts each item by its class's strategy: persona attempt, run the
   code, skip, or custom.
9. **Manifest** — `course/assessments/homework/HW0N.md`.
10. **Validate** — `classkit validate`.
11. **Gate 2** — the teacher approves the result: items go from `draft` to `shipped`. Logged.
12. **Documents** — the student and the teacher Word documents, with a leak check (HW-D23).
13. **Defaults** — update `homework-defaults.yaml` from what was accepted.
14. **Report.**

**`/new-hw-type <name>`** adds an item class through the same interview, and a writing skill for it
when the class needs one. **`/write-items N homework`** hands off to `/create-homework`.

## Decided for the port (2026-11-07)

These change the design above. They become recorded decisions when the port is a phase of its own.

1. **Two commands, as for units** (instead of HW-D15's one command with two gates):
   - **`/plan-homework [units] [purpose]`** — steps 1–5. It writes the plan into
     `course/assessments/homework/HW0N.md`. Gate 1 is `classkit approve homework N --stage planned`.
   - **`/build-homework N`** — steps 6–8 and 13: the items into the bank, their list into
     `HW0N.md`, then `classkit validate`. Gate 2 is `classkit approve homework N --stage built`; its
     hash covers the file and its items, so `classkit status` can say "built — edited since".
2. **How a homework is kept** — as a unit is: one file per homework, `HW0N.md`, holding the plan
   and then the list of its items, with the approval written into it. The items stay in the shared
   bank, `course/assessments/items/`, as the entry quiz's do. No `.plans/` folder (changes HW-D01),
   and no `status: draft` field: the state comes from the approval record (answers HW-Q03). This
   needs `classkit approve homework`, a homework line in `classkit status`, and in the schema an
   `approved` record and `items` allowed empty until the build.
3. **The Word or PDF documents are made when the teacher asks**, after the build, from the
   approved files — no longer a step of the build (changes HW-D23). Where they are saved stays as
   HW-D24 says.
4. **No item-bank work for now**: `classkit bank` (HW-D22) and the bank's questions (HW-Q02,
   HW-Q08) wait.

## Done and remaining

The module's ledger (`ROADMAP.md`) is authoritative: **72 rows done, 46 open.**

- ✅ **H0, the content** — the agents, commands, skills, schemas and templates; 34 decisions
  (HW-D01…D34); the specification.
- ⬜ **H1, loading** — `model.py` loads homework manifests and the three configuration files.
- ⬜ **H2–H4, the 21 validator rules** — manifest, class, tool, defaults, graded and completeness.
- ⬜ **H5, scaffold and CLI** — `classkit scaffold homework`, `scaffold item --class`, `classkit bank`.
- ⬜ **H6, integration tests**; ⬜ **H7, the documents** switched to "implemented".
- ⬜ **The first real homework** — no homework agent has run yet; the pipeline itself is tested only
  there.
- ⬜ **Open:** 8 questions (HW-Q01…Q08), and the design of the document generator (HW-D20).

## Matching it to the plugin

What the port has to change. None of it is done.

1. **Move** the files into `plugin/agents`, `commands`, `skills`, `schemas` and `templates`.
2. **The plugin's own files** are named through `${CLAUDE_PLUGIN_ROOT}` (invariant 7) — the
   commands and agents name `schemas/…` and `templates/…` as if they were in the course.
3. **Full names**: `/class-kit:<command>` and `class-kit:<agent>` (D-050).
4. **Skills in the frontmatter**: every skill an agent names goes in its `skills:` list, as
   `class-kit:<skill>` (finding 19). All five agents name skills; none declares them.
5. **The interview moves into the command.** The `interviewer` agent cannot work as written: it is
   told to ask the teacher and wait for the answer, and an agent cannot talk to the teacher (D-044).
   The commands interview in the chat with the `interviewing-teachers` skill; the agent goes. This
   reverses HW-D04, so it needs a decision.
6. **The changes to shared files**:
   - `assessment-item.schema.json`: the homework fields, and `answer` → `model_answer`, which is
     also the framework's step 5 (D-031g). Whichever lands first does it; the code that reads
     `answer` changes with it.
   - `course.schema.json`: the course's `tools`.
   - `write-items.md`: the hand-off to homework.
   - two item templates.
   - the cross-references in `CLAUDE.md`, `README.md`, `GETTING-STARTED.md`, `FRAMEWORK-SPEC.md`,
     `ROADMAP.md` and the decisions, re-made in today's versions.
7. **Writing**: the writer and the planner write through `classkit write` (HW-D12, invariant 5);
   the commands log through `classkit log`.
8. **A course's own writing skill** — `/new-hw-type` creates one in the course. How a plugin finds
   a teacher's own skills is Phase 11 of the migration, so this part waits for it.
9. **The Word or PDF documents**, made on request, need a library the plugin's environment does not
   install today.
10. **H1–H7** are then built in `plugin/src/classkit` and `tests/`, as the module's plan says.

**Dependencies.** Real homework needs built units (framework steps 4–6) and the answer locators
(D-019, step 4). The `model_answer` rename is shared with step 5.

## The names

Matching `plan-X`, `build-X`, `review-X` is **not required**: nothing checks it, and `new-course`,
`ingest` and `write-items` already stand outside it. The recommendation is to match it where a
command is one of those three:

| Now | Proposed | Why |
|---|---|---|
| `/create-homework` | `/plan-homework` and `/build-homework` — **decided** | As `/plan-units` and `/build-unit`. |
| `/new-hw-type` | `/new-item-class` | A setup command, like `/new-course`; the specification calls them item classes. |
| `/write-items N homework` | hands off to `/plan-homework` | Unchanged otherwise. |

- **No `/review-homework`.** HW-D17 removed it: the critic and the solver run inside the build. A
  teacher who knows `/review-unit` may look for it; re-reviewing an old homework is HW-Q07.
