# Parallel codebase exploration

A minimal, runnable example of the [agent teams](../../README.md) pattern:
instead of one agent reading a whole unfamiliar codebase subsystem by
subsystem in series, one read-only teammate per subsystem maps its own
corner concurrently, and their reports synthesize into a single architecture
document — including cross-subsystem couplings no single teammate could see
on its own.

Like [`multi-perspective-code-review`](../multi-perspective-code-review/),
teammates are read-only and share one working tree (no worktrees needed —
nothing is written until the synthesis step). Like
[`parallel-refactor`](../parallel-refactor/), it's **data-parallel**: one
subagent definition, dispatched once per subsystem, with only the assigned
directory differing per teammate.

## Pieces

- `sample_app/` — a tiny order-processing system split into five
  subsystems: `api` (HTTP-facing handlers), `queue` (an in-memory job
  queue), `worker` (background job processing), `storage` (persistence),
  and `notifications`. The subsystems aren't independent: `api` enqueues
  jobs that `worker` later drains, and `notifications` reaches directly
  into `storage` to look up a customer's email rather than being handed it
  by `worker` — a real coupling that only becomes visible once every
  subsystem's report is compared side by side.
- `demo.py` — runs one order through the full pipeline (`api` → `queue` →
  `worker` → `storage`/`notifications`) so the traced data flow in the
  synthesized document can be checked against actual behavior.
- `.claude/agents/subsystem-mapper.md` — a single read-only subagent
  (`Read`, `Grep`, `Glob`, `Bash`) that maps exactly one subsystem: its
  purpose, key files, public entry points, and — most importantly — every
  place it imports or calls into code outside itself. Reused for every
  teammate; only the assigned subsystem path differs.
- `.claude/commands/team-explore.md` — the orchestrator. Discovers the
  subsystems under the target directory, dispatches one `subsystem-mapper`
  teammate per subsystem **in parallel** (single message, one `Agent` call
  per subsystem), then reconciles their cross-subsystem dependency lists
  against each other, traces an end-to-end data flow, and writes the
  result to `ARCHITECTURE.md`.

## Running it

Inside Claude Code, from this directory:

```
/team-explore
```

Or point it at any other directory with multiple subsystems:
`/team-explore path/to/some/repo/src`.

You'll see which subsystems were found, then (once every teammate reports
back) a synthesized architecture document — an overview, a subsystem table,
a traced data flow, and a cross-subsystem coupling section — printed in the
response and written to `ARCHITECTURE.md`. Run `python3 demo.py` yourself
to confirm the traced data flow matches what the code actually does.

## Why this needs a synthesis step, not just five reports side by side

Each `subsystem-mapper` teammate can only see its own subsystem's imports —
it knows `notifications` reaches into `storage`, but not whether `worker`
also expected to be the one supplying that data. The coupling is only
visible by comparing multiple teammates' reports against each other, which
is exactly what step 4 of `team-explore.md` does: it's the one part of this
pattern that can't be parallelized, because it needs every other step's
output at once.

## Adapting this to a real repo

1. Copy `.claude/agents/subsystem-mapper.md` as-is — it doesn't reference
   anything specific to `sample_app`, only "the subsystem you're given."
2. Copy `.claude/commands/team-explore.md` and point step 1's directory
   listing at wherever your repo's subsystems actually live (`src/`,
   `services/`, `packages/`, etc.) — some repos need a smarter definition
   of "subsystem" than "immediate subdirectory," e.g. one per package in a
   monorepo's `packages/*` or one per service in `services/*/`.
3. For a very large repo, consider having each teammate write its raw
   report to a scratch file instead of returning it inline, so the
   orchestrator's context in step 3 only holds five file paths instead of
   five full reports — read them back in step 4 when synthesizing.
4. This pattern composes with `parallel-refactor`: run this first to find
   your bearings in an unfamiliar repo, then use what it surfaces (e.g. a
   duplicated helper visible across several subsystems' reports) as the
   target for a follow-up parallel refactor.
