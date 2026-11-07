---
description: Build a planned homework — write its items into the shared bank from the approved plan, review each with an independent critic, attempt each as student personas, list them in the homework's file, validate, and ask for approval of the whole homework as built
argument-hint: "<homework number, e.g. 3 or HW03>"
---

Build homework **$1** from its approved plan, in `course/assessments/homework/HW0N.md`. Each slot of
the plan becomes an item in the shared bank, `course/assessments/items/` — reused, adapted into a
new item, or written fresh — then reviewed, attempted, and listed in the homework's file. The
milestone is a **built** homework, approved by the teacher. There is no separate review command:
the critic and the solver run inside this build (HW-D17).

**How this command behaves.** The teacher decides at two points: before anything existing changes
(step 1, and the homework's file at step 5) and at the end (step 6, approval). In between, the
build runs without stopping, but announces each step as it goes — "writing item 3 of 6", "critic,
round 2", "solver". Writer, critic and solver rounds need no separate approval. This is how this
command applies "stepwise, with the teacher's approval".

**Every file goes through `classkit write`** (HW-D12) — never a raw file write. New items are
written plainly. Changing a file that already exists needs `--overwrite`, and only for a change the
teacher approved:

- adding `homework` to a reused item's `usage` — approved at step 1
- the homework's file — its item list, approved at step 5
- `homework-defaults.yaml` — approved at step 7

The one exception is an item **this run created**: it may be revised with `--overwrite` while the
build goes on. Never `--overwrite` any other item — it may be used by other homework, a quiz or an
exam. If `classkit write` refuses a change the teacher has not approved, stop and show them; never
retry with `--overwrite` on your own.

---

## Step 0 — Where the course stands, and the plan.

```bash
classkit status
```

Show it to the teacher, and read the homework's file (`$1` may be `3` or `HW03`).

- **No such homework:** say so, and offer `/class-kit:plan-homework`.
- **Not planned** (status: *drafted*): its plan was never approved. Say so and **ask whether to go
  on** — do not refuse. A placeholder with no slots has nothing to build: offer
  `/class-kit:plan-homework HW03`.
- **Planned, edited since:** mention it — the build follows the file as it is now.
- **Already built:** this run is a **revision** — ask which slots to rebuild, and build only those.

Then read: `course/course.yaml` (its `tools`) and the methodology file (`classkit status` names it),
the sessions of the homework's units, `course/assessments/item-classes.yaml`,
`homework-defaults.yaml`, and every item a slot's `from` names.

## Step 1 — Reused items. (A turn boundary when there is anything to ask.)

For every slot with `decision: reuse`: the item is used **unchanged**. If its `usage` lacks
`homework`, adding it changes an existing file — list those items, show the change
(`classkit write <item> --diff`), and ask once for all of them. An entry-quiz item of a unit
approved as *built* is part of that unit's approval: the change makes the unit read "built — edited
since" in `classkit status`. Say so; approving the unit again (`classkit approve unit N --stage
built`) records it, if the teacher wants.

**Wait for the answer.** On the go-ahead, write them with `--overwrite`. If the teacher declines,
the item is still used as it is — `homework_item_usage` will warn, and that is the teacher's call —
or they may choose another item, which changes the plan (`/class-kit:plan-homework HW03`).

## Step 2 — Write the items.

For every slot with `decision: fresh` or `adapt`, in plan order, send the
**class-kit:homework-item-writer** with that slot and the homework's `purpose` and `units`. It
creates the item with the next free id for its unit (`classkit scaffold item`), writes it through
`classkit write`, and returns its id. An adapted item is always a **new** item with `source_ref`
naming the original; the original never changes. Keep a list of every file this run creates.

## Step 3 — Review each item.

Send the **class-kit:item-critic** with the items and their slots. It returns, per item, issues
(severity, where, what) and that item's verdict: `pass`, `promote-anyway`, `revise` or
`deadlocked`. It never rewrites.

On `revise`, **revise the item yourself** (D-044), to the critic's findings — the item is one this
run created, so `classkit write <item> --overwrite` — and send it back to the critic. **At most two
rounds per item**; tell the critic which round it is on. Still blocking after the second: the item
goes on as **deadlocked**, and the disagreement goes to the teacher at step 6. A revision so large
that the item must be rewritten goes back to the writer.

Material fit (HW-D19): when the critic reports that the assigned material does not cover what an
item needs, revise the **item**. Never change sessions, study paths or answer locators; if the
material should change instead, that is the teacher's choice at step 6.

## Step 4 — Attempt each item.

Send the **class-kit:item-solver** with the items and their slots. It resolves each item's strategy
(the item's `evaluation_strategy`, else its class's `evaluation.strategy`; HW-D05, HW-D07): it
attempts as two student personas, runs a code item's tests, follows a class's `custom_guide`, or
skips — Research, and items needing a tool or data it cannot run (HW-D18) — returning a **teacher
aid** instead.

On `revise`, revise the item yourself as in step 3, and send it back to the solver — and to the
critic, if the change touched what the critic judged. **At most two rounds per item** in all;
still failing, it goes on as **deadlocked**. Keep every teacher aid: it is shown at step 6 and is
not saved anywhere (HW-Q06).

## Step 5 — The homework's item list. (A turn boundary.)

Write the built items into the homework's file — its front matter, everything else exactly as it
is:

- `items` — the shared slots' items, in plan order
- each version's `items` — its slots' items
- `item_tools` — each item whose slot names `tools`, with those tools (HW-D28)
- each slot's `item` — the item built for it

Show `classkit write course/assessments/homework/HW03.md --diff`, and say which items it lists.
**Wait for the go-ahead**, then write it with `--overwrite`.

Run `classkit validate` and **fix what the build caused** — an item that does not exist
(`homework_item_reference`), a class not declared (`item_class_declared`), a code item set to
`execute` without its reference solution or tests (`code_execution_reference_present`), an adapted
item whose original does not exist (`item_source_resolvable`), an item outside the declared units
(`homework_units_declared`), a declared unit no item covers (`homework_coverage`), the items over or
under the budget (`homework_budget_fits`), an `open` or `code` item without a rubric in a graded
homework (`graded_requires_rubric`), versions (`homework_versions_targeted`), an item outside its
class's range (`item_class_bundle_drift`). Fix by revising the items this run created — and say what
you fixed. `homework_item_usage` on an item the teacher chose not to change at step 1 stays. Report
every alert and error, and count the warnings. Never add `accepted:` or change `rules:` (HW-D32).

Then log:

```bash
classkit log "/class-kit:build-homework HW03, items written" \
  --changed "HW03: 5 items — U03-I12, U03-I13 (adapted from U03-I05), U04-I07 (reused), …" \
  --why "<built from the plan approved on …; anything the teacher decided on the way>" \
  --file assessments/homework/HW03.md --file assessments/items/U03-I12.md
```

## Step 6 — The teacher approves the result.

Show the teacher, in prose:

- The homework: each item by what it is about (not its id), its class and minutes; the total
  against `total_minutes`; the count per class; for versions, each student's workload
- Any **deadlock** — "the critic thinks X, the writer's version does Y; you decide" — and solver
  deadlocks the same way
- **Research items:** no automated key check by design — the teacher should read each one, with
  its teacher aid: references (marked if unverified) and what a strong answer covers
- **Check by hand:** every tool-dependent item the solver skipped, with the expected approach
- **Code items:** whether the reference solution passed its tests when the solver ran them, and if
  not, what failed
- **Material fit** (HW-D19): items the critic could not verify against the assigned material, and
  any case where the material, rather than the item, might be what should change
- The validator's warnings still standing, and the follow-ups from planning not yet resolved
- Every file created or changed in this run

Three outcomes:

- **Approve** →

  ```bash
  classkit approve homework 3 --stage built --why "<in a line: what was approved, and what is knowingly still open>"
  ```

  It records `approved: {date, stage: built, hash}` — the hash covers the homework's file and every
  item it lists — and logs the approval itself. Never approve on the teacher's behalf.
- **Revise specific items** → those items go back through steps 3–5. Return here when they are
  done.
- **Reject** → nothing is deleted: silent deletion risks losing work the teacher wanted to keep.
  The homework stays *planned* (`classkit status`); list the files this run created and changed, so
  the teacher can decide about each — keep them, edit them, or remove them themselves.

## Step 7 — Defaults.

After an approval only: compare what the teacher chose with `homework-defaults.yaml`. Values left
at the default: leave them. Values the teacher changed (the budget, the tools, collaboration, the
count per class), so the next homework need not ask again: show `classkit write --diff`, write with
`--overwrite` on the go-ahead, and log it. `default_class_counts` describes an ordinary homework:
update it only from a homework without versions.

## Step 8 — Report.

In prose: which Guiding Questions the homework exercises, which items were reused, adapted or
fresh, the total time against the budget, follow-ups that need the teacher, and anything the plan
cut for time. End by saying that the teacher can ask for the homework's **Word or PDF documents**
at any time — the student document and the teacher answers document (the
`class-kit:making-homework-documents` skill says how).

---

**Reference answers live in the item files**, per format: `open` → `model_answer` and `rubric`;
`numeric` → `model_answer` (with `tolerance`); autograded `code` → `expected_solution` and `tests`
(`model_answer` is not used); `multiple-choice`, `multiple-select`, `true-false` →
`choices[].correct`. Their git history is permanent. No worked solution goes in the homework's
body. Students only ever see the student document, protected by its leak check; publishing
solutions to them is the teacher's decision (HW-D25).
