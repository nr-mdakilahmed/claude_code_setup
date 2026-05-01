#!/usr/bin/env bash
# detect-stack.sh — detect languages and frameworks in a repo
#
# Contract: emits JSON {"languages": [...], "frameworks": [...], "primary": "..."}
# to stdout. Pure filesystem inspection — no network, no writes.
#
# Usage:
#   detect-stack.sh --repo <path>
#   detect-stack.sh --help

set -euo pipefail

REPO=""

usage() {
  cat <<'EOF'
detect-stack.sh — detect languages and frameworks in a repo

Usage:
  detect-stack.sh --repo <path>
  detect-stack.sh --help

Options:
  --repo <path>   Absolute path to the repo root to inspect. Required.
  --help          Show this help and exit 0.

Output (stdout, JSON):
  {
    "languages": ["python", "yaml", "sql"],
    "frameworks": ["airflow", "pyspark", "dbt"],
    "primary": "python"
  }

Heuristics:
  python      pyproject.toml | requirements*.txt | setup.py | Pipfile
  node        package.json
  go          go.mod
  rust        Cargo.toml
  ruby        Gemfile
  java        pom.xml | build.gradle | build.gradle.kts
  airflow     dags/ dir | airflow.cfg | requirement has apache-airflow
  pyspark     requirement has pyspark | *.py with pyspark imports
  dbt         dbt_project.yml
  kafka       requirement has kafka | docker-compose references kafka
  snowflake   requirement has snowflake-connector-python or snowflake-snowpark-python
  bigquery    requirement has google-cloud-bigquery
  terraform   *.tf files present
  docker      Dockerfile | docker-compose.yml
  kubernetes  k8s/ or kubernetes/ dir | *.yaml with `kind:` root
  sql         *.sql files
  shell       *.sh files

Primary selection rule:
  First framework match wins; else first language match;
  else "unknown".

Exit codes:
  0  success (JSON written to stdout)
  1  argument or path error

Examples:
  detect-stack.sh --repo "$(pwd)"
  detect-stack.sh --repo /path/to/repo | jq '.primary'
EOF
}

# --- arg parsing ---------------------------------------------------------
while [[ $# -gt 0 ]]; do
  case "$1" in
    --help|-h)
      usage
      exit 0
      ;;
    --repo)
      REPO="${2:-}"
      shift 2
      ;;
    *)
      echo "detect-stack.sh: unknown argument: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

if [[ -z "$REPO" ]]; then
  echo "detect-stack.sh: --repo is required" >&2
  exit 1
fi

if [[ ! -d "$REPO" ]]; then
  echo "detect-stack.sh: --repo path does not exist or is not a directory: $REPO" >&2
  exit 1
fi

REPO_ABS="$(cd "$REPO" && pwd)"

# --- language detection --------------------------------------------------
LANGUAGES=()

_has_file() {
  # Return 0 if any file in $REPO_ABS matches the pattern (first two levels only).
  local pattern="$1"
  find "$REPO_ABS" -maxdepth 3 -name "$pattern" -not -path '*/node_modules/*' \
    -not -path '*/.git/*' -not -path '*/.venv/*' -not -path '*/dist/*' \
    -not -path '*/build/*' -not -path '*/__pycache__/*' \
    -print -quit 2>/dev/null | grep -q .
}

_has_dir() {
  local dir="$1"
  [[ -d "$REPO_ABS/$dir" ]]
}

_grep_reqs() {
  # Grep requirements.txt / pyproject.toml / Pipfile for a pattern.
  local pattern="$1"
  local f
  for f in requirements.txt requirements-dev.txt requirements-prod.txt pyproject.toml Pipfile setup.py; do
    if [[ -f "$REPO_ABS/$f" ]] && grep -qiE "$pattern" "$REPO_ABS/$f" 2>/dev/null; then
      return 0
    fi
  done
  return 1
}

if _has_file 'pyproject.toml' || _has_file 'requirements*.txt' || _has_file 'setup.py' || _has_file 'Pipfile'; then
  LANGUAGES+=("python")
fi
if _has_file 'package.json'; then
  LANGUAGES+=("node")
fi
if _has_file 'go.mod'; then
  LANGUAGES+=("go")
fi
if _has_file 'Cargo.toml'; then
  LANGUAGES+=("rust")
fi
if _has_file 'Gemfile'; then
  LANGUAGES+=("ruby")
fi
if _has_file 'pom.xml' || _has_file 'build.gradle' || _has_file 'build.gradle.kts'; then
  LANGUAGES+=("java")
fi
if _has_file '*.sql'; then
  LANGUAGES+=("sql")
fi
if _has_file '*.sh'; then
  LANGUAGES+=("shell")
fi
if _has_file '*.tf'; then
  LANGUAGES+=("hcl")
fi
if _has_file '*.yaml' || _has_file '*.yml'; then
  LANGUAGES+=("yaml")
fi

# --- framework detection -------------------------------------------------
FRAMEWORKS=()

if _has_dir 'dags' || _has_file 'airflow.cfg' || _grep_reqs 'apache-airflow'; then
  FRAMEWORKS+=("airflow")
fi
if _grep_reqs 'pyspark'; then
  FRAMEWORKS+=("pyspark")
fi
if _has_file 'dbt_project.yml'; then
  FRAMEWORKS+=("dbt")
fi
if _grep_reqs 'kafka' || { [[ -f "$REPO_ABS/docker-compose.yml" ]] && grep -qi 'kafka' "$REPO_ABS/docker-compose.yml" 2>/dev/null; }; then
  FRAMEWORKS+=("kafka")
fi
if _grep_reqs 'snowflake-connector-python|snowflake-snowpark-python|snowflake-sqlalchemy'; then
  FRAMEWORKS+=("snowflake")
fi
if _grep_reqs 'google-cloud-bigquery'; then
  FRAMEWORKS+=("bigquery")
fi
if _grep_reqs 'redshift-connector|sqlalchemy-redshift'; then
  FRAMEWORKS+=("redshift")
fi
if _has_file '*.tf'; then
  FRAMEWORKS+=("terraform")
fi
if _has_file 'Dockerfile*' || _has_file 'docker-compose*.yml' || _has_file 'docker-compose*.yaml'; then
  FRAMEWORKS+=("docker")
fi
if _has_dir 'k8s' || _has_dir 'kubernetes' || _has_dir 'helm'; then
  FRAMEWORKS+=("kubernetes")
fi
if _has_file '*.ipynb'; then
  FRAMEWORKS+=("jupyter")
fi

# --- primary selection ---------------------------------------------------
PRIMARY="unknown"
if [[ ${#FRAMEWORKS[@]} -gt 0 ]]; then
  PRIMARY="${FRAMEWORKS[0]}"
elif [[ ${#LANGUAGES[@]} -gt 0 ]]; then
  PRIMARY="${LANGUAGES[0]}"
fi

# --- emit JSON -----------------------------------------------------------
_to_json_array() {
  local arr=("$@")
  if [[ ${#arr[@]} -eq 0 ]]; then
    echo "[]"
    return
  fi
  printf '['
  local first=1
  local item
  for item in "${arr[@]}"; do
    if [[ $first -eq 1 ]]; then
      first=0
    else
      printf ','
    fi
    printf '"%s"' "$item"
  done
  printf ']'
}

LANG_JSON=$(_to_json_array "${LANGUAGES[@]+"${LANGUAGES[@]}"}")
FW_JSON=$(_to_json_array "${FRAMEWORKS[@]+"${FRAMEWORKS[@]}"}")

if command -v jq >/dev/null 2>&1; then
  jq -n \
    --argjson languages "$LANG_JSON" \
    --argjson frameworks "$FW_JSON" \
    --arg primary "$PRIMARY" \
    '{languages: $languages, frameworks: $frameworks, primary: $primary}'
else
  printf '{"languages":%s,"frameworks":%s,"primary":"%s"}\n' \
    "$LANG_JSON" "$FW_JSON" "$PRIMARY"
fi
