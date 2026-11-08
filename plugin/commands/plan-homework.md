---
description: Plan a homework over the units named — its settings agreed in a short interview, then a plan of item slots (each testing named Guiding Questions), drafted, revised with you and approved as planned; /class-kit:build-homework then writes the items
argument-hint: "<units, e.g. U03 U04> [practice|graded|diagnostic] — or a homework, e.g. HW03, to revise its plan"
---

Plan one homework — `/class-kit:plan-homework U03 U04 graded`. A homework is a set of Assessment
Items students do at home after the units it covers. It is kept in **one file**,
`course/assessments/homework/HW0N.md`, as a unit is kept in its `unit.md`: its settings, its
**plan** (written here), later the items it was built from, and the teacher's approval. The items
themselves live in the shared bank, `course/assessments/items/`. The milestone of this command is a
**planned** homework — approved, not perfect: `/class-kit:build-homework N` then writes its items.

**How this command behaves.** It runs in steps. At each step: say what you are about to do, do only
that, show the result, and **wait for the teacher's approval or correction** before the next one.
The gates live here, between steps — a subagent cannot ask the teacher anything, so the
**class-kit:homework-planner** returns its questions and you ask them. Every approved step is logged
with `classkit log`. Never write a file directly: `classkit write` (which refuses to overwrite
without consent) puts everything on disk (HW-D12). If it refuses a change the teacher has not
approved, stop and show them; never retry with `--overwrite` on your own.

**Load the `class-kit:interviewing-teachers` skill** before step 2 (the interview), and the
**`class-kit:planning-homework` skill** before step 3's brief: it is the standard the planner drafts
to, and you apply the teacher's corrections — and later revisions — to that same standard.

**Student data never enters the repository** (HW-D33). A quiz report comes from outside the course
(Moodle, the teacher's spreadsheet); the teacher gives it in this conversation, as a file or pasted
text, and it is never saved to the repository. It may hold aggregated results only — percentages
per Guiding Question, per item, or per answer choice ("42% chose B"). If it contains student names,
identifiers, grades or per-student answers, stop and ask for an aggregated version; copy none of it
anywhere. Which student gets which version is the teacher's record, outside the repository; version
labels never identify students.

---

## Step 0 — Where the course stands, and which homework.

```bash
classkit status
```

Show it to the teacher. Then read `course/course.yaml` and the recent entries in `course/LOG.md`.

- **The arguments** (`$ARGUMENTS`): the units (`U03 U04`, or `3 4`) and optionally the purpose
  (`practice`, `graded`, `diagnostic`). Missing units: ask, suggesting the units most recently
  built. Missing purpose: it is part of the interview.
- **A homework named instead** (`HW03`): this run **revises its plan** — read its file and go to
  step 5 with what the teacher wants changed. If it is already *built*, say that a changed plan
  changes what was built, and that `/class-kit:build-homework` will then have to rebuild the
  affected slots.
- **A unit not started** (on the map, no folder yet): it has no Guiding Questions at all, and a
  homework cannot cover it (`homework_unit_reference` is an error). Say so, and offer to leave it
  out or to plan the unit first (`/class-kit:plan-units`).
- **A unit not built** (status: *drafted* or *planned*): its Guiding Questions are still
  placeholders, and a homework tests Guiding Questions. Say so, and **ask whether to go on** — the
  plan can only use questions that exist. Do not refuse.
- **One homework per run.**

## Step 1 — The homework's file.

```bash
classkit scaffold homework --units U03 U04
```

It creates `course/assessments/homework/HW0N.md` with the next free number — a placeholder — and,
the first time a course has homework, the three files homework works from (HW-D13: a course only
gets them once it uses homework): `course/assessments/item-classes.yaml` (the item classes),
`homework-defaults.yaml` (the teacher's usual choices) and `homework-document.yaml` (how the
documents look). It never overwrites, and logs what it created. Tell the teacher what was created,
and that the three files are theirs to edit.

Run `classkit validate`. **An older course may not declare the tools the starter classes name**
(`class_tools_declared`): propose adding them to `course.yaml`'s `tools` — show
`classkit write course/course.yaml --diff` with the whole file and the entries added, and write it
with `--overwrite` only on the teacher's go-ahead; then log it. A teacher who would rather change
the classes' `default_tools` may do that instead.

## Step 2 — The interview: the homework's settings.

Ground yourself first — read:

- `course/course.yaml` (its `tools` and `textbooks`) and the methodology file (`classkit status`
  names it)
- `course/syllabus/syllabus.md`
- `unit.md` and `sessions/*.md` of the units named
- `course/assessments/items/`, and any earlier `course/assessments/homework/HW*.md`
- `course/assessments/homework-defaults.yaml`, `item-classes.yaml` and `homework-document.yaml`

Then interview the teacher **in this conversation**, to the `class-kit:interviewing-teachers` skill:
draft the whole set of settings from the defaults and what the teacher already said, show it in
one message, and ask only what the teacher knows better — one round, two at most.

The settings to draft: `units`, `purpose`, `total_minutes`, `source` (`material`, or a quiz report —
`quiz_report` with `ref`, the unit whose entry quiz it reports on), the **count of items per class**
(from `default_class_counts`, HW-D27 — not item ids), `allowed_tools`, the tools particular items
will need (HW-D28: one or more per item; a programming language counts), `collaboration`, an
optional `due_date` (ask now — it is approved with the plan), and optional
`focus_notes` — free text for this homework ("focus on hashing; avoid chaining"), never student data
(HW-D31). For a quiz report: the report itself (see above), and whether the teacher wants
**targeted versions** (HW-D26) — then the counts for the shared items and for each version.

Say which values you took from the defaults. Follow-ups the teacher raises outside the settings are
listed, and each is acted on only as its own change, with consent:

- **A tool `course.yaml` does not declare** — offer to add it (`--diff`, then `--overwrite` on the
  go-ahead), or note it for the report. It does not block the interview.
- **An item class `item-classes.yaml` does not have** — the plan cannot use it. Offer
  `/class-kit:new-item-class`, then come back to this command.
- **Anything else** (a stylistic note, a scheduling remark) — note it for the report.

If `homework-document.yaml`'s `semester` looks out of date, mention it: it is used only when the
documents are made, and can be updated then.

### Step 2a — a quiz-report homework: what to cover (HW-D34).

The threshold finds candidates; the teacher decides. Read
`misconception_candidate_threshold_pct` from `homework-defaults.yaml` — never assume a number; if it
is missing, ask. From the report and the entry-quiz items of the `ref` unit (its items with
`in-class-quiz` in their `usage` — a choice's `rationale` names the misconception it detects), list
every misconception and Guiding Question at or above the threshold, highest first, in plain words:

> At least <threshold>% of students struggled with these:
> 1. Collision handling — 42%
> 2. Average versus worst-case complexity — 36%
> 3. Hash-function selection — 28%
>
> Which should the homework include? You can pick all, some, or add another.

**Wait for the selection.** The teacher may pick all, some, or add something below the threshold.
This is part of planning, not a gate: it is not logged.

## Step 3 — The draft plan.

Send the **class-kit:homework-planner** with: the homework's id and file, the settings as agreed —
in the teacher's words where they gave reasons — and, for a quiz report, only the aggregated figures
you used and the teacher's selection. It returns the brief, the complete homework file, the budget
check, its questions and what it guessed; it writes nothing.

Show the teacher **the brief** — prose, never the slot table unless they ask — then the planner's
questions, each with what the plan does if it stays unanswered, and what it guessed.

**Wait.** Apply the answers and corrections to the returned file yourself, to the
`class-kit:planning-homework` skill. "Show me the table" → show the slot table; the teacher may edit
slots by number. A change too large to make here — other units, another source, a different count
per class — goes back to the planner to **rework**, with the current file.

On **graded** homework with versions whose workload or targets differ, the teacher must approve
that difference explicitly — a plain "go on" is not enough.

**If the teacher stops here**, nothing but the placeholder was written. Say it stays — it adds no
finding of its own, and `classkit status` lists it as a placeholder — and leave it to them.

## Step 4 — Write the plan.

```bash
classkit write course/assessments/homework/HW03.md <<'HOMEWORK'
---
id: HW03
…
HOMEWORK
```

**It will exit with code 3** — the placeholder exists. Nothing is written.

### Step 4a — ask before writing. (A turn boundary: end your turn here.)

If the file holds **only the scaffolded placeholder** (no slots; status says *drafted* and nobody
has edited it), say so — the refusal quotes the opening. Otherwise the teacher has content there:
show `classkit write <path> --diff` with the same content. Ask for the go-ahead.

**Wait for the teacher's answer.** Nothing else happens in this turn.

### Step 4b — on the go-ahead: write, check, show.

Write it with `--overwrite`. Then run `classkit validate` and **fix what the plan caused** — a
Guiding Question that does not exist (`homework_plan_reference`), a unit that does not exist
(`homework_unit_reference`), a class not declared (`item_class_declared`), a tool not declared
(`homework_tools_declared`), a `from` item that does not exist (`homework_item_reference`), a slot
outside the declared units (`homework_units_declared`), a declared unit no slot covers
(`homework_coverage`), slots over or under the budget (`homework_budget_fits`), versions
(`homework_version_reference`, `homework_versions_targeted`), the quiz source
(`homework_source_quiz_exists`) — by correcting the plan and writing it again (`--diff`, then
`--overwrite`), and say what you fixed. Report every alert and error, and count the warnings. Never
add `accepted:` or change `rules:` (HW-D32).

Show the teacher the file on disk — `course/assessments/homework/HW03.md` — to read and edit by hand
as they like. **Wait.** Then log:

```bash
classkit log "/class-kit:plan-homework HW03, plan written" \
  --changed "HW03: U03-U04, graded, 5 slots (2 DIY, 2 Practicing, 1 Coding), 90 min, due 2026-11-30" \
  --why "<what the plan rests on, and the teacher's main decisions — focus, what was cut, reuse>" \
  --file assessments/homework/HW03.md
```

Name ids and course-relative files — never student data, and never the focus notes.

## Step 5 — Revision, as many rounds as the teacher wants.

Each round: the teacher says what to change. **You revise it yourself, in this conversation**
(D-044), to the `class-kit:planning-homework` skill's **Revising** section. **Re-read the file
first** — the teacher may have edited it by hand. Keep the slot numbers; keep the `approved` block
exactly as it is; on a homework already built, keep `items`, the versions' `items`, `item_tools` and
each slot's `item` too — a changed slot is rebuilt by `/class-kit:build-homework`, not by emptying
them here. Send the planner to **rework** only when the change is structural or the teacher asks,
and check what it returns against the same list before showing the diff.

Show the change before writing it (`classkit write <path> --diff`), write it with `--overwrite` on
the teacher's OK, run `classkit validate` and fix what the change caused. Log each approved round:

```bash
classkit log "/class-kit:plan-homework HW03, revision approved" --changed "HW03 slot 2: Practicing → Coding" \
  --why "<why the teacher wanted it>" --file assessments/homework/HW03.md
```

## Step 6 — Approval, when the teacher says so.

The teacher decides when the plan is good enough to build on. Never approve on your own, and never
propose approval as a formality: say what is still open (a slot the budget squeezes, a quiz signal
that was thin, a question the teacher left unanswered), so they approve knowingly.

```bash
classkit approve homework 3 --stage planned --why "<in a line: what was approved, and what is knowingly still open>"
```

Always `--stage planned` here. It records `approved: {date, stage: planned, hash}` in the homework's
file through the write path and logs the approval itself — no separate `classkit log`. `--diff`
shows the change first. Show `classkit status` afterwards: the homework now reads "planned".

Tell the teacher:

- **Edits after approval are normal.** Nothing un-approves; `classkit status` will say "planned … —
  edited since", and approving again records the new version. Building it does **not** count as an
  edit of the plan: the plan's record leaves out what the build writes.
- **Next:** `/class-kit:build-homework 3` writes the items, reviews and attempts each one, and asks
  for approval of the whole homework as *built*.
