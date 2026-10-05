# Test-Station Design

## Purpose

The test station should provide predictable physical lanes, deterministic workflows, media sources and destinations, operator visibility, and a path to repeatable evidence.

## Initial concept

An SN2410 acts as the central IP switch. A designated onboarding port connects to the device under test. Static port mapping determines which workflow is permitted on that lane, while LLDP identifies the attached device and supplies the management address.

The intended MN-IP validation workflow will use ST 2110 senders as sources and provision four receiver definitions on a FusioN gateway. The resulting video should be visible on an appropriate confidence monitor or test display. Application and device status will eventually be collected for an operator-readable result.

## Functional areas

```text
Management and automation
  - Utility VM or switch-hosted container
  - Switch management
  - Device management API

Onboarding lane
  - Fixed physical port
  - LLDP discovery
  - Reset and configuration workflow

Media generation
  - Known ST 2110 sender flows
  - Controlled SDP definitions

Device under test
  - FusioN ST 2110 gateway
  - Four configured receiver paths

Validation
  - Receiver state
  - Expected media flow
  - Video output or confidence display
  - Long-duration health observations

Reporting
  - Workflow events
  - Device and test metadata
  - Pass/fail outcome
  - Diagnostic details
```

## Design principles

- Label physical ports and cables consistently with configuration names.
- Keep management, media, and test-control assumptions documented.
- Use known-good source streams and version-controlled non-secret test definitions.
- Define pass/fail criteria before automating a validation.
- Record enough evidence to distinguish infrastructure failures from device failures.
- Make destructive lanes visually and operationally unambiguous.

## Open design questions

- Exact switchport allocation for senders, receivers, management, monitoring, and spare lanes
- VLAN and PTP design for the final media-validation topology
- Source of truth for SDP files
- Method for confirming video output automatically
- Required test duration and sampling frequency
- Failure classification and report format

These details should be added when the rough physical drawing and actual lab port plan are incorporated into the repository.
