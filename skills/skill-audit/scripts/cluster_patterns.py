#!/usr/bin/env python3
"""Bucket the extracted user messages into recurring intents and corrections.

Reads <out>/dedup.json (from extract_messages.py), writes <out>/clusters.txt: one header per
bucket (count, per-source split, date range, top working dirs) and up to 25 sample messages.
Buckets are keyword regexes, so they overlap and over-match; treat counts as a ranking, and
read the samples before concluding anything.
"""
import collections
import json
import random
import re

from _common import H, parse_out

OUT = parse_out(__doc__.splitlines()[0])

P = {
    'push/commit': r'\b(push|commit)\b',
    'merge/branch/PR': r'\b(merge|new branch|pull request|\bpr\b|merge on green)',
    'recap/status/where are we': r'(recap|where (are|we are|things are|are things)|status (update|report)|progress|how\'?s it look|update (on|of) where|overview of where|where we\'?re at)',
    'what next / next steps': r'(what\'?s next|whats next|next step|what should (come|be|i do)|roadmap)',
    'give me a prompt / handoff to other agent': r'(prompt for|give me (a|the) (next )?prompt|next prompt|dev agent|handoff|hand off|from the (dev|other) agent|claude said|codex said)',
    'explain simpler / clarify': r'(eli5|explain|what does .* mean|what do you mean|plain english|simpler|dumb it down|i don\'?t (follow|understand)|confused|elaborate)',
    'where in code / how does X work': r'(where (in the code|is .* in the code)|how does .* work|how do .* work)',
    'review report / run / dogfood / eval': r'(dogfood|\beval|latest run|report is in|test report|new run|run for today|update for today|smoke|baseline)',
    'manual inspection / step-by-step instructions for me': r'(manual (inspection|test)|step by step|what should i (do|check|test)|how do i (test|run|check))',
    'localhost / dev server / cant view': r'(localhost|dev server|can\'?t (view|see|open)|reestablish|port \d+)',
    'closeout / wrap up': r'(closeout|close out|wrap up|are we done|closeout checks)',
    'approve / go ahead': r'^(ok|okay|yes|yep|yeah|sure|great|perfect|approved|agreed|looks good)?[ ,.!]*(go ahead|go|proceed|implement|do it|continue|approved|yes please)\b',
    'UI nudge (px, shift, font, color)': r'(\bpx\b|shift it|font|padding|spacing|color|too (long|big|small)|align|fade|animation)',
    'bug still broken / not working': r'(still (not|broken|failing|seeing|doesn|isn|the same)|not (working|seeing)|doesn\'?t work|didn\'?t work|same (issue|error|problem)|again\b)',
    'correction: no/don\'t/stop': r'^(no\b|nope|stop\b|don\'?t\b|do not\b|wait\b)|\b(i said|i told you|i asked (you )?(to|for)|that\'?s not what|not what i (asked|meant|want)|you (forgot|missed|didn\'?t|broke|removed|changed)|why did you|why are you|why would you)',
    'scope/overcomplication pushback': r'(overkill|over.?engineer|too complicated|too complex|simpler|do we (even )?need|if we need them at all|keep it simple|just )',
    'verify / test before claiming': r'(did you (test|verify|check|run)|make sure (it|this|you)|double.?check|verify|actually (works|work|ran))',
    'docs / document it': r'(document (this|the|it)|update (the )?(docs|readme|roadmap|agents\.md|claude\.md)|write (it )?up)',
    'skill creation/meta': r'\bskills?\b',
    'second opinion / other agent review': r'(codex|claude).*(review|opinion|think|check)|(review|opinion).*(codex|claude)|duel|ensemble',
    'cost/speed/latency': r'(latency|cost|token|faster|slow|too long|taking forever|speed)',
    'obsidian/vault': r'(obsidian|vault|wiki)',
}
R = {k: re.compile(v, re.I) for k, v in P.items()}
res = {k: [] for k in P}
for r in json.load(open(OUT + '/dedup.json')):
    t = r['text']
    if len(t) > 1500:  # long pastes are prompts/reports, not typed intents
        continue
    for k, rx in R.items():
        if rx.search(t):
            res[k].append(r)
random.seed(1)
with open(OUT + '/clusters.txt', 'w') as out:
    for k, v in sorted(res.items(), key=lambda x: -len(x[1])):
        cw = collections.Counter((r.get('cwd') or r.get('proj') or '?').replace(H + '/', '') for r in v).most_common(4)
        src = collections.Counter(r['src'] for r in v)
        ts = sorted(r['ts'] for r in v)
        out.write(f'## {k}: {len(v)}  src={dict(src)} {ts[0] if ts else ""}..{ts[-1] if ts else ""} top={cw}\n')
        for r in random.sample(v, min(25, len(v))):
            out.write('  - ' + r['text'][:220].replace('\n', ' ') + '\n')
print(f'patterns: {len(P)} buckets -> {OUT}/clusters.txt')
