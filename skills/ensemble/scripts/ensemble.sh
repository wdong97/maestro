#!/usr/bin/env bash
# ensemble.sh — run Claude Code and Codex CLI together: duel, spawn, review.
# Live view is via tmux panes; results are also captured to files so an
# orchestrating agent can read final answers without slurping full streams.
#
# Subcommands:
#   duel   [--rw] [--name N] [--mc M] [--mx M] [--wait] "PROMPT"
#   spawn  <claude|codex> [--rw] [--dir D] [--name N] "PROMPT"
#   review [--base REF | --uncommitted | --commit SHA] [--by claude|codex|both]
#   attach [NAME]        status        clean [NAME]
#   install-review-hook  [--global]
#
# Conventions:
#   - Read-only is the default everywhere. In `duel`, --rw isolates each arm in
#     its own git worktree+branch so the two parallel edits never clobber. In
#     `spawn`, --rw lets the single peer edit the target dir IN PLACE (that's the
#     point of delegation); pass --dir <worktree> if you want it isolated.
#   - Prompts are fed on STDIN to both CLIs (claude -p reads stdin; codex exec -).
#   - Codex defaults: gpt-5.5 / xhigh (machine config). Override with --mx.
#   - Artifacts live under  ~/.ensemble/<kind>/<name>/  (*.out = clean answer,
#     *.log = full pane stream, *.done = agent exit code).

set -uo pipefail

ROOT_DEFAULT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
BASE_DIR="$HOME/.ensemble"
CODEX_MODEL_DEFAULT="gpt-5.5"
CODEX_EFFORT_DEFAULT="xhigh"

die() { echo "[ensemble] error: $*" >&2; exit 2; }
have() { command -v "$1" >/dev/null 2>&1; }
_realpath() {  # resolve symlinks portably (BSD/macOS readlink has no -f)
  local p="$1" d
  while [ -h "$p" ]; do
    d="$(cd -P "$(dirname "$p")" >/dev/null 2>&1 && pwd)"
    p="$(readlink "$p")"; case "$p" in /*) ;; *) p="$d/$p";; esac
  done
  d="$(cd -P "$(dirname "$p")" >/dev/null 2>&1 && pwd)"; printf '%s/%s\n' "$d" "$(basename "$p")"
}
slug() { echo "$1" | tr '[:upper:] ' '[:lower:]-' | tr -cd 'a-z0-9-' | cut -c1-32; }

have tmux || die "tmux not found"
have git  || die "git not found"

# Agent invocations that READ THE PROMPT FROM STDIN (no positional prompt arg).
# $1=mode(ro|rw) $2=model(or "") $3=workdir
claude_cmd() {
  local pm; [ "$1" = rw ] && pm=bypassPermissions || pm=plan
  local m=""; [ -n "$2" ] && m="--model $2"
  printf 'claude -p %s --permission-mode %s --add-dir %q --output-format text' "$m" "$pm" "$3"
}
# $1=mode $2=model $3=effort $4=workdir $5=outfile  (trailing '-' = read stdin)
codex_cmd() {
  local sb; [ "$1" = rw ] && sb="--sandbox workspace-write --full-auto" || sb="--sandbox read-only"
  printf "codex exec -C %q --skip-git-repo-check %s -m %s -c model_reasoning_effort=%q -c service_tier='\"fast\"' -o %q -" \
    "$4" "$sb" "$2" "\"$3\"" "$5"
}

# Resolve a friendly model name (or full id) to "family|model-id".
_resolve_model() {
  case "$1" in
    opus)       echo "claude|claude-opus-4-8";;
    fable)      echo "claude|claude-fable-5";;
    sonnet)     echo "claude|claude-sonnet-4-6";;
    haiku)      echo "claude|claude-haiku-4-5-20251001";;
    claude-*)   echo "claude|$1";;
    codex)      echo "codex|$CODEX_MODEL_DEFAULT";;
    gpt-*|gpt5*|o[0-9]*) echo "codex|$1";;
    *)          echo "|$1";;   # unknown family -> caller errors
  esac
}

# Run one agent in a tmux pane: stream live, tee clean answer to OUT, capture the
# whole pane to LOG, and write the AGENT's exit code (not tee's) to DONE.
#   $1=tmux target  $2=title  $3=agent-cmd(reads stdin)  $4=prompt
#   $5=out  $6=log  $7=done
# A generated bash runner owns all redirection/quoting so the pane's interactive
# shell (which may be zsh/fish) only has to invoke `bash <runner>`. This also
# keeps PIPESTATUS in bash and avoids losing keystrokes to a not-yet-ready shell.
# NOTE: $out must NOT equal a file the agent also writes itself (e.g. codex -o);
# pass a separate stream file in that case.
launch_pane() {
  local target="$1" title="$2" agent="$3" prompt="$4" out="$5" log="$6" done="$7"
  rm -f "$done"; : >"$log"; : >"$out"
  local base="${log%.log}"
  local pf="$base.prompt"; printf '%s' "$prompt" >"$pf"
  local runner="$base.run.sh"
  {
    printf '#!/usr/bin/env bash\nset -uo pipefail\n'
    printf '{\n  cat %q | %s | tee %q\n  echo ${PIPESTATUS[1]} > %q\n} 2>&1 | tee %q\n' \
      "$pf" "$agent" "$out" "$done" "$log"
    printf 'echo "[ensemble] %s finished (exit $(cat %q))"\n' "$title" "$done"
  } >"$runner"
  chmod +x "$runner"
  tmux select-pane -t "$target" -T "$title" 2>/dev/null
  tmux send-keys -t "$target" -l "bash $(printf %q "$runner")"
  tmux send-keys -t "$target" Enter
}

new_session() { # $1=name $2=cwd
  tmux kill-session -t "$1" 2>/dev/null
  tmux new-session -d -s "$1" -x 220 -y 50 -c "$2"
  tmux set-option -t "$1" pane-border-status top 2>/dev/null
  tmux set-option -t "$1" pane-border-format " #{pane_title} " 2>/dev/null
}

cmd_duel() {
  local mode=ro name="" mc="" mx="$CODEX_MODEL_DEFAULT" eff="$CODEX_EFFORT_DEFAULT" wait=0 prompt=""
  while [ $# -gt 0 ]; do case "$1" in
    --rw) mode=rw;; --name) name="$2"; shift;; --mc) mc="$2"; shift;;
    --mx) mx="$2"; shift;; --eff) eff="$2"; shift;; --wait) wait=1;; --) shift; prompt="$*"; break;;
    -*) die "unknown duel flag $1";; *) prompt="$*"; break;;
  esac; shift; done
  [ -n "$prompt" ] || die "duel needs a PROMPT"
  local root="$ROOT_DEFAULT"
  [ -z "$name" ] && name="$(slug "$prompt")-$(date +%s)"
  local dir="$BASE_DIR/duel/$name"; mkdir -p "$dir"
  local sess="duel-$name" cwd_c="$root" cwd_x="$root"

  if [ "$mode" = rw ]; then
    git -C "$root" rev-parse HEAD >/dev/null 2>&1 || die "rw mode needs a git repo with a commit"
    cwd_c="$dir/wt-claude"; cwd_x="$dir/wt-codex"
    git -C "$root" worktree add -f -B "ens/$name/claude" "$cwd_c" HEAD >/dev/null || die "worktree add (claude) failed"
    git -C "$root" worktree add -f -B "ens/$name/codex"  "$cwd_x" HEAD >/dev/null || die "worktree add (codex) failed"
    echo "[ensemble] worktrees: $cwd_c (ens/$name/claude) | $cwd_x (ens/$name/codex)"
  fi

  new_session "$sess" "$cwd_c"
  tmux split-window -h -t "$sess" -c "$cwd_x"
  tmux select-layout -t "$sess" even-horizontal

  launch_pane "$sess.0" "CLAUDE" "$(claude_cmd "$mode" "$mc" "$cwd_c")" \
    "$prompt" "$dir/claude.out" "$dir/claude.log" "$dir/claude.done"
  # codex writes its clean answer via -o (codex.out); the pane tee mirrors the noisy
  # live stream to a SEPARATE file (codex.stream) so the two never race on codex.out.
  launch_pane "$sess.1" "CODEX" "$(codex_cmd "$mode" "$mx" "$eff" "$cwd_x" "$dir/codex.out")" \
    "$prompt" "$dir/codex.stream" "$dir/codex.log" "$dir/codex.done"

  echo "[ensemble] duel '$name' launched (mode=$mode)"
  echo "[ensemble]   watch:  tmux attach -t $sess"
  echo "[ensemble]   claude: $dir/claude.out   codex: $dir/codex.out   dir: $dir"
  if [ "$wait" = 1 ]; then
    local to="${ENSEMBLE_WAIT_TIMEOUT:-1800}" t=0
    echo "[ensemble] waiting for both arms (timeout ${to}s)..."
    while [ ! -f "$dir/claude.done" ] || [ ! -f "$dir/codex.done" ]; do
      sleep 3; t=$((t+3))
      if [ "$t" -ge "$to" ]; then echo "[ensemble] WAIT TIMEOUT after ${to}s (claude.done=$([ -f "$dir/claude.done" ] && echo y || echo n) codex.done=$([ -f "$dir/codex.done" ] && echo y || echo n)); panes still live, attach to inspect"; return 1; fi
    done
    echo "[ensemble] both done. claude exit=$(cat "$dir/claude.done") codex exit=$(cat "$dir/codex.done")"
  fi
}

cmd_spawn() {
  local who="${1:-}"; shift || true
  [ "$who" = claude ] || [ "$who" = codex ] || die "spawn needs: claude|codex"
  local mode=ro name="" dir_in="" prompt="" mc="" mx="$CODEX_MODEL_DEFAULT" eff="$CODEX_EFFORT_DEFAULT"
  while [ $# -gt 0 ]; do case "$1" in
    --rw) mode=rw;; --name) name="$2"; shift;; --dir) dir_in="$2"; shift;;
    --mc) mc="$2"; shift;; --mx) mx="$2"; shift;; --eff) eff="$2"; shift;; --) shift; prompt="$*"; break;;
    -*) die "unknown spawn flag $1";; *) prompt="$*"; break;;
  esac; shift; done
  [ -n "$prompt" ] || die "spawn needs a PROMPT"
  local wd="${dir_in:-$ROOT_DEFAULT}"
  [ -z "$name" ] && name="$who-$(slug "$prompt")-$(date +%s)"
  local dir="$BASE_DIR/spawn/$name"; mkdir -p "$dir"
  local sess="ensemble"
  if tmux has-session -t "$sess" 2>/dev/null; then tmux new-window -t "$sess" -n "$name" -c "$wd"
  else new_session "$sess" "$wd"; tmux rename-window -t "$sess" "$name"; fi
  local agent tee_target
  if [ "$who" = claude ]; then
    agent="$(claude_cmd "$mode" "$mc" "$wd")"; tee_target="$dir/out.txt"   # claude stdout is clean
  else
    agent="$(codex_cmd "$mode" "$mx" "$eff" "$wd" "$dir/out.txt")"          # -o owns out.txt
    tee_target="$dir/stream.txt"                                            # noisy live stream only
  fi
  launch_pane "$sess" "$name" "$agent" "$prompt" "$tee_target" "$dir/run.log" "$dir/run.done"
  echo "[ensemble] spawned $who as window '$name' in session '$sess'"
  echo "[ensemble]   watch: tmux attach -t $sess   out: $dir/out.txt   done: $dir/run.done"
}

# Headless, cost-aware delegation to ANY model. Model-agnostic: --to picks the
# implementer (auto-routes to Codex or Claude by model family); runs in the
# background (zombie-proof) writing to ~/.ensemble/dispatch so it shows in `jobs`.
#   ensemble delegate --to <model> [--from <model>] [--eff E] [--ro] [--name N] [--dir D] "PROMPT"
cmd_delegate() {
  local to="" from="" eff="$CODEX_EFFORT_DEFAULT" mode=rw name="" prompt="" wd="$ROOT_DEFAULT"
  while [ $# -gt 0 ]; do case "$1" in
    --to) to="$2"; shift;; --from) from="$2"; shift;; --eff) eff="$2"; shift;;
    --ro) mode=ro;; --name) name="$2"; shift;; --dir) wd="$2"; shift;;
    --) shift; prompt="$*"; break;; -*) die "unknown delegate flag $1";; *) prompt="$*"; break;;
  esac; shift; done
  [ -n "$to" ] || die "delegate needs --to <model> (opus|fable|sonnet|haiku|codex|gpt-5.5|claude-…|gpt-…)"
  [ -n "$prompt" ] || die "delegate needs a PROMPT"
  local r fam id; r="$(_resolve_model "$to")"; fam="${r%%|*}"; id="${r#*|}"
  [ -n "$fam" ] || die "unknown model '$to' — try: opus|fable|sonnet|haiku|codex|gpt-5.5|claude-…|gpt-…"
  [ -z "$name" ] && name="d-$(slug "$to")-$(date +%s)"
  local dir="$BASE_DIR/dispatch"; mkdir -p "$dir"
  local log="$dir/$name.log" out="$dir/$name.out" done="$dir/$name.done" pf="$dir/$name.prompt" runner="$dir/$name.run.sh"
  rm -f "$done"; printf '%s' "$prompt" >"$pf"
  local agent pipeline
  if [ "$fam" = claude ]; then
    agent="$(claude_cmd "$mode" "$id" "$wd")"
    pipeline="cat $(printf %q "$pf") | $agent | tee $(printf %q "$out")"
  else
    agent="$(codex_cmd "$mode" "$id" "$eff" "$wd" "$out")"
    pipeline="cat $(printf %q "$pf") | $agent"
  fi
  # cd into the work dir so the implementer treats it as the project (Claude has no
  # -C; without this it would run in the caller's cwd). Harmless for Codex (uses -C too).
  printf '#!/usr/bin/env bash\nset -uo pipefail\ncd %q || exit 1\n%s\nexit ${PIPESTATUS[1]}\n' "$wd" "$pipeline" > "$runner"
  echo "[delegate] from=${from:-this session} -> to=$id ($fam)  mode=$mode$([ "$fam" = codex ] && echo "  eff=$eff")"
  echo "[delegate] run '$name'  |  follow: ensemble tail $name  |  clean result: $out"
  ( timeout -k 1m "${ENSEMBLE_DELEGATE_TIMEOUT:-30m}" bash "$runner" </dev/null >"$log" 2>&1; echo $? >"$done" ) &
  local cpid=$!
  tail -n +1 --pid="$cpid" -f "$log"
  echo "[delegate] $name finished (exit $(cat "$done"))  — read result: $out"
}

# Peer review of a diff. Default reviewer = codex (the free peer); --by both runs both.
cmd_review() {
  local sel="--uncommitted" by="codex" mx="$CODEX_MODEL_DEFAULT" eff="high"
  while [ $# -gt 0 ]; do case "$1" in
    --base) sel="--base $2"; shift;; --commit) sel="--commit $2"; shift;;
    --uncommitted) sel="--uncommitted";; --by) by="$2"; shift;;
    --mx) mx="$2"; shift;; *) die "unknown review flag $1";;
  esac; shift; done
  local root="$ROOT_DEFAULT"
  local dir="$BASE_DIR/review/$(date +%s)"; mkdir -p "$dir"
  local diff="$dir/diff.patch"
  case "$sel" in
    *--base*)   git -C "$root" diff "${sel#--base }"...HEAD >"$diff";;
    *--commit*) git -C "$root" show "${sel#--commit }" >"$diff";;
    *)          if git -C "$root" rev-parse HEAD >/dev/null 2>&1; then
                  git -C "$root" diff HEAD >"$diff"
                else { git -C "$root" diff; git -C "$root" diff --cached; } >"$diff"; fi;;
  esac
  if [ ! -s "$diff" ]; then echo "[ensemble] no changes to review ($sel)"; return 0; fi

  run_codex() {
    echo "===== CODEX REVIEW ($sel) ====="
    codex exec review $sel -m "$mx" -c model_reasoning_effort='"'"$eff"'"' -o "$dir/codex.out" >"$dir/codex.log" 2>&1 \
      || codex exec -C "$root" --skip-git-repo-check --sandbox read-only -m "$mx" \
           -c model_reasoning_effort='"'"$eff"'"' -o "$dir/codex.out" - >>"$dir/codex.log" 2>&1 <<EOF
Review this diff read-only for correctness bugs, security issues, and risky changes.
Be specific (file:line), rank by severity, end with a SHIP or HOLD verdict.

$(cat "$diff")
EOF
    cat "$dir/codex.out" 2>/dev/null
  }
  run_claude() {
    echo "===== CLAUDE REVIEW ($sel) ====="
    claude -p --permission-mode plan --add-dir "$root" --output-format text <<EOF | tee "$dir/claude.out"
You are reviewing a pending push, read-only. Review this diff for correctness bugs,
security issues, regressions, and risky changes. Rank findings by severity with
file:line refs; end with SHIP or HOLD.

$(cat "$diff")
EOF
  }
  case "$by" in
    codex)  run_codex;;
    claude) run_claude;;
    both)   run_claude; echo; run_codex;;
    *) die "--by must be claude|codex|both";;
  esac
  echo "[ensemble] review saved under $dir" >&2
}

cmd_attach() { tmux attach -t "${1:-ensemble}"; }

cmd_status() {
  echo "== tmux sessions =="; tmux ls 2>/dev/null | grep -E 'duel-|ensemble' || echo "(none)"
  echo "== recent runs =="
  local d s
  for d in "$BASE_DIR"/duel/* "$BASE_DIR"/spawn/*; do
    [ -d "$d" ] || continue
    s="running"; ls "$d"/*.done >/dev/null 2>&1 && s="done($(cat "$d"/*.done 2>/dev/null | tr '\n' ',' ))"
    echo "  $d  [$s]"
  done
  echo "== ensemble worktrees =="; git -C "$ROOT_DEFAULT" worktree list 2>/dev/null | grep -E 'ens/|wt-claude|wt-codex' || echo "(none)"
}

cmd_clean() {
  local name="${1:-}" w b pat
  # With NAME: remove only that run's session, dir, worktrees, and ens/<name>/* branches.
  # Without NAME (use --all): prune every ensemble worktree + ens/* branch.
  if [ "$name" = --all ]; then name=""; fi
  if [ -n "$name" ]; then
    tmux kill-session -t "duel-$name" 2>/dev/null
    pat="/duel/$name/wt-|/spawn/$name/"; local brpat="ens/$name/"
    git -C "$ROOT_DEFAULT" worktree list --porcelain 2>/dev/null | awk '/^worktree /{print $2}' | grep -E "$pat" | while read -r w; do
      git -C "$ROOT_DEFAULT" worktree remove --force "$w" 2>/dev/null
    done
    git -C "$ROOT_DEFAULT" worktree prune 2>/dev/null
    for b in $(git -C "$ROOT_DEFAULT" branch --list "$brpat*" 2>/dev/null | tr -d ' *'); do
      git -C "$ROOT_DEFAULT" branch -D "$b" 2>/dev/null
    done
    rm -rf "$BASE_DIR/duel/$name" "$BASE_DIR/spawn/$name"
    echo "[ensemble] cleaned run '$name' (its worktrees + ens/$name/* branches)"
  else
    git -C "$ROOT_DEFAULT" worktree list --porcelain 2>/dev/null | awk '/^worktree /{print $2}' | grep -E 'wt-claude|wt-codex' | while read -r w; do
      git -C "$ROOT_DEFAULT" worktree remove --force "$w" 2>/dev/null
    done
    git -C "$ROOT_DEFAULT" worktree prune 2>/dev/null
    for b in $(git -C "$ROOT_DEFAULT" branch --list 'ens/*' 2>/dev/null | tr -d ' *'); do
      git -C "$ROOT_DEFAULT" branch -D "$b" 2>/dev/null
    done
    echo "[ensemble] cleaned ALL ensemble worktrees + ens/* branches"
  fi
}

cmd_install_hook() {
  local scope="repo"; [ "${1:-}" = --global ] && scope="global"
  local self; self="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/ensemble.sh"
  local hookfile
  if [ "$scope" = global ]; then
    local hp="$HOME/.config/git/hooks"; mkdir -p "$hp"
    git config --global core.hooksPath "$hp"; hookfile="$hp/pre-push"
  else
    local gd; gd="$(git rev-parse --git-dir 2>/dev/null)" || die "not in a git repo"
    mkdir -p "$gd/hooks"; hookfile="$gd/hooks/pre-push"
  fi
  cat >"$hookfile" <<EOF
#!/usr/bin/env bash
# Auto-installed by ensemble: peer-review the push before it goes out.
# Bypass once with:  ENSEMBLE_REVIEW=0 git push     reviewer: ENSEMBLE_REVIEWER=claude|codex|both
if [ "\${ENSEMBLE_REVIEW:-1}" != 0 ]; then
  UP="\$(git rev-parse --abbrev-ref --symbolic-full-name @{u} 2>/dev/null)"
  SEL="--uncommitted"; [ -n "\$UP" ] && SEL="--base \$UP"
  echo "[ensemble] peer-reviewing push (\$SEL)..." >&2
  "$self" review \$SEL --by "\${ENSEMBLE_REVIEWER:-codex}" 1>&2
  if [ -t 1 ] && [ -e /dev/tty ]; then
    printf '\\n[ensemble] push anyway? [y/N] ' >&2; read -r a </dev/tty
    case "\$a" in y|Y|yes) :;; *) echo "[ensemble] push aborted." >&2; exit 1;; esac
  fi
fi
# Chain to a repo-local classic hook if one exists (so global install never
# silently disables a repo's own pre-push). Guarded against calling itself.
CLASSIC="\$(git rev-parse --absolute-git-dir 2>/dev/null)/hooks/pre-push"
SELF_RP="\$(readlink -f "\$0" 2>/dev/null || echo "\$0")"
CLASSIC_RP="\$(readlink -f "\$CLASSIC" 2>/dev/null || echo "\$CLASSIC")"
if [ -x "\$CLASSIC" ] && [ "\$CLASSIC_RP" != "\$SELF_RP" ]; then exec "\$CLASSIC" "\$@"; fi
exit 0
EOF
  chmod +x "$hookfile"
  echo "[ensemble] pre-push review hook installed ($scope): $hookfile"
  echo "[ensemble]   bypass once: ENSEMBLE_REVIEW=0 git push   |  reviewer env: ENSEMBLE_REVIEWER=claude|codex|both"
}

# Self-check: verify every moving part either agent relies on. Exit 1 on any FAIL.
cmd_doctor() {
  local P=0 W=0 F=0
  ok()   { echo "  [ OK ] $*"; P=$((P+1)); }
  warn() { echo "  [WARN] $*"; W=$((W+1)); }
  bad()  { echo "  [FAIL] $*"; F=$((F+1)); }
  net_ok() { # $1=host  — true if we can open a TLS/HTTP connection
    if have curl; then curl -sS --max-time 6 -o /dev/null "https://$1/" 2>/dev/null; return $?; fi
    if have wget; then wget -q --timeout=6 -O /dev/null "https://$1/" 2>/dev/null; return $?; fi
    timeout 6 bash -c "exec 3<>/dev/tcp/$1/443" 2>/dev/null   # last-resort TCP probe
  }

  echo "ensemble doctor — environment self-check"
  echo "[CLIs]"
  if have ensemble; then
    local ep; ep="$(command -v ensemble)"
    local rp; rp="$(_realpath "$ep" 2>/dev/null || echo "$ep")"
    [ "$rp" = "$(_realpath "${BASH_SOURCE[0]}")" ] && ok "ensemble on PATH -> $rp" \
      || warn "ensemble on PATH ($ep) resolves to $rp, not this script"
  else warn "ensemble not on PATH (use full script path, or symlink into ~/.local/bin)"; fi
  if have claude; then ok "claude: $(claude --version 2>/dev/null | head -1)"; else bad "claude not found on PATH"; fi
  if have codex;  then ok "codex:  $(codex --version 2>/dev/null | head -1)";  else bad "codex not found on PATH"; fi
  if have tmux;   then ok "tmux:   $(tmux -V)"; else bad "tmux not found"; fi

  echo "[tmux server]"
  if tmux ls >/dev/null 2>&1; then
    ok "a tmux server is already running -> Codex panes attach to it and get network even when sandboxed"
  else
    warn "no tmux server running yet -> the FIRST launch starts one; if started from inside a no-network sandbox the agent arm can't reach its API (run one duel from Claude first, or escalate)"
  fi

  echo "[skill + entry points]"
  [ -f "$HOME/.claude/skills/ensemble/SKILL.md" ] && ok "claude skill present (canonical)" || bad "missing ~/.claude/skills/ensemble/SKILL.md"
  if [ -L "$HOME/.codex/skills/ensemble" ] && [ -f "$HOME/.codex/skills/ensemble/SKILL.md" ]; then ok "codex skill symlink resolves"
  elif [ -e "$HOME/.codex/skills/ensemble" ]; then warn "~/.codex/skills/ensemble exists but isn't a resolving symlink"
  else warn "codex can't see the skill (no ~/.codex/skills/ensemble symlink)"; fi
  local c; for c in duel spawn ensemble-review ensemble-doctor; do
    [ -f "$HOME/.claude/commands/$c.md" ]    && ok "claude /$c command" || warn "missing claude command /$c"
    [ -e "$HOME/.codex/skills/$c/SKILL.md" ] && ok "codex \$$c skill"   || warn "missing codex skill $c"
  done

  echo "[push review hook]"
  local hp; hp="$(git config --global --get core.hooksPath || echo '')"
  if [ -n "$hp" ] && [ -x "$hp/pre-push" ] && grep -q ensemble "$hp/pre-push" 2>/dev/null; then
    ok "global pre-push review hook active ($hp/pre-push)"
  else warn "no global ensemble pre-push hook (run: ensemble install-review-hook --global)"; fi

  echo "[workspace]"
  if mkdir -p "$BASE_DIR" 2>/dev/null && [ -w "$BASE_DIR" ]; then ok "artifacts dir writable ($BASE_DIR)"
  else bad "cannot write artifacts dir $BASE_DIR (sandbox read-only?)"; fi

  echo "[network reachability]  (FAIL here from a Codex session = sandbox blocked network -> escalate the run)"
  net_ok api.anthropic.com && ok "api.anthropic.com reachable (claude arm can run)" || warn "api.anthropic.com NOT reachable from this context"
  net_ok api.openai.com    && ok "api.openai.com reachable (codex arm can run)"    || warn "api.openai.com NOT reachable from this context"

  echo "----"
  echo "summary: $P ok, $W warn, $F fail"
  [ "$F" -eq 0 ]
}

# ---- observability: one place to see/tail every run, from any terminal --------
hms() { local s="${1:-0}"; if [ "$s" -lt 60 ]; then echo "${s}s"; elif [ "$s" -lt 3600 ]; then echo "$((s/60))m"; else echo "$((s/3600))h$(((s%3600)/60))m"; fi; }
_age() { local m; m=$(stat -c %Y "$1" 2>/dev/null) || { echo 0; return; }; echo $(( $(date +%s) - m )); }
_donestat() { [ -f "$1" ] && echo "done($(tr -d '\n' <"$1"))" || echo "running"; }

# Emit one TAB-separated record per run: kind  name  status  age_secs  logpath
_emit_jobs() {
  local d f name st lg
  for d in "$BASE_DIR"/duel/*/; do [ -d "$d" ] || continue; d="${d%/}"; name=$(basename "$d")
    if [ -f "$d/claude.done" ] && [ -f "$d/codex.done" ]; then
      st="done(c:$(tr -d '\n' <"$d/claude.done"),x:$(tr -d '\n' <"$d/codex.done"))"
    else st="running"; fi
    printf 'duel\t%s\t%s\t%s\t%s\n' "$name" "$st" "$(_age "$d")" "$d/codex.log"
  done
  for d in "$BASE_DIR"/spawn/*/; do [ -d "$d" ] || continue; d="${d%/}"; name=$(basename "$d")
    printf 'spawn\t%s\t%s\t%s\t%s\n' "$name" "$(_donestat "$d/run.done")" "$(_age "$d")" "$d/run.log"
  done
  for d in "$BASE_DIR"/review/*/; do [ -d "$d" ] || continue; d="${d%/}"; name=$(basename "$d")
    st="running"; { [ -s "$d/codex.out" ] || [ -s "$d/claude.out" ]; } && st="done"
    lg="$d/codex.log"; [ -f "$lg" ] || lg="$d/claude.out"
    printf 'review\t%s\t%s\t%s\t%s\n' "$name" "$st" "$(_age "$d")" "$lg"
  done
  for f in "$HOME"/.codex/dispatch/*.log "$BASE_DIR"/dispatch/*.log; do [ -f "$f" ] || continue; name=$(basename "$f" .log)
    printf 'dispatch\t%s\t%s\t%s\t%s\n' "$name" "$(_donestat "${f%.log}.done")" "$(_age "$f")" "$f"
  done
}

cmd_jobs() {
  if [ "${1:-}" = --porcelain ]; then _emit_jobs; return; fi   # raw TAB records for the TUI
  local rows; rows="$(_emit_jobs)"
  if [ -z "$rows" ]; then echo "no runs yet (nothing under ~/.ensemble or ~/.codex/dispatch)"; return; fi
  printf '%-9s %-26s %-24s %-6s %s\n' KIND NAME STATUS AGE OUTPUT
  echo "$rows" | sort -t"$(printf '\t')" -k4,4n | while IFS="$(printf '\t')" read -r kind name st age log; do
    printf '%-9s %-26s %-24s %-6s %s\n' "$kind" "${name:0:26}" "$st" "$(hms "$age")" "$log"
  done
  echo
  echo "follow a run:  ensemble tail <name|last>     live dashboard:  ensemble watch"
}

cmd_tail() {
  local id="${1:-last}" rows row log st
  rows="$(_emit_jobs)"; [ -n "$rows" ] || { echo "no runs yet"; return 1; }
  if [ "$id" = last ]; then row="$(echo "$rows" | sort -t"$(printf '\t')" -k4,4n | head -1)"
  else
    row="$(echo "$rows" | awk -F"$(printf '\t')" -v n="$id" '$2==n{print;exit}')"
    [ -n "$row" ] || row="$(echo "$rows" | awk -F"$(printf '\t')" -v n="$id" 'index($2,n){print;exit}')"
  fi
  [ -n "$row" ] || { echo "no run matching '$id' — see: ensemble jobs"; return 1; }
  st="$(echo "$row" | cut -f3)"; log="$(echo "$row" | cut -f5)"
  [ -f "$log" ] || { echo "log not found: $log"; return 1; }
  case "$st" in
    running*) echo "[ensemble] tailing live: $log  (Ctrl-C to stop)"; tail -n 200 -f "$log";;
    *)        echo "[ensemble] $st — showing $log"; tail -n 400 "$log";;
  esac
}

cmd_watch() {
  local interval="${1:-2}"
  while true; do
    printf '\033[2J\033[H'
    printf 'ensemble watch — every %ss, Ctrl-C to exit   %s\n\n' "$interval" "$(date '+%Y-%m-%d %H:%M:%S')"
    cmd_jobs
    sleep "$interval" || break
  done
}

# Interactive curses dashboard (Python stdlib; falls back to `watch` if unavailable).
cmd_dash() {
  local self repo tui
  self="$(_realpath "${BASH_SOURCE[0]}")"
  repo="$(cd "$(dirname "$self")/../../.." && pwd)"
  tui="$repo/bin/ensemble-tui"
  if ! { [ -t 0 ] && [ -t 1 ]; }; then
    echo "[ensemble] 'dash' is an interactive TUI and needs a real terminal — it can't run"
    echo "           inside the agent's command box or a pipe. Run it from a normal shell:"
    echo "               ensemble dash"
    echo "           or detached in tmux (attach from anywhere):"
    echo "               tmux new -s dash 'ensemble dash'   # then: tmux attach -t dash"
    echo "[ensemble] one-shot snapshot instead:"; echo
    cmd_jobs; return 0
  fi
  if have python3 && [ -f "$tui" ]; then ENSEMBLE_BIN="$self" exec python3 "$tui"
  else echo "[ensemble] dashboard needs python3 + $tui — falling back to text watch"; cmd_watch "$@"; fi
}

sub="${1:-}"; shift || true
case "$sub" in
  duel)                cmd_duel "$@";;
  spawn)               cmd_spawn "$@";;
  delegate)            cmd_delegate "$@";;
  review)              cmd_review "$@";;
  attach)              cmd_attach "$@";;
  jobs)                cmd_jobs "$@";;
  tail)                cmd_tail "$@";;
  watch)               cmd_watch "$@";;
  dash|tui|dashboard)  cmd_dash "$@";;
  status)              cmd_status "$@";;
  clean)               cmd_clean "$@";;
  doctor)              cmd_doctor "$@";;
  install-review-hook) cmd_install_hook "$@";;
  *) cat >&2 <<USAGE
ensemble — Claude + Codex together (tmux-visible)
  duel [--rw] [--name N] [--mc M] [--mx M] [--eff low|medium|high|xhigh] [--wait] "PROMPT"
       both models answer the same prompt in side-by-side panes; --rw isolates
       each in its own git worktree+branch for parallel editing.
  spawn <claude|codex> [--rw] [--dir D] [--mx M] [--eff low|medium|high|xhigh] "PROMPT"
       launch one peer in a viewable tmux window (delegation you can watch).
       --eff scales Codex reasoning to the task (default xhigh; lower = faster).
  delegate --to <model> [--from <model>] [--eff E] [--ro] [--name N] [--dir D] "PROMPT"
       headless cost-aware delegation to ANY model (opus|fable|sonnet|haiku|codex|
       gpt-5.5|claude-…|gpt-…); auto-routes to the Codex or Claude CLI; runs in the
       background and shows in `ensemble jobs` (follow with `ensemble tail <name>`).
  review [--base REF|--uncommitted|--commit SHA] [--by claude|codex|both]
       peer-review a diff (default reviewer: codex).
  jobs                 list every run (duel/spawn/review/dispatch) + status, from anywhere
  tail <NAME|last>     follow a run's output live (works even if launched elsewhere)
  dash                 interactive TUI dashboard (select/attach/kill/filter); watch = plain text
  attach [NAME] | status | clean <NAME|--all> | doctor | install-review-hook [--global]
USAGE
     exit 1;;
esac
