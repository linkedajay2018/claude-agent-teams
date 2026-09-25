# Architecture spikes / bake-offs

A minimal, runnable example of the [agent teams](../../README.md) pattern:
instead of building one approach, seeing how it goes, and maybe trying
another, several competing approaches are prototyped **at the same time**,
each by its own isolated teammate, then benchmarked and compared objectively
before a human picks one to keep.

A third team shape, distinct from the other examples. Like
[`parallel-refactor`](../parallel-refactor/), teammates *write* code, so each
gets its own git worktree. Unlike `parallel-refactor`, candidates are never
merged — they're mutually exclusive answers to the same question, so the
orchestrator's job is to compare them and let a human choose, not to
reconcile them into one diff.

## Pieces

- `spec.md` — the interface contract every candidate must satisfy: a
  per-client `RateLimiter` with `allow(client_id, now) -> bool`, driven by a
  caller-supplied `now` instead of the wall clock (so comparisons are
  deterministic, not timing-dependent).
- `harness.py` — an objective, candidate-agnostic comparison tool. Given one
  or more `label=path/to/limiter.py` args, it loads each and runs three
  checks: correctness invariants (burst-then-block, per-client isolation,
  eventual recovery), throughput (calls/sec), and *worst-case burst ratio* —
  how many requests a candidate allows within any window-length span when
  hammered right at a window boundary. That last metric surfaces the classic
  trade-off: a fixed window counter can let through up to 2x its stated limit
  at the boundary, while a token bucket or sliding-window log stays bounded.
  Try it: `python3 harness.py a=path/to/a.py b=path/to/b.py`.
- `.claude/agents/spike-builder.md` — a single subagent (`Read`, `Write`,
  `Bash`, `Grep`, `Glob`) that implements one assigned algorithm against the
  shared spec, in isolation, and self-reports its own complexity and known
  weaknesses. Reused for every teammate; only the assigned algorithm differs
  per dispatch.
- `.claude/commands/team-spike.md` — the orchestrator. Creates one worktree +
  branch per candidate (`token-bucket`, `sliding-window-log`,
  `fixed-window-counter` by default), dispatches one `spike-builder` teammate
  per approach **in parallel**, runs `harness.py` once against all of them,
  merges the objective results with each teammate's self-reported tradeoffs,
  and asks — via `AskUserQuestion`, a real decision gate — which to keep. The
  winner's code is committed to a fresh integration branch; every worktree
  and spike branch (winner included) is cleaned up either way.

## Running it

Inside Claude Code, from this directory:

```
/team-spike
```

Or name a subset: `/team-spike token-bucket fixed-window-counter`.

Each teammate builds in `../agent-teams-worktrees/spike-<approach>` (a
sibling directory, created and removed by the command). You'll see the
harness's comparison table plus each teammate's tradeoff notes, then be asked
which to adopt. If you pick one, its implementation lands at
`spike/rate_limiter.py` on a new `team-spike/<timestamp>` branch; the branch
you ran the command from is left untouched either way.

## Why this doesn't merge candidates the way `parallel-refactor` does

`parallel-refactor`'s teammates each touch a disjoint module, so their
branches merge cleanly into one combined result — the whole point is that all
of them land. Here, all three candidates implement the *same* class at the
*same* path answering the *same* question; there's no meaningful merge of
"token bucket" and "fixed window counter," only a choice between them. That's
the defining shape of a bake-off: parallel exploration, mutually-exclusive
outcome.

## Adapting this to a real repo

1. Replace `spec.md` with your own interface contract — a cache eviction
   policy, a retry strategy, a serialization format, whatever the spike is
   actually about. Keep it algorithm-agnostic: the contract should be
   satisfiable by genuinely different approaches, or there's nothing to bake
   off.
2. Replace `harness.py`'s checks with ones that matter for your contract:
   correctness invariants every valid implementation must satisfy, a
   performance benchmark, and — if your problem has one — an objective metric
   that reveals the real trade-off between approaches, the way the
   burst-ratio test does here. Without an objective comparison, a bake-off
   degrades into "which one do I like the look of."
3. Copy `.claude/agents/spike-builder.md` and update its task section to
   point at your new spec; keep the "don't look at other worktrees" and
   "don't commit" rules as-is.
4. Copy `.claude/commands/team-spike.md`, update the candidate list and
   descriptions in step 3, and keep the worktree isolation, the objective
   harness run, and the human approval gate before anything is committed —
   the same reasons `parallel-refactor`'s README gives apply here too.
