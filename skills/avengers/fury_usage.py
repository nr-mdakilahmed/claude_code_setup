#!/usr/bin/env python3
"""
Compute EXACT token usage + cost for an avengers mission by parsing Claude Code transcript JSONLs.

Usage:
    python3 fury_usage.py <mission_start_epoch>            # prints JSON summary
    python3 fury_usage.py <mission_start_epoch> --pretty   # prints human-readable table
    python3 fury_usage.py --help

The mission_start_epoch is usually the TIMESTAMP suffix of the team name (e.g. 1777447817).
Set to 0 to tally the entire session history.

Sources:
- Main session JSONL: ~/.claude/projects/<proj>/<session-id>.jsonl (Fury's turns)
- Per-agent JSONLs:   ~/.claude/projects/<proj>/<session-id>/subagents/agent-<id>.jsonl

Each assistant turn has a `message.usage` block with real counts:
  input_tokens, output_tokens, cache_creation_input_tokens, cache_read_input_tokens

Cost = input * rate_in + output * rate_out + cache_write * rate_cw + cache_read * rate_cr  (per M)
"""

import json
import os
import sys
import glob
import pathlib
from datetime import datetime, timezone

# Prices per 1,000,000 tokens (USD) — Anthropic public pricing
# cache_write_5m is 1.25x input; cache_read is 0.10x input
PRICING = {
    'claude-opus-4-7':   {'input': 15.0, 'output': 75.0, 'cache_write': 18.75, 'cache_read': 1.50},
    'claude-opus-4-6':   {'input': 15.0, 'output': 75.0, 'cache_write': 18.75, 'cache_read': 1.50},
    'claude-opus-4':     {'input': 15.0, 'output': 75.0, 'cache_write': 18.75, 'cache_read': 1.50},
    'claude-sonnet-4-6': {'input':  3.0, 'output': 15.0, 'cache_write':  3.75, 'cache_read': 0.30},
    'claude-sonnet-4-5': {'input':  3.0, 'output': 15.0, 'cache_write':  3.75, 'cache_read': 0.30},
    'claude-sonnet-4':   {'input':  3.0, 'output': 15.0, 'cache_write':  3.75, 'cache_read': 0.30},
    'claude-haiku-4-5':  {'input':  1.0, 'output':  5.0, 'cache_write':  1.25, 'cache_read': 0.10},
    'claude-haiku-4':    {'input':  1.0, 'output':  5.0, 'cache_write':  1.25, 'cache_read': 0.10},
}

# Fallback for unknown variants — match prefix
def _resolve_price(model: str) -> dict:
    if model in PRICING:
        return PRICING[model]
    for key in PRICING:
        if model.startswith(key) or key.startswith(model.split('-20')[0]):
            return PRICING[key]
    # Coarse prefix fallback
    if 'opus' in model:   return PRICING['claude-opus-4']
    if 'haiku' in model:  return PRICING['claude-haiku-4']
    return PRICING['claude-sonnet-4']


def _parse_ts(raw) -> float:
    """Parse a JSONL timestamp (ISO string or epoch) to epoch seconds."""
    if raw is None:
        return 0.0
    if isinstance(raw, (int, float)):
        return float(raw)
    try:
        s = str(raw).replace('Z', '+00:00')
        return datetime.fromisoformat(s).timestamp()
    except Exception:
        return 0.0


def tally_jsonl(path: pathlib.Path, since_epoch: float, end_epoch: float | None = None) -> dict:
    """Sum tokens per model from an assistant-turn JSONL file.

    Filters entries to those with `since_epoch <= ts < end_epoch`. If end_epoch
    is None, the upper bound is unlimited (up to the present).
    """
    totals: dict[str, dict] = {}
    if not path.exists():
        return totals
    try:
        with path.open() as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    e = json.loads(line)
                except Exception:
                    continue
                if e.get('type') != 'assistant':
                    continue
                ts = _parse_ts(e.get('timestamp'))
                if ts < since_epoch:
                    continue
                if end_epoch is not None and ts >= end_epoch:
                    continue
                msg = e.get('message') or {}
                u = msg.get('usage') if isinstance(msg, dict) else None
                if not u:
                    continue
                model = msg.get('model') or 'unknown'
                bucket = totals.setdefault(model, {
                    'input': 0, 'output': 0, 'cache_write': 0, 'cache_read': 0, 'turns': 0,
                })
                bucket['input']       += u.get('input_tokens') or 0
                bucket['output']      += u.get('output_tokens') or 0
                bucket['cache_write'] += u.get('cache_creation_input_tokens') or 0
                bucket['cache_read']  += u.get('cache_read_input_tokens') or 0
                bucket['turns']       += 1
    except Exception as ex:
        totals['_error'] = {'path': str(path), 'error': str(ex)}
    return totals


def cost_for(totals: dict) -> tuple[float, int]:
    """Given a per-model totals dict, return (cost_usd, total_tokens)."""
    cost = 0.0
    total_tokens = 0
    for model, t in totals.items():
        if model == '_error':
            continue
        p = _resolve_price(model)
        cost += (t['input']       / 1e6) * p['input']
        cost += (t['output']      / 1e6) * p['output']
        cost += (t['cache_write'] / 1e6) * p['cache_write']
        cost += (t['cache_read']  / 1e6) * p['cache_read']
        total_tokens += t['input'] + t['output'] + t['cache_write'] + t['cache_read']
    return cost, total_tokens


def find_session_files(since_epoch: float) -> tuple[pathlib.Path | None, list[pathlib.Path]]:
    """Locate the active Claude Code session JSONL + subagent JSONLs modified after since_epoch."""
    root = pathlib.Path.home() / '.claude' / 'projects'
    if not root.exists():
        return None, []
    # Find the session JSONL with the latest mtime (the active one)
    jsonls = list(root.glob('*/*.jsonl'))
    if not jsonls:
        return None, []
    jsonls.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    session_file = jsonls[0]
    # Subagent transcripts live under <session-id>/subagents/
    session_id = session_file.stem
    subagents_dir = session_file.parent / session_id / 'subagents'
    subagent_files = []
    if subagents_dir.exists():
        for p in subagents_dir.glob('agent-*.jsonl'):
            if p.stat().st_mtime >= since_epoch:
                subagent_files.append(p)
    return session_file, subagent_files


def compute(mission_start_epoch: float, mission_end_epoch: float | None = None) -> dict:
    session_file, subagent_files = find_session_files(mission_start_epoch)
    result = {
        'mission_start_epoch': mission_start_epoch,
        'mission_end_epoch': mission_end_epoch,
        'session_file': str(session_file) if session_file else None,
        'fury': {'totals': {}, 'cost_usd': 0.0, 'total_tokens': 0},
        'subagents': [],
        'total_cost_usd': 0.0,
        'total_tokens': 0,
    }

    if session_file:
        fury_totals = tally_jsonl(session_file, mission_start_epoch, mission_end_epoch)
        fury_cost, fury_tokens = cost_for(fury_totals)
        result['fury'] = {
            'totals': fury_totals,
            'cost_usd': round(fury_cost, 4),
            'total_tokens': fury_tokens,
        }
        result['total_cost_usd'] += fury_cost
        result['total_tokens']   += fury_tokens

    for p in subagent_files:
        agent_id = p.stem.replace('agent-', '')
        sub_totals = tally_jsonl(p, mission_start_epoch, mission_end_epoch)
        sub_cost, sub_tokens = cost_for(sub_totals)
        if sub_tokens == 0:
            continue  # Agent had no turns in the window
        result['subagents'].append({
            'agent_id': agent_id,
            'file': str(p),
            'totals': sub_totals,
            'cost_usd': round(sub_cost, 4),
            'total_tokens': sub_tokens,
        })
        result['total_cost_usd'] += sub_cost
        result['total_tokens']   += sub_tokens

    result['total_cost_usd'] = round(result['total_cost_usd'], 4)
    return result


def pretty_print(r: dict) -> None:
    print(f"{'='*66}")
    print(f" Mission usage since epoch {int(r['mission_start_epoch'])}")
    print(f"{'='*66}")
    print(f" Session file: {r['session_file']}")
    print()
    print(f" FURY (main session, opus)")
    for model, t in r['fury']['totals'].items():
        if model == '_error':
            print(f"   ERROR: {t}")
            continue
        print(f"   {model}:")
        print(f"     turns={t['turns']:>4}  input={t['input']:>10,}  output={t['output']:>10,}")
        print(f"     cache_write={t['cache_write']:>10,}  cache_read={t['cache_read']:>10,}")
    print(f"   → tokens: {r['fury']['total_tokens']:,}    cost: ${r['fury']['cost_usd']:.4f}")
    print()
    print(f" SUBAGENTS ({len(r['subagents'])})")
    for sub in r['subagents']:
        print(f"   {sub['agent_id']}: {sub['total_tokens']:,} tok   ${sub['cost_usd']:.4f}")
        for model, t in sub['totals'].items():
            if model == '_error':
                continue
            print(f"     {model}: in={t['input']:,} out={t['output']:,} cr={t['cache_read']:,} cw={t['cache_write']:,}")
    print()
    print(f"{'='*66}")
    print(f" TOTAL:  {r['total_tokens']:,} tokens    ${r['total_cost_usd']:.4f}")
    print(f"{'='*66}")


def main():
    args = sys.argv[1:]
    if not args or args[0] in ('-h', '--help'):
        print(__doc__)
        sys.exit(0)
    try:
        since = float(args[0])
    except ValueError:
        print(f"Error: first arg must be an epoch number, got: {args[0]!r}")
        sys.exit(1)
    pretty = '--pretty' in args
    r = compute(since)
    if pretty:
        pretty_print(r)
    else:
        print(json.dumps(r, indent=2))


if __name__ == '__main__':
    main()
