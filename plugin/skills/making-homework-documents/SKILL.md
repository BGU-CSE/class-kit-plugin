---
name: making-homework-documents
description: How to make a homework's Word or PDF documents when the teacher asks for them, after /class-kit:build-homework — the student document (no answers; one per targeted version) and the teacher answers document, laid out as course/assessments/homework-document.yaml says, with a leak check on every student document and a safe place to save them. Use whenever the teacher asks for a homework's documents, a PDF of it, or a change to documents already made.
---

# Making a homework's documents

The homework is its file, `course/assessments/homework/HW0N.md`, and the items it lists in
`course/assessments/items/`. The Word and PDF documents are **outputs made from them, on request**
— never the source of truth, and never committed (HW-D23, HW-D24). Make them when the teacher
asks, normally once the homework is approved as built (`classkit status` says so); for one that
is not, say so and ask whether to go on.

## What goes in each document

Read the homework file, every item it lists, `course/course.yaml` (its `tools`) and
`course/assessments/homework-document.yaml` (HW-D30): course title, instructor, semester, the
title built from `title_format` (`{number}` is the homework number from its id: HW03 → 3;
`{id}`, `{units}`, `{course_title}`, `{semester}`), the due date (the homework's `due_date`, in
`due_date_format`), submission instructions, header, footer, logo, language and direction, font
and size, and whether to print each item's minutes (`show_est_minutes`). If `semester` looks out
of date, ask before using it — and offer to update the file (`classkit write --diff`, then
`--overwrite` on the teacher's go-ahead).

- **The student document** — the homework as students receive it: the title and course details,
  the due date and submission instructions, the collaboration rule, that it is open book (every homework is),
  then each item in order: its stem, its choices (with no marking of which is correct), its
  starter code, and the tools it needs (`item_tools`, with each tool's description from
  `course.yaml`). **No answers.** With targeted versions (HW-D26), one student document **per
  version**: the shared items plus that version's items, labelled by the version's label only.
- **The teacher answers document** — the same items with everything the student document leaves
  out: model answers (`model_answer`), the correct choices with their rationales, rubrics,
  reference solutions (`expected_solution`) and tests, and — when it is still in this
  conversation — the solver's teacher aid for items it skipped (it is not saved anywhere,
  HW-Q06). One document, every version clearly labelled.

**Never print the plan** — not `focus_notes`, not `quiz_summary`, not the slots — in either
document, and nothing about which student gets which version.

## Writing the Word file

Use the plugin's own Python, which has `python-docx`: `"$CLASSKIT_VENV/bin/python"` (on Windows
`"$CLASSKIT_VENV/Scripts/python.exe"`). Write the script to a temporary folder **outside the
course**, run it there, and delete it afterwards — the script is a tool, not course content. Set
the document's language and direction (right-to-left for Hebrew or Arabic, on every paragraph),
the font and size, header, footer and logo as the settings say. If `CLASSKIT_VENV` is not set,
tell the teacher to start a new session (the plugin sets up its Python when a session starts).

## The leak check — every student document, every time

After writing a student document, read its text back and confirm that none of the items' answer
fields appear in it: `model_answer`, a choice marked correct (or its rationale), `expected_solution`,
`tests`, `rubric`. Compare against the item files, not your memory of them. Anything suspicious is
shown to the teacher, never delivered silently. Report the result with the documents.

## A PDF

Convert the Word file with LibreOffice when it is installed: `soffice --headless --convert-to pdf
--outdir <folder> <file>.docx`. If it is not, say so and tell the teacher to save the Word file as
PDF from Word. Run the leak check on the Word file it was made from.

## Where to save them (HW-D24)

Ask the teacher. Any folder **outside** the course repository is fine. Inside the repository,
only a dedicated output folder holding no tracked files — never the repository root, and never a
broad existing folder such as `course/`, `assessments/`, `materials/` or `units/`.

Before writing inside the repository:

1. Resolve the repository root and the requested destination. Refuse if the destination is not
   the exact dedicated folder the teacher approved.
2. Check it with `git ls-files`. If the folder or either document is already tracked, stop and ask
   the teacher to choose another place. Ignoring a path does not untrack it.
3. Check the repository-relative destination with `git check-ignore`. If it is not ignored, add
   only that exact, anchored folder pattern to `.git/info/exclude` (local to this clone; never
   `.gitignore`), then run `git check-ignore` again to verify it.
4. Tell the teacher what local exclusion was added. Never run `git rm`, alter tracked files, or
   exclude a parent folder to make this work.

For later requests, ask the teacher where the documents are.

## Later changes

When the teacher asks to change something, change the **item in the bank first** — through
`classkit write`, `--diff` then `--overwrite` on their go-ahead — then make both documents again
and repeat the leak check. When the teacher has edited a document by hand, the bank is not
updated until they ask you to sync it; then read each change back into its item file and confirm
it with them.

Publishing solutions to students is the teacher's decision, outside this skill (HW-D25).
