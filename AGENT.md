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

- Additional Riedel platforms
- Netgear switches
- Luminex switches

## End State

Device Connected

↓

Discovery

↓

Identification

↓

Reset

↓

Provision

↓

Validation

↓

Monitoring

↓

Reporting

## Proven End-To-End Workflow

Validated on 2026-10-04.

Workflow:

SN2410 LLDP

↓

Management IP Extraction

↓

REST API Factory Reset

↓

Device Reboot

Successful.

Executed from:

- Linux Docker
- SN2410 Docker

Same container image.

## Architectural Principles

### Discovery Layer

Responsible for:

- LLDP
- Static Port Mapping
- Future discovery methods

Returns device metadata.

### Device Layer

Responsible for:

- Reset
- Provisioning
- Validation

Must remain independent from switch vendors.

### Reporting Layer

Responsible for:

- Logs
- Reports
- Audit history

## Confirmed Technical Findings

### Onyx Docker

Verified:

- SCP upload
- Standard Docker image import
- Container execution
- Same image runs on VM and SN2410

### LLDP

Verified:

show lldp interfaces ethernet 1/25 remote

Returns:

- System Name
- Chassis ID
- Management IP

Management IP can be consumed directly by automation.

### MN-IP REST API

Verified:

PUT /emsfp/node/v1/self/system

Factory Reset:

{
  "config_reset": "system"
}

Reboot:

{
  "reboot": "1"
}

## Static Port Strategy

Current preferred model:

Static port assignment

+

Dynamic LLDP metadata

Example:

Ethernet1/25
→ Factory Reset Lane

Future:

Port layout defined in configuration.

## Not Implemented Yet

- Provisioning
- Validation
- Reporting
- Inventory
- Netgear support
- Luminex support
- Overnight testing

## Development Philosophy

Build smallest working workflow first.

Avoid over-engineering.

Preserve portability between:

- Linux Docker
- Onyx Docker

