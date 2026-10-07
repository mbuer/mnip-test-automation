# Port-Mapping Strategy

## Decision

Use static physical lanes to select workflows and dynamic LLDP data to identify the currently connected device.

```text
Physical port -> intended lane and allowed workflow
LLDP          -> current device identity and management addresses
Reachability  -> separate switch-side assessment and optional recovery
```

The current validated lane is:

```text
Ethernet 1/25 -> MN-IP factory-reset watcher
```

## Why this model works

A support engineer can reason about a labeled physical port more easily than an invisible dynamic rule. LLDP removes the need to know or maintain the device's current IP ahead of time. Separating reachability prevents the system from assuming that an advertised management address is usable.

## Proposed configuration

```yaml
lanes:
  factory-reset-1:
    switch: lab-switch-1
    port: ethernet-1/25
    vlan: 1
    workflow: mnip-factory-reset
    allowed_device_families:
      - mn-ip
    poll_interval_seconds: 10
    discovery_timeout_seconds: 60
    rearm_down_seconds: 60
    recovery:
      enabled: true
      assumed_prefix_length: 24
      adjacent_address_policy: plus-one-except-254
```

This documents current behavior but is not yet an implemented schema.

## Current trigger semantics

1. Poll physical link state.
2. If link is Up, request LLDP.
3. Retry when LLDP is not yet available.
4. Parse and validate the neighbor.
5. Process the lane only if it is not already marked processed.
6. Test reachability from the switch.
7. Establish temporary reachability when required.
8. Run the workflow once.
9. Keep the lane locked during and after reboot.
10. Re-arm only after 60 seconds of continuous link-down.

The 60-second timer is reset by any return to link Up. It was validated to prevent a reboot-related link transition from causing a repeated reset.

## Identity and replacement

Physical disconnect is currently the decisive replacement signal. Future versions should also compare chassis ID and other stable identity fields, but identity change must not silently bypass destructive-action guards.

## Address-recovery caveat

The adjacent-address algorithm is an intentionally small PoC mechanism, not a general subnet inference system. LLDP does not provide the prefix. Before scaling the lane model, add configurable policies, conflict checks, invalid-address rejection, and clear failure behavior.

## Normalization

Normalize vendor-specific syntax such as `Eth1/25`, `Ethernet 1/25`, and `ethernet-1/25` internally. Preserve the vendor form in raw diagnostics where useful.
