# Executive Summary

MNIP Test Automation is a laboratory automation project for repeatable onboarding and validation of Riedel MN-IP devices. The project began by testing whether discovery and device control could run in a portable Docker image on both a Linux Utility VM and an NVIDIA/Mellanox SN2410 switch.

On October 4, 2026, the initial proof of concept succeeded. The application opened an interactive Onyx CLI session, queried LLDP on a predefined test port, extracted the attached device's management address, and sent a factory-reset request to the MN-IP REST API. The same Docker image completed the workflow from the Utility VM and from the switch.

This result establishes technical feasibility for a broader automation cycle:

```text
Discover -> identify -> reset -> recover -> configure -> provision -> validate -> monitor -> report
```

The intended first complete workflow will reset a FusioN ST 2110 gateway, configure four receivers with SDP information from ST 2110 senders, verify reception and expected video output, and retain useful results from tests lasting hours or days.

The project is currently a proof of concept, not a production system. Continuous triggering, safe state management, post-reset recovery checks, provisioning, media validation, durable logs, reporting, automated tests, and secure credential handling remain future work.

The architecture intentionally combines static physical lanes with dynamic discovery. A configured switchport selects the workflow, while LLDP identifies the device currently connected to that lane and provides its management address. Switch-specific discovery and device-specific automation will remain separate so that additional switch manufacturers and Riedel product families can be added later.
