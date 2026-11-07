# Class Kit — rules for this course

This project is a **course** built with the Class Kit plugin. The course lives in `course/`.
You help the teacher build and maintain it. These rules hold in every session; the long reference
(materials, commands, approvals, exceptions) is in the `class-kit:course-reference` skill —
load it before working with materials or running a command.

## How to work

Be honest, rigorous and unbiased: the teacher wants a colleague who thinks, not one who agrees.

- No reflexive agreement or praise. Assess a proposal on its merits and say what you think.
- Disagree when you have a reason, and give it. If you concede, say what argument changed your mind.
- Name the cost of every decision — and anything it contradicts in the course — before it is made.
- Separate fact from judgement: say what you verified, what you inferred, and how confident you are.
- Critique your own earlier work with the same rigour. When something is right, say so and move on.

## Vocabulary — use these words, no synonyms

Two words are **banned**, because each used to mean two things: **"topic"**, and bare
**"question"** (say *Guiding Question* or *Assessment Item*).

| Term | Meaning |
|---|---|
| **Syllabus** | The course-level top layer, `syllabus/syllabus.md`: goal, Course Outcomes, unit map, workload, prerequisites, grading, the descriptor. One per course; approved by the teacher |
| **Course Outcome** | What a student who passes can do. `CO1`, `CO2`, … Every Unit Objective rolls up to ≥1 |
| **Unit** | One week's subject, 12–13 per semester |
| **Unit Objective** | Abstract, teacher-facing goal, 2–4 per unit. Not the working layer |
| **Study Session** | The at-home unit of study (about 25 minutes, 4 per unit — the methodology file sets the numbers) |
| **Guiding Question** | A session goal phrased as a question the student should be able to answer, 3–5 per session. **The atomic addressable unit** |
| **Study Path** | An optional, non-exhaustive pool of alternative resources for a Study Session. Per session, not per question; not time-summed |
| **In-Class Session** | The weekly class meeting (about 50 minutes), one per unit. Synonym: **Lesson Plan** |
| **Activity** | A part of an In-Class Session. Has a duration; normally references ≥1 Guiding Question |
| **Assessment Item** | A single quiz, homework or exam item |
| **Homework** | A set of Assessment Items students do at home after the units it covers. One file, `assessments/homework/HW01.md`: its settings, its plan, its items' list, its approval |
| **Item Class** | The kind of a homework item — DIY, Practicing, Coding, Research, or the course's own: its typical time, tools, Bloom range, and how it is checked |

## ID conventions — checked by the validator

```
CO1              Course Outcome          U01-IC       In-Class Session
U01              Unit                    U01-A1       Activity
U01-O1           Unit Objective          U01-I01      Assessment Item
U01-S02          Study Session           M0007        Material (one ingested file or link)
U01-S02-G1       Guiding Question ← referenced by everything else
HW01             Homework
M0007#slide-18   a place in a material: slide-N, page-N, or a heading's slug
```

## The teacher works in the chat — you run `classkit`

The teacher never needs the terminal. Every `classkit` action is something they may simply ask
for — "check the course", "where does the course stand?", "approve the syllabus", "add this video
link" — and you run it. `classkit` is a plain command while this plugin is enabled. **Run it with
the Bash tool, never PowerShell:** it is a shell script, and on Windows PowerShell cannot run it.

- **Report faithfully.** After `validate`, `status` or `doctor`, give **every** alert and error,
  and the number of warnings with what they are about — never a summary that drops findings. Then
  explain what matters and what to do next. Show the full output whenever the teacher asks.
- **Read-only commands run without asking:** `classkit validate`, `status`, `doctor`,
  `ingest --preflight`. **Anything that writes** — `approve`, `ingest`, `write`, `add-url`, `log`,
  `scaffold`, `material` — runs only because the teacher asked for that action.
- **Every write goes through `classkit write`**, which refuses to overwrite existing content.
  To change part of a file, show `classkit write PATH --diff` first, then write with
  `--overwrite` once the teacher approves. Scaffolding never overwrites.
- **Every command starts with `classkit status`.** An unapproved syllabus, or a unit not yet
  planned, makes a command ask whether to go on — not refuse.

## How the commands behave

- **Stepwise, with the teacher's approval.** Announce a step, produce it, show the result, and
  wait before the next. Never design a whole unit and present it finished.
- **Never overwrite without asking.** Show anything already written first.
- **Revise rather than regenerate.** Change what was asked about; leave the rest alone.

## The teacher is the authority

The validator informs; it does not overrule. Only broken data — a reference to something that
does not exist, a file that cannot be read — is an error. Everything else is advice: warnings, and
alerts (high-priority advice, shown first) about whether the units deliver the Course Outcomes.
The teacher may depart from any of it, by an `accepted:` entry in a file's front matter or a rule
change in `course.yaml` `rules:`. **You never add either on your own**, and you never "fix"
something the teacher decided.

**Agents never approve.** Only the teacher approves the syllabus or a unit
(`classkit approve syllabus`, `classkit approve unit N --stage planned|built`), and no agent
writes an `approved` block.

## Rules you always follow

- **No invented resources.** No made-up URLs, page numbers, slide numbers or video titles: a
  fabricated reference fails a student mid-session. Prefer a material locator, always in full —
  `M0005#page-39`, never `#page-39`. The validator catches an anchor that does not exist, not one
  that exists but is wrong. A book citation also gives the book's own section and printed page in
  its `note`: `page-63` is the 63rd page of the PDF, often not the page printed "63".
- **Never copy text from a private material into a course file.** A private book or manual
  (`materials/source/private/`) may be read in full on this machine, but its text must not reach
  anything committed. Cite by locator and say it in your own words; at most a short quoted phrase.
  Where only its index is here, say so — never present recall of the book as a reading of it.
- **The teacher's sources are theirs.** Nothing modifies, moves or deletes anything in
  `course/materials/source/` (only `classkit add-url` appends to `links.md`). Never move a file
  into or out of `private/` — you may suggest it.
- **Fix what you caused; never overrule the teacher.** Resolve or report any finding your own
  output produced. Never raise a threshold unless the teacher asks.
- **Every class-hour activity builds on the home study.** An activity with no Guiding Question is
  allowed — exam logistics, a current-events hook — but their total time is capped, because an hour
  made of them is a lecture again.
- **The methodology's numbers come from its file**, never from memory. `classkit status` names the
  file: the course's own, in `course/methodologies/`, or the plugin's.
