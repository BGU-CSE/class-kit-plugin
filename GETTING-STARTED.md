# Getting started — for teachers

How you turn your existing course into a flipped one, with the **Class Kit** plugin for Claude Code.
You supply materials and settings; Claude does the design work; the validator catches what went
wrong.

You need:

- **Claude Code** — the Code tab of the Claude desktop app, or the `claude` command;
- **Python 3.10 or later** ([python.org](https://www.python.org/downloads/); on Windows, tick
  "Add python.exe to PATH" in the installer);
- **on Windows, [Git for Windows](https://git-scm.com/download/win)**, which brings the Git Bash the
  plugin's scripts run in.

> **The plugin is still being built.** Starting a course (`/class-kit:new-course`), the materials
> (`/class-kit:ingest`), the syllabus (`/class-kit:plan-syllabus`, `/class-kit:review-syllabus`) and
> planning units (`/class-kit:plan-units N…`) work today, with approvals and `classkit status`. The
> commands that build a unit (step 6) run, but are being rebuilt one step at a time —
> `dev/ROADMAP.md`'s ledger is the authoritative list of what is actually built, and `CHANGELOG.md`
> says what each release changed. Expect this document to change as they land.

---

## You work in the chat

**You never need the terminal.** Once the course folder is open in Claude Code, everything below is
something you **ask the chat** for, in your own words — "create the course tree for 202-1-2051,
Introduction to Data Structures", "check the course", "where does the course stand?", "approve the
syllabus", "add this video link". The chat runs the `classkit` command for you, reads its output,
and tells you what matters. The commands are shown in this guide so you know what is happening, not
because you must type them.

- Checks that only read (`classkit validate`, `status`, `doctor`) run without asking you.
- Anything that writes asks you to confirm first.
- The chat reports every alert and error it sees. If you want the raw output, ask for it.

The steps outside the chat are installing the plugin, once per computer, and making the folder your
course lives in.

## 1. Install the plugin — once per computer

In the **Claude desktop app**, add a marketplace with the address **`BGU-CSE/class-kit-plugin`** (or
`https://github.com/BGU-CSE/class-kit-plugin`) and install **Class Kit** from it. In a terminal, the
same:

```bash
claude plugin marketplace add BGU-CSE/class-kit-plugin
claude plugin install class-kit@class-kit
```

It is installed for the whole computer: every course you open has it, and nothing of the plugin is
copied into your courses. The first session after installing takes a minute longer — the plugin sets
up its Python tooling, once. If Python is missing, Claude says so at the start of the session, and
how to install it.

## 2. Make your course folder

Your course lives in **its own folder**. Best, make it a **private git repository**: it keeps every
version of your work, and lets a colleague or TA work on the same course. Create an empty private
repository on GitHub, clone it to your computer (GitHub Desktop does this with a click), and open
that folder in Claude Code. A plain empty folder works too; you can make it a repository later.

Keep it **private** — it will hold your assessment material.

## 3. Create the course tree

In that folder, run **`/class-kit:new-course`**. It asks, in one message, for the title, the course
code, the institution, the instructors and the number of weeks — anything not known yet can stay
empty — and then runs:

```bash
classkit scaffold course --code "202-1-2051" --title "Introduction to Data Structures"
```

When it is done, **start a new session** in the same folder, or type `/clear`. The course rules
Claude follows load when a session starts in a folder that holds a course, so the session that
created it does not have them yet.

That creates `course/`: the settings in `course.yaml`, an empty `units/`, a place for your existing
material, and **`course/syllabus/syllabus.md`** — the course's top layer. The syllabus holds the
course goal and its **Course Outcomes** (`CO1`, `CO2`, …): what a student who passes can do. Those
outcomes are the roof of everything below them — each unit's objectives roll up to them, so the
validator can ask whether your units together deliver what the course promised.

It also starts **`course/LOG.md`, the course log**: what changed in the course and *why* — the part
git's history does not record. The commands add an entry at each step you approve, and the agents
read the recent entries before they start work, so next year's revision knows what this year's
decided. Add your own entries by hand whenever something worth remembering happens ("taught U03 —
students found S02 too long"), or ask the chat to log it ("log that I taught U03 and students found
S02 too long").

The syllabus is **where your course descriptor lives** — everything the university's form asks for,
so you never keep syllabus information anywhere else. Its **front matter** holds what tools and
agents use: the goal, the outcomes, the **unit map** (the whole semester's units, in order), workload,
prerequisites, reading and grading. Its **body** holds what only people read — the catalogue
description, teaching methods, level, policies (including an AI-use policy), office hours — in your
institution's order. Only the goal and the outcomes are required: it is best effort, not a form.

It is scaffolded with placeholders and a default skeleton of sections; `/class-kit:plan-syllabus` (step 6)
drafts it from your materials, and it is yours to edit by hand at any time. Its `workload` block is
left out until credits are settled; `classkit validate` warns until you fill it in. That is a
reminder, not a failure.

Scaffolding never overwrites. Re-run it whenever you want the pieces you are missing — everything
you have already written is left exactly as it is.

It also writes **`.claude/settings.json`** beside `course/` — Claude Code's settings for this
folder: the read-only checks (`classkit validate`, `status`, `doctor`) run without asking you; on
Windows, commands run in Git Bash rather than PowerShell; and the plugin is named, so that a
colleague who opens the course is offered it. Commit it with the course.

## 4. Add your existing material

Drop whatever you already have into **`course/materials/source/`** — slides, PDFs, the syllabus,
past exams, reading lists, lecture notes. Any format. Nothing is required, and more is better:
the agents read this to work out what your course actually covers instead of inventing a
generic version of it.

It doesn't need to be organized — one folder of everything is fine. Identical copies are merged
automatically; a deck and its PDF export simply stay two materials (both can be cited; agents
prefer the deck). For videos and web pages, list them in
`course/materials/source/links.md`, one per line with an optional note, or run:

```bash
classkit add-url "https://www.youtube.com/watch?v=…" --note "heaps explained, 12 min"
```

PowerPoint, PDF, Word, Markdown and plain text are read out of the box. OpenDocument, RTF, HTML
and EPUB need [pandoc](https://pandoc.org) installed; old `.ppt`/`.doc` need LibreOffice. Anything
else — and a scanned PDF with no text, or a video file — is recorded and listed, never silently
dropped; export it to PDF if you want it read.

Then run **`/class-kit:ingest`** in Claude Code. It first shows you a **pre-flight report** — how many files of
each kind, slides and pages, links, what changed since last time, what it can't read, roughly how
long it will take —
and waits for your go-ahead. It then turns everything into a readable, citable copy in
`course/materials/ingested/`, one file per source with every slide and page marked, and lists them in
`course/materials/manifest.yaml` under a stable id (`M0007`). An agent then proposes what each one is
(slides, exam, textbook, …, and which units it serves) — **you see and correct that before it is
recorded** — mentions links inside your materials that look like course resources (only links
you list in `links.md` become materials), and reports what your course actually
covers and where it is thin — saying first which units your materials reach, and "no material
yet" for the rest. Once you have read it, it is saved to `course/materials/coverage.md` (a later run
asks before replacing it, so notes you add there are not lost), and `/class-kit:plan-syllabus` reads it. Each
step you approve is recorded in the course log.

What that buys you: an answer reference can point at **`M0007#slide-18`**, and `classkit validate`
reports an error if that slide does not exist — a made-up "slide 18" of a 12-slide deck is caught
before it reaches a student. (It cannot tell whether the answer is *on* slide 18; that is still a
human's or the reviewing agent's call.)

- **Your originals are never touched.** Nothing in `materials/source/` is modified, moved or deleted
  — the one exception is `classkit add-url`, which appends a line to `links.md`.
- **Files that must not be committed go in `materials/source/private/`** — a published textbook's
  PDF, a publisher's slides, a solutions manual. `course/.gitignore` (scaffolded) keeps that folder
  out of git. For each file there, ingest commits only an **index** in `ingested/` — its pages or
  slides with their labels (printed page numbers, the book's sections from its bookmarks, slide
  titles), no body text — so a citation like `M0005#page-63` is checked on every copy of the
  repo. The full text goes to `materials/private-text/`, also kept out of git, on your machine only;
  the agents read it there. A TA's clone without the PDF can still cite and validate the book; to
  let agents read it there, copy the PDF into their `private/` and run `/class-kit:ingest`.
  - **Put only that in `private/`** — what must not be in the repo. Your own slides, notes and old
    syllabi belong outside it: a TA's clone sees only an index of what is in `private/`.
  - Everything **outside** `private/` is committed — the source *and* its full extracted text.
    Anything pushed to GitHub stays in the repository's history even if deleted later. If a book is
    already committed, moving it into `private/` stops future commits but not the history;
    `classkit validate` warns about it (`private_material_committed`), and cleaning history is up
    to you.
  - A private file missing from a machine is "not on this machine", never "removed" — a TA's
    clone and a lost file look the same. If it is gone for good: `classkit material remove M0005`.
  - Private is **where the file is**; who may *see* it is separate. Mark material students must
    never be pointed at — a solutions manual, a past exam — as **`audience: instructor`** (the
    `/class-kit:ingest` agent proposes it, you confirm; or `classkit material set M0012 --audience
    instructor`). A study path citing it then raises an alert; your in-class plan may cite it.
    A textbook is private but `student`.
- **`classkit doctor`** checks this machine's copy: that the `.gitignore` is in effect, which
  private files are here and whether their full text is current, and that the tools are installed.
  Each line that needs action says what to run. `/class-kit:ingest` runs it first.
- **Reorganize freely.** A renamed or moved file keeps its id, so nothing that cites it breaks.
- **Fix a bad extraction by hand** in `ingested/`. A later ingest notices your edit and asks before
  replacing it — it shows what replacing would change, slide by slide or page by page, and you
  choose to keep your edit or take a fresh extraction. If you corrected something by hand that a
  newer version of the framework now extracts properly (Word text boxes, equations), choose the
  fresh extraction once; until then that file stays "edited by hand".
- **Thin extraction is reported.** The summary lists slides and pages with no text and documents
  that came out far smaller than their source — so a deck of pictures is not mistaken for a thin
  week.
- **Add material any time** and run `/class-kit:ingest` again — only what's new or changed is processed, and
  an interrupted run picks up where it stopped. Until you do, `classkit validate` warns that some
  material is not ingested yet.
- **A deleted file** stays in the manifest, marked removed, so anything still citing it is reported.
- **Running `classkit ingest` yourself** is fine; it adds an entry to the course log saying what
  changed (`--why "…"` to say why).
- **Citing a book:** `M0003#page-63` is the 63rd page of the PDF, which may not be the page printed
  "63". So a book citation also says, in its note, the section, the exercise or question number, and
  the printed page — `CLRS §6.2, Exercise 6.2-3 (printed p. 45)`.

If your textbook isn't a file, record it in `course/course.yaml` under `textbooks:` — study
paths and answer references cite it by key.

## 5. Set your settings

The course's *aim* — its goal, outcomes, unit map, prerequisites, workload and grading — lives in
`course/syllabus/syllabus.md`, which `/class-kit:plan-syllabus` drafts and you edit. Everything *tunable* is in
**`course/course.yaml`**:

| Setting | What it controls |
|---|---|
| `units` | How many weeks (12 or 13) |
| `methodology` | The study-session design. Default `question-driven-25` |
| `textbooks` | Keys that study paths and answers cite, e.g. `CLRS` |
| `in_class.max_unmapped_minutes` | How much of the class hour may be spent on activities that build on no guiding question — exam logistics, a news item. Default 10 of 50. *Not built yet* |
| `time_constants` | Assumed reading, watching and exercise rates, used to *propose* study times |

Two of these are worth understanding rather than just setting.

**`time_constants` is advisory.** It does not decide whether a session fits its budget. The
session's time is the sum of a per-question `est_minutes` that **you approve** — the constants only
help the agents propose a sensible number in the first place, and help the reviewing agent notice
one that looks wrong. The shipped defaults are placeholders; adjust them to your students.

**`in_class.max_unmapped_minutes` is the guardrail on the class hour.** Most activities should build
on the week's guiding questions. A few legitimately do not, and those are fine — but if they add up
past this cap, the validator warns you, because an hour made of them is a lecture again. Raise it if your
teaching genuinely needs more; set it to the full hour to switch the guardrail off entirely. It is
your course.

To use a different pedagogy entirely, save a methodology file in your course, as
`course/methodologies/<name>.yaml`, and name it here: the course's own file is used before the
plugin's, and `classkit status` says which one is in use. The rest of the framework keeps working.

## 6. Let Claude build the course

Open Claude Code in your course folder and run these in order:

| Command | What it does |
|---|---|
| `/class-kit:ingest` | Reads `materials/source/` and `links.md` — pre-flight, convert, classify — and reports what your course covers |
| `/class-kit:plan-syllabus` | The syllabus: evidence and questions → a full draft → revisions with you → your approval |
| `/class-kit:review-syllabus` | Optional: an independent critic reads the syllabus — outcomes that are topic labels, claims nothing supports |
| `/class-kit:plan-units 1 2` | The units named, a few at a time as their material arrives: each one's objectives (each serving a Course Outcome), prerequisites, and what students find hard — drafted, revised with you, approved as *planned* |
| `/class-kit:build-unit 3` | The main event: the week's study sessions with their guiding questions, the entry quiz, then the in-class hour built on both. *Being rebuilt one part at a time* |
| `/class-kit:review-unit 3` | An adversarial critic — checks the hour genuinely depends on the prework |
| `/class-kit:write-items 3` | More assessment items for the entry quiz |

*Homework, programming assignments and exams (`/class-kit:write-items` in its full form) and the class Gem
(`/class-kit:build-gem`) are later phases. They are not built.*

### The syllabus first — and approving it

Establish the syllabus before any unit: it is often what you upload to the university, and the units
build on it. `/class-kit:plan-syllabus` drafts it **best effort** from the evidence you ingested — an old
syllabus above all, the book's table of contents, your decks — and **asks** what the evidence cannot
answer (credits, grading, office hours) rather than inventing it. What nobody knows yet appears in
the body as **TBD**. You revise it in conversation or by hand, as many rounds as you like.

When it is good enough to build on, **approve** it — at the command's last step, by saying "approve
the syllabus", or by hand. Approval is recorded in the file itself (`approved: {date, hash}`), by
`classkit approve syllabus`. Editing afterwards is normal: nothing un-approves, and `classkit status`
says "approved 5 Oct — edited since" until you approve again. Approved does not mean perfect — unit
work builds on what you approved, and the validator reports any inconsistency; nothing waits on it.

**`classkit status`** shows where the course stands — the syllabus, the unit map with each unit's
state, the materials. Every command shows it first.

### Then the units — a few at a time

You do not plan the whole semester's units at once. When a unit's material is in, `/class-kit:plan-units 3 4`
plans those units: for each, a short summary, the earlier units it needs, its 2–4 objectives (the
number comes from your methodology) — each naming the Course Outcome it serves — and, if you know
them, the **difficulties** students meet in it. If you do not know them yet (a course you are
flipping for the first time), say so: planning goes on, and you can add them after teaching the week.
The agent may *propose* classic difficulties of a well-known subject; one is recorded only if you
accept it, and stays marked `proposed` so later agents know it is a guess.

Approve each unit when its plan is good enough ("approve unit 3"); `classkit approve unit 3 --stage planned` records
it in `unit.md` as **planned** (the stage is always named, so a second "approve" can never mark an
unplanned unit as built — the chat picks it from where the unit stands, and asks if unsure). Later, approving the finished unit at the end of `/class-kit:build-unit`
records it as **built** — and editing any part of it afterwards shows "built — edited since".
In `classkit status` each unit reads *not started* (on the map, nothing yet), *drafted, not
approved*, *planned* or *built*. Nothing is blocked by these states; they tell you where you are.
(Before version 0.3.0, *built* was called *designed*; a unit approved then still counts.)

To upload the syllabus to the university, copy from `syllabus.md` for now; a formatted document is
a later export.

### How the commands behave

Hold them to this — it is how they are specified to work:

- **Stepwise, with your approval.** A command tells you what it is about to do, produces that one
  step, shows you the result, and waits. It does not design a whole unit and hand you the finished
  article. A correction at a checkpoint is applied before it moves on.
- **Never overwrite without asking.** If something is already written, you are shown what is there
  and asked first. This one is enforced by the tooling, not merely by instruction — losing work you
  authored is the one failure the framework must never have.
- **Revise rather than regenerate.** Where output already exists, the default is to change the part
  you asked about and leave everything else alone.

### What's actually happening

You only ever type commands. Each one is a short script that pulls in **agents** — specialists with
their own instructions, working in their own context.

`/class-kit:build-unit 3` runs three of them in order: the **study-session-designer** writes the week's
guiding questions, their answer references and their study times; the **assessment-writer** then
produces the entry quiz; and the **lesson-planner** builds the hour last, because it needs both the
questions *and* the real quiz items it will refer to.

`/class-kit:review-unit 3` runs the **course-critic**, which is deliberately a *different* agent from the ones
that did the work. An agent reviewing its own output is systematically generous. It is also the only
thing that can judge whether your study-time estimates are honest — the validator can check that
they add up, not that they are true.

You don't invoke agents directly, though you can — ask Claude Code to "use the topic-researcher to
find videos for unit 4" and it will.

Then, always:

```bash
classkit validate
```

Work **one unit at a time**. Review unit 1 properly before generating twelve more — the agents
learn your subject from what's already in the repo, so a good unit 1 makes unit 2 better, and a
bad unit 1 propagates.

## Updating the plugin

Once a day, at the start of a session, the plugin checks whether a newer version has been released.
When there is one, Claude tells you and asks whether to update — it updates only if you say yes —
and then asks you to close Claude Code and open it again, so the new version loads. What changed is
in `CHANGELOG.md`, with anything you need to do after updating.

An update replaces the plugin, never anything in your course. What you change in your course —
`course.yaml`, your own methodology, accepted exceptions, everything under `course/` — stays yours.

## A colleague or TA on the same course

They clone your course repository and open the folder in Claude Code. If the plugin is not installed
on their computer, the course's settings bring it in once they trust the folder; or they install it
first (step 1). If it came in with the course, the first session does not have the course rules yet:
type `/clear` or start a new session.

Every entry in the course log names the plugin version that wrote it. If one computer runs an older
version than one that has already worked on the course, Claude says so at the start of the session
and offers to update — before anything is changed.

## What the validator tells you

**You are the authority.** The validator catches what the agents get wrong and tells you what it
sees; it does not overrule you. It reports three kinds of finding:

- **Errors — broken data.** A reference to something that doesn't exist: a guiding question an
  activity names but nobody wrote, a quiz item that isn't there, a study path pointing at
  `M0007#slide-18` of a 12-slide deck. These are almost never intentional, and the agents can't work correctly over them.
- **Alerts — high priority, shown first.** Coverage: a Course Outcome no unit delivers, an objective
  no guiding question addresses, an objective that rolls up to no outcome, a missing syllabus. Often
  a temporary state while you build — but worth looking at.
- **Warnings — departures from good practice.** A session over its time budget, a guiding question
  with no recorded answer, a class hour drifting off the home study, a week with no class meeting.
  Sometimes that is exactly what you meant.

When a departure is deliberate, mark it so it stops nagging — in the front matter of the file the
finding is reported against. A week with no class meeting is reported against the unit's `unit.md`:

```yaml
accepted:
  - rule: in_class_missing
    reason: "holiday week — no class meeting"
```

— or change a rule for the whole course under `rules:` in `course.yaml` (e.g.
`session_count: off`). Agents never do this on their own; only you do. The rule's name is the one
`classkit validate` prints in brackets; a name it does not recognise gets a warning, because a
mistyped exception silently does nothing. A missing `reason` is allowed but also gets a warning —
the reason is what explains the exception to you, or a colleague, next year. Accepted exceptions are still counted at the end of the
report, so they never disappear from view.

Some checks only run once your unit map is complete — a half-built course is a normal state, and
the validator says when it has skipped something for that reason.

## What you still have to do yourself

The agents draft; they don't know your students. Expect to rewrite guiding questions that are
too easy, cut a study session that's overstuffed, and replace distractors that don't match the
misconceptions you actually see in office hours. The framework's job is to make that editing
cheap and to stop structural mistakes reaching your students.
