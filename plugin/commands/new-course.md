---
description: Create a new course in this folder — the course skeleton with its syllabus template — and have the teacher start a new session so the course rules load
argument-hint: "[optional: the course title]"
---

Create the teacher's course in the folder this session was started in. This is the teacher's first
step. The course rules are **not** loaded yet: they load when a session starts in a folder that
holds a course, and there is none yet. So this command carries what it needs.

Run every `classkit` command with the **Bash** tool, never PowerShell: `classkit` is a shell
script, and on Windows PowerShell cannot run it.

1. **Is there a course already?** Run `classkit status || true` — the `|| true` keeps the expected
   "no course" answer from showing to the teacher as a failed step. If it shows a course, stop: say
   where it is, and that this command only creates a new one. "cannot find a course" means go on.
   Any other error: stop and report it as it is.

2. **The course's details.** Ask the teacher, in one message, for what they have not already said
   (here: $ARGUMENTS): the **title** (required); the **course code**; the **institution** (default:
   Ben-Gurion University of the Negev); the **instructor(s)**; the **number of units** — weeks in
   the semester (default 13). A code or instructor not known yet stays empty;
   `/class-kit:plan-syllabus` asks again.

3. **Create it, once the teacher confirms.** Show the command, then run it from this folder:

   ```bash
   classkit scaffold course --title "…" --code "…" --institution "…" --instructor "…" --units N
   ```

   Leave out an option whose value is empty. **Never pass `--path`**: the course belongs in
   `course/` inside this folder, where `classkit` and the plugin look for it. Scaffolding never
   overwrites anything; report what it created.

4. **Check it:** `classkit validate`. A fresh course has 0 errors and two expected warnings (no
   workload yet; no units yet). Report every line as it is.

5. **Tell the teacher what comes next, in this order:**
   - **Start a new session now** — open a new session in this same folder, or type `/clear` — so
     the course rules load. This session does not have them.
   - Put the existing materials in `course/materials/source/`, in any files and any structure;
     published books and solutions manuals in `course/materials/source/private/`, which is kept out
     of git.
   - Then run `/class-kit:ingest`.

   Do not start ingesting or planning in this session.
