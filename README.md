# MN-IP Test Automation

Production-oriented factory-reset automation for Riedel MN-IP devices in a controlled lab or test-station environment.

> **Current status:** `v1.0-rc1` is implemented, unit-tested, and ready for lab validation. The release candidate adds a third independent lane for a 10G FusioN device. Existing FusioN 25G and MuoN A10 workflows are validated. Final v1.0 release requires validation of all three lanes on the target switch.

## Why this project exists

Returned, repurposed, or lab devices may arrive with unknown management addresses. Manual recovery requires repeated discovery, temporary network configuration, destructive reset commands, and cleanup. MN-IP Test Automation turns those steps into a repeatable switch-hosted workflow.

The service runs in Docker on NVIDIA Onyx, discovers devices through LLDP, establishes temporary Layer 3 reachability when required, sends the exact narrow reset request, removes temporary addressing, and waits for physical removal before re-arming a lane.

## v1.0 lane model

The interactive helper asks for the actual switchports. The following values are examples only:

```text
FusioN 25G lane: example port 1/1
FusioN 10G lane: example port 1/3
MuoN A10 10G lane: example port 1/5
```

Each lane maintains independent processed and re-arm state.

## Validated switch platform

The current release candidate was developed and validated on:

```text
NVIDIA/Mellanox SN2410
Onyx X86_64 3.10.4100
```

Other Onyx versions may use different Docker CLI syntax. Deployment requires
support for `user-env` on `docker start`; upgrade older switches before using
this release.

## Network contract

- All onboarding ports must already be access ports in VLAN 1.
- The switch VLAN IP must be a usable host address in `192.168.39.0/24`.
- `192.168.39.10` is an example only.
- Temporary recovery uses an assumed `/24`.
- Polling interval is 10 seconds.
- A processed lane re-arms after 60 seconds continuously down.
- Simultaneously connected devices must not advertise the same management IP.
- Expected speeds are documented but are not configured or validated automatically.

## Exact reset operation

Both FusioN and MuoN A10 use:

```http
PUT /emsfp/node/v1/self/system
```

with exactly:

```json
{"config_reset": "system"}
```

The payload is intentionally narrow. The application does not send a complete system representation or unrelated fields.

## High-level workflow

```text
Port link detected
  -> wait for LLDP
  -> discover management IPv4 address
  -> reject duplicate IP across active lanes
  -> test reachability from the switch
  -> add temporary VLAN address when required
  -> send factory-reset request from the Onyx-hosted container
  -> remove temporary address in cleanup
  -> mark lane processed
  -> re-arm after 60 seconds continuously down
```

## Repository structure

```text
src/mnip_test_automation/
  app.py          startup and composition
  config.py       configuration loading and validation
  configure.py    interactive persistent configuration helper
  device.py       exact MN-IP reset request
  models.py       lane runtime state
  switch.py       Onyx interaction
  watcher.py      multi-lane workflow coordination

docker/           image and helper entrypoints
config/           safe public configuration example
tests/            automated tests
docs/             focused operator and engineering documentation
```

## Deploy

Start with [Deployment](docs/deployment.md). The guide begins in Windows PowerShell with the TAR in the user Downloads folder and labels every required Onyx prompt mode.

## Documentation

- [Architecture](docs/architecture.md)
- [Deployment](docs/deployment.md)
- [Development](docs/development.md)
- [API and device support](docs/api-and-device-support.md)
- [Validation history](docs/validation-history.md)
- [Roadmap](docs/roadmap.md)

## Current limitations

- SSH/CLI handling still uses fixed sleeps and broad reads.
- Temporary recovery assumes `/24` and an adjacent address.
- General ARP conflict detection is not implemented.
- Expected port speed is not validated automatically.
- Processed state is not durable across container restart.
- Post-reset readiness and structured result reporting remain future work.
- v1.0-rc1 still requires hardware validation of the third FusioN 10G lane.

## Production scope

“Production” means deployment in the controlled Riedel lab/test-station environment described in this repository. It does not mean unrestricted deployment into arbitrary customer networks.
