# Cross-service coordinated changes

A minimal, runnable example of the [agent teams](../../README.md) pattern: a
change spanning several independent microservices through a shared contract,
where per-service work genuinely can't start until the contract itself is
settled — dispatched in two phases instead of one.

Every other example in this repo dispatches its whole team in a single
parallel step. This one can't: a service consuming an event has nothing
correct to build until it knows the exact field name and type the event will
carry, and that's a decision only one teammate makes. So this example runs
**sequential, then parallel**: one `contract-owner` teammate finalizes the
shared schema alone first; only once that's done are three `service-updater`
teammates — one per microservice — dispatched together against the now-fixed
contract.

## Pieces

- `contract/events.py` — the single source of truth for the `OrderShipped`
  event: a schema version number, a `REQUIRED_FIELDS` mapping per version,
  and `validate_event()`. Every producer and consumer imports from here;
  nothing hardcodes field names on its own.
- `shipping_service/producer.py` — builds and validates the event (the
  producer).
- `billing_service/consumer.py`, `notifications_service/consumer.py` — two
  independent consumers of the same event, each reacting differently.
- `contract_test.py` — the objective proof that everyone actually agrees: it
  builds one event via the producer, feeds it to both consumers, and asserts
  every required field is both present *and* actually used in each
  consumer's output — not just accepted without crashing. Run it before and
  after a change to prove the system is really in sync, not just claimed to
  be.
- `.claude/agents/contract-owner.md` — a single subagent that finalizes a
  contract change: bumps the schema version, adds the new field(s), and
  updates the contract test's sample call. Runs alone, first; its report is
  the "message" relayed into every other teammate's prompt afterward.
- `.claude/agents/service-updater.md` — a single subagent definition, reused
  once per microservice, that updates exactly one service's producer or
  consumer code to match the field name/type it's given. It never sees the
  contract-owner's actual diff — only the finalized values reported forward
  to it.
- `.claude/commands/team-contract-change.md` — the orchestrator. Runs the
  contract-owner step to completion first, commits it to its own branch,
  then branches all three service worktrees **from that branch** (not from
  `base_branch`) so every service starts from the finalized contract, and
  dispatches all three `service-updater` teammates **in parallel**. Merges
  everything into one preview, runs `contract_test.py` against the merged
  result, and gates on human approval before anything lands.

## Running it

Inside Claude Code, from this directory:

```
/team-contract-change
```

Or describe a different change: `/team-contract-change add an optional
carrier: str field, schema version 2`.

You'll see the finalized contract (field name, type, sample value) reported
before any service work starts — the coordination step made visible. Then
all three services update in parallel, and you'll see the combined diff plus
the contract test's pass/fail output before being asked whether to keep the
change. If kept, it lands on a new `team-contract-change/<timestamp>`
branch; the branch you ran the command from is left untouched either way.

## Why this needs two phases instead of one

In every other example here, every teammate can start immediately because
none needs a decision only another teammate can make. Here, a consumer
teammate literally cannot write correct code without knowing the producer's
exact field name — guessing risks a typo that breaks the contract in a way
no single service's tests would catch (each service's own code looks fine
in isolation; only `contract_test.py`, which exercises all of them together,
would catch the mismatch). Making the contract-owner step run to completion,
and explicitly relaying its report into every other prompt, is what keeps
the phase-2 fan-out actually safe to parallelize.

## Adapting this to a real repo

1. Replace `contract/events.py` with your real shared contract — an OpenAPI
   schema, a protobuf/Avro definition, a JSON schema file, whatever your
   services actually share. The pattern only needs a single file every
   service depends on and a version marker inside it.
2. Replace `contract_test.py` with your real contract test (a Pact contract
   test, a schema-registry compatibility check, or an integration test like
   this one) — keep it generic across schema versions the way this one
   loops over `REQUIRED_FIELDS[CURRENT_SCHEMA_VERSION]`, so a new field
   doesn't require editing the test's assertions, only its sample call.
3. Copy `.claude/agents/contract-owner.md` and `.claude/agents/service-updater.md`,
   and point them at your real contract file and service directories.
4. Copy `.claude/commands/team-contract-change.md` and update the service
   list in phase 2. Keep the sequencing — contract first, alone; services
   after, in parallel, branched from the contract's own branch — since
   that's what makes the parallel fan-out safe here at all.
5. Keep the single, late approval gate covering the *merged* result. Gating
   after phase 1 alone would approve a contract decision before anyone can
   see whether it actually works end to end; only after every service has
   caught up and the contract test has run against all of them together
   does that become clear.
