# Architecture

## Architectural intent

The system should grow from a proven one-shot PoC into a workflow-driven onboarding platform without coupling device behavior to a particular switch vendor.

## Logical components

```text
+---------------- Test-station configuration ----------------+
| Switch connection | Port-to-workflow map | Runtime policy  |
+-----------------------------+-------------------------------+
                              |
                              v
+---------------------- Switch adapter -----------------------+
| Interface state | LLDP retrieval | Vendor-specific parsing |
+-----------------------------+-------------------------------+
                              |
                              v
+-------------------- Normalized discovery -------------------+
| Port | chassis ID | system name | description | management IP|
+-----------------------------+-------------------------------+
                              |
                              v
+--------------------- Workflow coordinator ------------------+
| Eligibility | de-bounce | one-shot guard | state | timeout |
+---------------+-------------------------------+-------------+
                |                               |
                v                               v
+--------- Device adapter --------+    +------ Reporting ------+
| reset | configure | status      |    | events | outcome      |
| SDP provisioning | health      |    | diagnostics | history |
+------------------+-------------+    +-----------------------+
                   |
                   v
+---------------------- Validation adapters ------------------+
| API health | ST 2110 reception | video output | duration    |
+-------------------------------------------------------------+
```

## Core data records

### Port configuration

Describes what a physical lane is intended to do. It should contain a normalized port identifier, workflow name, eligibility rules, polling policy, and non-secret references to required credentials.

### Discovery record

A vendor-neutral result produced by a switch adapter:

```yaml
switch_id: lab-switch-1
port: ethernet-1/25
link_state: up
chassis_id: "example-value"
system_name: "example-device"
system_description: "example-description"
management_addresses:
  - "192.0.2.25"
observed_at: "RFC3339 timestamp"
```

The address above is documentation-only. Do not treat it as a product default.

### Workflow run

Records run identity, lane, discovered device, selected workflow, state transitions, timestamps, action outcomes, validation outcomes, and final status.

## State model

A persistent watcher should use explicit states rather than a simple infinite loop:

```text
IDLE
  -> LINK_SEEN
  -> WAITING_FOR_LLDP
  -> DEVICE_DISCOVERED
  -> ELIGIBILITY_CHECK
  -> RUNNING
  -> WAITING_FOR_RECOVERY
  -> VALIDATING
  -> COMPLETE or FAILED
  -> WAITING_FOR_REMOVAL
  -> IDLE
```

This prevents repeated destructive actions while the same device remains connected. A device should not be eligible again until the configured re-arm condition is met.

## Adapter boundaries

### Switch adapter

Owns connection and parsing details for Onyx or future switch platforms. It must not call MN-IP APIs or decide which device action to run.

### Device adapter

Owns device-family API calls, response validation, and device readiness checks. It must not know how LLDP was obtained.

### Workflow coordinator

Owns ordering, retries, timeouts, safety rules, and transitions. It consumes normalized discovery and device capabilities.

### Validation adapters

Own external or device-level evidence used to decide whether a test passed. Media validation must be based on defined observations, not merely API request success.

## Deployment model

The same application image should remain usable in two locations:

- **Utility VM:** development, tests, diagnostics, and centralized operation
- **Onyx Docker:** compact switch-hosted operation where supported

Configuration and secrets should be supplied at runtime. The application must not assume that container stdout is automatically easy to retrieve on Onyx.

## Reliability principles

- Use prompt-aware SSH reads instead of fixed sleeps.
- Apply bounded retries and explicit timeouts.
- Validate and normalize LLDP data before use.
- Make destructive actions idempotent where possible and guarded where not.
- Preserve state and diagnostics needed to explain failures.
- Separate action success from end-to-end workflow success.
- Re-arm only after a well-defined removal or reset condition.
