---
description: Adversarially review the syllabus for the problems the validator cannot catch (optional)
argument-hint: "[optional: what to focus on]"
---

Review `course/syllabus/syllabus.md` using the **class-kit:course-critic** agent — an agent that did not write
it. Optional: `/class-kit:build-syllabus` offers it once a full draft exists, before or after approval.

This command changes nothing in the syllabus; it only logs the review. Fixes go back through `/class-kit:build-syllabus` (its revision step), only the
ones the teacher picks.

1. Run `classkit status` and show it — the critic should know whether it is reading a draft, an
   approved syllabus, or one edited since approval.
2. Run `classkit validate` and hand its output to the critic, so it does not spend effort
   re-deriving what the tooling already found. Run `classkit doctor` and tell it which private
   materials are index-only on this machine.
3. Run the **class-kit:course-critic** on the **syllabus** (its "Reviewing the syllabus" section), with
   anything the teacher asked it to focus on (`$1`).

Present its findings ordered by how much damage each does if the syllabus is approved and built on
— or uploaded to the university — separating **"this is broken"** from **"I would have done this
differently"**.

Then ask the teacher which, if any, to act on. Do not apply them: several depend on knowing the
students and the institution. The ones the teacher picks become revision requests in
`/class-kit:build-syllabus`, which logs each change. Log the review itself once the teacher has
answered — even when nothing changes, because the findings they kept for later exist nowhere else
once this conversation ends:

```bash
classkit log "/class-kit:review-syllabus" --changed "review: 10 findings (4 broken), 1, 3, 4 to fix" \
  --why "<what the teacher chose to fix, and what they kept and why — e.g. credit points left to the department>"
```
