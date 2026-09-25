---
description: Cross-service coordinated change — one contract-owner teammate finalizes a shared event schema change first, then one teammate per microservice updates its producer/consumer code to match, each isolated in a worktree branched from the finalized contract. A combined contract test and one human approval gate run before anything is committed.
---

Change: `$ARGUMENTS` (default: add a required `tracking_number: str` field to
the `OrderShipped` event, as schema version 2). Services involved:
`shipping_service` (producer), `billing_service` and `notifications_service`
(consumers), coordinated through `contract/events.py` and verified by
`contract_test.py`.

Do the following:

1. Note the branch you're currently on (`base_branch=$(git branch --show-current)`) — never commit or push directly to it.

2. **Phase 1 — contract negotiation (sequential, not parallel).** Everything
   in phase 2 depends on this finishing first; do not skip ahead.
   a. Create one worktree for the contract change: `git worktree add ../agent-teams-worktrees/contract -b contract/schema-update`.
   b. Launch a single `contract-owner` agent in that worktree, given the change description, the path to `contract/events.py`, and the path to `contract_test.py`. Wait for it to finish before touching anything else.
   c. Commit its change on the `contract/schema-update` branch with a concise message.
   d. Tell the user the finalized field name(s), type(s), and sample value(s) from its report before moving on — the point where coordination becomes visible, not just implicit.

3. **Phase 2 — per-service updates (parallel, now that the contract is fixed).**
   a. For each service (`shipping_service`, `billing_service`, `notifications_service`), create an isolated worktree **branched from `contract/schema-update`**, not from `base_branch`, so each starts already containing the finalized contract: `git worktree add ../agent-teams-worktrees/<service> -b service/<service> contract/schema-update`.
   b. In a single message, launch one `service-updater` agent per service in parallel via the Agent tool. Give each: its own service directory path inside its worktree, whether it's the producer or a consumer, and the exact field name(s)/type(s)/sample value(s) from step 2d's report — copy them verbatim into every prompt; a mismatch here is exactly the bug this pattern exists to prevent.
   c. Wait for all three to finish. Nothing is committed in these worktrees yet.

4. Commit each service worktree's change onto its own `service/<name>` branch with a concise message.

5. Create a temporary integration branch off `base_branch` (e.g. `_team-contract-change-preview`) and merge `contract/schema-update` plus all three `service/*` branches into it — they touch disjoint files sharing one ancestor, so this should be conflict-free. Run `contract_test.py` from that merged worktree and capture its full output.

6. Show the user the combined diff (`git diff base_branch..._team-contract-change-preview`) together with the contract test result, and confirm each per-service change touched only its own service directory.

7. Ask the user, via the AskUserQuestion tool (not just a text question), whether to keep this change or discard it. If the contract test failed in step 5, say so plainly before asking — don't let the user approve a broken merge without knowing.

8. If kept:
   a. Rename the temporary integration branch to `team-contract-change/<UTC timestamp, e.g. 20260925-094500>` and push it to `origin`.
   b. Check out `base_branch` again so the working tree is left exactly where the user started.
   c. Remove all four worktrees (`contract`, `shipping_service`, `billing_service`, `notifications_service`) with `git worktree remove`, and delete `contract/schema-update` and every `service/<name>` branch — their commits now live on the integration branch.
   d. Report the new branch name and mention `gh pr create` as the natural next step.

9. If discarded: remove all four worktrees with `git worktree remove --force` (drops all uncommitted edits), and delete the temporary integration branch, `contract/schema-update`, and every `service/<name>` branch. Confirm nothing was committed or pushed and that `base_branch` is untouched.
