#!/usr/bin/env python3
"""Extract user-typed messages from Claude transcripts and Codex sessions.

Writes <out>/msgs.jsonl (every message) and <out>/dedup.json (the corpus cluster_patterns.py reads:
headless runs dropped -- Codex `codex exec` sessions and Claude sdk-cli entrypoints -- plus
Codex's own injected "agent history" review prompts, then identical records (same dir, day, text)
collapsed so resumed/forked sessions that replay history count once; genuine repeats on
other days or in other dirs are kept, since recurrence is the signal).

SENSITIVE: this corpus is raw user text and can contain pasted secrets. Keep it under
~/.cache, never commit it, and delete msgs.jsonl + dedup.json after the review.
"""
import glob
import json
import os
import re

from _common import H, parse_out

OUT = parse_out(__doc__.splitlines()[0])


def clean(t):
    t = re.sub(r'<system-reminder>.*?</system-reminder>', '', t, flags=re.S)
    t = re.sub(r'<(local-command-\w+|command-\w+|bash-\w+|task-notification|user-prompt-submit-hook)>.*?</\1>', '', t,
               flags=re.S)
    return t.strip()


msgs = []
for f in glob.glob(H + '/.claude/projects/*/*.jsonl'):
    proj = os.path.basename(os.path.dirname(f))
    for l in open(f, errors='ignore'):
        if '"type":"user"' not in l:
            continue
        try:
            d = json.loads(l)
        except Exception:
            continue
        if d.get('type') != 'user' or d.get('isSidechain') or d.get('isMeta'):
            continue
        c = (d.get('message') or {}).get('content')
        if isinstance(c, list):
            c = ' '.join(x.get('text', '') for x in c if isinstance(x, dict) and x.get('type') == 'text')
        if not isinstance(c, str):
            continue
        if c.startswith('[Request interrupted') or 'This session is being continued' in c[:200] or c.startswith('Caveat:'):
            continue
        m = re.search(r'<command-name>(.*?)</command-name>', c); a = re.search(r'<command-args>(.*?)</command-args>', c, re.S)
        t = clean(c)
        if m:  # keep typed slash commands as "/name args"
            t = (m.group(1) + ' ' + (a.group(1) if a else '')).strip()
        if not t:
            continue
        msgs.append({'src': 'claude', 'proj': proj, 'cwd': d.get('cwd'), 'ts': (d.get('timestamp') or '')[:10],
                     'text': t, 'ent': d.get('entrypoint')})
for f in glob.glob(H + '/.codex/sessions/**/*.jsonl', recursive=True):
    orig = None; cwd = None
    for i, l in enumerate(open(f, errors='ignore')):
        if i == 0:
            try:
                p = json.loads(l)['payload']; orig = p.get('originator'); cwd = p.get('cwd')
            except Exception:
                pass
            continue
        if '"user_message"' not in l[:200]:
            continue
        try:
            d = json.loads(l)
        except Exception:
            continue
        p = d.get('payload', {})
        if p.get('type') != 'user_message':
            continue
        t = clean(p.get('message', ''))
        if not t:
            continue
        msgs.append({'src': 'codex', 'orig': orig, 'cwd': cwd, 'ts': (d.get('timestamp') or '')[:10], 'text': t})

with open(OUT + '/msgs.jsonl', 'w') as fh:
    for r in msgs:
        fh.write(json.dumps(r) + '\n')
seen = set(); dedup = []
for r in msgs:
    if r.get('orig') == 'codex_exec' or r.get('ent') == 'sdk-cli':
        continue
    if r['text'].startswith('The following is the Codex agent history'):
        continue
    k = json.dumps(r, sort_keys=True)
    if k in seen:
        continue
    seen.add(k); dedup.append(r)
with open(OUT + '/dedup.json', 'w') as fh:
    json.dump(dedup, fh)
print(f'messages: {len(msgs)} extracted, {len(dedup)} after dropping headless runs + duplicates -> {OUT}/dedup.json')
