# Writing the eval harness

The loop can only be as good as the evals. A loop with a weak eval doesn't fail loudly. It "succeeds" at the wrong thing. Spend real effort here.

## Contents
1. Output contract
2. Metric mode patterns
3. Feature mode patterns
4. Subjective criteria (LLM judge)
5. Noise and min_delta
6. Holdout set
7. Anti-gaming checklist

## 1. Output contract

`.goal/evals/run` is any executable (shebang script). `goalctl` runs it from the project root. Its **last JSON line on stdout** must be:

```json
{"score": 0.83, "passed": false, "checks": {"login_redirects": true, "csv_export_has_headers": false}}
```

- `score` (required, number): what the loop climbs. A missing or non-numeric score counts as a failed iteration and is reverted.
- `passed` (optional, bool): `true` means the goal is met. Use it when "done" is more than a threshold on `score`.
- `checks` (optional, name → bool): per-criterion results. `goalctl` refuses to keep an iteration that turns a previously passing check into a failing one, even when the total score goes up. That rule is what stops "fix 3 things, quietly break 1" in feature mode.

Write anything else (build output, timings, artifacts) to stderr or into `.goal/runs/`, never into `.goal/evals/`. The evals directory is hashed, so changing anything in it breaks the freeze.

## 2. Metric mode patterns

Measure the real thing at the boundary the user cares about, not an internal proxy.

```bash
#!/usr/bin/env bash
# .goal/evals/run: p95 latency of /search over the fixture queries, median of 5 trials
set -euo pipefail
npm run build >&2
python3 .goal/evals/bench.py --queries .goal/evals/queries.txt --trials 5   # prints {"score": <p95_ms>, ...}
```

- Always include a **correctness gate**: if the output is wrong, emit a terrible score (or `"score": null`). Otherwise the fastest "improvement" is returning garbage.
- Run the project's existing test suite inside the harness when it's fast enough, and fail the iteration if it fails. That makes "don't break existing behavior" mechanical instead of aspirational.
- Fix seeds, pin inputs, warm caches consistently.

## 3. Feature mode patterns

Turn each done criterion from GOAL.md into a named check. `score` = fraction passing, `passed` = all pass.

```python
#!/usr/bin/env python3
# .goal/evals/run
import json, subprocess
def ok(cmd): return subprocess.run(cmd, shell=True, capture_output=True).returncode == 0
checks = {
    "unit_tests_pass":        ok("npm test --silent"),
    "export_endpoint_200":    ok("bash .goal/evals/e2e_export.sh"),
    "csv_has_header_row":     ok("python3 .goal/evals/check_csv.py"),
    "settings_page_renders":  ok("npx playwright test .goal/evals/settings.spec.ts"),
}
print(json.dumps({"score": sum(checks.values()) / len(checks), "passed": all(checks.values()), "checks": checks}))
```

- Prefer end-to-end checks (hit the endpoint, drive the UI, run the CLI) over unit tests the agent will also be writing. Agent-written unit tests tend to test what was built, not what was asked for.
- Keep checks independent so partial progress shows up in the score.
- For a big feature, 5–20 checks is a good range. Fewer makes the gradient too coarse; more is usually padding.

## 4. Subjective criteria (LLM judge)

For things like "the error messages are helpful" or "the docs explain setup clearly", use a judge with a fixed rubric, run in a fresh context so it doesn't share the builder's biases:

```bash
claude -p "You are grading against this rubric: $(cat .goal/evals/rubric.md)
Artifact:
$(cat docs/setup.md)
Reply with only JSON: {\"pass\": true|false, \"reason\": \"...\"}" --output-format text
```

- Make rubric items binary and concrete ("mentions the required env vars by name"), not vibes ("is clear").
- Judges are noisy. Run them 3 times and take the majority, and keep judged checks a minority of the total.

## 5. Noise and min_delta

Before freezing a metric eval, run it 3–5 times on the unchanged code (`goalctl run`) and look at the spread. Set `--min-delta` comfortably above that noise (about 2× the spread is a good default). If you skip this, the loop "improves" by chance and keeps random changes.

## 6. Holdout set

Self-written evals get overfit, even without bad intent: the agent sees every failure and patches exactly that case. A holdout catches it.

- Spawn a subagent with only GOAL.md as context and have it write `.goal/evals/holdout/run` (same contract, different cases from the same distribution: other queries, other inputs, other user flows).
- Don't read the holdout files yourself. Not reading them is what makes them a holdout.
- Run `goalctl run --holdout` at the end (and optionally every ~10 iterations). If the holdout is far below the main score, say so plainly in the wrap-up; that gap is the most important thing for the user to know.

## 7. Anti-gaming checklist

Before asking the user to approve the evals, check each item:
- Could a trivial implementation (hardcoding, special-casing fixture inputs, returning cached answers) pass? Add a check that defeats it.
- Does a correctness gate guard every performance metric?
- Does the harness run the existing tests, so deleting or skipping a test can't raise the score? If the agent could edit the project's test files to pass, add a check that the existing test count didn't drop.
- Is the harness deterministic enough (noise measured, min_delta set)?
- Does every done criterion in GOAL.md map to at least one check?
