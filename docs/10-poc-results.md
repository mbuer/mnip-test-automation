# Proof-of-Concept and Watcher Validation Results

## Milestone 1: one-shot feasibility

**Validation date:** October 4, 2026

### Objective

Determine whether a portable Docker application could use SN2410 LLDP information to discover an MN-IP device and trigger factory reset through the device REST API.

### Result

The image built on the Linux Utility VM, connected to Onyx through an interactive Paramiko shell, queried Ethernet 1/25, extracted the management IPv4 address, and sent the reset request. The device returned HTTP 200 with `system rebooting` and rebooted. The same image subsequently ran on the SN2410.

### Key Onyx findings

- The account was CLI-only and rejected remote UNIX commands.
- `invoke_shell()` was required.
- `terminal length 0` was invalid on the tested release.
- One-shot containers remained registered after exit.
- Application output was not conveniently exposed through basic container status.

## Milestone 2: unreachable-device recovery

**Validation date:** October 6, 2026

### Objective

Determine whether the station could reset a device that advertises its management address through LLDP but is not in the switch VLAN's current IP subnet.

### Initial condition

```text
Switch VLAN 1 primary: 192.168.39.10/24
Device: 10.10.10.10/24
LLDP: device identity and 10.10.10.10 visible
Ping: failed
```

### Manual validation

Onyx accepted:

```text
interface vlan 1
ip address 10.10.10.11/24
```

After assignment, switch ping succeeded. After:

```text
no ip address 10.10.10.11/24
```

ping failed again. This repeated add/remove sequence established clear cause and effect.

### Automation lessons

The first VM-hosted attempt restored switch reachability but the REST call still timed out because `requests.put()` ran from the Utility VM. This confirmed that temporary switch addressing does not alter the VM route.

The successful workflow ran inside Docker on the SN2410:

```text
LLDP discovery
-> switch-side ping failed
-> enable
-> configure terminal
-> add temporary VLAN address
-> switch-side ping succeeded
-> container sent REST reset
-> finally cleanup removed temporary address
```

The device factory-reset successfully, and `show ip interface brief` confirmed cleanup.

## Milestone 3: persistent watcher and reset-cycle guard

**Validation date:** October 6, 2026

### Objective

Keep the container running, process a device automatically when connected, avoid repeated reset during reboot, and re-arm after actual removal.

### Validated behavior

- Watcher remained running while the port was empty.
- Poll interval was configured at approximately 10 seconds.
- Link Up was observed before LLDP was always ready; the watcher retried LLDP.
- A newly connected device was processed automatically.
- The watcher remained running after reset.
- A simple immediate re-arm on link Down was identified as unsafe because reset may flap the link.
- Re-arm was changed to require 60 seconds of continuous link Down.
- The revised watcher processed a device configured at `172.20.50.100/24` using temporary `172.20.50.101/24`.
- The device returned to its factory address and remained connected without another reset.
- The port stayed Up for more than three minutes after the reset without a new operational transition.
- The temporary address was absent after completion.

### Result

The v0.4 watcher prototype met the intended trigger semantics for the tested lane:

```text
wait -> discover -> recover reachability -> reset once -> cleanup
     -> hold processed state -> re-arm after sustained removal
```

## What is now proven

- LLDP discovery does not require Layer 3 reachability.
- Onyx can hold an additional IPv4 address on an existing VLAN interface.
- Controlled temporary adjacency can enable a short REST transaction to an otherwise unreachable device.
- The REST call must execute from a network context that has the temporary path.
- A switch-hosted Docker watcher can remain running and process device connection events.
- Sustained-down re-arm protects against the tested reboot cycle.
- Cleanup can return the switch VLAN to its original state after success.

## What remains unproven or incomplete

- General safety of `/24` and adjacent-address assumptions
- Address-conflict detection
- Prompt-aware SSH and robust CLI error handling
- Cleanup behavior across process kill, switch reboot, or loss of management connectivity
- Persisted lane state and restart recovery
- Post-reset service readiness
- Multiple lanes or simultaneous devices
- Secure production credential injection
- Structured logging and result retention
- Configuration, SDP provisioning, ST 2110 validation, and video confirmation
- Automated test coverage

## Conclusion

The project has moved from a one-shot feasibility script to a valuable onboarding prototype. A device can arrive on the designated lane with an unexpected management address, be discovered through LLDP, temporarily reached by the switch, reset from the switch-hosted container, and released without leaving the temporary address configured. The watcher can then remain active without repeatedly resetting the same rebooting device.

The next work should harden this behavior rather than immediately adding more device operations.
