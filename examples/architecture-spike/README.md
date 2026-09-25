# Architecture spikes / bake-offs

A minimal, runnable example of the [agent teams](../../README.md) pattern:
instead of building one approach to a problem, seeing how it goes, and maybe
trying another, several competing approaches are prototyped **at the same
time**, each by its own isolated teammate, then benchmarked and compared
objectively before a human picks one to keep.

This is a third shape of team, distinct from the other two examples. Like
[`parallel-refactor`](../parallel-refactor/), teammates *write* code, so each
gets its own git worktree. Unlike `parallel-refactor`, the candidates are
never merged together — they're mutually exclusive answers to the same
question, so the orchestrator's job is to compare them and let a human
choose one, not to reconcile them into a single diff.

## Pieces

- `spec.md` — the interface contract every candidate must satisfy: a
  per-client `RateLimiter` with `allow(client_id, now) -> bool`, driven by a
  caller-supplied `now` instead of the wall clock (so comparisons are
  deterministic, not timing-dependent).
- `harness.py` — an objective comparison tool, not specific to any one
  candidate. Given one or more `label=path/to/limiter.py` arguments, it
  loads each, then runs the same three checks against every candidate:
  correctness invariants (burst-then-block, per-client isolation, eventual
  recovery), throughput (calls/sec), and a *worst-case burst ratio* — how
  many requests a candidate actually allows within any window-length span
  when hammered right at a window boundary. That last metric is what
  surfaces the real, well-known trade-off between these algorithms: a fixed
  window counter can let through up to 2x its stated limit right at the
  boundary, while a token bucket or sliding-window log stays bounded. Try it
  yourself against any three implementations you write:
  `python3 harness.py a=path/to/a.py b=path/to/b.py`.
- `.claude/agents/spike-builder.md` — a single subagent (`Read`, `Write`,
  `Bash`, `Grep`, `Glob`) that implements exactly one assigned algorithm
  against the shared spec, in isolation, and self-reports its own
  complexity and known weaknesses. The same definition is reused for every
  teammate; only the assigned algorithm differs per dispatch.
- `.claude/commands/team-spike.md` — the orchestrator. Creates one worktree
  + branch per candidate approach (`token-bucket`, `sliding-window-log`,
  `fixed-window-counter` by default), dispatches one `spike-builder`
  teammate per approach **in parallel**, runs `harness.py` once against all
  of them together, merges the objective results with each teammate's
  self-reported tradeoffs into one comparison, and asks — via
  `AskUserQuestion`, a real decision gate — which one to keep. The winner's
  code is committed onto a fresh integration branch; every worktree and
  every losing (and winning) spike branch is cleaned up either way.

## Running it

Inside Claude Code, from this directory:

```
/team-spike
```

Or name a different subset: `/team-spike token-bucket fixed-window-counter`.

Each teammate builds in `../agent-teams-worktrees/spike-<approach>` (a
sibling directory, created and removed by the command). You'll see the
harness's comparison table plus each teammate's own tradeoff notes, then be
asked which one to adopt. If you pick one, its implementation lands at
`spike/rate_limiter.py` on a new `team-spike/<timestamp>` branch; the branch
you ran the command from is left untouched either way.

## Why this doesn't merge candidates the way `parallel-refactor` does

`parallel-refactor`'s teammates each touch a disjoint module, so their
branches merge cleanly into one combined result — the whole point is that
all of them land. Here, all three candidates implement the *same* class at
the *same* path answering the *same* question; there is no meaningful merge
of "token bucket" and "fixed window counter," only a choice between them.
That's the defining shape of a bake-off: parallel of exploration,
mutually-exclusive of outcome.

## Adapting this to a real repo

1. Replace `spec.md` with your own interface contract — a new cache
   eviction policy, a retry strategy, a serialization format, whatever the
   spike is actually about. Keep it algorithm-agnostic: the contract should
   be satisfiable by genuinely different approaches, or there's nothing to
   bake off.
2. Replace `harness.py`'s checks with ones that matter for your contract:
   correctness invariants every valid implementation must satisfy, a
   performance benchmark, and — if your problem has one — an objective
   metric that reveals the real trade-off between approaches, the way the
   burst-ratio test does here. A bake-off without an objective comparison
   degrades into "which one do I like the look of," which doesn't need a
   team of teammates to answer.
3. Copy `.claude/agents/spike-builder.md` and update its task section to
   point at your new spec; keep the "don't look at other worktrees" and
   "don't commit" rules as-is.
4. Copy `.claude/commands/team-spike.md`, update the candidate list and
   descriptions in step 3, and keep the worktree isolation, the objective
   harness run, and the human approval gate before anything is committed —
   the same reasons `parallel-refactor`'s README gives for keeping those
   apply here too.
