#!/usr/bin/env python3
"""Inventory every installed skill: where it really lives, which agents see it, and its description size.

Writes <out>/skills_inventory.csv. One row per real path (symlinks collapse onto their
target; link_paths lists every link). desc_chars is the always-loaded context cost.
Broken symlinks and stray files (zips etc.) get their own rows so they can be cleaned up.
"""
import csv
import glob
import json
import os
import re

from _common import AGENT_ROOTS, H, MAESTRO, listdir, parse_out

OUT = parse_out(__doc__.splitlines()[0])


def fm(p):
    t = open(p, encoding='utf-8', errors='replace').read()
    m = re.match(r'---\n(.*?)\n---', t, re.S); f = m.group(1) if m else ''

    def g(k):
        mm = re.search(r'^' + k + r':\s*(.*?)(?=^\S[\w-]*:|\Z)', f, re.S | re.M)
        if not mm:
            return ''
        v = mm.group(1).strip()
        v = re.sub(r'^[>|]-?\s*', '', v); v = ' '.join(v.split()).strip('"\'')
        return v
    return g('name'), g('description'), g('disable-model-invocation'), t.count('\n')


rows = {}
for ag, r in AGENT_ROOTS.items():
    for e in listdir(r):
        p = os.path.join(r, e)
        if e.startswith('.'):
            continue
        if os.path.islink(p) and not os.path.exists(p):
            rows[('BROKEN', p)] = {'name': e, 'real': p, 'agents': {ag}, 'via': [p + ' -> ' + os.readlink(p)],
                                   'src': 'BROKEN symlink'}
            continue
        if not os.path.isdir(p):
            rows[('STRAY', p)] = {'name': e, 'real': p, 'agents': set(), 'via': [], 'src': 'stray file'}
            continue
        if ag == 'claude' and e == 'synced':  # claude.ai-synced skills: synced/<bucket>/<name>/
            for sp in glob.glob(p + '/*/*/'):
                sp = sp.rstrip('/')
                rows[sp] = {'name': os.path.basename(sp), 'real': sp, 'agents': {'claude'}, 'via': [sp],
                            'src': 'claude.ai synced'}
            continue
        real = os.path.realpath(p)
        d = rows.setdefault(real, {'name': e, 'real': real, 'agents': set(), 'via': []})
        d['agents'].add(ag); d['via'].append(p + (' -> ' + os.readlink(p) if os.path.islink(p) else ''))
for sysd in glob.glob(H + '/.codex/skills/.system/*/'):
    sysd = sysd.rstrip('/')
    rows[sysd] = {'name': os.path.basename(sysd), 'real': sysd, 'agents': {'codex'}, 'via': [sysd],
                  'src': 'codex built-in (.system)'}
# installed Claude plugins only (the cache keeps old versions; marketplaces list uninstalled ones)
plugin_dirs = []
try:
    for recs in json.load(open(H + '/.claude/plugins/installed_plugins.json')).get('plugins', {}).values():
        for rec in recs:
            plugin_dirs += glob.glob(rec['installPath'] + '/skills/*/')
except (OSError, ValueError, KeyError):
    pass
plugin_dirs += glob.glob(H + '/.claude/plugins/synced/*/*/skills/*/')
for p in plugin_dirs:
    p = p.rstrip('/')
    rows[p] = {'name': os.path.basename(p), 'real': p, 'agents': {'claude'}, 'via': [p], 'src': 'plugin'}

out = []
for d in rows.values():
    real = d['real']; sk = os.path.join(real, 'SKILL.md')
    if 'src' not in d:
        if real.startswith(MAESTRO + '/'): d['src'] = 'maestro repo'
        elif real.startswith(H + '/.agents/'): d['src'] = '~/.agents third-party'
        elif real.startswith(H + '/.codex/'): d['src'] = '~/.codex local (unversioned)'
        elif real.startswith(H + '/.claude/'): d['src'] = '~/.claude local (unversioned)'
        else: d['src'] = 'other: ' + os.path.dirname(real)
    n, desc, dmi, lines = fm(sk) if os.path.isfile(sk) else ('', '', '', 0)
    cmd = os.path.exists(MAESTRO + '/commands/' + d['name'] + '.md')
    out.append([d['name'], n, real, '+'.join(sorted(d['agents'])), d['src'], dmi, lines, len(desc),
                'yes' if cmd else '', desc, ' | '.join(d['via'])])
out.sort(key=lambda r: (r[4], r[0]))
with open(OUT + '/skills_inventory.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['dir_name', 'fm_name', 'real_path', 'linked_into', 'source', 'disable_model_invocation',
                'skill_md_lines', 'desc_chars', 'maestro_command', 'description', 'link_paths'])
    w.writerows(out)
print(f'inventory: {len(out)} rows -> {OUT}/skills_inventory.csv')
