---
name: skill-audit
description: Audit which agent skills are actually used, unused, duplicated, or broken across Claude and Codex, and mine chat logs for recurring requests. Use when the user asks which skills they use, wants to prune or consolidate skills, or asks for a skill audit. Reports only; any archive, merge, or delete waits for approval.
---

# skill-audit — what's used, what's dead weight, what keeps getting asked

Every installed skill costs context: its description loads into every session whether
it's used or not. This audit puts numbers on that. Which skills actually get used, which
never do, which exist twice, and which requests the user keeps typing that no skill
covers yet. It **reports**. Nothing gets moved or deleted until the user says so.

## 1. Run it

```
python3 skills/skill-audit/scripts/audit.py            # -> ~/.cache/skill-audit/<today>/
python3 skills/skill-audit/scripts/audit.py --out DIR  # somewhere else
```

Stdlib Python 3 only, read-only against `~/.claude`, `~/.codex`, `~/.agents`. It takes
about a minute on a few thousand sessions. Each step can also run alone with the same
`--out`:

| Script | Reads | Writes |
|---|---|---|
| `usage.py` | `~/.claude/projects/**/*.jsonl`, `~/.codex/sessions/**/*.jsonl` | `skill_usage.csv`, `usage_meta.json` |
| `inventory.py` | the three skills dirs, codex `.system`, installed plugins, claude.ai-synced | `skills_inventory.csv` |
| `extract_messages.py` | both log sources | `msgs.jsonl`, `dedup.json` (**sensitive**, see §4) |
| `cluster_patterns.py` | `dedup.json` | `clusters.txt` |

The driver prints a one-screen summary: the log window, the top-used skills, installed
skills never used, duplicates, broken symlinks, stray files, total description cost, and
the top recurring request patterns.

## 2. Read the results

- **`skill_usage.csv`**: one row per skill name. `claude_model` counts Skill tool calls,
  `claude_slash` counts typed `/commands`, `codex_user_mention` counts `$skill` injections,
  and `codex_agent_read` counts SKILL.md reads. `codex_uses_in_exec_runs` is the share that
  came from headless runs. `codex_maintenance_touches` counts edits to the skill itself,
  which are not use. `first_used` / `last_used` bound the activity.
- **`skills_inventory.csv`**: one row per real copy on disk. `linked_into` shows which
  agents' skills dirs point at it. `source` is maestro, local and unversioned,
  third-party, plugin, synced, `BROKEN symlink`, or `stray file`. `desc_chars` is the
  always-loaded cost. `link_paths` lists every symlink.
- **`clusters.txt`**: keyword buckets over what the user typed, with counts, per-agent
  split, date range, top working dirs, and 25 sample messages each. The buckets overlap
  and over-match, so use the counts to rank and the samples to judge.
  A big bucket with no matching skill is a candidate for a new skill. A skill whose
  bucket is empty may be solving a problem the user doesn't have.
- **`usage_meta.json`**: log date ranges, file counts, subagent types, and the top slash
  commands, built-ins included.

## 3. Counting caveats. Say them with the numbers.

- **A Codex read is not a use.** Codex opens a SKILL.md to decide whether it applies, so
  reads overstate use. Only `codex_user_mention` is the user asking for the skill.
- **Headless `codex exec` inflates counts.** Scripted and delegated runs can load the
  same skill hundreds of times. Check `codex_uses_in_exec_runs` before calling anything
  "heavily used". A skill used almost only in exec runs is used by a pipeline, not a
  person.
- **Claude transcripts are pruned.** `~/.claude/projects` keeps only recent history (see
  `cl_range` in `usage_meta.json`). "Never used in Claude" means never used *in that
  window*. Codex history usually goes back further, so the two columns cover different
  periods.
- Resumed and forked sessions replay history. Tool calls are deduplicated by id, and
  messages by dir, day, and text. Skills the harness auto-loads without a tool call are
  invisible.
- A name match is not always the same skill. Plugin-namespaced calls (`plugin:skill`)
  are folded onto the bare name.

## 4. The message corpus is sensitive

`msgs.jsonl` and `dedup.json` are the user's raw messages and can contain pasted
secrets: keys, tokens, passwords, customer data. They stay in the out dir under
`~/.cache`. They never go into a repo, a commit, a gist, an artifact, or a chat reply
beyond short quoted samples. Once the review is done, delete them:

```
rm ~/.cache/skill-audit/<date>/msgs.jsonl ~/.cache/skill-audit/<date>/dedup.json
```

`clusters.txt` quotes samples too. Treat it the same way, and never publish it as-is.

## 5. Propose changes. Act only on a yes.

The audit ends with a proposal, not an action. Group it the way the user will decide:

- **Archive**: never used, or used only by a dead pipeline. Give the evidence (the
  window, the zero, the last date).
- **Merge**: two skills that answer the same bucket, or duplicate copies of one skill.
  Say which copy survives and why.
- **Fix**: broken symlinks, stray files, a copy outside version control that should
  live in maestro.
- **Trim**: descriptions long enough to cost real context for their usage.
- **New**: a recurring request with no skill. Name the bucket and quote two samples.

Then stop and wait. Nothing is archived, merged, or deleted until the user approves,
item by item or as an explicit batch. When they approve an archive:

- Move the skill, don't delete it: `~/skill-archive/<YYYY-MM-DD>/<skill>/`. Remove the
  now-dangling symlinks from every agent's skills dir.
- Write `~/skill-archive/<date>/MANIFEST` with one line per skill: its name, original
  real path, every symlink that pointed at it, and why it was archived.
- Write an executable `~/skill-archive/<date>/restore.sh` that moves each skill back and
  recreates its symlinks, so one command undoes the whole batch.
- Re-run `inventory.py` afterwards and confirm no broken symlinks are left.

## When another skill fits better

- Writing or restructuring one skill → `anthropic-skills:skill-creator`.
- Finding a new skill to install → `find-skills`.
- Summing up the session this audit ran in → `recap`.
