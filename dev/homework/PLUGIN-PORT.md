# Bringing homework into the plugin

Homework was designed in the class-framework repository (branch `homework-by-shira`, forked from its
`main` at `24092db`), before Class Kit became a plugin (D-049). It came into this repository in two
steps:

1. **Staged** (`homework/bring-in`): the documents unchanged, the module's own files at their old
   paths, its changes to framework files as a patch — nothing in `plugin/`.
2. **Ported** (`homework/port`): the files moved into `plugin/` in plugin form, the Python built, the
   tests written, the staged copies removed (they stay in the history of `homework/bring-in`).

What was decided for the port is **HW-D35** (`_devlog/01-decisions.md`); what homework now is,
`HOMEWORK-SPEC.md`; what exists, `ROADMAP.md`'s ledger.

## The workflow

**`/class-kit:plan-homework U03 U04 [purpose]`** — status → `classkit scaffold homework` (the file,
and the configuration the first time) → the interview, in the chat → the planner's draft and brief →
revised with the teacher → written, validated, logged → **Gate 1:** `classkit approve homework N
--stage planned`.

**`/class-kit:build-homework N`** — status → reused items (consent to add `homework` to their usage)
→ the writer, one slot at a time → the critic → the solver → the item list written into the homework
file → validated, logged → **Gate 2:** `classkit approve homework N --stage built` → the defaults
updated → the report. The Word or PDF documents: whenever the teacher asks.

**`/class-kit:new-item-class <name>`** — an item class through a short interview, and, if it needs
one, a writing guide as a course file.

## Matching to the plugin — what was done

| The module had | The plugin has |
|---|---|
| `/create-homework` (one run, two gates) | `/class-kit:plan-homework` and `/class-kit:build-homework` |
| `/new-hw-type` | `/class-kit:new-item-class` |
| the `interviewer` agent | the interview in the commands, with the `interviewing-teachers` skill |
| `.plans/HW0N.md` and `status: draft` | the `plan` in `HW0N.md`, and its `approved` record |
| documents as step 12 | the `making-homework-documents` skill, when the teacher asks |
| `custom_skill`, writing skills in the course | `writing_guide` / `custom_guide`: course files the agents read |
| the planner writing its plan | the planner returning it; the chat revising and writing (D-044), to the new `planning-homework` skill |
| `classkit bank` | deferred |
| paths relative to the repository, short names | `${CLAUDE_PLUGIN_ROOT}`, `/class-kit:…`, `class-kit:…`, skills in the agents' frontmatter |

## What is left

- **The first real homework** — plan and build one on a real course; the agents have never run.
- **The teacher documentation** — `README.md` and `GETTING-STARTED.md` gain the homework commands
  once the teacher-documentation branch (Phase 8) is merged, to avoid editing them twice.
- **Open:** HW-Q01, HW-Q04, HW-Q05 (a sandbox for running code), HW-Q06 (where a teacher aid is
  kept), HW-Q07; the rubric wording when framework D-038 G-19 lands; material fit once the answer
  locators (D-019) exist.
- **Deferred:** `classkit bank`, item-bank ingest (HW-Q02), bank growth (HW-Q08),
  `assessment_scheme_complete` (waits for the syllabus's `assessment` block).
