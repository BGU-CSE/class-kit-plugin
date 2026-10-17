#!/usr/bin/env bash
# SessionStart: make sure the venv with classkit's dependencies exists, and tell later Bash
# commands where it is (CLASSKIT_VENV, through CLAUDE_ENV_FILE). bin/classkit runs with it.
#
# Never blocks the session: every path ends in exit 0. Prints nothing to stdout, which would
# become context; everything goes to $CLAUDE_PLUGIN_DATA/bootstrap.log.

root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
. "$root/hooks/find-python.sh"

# Forward slashes, and a Windows path Python understands (C:/Users/…, not /c/Users/…).
to_native() {
    if command -v cygpath > /dev/null 2>&1; then cygpath -m -- "$1"; else printf '%s\n' "${1//\\//}"; fi
}

if [ -z "${CLAUDE_PLUGIN_DATA:-}" ]; then
    echo "class-agent-kit bootstrap: CLAUDE_PLUGIN_DATA is not set; run as a plugin hook" >&2
    exit 0
fi
data="$(to_native "$CLAUDE_PLUGIN_DATA")"
mkdir -p "$data"
logfile="$data/bootstrap.log"
log() { printf '%s  %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*" >> "$logfile"; }

log "session start: $(uname -s 2>/dev/null) $(uname -r 2>/dev/null); plugin root $root"

if [ ${#PYTHON[@]} -eq 0 ]; then
    msg="class-agent-kit: no Python 3.10 or later found (tried python3, python, py -3). Install Python, then start a new session."
    log "$msg"
    echo "$msg" >&2
    exit 0
fi
log "python: ${PYTHON[*]} ($("${PYTHON[@]}" --version 2>&1))"

requirements="$(to_native "$root/requirements.txt")"
hash="$("${PYTHON[@]}" -c 'import hashlib, sys; print(hashlib.sha256(open(sys.argv[1], "rb").read()).hexdigest()[:12])' "$requirements")"
venv="$data/venv-$hash"

venv_python() {
    if [ -x "$venv/bin/python" ]; then echo "$venv/bin/python"
    elif [ -f "$venv/Scripts/python.exe" ]; then echo "$venv/Scripts/python.exe"
    fi
}

publish() {
    if [ -n "${CLAUDE_ENV_FILE:-}" ]; then
        printf 'export CLASSKIT_VENV="%s"\n' "$venv" >> "$CLAUDE_ENV_FILE"
        log "published CLASSKIT_VENV=$venv"
    else
        log "CLAUDE_ENV_FILE not set; CLASSKIT_VENV not published"
    fi
}

# `.complete` is written last, so a venv without it was interrupted and is rebuilt.
if [ -f "$venv/.complete" ]; then
    log "venv ready: $venv"
    publish
    exit 0
fi

# Two sessions starting at once: one installs, the other waits for it.
lock="$venv.lock"
if ! mkdir "$lock" 2> /dev/null; then
    log "another session is installing; waiting"
    for _ in $(seq 1 280); do
        [ -f "$venv/.complete" ] && { log "venv ready after waiting"; publish; exit 0; }
        sleep 1
    done
    log "gave up waiting for the other install"
    exit 0
fi
trap 'rmdir "$lock" 2> /dev/null' EXIT

rm -rf "$venv"
start=$(date +%s)
log "creating $venv"
if "${PYTHON[@]}" -m venv "$venv" >> "$logfile" 2>&1 \
    && vpy="$(venv_python)" && [ -n "$vpy" ] \
    && "$vpy" -m pip install --disable-pip-version-check --no-input -r "$requirements" >> "$logfile" 2>&1; then
    touch "$venv/.complete"
    log "installed in $(( $(date +%s) - start ))s"
    publish
else
    log "install FAILED after $(( $(date +%s) - start ))s; removing $venv"
    rm -rf "$venv"
    echo "class-agent-kit: installing classkit's Python dependencies failed; see $logfile" >&2
fi
exit 0
