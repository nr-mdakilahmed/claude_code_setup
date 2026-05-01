#!/usr/bin/env bash
#
# validate-ingestion-yaml.sh — quick structural check of an OpenMetadata
# ingestion workflow YAML before shipping it to a runner.
#
# Checks performed:
#   1. File exists and is valid YAML (via python3 + PyYAML).
#   2. Top-level keys `source`, `sink`, `workflowConfig` are present.
#   3. `source.type` and `source.serviceName` are set.
#   4. `sink.type` is `metadata-rest`.
#   5. `workflowConfig.openMetadataServerConfig.hostPort` is set.
#   6. `serviceName` matches FQN-safe characters: [A-Za-z0-9_-].
#
# Exit codes:
#   0 — valid
#   1 — usage error / file not found / invalid YAML / missing field
#
# Usage: validate-ingestion-yaml.sh --file <path>

set -euo pipefail

print_help() {
  cat <<'EOF'
validate-ingestion-yaml.sh — validate an OpenMetadata ingestion YAML

USAGE:
  validate-ingestion-yaml.sh --file <path>
  validate-ingestion-yaml.sh --help

OPTIONS:
  --file <path>   Path to the ingestion YAML file. Required.
  --help          Print this message and exit 0.

EXAMPLES:
  validate-ingestion-yaml.sh --file ingestion/snowflake-metadata.yaml
EOF
}

FILE=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --file)
      FILE="${2:-}"
      shift 2
      ;;
    --help|-h)
      print_help
      exit 0
      ;;
    *)
      echo "error: unknown argument: $1" >&2
      print_help >&2
      exit 1
      ;;
  esac
done

if [[ -z "$FILE" ]]; then
  echo "error: --file is required" >&2
  print_help >&2
  exit 1
fi

if [[ ! -f "$FILE" ]]; then
  echo "error: file not found: $FILE" >&2
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "error: python3 not found on PATH" >&2
  exit 1
fi

python3 - "$FILE" <<'PY'
import re
import sys

try:
    import yaml
except ImportError:
    sys.stderr.write("error: PyYAML not installed. Run: pip install pyyaml\n")
    sys.exit(1)

path = sys.argv[1]

try:
    with open(path) as fh:
        doc = yaml.safe_load(fh)
except yaml.YAMLError as exc:
    sys.stderr.write(f"error: invalid YAML in {path}: {exc}\n")
    sys.exit(1)

if not isinstance(doc, dict):
    sys.stderr.write(f"error: {path} top level must be a mapping\n")
    sys.exit(1)

errors = []

for key in ("source", "sink", "workflowConfig"):
    if key not in doc:
        errors.append(f"missing top-level key: {key}")

src = doc.get("source") or {}
if isinstance(src, dict):
    if not src.get("type"):
        errors.append("source.type is required")
    service_name = src.get("serviceName")
    if not service_name:
        errors.append("source.serviceName is required")
    elif not re.fullmatch(r"[A-Za-z0-9_\-]+", str(service_name)):
        errors.append(
            f"source.serviceName '{service_name}' must match [A-Za-z0-9_-] "
            "(used as FQN prefix)"
        )

sink = doc.get("sink") or {}
if isinstance(sink, dict):
    if sink.get("type") != "metadata-rest":
        errors.append("sink.type must be 'metadata-rest'")

wfc = doc.get("workflowConfig") or {}
om = (wfc.get("openMetadataServerConfig") or {}) if isinstance(wfc, dict) else {}
if not om.get("hostPort"):
    errors.append("workflowConfig.openMetadataServerConfig.hostPort is required")

if errors:
    sys.stderr.write(f"invalid: {path}\n")
    for err in errors:
        sys.stderr.write(f"  - {err}\n")
    sys.exit(1)

print(f"ok: {path}")
PY
