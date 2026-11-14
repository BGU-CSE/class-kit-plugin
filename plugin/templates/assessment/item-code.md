---
id: {{item_id}}
unit: {{unit_id}}
format: code
guiding_questions: [{{unit_id}}-S01-G1]
usage: [homework]
difficulty: medium
bloom: analyze
# est_minutes is optional for a class with time_variance: high, such as Coding (HW-D06):
# when absent, the homework budget uses the midpoint of the class's typical_minutes range.
stem: "TODO — problem statement: inputs, outputs, constraints (including complexity)."
starter_code: |
  # Skeleton the student edits. Omit for from-scratch problems.
  def solve(nums):
      pass
expected_solution: |
  # Reference solution. Teacher-only: it goes to the teacher answers document.
  def solve(nums):
      return sum(nums)
tests:
  - input: "[1, 2, 3]"
    expected: "6"
    note: "typical case"
  - input: "[]"
    expected: "0"
    note: "empty case — the tripwire"
  - input: "[-1, 1]"
    expected: "0"
    note: "cancellation"
rubric:
  - criterion: "Handles the empty case."
    points: 3
  - criterion: "Correct for the general non-empty case."
    points: 5
  - criterion: "Meets the complexity constraint stated in the stem."
    points: 2
---

Notes: code items combine a rubric (which grades the student's *approach*)
with tests (which grade correctness mechanically). Both should be present.
The rubric catches "correct logic, one edge case missed"; the tests catch
"looks reasonable but wrong on real input."

Tests must be deterministic — no wall-clock, no randomness, no network. The
grader runs them, and a flaky test in an item bank is worse than no test.

# Notes

- The template for `format: code`, usually with `item_class: Coding`
  (`classkit scaffold item U03 --format code --class Coding`). It adds the fields
  a code item needs: `starter_code`, `expected_solution` and `tests`.
- `format: code` means autograded — the item's `tests` are run against the student's
  code. Use this template when the item has a runnable check.
- For a Coding-class homework item that will be graded by a human reading the code
  (not autograded), start from the open template instead
  (`--format open --class Coding`), and structure the rubric for reading code.
