#!/usr/bin/env python3
"""Live build board updater — atomic, lock-safe, gate-governed.

Single source of truth: board-state.json (this folder). Agents and humans update
it through this CLI — never hand-edit while agents are running. View it with
./serve.sh then open the dashboard.

  ./status.py claim    S1.api --owner codex-A [--note ..] [--force]   # start: in-progress + owner
  ./status.py progress S1.api --note "endpoint wired"
  ./status.py block    S1.api --reason "schema undecided"
  ./status.py review   S1.api
  ./status.py done     S1.api --note "merged"
  ./status.py gate     S1 tests pass --by codex-A [--note "ci#123"]   # pass|fail|pending (+evidence)
  ./status.py signoff  S1 --by alice [--note "reviewed, ship it"]     # maintainer/DRI gate sign-off
  ./status.py ledger   S1 p95_ms 180 [--force]                        # record a gate-ledger metric
  ./status.py add      ITER "verify deploy" --owner alice             # NEW card mid-iteration
  ./status.py drop     ITER.verify-deploy [--force]                   # remove a card
  ./status.py show     [S1]                                            # print the board (read-only)

A slice reads "done" only when: all its tasks are done AND all gate checks pass
AND (if it has gates) a sign-off is recorded. Tasks-done-but-gate-not-green or
unsigned shows "in-review". Put unplanned/cross-cutting work in the ITER bucket.
"""
import argparse, json, sys, os, fcntl, tempfile
from datetime import datetime, timezone

STATE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "board-state.json")
LOCK = STATE + ".lock"
TASK_STATUSES = {"todo", "in-progress", "blocked", "in-review", "done"}


def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _gate_checks(sl):
    g = sl.get("gate", {}) or {}
    return list(g.get("quality", [])) + list(g.get("performance", []))


def _recompute_slice(sl):
    tasks = sl["tasks"]
    ts = [t["status"] for t in tasks]
    checks = _gate_checks(sl)
    gated = len(checks) > 0
    all_done = bool(ts) and all(s == "done" for s in ts)
    gate_green = all(c.get("status") == "pass" for c in checks)  # vacuously True if no checks
    signed = bool(sl.get("sign_off"))
    if all_done and gate_green and (not gated or signed):
        sl["status"] = "done"
    elif all_done and gated:                       # tasks done, gate not green or unsigned
        sl["status"] = "in-review"
    elif any(s in ("in-progress", "in-review") for s in ts):
        sl["status"] = "in-progress"
    elif any(s == "blocked" for s in ts):
        sl["status"] = "blocked"
    elif all_done:                                 # all done, ungated (e.g. ITER)
        sl["status"] = "done"
    else:
        sl["status"] = "todo"


def _find_task(data, tid):
    for sl in data["slices"]:
        for t in sl["tasks"]:
            if t["id"] == tid:
                return sl, t
    return None, None


def _find_slice(data, sid):
    return next((s for s in data["slices"] if s["id"] == sid), None)


def _with_state(fn):
    """Lock-safe (flock on a sidecar lockfile) + crash-safe (temp + atomic rename)."""
    with open(LOCK, "a+") as lf:
        fcntl.flock(lf, fcntl.LOCK_EX)
        with open(STATE, "r", encoding="utf-8") as f:
            data = json.load(f)
        out = fn(data)
        data["updated_at"] = _now()
        d = os.path.dirname(STATE)
        fd, tmp = tempfile.mkstemp(dir=d, prefix=".bs-", suffix=".json")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as tf:
                json.dump(data, tf, indent=2, ensure_ascii=False)
                tf.write("\n")
                tf.flush()
                os.fsync(tf.fileno())
            os.replace(tmp, STATE)
        except BaseException:
            try: os.unlink(tmp)
            except OSError: pass
            raise
        return out


def set_task(tid, status, owner=None, note=None, force=False):
    def fn(data):
        sl, t = _find_task(data, tid)
        if not t:
            sys.exit(f"task not found: {tid}")
        if (status == "in-progress" and not force and owner
                and t["status"] == "in-progress" and t.get("owner") and t["owner"] != owner):
            sys.exit(f"refusing: {tid} is in-progress by @{t['owner']} (use --force to take it over)")
        was_done = t["status"] == "done"
        t["status"] = status
        t["updated_at"] = _now()
        if owner is not None:
            t["owner"] = owner
        if note is not None:
            t["note"] = note
        if was_done and status != "done":          # reopening completed work invalidates the sign-off
            sl.pop("sign_off", None)
        _recompute_slice(sl)
        return f"{tid} -> {status}" + (f"  @{t['owner']}" if t.get("owner") else "")
    print(_with_state(fn))


def set_gate(sid, check_id, status, by, note=None):
    def fn(data):
        sl = _find_slice(data, sid)
        if not sl:
            sys.exit(f"slice not found: {sid}")
        for c in _gate_checks(sl):
            if c["id"] == check_id:
                c["status"] = status
                c["by"] = by
                c["at"] = _now()
                if note is not None:
                    c["note"] = note
                _recompute_slice(sl)
                return f"{sid}.gate.{check_id} -> {status}  (by @{by})"
        sys.exit(f"gate check '{check_id}' not found in {sid} (run: status.py show {sid})")
    print(_with_state(fn))


def signoff(sid, by, note=None):
    def fn(data):
        sl = _find_slice(data, sid)
        if not sl:
            sys.exit(f"slice not found: {sid}")
        if not _gate_checks(sl):
            sys.exit(f"{sid} has no gate to sign off")
        sl["sign_off"] = {"by": by, "at": _now(), "note": note or ""}
        _recompute_slice(sl)
        warn = "" if all(c.get("status") == "pass" for c in _gate_checks(sl)) \
            else "  (WARNING: gate not all-pass — slice stays in-review until it is)"
        return f"{sid} signed off by @{by}{warn}"
    print(_with_state(fn))


def set_ledger(sid, metric, value, force=False):
    def fn(data):
        sl = _find_slice(data, sid)
        if not sl:
            sys.exit(f"slice not found: {sid}")
        led = sl.setdefault("ledger", {})
        if metric not in led and not force:
            keys = ", ".join(led.keys()) or "(none declared)"
            sys.exit(f"unknown metric '{metric}' for {sid}. declared: {keys}. use --force to add a new one.")
        v = value
        try:
            v = float(v)
        except (ValueError, TypeError):
            pass
        led[metric] = v
        return f"{sid}.ledger.{metric} = {v}"
    print(_with_state(fn))


def add_task(sid, title, tid=None, owner=None):
    def fn(data):
        sl = _find_slice(data, sid)
        if not sl:
            sys.exit(f"slice not found: {sid} (use a slice id, or ITER for ad-hoc)")
        nonlocal tid
        if not tid:
            slug = "-".join("".join(c if c.isalnum() else " " for c in title.lower()).split())[:24]
            tid = f"{sid}.{slug or 'task'}"
        existing = {t["id"] for s in data["slices"] for t in s["tasks"]}
        base, n = tid, 2
        while tid in existing:
            tid = f"{base}-{n}"; n += 1
        sl["tasks"].append({"id": tid, "title": title, "status": "todo",
                            "owner": owner, "updated_at": _now(), "note": ""})
        sl.pop("sign_off", None)                    # new work invalidates a prior sign-off
        _recompute_slice(sl)
        return f"added {tid} to {sid}: {title}"
    print(_with_state(fn))


def drop_task(tid, force=False):
    def fn(data):
        for sl in data["slices"]:
            for i, t in enumerate(sl["tasks"]):
                if t["id"] == tid:
                    if sl["id"] != "ITER" and not force:
                        sys.exit(f"refusing to drop canonical task {tid} from {sl['id']} "
                                 f"(only ITER cards drop freely; use --force if you really mean it)")
                    del sl["tasks"][i]
                    _recompute_slice(sl)
                    return f"dropped {tid}"
        sys.exit(f"task not found: {tid}")
    print(_with_state(fn))


def show(sid=None):
    with open(LOCK, "a+") as lf:
        fcntl.flock(lf, fcntl.LOCK_SH)
        with open(STATE, encoding="utf-8") as f:
            data = json.load(f)
    print(f"{data['project']} - updated {data['updated_at']}")
    for sl in data["slices"]:
        if sid and sl["id"] != sid:
            continue
        tasks = sl["tasks"]
        done = sum(1 for t in tasks if t["status"] == "done")
        checks = _gate_checks(sl)
        gp = sum(1 for c in checks if c.get("status") == "pass")
        gate = f"  gate {gp}/{len(checks)}" if checks else ""
        so = ""
        if checks:
            so = f"  signoff:@{sl['sign_off']['by']}" if sl.get("sign_off") else "  signoff:none"
        print(f"\n{sl['id']} [{sl['status']}] {sl['title']}  ({done}/{len(tasks)}){gate}{so}")
        for t in tasks:
            o = f"  @{t['owner']}" if t.get("owner") else ""
            n = f"  — {t['note']}" if t.get("note") else ""
            print(f"  - [{t['status']:<11}] {t['id']}: {t['title']}{o}{n}")
        led = {k: v for k, v in (sl.get("ledger") or {}).items() if v is not None}
        if led:
            print("    ledger: " + " · ".join(f"{k}={v}" for k, v in led.items()))


def main():
    p = argparse.ArgumentParser(description="Live build board updater (see README.md)")
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("claim"); c.add_argument("task"); c.add_argument("--owner", required=True); c.add_argument("--note"); c.add_argument("--force", action="store_true")
    for name in ("progress", "review", "done"):
        sp = sub.add_parser(name); sp.add_argument("task"); sp.add_argument("--owner"); sp.add_argument("--note")
    b = sub.add_parser("block"); b.add_argument("task"); b.add_argument("--reason", required=True); b.add_argument("--owner")
    g = sub.add_parser("gate"); g.add_argument("slice"); g.add_argument("check"); g.add_argument("status", choices=["pending", "pass", "fail"]); g.add_argument("--by", required=True); g.add_argument("--note")
    so = sub.add_parser("signoff"); so.add_argument("slice"); so.add_argument("--by", required=True); so.add_argument("--note")
    le = sub.add_parser("ledger"); le.add_argument("slice"); le.add_argument("metric"); le.add_argument("value"); le.add_argument("--force", action="store_true")
    ad = sub.add_parser("add"); ad.add_argument("slice"); ad.add_argument("title"); ad.add_argument("--id"); ad.add_argument("--owner")
    dr = sub.add_parser("drop"); dr.add_argument("task"); dr.add_argument("--force", action="store_true")
    s = sub.add_parser("show"); s.add_argument("slice", nargs="?")
    a = p.parse_args()

    if a.cmd == "claim":
        set_task(a.task, "in-progress", owner=a.owner, note=a.note, force=a.force)
    elif a.cmd == "progress":
        set_task(a.task, "in-progress", owner=a.owner, note=a.note, force=True)
    elif a.cmd == "review":
        set_task(a.task, "in-review", owner=a.owner, note=a.note, force=True)
    elif a.cmd == "done":
        set_task(a.task, "done", owner=a.owner, note=a.note, force=True)
    elif a.cmd == "block":
        set_task(a.task, "blocked", owner=a.owner, note=f"BLOCKED: {a.reason}", force=True)
    elif a.cmd == "gate":
        set_gate(a.slice, a.check, a.status, a.by, a.note)
    elif a.cmd == "signoff":
        signoff(a.slice, a.by, a.note)
    elif a.cmd == "ledger":
        set_ledger(a.slice, a.metric, a.value, force=a.force)
    elif a.cmd == "add":
        add_task(a.slice, a.title, tid=a.id, owner=a.owner)
    elif a.cmd == "drop":
        drop_task(a.task, force=a.force)
    elif a.cmd == "show":
        show(a.slice)


if __name__ == "__main__":
    main()
