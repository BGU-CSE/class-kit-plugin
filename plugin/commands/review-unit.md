---
description: Adversarially review a built unit — or a unit's plan — for the problems the validator cannot catch
argument-hint: "<unit number>"
---

Review unit **$1** using the **class-kit:course-critic** agent — an independent agent, which did not
write the work it judges.

Run `classkit status` first. **If the unit is planned but not built** (its sessions are still
placeholders), the review is of its **plan**: tell the critic so — it has a section for a unit's
plan and loads the `class-kit:planning-units` skill. Its findings go back through
`/class-kit:plan-unit $1` as revision requests, only the ones the teacher picks.

Otherwise the review is of the **built unit**: its study sessions, its entry quiz and its class hour.
Run `classkit validate` first and hand the critic its output, so it doesn't spend effort
re-deriving structural problems the tooling already found. Tell it which private materials are
index-only on this machine (`classkit doctor`).

The critic looks for what the validator cannot see:

- guiding questions that are topic labels with a question mark on the end
- answers that point at a real place that does not answer the question
- study times (`est_minutes`) that add up while being unrealistic against the material — the critic
  is the only check on whether they are honest (D-025)
- questions deferred to class that dodge an answer, or that the hour names without resolving
- activities that reference the prework without depending on it — the test is *which activities
  would still work if the students had done nothing at home?* — and unmapped activities whose
  reason is a lecture with an excuse
- an entry quiz whose keys the locators do not support, or whose distractors diagnose nothing
- an hour planned for a different room than the one the syllabus describes

Present the findings ordered by how much damage each does if shipped, separating **"this is
broken"** from **"I'd have done this differently"**.

Then **ask the teacher which to fix** — and wait. Do not apply the fixes automatically: this is their
course, and several of these judgements depend on knowing the students. Each one they pick goes
back through `/class-kit:build-unit $1` with its part (`session K`, `quiz`, `class`) — or is revised in
this conversation, shown with `classkit write --diff` before it is written. Review is optional and is
not a state; log it once the teacher has read it:

```bash
classkit log "/class-kit:review-unit $1" --changed "review: 3 findings (1 broken), 2 to fix" \
  --why "<what the teacher chose to fix, and what they kept and why>"
```
