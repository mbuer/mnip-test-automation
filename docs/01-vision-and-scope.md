# Vision and Scope

## Vision

Provide a repeatable onboarding and test platform that can process supported devices with minimal operator intervention and produce results that support engineers can understand and trust.

The first complete target experience is:

```text
An operator connects a FusioN gateway to a designated lane.
The system discovers and identifies the device.
The system returns the device to a known state.
The system waits for recovery and applies configuration.
The system provisions four receiver SDP definitions from ST 2110 senders.
The system validates stream reception and expected video output.
The system monitors the setup for the requested duration.
The system creates a clear result and technical log.
```

## Phase 1 scope

- Riedel MN-IP device automation
- NVIDIA/Mellanox SN2410 with Onyx
- Static port-to-workflow mapping
- Dynamic LLDP metadata and management-address discovery
- Docker deployment on Linux and Onyx
- CLI/container operation

## Future scope

- Additional onboarding workflows
- Configuration and firmware operations
- ST 2110 sender and receiver validation
- Overnight and multi-day tests
- Structured logs, reports, and history
- Additional Riedel device families
- Additional switch platforms, potentially including Netgear and Luminex

## Explicit non-goals for the current phase

- General-purpose network-management platform
- Full inventory system
- Web UI
- Multi-vendor abstraction before real adapters are required
- Production credential-management system
- Automatic media-quality analysis without defined test instruments and acceptance criteria

## Success criteria

Phase 1 feasibility was achieved when the same container image successfully discovered an attached device through Onyx LLDP and initiated the MN-IP factory reset from both the Utility VM and the SN2410.

The next milestone succeeds when a persistent service safely detects a newly attached eligible device, runs exactly one reset workflow, verifies recovery, waits for removal, and re-arms without manual container recreation.
