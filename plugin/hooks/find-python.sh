# Sourced by bootstrap.sh and rules.sh. Sets PYTHON to a command (an array) that runs Python 3.10
# or later, or leaves it empty. On Windows `python3` may be the Microsoft Store placeholder, which
# exists but does not run Python, so each candidate is run, not just looked up.

PYTHON=()
for candidate in "python3" "python" "py -3"; do
    read -r -a cmd <<< "$candidate"
    command -v "${cmd[0]}" > /dev/null 2>&1 || continue
    if "${cmd[@]}" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' > /dev/null 2>&1; then
        PYTHON=("${cmd[@]}")
        break
    fi
done
