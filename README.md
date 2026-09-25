# claude-agent-teams

Working examples of the "agent teams" pattern in [Claude Code](https://claude.com/claude-code):
splitting a task across multiple specialized subagents — each with its own scoped
tools, prompt, and role — instead of one agent handling everything serially.

Each example under [`examples/`](examples/) is self-contained: its own sample
code, its own `.claude/agents/*.md` subagent definitions, its own orchestrating
slash command, and its own README with instructions to run it as-is.

## Examples

- [`multi-perspective-code-review/`](examples/multi-perspective-code-review/) —
  three subagents (security, performance, correctness) review the same diff in
  parallel; their findings are merged into one ranked report.
- [`parallel-refactor/`](examples/parallel-refactor/) — one teammate per
  module, each isolated in its own git worktree, migrating off a duplicated
  helper in parallel; branches are verified and merged back at the end.
- [`parallel-codebase-exploration/`](examples/parallel-codebase-exploration/) —
  one read-only teammate per subsystem maps its own corner of an unfamiliar
  repo concurrently; their reports are synthesized into one architecture
  document, including couplings no single teammate could see alone.
- [`architecture-spike/`](examples/architecture-spike/) — several competing
  approaches to the same problem, each prototyped in parallel in its own
  worktree, benchmarked objectively, and compared before a human picks a
  winner to commit.
- [`cross-service-change/`](examples/cross-service-change/) — one teammate
  finalizes a shared event contract first, then one teammate per
  microservice updates its producer/consumer code to match in parallel,
  gated on a combined contract test before anything is committed.

More examples land here over time. Other use cases this pattern fits well:

- **Incident response triage** — one agent tails logs, another correlates
  deploys, another drafts the postmortem timeline, concurrently.
- **Background long-running work** — delegate a slow task (dependency upgrade,
  doc sprint) to a background teammate while you keep working in the foreground.

## How the pattern works in Claude Code

- **`.claude/agents/*.md`** — custom subagent definitions. Frontmatter
  (`name`, `description`, `tools`, `model`) scopes what the subagent can touch
  and when it should trigger; the body is its system prompt.
- **`.claude/commands/*.md`** — slash commands that orchestrate: compute shared
  context once, dispatch multiple subagents in parallel (a single message with
  multiple `Agent` tool calls), then merge their results.
- New `.claude/agents/*.md` files are picked up at session start, not
  hot-reloaded — start a fresh Claude Code session in a repo after adding or
  editing agent definitions there.

## License

[MIT](LICENSE)
