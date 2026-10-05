# AGENT CONTEXT

## Project

MNIP Test Automation

Repository:

https://github.com/mbuer/mnip-test-automation

## Mission

Create a reusable automated onboarding framework for Riedel devices.

Current implementation target:

- Riedel MN-IP
- NVIDIA Onyx (SN2410)

Future targets:

- Additional Riedel products
- Netgear switches
- Luminex switches

## Long Term Workflow

Discovery
→ Identification
→ Reset
→ Provision
→ Validation
→ Reporting

## Architectural Principles

### Discovery Layer

Responsible for finding devices.

Examples:

- LLDP
- Static Port Mapping
- Future discovery methods

Discovery returns device information.

Automation must not depend on specific switch vendors.

### Device Layer

Responsible for:

- Factory Reset
- Provisioning
- Validation

Uses device-specific APIs.

### Reporting Layer

Responsible for:

- Logs
- Test results
- Future audit trails

## Confirmed Technical Findings

### Onyx Docker

Verified:

- SCP upload works
- Standard Docker images load successfully
- Containers execute successfully
- Same image runs on Linux VM and SN2410

### LLDP

Verified:

show lldp interfaces ethernet 1/25 remote

Returns:

- System Name
- Chassis ID
- Management IP Address

Management IP is directly usable for API operations.

### MN-IP REST API

Verified:

PUT /emsfp/node/v1/self/system

Factory reset:

{
  "config_reset": "system"
}

Reboot:

{
  "reboot": "1"
}

### Proof Of Concept Success

Workflow verified:

LLDP Detection
→ Management IP Extraction
→ REST API Factory Reset

Executed successfully from:

- Linux Docker
- NVIDIA Onyx Docker

## Static Port Strategy

Current laboratory design uses fixed onboarding ports.

Example:

Ethernet1/25
→ Factory Reset

Future:

Port mapping defined in configuration.

LLDP will enrich metadata but not replace static assignments.

## Things Not Implemented Yet

- Provisioning
- Reporting
- Device inventory
- Netgear support
- Luminex support
- Validation workflows
- Long duration testing
- Web UI

## Development Philosophy

Build smallest working workflow first.

Avoid over-engineering.

Always maintain portability between:

- Linux Docker
- Switch Docker

