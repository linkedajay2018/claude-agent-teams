---
description: Parallel codebase exploration — one read-only teammate per subsystem maps its purpose, entry points, and cross-subsystem dependencies concurrently; results are synthesized into one architecture document.
---

Exploration target: `$ARGUMENTS` (a directory containing multiple subsystems). If empty, use `sample_app`.

Do the following:

1. List the immediate subdirectories of the target that contain Python files
   (skip `__pycache__`, hidden directories, and anything with no source
   files) — these are the subsystems to map. Tell the user which ones you
   found before dispatching anything.
2. In a single message, launch one `subsystem-mapper` agent per subsystem in
   parallel via the Agent tool. Give each one: the repo root, the absolute
   path to its one assigned subsystem, and nothing about what the other
   subsystems contain — each teammate should discover cross-subsystem
   dependencies from the code, not from being told about them.
3. Wait for all teammates to finish. Do not pre-filter or summarize any
   individual report yourself before the synthesis step — collect them raw.
4. Synthesize the reports into a single mental model. Specifically:
   - Reconcile every subsystem's "external dependencies" list against every
     other subsystem's report so the edges agree (if worker's report says it
     depends on notifications, and notifications' own report separately
     describes itself, use both to describe that edge accurately).
   - Build a request/data flow narrative: trace an actual path through the
     system end to end (e.g. "an API call creates state in storage, queues
     a job, which the worker later picks up, updates storage, and triggers a
     downstream effect") grounded in the real functions each teammate found,
     not invented.
   - Carry forward every "notable coupling or surprise" any teammate flagged
     — these are exactly the things a synthesis across subsystems is for,
     since no single subsystem's teammate could see both sides of the
     coupling.
5. Write the synthesis to `<target>/ARCHITECTURE.md` with these sections:
   `## Overview` (2-3 sentences on what the system does), `## Subsystems` (a
   table: subsystem, purpose, key entry points), `## Data flow` (the traced
   narrative from step 4), and `## Cross-subsystem coupling` (the dependency
   edges and any flagged surprises, each attributed to which subsystem's
   report it came from).
6. Print the same synthesis in your response so the user sees it without
   opening the file, and name the file you wrote it to.
