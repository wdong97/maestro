"""Shared paths and --out handling for the skill-audit scripts (stdlib only)."""
import argparse
import datetime
import os

H = os.path.expanduser('~')
# scripts/ -> skill-audit/ -> skills/ -> maestro repo root (resolves through install symlinks)
MAESTRO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
AGENT_ROOTS = {'claude': H + '/.claude/skills', 'codex': H + '/.codex/skills', 'agents': H + '/.agents/skills'}


def default_out():
    return os.path.join(H, '.cache', 'skill-audit', datetime.date.today().isoformat())


def parse_out(desc):
    ap = argparse.ArgumentParser(description=desc)
    ap.add_argument('--out', default=default_out(), help='output dir (default: ~/.cache/skill-audit/<today>/)')
    a = ap.parse_args()
    # The out dir can hold raw user messages (and any secrets pasted into them): owner-only.
    os.umask(0o077)
    os.makedirs(a.out, mode=0o700, exist_ok=True)
    os.chmod(a.out, 0o700)
    return a.out


def listdir(d):
    try:
        return sorted(os.listdir(d))
    except OSError:
        return []
