# Roadmap

## Phase 1: Technical feasibility

**Status: validated on October 4, 2026**

- Build a Python Docker image on the Utility VM
- Query Onyx LLDP on Ethernet 1/25
- Extract the MN-IP management address
- Trigger factory reset through REST
- Execute the same image on the SN2410

## Phase 2: Reliable trigger service

- Persistent container/service
- Prompt-aware Onyx integration
- Link and LLDP polling
- Normalized discovery record
- De-bounce and duplicate-action protection
- Waiting-for-removal and re-arm behavior
- Post-reset reachability and readiness checks
- Actionable CLI logs
- Unit tests for parsing and state transitions

## Phase 3: Configuration and provisioning

- Product and firmware identification
- Baseline configuration deployment
- Managed configuration templates
- Four-receiver SDP provisioning
- Clear rollback and failure handling

## Phase 4: Validation

- ST 2110 receiver-state checks
- Known-flow validation
- Video-output confirmation method
- Defined acceptance criteria
- Repeatable pass/fail result

## Phase 5: Long-duration operation and reporting

- Overnight and multi-day test plans
- Structured event logs
- Result persistence
- Operator summaries
- Detailed diagnostics
- Test-run history

## Phase 6: Expansion

- Additional Riedel device adapters
- Additional workflows
- Netgear and Luminex switch adapters where justified
- Multiple lanes and concurrent runs
- Optional service API or UI after CLI workflows are stable

## Roadmap rule

Do not add generalized abstractions solely because a future vendor might need them. Add extension points when a second real implementation makes the common interface clear.
