---
# One homework (homework module). Validated against schemas/homework.schema.json.
# /class-kit:plan-homework writes the plan; /class-kit:build-homework writes the items into the
# shared bank (course/assessments/items/) and lists them here. You can edit this file by hand.

id: {{homework_id}}
units: [{{units}}]                   # the units it covers
purpose: practice                    # practice | graded | diagnostic
total_minutes: {{total_minutes}}     # the time budget for a student
# due_date: 2026-11-15               # optional; printed on the student document

source:
  kind: material                     # material | quiz_report
  # ref: U03                         # for quiz_report: the unit whose entry quiz it reports on.
                                     # The report itself is given in the session, never stored.

allowed_tools: []                    # tools from course.yaml's `tools` — the plan fills them in
collaboration: discussion_only       # forbidden | discussion_only | allowed

# THE PLAN — /class-kit:plan-homework fills it in. One slot per item to build:
#   slot, guiding_questions, intent, item_class, format, difficulty, bloom, est_minutes,
#   tools, decision (fresh | reuse | adapt), from (for reuse and adapt), version (a label).
plan:
  slots: []

# Targeted versions — optional, planned from a quiz report. Every student gets the shared items
# plus those of their version. A label never names a student.
# versions:
#   - label: A
#     targets: [U03-S01-G1, U03-S01-G2]
#     items: []                      # written by the build

# THE ITEMS — written by /class-kit:build-homework: the shared items in order, and the tools a
# particular item needs.
items: []
# item_tools:
#   U03-I05: [wireshark]

# APPROVAL — written by `classkit approve homework {{homework_number}}` (date, stage, hash).
# `planned` once the plan is approved; `built` once the whole homework is. Editing afterwards is
# normal.
---

# {{homework_id}}

Teacher notes on this homework — why it is shaped this way, what to change next time. Not shown
to students.
