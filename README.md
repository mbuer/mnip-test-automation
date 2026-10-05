# MNIP Test Automation

Automated onboarding, provisioning, validation and testing framework for Riedel MN-IP devices.

## Executive Summary

MNIP Test Automation is a laboratory automation platform intended to remove repetitive manual work from device onboarding and validation processes.

The initial implementation targets:

- Riedel MN-IP devices
- NVIDIA Onyx switches (SN2410)
- LLDP-based discovery
- REST API automation
- Docker-based deployment

## Vision

Device Connected -> Discovery -> Identification -> Reset -> Provision -> Validation -> Reporting

## Current Status

Phase 1 proof of concept completed.

Validated:
- Docker execution on Linux VM
- Docker execution on NVIDIA Onyx SN2410
- LLDP management IP extraction
- Automated MN-IP factory reset

## Documentation

See docs directory for architecture, roadmap, deployment and integration details.
