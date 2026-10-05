# Port-Mapping Strategy

## Decision

Use static physical port assignments to select a workflow and dynamic LLDP data to identify the connected device.

```text
Physical port -> intended lane/workflow
LLDP          -> current device metadata and management address
```

For the Phase 1 proof of concept:

```text
Ethernet 1/25 -> factory-reset lane
```

The lab address observed during testing is not a permanent property of the lane and must not be hard-coded as the device identity.

## Why combine both methods

Static port mapping is easy for support engineers to understand and aligns automation with the physical test station. LLDP avoids maintaining a manual IP assignment for each device and provides useful identity metadata.

## Recommended configuration model

```yaml
lanes:
  factory-reset-1:
    switch: lab-switch-1
    port: ethernet-1/25
    workflow: mnip-factory-reset
    allowed_device_families:
      - mn-ip
    poll_interval_seconds: 5
    discovery_timeout_seconds: 60
    rearm_condition: neighbor-removed
```

This is a proposed model, not an implemented schema.

## Trigger semantics

A link becoming active is not sufficient proof that LLDP data is ready. The service should:

1. Detect link or poll LLDP.
2. Wait for a complete eligible discovery record.
3. De-bounce repeated observations.
4. Run the configured workflow once.
5. Keep the lane locked for the current device.
6. Re-arm after neighbor removal or another explicitly configured condition.

## Normalization

Vendor-specific port syntax such as `Eth1/25` and `Ethernet1/25` should normalize to one internal identifier. Display the original vendor form in diagnostics where useful.
