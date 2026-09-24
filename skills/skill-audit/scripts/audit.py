#!/usr/bin/env python3
"""Run the whole skill audit into one out dir and print a short summary.

Usage: audit.py [--out DIR]   (default ~/.cache/skill-audit/<today>/)
Report only: nothing here moves, archives, or deletes a skill.
"""
import collections
import csv
import json
import os
import re
import subprocess
import sys

from _common import parse_out

OUT = parse_out(__doc__.splitlines()[0])
HERE = os.path.dirname(os.path.abspath(__file__))

for s in ('usage.py', 'inventory.py', 'extract_messages.py', 'cluster_patterns.py'):
    subprocess.run([sys.executable, os.path.join(HERE, s), '--out', OUT], check=True)

usage = list(csv.DictReader(open(OUT + '/skill_usage.csv')))
inv = list(csv.DictReader(open(OUT + '/skills_inventory.csv')))
meta = json.load(open(OUT + '/usage_meta.json'))
N = lambda r, k: int(r[k] or 0)


def rng(x):
    return f'{(x[0] or "?")[:10]}..{(x[1] or "?")[:10]}'


print(f'\n=== skill audit -> {OUT}')
print(f'log window: Claude {rng(meta["cl_range"])} ({meta["n_claude_files"]} transcripts, pruned: older history is gone), '
      f'Codex {rng(meta["cx_range"])} ({meta["n_codex_files"]} sessions, {meta["exec_files"]} headless exec)')

print('\n-- top used (total = claude model+slash + codex mention+read; codex reads are not proof of use)')
for r in usage[:10]:
    cx = N(r, 'codex_user_mention') + N(r, 'codex_agent_read')
    print(f'  {r["skill"]:32} {N(r, "total"):5}  claude={N(r, "claude_model") + N(r, "claude_slash")} '
          f'codex={cx} (in exec runs: {N(r, "codex_uses_in_exec_runs")})  last={r["last_used"]}')

tot = {r['skill']: N(r, 'total') for r in usage}
never = sorted({r['dir_name'] for r in inv if r['source'] not in ('stray file', 'BROKEN symlink')
                and tot.get(r['dir_name'], 0) == 0})
print(f'\n-- installed skills never used in the log window: {len(never)}')
print('  ' + ', '.join(never))

by_name = collections.defaultdict(set)
for r in inv:
    if r['source'] not in ('stray file', 'BROKEN symlink'):
        by_name[r['fm_name'] or r['dir_name']].add(r['real_path'])
dups = {k: v for k, v in by_name.items() if len(v) > 1}
print(f'\n-- duplicates (same name, different real copies): {len(dups)}')
for k, v in sorted(dups.items()):
    print(f'  {k}: ' + ' | '.join(sorted(v)))
broken = [r for r in inv if r['source'] == 'BROKEN symlink']
stray = [r for r in inv if r['source'] == 'stray file']
print(f'\n-- broken symlinks: {len(broken)}' + ''.join(f'\n  {r["link_paths"]}' for r in broken))
print(f'-- stray files in skill dirs: {len(stray)}' + ''.join(f'\n  {r["real_path"]}' for r in stray))

live = [r for r in inv if r['disable_model_invocation'].lower() != 'true' and r['source'] not in ('stray file', 'BROKEN symlink')]
chars = sum(N(r, 'desc_chars') for r in live)
per = collections.Counter()
for r in live:
    for a in r['linked_into'].split('+'):
        if a:
            per[a] += N(r, 'desc_chars')
print(f'\n-- description context cost: {len(live)} model-invocable skills, {chars} chars (~{chars // 4} tokens) '
      f'across all agents; by skills dir: ' + ', '.join(f'{a}={c}' for a, c in per.most_common()))
print('  longest: ' + ', '.join(f'{r["dir_name"]}={r["desc_chars"]}' for r in sorted(live, key=lambda r: -N(r, 'desc_chars'))[:5]))

print('\n-- top recurring user patterns (keyword buckets; overlapping, read samples in clusters.txt)')
hdrs = [l for l in open(OUT + '/clusters.txt') if l.startswith('## ')]
for l in hdrs[:8]:
    m = re.match(r'## (.*?): (\d+)  src=(\{.*?\})', l)
    print(f'  {m.group(2):>5}  {m.group(1)}  {m.group(3)}' if m else '  ' + l.strip())

print(f'\nfiles: {OUT}/{{skill_usage.csv,usage_meta.json,skills_inventory.csv,clusters.txt}}')
print(f'SENSITIVE: {OUT}/msgs.jsonl and dedup.json hold raw user messages (may include pasted secrets). '
      f'Never commit them; delete after the review: rm {OUT}/msgs.jsonl {OUT}/dedup.json')
