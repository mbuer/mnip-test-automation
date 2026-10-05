# MNIP Test Automation

Automated onboarding, provisioning, validation, and long-duration testing for Riedel MN-IP devices.

> **Project status:** Phase 1 proof of concept validated on October 4, 2026. The current implementation discovers an MN-IP device through LLDP and triggers a factory reset through the device REST API. Provisioning, media validation, and reporting are planned.

## Executive summary

MNIP Test Automation is a laboratory automation project for repeatable device onboarding and validation. It is intended to reduce the manual work required to return devices to a known state, apply test configurations, validate operation, and preserve useful results over tests that may run for hours or days.

The first supported environment combines a Riedel MN-IP device with an NVIDIA/Mellanox SN2410 running Onyx. A Python application packaged as a Docker image uses a statically assigned switchport and dynamically reads LLDP information from the switch. The advertised management address is then used to call the device REST API.

The initial proof of concept demonstrated the complete path:

```text
Device connected to Ethernet 1/25
              |
              v
Onyx LLDP query through interactive SSH
              |
              v
MN-IP management address extracted
              |
              v
Factory-reset request sent through REST API
              |
              v
Device accepts request and reboots
```

The same Docker image executed successfully on both the Utility VM and the SN2410. This validates the central deployment idea: development and testing can take place on a conventional Linux VM, while the resulting image can also run directly on the switch.

## Why this project exists

A complete onboarding or test cycle involves more than a reset. Engineers may need to discover a device, identify its type and software, return it to a known state, load configuration, provision media receivers, verify operational health, observe the result, and retain evidence of the test.

The project aims to turn those manual steps into explicit, reusable workflows. The intended end state for the first MN-IP workflow is:

```text
Connect device
  -> discover and identify
  -> factory reset
  -> wait for recovery
  -> configure
  -> load SDP receiver definitions
  -> receive ST 2110 sender flows on four FusioN receivers
  -> confirm expected video output
  -> continue monitoring for hours or days
  -> create an operator-readable result and technical log
```

## What was validated in Phase 1

- A Python Docker image can be built and tested on a Linux Utility VM.
- The image can be exported with `docker save`, transferred to Onyx, loaded, and started on an SN2410.
- The same image runs on both platforms without application-code changes.
- Onyx can be accessed with Paramiko through an interactive CLI channel.
- `show lldp interfaces ethernet 1/25 remote` returns the attached device's system details and management IPv4 address.
- The Python application can extract that address from the LLDP output.
- The MN-IP REST API accepted a factory-reset request and returned HTTP 200 with `system rebooting`.
- The container exited with status 0 on the switch after performing the workflow.

These findings prove technical feasibility. They do not yet constitute a production-ready onboarding service.

## Technology overview

- **Python** implements discovery and device actions.
- **Docker** provides a portable runtime for the Utility VM and Onyx switch.
- **Paramiko** establishes the interactive SSH session required by the Onyx CLI-only account.
- **LLDP** supplies device identity metadata and the current management address.
- **Static port mapping** assigns a role or workflow to a physical test-station port.
- **REST API calls** perform device-specific actions such as factory reset.
- **YAML configuration** currently supplies environment-specific settings in the proof of concept.

## Architecture at a glance

The long-term design separates switch integration from device logic and workflow orchestration:

```text
Port state / polling
        |
        v
Switch adapter -> Discovery record -> Device adapter
        |                              |
        v                              v
  Onyx today                    MN-IP today
  other vendors later           other devices later
        \______________________________/
                       |
                       v
             Workflow state machine
                       |
                       v
       Validation, logs, and test report
```

The current proof of concept is deliberately smaller than this target architecture. See [Architecture](docs/02-architecture.md) for the boundary between validated behavior and planned design.

## Current scope and limitations

### Implemented

- One configured Onyx switch
- One statically selected onboarding port, Ethernet 1/25
- Dynamic LLDP management-address extraction
- MN-IP factory reset through REST
- CLI/container output
- Execution on Linux Docker and Onyx Docker

### Not yet implemented

- Continuous port-state monitoring and re-arming after device removal
- Duplicate-action protection beyond one-shot container exit
- Device recovery checks after reset
- Configuration and SDP provisioning
- ST 2110 media validation
- Video-output confirmation
- Structured logs, reports, inventory, or historical records
- Credential injection suitable for production
- Automated tests and support for additional switch or device families

## Repository layout

```text
.
├── README.md
├── AGENT.md
├── docs/
│   ├── 00-executive-summary.md
│   ├── 01-vision-and-scope.md
│   ├── 02-architecture.md
│   ├── 03-onyx-integration.md
│   ├── 04-mn-ip-api.md
│   ├── 05-test-station-design.md
│   ├── 06-port-mapping-strategy.md
│   ├── 07-roadmap.md
│   ├── 08-development-guide.md
│   ├── 09-deployment.md
│   └── 10-poc-results.md
└── v0.1/                  # Existing proof-of-concept implementation
```

The `v0.1` directory preserves the first working proof of concept. Future development should migrate stable application code into an ordinary source layout and use Git tags for releases.

## Documentation

Start with the documents that match the reader's role:

- [Executive summary](docs/00-executive-summary.md) for managers, stakeholders, and support leads
- [Vision and scope](docs/01-vision-and-scope.md) for project boundaries and intended outcomes
- [Architecture](docs/02-architecture.md) for system responsibilities and extension points
- [Onyx integration](docs/03-onyx-integration.md) for LLDP, SSH, and Docker findings
- [MN-IP API notes](docs/04-mn-ip-api.md) for validated device actions and safety guidance
- [Test-station design](docs/05-test-station-design.md) for the physical and operational concept
- [Port-mapping strategy](docs/06-port-mapping-strategy.md) for static lanes with dynamic discovery
- [Roadmap](docs/07-roadmap.md) for implementation phases
- [Development guide](docs/08-development-guide.md) for repository and engineering practices
- [Deployment guide](docs/09-deployment.md) for VM and Onyx workflows
- [Proof-of-concept results](docs/10-poc-results.md) for the October 4, 2026 validation record
- [Agent context](AGENT.md) for future AI agents and collaborators

## Security

Do not commit passwords, tokens, private keys, production addresses, or configuration containing credentials. The first proof of concept used local configuration for speed; that is not the intended long-term secret-management model.

Use ignored local files or runtime environment variables for development. A later phase should define a formal secret-injection mechanism and least-privilege accounts for switch and device access.

## Near-term direction

The next engineering milestone is a continuously running watcher for a statically assigned port. The watcher should detect the transition from no usable neighbor to a discovered device, execute a workflow once, wait for removal, and then re-arm safely.

After reliable triggering and recovery checks, the project can progress to configuration, four-receiver SDP provisioning, ST 2110 validation, longer-duration monitoring, and reporting.
