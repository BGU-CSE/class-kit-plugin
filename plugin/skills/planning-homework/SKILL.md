---
name: planning-homework
description: The standard for a homework's plan (the `plan` of course/assessments/homework/HW0N.md) — a coverage skeleton of item slots, each testing named Guiding Questions; reuse, adapt or fresh; the time budget; quiz-report homework and targeted versions; and the brief the teacher reads instead of the slot table. Use when planning or revising a homework — by homework-planner, and by the chat during /class-kit:plan-homework's revision rounds.
---

# Planning a homework

A homework is a set of Assessment Items students do at home after the units it covers. Planning
it decides **what it covers and with what shape of items** — before anyone writes an item
(`/class-kit:build-homework`). The agent that drafts the plan and the chat that revises it with
the teacher both work to this skill, so the teacher gets one standard.

**The plan is a coverage skeleton, not a set of items.** Every slot names one Guiding Question
(or a small set) and the intent of the item that will test it. The item's stem is not the
planner's job; its purpose is.

The shape is `${CLAUDE_PLUGIN_ROOT}/schemas/homework.schema.json`: the homework's settings
(`units`, `purpose`, `total_minutes`, `due_date`, `source`, `allowed_tools`, `collaboration`,
`open_book`), the `plan` (`focus_notes`, `quiz_summary`, `slots`), `versions` when targeted, and
`items: []` — the build fills `items`, `versions[].items`, `item_tools` and each slot's `item`.

## A slot

| Field | What it holds |
|---|---|
| `slot` | Its number — the teacher edits slots by number ("slot 2 harder") |
| `guiding_questions` | What the item will test, by id — real ones only |
| `intent` | One line: "remediate the O(1) vs worst-case misconception from the U03 quiz", not "assess understanding of hashing" |
| `item_class` | A class from `course/assessments/item-classes.yaml` |
| `format` | The answer shape: open, code, numeric, multiple-choice, multiple-select, true-false |
| `difficulty`, `bloom` | The target |
| `est_minutes` | For a class with `time_variance: low`; optional for `high` (its range midpoint is used) |
| `tools` | The tools this item needs (HW-D28): one or more, a programming language counts, all declared in `course.yaml`'s `tools`. The build copies them into `item_tools` |
| `decision`, `from` | `fresh`; `reuse` with `from: U03-I05`; `adapt` with `from: U03-I05` |
| `version` | A version's label, for a version slot; absent for a shared slot |

The number of slots per class is the teacher's count for this homework — from
`homework-defaults.yaml`'s `default_class_counts` unless they gave others (HW-D27).

## The budget

Sum the slots' minutes: a slot's `est_minutes` when present (typical for DIY and Practicing,
`time_variance: low`); the midpoint of its class's `typical_minutes` when absent (Coding and
Research, `time_variance: high`, where a single number is fake precision). Compare with
`total_minutes`. If the sum is further off than `budget_tolerance_minutes` (in
`homework-defaults.yaml`), revise before showing the brief. When the plan is heavy on
high-variance classes, say in the brief that actual times will vary widely per student — the sum
is a rough budget, not a promise.

## Where the slots come from

**From material.** Draw Guiding Questions across the declared units in proportion to their weight.
The teacher's `focus_notes` override even distribution — "focus on hashing" means weight toward
the unit that teaches it. Never target a Guiding Question of a unit the homework does not declare
(`homework_units_declared` would warn, and the plan caused it — revise the plan instead).

Guiding Questions are approved work of the units: do not re-audit them here. If one is malformed
enough to break planning, the build's critic will catch the resulting item.

**From a quiz report** (`source: {kind: quiz_report, ref: U03}` — the unit whose entry quiz it
reports on). Map each result to what it means: a Guiding Question's percentage directly; an
answer choice through that choice's `rationale`, which names the misconception it detects. The
teacher has chosen which misconceptions and Guiding Questions to cover (HW-D34); plan **only**
from that selection, each selected one getting at least one slot whose `intent` names it.

`plan.quiz_summary` keeps only the aggregated figures the plan used ("U03-S02-G2: 38% correct";
"U03-I04, choice B: 42% — confuses average with worst case") and the teacher's selection. Nothing
else from the report enters the repository — never names, identifiers, grades or per-student
answers (HW-D33).

If the report is thin, say so — don't fabricate a diagnostic story to justify the homework. A
report with no signal is a homework that should come from `material`, and the teacher needs to
know.

**Targeted versions** (HW-D26) — when the teacher wants them. Group the selected Guiding
Questions into versions: each with a unique `label` (never a student's name), at least one
target, and at least one slot per target. A version slot tests only its version's targets;
anything everyone should practise goes in the shared slots. The same item may serve several
versions. Keep version workloads close; if they differ, say by how much and why. Which student
gets which version is the teacher's record, outside the repository.

## Reuse

Read `reuse_policy` from `homework-defaults.yaml` (default `practice`):

- `never` — every slot is `fresh`.
- `practice` — reuse only when `purpose: practice`; graded and diagnostic homework get fresh items.
- `always` — reuse allowed for any purpose; the teacher is on the hook for the trade-off.

Both reuse and adaptation count as reuse, and are refused when the policy forbids them.

**Declared and actual use are different facts.** An item with `homework` in its `usage` is
eligible; only a homework file listing it proves it was assigned. An entry-quiz item is one with
`in-class-quiz` in its `usage`. Prefer items of homework approved as built (`classkit status`); an
item no built homework or unit uses may be left over from an abandoned run — say so if you
propose it.

### The teacher pointing at items

During review the teacher can point at items in the bank in three ways — recognize each from the
phrasing:

- **Direct reuse** — "use the browser-cache item", "reuse `U03-I05`", "slot 2 = the workload one"
  → `decision: reuse, from: U03-I05`. The item's `unit` must be a declared unit; if it is not,
  don't propose it — say so and offer the closest in-scope item.
- **Adaptation** — "adapt the browser-cache one for a DB index", "like `U03-I05` but harder" →
  `decision: adapt, from: U03-I05`. Name the keep/change axes explicitly in the `intent`; if the
  teacher is ambiguous, ask before recording. Typically kept: format, item class, difficulty,
  misconception target, rubric shape. Typically changed: the Guiding Question, the scenario, one
  difficulty step, one Bloom level. Adaptation makes a new item; the original never changes.
- **Search and browse** — "show me candidates for slot 2", "any items on chaining I could reuse"
  → a short table, about 8 rows at most: id, a one-line stem summary, class, difficulty, minutes,
  the Guiding Question's prompt (not its id alone). Least recently used first, then closest to
  the plan's other Guiding Questions. Filters, each optional: unit, Guiding Questions, format,
  item class, difficulty, Bloom, used in a homework or not, text in the stem. An empty result is
  said plainly — never fabricate a match; suggest loosening the tightest filter or a `fresh`
  slot. "Last year's" has no semester tag in the course: the closest proxy is items a homework
  already used, least recently used first — say that it is a proxy.

## The brief — what the teacher reads

The plan in the file is a slot table. What the teacher reads is a **prose brief**. Never lead
with the table.

One paragraph per item, in the teacher's language:

- **Reference existing items by what they are about**, not their id. "The browser-cache item I
  used earlier" — not `U03-I05`.
- **Name Bloom levels only when they distinguish the item's role**, in plain words. "Quick concept
  check" is enough; "medium/understand" is jargon.
- **Show time and count.** Total minutes; how many items. That's it for numbers.
- **Show the due date and the focus notes**, when there are any. The teacher approves both with
  the rest of the plan.
- **For targeted versions**, every version: its targets in plain words, which items cover each,
  and its approximate minutes beside the others. On **graded** homework, name any difference in
  workload or targets between versions — the teacher must approve it explicitly.
- **End with the real decisions the teacher has to make**, one sentence each. If there are none,
  end with "Approve, revise, or say more?"

**Never show a Guiding Question by its id alone.** Always the prompt:

> `U03-S02-G3`: *Given a workload with specific read/write patterns and size, which hash-table
> variant is better and why?*

The id is for validation; the prompt is for the teacher.

**Surface a genuine trade-off in one sentence** — an adaptation that shifts the Guiding Question,
a quiz signal below the threshold, a budget conflict. "The browser-cache item I'm adapting
exercises a slightly different angle than your quiz showed. Push the rubric to force the
workload-property reasoning, or leave it more general?" — not four paragraphs of id analysis.

### The table — only when asked

Show it when the teacher asks ("show me the details", "the slot breakdown"), when they edit a slot
by number (show that row), or when `classkit validate` reports a finding about a slot. Columns:
`#`, class, format, difficulty, Bloom, minutes, tools, decision — and version, when the homework
has versions. Homework items may be any format.

## Revising — change what was asked, leave the rest

Re-read the file first: the teacher may have edited it by hand, and those edits are theirs. Change
the slots the teacher named; keep the others, their numbers, and the `approved` block exactly as
they are. A change to a homework already built (its slots have an `item`) changes what the build
made: say which items it affects.
