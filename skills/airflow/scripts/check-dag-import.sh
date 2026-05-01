#!/usr/bin/env bash
# check-dag-import.sh — validate an Airflow DAG file parses and imports cleanly.
#
# Runs two checks:
#   1. AST parse via `python -c "import ast; ast.parse(open(path).read())"`
#   2. Full Python import (catches side-effect errors at module load)
#
# Exits 0 on success, non-zero with the traceback on failure.

set -euo pipefail

usage() {
  cat <<'EOF'
Usage: check-dag-import.sh --dag-file <path> [--help]

Validates an Airflow DAG file:
  1. Python AST parse (syntax check).
  2. Full import (catches ImportError, NameError at module load — the class of
     failures that cause DAGs to vanish from the Airflow UI).

Options:
  --dag-file <path>   Path to the DAG file to validate. Required.
  --help              Show this message and exit 0.

Example:
  bash check-dag-import.sh --dag-file dags/daily_etl.py
EOF
}

DAG_FILE=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --help|-h)
      usage
      exit 0
      ;;
    --dag-file)
      DAG_FILE="${2:-}"
      shift 2
      ;;
    *)
      echo "unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ -z "$DAG_FILE" ]]; then
  echo "error: --dag-file is required" >&2
  usage >&2
  exit 2
fi

if [[ ! -f "$DAG_FILE" ]]; then
  echo "error: file not found: $DAG_FILE" >&2
  exit 2
fi

echo "[1/2] AST parse: $DAG_FILE"
python3 -c "import ast, sys; ast.parse(open('$DAG_FILE').read(), filename='$DAG_FILE')"
echo "      ok"

echo "[2/2] Import module: $DAG_FILE"
# Execute the file in a fresh Python process so decorators and DAG()
# construction run. Errors here are what make the scheduler skip the DAG.
python3 -c "
import importlib.util, sys
spec = importlib.util.spec_from_file_location('dag_under_test', '$DAG_FILE')
if spec is None or spec.loader is None:
    print('error: could not load spec', file=sys.stderr)
    sys.exit(1)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
"
echo "      ok"

echo "DAG import check passed: $DAG_FILE"
