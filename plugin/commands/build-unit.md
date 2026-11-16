---
description: Build one planned unit — its study sessions (guiding questions, where each answer is found, study times, study paths), its entry quiz and its class hour — revised with the teacher, step by step
argument-hint: "<unit number> [session K | quiz | class] [optional: what to change, or what to focus on]"
---

Build unit **N** — `/class-kit:build-unit 3` — on its approved plan: the **study sessions** students
work through at home, the **entry quiz** that opens the class meeting, and the **class hour** built on
both. The agents draft from the unit's plan and its own material; the teacher revises, in
conversation or by hand. A part after the number — `session 2`, `quiz`, `class` — builds or revises
that part alone.

**How this command behaves.** It runs in steps. At each step: say what you are about to do, do only
that, show the result, and **wait for the teacher's approval or correction** before the next one.
The gates live here, between steps — a subagent cannot ask the teacher anything, so the agent
returns its questions and you ask them. Every approved step is logged with `classkit log`. Never
write a file directly: the agents return text, and `classkit write` (which refuses to overwrite
without consent) puts it on disk. The order is load-bearing: the sessions first (the quiz and the
hour are built on their guiding questions), the quiz before the hour (the hour lists the quiz's real
item ids — D-031a).

**Load the `class-kit:writing-guiding-questions` and `class-kit:estimating-study-time` skills** before
step 1's gate: they are the standard the designer drafts to, and you apply the teacher's corrections
to that same standard.

---

## Step 0 — Where the course stands, and what to build.

```bash
classkit status
```

Show it to the teacher. Then read `course/course.yaml`, the methodology file `status` names, the
unit's `unit.md`, the syllabus's Course Outcomes and unit map, and the recent entries in
`course/LOG.md`.

- **Which unit, which part.** The number is the first word of `$ARGUMENTS`; then, optionally, a part
  — `session K`, `quiz`, `class` — and anything after it is what the teacher wants changed or
  focused on. No number: ask, and suggest the first unit that is *planned* and not *built*. A part
  named: go straight to its step and build or revise that part alone.
- **The unit is not started** (on the map, no directory): units are planned first — offer
  `/class-kit:plan-unit N`.
- **The unit is not planned** (status says *drafted*, no approval): say so — the sessions are built
  on its objectives, which may still change — and **ask whether to go on**. Do not refuse (D-043).
- **The unit is built already**, or a part has the teacher's content: this run is a **revision**
  (§5.2 rule 3) — of the part named, or of what the teacher wants changed. Rebuilding from scratch
  only on the teacher's explicit word, and still through the diff.

Run `classkit doctor` and note which private materials are **index-only on this machine** — the
agents must be told.

## Step 1 — The study sessions.

Run the **class-kit:study-session-designer** agent with task **`draft`** (or **`rework`** for one session,
`session K`), naming the unit. Tell it which private materials are index-only here, whether the unit
is planned, and what the teacher said they want — **in their own words**. If the teacher wants a
session students may start a week early (a light unit absorbing part of a heavy one — D-052), tell
the agent: it says so in that session's text.

Show the teacher, session by session:

1. the **guiding questions** — each with its objectives, its `est_minutes`, and where its answer is
   (the locators); the deferred ones marked;
2. **the budget** — per session, the sum against the methodology's minutes, and what each estimate
   rests on;
3. any **objective no question addresses**, and any **difficulty no question surfaces**;
4. the **study paths** offered;
5. the agent's **questions**, each with what the sessions do if it stays unanswered;
6. what it **guessed**, and which materials it read only by index on this machine.

**Wait.** Collect the teacher's answers and corrections; then apply them to the returned files
yourself, with the skills. A change too large to make here goes back to the designer as a
**`rework`**. If the teacher wants real videos or web resources for a session's paths, run the
**class-kit:topic-researcher** agent and add only what it verified and the teacher wants.

### Step 1a — ask before writing. (A turn boundary: end your turn here.)

The session files exist — scaffolded with the unit. For each: if it holds **only the scaffolded
placeholders** (`prompt: "TODO…"`), say so; otherwise the teacher has content there — show
`classkit write <path> --diff` with the new content. If the sessions now number **more** than the
files, the new ones are new files; if **fewer**, say which file is left over — nothing here deletes
a file: the teacher removes it by hand, or keeps it. Either way `session_count` will warn, and
accepting it is the teacher's call. Ask for the go-ahead — one question for all the sessions of this
run.

**Wait for the teacher's answer.** Nothing else happens in this turn.

### Step 1b — on the go-ahead: write, check, show.

Write each session through the write path:

```bash
classkit write course/units/03-heaps/sessions/01.md --overwrite <<'SESSION'
---
id: U03-S01
…
SESSION
```

Then run `classkit validate` and **fix what the sessions caused** — a schema error, an objective the
unit does not define (`goal_maps_to_objective`), a locator that does not resolve
(`material_locator_resolves`), a session over its budget (`session_budget_feasibility` — by cutting or
moving a question, **never by shaving an estimate**), a question with no answer that is not deferred
(`answer_reference_present`), an instructor material cited to students (`instructor_material_cited`)
— by correcting the session and writing it again (`--diff`, then `--overwrite`); say what you fixed.
Report every alert and error, and count the warnings. **Expected at this stage** — say what they
are rather than fixing them: `deferred_question_resolved_in_class` until the class hour picks the
deferred questions up (step 3), `unit_has_entry_quiz_items` until the quiz exists (step 2) — only for
a unit not approved as *planned*, which is not checked for it —
and the placeholder class hour's findings. Never add `accepted:` or
change `rules:`.

Show the teacher where the files are — `course/units/NN-slug/sessions/` — to read and edit by hand as
they like. **Wait.** Then log:

```bash
classkit log "/class-kit:build-unit 3, step 1 approved — study sessions written" \
  --changed "U03: 4 sessions, 15 guiding questions (1 deferred), 98 of 100 min" \
  --why "<what the sessions rest on, and the teacher's main decisions — what was cut, what was deferred>" \
  --file units/03-heaps/sessions/01.md --file units/03-heaps/sessions/02.md …
```

## Step 2 — The entry quiz.

The quiz opens the class hour: a few items that show who studied and which misconception the next
activity must address — **diagnosis, not a grade**.

Run the **class-kit:assessment-writer** agent with task **`draft`** (or **`rework`**, for `quiz` with
something to change), naming the unit. Tell it which private materials are index-only here, how long
the teacher wants the quiz (or that the hour's quiz activity sets it), and what the teacher has said
about their students' misconceptions — **in their own words**.

Show the teacher, item by item:

1. the stem and its choices — which is correct, and **what each wrong choice reveals** (the
   rationales are where the quality is, and what the teacher checks against the misconceptions they
   see) — or, for an open item, its rubric;
2. the guiding question it tests, and the locator its answer key rests on;
3. the total minutes, against the quiz's slot in the hour;
4. what the quiz leaves untested, the agent's **questions**, and what it **guessed**.

**Wait.** Apply the teacher's corrections yourself — to the agent's own standard for distractors
and rubrics (its sections *Multiple-choice: the distractors are the item* and *Open questions: the
rubric is the item*, in `${CLAUDE_PLUGIN_ROOT}/agents/assessment-writer.md`). A change too large to make
here goes back to the agent as a **`rework`**.

### Step 2a — ask before writing. (A turn boundary: end your turn here.)

A new item is a new file — nothing is replaced; say which files will be created. An item the teacher
already has (a revision): show `classkit write <path> --diff` with the new content. Ask for the
go-ahead — one question for all the items of this run.

**Wait for the teacher's answer.** Nothing else happens in this turn.

### Step 2b — on the go-ahead: write, check, show.

Write each item through the write path — a new file is created; an existing one is replaced only
with `--overwrite`, given for that item at 2a:

```bash
classkit write course/assessments/items/U03-I05.md <<'ITEM'
---
id: U03-I05
unit: U03
format: multiple-choice
usage: [in-class-quiz]
…
ITEM
```

Then run `classkit validate` and **fix what the items caused** — a schema error, a guiding question
that does not exist (`item_reference`), a choice item with no correct choice
(`item_no_correct_choice`), an open item with no rubric (`open_item_without_rubric`) — and say what you
fixed. Report every alert and error, and count the warnings. **Expected at this stage**: the class
hour's quiz activity does not list the items yet — step 3 does.

Show the teacher where the items are — `course/assessments/items/` — and **wait**. Then log:

```bash
classkit log "/class-kit:build-unit 3, step 2 approved — entry quiz written" \
  --changed "U03-I05…I08: 4 items, 7 min — U03-S01-G2, U03-S02-G1, U03-S03-G3, U03-S04-G1" \
  --why "<which misconceptions the quiz is aimed at, and the teacher's main decisions>" \
  --file assessments/items/U03-I05.md --file assessments/items/U03-I06.md …
```

## Step 3 — The class hour.

The hour is built on the home study and opens with the quiz, so it comes last: it needs the guiding
questions, and the quiz's **real** item ids (D-031a).

**How the meeting really runs** (Q-033, D-053). Read the syllabus's *teaching methods* section. If it
does not say how big a group is, whether the same hour is taught to several groups, or whether
students also have a TA session, **ask the teacher once** — in one message — and pass the answer on;
"I don't know" is a valid answer. Then suggest they write it into that section — by hand, or with
`/class-kit:build-syllabus` — so the next unit's hour and the critic read it there; this command does
not edit the syllabus.

Run the **class-kit:lesson-planner** agent with task **`draft`** (or **`rework`**, for `class` with
something to change), naming the unit. Tell it how the meeting runs, and what the teacher has said
they want from the hour — **in their own words**.

Show the teacher:

1. **the hour** — each activity, its minutes, the guiding questions it builds on, the quiz's item ids;
   the total against the methodology's minutes;
2. which **deferred** questions each activity resolves, and which **difficulties** it repairs;
3. the activities that build on **no guiding question**, their reasons, and their total against the
   cap — the cap is the teacher's to raise, never yours or the agent's (invariant 4);
4. the agent's **questions**, and what it **guessed**.

**Wait.** Apply the teacher's corrections yourself. A change too large to make here goes back to the
agent as a **`rework`**.

### Step 3a — ask before writing. (A turn boundary: end your turn here.)

`in-class.md` exists — scaffolded with the unit. If it holds **only the scaffolded placeholders**
(`title: "TODO"` activities), say so; otherwise the teacher has content there — show
`classkit write <path> --diff` with the new content. Ask for the go-ahead.

**Wait for the teacher's answer.** Nothing else happens in this turn.

### Step 3b — on the go-ahead: write, check, show.

```bash
classkit write course/units/03-heaps/in-class.md --overwrite <<'HOUR'
---
id: U03-IC
…
HOUR
```

Then run `classkit validate` and **fix what the hour caused** — an item id that does not exist
(`activity_item_reference`), a guiding question that does not exist
(`activity_references_guiding_question`), activities that do not sum to the hour
(`in_class_duration_match`), a deferred question no activity picks up
(`deferred_question_resolved_in_class`), unmapped time over the cap (`in_class_unmapped_time_cap` — by
building the activity on the week's questions or cutting it, **never by raising the cap**) — and say
what you fixed. Report every alert and error, and count the warnings. Never add `accepted:` or change
`rules:` or the cap.

Show the teacher where the file is — `course/units/NN-slug/in-class.md` — and **wait**. Then log:

```bash
classkit log "/class-kit:build-unit 3, step 3 approved — class hour written" \
  --changed "U03-IC: 5 activities, 50 min; quiz U03-I05…I08; resolves U03-S02-G4; 5 min unmapped (exam logistics)" \
  --why "<what the hour is built to repair, and the teacher's main decisions>" \
  --file units/03-heaps/in-class.md
```

## Step 4 — Approval, when the teacher says so.

The teacher decides when the unit is good enough to teach — at this gate, or later in conversation
("approve unit 3"). Never approve on your own, and never propose approval as a formality: say what is
still open (a session over budget, a deferred question no activity resolves, a guess the teacher has
not confirmed, an independent review not run), so they approve knowingly.

```bash
classkit approve unit 3 --stage built --why "<in a line: what was approved, and what is knowingly still open>"
```

It records `approved: {date, stage: built, hash}` in `unit.md` — the hash over the whole unit:
`unit.md`, its sessions, its class hour and its entry-quiz items — through the write path, and logs
the approval itself. Show `classkit status` afterwards: the unit now reads "built".

Tell the teacher:

- **Edits after approval are normal.** Nothing un-approves; editing any part of the unit makes
  `status` say "built — edited since", and approving again records the new version.
- **Next:** `/class-kit:review-unit N` for an independent review (optional); homework on the unit,
  `/class-kit:plan-homework`; the next unit, `/class-kit:plan-unit N` when its material is in.

## Revision — as many rounds as the teacher wants.

Each round: the teacher says what to change. **You revise it yourself, in this conversation**
(D-044) — you have what the teacher said, and an agent sent off again would start cold and lose it.
**Re-read the file first** — the teacher may have edited it by hand, and those edits are theirs.
Keep the ids (activities and items reference guiding questions by id); keep any `approved` block
exactly as it is. Show the change before writing it (`classkit write <path> --diff`), write it with
`--overwrite` on the teacher's OK, run `classkit validate` and fix what the change caused, and log the
round:

```bash
classkit log "/class-kit:build-unit 3, revision approved" --changed "U03-S02-G3 est_minutes 6 → 9; G4 moved to S03" \
  --why "<why the teacher wanted it>" --file units/03-heaps/sessions/02.md --file units/03-heaps/sessions/03.md
```

A change that belongs to the **plan** — a new objective, a different difficulty — is not made here:
say so, and offer `/class-kit:plan-unit N`. An independent review is optional:
`/class-kit:review-unit N`.

---

**Later runs.** Run `/class-kit:build-unit N session K` (or `quiz`, `class`) at any time — after
teaching the week, next year, or when the material changes. It revises that part; it never
regenerates what the teacher wrote unless asked.
