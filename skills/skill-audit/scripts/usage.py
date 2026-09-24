#!/usr/bin/env python3
"""Count skill use from Claude transcripts and Codex sessions.

Writes <out>/skill_usage.csv and <out>/usage_meta.json.

Claude: Skill tool_use calls (model-invoked) + typed <command-name> slash commands.
Codex:  $skill injections in user messages + SKILL.md reads by the agent. A read is
        NOT proof of use, and headless `codex exec` runs are counted separately
        (codex_uses_in_exec_runs) because scripted runs inflate totals. Calls that
        touch >2 skills, apply patches, or sed -i are maintenance, not use.
"""
import collections
import csv
import glob
import itertools
import json
import os
import re

from _common import H, MAESTRO, listdir, parse_out

OUT = parse_out(__doc__.splitlines()[0])

# ---------- universe: every skill/command name that exists on disk ----------
uni = {}  # name -> set(sources)


def add(n, src):
    n = n.strip('/').removesuffix('.md')
    if n and not n.startswith('.') and not n.endswith('.zip') and n not in ('_archive', 'synced', 'README'):
        uni.setdefault(n, set()).add(src)


for d, src in [(H + '/.claude/skills', 'claude'), (H + '/.codex/skills', 'codex'), (H + '/.agents/skills', 'agents'),
               (H + '/.claude/commands', 'claude-cmd'), (MAESTRO + '/skills', 'maestro'),
               (MAESTRO + '/commands', 'maestro-cmd')]:
    for n in listdir(d):
        add(n, src)
for n in listdir(H + '/.codex/skills/.system'):
    add(n, 'codex-system')
for p in glob.glob(H + '/.claude/skills/synced/*/*/'):
    add(os.path.basename(p.rstrip('/')), 'synced')
for p in glob.glob(H + '/.claude/plugins/**/SKILL.md', recursive=True):
    add(os.path.basename(os.path.dirname(p)), 'plugin')


def norm(n):
    n = n.strip().lstrip('/$')
    return n.split(':')[-1]


# ---------- Claude ----------
cl_model = collections.Counter(); cl_slash = collections.Counter()
cl_dates = collections.defaultdict(list)
agent_types = collections.Counter(); workflow = collections.Counter()
seen = set(); cl_range = [None, None]
cmd_re = re.compile(r'<command-name>\s*/?([^<\s]+)\s*</command-name>')
files = glob.glob(H + '/.claude/projects/**/*.jsonl', recursive=True)
for f in files:
    with open(f, errors='replace') as fh:
        for line in fh:
            if '"Skill"' not in line and 'command-name' not in line and '"Agent"' not in line \
               and '"Task"' not in line and 'Workflow' not in line and '"timestamp"' not in line:
                continue
            try:
                d = json.loads(line)
            except Exception:
                continue
            ts = d.get('timestamp')
            if ts:
                if not cl_range[0] or ts < cl_range[0]: cl_range[0] = ts
                if not cl_range[1] or ts > cl_range[1]: cl_range[1] = ts
            m = d.get('message')
            if not isinstance(m, dict):
                continue
            c = m.get('content')
            if d.get('type') == 'assistant' and isinstance(c, list):
                for b in c:
                    if not isinstance(b, dict) or b.get('type') != 'tool_use':
                        continue
                    key = b.get('id')
                    if key in seen:  # resumed/forked sessions replay history
                        continue
                    seen.add(key)
                    nm = b.get('name'); inp = b.get('input') or {}
                    if nm == 'Skill':
                        s = norm(str(inp.get('skill', '')))
                        cl_model[s] += 1; cl_dates[s].append(ts)
                    elif nm in ('Agent', 'Task'):
                        agent_types[inp.get('subagent_type') or '(default)'] += 1
                    elif nm and 'Workflow' in nm:
                        workflow[nm] += 1
            elif d.get('type') == 'user' and not d.get('isSidechain'):
                if isinstance(c, str):
                    txt = c
                elif isinstance(c, list):
                    txt = ' '.join(b.get('text', '') for b in c if isinstance(b, dict))
                else:
                    txt = ''
                for s in cmd_re.findall(txt):
                    key = (d.get('uuid'), s)
                    if key in seen:
                        continue
                    seen.add(key)
                    s = norm(s)
                    cl_slash[s] += 1; cl_dates[s].append(ts)

# ---------- Codex ----------
cx_user = collections.Counter(); cx_read = collections.Counter(); cx_dev = collections.Counter()
cx_dates = collections.defaultdict(list); cx_range = [None, None]; cxseen = set()
skill_inj = re.compile(r'<skill>\s*<name>([^<]+)</name>')
skill_path = re.compile(r'skills/([A-Za-z0-9_.-]+)/SKILL\.md')
cx_sess = collections.defaultdict(set); cx_exec = collections.Counter(); exec_files = 0; cx_files = 0
for f in glob.glob(H + '/.codex/sessions/**/*.jsonl', recursive=True):
    cx_files += 1
    with open(f, errors='replace') as fh:
        first = fh.readline()
        is_exec = '"originator":"codex_exec"' in first[:5000] or '"source":"exec"' in first[:5000]
        exec_files += is_exec
        for line in itertools.chain([first], fh):
            if line.startswith('{"timestamp":"'):
                ts = line[14:38]
                if not cx_range[0] or ts < cx_range[0]: cx_range[0] = ts
                if not cx_range[1] or ts > cx_range[1]: cx_range[1] = ts
            if '<skill>' not in line and 'SKILL.md' not in line:
                continue
            try:
                d = json.loads(line)
            except Exception:
                continue
            p = d.get('payload') or {}
            if not isinstance(p, dict):
                continue
            ts = d.get('timestamp')
            t = p.get('type')
            if t == 'message' and p.get('role') == 'user':
                txt = json.dumps(p.get('content'))
                for s in skill_inj.findall(txt.replace('\\n', '\n')):
                    key = ('u', ts, s)  # forked/resumed sessions replay identical history
                    if key in cxseen:
                        continue
                    cxseen.add(key)
                    s = norm(s); cx_user[s] += 1; cx_dates[s].append(ts); cx_sess[s].add(f); cx_exec[s] += is_exec
            elif t in ('function_call', 'custom_tool_call', 'local_shell_call'):
                body = str(p.get('arguments') or p.get('input') or json.dumps(p.get('action')))
                key = ('c', p.get('call_id') or p.get('id'), ts)
                if key in cxseen:
                    continue
                cxseen.add(key)
                names = set(skill_path.findall(body))
                if not names:
                    continue
                # bulk listing/editing of many skills, or patches => skill maintenance, not use
                dev = len(names) > 2 or 'apply_patch' in body or '*** Begin Patch' in body or 'sed -i' in body
                for s in names:
                    s = norm(s)
                    if dev:
                        cx_dev[s] += 1
                    else:
                        cx_read[s] += 1; cx_dates[s].append(ts); cx_sess[s].add(f); cx_exec[s] += is_exec

# ---------- report ----------
allnames = set(uni) | set(cl_model) | set(cl_slash) | set(cx_user) | set(cx_read)
rows = []
for n in allnames:
    inu = n in uni
    tot = cl_model[n] + cl_slash[n] + cx_user[n] + cx_read[n]
    if not inu and tot == 0:
        continue
    ds = [x for x in cl_dates[n] + cx_dates[n] if x]
    rows.append(dict(skill=n, in_universe='yes' if inu else 'no (builtin/other)',
                     sources=','.join(sorted(uni.get(n, []))),
                     claude_model=cl_model[n], claude_slash=cl_slash[n],
                     codex_user_mention=cx_user[n], codex_agent_read=cx_read[n],
                     codex_maintenance_touches=cx_dev[n], codex_sessions=len(cx_sess[n]),
                     codex_uses_in_exec_runs=cx_exec[n], total=tot,
                     first_used=min(ds)[:10] if ds else '', last_used=max(ds)[:10] if ds else ''))
rows.sort(key=lambda r: (-r['total'], r['skill']))
fields = ['skill', 'in_universe', 'sources', 'claude_model', 'claude_slash', 'codex_user_mention', 'codex_agent_read',
          'codex_maintenance_touches', 'codex_sessions', 'codex_uses_in_exec_runs', 'total', 'first_used', 'last_used']
with open(OUT + '/skill_usage.csv', 'w', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=fields); w.writeheader(); w.writerows(rows)
with open(OUT + '/usage_meta.json', 'w') as fh:
    json.dump(dict(cl_range=cl_range, cx_range=cx_range, n_claude_files=len(files), n_codex_files=cx_files,
                   exec_files=exec_files, agent_types=agent_types.most_common(), workflow=workflow.most_common(),
                   cl_slash_top=cl_slash.most_common(60)), fh, indent=1)
print(f'usage: {len(rows)} rows -> {OUT}/skill_usage.csv')
