# Roadmap

## Phase 1: Technical feasibility

**Status: validated October 4, 2026**

- Build the Python Docker image on the Utility VM
- Query Onyx LLDP on Ethernet 1/25
- Extract the MN-IP management address
- Trigger factory reset through REST
- Execute the same image on the SN2410

## Phase 2A: Reachability recovery

**Status: validated October 6, 2026**

- Prove LLDP discovery without Layer 3 reachability
- Add a secondary address to the existing Onyx VLAN interface
- Restore reachability to an arbitrarily addressed device
- Execute REST from the switch-hosted container
- Remove temporary configuration after the action
- Repeat with a second private subnet

## Phase 2B: Persistent trigger watcher

**Status: prototype validated October 6, 2026**

- Persistent running container
- 10-second link/LLDP polling policy
- Delayed LLDP handling after link-up
- One-shot processed guard
- 60-second continuous link-down re-arm policy
- Reboot-cycle protection
- Cleanup through `try/finally`
- Unbuffered Python output

## Phase 2C: Production hardening

**Status: next milestone**

- Prompt-aware Onyx session handling
- Explicit state machine and event model
- Typed LLDP and port records
- Configurable lane, VLAN, timing, and recovery policy
- Temporary-address conflict detection
- Verified cleanup and escalation
- Durable state for safe restart
- Structured logs and operator-visible results
- Host-key and secret-management hardening
- Unit and integration tests
- Post-reset rediscovery and readiness

## Phase 3: Configuration and provisioning

- Product and firmware identification
- Approved baseline configuration
- Managed templates and change evidence
- Four-receiver SDP provisioning
- Rollback and partial-failure behavior

## Phase 4: Validation

- ST 2110 receiver-state checks
- Known-flow validation
- Video-output confirmation
- Defined acceptance criteria
- Repeatable pass/fail result

## Phase 5: Long-duration operation and reporting

- Overnight and multi-day plans
- Structured event storage
- Operator summaries and technical diagnostics
- Test-run history and comparison

## Phase 6: Expansion

- Additional Riedel device adapters
- Additional workflows and lanes
- Netgear and Luminex adapters where justified
- Controlled concurrency
- Optional API or UI after the CLI and result model are stable

## Roadmap rule

Do not skip Phase 2C because the prototype works. A destructive automation service must make retries, cleanup, state, secrets, and observability more dependable than the manual process it replaces.
