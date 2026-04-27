---
name: shell
description: >
  Use when writing Bash/shell scripts, automation scripts, or Linux CLI tools.
  Covers strict mode, variable handling, argument parsing, error handling,
  security, and function patterns. Auto-triggers for .sh/.bash files.
---

# Shell Script Patterns

## Script Template

```bash
#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

readonly SCRIPT_NAME="$(basename "$0")"
readonly SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

main() {
    parse_args "$@"
    validate_inputs
    do_work
}

main "$@"
```

## Strict Mode

```bash
set -euo pipefail  # Exit on error, undefined vars, pipe failures
set -E             # ERR traps inherited by functions
```

## Variables

```bash
# ALWAYS quote variables
cp "$file" "$destination"

# Defaults and required
name="${1:-default}"           # Default if unset
name="${1:?'Name required'}"   # Error if unset

# Manipulation
echo "${filename%.gz}"         # Remove suffix
echo "${filename##*.}"         # Extension only
echo "${string//old/new}"      # Replace all
```

## Naming

```bash
readonly MAX_RETRIES=3         # Constants: UPPER_SNAKE + readonly
local file_count=0             # Locals: lower_snake
process_file() { ... }         # Functions: lower_snake, verb-based
```

## Error Handling

```bash
cleanup() {
    local exit_code=$?
    [[ -n "${TEMP_FILE:-}" && -f "$TEMP_FILE" ]] && rm -f "$TEMP_FILE"
    exit "$exit_code"
}
trap cleanup EXIT

die() { echo "Error: $1" >&2; exit "${2:-1}"; }

command -v docker &>/dev/null || die "Docker required"
[[ -f "$config" ]] || die "Config not found: $config"
```

## Argument Parsing

```bash
parse_args() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -h|--help) usage; exit 0 ;;
            -v|--verbose) VERBOSE=true; shift ;;
            -o|--output)
                OUTPUT="${2:-}"
                [[ -n "$OUTPUT" ]] || die "-o requires argument"
                shift 2 ;;
            --) shift; break ;;
            -*) die "Unknown option: $1" ;;
            *) break ;;
        esac
    done
}
```

## Logging

```bash
log_info()  { echo "[INFO]  $*" >&2; }
log_warn()  { echo "[WARN]  $*" >&2; }
log_error() { echo "[ERROR] $*" >&2; }
# Data to stdout, messages to stderr
```

## Security

```bash
TEMP_FILE="$(mktemp)" || exit 1
trap 'rm -f "$TEMP_FILE"' EXIT

umask 077                              # Restrictive permissions
export PATH="/usr/local/bin:/usr/bin:/bin"  # Secure PATH
read -rs -p "Password: " password      # Read securely

# NEVER: eval "$user_input" or bash -c "process $user_input"
```

## Anti-Patterns

| Pattern | Fix |
|---|---|
| Unquoted variables | Always `"$var"` |
| No `set -euo pipefail` | Add to every script |
| `eval "$user_input"` | Never eval untrusted input |
| No cleanup trap | `trap cleanup EXIT` |
| Parsing `ls` output | Use `find` or globbing |
| `cat file \| grep` | `grep pattern file` |
| No error on missing command | `command -v X &>/dev/null \|\| die` |
