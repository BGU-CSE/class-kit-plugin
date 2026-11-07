# Homework

Homework in Class Kit — designed as a separate module of the class-framework repository, and
brought into the plugin in its own form (HW-D35, 2026-11-07). These are its development documents;
what a teacher receives is in `plugin/`.

## What homework adds

- A homework as a first-class content type: one file, `course/assessments/homework/HW0N.md`, with
  its settings, its plan, the items it was built from and the teacher's approval — kept as a unit is
- A three-axis item model: `format` (answer shape), `usage` (context), `item_class` (the kind of
  homework item: its typical time, tools, Bloom range and how it is checked) — the third axis is new
- Two commands, as for units: `/class-kit:plan-homework` (the interview, the plan, approved as
  *planned*) and `/class-kit:build-homework` (the items, an independent critic, a solver that attempts
  each item, validation, approved as *built*); and `/class-kit:new-item-class`
- Item checking by class (persona attempts, running code, skip, custom), and time estimates that
  depend on the class (HW-D06)
- The student and teacher Word or PDF documents, made when the teacher asks, with a leak check
- Tools as course-declared strings, and the hand-off from `/class-kit:write-items N homework`

Thirty-five decisions (HW-D01…HW-D35) and eight open questions (HW-Q01…HW-Q08) record the design.

## Where things are

```
dev/homework/                  the documents (never shipped)
├── README.md                  this file
├── HOMEWORK-SPEC.md           the specification (source of truth for what homework is)
├── ROADMAP.md                 the plan and the ledger (authoritative for what exists)
├── PLUGIN-PORT.md             how homework came into the plugin, and what is left
└── _devlog/                   the design history: brief, decisions, progress, open
                               questions, the implementer's notes

plugin/                        what a teacher receives — HOMEWORK-SPEC §11 lists the files
tests/test_homework.py         every rule, scaffolding, approval and status
```

**One item schema** (HW-D01): homework adds optional fields to the shared item schema, so an item
can serve a quiz, a homework and an exam by its `usage`, without copies. What homework requires is
checked by rules that judge only homework items and classes (HW-D10).

## Status

- Design: complete and reviewed; HW-D35 adapted it to the plugin.
- In the plugin: the commands, agents, skills, schemas and templates; the Python — loading, the 21
  rules, `classkit scaffold homework`, `classkit approve homework`, homework in `classkit status`;
  the tests.
- Not yet: **the first real homework** — no homework agent has run on a real course. Deferred:
  `classkit bank` and item-bank ingest (HW-D35).
