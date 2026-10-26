# Validation History

This document is append-only evidence. Current operating instructions belong elsewhere.

## October 4, 2026: one-shot proof of concept

Validated:

- Docker image built on Linux Utility VM;
- Onyx LLDP queried through Paramiko interactive shell;
- management IPv4 extracted from Ethernet 1/25;
- narrow factory-reset PUT accepted;
- same image executed on SN2410.

## October 6, 2026: arbitrary-address recovery

Lab observation:

```text
Switch VLAN primary: 192.168.39.10/24
Device LLDP address: 10.10.10.10
Initial IP reachability: failed
```

Adding `10.10.10.11/24` to the existing VLAN interface restored switch-to-device reachability. Removing the address removed reachability. The workflow was repeated with another private subnet.

These are historical lab values, not defaults.

## October 6, 2026: persistent watcher

Validated:

- persistent container;
- 10-second polling;
- link-up before LLDP readiness;
- one-shot processed guard;
- 60-second continuous-down re-arm;
- prevention of reboot-induced reset loops;
- cleanup of temporary VLAN addressing.

## October 12, 2026: v0.6 multi-lane

Implemented and tested:

- FusioN and MuoN A10 independent lanes;
- configurable ports;
- persistent `mnip-config` label;
- interactive helper with hidden password entry;
- secret-safe image;
- duplicate management-IP guard;
- unit-test coverage.

Hardware validated:

- FusioN expected 25G lane;
- MuoN A10 expected 10G lane, repeatedly.

## October 26, 2026: v1.0-rc1

Implemented on the Utility VM:

- third lane for FusioN expected 10G;
- generic example ports `1/1`, `1/3`, and `1/5`;
- example VLAN IP `192.168.39.10` clearly labeled;
- switch VLAN subnet requirement `192.168.39.0/24`;
- 58 MB release-candidate TAR;
- helper test for the generated three-lane YAML.

Pending lab validation:

- fresh deployment with final instructions;
- FusioN 25G lane;
- FusioN 10G third lane;
- MuoN A10 10G lane;
- three-lane conflict behavior;
- cleanup and independent re-arm checks.
