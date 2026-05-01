---
name: shell
description: Writes, reviews, and hardens Bash scripts at production standards. Triggers when Claude writes Bash/shell scripts, automation scripts, Linux CLI tools, or edits .sh/.bash files. Covers strict mode, quoting discipline, trap-based cleanup, argument parsing, and safe subshell/IFS handling.
when_to_use: Auto-trigger when the user asks to write, review, or debug shell scripts. Invoke explicitly for CLI hardening or strict-mode migration.
paths:
  - "**/*.sh"
  - "**/*.bash"
---

# Shell Script Patterns

Turns Claude into a defensive Bash author: enforces strict mode, quotes every expansion, installs cleanup traps, and refuses the unsafe idioms (eval, unquoted globs, `cat | grep`) that silently break in production.

**Freedom level: High** — Shell tasks admit many valid approaches. The skill directs tactics with principles, not step-by-step recipes.

## 1. Strict Mode Or Nothing

**Every script starts with `set -euo pipefail` and a locked-down IFS.**

- Header is non-negotiable: `#!/usr/bin/env bash`, `set -euo pipefail`, `IFS=$'\n\t'`.
- Add `set -E` when functions use `trap ... ERR` — without it the trap is not inherited.
- Never silence errors with `|| true` unless you immediately check the status and explain why.
- Copy `scripts/strict-template.sh` as the starting point for any new script.

## 2. Quote Every Variable

**Unquoted expansions are bugs waiting for a filename with a space.**

- `cp "$src" "$dst"` — always. Including inside `[[ ... ]]`, arithmetic, and here-strings.
- Arrays: `"${arr[@]}"` (each element separately) — never `${arr[*]}` unless you want one joined string.
- `"$@"` to forward all args; `"$*"` only for display.
- "Parsing `ls`" → "`find` with `-print0` piped to `xargs -0`" or `for f in *.ext; do`.

## 3. Fail Fast Trap Always

**Install cleanup on EXIT before creating any resource.**

- `trap cleanup EXIT` must be set before `mktemp`, `mkdir -p /tmp/x`, or any lockfile.
- Preserve the exit code: `cleanup() { local rc=$?; rm -f "$TMP"; exit "$rc"; }`.
- Fail loudly at dependency boundaries: `command -v jq >/dev/null || die "jq required"`.
- `die() { echo "Error: $*" >&2; exit "${2:-1}"; }` — standard across every script.

## 4. Functions Over Copy-Paste

**Factor repeated logic into named functions with `local` variables.**

- Verb-based names: `parse_args`, `validate_inputs`, `process_file`. Avoid `doit`.
- All function variables are `local` — unscoped vars leak into the parent shell.
- One `main "$@"` at the bottom; no logic at file scope except sourcing and constants.
- Scripts over ~200 lines or reused from multiple callers: split into a library sourced via `. "$(dirname "$0")/lib.sh"`.

## Quick reference

| Need | Use | Why |
|---|---|---|
| Parse short + long options | `while [[ $# -gt 0 ]]; case "$1" in ... esac` | Works everywhere, supports `--opt=val`, clearer than `getopts` |
| Exit-on-error + cleanup | `set -euo pipefail` + `trap cleanup EXIT` | Catches unset vars, pipeline failures, and leaked tempfiles |
| Log line (info/warn/error) | `log_info(){ echo "[INFO]  $*" >&2; }` | Stderr for messages, stdout for data — composes with pipes |
| Read file lines safely | `while IFS= read -r line; do ... done < "$f"` | Preserves whitespace, no word splitting, no glob expansion |
| Temp files / dirs | `TMP="$(mktemp)"; trap 'rm -f "$TMP"' EXIT` | Safe names, auto-cleanup, works under `set -e` |

## Anti-patterns

| Pattern | Fix |
|---|---|
| Missing `set -euo pipefail` | Add to every script; copy `scripts/strict-template.sh` |
| Unquoted `$var` or `$(cmd)` | `"$var"` / `"$(cmd)"` — including inside `[[ ]]` |
| `eval "$user_input"` | Never. Use arrays or `printf -v` for dynamic construction |
| `cat file \| grep pat` | `grep pat file` — no useless `cat` |
| Parsing `ls` output | `for f in *.ext` or `find ... -print0 \| xargs -0` |
| No cleanup trap on tempfiles | `trap 'rm -f "$TMP"' EXIT` set before `mktemp` |
| `[ $x = "y" ]` with `sh`-style single brackets | `[[ "$x" == "y" ]]` — no word-split, supports `=~` |
| Mixing stdout data with log messages | Log to `>&2`; stdout is data only |

## Troubleshooting

| Symptom | Fix |
|---|---|
| `unbound variable` under `set -u` | Use `"${var:-}"` for optional; `"${var:?msg}"` to require |
| Variable set in pipeline is empty after | Pipeline runs subshell; use `< <(cmd)` process substitution or `shopt -s lastpipe` |
| `for f in $files` breaks on spaces | Store paths in an array: `files=(*.ext); for f in "${files[@]}"` |
| Trap fires but exit code is 0 | Capture first in cleanup: `local rc=$?; ...; exit "$rc"` |
| `read` in a loop loses the last line | File missing trailing newline — use `while IFS= read -r line \|\| [[ -n "$line" ]]` |
| `$(< file)` strips trailing newlines | Expected Bash behavior; use `mapfile -t lines < file` to preserve structure |
| `cd` inside script changes caller's dir | It does not — scripts run in subshell; use `source` only if intentional |
| Glob returns literal `*.ext` when no match | `shopt -s nullglob` (empty expansion) or check `[[ -e "$f" ]]` before using |
| IFS changes leak between functions | Set `local IFS=...` inside the function, not globally |
| `exit` inside sourced script kills caller | Use `return` in sourced libs; reserve `exit` for top-level scripts |

## Checklist

- [ ] `#!/usr/bin/env bash` shebang (not `/bin/sh`, not `/bin/bash`)
- [ ] `set -euo pipefail` + `IFS=$'\n\t'` at the top
- [ ] Every variable expansion quoted: `"$var"`, `"${arr[@]}"`, `"$@"`
- [ ] `trap cleanup EXIT` installed before any `mktemp` / lockfile
- [ ] `command -v <dep> >/dev/null \|\| die` for each external binary
- [ ] `--help` flag returns 0 and prints usage
- [ ] Functions use `local` for all internal variables
- [ ] Log messages go to `>&2`; stdout is data only
- [ ] `bash -n script.sh` passes syntax check
- [ ] `shellcheck script.sh` reports no warnings (or only intentional `# shellcheck disable=CODE`)
- [ ] No `eval` on any input that could come from a user, file, or network

## References

- `scripts/strict-template.sh` — copy as starting point. Shebang, strict mode, IFS, `die`/log helpers, arg parser with `--help`, cleanup trap. Run `./strict-template.sh --help` to preview.
- `references/argparse-advanced.md` — `getopt`/`getopts`/manual parsing trade-offs, long options with values, subcommand dispatch. Read when the default template parser is insufficient.

## Cross-references

| Skill | When |
|---|---|
| `cicd` | Shell scripts inside GitHub Actions, pre-commit hooks |
| `docker` | ENTRYPOINT/CMD scripts, healthchecks |
| `python` | Porting a grown-over-200-line script to Python |
