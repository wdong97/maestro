#!/usr/bin/env python3
"""goalctl: state, eval running, and keep/revert bookkeeping for the goal-loop skill.

All state lives in <project>/.goal/:
  GOAL.md        the contract the user approved
  evals/run      executable eval harness; last stdout line is JSON {"score": ..., "passed": ..., "checks": {...}}
  evals/holdout/ optional held-out harness (same contract), written by a separate agent
  state.json     machine state (status, budget, best score, frozen eval hash)
  LOG.md         human-readable iteration log + notes
  results.tsv    one row per iteration
  runs/          raw eval output per iteration

Statuses: drafting -> frozen -> running -> {done, plateau, budget_exhausted, stalled, blocked, paused}
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

GOAL_DIR = ".goal"
SKIP_PARTS = {"__pycache__", ".DS_Store", "node_modules", ".pytest_cache", ".mypy_cache"}
HOOK_SCRIPT = Path(__file__).resolve().parent / "stop_hook.py"

GOAL_TEMPLATE = """# Goal: {slug}

## Objective
<one or two sentences: what will be true when this is done, and why it matters>

## Done criteria
<observable, checkable conditions. For a metric: the metric, how it's measured, direction, target.
For a feature: the acceptance checks, each phrased so a script or a judge can say pass/fail.>

## Constraints
<what must not change or break: public APIs, dependencies, existing tests, performance floors, style>

## Non-goals
<tempting adjacent work that is explicitly out of scope>

## Budget & stopping
- Max iterations: {max_iterations}
- Patience (iterations without improvement before stopping): {patience}
- Deadline: {deadline}

## Escalate to the user when
<decisions the agent must not make alone, e.g. adding a dependency, changing a schema, deleting data>
"""


def die(msg, code=1):
    print("goalctl: " + msg, file=sys.stderr)
    sys.exit(code)


def find_root(start=None):
    p = Path(start or os.getcwd()).resolve()
    for d in [p] + list(p.parents):
        if (d / GOAL_DIR / "state.json").exists():
            return d
    return None


def gdir(root):
    return root / GOAL_DIR


def load(root):
    return json.loads((gdir(root) / "state.json").read_text())


def save(root, st):
    path = gdir(root) / "state.json"
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(st, indent=2))
    tmp.replace(path)


def need():
    root = find_root()
    if not root:
        die("no .goal/state.json found here or in any parent; run `goalctl init` first")
    return root, load(root)


def log(root, text):
    with open(gdir(root) / "LOG.md", "a") as f:
        f.write(text.rstrip() + "\n\n")


def now():
    return time.strftime("%Y-%m-%d %H:%M")


def git(root, *args, check=True):
    p = subprocess.run(["git"] + list(args), cwd=root, capture_output=True, text=True)
    if check and p.returncode != 0:
        die("git %s failed: %s" % (" ".join(args), p.stderr.strip()))
    return p


def is_git(root):
    return git(root, "rev-parse", "--is-inside-work-tree", check=False).returncode == 0


def evals_hash(root):
    base = gdir(root) / "evals"
    h = hashlib.sha256()
    for f in sorted(base.rglob("*")):
        rel = f.relative_to(base)
        if any(part in SKIP_PARTS for part in rel.parts) or f.suffix == ".pyc" or not f.is_file():
            continue
        h.update(str(rel).encode() + b"\0")
        h.update(f.read_bytes())
    return h.hexdigest()


def fmt(x):
    return "n/a" if x is None else ("%g" % x if isinstance(x, (int, float)) else str(x))


# ---------------------------------------------------------------- eval running

def run_eval(root, st, holdout=False, label=None):
    script = gdir(root) / "evals" / ("holdout/run" if holdout else "run")
    if not script.exists():
        die("%s does not exist" % script.relative_to(root))
    if not os.access(str(script), os.X_OK):
        die("%s is not executable (chmod +x it)" % script.relative_to(root))
    if st.get("evals_hash") and evals_hash(root) != st["evals_hash"]:
        die("evals changed since they were frozen. Restore them (git cannot help: .goal is untracked) "
            "or, only with the user's explicit approval, run `goalctl unfreeze --reason ...`.")
    runs = gdir(root) / "runs"
    runs.mkdir(exist_ok=True)
    logf = runs / ("%s.log" % (label or ("holdout" if holdout else "adhoc")))
    t0 = time.time()
    try:
        p = subprocess.run([str(script)], cwd=root, capture_output=True, text=True,
                           timeout=st.get("eval_timeout", 1800))
        out, err, rc = p.stdout, p.stderr, p.returncode
    except subprocess.TimeoutExpired as e:
        out, err, rc = (e.stdout or ""), (e.stderr or ""), "timeout"
        if isinstance(out, bytes):
            out = out.decode(errors="replace")
        if isinstance(err, bytes):
            err = err.decode(errors="replace")
    logf.write_text("exit: %s\n--- stdout\n%s\n--- stderr\n%s" % (rc, out, err))
    result = None
    for line in reversed(out.strip().splitlines()):
        try:
            obj = json.loads(line)
        except ValueError:
            continue
        if isinstance(obj, dict) and "score" in obj:
            result = obj
            break
    if result is None:
        result = {"score": None, "error": "no JSON score line (exit %s)" % rc}
    result["seconds"] = round(time.time() - t0, 1)
    result["log"] = str(logf.relative_to(root))
    return result


def compare(st, res):
    """Return (keep, improved, why)."""
    s = res.get("score")
    if not isinstance(s, (int, float)):
        return False, False, "eval failed: %s" % res.get("error", "non-numeric score")
    best = st.get("best_score")
    if best is None:
        return True, True, "first score"
    new_checks = res.get("checks") or {}
    lost = [k for k, v in (st.get("best_checks") or {}).items() if v and not new_checks.get(k)]
    if lost:
        return False, False, "regressed previously-passing checks: " + ", ".join(lost[:8])
    d = (s - best) if st["direction"] == "max" else (best - s)
    if d > st["min_delta"]:
        return True, True, "improved by %g" % d
    if st["keep_on_tie"] and d >= 0:
        return True, False, "no regression (tie kept)"
    return False, False, "not better than best (delta %g, need > %g)" % (d, st["min_delta"])


def goal_met(st, res):
    if res.get("passed") is True:
        return True
    t, b = st.get("target"), st.get("best_score")
    if t is None or b is None:
        return False
    return b >= t if st["direction"] == "max" else b <= t


def check_limits(st):
    if st["iteration"] >= st["max_iterations"]:
        return "budget_exhausted", "hit max iterations (%d)" % st["max_iterations"]
    if st.get("deadline") and time.time() > st["deadline"]:
        return "budget_exhausted", "deadline passed"
    if st["since_best"] >= st["patience"]:
        return "plateau", "%d iterations without improvement" % st["since_best"]
    return None, None


# ---------------------------------------------------------------- commands

def cmd_init(a):
    root = find_root() or Path(os.getcwd()).resolve()
    g = gdir(root)
    existing = load(root) if (g / "state.json").exists() else None
    if existing and existing["status"] not in ("drafting",):
        die("a goal already exists with status '%s'; finish it or move .goal/ aside first" % existing["status"])
    mode = a.mode
    direction = a.direction or ("max" if mode == "feature" else None)
    if not direction:
        die("--direction max|min is required for metric mode")
    (g / "evals").mkdir(parents=True, exist_ok=True)
    (g / "runs").mkdir(exist_ok=True)
    deadline = time.time() + a.hours * 3600 if a.hours else None
    st = {
        "slug": a.slug, "mode": mode, "direction": direction, "target": a.target,
        "min_delta": a.min_delta if a.min_delta is not None else 0.0,
        "keep_on_tie": mode == "feature",
        "max_iterations": a.max_iterations, "patience": a.patience, "deadline": deadline,
        "eval_timeout": a.eval_timeout,
        "status": "drafting", "reason": None, "iteration": 0, "since_best": 0,
        "baseline_score": None, "best_score": None, "best_checks": None,
        "evals_hash": None, "branch": None, "base_commit": None, "session_id": None,
        "hook": {}, "created": now(),
    }
    save(root, st)
    if not (g / "GOAL.md").exists():
        (g / "GOAL.md").write_text(GOAL_TEMPLATE.format(
            slug=a.slug, max_iterations=a.max_iterations, patience=a.patience,
            deadline=time.strftime("%Y-%m-%d %H:%M", time.localtime(deadline)) if deadline else "none"))
    if not (g / "LOG.md").exists():
        (g / "LOG.md").write_text("# Goal log: %s\n\n" % a.slug)
    if not (g / "results.tsv").exists():
        (g / "results.tsv").write_text("iter\ttime\tscore\tbest\tverdict\tdesc\n")
    if is_git(root):
        excl = Path(git(root, "rev-parse", "--git-path", "info/exclude").stdout.strip())
        if not excl.is_absolute():
            excl = root / excl
        excl.parent.mkdir(parents=True, exist_ok=True)
        cur = excl.read_text() if excl.exists() else ""
        if ".goal/" not in cur.splitlines():
            excl.write_text(cur + ("" if cur.endswith("\n") or not cur else "\n") + ".goal/\n")
    print("initialized %s (mode=%s, direction=%s, target=%s, max_iterations=%d, patience=%d)"
          % (g, mode, direction, fmt(a.target), a.max_iterations, a.patience))
    if not is_git(root):
        print("warning: not a git repo; keep/revert needs git. Ask the user before running `git init`.")


def cmd_freeze(a):
    root, st = need()
    if st["status"] not in ("drafting", "frozen"):
        die("can only freeze from drafting (status is %s)" % st["status"])
    run = gdir(root) / "evals" / "run"
    if not run.exists() or not os.access(str(run), os.X_OK):
        die(".goal/evals/run must exist and be executable")
    st["evals_hash"] = evals_hash(root)
    st["status"] = "frozen"
    save(root, st)
    log(root, "**%s — evals frozen** (sha256 %s…)" % (now(), st["evals_hash"][:12]))
    print("frozen; hash %s" % st["evals_hash"][:12])


def cmd_unfreeze(a):
    root, st = need()
    st["evals_hash"] = None
    st["status"] = "drafting"
    save(root, st)
    log(root, "**%s — evals UNFROZEN.** Reason: %s" % (now(), a.reason))
    print("unfrozen; edit evals, then `goalctl freeze` and `goalctl start` again")


def cmd_start(a):
    root, st = need()
    if st["status"] == "running":
        die("already running")
    if st["status"] == "drafting":
        die("freeze the evals first (`goalctl freeze`)")
    if not is_git(root):
        die("keep/revert needs a git repo; ask the user before running `git init`")
    if a.add_iterations:
        st["max_iterations"] += a.add_iterations
    if a.add_hours:
        st["deadline"] = max(st.get("deadline") or time.time(), time.time()) + a.add_hours * 3600
    if a.reset_patience:
        st["since_best"] = 0
    dirty = git(root, "status", "--porcelain").stdout.strip()
    if dirty:
        die("working tree has uncommitted changes; reverts would destroy them. "
            "Ask the user to commit or stash first:\n" + dirty)
    if st["baseline_score"] is None:
        branch = "goal/" + st["slug"]
        exists = git(root, "rev-parse", "--verify", "--quiet", branch, check=False).returncode == 0
        git(root, "checkout", "-q", branch) if exists else git(root, "checkout", "-q", "-b", branch)
        st["branch"] = branch
        st["base_commit"] = git(root, "rev-parse", "HEAD").stdout.strip()
        res = run_eval(root, st, label="iter-000-baseline")
        if not isinstance(res.get("score"), (int, float)):
            die("baseline eval did not produce a numeric score: %s (see %s)" % (res.get("error"), res["log"]))
        st["baseline_score"] = st["best_score"] = res["score"]
        st["best_checks"] = res.get("checks")
        with open(gdir(root) / "results.tsv", "a") as f:
            f.write("0\t%s\t%s\t%s\tBASELINE\tbaseline\n" % (now(), fmt(res["score"]), fmt(res["score"])))
        log(root, "## baseline — score %s\nbranch `%s` from %s; eval log %s"
            % (fmt(res["score"]), branch, st["base_commit"][:8], res["log"]))
        if goal_met(st, res):
            st["status"], st["reason"] = "done", "baseline already meets the goal"
            save(root, st)
            print("baseline %s already meets the goal; nothing to do" % fmt(res["score"]))
            return
    status, reason = check_limits(st)
    if status:
        die("cannot start: %s. Use --add-iterations/--add-hours/--reset-patience if the user wants more." % reason)
    st["status"], st["reason"] = "running", None
    st["session_id"] = None  # the Stop hook claims the session that stops next
    st["hook"] = {}
    save(root, st)
    log(root, "**%s — running** (iteration %d/%d, best %s)" % (now(), st["iteration"], st["max_iterations"], fmt(st["best_score"])))
    print("running. baseline=%s best=%s target=%s iteration=%d/%d"
          % (fmt(st["baseline_score"]), fmt(st["best_score"]), fmt(st.get("target")), st["iteration"], st["max_iterations"]))


def cmd_iterate(a):
    root, st = need()
    if st["status"] != "running":
        die("status is '%s', not running" % st["status"])
    n = st["iteration"] + 1
    res = run_eval(root, st, label="iter-%03d" % n)
    keep, improved, why = compare(st, res)
    prev_best = st["best_score"]
    st["iteration"] = n
    if keep:
        git(root, "add", "-A")
        if git(root, "diff", "--cached", "--quiet", check=False).returncode != 0:
            git(root, "commit", "-q", "-m", "goal(%s) iter %d: %s [score %s]" % (st["slug"], n, a.desc, fmt(res["score"])))
        st["best_score"] = res["score"]
        if res.get("checks"):
            st["best_checks"] = res["checks"]
        st["since_best"] = 0 if improved else st["since_best"] + 1
        verdict = "KEEP"
    else:
        git(root, "reset", "-q", "--hard", "HEAD")
        git(root, "clean", "-q", "-fd")
        st["since_best"] += 1
        verdict = "REVERT"
    with open(gdir(root) / "results.tsv", "a") as f:
        f.write("%d\t%s\t%s\t%s\t%s\t%s\n" % (n, now(), fmt(res.get("score")), fmt(st["best_score"]), verdict,
                                              a.desc.replace("\t", " ").replace("\n", " ")))
    failing = sorted(k for k, v in (res.get("checks") or {}).items() if not v)
    log(root, "## iter %d — %s (%s → %s)\n%s\n- why: %s\n- eval: %ss, log %s%s"
        % (n, verdict, fmt(prev_best), fmt(res.get("score")), a.desc, why, res["seconds"], res["log"],
           ("\n- still failing: " + ", ".join(failing[:15])) if failing else ""))
    if keep and goal_met(st, res):
        st["status"], st["reason"] = "done", "goal met at iteration %d" % n
    else:
        status, reason = check_limits(st)
        if status:
            st["status"], st["reason"] = status, reason
    save(root, st)
    if st["status"] != "running":
        log(root, "**%s — stopped: %s** (%s)" % (now(), st["status"], st["reason"]))
    print("%s: %s" % (verdict, why))
    print("score=%s best=%s target=%s iteration=%d/%d since_best=%d/%d status=%s"
          % (fmt(res.get("score")), fmt(st["best_score"]), fmt(st.get("target")), n, st["max_iterations"],
             st["since_best"], st["patience"], st["status"]))
    if failing:
        print("failing checks: " + ", ".join(failing[:15]))
    if res.get("error"):
        print("eval error: %s (see %s)" % (res["error"], res["log"]))
    if st["status"] != "running":
        print("loop finished (%s). Do the wrap-up step." % st["reason"])


def cmd_run(a):
    root, st = need()
    res = run_eval(root, st, holdout=a.holdout, label="holdout-%s" % time.strftime("%H%M%S") if a.holdout else "adhoc")
    if a.holdout:
        log(root, "**%s — holdout eval:** score %s, passed %s (log %s)"
            % (now(), fmt(res.get("score")), res.get("passed"), res["log"]))
    print(json.dumps(res, indent=2))


def cmd_set_status(status):
    def f(a):
        root, st = need()
        st["status"], st["reason"] = status, a.reason
        save(root, st)
        log(root, "**%s — %s:** %s" % (now(), status, a.reason))
        print("status=%s" % status)
    return f


def cmd_note(a):
    root, _ = need()
    log(root, "> note (%s): %s" % (now(), a.text))
    print("noted")


def cmd_status(a):
    root = find_root()
    if not root:
        print("no active goal (no .goal/state.json here or above)")
        return
    st = load(root)
    keys = ["slug", "mode", "status", "reason", "iteration", "max_iterations", "since_best", "patience",
            "baseline_score", "best_score", "target", "direction", "min_delta", "branch"]
    for k in keys:
        print("%-15s %s" % (k, fmt(st.get(k))))
    if st.get("deadline"):
        print("%-15s %s" % ("deadline", time.strftime("%Y-%m-%d %H:%M", time.localtime(st["deadline"]))))
    print("%-15s %s" % ("evals_frozen", "yes" if st.get("evals_hash") else "no"))
    print("%-15s %s" % ("root", root))


def cmd_install_hook(a):
    settings = Path.home() / ".claude" / "settings.json"
    data = json.loads(settings.read_text()) if settings.exists() else {}
    cmd = 'python3 "%s"' % HOOK_SCRIPT
    stops = data.setdefault("hooks", {}).setdefault("Stop", [])
    for group in stops:
        for h in group.get("hooks", []):
            if "goal-loop" in h.get("command", "") and "stop_hook.py" in h.get("command", ""):
                print("Stop hook already installed in %s" % settings)
                return
    stops.append({"hooks": [{"type": "command", "command": cmd, "timeout": 10}]})
    settings.write_text(json.dumps(data, indent=2) + "\n")
    print("installed Stop hook in %s: %s" % (settings, cmd))


def main():
    ap = argparse.ArgumentParser(prog="goalctl")
    sub = ap.add_subparsers(dest="cmd")
    sub.required = True

    p = sub.add_parser("init", help="create .goal/ (re-runnable while drafting)")
    p.add_argument("--slug", required=True)
    p.add_argument("--mode", choices=["metric", "feature"], required=True)
    p.add_argument("--direction", choices=["max", "min"])
    p.add_argument("--target", type=float)
    p.add_argument("--min-delta", type=float, help="improvement must exceed this (set above measured noise)")
    p.add_argument("--max-iterations", type=int, default=30)
    p.add_argument("--patience", type=int, default=8)
    p.add_argument("--hours", type=float, help="wall-clock deadline from now")
    p.add_argument("--eval-timeout", type=int, default=1800)
    p.set_defaults(fn=cmd_init)

    sub.add_parser("freeze", help="hash evals; they may not change after this").set_defaults(fn=cmd_freeze)
    p = sub.add_parser("unfreeze", help="ONLY with explicit user approval")
    p.add_argument("--reason", required=True)
    p.set_defaults(fn=cmd_unfreeze)

    p = sub.add_parser("start", help="branch, run baseline, set running (also resumes)")
    p.add_argument("--add-iterations", type=int, default=0)
    p.add_argument("--add-hours", type=float, default=0)
    p.add_argument("--reset-patience", action="store_true")
    p.set_defaults(fn=cmd_start)

    p = sub.add_parser("iterate", help="eval current tree, then commit (keep) or reset (revert)")
    p.add_argument("--desc", required=True, help="the hypothesis / change made this iteration")
    p.set_defaults(fn=cmd_iterate)

    p = sub.add_parser("run", help="run evals without recording (or the holdout set)")
    p.add_argument("--holdout", action="store_true")
    p.set_defaults(fn=cmd_run)

    for name, status in [("block", "blocked"), ("pause", "paused"), ("finish", "done")]:
        p = sub.add_parser(name, help="set status to %s" % status)
        p.add_argument("--reason", required=True)
        p.set_defaults(fn=cmd_set_status(status))

    p = sub.add_parser("note", help="append a learning to LOG.md")
    p.add_argument("text")
    p.set_defaults(fn=cmd_note)

    sub.add_parser("status").set_defaults(fn=cmd_status)
    sub.add_parser("install-hook", help="add the Stop hook to ~/.claude/settings.json").set_defaults(fn=cmd_install_hook)

    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
