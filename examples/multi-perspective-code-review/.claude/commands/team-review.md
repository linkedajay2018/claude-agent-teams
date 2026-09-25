---
description: Multi-perspective code review — dispatches security, performance, and correctness subagents in parallel and merges their findings
---

Review target: `$ARGUMENTS` (a git diff range, e.g. `HEAD~1..HEAD` or `main..HEAD`). If empty, use `HEAD~1..HEAD`.

Do the following:

1. Run `git diff <target>` yourself once to confirm the target resolves to a non-empty diff. If it's empty, tell the user and stop.
2. In a single message, launch three agents in parallel via the Agent tool, one per subagent_type: `security-reviewer`, `performance-reviewer`, `correctness-reviewer`. Give each the same target and tell it to review that diff strictly through its own lens.
3. Wait for all three to return. Do not summarize or pre-filter their findings yourself — pass each one's raw findings through.
4. Merge the three result sets into one list, dedupe anything that's genuinely the same underlying issue flagged by more than one reviewer, and report the combined list via the ReportFindings tool, most-severe first across all three categories (not grouped by reviewer).
