# AGENT CONTEXT

## Project

MNIP Test Automation

Repository

https://github.com/mbuer/mnip-test-automation

## Mission

Create a reusable onboarding framework for Riedel devices.

## Proven Findings

- Docker images built on Linux VM execute on SN2410.
- Standard docker save archives load successfully on Onyx.
- LLDP management IP extraction works from Ethernet1/25.
- MN-IP factory reset successfully triggered via REST API.

## End State

Discovery -> Identification -> Reset -> Provision -> Validation -> Monitoring -> Reporting
## Architecture Rule

Keep Discovery, Automation and Reporting as separate layers.

Discovery must not contain device business logic.
