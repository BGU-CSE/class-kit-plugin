---
description: Hands assessment items for a unit to the command that writes them — the entry quiz to /class-kit:build-unit, homework to /class-kit:plan-homework; exam items are not in Core
argument-hint: "<unit number> [quiz|homework|exam]"
---

Write assessment items for unit **$1**, for `$2` (default: the entry quiz).

If `$2` is `homework`, stop this command and run `/class-kit:plan-homework $1` instead, with the
unit given. Tell the teacher that homework is planned and built by its own
commands — `/class-kit:plan-homework`, then `/class-kit:build-homework` — so that every homework
item has a class and is reviewed and attempted before it is approved. Do not continue with the
steps below.

**For an entry quiz** (`quiz`, the default), stop this command and run `/class-kit:build-unit $1 quiz`
instead: the entry quiz is built with its unit, step by step, so that the class hour can list its
items (D-043). Tell the teacher so. Do not continue.

**For exam items** — stop. Exam items return with the Assessment phase: where they may live is
still undecided (Q-002) — the course repo is shared with collaborators and git history is permanent,
so exam content in it is a leak waiting to happen. Tell the teacher so; nothing is written.
