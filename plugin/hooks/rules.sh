#!/usr/bin/env bash
# SessionStart (no matcher, so also after /clear and compaction): inject rules/core.md as context
# when the project holds a course — wherever classkit would find one. Silent everywhere else.

root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
project="${CLAUDE_PROJECT_DIR:-$PWD}"
# Git Bash: C:\Projects\x → /c/Projects/x, so that dirname can walk up it.
command -v cygpath > /dev/null 2>&1 && project="$(cygpath -u -- "$project")"
rules="$root/rules/core.md"
limit=10000  # Claude Code's cap on a hook's additionalContext; past it, only a 2,000-char preview arrives

# The places classkit's find_course_root() looks: course.yaml in the project folder itself (a course
# created with --path ., or a session started inside course/), or course/course.yaml there or in
# any folder above it (a session started deeper inside the repository). Sets $course to that folder.
is_course() {
    local dir="$1" parent
    [ -f "$dir/course.yaml" ] && course="$dir" && return 0
    while :; do
        [ -f "$dir/course/course.yaml" ] && course="$dir/course" && return 0
        parent="$(dirname -- "$dir")"
        [ "$parent" = "$dir" ] && return 1
        dir="$parent"
    done
}
is_course "$project" || exit 0

if [ ! -f "$rules" ]; then
    echo "class-agent-kit: $rules is missing; the course rules were not loaded" >&2
    exit 2
fi

. "$root/hooks/find-python.sh"

if [ ${#PYTHON[@]} -gt 0 ]; then
    native_rules="$rules" native_root="$root" native_course="$course"
    if command -v cygpath > /dev/null 2>&1; then
        native_rules="$(cygpath -m -- "$rules")" native_root="$(cygpath -m -- "$root")"
        native_course="$(cygpath -m -- "$course")"
    fi
    # The rules, plus a note when the course log names a newer plugin than this one, or else when the
    # marketplace offers another version (inject_rules.py). Exit 3 = too long; the JSON goes to
    # stdout only when it fits.
    "${PYTHON[@]}" "$native_root/hooks/inject_rules.py" "$native_rules" "$limit" "$native_root" "$native_course"
    status=$?
    [ $status -eq 0 ] && exit 0
    [ $status -eq 3 ] && exit 2
    echo "class-agent-kit: could not encode the course rules (python exit $status)" >&2
    exit 2
fi

# No Python: plain stdout is context too on SessionStart. The rules, plus a note so that Claude tells
# the teacher at once, not only when a classkit command fails (finding 8). Characters, not bytes.
note='

## Python is missing on this computer

Class Agent Kit needs Python 3.10 or later, and none was found, so `classkit` cannot run in this
session. In your first reply, tell the teacher this, and that the fix is to install Python from
https://www.python.org/downloads/ (on Windows, tick "Add python.exe to PATH" in the installer),
then start a new session. Until then, do not run `classkit` commands.'
size=$(( $(LC_ALL=C.UTF-8 wc -m < "$rules" | tr -d ' ') + $(printf '%s' "$note" | LC_ALL=C.UTF-8 wc -m | tr -d ' ') ))
if [ "$size" -gt "$limit" ]; then
    echo "class-agent-kit: the course rules are $size characters, over the $limit Claude Code accepts; they were NOT loaded" >&2
    exit 2
fi
cat "$rules"
printf '%s\n' "$note"
exit 0
