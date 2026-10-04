#!/usr/bin/env python3
"""Claude Code Stop hook for the goal-loop skill.

Does nothing unless the session's cwd (or a parent) has .goal/state.json with status "running".
When it does, it blocks the stop and tells the agent to continue the loop, until goalctl moves the
status to a terminal state, the budget/deadline runs out, or the agent stops STALL_LIMIT times in a
row without completing an iteration (a safety valve against a stuck loop).

Escape hatches for the user: `touch .goal/PAUSE`, or `goalctl.py pause --reason ...`.
"""
import json
import os
import sys
import time
from pathlib import Path

STALL_LIMIT = 3
GOALCTL = Path(__file__).resolve().parent / "goalctl.py"


def find_root(start):
    p = Path(start).resolve()
    for d in [p] + list(p.parents):
        if (d / ".goal" / "state.json").exists():
            return d
    return None


def fmt(x):
    return "n/a" if x is None else ("%g" % x if isinstance(x, (int, float)) else str(x))


def main():
    inp = json.load(sys.stdin)
    root = find_root(inp.get("cwd") or os.getcwd())
    if not root:
        return
    path = root / ".goal" / "state.json"
    st = json.loads(path.read_text())
    if st.get("status") != "running" or (root / ".goal" / "PAUSE").exists():
        return
    sid = inp.get("session_id")
    if st.get("session_id") and sid and st["session_id"] != sid:
        return  # another session owns this loop
    st["session_id"] = st.get("session_id") or sid

    hook = st.setdefault("hook", {})
    it = st.get("iteration", 0)
    if hook.get("last_seen_iteration") == it:
        hook["stalls"] = hook.get("stalls", 0) + 1
    else:
        hook["last_seen_iteration"], hook["stalls"] = it, 0

    def finish(status, reason):
        st["status"], st["reason"] = status, reason
        path.write_text(json.dumps(st, indent=2))
        with open(root / ".goal" / "LOG.md", "a") as f:
            f.write("**%s — stopped by hook: %s** (%s)\n\n" % (time.strftime("%Y-%m-%d %H:%M"), status, reason))
        print(json.dumps({"systemMessage": "goal-loop: stopped (%s: %s)" % (status, reason)}))

    if hook["stalls"] >= STALL_LIMIT:
        return finish("stalled", "agent ended %d turns in a row without completing an iteration" % STALL_LIMIT)
    if st.get("deadline") and time.time() > st["deadline"]:
        return finish("budget_exhausted", "deadline passed")

    path.write_text(json.dumps(st, indent=2))
    goalctl = 'python3 "%s"' % GOALCTL
    reason = (
        "[goal-loop] Goal '{slug}' is still running: iteration {it}/{max}, best {best} (baseline {base}, target {target}), "
        "{sb}/{pat} iterations since last improvement. Keep going: re-read .goal/GOAL.md if unsure of the goal, check "
        ".goal/LOG.md for what has already been tried, make ONE focused change, then run "
        "`{g} iterate --desc \"<what you changed and why>\"`. If you truly need a decision only the user can make, run "
        "`{g} block --reason \"<question>\"` and then stop. If the user asked you to pause, run `{g} pause --reason ...`."
    ).format(slug=st.get("slug"), it=it, max=st.get("max_iterations"), best=fmt(st.get("best_score")),
             base=fmt(st.get("baseline_score")), target=fmt(st.get("target")) if st.get("target") is not None else "all checks pass",
             sb=st.get("since_best", 0), pat=st.get("patience"), g=goalctl)
    if hook["stalls"]:
        reason += " (Warning: you stopped without completing an iteration; %d more and the loop is marked stalled.)" % (
            STALL_LIMIT - hook["stalls"])
    print(json.dumps({"decision": "block", "reason": reason}))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:  # never break the user's session because of this hook
        print("goal-loop stop hook error: %s" % e, file=sys.stderr)
    sys.exit(0)
