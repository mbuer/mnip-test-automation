# MNIP Test Automation

Automated onboarding, provisioning, validation, and long-duration testing for Riedel MN-IP devices.

> **Project status:** A persistent factory-reset watcher was validated on October 6, 2026, using a Riedel MN-IP FusioN device and an NVIDIA/Mellanox SN2410 running Onyx. The watcher discovers a device through LLDP, establishes temporary Layer 3 reachability when necessary, performs the reset once, removes its temporary address, and remains active for the next device. Provisioning, media validation, reporting, and production hardening remain future work.

## Executive summary

MNIP Test Automation is a laboratory automation project for repeatable device onboarding and validation. It is intended to remove repetitive setup work, make destructive actions predictable, and preserve the observations needed to explain why a test passed or failed.

The first implementation focuses on a practical support problem: a device may arrive with an unknown management address that is not reachable from the test station. The automation uses a designated switchport as the workflow lane and LLDP as the source of current device identity and management addressing. If the advertised address is outside the switch VLAN's configured subnet, the watcher temporarily adds an adjacent address to the existing VLAN interface, performs the device operation, and cleans up afterward.

The validated switch-hosted workflow is now:

```text
Device connected to Ethernet 1/25
              |
              v
Watcher detects link state and waits for LLDP
              |
              v
LLDP supplies identity and management IPv4 address
              |
              v
Switch tests Layer 3 reachability
              |
              +---- reachable ----------------------+
              |                                     |
              +---- unreachable                     |
                         |                           |
                         v                           |
             Add temporary VLAN address             |
                         |                           |
                         +---------------------------+
                                      |
                                      v
                         Send MN-IP factory-reset request
                                      |
                                      v
                     Remove temporary VLAN address in cleanup
                                      |
                                      v
                Keep lane locked; re-arm after 60 seconds down
```

This is an important step beyond the original one-shot proof of concept. The service can remain running, process a newly attached device once, tolerate the device's reboot without immediately resetting it again, and re-arm after a deliberate or sustained disconnect.

## Why this project exists

A complete onboarding or validation cycle involves more than sending an API request. Engineers may need to:

- discover and identify a device whose current configuration is unknown;
- return it to a known state without first reconfiguring a laptop or management network;
- wait for reboot and application readiness;
- apply an approved baseline configuration;
- provision media receivers from controlled SDP definitions;
- validate ST 2110 reception and expected video output;
- monitor behavior over hours or days; and
- produce a result that another engineer can understand and reproduce.

The intended first complete workflow is:

```text
Connect device
  -> discover and identify
  -> establish temporary reachability if required
  -> reset to a known state
  -> wait for recovery
  -> configure
  -> provision four receiver SDP definitions
  -> validate ST 2110 reception and video output
  -> monitor for the requested duration
  -> create an operator summary and technical evidence
```

Factory reset is the first proven device action, not the final scope of the platform.

## Validated milestones

### October 4, 2026: one-shot feasibility

- Built a Python Docker image on the Linux Utility VM.
- Queried Onyx LLDP through a Paramiko interactive shell.
- Extracted the attached MN-IP device's management address.
- Sent the MN-IP factory-reset request and observed HTTP 200 with `system rebooting`.
- Exported the same image, loaded it into Onyx Docker, and ran it on the SN2410.

### October 6, 2026: arbitrary-address recovery and persistent watcher

- Confirmed LLDP still advertised a device at `10.10.10.10/24` while the switch VLAN used `192.168.39.10/24` and Layer 3 communication failed.
- Confirmed Onyx accepts multiple IPv4 addresses on the same VLAN interface.
- Temporarily adding `10.10.10.11/24` to VLAN 1 restored communication; removing it removed communication again.
- Automated the privilege sequence `enable` -> `configure terminal` -> `interface vlan 1` before adding or removing the temporary address.
- Confirmed that reachability checks must run from the switch and that the REST request must run from the switch-hosted container. A request from the Utility VM still follows the VM's routing path.
- Validated the complete Docker-hosted flow with an initially unreachable device.
- Converted the one-shot process into a persistent watcher with a 10-second polling policy.
- Added a 60-second continuous link-down requirement before re-arming, preventing a reboot-related link transition from causing a reset cycle.
- Repeated the test with a different private subnet, `172.20.50.100/24`, using `172.20.50.101/24` temporarily.
- Confirmed cleanup after success and confirmed the watcher remained running without resetting the recovered device again.

Example addresses above are lab observations, not product defaults.

## Technology overview

- **Python** implements switch interaction, parsing, workflow control, and MN-IP REST actions.
- **Docker** provides a portable runtime built on the Utility VM and executed on Onyx.
- **Paramiko** drives the Onyx CLI through `invoke_shell()`.
- **LLDP** supplies current neighbor identity and management addressing independently of IP reachability.
- **Onyx VLAN interfaces** provide temporary Layer 3 adjacency for otherwise unreachable devices.
- **Requests** performs the MN-IP REST call from the switch-hosted container.
- **YAML** currently supplies environment-specific proof-of-concept configuration.

## Current capability

The current prototype can:

- remain active as a background watcher;
- poll Ethernet 1/25 approximately every 10 seconds;
- distinguish physical link state from LLDP readiness;
- discover an MN-IP device's management IPv4 address through LLDP;
- test reachability from the switch;
- derive a temporary adjacent address under the current `/24` recovery policy;
- add and remove an additional IPv4 address on VLAN 1;
- issue the factory-reset request from the Onyx-hosted container;
- mark the connected device as processed;
- ignore short link drops during device reboot; and
- re-arm only after the port remains down continuously for 60 seconds.

## Important limitations

This remains a validated prototype rather than a production service:

- The active code now uses a conventional package layout under `src/mnip_test_automation/`.
- The watcher uses fixed sleeps and opens multiple SSH sessions instead of maintaining a prompt-aware session.
- LLDP parsing is regex-based and assumes one useful IPv4 row.
- Recovery currently assumes `/24` and derives an adjacent address. The device's actual prefix length is not learned from LLDP.
- The derived address is not yet checked for conflicts before assignment.
- Only one switch, VLAN, lane, and tested MN-IP device family are covered.
- Recovery after process or switch restart is not persisted.
- Container-output retrieval on Onyx is still limited; unbuffered output helps but is not a complete logging solution.
- Host-key verification, credential injection, error classification, and configuration safety require hardening.
- Post-reset device readiness, provisioning, media validation, reporting, and automated tests are not implemented.

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
├── src/mnip_test_automation/  # Active application package
├── docker/                   # Container build definition
├── config/                   # Example config; local config is ignored
├── tests/                    # Automated tests to be added
└── requirements.txt
```

The next structural improvement should migrate active code into a conventional `src/` layout while retaining the original PoC as a documented milestone. Releases should use Git tags rather than additional version-number directories.

## Documentation map

- [Executive summary](docs/00-executive-summary.md): concise project value, status, and next decisions
- [Vision and scope](docs/01-vision-and-scope.md): target workflow and boundaries
- [Architecture](docs/02-architecture.md): components, states, recovery boundaries, and reliability rules
- [Onyx integration](docs/03-onyx-integration.md): SSH modes, CLI privilege flow, LLDP, Docker, and VLAN findings
- [MN-IP API notes](docs/04-mn-ip-api.md): validated reset action and safety requirements
- [Test-station design](docs/05-test-station-design.md): physical lane and validation concept
- [Port-mapping strategy](docs/06-port-mapping-strategy.md): lane semantics, dynamic discovery, and re-arm policy
- [Roadmap](docs/07-roadmap.md): completed and upcoming phases
- [Development guide](docs/08-development-guide.md): engineering, testing, secrets, and repository hygiene
- [Deployment guide](docs/09-deployment.md): build, export, Onyx load/start/remove, and artifact cleanup
- [Proof-of-concept results](docs/10-poc-results.md): dated validation record for both milestones
- [Agent context](AGENT.md): precise durable instructions for future AI agents and collaborators

## Near-term direction

The next milestone is not another device action. It is hardening the watcher that now works:

1. Replace fixed sleeps with prompt-aware Onyx command execution.
2. Normalize interface and LLDP data into typed records.
3. Validate candidate temporary addresses and detect conflicts.
4. Persist enough lane state to recover safely after restart.
5. Add structured events and an operator-visible result channel.
6. Add automated tests for parsing, recovery-address selection, cleanup, and state transitions.
7. Add post-reset rediscovery and readiness checks.

Only after that foundation is dependable should the project proceed to baseline configuration, four-receiver SDP provisioning, ST 2110 validation, and long-duration reporting.

## Security

Never commit switch or device passwords, API tokens, private keys, local `.env` files, generated Docker archives, or logs containing sensitive environment details. `AutoAddPolicy` and locally stored credentials were expedient PoC choices and must not be treated as production defaults.
