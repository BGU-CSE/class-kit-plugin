# Homework specification

What homework in Class Kit must contain, and the exact fields, rules, agents, commands and
identifiers it is made of. Homework was designed as a separate module of the class-framework
repository and brought into the plugin in its own form (HW-D35, `PLUGIN-PORT.md`); this document
describes the plugin form.

**Why homework exists and what it is for is in [`README.md`](README.md).** This document assumes
that and specifies the *what*. It is written to be **self-contained**: an agent with no memory of
the design conversations should be able to implement or verify homework from this file alone.
Rationale is stated in a sentence or two and tagged `HW-Dnn` — breadcrumbs into
`_devlog/01-decisions.md`, which holds the history. **[`ROADMAP.md`](ROADMAP.md)'s ledger is
authoritative for what exists.**

---

## 1. Scope

### 1.1 What a homework is

A homework is a set of Assessment Items students do at home after the units it covers. It is a
**first-class content type** (HW-D01): its own schema, its own place on disk, its own settings — and,
like a unit, **one file** that holds its plan, the items it was built from and the teacher's
approval (HW-D35). It references items in the shared item bank; it never copies them.

### 1.2 What it covers

- The homework file — schema, place, states — and the approval of a homework
- The item-class taxonomy (a third axis on items)
- Two commands, `/class-kit:plan-homework` and `/class-kit:build-homework`, and the setup command
  `/class-kit:new-item-class`; the hand-off from `/class-kit:write-items N homework`
- The Word and PDF documents, made when the teacher asks (a skill, not a command)
- 21 validator rules
- Templates for the new files

### 1.3 What it does not cover

- Programming assignments as a separate content type — they are homework items with
  `item_class: Coding` (HW-D01, Q-026)
- Exam confidentiality — still open (Q-002)
- An item-bank overview (`classkit bank`, HW-D22) and item-bank ingest (HW-Q02) — deferred (HW-D35)
- A sandbox for running code (HW-Q05)

---

## 2. Architecture

### 2.1 The three axes of an item

| Axis | What it answers | Values | Extensible? |
|---|---|---|---|
| `format` | What shape is the student's answer? | `multiple-choice`, `multiple-select`, `true-false`, `open`, `numeric`, `code` | HW-Q01 (proposed) |
| `usage` | Where may this item be used? | `in-class-quiz`, `homework`, `exam`, `self-check`, `gem-practice` | No (fixed enum) |
| `item_class` | What kind of homework item? | Defined by each course | Yes — `/class-kit:new-item-class` (HW-D02) |

The axes are independent: `format: open, item_class: Practicing, usage: [homework]` is legal, and so
is `format: multiple-choice, item_class: DIY, usage: [in-class-quiz, homework]`. Reuse across
contexts is by more values in `usage`, never by duplicating the file.

### 2.2 Content model

```
course/
├── course.yaml                    # gains a `tools` map (HW-D03)
└── assessments/
    ├── items/*.md                 # the shared item bank (HW-D21)
    ├── homework/
    │   ├── HW01.md                # one homework: settings, plan, items, approval (HW-D01, HW-D35)
    │   └── HW02.md
    ├── item-classes.yaml          # the item classes (HW-D02)           } created by
    ├── homework-defaults.yaml     # the teacher's usual choices (HW-D16) } `classkit scaffold
    ├── homework-document.yaml     # how the documents look (HW-D30)      } homework` (HW-D13)
    └── writing-guides/*.md        # a course's own guides for a class (HW-D35), optional
```

### 2.3 Components (all in `plugin/`)

- **Commands (3):** `plan-homework`, `build-homework`, `new-item-class`; `write-items` hands
  `homework` off to `plan-homework`.
- **Agents (4):** `homework-planner` (drafts the plan; writes nothing), `homework-item-writer`
  (HW-D09), `item-critic` (independent review), `item-solver` (HW-D05, HW-D07).
- **Skills (5):** `interviewing-teachers` (the interview, held by the command in the chat),
  `planning-homework` (the standard for a plan — shared by the planner and the chat that revises),
  `writing-code-items`, `writing-research-items`, `making-homework-documents`.
- **Schemas:** new — `homework`, `item-classes`, `homework-defaults`, `homework-document`; changed —
  `assessment-item` (optional homework fields; `answer` → `model_answer`), `course` (`tools`).
- **Templates:** `assessment/homework.md`; item templates for all six formats; `course/`
  `item-classes.yaml`, `homework-defaults.yaml`, `homework-document.yaml`; `course.yaml` declares
  three starter tools.
- **Python:** `model.py` loads homework and its configuration; `validate_homework.py` holds the
  rules; `approve.py` approves a homework; `status.py` shows it; `scaffold.py` creates a homework
  and classed items.

**One item schema, not two** (HW-D01): the item bank is shared across quiz, homework and exam, so
homework adds optional fields to the one item schema. What homework requires of an item is checked
by rules that judge only homework items and classes (HW-D10).

---

## 3. Content model — normative

### 3.1 The homework file

`course/assessments/homework/HW{NN}.md` — only names of that form are homework (a teacher's
`HW-notes.md` beside them is not): YAML front matter, validated against
`schemas/homework.schema.json`, and a teacher-facing body. Written in three stages — scaffolded,
planned, built — and approved twice.

**Required:** `id` (`^HW\d{2}$`, equal to the file name), `units` (≥1 unit id, unique), `purpose`
(`practice` | `graded` | `diagnostic`), `total_minutes` (integer ≥ 5, a student's budget), `items`
(array of item ids, unique — **empty until the build**).

**Settings (optional):** `due_date` (YYYY-MM-DD — quoted or not; printed on the student document,
HW-D30),
`source` (`{kind: material}` or `{kind: quiz_report, ref: U03}` — `ref` is the unit whose entry quiz
the report is about, HW-D35), `allowed_tools` (tool ids from `course.yaml`), `collaboration`
(`forbidden` | `discussion_only` | `allowed`), `accepted` (the teacher's exceptions,
framework D-037).

**Every homework is open book** — there is no setting for it (HW-D35).

**`plan`** — written by `/class-kit:plan-homework`, never printed in either document:
- `focus_notes`: the teacher's guidance for this homework; no student data (HW-D31)
- `quiz_summary`: for a quiz report, only the aggregated figures used and the misconceptions the
  teacher chose (HW-D33, HW-D34)
- `slots`: one per item to build — `slot` (number, unique), `guiding_questions` (≥1), `intent` (one
  line: what the item is for), `item_class`, `format`, and optionally `difficulty`, `bloom`,
  `est_minutes` (optional for a `time_variance: high` class, HW-D06), `tools` (HW-D28), `decision`
  (`fresh` | `reuse` | `adapt`; `reuse` and `adapt` need `from`, the existing item), `version` (a
  version label; absent — a shared slot), `item` (written by the build)

**`versions`** (targeted, HW-D26) — `label` (unique; never a student name), `targets` (≥1 Guiding
Question of the declared units), `items` (written by the build: each tests ≥1 target and no other
Guiding Question; never also a shared item). Versions need a `quiz_report` source. Every student
gets the shared `items` plus their version's.

**Written by the build:** `items`, each version's `items`, `item_tools` (item id → tools,
HW-D28, from the slots), each slot's `item`.

**`approved`** — `{date, stage, hash}`, written by `classkit approve homework N --stage planned |
built` (§4.4).

The quiz report itself is given in the session and never stored (HW-D33): aggregated results only;
names, identifiers, grades and the assignment of students to versions never enter the repository.

### 3.2 The item classes

`course/assessments/item-classes.yaml`: each key a class name (case-sensitive), each value:

| Field | Required | Notes |
|---|---|---|
| `description` | yes | one paragraph, shown while planning and on the student document |
| `typical_minutes` | yes | `{min, max}` (HW-D06) |
| `typical_bloom` | yes | Bloom levels the class works at |
| `default_tools` | yes | tool ids from `course.yaml` |
| `time_variance` | no | `low` (per-item minutes expected) or `high` (the range midpoint stands in) |
| `evaluation` | no | `strategy`: `persona_attempt` \| `execute` \| `skip` \| `custom` (HW-D05); `notes`; `custom_guide` — required for `custom`: a file, path relative to `course/` |
| `writing_guide` | no | the course's own guide for writing items of the class — a file, path relative to `course/` (HW-D35) |

The plugin's own guidance for the starter classes Coding and Research is in the skills
`writing-code-items` and `writing-research-items`. A course's own class gets its guidance as an
ordinary file that the writer and the critic **read** — an agent can read a file; it cannot load a
skill that is not in its own frontmatter (HW-D35).

### 3.3 The item schema's homework fields

Optional, and no format rules are added: quiz and exam items behave as before (HW-D10).

| Field | Purpose | Checked by |
|---|---|---|
| `item_class` | the item's class | `item_class_declared`, `item_class_bundle_drift` |
| `tolerance`, `tolerance_pct` | a numeric answer's tolerance — one of the two | — |
| `measurement_units` | a numeric answer's units (not `units`, which means course units; HW-D14) | — |
| `starter_code` | the skeleton a Coding student edits | — |
| `expected_solution`, `tests` | an autograded code item's reference and deterministic tests | `code_execution_reference_present` |
| `source_ref` | an adapted item's original, never changed | `item_source_resolvable` |
| `evaluation_strategy` | this item's own strategy, over its class's (HW-D07) | `code_execution_reference_present` |

`answer` is renamed **`model_answer`** (framework D-031g, carried out here, HW-D08), so it is not
confused with a Guiding Question's `answer` (where the answer is found); an item written with
`answer` is still read, as `model_answer`. There is no `status` field (HW-D35).

### 3.4 `course.yaml`'s tools

`tools`: tool id → `{description, availability?, url?}` (HW-D03). Every tool a homework's
`allowed_tools`, `item_tools` or a slot names, and every class's `default_tools`, must be a key
here. Items carry no tools of their own (HW-D28). A new course's `course.yaml` declares the three
tools the starter classes name; an older course is offered them by `/class-kit:plan-homework`.

### 3.5 Homework defaults

`course/assessments/homework-defaults.yaml` (HW-D16): `total_minutes`, `default_class_counts`
(items per class for an ordinary homework, HW-D27), `allowed_tools`, `collaboration`,
`reuse_policy`, `budget_tolerance_minutes`, `misconception_candidate_threshold_pct` (HW-D34). Read
by `/class-kit:plan-homework` and the planner; updated by `/class-kit:build-homework` after the
homework is approved as built.

### 3.6 Document settings

`course/assessments/homework-document.yaml` (HW-D30): required `course_title`, `semester`,
`title_format`, `language`, `direction`; optional `instructor`, `due_date_format`,
`submission_instructions`, `header`, `footer`, `logo`, `font`, `font_size`, `show_est_minutes`.
`title_format` placeholders: `{course_title}`, `{semester}`, `{number}` (`HW03` → 3), `{id}`,
`{units}`. Holds no answers; committed with the course.

---

## 4. Control flow

### 4.1 `/class-kit:plan-homework [units] [purpose]`

0. **Status** (`classkit status`). A unit not yet built is said, and the teacher asked whether to go
   on. A homework named instead (`HW03`) revises its plan.
1. **The file:** `classkit scaffold homework --units U03 U04` — the next `HW{NN}.md` as a placeholder,
   and the three configuration files when missing (create-only, logged). An older course that lacks
   the starter classes' tools is offered them (`--diff`, then `--overwrite` on the go-ahead).
2. **The interview, in the chat** (`interviewing-teachers`; HW-D35 reverses HW-D04): the whole set of
   settings drafted from the defaults, shown once; only what the teacher knows better is asked; two
   rounds at most. Due date and focus notes are agreed here. Follow-ups are listed and acted on only
   with consent. For a quiz report (2a): misconceptions at or above the threshold are listed and the
   teacher chooses (HW-D34).
3. **The draft plan:** `homework-planner` returns the brief, the complete file and its questions; the
   teacher sees the brief (prose; the slot table on request); the chat revises (`planning-homework`).
4. **Write** (exit 3 on the placeholder → go-ahead → `--overwrite`), validate, fix what the plan
   caused, log.
5. **Revision**, as many rounds as the teacher wants.
6. **Gate 1:** `classkit approve homework N --stage planned`.

### 4.2 `/class-kit:build-homework N`

0. **Status.** A homework not approved as planned: ask whether to go on.
1. **Reused items:** adding `homework` to an existing item's `usage` is a change to it — `--diff`,
   one go-ahead for all. An entry-quiz item of a unit approved as built is part of that unit's
   approval: the unit then reads "built — edited since", and the teacher is told.
2. **Write** — `homework-item-writer`, one slot at a time: a new item with the next free id for its
   unit (`classkit scaffold item UNN --format F --class C`, then filled). An adapted item is a new
   item with `source_ref`; the original is never changed.
3. **Review** — `item-critic`: alignment, stem clarity, Bloom and class fit, giveaways, rubric, and
   material fit — what the item needs must be in what students were assigned (HW-D19). The chat
   applies fixes; the writer is re-sent only for a rewrite. **At most two rounds per item.**
4. **Attempt** — `item-solver`, by strategy (§4.3); at most two rounds. A skipped item gets a
   teacher aid (HW-D18), shown, not saved (HW-Q06).
5. **The item list** — `items`, versions' `items`, `item_tools`, slots' `item` written into the
   homework file (`--diff`, then `--overwrite` on the go-ahead); `classkit validate`; fix what the
   build caused; log.
6. **Gate 2:** `classkit approve homework N --stage built`. Without it the homework stays *planned*,
   and the files this run created and changed are listed — nothing is deleted.
7. **Defaults** updated from what the teacher chose (`--diff`, go-ahead, `--overwrite`), logged.
8. **Report** — and the Word or PDF documents are available whenever the teacher asks.

Never silently converge by lowering standards: what is still disputed after two rounds goes to the
teacher at Gate 2.

### 4.3 How an item is checked (item-solver)

1. The item's `evaluation_strategy`; else its class's `evaluation.strategy`; else `persona_attempt`
   when it has a model answer or rubric, `not_applicable` otherwise.
2. `execute` on a format other than `code` falls back to `persona_attempt` (HW-D07).
3. `custom` follows the class's `custom_guide` file.
4. An item that needs a tool or data the agent cannot run is skipped, never invented (HW-D18).
5. Code runs only in a temporary folder outside the course — no installs, no network, no course
   files (HW-Q05 is still open).

### 4.4 States and approval

As for a unit (framework D-046): a homework is **drafted** (a file, not approved), **planned** (its
plan approved), **built** (the whole homework approved), each approved stage "edited since" when
its hash no longer matches. Nothing un-approves; no stage is blocked by another.

- The **planned** hash is over the file without its record and **without what the build writes**
  (`items`, `item_tools`, versions' `items`, slots' `item`) — so building does not make the plan
  "edited since"; `classkit status` says "items written, not yet approved as built".
- The **built** hash is over the file and every item it lists (by id; a missing item counts as
  missing), so editing an item shows "built — edited since".
- `classkit status` lists each homework only when there is one; a placeholder with no plan is
  listed among the placeholders.

There is no `status: draft` field and no `.plans/` folder (HW-D35, answering HW-Q03).

### 4.5 The documents, on request

When the teacher asks — after the build, at any time — the chat follows `making-homework-documents`
(HW-D23, HW-D24, HW-D30, HW-D35): a student document (no answers; one per version) and a teacher
answers document, laid out from `homework-document.yaml`; a **leak check** on every student
document; saved outside the repository or in a dedicated, locally ignored folder; never committed;
the `plan` never printed. Word through python-docx with the plugin's own Python; PDF converted from
the Word file with LibreOffice when it is installed, otherwise by the teacher from Word. A later
change goes into the item in the bank first, then the documents are made again.

### 4.6 The course log

Every approved step appends one `classkit log` entry; `classkit approve` logs itself. Entries name
ids and files — never student data, never the focus notes (HW-D32, HW-D33).

---

## 5. Data flow

| Who | Reads | Writes |
|---|---|---|
| `homework-planner` | course, syllabus, the units' sessions, the item bank, earlier homework, the configuration, the settings and aggregated figures it is given | nothing — returns the brief and the file |
| `homework-item-writer` | its slot, the unit's sessions, the item bank, the class (and its `writing_guide`), the plugin's item-writing craft | new item files, through `classkit write` |
| `item-critic` | the item, its slot, the Guiding Questions and their `answer` locators, the session's study paths, the class (and its guide) | nothing — returns findings |
| `item-solver` | the item, its slot, the class (and its `custom_guide`), course materials for teacher aids | nothing in the course — returns findings and teacher aids |
| the commands | everything above | the homework file, the configuration, reuse edits, the course log |

---

## 6. Invariants

- Every write goes through `classkit write`; an existing file is changed only after the teacher saw
  the diff and agreed (framework invariant 5, HW-D12).
- An adaptation creates a new item; the original is never changed.
- No student data in the repository (HW-D26, HW-D33).
- Homework is optional (HW-D13): a course without homework, and a scaffolded placeholder, have no
  homework findings; the configuration files appear only with the first homework.
- Nothing hardcodes a methodology or budget number: the budget tolerance is the teacher's
  `budget_tolerance_minutes`, else `homework_budget_tolerance_minutes` in
  `defaults/time-constants.yaml`.

---

## 7. Reference

### 7.1 Validator rules — 21

All are **consistency** rules (framework D-033): they judge the homework, classes and defaults that
exist, and are silent without them. Severities follow framework D-037 (HW-D32): a rule that finds
something that does not exist, or cannot be used, is an **error**; a departure the teacher may mean
is a **warn**, or an **alert** when it matters most. A homework file may `accepted:` an exception;
a course may change a severity in `course.yaml` `rules:`.

| Rule | Severity | Checks |
|---|---|---|
| `homework_item_reference` | error | Every item the homework lists, and every slot's `from` and `item`, exists; every `item_tools` key is an item of this homework |
| `homework_unit_reference` | error | Every unit in `units` exists |
| `homework_plan_reference` | error | Every slot's Guiding Questions exist; a slot's `version` is a version of this homework; slot numbers are unique |
| `homework_version_reference` | error | Version labels are unique; every target is an existing Guiding Question |
| `homework_source_quiz_exists` | error | A `quiz_report`'s `ref` unit exists and has entry-quiz items (`usage: in-class-quiz`) |
| `homework_tools_declared` | error | `allowed_tools`, `item_tools` and the slots' `tools` are declared in `course.yaml` |
| `class_tools_declared` | error | Every class's `default_tools` are declared in `course.yaml` |
| `item_class_declared` | error | An item's or a slot's `item_class` is defined in `item-classes.yaml` |
| `item_class_guide_reference` | error | A class's `writing_guide` and `custom_guide` files exist, inside `course/` |
| `item_source_resolvable` | error | An adapted item's `source_ref` exists |
| `code_execution_reference_present` | error | A `code` item checked by `execute` has `expected_solution` and `tests` |
| `homework_defaults_class_reference` | error | Every class `default_class_counts` names exists |
| `homework_coverage` | **alert** | Every unit of the homework is tested by one of its items — or, before the build, by one of its slots |
| `homework_item_usage` | warn | A listed item has `homework` in its `usage` |
| `homework_units_declared` | warn | A listed item, or a slot's Guiding Question, belongs to one of the homework's units |
| `homework_budget_fits` | warn | A student's minutes (the shared items — plus, with versions, each version's; the shared part is then never judged alone; before the build, the slots) are within the tolerance of `total_minutes`; a missing estimate counts the class midpoint (HW-D06) |
| `homework_versions_targeted` | warn | Targets are in the homework's units; each target is tested by a version item; each version item tests a target and nothing else, and is not also shared |
| `graded_requires_rubric` | warn | On a graded homework, every `open` and `code` item has a rubric |
| `item_class_bundle_drift` | warn | An item's Bloom level and minutes are within its class |
| `item_class_evaluation_declared` | warn | A class says how its items are checked |
| `homework_defaults_consistent` | warn | The default counts plan at least one item, and fit the default budget |

Two rules of the module's design are the plugin's own: `homework_schema` is `schema`, and
`homework_id_consistency` is `id_consistency` (HW-D35). `assessment_scheme_complete` — the one
completeness rule — waits for the syllabus's `assessment` block, which is not designed; it is not
registered.

### 7.2 Identifiers

- Homework: `^HW\d{2}$` — `HW01`…`HW99`, the file's name
- Item: `^U\d{2}-I\d{2}$`; Guiding Question: `^U\d{2}-S\d{2}-G\d+$`
- Version label: unique within the homework; never identifies a student

---

## 8. Design decisions — index

Each decision has a full entry in `_devlog/01-decisions.md`. **HW-D35 changes several of the
earlier ones** for the plugin; where an earlier decision says otherwise, HW-D35 holds.

| ID | Title | Status |
|---|---|---|
| HW-D01 | Homework as a first-class content type | provisional (its separate plan file replaced by HW-D35) |
| HW-D01 addendum | `/write-items homework` hand-off | provisional (now to `/class-kit:plan-homework`) |
| HW-D02 | Item classes as pedagogical bundles | provisional |
| HW-D03 | Tools as open course-declared strings | provisional |
| HW-D04 | Interviewer as a general-purpose agent | **reversed by HW-D35** |
| HW-D05 | Evaluation strategy declared per item class | provisional |
| HW-D06 | Item time estimates are class-dependent | provisional |
| HW-D07 | Evaluation strategy overridable per item | provisional |
| HW-D08 | The D-031g rename (`answer` → `model_answer`) carried out here | done |
| HW-D09 | Homework items get their own writer agent | provisional |
| HW-D10 | Formats belong to the framework; homework adds only the class axis | provisional |
| HW-D11 | Module-local numbering (`HW-D`, `HW-Q`) | provisional |
| HW-D12 | All homework writes go through `classkit write` | provisional |
| HW-D13 | Homework is optional | provisional |
| HW-D14 | Numeric answer units are `measurement_units` | provisional |
| HW-D15 | One command with two gates | **replaced by HW-D35** (two commands) |
| HW-D16 | `homework-defaults.yaml` gets a schema and a rule | provisional |
| HW-D17 | `/review-homework` removed | provisional |
| HW-D18 | Tool-dependent items are skipped; skipped items get a teacher aid | provisional |
| HW-D19 | `item-critic` checks material fit | provisional |
| HW-D20 | Homework documents are in scope | provisional |
| HW-D21 | One shared item bank | provisional |
| HW-D22 | `classkit bank` | **deferred by HW-D35** |
| HW-D23 | An agent creates the Word documents, with a leak check | provisional (on request, HW-D35) |
| HW-D24 | The documents go where the teacher chooses, never into git | provisional |
| HW-D25 | `answer_release` dropped | provisional |
| HW-D26 | Targeted versions; no student data in the repository | provisional |
| HW-D27 | Item counts per class | provisional |
| HW-D28 | Per-item tools in the homework (`item_tools`) | provisional |
| HW-D29 | `prerequisites` dropped | provisional |
| HW-D30 | Document settings in `homework-document.yaml` | provisional |
| HW-D31 | Focus notes never in the documents; due date approved with the plan | provisional (stored in the plan, HW-D35) |
| HW-D32 | Severities follow framework D-037; `accepted:`; log entries at approvals | provisional |
| HW-D33 | The quiz report is given in the session, aggregated, never stored | provisional |
| HW-D34 | A threshold lists misconceptions; the teacher chooses | provisional |
| HW-D35 | The plugin form: two commands, one file with its approval, documents on request, the interview in the chat, course guides as files | decided 2026-11-07 |

---

## 9. Open questions — index

Each has a full entry in `_devlog/03-open-questions.md`.

| ID | Title | Status |
|---|---|---|
| HW-Q01 | Item format extensibility | open |
| HW-Q02 | Item bank ingest | deferred (HW-D35) |
| HW-Q03 | Agent-authored files: what status? | **answered by HW-D35** — the approval record, no `status` field |
| HW-Q04 | Should item-critic and item-solver apply to quiz and exam items? | open |
| HW-Q05 | A sandbox for running code | open |
| HW-Q06 | Where homework is graded, and what must stay hidden | open — linked to Q-002 |
| HW-Q07 | Re-reviewing a finished or old homework | open |
| HW-Q08 | Bank growth: identifier capacity and provenance | deferred (HW-D35) |

---

## 10. Known weaknesses and open risks

- **The agents have never run on a real course.** The rules, scaffolding and approval are tested
  (`tests/test_homework.py`); the commands, gates and loops are first exercised by the first real
  homework.
- **No sandbox for `execute`.** The solver runs code in a temporary folder, with the teacher's
  permission prompts; there is no resource policy (HW-Q05).
- **Quiz and exam items get less review** than homework items (HW-Q04).
- **The teacher aid is not saved** (HW-Q06): the documents can use it only while it is still in the
  conversation.
- **A placeholder may be left behind:** a plan abandoned before it is written leaves its scaffolded
  file, which adds no finding of its own and shows as a placeholder in `classkit status`.
- **An older course declares no tools:** its first homework creates item classes that name three;
  `class_tools_declared` reports them until they are declared — `classkit scaffold homework` says
  so, and `/class-kit:plan-homework` offers to add them.
- **An unreadable `item-classes.yaml`** is one `schema` error; until it is fixed, no item or count is
  reported as naming an undefined class.

---

## 11. File map

```
dev/homework/                      the documents (never shipped)
├── README.md, HOMEWORK-SPEC.md, ROADMAP.md, PLUGIN-PORT.md
└── _devlog/  README, 00-brief, 01-decisions (HW-D01..D35), 02-progress,
              03-open-questions (HW-Q01..Q08), 04-handoff

plugin/
├── commands/   plan-homework.md, build-homework.md, new-item-class.md, write-items.md (hand-off)
├── agents/     homework-planner.md, homework-item-writer.md, item-critic.md, item-solver.md
├── skills/     interviewing-teachers, planning-homework, writing-code-items,
│               writing-research-items, making-homework-documents
├── schemas/    homework, item-classes, homework-defaults, homework-document (new);
│               assessment-item, course (changed)
├── templates/  assessment/homework.md, assessment/item-{six formats}.md,
│               course/item-classes.yaml, homework-defaults.yaml, homework-document.yaml,
│               course/course.yaml (tools)
├── defaults/time-constants.yaml   homework_budget_tolerance_minutes
└── src/classkit/  model.py, validate.py + validate_homework.py, approve.py, status.py,
                   scaffold.py, cli.py

tests/test_homework.py
```
