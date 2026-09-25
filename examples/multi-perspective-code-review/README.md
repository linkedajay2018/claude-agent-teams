# Multi-perspective code review

A minimal, runnable example of the [agent teams](../../README.md) pattern:
instead of one agent switching between security/performance/correctness
lenses on a diff, three specialized subagents review the same change in
parallel and their findings merge into one report.

## Pieces

- `sample_app/api.py` — a tiny in-memory order service. Commit 1 (`fd58704`)
  is a clean baseline. Commit 2 (`e2fb40a`) is the "PR" under review — it
  seeds three independent bugs, one per lens:
  - **Security**: `authenticate` runs `eval(token)` on caller input.
  - **Performance**: `deduplicate_orders` does an O(n²) linear scan (`if o
    not in seen`, a list) instead of an O(1) set lookup.
  - **Correctness**: `apply_discount(order, code, history=[])` uses a
    mutable default argument, so `history` leaks state across calls.
- `.claude/agents/security-reviewer.md`, `performance-reviewer.md`,
  `correctness-reviewer.md` — custom subagents, each restricted to
  read-only tools (`Read`, `Grep`, `Glob`, `Bash`) and scoped by its
  `description` and system prompt to only its one lens.
- `.claude/commands/team-review.md` — the orchestrator. Computes the diff
  once, dispatches all three reviewers **in parallel** (single message,
  three `Agent` calls), then merges and ranks their findings via the
  `ReportFindings` tool.

## Running it

Inside Claude Code, from this directory, against either of the two seeded
examples in this repo:

```
/team-review fd58704..e2fb40a
```

That range is the first seeded PR: `fd58704` is the clean baseline,
`e2fb40a` adds the three bugs described above.

```
/team-review main..demo/refund-feature
```

That range is [PR #1](https://github.com/linkedajay2018/claude-agent-teams/pull/1),
an actual open GitHub PR — `refund_order()` has an inverted auth check
(`if not authenticate(token) or is_priority:`) that lets an invalid token
bypass authentication entirely. The merged findings from running this
command are posted as a comment on that PR.

Run `/team-review` with no argument to review `HEAD~1..HEAD` instead —
useful once you're using this pattern on your own commits, but note that
range won't point at either seeded example once this repo has more history
on top of it. Or pass any other range: `/team-review main..my-branch`.

## Adapting this to a real repo

1. Copy `.claude/agents/*.md` into your repo (or your `~/.claude/agents/`
   for a global copy).
2. Adjust each agent's `tools:` and `description:` frontmatter to fit your
   repo's conventions — add more lenses (e.g. `test-coverage-reviewer`,
   `api-compat-reviewer`) the same way.
3. Copy `.claude/commands/team-review.md` and point it at your PR/branch
   naming convention.
4. For a heavier-weight version of this same idea already built into
   Claude Code, see `/code-review ultra`, which runs a multi-agent review
   in the cloud.
