---
description: Parallel refactor across module boundaries — one teammate per module, each isolated in its own git worktree, migrating off a duplicated helper in parallel
---

Refactor targets: `billing`, `shipping`, `inventory` under `sample_app/` (or the modules named in `$ARGUMENTS`), each still defining a local `_format_currency` that should migrate to the shared `sample_app/common/currency.format_currency`.

Do the following:

1. For each target module, create an isolated git worktree on its own branch from the repo root: `git worktree add ../agent-teams-worktrees/<module> -b refactor/<module>`. Skip a module if its branch or worktree already exists and say so.
2. In a single message, launch one `module-refactor` agent per module in parallel. Give each one: the absolute path to its module inside its own worktree (`.../agent-teams-worktrees/<module>/examples/parallel-refactor/sample_app/<module>/service.py`), the shared import path (`sample_app.common.currency`), and the absolute path to that worktree's `check.py` (`.../agent-teams-worktrees/<module>/examples/parallel-refactor/check.py`, run from its directory).
3. Wait for all teammates to finish and commit on their own branches.
4. Show the diff from each worktree (`git -C ../agent-teams-worktrees/<module> diff refactor/<module>~1..refactor/<module>`) and confirm each touched only its own module before merging anything.
5. Back on the current branch, merge each `refactor/<module>` branch one at a time (they touch disjoint files, so this should be conflict-free), then remove each worktree with `git worktree remove`.
6. Run `check.py` once more on the merged result and report the outcome.
