---
description: Architecture spike / bake-off — prototypes several competing approaches to the same problem in parallel, each isolated in its own git worktree, benchmarks and compares them objectively, then lets a human pick a winner before anything is committed.
---

Spike target: the rate-limiter interface defined in `spec.md`. Candidate
approaches (or the ones named in `$ARGUMENTS`, space-separated):

- `token-bucket` — tokens refill continuously, proportional to elapsed time,
  capped at max_requests; each allowed request consumes one token.
- `sliding-window-log` — a per-client log of request timestamps; on each
  call, purge entries older than window_seconds, then allow only if what's
  left is under the limit.
- `fixed-window-counter` — time is divided into fixed-size window_seconds
  blocks; a per-(client, block) counter resets whenever the block changes.

Do the following:

1. Note the branch you're currently on (`base_branch=$(git branch --show-current)`) — this run must never commit or push directly to it.
2. For each candidate approach, create an isolated git worktree on its own branch from the repo root: `git worktree add ../agent-teams-worktrees/spike-<approach> -b spike/<approach>`. Skip one if its branch or worktree already exists and say so.
3. In a single message, launch one `spike-builder` agent per approach in parallel. Give each: the absolute path to `spec.md` inside its own worktree, the algorithm name and one-line description assigned to it (from the list above), and the absolute path to write its implementation inside its own worktree (`.../agent-teams-worktrees/spike-<approach>/examples/architecture-spike/spike/<approach>/limiter.py`). Make clear each must not commit and must not inspect any other teammate's worktree.
4. Wait for all teammates to finish. Nothing is committed yet — do not run `git commit` anywhere in this step.
5. Run `harness.py` yourself, once, from this directory, pointing it at every candidate's file across worktrees in one invocation, e.g.:
   `python3 harness.py token-bucket=../agent-teams-worktrees/spike-token-bucket/examples/architecture-spike/spike/token-bucket/limiter.py sliding-window-log=... fixed-window-counter=...`
   This prints one table: correctness pass/fail, throughput (calls/sec), and worst-case allowed burst at a window boundary, for every candidate side by side.
6. Combine the harness's objective results with each teammate's self-reported tradeoffs (time/memory complexity, known edge cases) into one readable comparison — lead with the objective table, then each candidate's own notes underneath.
7. Ask the user, using the AskUserQuestion tool (not just a text question), which candidate to adopt, or none.
8. If a candidate is chosen:
   a. Create a fresh integration branch off `base_branch`, named `team-spike/<UTC timestamp, e.g. 20260925-094500>` — never reuse `base_branch` itself.
   b. Copy the winning worktree's `limiter.py` onto that branch at `spike/rate_limiter.py` — a single canonical, algorithm-neutral path, since it's now *the* implementation rather than one candidate among several.
   c. Commit it there with a message naming which approach won and citing the comparison result that decided it.
   d. Push the new branch to `origin`, then check out `base_branch` again so the working tree is left exactly where the user started.
   e. Remove every worktree with `git worktree remove` and delete every `spike/<approach>` branch, including the winner's (its code now lives on the integration branch instead).
   f. Report the new branch name and mention `gh pr create` as the natural next step.
9. If none is chosen: remove every worktree with `git worktree remove --force` (drops all uncommitted candidate code) and delete every `spike/<approach>` branch. No integration branch is ever created. Confirm nothing was committed or pushed, and that `base_branch` is untouched.
