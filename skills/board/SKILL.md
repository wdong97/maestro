---
name: board
description: Track multi-agent build work on a shared, server-less Kanban + roadmap board that humans and agents both update. Use when coordinating who is doing what across Claude/Codex, planning slices/tasks with quality+performance gates, or when the user asks to see/update the build board, claim a task, mark progress, block/review/finish work, record a gate or sign-off, or set up the board for a repo.
---

# board — shared live build board (Kanban + roadmap)

A project's `orchestration/board-state.json` is the single source of truth for what's
being worked. Update it via the `board` CLI (lock-safe; never hand-edit the JSON while
agents run). Complements `ensemble jobs`/`dash` (which show running *processes*) — this
shows the *work*.

## Set up (once per repo)
```bash
board init            # scaffolds orchestration/ into the current repo
# edit orchestration/board-state.json: set "project" and define your slices/tasks
board serve           # open the printed URL to watch it live (Board + Roadmap views)
```

## The protocol — every agent follows this
1. **Claim before starting:** `board claim <task> --owner <you>` (refuses to steal
   another agent's in-progress card without `--force`). Use a stable owner handle
   (e.g. `codex-A`, `claude`).
2. **Update as you go:** `board progress <task> --note "…"`; `board block <task>
   --reason "…"` when stuck.
3. **Finish honestly and gate it:** `board review <task>` → `board done <task>`;
   record gate checks with evidence: `board gate <slice> <check> pass --by <you>`.
   A gated slice is **done only when all tasks done + all gate checks pass + a
   `board signoff <slice> --by <maintainer>`** — the CLI enforces it (otherwise the
   slice reads `in-review`).
4. **New work mid-iteration:** `board add <slice> "title"` — put unplanned /
   cross-cutting items in the **`ITER`** bucket so planned slices stay clean.
5. **Read state any time:** `board show [slice]` (read-only).

## Guidance
- Keep one task = one card; split big work into a slice with several tasks.
- Record real evidence on gates (CI link, test count, p95) — the board is a build log.
- It's git-tracked: commit `board-state.json` changes so history is the record.
- If `board` isn't on PATH, use the repo-local `./orchestration/status.py` (same commands).
