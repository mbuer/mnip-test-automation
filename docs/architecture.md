# Architecture

## Purpose

MN-IP Test Automation uses a switch-hosted watcher to discover, reach, and factory-reset supported Riedel devices connected to designated physical lanes.

## Components

```text
Persistent YAML configuration
  -> independent lane definitions
  -> Onyx switch adapter
  -> LLDP discovery and reachability recovery
  -> exact MN-IP device operation
  -> lane state and re-arm policy
```

### Module responsibilities

- `config.py`: configuration path selection and validation
- `configure.py`: interactive configuration writer
- `models.py`: independent mutable lane state
- `switch.py`: Onyx SSH, port status, LLDP, ping, and temporary VLAN addresses
- `device.py`: exact narrow factory-reset request
- `watcher.py`: orchestration, conflict prevention, cleanup, and re-arm
- `app.py`: dependency composition and startup

## Three-lane model

```text
FusioN 25G lane
FusioN 10G lane
MuoN A10 10G lane
```

Ports are configurable. Examples `1/1`, `1/3`, and `1/5` are not requirements.

Each lane owns:

- configured port;
- expected speed metadata;
- device family;
- workflow;
- processed flag;
- continuous-down timer.

## State flow

```text
WAITING_FOR_LINK
  -> WAITING_FOR_LLDP
  -> DISCOVERED
  -> CONFLICT_CHECK
  -> CHECKING_REACHABILITY
  -> RECOVERING_REACHABILITY (optional)
  -> RESETTING
  -> CLEANUP
  -> PROCESSED
  -> WAITING_FOR_60_SECONDS_DOWN
  -> WAITING_FOR_LINK
```

## Network contract

- Shared access VLAN: VLAN 1
- Required switch VLAN subnet: `192.168.39.0/24`
- Temporary prefix: `/24`
- All configured ports must already be access ports in VLAN 1.
- Expected speed is not automatically configured or validated.

LLDP provides the current management address but not the device prefix. The current recovery policy derives an adjacent temporary address: `+1`, except `.254` uses `-1`.

## Shared-VLAN protections

Before processing a lane, the watcher checks the other active lanes. If another lane advertises the same LLDP management IP, reset is skipped.

This guard protects against the simplest cross-lane ambiguity. It is not general ARP conflict detection for the temporary address.

## Cleanup

Temporary VLAN configuration is a transaction:

```text
calculate -> add -> verify reachability -> use -> remove
```

Removal runs through `finally`. Future hardening should verify removal explicitly and stop destructive workflows when cleanup fails.

## Execution location

- Switch-side ping and VLAN configuration run through Onyx CLI.
- REST runs inside the Onyx-hosted container.
- The Utility VM is for development, build, tests, and normal routed cases.

## Current limitations

- fixed sleeps and broad channel reads;
- repeated SSH sessions;
- regex/text parsing;
- no durable state after restart;
- no post-reset readiness check;
- no structured result store;
- no automatic port-speed validation;
- no general temporary-address conflict detection.
