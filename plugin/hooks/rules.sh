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
# any folder above it (a session started deeper inside the repository).
is_course() {
    local dir="$1" parent
    [ -f "$dir/course.yaml" ] && return 0
    while :; do
        [ -f "$dir/course/course.yaml" ] && return 0
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
    native="$rules"
    command -v cygpath > /dev/null 2>&1 && native="$(cygpath -m -- "$rules")"
    # Exit 3 = too long; the JSON goes to stdout only when it fits.
    "${PYTHON[@]}" - "$native" "$limit" <<'PY'
import json, sys
text = open(sys.argv[1], encoding="utf-8").read()
if len(text) > int(sys.argv[2]):
    print(f"class-agent-kit: rules/core.md is {len(text)} characters, over the {sys.argv[2]} "
          "Claude Code accepts; the course rules were NOT loaded", file=sys.stderr)
    sys.exit(3)
sys.stdout.reconfigure(encoding="utf-8")
print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": text}}))
PY
    status=$?
    [ $status -eq 0 ] && exit 0
    [ $status -eq 3 ] && exit 2
    echo "class-agent-kit: could not encode the course rules (python exit $status)" >&2
    exit 2
fi

# No Python: plain stdout is context too on SessionStart. Characters, not bytes.
size=$(LC_ALL=C.UTF-8 wc -m < "$rules" | tr -d ' ')
if [ "$size" -gt "$limit" ]; then
    echo "class-agent-kit: rules/core.md is $size characters, over the $limit Claude Code accepts; the course rules were NOT loaded" >&2
    exit 2
fi
cat "$rules"
exit 0
