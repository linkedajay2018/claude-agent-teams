---
description: Parallel refactor across module boundaries — one teammate per module, each isolated in its own git worktree, migrating off a duplicated helper in parallel. Shows the combined diff and waits for human approval before anything is committed or pushed.
---

Refactor targets: `billing`, `shipping`, `inventory` under `sample_app/` (or the modules named in `$ARGUMENTS`), each still defining a local `_format_currency` that should migrate to the shared `sample_app/common/currency.format_currency`.

Do the following:

1. For each target module, create an isolated git worktree on its own branch from the repo root: `git worktree add ../agent-teams-worktrees/<module> -b refactor/<module>`. Skip a module if its branch or worktree already exists and say so.
2. In a single message, launch one `module-refactor` agent per module in parallel. Give each one: the absolute path to its module inside its own worktree (`.../agent-teams-worktrees/<module>/examples/parallel-refactor/sample_app/<module>/service.py`), the shared import path (`sample_app.common.currency`), and the absolute path to that worktree's `check.py` (`.../agent-teams-worktrees/<module>/examples/parallel-refactor/check.py`, run from its directory). Make clear in the prompt that they must not commit.
3. Wait for all teammates to finish. Nothing is committed yet — do not run `git commit` anywhere in this step.
4. Show the user each worktree's diff (`git -C ../agent-teams-worktrees/<module> diff`) and each teammate's check result, combined into one readable summary, and confirm each touched only its own module.
5. Ask the user, using the AskUserQuestion tool (not just a text question), whether to commit and push this refactor or discard it.
6. If approved:
   a. In each worktree, commit the change on its branch with a concise message.
   b. Back on the current branch, merge each `refactor/<module>` branch one at a time (they touch disjoint files, so this should be conflict-free).
   c. Push the current branch to `origin`.
   d. Remove each worktree with `git worktree remove` and delete the now-merged `refactor/<module>` branches.
   e. Run `check.py` once more on the merged result and report the outcome.
7. If discarded: remove each worktree with `git worktree remove --force` (this drops the uncommitted edits) and delete the `refactor/<module>` branches. Confirm nothing was committed or pushed.
