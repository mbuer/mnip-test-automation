# MNIP Test Automation

Automated onboarding, provisioning, validation, and testing framework for Riedel MN-IP devices.

## Executive Summary

MNIP Test Automation provides a repeatable onboarding workflow for MN-IP devices connected to a dedicated test station.

Current proof of concept capabilities include:

- LLDP-based device discovery on NVIDIA Onyx switches
- Extraction of management IP addresses from LLDP advertisements
- REST API integration with MN-IP devices
- Automated factory reset execution
- Containerized deployment using Docker
- Execution on both Linux VMs and NVIDIA SN2410 switches

Future development phases include:

- Device provisioning
- Configuration deployment
- ST2110 receiver validation
- Signal verification
- Long-term stability testing
- Reporting and audit logging
- Support for additional switch vendors

## Current Status

Proof of concept completed.

Verified:

- Docker execution on Linux VM
- Docker execution on NVIDIA Onyx (SN2410)
- LLDP discovery on Onyx
- Automated MN-IP factory reset via REST API

## Architecture

High-level workflow:

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

Validate

↓

Report

## Documentation

- docs/00-executive-summary.md
- docs/01-vision-and-scope.md
- docs/02-architecture.md
- docs/03-onyx-integration.md
- docs/04-mn-ip-api.md
- docs/05-test-station-design.md
- docs/06-port-mapping-strategy.md
- docs/07-roadmap.md
- docs/08-development-guide.md
- docs/09-deployment.md
- docs/10-poc-results.md

## Design Goals

- Fully automated onboarding
- Reusable workflows
- Vendor-agnostic switch abstraction
- Portable Docker deployment
- Support for future Riedel devices
- Clean separation between discovery and automation

## Deployment Targets

Current:

- Linux Docker
- NVIDIA Onyx Docker

Future:

- Netgear
- Luminex
- Additional switch platforms

## Security

- No credentials stored in Git
- Configuration supplied externally
- Secrets excluded from repository

