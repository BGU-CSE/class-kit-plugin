# Class Kit

A Claude Code plugin for developing and maintaining a university course **with AI agents as working
partners** — versioned in git, structured on disk, authored with specialized agents, and checked by
tooling that catches structural mistakes before students see them.

A general-purpose chatbot can help you write a paragraph, but it cannot work on *your course*: it
has no map of what the course is, what unit 7 contains, or what changing one goal would affect. Give
the course an explicit structure and it becomes something agents can operate on.

Its first purpose is a specific transformation — taking a conventional course of **three weekly
lecture hours across 13 weeks** and turning it into a **flipped course**:

```
COURSE
├── Syllabus — goal, Course Outcomes (CO1, CO2 …), workload, prerequisites
│     Every unit objective rolls up to an outcome, so "do the units together
│     deliver what the course promised?" is a question the tooling can ask.
│
└── UNIT = one week = 150 min
    ├── AT HOME  100 min = 2 × 50        goal: acquisition
    │   └── 4 × Study Session (~25 min)
    │       ├── 3–5 Guiding Questions — each a question the student should be
    │       │     able to answer, carrying:
    │       │       · answer — where the correct answer is found (a textbook
    │       │         section, a slide, a video timestamp). Never the answer
    │       │         itself: course content stays out of the repo.
    │       │       · est_minutes — teacher-approved study time. The session's
    │       │         25 minutes is the sum of these.
    │       └── Study Paths — an optional pool of alternative resources for the
    │             session. Not exhaustive; students may use their own instead.
    └── IN CLASS  50 min                 goal: application, not re-explanation
        └── Activities, opening with the entry quiz — misconception debrief,
            worked examples, small-group work, synthesis
```

The **Guiding Question** is the atomic unit of the whole system. Assessment items and in-class
activities reference question IDs. That is what lets the tooling check the design rather than merely
store it.

## What the tooling checks

A flipped course fails in two predictable ways, and the tooling flags both:

- **The class hour quietly becomes a lecture again.** In-class activities are built on that unit's
  guiding questions; activities that aren't — exam logistics, a current-events hook — are fine, but
  their total time is flagged past a limit, because an hour made of them is a lecture.
- **"Two hours at home" turns out to be fiction.** Each guiding question carries a teacher-approved
  study time, and a session whose questions don't sum to roughly its length is flagged.

Alongside those: every guiding question records where its answer can be found, objectives roll up to
Course Outcomes and are covered by questions, and every reference points at something that exists.

**The teacher is the authority.** Only broken data — a reference to something that doesn't exist —
is an error. Everything pedagogical is advice: warnings, and high-priority *alerts* for coverage. A
teacher can accept any deliberate exception, and it stops nagging. Validation exists because agents
author the content and something has to catch what they get wrong — not to overrule the person
responsible for the course. **Code verifies; agents judge; the teacher decides.**

## Status

**Version 0.3.0. Core is being implemented.** Starting a course, ingesting materials, the syllabus,
planning units, approvals, `classkit status` and `classkit doctor` are built and have been used on a
real course. `/class-kit:build-unit`, `/class-kit:review-unit` and `/class-kit:write-items` run, but
are being rebuilt one step at a time (study sessions, the entry quiz, the class hour). Not built:
homework and exams, the Gem builder, PPTX export, Moodle sync.

`dev/ROADMAP.md` carries the implementation plan and a ledger which is **authoritative for what
actually exists**; `CHANGELOG.md` says what each release changed.

**Teachers start at [GETTING-STARTED.md](GETTING-STARTED.md).** **Developers start at
[CLAUDE.md](CLAUDE.md)**, then [dev/VISION.md](dev/VISION.md) — why the project exists — and
[dev/FRAMEWORK-SPEC.md](dev/FRAMEWORK-SPEC.md), which specifies what the framework must contain. The
rest of this file is a summary.

## Installing

You need Claude Code — the Code tab of the Claude desktop app, or the `claude` command — and Python
3.10 or later. On Windows, also [Git for Windows](https://git-scm.com/download/win), which brings the
Git Bash that the plugin's scripts run in.

Install once per computer. In the Claude desktop app: in any session, **+** in the message box →
**Add plugins** → **Add** → **Add marketplace** → **Add from a repository**, with
`https://github.com/BGU-CSE/class-kit-plugin`; then install **Class Kit** from the list. In a
terminal, the same:

```bash
claude plugin marketplace add BGU-CSE/class-kit-plugin
claude plugin install class-kit@class-kit
```

The first session after installing takes a minute longer: the plugin sets up its Python tooling,
once.

## Starting a course

A course lives in **its own folder** — best, its own private git repository — never in this one.
Open an empty folder in Claude Code and run **`/class-kit:new-course`**. It asks for the title and
a few details, creates the course skeleton in `course/`, and tells you to start a new session so the
course rules load. Then put your existing materials in `course/materials/source/` and run
`/class-kit:ingest`.

## Updating

Once a day, at the start of a session, the plugin checks whether a newer version has been released.
When there is one, Claude tells you and asks whether to update; it updates only if you say yes.
`CHANGELOG.md` says what changed, and what to do after updating, if anything.

Every entry in a course's log names the plugin version that wrote it. If a computer with an older
version opens a course that a newer one has worked on, Claude says so first and offers to update.

## Who does the work

The design work is done by **agents running in the teacher's own Claude Code**, inside their course
folder. The tooling exists to give those agents a target format and to catch them when they get it
wrong.

| Agent | Responsible for |
|---|---|
| `material-classifier` | What your existing materials are, which units they serve, who may see them, and what the course covers |
| `syllabus-designer` | The syllabus: course goal, Course Outcomes, the unit map, workload, grading, and the descriptor the university asks for — best effort, asking rather than inventing |
| `curriculum-architect` | The plan of the units named — objectives (each serving a Course Outcome), prerequisites, difficulties — from each unit's own material, against the approved syllabus |
| `study-session-designer` | Home study: guiding questions, their answers and study times |
| `assessment-writer` | Items with diagnostic distractors and real rubrics |
| `lesson-planner` | The 50-minute meeting, built from activities |
| `topic-researcher` | Finding **real**, verified study resources |
| `course-critic` | Adversarial review of what the validator can't see |
| `gem-builder` | The class Gem bundle — *later phase* |

Teacher-facing commands: `/class-kit:new-course`, `/class-kit:ingest`, `/class-kit:plan-syllabus`,
`/class-kit:review-syllabus`, `/class-kit:plan-units N…`, `/class-kit:build-unit N`,
`/class-kit:review-unit N`, `/class-kit:write-items N`. (`/class-kit:build-gem N` is a later phase.)
They read plan, build, review.

Commands are **stepwise**: each announces a step, produces it, shows you the result and waits for
your approval before the next. Nothing overwrites work you authored without asking you first — that
one is enforced in code, not by instruction.

Shared craft lives in skills — `writing-a-syllabus`, `planning-units`, `writing-guiding-questions`,
`estimating-study-time` — so the designer, the chat revising with you, and the critic apply the same
standard. Each agent starts with its skills loaded.

## The `classkit` command

The plugin puts `classkit` on the path of Claude's shell. You rarely type it: you ask the chat, and
the chat runs it.

| Command | What it does |
|---|---|
| `classkit scaffold course` | Create the course tree, including the syllabus and the course folder's Claude Code settings |
| `classkit scaffold unit N` | Create a unit with its study sessions and lesson plan |
| `classkit scaffold session U05 5` | Add one more study session to a unit |
| `classkit scaffold item U05` | Add an assessment item |
| `classkit validate` | Check the course against its methodology and schemas |
| `classkit write` | The write path agents use — refuses to replace existing content without explicit confirmation; `--diff` shows exactly what a replacement would change |
| `classkit log` | Append an entry to the course log, `LOG.md` — what changed and why |
| `classkit ingest` | Convert new or changed materials into citable Markdown (`--preflight`: report only) |
| `classkit add-url URL` | Add a link to `materials/source/links.md` |
| `classkit material` | Record materials' kinds, units and audience (`apply`, a batch; `set`, one); optionally merge two materials the teacher says are one; `remove` a private material |
| `classkit doctor` | Check this machine's copy of the course — private files present or stale, the `.gitignore`, dependencies, the plugin's version; each problem with its fix |
| `classkit status` | Where the course stands — the syllabus (approved, edited since, draft), the unit map with each unit's state (not started, drafted, planned, built, edited since), the materials, the methodology in use. Every command shows it first |
| `classkit approve syllabus` | Record the teacher's approval in the syllabus itself (date and hash) and log it; `--diff` shows the change first |
| `classkit approve unit N` | Record a unit's approval in its `unit.md` — `--stage planned` (its plan) or `built` (the whole unit: sessions, class hour, entry quiz) — and log it |

Scaffolding **never overwrites**. Re-run it any time — you get whatever is missing and keep
everything you wrote. Skipped files are reported.

## Layout

```
.claude-plugin/marketplace.json   the marketplace: it lists the plugin at ./plugin
plugin/                    everything a teacher installs
  commands/                /class-kit:new-course, ingest, plan-syllabus, plan-units, build-unit …
  agents/                  the agents that do the design work
  skills/                  shared craft: the syllabus, planning units, guiding questions, study time
  rules/core.md            the rules Claude follows in a course, loaded at the start of a session
  hooks/                   session start: sets up the Python tooling, loads the rules, checks the version
  bin/classkit             the classkit command
  schemas/                 JSON Schema for every content type — the contract
  methodologies/           pluggable study-session designs; question-driven-25 is the default
  defaults/                advisory time constants, used to propose study-time estimates
  templates/               what scaffold copies into a course
  src/classkit/            the tooling
tests/                     scaffold → validate round-trip, the write path, ingest, the plugin's scripts
dev/                       framework-development docs (vision, spec, roadmap, decisions, logs);
                           not a teacher's concern, and not installed
```

There is deliberately **no `course/` directory here**. Course content lives only in course
folders, created by `/class-kit:new-course`. That is what keeps plugin updates and teacher content
from colliding: an update replaces the plugin, never anything in your course.

## Methodologies

`question-driven-25` — four 25-minute sessions per unit, 3–5 guiding questions each — is one
implementation of a contract, not a fixed rule. A teacher can save a different methodology in their
course, as `course/methodologies/<name>.yaml`, and select it in `course.yaml`; the course's own file
is used before the plugin's. Downstream tooling consumes the *output* (`goals[]`), never the
methodology that produced it, so the rest of the framework keeps working.

No tool or agent may hardcode "4 sessions", "25 minutes", or "3–5 questions". Those are read
from the methodology file.

## Developing

Work lands in the **`dev`** branch: open a pull request into `dev`, from a branch or a fork — GitHub
proposes `main`, so change the base. `main` takes only releases. `CLAUDE.md` is the developers'
guide; `pip install -e ".[dev]"`, then `pytest` and `claude plugin validate --strict plugin`.

## License

MIT. See [LICENSE](LICENSE).
