# Contributing

New examples are welcome. Each one should demonstrate a distinct agent-teams
use case (see the list in the root [README](README.md)) and be self-contained
and runnable with no setup beyond Python's standard library and Claude Code
itself.

## Adding an example

Create `examples/<kebab-case-use-case-name>/` containing:

- Sample code that gives the reviewer/reader something concrete to look at —
  small and dependency-free, in whatever language fits the scenario.
- `.claude/agents/*.md` — the custom subagent(s) for this pattern. Scope
  `tools:` to the minimum the agent needs (read-only tools for a reviewer,
  for example), and write a `description:` specific enough that the agent
  doesn't fire outside this example.
- `.claude/commands/*.md` — the slash command that orchestrates the team:
  gather shared context once, dispatch subagents in parallel, merge results.
- `README.md` — what it demonstrates, the pieces involved, how to run it
  (with a copy-pasteable command), and how to adapt it to a real repo.

Then add a one-line entry for it under `## Examples` in the root README.

## Before opening a PR

- CI compile-checks every `.py` file under `examples/` and validates that
  every `.claude/agents/*.md` and `.claude/commands/*.md` file has YAML
  frontmatter with at least a `description:` field — make sure both pass
  locally first.
- Keep the example focused on one pattern. If you're demonstrating two
  things, that's probably two examples.
