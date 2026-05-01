#!/usr/bin/env bash
#
# strict-template.sh — canonical starting point for new Bash scripts.
# Copy this file, rename it, and replace the body of `run` with your logic.
#
# Features:
#   - Strict mode (set -euo pipefail) + locked-down IFS
#   - ERR-trap-friendly (set -E) so traps are inherited by functions
#   - Standard logging (log_info / log_warn / log_error) to stderr
#   - `die` helper that preserves the caller's intent
#   - Cleanup trap on EXIT that preserves the exit code
#   - Argument parser with short + long flags and `--help`
#
# Usage:
#   ./strict-template.sh --help
#   ./strict-template.sh -v -o /tmp/out input.txt

set -Eeuo pipefail
IFS=$'\n\t'

readonly SCRIPT_NAME="$(basename "${BASH_SOURCE[0]}")"
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ---------- globals populated by parse_args ---------------------------------
VERBOSE=false
OUTPUT=""
INPUT=""
TMP_DIR=""

# ---------- logging ---------------------------------------------------------
log_info()  { echo "[INFO]  $*" >&2; }
log_warn()  { echo "[WARN]  $*" >&2; }
log_error() { echo "[ERROR] $*" >&2; }
die()       { log_error "$1"; exit "${2:-1}"; }

# ---------- cleanup ---------------------------------------------------------
cleanup() {
  local rc=$?
  [[ -n "${TMP_DIR:-}" && -d "$TMP_DIR" ]] && rm -rf "$TMP_DIR"
  exit "$rc"
}
trap cleanup EXIT

# ---------- help ------------------------------------------------------------
usage() {
  cat <<EOF
Usage: $SCRIPT_NAME [OPTIONS] INPUT

Process INPUT and write results to OUTPUT.

Options:
  -o, --output PATH   Output path (default: stdout)
  -v, --verbose       Enable verbose logging
  -h, --help          Show this message and exit

Examples:
  $SCRIPT_NAME input.txt
  $SCRIPT_NAME -v -o result.txt input.txt
EOF
}

# ---------- argument parser -------------------------------------------------
parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      -h|--help)    usage; exit 0 ;;
      -v|--verbose) VERBOSE=true; shift ;;
      -o|--output)
        [[ $# -ge 2 ]] || die "Option $1 requires an argument"
        OUTPUT="$2"; shift 2 ;;
      --output=*)   OUTPUT="${1#*=}"; shift ;;
      --)           shift; break ;;
      -*)           die "Unknown option: $1 (use --help)" ;;
      *)            INPUT="$1"; shift ;;
    esac
  done
  [[ -n "$INPUT" ]] || { usage >&2; die "INPUT is required"; }
}

# ---------- dependency checks ----------------------------------------------
require_deps() {
  local dep
  for dep in "$@"; do
    command -v "$dep" >/dev/null 2>&1 || die "Required command not found: $dep"
  done
}

# ---------- main work -------------------------------------------------------
run() {
  [[ -f "$INPUT" ]] || die "Input file not found: $INPUT"
  TMP_DIR="$(mktemp -d)"
  $VERBOSE && log_info "Working in $TMP_DIR, input=$INPUT, output=${OUTPUT:-<stdout>}"

  # Replace this block with your real logic.
  if [[ -n "$OUTPUT" ]]; then
    cp "$INPUT" "$OUTPUT"
    log_info "Wrote $OUTPUT"
  else
    cat "$INPUT"
  fi
}

main() {
  parse_args "$@"
  require_deps cat cp mktemp
  run
}

main "$@"
