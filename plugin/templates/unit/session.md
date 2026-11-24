---
id: {{session_id}}
unit: {{unit_id}}
number: {{session_number}}
title: "{{session_title}}"
duration_minutes: {{session_minutes}}

# {{goals_min}}-{{goals_max}} Guiding Questions. Each `prompt` is a QUESTION the student should be
# able to answer after this session — "Why is amortized append O(1) when some appends cost O(n)?",
# not "Amortized analysis".
#
# Each question carries:
#   est_minutes — your approved estimate of the time to study it. The session's budget is the
#                 sum of these plus a small overhead; the validator warns when it overruns.
#   answer      — WHERE the correct answer is found, never the answer itself: a material locator
#                 (a slide of your deck, a page of the book) — for a book, its own section and
#                 printed page in `note`.
#
# A question may instead be a thinking prompt whose answer waits for the class meeting:
#   - id: {{session_id}}-G4
#     type: question
#     prompt: "Which would you choose here, and why?"
#     objectives: [{{unit_id}}-O1]
#     est_minutes: 5
#     defer_to_class: true      # no `answer`; an activity of the class hour must pick it up
goals:
  - id: {{session_id}}-G1
    type: question
    prompt: "TODO — phrase as a question the student should be able to answer"
    objectives: [{{unit_id}}-O1]
    est_minutes: 7
    answer:
      - kind: slides
        ref: "TODO — where the answer is: a material locator, e.g. a slide of your deck"
  - id: {{session_id}}-G2
    type: question
    prompt: "TODO"
    objectives: [{{unit_id}}-O1]
    est_minutes: 7
    answer:
      - kind: textbook
        ref: "TODO"
  - id: {{session_id}}-G3
    type: question
    prompt: "TODO"
    objectives: [{{unit_id}}-O2]
    est_minutes: 7
    answer:
      - kind: textbook
        ref: "TODO"

# Study paths — an optional pool of other resources for the whole session (a chapter, a video,
# the class Gem). None is mandatory; a student may use their own. They are not timed.
paths:
  - kind: gem
    ref: "{{unit_id}}"
---

# {{session_title}}

Optional framing for the student — why this session matters and how it connects to the
previous one. Keep it short; the questions above carry the work. If students may start this
session a week early, once the previous unit's sessions are done, say so here.
