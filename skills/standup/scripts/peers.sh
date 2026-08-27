#!/usr/bin/env bash
# peers.sh — evidence half of a standup: which agent sessions are live, which
# working tree each one sits in, and where two agents can actually collide.
#   same working tree  = HARD collision (same files, same index)
#   same repo, diff wt = SOFT collision (shared refs/branches, pushes, migrations)
# Read-only: never touches a working tree. Linux/WSL (needs /proc).
set -uo pipefail

ONLY_REPO=0
[ "${1:-}" = --repo ] && ONLY_REPO=1   # only sessions sharing THIS session's repo

[ -r /proc/self/cwd ] || { echo "peers.sh needs /proc (Linux/WSL only)"; exit 1; }
MYREPO=$(git rev-parse --path-format=absolute --git-common-dir 2>/dev/null); MYREPO="${MYREPO%/.git}"
MYWT=$(git rev-parse --show-toplevel 2>/dev/null)

# One row per SESSION: an agent process whose parent is also an agent process is a
# child of that session, not a session of its own.
rows=$(ps -eo pid=,ppid=,comm=,args= 2>/dev/null | awk '
  { c=$3; l=tolower($0) }
  (c=="codex"||c=="claude" || l ~ /codex exec|codex resume|claude -p/) \
    && l !~ /ensemble\.sh|ensemble-tui|status\.py|peers\.sh|maestro\/bin|awk| -eo / {
    pid[$1]=1; par[$1]=$2
    kind[$1] = (c=="codex") ? "codex" : (c=="claude") ? "claude" \
             : ($4 ~ /(^|\/)codex$/) ? "codex" : ($4 ~ /(^|\/)claude$/) ? "claude" \
             : (l ~ /codex (exec|resume)/) ? "codex" : "claude" }
  END { for (p in pid) if (!(par[p] in pid)) printf "%s\t%s\n", p, kind[p] }')
[ -z "$rows" ] && { echo "(no live claude/codex agent processes)"; exit 0; }

tmp=$(mktemp); trap 'rm -f "$tmp"' EXIT
# repo<TAB>worktree<TAB>pid<TAB>kind<TAB>branch<TAB>dirtycount
while IFS=$'\t' read -r pid kind; do
  cwd=$(readlink "/proc/$pid/cwd" 2>/dev/null); [ -n "$cwd" ] || continue
  wt=$(git -C "$cwd" rev-parse --show-toplevel 2>/dev/null)
  repo=$(git -C "$cwd" rev-parse --path-format=absolute --git-common-dir 2>/dev/null)
  repo="${repo%/.git}"
  if [ -z "$wt" ]; then                        # session outside any git worktree
    [ "$ONLY_REPO" = 1 ] && continue           # ...never in scope for --repo
    printf -- '-\t%s\t%s\t%s\t-\t-\n' "$cwd" "$pid" "$kind" >>"$tmp"; continue
  fi
  [ "$ONLY_REPO" = 1 ] && [ "$repo" != "$MYREPO" ] && continue
  br=$(git -C "$wt" rev-parse --abbrev-ref HEAD 2>/dev/null)
  n=$(git -C "$wt" status --porcelain 2>/dev/null | wc -l)
  printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$repo" "$wt" "$pid" "$kind" "$br" "$n" >>"$tmp"
done <<<"$rows"

# Which row (if any) IS this session? Walk our own ancestry until we hit a listed
# pid — running from a plain shell, none of them is us and every row is a peer.
MYPID=""
p=$$
while [ -n "$p" ] && [ "$p" != 1 ]; do
  if cut -f3 "$tmp" | grep -qx "$p"; then MYPID="$p"; break; fi
  p=$(ps -o ppid= -p "$p" 2>/dev/null | tr -d ' ')
done

if [ "$ONLY_REPO" = 1 ]; then
  echo "== agent sessions in this repo: ${MYREPO:-not a git repo} =="
  total=$(wc -l <"$tmp"); [ -n "$MYPID" ] && peers=$((total - 1)) || peers=$total
  if [ "${peers:-0}" -le 0 ]; then
    echo "  no peer sessions in this repo — only you. Nothing to ping."
    echo "  (drop --repo to see every agent on the machine.)"
    exit 0
  fi
fi

echo "== live agent sessions =="
printf "  %-8s %-6s %-5s %-34s %s\n" PID AGENT DIRTY BRANCH "WORKING TREE"
sort "$tmp" | while IFS=$'\t' read -r repo wt pid kind br n; do
  tag=""; [ "$wt" = "$MYWT" ] && tag="  <- your tree"
  [ "$pid" = "$MYPID" ] && tag="  <- you"
  printf "  %-8s %-6s %-5s %-34s %s%s\n" "$pid" "$kind" "$n" "$br" "$wt" "$tag"
done
if cut -f4 "$tmp" | grep -qx codex; then
  echo "  note: codex sessions have no SendMessage inbox — evidence only, you cannot ping them."
fi

echo
echo "== collision surface =="
found=0
while read -r n wt; do
  [ "$n" -ge 2 ] || continue; found=1
  echo "  HARD  $n agents in the SAME working tree: $wt"
  awk -F'\t' -v w="$wt" '$2==w{printf "          pid %s (%s) on %s\n",$3,$4,$5}' "$tmp"
  git -C "$wt" status --porcelain 2>/dev/null | head -12 | sed 's/^/          /'
done < <(cut -f2 "$tmp" | sort | uniq -c | sort -rn)

while read -r n repo; do
  [ "$n" -ge 2 ] && [ "$repo" != - ] || continue
  wtn=$(awk -F'\t' -v r="$repo" '$1==r{print $2}' "$tmp" | sort -u | wc -l)
  [ "$wtn" -ge 2 ] || continue; found=1
  echo "  SOFT  $n agents in the SAME repo, $wtn working trees: $repo"
  awk -F'\t' -v r="$repo" '$1==r{printf "          pid %s (%s) on %-28s %s\n",$3,$4,$5,$2}' "$tmp" | sort -u
done < <(cut -f1 "$tmp" | sort | uniq -c | sort -rn)

[ "$found" = 0 ] && echo "  (none — every agent has its own working tree in its own repo)"
exit 0
