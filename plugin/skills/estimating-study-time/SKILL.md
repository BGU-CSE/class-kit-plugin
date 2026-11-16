---
name: estimating-study-time
description: How to estimate honestly how long a guiding question takes to study, so a session's minutes are real. Use when proposing or revising a guiding question's est_minutes (under /class-kit:build-unit), checking whether a session fits its budget, or auditing whether a home-study workload is realistic (/class-kit:review-unit).
---

# Estimating study time

Each guiding question carries one number, `est_minutes`: the time a student needs to study it — to
reach and understand its answer. The teacher approves it. A session's budget is the **sum** of its
questions' minutes plus a small overhead, and `classkit validate` checks that arithmetic (D-020).

Code checks the sum; **it cannot check that a number is honest**. Type "3" for a fifteen-minute
question and the validator stays quiet. That is why this skill exists: the designer proposes each
estimate by it, and the critic checks each against it (D-025). Optimistic estimates are the single
most damaging thing in a course — they launder an unrealistic week as a verified one, and a "two-hour"
week that takes four is a week students stop doing the prework, which collapses the class hour.

## The yardstick

`${CLAUDE_PLUGIN_ROOT}/defaults/time-constants.yaml`, overridden per course in `course.yaml` under
`time_constants`. It is **advisory**: it helps you propose a number and helps the critic doubt one;
no rule derives a time from it. Its values are placeholders until tuned to real students (Q-005).

- **Reading.** `textbook_pages_per_minute` — technical prose with notation and proofs is far slower
  than ordinary reading; a page with three equations can take longer than five pages of exposition.
  Look at the actual pages the `answer` points to, and raise the estimate for dense ones.
- **Video.** `video_realtime_multiplier` — students pause, rewind and re-watch. Use the real
  duration, checked, not one guessed from a title.
- **The class Gem.** `gem_minutes_per_goal` — a tutoring exchange that reaches a real answer is
  several turns, not one.
- **An exercise.** `exercise_default_minutes` — the time to *attempt* it, being stuck included.
- **A deferred question** (`defer_to_class`) — thinking time: how long to form a view worth bringing
  to class, not to reach the answer.

## The arithmetic

For a session: `session_overhead_minutes` once, plus each question's `est_minutes`. It must not
exceed the session's minutes by more than the methodology's `budget_tolerance_minutes` — the
estimates are approximate, so a small overrun is not a failure. Study paths are **not** counted:
they are alternatives, and the student takes one route.

When the sum does not fit, **the design is wrong — fix the design**:

- cut a question (usually right: three good ones beat five rushed);
- move a question to another session, or another unit with the teacher's agreement;
- split the question's material so less of it is needed.

**Never shave an estimate to make the number fit.** That is the one move that turns the whole
mechanism into theatre.

A question with no `est_minutes` makes its session **unverifiable**, and the validator says so. When
you cannot judge a resource's length, leave the estimate off and say what needs confirming — that
is the honest state.

## Sanity checks a validator cannot run

- Does "8 min" survive contact with the eight pages of proofs its `answer` points to? Open the
  material and ask whether you believe it.
- Are all of a session's estimates suspiciously alike? That usually means they were filled in by
  pattern rather than considered.
- Does the answer really answer the question in that time — or does a 4-minute slide cover a third
  of it?
- Sum the whole unit. Four sessions each "just fitting" is a week with no slack at all, and no student
  is average on every question.

## When you don't know

Say so. An estimate flagged as a guess is useful; a guess presented as a measurement is not.
