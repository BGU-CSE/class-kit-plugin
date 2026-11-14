---
description: Add an item class to this course's homework — a kind of homework item with its typical time, tools, Bloom range and how it is checked — drafted from a short interview, and approved by you
argument-hint: "<class name> [a short description]"
---

Add an item class named **$1** to the course, from the description **$2** (interview the teacher
for anything missing). An item class is the kind of a homework item — DIY, Practicing, Coding,
Research, or one the course adds — and carries its typical minutes, its tools, its Bloom range and
how the build's solver checks it. Adding one is a change to this course only; the classes live in
`course/assessments/item-classes.yaml`.

**Load the `class-kit:interviewing-teachers` skill** before step 2.

1. **Ground yourself.** `classkit status`, then read:
   - `course/assessments/item-classes.yaml` — the existing classes; the new one must not collide by
     name (names are case-sensitive: `DIY` and `Diy` are two classes)
   - `course/assessments/homework-defaults.yaml` — its `default_class_counts`, which gets the new
     class at 0
   - `course/course.yaml` — the declared `tools`: the class's `default_tools` must be among them

   If the course has no `item-classes.yaml` or `homework-defaults.yaml` yet (it has never had
   homework), create each from its template — `${CLAUDE_PLUGIN_ROOT}/templates/course/item-classes.yaml`
   and `${CLAUDE_PLUGIN_ROOT}/templates/course/homework-defaults.yaml` — through `classkit write`
   (new files; nothing is overwritten), and tell the teacher (HW-D13).

2. **The interview**, in this conversation, to the skill: draft the whole entry — `description`,
   `typical_minutes` (`min`, `max`), `time_variance` (`low` for items with a predictable duration,
   `high` for those that vary widely per student), `typical_bloom`, `default_tools`, `evaluation`
   (`strategy`: `persona_attempt`, `execute`, `skip` or `custom`, and a line of `notes`) — taking
   the closest existing class as the example (Practicing for a no-AI class, Research for an
   investigation). Show it in one message, and ask only what the teacher knows better. A tool the
   course does not declare is a follow-up: offer to add it to `course.yaml`'s `tools`, as its own
   change.

3. **A writing guide?** Decide this yourself — it is a workflow choice, not an interview question.
   Rough rule: yes if the class has concerns the item writer would not know (as Coding has tests,
   and Research has source citation); no if it is a simple envelope (as DIY and Practicing are). If
   yes, draft it as an ordinary course file, `course/assessments/writing-guides/<slug>.md` (slug:
   the class name in lower case, words joined by `-`): what a good item of this class asks, what
   its rubric weighs, its common failure modes — taking the plugin's guidance for Coding or
   Research as a model of shape, not of content. The class names it in `writing_guide:
   assessments/writing-guides/<slug>.md`; the item writer and the critic read it. A class checked
   by `strategy: custom` needs a guide for that too: draft it the same way, and name it in
   `evaluation.custom_guide`. Tell the teacher a drafted guide should be read once and improved
   through use before it is trusted.

4. **Show the change set**, all together in one message: the new entry for `item-classes.yaml`, the
   new line in `default_class_counts` (at 0 — the class stays out of the ordinary homework until the
   teacher includes it), and the guide, if any. The teacher approves, edits, or rejects.

5. **On approval, write it** — all of it or none:
   - `item-classes.yaml` and `homework-defaults.yaml` exist: show each with
     `classkit write <path> --diff` (the whole file, the class appended), then write with
     `--overwrite`
   - the guide is new: `classkit write course/assessments/writing-guides/<slug>.md`

6. **Log and check:**

   ```bash
   classkit log "/class-kit:new-item-class Reading" --changed "item class Reading (10–25 min, low variance, persona_attempt); writing guide drafted" \
     --why "<the teacher's reason>" --file assessments/item-classes.yaml --file assessments/homework-defaults.yaml \
     --file assessments/writing-guides/reading.md
   ```

   Never log a rejected change set. Then `classkit validate`: the new class's tools must be declared
   (`class_tools_declared`), its guides must exist (`item_class_guide_reference`), and it should
   name an evaluation strategy (`item_class_evaluation_declared`).

7. **Report**: the class, the files written, and — if a guide was drafted — that the teacher should
   read it once. The class is available to the next `/class-kit:plan-homework`.

**This command only adds.** Changing an existing class is done in conversation or by hand — show
the diff, write with `--overwrite` on the teacher's go-ahead. **One class per run**: if the teacher
describes several, ask which to add first.
