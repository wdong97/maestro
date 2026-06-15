---
name: delegate
description: Cost-aware work routing between this main session (Fable 5) and Codex (gpt-5.5 xhigh). Use when deciding who does a task, when the user invokes /delegate, or before starting backend/heavy implementation that should be specced and handed to Codex via /goal to save tokens. Keep planning, frontend, visual, and ideation work in this session; dispatch backend and heavy implementation to Codex.
---

# Delegate — Cost-Aware Routing

This session runs on **Fable 5** — expensive but worth it for planning, frontend,
visual output, and ideas. **Codex** runs on **gpt-5.5 xhigh** and the user's quota
there sits unused, so it's effectively free capacity for heavy execution.

Goal: spend Fable tokens only where they earn their price. Route everything else to Codex.

## Routing Rules

**Keep in this session (Fable 5):**
- Planning, architecture, and task decomposition
- Frontend work — UI, layout, styling, components, anything with visual output
- Design, ideation, and judgment calls where taste matters
- The hardest parts — gnarly logic, subtle bugs, decisions Codex would get wrong

**Dispatch to Codex (gpt-5.5 xhigh) via `/goal`:**
- Backend implementation
- Heavy/bulk implementation work — large mechanical edits, scaffolding, boilerplate
- Anything well-specified enough that execution is the bottleneck, not thinking

When unsure, ask: *is the value here in the ideas/visuals, or in the keystrokes?*
Ideas and visuals stay; keystrokes go to Codex.

## How to Dispatch

1. **Write a clear spec first.** Codex executes against the spec, so it must be
   self-contained: repo path, exact task, files/modules involved, expected behavior,
   constraints, and what "done" looks like. A vague spec wastes the free quota and
   forces rework here.
2. **Hand it to Codex with `/goal`** so Codex drives the execution autonomously.
   Always run it as **gpt-5.5 / xhigh / fast**. `model` and `model_reasoning_effort`
   are the local config defaults, but `fast_default_opt_out = true` means the `fast`
   service tier is **not** applied unless you pass it explicitly. So set all three on
   the command line for every dispatch. Use the **zombie-proof launch pattern** below —
   it gives a live Output panel *and* guarantees the background shell always exits, so a
   dispatch can never linger as a "running" zombie after Codex has died (see
   "Zombie prevention" for why each piece matters):

   - Codex writes its **stream** to `$LOG` (a *file*, never a pipe) and its **final
     message** to `$OUT` (`-o`).
   - A `tail --pid` mirrors `$LOG` to the shell's **Output** panel live and **exits the
     instant Codex's PID dies** — clean exit, crash, or timeout-kill alike.
   - The codex subshell always writes its exit code to `$DONE`, so completion is provable
     independently of the harness's status flag.

   ```bash
   SLUG=auth-endpoints                       # short kebab name for this dispatch
   DIR=~/.codex/dispatch && mkdir -p "$DIR"
   LOG="$DIR/$SLUG.log"; OUT="$DIR/$SLUG.out"; DONE="$DIR/$SLUG.done"
   rm -f "$DONE"; : > "$LOG"

   # codex -> file, bounded by a timeout, no stdin; records its own exit in $DONE
   ( timeout -k 1m 30m codex exec -C "$REPO" --skip-git-repo-check \
       -m gpt-5.5 \
       -c model_reasoning_effort='"xhigh"' \
       -c service_tier='"fast"' \
       --sandbox workspace-write --full-auto \
       -o "$OUT" "$PROMPT" </dev/null >"$LOG" 2>&1 ; echo "$?" >"$DONE" ) &
   CPID=$!
   # mirror to the Output panel; this tail dies with codex, so the shell always exits
   tail -n +1 --pid="$CPID" -f "$LOG"
   echo "[delegate] $SLUG finished, codex exit=$(cat "$DONE")"
   ```

   Use `--sandbox read-only` instead when the dispatch is analysis, not editing.
   Set the `timeout` budget to the work: ~`30m` for a big `xhigh` build, less for
   smaller runs — it's the hard ceiling that stops a hung Codex from running forever.

   **Always run this in the background** (`run_in_background: true`) so you keep working
   here while Codex executes. The stream lives in the background task's Output panel and
   in `$LOG` — it does **not** enter this session's context until something reads it,
   which is the whole point of the next step.

3. **Review what comes back here — read `$OUT` only.** When the background task
   finishes, read just the short final message (`$OUT`). Do **not** pull the task's full
   Output / `$LOG` back into this session (no `TaskOutput` of the whole stream, no
   `cat "$LOG"`) unless you're actively debugging a failure — that long stream is exactly
   the token cost delegation is meant to avoid. The stream being visible in the Output
   panel is for *the user*; it stays out of this session's context as long as you don't
   read it. Then verify Codex's work against the spec, the repo, and tests before
   trusting or committing it. Fable owns the final judgment.

   Treat `$DONE` as ground truth for "is it finished," not the harness status: if
   `$DONE` exists the run ended (its contents are Codex's exit code — `0` = success,
   `124` = hit the timeout, anything else = failure); if `$DONE` is absent Codex is
   genuinely still running. Never infer "still working" from a shell that merely *says*
   running.

## Zombie Prevention & Reaping

The failure to avoid: a dispatch's Codex process dies (crash, OOM, killed) but the
background shell never reports an exit and lingers as a "running" zombie. The launch
pattern above is built to make that impossible, and gives a way to clean up any that
predate it:

- **Why it can't zombie:** Codex's stream goes to a *file*, so no stray child can wedge
  a pipe open and block a reader. The only foreground process is `tail --pid=$CPID`,
  which the kernel makes exit the moment Codex's PID dies — so the shell always reaches
  its final `echo` and exits, and the harness always gets the signal. `timeout -k 1m`
  caps the wall clock so even a hung (not dead) Codex is force-killed and reaped.
  `</dev/null` stops Codex blocking forever on a stdin read.

- **Ground truth, not status flags:** `$DONE` (exit code) and a non-empty `$OUT` prove a
  run finished regardless of what the task list shows. A shell showing "running" with
  `$DONE` already written — or with no live PID — is a zombie to reap.

- **Find zombies:** list live Codex processes and compare against shells still marked
  running:
  ```bash
  pgrep -af 'codex exec'                 # PIDs actually still working
  ls ~/.codex/dispatch/*.done 2>/dev/null # dispatches that have already ended
  ```
  A dispatch whose `.done` exists (or whose PID is absent from `pgrep`) but whose shell
  still says running is dead — reap it.

- **Reap them:** stop the lingering background shell with `TaskStop` (preferred — it's
  the harness's own handle). As a last resort for orphaned OS processes:
  ```bash
  pkill -f 'codex exec'                  # or: kill <PID> for a specific one
  ```
  Don't leave zombie shells around: they clutter the task list and make it look like
  work is still in flight when it isn't.

## Watching / Reviewing a Dispatch

`codex exec` is headless — there is no live TUI window to attach to. Visibility comes
from three places:

- **Live, while it runs** — two equivalent ways (the run mirrors `$LOG` to both):
  - Open the background shell's details; the stream shows in the **Output** section.
  - Or tail the log directly (`$OUT` stays empty until the run ends, so tail `$LOG`):
    ```bash
    tail -f ~/.codex/dispatch/$SLUG.log  # live progress, reasoning, tool calls, diffs
    ```
  **Always** give the user this exact `tail -f` line the moment you dispatch, so they
  can open a shell and watch the run live — every dispatch, without being asked.
- **After the fact** — every run is recorded as a full JSONL transcript under
  `~/.codex/sessions/YYYY/MM/DD/rollout-<timestamp>-<session-id>.jsonl`. Latest first:
  ```bash
  ls -t ~/.codex/sessions/**/*.jsonl | head
  ```
- **Reopen interactively** — resume the session into the real Codex TUI to read or
  continue it:
  ```bash
  codex resume --last            # most recent session
  codex resume <session-id>      # a specific one
  ```
  For a headless follow-up prompt instead, use `codex exec resume --last -`.

## Cost & Speed Notes

- **`xhigh` is the slowest, most token-heavy reasoning setting** on the Codex side — by
  design. It's worth it for genuinely hard implementation, but for bulk mechanical work
  (scaffolding, renames, boilerplate) drop to `-c model_reasoning_effort='"high"'` or
  `'"medium"'` for a much faster, cheaper run. Match effort to difficulty.
- **The expensive mistake is letting the Codex stream into this session.** The stream
  being visible to the *user* (Output panel / `tail -f $LOG`) costs nothing here — it
  only costs Fable tokens if *this session* reads it. So: background the run, and read
  back only `$OUT`. Never `cat $LOG` or `TaskOutput` the whole stream except to debug a
  failure. Codex-side token spend is the free/unused quota; Fable-side spend is the bill.

## When Invoked Explicitly

If the user runs `/delegate` (optionally naming a task), apply the rules above to the
current or next piece of work: state which side should do it and why in one line, then
either proceed here or write the spec and dispatch to Codex. Don't over-explain —
make the call and act. On every Codex dispatch, immediately hand the user the
`tail -f ~/.codex/dispatch/<slug>.log` line so they can watch it live.

## Guardrails

- Don't dispatch the hard parts just to save tokens — a wrong Codex result costs more
  Fable tokens to diagnose and fix than doing it here would have.
- Don't dispatch without a spec. "Figure out the backend" is not a spec.
- Keep the spec text tight; the savings come from *not* doing the keystrokes here, not
  from a long handoff.
- See the `codex` skill for command shapes and the `agent-sync` skill for handoff
  packets and session linking when work bounces between the two.
