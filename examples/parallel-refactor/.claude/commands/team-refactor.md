---
description: Parallel refactor across module boundaries — one teammate per module, each isolated in its own git worktree, migrating off a duplicated helper in parallel. Shows the combined diff and waits for human approval before anything is committed; the result always lands on a fresh branch, never directly on the branch you ran this from.
---

Refactor targets: `billing`, `shipping`, `inventory` under `sample_app/` (or the modules named in `$ARGUMENTS`), each still defining a local `_format_currency` that should migrate to the shared `sample_app/common/currency.format_currency`.

Do the following:

1. Note the branch you're currently on (`base_branch=$(git branch --show-current)`) — this run must never commit or push directly to it.
2. For each target module, create an isolated git worktree on its own branch from the repo root: `git worktree add ../agent-teams-worktrees/<module> -b refactor/<module>`. Skip a module if its branch or worktree already exists and say so.
3. In a single message, launch one `module-refactor` agent per module in parallel. Give each one: the absolute path to its module inside its own worktree (`.../agent-teams-worktrees/<module>/examples/parallel-refactor/sample_app/<module>/service.py`), the shared import path (`sample_app.common.currency`), and the absolute path to that worktree's `check.py` (`.../agent-teams-worktrees/<module>/examples/parallel-refactor/check.py`, run from its directory). Make clear in the prompt that they must not commit.
4. Wait for all teammates to finish. Nothing is committed yet — do not run `git commit` anywhere in this step.
5. Show the user each worktree's diff (`git -C ../agent-teams-worktrees/<module> diff`) and each teammate's check result, combined into one readable summary, and confirm each touched only its own module.
6. Ask the user, using the AskUserQuestion tool (not just a text question), whether to commit this refactor onto a new branch or discard it.
7. If approved:
   a. In each worktree, commit the change on its branch with a concise message.
   b. Create a fresh integration branch off `base_branch`, named `team-refactor/<UTC timestamp, e.g. 20260925-094500>` — never reuse `base_branch` itself as the merge target.
   c. On that new branch, merge each `refactor/<module>` branch one at a time (they touch disjoint files, so this should be conflict-free).
   d. Run `check.py` on the merged result. If it fails, stop and report — do not push a broken merge.
   e. Push the new branch to `origin`, then check out `base_branch` again so the working tree is left exactly where the user started.
   f. Remove each worktree with `git worktree remove` and delete the now-merged `refactor/<module>` branches (the integration branch stays — it's the result).
   g. Report the new branch name, its pushed URL, and mention `gh pr create` as the natural next step if they want it reviewed as a PR.
8. If discarded: remove each worktree with `git worktree remove --force` (this drops the uncommitted edits) and delete the `refactor/<module>` branches. No integration branch is ever created in this path. Confirm nothing was committed or pushed, and that `base_branch` is untouched.
