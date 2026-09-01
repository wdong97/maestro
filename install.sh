#!/usr/bin/env bash
# maestro install — wire this repo into the local Claude Code + Codex setup.
# The repo is the single source of truth; home-dir locations become symlinks into
# it, so editing a file here is live and `git pull` updates the whole system.
# Idempotent. Existing non-maestro files are backed up to <path>.maestro-bak.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE="$HOME/.claude"
# Codex reads CODEX_HOME when it is set — on some setups (orca, sandboxes, CI) that is
# NOT ~/.codex, and linking only into ~/.codex leaves Codex seeing none of these skills.
CODEX="${CODEX_HOME:-$HOME/.codex}"
CODEX_PLAIN="$HOME/.codex"
# The cross-agent root: any agent that follows the ~/.agents convention reads from here.
AGENTS="$HOME/.agents"
BIN="$HOME/.local/bin"
GITHOOKS="$HOME/.config/git/hooks"
STATE="$HOME/.config/maestro"

WITH_HOOK=1
for a in "$@"; do case "$a" in
  --no-hook) WITH_HOOK=0;;
  -h|--help) cat <<'HELP'
maestro install — wire this repo into ~/.claude, ~/.codex, ~/.local/bin, git hooks.

  ./install.sh              full install, including the global pre-push review hook
  ./install.sh --no-hook    everything EXCEPT the global git core.hooksPath change

The hook step sets git's global core.hooksPath, which overrides every repo's own
.git/hooks on this machine. Use --no-hook to skip it; you can install the review
hook per-repo later with `ensemble install-review-hook`.

Idempotent. Existing non-maestro files are backed up to <path>.maestro-bak.
HELP
    exit 0;;
  *) echo "unknown flag: $a (try: ./install.sh --help)" >&2; exit 2;;
esac; done

note() { printf '  %s\n' "$*"; }

# link <target> <linkpath> — point linkpath at target, backing up anything real.
link() {
  local target="$1" dest="$2"
  if [ -L "$dest" ] && [ "$(readlink -f "$dest")" = "$(readlink -f "$target")" ]; then
    note "ok    $dest"; return
  fi
  if [ -e "$dest" ] || [ -L "$dest" ]; then
    if [ ! -e "$dest.maestro-bak" ]; then mv "$dest" "$dest.maestro-bak"; note "bak   $dest -> $dest.maestro-bak"
    else rm -rf "$dest"; fi
  fi
  mkdir -p "$(dirname "$dest")"
  ln -sfn "$target" "$dest"
  note "link  $dest -> $target"
}

# ensure_import <file> <line> — append an @import line if not already present.
ensure_import() {
  local file="$1" line="$2"
  mkdir -p "$(dirname "$file")"; touch "$file"
  grep -qxF "$line" "$file" || printf '%s\n' "$line" >>"$file"
  note "import $file  <=  $line"
}

echo "maestro install from: $REPO"

# prune_root <dir> — drop symlinks into this repo whose target is gone, so a skill or
# command deleted upstream does not survive a `git pull && ./install.sh` as a dangling link.
prune_root() {
  local root="$1" entry
  [ -d "$root" ] || return 0
  for entry in "$root"/*; do
    [ -L "$entry" ] || continue
    case "$(readlink "$entry")" in "$REPO"/*) ;; *) continue;; esac
    [ -e "$entry" ] && continue          # -e follows the link: target still exists
    rm -f "$entry"; note "prune $entry (removed from the repo)"
    # put back whatever this link displaced, or it is stranded forever: uninstall can no
    # longer find it once our symlink is gone.
    if [ -e "$entry.maestro-bak" ] || [ -L "$entry.maestro-bak" ]; then
      mv "$entry.maestro-bak" "$entry"; note "restore $entry (from backup)"
    fi
  done
}

echo "[skills] -> claude, codex, and the shared ~/.agents root"
for d in "$REPO"/skills/*/; do
  name="$(basename "$d")"
  link "$d" "$CLAUDE/skills/$name"
  link "$d" "$CODEX/skills/$name"
  # when CODEX_HOME points elsewhere, cover plain ~/.codex too, so the skills are there
  # whether or not that variable is set in the shell that runs the agent
  [ "$CODEX" = "$CODEX_PLAIN" ] || link "$d" "$CODEX_PLAIN/skills/$name"
  link "$d" "$AGENTS/skills/$name"
done
# Prune every root we have ever installed into, not just this run's: changing CODEX_HOME
# must not leave the previous home full of dangling links.
{ printf '%s\n' "$CLAUDE/skills" "$CODEX/skills" "$CODEX_PLAIN/skills" "$AGENTS/skills"
  [ -f "$STATE/skill-roots" ] && cat "$STATE/skill-roots"
} | awk 'NF && !seen[$0]++' | while IFS= read -r root; do prune_root "$root"; done
[ "$CODEX" = "$CODEX_PLAIN" ] || note "note  CODEX_HOME=$CODEX (linked there as well as ~/.codex)"
# Record the roots we linked into. CODEX_HOME can differ between install and uninstall
# (it is an env var), and an uninstall that guesses leaves symlinks and backups behind.
mkdir -p "$STATE"
# Merge, never overwrite: reinstalling under a different CODEX_HOME must not make the
# previous root unknown to uninstall.
{ [ -f "$STATE/skill-roots" ] && cat "$STATE/skill-roots"
  printf '%s\n' "$CLAUDE/skills" "$CODEX/skills" "$CODEX_PLAIN/skills" "$AGENTS/skills"
} | awk 'NF && !seen[$0]++' >"$STATE/skill-roots.tmp" && mv "$STATE/skill-roots.tmp" "$STATE/skill-roots"
note "state $STATE/skill-roots (roots to clean on uninstall)"

echo "[commands] -> ~/.claude/commands (Claude slash commands)"
for f in "$REPO"/commands/*.md; do link "$f" "$CLAUDE/commands/$(basename "$f")"; done
prune_root "$CLAUDE/commands"

echo "[cli] -> ~/.local/bin/ensemble"
chmod +x "$REPO/skills/ensemble/scripts/ensemble.sh"
link "$REPO/skills/ensemble/scripts/ensemble.sh" "$BIN/ensemble"
case ":$PATH:" in *":$BIN:"*) ;; *) note "WARN  $BIN is not on PATH — add it to your shell rc";; esac

if [ -d "$REPO/bin" ]; then
  echo "[bin] -> ~/.local/bin (tui, future tools)"
  for f in "$REPO"/bin/*; do [ -f "$f" ] || continue; chmod +x "$f"; link "$f" "$BIN/$(basename "$f")"; done
fi

echo "[guidelines] -> both homes + @import"
link "$REPO/guidelines/coding-guidelines.md" "$CLAUDE/coding-guidelines.md"
link "$REPO/guidelines/coding-guidelines.md" "$CODEX_PLAIN/coding-guidelines.md"
ensure_import "$CLAUDE/CLAUDE.md" "@coding-guidelines.md"
ensure_import "$CODEX/AGENTS.md"  "@$CODEX_PLAIN/coding-guidelines.md"

if [ "$WITH_HOOK" = 1 ]; then
  echo "[hook] global pre-push peer review"
  chmod +x "$REPO/hooks/pre-push"
  link "$REPO/hooks/pre-push" "$GITHOOKS/pre-push"
  cur="$(git config --global --get core.hooksPath || true)"
  if [ "$cur" != "$GITHOOKS" ]; then
    # core.hooksPath is machine-global and overrides EVERY repo's own .git/hooks.
    # Record the previous value first so uninstall.sh can put it back exactly.
    mkdir -p "$STATE"; printf '%s\n' "$cur" >"$STATE/prev-hookspath"
    git config --global core.hooksPath "$GITHOOKS"
    note "set   core.hooksPath=$GITHOOKS   (was: ${cur:-unset})"
    note "NOTE  that setting is GLOBAL and takes precedence over each repo's own"
    note "      .git/hooks. Our pre-push chains to a repo-local one if it exists."
    note "      ./uninstall.sh restores it; skip it next time with --no-hook."
  else note "ok    core.hooksPath=$GITHOOKS"; fi
else
  echo "[hook] skipped (--no-hook) — no global git config touched"
  note "add it later per-repo:  ensemble install-review-hook"
  note "            or global:  ensemble install-review-hook --global"
fi

echo
echo "maestro installed — verifying:"
echo
"$BIN/ensemble" doctor || note "doctor found problems above; fix them, then re-run: ensemble doctor"
echo
echo "(slash commands / skills load in NEW agent sessions.)"
