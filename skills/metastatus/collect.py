#!/usr/bin/env python3
"""Gather every agent session on both machines plus its last screen, as one JSON file.

Reuses the `cb` CLI (roster + Orca helpers), so it runs unchanged on WSL and the Mac.
Read-only: it lists terminals and reads screens; it never sends input.

Usage: collect.py [--out PATH] [--lines 60]
"""

from __future__ import annotations

import argparse
import importlib.machinery
import importlib.util
import json
import os
import shutil
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path


def load_cb():
    path = shutil.which("cb")
    if not path:
        fallback = Path.home() / "devel" / "agent-memory" / "bin" / "cb"
        path = str(fallback) if fallback.exists() else None
    if not path:
        sys.exit("metastatus: `cb` is not on PATH (it ships in the agent-memory repo)")
    path = os.path.realpath(path)
    loader = importlib.machinery.SourceFileLoader("cb_cli", path)
    spec = importlib.util.spec_from_loader("cb_cli", loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path)
    parser.add_argument("--lines", type=int, default=60)
    args = parser.parse_args()

    cb = load_cb()
    cb.sync("pull")
    entries, unregistered = cb.live_roster()
    me = cb.my_terminal()

    def read(row: dict) -> dict:
        out = {k: row.get(k) for k in ("label", "machine", "terminal", "scope", "session", "title", "state", "agent")}
        out["is_me"] = row.get("terminal") == me
        if row.get("state") == "gone" or out["is_me"]:
            out["screen"] = ""
            return out
        raw = cb.run_orca("terminal", "read", *cb.env_args(row["machine"]),
                          "--terminal", row["terminal"], "--limit", str(args.lines))
        screen = cb.clean_screen(raw)
        out["screen"] = screen
        out["read_ok"] = bool(screen)
        out["self_recap"] = cb.recap_of(screen)
        out["needs_you"] = bool(cb.NEEDS_YOU.search("\n".join(screen.splitlines()[-14:])))
        return out

    live = [e for e in entries if e.get("state") != "gone"]
    with ThreadPoolExecutor(6) as pool:
        sessions = list(pool.map(read, live))
        others = list(pool.map(read, unregistered))
    report = {
        "collected_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "from_machine": cb.MACHINE,
        "sessions": sessions,
        "gone": sorted(e["label"] for e in entries if e.get("state") == "gone"),
        "unregistered": others,
    }
    text = json.dumps(report, indent=1, ensure_ascii=False)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(args.out, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        os.fchmod(fd, 0o600)  # an existing file keeps its old mode otherwise; screens are private
        with os.fdopen(fd, "w") as f:
            f.write(text + "\n")
        print(f"{len(sessions)} live, {len(report['gone'])} gone, {len(others)} unregistered -> {args.out}")
    else:
        print(text)


if __name__ == "__main__":
    main()
