# Test-Station Design

## Purpose

The test station should make a complex onboarding process feel physically obvious: each labeled lane has a known purpose, the automation discovers what is connected, and the resulting evidence distinguishes device failures from infrastructure failures.

## Current validated lane

```text
Ethernet 1/25 -> MN-IP factory-reset watcher
```

The lane remains statically assigned while the connected device identity and management address are learned dynamically through LLDP.

A useful property of this design is that a returned or lab device may arrive with an address outside the station's normal management subnet. The switch can temporarily join that device's Layer 2 segment under a controlled recovery policy, perform the onboarding action, and remove the additional address afterward.

## Functional areas

```text
Management and automation
  - Utility VM for development and image builds
  - Onyx-hosted watcher for lane-local operation
  - Switch and device credentials supplied outside Git

Onboarding lane
  - Fixed physical port
  - Link and LLDP observation
  - Temporary reachability recovery
  - Reset and later configuration workflows

Media generation
  - Known ST 2110 sender flows
  - Controlled SDP definitions

Device under test
  - FusioN ST 2110 gateway
  - Four future receiver paths

Validation
  - Device readiness
  - Receiver state and expected flows
  - Video output or confidence display
  - Long-duration observations

Reporting
  - Workflow and cleanup events
  - Device/test metadata
  - Pass/fail outcome
  - Diagnostics and operator actions
```

## Human factors

- Label destructive lanes unambiguously.
- Display which workflow is armed before a device is connected.
- Show when temporary switch configuration is active.
- Make cleanup failure visible and require acknowledgement.
- Provide a way to inhibit or maintenance-lock a lane.
- Do not make an operator infer success solely from a reboot.

## Network design considerations

Temporary VLAN addressing is useful for onboarding, but it is not automatic address management. Before expanding beyond a controlled lab lane, define:

- VLAN isolation and who else can be present in the broadcast domain;
- acceptable prefix assumptions;
- conflict-detection behavior;
- prohibited address ranges;
- how management and media VLANs are separated;
- PTP and ST 2110 topology;
- cleanup verification and escalation.

## Open design questions

- Final port allocation for senders, receivers, management, monitoring, and spares
- Source of truth and versioning for SDP files
- Automatic video-output confirmation method
- Test duration and health-sampling frequency
- Failure taxonomy and report format
- Operator acknowledgement and lane maintenance controls
- Number of concurrent lanes supported by switch and workflow state
