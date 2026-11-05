---
name: course-reference
description: The long reference for a course built with Class Kit — the commands and what each does, the materials rules (sources, links, private material, locators, annotations, roles, the coverage report), approvals, and how the teacher records an exception. Load it before ingesting or citing materials, before running any /class-kit command, and whenever the teacher asks how the course's rules work. The always-on rules are injected at session start; this is the detail behind them.
---

# Course reference

The detail behind the always-on rules (`rules/core.md`, injected when a session starts in a course
repository). Same vocabulary, same IDs.

## The commands

| Command | What it does |
|---|---|
| `/class-kit:new-course` | Create the course in this folder, then start a new session so the course rules load |
| `/class-kit:ingest` | Read your existing materials and report what the course actually covers |
| `/class-kit:plan-syllabus` | The syllabus: course goal, Course Outcomes, the unit map, workload, grading, the descriptor — drafted best effort, revised with you, approved |
| `/class-kit:review-syllabus` | Optional: an independent agent reviews the syllabus |
| `/class-kit:plan-units N…` | The units named, as their material arrives: objectives (each serving a Course Outcome), prerequisites, difficulties — drafted, revised with you, approved as *planned* |
| `/class-kit:build-unit N` | One unit end to end — study sessions, the in-class hour, the entry quiz |
| `/class-kit:review-unit N` | An independent agent reviews what it did not write |

**Every command starts with `classkit status`** — the syllabus (approved / approved, edited since /
draft), the unit map with each unit's state (not started / drafted / planned / built, or edited
since), the materials. The teacher approves the syllabus at `/class-kit:plan-syllabus`'s last step, in
conversation, or by hand; `classkit approve syllabus` records it in the file (date and hash) and
logs it. A unit is approved the same way — `classkit approve unit N --stage planned` at the end of
`/class-kit:plan-units`, `--stage built` once the whole unit is built — recorded in its `unit.md`.
**Agents never approve and never write the `approved` block.** An unapproved syllabus — or a unit
not yet planned — makes a command ask whether to go on, not refuse.

## Materials

- **`course/materials/source/`** is the teacher's: any files, any structure, duplicates included.
  **Nothing modifies, moves or deletes anything in it** — no agent, no tool — with one exception:
  `classkit add-url` appends a line to `source/links.md`.
- **`source/links.md`** lists the course's links, one per line with an optional ` — note`. Add one
  with `classkit add-url URL --note "…"`.
- **`source/private/`** holds only what must not be in the repo — a published book, a solutions
  manual. The teacher's own slides belong outside it: a TA's clone sees only an index of what is in
  `private/`.
- **`course/materials/ingested/`** is derived: `classkit ingest` (run by `/class-kit:ingest`) writes one
  Markdown copy per material, `M0007-heaps.md`, with an anchor per slide (`## Slide 18`), per page
  (`## Page 34`), or the document's own headings. **`materials/manifest.yaml`** lists every
  material. A renamed or moved source keeps its id; a removed one is marked, never forgotten.
- **Cite material by locator** — `M0007#slide-18`. `classkit validate` checks that the material and
  the anchor exist (`material_locator_resolves`, an error), though not that the answer is there.
  A textbook key (`"CLRS ch.6"`) is still allowed for what is not ingested, but cannot be checked.
  A `M0007#slide-18` written in **prose** — a unit's or session's body, `materials/coverage.md` — is
  checked too (`material_locator_in_text`, a warning; not `LOG.md`, not `ingested/`).
- **A book citation also gives the book's own coordinates** in its `note` — section, exercise or
  question number where there is one, and the printed page: `ref: "M0003#page-63"`,
  `note: "CLRS §6.2, Exercise 6.2-3 (printed p. 45)"`. `page-63` is the 63rd page of the PDF, which
  is often not the page printed "63"; a wrong page still validates, so the note is the check.
- The teacher may correct a bad extraction in `ingested/` by hand. A later ingest asks before
  replacing the edit (it exits 3); agents never answer that question for the teacher.
- **Private material** — a published textbook's PDF, a solutions manual: anything that must not be
  committed — goes in **`source/private/`**, which `course/.gitignore` keeps out of git. Its
  committed `ingested/` file is an **index** (`text: index`: every anchor with one-line labels —
  printed page, sections, slide titles — no body text), so its locators validate on every clone. Its
  full text is in **`materials/private-text/`** (gitignored), only on a machine that has the source.
  **Read the full text when it is there; where it is not, the material is index-only here — say so,
  and never present recall of the book as a reading of it.** `classkit doctor` says which.
  A missing private source is "not on this machine", never "removed";
  `classkit material remove ID` removes one, only on the teacher's word. Agents never move a file
  into or out of `private/` — they may suggest it.
- **`audience: instructor`** in the manifest marks material students must never be pointed at — a
  solutions manual, a past exam. Citing it from a study path raises the alert
  `instructor_material_cited`; the in-class plan may cite it. No export will bundle it.
- **Your annotations count.** Highlights and margin comments on a PDF are extracted, page by page,
  as a "Teacher's annotations" block — for a private PDF only in the local full text (the committed
  index just counts them). They are how agents learn what you teach and how deep.
- **`roles`** on a material: `scope` (your decks and annotated notes — they decide what a unit
  teaches and how deep) and/or `reference` (the book — the fuller source). `/class-kit:plan-units` says "book
  only — scope not confirmed" for a unit only the book reaches, and asks whether to wait or plan
  provisionally.
- The classifying agent only reads and **returns** each material's kind, units, audience and roles;
  `/class-kit:ingest` shows them to the teacher and records them (`classkit material apply`). Nobody edits the
  manifest's bookkeeping by hand. Identical copies merge automatically; a deck and its PDF export
  stay two materials and nobody is asked — **cite the deck**. `classkit material merge` is optional,
  only on the teacher's word.
- **Links become materials only from `links.md`** (`classkit add-url`); a link inside a deck is read
  in its ingested text, never harvested.
- **`units`** on a material is a hint: a list, **`all`** for course-wide material (the textbook,
  the course Gem — read it as every unit), or `[]`.
- **`materials/coverage.md`** is the coverage report `/class-kit:ingest` saved after the teacher read it: a
  dated snapshot of what the materials cover, with its scope ("no material yet" for units nothing
  reaches is not "thin"). Read it as input, not as truth; replace it only on the teacher's word.
- To change **part of a file** (one key in `course.yaml`), show `classkit write PATH --diff` first,
  then write with `--overwrite` once the teacher approves.
- Running `classkit ingest` by hand writes a course-log entry saying what changed; add `--why` to
  say why.

## The teacher is the authority

The validator **informs you; it doesn't overrule you.** Only *broken data* — a reference to
something that doesn't exist, a file that can't be read — is an error. Everything else is advice
about good practice: warnings, and **alerts** (high-priority advice, shown first) for coverage —
whether the units deliver the course outcomes. You may depart from any of it.

To make a deliberate exception stop nagging, add it to the front matter of the file the finding
is reported against — here, the unit's `unit.md`:

```yaml
accepted:
  - rule: in_class_missing
    reason: "holiday week — no class meeting"
```

A `reason` is optional but worth writing: it is what explains the exception next year.

To accept an exception for **one item only** — one objective, one guiding question — add its `id`
(`- rule: objective_maps_to_outcome`, `id: U01-O3`); without `id` it covers the whole file.

or change a rule for the whole course in `course.yaml` under `rules:`. **Agents never do either on
their own** — only when you ask — and they never "fix" something you decided.
