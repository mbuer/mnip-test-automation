# Vision and Scope

## Vision

Provide a repeatable onboarding and test platform that can process supported devices with minimal operator intervention and produce results that support engineers can understand and trust.

The desired operator experience is physical and simple:

```text
Connect a supported device to a clearly labeled lane.
The system recognizes the lane and discovers the device.
If the current management network is unknown, the system establishes controlled temporary reachability.
The system returns the device to a known state.
The system waits for recovery and applies the approved configuration.
The system provisions four receiver SDP definitions from known ST 2110 senders.
The system validates reception and expected video output.
The system monitors for the requested duration.
The system creates a clear result and technical log.
```

## Validated current scope

- Riedel MN-IP FusioN device
- NVIDIA/Mellanox SN2410 with Onyx
- Ethernet 1/25 as a statically assigned onboarding lane
- Link-state and LLDP polling
- Dynamic management-address discovery
- Switch-side reachability testing
- Temporary additional VLAN addressing under a controlled `/24` prototype policy
- MN-IP factory reset from an Onyx-hosted Docker container
- Persistent watcher with duplicate-action protection
- 60-second continuous link-down re-arm policy
- Docker build on Linux and execution on Onyx

## Future scope

- Post-reset rediscovery and readiness verification
- Baseline configuration and firmware-aware workflows
- Four-receiver SDP provisioning
- ST 2110 sender/receiver validation
- Video-output confidence checks
- Overnight and multi-day tests
- Structured logs, results, and history
- Multiple lanes and controlled concurrency
- Additional Riedel device families
- Additional switch platforms where real use cases justify adapters

## Explicit non-goals for the current phase

- General-purpose network management
- Automatic allocation in arbitrary customer address plans
- Production secret management before the runtime architecture is stable
- Web UI before CLI workflows and result semantics are dependable
- Vendor abstraction without a second real implementation
- Media-quality acceptance criteria without agreed instruments and observations

## Success criteria

The initial feasibility milestone required LLDP discovery and factory reset from the same Docker image on Linux and Onyx.

The persistent-watcher milestone required the service to:

- detect a connected device;
- tolerate delayed LLDP availability;
- establish temporary reachability when required;
- reset the device once;
- remove temporary configuration;
- remain running;
- avoid a reset cycle during reboot; and
- re-arm after sustained physical removal.

That milestone was validated on October 6, 2026.

The next milestone succeeds when the current behavior is refactored into tested components with prompt-aware Onyx interaction, conflict-safe temporary addressing, durable events, and post-reset readiness verification.
