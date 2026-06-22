# Build board — the live, shared work tracker

A server-less Kanban + roadmap board that **agents and humans update together**.
One JSON file is the source of truth (`board-state.json`); a self-refreshing HTML
page shows it; a tiny lock-safe CLI changes it. No server, no database.

This complements maestro's *runtime* view (`ensemble jobs` / `ensemble dash`, which
shows agent *processes*). This board shows the *work*: what's planned, in progress,
blocked, in review, done — and the quality/perf gates each slice must pass.

## View it

```bash
./serve.sh                 # serves this folder on :8765 (frees the port first)
# open the printed URL → dashboard.html
```
Two toggleable views: **Board** (Kanban across all slices, filterable) and
**Roadmap** (slices with progress bars, gates, and sign-off). It polls every 3s.

## Update it (agents + humans) — never hand-edit while agents run

```bash
./status.py claim    S1.api --owner alice     # start a task (in-progress + owner)
./status.py progress S1.api --note "wired"    # note progress
./status.py block    S1.api --reason "schema undecided"
./status.py review   S1.api                    # ready for review
./status.py done     S1.api --note "merged"
./status.py gate     S1 tests pass --by alice  # a gate check: pass|fail|pending
./status.py signoff  S1 --by maria             # maintainer sign-off (required to finish a gated slice)
./status.py add      ITER "verify deploy"      # new card mid-iteration (ITER = ad-hoc bucket)
./status.py drop     ITER.verify-deploy        # remove an ITER card
./status.py show     [S1]                       # print the board (read-only)
```

If `board` is on your PATH (maestro installed), run it from the repo root instead
of `./status.py` — e.g. `board claim S1.api --owner alice`, `board serve`.

## The protocol (every agent follows this)

1. **Claim before you start** — `claim <task> --owner you` (won't steal another
   agent's in-progress card without `--force`).
2. **Update as you go** — `progress` / `block` with a short note.
3. **Finish honestly & gate it** — `review` → `done`; record gate checks with
   evidence (`gate … --by …`). A slice is **done only when all tasks are done,
   every gate check passes, and it's signed off** — the CLI enforces this
   (tasks-done-but-unsigned reads `in-review`).
4. **New work mid-iteration** — `add <slice> "title"` (use `ITER` for ad-hoc /
   cross-cutting items so planned slices stay clean).

It's git-tracked, so the file's history *is* the build log.
