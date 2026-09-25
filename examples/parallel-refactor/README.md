# Parallel refactors across module boundaries

A minimal, runnable example of the [agent teams](../../README.md) pattern:
split a refactor that spans several independent modules across one teammate
per module, each isolated in its own git worktree so they can't step on
each other's edits. Teammates only edit — nothing is committed until you
review the combined diff and approve it. On approval, the result lands on a
fresh branch created for that run; the branch you started from is never
committed or pushed to directly.

A different shape of team than
[`multi-perspective-code-review`](../multi-perspective-code-review/): that
example is **role-parallel** — three differently-specialized subagents look
at the *same* code. This one is **data-parallel** — one subagent
definition, dispatched three times with a different module assigned each
time.

## Pieces

- `sample_app/` — three independent service modules (`billing`, `shipping`,
  `inventory`), each still defining its own local `_format_currency(cents)`
  helper, duplicating the shared implementation that already exists at
  `sample_app/common/currency.py`. The refactor: migrate each module to
  import the shared function and delete its local copy.
- `check.py` — asserts each module's public function still returns the
  right value. Run it before and after the refactor to prove it's
  behavior-preserving, not a behavior change.
- `.claude/agents/module-refactor.md` — a single subagent definition
  (`Read`, `Edit`, `Bash`, `Grep`, `Glob`) that performs the migration for
  exactly one module, wherever it's told to look, and stops without
  committing. Reused for every teammate; only the assigned module path
  differs per dispatch.
- `.claude/commands/team-refactor.md` — the orchestrator. Creates one git
  worktree + branch per module, dispatches a `module-refactor` teammate
  into each **in parallel** (single message, three `Agent` calls), then
  shows you the combined diff and each teammate's check result and asks —
  via `AskUserQuestion`, a real approval gate, not just asking in text —
  whether to commit or discard. On approval, it commits each branch, merges
  them onto a brand new `team-refactor/<timestamp>` branch (never onto the
  branch you ran the command from), verifies the merged result still passes
  `check.py`, and pushes that new branch. A decline discards every
  worktree's edits — nothing is committed, merged, or pushed, and no new
  branch is created.

## Running it

Inside Claude Code, from this directory:

```
/team-refactor
```

Or name specific modules: `/team-refactor billing shipping`.

Each teammate works in `../agent-teams-worktrees/<module>` (a sibling
directory to this repo, created and removed by the command) so three agents
can edit the repo at once without racing each other on the same working
tree. You'll see each module's diff and be asked to approve before anything
is committed. If you approve, the merged refactor is pushed on its own
`team-refactor/<timestamp>` branch — the branch you ran the command from
(likely `main`) is left exactly as it was, so `sample_app/` stays in its
"before" state for the next run.

## Why worktrees here and not just parallel `Edit` calls in one working tree

Read-only reviewers (like the code-review example) can safely share one
working tree — they never write. The moment teammates *write* code in
parallel, they need either non-overlapping files in a shared tree, or their
own tree entirely. Worktrees give every teammate a real, independent
filesystem view on its own branch, so a mid-refactor `git status` or
partial edit in one module can never be seen by another module's teammate —
then ordinary `git merge` reconciles them, same as merging any other set of
branches.

## Adapting this to a real repo

1. Copy `.claude/agents/module-refactor.md` and rewrite its task section
   for your actual migration (e.g. an old logging call, a deprecated
   client, a renamed field) instead of `_format_currency`.
2. Copy `.claude/commands/team-refactor.md` and point step 1's module list
   at your repo's real module/service directories.
3. Keep a check step (tests, a smoke script, a type check) that each
   teammate must pass before reporting back — it's what makes "did the
   refactor actually preserve behavior" verifiable per module instead of
   only at the end.
4. Keep the approval gate. Teammates writing code unattended across
   several modules is exactly the case where a human should see the diff
   before anything lands — don't let the orchestrator skip straight to
   commit+push.
5. Keep the fresh-branch rule. Never let the orchestrator commit or push
   directly to the branch it was run from (often your default branch) —
   always land the result on a new branch and let a PR (or a second
   explicit approval) gate merging it further.
