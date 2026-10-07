# Executive Summary

MNIP Test Automation is a laboratory automation project for repeatable onboarding and validation of Riedel MN-IP devices. Its purpose is to turn a physical test lane into a predictable workflow: connect a device, discover its current identity and address, return it to a known state, configure and validate it, and retain useful evidence.

The project began by asking whether a portable Docker application could combine NVIDIA Onyx LLDP data with the Riedel MN-IP REST API. That one-shot proof of concept succeeded on October 4, 2026. The same image ran on a Linux Utility VM and on an NVIDIA/Mellanox SN2410.

On October 6, 2026, the project solved a more realistic onboarding problem. A device was deliberately moved to an address outside the switch VLAN's configured subnet. LLDP still supplied its management address, but Layer 3 communication failed. Onyx accepted an additional address on the existing VLAN interface, making the device reachable without replacing the switch's primary address. The automation then added that address temporarily, sent the reset request from a switch-hosted container, and removed the address afterward.

The prototype was also converted into a persistent watcher. It polls a designated lane, waits for LLDP, performs the reset once, remains active, and requires 60 seconds of continuous link-down before re-arming. This guard prevented the device's normal reboot link transition from causing a reset cycle. The workflow was repeated successfully with a second private subnet.

The current validated capability is therefore:

```text
Discover -> assess reachability -> recover reachability if needed
         -> reset once -> clean up -> hold lane -> re-arm after removal
```

This is meaningful support value: a device does not have to arrive in the test station's known management subnet, provided it advertises a usable management address through LLDP and the controlled temporary-address policy is acceptable.

The project is still a prototype. Prompt-aware switch interaction, conflict detection, durable state, secure secrets, post-reset readiness, structured logs, tests, provisioning, media validation, and reporting remain future work.

The first complete target workflow remains:

```text
Discover -> identify -> reset -> recover -> configure
         -> provision four SDP receivers -> validate ST 2110 and video
         -> monitor -> report
```
