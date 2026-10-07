# Architecture

## Architectural intent

The system should grow from a validated switch-hosted watcher into a workflow-driven onboarding platform without coupling device behavior to one switch vendor or confusing discovery with reachability.

The decisive finding from the second validation milestone is:

> LLDP discovery can succeed while Layer 3 communication fails.

Discovery, reachability assessment, temporary reachability recovery, and device operations are therefore separate architectural responsibilities.

## Logical components

```text
+------------------- Test-station configuration -------------------+
| switch | lane | VLAN | workflow | poll/re-arm policy | secret refs |
+-------------------------------+----------------------------------+
                                |
                                v
+------------------------ Switch adapter ---------------------------+
| prompt-aware CLI | link state | LLDP | VLAN address add/remove     |
+-------------------------------+----------------------------------+
                                |
                +---------------+----------------+
                |                                |
                v                                v
+---------------------------+       +------------------------------+
| Normalized discovery      |       | Reachability service         |
| identity and addresses    |       | probe, derive, validate,     |
| observed on a lane        |       | apply temporary adjacency    |
+-------------+-------------+       +---------------+--------------+
              |                                     |
              +------------------+------------------+
                                 |
                                 v
+------------------------ Workflow coordinator --------------------+
| eligibility | one-shot guard | states | retries | cleanup | re-arm |
+----------------------+-----------------------------+--------------+
                       |                             |
                       v                             v
+-----------------------------+       +-----------------------------+
| Device adapter              |       | Reporting                   |
| reset | readiness | config  |       | events | outcome | evidence |
| SDP provisioning | health   |       | diagnostics | history       |
+---------------+-------------+       +-----------------------------+
                |
                v
+----------------------- Validation adapters ----------------------+
| API health | ST 2110 reception | video output | duration policy   |
+------------------------------------------------------------------+
```

## Validated prototype flow

```text
WAITING_FOR_LINK
  -> WAITING_FOR_LLDP
  -> DISCOVERED
  -> CHECKING_REACHABILITY
  -> RECOVERING_REACHABILITY (when required)
  -> RESETTING
  -> CLEANUP
  -> PROCESSED
  -> WAITING_FOR_60_SECONDS_DOWN
  -> WAITING_FOR_LINK
```

The prototype currently implements this with a small number of variables and a polling loop. The target implementation should use explicit state types and event records.

## Core records

### Lane configuration

A lane should define physical and policy intent, not a device's current IP address.

```yaml
lane_id: factory-reset-1
switch: lab-switch-1
port: ethernet-1/25
vlan: 1
workflow: mnip-factory-reset
poll_interval_seconds: 10
rearm_down_seconds: 60
recovery:
  enabled: true
  assumed_prefix_length: 24
credential_refs:
  switch: local-secret-reference
```

This is a proposed schema, not yet implemented.

### Discovery record

```yaml
switch_id: lab-switch-1
port: ethernet-1/25
link_state: up
chassis_id: example-value
system_name: example-device
system_description: example-description
management_addresses:
  - 192.0.2.25
observed_at: RFC3339-timestamp
```

The address is documentation-only.

### Reachability lease

Temporary switch configuration should be represented as a lease so ownership and cleanup are explicit:

```yaml
lane_id: factory-reset-1
vlan: 1
device_address: 172.20.50.100
temporary_address: 172.20.50.101
prefix_length: 24
created_at: RFC3339-timestamp
cleanup_required: true
```

Never add a temporary address without recording enough information to remove and verify it.

### Workflow run

A run should record lane, discovery identity, states, temporary configuration, device actions, cleanup result, timestamps, and final outcome.

## Reachability recovery boundary

The current adjacent-address method is useful but constrained:

- LLDP supplies an address, not its subnet mask.
- The prototype assumes `/24`.
- `+1` is used except for `.254`, where `-1` is used.
- No conflict detection is implemented.
- A mismatched prefix may still permit one local TCP transaction, but that must not be presented as generally safe networking.

The future reachability component must:

1. validate the discovered IPv4 address;
2. apply an explicit configured prefix policy;
3. generate candidate addresses without selecting network/broadcast/invalid values;
4. check for apparent conflicts before use;
5. add the address only on the configured VLAN;
6. verify the switch can reach the device;
7. return a lease to the workflow; and
8. remove and verify the address in `finally` cleanup.

## Re-arm semantics

Link loss during reset is not proof of device removal. The validated prototype requires 60 seconds of continuous link-down before clearing the processed guard. A link-up event resets the down timer.

This policy is intentionally conservative. It trades faster reuse for protection against repeated destructive actions during reboot.

Future policy may combine:

- sustained physical link-down;
- LLDP neighbor absence;
- chassis identity change;
- operator acknowledgement; and
- persisted lane state.

## Execution-location rule

The actor performing the network operation must have the intended route:

- Onyx CLI performs switch-side reachability checks and VLAN configuration.
- The Onyx-hosted container performs REST communication to a temporarily adjacent device.
- The Utility VM is suitable for development and normal routed cases, but temporary switch addressing does not automatically extend that path to the VM.

## Failure and cleanup model

Temporary network configuration is a transaction:

```text
prepare -> apply -> verify -> use -> remove -> verify removal
```

Device-action failure must still trigger cleanup. Cleanup failure must override an otherwise successful result or produce a high-severity partial failure requiring operator intervention.

## Reliability principles

- Read until recognized prompts instead of sleeping blindly.
- Recognize CLI privilege levels and errors.
- Use bounded retries and explicit timeouts.
- Normalize and validate discovery before acting.
- Persist state before destructive actions when restart recovery is added.
- Separate request acceptance from device recovery and workflow success.
- Preserve raw command output when it helps explain parsing or configuration failures.
- Keep a lane locked until the configured re-arm condition is satisfied.
