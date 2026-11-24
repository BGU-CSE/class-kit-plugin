---
name: writing-guiding-questions
description: How to phrase a study goal as a guiding question a student can actually answer and check, say where its answer is found, and when to defer it to the class meeting. Use when writing, reviewing, or revising the goals of a study session (under /class-kit:build-unit), or when judging whether an existing goal is a real question or a topic label in disguise.
---

# Writing guiding questions

A guiding question is a study goal phrased as a question the student is expected to be able to
answer after the session. It is the atomic unit of the whole course: assessment items, in-class
activities and the class Gem all reference it. Get these wrong and everything downstream inherits
the mistake.

## The move

Take what you want the student to be able to do, and write the question they could answer only if
they could do it.

| Topic label | Guiding question |
|---|---|
| Amortized analysis | Why is appending to a dynamic array O(1) amortized when some appends cost O(n)? |
| Hash collisions | What happens to lookup time as the load factor approaches 1, and why? |
| Recursion | How can you tell whether a recursive function will terminate? |
| Big-O notation | Why does O(n) describe an upper bound rather than the exact running time? |
| Binary search trees | What makes a BST degrade to O(n), and what do balanced trees do about it? |

Notice what changes: the label names territory, the question names a destination.

## Five tests

Apply all five to every question you write.

1. **Answerable and checkable.** Could the student tell whether they'd answered it? "Understand
   sorting" fails. "Why can't comparison sorts beat O(n log n)?" passes.
2. **It has a real answer.** Not a yes/no. Not "discuss". If the honest answer is one word, it's a
   flashcard, not a session goal.
3. **It fits the budget.** A question needing 40 minutes doesn't belong in a 25-minute session.
   Split it or move it.
4. **Together they're sufficient.** A student who can answer all 3–5 questions has genuinely done
   the session. If something important isn't reachable through any question, either add one or
   accept it's out of scope — don't leave it implied.
5. **Mostly why and how.** Some recall is fine. A session made entirely of "what is X?" is a
   reading assignment with extra formatting.

## Failure modes

**The question mark disguise.** "What is a hash table?" is a topic label wearing punctuation. Test:
could the student answer it by copying one sentence from the index? Then it isn't a guiding
question.

**The essay.** "How do the various tree structures compare across their operations and what are
the tradeoffs?" is four questions and forty minutes. Split it.

**The question that needs the class hour.** Home study comes *first*. If a question can only be
answered after the discussion the teacher plans to run on Wednesday, it is either an in-class
activity, or — when thinking about it beforehand is the point — a question **deferred to class**
(below). Never a question that silently depends on the meeting.

**The unanswerable-from-its-own-answer question.** Follow the `answer`. If the question asks "why"
and the locator leads to a definition, the student cannot get there from here.

**The invisible-scaffolding question.** It quietly assumes a concept from a later unit. Check the
prerequisites.

## Where the answer is — `answer`

Every guiding question records **where its correct answer is found**, never the answer itself
(D-019). It is the ground truth the entry quiz's answer key, the critic and later the class Gem
rest on.

- **A material locator first**: `ref: "M0007#slide-18"` — the validator checks that the material
  and the anchor exist. It needs no `kind`: the manifest knows it.
- **Precise**: the slide, the page, the subsection that answers *this* question — not the chapter.
  Two locators are fine when the answer really spans two places.
- **A book cited by page carries its own coordinates** in `note`: `page-63` is the PDF's 63rd page,
  often not the page printed "63" — `note: "CLRS §6.2, Exercise 6.2-3 (printed p. 45)"`.
- A source that is cited but not ingested: a textbook key with its locator (`"CLRS §2.3.1"`) and a
  `kind`. **Never a locator you have not read there** — a fabricated slide number validates as
  well as a real one, and fails a student mid-session.
- **Not a material for instructors** (`audience: instructor`, a solutions manual): students are
  pointed at answers.

## Deferring a question to class — `defer_to_class`

A question may instead be a **pre-class thinking prompt** whose resolution is the class meeting's
job — "how would you choose between a heap and a sorted array here?" (D-023). Mark it
`defer_to_class: true` and give it no `answer`. Its `est_minutes` is thinking time and still counts.

The discipline: an activity of the unit's class hour **must** pick it up (the validator warns
otherwise), so deferring costs contact time — it is not a way to skip finding an answer. Use it
rarely and on purpose: a session whose questions are mostly deferred teaches nothing at home.

## Phrasing

Ask about the subject, not about the course: "Why does quicksort degrade on sorted input?", not
"What does the lecture say about quicksort's worst case?" The student should be able to take the
question to a textbook, a video, or the class Gem — any of the session's study paths — and have all
of them be a route to the same answer.

Keep them short. If a question needs three sentences of setup, the setup belongs in the session
body and the question should stand alone.
