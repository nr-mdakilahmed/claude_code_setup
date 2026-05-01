# Advanced Argument Parsing

Read when `scripts/strict-template.sh`'s default `while/case` parser is insufficient — subcommand dispatch, GNU-style long options with optional values, cluster flags, or portability beyond Bash.

## Contents

- Parser choice (decision table)
- `getopts` — POSIX, short options only
- `getopt` — GNU, supports long options but non-portable
- Manual `while/case` — the template default, when to extend it
- Long options with values (`--opt=value` and `--opt value`)
- Subcommand dispatch (`git`-style)
- Cluster flags (`-abc` → `-a -b -c`)
- End-of-options marker (`--`)

## Parser choice

| Need | Use |
|---|---|
| Short flags only, POSIX portability | `getopts` (builtin) |
| Long flags (`--verbose`), Linux only | GNU `getopt` (external) |
| Long + short flags, cross-platform | Manual `while/case` (template default) |
| Subcommands (`tool build`, `tool test`) | Manual dispatch; see below |

## `getopts` — short options, POSIX

Bash builtin. Works everywhere. No long options, no optional argument values.

```bash
while getopts ":ho:v" opt; do
  case "$opt" in
    h) usage; exit 0 ;;
    o) OUTPUT="$OPTARG" ;;
    v) VERBOSE=true ;;
    \?) die "Unknown option: -$OPTARG" ;;
    :)  die "Option -$OPTARG requires an argument" ;;
  esac
done
shift $((OPTIND - 1))
```

Leading `:` in the optstring enables the `:` case for missing argument values.

## `getopt` — GNU, long options

External binary. macOS ships BSD `getopt` which does not support long options — on macOS install GNU getopt via `brew install gnu-getopt`.

```bash
PARSED="$(getopt -o ho:v --long help,output:,verbose -n "$SCRIPT_NAME" -- "$@")" || exit 2
eval set -- "$PARSED"
while true; do
  case "$1" in
    -h|--help)    usage; exit 0 ;;
    -o|--output)  OUTPUT="$2"; shift 2 ;;
    -v|--verbose) VERBOSE=true; shift ;;
    --)           shift; break ;;
  esac
done
```

Do not ship this for Mac/Linux portability. Prefer the manual parser.

## Manual `while/case` — template default

See `scripts/strict-template.sh`. Extensions you might need:

### Long option with `=value` form

```bash
--output=*) OUTPUT="${1#*=}"; shift ;;
--output)   OUTPUT="${2:?--output requires a value}"; shift 2 ;;
```

### Optional value (`--log` or `--log=DEBUG`)

```bash
--log)       LOG_LEVEL="INFO"; shift ;;
--log=*)     LOG_LEVEL="${1#*=}"; shift ;;
```

### Repeatable option (`-I path -I path`)

```bash
INCLUDES=()
# inside the parser loop:
-I|--include) INCLUDES+=("$2"); shift 2 ;;
# later:
for inc in "${INCLUDES[@]}"; do ...; done
```

### Cluster short flags (`-abc` → `-a -b -c`)

Not supported by the default template (to keep it simple). If you need it, preprocess:

```bash
args=()
for a in "$@"; do
  if [[ "$a" =~ ^-[a-zA-Z]{2,}$ ]]; then
    for ((i=1; i<${#a}; i++)); do args+=("-${a:$i:1}"); done
  else
    args+=("$a")
  fi
done
set -- "${args[@]}"
```

## Subcommand dispatch

Pattern for `tool <subcommand> [options]`:

```bash
main() {
  [[ $# -ge 1 ]] || { usage >&2; exit 2; }
  local subcmd="$1"; shift
  case "$subcmd" in
    build) cmd_build "$@" ;;
    test)  cmd_test  "$@" ;;
    deploy) cmd_deploy "$@" ;;
    -h|--help) usage; exit 0 ;;
    *) die "Unknown subcommand: $subcmd" ;;
  esac
}

cmd_build() {
  local target=""
  while [[ $# -gt 0 ]]; do
    case "$1" in
      -t|--target) target="$2"; shift 2 ;;
      -h|--help)   build_usage; exit 0 ;;
      *) die "Unknown build option: $1" ;;
    esac
  done
  # ... build logic
}
```

Each subcommand has its own parser and its own `--help`.

## End-of-options marker

Honor `--` to let users pass filenames that begin with `-`:

```bash
--) shift; break ;;   # stop parsing; remaining args are positional
```

After the parser loop, `"$@"` contains the positional args — quote it when forwarding: `process "$@"`.
